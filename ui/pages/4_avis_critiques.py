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

# Sidebar pour la navigation
view_option = st.sidebar.selectbox(
    "Vue",
    ["Sélectionner un épisode", "Vue d'ensemble des résumés"],
    help="Choisissez comment afficher les épisodes",
)


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


def check_existing_summaries(episodes_df):
    """Vérifie quels épisodes ont déjà des résumés d'avis critiques"""
    try:
        collection = get_collection(collection_name="avis_critiques")

        # Récupérer tous les OIDs d'épisodes qui ont des résumés
        existing_summaries = collection.find({}, {"episode_oid": 1})
        existing_oids = {summary["episode_oid"] for summary in existing_summaries}

        # Ajouter une colonne pour indiquer si un résumé existe
        episodes_df["has_critique_summary"] = (
            episodes_df["oid"].astype(str).isin(existing_oids)
        )

        return episodes_df

    except Exception as e:
        st.warning(f"Impossible de vérifier les résumés existants: {str(e)}")
        # En cas d'erreur, créer une colonne avec False partout
        episodes_df["has_critique_summary"] = False
        return episodes_df


def afficher_selection_episode():
    """Affiche la sélection d'épisode similaire à la page episodes"""
    episodes_df = get_episodes_with_transcriptions()

    if episodes_df.empty:
        st.warning("Aucun épisode avec transcription disponible")
        st.info(
            "Veuillez d'abord générer des transcriptions pour les épisodes sur la page d'accueil"
        )
        return None

    # Vérifier quels épisodes ont déjà des résumés
    episodes_df = check_existing_summaries(episodes_df)

    # Préparer les données pour la sélection
    episodes_df = episodes_df.copy()

    # Trier par date décroissante AVANT de convertir en string
    episodes_df = episodes_df.sort_values("date", ascending=False)

    episodes_df["date"] = episodes_df["date"].apply(lambda x: x.strftime(DATE_FORMAT))

    # Ajouter des indicateurs visuels dans le sélecteur
    def format_episode_selector(row):
        base_text = f"{row['date']} - {row['titre'][:100]}"
        if row["has_critique_summary"]:
            return f"📊 {base_text}"  # Icône pour indiquer qu'un résumé existe
        else:
            return f"📝 {base_text}"  # Icône pour indiquer qu'aucun résumé n'existe

    episodes_df["selecteur"] = episodes_df.apply(format_episode_selector, axis=1)

    # Afficher un résumé des statistiques
    total_episodes = len(episodes_df)
    episodes_with_summaries = episodes_df["has_critique_summary"].sum()
    episodes_without_summaries = total_episodes - episodes_with_summaries

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total épisodes", total_episodes)
    with col2:
        st.metric("📊 Avec résumé", episodes_with_summaries)
    with col3:
        st.metric("📝 Sans résumé", episodes_without_summaries)

    # Légende pour les icônes
    st.caption("📊 = Résumé d'avis critiques disponible | 📝 = Résumé à générer")

    selected = st.selectbox("Sélectionnez un épisode", episodes_df["selecteur"])

    # Filtrer le DataFrame pour trouver la ligne correspondant à la sélection
    episode = episodes_df[episodes_df["selecteur"] == selected]

    if not episode.empty:
        episode = episode.iloc[0]

        # Afficher le titre avec un indicateur visuel
        if episode["has_critique_summary"]:
            st.write(f"### 📊 {episode['titre']}")
            st.success("✅ Un résumé d'avis critiques existe déjà pour cet épisode")
        else:
            st.write(f"### 📝 {episode['titre']}")
            st.info(
                "💡 Aucun résumé d'avis critiques pour cet épisode - vous pouvez en générer un"
            )

        st.write(f"**Date**: {episode['date']}")
        st.write(f"**Durée**: {episode['duree (min)']} minutes")
        st.write(f"**Description**: {episode['description']}")

        # Récupérer l'OID de l'épisode pour le cache
        episode_oid = str(episode["oid"])  # Utiliser l'OID de la colonne

        # Initialiser la variable de session pour la régénération
        if "regenerating" not in st.session_state:
            st.session_state.regenerating = False

        # Vérifier si un résumé existe déjà dans le cache
        cached_summary = get_summary_from_cache(episode_oid)

        # Bouton pour regénérer le résumé (affiché en premier si un résumé existe)
        regenerate_clicked = False
        if cached_summary:
            regenerate_clicked = st.button("� Regénérer le résumé", type="secondary")

        # Bouton pour générer le résumé (affiché si pas de résumé en cache)
        generate_clicked = False
        if not cached_summary:
            generate_clicked = st.button(
                "✨ Générer le résumé des avis critiques", type="primary"
            )

        # Traitement des clics de boutons
        if regenerate_clicked or generate_clicked:
            # Créer un container pour le statut
            status_container = st.container()

            with status_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    transcription = episode["transcription"]
                    if not transcription:
                        st.error(
                            "La transcription n'est pas disponible pour cet épisode"
                        )
                    else:
                        # Étape 1: Préparation
                        progress_bar.progress(10)
                        status_text.text("📝 Préparation de la transcription...")

                        # Étape 2: Génération
                        progress_bar.progress(30)
                        status_text.text("🤖 Génération du résumé avec l'IA...")

                        # Génération du résumé
                        summary = generate_critique_summary(transcription)

                        # Étape 3: Sauvegarde
                        progress_bar.progress(80)
                        status_text.text("💾 Sauvegarde dans le cache...")

                        # Sauvegarde dans le cache
                        save_summary_to_cache(
                            episode_oid, episode["titre"], episode["date"], summary
                        )

                        # Étape 4: Finalisation
                        progress_bar.progress(100)
                        status_text.text("✅ Terminé!")

                        # Nettoyer les indicateurs de progression
                        progress_bar.empty()
                        status_text.empty()

                        # Affichage immédiat du nouveau résumé
                        if regenerate_clicked:
                            st.success("✅ Résumé régénéré avec succès!")
                        else:
                            st.success("✅ Résumé généré avec succès!")

                        st.subheader("📊 Résumé des avis critiques")
                        st.markdown(summary, unsafe_allow_html=True)

                except Exception as e:
                    # Nettoyer les indicateurs de progression en cas d'erreur
                    progress_bar.empty()
                    status_text.empty()

                    st.error(f"Erreur lors de la génération du résumé: {str(e)}")
                    st.info(
                        "Vérifiez que la clé API Azure OpenAI est correctement configurée dans votre fichier .env"
                    )

                    # Afficher plus de détails sur l'erreur si c'est un timeout
                    if "timeout" in str(e).lower():
                        st.warning(
                            "⏰ La génération a pris trop de temps. Essayez de nouveau ou contactez l'administrateur."
                        )
                    elif "rate limit" in str(e).lower():
                        st.warning(
                            "🚦 Limite de taux atteinte. Attendez quelques minutes avant de réessayer."
                        )
                    else:
                        st.error(f"Détails de l'erreur: {str(e)}")

                    # Bouton pour réessayer
                    if st.button("🔄 Réessayer", key="retry_button"):
                        st.rerun()

        # Afficher le résumé en cache uniquement si aucun bouton n'a été cliqué
        elif cached_summary:
            st.info(
                f"📄 Résumé existant (généré le {cached_summary['created_at'].strftime('%d %B %Y à %H:%M')})"
            )
            st.subheader("📊 Résumé des avis critiques")
            st.markdown(cached_summary["summary"], unsafe_allow_html=True)
    else:
        st.write("Aucun épisode trouvé pour cette sélection.")

    return episode if not episode.empty else None


def post_process_and_sort_summary(summary_text):
    """Post-traite le résumé pour corriger le tri des notes"""
    import re

    lines = summary_text.split("\n")
    result_lines = []

    # Variables pour capturer les tableaux
    in_main_table = False
    in_coups_table = False
    main_table_lines = []
    coups_table_lines = []
    header_line = None
    separator_line = None

    for line in lines:
        # Détecter le début du tableau principal
        if "1. LIVRES DISCUTÉS AU PROGRAMME" in line:
            in_main_table = True
            in_coups_table = False
            result_lines.append(line)
            continue

        # Détecter le début du tableau coups de cœur
        if (
            "2. COUPS DE COEUR DES CRITIQUES" in line
            or "2. COUPS DE CŒUR DES CRITIQUES" in line
        ):
            in_main_table = False
            in_coups_table = True

            # Traiter le tableau principal avant de passer au suivant
            if main_table_lines:
                sorted_main = sort_table_by_rating(
                    main_table_lines, header_line, separator_line
                )
                result_lines.extend(sorted_main)
                main_table_lines = []
                header_line = None
                separator_line = None

            result_lines.append(line)
            continue

        # Si on est dans un tableau
        if in_main_table or in_coups_table:
            # Détecter l'en-tête du tableau (contient "Auteur" et "Titre")
            if "Auteur" in line and "Titre" in line and not header_line:
                header_line = line
                continue

            # Détecter la ligne de séparation (contient des tirets)
            elif "---" in line or "|-" in line:
                separator_line = line
                continue

            # Si c'est une ligne de données du tableau (contient des notes colorées)
            elif re.search(r"<span[^>]*>(\d+\.?\d*)</span>", line):
                if in_main_table:
                    main_table_lines.append(line)
                else:
                    coups_table_lines.append(line)
                continue

        # Pour toutes les autres lignes, les ajouter directement
        result_lines.append(line)

    # Traiter le dernier tableau (coups de cœur) si il existe
    if coups_table_lines:
        sorted_coups = sort_table_by_rating(
            coups_table_lines, header_line, separator_line
        )
        result_lines.extend(sorted_coups)

    return "\n".join(result_lines)


def sort_table_by_rating(table_lines, header_line, separator_line):
    """Trie les lignes d'un tableau par note décroissante"""
    import re

    # Extraire les notes et associer aux lignes
    lines_with_ratings = []

    for line in table_lines:
        # Chercher la note dans les spans HTML
        rating_match = re.search(r"<span[^>]*>(\d+\.?\d*)</span>", line)
        if rating_match:
            rating = float(rating_match.group(1))
            lines_with_ratings.append((rating, line))

    # Trier par note décroissante
    lines_with_ratings.sort(key=lambda x: x[0], reverse=True)

    # Reconstruire le tableau
    result = []
    if header_line:
        result.append("")  # Ligne vide avant le tableau
        result.append(header_line)
    if separator_line:
        result.append(separator_line)

    # Ajouter les lignes triées
    for rating, line in lines_with_ratings:
        result.append(line)

    return result


def generate_critique_summary(transcription):
    """Génère un résumé des avis critiques à partir d'une transcription"""

    # Limiter la taille de la transcription si elle est trop longue
    max_chars = 50000  # Limite pour éviter les timeouts
    if len(transcription) > max_chars:
        transcription = transcription[:max_chars] + "... [transcription tronquée]"
        st.warning(
            f"⚠️ Transcription tronquée à {max_chars} caractères pour éviter les timeouts"
        )

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

Pour la colonne "Note moyenne", utilise un code couleur HTML avec un fond coloré selon cette échelle :
- 9.0-10.0 : <span style="background-color: #00C851; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (vert foncé)
- 8.0-8.9 : <span style="background-color: #4CAF50; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (vert)
- 7.0-7.9 : <span style="background-color: #8BC34A; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (vert clair)
- 6.0-6.9 : <span style="background-color: #CDDC39; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (jaune-vert)
- 5.0-5.9 : <span style="background-color: #FFEB3B; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (jaune)
- 4.0-4.9 : <span style="background-color: #FF9800; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (orange)
- 3.0-3.9 : <span style="background-color: #FF5722; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (rouge-orange)
- 1.0-2.9 : <span style="background-color: #F44336; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">NOTE</span> (rouge)

## 2. COUPS DE COEUR DES CRITIQUES
Ce sont les livres mentionnés rapidement par un seul critique comme recommandation personnelle, souvent en fin d'émission.

Pour ces livres, affiche seulement :
- Auteur
- Titre
- Éditeur (si mentionné)
- Critique qui le recommande
- Sa note (entre 8 et 10, car c'est un coup de coeur)

Applique le même code couleur pour la colonne Note que ci-dessus.

Tu me restitueras ces 2 listes sous la forme de 2 tableaux séparés au format markdown avec le HTML pour les couleurs.

Ne genere pas de code python, juste les 2 tableaux markdown avec leurs titres respectifs et le code couleur HTML.
"""

    try:
        # Utiliser Azure OpenAI avec timeout configuré dans llm.py (120 secondes)
        model = get_azure_llm()
        st.info("🔧 Utilisation du timeout Azure OpenAI (120 secondes)")
        response = model.complete(prompt)

        # Post-traiter pour corriger le tri
        st.info("🔄 Correction automatique du tri des notes...")
        sorted_summary = post_process_and_sort_summary(response.text)

        return sorted_summary

    except Exception as e:
        error_msg = str(e).lower()
        st.error(f"Erreur lors de la génération avec l'IA: {str(e)}")

        # Ajouter plus de détails sur l'erreur
        if "timeout" in error_msg or "timed out" in error_msg:
            st.warning("⏰ Timeout: La génération a pris trop de temps (>120 secondes)")
            st.info("💡 Essayez avec un épisode plus court ou réessayez plus tard")
        elif "rate limit" in error_msg:
            st.warning(
                "🚦 Limite de taux atteinte. Attendez quelques minutes avant de réessayer."
            )
        elif "invalid request" in error_msg:
            st.warning(
                "📝 Requête invalide. La transcription est peut-être trop longue."
            )
        elif "connection" in error_msg:
            st.warning("🌐 Problème de connexion. Vérifiez votre connexion internet.")
        elif "unauthorized" in error_msg or "api key" in error_msg:
            st.warning(
                "🔑 Problème d'authentification. Vérifiez votre clé API Azure OpenAI."
            )
        else:
            st.error(f"Détails techniques: {str(e)}")

        raise e


# Interface principale
try:
    afficher_selection_episode()
except Exception as e:
    st.error(f"Erreur lors du chargement des épisodes: {str(e)}")
    st.info("Vérifiez que la base de données MongoDB est accessible")
