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

st.page_link("pages/1_episodes.py", label="episodes", icon=":material/music_note:")
st.page_link("pages/2_auteurs.py", label="auteurs", icon=":material/person:")
st.page_link("pages/3_livres.py", label="livres", icon=":material/menu_book:")
st.page_link(
    "pages/4_avis_critiques.py", label="avis critiques", icon=":material/rate_review:"
)

st.write("## Contenu (a mettre sous forme de cartes)")
st.write(f"Auteurs tbd")
st.write(f"Livres tbd")
st.write(f"Avis tbd")

import locale

from mongo_episode import Episodes

episodes = Episodes()

import io
import sys
import subprocess

# Bouton de rafraîchissement des épisodes avec affichage avancé de l'output
if st.button("🔄 Rafraîchir Episodes"):
    nb_episodes = episodes.len_total_entries()
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    with st.spinner("Mise à jour des épisodes en cours..."):
        podcast = Podcast()
        # Capturer la sortie de la fonction
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            podcast.store_last_large_episodes()
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()
        if output:
            st.expander("Output de la mise à jour").code(output, language="bash")
    nb_episodes_after = episodes.len_total_entries()
    if nb_episodes_after > nb_episodes:
        st.success(f"{nb_episodes_after - nb_episodes} episodes mis à jour !")
    else:
        st.warning("Pas de nouveaux épisodes aujourd'hui")

episodes.get_missing_transcriptions()
if len(episodes) > 0:
    if st.button("📥 Télécharger transcriptions "):
        with st.spinner("Téléchargement des transcriptions en cours..."):
            # Exécuter le script get_one_transcription.py situé dans le dossier scripts
            episodes.get_missing_transcriptions()
            if len(episodes) > 0:
                # on prend le dernier
                episode = episodes[-1]

                # Capturer la sortie de la fonction
                buf = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = buf
                try:
                    episode.set_transcription(verbose=True)
                finally:
                    sys.stdout = old_stdout
                output = buf.getvalue()
                if output:
                    st.expander("Output du telechargement").code(
                        output, language="None"
                    )
                episodes.get_missing_transcriptions()
            else:
                st.warning("Il n'y a pas d'episodes sans transcriptions")


def affiche_episodes(episodes=episodes):
    card(
        title="# episodes",
        text=f"{episodes.len_total_entries()}",
        image="http://placekitten.com/300/250",
        url="/episodes",
    )


# Définir la locale en français

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
from date_utils import DATE_FORMAT, format_date


def affiche_last_date(episodes=episodes):
    episodes.get_entries(limit=1)
    card(
        title="last episode",
        text=f"{format_date(episodes[0].to_dict().get('date'))}",
        image="http://placekitten.com/300/250",
        url="/episodes",
    )


def affiche_missing_transcription(episodes=episodes):
    episodes.get_missing_transcriptions()
    card(
        title="# missing transcriptions",
        text=f"{len(episodes)}",
        image="http://placekitten.com/300/250",
        url="/episodes",
    )


# Créer des colonnes pour afficher les cartes sur la même ligne
col1, col2, col3 = st.columns(3)

with col1:
    affiche_episodes(episodes)
with col2:
    affiche_last_date(episodes)
with col3:
    affiche_missing_transcription(episodes)
