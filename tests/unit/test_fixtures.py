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

    def test_env_test_file_exists_and_valid(self):
        """Test que .env.test existe et contient les variables attendues"""
        import os
        from pathlib import Path

        # ARRANGE : Vérifier que le fichier .env.test existe
        env_test_path = Path("/workspaces/lmelp/.env.test")
        assert env_test_path.exists(), ".env.test file should exist"

        # ACT : Lire le contenu du fichier
        content = env_test_path.read_text()

        # ASSERT : Vérifier que les variables principales sont présentes
        assert "TEST_MODE=true" in content
        assert "RSS_LMELP_URL=https://example.com/test-rss-feed.xml" in content
        assert "AZURE_API_KEY=test-azure-api-key-12345" in content
        assert "AZURE_ENDPOINT=https://test-azure-openai.openai.azure.com" in content
        assert "DB_NAME=test_lmelp_db" in content

    def test_env_test_variables_consistency_with_sample_config(self):
        """Test que .env.test est cohérent avec sample_config.json"""
        from pathlib import Path

        # ARRANGE : Charger les deux sources de configuration
        config_data = load_sample_json("sample_config.json")
        env_vars_from_json = config_data["environment_variables"]

        env_test_path = Path("/workspaces/lmelp/.env.test")
        env_test_content = env_test_path.read_text()

        # ACT & ASSERT : Vérifier la cohérence des valeurs principales
        assert (
            f"RSS_LMELP_URL={env_vars_from_json['RSS_LMELP_URL']}" in env_test_content
        )
        assert (
            f"AZURE_API_KEY={env_vars_from_json['AZURE_API_KEY']}" in env_test_content
        )
        assert (
            f"AZURE_ENDPOINT={env_vars_from_json['AZURE_ENDPOINT']}" in env_test_content
        )
        assert (
            f"GEMINI_API_KEY={env_vars_from_json['GEMINI_API_KEY']}" in env_test_content
        )
        assert f"DB_NAME={env_vars_from_json['DB_NAME']}" in env_test_content

    def test_env_test_is_actually_loaded_by_pytest(self):
        """Test de validation critique : s'assurer que .env.test est VRAIMENT chargé par pytest"""
        import os

        # ARRANGE : Cette valeur unique n'existe que dans .env.test
        # Si ce test échoue, c'est que .env.test n'est pas chargé correctement
        expected_validation_value = "env_test_is_loaded_correctly_12345"

        # ACT & ASSERT : Si .env.test est chargé, cette valeur doit être présente
        actual_value = os.getenv("TEST_VALIDATION_KEY")
        assert actual_value == expected_validation_value, (
            f"ÉCHEC CRITIQUE : .env.test n'est pas chargé correctement ! "
            f"Attendu: {expected_validation_value}, Reçu: {actual_value}. "
            f"Vérifiez la configuration pytest-env dans pytest.ini"
        )

    def test_manual_load_env_test_with_dotenv(self):
        """Test : charger manuellement .env.test avec load_dotenv() comme dans config.py"""
        import os
        from dotenv import load_dotenv, find_dotenv

        # ARRANGE : Sauvegarder la valeur actuelle si elle existe
        original_value = os.getenv("TEST_VALIDATION_KEY")

        # ACT : Charger explicitement .env.test (comme le fait config.py)
        env_test_path = find_dotenv(".env.test")
        assert env_test_path  # S'assurer que le fichier est trouvé

        loaded = load_dotenv(env_test_path, override=True)
        assert loaded  # S'assurer que le chargement a réussi

        # ASSERT : Maintenant la variable devrait être chargée
        actual_value = os.getenv("TEST_VALIDATION_KEY")
        expected_value = "env_test_is_loaded_correctly_12345"

        assert actual_value == expected_value, (
            f"Chargement manuel de .env.test échoué ! "
            f"Attendu: {expected_value}, Reçu: {actual_value}"
        )

        # CLEANUP : Restaurer l'état original si besoin
        if original_value is None:
            os.environ.pop("TEST_VALIDATION_KEY", None)
        else:
            os.environ["TEST_VALIDATION_KEY"] = original_value

    def test_load_env_test_robustness_for_cicd(self):
        """Test robustesse load_env_test() pour CI/CD (indépendant du working directory)"""
        import os
        import tempfile
        from tests.conftest import load_env_test

        # ARRANGE : Sauvegarder working directory actuel et variables
        original_cwd = os.getcwd()
        original_value = os.getenv("TEST_VALIDATION_KEY")

        try:
            # ACT : Changer vers un répertoire temporaire (simule CI/CD)
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)

                # Nettoyer la variable pour vraiment tester le chargement
                if "TEST_VALIDATION_KEY" in os.environ:
                    del os.environ["TEST_VALIDATION_KEY"]

                # Charger depuis un autre répertoire
                result = load_env_test()

                # ASSERT : Doit fonctionner même depuis un autre répertoire
                assert (
                    result == True
                ), "load_env_test() doit réussir depuis n'importe quel répertoire"

                # Vérifier que la variable est bien chargée
                actual_value = os.getenv("TEST_VALIDATION_KEY")
                expected_value = "env_test_is_loaded_correctly_12345"
                assert actual_value == expected_value, (
                    f"Variables .env.test non chargées depuis répertoire {temp_dir}. "
                    f"Attendu: {expected_value}, Reçu: {actual_value}"
                )

        finally:
            # CLEANUP : Restaurer l'état original
            os.chdir(original_cwd)
            if original_value is None:
                os.environ.pop("TEST_VALIDATION_KEY", None)
            else:
                os.environ["TEST_VALIDATION_KEY"] = original_value
