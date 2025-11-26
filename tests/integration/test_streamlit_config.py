"""
Tests d'intégration pour la configuration Streamlit.

Ces tests vérifient que :
- Le fichier de configuration Streamlit existe
- La configuration contient les bonnes options de logging
- Le fichier est bien présent pour le Docker build
"""

import os
from pathlib import Path
import pytest


class TestStreamlitConfig:
    """Tests pour la configuration Streamlit."""

    def test_streamlit_config_file_exists(self):
        """Vérifie que le fichier config.toml existe."""
        config_path = Path(__file__).parent.parent.parent / ".streamlit" / "config.toml"
        assert config_path.exists(), f"Config file not found at {config_path}"
        assert config_path.is_file(), f"Config path is not a file: {config_path}"

    def test_streamlit_config_contains_logging_settings(self):
        """Vérifie que le fichier config.toml contient les paramètres de logging."""
        config_path = Path(__file__).parent.parent.parent / ".streamlit" / "config.toml"

        with open(config_path, "r") as f:
            content = f.read()

        # Vérifier la présence des sections importantes
        assert "[logger]" in content, "Logger section missing"
        assert 'level = "info"' in content, "Logger level not set to info"
        assert "messageFormat" in content, "Message format not configured"

        # Vérifier les options du serveur
        assert "[server]" in content, "Server section missing"
        assert "[browser]" in content, "Browser section missing"
        assert "gatherUsageStats = false" in content, "Usage stats should be disabled"

    def test_streamlit_config_message_format(self):
        """Vérifie que le format de message contient timestamp et niveau."""
        config_path = Path(__file__).parent.parent.parent / ".streamlit" / "config.toml"

        with open(config_path, "r") as f:
            content = f.read()

        # Le format devrait inclure timestamp, niveau et message
        assert "%(asctime)s" in content, "Timestamp not in message format"
        assert "%(levelname)s" in content, "Log level not in message format"
        assert "%(message)s" in content, "Message not in message format"


class TestDockerEntrypoint:
    """Tests pour le script entrypoint.sh."""

    def test_entrypoint_exists(self):
        """Vérifie que le script entrypoint.sh existe."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )
        assert (
            entrypoint_path.exists()
        ), f"Entrypoint script not found at {entrypoint_path}"
        assert entrypoint_path.is_file()

    def test_entrypoint_simplified_banner(self):
        """Vérifie que la bannière a été simplifiée."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path, "r") as f:
            content = f.read()

        # Vérifier que la bannière simplifiée est présente
        assert "[lmelp] Starting in" in content, "Simplified banner not found"

        # Vérifier qu'on n'a pas l'ancienne bannière avec les ====
        lines = content.split("\n")
        # On compte le nombre de lignes avec beaucoup de "="
        banner_lines = [line for line in lines if line.count("=") > 20]
        # Il ne devrait pas y avoir plus de 2 lignes avec beaucoup de "=" (dans les messages d'erreur)
        assert (
            len(banner_lines) <= 2
        ), f"Too many banner lines found: {len(banner_lines)}"

    def test_entrypoint_logger_level_option(self):
        """Vérifie que l'option --logger.level=info est présente dans la commande streamlit."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path, "r") as f:
            content = f.read()

        # Vérifier que l'option de logging est présente
        assert (
            "--logger.level=info" in content
        ), "Logger level option not set in streamlit command"


class TestDockerfile:
    """Tests pour le Dockerfile."""

    def test_dockerfile_exists(self):
        """Vérifie que le Dockerfile existe."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )
        assert dockerfile_path.exists(), f"Dockerfile not found at {dockerfile_path}"

    def test_dockerfile_copies_streamlit_config(self):
        """Vérifie que le Dockerfile copie le répertoire .streamlit."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )

        with open(dockerfile_path, "r") as f:
            content = f.read()

        # Vérifier que .streamlit est copié dans l'image
        assert (
            "COPY .streamlit/" in content
        ), ".streamlit directory not copied in Dockerfile"
        assert (
            "/app/.streamlit/" in content
        ), ".streamlit not copied to correct location"
