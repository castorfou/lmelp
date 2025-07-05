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
from llm import get_gemini_llm
import pandas as pd
import locale

# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

st.title("📝 Avis Critiques")
st.write("Générez des résumés d'avis critiques à partir des transcriptions d'épisodes")


@st.cache_data
def get_episodes_with_transcriptions():
    """Récupère les épisodes qui ont des transcriptions disponibles"""
    episodes = Episodes()
    episodes.get_entries()

    episodes_with_transcriptions = []
    for oid in episodes.oid_episodes:
        episode = Episode.from_oid(oid)
        if hasattr(episode, "whisper") and episode.whisper:
            episodes_with_transcriptions.append(
                {
                    "oid": str(oid),
                    "titre": episode.title,
                    "date": episode.date,
                    "description": (
                        episode.description[:100] + "..."
                        if len(episode.description) > 100
                        else episode.description
                    ),
                }
            )

    return pd.DataFrame(episodes_with_transcriptions)


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

    model = get_gemini_llm()
    response = model.generate_content(prompt)
    return response.text


# Interface principale
try:
    episodes_df = get_episodes_with_transcriptions()

    if episodes_df.empty:
        st.warning("Aucun épisode avec transcription disponible")
        st.info(
            "Veuillez d'abord générer des transcriptions pour les épisodes sur la page d'accueil"
        )
    else:
        st.success(f"{len(episodes_df)} épisodes avec transcriptions disponibles")

        # Sélection de l'épisode
        st.subheader("Sélectionner un épisode")

        # Tri par date décroissante
        episodes_df = episodes_df.sort_values("date", ascending=False)

        # Affichage des épisodes pour sélection
        selected_episode = st.selectbox(
            "Choisir un épisode:",
            episodes_df.index,
            format_func=lambda x: f"{episodes_df.loc[x, 'date'].strftime('%d/%m/%Y')} - {episodes_df.loc[x, 'titre']}",
        )

        if selected_episode is not None:
            episode_info = episodes_df.loc[selected_episode]

            # Affichage des informations de l'épisode sélectionné
            st.write("### Épisode sélectionné")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Date:** {episode_info['date'].strftime('%d %B %Y')}")
                st.write(f"**Titre:** {episode_info['titre']}")
            with col2:
                st.write(f"**Description:** {episode_info['description']}")

            # Bouton pour générer le résumé
            if st.button("🚀 Générer le résumé des avis critiques", type="primary"):
                with st.spinner(
                    "Génération du résumé en cours... Cela peut prendre quelques minutes."
                ):
                    try:
                        # Récupération de la transcription complète
                        episode = Episode.from_oid(episode_info["oid"])
                        transcription = episode.whisper

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
                                file_name=f"avis_critiques_{episode_info['date'].strftime('%Y%m%d')}_{episode_info['titre'][:50]}.md",
                                mime="text/markdown",
                            )

                    except Exception as e:
                        st.error(f"Erreur lors de la génération du résumé: {str(e)}")
                        st.info(
                            "Vérifiez que la clé API Gemini est correctement configurée dans votre fichier .env"
                        )

except Exception as e:
    st.error(f"Erreur lors du chargement des épisodes: {str(e)}")
    st.info("Vérifiez que la base de données MongoDB est accessible")
