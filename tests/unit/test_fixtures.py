"""Tests pour le package fixtures"""

import pytest
from pathlib import Path
from tests.fixtures import (
    FIXTURES_DIR,
    SAMPLE_DATA_DIR,
    load_sample_json,
    load_sample_text,
)


def get_project_root():
    """Obtient le répertoire racine du projet de manière portable"""
    current = Path(__file__).resolve()
    # Remonte jusqu'à trouver le répertoire contenant pytest.ini
    for parent in current.parents:
        if (parent / "pytest.ini").exists():
            return parent
    # Fallback : assume qu'on est dans tests/unit/
    return current.parent.parent


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

        # ARRANGE : Vérifier que le fichier .env.test existe (chemin relatif)
        project_root = get_project_root()
        env_test_path = project_root / ".env.test"
        assert env_test_path.exists(), f".env.test file should exist at {env_test_path}"

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

        project_root = get_project_root()
        env_test_path = project_root / ".env.test"
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

    def test_github_actions_workflow_exists(self):
        """Test que le workflow GitHub Actions pour T007 existe et est valide"""
        from pathlib import Path
        import yaml

        # ARRANGE : Chemin vers le workflow (chemin relatif)
        project_root = get_project_root()
        workflow_path = project_root / ".github" / "workflows" / "tests.yml"

        # ACT & ASSERT : Le fichier doit exister
        assert (
            workflow_path.exists()
        ), f"Le workflow GitHub Actions tests.yml doit exister (T007) at {workflow_path}"

        # ACT : Lire et parser le YAML
        content = workflow_path.read_text()
        workflow_config = yaml.safe_load(content)

        # ASSERT : Vérifier la structure du workflow
        assert "name" in workflow_config, "Le workflow doit avoir un nom"
        # Note: 'on' devient True en YAML, donc on teste les deux cas
        assert (
            "on" in workflow_config or True in workflow_config
        ), "Le workflow doit avoir des triggers"
        assert "jobs" in workflow_config, "Le workflow doit avoir des jobs"

        # Vérifier les jobs principaux
        jobs = workflow_config["jobs"]
        assert "test" in jobs, "Le job 'test' doit exister"

        # Vérifier que le job test utilise Ubuntu
        test_job = jobs["test"]
        assert test_job["runs-on"] == "ubuntu-latest", "Doit utiliser ubuntu-latest"

        # Vérifier les étapes critiques
        steps = test_job["steps"]
        step_names = [step.get("name", step.get("uses", "")) for step in steps]

        assert any(
            "checkout" in name.lower() for name in step_names
        ), "Doit avoir checkout"
        assert any(
            "python" in name.lower() for name in step_names
        ), "Doit configurer Python"

        # Vérifier qu'il y a une étape qui lance pytest
        run_commands = [step.get("run", "") for step in steps if "run" in step]
        assert any(
            "pytest" in cmd for cmd in run_commands
        ), "Doit lancer pytest dans une étape run"

    def test_load_sample_episode_json(self):
        """Test le chargement du fichier sample_episode.json"""
        # ARRANGE & ACT
        data = load_sample_json("sample_episode.json")

        # ASSERT
        assert isinstance(data, dict), "Le fichier doit contenir un dictionnaire"
        assert "episodes" in data, "Le fichier doit avoir une section 'episodes'"
        assert (
            "test_scenarios" in data
        ), "Le fichier doit avoir une section 'test_scenarios'"
        assert (
            "date_formats" in data
        ), "Le fichier doit avoir une section 'date_formats'"
        assert (
            "validation_data" in data
        ), "Le fichier doit avoir une section 'validation_data'"

        # Vérifier la structure des épisodes
        episodes = data["episodes"]
        assert len(episodes) >= 1, "Il doit y avoir au moins un épisode d'exemple"

        first_episode = episodes[0]
        required_fields = [
            "_id",
            "date",
            "titre",
            "description",
            "url_telechargement",
            "audio_rel_filename",
            "transcription",
            "type",
            "duree",
        ]
        for field in required_fields:
            assert field in first_episode, f"L'épisode doit avoir le champ '{field}'"

    def test_sample_episode_date_formats(self):
        """Test que les formats de date dans sample_episode.json sont corrects"""
        # ARRANGE & ACT
        data = load_sample_json("sample_episode.json")

        # ASSERT
        date_formats = data["date_formats"]
        assert date_formats["DATE_FORMAT"] == "%Y-%m-%dT%H:%M:%S"
        assert date_formats["LOG_DATE_FORMAT"] == "%d %b %Y %H:%M"

        # Test qu'on peut parser les dates d'exemple avec le bon format
        from datetime import datetime

        valid_dates = data["validation_data"]["valid_dates"]
        for date_str in valid_dates:
            try:
                parsed_date = datetime.strptime(date_str, date_formats["DATE_FORMAT"])
                assert isinstance(parsed_date, datetime)
            except ValueError:
                pytest.fail(
                    f"Impossible de parser la date '{date_str}' avec le format '{date_formats['DATE_FORMAT']}'"
                )

    def test_sample_episode_test_scenarios(self):
        """Test que les scénarios de test dans sample_episode.json sont cohérents"""
        # ARRANGE & ACT
        data = load_sample_json("sample_episode.json")

        # ASSERT
        scenarios = data["test_scenarios"]
        episodes = data["episodes"]

        # Vérifier que les IDs des scénarios correspondent à des épisodes existants
        episode_ids = {ep["_id"] for ep in episodes}

        for scenario_name, scenario in scenarios.items():
            episode_id = scenario["episode_id"]
            assert (
                episode_id in episode_ids
            ), f"Le scénario '{scenario_name}' référence un épisode inexistant: {episode_id}"

            # Vérifier la cohérence des flags avec les données réelles
            episode = next(ep for ep in episodes if ep["_id"] == episode_id)

            if scenario["has_transcription"]:
                assert (
                    episode["transcription"] is not None
                ), f"Le scénario '{scenario_name}' dit qu'il y a une transcription mais elle est null"

            if scenario["has_audio"]:
                assert (
                    episode["audio_rel_filename"] is not None
                ), f"Le scénario '{scenario_name}' dit qu'il y a un audio mais le filename est null"

    def test_load_sample_transcription_txt(self):
        """Test que le fichier sample_transcription.txt peut être chargé"""
        transcription = load_sample_text("sample_transcription.txt")

        # Vérifier que c'est bien du texte
        assert isinstance(transcription, str)
        assert len(transcription) > 0

        # Vérifier le format d'une émission "Le Masque et la Plume"
        assert "Masque et la Plume" in transcription
        assert "Bonjour et bienvenue" in transcription

        # Vérifier la structure typique d'une émission
        assert "Marie-Claire" in transcription  # Nom d'intervenant
        assert "éditions" in transcription  # Mention d'éditeur
        assert "[Générique" in transcription  # Indications techniques

    def test_sample_transcription_structure(self):
        """Test que la transcription exemple a la structure attendue"""
        transcription = load_sample_text("sample_transcription.txt")

        # Vérifier les éléments structurels
        lines = transcription.split("\n")
        assert len(lines) > 50  # Assez long pour être réaliste

        # Vérifier qu'il y a des noms d'intervenants
        intervenant_pattern = r"^[A-Za-z-]+\s[A-Za-z-]+\s:"
        import re

        intervenant_lines = [
            line for line in lines if re.match(intervenant_pattern, line)
        ]
        assert len(intervenant_lines) > 3  # Au moins quelques intervenants

        # Vérifier qu'il y a des mentions d'ouvrages (entre guillemets)
        livre_mentions = [line for line in lines if '"' in line and '"' in line]
        assert len(livre_mentions) > 0  # Au moins une mention d'ouvrage

    def test_sample_transcription_content_quality(self):
        """Test que la transcription exemple contient du contenu de qualité pour les tests LLM"""
        transcription = load_sample_text("sample_transcription.txt")

        # Vérifier qu'il y a des éléments typiques d'une critique littéraire
        required_elements = [
            "roman",
            "auteur",
            "livre",
            "critique",
            "écriture",
            "prose",
        ]

        transcription_lower = transcription.lower()
        for element in required_elements:
            assert (
                element in transcription_lower
            ), f"L'élément '{element}' devrait être présent dans la transcription"

        # Vérifier qu'il y a des noms d'éditeurs
        editeurs = ["Gallimard", "Minuit", "Lattès"]
        found_editeurs = [editeur for editeur in editeurs if editeur in transcription]
        assert (
            len(found_editeurs) > 0
        ), "Au moins un éditeur connu devrait être mentionné"
