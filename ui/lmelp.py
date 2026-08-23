import streamlit as st
from streamlit_card import card
from ui_tools import add_to_sys_path
from pathlib import Path
from PIL import Image

add_to_sys_path()

from rss import Podcast  # Ajout de l'importation nécessaire

# Load favicon
favicon_path = Path(__file__).parent / "assets" / "favicons" / "favicon-32x32.png"
favicon = Image.open(favicon_path)

st.set_page_config(
    page_title="le masque et la plume",
    page_icon=favicon,
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

from config import get_pgx_config
from date_utils import format_date
from mongo_episode import Episodes
from pgx import get_pgx_config_missing_vars, pgx_fully_configured, run_pgx_diagnostics

episodes = Episodes()

import io
import sys
import subprocess

# Bouton de rafraîchissement des épisodes avec affichage avancé de l'output
if st.button("🔄 Rafraîchir Episodes"):
    nb_episodes = episodes.len_total_entries()
    # Essayer de définir la locale, avec fallback si non disponible
    try:
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
        except locale.Error:
            # Si aucune locale ne fonctionne, continuer sans changer la locale
            pass
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
    nb_episodes_after = episodes.len_total_entries()
    st.session_state["refresh_episodes_result"] = {
        "output": output,
        "nb_new": nb_episodes_after - nb_episodes,
    }

if st.session_state.get("refresh_episodes_result"):
    refresh_result = st.session_state["refresh_episodes_result"]
    if refresh_result["nb_new"] > 0:
        st.success(f"{refresh_result['nb_new']} episodes mis à jour !")
    else:
        st.warning("Pas de nouveaux épisodes aujourd'hui")
    if refresh_result["output"]:
        st.expander("Output de la mise à jour").code(
            refresh_result["output"], language="bash"
        )

episodes.get_missing_transcriptions()
if len(episodes) > 0:
    pgx_config = get_pgx_config()
    missing_pgx_vars = get_pgx_config_missing_vars(pgx_config)
    if missing_pgx_vars:
        pgx_ready = False
    else:
        if "pgx_diagnostics" not in st.session_state:
            st.session_state["pgx_diagnostics"] = run_pgx_diagnostics()
        pgx_ready = pgx_fully_configured(st.session_state["pgx_diagnostics"])

    if not pgx_ready:
        st.warning(
            "⚠️ PGX n'est pas encore correctement configurée/joignable — consultez la "
            "page PGX pour le diagnostic avant de lancer une transcription."
        )
        st.page_link("pages/5_pgx.py", label="Aller à la page PGX", icon="🖥️")

    if st.button("📥 Télécharger transcriptions ", disabled=not pgx_ready):
        with st.spinner("Téléchargement des transcriptions en cours..."):
            # Exécuter le script get_one_transcription.py situé dans le dossier scripts
            episodes.get_missing_transcriptions()
            if len(episodes) > 0:
                # on prend le dernier
                episode = episodes[-1]
                titre = episode.titre
                date_str = format_date(episode.date)

                # Capturer la sortie de la fonction
                buf = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = buf
                try:
                    episode.set_transcription(verbose=True)
                finally:
                    sys.stdout = old_stdout
                episodes.get_missing_transcriptions()
                st.session_state["transcription_download_result"] = {
                    "titre": titre,
                    "date_str": date_str,
                    "success": episode.transcription is not None,
                    "output": buf.getvalue(),
                }
            else:
                st.warning("Il n'y a pas d'episodes sans transcriptions")

if st.session_state.get("transcription_download_result"):
    download_result = st.session_state["transcription_download_result"]
    label = f"{download_result['titre']} ({download_result['date_str']})"
    if download_result["success"]:
        st.success(f"✅ Transcription récupérée : {label}")
    else:
        st.error(f"❌ Échec de la transcription : {label}")
    if download_result["output"]:
        st.expander("Output du téléchargement").code(
            download_result["output"], language="None"
        )


def affiche_episodes(episodes=episodes):
    card(
        title="# episodes",
        text=f"{episodes.len_total_entries()}",
        image="http://placekitten.com/300/250",
        url="/episodes",
    )


# Définir la locale en français

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
from date_utils import DATE_FORMAT


def affiche_last_date(episodes=episodes):
    episodes.get_entries(limit=1)
    if len(episodes) > 0:
        date_text = format_date(episodes[0].to_dict().get("date"))
    else:
        date_text = "No episodes yet"
    card(
        title="last episode",
        text=date_text,
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
