"""
Advanced dataset drift comparison engine.
Provides global severity scoring and per-class breakdown.
"""

from pathlib import Path
from typing import Dict, Any
import math

from datasetvision.intelligence import generate_intelligence_report


def _compute_class_drift(class_a: Dict[str, Any], class_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute per-class distribution drift.
    """

    classes_a = class_a.get("classes", {})
    classes_b = class_b.get("classes", {})

    all_classes = sorted(set(classes_a.keys()) | set(classes_b.keys()))

    class_drift: Dict[str, Any] = {}

    for cls in all_classes:
        old_count = classes_a.get(cls, {}).get("count", 0)
        new_count = classes_b.get(cls, {}).get("count", 0)

        delta = new_count - old_count

        percent_change = (
            (delta / old_count) * 100 if old_count > 0 else (100 if new_count > 0 else 0)
        )

        severity = "LOW"
        if abs(percent_change) > 50:
            severity = "HIGH"
        elif abs(percent_change) > 20:
            severity = "MODERATE"

        class_drift[cls] = {
            "old_count": old_count,
            "new_count": new_count,
            "delta": delta,
            "percent_change": round(percent_change, 2),
            "severity": severity,
        }

    return class_drift


def _compute_global_score(raw_metrics: Dict[str, Any], class_drift: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute normalized global drift severity score.
    """

    image_delta_norm = min(abs(raw_metrics["image_count_delta"]) / 100, 1)
    imbalance_norm = min(abs(raw_metrics["imbalance_severity_delta"]) / 3, 1)
    noise_norm = min(abs(raw_metrics["noise_delta"]) / 10, 1)

    class_shift_norm = 0
    if class_drift:
        avg_shift = sum(
            abs(v["percent_change"]) for v in class_drift.values()
        ) / len(class_drift)
        class_shift_norm = min(avg_shift / 100, 1)

    score = (
        0.3 * image_delta_norm +
        0.3 * class_shift_norm +
        0.2 * imbalance_norm +
        0.2 * noise_norm
    )

    if score < 0.2:
        severity = "LOW"
    elif score < 0.5:
        severity = "MODERATE"
    elif score < 0.75:
        severity = "HIGH"
    else:
        severity = "CRITICAL"

    return {
        "score": round(score, 3),
        "severity": severity,
    }


def compare_datasets(dataset_a: Path, dataset_b: Path) -> Dict[str, Any]:
    """
    Compare two datasets with layered drift intelligence.
    """

    report_a = generate_intelligence_report(dataset_a)
    report_b = generate_intelligence_report(dataset_b)

    fingerprint_a = report_a["dataset_fingerprint"]
    fingerprint_b = report_b["dataset_fingerprint"]

    class_a = report_a["class_analysis"]
    class_b = report_b["class_analysis"]

    noise_a = report_a["label_noise"]
    noise_b = report_b["label_noise"]

    raw_metrics = {
        "fingerprint_changed": fingerprint_a["dataset_hash"]
        != fingerprint_b["dataset_hash"],
        "image_count_delta": fingerprint_b["total_images"]
        - fingerprint_a["total_images"],
        "imbalance_severity_delta": class_b.get("imbalance", {}).get("severity_score", 0)
        - class_a.get("imbalance", {}).get("severity_score", 0),
        "noise_delta": noise_b.get("num_suspicious", 0)
        - noise_a.get("num_suspicious", 0),
        "class_count_delta": class_b.get("num_classes", 0)
        - class_a.get("num_classes", 0),
    }

    class_drift = _compute_class_drift(class_a, class_b)
    global_score = _compute_global_score(raw_metrics, class_drift)

    return {
        "dataset_a": str(dataset_a),
        "dataset_b": str(dataset_b),
        "raw_metrics": raw_metrics,
        "class_drift": class_drift,
        "global_drift": global_score,
    }
