"""
Tests pour le module nbs/rss.py (T020)
Testing complet des fonctions RSS et classe Podcast avec mocking HTTP/DB
"""

import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import pytz
import sys
import os


# Mock all external dependencies at module level
@pytest.fixture(autouse=True)
def mock_external_imports():
    """Mock toutes les dépendances externes automatiquement pour tous les tests"""
    with patch.dict(
        "sys.modules",
        {
            "feedparser": MagicMock(),
            "feedparser.util": MagicMock(),
            "pymongo": MagicMock(),
            "pymongo.collection": MagicMock(),
            "pymongo.errors": MagicMock(),
            "mongo_episode": MagicMock(),
            "mongo": MagicMock(),
            "config": MagicMock(),
            # Notez: pytz n'est plus mocké ici pour permettre l'utilisation de vraies timezones
        },
    ):
        yield


# Configuration du path pour importer nos modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../nbs"))


class TestExtraireDureeSummary:
    """Tests pour la fonction extraire_dureesummary"""

    def test_extraire_duree_format_standard(self):
        """Test extraire_dureesummary avec format durée standard"""
        # Import du module après le mocking
        from rss import extraire_dureesummary

        # Arrange
        summary = (
            "Episode du Masque et la Plume - durée : 58:42:00 - avec François Busnel"
        )

        # Act
        result = extraire_dureesummary(summary)

        # Assert
        expected = 58 * 3600 + 42 * 60 + 0  # 211320 seconds
        assert result == expected

    def test_extraire_duree_format_court(self):
        """Test extraire_dureesummary avec durée courte"""
        # Import du module après le mocking
        from rss import extraire_dureesummary

        # Arrange
        summary = "Courte émission - durée : 12:35:45"

        # Act
        result = extraire_dureesummary(summary)

        # Assert
        expected = 12 * 3600 + 35 * 60 + 45  # 45345 seconds
        assert result == expected

    def test_extraire_duree_espaces_variables(self):
        """Test extraire_dureesummary avec espaces variables autour du ':'"""
        # Import du module après le mocking
        from rss import extraire_dureesummary

        # Arrange
        summary = "Emission spéciale - durée    :   01:23:45 - invités"

        # Act
        result = extraire_dureesummary(summary)

        # Assert
        expected = 1 * 3600 + 23 * 60 + 45  # 5025 seconds
        assert result == expected

    def test_extraire_duree_non_trouvee(self):
        """Test extraire_dureesummary quand aucune durée n'est trouvée"""
        # Import du module après le mocking
        from rss import extraire_dureesummary

        # Arrange
        summary = "Episode sans indication de durée"

        # Act
        result = extraire_dureesummary(summary)

        # Assert
        assert result == -1

    def test_extraire_duree_format_invalide(self):
        """Test extraire_dureesummary avec format invalide"""
        # Import du module après le mocking
        from rss import extraire_dureesummary

        # Arrange
        summary = "Episode avec durée: 1h30m - format non standard"

        # Act
        result = extraire_dureesummary(summary)

        # Assert
        assert result == -1

    def test_extraire_duree_string_vide(self):
        """Test extraire_dureesummary avec string vide"""
        # Import du module après le mocking
        from rss import extraire_dureesummary

        # Arrange
        summary = ""

        # Act
        result = extraire_dureesummary(summary)

        # Assert
        assert result == -1


class TestExtraireUrlsRss:
    """Tests pour la fonction extraire_urls_rss"""

    @patch("rss.feedparser.parse")
    @patch("rss.get_RSS_URL")
    @patch("rss.extraire_dureesummary")
    def test_extraire_urls_rss_episodes_longs(
        self, mock_duree, mock_get_url, mock_parse
    ):
        """Test extraire_urls_rss avec épisodes longs"""
        # Import du module après le mocking
        from rss import extraire_urls_rss

        # Arrange
        mock_get_url.return_value = "https://test.rss.url"
        mock_duree.side_effect = [1800, 600, 2400]  # 30min, 10min, 40min

        # Mock feedparser response
        mock_entry1 = MagicMock()
        mock_entry1.summary = "Episode 1 - durée : 30:00:00"
        mock_entry1.links = [MagicMock(type="audio/mpeg", href="https://audio1.mp3")]

        mock_entry2 = MagicMock()
        mock_entry2.summary = "Episode 2 - durée : 10:00:00"
        mock_entry2.links = [MagicMock(type="audio/mpeg", href="https://audio2.mp3")]

        mock_entry3 = MagicMock()
        mock_entry3.summary = "Episode 3 - durée : 40:00:00"
        mock_entry3.links = [MagicMock(type="audio/mpeg", href="https://audio3.mp3")]

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry1, mock_entry2, mock_entry3]
        mock_parse.return_value = mock_feed

        # Act
        result = extraire_urls_rss(duree_mini_minutes=15)

        # Assert
        assert len(result) == 2  # Episodes 1 et 3 (> 15 minutes)
        assert "https://audio1.mp3" in result
        assert "https://audio3.mp3" in result
        assert "https://audio2.mp3" not in result  # Trop court
        mock_get_url.assert_called_once()
        mock_parse.assert_called_once_with("https://test.rss.url")

    @patch("rss.feedparser.parse")
    @patch("rss.get_RSS_URL")
    @patch("rss.extraire_dureesummary")
    def test_extraire_urls_rss_aucun_episode_long(
        self, mock_duree, mock_get_url, mock_parse
    ):
        """Test extraire_urls_rss quand aucun épisode n'est assez long"""
        # Import du module après le mocking
        from rss import extraire_urls_rss

        # Arrange
        mock_get_url.return_value = "https://test.rss.url"
        mock_duree.return_value = 600  # 10 minutes

        mock_entry = MagicMock()
        mock_entry.summary = "Episode court"
        mock_entry.links = [MagicMock(type="audio/mpeg", href="https://audio.mp3")]

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        # Act
        result = extraire_urls_rss(duree_mini_minutes=15)

        # Assert
        assert result == []

    @patch("rss.feedparser.parse")
    @patch("rss.get_RSS_URL")
    def test_extraire_urls_rss_types_non_audio(self, mock_get_url, mock_parse):
        """Test extraire_urls_rss avec liens non-audio"""
        # Import du module après le mocking
        from rss import extraire_urls_rss

        # Arrange
        mock_get_url.return_value = "https://test.rss.url"

        mock_entry = MagicMock()
        mock_entry.summary = "Episode avec liens divers"
        mock_entry.links = [
            MagicMock(type="text/html", href="https://web.html"),
            MagicMock(type="image/jpeg", href="https://image.jpg"),
        ]

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        # Act
        with patch("rss.extraire_dureesummary", return_value=1800):
            result = extraire_urls_rss(duree_mini_minutes=15)

        # Assert
        assert result == []  # Aucun lien audio/mpeg

    @patch("rss.feedparser.parse")
    @patch("rss.get_RSS_URL")
    def test_extraire_urls_rss_flux_vide(self, mock_get_url, mock_parse):
        """Test extraire_urls_rss avec flux RSS vide"""
        # Import du module après le mocking
        from rss import extraire_urls_rss

        # Arrange
        mock_get_url.return_value = "https://test.rss.url"
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed

        # Act
        result = extraire_urls_rss()

        # Assert
        assert result == []


class TestPodcastInit:
    """Tests pour l'initialisation de la classe Podcast"""

    @patch("rss.get_collection")
    @patch("rss.get_DB_VARS")
    @patch("rss.feedparser.parse")
    @patch("rss.get_RSS_URL")
    def test_podcast_init_success(
        self, mock_get_url, mock_parse, mock_get_db_vars, mock_get_collection
    ):
        """Test initialisation Podcast réussie"""
        # Import du module après le mocking
        from rss import Podcast

        # Arrange
        mock_get_url.return_value = "https://test.rss.url"
        mock_parse.return_value = MagicMock(name="parsed_feed")
        mock_get_db_vars.return_value = ("localhost", "testdb", None)
        mock_collection = MagicMock(name="test_collection")
        mock_get_collection.return_value = mock_collection

        # Act
        podcast = Podcast()

        # Assert
        assert podcast.parsed_flow is not None
        assert podcast.collection == mock_collection
        mock_get_url.assert_called_once()
        mock_parse.assert_called_once_with("https://test.rss.url")
        mock_get_db_vars.assert_called_once()
        mock_get_collection.assert_called_once_with(
            target_db="localhost", client_name="testdb", collection_name="episodes"
        )

    @patch("rss.get_collection")
    @patch("rss.get_DB_VARS")
    @patch("rss.feedparser.parse")
    @patch("rss.get_RSS_URL")
    def test_podcast_init_with_errors(
        self, mock_get_url, mock_parse, mock_get_db_vars, mock_get_collection
    ):
        """Test initialisation Podcast avec erreur de connexion"""
        # Import du module après le mocking
        from rss import Podcast

        # Arrange
        mock_get_url.return_value = "https://test.rss.url"
        mock_parse.return_value = MagicMock(name="parsed_feed")
        mock_get_db_vars.return_value = ("localhost", "testdb", None)
        mock_get_collection.side_effect = Exception("DB connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="DB connection failed"):
            Podcast()


class TestPodcastGetMostRecentEpisode:
    """Tests pour get_most_recent_episode_from_DB"""

    def test_get_most_recent_episode_found(self):
        """Test get_most_recent_episode_from_DB avec épisode trouvé"""
        # Import du module après le mocking
        from rss import Podcast

        with patch("rss.get_collection") as mock_get_collection, patch(
            "rss.get_DB_VARS"
        ) as mock_get_db_vars, patch("rss.feedparser.parse") as mock_parse, patch(
            "rss.get_RSS_URL"
        ) as mock_get_url:

            # Arrange
            mock_get_url.return_value = "https://test.rss.url"
            mock_parse.return_value = MagicMock()
            mock_get_db_vars.return_value = ("localhost", "testdb", None)

            # Mock collection and cursor avec une date sans timezone (plus simple)
            test_date = datetime(2025, 1, 15, 10, 30, 0)
            mock_doc = {"date": test_date}
            mock_cursor = [mock_doc]

            mock_collection = MagicMock()
            mock_collection.find.return_value.sort.return_value.limit.return_value = (
                mock_cursor
            )
            mock_get_collection.return_value = mock_collection

            # Act
            podcast = Podcast()
            result = podcast.get_most_recent_episode_from_DB()

            # Assert
            assert result is not None
            assert result.year == 2025
            assert result.month == 1
            assert result.day == 15
            # Vérifier que la timezone est ajoutée
            assert result.tzinfo is not None
            mock_collection.find.assert_called_once()
            mock_collection.find.return_value.sort.assert_called_once_with({"date": -1})
            mock_collection.find.return_value.sort.return_value.limit.assert_called_once_with(
                1
            )

    def test_get_most_recent_episode_not_found(self):
        """Test get_most_recent_episode_from_DB sans épisode"""
        # Import du module après le mocking
        from rss import Podcast

        with patch("rss.get_collection") as mock_get_collection, patch(
            "rss.get_DB_VARS"
        ) as mock_get_db_vars, patch("rss.feedparser.parse") as mock_parse, patch(
            "rss.get_RSS_URL"
        ) as mock_get_url:

            # Arrange
            mock_get_url.return_value = "https://test.rss.url"
            mock_parse.return_value = MagicMock()
            mock_get_db_vars.return_value = ("localhost", "testdb", None)

            # Mock empty cursor
            mock_cursor = []
            mock_collection = MagicMock()
            mock_collection.find.return_value.sort.return_value.limit.return_value = (
                mock_cursor
            )
            mock_get_collection.return_value = mock_collection

            # Act
            podcast = Podcast()
            result = podcast.get_most_recent_episode_from_DB()

            # Assert
            assert result is None


class TestPodcastListLastLargeEpisodes:
    """Tests pour list_last_large_episodes"""

    def test_list_last_large_episodes_with_new_episodes(self):
        """Test list_last_large_episodes avec nouveaux épisodes longs"""
        # Import du module après le mocking
        from rss import Podcast, RSS_DATE_FORMAT

        with patch("rss.get_collection") as mock_get_collection, patch(
            "rss.get_DB_VARS"
        ) as mock_get_db_vars, patch("rss.feedparser.parse") as mock_parse, patch(
            "rss.get_RSS_URL"
        ) as mock_get_url, patch(
            "rss.RSS_episode"
        ) as mock_rss_episode:

            # Arrange
            mock_get_url.return_value = "https://test.rss.url"
            mock_get_db_vars.return_value = ("localhost", "testdb", None)
            mock_get_collection.return_value = MagicMock()

            # Mock entries in RSS feed
            entry1 = MagicMock()
            entry1.published = "Mon, 20 Jan 2025 15:00:00 +0100"
            entry1.itunes_duration = "58:42:00"

            entry2 = MagicMock()
            entry2.published = "Tue, 21 Jan 2025 16:00:00 +0100"
            entry2.itunes_duration = "12:30:00"  # Court

            entry3 = MagicMock()
            entry3.published = "Wed, 22 Jan 2025 17:00:00 +0100"
            entry3.itunes_duration = "45:15:00"

            mock_parsed_flow = MagicMock()
            mock_parsed_flow.entries = [entry1, entry2, entry3]
            mock_parse.return_value = mock_parsed_flow

            # Mock RSS_episode.get_duree_in_seconds
            # Les durées doivent être en secondes, et nous testons avec duree_mini_minutes=15 (900 secondes)
            mock_rss_episode.get_duree_in_seconds.side_effect = [
                58 * 60
                + 42,  # 58:42:00 -> 58 minutes 42 secondes = 3522 (> 900, donc long)
                12 * 60
                + 30,  # 12:30:00 -> 12 minutes 30 secondes = 750 (< 900, donc court)
                45 * 60
                + 15,  # 45:15:00 -> 45 minutes 15 secondes = 2715 (> 900, donc long)
            ]

            # Act
            podcast = Podcast()

            # Mock get_most_recent_episode_from_DB pour retourner une date antérieure
            with patch.object(
                podcast, "get_most_recent_episode_from_DB"
            ) as mock_get_recent:
                import pytz

                mock_get_recent.return_value = datetime(
                    2025, 1, 19, 12, 0, 0, tzinfo=pytz.timezone("Europe/Paris")
                )
                result = podcast.list_last_large_episodes(duree_mini_minutes=15)

            # Assert
            assert len(result) == 2  # entry1 et entry3 (longs et récents)
            assert entry1 in result
            assert entry3 in result
            assert entry2 not in result  # Trop court

    def test_list_last_large_episodes_no_db_date(self):
        """Test list_last_large_episodes quand pas de date en DB"""
        # Import du module après le mocking
        from rss import Podcast

        with patch("rss.get_collection") as mock_get_collection, patch(
            "rss.get_DB_VARS"
        ) as mock_get_db_vars, patch("rss.feedparser.parse") as mock_parse, patch(
            "rss.get_RSS_URL"
        ) as mock_get_url:

            # Arrange
            mock_get_url.return_value = "https://test.rss.url"
            mock_get_db_vars.return_value = ("localhost", "testdb", None)
            mock_get_collection.return_value = MagicMock()
            mock_parse.return_value = MagicMock(entries=[])

            # Act
            podcast = Podcast()

            with patch.object(
                podcast, "get_most_recent_episode_from_DB"
            ) as mock_get_recent:
                mock_get_recent.return_value = None  # Aucune date en DB
                result = podcast.list_last_large_episodes()

            # Assert
            assert result == []  # Aucun épisode car pas de référence temporelle


class TestPodcastStoreLastLargeEpisodes:
    """Tests pour store_last_large_episodes"""

    def test_store_last_large_episodes_success(self):
        """Test store_last_large_episodes avec succès"""
        # Import du module après le mocking
        from rss import Podcast

        with patch("rss.get_collection") as mock_get_collection, patch(
            "rss.get_DB_VARS"
        ) as mock_get_db_vars, patch("rss.feedparser.parse") as mock_parse, patch(
            "rss.get_RSS_URL"
        ) as mock_get_url, patch(
            "rss.RSS_episode"
        ) as mock_rss_episode, patch(
            "builtins.print"
        ) as mock_print:

            # Arrange
            mock_get_url.return_value = "https://test.rss.url"
            mock_get_db_vars.return_value = ("localhost", "testdb", None)
            mock_get_collection.return_value = MagicMock()
            mock_parse.return_value = MagicMock()

            # Mock episodes list
            mock_entry1 = MagicMock()
            mock_entry2 = MagicMock()
            episodes_list = [mock_entry1, mock_entry2]

            # Mock RSS_episode instances
            mock_rss_instance1 = MagicMock()
            mock_rss_instance1.keep.return_value = 1  # Success
            mock_rss_instance2 = MagicMock()
            mock_rss_instance2.keep.return_value = 1  # Success

            mock_rss_episode.from_feed_entry.side_effect = [
                mock_rss_instance1,
                mock_rss_instance2,
            ]

            # Act
            podcast = Podcast()

            with patch.object(podcast, "list_last_large_episodes") as mock_list:
                mock_list.return_value = episodes_list
                podcast.store_last_large_episodes(duree_mini_minutes=20)

            # Assert
            mock_list.assert_called_once_with(20)
            assert mock_rss_episode.from_feed_entry.call_count == 2
            mock_rss_episode.from_feed_entry.assert_any_call(mock_entry1)
            mock_rss_episode.from_feed_entry.assert_any_call(mock_entry2)
            mock_rss_instance1.keep.assert_called_once()
            mock_rss_instance2.keep.assert_called_once()
            mock_print.assert_called_once_with("Updated episodes: 2")

    def test_store_last_large_episodes_no_updates(self):
        """Test store_last_large_episodes sans mises à jour"""
        # Import du module après le mocking
        from rss import Podcast

        with patch("rss.get_collection") as mock_get_collection, patch(
            "rss.get_DB_VARS"
        ) as mock_get_db_vars, patch("rss.feedparser.parse") as mock_parse, patch(
            "rss.get_RSS_URL"
        ) as mock_get_url, patch(
            "builtins.print"
        ) as mock_print:

            # Arrange
            mock_get_url.return_value = "https://test.rss.url"
            mock_get_db_vars.return_value = ("localhost", "testdb", None)
            mock_get_collection.return_value = MagicMock()
            mock_parse.return_value = MagicMock()

            # Act
            podcast = Podcast()

            with patch.object(podcast, "list_last_large_episodes") as mock_list:
                mock_list.return_value = []  # Aucun épisode
                podcast.store_last_large_episodes()

            # Assert
            mock_print.assert_called_once_with("Updated episodes: 0")


class TestRSSConstantsAndImports:
    """Tests pour les constantes et imports du module RSS"""

    def test_rss_date_format_constant(self):
        """Test que la constante RSS_DATE_FORMAT est correctement définie"""
        # Import du module après le mocking
        from rss import RSS_DATE_FORMAT

        # Assert
        assert RSS_DATE_FORMAT == "%a, %d %b %Y %H:%M:%S %z"

        # Test que le format fonctionne avec un exemple
        test_date_str = "Sun, 29 Dec 2024 10:59:39 +0100"
        parsed_date = datetime.strptime(test_date_str, RSS_DATE_FORMAT)
        assert parsed_date.year == 2024
        assert parsed_date.month == 12
        assert parsed_date.day == 29

    def test_module_all_exports(self):
        """Test que les exports __all__ sont corrects"""
        # Import du module après le mocking
        import rss

        # Assert
        expected_exports = [
            "RSS_DATE_FORMAT",
            "extraire_dureesummary",
            "extraire_urls_rss",
            "Podcast",
        ]
        assert rss.__all__ == expected_exports

        # Verify all exported items exist
        for export in expected_exports:
            assert hasattr(rss, export), f"Missing export: {export}"
