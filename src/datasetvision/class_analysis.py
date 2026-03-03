"""
Class-wise dataset analysis and imbalance detection.
"""

from pathlib import Path
from typing import Dict, Any
import logging

from datasetvision.utils import get_image_files

logger = logging.getLogger(__name__)


def analyze_class_distribution(dataset_path: Path) -> Dict[str, Any]:
    """
    Analyze class-wise image distribution.

    Assumes dataset structure:
        dataset/
            class_a/
            class_b/
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    class_counts: Dict[str, int] = {}

    # Identify immediate subdirectories as classes
    subdirs = [d for d in dataset_path.iterdir() if d.is_dir()]

    # If no subdirectories, treat entire folder as single class
    if not subdirs:
        total_images = len(get_image_files(dataset_path))
        return {
            "num_classes": 1,
            "class_counts": {"default": total_images},
            "imbalance_ratio": 1.0,
            "imbalanced": False,
        }

    for subdir in subdirs:
        images = get_image_files(subdir)
        class_counts[subdir.name] = len(images)

    if not class_counts:
        return {
            "num_classes": 0,
            "class_counts": {},
            "imbalance_ratio": None,
            "imbalanced": False,
        }

    max_count = max(class_counts.values())
    min_count = min(class_counts.values())

    imbalance_ratio = max_count / min_count if min_count > 0 else float("inf")

    # Simple imbalance rule:
    # If largest class is >2x smallest class → flag
    imbalanced = imbalance_ratio > 2.0

    logger.info("Class analysis completed")

    return {
        "num_classes": len(class_counts),
        "class_counts": class_counts,
        "imbalance_ratio": imbalance_ratio,
        "imbalanced": imbalanced,
    }
