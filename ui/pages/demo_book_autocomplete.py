#!/usr/bin/env python3
"""
Page de démonstration du composant BookAutocomplete.

Cette page permet de tester le composant en situation réelle
avec l'interface Streamlit complète.
"""

import streamlit as st
import sys
from pathlib import Path

# Configuration de la page
st.set_page_config(page_title="Démo Book Autocomplete", page_icon="📚", layout="wide")

# Ajout des paths nécessaires
ui_components_path = Path(__file__).parent.parent / "components"
nbs_path = Path(__file__).parent.parent.parent / "nbs"

if str(ui_components_path) not in sys.path:
    sys.path.insert(0, str(ui_components_path))
if str(nbs_path) not in sys.path:
    sys.path.insert(0, str(nbs_path))

from book_autocomplete import (
    BookAutocompleteConfig,
    BookAutocompleteComponent,
    render_book_autocomplete,
    render_book_autocomplete_with_episodes,
)


def main():
    """Page principale de démonstration"""
    st.title("📚 Démonstration du composant Book Autocomplete")
    st.markdown("---")

    # Section 1: Composant simple
    st.header("1. Composant simple")
    st.write("Recherche basique avec configuration par défaut")

    try:
        selected = render_book_autocomplete(
            key="demo_simple", label="Rechercher un livre ou auteur (simple)"
        )

        if selected:
            st.success(f"Sélectionné: **{selected.livre}** par *{selected.auteur}*")
    except Exception as e:
        st.error(f"Erreur composant simple: {e}")

    st.markdown("---")

    # Section 2: Composant avec configuration personnalisée
    st.header("2. Composant avec configuration personnalisée")
    st.write("Recherche avec configuration adaptée")

    # Configuration personnalisée
    custom_config = BookAutocompleteConfig(
        min_chars=2,
        max_suggestions=5,
        placeholder="Tapez 2 caractères minimum...",
        help_text="Recherche personnalisée avec seuil de 2 caractères",
        fuzzy_threshold=80,
        show_episodes_count=False,
        enable_clear_button=True,
    )

    try:
        selected_custom = render_book_autocomplete(
            config=custom_config,
            key="demo_custom",
            label="Rechercher avec configuration personnalisée",
        )

        if selected_custom:
            st.success(
                f"Sélectionné (custom): **{selected_custom.livre}** par *{selected_custom.auteur}*"
            )
    except Exception as e:
        st.error(f"Erreur composant custom: {e}")

    st.markdown("---")

    # Section 3: Composant avec épisodes
    st.header("3. Composant avec affichage automatique des épisodes")
    st.write("Recherche avec affichage immédiat des épisodes correspondants")

    try:
        selected_episodes, episodes = render_book_autocomplete_with_episodes(
            key="demo_episodes", label="Rechercher avec affichage des épisodes"
        )

        if selected_episodes and episodes:
            st.success(
                f"Trouvé **{len(episodes)}** épisode(s) pour **{selected_episodes.livre}**"
            )
    except Exception as e:
        st.error(f"Erreur composant avec épisodes: {e}")

    st.markdown("---")

    # Section 4: Tests manuels
    st.header("4. Zone de tests manuels")

    with st.expander("🧪 Tests suggérés", expanded=False):
        st.markdown(
            """
        **Tests de fonctionnalité :**
        - Tapez moins de 3 caractères → message d'info
        - Tapez un terme inexistant → message "aucun résultat"
        - Tapez un terme valide → liste de suggestions
        - Sélectionnez une suggestion → affichage détaillé
        
        **Tests d'erreur :**
        - Test de performance avec de longues requêtes
        - Test de résistance aux caractères spéciaux
        - Test du bouton clear (🗑️)
        
        **Exemples de recherche :**
        - "Hugo" (auteur)
        - "Harry Potter" (livre)
        - "1984" (titre)
        - "roman" (terme générique)
        """
        )

    # Section informations techniques
    with st.expander("ℹ️ Informations techniques", expanded=False):
        st.markdown(
            """
        **Composant :** `BookAutocompleteComponent`
        **Moteur de recherche :** `AvisSearchEngine` 
        **Base de données :** MongoDB collection `episode_livres`
        **Algorithme fuzzy :** thefuzz avec token_set_ratio
        **Cache :** Streamlit @st.cache_data activé
        
        **Configuration par défaut :**
        - Minimum de caractères : 3
        - Suggestions maximum : 10
        - Seuil fuzzy : 70%
        - Bouton clear : activé
        - Affichage info : activé
        """
        )


if __name__ == "__main__":
    main()
