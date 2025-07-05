import streamlit as st
import sys
import re
from pathlib import Path

# st.set_page_config(page_title="Livres")

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path

from mongo_livre import Livre

add_to_sys_path()


def afficher_livres():
    st.write("### Livres")
    st.write("Liste des livres discutés dans l'émission.")
    # Récupération et tri des noms
    docs = Livre("test").collection.find({}, {"nom": 1, "_id": 0})
    livres = sorted([doc["nom"] for doc in docs], key=lambda n: n.lower())

    # Champ de filtre dynamique
    filtre = st.text_input("Filtrer les livres:", "")

    # Filtrer la liste en fonction du texte saisi, insensible à la casse
    livres_affiches = (
        [nom for nom in livres if filtre.lower() in nom.lower()] if filtre else livres
    )

    # Afficher le nombre d'livres après filtrage
    st.markdown(
        f"<p style='color: grey; font-size: small;'>Nombre d'livres affichés&nbsp;: {len(livres_affiches)}</p>",
        unsafe_allow_html=True,
    )

    # Mettre en évidence le texte correspondant au filtre dans chaque nom
    if filtre:
        # Utiliser re.escape pour éviter les problèmes avec des caractères spéciaux
        pattern = re.compile(re.escape(filtre), re.IGNORECASE)
        livres_highlight = [
            pattern.sub(lambda m: f"**{m.group(0)}**", nom) for nom in livres_affiches
        ]
    else:
        livres_highlight = livres_affiches

    # Concaténer la liste filtrée en une chaîne de caractères et l'afficher en Markdown
    texte_livres = ", ".join(livres_highlight)
    st.markdown(texte_livres)


afficher_livres()
