"""Tests pour le package fixtures"""

import pytest
from pathlib import Path
from tests.fixtures import (
    FIXTURES_DIR,
    SAMPLE_DATA_DIR,
    load_sample_json,
    load_sample_text,
)


class TestFixturesPackage:
    """Tests pour l'infrastructure des fixtures"""

    def test_fixtures_dir_exists(self):
        """Test que le répertoire fixtures existe"""
        assert FIXTURES_DIR.exists()
        assert FIXTURES_DIR.is_dir()

    def test_sample_data_dir_defined(self):
        """Test que SAMPLE_DATA_DIR est défini correctement"""
        expected_path = FIXTURES_DIR / "data"
        assert SAMPLE_DATA_DIR == expected_path

    def test_load_sample_json_function_exists(self):
        """Test que la fonction load_sample_json est disponible"""
        assert callable(load_sample_json)

    def test_load_sample_text_function_exists(self):
        """Test que la fonction load_sample_text est disponible"""
        assert callable(load_sample_text)

    def test_load_sample_json_file_not_found(self):
        """Test load_sample_json avec fichier inexistant"""
        with pytest.raises(FileNotFoundError, match="Fichier de test non trouvé"):
            load_sample_json("nonexistent.json")

    def test_load_sample_text_file_not_found(self):
        """Test load_sample_text avec fichier inexistant"""
        with pytest.raises(FileNotFoundError, match="Fichier de test non trouvé"):
            load_sample_text("nonexistent.txt")

    def test_sample_data_dir_exists(self):
        """Test que le répertoire data existe après T014"""
        assert SAMPLE_DATA_DIR.exists()
        assert SAMPLE_DATA_DIR.is_dir()

    def test_load_sample_config_json(self):
        """Test load_sample_json avec le fichier sample_config.json créé par T014"""
        # ACT : Charger le fichier de configuration d'exemple
        config_data = load_sample_json("sample_config.json")

        # ASSERT : Vérifier la structure attendue
        assert isinstance(config_data, dict)
        assert "_description" in config_data
        assert "environment_variables" in config_data
        assert "default_values" in config_data
        assert "test_scenarios" in config_data
        assert "validation_data" in config_data

        # Vérifier quelques variables d'environnement spécifiques
        env_vars = config_data["environment_variables"]
        assert "RSS_LMELP_URL" in env_vars
        assert "AZURE_API_KEY" in env_vars
        assert "GEMINI_API_KEY" in env_vars
