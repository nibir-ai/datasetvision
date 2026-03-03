"""
Hashing utilities for duplicate detection.
"""

from pathlib import Path
import hashlib
from PIL import Image
import numpy as np


def compute_md5(file_path: Path) -> str:
    """
    Compute MD5 hash of a file.
    """
    hasher = hashlib.md5()

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def perceptual_hash(image_path: Path) -> str:
    """
    Compute perceptual average hash (aHash).
    """

    with Image.open(image_path) as img:
        img = img.convert("L").resize((8, 8))
        pixels = np.array(img)
        avg = pixels.mean()
        diff = pixels > avg
        return "".join(["1" if val else "0" for val in diff.flatten()])
