"""
Dataset drift comparison engine.
"""

from pathlib import Path
from typing import Dict, Any

from datasetvision.intelligence import generate_intelligence_report


def compare_datasets(
    dataset_a: Path,
    dataset_b: Path,
) -> Dict[str, Any]:
    """
    Compare two datasets and compute drift metrics.
    """

    report_a = generate_intelligence_report(dataset_a)
    report_b = generate_intelligence_report(dataset_b)

    fingerprint_a = report_a["dataset_fingerprint"]
    fingerprint_b = report_b["dataset_fingerprint"]

    class_a = report_a["class_analysis"]
    class_b = report_b["class_analysis"]

    noise_a = report_a["label_noise"]
    noise_b = report_b["label_noise"]

    drift: Dict[str, Any] = {
        "fingerprint_changed": fingerprint_a["dataset_hash"]
        != fingerprint_b["dataset_hash"],
        "image_count_delta": (
            fingerprint_b["total_images"] - fingerprint_a["total_images"]
        ),
        "imbalance_severity_delta": (
            class_b.get("imbalance", {}).get("severity_score", 0)
            - class_a.get("imbalance", {}).get("severity_score", 0)
        ),
        "noise_delta": (
            noise_b.get("num_suspicious", 0)
            - noise_a.get("num_suspicious", 0)
        ),
        "class_count_delta": (
            class_b.get("num_classes", 0)
            - class_a.get("num_classes", 0)
        ),
    }

    return {
        "dataset_a": str(dataset_a),
        "dataset_b": str(dataset_b),
        "drift_metrics": drift,
    }
