"""
Duplicate detection module.
"""

from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from datasetvision.utils import get_image_files
from datasetvision.hashing import compute_md5, perceptual_hash, hamming_distance


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


def find_near_duplicates(
    dataset_path: Path,
    threshold: int = 5,
) -> Dict[str, List[str]]:
    """
    Find near-duplicate images using perceptual hash and Hamming distance.

    Groups images whose distance <= threshold.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    image_files = get_image_files(dataset_path)

    # Compute hashes
    hashes: Dict[str, int] = {}
    for image_path in image_files:
        hashes[str(image_path)] = perceptual_hash(image_path)

    paths = list(hashes.keys())
    groups: List[List[str]] = []
    visited = set()

    for i in range(len(paths)):
        base_path = paths[i]

        if base_path in visited:
            continue

        group = [base_path]
        visited.add(base_path)

        for j in range(i + 1, len(paths)):
            compare_path = paths[j]

            if compare_path in visited:
                continue

            distance = hamming_distance(
                hashes[base_path],
                hashes[compare_path],
            )

            if distance <= threshold:
                group.append(compare_path)
                visited.add(compare_path)

        if len(group) > 1:
            groups.append(group)

    return {f"group_{i}": group for i, group in enumerate(groups)}
