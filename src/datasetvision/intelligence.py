"""
Comprehensive dataset intelligence engine.
Industry-grade deterministic governance report.
"""

from pathlib import Path
from typing import Dict, Any
import json
import logging
from datetime import datetime
import numpy as np

from datasetvision.class_analysis import analyze_class_distribution
from datasetvision.label_noise import detect_label_noise
from datasetvision.fingerprint import generate_dataset_fingerprint
from datasetvision.hashing import perceptual_hash, hamming_distance
from datasetvision.utils import get_image_files

logger = logging.getLogger(__name__)

REPORT_SCHEMA_VERSION = "2.1"


def _compute_similarity_matrix(dataset_path: Path) -> Dict[str, Dict[str, float | None]]:
    """
    Compute cross-class similarity matrix using perceptual hashes.
    """

    class_dirs = sorted([d for d in dataset_path.iterdir() if d.is_dir()])
    class_hashes: Dict[str, list[int]] = {}

    for class_dir in class_dirs:
        hashes = [
            perceptual_hash(p)
            for p in get_image_files(class_dir)
        ]
        class_hashes[class_dir.name] = hashes

    similarity_matrix: Dict[str, Dict[str, float | None]] = {}

    for class_a, hashes_a in class_hashes.items():
        similarity_matrix[class_a] = {}

        for class_b, hashes_b in class_hashes.items():
            if not hashes_a or not hashes_b:
                similarity_matrix[class_a][class_b] = None
                continue

            distances = [
                hamming_distance(ha, hb)
                for ha in hashes_a
                for hb in hashes_b
            ]

            similarity_matrix[class_a][class_b] = float(np.mean(distances))

    return similarity_matrix


def generate_intelligence_report(dataset_path: Path) -> Dict[str, Any]:
    """
    Generate full deterministic dataset governance report.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    logger.info("Generating dataset fingerprint")
    fingerprint = generate_dataset_fingerprint(dataset_path)

    logger.info("Running class analysis")
    class_info = analyze_class_distribution(dataset_path)

    logger.info("Running label noise detection")
    noise_info = detect_label_noise(dataset_path)

    logger.info("Computing similarity matrix")
    similarity_matrix = _compute_similarity_matrix(dataset_path)

    report: Dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at_utc": datetime.utcnow().isoformat(),
        "dataset_fingerprint": fingerprint,
        "class_analysis": class_info,
        "label_noise": noise_info,
        "similarity_matrix": similarity_matrix,
    }

    return report


def save_intelligence_json(report: Dict[str, Any], output_path: Path) -> None:
    """
    Save deterministic JSON report.
    """

    with output_path.open("w") as f:
        json.dump(
            report,
            f,
            indent=4,
            sort_keys=True,
        )
