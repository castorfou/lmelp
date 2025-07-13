"""
Tests pour le module nbs.web.

Ce module teste les fonctionnalités de parsing HTML incluant :
- Classe WebPage (parsing HTML et extraction d'épisodes)
- Méthodes d'accès aux données (__getitem__, __len__)
- Représentations string (__str__, __repr__)
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
from typing import List, Dict, Any

# Configuration des variables d'environnement pour éviter les erreurs
import os

os.environ.setdefault("AUDIO_PATH", "/tmp/test_audio")


@pytest.fixture(autouse=True)
def mock_web_dependencies():
    """Mock toutes les dépendances externes pour web automatiquement"""
    # Configuration du mock config pour être compatible
    mock_config = MagicMock()
    mock_config.get_WEB_filename.return_value = "/tmp/test_web.html"

    with patch.dict(
        "sys.modules",
        {
            "config": mock_config,
            "bs4": MagicMock(),
        },
    ):
        yield


@pytest.fixture
def sample_html_content():
    """Fixture pour du contenu HTML de test"""
    return """
    <html>
        <body>
            <ul>
                <li class="Collection-section-items-item">
                    <span class="CardTitle">Test Episode 1</span>
                    <a class="underline-hover" href="https://example.com/episode1">Link</a>
                    <div class="CardDescription">Description du premier épisode</div>
                    <div class="DefaultDetails-secondLine">
                        <p>22 Dec 2024</p>
                        <p>Separator</p>
                        <p>60 min</p>
                    </div>
                </li>
                <li class="Collection-section-items-item">
                    <span class="CardTitle">Test Episode 2</span>
                    <a class="underline-hover" href="https://example.com/episode2">Link</a>
                    <div class="CardDescription">Description du deuxième épisode</div>
                    <div class="DefaultDetails-secondLine">
                        <p>21 Dec 2024</p>
                        <p>Separator</p>
                        <p>45 min</p>
                    </div>
                </li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def sample_empty_html():
    """Fixture pour du contenu HTML vide"""
    return """
    <html>
        <body>
            <p>No episodes found</p>
        </body>
    </html>
    """


@pytest.fixture
def sample_incomplete_html():
    """Fixture pour du contenu HTML avec des éléments manquants"""
    return """
    <html>
        <body>
            <ul>
                <li class="Collection-section-items-item">
                    <span class="CardTitle">Incomplete Episode</span>
                    <!-- Missing link, description, or date elements -->
                </li>
            </ul>
        </body>
    </html>
    """


class TestModuleConstants:
    """Tests pour les constantes et exports du module"""

    def test_module_exports(self):
        """Test des exports __all__ du module"""
        from nbs import web

        expected_exports = ["WebPage"]

        # Assert
        assert web.__all__ == expected_exports

        # Verify all exports exist
        for export in expected_exports:
            assert hasattr(web, export), f"Missing export: {export}"


class TestWebPageInitialization:
    """Tests pour l'initialisation de WebPage"""

    def test_webpage_init_with_valid_html(self, sample_html_content):
        """Test d'initialisation avec du HTML valide"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data=sample_html_content)
        ), patch("nbs.web.BeautifulSoup") as mock_soup:

            # Mock BeautifulSoup parsing
            mock_soup_instance = MagicMock()
            mock_soup.return_value = mock_soup_instance

            # Mock les éléments trouvés
            mock_item1 = MagicMock()
            mock_item2 = MagicMock()

            # Configuration du premier épisode
            mock_title1 = MagicMock()
            mock_title1.get_text.return_value = "Test Episode 1"
            mock_link1 = MagicMock()
            mock_link1.__getitem__.return_value = "https://example.com/episode1"
            mock_desc1 = MagicMock()
            mock_desc1.get_text.return_value = "Description du premier épisode"
            mock_date_div1 = MagicMock()
            mock_date_p1 = MagicMock()
            mock_date_p1.get_text.return_value = "22 Dec 2024"
            mock_date_p2 = MagicMock()
            mock_date_p2.get_text.return_value = "60 min"
            mock_date_div1.find_all.return_value = [
                mock_date_p1,
                MagicMock(),
                mock_date_p2,
            ]

            mock_item1.find.side_effect = lambda tag, class_=None: {
                ("span", "CardTitle"): mock_title1,
                ("a", "underline-hover"): mock_link1,
                ("div", "CardDescription"): mock_desc1,
                ("div", "DefaultDetails-secondLine"): mock_date_div1,
            }.get((tag, class_))

            # Configuration du deuxième épisode
            mock_title2 = MagicMock()
            mock_title2.get_text.return_value = "Test Episode 2"
            mock_link2 = MagicMock()
            mock_link2.__getitem__.return_value = "https://example.com/episode2"
            mock_desc2 = MagicMock()
            mock_desc2.get_text.return_value = "Description du deuxième épisode"
            mock_date_div2 = MagicMock()
            mock_date_p3 = MagicMock()
            mock_date_p3.get_text.return_value = "21 Dec 2024"
            mock_date_p4 = MagicMock()
            mock_date_p4.get_text.return_value = "45 min"
            mock_date_div2.find_all.return_value = [
                mock_date_p3,
                MagicMock(),
                mock_date_p4,
            ]

            mock_item2.find.side_effect = lambda tag, class_=None: {
                ("span", "CardTitle"): mock_title2,
                ("a", "underline-hover"): mock_link2,
                ("div", "CardDescription"): mock_desc2,
                ("div", "DefaultDetails-secondLine"): mock_date_div2,
            }.get((tag, class_))

            mock_soup_instance.find_all.return_value = [mock_item1, mock_item2]

            from nbs.web import WebPage

            webpage = WebPage()

            # Assert
            assert len(webpage.episodes) == 2
            assert webpage.episodes[0]["title"] == "Test Episode 1"
            assert webpage.episodes[0]["url"] == "https://example.com/episode1"
            assert (
                webpage.episodes[0]["description"] == "Description du premier épisode"
            )
            assert webpage.episodes[0]["date"] == "22 Dec 2024"
            assert webpage.episodes[0]["duration"] == "60 min"

    def test_webpage_init_with_empty_html(self, sample_empty_html):
        """Test d'initialisation avec du HTML vide (sans épisodes)"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data=sample_empty_html)
        ), patch("nbs.web.BeautifulSoup") as mock_soup:

            # Mock BeautifulSoup pour ne trouver aucun épisode
            mock_soup_instance = MagicMock()
            mock_soup.return_value = mock_soup_instance
            mock_soup_instance.find_all.return_value = []

            from nbs.web import WebPage

            webpage = WebPage()

            # Assert
            assert len(webpage.episodes) == 0
            assert webpage.episodes == []

    def test_webpage_init_with_incomplete_html(self, sample_incomplete_html):
        """Test d'initialisation avec du HTML incomplet - doit lever une exception"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data=sample_incomplete_html)
        ), patch("nbs.web.BeautifulSoup") as mock_soup:

            # Mock BeautifulSoup avec des éléments manquants
            mock_soup_instance = MagicMock()
            mock_soup.return_value = mock_soup_instance

            mock_item = MagicMock()
            mock_title = MagicMock()
            mock_title.get_text.return_value = "Incomplete Episode"

            # Simuler des éléments manquants
            mock_item.find.side_effect = lambda tag, class_=None: {
                ("span", "CardTitle"): mock_title,
                ("a", "underline-hover"): None,  # Link manquant
                ("div", "CardDescription"): None,  # Description manquante
                (
                    "div",
                    "DefaultDetails-secondLine",
                ): None,  # Date manquante -> va causer AttributeError
            }.get((tag, class_))

            mock_soup_instance.find_all.return_value = [mock_item]

            from nbs.web import WebPage

            # Assert que l'exception est levée à cause du HTML incomplet
            with pytest.raises(AttributeError):
                WebPage()

    def test_webpage_init_file_reading(self):
        """Test que le fichier HTML est bien lu"""
        test_content = "<html><body>Test</body></html>"

        with patch(
            "nbs.web.get_WEB_filename", return_value="/tmp/test.html"
        ) as mock_get_filename, patch(
            "builtins.open", mock_open(read_data=test_content)
        ) as mock_file, patch(
            "nbs.web.BeautifulSoup"
        ) as mock_soup:

            mock_soup_instance = MagicMock()
            mock_soup.return_value = mock_soup_instance
            mock_soup_instance.find_all.return_value = []

            from nbs.web import WebPage

            webpage = WebPage()

            # Assert
            mock_get_filename.assert_called_once()
            mock_file.assert_called_once_with("/tmp/test.html", "r", encoding="utf-8")
            mock_soup.assert_called_once_with(test_content, "html.parser")


class TestWebPageMethods:
    """Tests pour les méthodes de WebPage"""

    def test_getitem_method(self):
        """Test de la méthode __getitem__"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data="")
        ), patch("nbs.web.BeautifulSoup"):

            from nbs.web import WebPage

            webpage = WebPage()

            # Ajouter manuellement des épisodes pour le test
            webpage.episodes = [
                {"title": "Episode 1", "url": "url1"},
                {"title": "Episode 2", "url": "url2"},
            ]

            # Assert
            assert webpage[0] == {"title": "Episode 1", "url": "url1"}
            assert webpage[1] == {"title": "Episode 2", "url": "url2"}

    def test_len_method(self):
        """Test de la méthode __len__"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data="")
        ), patch("nbs.web.BeautifulSoup"):

            from nbs.web import WebPage

            webpage = WebPage()

            # Test avec 0 épisodes
            assert len(webpage) == 0

            # Ajouter des épisodes
            webpage.episodes = [{"title": "Episode 1"}, {"title": "Episode 2"}]
            assert len(webpage) == 2

    def test_str_method(self):
        """Test de la méthode __str__"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data="")
        ), patch("nbs.web.BeautifulSoup"):

            from nbs.web import WebPage

            webpage = WebPage()

            # Test avec épisodes
            webpage.episodes = [
                {
                    "title": "Test Episode",
                    "url": "https://example.com",
                    "description": "Test description",
                    "date": "22 Dec 2024",
                    "duration": "60 min",
                }
            ]

            result = str(webpage)

            # Assert
            assert "Test Episode" in result
            assert "https://example.com" in result
            assert "Test description" in result
            assert "22 Dec 2024" in result
            assert "60 min" in result
            assert "Title:" in result
            assert "URL:" in result

    def test_str_method_empty(self):
        """Test de la méthode __str__ avec aucun épisode"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data="")
        ), patch("nbs.web.BeautifulSoup"):

            from nbs.web import WebPage

            webpage = WebPage()

            result = str(webpage)

            # Assert
            assert result == ""

    def test_repr_method(self):
        """Test de la méthode __repr__"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data="")
        ), patch("nbs.web.BeautifulSoup"):

            from nbs.web import WebPage

            webpage = WebPage()

            # Test que __repr__ retourne la même chose que __str__
            webpage.episodes = [
                {
                    "title": "Test",
                    "url": "url",
                    "description": "desc",
                    "date": "date",
                    "duration": "dur",
                }
            ]

            assert repr(webpage) == str(webpage)


class TestWebPageEdgeCases:
    """Tests pour les cas limites de WebPage"""

    def test_getitem_index_error(self):
        """Test de __getitem__ avec un index invalide"""
        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data="")
        ), patch("nbs.web.BeautifulSoup"):

            from nbs.web import WebPage

            webpage = WebPage()

            # Test avec index out of bounds
            with pytest.raises(IndexError):
                _ = webpage[0]

            with pytest.raises(IndexError):
                _ = webpage[99]

    def test_file_not_found_error(self):
        """Test quand le fichier HTML n'existe pas"""
        with patch(
            "nbs.web.get_WEB_filename", return_value="/tmp/nonexistent.html"
        ), patch("builtins.open", side_effect=FileNotFoundError("File not found")):

            from nbs.web import WebPage

            # Assert que l'exception est propagée
            with pytest.raises(FileNotFoundError):
                WebPage()

    def test_parsing_with_malformed_html(self):
        """Test avec du HTML malformé"""
        malformed_html = "<html><body><li class='wrong'>No proper structure"

        with patch("nbs.web.get_WEB_filename", return_value="/tmp/test.html"), patch(
            "builtins.open", mock_open(read_data=malformed_html)
        ), patch("nbs.web.BeautifulSoup") as mock_soup:

            # Mock BeautifulSoup pour gérer le HTML malformé
            mock_soup_instance = MagicMock()
            mock_soup.return_value = mock_soup_instance
            mock_soup_instance.find_all.return_value = []

            from nbs.web import WebPage

            webpage = WebPage()

            # Assert - aucun épisode trouvé avec HTML malformé
            assert len(webpage.episodes) == 0
