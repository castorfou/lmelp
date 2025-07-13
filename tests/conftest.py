"""Configuration globale pytest pour le projet LMELP"""

import os
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    """Isole l'environnement de test"""
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
