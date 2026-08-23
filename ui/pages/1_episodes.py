import os
import sys
from pathlib import Path

import streamlit as st


sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path


add_to_sys_path()

import locale

import pandas as pd
import plotly.express as px
from bson import ObjectId
from mongo_episode import Episode, Episodes


# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
from date_utils import format_date


@st.cache_data  # 👈 Add the caching decorator
def get_episodes():
    episodes = Episodes()
    episodes.get_entries()
    all_episodes = [Episode.from_oid(oid) for oid in episodes.oid_episodes]
    # Créer le DataFrame avec les données des épisodes
    episodes_data = []
    for i, episode in enumerate(all_episodes):
        data = episode.to_dict()
        data["_id"] = str(episodes.oid_episodes[i])  # Ajouter l'OID
        episodes_data.append(data)

    episodes_df = pd.DataFrame(episodes_data)
    episodes_df["duree (min)"] = (episodes_df["duree"] / 60).round(1)
    episodes_df.drop(
        columns=["url_telechargement", "type", "duree"],
        inplace=True,
    )
    return episodes_df


@st.cache_data  # 👈 Add the caching decorator
def print_episodes_info(episodes_df):
    st.write("### Informations sur les épisodes")
    st.write(f"{episodes_df.shape[0]} épisodes")
    st.write(
        f"{format_date(episodes_df['date'].min())} - {format_date(episodes_df['date'].max())}"
    )
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
    episodes_df = episodes_df.copy()
    episodes_df["date"] = episodes_df["date"].apply(lambda x: format_date(x))
    st.dataframe(episodes_df, width="stretch")


def afficher_un_episode(episodes_df):
    # Widget de sélection de date
    episodes_df = episodes_df.copy()
    episodes_df["date"] = episodes_df["date"].apply(lambda x: format_date(x))
    episodes_df["selecteur"] = (
        episodes_df["date"] + " - " + episodes_df["titre"].str[:100]
    )
    selected = st.selectbox("Sélectionnez un épisode", episodes_df["selecteur"])

    # Filtrer le DataFrame pour trouver la ligne correspondant à la date sélectionnée
    episode_row = episodes_df[episodes_df["selecteur"] == selected]

    if not episode_row.empty:
        episode_data = episode_row.iloc[0]
        st.write(f"### {episode_data['titre']}")
        st.write(f"**Date**: {episode_data['date']}")
        st.write(f"**Durée**: {episode_data['duree (min)']} minutes")
        st.write(f"**Description**: {episode_data['description']}")

        # Afficher la transcription si elle existe
        if pd.notna(episode_data["transcription"]) and episode_data["transcription"]:
            # Bouton pour relancer la transcription (AVANT la transcription)
            if st.button(
                "🔄 Relancer la transcription",
                key="relaunch_transcription",
                type="primary",
            ):
                with st.spinner("Suppression de la transcription et du cache..."):
                    # Récupérer l'objet Episode complet
                    episode = Episode.from_oid(ObjectId(episode_data["_id"]))

                    # Supprimer la transcription de la DB
                    episode.collection.update_one(
                        {"_id": episode.get_oid()},
                        {"$unset": {"transcription": "", "whisper": ""}},
                    )

                    # Supprimer le fichier cache si existe
                    from mongo_episode import AUDIO_PATH, get_audio_path

                    mp3_fullfilename = (
                        get_audio_path(AUDIO_PATH, year="") + episode.audio_rel_filename
                    )
                    cache_transcription_filename = (
                        f"{os.path.splitext(mp3_fullfilename)[0]}.txt"
                    )
                    if os.path.exists(cache_transcription_filename):
                        os.remove(cache_transcription_filename)
                        st.success(f"Cache supprimé: {cache_transcription_filename}")

                with st.status("Transcription PGX en cours…", expanded=True) as status:
                    # Relancer la transcription
                    episode.transcription = None  # Réinitialiser l'attribut
                    episode.set_transcription(
                        verbose=True, on_progress=lambda msg: st.write(msg)
                    )
                    if episode.transcription:
                        status.update(label="Transcription terminée", state="complete")
                        st.success("✅ Transcription terminée avec succès!")
                        st.rerun()
                    else:
                        status.update(label="Échec de la transcription", state="error")
                        st.error(
                            "❌ La transcription a échoué — voir le détail ci-dessus."
                        )

            # Afficher la transcription dans un expander pour ne pas prendre trop de place
            with st.expander("📝 Voir la transcription", expanded=False):
                st.write(episode_data["transcription"])
        else:
            st.warning("⚠️ Aucune transcription disponible pour cet épisode")

            # Bouton pour lancer la transcription
            if st.button("▶️ Lancer la transcription", key="launch_transcription"):
                with st.status("Transcription PGX en cours…", expanded=True) as status:
                    episode = Episode.from_oid(ObjectId(episode_data["_id"]))
                    episode.set_transcription(
                        verbose=True, on_progress=lambda msg: st.write(msg)
                    )
                    if episode.transcription:
                        status.update(label="Transcription terminée", state="complete")
                        st.success("✅ Transcription terminée avec succès!")
                        st.rerun()
                    else:
                        status.update(label="Échec de la transcription", state="error")
                        st.error(
                            "❌ La transcription a échoué — voir le détail ci-dessus."
                        )
    else:
        st.write("Aucun épisode trouvé pour cette date.")


def nb_mots_transcription(episodes_df):

    st.write("### Nombre de mots par transcription")
    # Compter le nombre de mots dans chaque transcription

    episodes_df = episodes_df.copy()
    episodes_df["date"] = episodes_df["date"].apply(lambda x: format_date(x))

    # Calculer le nombre de mots par minute
    episodes_df["mots_par_minute"] = (
        episodes_df["transcription"].apply(lambda x: len(x.split()))
        / episodes_df["duree (min)"]
    )

    # Créer le graphique interactif
    fig = px.bar(
        episodes_df,
        x="date",
        y="mots_par_minute",
        custom_data=["date", "titre", "mots_par_minute", "duree (min)"],
        labels={"mots_par_minute": "Mots par Minute"},
        title="Nombre de Mots par Minute par Épisode",
    )

    # # Mettre à jour les informations de survol
    fig.update_traces(
        hovertemplate="<b>Date:</b> %{customdata[0]}<br><b>Titre:</b> %{customdata[1]}<br><b>Mots par Minute:</b> %{customdata[2]:.1f}<br><b>Duree en Minute:</b> %{customdata[3]:.1f}"
    )

    # Afficher le graphique
    st.plotly_chart(fig, width="stretch")


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
