#!/usr/bin/env python3
"""
Tests pour le composant UI book_autocomplete.py

Ces tests valident :
1. La configuration du composant
2. La création et initialisation
3. L'intégration avec AvisSearchEngine (avec mocks)
4. Les fonctions helper
5. La gestion d'erreurs
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from dataclasses import asdict

# Ajout du répertoire ui/components au path
ui_components_path = Path(__file__).parent.parent / "ui" / "components"
nbs_path = Path(__file__).parent.parent / "nbs"
sys.path.insert(0, str(ui_components_path))
sys.path.insert(0, str(nbs_path))

# Mock Streamlit avant import
sys.modules["streamlit"] = MagicMock()

from book_autocomplete import (
    BookAutocompleteConfig,
    BookAutocompleteComponent,
    render_book_autocomplete,
    render_book_autocomplete_with_episodes,
)


class TestBookAutocompleteConfig(unittest.TestCase):
    """Tests pour la dataclass BookAutocompleteConfig"""

    def test_config_creation_defaults(self):
        """Test de création avec valeurs par défaut"""
        config = BookAutocompleteConfig()

        self.assertEqual(config.min_chars, 3)
        self.assertEqual(config.max_suggestions, 10)
        self.assertEqual(
            config.placeholder, "Tapez un titre de livre ou nom d'auteur..."
        )
        self.assertEqual(
            config.help_text,
            "Recherche fuzzy dans les livres et auteurs des avis critiques",
        )
        self.assertEqual(config.fuzzy_threshold, 70)
        self.assertTrue(config.show_episodes_count)
        self.assertTrue(config.enable_clear_button)

    def test_config_creation_custom(self):
        """Test de création avec valeurs personnalisées"""
        config = BookAutocompleteConfig(
            min_chars=2,
            max_suggestions=5,
            placeholder="Custom placeholder",
            help_text="Custom help",
            fuzzy_threshold=80,
            show_episodes_count=False,
            enable_clear_button=False,
        )

        self.assertEqual(config.min_chars, 2)
        self.assertEqual(config.max_suggestions, 5)
        self.assertEqual(config.placeholder, "Custom placeholder")
        self.assertEqual(config.help_text, "Custom help")
        self.assertEqual(config.fuzzy_threshold, 80)
        self.assertFalse(config.show_episodes_count)
        self.assertFalse(config.enable_clear_button)


class TestBookAutocompleteComponent(unittest.TestCase):
    """Tests pour la classe BookAutocompleteComponent"""

    def setUp(self):
        """Configuration avant chaque test"""
        # Mock AvisSearchEngine
        self.mock_search_engine = Mock()
        self.patcher_search_engine = patch(
            "book_autocomplete.AvisSearchEngine", return_value=self.mock_search_engine
        )
        self.patcher_search_engine.start()

        # Mock Streamlit functions
        self.mock_st = MagicMock()
        sys.modules["streamlit"] = self.mock_st

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher_search_engine.stop()

    def test_component_creation_default_config(self):
        """Test de création avec configuration par défaut"""
        component = BookAutocompleteComponent()

        self.assertIsNotNone(component.config)
        self.assertEqual(component.config.min_chars, 3)
        self.assertIsNotNone(component.search_engine)

    def test_component_creation_custom_config(self):
        """Test de création avec configuration personnalisée"""
        config = BookAutocompleteConfig(min_chars=2, fuzzy_threshold=80)
        component = BookAutocompleteComponent(config)

        self.assertEqual(component.config.min_chars, 2)
        self.assertEqual(component.config.fuzzy_threshold, 80)

    @patch("book_autocomplete.st")
    def test_render_query_too_short(self, mock_st):
        """Test avec query trop courte"""
        component = BookAutocompleteComponent()

        # Mock text_input retourne query courte
        mock_st.text_input.return_value = "ab"
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        result = component.render()

        # Vérifications
        self.assertIsNone(result)
        mock_st.info.assert_called_once()

    @patch("book_autocomplete.st")
    def test_render_query_empty(self, mock_st):
        """Test avec query vide"""
        component = BookAutocompleteComponent()

        # Mock text_input retourne chaîne vide
        mock_st.text_input.return_value = ""
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        result = component.render()

        # Vérifications
        self.assertIsNone(result)
        mock_st.info.assert_not_called()
        mock_st.warning.assert_not_called()

    @patch("book_autocomplete.st")
    def test_render_no_results(self, mock_st):
        """Test avec aucun résultat trouvé"""
        component = BookAutocompleteComponent()

        # Mock text_input et search_engine
        mock_st.text_input.return_value = "inexistant"
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        self.mock_search_engine.search_combined.return_value = []

        result = component.render()

        # Vérifications
        self.assertIsNone(result)
        mock_st.warning.assert_called_once()

    @patch("book_autocomplete.st")
    def test_render_with_results_no_selection(self, mock_st):
        """Test avec résultats mais aucune sélection"""
        component = BookAutocompleteComponent()

        # Mock text_input, search_engine et selectbox
        mock_st.text_input.return_value = "livre test"
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Mock résultats de recherche
        mock_result = Mock()
        mock_result.livre = "Test Livre"
        mock_result.auteur = "Test Auteur"
        self.mock_search_engine.search_combined.return_value = [mock_result]
        self.mock_search_engine.format_suggestion.return_value = (
            "Test Livre - Test Auteur"
        )

        # Mock selectbox sans sélection
        mock_st.selectbox.return_value = ""

        result = component.render()

        # Vérifications
        self.assertIsNone(result)
        self.mock_search_engine.search_combined.assert_called_once()

    @patch("book_autocomplete.st")
    def test_render_with_results_and_selection(self, mock_st):
        """Test avec résultats et sélection"""
        component = BookAutocompleteComponent()

        # Mock text_input, search_engine et selectbox
        mock_st.text_input.return_value = "livre test"
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Mock résultats de recherche
        mock_result = Mock()
        mock_result.livre = "Test Livre"
        mock_result.auteur = "Test Auteur"
        self.mock_search_engine.search_combined.return_value = [mock_result]
        self.mock_search_engine.format_suggestion.return_value = (
            "Test Livre - Test Auteur"
        )

        # Mock selectbox avec sélection
        mock_st.selectbox.return_value = "Test Livre - Test Auteur"

        result = component.render()

        # Vérifications
        self.assertEqual(result, mock_result)
        self.mock_search_engine.search_combined.assert_called_once()

    @patch("book_autocomplete.st")
    def test_render_search_error(self, mock_st):
        """Test avec erreur lors de la recherche"""
        component = BookAutocompleteComponent()

        # Mock text_input et erreur search_engine
        mock_st.text_input.return_value = "livre test"
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        self.mock_search_engine.search_combined.side_effect = Exception("Erreur test")

        result = component.render()

        # Vérifications
        self.assertIsNone(result)
        mock_st.error.assert_called_once()

    @patch("book_autocomplete.st")
    def test_render_with_episodes_success(self, mock_st):
        """Test render_with_episodes avec succès"""
        component = BookAutocompleteComponent()

        # Mock d'une sélection
        mock_result = Mock()
        mock_result.livre = "Test Livre"
        mock_result.auteur = "Test Auteur"

        # Mock get_book_episodes
        mock_episode = Mock()
        mock_episode.titre_episode = "Episode Test"
        mock_episode.date_diffusion = "2024-01-01"
        mock_episode.emission = "Test Emission"
        mock_episode.avis_critique = "Avis test"
        mock_episode.url_episode = "http://test.com"
        mock_episode.type_oeuvre = "livre"

        self.mock_search_engine.get_book_episodes.return_value = [mock_episode]

        # Mock render qui retourne le résultat
        with patch.object(component, "render", return_value=mock_result):
            selected, episodes = component.render_with_episodes()

        # Vérifications
        self.assertEqual(selected, mock_result)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0], mock_episode)
        mock_st.subheader.assert_called_once()

    @patch("book_autocomplete.st")
    def test_render_with_episodes_no_episodes(self, mock_st):
        """Test render_with_episodes sans épisodes"""
        component = BookAutocompleteComponent()

        # Mock d'une sélection
        mock_result = Mock()
        mock_result.livre = "Test Livre"
        mock_result.auteur = "Test Auteur"

        # Mock get_book_episodes sans résultat
        self.mock_search_engine.get_book_episodes.return_value = []

        # Mock render qui retourne le résultat
        with patch.object(component, "render", return_value=mock_result):
            selected, episodes = component.render_with_episodes()

        # Vérifications
        self.assertEqual(selected, mock_result)
        self.assertEqual(len(episodes), 0)
        mock_st.info.assert_called_once()

    @patch("book_autocomplete.st")
    def test_display_selection_info_with_info(self, mock_st):
        """Test display_selection_info avec informations"""
        config = BookAutocompleteConfig(show_episodes_count=True)
        component = BookAutocompleteComponent(config)

        # Mock résultat avec attributs
        mock_result = Mock()
        mock_result.livre = "Test Livre"
        mock_result.auteur = "Test Auteur"
        mock_result.episodes_count = 5
        mock_result.type_oeuvre = "roman"

        # Mock expander et columns
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        component._display_selection_info(mock_result)

        # Vérifications
        mock_st.expander.assert_called_once()

    @patch("book_autocomplete.st")
    def test_display_selection_info_disabled(self, mock_st):
        """Test display_selection_info désactivé"""
        config = BookAutocompleteConfig(show_episodes_count=False)
        component = BookAutocompleteComponent(config)

        mock_result = Mock()
        component._display_selection_info(mock_result)

        # Vérifications - aucun appel à expander
        mock_st.expander.assert_not_called()


class TestHelperFunctions(unittest.TestCase):
    """Tests pour les fonctions helper"""

    def setUp(self):
        """Configuration avant chaque test"""
        # Mock AvisSearchEngine
        self.mock_search_engine = Mock()
        self.patcher_search_engine = patch(
            "book_autocomplete.AvisSearchEngine", return_value=self.mock_search_engine
        )
        self.patcher_search_engine.start()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher_search_engine.stop()

    def test_render_book_autocomplete_function(self):
        """Test de la fonction render_book_autocomplete"""
        with patch(
            "book_autocomplete.BookAutocompleteComponent"
        ) as mock_component_class:
            mock_component = Mock()
            mock_component_class.return_value = mock_component
            mock_component.render.return_value = "test_result"

            result = render_book_autocomplete(
                config=None, key="test_key", label="Test Label"
            )

            # Vérifications
            self.assertEqual(result, "test_result")
            mock_component_class.assert_called_once_with(None)
            mock_component.render.assert_called_once_with(
                key="test_key", label="Test Label"
            )

    def test_render_book_autocomplete_with_episodes_function(self):
        """Test de la fonction render_book_autocomplete_with_episodes"""
        with patch(
            "book_autocomplete.BookAutocompleteComponent"
        ) as mock_component_class:
            mock_component = Mock()
            mock_component_class.return_value = mock_component
            mock_component.render_with_episodes.return_value = (
                "test_result",
                ["episode1"],
            )

            result, episodes = render_book_autocomplete_with_episodes(
                config=None, key="test_key", label="Test Label"
            )

            # Vérifications
            self.assertEqual(result, "test_result")
            self.assertEqual(episodes, ["episode1"])
            mock_component_class.assert_called_once_with(None)
            mock_component.render_with_episodes.assert_called_once_with(
                key="test_key", label="Test Label"
            )


class TestComponentIntegration(unittest.TestCase):
    """Tests d'intégration du composant"""

    def setUp(self):
        """Configuration avant chaque test"""
        # Mock complet de Streamlit
        self.mock_st = MagicMock()
        sys.modules["streamlit"] = self.mock_st

        # Mock AvisSearchEngine
        self.mock_search_engine = Mock()
        self.patcher_search_engine = patch(
            "book_autocomplete.AvisSearchEngine", return_value=self.mock_search_engine
        )
        self.patcher_search_engine.start()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher_search_engine.stop()

    def test_component_configuration_propagation(self):
        """Test que la configuration est bien propagée"""
        config = BookAutocompleteConfig(
            min_chars=2, fuzzy_threshold=80, max_suggestions=5
        )

        # Vérifier que AvisSearchEngine est créé avec les bons paramètres
        component = BookAutocompleteComponent(config)

        # Vérifications de l'initialisation de AvisSearchEngine
        from book_autocomplete import AvisSearchEngine

        AvisSearchEngine.assert_called_with(min_chars=2, fuzzy_threshold=80)

    def test_key_uniqueness(self):
        """Test de l'unicité des clés Streamlit"""
        component = BookAutocompleteComponent()

        # Mock des appels Streamlit
        with patch("book_autocomplete.st") as mock_st:
            mock_st.text_input.return_value = ""
            mock_st.columns.return_value = [MagicMock(), MagicMock()]

            component.render(key="unique_key")

            # Vérifier que les clés contiennent le préfixe unique
            calls = mock_st.text_input.call_args_list
            self.assertTrue(any("unique_key" in str(call) for call in calls))


if __name__ == "__main__":
    unittest.main(verbosity=2)
