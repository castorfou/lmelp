import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path

add_to_sys_path()

st.set_page_config(
    page_title="le masque et la plume - avis critiques",
    page_icon=":material/rate_review:",
    layout="wide",
    initial_sidebar_state="auto",
)

from mongo_episode import Episodes, Episode
from llm import get_azure_llm
from mongo import get_collection
import pandas as pd
import locale
from datetime import datetime
from bson import ObjectId

# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

st.title("📝 Avis Critiques")
st.write("Générez des résumés d'avis critiques à partir des transcriptions d'épisodes")


DATE_FORMAT = "%d %b %Y"


def get_summary_from_cache(episode_oid):
    """Récupère un résumé existant depuis MongoDB"""
    try:
        collection = get_collection(collection_name="avis_critiques")
        cached_summary = collection.find_one({"episode_oid": episode_oid})
        return cached_summary
    except Exception as e:
        st.error(f"Erreur lors de la récupération du cache: {str(e)}")
        return None


def save_summary_to_cache(episode_oid, episode_title, episode_date, summary):
    """Sauvegarde un résumé dans MongoDB"""
    try:
        collection = get_collection(collection_name="avis_critiques")

        # Supprimer l'ancien résumé s'il existe
        collection.delete_one({"episode_oid": episode_oid})

        # Insérer le nouveau résumé
        summary_doc = {
            "episode_oid": episode_oid,
            "episode_title": episode_title,
            "episode_date": episode_date,
            "summary": summary,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        collection.insert_one(summary_doc)
        st.success("Résumé sauvegardé dans le cache!")

    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du cache: {str(e)}")


@st.cache_data
def get_episodes_with_transcriptions():
    """Récupère tous les épisodes et filtre ceux qui ont des transcriptions"""
    episodes = Episodes()
    episodes.get_entries()
    all_episodes = [Episode.from_oid(oid) for oid in episodes.oid_episodes]
    episodes_df = pd.DataFrame([episode.to_dict() for episode in all_episodes])
    episodes_df["duree (min)"] = (episodes_df["duree"] / 60).round(1)

    # Ajouter les OIDs comme colonne
    episodes_df["oid"] = episodes.oid_episodes

    # Filtrer seulement les épisodes avec transcriptions
    episodes_with_transcriptions = episodes_df[
        episodes_df["transcription"].notna()
    ].copy()

    return episodes_with_transcriptions


def afficher_selection_episode():
    """Affiche la sélection d'épisode similaire à la page episodes"""
    episodes_df = get_episodes_with_transcriptions()

    if episodes_df.empty:
        st.warning("Aucun épisode avec transcription disponible")
        st.info(
            "Veuillez d'abord générer des transcriptions pour les épisodes sur la page d'accueil"
        )
        return None

    # Préparer les données pour la sélection
    episodes_df = episodes_df.copy()

    # Trier par date décroissante AVANT de convertir en string
    episodes_df = episodes_df.sort_values("date", ascending=False)

    episodes_df["date"] = episodes_df["date"].apply(lambda x: x.strftime(DATE_FORMAT))
    episodes_df["selecteur"] = (
        episodes_df["date"] + " - " + episodes_df["titre"].str[:100]
    )

    st.success(f"{len(episodes_df)} épisodes avec transcriptions disponibles")

    selected = st.selectbox("Sélectionnez un épisode", episodes_df["selecteur"])

    # Filtrer le DataFrame pour trouver la ligne correspondant à la sélection
    episode = episodes_df[episodes_df["selecteur"] == selected]

    if not episode.empty:
        episode = episode.iloc[0]
        st.write(f"### {episode['titre']}")
        st.write(f"**Date**: {episode['date']}")
        st.write(f"**Durée**: {episode['duree (min)']} minutes")
        st.write(f"**Description**: {episode['description']}")

        # Récupérer l'OID de l'épisode pour le cache
        episode_oid = str(episode["oid"])  # Utiliser l'OID de la colonne

        # Vérifier si un résumé existe déjà dans le cache
        cached_summary = get_summary_from_cache(episode_oid)

        if cached_summary:
            # Afficher le résumé en cache
            st.info(
                f"� Résumé existant (généré le {cached_summary['created_at'].strftime('%d %B %Y à %H:%M')})"
            )
            st.subheader("📊 Résumé des avis critiques")
            st.markdown(cached_summary["summary"])

            # Bouton pour regénérer le résumé
            if st.button("🔄 Regénérer le résumé", type="secondary"):
                with st.spinner(
                    "Régénération du résumé en cours... Cela peut prendre quelques minutes."
                ):
                    try:
                        transcription = episode["transcription"]
                        if not transcription:
                            st.error(
                                "La transcription n'est pas disponible pour cet épisode"
                            )
                        else:
                            # Génération du nouveau résumé
                            summary = generate_critique_summary(transcription)

                            # Sauvegarde dans le cache
                            save_summary_to_cache(
                                episode_oid, episode["titre"], episode["date"], summary
                            )

                            # Affichage du nouveau résumé
                            st.subheader("📊 Nouveau résumé des avis critiques")
                            st.markdown(summary)

                    except Exception as e:
                        st.error(f"Erreur lors de la régénération du résumé: {str(e)}")
                        st.info(
                            "Vérifiez que la clé API Azure OpenAI est correctement configurée dans votre fichier .env"
                        )
        else:
            # Pas de résumé en cache, afficher le bouton pour générer
            if st.button("� Générer le résumé des avis critiques", type="primary"):
                with st.spinner(
                    "Génération du résumé en cours... Cela peut prendre quelques minutes."
                ):
                    try:
                        transcription = episode["transcription"]
                        if not transcription:
                            st.error(
                                "La transcription n'est pas disponible pour cet épisode"
                            )
                        else:
                            # Génération du résumé
                            summary = generate_critique_summary(transcription)

                            # Sauvegarde dans le cache
                            save_summary_to_cache(
                                episode_oid, episode["titre"], episode["date"], summary
                            )

                            # Affichage du résumé
                            st.subheader("📊 Résumé des avis critiques")
                            st.markdown(summary)

                    except Exception as e:
                        st.error(f"Erreur lors de la génération du résumé: {str(e)}")
                        st.info(
                            "Vérifiez que la clé API Azure OpenAI est correctement configurée dans votre fichier .env"
                        )
    else:
        st.write("Aucun épisode trouvé pour cette sélection.")

    return episode if not episode.empty else None


def generate_critique_summary(transcription):
    """Génère un résumé des avis critiques à partir d'une transcription"""

    prompt = f"""
Je vais te donner la transcription d'un episode d'une emission de radio qui s'appelle le masque et la plume sur France Inter.
Cet episode dure 1h et porte sur des livres. Il y a des intervenants qui parlent des livres qu'ils ont lus. Ils ne sont parfois pas d'accord.

Voici la transcription:
{transcription}

Je veux que tu identifies l'ensemble des livres dont on parle dans cette emission et que tu les sépares en 2 catégories :

## 1. LIVRES DISCUTÉS AU PROGRAMME
Ce sont les livres qui font l'objet de discussions approfondies entre plusieurs critiques.

Pour ces livres, je veux que tu me restitues cette liste en separant auteur et titre. Si l'editeur est mentionne tu peux aussi le noter.

Concernant les avis des critiques, je veux que tu en fasses une forme de synthese en donnant une note de 1 à 10 (1 etant la note la plus basse et 10 la note la plus haute) utilisant les regles suivantes:
- la note 1 est vraiment pour les livres a eviter, les purges
- la note 10 est pour les livres a lire absolument, les chefs d'oeuvre
- la note 9 est pour les livres excellents, 
- la note 5 est pour les livres moyens, sans plus. pas horrible mais pas genial non plus
- les notations seront assez severes, ne garde la note 10 vraiment que pour les chefs d'oeuvre
- si un seul critique donne son avis, tu prendras sa note
- si plusieurs critiques se prononcent, tu prendras la moyenne de leurs notes

Je veux que tu conserves l'avis de chaque critique avec son prenom et son nom.
et que tu donnes la note moyenne obtenue pour chaque livre.
tu rajouteras une colonne pour dire le nombre de critiques qui ont donne leur avis sur le livre.
Puis si un des critiques a vraiment adore le livre (ce qui correspond a une note de 9 ou 10), tu mentionneras les noms des critiques dans une colonne "coup de coeur" a part.
Enfin si un des critiques fait etat d'un chef d'oeuvre (note 10), tu mentionneras cela dans une colonne "chef d'oeuvre" a part.

## 2. COUPS DE COEUR DES CRITIQUES
Ce sont les livres mentionnés rapidement par un seul critique comme recommandation personnelle, souvent en fin d'émission.

Pour ces livres, affiche seulement :
- Auteur
- Titre
- Éditeur (si mentionné)
- Critique qui le recommande
- Sa note (entre 8 et 10, car c'est un coup de coeur)

Tu me restitueras ces 2 listes sous la forme de 2 tableaux séparés au format markdown.

Ne genere pas de code python, juste les 2 tableaux markdown avec leurs titres respectifs.
"""

    model = get_azure_llm()
    response = model.complete(prompt)
    return response.text


# Interface principale
try:
    afficher_selection_episode()
except Exception as e:
    st.error(f"Erreur lors du chargement des épisodes: {str(e)}")
    st.info("Vérifiez que la base de données MongoDB est accessible")
