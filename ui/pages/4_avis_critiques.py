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
import pandas as pd
import locale

# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

st.title("📝 Avis Critiques")
st.write("Générez des résumés d'avis critiques à partir des transcriptions d'épisodes")


DATE_FORMAT = "%d %b %Y"


@st.cache_data
def get_episodes_with_transcriptions():
    """Récupère tous les épisodes et filtre ceux qui ont des transcriptions"""
    episodes = Episodes()
    episodes.get_entries()
    all_episodes = [Episode.from_oid(oid) for oid in episodes.oid_episodes]
    episodes_df = pd.DataFrame([episode.to_dict() for episode in all_episodes])
    episodes_df["duree (min)"] = (episodes_df["duree"] / 60).round(1)

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

        # Bouton pour générer le résumé
        if st.button("🚀 Générer le résumé des avis critiques", type="primary"):
            with st.spinner(
                "Génération du résumé en cours... Cela peut prendre quelques minutes."
            ):
                try:
                    # Récupération de la transcription complète
                    transcription = episode["transcription"]

                    if not transcription:
                        st.error(
                            "La transcription n'est pas disponible pour cet épisode"
                        )
                    else:
                        # Génération du résumé
                        summary = generate_critique_summary(transcription)

                        # Affichage du résumé
                        st.subheader("📊 Résumé des avis critiques")
                        st.markdown(summary)

                        # Option pour télécharger le résumé
                        st.download_button(
                            label="💾 Télécharger le résumé",
                            data=summary,
                            file_name=f"avis_critiques_{episode['date'].replace(' ', '_')}_{episode['titre'][:50]}.md",
                            mime="text/markdown",
                        )

                except Exception as e:
                    st.error(f"Erreur lors de la génération du résumé: {str(e)}")
                    st.info(
                        "Vérifiez que la clé API Gemini est correctement configurée dans votre fichier .env"
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

Je veux que tu identifies l'ensemble des livres dont on parle dans cette emission.
Et que tu me restitues cette liste de livres en separant auteur et titre. Si l'editeur est mentionne tu peux aussi le noter.

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
Tu me restitueras cette liste sous la forme d'un tableau au format markdown.

Ne genere pas de code python, juste le tableau markdown.
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
