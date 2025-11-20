"""Test suite to verify favicon usage across all Streamlit pages."""

import re
from pathlib import Path

import pytest


class TestFaviconUsage:
    """Test that all Streamlit pages use the favicon correctly."""

    @pytest.fixture
    def ui_files(self):
        """Return all UI files that should use st.set_page_config."""
        project_root = Path(__file__).resolve().parent.parent.parent
        ui_dir = project_root / "ui"

        # Main page
        main_page = ui_dir / "lmelp.py"

        # All pages in ui/pages/
        pages_dir = ui_dir / "pages"
        page_files = list(pages_dir.glob("*.py")) if pages_dir.exists() else []

        all_files = [main_page] + page_files
        return [f for f in all_files if f.exists()]

    def test_all_ui_files_exist(self, ui_files):
        """Test that we found UI files to check."""
        assert len(ui_files) > 0, "No UI files found to test"

    def test_main_page_uses_set_page_config(self, ui_files):
        """Test that main page uses st.set_page_config."""
        main_page = [f for f in ui_files if f.name == "lmelp.py"][0]
        content = main_page.read_text()
        assert (
            "st.set_page_config" in content
        ), "Main page should use st.set_page_config"

    def test_main_page_uses_favicon_with_pil(self, ui_files):
        """Test that main page (lmelp.py) loads favicon using PIL.Image."""
        main_page = [f for f in ui_files if f.name == "lmelp.py"][0]
        content = main_page.read_text()

        # Check if main page imports PIL Image
        assert "from PIL import Image" in content, "Main page should import PIL Image"

        # Check if main page loads favicon with PIL
        assert re.search(
            r"Image\.open\([^)]*favicon[^)]*\)", content
        ), "Main page should load favicon with Image.open()"

        # Check if page_icon uses the favicon variable
        assert re.search(
            r"page_icon\s*=\s*favicon", content
        ), "Main page should use page_icon=favicon"

    def test_subpages_dont_configure_favicon(self, ui_files):
        """Test that sub-pages don't configure page_icon (inherited from main)."""
        subpages = [f for f in ui_files if f.name != "lmelp.py"]

        for subpage in subpages:
            content = subpage.read_text()

            # Sub-pages should not have page_icon configuration
            has_page_icon = "page_icon" in content

            if has_page_icon:
                pytest.fail(
                    f"Sub-page {subpage.name} should not configure page_icon. "
                    f"It inherits from main page (lmelp.py)."
                )

    def test_favicon_path_uses_pil_image(self, ui_files):
        """Test that main page uses PIL Image object, not string path."""
        main_page = [f for f in ui_files if f.name == "lmelp.py"][0]
        content = main_page.read_text()

        # Should use PIL Image, not string path
        string_path_pattern = re.compile(r'page_icon\s*=\s*["\'][^"\']+["\']')
        match = string_path_pattern.search(content)

        assert not match, (
            "Main page should use PIL Image object (page_icon=favicon), "
            "not a string path"
        )
