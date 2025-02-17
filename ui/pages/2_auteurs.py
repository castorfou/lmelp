import streamlit as st
import sys
import re
from pathlib import Path

# st.set_page_config(page_title="Auteurs")

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path

add_to_sys_path()

from mongo_auteur import Auteur


def afficher_auteurs():
    st.write("### Auteurs")
    st.write("Liste des auteurs discutés dans l'émission.")
    # Récupération et tri des noms
    docs = Auteur("test").collection.find({}, {"nom": 1, "_id": 0})
    auteurs = sorted([doc["nom"] for doc in docs], key=lambda n: n.lower())

    # Champ de filtre dynamique
    filtre = st.text_input("Filtrer les auteurs:", "")

    # Filtrer la liste en fonction du texte saisi, insensible à la casse
    auteurs_affiches = (
        [nom for nom in auteurs if filtre.lower() in nom.lower()] if filtre else auteurs
    )

    # Afficher le nombre d'auteurs après filtrage
    st.markdown(
        f"<p style='color: grey; font-size: small;'>Nombre d'auteurs affichés&nbsp;: {len(auteurs_affiches)}</p>",
        unsafe_allow_html=True,
    )

    # Mettre en évidence le texte correspondant au filtre dans chaque nom
    if filtre:
        # Utiliser re.escape pour éviter les problèmes avec des caractères spéciaux
        pattern = re.compile(re.escape(filtre), re.IGNORECASE)
        auteurs_highlight = [
            pattern.sub(lambda m: f"**{m.group(0)}**", nom) for nom in auteurs_affiches
        ]
    else:
        auteurs_highlight = auteurs_affiches

    # Concaténer la liste filtrée en une chaîne de caractères et l'afficher en Markdown
    texte_auteurs = ", ".join(auteurs_highlight)
    st.markdown(texte_auteurs)


afficher_auteurs()
