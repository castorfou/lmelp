"""Test suite to verify Streamlit favicon patch has been applied."""

from pathlib import Path

import pytest

# Skip all tests if streamlit is not installed (e.g., in CI/CD)
try:
    import streamlit  # noqa: F401

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not STREAMLIT_AVAILABLE, reason="Streamlit not installed (minimal test environment)"
)


class TestStreamlitPatch:
    """Test that Streamlit favicon has been patched with our custom icon."""

    @pytest.fixture
    def streamlit_favicon_path(self):
        """Return the path to Streamlit's favicon."""
        import streamlit

        streamlit_path = Path(streamlit.__file__).parent
        return streamlit_path / "static" / "favicon.png"

    @pytest.fixture
    def custom_favicon_path(self):
        """Return the path to our custom favicon."""
        project_root = Path(__file__).resolve().parent.parent.parent
        return project_root / "ui" / "assets" / "favicons" / "favicon-32x32.png"

    @pytest.fixture
    def backup_favicon_path(self, streamlit_favicon_path):
        """Return the path to the backup of original Streamlit favicon."""
        return streamlit_favicon_path.with_suffix(".png.original")

    def test_streamlit_favicon_exists(self, streamlit_favicon_path):
        """Test that Streamlit's favicon file exists."""
        assert (
            streamlit_favicon_path.exists()
        ), f"Streamlit favicon not found: {streamlit_favicon_path}"
        assert (
            streamlit_favicon_path.is_file()
        ), f"Streamlit favicon is not a file: {streamlit_favicon_path}"

    def test_custom_favicon_exists(self, custom_favicon_path):
        """Test that our custom favicon exists."""
        assert (
            custom_favicon_path.exists()
        ), f"Custom favicon not found: {custom_favicon_path}"
        assert (
            custom_favicon_path.is_file()
        ), f"Custom favicon is not a file: {custom_favicon_path}"

    def test_backup_exists_after_patch(self, backup_favicon_path):
        """Test that backup of original Streamlit favicon exists."""
        assert backup_favicon_path.exists(), (
            f"Backup favicon not found: {backup_favicon_path}. "
            "Run 'python scripts/patch_streamlit_favicon.py' to create the patch."
        )
        assert (
            backup_favicon_path.is_file()
        ), f"Backup favicon is not a file: {backup_favicon_path}"

    def test_streamlit_favicon_matches_custom(
        self, streamlit_favicon_path, custom_favicon_path
    ):
        """Test that Streamlit's favicon has been replaced with our custom one."""
        import hashlib

        # Calculate hash of Streamlit's current favicon
        with open(streamlit_favicon_path, "rb") as f:
            streamlit_hash = hashlib.md5(f.read()).hexdigest()

        # Calculate hash of our custom favicon
        with open(custom_favicon_path, "rb") as f:
            custom_hash = hashlib.md5(f.read()).hexdigest()

        assert streamlit_hash == custom_hash, (
            f"Streamlit favicon has not been patched. "
            f"Expected hash: {custom_hash}, got: {streamlit_hash}. "
            "Run 'python scripts/patch_streamlit_favicon.py' to apply the patch."
        )

    def test_backup_different_from_custom(
        self, backup_favicon_path, custom_favicon_path
    ):
        """Test that backup is different from our custom favicon."""
        import hashlib

        if not backup_favicon_path.exists():
            pytest.skip("Backup file doesn't exist yet")

        # Calculate hash of backup
        with open(backup_favicon_path, "rb") as f:
            backup_hash = hashlib.md5(f.read()).hexdigest()

        # Calculate hash of our custom favicon
        with open(custom_favicon_path, "rb") as f:
            custom_hash = hashlib.md5(f.read()).hexdigest()

        assert backup_hash != custom_hash, (
            "Backup favicon should be different from custom favicon. "
            "This suggests the original Streamlit favicon was never backed up properly."
        )

    def test_get_custom_favicon_path_returns_valid_path(self):
        """Test that get_custom_favicon_path() returns a path that exists."""
        # Import the function from the patch script
        import sys
        from pathlib import Path

        script_path = (
            Path(__file__).resolve().parent.parent.parent
            / "ui"
            / "assets"
            / "favicons"
            / "scripts"
            / "patch_streamlit_favicon.py"
        )

        # Add the script directory to sys.path to import it
        sys.path.insert(0, str(script_path.parent))

        try:
            from patch_streamlit_favicon import get_custom_favicon_path

            # Get the path from the function
            custom_path = get_custom_favicon_path()

            # Verify the path exists
            assert (
                custom_path.exists()
            ), f"get_custom_favicon_path() returned non-existent path: {custom_path}"
            assert (
                custom_path.is_file()
            ), f"get_custom_favicon_path() returned path is not a file: {custom_path}"

            # Verify it's the right file (favicon-32x32.png)
            assert (
                custom_path.name == "favicon-32x32.png"
            ), f"Expected filename 'favicon-32x32.png', got: {custom_path.name}"

        finally:
            # Clean up sys.path
            sys.path.pop(0)
