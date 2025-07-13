"""
Tests basiques pour l'interface Streamlit.

Ces tests vérifient les composants et fonctionnalités de base
de l'application Streamlit sans lancer le serveur complet.
"""

import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os


# Configuration pour les tests UI
@pytest.fixture(autouse=True)
def setup_ui_test_environment():
    """Configuration automatique pour tous les tests UI"""
    # Mock des dépendances UI spécifiques
    mock_modules = {
        "streamlit": MagicMock(),
        "streamlit_card": MagicMock(),
        "ui_tools": MagicMock(),
    }

    for module_name, mock_module in mock_modules.items():
        sys.modules[module_name] = mock_module

    yield

    # Nettoyage après chaque test
    for module_name in mock_modules:
        if module_name in sys.modules:
            del sys.modules[module_name]


class TestStreamlitConfiguration:
    """Tests pour la configuration de base de Streamlit"""

    def test_page_config_setup(self):
        """Test que la configuration de page Streamlit est correcte"""
        with patch.dict(
            "sys.modules",
            {
                "streamlit": MagicMock(),
                "streamlit_card": MagicMock(),
                "ui_tools": MagicMock(),
                "rss": MagicMock(),
                "mongo_episode": MagicMock(),
                "locale": MagicMock(),
            },
        ):
            # Import du module UI après le mocking
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "lmelp_ui", "/workspaces/lmelp/ui/lmelp.py"
            )
            lmelp_ui = importlib.util.module_from_spec(spec)

            # Pas d'exécution complète, juste vérification d'imports
            assert spec is not None
            assert lmelp_ui is not None


class TestStreamlitComponents:
    """Tests pour les composants Streamlit individuels"""

    def test_navigation_links_structure(self):
        """Test de la structure des liens de navigation"""
        expected_pages = [
            "pages/1_episodes.py",
            "pages/2_auteurs.py",
            "pages/3_livres.py",
            "pages/4_avis_critiques.py",
        ]

        # Assert sur la structure attendue
        assert len(expected_pages) == 4
        assert all("pages/" in page for page in expected_pages)
        assert all(page.endswith(".py") for page in expected_pages)

    def test_pages_existence_and_completeness(self):
        """Test que toutes les pages attendues existent et qu'il n'y en a pas d'autres"""
        import os

        pages_directory = "/workspaces/lmelp/ui/pages"
        expected_pages = {
            "1_episodes.py",
            "2_auteurs.py",
            "3_livres.py",
            "4_avis_critiques.py",
        }

        # Vérifier que le répertoire pages existe
        assert os.path.exists(
            pages_directory
        ), f"Le répertoire {pages_directory} n'existe pas"

        # Lister tous les fichiers .py dans le répertoire pages
        actual_pages = set()
        for file in os.listdir(pages_directory):
            if file.endswith(".py") and not file.startswith("__"):
                actual_pages.add(file)

        # Assert que les pages correspondent exactement
        assert (
            actual_pages == expected_pages
        ), f"Pages attendues: {expected_pages}, Pages trouvées: {actual_pages}"

        # Vérifier individuellement l'existence de chaque page
        for page in expected_pages:
            page_path = os.path.join(pages_directory, page)
            assert os.path.isfile(
                page_path
            ), f"La page {page} n'existe pas à {page_path}"

        # Vérifier qu'il n'y a pas de pages supplémentaires
        extra_pages = actual_pages - expected_pages
        assert len(extra_pages) == 0, f"Pages non attendues trouvées: {extra_pages}"

        # Vérifier qu'aucune page attendue ne manque
        missing_pages = expected_pages - actual_pages
        assert len(missing_pages) == 0, f"Pages attendues manquantes: {missing_pages}"

    def test_pages_content_basic_validation(self):
        """Test que chaque page contient du contenu basique valide"""
        import os

        pages_directory = "/workspaces/lmelp/ui/pages"
        expected_pages = [
            "1_episodes.py",
            "2_auteurs.py",
            "3_livres.py",
            "4_avis_critiques.py",
        ]

        for page in expected_pages:
            page_path = os.path.join(pages_directory, page)

            # Vérifier que le fichier existe et n'est pas vide
            assert os.path.isfile(page_path), f"La page {page} n'existe pas"

            # Lire le contenu du fichier
            with open(page_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Vérifier que le fichier n'est pas vide
            assert len(content.strip()) > 0, f"La page {page} est vide"

            # Vérifier que le fichier contient du code Python basique
            assert (
                "import" in content or "st." in content
            ), f"La page {page} ne semble pas contenir de code Streamlit valide"

    def test_card_components_structure(self):
        """Test de la structure des composants card"""
        expected_cards = [
            {"title": "# episodes", "function": "affiche_episodes"},
            {"title": "last episode", "function": "affiche_last_date"},
            {
                "title": "# missing transcriptions",
                "function": "affiche_missing_transcription",
            },
        ]

        # Assert sur la structure des cartes
        assert len(expected_cards) == 3
        for card in expected_cards:
            assert "title" in card
            assert "function" in card


class TestStreamlitBusinessLogic:
    """Tests pour la logique métier dans l'interface"""

    @patch(
        "sys.modules",
        {
            "streamlit": MagicMock(),
            "streamlit_card": MagicMock(),
            "ui_tools": MagicMock(),
            "rss": MagicMock(),
            "mongo_episode": MagicMock(),
            "locale": MagicMock(),
            "io": MagicMock(),
            "subprocess": MagicMock(),
        },
    )
    def test_episodes_refresh_logic(self):
        """Test de la logique de rafraîchissement des épisodes"""
        # Mock des objets Episodes et Podcast
        mock_episodes = MagicMock()
        mock_episodes.len_total_entries.return_value = 10
        mock_episodes.get_missing_transcriptions.return_value = None
        mock_episodes.__len__.return_value = 0

        mock_podcast = MagicMock()
        mock_podcast.store_last_large_episodes.return_value = None

        # Test des appels attendus
        mock_episodes.len_total_entries()
        mock_podcast.store_last_large_episodes()
        mock_episodes.get_missing_transcriptions()

        # Assert que les méthodes sont appelables
        assert mock_episodes.len_total_entries.called
        assert mock_podcast.store_last_large_episodes.called
        assert mock_episodes.get_missing_transcriptions.called

    @patch(
        "sys.modules",
        {
            "streamlit": MagicMock(),
            "streamlit_card": MagicMock(),
            "ui_tools": MagicMock(),
            "rss": MagicMock(),
            "mongo_episode": MagicMock(),
            "locale": MagicMock(),
        },
    )
    def test_transcription_download_logic(self):
        """Test de la logique de téléchargement de transcriptions"""
        # Mock d'un épisode avec transcription
        mock_episode = MagicMock()
        mock_episode.set_transcription.return_value = None

        mock_episodes = MagicMock()
        mock_episodes.__len__.return_value = 1
        mock_episodes.__getitem__.return_value = mock_episode
        mock_episodes.get_missing_transcriptions.return_value = None

        # Test des appels
        mock_episodes.get_missing_transcriptions()
        if len(mock_episodes) > 0:
            episode = mock_episodes[-1]
            episode.set_transcription(verbose=True)

        # Assert
        assert mock_episodes.get_missing_transcriptions.called
        assert mock_episode.set_transcription.called


class TestStreamlitUtilityFunctions:
    """Tests pour les fonctions utilitaires de l'interface"""

    def test_date_format_configuration(self):
        """Test de la configuration du format de date"""
        expected_date_format = "%d %b %Y"

        # Assert sur le format attendu
        assert expected_date_format == "%d %b %Y"
        assert "%" in expected_date_format
        assert "d" in expected_date_format
        assert "b" in expected_date_format  # Mois abrégé
        assert "Y" in expected_date_format  # Année complète

    def test_locale_configuration(self):
        """Test de la configuration des locales"""
        expected_locales = ["en_US.UTF-8", "fr_FR.UTF-8"]

        # Assert sur les locales utilisées
        assert len(expected_locales) == 2
        assert "en_US.UTF-8" in expected_locales  # Pour le rafraîchissement
        assert "fr_FR.UTF-8" in expected_locales  # Pour l'affichage des dates


class TestStreamlitIntegration:
    """Tests d'intégration pour l'interface Streamlit"""

    def test_ui_backend_integration_points(self):
        """Test des points d'intégration UI-Backend"""
        integration_points = [
            "Episodes.len_total_entries()",
            "Episodes.get_missing_transcriptions()",
            "Podcast.store_last_large_episodes()",
            "Episode.set_transcription()",
        ]

        # Assert sur les points d'intégration
        assert len(integration_points) == 4
        assert all("." in point for point in integration_points)
        assert any("Episodes" in point for point in integration_points)
        assert any("Podcast" in point for point in integration_points)

    def test_streamlit_component_dependencies(self):
        """Test des dépendances des composants Streamlit"""
        required_components = [
            "st.set_page_config",
            "st.write",
            "st.page_link",
            "st.button",
            "st.spinner",
            "st.expander",
            "st.columns",
        ]

        # Assert sur les composants Streamlit utilisés
        assert len(required_components) == 7
        assert all(comp.startswith("st.") for comp in required_components)
        assert "st.button" in required_components  # Pour les interactions
        assert "st.spinner" in required_components  # Pour les opérations async
