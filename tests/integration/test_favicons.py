"""Test suite for favicon generation and existence."""

from pathlib import Path

import pytest


class TestFavicons:
    """Test favicon files generation and existence."""

    @pytest.fixture
    def favicon_dir(self):
        """Return the favicon directory path."""
        return (
            Path(__file__).resolve().parent.parent.parent / "ui" / "assets" / "favicons"
        )

    def test_favicon_directory_exists(self, favicon_dir):
        """Test that the favicon directory exists."""
        assert favicon_dir.exists(), f"Favicon directory not found: {favicon_dir}"
        assert favicon_dir.is_dir(), f"Favicon path is not a directory: {favicon_dir}"

    def test_source_favicon_exists(self, favicon_dir):
        """Test that the source favicon.png exists."""
        source = favicon_dir / "favicon.png"
        assert source.exists(), f"Source favicon not found: {source}"

    def test_all_favicon_files_exist(self, favicon_dir):
        """Test that all required favicon files exist."""
        required_files = [
            "favicon.ico",
            "favicon-16x16.png",
            "favicon-32x32.png",
            "favicon-48x48.png",
            "apple-touch-icon.png",
            "android-chrome-192x192.png",
            "android-chrome-512x512.png",
        ]

        for filename in required_files:
            filepath = favicon_dir / filename
            assert filepath.exists(), f"Required favicon file not found: {filename}"
            assert filepath.is_file(), f"Path is not a file: {filename}"

    def test_favicon_file_sizes(self, favicon_dir):
        """Test that favicon files have non-zero size."""
        files_to_check = [
            "favicon.ico",
            "favicon-16x16.png",
            "favicon-32x32.png",
            "favicon-48x48.png",
            "apple-touch-icon.png",
            "android-chrome-192x192.png",
            "android-chrome-512x512.png",
        ]

        for filename in files_to_check:
            filepath = favicon_dir / filename
            if filepath.exists():
                assert filepath.stat().st_size > 0, f"Favicon file is empty: {filename}"
