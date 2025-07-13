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
