"""
Tests d'intégration pour la configuration Streamlit.

Ces tests vérifient que :
- Le fichier de configuration Streamlit existe
- La configuration contient les bonnes options de logging
- Le fichier est bien présent pour le Docker build
"""

from pathlib import Path


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

        with open(config_path) as f:
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

        with open(config_path) as f:
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
        assert entrypoint_path.exists(), (
            f"Entrypoint script not found at {entrypoint_path}"
        )
        assert entrypoint_path.is_file()

    def test_entrypoint_simplified_banner(self):
        """Vérifie que la bannière a été simplifiée."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path) as f:
            content = f.read()

        # Vérifier que la bannière simplifiée est présente
        assert "[lmelp] Starting in" in content, "Simplified banner not found"

        # Vérifier qu'on n'a pas l'ancienne bannière avec les ====
        lines = content.split("\n")
        # On compte le nombre de lignes avec beaucoup de "="
        banner_lines = [line for line in lines if line.count("=") > 20]
        # Il ne devrait pas y avoir plus de 2 lignes avec beaucoup de "=" (dans les messages d'erreur)
        assert len(banner_lines) <= 2, (
            f"Too many banner lines found: {len(banner_lines)}"
        )

    def test_entrypoint_logger_level_option(self):
        """Vérifie que l'option --logger.level=info est présente dans la commande streamlit."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path) as f:
            content = f.read()

        # Vérifier que l'option de logging est présente
        assert "--logger.level=info" in content, (
            "Logger level option not set in streamlit command"
        )

    def test_entrypoint_reads_puid_pgid_with_defaults(self):
        """Vérifie que PUID/PGID sont lus avec une valeur par défaut (issue #105)."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path) as f:
            content = f.read()

        assert "PUID=${PUID:-" in content, "PUID not read with a default value"
        assert "PGID=${PGID:-" in content, "PGID not read with a default value"

    def test_entrypoint_remaps_uid_gid(self):
        """Vérifie que l'utilisateur non-root est remappé vers PUID/PGID (issue #105)."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path) as f:
            content = f.read()

        assert "usermod" in content, "usermod not used to remap the non-root user UID"
        assert "groupmod" in content, (
            "groupmod not used to remap the non-root group GID"
        )

    def test_entrypoint_chowns_volume_directories(self):
        """Vérifie que les répertoires de volumes sont chownés vers PUID/PGID (issue #105)."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path) as f:
            content = f.read()

        assert "chown" in content, "chown not used on volume directories"
        for volume_dir in ("/app/audios", "/app/db", "/app/logs"):
            assert volume_dir in content, f"{volume_dir} not referenced for chown"

    def test_entrypoint_drops_privileges_with_gosu(self):
        """Vérifie que le process applicatif est bien lancé sous l'utilisateur non-root (issue #105)."""
        entrypoint_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "entrypoint.sh"
        )

        with open(entrypoint_path) as f:
            content = f.read()

        assert "gosu appuser" in content, "gosu not used to drop privileges to appuser"


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

        with open(dockerfile_path) as f:
            content = f.read()

        # Vérifier que .streamlit est copié dans l'image
        assert "COPY .streamlit/" in content, (
            ".streamlit directory not copied in Dockerfile"
        )
        assert "/app/.streamlit/" in content, (
            ".streamlit not copied to correct location"
        )

    def test_dockerfile_installs_gosu(self):
        """Vérifie que gosu est installé pour permettre de dropper les privilèges (issue #105)."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )

        with open(dockerfile_path) as f:
            content = f.read()

        assert "gosu" in content, "gosu not installed in Dockerfile"

    def test_dockerfile_declares_uid_gid_build_args(self):
        """Vérifie que l'UID/GID par défaut sont déclarés via des ARG (issue #105)."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )

        with open(dockerfile_path) as f:
            content = f.read()

        assert "ARG APP_UID=" in content, "APP_UID build arg not declared"
        assert "ARG APP_GID=" in content, "APP_GID build arg not declared"

    def test_dockerfile_creates_non_root_user_from_args(self):
        """Vérifie que l'utilisateur non-root est créé à partir des ARG (issue #105)."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )

        with open(dockerfile_path) as f:
            content = f.read()

        assert "useradd" in content, "useradd not used to create a non-root user"
        assert "$APP_UID" in content, "useradd does not reference $APP_UID"
        assert "$APP_GID" in content, "groupadd does not reference $APP_GID"

    def test_dockerfile_sets_home_for_non_root_user(self):
        """Vérifie que HOME est positionné vers le home du non-root user (issue #105)."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )

        with open(dockerfile_path) as f:
            content = f.read()

        assert "ENV HOME=" in content, "HOME env var not set for the non-root user"

    def test_dockerfile_does_not_hardcode_static_user_directive(self):
        """Vérifie que le switch d'utilisateur se fait dynamiquement dans l'entrypoint,
        pas via une directive USER statique au build (issue #105)."""
        dockerfile_path = (
            Path(__file__).parent.parent.parent / "docker" / "build" / "Dockerfile"
        )

        with open(dockerfile_path) as f:
            lines = f.readlines()

        user_lines = [line for line in lines if line.strip().startswith("USER ")]
        assert not user_lines, (
            f"Static USER directive found, UID switch should happen in entrypoint.sh: {user_lines}"
        )
