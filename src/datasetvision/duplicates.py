"""
Duplicate detection module.
"""

from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from datasetvision.utils import get_image_files
from datasetvision.hashing import compute_md5, perceptual_hash


def find_exact_duplicates(dataset_path: Path) -> Dict[str, List[str]]:
    """
    Find exact duplicate images using MD5 hashing.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    hash_map: Dict[str, List[str]] = defaultdict(list)

    for image_path in get_image_files(dataset_path):
        file_hash = compute_md5(image_path)
        hash_map[file_hash].append(str(image_path))

    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def find_near_duplicates(dataset_path: Path) -> Dict[str, List[str]]:
    """
    Find near-duplicate images using perceptual hashing.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    hash_map: Dict[str, List[str]] = defaultdict(list)

    for image_path in get_image_files(dataset_path):
        p_hash = perceptual_hash(image_path)
        hash_map[p_hash].append(str(image_path))

    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}
