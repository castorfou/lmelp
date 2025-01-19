import streamlit as st
from git import Repo
import os
import sys


def get_git_root(path):
    git_repo = Repo(path, search_parent_directories=True)
    return git_repo.git.rev_parse("--show-toplevel")


project_root = get_git_root(os.getcwd())

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(project_root, "nbs")))

from mongo_episode import Episodes
import pandas as pd


@st.cache_data  # 👈 Add the caching decorator
def get_episodes():
    episodes = Episodes()
    episodes_df = pd.DataFrame(
        [episode.to_dict() for episode in episodes.get_entries()]
    )
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


afficher_episodes()
