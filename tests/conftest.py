"""Configuration globale pytest pour le projet LMELP"""

import os
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv, find_dotenv


def load_env_test():
    """Charge le fichier .env.test pour les tests (similaire à config.load_env())"""
    # Chemin robuste : relatif à ce fichier conftest.py, indépendant du working directory
    current_dir = os.path.dirname(__file__)  # /path/to/tests/
    project_root = os.path.dirname(current_dir)  # /path/to/project/
    env_test_path = os.path.join(project_root, ".env.test")

    if os.path.exists(env_test_path):
        return load_dotenv(env_test_path, override=True)
    else:
        # Fallback : essayer find_dotenv pour le développement local
        env_test_path = find_dotenv(".env.test")
        if env_test_path:
            return load_dotenv(env_test_path, override=True)

    return False


@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    """Isole l'environnement de test et charge .env.test"""
    # D'abord charger .env.test pour avoir les valeurs de base
    load_env_test()

    # Puis surcharger avec isolation via monkeypatch si nécessaire
    monkeypatch.setenv("TEST_MODE", "true")
    # Azure OpenAI (seule API utilisée)
    monkeypatch.setenv("AZURE_API_KEY", "test-azure-key")
    monkeypatch.setenv("AZURE_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_API_VERSION", "2024-09-01-preview")


@pytest.fixture(autouse=True)
def mock_mongodb(monkeypatch):
    """Mock complet de MongoDB pour éviter les connexions réelles"""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    # Chaîne de mocks : client -> db -> collection
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock de pymongo.MongoClient
    monkeypatch.setattr("pymongo.MongoClient", lambda *args, **kwargs: mock_client)

    return mock_collection


@pytest.fixture
def test_config():
    """Configuration de test basique"""
    return {
        "azure_openai": {
            "api_key": "test-azure-key",
            "endpoint": "https://test.openai.azure.com",
            "api_version": "2024-09-01-preview",
        },
        "paths": {"audio": "/tmp/test_audio"},
    }
