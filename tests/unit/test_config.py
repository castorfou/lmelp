"""Tests pour nbs/config.py - Configuration et variables d'environnement"""

import pytest
import os
from nbs.config import (
    get_RSS_URL,
    get_azure_openai_keys,
    get_audio_path,
    get_DB_VARS,
    get_WEB_filename,
    get_gemini_api_key,
    get_openai_api_key,
    get_google_projectID,
    get_google_auth_file,
    get_git_root,
)


class TestConfig:
    """Tests pour les fonctions de nbs/config.py"""

    def test_get_RSS_URL_with_env_var(self, monkeypatch):
        """Test get_RSS_URL() quand RSS_LMELP_URL est définie"""
        # ARRANGE : Préparer
        test_url = "https://example.com/test-rss.xml"
        monkeypatch.setenv("RSS_LMELP_URL", test_url)

        # ACT : Exécuter
        result = get_RSS_URL()

        # ASSERT : Vérifier
        assert result == test_url

    def test_get_RSS_URL_without_env_var(self, monkeypatch):
        """Test get_RSS_URL() quand RSS_LMELP_URL n'est pas définie (valeur par défaut)"""
        # ARRANGE : Préparer (supprimer la variable si elle existe)
        monkeypatch.delenv("RSS_LMELP_URL", raising=False)

        # ACT : Exécuter
        result = get_RSS_URL()

        # ASSERT : Vérifier qu'on obtient l'URL par défaut
        expected_default = "https://radiofrance-podcast.net/podcast09/rss_14007.xml"
        assert result == expected_default

    def test_get_RSS_URL_returns_string(self):
        """Test que get_RSS_URL() retourne toujours une string non-vide"""
        # ACT : Exécuter
        result = get_RSS_URL()

        # ASSERT : Vérifier le type et la longueur
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.startswith("https://")  # doit être une URL HTTPS


class TestConfigAzureOpenAI:
    """Tests pour les fonctions Azure OpenAI de nbs/config.py"""

    def test_get_azure_openai_keys_all_set(self, monkeypatch):
        """Test get_azure_openai_keys() quand toutes les variables sont définies"""
        # ARRANGE : Préparer toutes les variables Azure
        test_api_key = "test-azure-key-123"
        test_endpoint = "https://test.openai.azure.com"
        test_version = "2024-09-01-preview"

        monkeypatch.setenv("AZURE_API_KEY", test_api_key)
        monkeypatch.setenv("AZURE_ENDPOINT", test_endpoint)
        monkeypatch.setenv("AZURE_API_VERSION", test_version)

        # ACT : Exécuter
        api_key, endpoint, version = get_azure_openai_keys()

        # ASSERT : Vérifier chaque élément du tuple
        assert api_key == test_api_key
        assert endpoint == test_endpoint
        assert version == test_version

    def test_get_azure_openai_keys_missing_vars(self, monkeypatch):
        """Test get_azure_openai_keys() quand les variables sont absentes"""

        # ARRANGE : Mock os.getenv pour retourner None
        def mock_getenv(key, default=None):
            if key in ["AZURE_API_KEY", "AZURE_ENDPOINT", "AZURE_API_VERSION"]:
                return None
            return default

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT : Exécuter
        api_key, endpoint, version = get_azure_openai_keys()

        # ASSERT : Vérifier que les valeurs sont None
        assert api_key is None
        assert endpoint is None
        assert version is None

    def test_get_azure_openai_keys_returns_tuple(self):
        """Test que get_azure_openai_keys() retourne toujours un tuple de 3 éléments"""
        # ACT : Exécuter
        result = get_azure_openai_keys()

        # ASSERT : Vérifier le type et la structure
        assert isinstance(result, tuple)
        assert len(result) == 3


class TestConfigAudioPath:
    """Tests pour les fonctions de gestion des chemins audio de nbs/config.py"""

    def test_get_audio_path_default_year(self):
        """Test get_audio_path() avec l'année par défaut"""
        # ACT : Exécuter avec paramètres par défaut
        result = get_audio_path()

        # ASSERT : Vérifier la structure du chemin
        assert isinstance(result, str)
        assert len(result) > 0
        assert "audios" in result
        assert "2024" in result  # année par défaut

    def test_get_audio_path_custom_year(self):
        """Test get_audio_path() avec une année spécifique"""
        # ARRANGE : Préparer
        test_year = "2023"

        # ACT : Exécuter
        result = get_audio_path(year=test_year)

        # ASSERT : Vérifier que l'année apparaît dans le chemin
        assert isinstance(result, str)
        assert test_year in result


class TestConfigDatabaseWeb:
    """Test database and web configuration functions"""

    def test_get_DB_VARS_with_environment(self, monkeypatch):
        """Test get_DB_VARS returns environment variables when set"""

        # ARRANGE
        def mock_getenv(key, default=None):
            env_vars = {
                "DB_HOST": "localhost",
                "DB_NAME": "lmelp_test",
                "DB_LOGS": "true",
            }
            return env_vars.get(key, default)

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT
        db_host, db_name, db_logs = get_DB_VARS()

        # ASSERT
        assert db_host == "localhost"
        assert db_name == "lmelp_test"
        assert db_logs == "true"

    def test_get_DB_VARS_without_environment(self, monkeypatch):
        """Test get_DB_VARS returns None when environment variables not set"""

        # ARRANGE
        def mock_getenv(key, default=None):
            return None

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT
        db_host, db_name, db_logs = get_DB_VARS()

        # ASSERT
        assert db_host is None
        assert db_name is None
        assert db_logs is None

    def test_get_WEB_filename_with_environment(self, monkeypatch):
        """Test get_WEB_filename with custom environment variable"""

        # ARRANGE
        def mock_getenv(key, default=None):
            if key == "WEB_LMELP_FILENAME":
                return "custom/path/file.html"
            return None

        def mock_get_git_root(path):
            return "/fake/project"

        monkeypatch.setattr(os, "getenv", mock_getenv)
        from nbs.config import get_git_root

        monkeypatch.setattr("nbs.config.get_git_root", mock_get_git_root)

        # ACT
        result = get_WEB_filename()

        # ASSERT
        assert result == "/fake/project/custom/path/file.html"

    def test_get_WEB_filename_with_default(self, monkeypatch):
        """Test get_WEB_filename with default path when env var not set"""

        # ARRANGE
        def mock_getenv(key, default=None):
            return None

        def mock_get_git_root(path):
            return "/fake/project"

        monkeypatch.setattr(os, "getenv", mock_getenv)
        from nbs.config import get_git_root

        monkeypatch.setattr("nbs.config.get_git_root", mock_get_git_root)

        # ACT
        result = get_WEB_filename()

        # ASSERT
        expected = "/fake/project/db/À écouter plus tard I Radio France/À écouter plus tard I Radio France.html"
        assert result == expected


class TestConfigApiKeys:
    """Test API key configuration functions"""

    def test_get_gemini_api_key(self, monkeypatch):
        """Test get_gemini_api_key returns environment variable"""

        # ARRANGE
        def mock_getenv(key, default=None):
            if key == "GEMINI_API_KEY":
                return "fake_gemini_key_123"
            return None

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT
        result = get_gemini_api_key()

        # ASSERT
        assert result == "fake_gemini_key_123"

    def test_get_openai_api_key(self, monkeypatch):
        """Test get_openai_api_key returns environment variable"""

        # ARRANGE
        def mock_getenv(key, default=None):
            if key == "OPENAI_API_KEY":
                return "fake_openai_key_456"
            return None

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT
        result = get_openai_api_key()

        # ASSERT
        assert result == "fake_openai_key_456"

    def test_get_google_projectID(self, monkeypatch):
        """Test get_google_projectID returns environment variable"""

        # ARRANGE
        def mock_getenv(key, default=None):
            if key == "GOOGLE_PROJECT_ID":
                return "fake-project-id"
            return None

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT
        result = get_google_projectID()

        # ASSERT
        assert result == "fake-project-id"

    def test_get_google_auth_file(self, monkeypatch):
        """Test get_google_auth_file returns environment variable"""

        # ARRANGE
        def mock_getenv(key, default=None):
            if key == "GOOGLE_AUTH_FILE":
                return "path/to/auth.json"
            return None

        monkeypatch.setattr(os, "getenv", mock_getenv)

        # ACT
        result = get_google_auth_file()

        # ASSERT
        assert result == "path/to/auth.json"


class TestConfigGitRoot:
    """Test git root functionality"""

    def test_get_git_root(self, monkeypatch):
        """Test get_git_root returns git repository root"""

        # ARRANGE
        class MockRepo:
            def __init__(self, path, search_parent_directories=True):
                self.git = MockGit()

        class MockGit:
            def rev_parse(self, option):
                if option == "--show-toplevel":
                    return "/fake/git/root"
                return None

        from nbs.config import Repo

        monkeypatch.setattr("nbs.config.Repo", MockRepo)

        # ACT
        result = get_git_root("/some/path")

        # ASSERT
        assert result == "/fake/git/root"

    def test_get_git_root_no_git_repo(self, monkeypatch):
        """Test get_git_root returns path when no git repo found (Docker case)"""
        # ARRANGE
        from git.exc import InvalidGitRepositoryError

        def mock_repo_raise(*args, **kwargs):
            raise InvalidGitRepositoryError("No git repo")

        monkeypatch.setattr("nbs.config.Repo", mock_repo_raise)

        test_path = "/app/test"

        # ACT
        result = get_git_root(test_path)

        # ASSERT
        assert result == test_path


# Déplaçons ce test dans la bonne classe
class TestConfigAudioPathExtended:
    """Tests supplémentaires pour get_audio_path"""

    def test_get_audio_path_custom_path_and_year(self):
        """Test get_audio_path() avec chemin et année personnalisés"""
        # ARRANGE : Préparer
        test_path = "test_audios"
        test_year = "2022"

        # ACT : Exécuter
        result = get_audio_path(audio_path=test_path, year=test_year)

        # ASSERT : Vérifier que les paramètres apparaissent dans le chemin
        assert isinstance(result, str)
        assert test_path in result
        assert test_year in result
