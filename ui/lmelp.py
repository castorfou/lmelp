import streamlit as st
from streamlit_card import card
from ui_tools import add_to_sys_path

add_to_sys_path()

from rss import Podcast  # Ajout de l'importation nécessaire

st.set_page_config(
    page_title="le masque et la plume",
    page_icon=":book:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.write("## Quel critique du masque etes-vous ?")
st.write(
    "découvrez quel critique du masque vous êtes en fonction de vos gouts littéraires"
)

st.page_link("lmelp.py", label="Home", icon="🏠")

# https://fonts.google.com/icons?selected=Material+Symbols+Outlined:music_note:FILL@0;wght@400;GRAD@0;opsz@24&icon.query=music&icon.size=24&icon.color=%235f6368

st.page_link("pages/1_st_episodes.py", label="episodes", icon=":material/music_note:")
st.page_link("pages/2_st_auteurs.py", label="auteurs", icon=":material/person:")
st.page_link("pages/3_st_livres.py", label="livres", icon=":material/menu_book:")

st.write("## Contenu (a mettre sous forme de cartes)")
st.write(f"Auteurs tbd")
st.write(f"Livres tbd")
st.write(f"Avis tbd")

import locale

from mongo_episode import Episodes

episodes = Episodes()

# Bouton de rafraîchissement des épisodes
if st.button("Refresh Episodes"):
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    with st.spinner("Mise à jour des épisodes en cours..."):
        podcast = Podcast()
        podcast.store_last_large_episodes()
        # Rechargement des épisodes après mise à jour
    st.success("Episodes mis à jour !")


def affiche_episodes(episodes=episodes):
    episodes.get_entries()
    card(
        title="# episodes",
        text=f"{len(episodes)}",
        image="http://placekitten.com/300/250",
        url="/st_episodes",
    )


# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

DATE_FORMAT = "%d %b %Y"


def affiche_last_date(episodes=episodes):
    episodes.get_entries(limit=1)
    card(
        title="last episode",
        text=f"{episodes[0].to_dict().get('date').strftime(DATE_FORMAT)}",
        image="http://placekitten.com/300/250",
        url="/st_episodes",
    )


def affiche_missing_transcription(episodes=episodes):
    episodes.get_missing_transcriptions()

    card(
        title="# missing transcriptions",
        text=f"{len(episodes)}",
        image="http://placekitten.com/300/250",
        url="/st_episodes",
    )


# Créer des colonnes pour afficher les cartes sur la même ligne
col1, col2, col3 = st.columns(3)

with col1:
    affiche_episodes(episodes)
with col2:
    affiche_last_date(episodes)
with col3:
    affiche_missing_transcription(episodes)
