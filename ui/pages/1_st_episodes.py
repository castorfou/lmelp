import streamlit as st
from git import Repo
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path

add_to_sys_path()

from mongo_episode import Episodes
import pandas as pd
from datetime import datetime

import locale

# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

DATE_FORMAT = "%d %b %Y"


@st.cache_data  # 👈 Add the caching decorator
def get_episodes():
    episodes = Episodes()
    all_episodes = episodes.episodes
    episodes_df = pd.DataFrame([episode.to_dict() for episode in all_episodes])
    episodes_df["date"] = episodes_df["date"].dt.strftime("%Y/%m/%d")
    episodes_df["duree (min)"] = (episodes_df["duree"] / 60).round(1)
    episodes_df.drop(
        columns=["url_telechargement", "audio_rel_filename", "type", "duree"],
        inplace=True,
    )
    return episodes_df


@st.cache_data  # 👈 Add the caching decorator
def print_episodes_info(episodes_df):
    st.write("### Informations sur les épisodes")
    st.write(f"{episodes_df.shape[0]} épisodes")
    st.write(f"{episodes_df['date'].min()} - {episodes_df['date'].max()}")
    # Compter les transcriptions disponibles et manquantes
    transcriptions_ok = episodes_df["transcription"].notna().sum()
    transcriptions_missing = episodes_df["transcription"].isna().sum()

    st.write(f"Transcriptions OK : {transcriptions_ok}")
    st.write(f"Transcriptions manquantes : {transcriptions_missing}")


def afficher_episodes():
    st.write("### Épisodes")
    st.write("Liste des épisodes du Masque et la Plume.")
    episodes_df = get_episodes()
    print_episodes_info(episodes_df)
    # Ajoutez ici le code pour afficher les épisodes
    st.dataframe(episodes_df, use_container_width=True)


def afficher_un_episode(episodes_df):
    # Widget de sélection de date
    selected_date = st.date_input(
        "Sélectionnez une date",
        min_value=datetime(1958, 1, 1),
        max_value=datetime.today(),
    )

    # Convertir la date sélectionnée en chaîne de caractères au format yyyy/mm/dd
    selected_date_str = selected_date.strftime("%Y/%m/%d")

    # Filtrer le DataFrame pour trouver la ligne correspondant à la date sélectionnée
    episode = episodes_df[episodes_df["date"] == selected_date_str]

    if not episode.empty:
        episode = episode.iloc[0]
        st.write(f"### {episode['titre']}")
        st.write(f"Date: {selected_date.strftime(DATE_FORMAT)}")

        st.write(f"Durée: {episode['duree (min)']} minutes")
        st.write(f"Description: {episode['description']}")
        st.write(f"Transcription: {episode['transcription']}")
    else:
        st.write("Aucun épisode trouvé pour cette date.")


# Sidebar pour la navigation
option = st.sidebar.selectbox(
    "Options", ["Visualiser l'ensemble des épisodes", "Visualiser un épisode"]
)

episodes_df = get_episodes()
# Afficher le contenu en fonction de la sélection
if option == "Visualiser l'ensemble des épisodes":
    afficher_episodes()
elif option == "Visualiser un épisode":
    afficher_un_episode(episodes_df)
