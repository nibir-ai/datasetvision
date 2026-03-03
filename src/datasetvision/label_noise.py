"""
Label noise detection using perceptual similarity heuristics.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging

from datasetvision.utils import get_image_files
from datasetvision.hashing import perceptual_hash, hamming_distance

logger = logging.getLogger(__name__)


def detect_label_noise(dataset_path: Path) -> Dict[str, Any]:
    """
    Detect potential label noise based on perceptual similarity.

    Flags images that are more similar to another class than their own.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    class_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]

    if len(class_dirs) < 2:
        return {
            "message": "Label noise detection requires at least 2 classes.",
            "suspicious_images": [],
        }

    # Compute hashes grouped by class
    class_hashes: Dict[str, Dict[str, int]] = {}

    for class_dir in class_dirs:
        hashes = {}
        for image_path in get_image_files(class_dir):
            hashes[str(image_path)] = perceptual_hash(image_path)
        class_hashes[class_dir.name] = hashes

    suspicious: List[Dict[str, Any]] = []

    # Compare across classes
    for class_name, images in class_hashes.items():
        for image_path, image_hash in images.items():

            # Compute min intra-class distance
            intra_distances = [
                hamming_distance(image_hash, other_hash)
                for other_path, other_hash in images.items()
                if other_path != image_path
            ]

            min_intra = min(intra_distances) if intra_distances else float("inf")

            # Compute min inter-class distance
            inter_distances = []

            for other_class, other_images in class_hashes.items():
                if other_class == class_name:
                    continue

                for other_hash in other_images.values():
                    inter_distances.append(
                        hamming_distance(image_hash, other_hash)
                    )

            if not inter_distances:
                continue

            min_inter = min(inter_distances)

            # Heuristic condition
            if min_inter < min_intra:
                suspicious.append(
                    {
                        "image": image_path,
                        "assigned_class": class_name,
                        "min_intra_distance": min_intra,
                        "min_inter_distance": min_inter,
                    }
                )

    logger.info("Label noise detection completed")

    return {
        "num_suspicious": len(suspicious),
        "suspicious_images": suspicious,
    }
