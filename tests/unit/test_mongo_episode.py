"""
Tests pour le module nbs.mongo_episode.

Ce module teste les fonctionnalités de gestion des épisodes incluant :
- Classe Episode (CRUD operations)
- RSS_episode et WEB_episode (parsing RSS et web)
- Episodes (collection d'épisodes)
- Fonctions utilitaires (prevent_sleep, extract_whisper)
- Constantes et formats de date
"""

import pytest
from unittest.mock import MagicMock, patch, call
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bson import ObjectId

# Configuration des variables d'environnement pour éviter les erreurs
import os

os.environ.setdefault("AUDIO_PATH", "/tmp/test_audio")

# Configuration du path pour les imports relatifs (compatible GitHub Actions)
import sys
from pathlib import Path

nbs_path = Path(__file__).parent.parent.parent / "nbs"
if str(nbs_path) not in sys.path:
    sys.path.insert(0, str(nbs_path))

# Mock des dépendances AVANT l'import du module pour éviter les erreurs
# Mocker torch et les autres dépendances ML qui ne sont pas disponibles dans GitHub Actions
mock_torch = MagicMock()
mock_torch.cuda.is_available.return_value = False
mock_torch.float32 = "float32"
mock_torch.float16 = "float16"

mock_transformers = MagicMock()
mock_datasets = MagicMock()
mock_dbus = MagicMock()

sys.modules["torch"] = mock_torch
sys.modules["transformers"] = mock_transformers
sys.modules["datasets"] = mock_datasets
sys.modules["dbus"] = mock_dbus
sys.modules["transformers.models"] = MagicMock()
sys.modules["transformers.models.auto"] = MagicMock()
sys.modules["transformers.models.auto.modeling_auto"] = MagicMock()
sys.modules["transformers.models.auto.processing_auto"] = MagicMock()

# Maintenant on peut importer le module mongo_episode
try:
    import nbs.mongo_episode as mongo_episode_module
except ImportError:
    import mongo_episode as mongo_episode_module


@pytest.fixture(autouse=True)
def mock_mongo_episode_dependencies():
    """Mock toutes les dépendances externes pour mongo_episode automatiquement"""
    # Configuration du mock config pour être compatible
    mock_config = MagicMock()
    mock_config.get_DB_VARS.return_value = ("localhost", "test_db", "true")
    mock_config.get_audio_path.return_value = "/tmp/test_audio"
    mock_config.AUDIO_PATH = "/tmp/test_audio"

    # Assurer que nbs.mongo_episode est disponible pour tous les imports
    if "nbs.mongo_episode" not in sys.modules:
        sys.modules["nbs.mongo_episode"] = mongo_episode_module

    # Mock pour whisper et ML
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.float32 = "float32"
    mock_torch.float16 = "float16"

    mock_transformers = MagicMock()
    mock_pipeline = MagicMock()
    mock_pipeline.return_value = MagicMock()

    with patch.dict(
        "sys.modules",
        {
            "mongo": MagicMock(),
            "config": mock_config,
            "torch": mock_torch,
            "transformers": mock_transformers,
            "dbus": MagicMock(),
            "llm": MagicMock(),
            "llama_index": MagicMock(),
            "llama_index.core": MagicMock(),
            "llama_index.core.llms": MagicMock(),
            "requests": MagicMock(),
        },
    ):
        yield


@pytest.fixture
def sample_episode_data():
    """Fixture pour les données d'épisode de test"""
    return {
        "date": "2024-12-22T09:59:39",
        "titre": "Test Episode - Victor Hugo",
        "description": "Discussion autour de l'œuvre de Victor Hugo",
        "url": "https://example.com/audio.mp3",
        "duree": 3600,  # 1 heure
        "type": "livre",
    }


class TestModuleConstants:
    """Tests pour les constantes du module"""

    def test_date_format_constants(self):
        """Test des constantes de format de date"""
        from nbs.mongo_episode import DATE_FORMAT, LOG_DATE_FORMAT

        # Assert
        assert DATE_FORMAT == "%Y-%m-%dT%H:%M:%S"
        assert LOG_DATE_FORMAT == "%d %b %Y %H:%M"
        assert isinstance(DATE_FORMAT, str)
        assert isinstance(LOG_DATE_FORMAT, str)

    def test_module_exports(self):
        """Test des exports __all__ du module"""
        from nbs import mongo_episode

        expected_exports = [
            "DATE_FORMAT",
            "LOG_DATE_FORMAT",
            "RSS_DUREE_MINI_MINUTES",
            "RSS_DATE_FORMAT",
            "WEB_DATE_FORMAT",
            "prevent_sleep",
            "extract_whisper",
            "Episode",
            "RSS_episode",
            "WEB_episode",
            "Episodes",
        ]

        # Assert
        assert mongo_episode.__all__ == expected_exports

        # Verify all exports exist
        for export in expected_exports:
            assert hasattr(mongo_episode, export), f"Missing export: {export}"


class TestPreventSleep:
    """Tests pour le décorateur prevent_sleep"""

    def test_prevent_sleep_decorator_structure(self):
        """Test que prevent_sleep est un décorateur valide"""
        from nbs.mongo_episode import prevent_sleep

        # Test function pour décorer
        @prevent_sleep
        def test_function():
            return "test_result"

        # Assert que la fonction est correctement décorée
        assert callable(test_function)
        assert hasattr(test_function, "__call__")

    def test_prevent_sleep_with_mock_dbus(self):
        """Test du décorateur avec mock D-Bus"""
        # Mock D-Bus components
        mock_bus = MagicMock()
        mock_proxy = MagicMock()
        mock_interface = MagicMock()
        mock_interface.Inhibit.return_value = "test_cookie"

        with patch("nbs.mongo_episode.dbus") as mock_dbus:
            mock_dbus.SessionBus.return_value = mock_bus
            mock_bus.get_object.return_value = mock_proxy
            mock_dbus.Interface.return_value = mock_interface

            from nbs.mongo_episode import prevent_sleep

            @prevent_sleep
            def test_function():
                return "success"

            result = test_function()

            # Assert
            assert result == "success"
            mock_interface.Inhibit.assert_called_once()
            mock_interface.UnInhibit.assert_called_once_with("test_cookie")


class TestExtractWhisper:
    """Tests pour la fonction extract_whisper"""

    def test_extract_whisper_basic_functionality(self):
        """Test de base de extract_whisper"""
        # Mock de la pipeline Whisper
        mock_result = {"text": "Transcription test de l'audio"}
        mock_pipe = MagicMock()
        mock_pipe.return_value = mock_result

        with patch("nbs.mongo_episode.pipeline", return_value=mock_pipe), patch(
            "nbs.mongo_episode.AutoModelForSpeechSeq2Seq"
        ) as mock_model, patch("nbs.mongo_episode.AutoProcessor") as mock_processor:

            from nbs.mongo_episode import extract_whisper

            result = extract_whisper("/path/to/test.mp3")

            # Assert
            assert result == "Transcription test de l'audio"
            # Vérifier que pipeline a été appelé avec les bons paramètres

    def test_extract_whisper_cuda_detection(self):
        """Test de la détection CUDA"""
        mock_pipe = MagicMock()
        mock_pipe.return_value = {"text": "test"}

        with patch("nbs.mongo_episode.torch") as mock_torch, patch(
            "nbs.mongo_episode.AutoModelForSpeechSeq2Seq"
        ) as mock_model, patch(
            "nbs.mongo_episode.AutoProcessor"
        ) as mock_processor, patch(
            "nbs.mongo_episode.pipeline", return_value=mock_pipe
        ):

            mock_torch.cuda.is_available.return_value = True
            mock_torch.float16 = "float16"
            mock_torch.float32 = "float32"

            from nbs.mongo_episode import extract_whisper

            extract_whisper("/path/to/test.mp3")

            # Assert que CUDA est détecté correctement
            assert mock_torch.cuda.is_available.called


@patch("nbs.mongo_episode.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
class TestEpisodeClass:
    """Tests pour la classe Episode"""

    def test_episode_initialization_new(self, mock_get_db_vars, sample_episode_data):
        """Test d'initialisation d'un nouvel épisode"""
        # Mock collection sans épisode existant
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            # Assert
            assert episode.titre == sample_episode_data["titre"]
            assert episode.description is None
            assert episode.url_telechargement is None
            assert episode.duree == -1

    def test_episode_initialization_existing(
        self, mock_get_db_vars, sample_episode_data
    ):
        """Test d'initialisation d'un épisode existant"""
        # Mock collection avec épisode existant
        mock_collection = MagicMock()
        existing_episode = {
            "description": sample_episode_data["description"],
            "url": sample_episode_data["url"],
            "duree": sample_episode_data["duree"],
            "type": sample_episode_data["type"],
            "audio_rel_filename": "test.mp3",
            "transcription": "Test transcription",
        }
        mock_collection.find_one.return_value = existing_episode

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            # Assert
            assert episode.titre == sample_episode_data["titre"]
            assert episode.description == sample_episode_data["description"]
            assert episode.url_telechargement == sample_episode_data["url"]
            assert episode.duree == sample_episode_data["duree"]

    def test_episode_exists_true(self, mock_get_db_vars, sample_episode_data):
        """Test exists() retourne True quand l'épisode existe"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"titre": "test"}

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            # Assert
            assert episode.exists() is True

    def test_episode_exists_false(self, mock_get_db_vars, sample_episode_data):
        """Test exists() retourne False quand l'épisode n'existe pas"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            # Assert
            assert episode.exists() is False

    def test_episode_from_oid(self, mock_get_db_vars, sample_episode_data):
        """Test de création d'épisode à partir d'ObjectId"""
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_document = {
            "date": datetime.strptime(sample_episode_data["date"], "%Y-%m-%dT%H:%M:%S"),
            "titre": sample_episode_data["titre"],
        }
        # Plusieurs appels : from_oid, __init__ (exists), __init__ (load data)
        mock_collection.find_one.side_effect = [
            mock_document,
            mock_document,
            mock_document,
        ]

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode.from_oid(test_oid)

            # Assert
            assert episode.titre == sample_episode_data["titre"]
            # Vérifier qu'au moins un appel a été fait avec le bon ObjectId
            assert any(
                call.args[0] == {"_id": test_oid}
                for call in mock_collection.find_one.call_args_list
            )

    def test_episode_get_oid_success(self, mock_get_db_vars, sample_episode_data):
        """Test get_oid() retourne l'ObjectId correct"""
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = [
            None,  # Premier appel pour exists()
            {"_id": test_oid},  # Deuxième appel pour get_oid()
        ]

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            oid = episode.get_oid()

            # Assert
            assert oid == test_oid

    def test_episode_get_oid_not_found(self, mock_get_db_vars, sample_episode_data):
        """Test get_oid() retourne None si non trouvé"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            oid = episode.get_oid()

            # Assert
            assert oid is None


class TestEpisodeStaticMethods:
    """Tests pour les méthodes statiques de Episode"""

    def test_get_date_from_string(self):
        """Test de conversion string vers datetime"""
        from nbs.mongo_episode import Episode

        date_str = "2024-12-22T09:59:39"
        result = Episode.get_date_from_string(date_str)

        # Assert
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 22
        assert result.hour == 9
        assert result.minute == 59
        assert result.second == 39

    def test_get_string_from_date(self):
        """Test de conversion datetime vers string"""
        from nbs.mongo_episode import Episode

        date_obj = datetime(2024, 12, 22, 9, 59, 39)
        result = Episode.get_string_from_date(date_obj)

        # Assert
        assert result == "2024-12-22T09:59:39"

    def test_get_string_from_date_custom_format(self):
        """Test de conversion datetime vers string avec format personnalisé"""
        from nbs.mongo_episode import Episode

        date_obj = datetime(2024, 12, 22, 9, 59, 39)
        result = Episode.get_string_from_date(date_obj, format="%d/%m/%Y")

        # Assert
        assert result == "22/12/2024"

    def test_format_duration(self):
        """Test de formatage de durée"""
        from nbs.mongo_episode import Episode

        # Test différentes durées
        assert Episode.format_duration(3661) == "01:01:01"  # 1h 1min 1sec
        assert Episode.format_duration(3600) == "01:00:00"  # 1h exact
        assert Episode.format_duration(61) == "00:01:01"  # 1min 1sec
        assert Episode.format_duration(0) == "00:00:00"  # 0


@patch("nbs.mongo_episode.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
class TestEpisodeCRUDOperations:
    """Tests pour les opérations CRUD de Episode"""

    def test_episode_keep_new_episode(self, mock_get_db_vars, sample_episode_data):
        """Test keep() pour un nouvel épisode"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None  # Épisode n'existe pas
        mock_collection.insert_one.return_value.inserted_id = ObjectId()

        with patch(
            "nbs.mongo_episode.get_collection", return_value=mock_collection
        ), patch("nbs.mongo_episode.mongolog") as mock_mongolog:

            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            # Mock download_audio pour éviter le téléchargement réel
            episode.download_audio = MagicMock()
            episode.description = sample_episode_data["description"]
            episode.url_telechargement = sample_episode_data["url"]
            episode.duree = sample_episode_data["duree"]
            episode.type = sample_episode_data["type"]
            episode.audio_rel_filename = "test.mp3"
            episode.transcription = "test transcription"

            result = episode.keep()

            # Assert
            assert result == 1
            episode.download_audio.assert_called_once_with(verbose=True)
            mock_collection.insert_one.assert_called_once()
            mock_mongolog.assert_called_once()

    def test_episode_remove(self, mock_get_db_vars, sample_episode_data):
        """Test remove() supprime l'épisode"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch(
            "nbs.mongo_episode.get_collection", return_value=mock_collection
        ), patch("nbs.mongo_episode.mongolog") as mock_mongolog:

            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )

            episode.remove()

            # Assert
            mock_collection.delete_one.assert_called_once()
            mock_mongolog.assert_called_once()

    def test_episode_update_date(self, mock_get_db_vars, sample_episode_data):
        """Test update_date() met à jour la date"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch(
            "nbs.mongo_episode.get_collection", return_value=mock_collection
        ), patch("nbs.mongo_episode.mongolog") as mock_mongolog:

            from nbs.mongo_episode import Episode

            episode = Episode(
                date=sample_episode_data["date"], titre=sample_episode_data["titre"]
            )
            episode.get_oid = MagicMock(return_value=ObjectId())

            new_date = datetime(2025, 1, 1, 10, 0, 0)
            episode.update_date(new_date)

            # Assert
            assert episode.date == new_date
            mock_collection.update_one.assert_called_once()
            mock_mongolog.assert_called_once()


@patch("nbs.mongo_episode.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
class TestEpisodeClassMethods:
    """Tests pour les méthodes de classe de Episode"""

    def test_episode_from_date_found(self, mock_get_db_vars, sample_episode_data):
        """Test from_date() trouve un épisode"""
        mock_collection = MagicMock()
        test_date = datetime(2024, 12, 22, 9, 59, 39)
        mock_document = {"date": test_date, "titre": sample_episode_data["titre"]}
        mock_collection.find_one.return_value = mock_document

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            result = Episode.from_date(test_date)

            # Assert
            assert result is not None
            assert result.titre == sample_episode_data["titre"]

    def test_episode_from_date_not_found(self, mock_get_db_vars):
        """Test from_date() ne trouve pas d'épisode"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch("nbs.mongo_episode.get_collection", return_value=mock_collection):
            from nbs.mongo_episode import Episode

            test_date = datetime(2024, 12, 22)
            result = Episode.from_date(test_date)

            # Assert
            assert result is None
