"""
Advanced class-level anomaly detection using feature embeddings.
CPU-only, offline, statistical modeling.
"""

from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import cv2
import statistics

from datasetvision.utils import get_image_files


def _compute_embedding(image_path: Path) -> np.ndarray:
    """
    Compute lightweight image embedding using
    32x32 grayscale normalized pixel vector.
    """

    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError(f"Unreadable image: {image_path}")

    resized = cv2.resize(img, (32, 32))
    vector = resized.flatten().astype(np.float32)

    # Normalize
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector

    return vector / norm


def analyze_class_anomalies(
    dataset_path: Path,
    z_threshold: float = 2.5,
) -> Dict[str, Any]:
    """
    Detect intra-class anomalies using embedding-based z-score modeling.
    """

    class_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
    results: Dict[str, Any] = {}

    for class_dir in class_dirs:
        image_files = list(get_image_files(class_dir))

        if len(image_files) < 5:
            # Too few samples for reliable stats
            continue

        embeddings: List[np.ndarray] = []
        valid_paths: List[Path] = []

        for img_path in image_files:
            try:
                emb = _compute_embedding(img_path)
                embeddings.append(emb)
                valid_paths.append(img_path)
            except Exception:
                continue

        if len(embeddings) < 5:
            continue

        matrix = np.vstack(embeddings)

        centroid = np.mean(matrix, axis=0)

        distances = np.linalg.norm(matrix - centroid, axis=1)

        mean_dist = float(np.mean(distances))
        std_dist = float(np.std(distances))

        if std_dist == 0:
            continue

        z_scores = (distances - mean_dist) / std_dist

        outliers = [
            str(valid_paths[i])
            for i, z in enumerate(z_scores)
            if abs(z) > z_threshold
        ]

        outlier_ratio = len(outliers) / len(valid_paths)

        if outlier_ratio == 0:
            severity = "HEALTHY"
        elif outlier_ratio <= 0.05:
            severity = "MILD"
        elif outlier_ratio <= 0.15:
            severity = "MODERATE"
        else:
            severity = "SEVERE"

        results[class_dir.name] = {
            "mean_distance": round(mean_dist, 4),
            "std_distance": round(std_dist, 4),
            "outlier_count": len(outliers),
            "total_images": len(valid_paths),
            "severity": severity,
            "outliers": outliers,
        }

    return results
