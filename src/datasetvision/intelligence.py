"""
Comprehensive dataset intelligence engine.
"""

from pathlib import Path
from typing import Dict, Any
import json
import numpy as np
import logging

from datasetvision.class_analysis import analyze_class_distribution
from datasetvision.label_noise import detect_label_noise
from datasetvision.hashing import perceptual_hash, hamming_distance
from datasetvision.utils import get_image_files

logger = logging.getLogger(__name__)


def _compute_similarity_matrix(dataset_path: Path) -> Dict[str, Any]:
    """
    Compute cross-class similarity matrix using perceptual hashes.
    """

    class_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
    class_hashes = {}

    for class_dir in class_dirs:
        hashes = [
            perceptual_hash(p)
            for p in get_image_files(class_dir)
        ]
        class_hashes[class_dir.name] = hashes

    similarity_matrix = {}

    for class_a, hashes_a in class_hashes.items():
        similarity_matrix[class_a] = {}

        for class_b, hashes_b in class_hashes.items():
            if not hashes_a or not hashes_b:
                similarity_matrix[class_a][class_b] = None
                continue

            distances = []
            for ha in hashes_a:
                for hb in hashes_b:
                    distances.append(hamming_distance(ha, hb))

            similarity_matrix[class_a][class_b] = float(np.mean(distances))

    return similarity_matrix


def _compute_noise_confidence(noise_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add confidence scoring to label noise detection.
    """

    suspicious = noise_result.get("suspicious_images", [])

    for entry in suspicious:
        intra = entry["min_intra_distance"]
        inter = entry["min_inter_distance"]

        if intra == float("inf"):
            confidence = 1.0
        else:
            confidence = max(0.0, min(1.0, (intra - inter) / max(intra, 1)))

        entry["confidence_score"] = round(confidence, 3)

    return noise_result


def generate_intelligence_report(dataset_path: Path) -> Dict[str, Any]:
    """
    Generate comprehensive dataset intelligence report.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    logger.info("Running class analysis")
    class_info = analyze_class_distribution(dataset_path)

    logger.info("Running label noise detection")
    noise_info = detect_label_noise(dataset_path)
    noise_info = _compute_noise_confidence(noise_info)

    logger.info("Computing similarity matrix")
    similarity_matrix = _compute_similarity_matrix(dataset_path)

    return {
        "class_analysis": class_info,
        "label_noise": noise_info,
        "similarity_matrix": similarity_matrix,
    }


def save_intelligence_json(report: Dict[str, Any], output_path: Path) -> None:
    """
    Save intelligence report as JSON.
    """
    with output_path.open("w") as f:
        json.dump(report, f, indent=4)
