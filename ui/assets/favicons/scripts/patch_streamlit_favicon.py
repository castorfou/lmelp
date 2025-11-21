#!/usr/bin/env python3
"""
Script to replace Streamlit's default favicon with our custom one.

This script patches the Streamlit installation to use our custom favicon
instead of the default crown icon. This prevents the "flash" effect where
the default favicon appears briefly before being replaced by st.set_page_config().

Background:
-----------
This is a known Streamlit limitation (see GitHub issue #9058 and community discussions).
The default favicon is hardcoded in Streamlit's static files and loads before JavaScript
can apply st.set_page_config() settings, causing a visible "flicker".

The community consensus is that the only reliable fix is to patch the Streamlit installation
directly. This script automates that process.

References:
- https://github.com/streamlit/streamlit/issues/9058
- https://discuss.streamlit.io/t/favicon-and-title-change-during-refresh/74003
- https://discuss.streamlit.io/t/page-title-icon-flicker-before-override/30884

Usage:
------
    # Patch Streamlit with custom favicon
    python scripts/patch_streamlit_favicon.py

    # Restore original Streamlit favicon
    python scripts/patch_streamlit_favicon.py --restore

When to run:
------------
- After installing/updating Streamlit (pip install/upgrade)
- After creating a new virtual environment
- As part of devcontainer postCreateCommand
- When you see the default crown icon flash on page load
"""

import shutil
import sys
from pathlib import Path


def get_streamlit_favicon_path():
    """Get the path to Streamlit's default favicon."""
    try:
        import streamlit

        streamlit_path = Path(streamlit.__file__).parent
        return streamlit_path / "static" / "favicon.png"
    except ImportError:
        print("❌ Streamlit is not installed")
        return None


def get_custom_favicon_path():
    """Get the path to our custom favicon."""
    # First, check for Docker build context where file is copied to /tmp
    docker_favicon = Path("/tmp/custom-favicon.png")
    if docker_favicon.exists():
        return docker_favicon

    # Standard project location: go up 4 levels from script location
    # __file__ = /path/to/ui/assets/favicons/scripts/patch_streamlit_favicon.py
    # .parent = /path/to/ui/assets/favicons/scripts
    # .parent.parent = /path/to/ui/assets/favicons
    # .parent.parent.parent = /path/to/ui/assets
    # .parent.parent.parent.parent = /path/to/ui
    # Then back down to favicons
    script_dir = Path(__file__).resolve().parent  # scripts/
    favicons_dir = script_dir.parent  # favicons/
    custom_favicon = favicons_dir / "favicon-32x32.png"

    if custom_favicon.exists():
        return custom_favicon

    # If neither exists, return the standard location (will fail with proper error)
    return custom_favicon


def patch_streamlit_favicon():
    """Replace Streamlit's default favicon with our custom one."""

    streamlit_favicon = get_streamlit_favicon_path()
    if not streamlit_favicon:
        return False

    if not streamlit_favicon.exists():
        print(f"❌ Streamlit favicon not found at: {streamlit_favicon}")
        return False

    custom_favicon = get_custom_favicon_path()
    if not custom_favicon.exists():
        print(f"❌ Custom favicon not found at: {custom_favicon}")
        return False

    # Backup the original if not already done
    backup_favicon = streamlit_favicon.with_suffix(".png.original")
    if not backup_favicon.exists():
        shutil.copy2(streamlit_favicon, backup_favicon)
        print(f"✅ Backed up original Streamlit favicon")
        print(f"   Backup: {backup_favicon}")

    # Replace with our custom favicon
    shutil.copy2(custom_favicon, streamlit_favicon)
    print(f"✅ Patched Streamlit favicon with custom icon")
    print(f"   Custom: {custom_favicon}")
    print(f"   Target: {streamlit_favicon}")
    print()
    print("🎉 The default crown icon will no longer flash on page load!")

    return True


def restore_streamlit_favicon():
    """Restore Streamlit's original favicon from backup."""

    streamlit_favicon = get_streamlit_favicon_path()
    if not streamlit_favicon:
        return False

    backup_favicon = streamlit_favicon.with_suffix(".png.original")
    if not backup_favicon.exists():
        print(f"❌ No backup found at: {backup_favicon}")
        print("   The original favicon was never backed up.")
        return False

    shutil.copy2(backup_favicon, streamlit_favicon)
    print(f"✅ Restored original Streamlit favicon from backup")
    print(f"   Backup: {backup_favicon}")
    print(f"   Target: {streamlit_favicon}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        print("🔄 Restoring original Streamlit favicon...")
        print()
        success = restore_streamlit_favicon()
    else:
        print("🔧 Patching Streamlit favicon...")
        print()
        success = patch_streamlit_favicon()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
