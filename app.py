import os
import difflib
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)
mots_cuisine_reference = [
    # Actions
    "cuire", "cuisiner", "préparer", "faire", "recette", "mélanger",
    "griller", "bouillir", "frire", "mijoter", "mariner", "assaisonner",
    "couper", "éplucher", "râper", "fouetter", "pétrir", "rôtir",

    # Ingrédients de base
    "ingrédient", "farine", "oeuf", "beurre", "huile", "sel", "sucre",
    "lait", "crème", "eau", "levure", "fécule", "amidon",

    # Légumes
    "tomate", "oignon", "ail", "carotte", "pomme", "courgette",
    "aubergine", "poivron", "épinard", "haricot", "pois", "lentille",
    "navet", "céleri", "poireau", "concombre", "salade",

    # Viandes & poissons
    "viande", "poulet", "boeuf", "agneau", "mouton", "dinde", "veau",
    "poisson", "thon", "sardine", "crevette", "saumon", "calmar",
    # Plats
    "plat", "soupe", "sauce", "salade", "dessert", "entrée",
    "pizza", "pâte", "pain", "gâteau", "crêpe", "tarte", "quiche",
    "couscous", "tajine", "chorba", "brika", "makroudh", "tiramisu",
    "risotto", "paella", "lasagne", "burger", "sandwich",

    # Épices
    "épice", "cumin", "curcuma", "paprika", "cannelle", "gingembre",
    "coriandre", "persil", "thym", "basilic", "menthe", "safran",

    # Ustensiles
    "four", "casserole", "poêle", "moule", "couteau", "mixeur",

    # Général
    "cuisine", "manger", "recette", "chocolat", "fromage", "yaourt"
]
mots_interdits = [
    "exercice", "examen", "tp", "devoir", "math", "physique", "chimie", 
    "science", "programmation", "code", "langage", "informatique", "python", "java"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_msg = data.get("message", "")

        if not user_msg:
            return jsonify({"reponse": "Dis-moi quelque chose !"})

        msg_minuscule = user_msg.lower()
        if any(mot in msg_minuscule for mot in mots_interdits):
            return jsonify({"reponse": "Désolé, c'est pas mon domaine."})

        # Pre-processing avec difflib
        mots_utilisateur = msg_minuscule.split()
        mots_corriges = []

        for mot in mots_utilisateur:
            correction = difflib.get_close_matches(
                mot,
                mots_cuisine_reference,
                n=1,
                cutoff=0.6
            )
            if correction:
                mots_corriges.append(correction[0])
            else:
                mots_corriges.append(mot)
        message_corrige = " ".join(mots_corriges)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.0, 
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un Chef de cuisine expert. "
                        "RÉPONDS UNIQUEMENT en français. "
                        "Tu dois refuser catégoriquement de répondre aux sujets académiques, "
                        "scientifiques, mathématiques ou informatiques (code, exercice, examen, TP). "
                        "Si la question n'est pas DIRECTEMENT ET EXCLUSIVEMENT liée à la cuisine, "
                        "réponds exactement et uniquement : 'Désolé, c'est pas mon domaine.'"
                    )
                },
                {
                    "role": "user",
                    "content": message_corrige
                }
            ]
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"reponse": answer})

    except Exception as e:
        print(f"Erreur : {e}")
        return jsonify({"reponse": f"Une erreur est survenue : {e}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
