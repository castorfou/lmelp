import streamlit as st
from git import Repo
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path

add_to_sys_path()

st.set_page_config(
    page_title="le masque et la plume",
    page_icon=":material/music_note:",
    layout="wide",
    initial_sidebar_state="auto",
)

from mongo_episode import Episodes
import pandas as pd
from datetime import datetime

import locale
import plotly.express as px

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


def afficher_episodes(episodes_df):
    st.write("### Épisodes")
    st.write("Liste des épisodes du Masque et la Plume.")
    print_episodes_info(episodes_df)
    # Ajoutez ici le code pour afficher les épisodes
    st.dataframe(episodes_df, use_container_width=True)


def afficher_un_episode(episodes_df):
    # Widget de sélection de date
    selected_date = st.selectbox("Sélectionnez un épisode", episodes_df["date"])

    # Filtrer le DataFrame pour trouver la ligne correspondant à la date sélectionnée
    episode = episodes_df[episodes_df["date"] == selected_date]

    if not episode.empty:
        episode = episode.iloc[0]
        st.write(f"### {episode['titre']}")
        selected_date_dt = datetime.strptime(selected_date, "%Y/%m/%d")
        st.write(f"**Date**: {selected_date_dt.strftime(DATE_FORMAT)}")

        st.write(f"**Durée**: {episode['duree (min)']} minutes")
        st.write(f"**Description**: {episode['description']}")
        st.write(f"**Transcription**: {episode['transcription']}")
    else:
        st.write("Aucun épisode trouvé pour cette date.")


def nb_mots_transcription(episodes_df):

    st.write("### Nombre de mots par transcription")
    # Compter le nombre de mots dans chaque transcription

    episodes_df = episodes_df.copy()

    # Calculer le nombre de mots par minute
    episodes_df["mots_par_minute"] = (
        episodes_df["transcription"].apply(lambda x: len(x.split()))
        / episodes_df["duree (min)"]
    )

    # Transformer la date en format dd/mm/yyyy
    episodes_df["date_formatted"] = episodes_df["date"].apply(
        lambda x: datetime.strptime(x, "%Y/%m/%d")
    )
    episodes_df["date_formatted"] = episodes_df["date_formatted"].apply(
        lambda x: x.strftime("%d/%m/%Y")
    )

    # Trier les données par nombre de mots par minute décroissant
    episodes_df = episodes_df.sort_values(by="mots_par_minute", ascending=False)

    # Créer le graphique interactif
    fig = px.bar(
        episodes_df,
        x="date_formatted",
        y="mots_par_minute",
        custom_data=["date_formatted", "titre", "mots_par_minute", "duree (min)"],
        labels={"mots_par_minute": "Mots par Minute"},
        title="Nombre de Mots par Minute par Épisode",
    )

    # # Mettre à jour les informations de survol
    fig.update_traces(
        hovertemplate="<b>Date:</b> %{customdata[0]}<br><b>Titre:</b> %{customdata[1]}<br><b>Mots par Minute:</b> %{customdata[2]:.1f}<br><b>Duree en Minute:</b> %{customdata[3]:.1f}"
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


# Sidebar pour la navigation
option = st.sidebar.selectbox(
    "Options",
    ["Tous les épisodes", "Visualiser un épisode", "# mots par transcription"],
)

episodes_df = get_episodes()
# Afficher le contenu en fonction de la sélection
if option == "Tous les épisodes":
    afficher_episodes(episodes_df)
elif option == "Visualiser un épisode":
    afficher_un_episode(episodes_df)
elif option == "# mots par transcription":
    nb_mots_transcription(episodes_df)
