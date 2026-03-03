"""
Advanced dataset drift comparison engine with centroid shift detection.
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np

from datasetvision.intelligence import generate_intelligence_report


def _compute_centroid_drift(anom_a: Dict[str, Any], anom_b: Dict[str, Any]) -> Dict[str, Any]:
    all_classes = sorted(set(anom_a.keys()) | set(anom_b.keys()))
    result: Dict[str, Any] = {}

    for cls in all_classes:
        centroid_a = anom_a.get(cls, {}).get("centroid")
        centroid_b = anom_b.get(cls, {}).get("centroid")

        if centroid_a is None or centroid_b is None:
            continue

        vec_a = np.array(centroid_a)
        vec_b = np.array(centroid_b)

        distance = float(np.linalg.norm(vec_a - vec_b))

        if distance < 0.05:
            severity = "STABLE"
        elif distance < 0.15:
            severity = "MINOR_SHIFT"
        elif distance < 0.3:
            severity = "MODERATE_SHIFT"
        else:
            severity = "MAJOR_SHIFT"

        result[cls] = {
            "centroid_distance": round(distance, 4),
            "severity": severity,
        }

    return result


def compare_datasets(dataset_a: Path, dataset_b: Path) -> Dict[str, Any]:

    report_a = generate_intelligence_report(dataset_a)
    report_b = generate_intelligence_report(dataset_b)

    anomaly_a = report_a.get("class_anomalies", {})
    anomaly_b = report_b.get("class_anomalies", {})

    centroid_drift = _compute_centroid_drift(anomaly_a, anomaly_b)

    return {
        "dataset_a": str(dataset_a),
        "dataset_b": str(dataset_b),
        "centroid_drift": centroid_drift,
    }
