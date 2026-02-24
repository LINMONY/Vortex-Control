from pathlib import Path
import os

def get_base_dir() -> Path:
    """Returns the base directory of the application."""
    # Assuming this file is in utils/paths.py, parent is utils, parent.parent is core root
    return Path(__file__).resolve().parent.parent

def get_assets_dir() -> Path:
    """Returns the assets directory path."""
    return get_base_dir() / "assets"
