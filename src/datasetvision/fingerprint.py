"""
Dataset fingerprinting for reproducibility and audit tracking.
"""

from pathlib import Path
from typing import Dict, Any
import hashlib

from datasetvision.utils import get_image_files


def generate_dataset_fingerprint(dataset_path: Path) -> Dict[str, Any]:
    """
    Generate deterministic dataset fingerprint.
    """

    image_files = sorted(str(p) for p in get_image_files(dataset_path))

    sha = hashlib.sha256()

    for file_path in image_files:
        sha.update(file_path.encode())

    fingerprint = sha.hexdigest()

    return {
        "total_images": len(image_files),
        "dataset_hash": fingerprint,
    }
