"""
Dataset statistics module.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np

from datasetvision.utils import get_image_files


def compute_stats(dataset_path: Path) -> Dict[str, Any]:
    """
    Compute dataset statistics including:
    - Mean image size
    - Mean channel values
    - Number of images
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    sizes: List[Tuple[int, int]] = []
    channel_means: List[np.ndarray] = []

    image_files = get_image_files(dataset_path)

    for image_path in image_files:
        img = cv2.imread(str(image_path))

        if img is None:
            continue

        height, width = img.shape[:2]
        sizes.append((width, height))

        channel_means.append(img.mean(axis=(0, 1)))

    if not sizes:
        return {
            "num_images": 0,
            "mean_size": None,
            "mean_channel_values": None,
        }

    mean_size = tuple(np.mean(sizes, axis=0))
    mean_channels = np.mean(channel_means, axis=0)

    return {
        "num_images": len(sizes),
        "mean_size": mean_size,
        "mean_channel_values": mean_channels.tolist(),
    }
