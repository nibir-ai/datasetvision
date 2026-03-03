"""
Class-level anomaly detection engine.
Uses perceptual hash statistical modeling.
"""

from pathlib import Path
from typing import Dict, Any, List
import statistics

from datasetvision.hashing import perceptual_hash, hamming_distance
from datasetvision.utils import get_image_files


def analyze_class_anomalies(dataset_path: Path, sigma: float = 2.0) -> Dict[str, Any]:
    """
    Detect intra-class anomalies using perceptual hash distance statistics.
    """

    class_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
    results: Dict[str, Any] = {}

    for class_dir in class_dirs:
        image_files = list(get_image_files(class_dir))

        if len(image_files) < 3:
            # Not enough samples for statistical modeling
            continue

        hashes = [perceptual_hash(p) for p in image_files]

        # Compute centroid (mean hash as bitwise majority vote)
        bit_length = 64
        centroid_bits = []

        for bit in range(bit_length):
            ones = sum((h >> bit) & 1 for h in hashes)
            centroid_bits.append(1 if ones > len(hashes) / 2 else 0)

        centroid = 0
        for i, bit in enumerate(centroid_bits):
            centroid |= (bit << i)

        distances: List[int] = [
            hamming_distance(h, centroid) for h in hashes
        ]

        mean_dist = statistics.mean(distances)
        std_dist = statistics.stdev(distances)

        threshold = mean_dist + sigma * std_dist

        outliers = [
            str(image_files[i])
            for i, d in enumerate(distances)
            if d > threshold
        ]

        total = len(image_files)
        outlier_ratio = len(outliers) / total

        if outlier_ratio == 0:
            severity = "HEALTHY"
        elif outlier_ratio <= 0.05:
            severity = "MILD"
        elif outlier_ratio <= 0.15:
            severity = "MODERATE"
        else:
            severity = "SEVERE"

        results[class_dir.name] = {
            "mean_distance": round(mean_dist, 3),
            "std_distance": round(std_dist, 3),
            "variance": round(statistics.variance(distances), 3),
            "outlier_count": len(outliers),
            "total_images": total,
            "severity": severity,
            "outliers": outliers,
        }

    return results
