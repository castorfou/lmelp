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


afficher_episodes()
