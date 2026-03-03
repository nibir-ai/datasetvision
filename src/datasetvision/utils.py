"""
Utility functions for datasetvision.
"""

from pathlib import Path
from typing import List

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


def get_image_files(dataset_path: Path) -> List[Path]:
    """
    Recursively collect supported image files.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    return [
        path
        for path in dataset_path.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
