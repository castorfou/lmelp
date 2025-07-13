"""
Composant Streamlit pour autocomplétion de livres et auteurs.

Utilise AvisSearchEngine pour fournir une interface d'autocomplétion
rapide et intuitive pour la recherche de livres/auteurs dans les avis critiques.
"""

import streamlit as st
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

# Ajout du répertoire nbs au path pour imports
nbs_path = Path(__file__).parent.parent.parent / "nbs"
if str(nbs_path) not in sys.path:
    sys.path.insert(0, str(nbs_path))

from avis_search import AvisSearchEngine, AutocompleteResult, EpisodeAvis


@dataclass
class BookAutocompleteConfig:
    """Configuration du composant d'autocomplétion"""

    min_chars: int = 3
    max_suggestions: int = 10
    placeholder: str = "Tapez un titre de livre ou nom d'auteur..."
    help_text: str = "Recherche fuzzy dans les livres et auteurs des avis critiques"
    fuzzy_threshold: int = 70
    show_episodes_count: bool = True
    enable_clear_button: bool = True


class BookAutocompleteComponent:
    """Composant Streamlit pour autocomplétion livre/auteur"""

    def __init__(self, config: Optional[BookAutocompleteConfig] = None):
        self.config = config or BookAutocompleteConfig()
        self.search_engine = AvisSearchEngine(
            min_chars=self.config.min_chars, fuzzy_threshold=self.config.fuzzy_threshold
        )

    def render(
        self,
        key: str = "book_autocomplete",
        label: str = "Rechercher un livre ou auteur",
    ) -> Optional[AutocompleteResult]:
        """
        Rend le composant d'autocomplétion dans Streamlit.

        Args:
            key (str): Clé unique pour le composant Streamlit
            label (str): Label affiché au-dessus du champ

        Returns:
            Optional[AutocompleteResult]: Résultat sélectionné ou None
        """
        col1, col2 = (
            st.columns([4, 1])
            if self.config.enable_clear_button
            else (st.container(), None)
        )

        with col1:
            # Champ de recherche principal
            query = st.text_input(
                label=label,
                placeholder=self.config.placeholder,
                help=self.config.help_text,
                key=f"{key}_input",
            )

        if col2 and self.config.enable_clear_button:
            with col2:
                st.write("")  # Espacement
                if st.button("🗑️", help="Effacer", key=f"{key}_clear"):
                    st.rerun()

        # Recherche et affichage des suggestions
        if query and len(query.strip()) >= self.config.min_chars:
            return self._render_suggestions(query.strip(), key)
        elif query and len(query.strip()) < self.config.min_chars:
            st.info(
                f"Tapez au moins {self.config.min_chars} caractères pour lancer la recherche"
            )

        return None

    def _render_suggestions(self, query: str, key: str) -> Optional[AutocompleteResult]:
        """Rend les suggestions de recherche"""
        try:
            # Recherche via AvisSearchEngine
            results = self.search_engine.search_combined(
                query, limit=self.config.max_suggestions
            )

            if not results:
                st.warning("Aucun livre ou auteur trouvé pour cette recherche")
                return None

            # Formatage des suggestions pour selectbox
            suggestions = []
            formatted_results = {}

            for result in results:
                formatted = self.search_engine.format_suggestion(
                    result.auteur_nom, result.livre_titre
                )
                suggestions.append(formatted)
                formatted_results[formatted] = result

            # Selectbox avec suggestions
            selected = st.selectbox(
                f"Suggestions ({len(suggestions)} trouvée(s))",
                options=[""] + suggestions,
                key=f"{key}_selectbox",
                format_func=lambda x: x if x else "-- Sélectionnez une option --",
            )

            if selected:
                selected_result = formatted_results[selected]
                self._display_selection_info(selected_result)
                return selected_result

        except Exception as e:
            st.error(f"Erreur lors de la recherche: {e}")

        return None

    def _display_selection_info(self, result: AutocompleteResult) -> None:
        """Affiche les informations sur la sélection"""
        if not self.config.show_episodes_count:
            return

        with st.expander("ℹ️ Informations sur la sélection", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Livre:** {result.livre}")
                st.write(f"**Auteur:** {result.auteur}")

            with col2:
                if hasattr(result, "episodes_count"):
                    st.write(f"**Épisodes:** {result.episodes_count}")
                if hasattr(result, "type_oeuvre"):
                    st.write(f"**Type:** {result.type_oeuvre}")

    def render_with_episodes(
        self,
        key: str = "book_autocomplete_episodes",
        label: str = "Rechercher un livre ou auteur",
    ) -> Tuple[Optional[AutocompleteResult], List[EpisodeAvis]]:
        """
        Rend le composant avec affichage automatique des épisodes.

        Returns:
            Tuple[AutocompleteResult, List[EpisodeAvis]]: Sélection et épisodes correspondants
        """
        selected = self.render(key=key, label=label)
        episodes = []

        if selected:
            try:
                episodes = self.search_engine.get_book_episodes(
                    book_oid=getattr(selected, "book_oid", None),
                    livre=selected.livre,
                    auteur=selected.auteur,
                )

                if episodes:
                    st.subheader(f"Épisodes trouvés ({len(episodes)})")
                    self._display_episodes_list(episodes)
                else:
                    st.info("Aucun épisode trouvé pour cette sélection")

            except Exception as e:
                st.error(f"Erreur lors de la récupération des épisodes: {e}")

        return selected, episodes

    def _display_episodes_list(self, episodes: List[EpisodeAvis]) -> None:
        """Affiche la liste des épisodes"""
        for i, episode in enumerate(episodes):
            with st.expander(f"📻 {episode.titre_episode}", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Date:** {episode.date_diffusion}")
                    st.write(f"**Émission:** {episode.emission}")
                    if episode.avis_critique:
                        st.write("**Avis critique:**")
                        st.write(episode.avis_critique)

                with col2:
                    if episode.url_episode:
                        st.link_button("🎧 Écouter", episode.url_episode)
                    st.write(f"**Type:** {episode.type_oeuvre}")


def render_book_autocomplete(
    config: Optional[BookAutocompleteConfig] = None,
    key: str = "book_autocomplete",
    label: str = "Rechercher un livre ou auteur",
) -> Optional[AutocompleteResult]:
    """
    Fonction helper pour rendre rapidement le composant d'autocomplétion.

    Args:
        config: Configuration du composant
        key: Clé unique Streamlit
        label: Label du champ

    Returns:
        Résultat sélectionné ou None
    """
    component = BookAutocompleteComponent(config)
    return component.render(key=key, label=label)


def render_book_autocomplete_with_episodes(
    config: Optional[BookAutocompleteConfig] = None,
    key: str = "book_autocomplete_episodes",
    label: str = "Rechercher un livre ou auteur",
) -> Tuple[Optional[AutocompleteResult], List[EpisodeAvis]]:
    """
    Fonction helper pour rendre le composant avec affichage automatique des épisodes.

    Returns:
        Tuple[AutocompleteResult, List[EpisodeAvis]]: Sélection et épisodes
    """
    component = BookAutocompleteComponent(config)
    return component.render_with_episodes(key=key, label=label)
