"""
Tests pour le module nbs.whisper.

Ce module teste les fonctionnalités de transcription audio avec Whisper incluant :
- Constantes et configuration (AUDIO_PATH)
- Listing de fichiers audio (list_mp3_files, list_audio_files)
- Transcription avec Whisper (extract_whisper)
- Stockage en base de données (store_whisper_in_db)
"""

import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os
from typing import List
from bson import ObjectId

# Configuration des variables d'environnement pour éviter les erreurs
os.environ.setdefault("AUDIO_PATH", "/tmp/test_audio")

# Ajouter le répertoire nbs au path pour permettre les imports relatifs
from pathlib import Path

nbs_path = Path(__file__).parent.parent.parent / "nbs"
if str(nbs_path) not in sys.path:
    sys.path.insert(0, str(nbs_path))

# Mock des dépendances ML AVANT toute importation pour GitHub Actions
mock_torch = MagicMock()
mock_torch.cuda.is_available.return_value = False
mock_torch.float32 = "float32"
mock_torch.float16 = "float16"

mock_transformers = MagicMock()
mock_datasets = MagicMock()
mock_pymongo = MagicMock()

sys.modules["torch"] = mock_torch
sys.modules["transformers"] = mock_transformers
sys.modules["datasets"] = mock_datasets
sys.modules["pymongo"] = mock_pymongo


@pytest.fixture(autouse=True)
def mock_whisper_dependencies():
    """Mock toutes les dépendances externes pour whisper automatiquement"""
    # Mock pour mongo_episode
    mock_mongo_episode = MagicMock()
    mock_mongo_episode.get_audio_path.return_value = "/test/audio/path"

    # Mock pour les modules ML lourds
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.float32 = "float32"
    mock_torch.float16 = "float16"

    mock_transformers = MagicMock()
    mock_datasets = MagicMock()
    mock_pymongo = MagicMock()

    with patch.dict(
        "sys.modules",
        {
            "mongo_episode": mock_mongo_episode,
            "torch": mock_torch,
            "transformers": mock_transformers,
            "datasets": mock_datasets,
            "pymongo": mock_pymongo,
            "bson": MagicMock(),
        },
    ):
        yield {
            "mongo_episode": mock_mongo_episode,
            "torch": mock_torch,
            "transformers": mock_transformers,
            "datasets": mock_datasets,
            "pymongo": mock_pymongo,
        }


# Importation du module à tester après le mock
@pytest.fixture
def whisper_module(mock_whisper_dependencies):
    """Import du module whisper avec les dépendances mockées"""
    import whisper

    return whisper


class TestWhisperConstants:
    """Tests pour les constantes du module whisper"""

    def test_audio_path_constant(self, whisper_module):
        """Test que la constante AUDIO_PATH est définie correctement"""
        assert hasattr(whisper_module, "AUDIO_PATH")
        assert whisper_module.AUDIO_PATH == "audios"

    def test_module_exports(self, whisper_module):
        """Test que toutes les fonctions attendues sont exportées"""
        expected_exports = [
            "AUDIO_PATH",
            "list_mp3_files",
            "list_audio_files",
            "extract_whisper",
            "store_whisper_in_db",
        ]

        for export in expected_exports:
            assert hasattr(whisper_module, export)


class TestListMp3Files:
    """Tests pour la fonction list_mp3_files"""

    @patch("glob.glob")
    @patch("os.path.join")
    def test_list_mp3_files_default_path(
        self, mock_join, mock_glob, whisper_module, mock_whisper_dependencies
    ):
        """Test list_mp3_files avec le chemin par défaut"""
        # Configuration des mocks
        mock_join.return_value = "/test/audio/path/**/*.mp3"
        mock_glob.return_value = [
            "/test/audio/path/file1.mp3",
            "/test/audio/path/file2.mp3",
        ]

        # Appel de la fonction
        result = whisper_module.list_mp3_files()

        # Vérifications
        mock_whisper_dependencies[
            "mongo_episode"
        ].get_audio_path.assert_called_once_with("audios", year="")
        mock_join.assert_called_once_with("/test/audio/path", "**/*.mp3")
        mock_glob.assert_called_once_with("/test/audio/path/**/*.mp3", recursive=True)
        assert result == ["/test/audio/path/file1.mp3", "/test/audio/path/file2.mp3"]

    @patch("glob.glob")
    @patch("os.path.join")
    def test_list_mp3_files_custom_path(
        self, mock_join, mock_glob, whisper_module, mock_whisper_dependencies
    ):
        """Test list_mp3_files avec un chemin personnalisé"""
        # Configuration des mocks
        mock_join.return_value = "/test/custom/path/**/*.mp3"
        mock_glob.return_value = ["/test/custom/path/custom.mp3"]

        # Appel de la fonction avec un chemin personnalisé
        result = whisper_module.list_mp3_files("/custom/audio")

        # Vérifications
        mock_whisper_dependencies[
            "mongo_episode"
        ].get_audio_path.assert_called_once_with("/custom/audio", year="")
        mock_join.assert_called_once_with("/test/audio/path", "**/*.mp3")
        mock_glob.assert_called_once_with("/test/custom/path/**/*.mp3", recursive=True)
        assert result == ["/test/custom/path/custom.mp3"]

    @patch("glob.glob")
    @patch("os.path.join")
    def test_list_mp3_files_empty_result(self, mock_join, mock_glob, whisper_module):
        """Test list_mp3_files quand aucun fichier n'est trouvé"""
        # Configuration des mocks
        mock_join.return_value = "/test/audio/path/**/*.mp3"
        mock_glob.return_value = []

        # Appel de la fonction
        result = whisper_module.list_mp3_files()

        # Vérifications
        assert result == []


class TestListAudioFiles:
    """Tests pour la fonction list_audio_files"""

    @patch("glob.glob")
    @patch("os.path.join")
    def test_list_audio_files_both_formats(
        self, mock_join, mock_glob, whisper_module, mock_whisper_dependencies
    ):
        """Test list_audio_files avec des fichiers MP3 et M4A"""
        # Configuration des mocks pour les deux appels glob
        mp3_files = ["/test/audio/path/file1.mp3", "/test/audio/path/file2.mp3"]
        m4a_files = ["/test/audio/path/file1.m4a", "/test/audio/path/file2.m4a"]

        def mock_join_side_effect(path, pattern):
            return f"{path}/{pattern}"

        def mock_glob_side_effect(pattern, recursive=True):
            if pattern.endswith("*.mp3"):
                return mp3_files
            elif pattern.endswith("*.m4a"):
                return m4a_files
            return []

        mock_join.side_effect = mock_join_side_effect
        mock_glob.side_effect = mock_glob_side_effect

        # Appel de la fonction
        result = whisper_module.list_audio_files()

        # Vérifications
        mock_whisper_dependencies[
            "mongo_episode"
        ].get_audio_path.assert_called_once_with("audios", year="")
        assert mock_join.call_count == 2
        assert mock_glob.call_count == 2
        expected_result = mp3_files + m4a_files
        assert result == expected_result

    @patch("glob.glob")
    @patch("os.path.join")
    def test_list_audio_files_custom_path(
        self, mock_join, mock_glob, whisper_module, mock_whisper_dependencies
    ):
        """Test list_audio_files avec un chemin personnalisé"""
        # Configuration des mocks
        mock_join.side_effect = lambda path, pattern: f"{path}/{pattern}"
        mock_glob.return_value = ["/test/custom/audio.mp3"]

        # Appel de la fonction avec un chemin personnalisé
        result = whisper_module.list_audio_files("/custom/audio")

        # Vérifications
        mock_whisper_dependencies[
            "mongo_episode"
        ].get_audio_path.assert_called_once_with("/custom/audio", year="")
        assert result == [
            "/test/custom/audio.mp3",
            "/test/custom/audio.mp3",
        ]  # MP3 + M4A (même mock)

    @patch("glob.glob")
    @patch("os.path.join")
    def test_list_audio_files_empty_result(self, mock_join, mock_glob, whisper_module):
        """Test list_audio_files quand aucun fichier n'est trouvé"""
        # Configuration des mocks
        mock_join.side_effect = lambda path, pattern: f"{path}/{pattern}"
        mock_glob.return_value = []

        # Appel de la fonction
        result = whisper_module.list_audio_files()

        # Vérifications
        assert result == []


class TestExtractWhisper:
    """Tests pour la fonction extract_whisper"""

    @patch("datasets.load_dataset")
    def test_extract_whisper_cpu_mode(
        self, mock_load_dataset, whisper_module, mock_whisper_dependencies
    ):
        """Test extract_whisper en mode CPU"""
        # Configuration des mocks
        mock_torch = mock_whisper_dependencies["torch"]
        mock_torch.cuda.is_available.return_value = False

        mock_transformers = mock_whisper_dependencies["transformers"]
        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.return_value = (
            mock_model
        )
        mock_transformers.AutoProcessor.from_pretrained.return_value = mock_processor
        mock_transformers.pipeline.return_value = MagicMock()
        mock_transformers.pipeline.return_value.return_value = {
            "text": "Test transcription"
        }

        mock_dataset = MagicMock()
        mock_dataset[0] = {"audio": "mock_audio_data"}
        mock_load_dataset.return_value = mock_dataset

        # Appel de la fonction
        result = whisper_module.extract_whisper("/test/audio.mp3")

        # Vérifications
        mock_torch.cuda.is_available.assert_called()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.assert_called_once()
        mock_transformers.AutoProcessor.from_pretrained.assert_called_once()
        mock_model.to.assert_called_once_with("cpu")
        assert result == "Test transcription"

    @patch("datasets.load_dataset")
    def test_extract_whisper_cuda_mode(
        self, mock_load_dataset, whisper_module, mock_whisper_dependencies
    ):
        """Test extract_whisper en mode CUDA"""
        # Configuration des mocks
        mock_torch = mock_whisper_dependencies["torch"]
        mock_torch.cuda.is_available.return_value = True

        mock_transformers = mock_whisper_dependencies["transformers"]
        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.return_value = (
            mock_model
        )
        mock_transformers.AutoProcessor.from_pretrained.return_value = mock_processor
        mock_transformers.pipeline.return_value = MagicMock()
        mock_transformers.pipeline.return_value.return_value = {
            "text": "Test transcription CUDA"
        }

        mock_dataset = MagicMock()
        mock_dataset[0] = {"audio": "mock_audio_data"}
        mock_load_dataset.return_value = mock_dataset

        # Appel de la fonction
        result = whisper_module.extract_whisper("/test/audio_cuda.mp3")

        # Vérifications
        mock_torch.cuda.is_available.assert_called()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.assert_called_once()
        mock_model.to.assert_called_once_with("cuda:0")
        assert result == "Test transcription CUDA"


class TestStoreWhisperInDb:
    """Tests pour la fonction store_whisper_in_db"""

    def test_store_whisper_new_document(self, whisper_module):
        """Test store_whisper_in_db pour un nouveau document"""
        # Configuration des mocks
        mock_collection = MagicMock()
        test_oid = str(ObjectId())
        mock_document = {"_id": ObjectId(test_oid), "title": "Test Episode"}
        mock_collection.find_one.return_value = mock_document

        # Appel de la fonction
        result = whisper_module.store_whisper_in_db(
            whisper="Test transcription",
            collection=mock_collection,
            oid=test_oid,
            verbose=True,
        )

        # Vérifications
        assert result is True
        mock_collection.find_one.assert_called_once()
        mock_collection.update_one.assert_called_once()

        # Vérifier que le whisper a été ajouté au document (sans vérifier l'ObjectId exact)
        update_call = mock_collection.update_one.call_args
        assert "_id" in update_call[0][0]
        assert "$set" in update_call[0][1]
        assert "whisper" in update_call[0][1]["$set"]
        assert update_call[0][1]["$set"]["whisper"] == "Test transcription"

    def test_store_whisper_existing_without_force(self, whisper_module):
        """Test store_whisper_in_db avec un whisper existant, sans forcer"""
        # Configuration des mocks
        mock_collection = MagicMock()
        test_oid = str(ObjectId())
        mock_document = {
            "_id": ObjectId(test_oid),
            "title": "Test Episode",
            "whisper": "Existing transcription",
        }
        mock_collection.find_one.return_value = mock_document

        # Appel de la fonction
        result = whisper_module.store_whisper_in_db(
            whisper="New transcription",
            collection=mock_collection,
            oid=test_oid,
            force=False,
            verbose=True,
        )

        # Vérifications
        assert result is False
        mock_collection.find_one.assert_called_once()
        mock_collection.update_one.assert_not_called()

    def test_store_whisper_existing_with_force(self, whisper_module):
        """Test store_whisper_in_db avec un whisper existant, en forçant"""
        # Configuration des mocks
        mock_collection = MagicMock()
        test_oid = str(ObjectId())
        mock_document = {
            "_id": ObjectId(test_oid),
            "title": "Test Episode",
            "whisper": "Existing transcription",
        }
        mock_collection.find_one.return_value = mock_document

        # Appel de la fonction
        result = whisper_module.store_whisper_in_db(
            whisper="New transcription",
            collection=mock_collection,
            oid=test_oid,
            force=True,
            verbose=True,
        )

        # Vérifications
        assert result is True
        mock_collection.find_one.assert_called_once()
        mock_collection.update_one.assert_called_once()

        # Vérifier que le whisper a été mis à jour
        update_call = mock_collection.update_one.call_args
        assert update_call[0][1]["$set"]["whisper"] == "New transcription"

    def test_store_whisper_document_not_found(self, whisper_module):
        """Test store_whisper_in_db quand le document n'existe pas"""
        # Configuration des mocks
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        test_oid = str(ObjectId())

        # Appel de la fonction
        result = whisper_module.store_whisper_in_db(
            whisper="Test transcription",
            collection=mock_collection,
            oid=test_oid,
            verbose=True,
        )

        # Vérifications
        assert result is False
        mock_collection.find_one.assert_called_once()
        mock_collection.update_one.assert_not_called()

    def test_store_whisper_silent_mode(self, whisper_module):
        """Test store_whisper_in_db en mode silencieux (verbose=False)"""
        # Configuration des mocks
        mock_collection = MagicMock()
        test_oid = str(ObjectId())
        mock_document = {"_id": ObjectId(test_oid), "title": "Test Episode"}
        mock_collection.find_one.return_value = mock_document

        # Appel de la fonction en mode silencieux
        result = whisper_module.store_whisper_in_db(
            whisper="Test transcription",
            collection=mock_collection,
            oid=test_oid,
            verbose=False,  # Mode silencieux
        )

        # Vérifications
        assert result is True
        mock_collection.find_one.assert_called_once()
        mock_collection.update_one.assert_called_once()
