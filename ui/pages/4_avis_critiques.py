import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ui_tools import add_to_sys_path

add_to_sys_path()

st.set_page_config(
    page_title="le masque et la plume - avis critiques",
    page_icon=":material/rate_review:",
    layout="wide",
    initial_sidebar_state="auto",
)

import locale
import re
from datetime import datetime

import pandas as pd
from bson import ObjectId
from config import get_DB_VARS
from date_utils import DATE_FORMAT, format_date
from llm import get_azure_llm
from mongo import get_collection
from mongo_episode import Episode, Episodes

# Définir la locale en français
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

st.title("📝 Avis Critiques")
st.write("Générez des résumés d'avis critiques à partir des transcriptions d'épisodes")

# Afficher la date actuelle pour les captures d'écran
from datetime import datetime

current_date = format_date(datetime.now(), "%d %B %Y")
st.caption(f"📅 {current_date}")


def get_summary_from_cache(episode_oid):
    """Récupère un résumé existant depuis MongoDB"""
    try:
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        collection = get_collection(target_db=DB_HOST, client_name=DB_NAME, collection_name="avis_critiques")
        cached_summary = collection.find_one({"episode_oid": episode_oid})
        return cached_summary
    except Exception as e:
        st.error(f"Impossible de vérifier les résumés existants: {str(e)}")
        return None


def is_summary_truncated(summary_text):
    """Vérifie si un résumé semble tronqué et ne devrait pas être sauvegardé"""
    if not summary_text or isinstance(summary_text, str) and summary_text.strip() == "":
        return True

    # Vérifier si c'est le message d'erreur pour résumé tronqué
    if "Réponse de l'IA tronquée. Veuillez réessayer." in summary_text:
        return True

    # Vérifier la longueur minimale (réduite car un résumé avec un seul livre peut être court)
    if len(summary_text) < 200:
        return True

    # Vérifier les fins brutales typiques de troncature (mais pas le pipe seul qui peut être normal)
    if (
        summary_text.endswith("**")
        or summary_text.endswith("→")
        or summary_text.endswith("...")
    ):
        return True

    # Vérifier qu'il y a au moins un titre de section
    if "## 1." not in summary_text:
        return True

    # Vérifier que le résumé se termine correctement (pas au milieu d'un tableau)
    lines = summary_text.strip().split("\n")
    last_non_empty_line = ""
    for line in reversed(lines):
        if line.strip():
            last_non_empty_line = line.strip()
            break

    # Si la dernière ligne est une ligne de tableau incomplète (moins de 3 pipes OU juste des pipes sans contenu)
    if last_non_empty_line.startswith("|"):
        # Compter les segments entre les pipes
        segments = last_non_empty_line.split("|")
        # Filtrer les segments vides (au début et à la fin)
        non_empty_segments = [seg.strip() for seg in segments if seg.strip()]

        # Si il y a moins de 2 colonnes avec du contenu, c'est probablement tronqué
        if len(non_empty_segments) < 2:
            return True

        # Si la ligne se termine bizarrement (par exemple juste "|" ou "| |")
        if last_non_empty_line.strip() in ["|", "| |", "||"]:
            return True

    return False


def debug_truncation_detection(summary_text):
    """Fonction de débogage pour comprendre pourquoi un résumé est considéré comme tronqué"""
    debug_info = []

    if not summary_text or isinstance(summary_text, str) and summary_text.strip() == "":
        debug_info.append("❌ Résumé vide ou None")
        return debug_info

    debug_info.append(f"📏 Longueur: {len(summary_text)} caractères")

    # Vérifier le message d'erreur
    if "Réponse de l'IA tronquée. Veuillez réessayer." in summary_text:
        debug_info.append("❌ Contient le message d'erreur de troncature")

    # Vérifier la longueur minimale
    if len(summary_text) < 200:
        debug_info.append("❌ Trop court (< 200 caractères)")
    else:
        debug_info.append("✅ Longueur suffisante")

    # Vérifier les fins brutales
    endings = []
    if summary_text.endswith("**"):
        endings.append("**")
    if summary_text.endswith("→"):
        endings.append("→")
    if summary_text.endswith("..."):
        endings.append("...")

    if endings:
        debug_info.append(f"❌ Se termine par: {', '.join(endings)}")
    else:
        debug_info.append("✅ Fin normale")

    # Vérifier la structure
    if "## 1." not in summary_text:
        debug_info.append("❌ Pas de titre de section '## 1.'")
    else:
        debug_info.append("✅ Contient un titre de section")

    # Analyser la dernière ligne
    lines = summary_text.strip().split("\n")
    last_non_empty_line = ""
    for line in reversed(lines):
        if line.strip():
            last_non_empty_line = line.strip()
            break

    debug_info.append(f"🔍 Dernière ligne: '{last_non_empty_line[:100]}...'")

    if last_non_empty_line.startswith("|"):
        segments = last_non_empty_line.split("|")
        non_empty_segments = [seg.strip() for seg in segments if seg.strip()]
        debug_info.append(f"📊 Segments du tableau: {len(non_empty_segments)} colonnes")

        if len(non_empty_segments) < 2:
            debug_info.append("❌ Tableau incomplet (< 2 colonnes)")
        else:
            debug_info.append("✅ Tableau semble complet")

        if last_non_empty_line.strip() in ["|", "| |", "||"]:
            debug_info.append("❌ Ligne de tableau vide/malformée")
    else:
        debug_info.append("✅ Ne se termine pas par une ligne de tableau")

    return debug_info


def save_summary_to_cache(episode_oid, episode_title, episode_date, summary):
    """Sauvegarde un résumé dans MongoDB seulement s'il n'est pas tronqué"""
    try:
        # Vérifier si le résumé est tronqué avant de le sauvegarder
        if is_summary_truncated(summary):
            st.warning(
                "⚠️ Résumé tronqué détecté - sauvegarde annulée pour préserver la qualité des données"
            )

            # Afficher les détails de débogage
            debug_info = debug_truncation_detection(summary)
            with st.expander("🔍 Détails de la détection (cliquez pour déboguer)"):
                for info in debug_info:
                    st.write(info)

            st.info(
                "💡 Le résumé ne sera pas sauvegardé dans la base de données. Réessayez pour obtenir un résumé complet."
            )
            return False

        DB_HOST, DB_NAME, _ = get_DB_VARS()
        collection = get_collection(target_db=DB_HOST, client_name=DB_NAME, collection_name="avis_critiques")

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
        st.success("✅ Résumé complet sauvegardé dans le cache!")
        return True

    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du cache: {str(e)}")
        return False


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
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        collection = get_collection(target_db=DB_HOST, client_name=DB_NAME, collection_name="avis_critiques")

        # Récupérer tous les OIDs d'épisodes qui ont des résumés
        existing_summaries = collection.find({}, {"episode_oid": 1})
        existing_oids = {summary["episode_oid"] for summary in existing_summaries}

        # Ajouter une colonne pour indiquer si un résumé existe
        episodes_df_copy = episodes_df.copy()
        episodes_df_copy["has_critique_summary"] = (
            episodes_df_copy["oid"].astype(str).isin(existing_oids)
        )

        return episodes_df_copy

    except Exception as e:
        st.warning(f"Impossible de vérifier les résumés existants: {str(e)}")
        # En cas d'erreur, créer une colonne avec False partout
        episodes_df_copy = episodes_df.copy()
        episodes_df_copy["has_critique_summary"] = False
        return episodes_df_copy


def afficher_selection_episode():
    """Affiche la sélection d'épisode similaire à la page episodes"""
    episodes_df = get_episodes_with_transcriptions()

    if episodes_df.empty:
        st.warning("Aucun épisode avec transcription disponible")
        st.info(
            "Veuillez d'abord générer des transcriptions pour les épisodes sur la page d'accueil"
        )
        return None

    # Vérifier quels épisodes ont déjà des résumés (toujours en temps réel)
    episodes_df = check_existing_summaries(episodes_df)

    # Préparer les données pour la sélection
    episodes_df = episodes_df.copy()

    # Trier par date décroissante AVANT de convertir en string
    # Reset index pour que l'index corresponde aux positions (0, 1, 2, ...)
    episodes_df = episodes_df.sort_values("date", ascending=False).reset_index(drop=True)

    episodes_df["date"] = episodes_df["date"].apply(lambda x: format_date(x))

    # Ajouter des indicateurs visuels dans le sélecteur
    def format_episode_selector(row):
        base_text = f"{row['date']} - {row['titre'][:100]}"
        if row["has_critique_summary"]:
            return f"🟢 {base_text}"  # Icône verte pour indiquer qu'un résumé existe
        else:
            return (
                f"⚪ {base_text}"  # Icône grise pour indiquer qu'aucun résumé n'existe
            )

    episodes_df["selecteur"] = episodes_df.apply(format_episode_selector, axis=1)

    # Afficher un résumé des statistiques
    total_episodes = len(episodes_df)
    episodes_with_summaries = episodes_df["has_critique_summary"].sum()
    episodes_without_summaries = total_episodes - episodes_with_summaries

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total épisodes", total_episodes)
    with col2:
        st.metric("🟢 Avec résumé", episodes_with_summaries)
    with col3:
        st.metric("⚪ Sans résumé", episodes_without_summaries)

    # Légende pour les icônes
    st.caption("🟢 = Résumé d'avis critiques disponible | ⚪ = Résumé à générer")
    st.caption(
        "⌨️ **Navigation clavier** : utilisez les flèches ← → pour naviguer entre les épisodes"
    )

    # Navigation et sélection d'épisode avec alignement vertical
    col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])

    # Initialiser l'index sélectionné dans le session state
    if "selected_episode_index" not in st.session_state:
        st.session_state.selected_episode_index = 0

    # Sélecteur d'épisode (colonne centrale)
    with col_nav2:
        # S'assurer que l'index est dans les limites
        if st.session_state.selected_episode_index >= len(episodes_df):
            st.session_state.selected_episode_index = 0

        selected = st.selectbox(
            "Sélectionnez un épisode",
            episodes_df["selecteur"],
            index=st.session_state.selected_episode_index,
            key="episode_selector",
        )

        # Mettre à jour l'index si l'utilisateur change la sélection manuellement
        # Avec reset_index, l'index correspond directement à la position
        # Convertir explicitement en int Python pour éviter les problèmes avec numpy types
        selected_position = int(episodes_df[episodes_df["selecteur"] == selected].index[0])
        if selected_position != st.session_state.selected_episode_index:
            st.session_state.selected_episode_index = selected_position

    # Boutons de navigation alignés verticalement avec la selectbox
    with col_nav1:
        # Petit espace pour aligner avec le label de la selectbox
        st.write("")
        if st.button(
            "⬅️ Précédent",
            disabled=bool(st.session_state.selected_episode_index >= len(episodes_df) - 1),
            use_container_width=True,
            key="prev_btn",
        ):
            st.session_state.selected_episode_index = int(min(
                len(episodes_df) - 1, st.session_state.selected_episode_index + 1
            ))
            st.rerun()

    with col_nav3:
        # Petit espace pour aligner avec le label de la selectbox
        st.write("")
        if st.button(
            "Suivant ➡️",
            disabled=bool(st.session_state.selected_episode_index == 0),
            use_container_width=True,
            key="next_btn",
        ):
            st.session_state.selected_episode_index = int(max(
                0, st.session_state.selected_episode_index - 1
            ))
            st.rerun()

    # Ajouter la navigation clavier après que les boutons soient créés
    st.components.v1.html(
        """
        <script>
        // Attendre que la page soit complètement chargée
        setTimeout(function() {
            function findButtonByText(text) {
                const buttons = window.parent.document.querySelectorAll('button');
                for (let button of buttons) {
                    if (button.textContent.includes(text)) {
                        return button;
                    }
                }
                return null;
            }

            // Gestionnaire d'événements pour les touches de clavier
            function handleKeyboard(event) {
                // Vérifier que l'utilisateur n'est pas en train de taper dans un champ
                if (event.target.tagName.toLowerCase() === 'input' || 
                    event.target.tagName.toLowerCase() === 'textarea' ||
                    event.target.contentEditable === 'true') {
                    return;
                }
                
                if (event.key === 'ArrowLeft') {
                    event.preventDefault();
                    const prevBtn = findButtonByText('⬅️ Précédent');
                    if (prevBtn && !prevBtn.disabled) {
                        prevBtn.click();
                        showNavigationFeedback('← Précédent');
                    }
                } else if (event.key === 'ArrowRight') {
                    event.preventDefault();
                    const nextBtn = findButtonByText('Suivant ➡️');
                    if (nextBtn && !nextBtn.disabled) {
                        nextBtn.click();
                        showNavigationFeedback('Suivant →');
                    }
                }
            }

            // Afficher un feedback visuel lors de la navigation
            function showNavigationFeedback(text) {
                // Supprimer l'ancien indicateur s'il existe
                const existing = window.parent.document.getElementById('keyboard-nav-indicator');
                if (existing) {
                    existing.remove();
                }

                const indicator = window.parent.document.createElement('div');
                indicator.id = 'keyboard-nav-indicator';
                indicator.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0, 123, 255, 0.9);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    z-index: 9999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    font-size: 14px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    animation: slideIn 0.3s ease-out;
                `;
                indicator.textContent = text;
                
                // Ajouter l'animation CSS
                const style = window.parent.document.createElement('style');
                style.textContent = `
                    @keyframes slideIn {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                `;
                if (!window.parent.document.getElementById('keyboard-nav-styles')) {
                    style.id = 'keyboard-nav-styles';
                    window.parent.document.head.appendChild(style);
                }
                
                window.parent.document.body.appendChild(indicator);
                
                setTimeout(() => {
                    if (indicator.parentNode) {
                        indicator.style.animation = 'slideIn 0.3s ease-out reverse';
                        setTimeout(() => indicator.remove(), 300);
                    }
                }, 1500);
            }

            // Ajouter l'écouteur d'événements
            window.parent.document.addEventListener('keydown', handleKeyboard);
            
        }, 100); // Petit délai pour s'assurer que les boutons sont rendus
        </script>
        """,
        height=0,
    )

    # Filtrer le DataFrame pour trouver la ligne correspondant à la sélection
    episode = episodes_df[episodes_df["selecteur"] == selected]

    if not episode.empty:
        episode = episode.iloc[0]

        # Afficher le titre avec un indicateur visuel
        if episode["has_critique_summary"]:
            st.write(f"### 🟢 {episode['titre']}")
            st.success("✅ Un résumé d'avis critiques existe déjà pour cet épisode")
        else:
            st.write(f"### ⚪ {episode['titre']}")
            st.info(
                "💡 Aucun résumé d'avis critiques pour cet épisode - vous pouvez en générer un"
            )

        st.write(f"**Date**: {episode['date']}")
        st.write(f"**Durée**: {episode['duree (min)']} minutes")
        st.write(f"**Description**: {episode['description']}")

        # Récupérer l'OID de l'épisode pour le cache
        episode_oid = str(episode["oid"])

        # Vérifier si un résumé existe déjà dans le cache
        cached_summary = get_summary_from_cache(episode_oid)

        # Bouton pour regénérer le résumé (affiché en premier si un résumé existe)
        regenerate_clicked = False
        if cached_summary:
            regenerate_clicked = st.button("🔄 Regénérer le résumé", type="secondary")

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

                        # Génération du résumé avec la date de l'épisode
                        summary = generate_critique_summary(
                            transcription, episode["date"]
                        )

                        # Étape 3: Sauvegarde
                        progress_bar.progress(80)
                        status_text.text("💾 Sauvegarde dans le cache...")

                        # Sauvegarde dans le cache seulement si le résumé n'est pas tronqué
                        save_success = save_summary_to_cache(
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
                            if save_success:
                                st.success(
                                    "✅ Résumé régénéré et sauvegardé avec succès!"
                                )
                            else:
                                st.warning(
                                    "⚠️ Résumé régénéré mais non sauvegardé (résumé incomplet)"
                                )
                        else:
                            if save_success:
                                st.success(
                                    "✅ Résumé généré et sauvegardé avec succès!"
                                )
                            else:
                                st.warning(
                                    "⚠️ Résumé généré mais non sauvegardé (résumé incomplet)"
                                )

                        st.subheader("📊 Résumé des avis critiques")
                        st.markdown(summary, unsafe_allow_html=True)

                        # Message approprié selon le statut de sauvegarde
                        if save_success:
                            st.info(
                                "💡 Résumé généré avec succès ! Rechargez la page (F5) pour voir la mise à jour des indicateurs."
                            )
                        else:
                            st.warning(
                                "⚠️ Résumé affiché mais non sauvegardé car il semble incomplet. Réessayez pour obtenir un résumé complet qui sera sauvegardé."
                            )

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
                f"📄 Résumé existant (généré le {format_date(cached_summary['created_at'], '%d %B %Y à %H:%M')})"
            )
            st.subheader("📊 Résumé des avis critiques")
            st.markdown(cached_summary["summary"], unsafe_allow_html=True)
    else:
        st.write("Aucun épisode trouvé pour cette sélection.")

    return episode if not episode.empty else None


def post_process_and_sort_summary(summary_text, episode_date=None):
    """Post-traite le résumé pour corriger le tri des notes, supprimer les phrases explicatives et ajouter la date"""
    import re

    # Formater la date pour l'insertion dans les titres
    date_str = ""
    if episode_date:
        if isinstance(episode_date, str):
            date_str = f" du {episode_date}"
        else:
            date_str = f" du {format_date(episode_date, '%d %B %Y')}"

    # Supprimer diverses phrases explicatives que l'IA pourrait générer
    phrases_to_remove = [
        "Les livres discutés au programme principal sont classés par note décroissante, avec des avis détaillés et des notes attribuées par chaque critique. Les coups de cœur personnels sont également classés par note décroissante, avec des commentaires sur les raisons de leur recommandation.",
        "Les livres sont classés par note décroissante.",
        "Voici l'analyse de la transcription",
        "En résumé,",
        "Voici les tableaux demandés",
        "Analyse de l'émission",
        "D'après la transcription",
        "Basé sur la transcription fournie",
        "Voici l'analyse des avis critiques",
    ]

    for phrase in phrases_to_remove:
        summary_text = summary_text.replace(phrase, "")

    # Supprimer les phrases introductives génériques avec regex
    summary_text = re.sub(r"^.*[Vv]oici.*\n", "", summary_text, flags=re.MULTILINE)
    summary_text = re.sub(r"^.*[Aa]nalyse.*\n", "", summary_text, flags=re.MULTILINE)
    summary_text = re.sub(r"^.*[Dd]\'après.*\n", "", summary_text, flags=re.MULTILINE)
    summary_text = re.sub(r"^.*[Bb]asé sur.*\n", "", summary_text, flags=re.MULTILINE)

    # NOUVEAU: Forcer l'ajout de la date dans les titres des tableaux si elle n'y est pas
    if date_str:
        # Ajouter la date au titre du programme principal si elle n'y est pas déjà
        summary_text = re.sub(
            r"(## 1\. LIVRES DISCUTÉS AU PROGRAMME)(?! du)",
            r"\1" + date_str,
            summary_text,
        )

        # Ajouter la date au titre des coups de cœur si elle n'y est pas déjà
        summary_text = re.sub(
            r"(## 2\. COUPS DE C[ŒO]EUR DES CRITIQUES)(?! du)",
            r"\1" + date_str,
            summary_text,
        )

    # Nettoyer les lignes vides multiples
    summary_text = re.sub(r"\n\s*\n", "\n\n", summary_text)
    summary_text = summary_text.strip()

    # S'assurer que le texte commence par un titre de section
    if not summary_text.startswith("##"):
        # Chercher le premier titre de section et commencer à partir de là
        lines = summary_text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("## 1."):
                summary_text = "\n".join(lines[i:])
                break

    # Si le résumé ne contient pas de tableaux avec des notes, le retourner tel quel
    if not re.search(r"<span[^>]*>(\d+\.?\d*)</span>", summary_text):
        return summary_text

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
            "2. COUPS DE CŒUR DES CRITIQUES" in line
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

            # Si c'est une ligne de données du tableau (contient des notes colorées OU des données)
            elif re.search(r"<span[^>]*>(\d+\.?\d*)</span>", line) or (
                "|" in line and line.strip() != ""
            ):
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

    # Séparer les lignes avec notes de celles sans notes
    lines_with_ratings = []
    lines_without_ratings = []

    for line in table_lines:
        # Chercher la note dans les spans HTML
        rating_match = re.search(r"<span[^>]*>(\d+\.?\d*)</span>", line)
        if rating_match:
            rating = float(rating_match.group(1))
            lines_with_ratings.append((rating, line))
        else:
            lines_without_ratings.append(line)

    # Trier par note décroissante seulement les lignes avec notes
    lines_with_ratings.sort(key=lambda x: x[0], reverse=True)

    # Reconstruire le tableau
    result = []
    if header_line:
        result.append("")  # Ligne vide avant le tableau
        result.append(header_line)
    if separator_line:
        result.append(separator_line)

    # Ajouter d'abord les lignes triées par note
    for rating, line in lines_with_ratings:
        result.append(line)

    # Puis ajouter les lignes sans notes (si il y en a)
    for line in lines_without_ratings:
        result.append(line)

    return result


def generate_critique_summary(transcription, episode_date=None):
    """Génère un résumé des avis critiques à partir d'une transcription"""

    # Vérifier que la transcription n'est pas vide ou trop courte
    if not transcription or len(transcription.strip()) < 100:
        raise ValueError(
            "La transcription est trop courte ou vide pour générer un résumé"
        )

    # Limiter la taille de la transcription si elle est trop longue
    max_chars = 100000  # Augmentation de la limite pour capturer les coups de cœur en fin d'émission
    if len(transcription) > max_chars:
        transcription = transcription[:max_chars] + "... [transcription tronquée]"
        st.warning(
            f"⚠️ Transcription tronquée à {max_chars} caractères pour éviter les timeouts"
        )

    # Vérifier si la transcription contient des mots-clés liés aux livres
    book_keywords = [
        "livre",
        "auteur",
        "roman",
        "critique",
        "littérature",
        "publication",
        "édition",
        "éditeur",
    ]
    transcription_lower = transcription.lower()
    keyword_count = sum(
        1 for keyword in book_keywords if keyword in transcription_lower
    )

    if keyword_count < 3:
        st.warning(
            "⚠️ Cette transcription ne semble pas contenir beaucoup de discussions sur les livres"
        )

    # Formater la date pour l'insertion dans les titres
    date_str = ""
    if episode_date:
        if isinstance(episode_date, str):
            date_str = f" du {episode_date}"
        else:
            date_str = f" du {format_date(episode_date, '%d %B %Y')}"

    prompt = f"""
Tu es un expert en critique littéraire qui analyse la transcription de l'émission "Le Masque et la Plume" sur France Inter.

IMPORTANT: Si cette transcription ne contient PAS de discussions sur des livres, réponds simplement:
"Aucun livre discuté dans cet épisode. Cette émission semble porter sur d'autres sujets (cinéma, théâtre, musique)."

Voici la transcription:
{transcription}

CONSIGNE PRINCIPALE:
Identifie TOUS les livres discutés et crée 2 tableaux détaillés et complets:

1. **LIVRES DU PROGRAMME PRINCIPAL**: Tous les livres qui font l'objet d'une discussion approfondie entre plusieurs critiques
2. **COUPS DE CŒUR PERSONNELS**: UNIQUEMENT les livres mentionnés rapidement par un critique comme recommandation personnelle (différents du programme principal)

⚠️ CONSIGNE CRUCIALE: NE RETOURNE QUE LES DEUX TABLEAUX, SANS AUCUNE PHRASE D'EXPLICATION, SANS COMMENTAIRE, SANS PHRASE INTRODUCTIVE. COMMENCE DIRECTEMENT PAR "## 1. LIVRES DISCUTÉS AU PROGRAMME" et termine par le dernier tableau.

---

## 1. LIVRES DISCUTÉS AU PROGRAMME{date_str}

Format de tableau markdown OBLIGATOIRE avec HTML pour les couleurs:

| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|-------------|-------------|-------------|
| [Nom auteur] | [Titre livre] | [Éditeur] | **[Nom COMPLET critique 1]**: [avis détaillé et note] <br>**[Nom COMPLET critique 2]**: [avis détaillé et note] <br>**[Nom COMPLET critique 3]**: [avis détaillé et note] | [Note colorée] | [Nombre] | [Noms si note ≥9] | [Noms si note=10] |

⚠️ IMPORTANT: CLASSE LES LIVRES PAR NOTE DÉCROISSANTE (meilleure note d'abord, pire note en dernier).

RÈGLES DE NOTATION STRICTES:
- Note 1-2: Livres détestés, "purges", "ennuyeux", "raté"
- Note 3-4: Livres décevants, "pas terrible", "problématique"
- Note 5-6: Livres moyens, "correct sans plus", "mitigé"
- Note 7-8: Bons livres, "plaisant", "réussi", "bien écrit"
- Note 9: Excellents livres, "formidable", "remarquable", "coup de cœur"
- Note 10: Chefs-d'œuvre, "génial", "exceptionnel", "chef-d'œuvre"

COULEURS HTML OBLIGATOIRES pour la Note moyenne:
- 9.0-10.0: <span style="background-color: #00C851; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 8.0-8.9: <span style="background-color: #4CAF50; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 7.0-7.9: <span style="background-color: #8BC34A; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 6.0-6.9: <span style="background-color: #CDDC39; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 5.0-5.9: <span style="background-color: #FFEB3B; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 4.0-4.9: <span style="background-color: #FF9800; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 3.0-3.9: <span style="background-color: #FF5722; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>
- 1.0-2.9: <span style="background-color: #F44336; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">X.X</span>

INSTRUCTIONS DÉTAILLÉES POUR EXTRAIRE TOUS LES AVIS:
1. Identifie TOUS les critiques qui parlent de chaque livre: Jérôme Garcin, Elisabeth Philippe, Frédéric Beigbeder, Michel Crépu, Arnaud Viviant, Judith Perrignon, Xavier Leherpeur, Patricia Martin, etc.
2. Pour chaque critique, capture son NOM COMPLET (Prénom + Nom) 
3. Cite leurs avis EXACTS avec leurs mots-clés d'appréciation
4. Attribue une note individuelle basée sur leur vocabulaire (entre 1 et 10)
5. Calcule la moyenne arithmétique précise (ex: 7.3, 8.7)
6. Identifie les "coups de cœur" (critiques très enthousiastes, note ≥9)
7. **CLASSE OBLIGATOIREMENT PAR NOTE DÉCROISSANTE** (meilleure note d'abord)

---

## 2. COUPS DE CŒUR DES CRITIQUES{date_str}

⚠️ ATTENTION: Ce tableau contient UNIQUEMENT les livres/ouvrages mentionnés rapidement par les critiques comme recommandations personnelles supplémentaires (souvent en fin d'émission avec "mon coup de cœur", "je recommande", etc.). 
Ce sont des ouvrages DIFFÉRENTS de ceux discutés au programme principal ci-dessus.
INCLUT TOUS TYPES D'OUVRAGES : romans, essais, BD, guides, biographies, etc.

Format de tableau pour ces recommandations personnelles:

| Auteur | Titre | Éditeur | Critique | Note | Commentaire |
|--------|-------|---------|----------|------|-------------|
| [Nom] | [Titre] | [Éditeur] | [Nom COMPLET critique] | [Note colorée] | [Raison du coup de cœur] |

⚠️ IMPORTANT: 
- CLASSE LES COUPS DE CŒUR PAR NOTE DÉCROISSANTE AUSSI
- N'INCLUS QUE les livres mentionnés comme recommandations PERSONNELLES, PAS ceux du programme principal
- CHERCHE SPÉCIALEMENT en fin de transcription les sections "coups de cœur", "conseils de lecture", "recommandations"

EXIGENCES QUALITÉ:
- Noms COMPLETS de TOUS les critiques (Prénom + Nom)
- Citations exactes des avis les plus marquants
- Éditeurs mentionnés quand disponibles
- Tableaux markdown parfaitement formatés
- Couleurs HTML correctement appliquées
- **CLASSEMENT OBLIGATOIRE PAR NOTE DÉCROISSANTE**
- Capture de TOUS les avis individuels (pas seulement Elisabeth Philippe)
- **RECHERCHE ACTIVE des coups de cœur en fin de transcription** : cherche "coups de cœur", "conseil de lecture", "je recommande", "mon choix"

⚠️ SPÉCIAL COUPS DE CŒUR: Les critiques mentionnent souvent leurs recommandations personnelles vers la fin de l'émission. SCRUTE ATTENTIVEMENT la fin de la transcription pour ne pas les manquer !

⚠️ FORMAT DE RÉPONSE: Retourne UNIQUEMENT les 2 tableaux markdown avec leurs titres. N'ajoute AUCUNE explication, phrase introductive, ou commentaire sur la méthode de génération. Commence directement par "## 1. LIVRES DISCUTÉS AU PROGRAMME" et termine par le dernier tableau.

RAPPEL FINAL: NE RETOURNE AUCUN TEXTE EXPLICATIF AVANT OU APRÈS LES TABLEAUX. AUCUNE PHRASE COMME "voici l'analyse" ou "en résumé". COMMENCE IMMÉDIATEMENT PAR LE PREMIER TITRE DE TABLEAU.

Sois EXHAUSTIF et PRÉCIS. Capture TOUS les livres, TOUS les critiques, et TOUS les avis individuels."""

    try:
        # Utiliser Azure OpenAI avec timeout configuré dans llm.py (300 secondes)
        model = get_azure_llm()
        st.info("🔧 Utilisation du timeout Azure OpenAI (300 secondes / 5 minutes)")

        # Configurer les paramètres pour obtenir une réponse plus longue et détaillée
        response = model.complete(
            prompt,
            max_tokens=4000,  # Augmenter significativement la limite pour des résumés détaillés
            temperature=0.1,  # Réduire la créativité pour plus de cohérence
        )

        # DEBUG: Affichage de la réponse brute pour le débogage
        # Décommentez les lignes ci-dessous si vous avez besoin de déboguer la génération :
        # - Pour voir la réponse complète de l'IA avant post-traitement
        # - Pour vérifier si la réponse est tronquée
        # - Pour analyser les problèmes de formatage ou de contenu

        response_text = response.text.strip()
        st.write("🔍 **DEBUG - Réponse brute de l'IA:**")
        st.code(
            (
                response_text[:1000] + "..."
                if len(response_text) > 1000
                else response_text
            ),
            language="markdown",
        )
        st.write(f"📊 **Longueur de la réponse:** {len(response_text)} caractères")

        response_text = response.text.strip()

        # Vérifier si la réponse semble tronquée
        if (
            len(response_text) < 300
            or response_text.endswith("**")
            or response_text.endswith("→")
        ):
            st.error(
                "⚠️ La réponse de l'IA semble tronquée (trop courte ou se termine brutalement)"
            )
            st.info(
                "💡 Cela peut être dû à une limite de tokens. Essayez avec un épisode plus court ou réessayez."
            )
            return "Réponse de l'IA tronquée. Veuillez réessayer."

        # Vérifier si l'IA indique qu'aucun livre n'est discuté
        if (
            "Aucun livre discuté" in response_text
            or "porte sur d'autres sujets" in response_text
        ):
            st.warning("📚 Aucun livre discuté dans cet épisode")
            return response_text

        # Le nouveau format nécessite un post-traitement pour corriger le tri
        st.info("🔄 Correction automatique du tri par notes décroissantes...")
        sorted_summary = post_process_and_sort_summary(response_text, episode_date)

        st.info("✅ Résumé détaillé généré avec noms des critiques et avis individuels")
        return sorted_summary

    except Exception as e:
        error_msg = str(e).lower()
        st.error(f"Erreur lors de la génération avec l'IA: {str(e)}")

        # Ajouter plus de détails sur l'erreur
        if "transcription est trop courte" in str(e):
            st.warning(
                "📝 La transcription est trop courte pour générer un résumé valide"
            )
        elif "timeout" in error_msg or "timed out" in error_msg:
            st.warning("⏰ Timeout: La génération a pris trop de temps (>300 secondes)")
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


def debug_truncation_detection(summary_text):
    """Fonction de débogage pour comprendre pourquoi un résumé est considéré comme tronqué"""
    debug_info = []

    if not summary_text or isinstance(summary_text, str) and summary_text.strip() == "":
        debug_info.append("❌ Résumé vide ou None")
        return debug_info

    debug_info.append(f"📏 Longueur: {len(summary_text)} caractères")

    # Vérifier le message d'erreur
    if "Réponse de l'IA tronquée. Veuillez réessayer." in summary_text:
        debug_info.append("❌ Contient le message d'erreur de troncature")

    # Vérifier la longueur minimale
    if len(summary_text) < 200:
        debug_info.append("❌ Trop court (< 200 caractères)")
    else:
        debug_info.append("✅ Longueur suffisante")

    # Vérifier les fins brutales
    endings = []
    if summary_text.endswith("**"):
        endings.append("**")
    if summary_text.endswith("→"):
        endings.append("→")
    if summary_text.endswith("..."):
        endings.append("...")

    if endings:
        debug_info.append(f"❌ Se termine par: {', '.join(endings)}")
    else:
        debug_info.append("✅ Fin normale")

    # Vérifier la structure
    if "## 1." not in summary_text:
        debug_info.append("❌ Pas de titre de section '## 1.'")
    else:
        debug_info.append("✅ Contient un titre de section")

    # Analyser la dernière ligne
    lines = summary_text.strip().split("\n")
    last_non_empty_line = ""
    for line in reversed(lines):
        if line.strip():
            last_non_empty_line = line.strip()
            break

    debug_info.append(f"🔍 Dernière ligne: '{last_non_empty_line[:100]}...'")

    if last_non_empty_line.startswith("|"):
        segments = last_non_empty_line.split("|")
        non_empty_segments = [seg.strip() for seg in segments if seg.strip()]
        debug_info.append(f"📊 Segments du tableau: {len(non_empty_segments)} colonnes")

        if len(non_empty_segments) < 2:
            debug_info.append("❌ Tableau incomplet (< 2 colonnes)")
        else:
            debug_info.append("✅ Tableau semble complet")

        if last_non_empty_line.strip() in ["|", "| |", "||"]:
            debug_info.append("❌ Ligne de tableau vide/malformée")
    else:
        debug_info.append("✅ Ne se termine pas par une ligne de tableau")

    return debug_info


# Interface principale
try:
    afficher_selection_episode()
except Exception as e:
    st.error(f"Erreur lors du chargement des épisodes: {str(e)}")
    st.info("Vérifiez que la base de données MongoDB est accessible")
