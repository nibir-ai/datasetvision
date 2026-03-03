"""
Class-wise dataset analysis and imbalance intelligence.
"""

from pathlib import Path
from typing import Dict, Any
import logging
import numpy as np
import cv2

from datasetvision.utils import get_image_files

logger = logging.getLogger(__name__)


def _compute_class_stats(class_path: Path) -> Dict[str, Any]:
    """
    Compute per-class statistics:
    - image count
    - mean image size
    - mean channel values
    """

    image_files = get_image_files(class_path)

    sizes = []
    channel_means = []

    for image_path in image_files:
        img = cv2.imread(str(image_path))
        if img is None:
            continue

        h, w = img.shape[:2]
        sizes.append((w, h))
        channel_means.append(img.mean(axis=(0, 1)))

    if not sizes:
        return {
            "count": 0,
            "mean_size": None,
            "mean_channel_values": None,
        }

    mean_size = tuple(np.mean(sizes, axis=0))
    mean_channels = np.mean(channel_means, axis=0)

    return {
        "count": len(sizes),
        "mean_size": mean_size,
        "mean_channel_values": mean_channels.tolist(),
    }


def _compute_imbalance_severity(counts: Dict[str, int]) -> Dict[str, Any]:
    """
    Compute imbalance severity score.
    """

    if not counts:
        return {
            "imbalance_ratio": None,
            "severity_score": 0,
            "imbalanced": False,
        }

    values = list(counts.values())

    max_count = max(values)
    min_count = min(values)

    if min_count == 0:
        imbalance_ratio = float("inf")
    else:
        imbalance_ratio = max_count / min_count

    # Severity scoring
    if imbalance_ratio <= 1.5:
        severity_score = 0  # balanced
    elif imbalance_ratio <= 2.0:
        severity_score = 1  # mild
    elif imbalance_ratio <= 5.0:
        severity_score = 2  # moderate
    else:
        severity_score = 3  # severe

    return {
        "imbalance_ratio": imbalance_ratio,
        "severity_score": severity_score,
        "imbalanced": severity_score >= 2,
    }


def analyze_class_distribution(dataset_path: Path) -> Dict[str, Any]:
    """
    Analyze class distribution and compute per-class statistics.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    subdirs = [d for d in dataset_path.iterdir() if d.is_dir()]

    # Single-class dataset fallback
    if not subdirs:
        stats = _compute_class_stats(dataset_path)
        return {
            "num_classes": 1,
            "classes": {"default": stats},
            "imbalance": {
                "imbalance_ratio": 1.0,
                "severity_score": 0,
                "imbalanced": False,
            },
        }

    class_stats: Dict[str, Dict[str, Any]] = {}
    class_counts: Dict[str, int] = {}

    for subdir in subdirs:
        stats = _compute_class_stats(subdir)
        class_stats[subdir.name] = stats
        class_counts[subdir.name] = stats["count"]

    imbalance_info = _compute_imbalance_severity(class_counts)

    logger.info("Class intelligence analysis completed")

    return {
        "num_classes": len(class_stats),
        "classes": class_stats,
        "imbalance": imbalance_info,
    }
