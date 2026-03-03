"""
Dataset scanning module.
"""

from pathlib import Path
from typing import Dict, Any
import json
import cv2
import numpy as np

from datasetvision.utils import get_image_files


def scan_dataset(dataset_path: Path) -> Dict[str, Any]:
    """
    Scan dataset directory for corrupted, blank, and extreme aspect ratio images.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    results: Dict[str, Any] = {
        "total_images": 0,
        "corrupted": [],
        "blank": [],
        "extreme_aspect_ratio": [],
        "dimensions": [],
    }

    image_files = get_image_files(dataset_path)
    results["total_images"] = len(image_files)

    for img_path in image_files:
        try:
            img = cv2.imread(str(img_path))

            if img is None:
                results["corrupted"].append(str(img_path))
                continue

            height, width = img.shape[:2]

            results["dimensions"].append(
                {"path": str(img_path), "width": width, "height": height}
            )

            if height == 0 or width == 0:
                results["corrupted"].append(str(img_path))
                continue

            aspect_ratio = width / height

            if aspect_ratio > 5 or aspect_ratio < 0.2:
                results["extreme_aspect_ratio"].append(str(img_path))

            if np.std(img) < 1:
                results["blank"].append(str(img_path))

        except Exception:
            results["corrupted"].append(str(img_path))

    return results


def save_scan_report(results: Dict[str, Any], output_path: Path) -> None:
    """
    Save scan results to JSON file.
    """
    with output_path.open("w") as f:
        json.dump(results, f, indent=4)
