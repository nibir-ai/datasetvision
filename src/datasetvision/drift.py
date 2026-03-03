"""
Advanced dataset drift comparison engine.
Fully structured output with centroid semantic drift integrated.
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np

from datasetvision.intelligence import generate_intelligence_report


# ------------------------------------------------------------
# ANOMALY COUNT DRIFT
# ------------------------------------------------------------

def _compute_anomaly_drift(anom_a: Dict[str, Any], anom_b: Dict[str, Any]) -> Dict[str, Any]:
    all_classes = sorted(set(anom_a.keys()) | set(anom_b.keys()))
    result: Dict[str, Any] = {}

    for cls in all_classes:
        old_out = anom_a.get(cls, {}).get("outlier_count", 0)
        new_out = anom_b.get(cls, {}).get("outlier_count", 0)

        delta = new_out - old_out

        if delta > 5:
            severity = "SPIKE"
        elif delta > 0:
            severity = "INCREASE"
        elif delta < 0:
            severity = "DECREASE"
        else:
            severity = "STABLE"

        result[cls] = {
            "old_outliers": old_out,
            "new_outliers": new_out,
            "delta": delta,
            "severity": severity,
        }

    return result


# ------------------------------------------------------------
# CENTROID DRIFT
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# GLOBAL SCORING
# ------------------------------------------------------------

def _compute_global_score(
    image_delta: int,
    anomaly_drift: Dict[str, Any],
    centroid_drift: Dict[str, Any],
) -> Dict[str, Any]:

    image_norm = min(abs(image_delta) / 100, 1)

    anomaly_norm = 0
    if anomaly_drift:
        avg = sum(abs(v["delta"]) for v in anomaly_drift.values()) / len(anomaly_drift)
        anomaly_norm = min(avg / 10, 1)

    centroid_norm = 0
    if centroid_drift:
        avg = sum(v["centroid_distance"] for v in centroid_drift.values()) / len(centroid_drift)
        centroid_norm = min(avg / 0.5, 1)

    score = (
        0.4 * image_norm +
        0.3 * anomaly_norm +
        0.3 * centroid_norm
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


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def compare_datasets(dataset_a: Path, dataset_b: Path) -> Dict[str, Any]:

    report_a = generate_intelligence_report(dataset_a)
    report_b = generate_intelligence_report(dataset_b)

    anomaly_a = report_a.get("class_anomalies", {})
    anomaly_b = report_b.get("class_anomalies", {})

    anomaly_drift = _compute_anomaly_drift(anomaly_a, anomaly_b)
    centroid_drift = _compute_centroid_drift(anomaly_a, anomaly_b)

    image_delta = (
        report_b["dataset_fingerprint"]["total_images"]
        - report_a["dataset_fingerprint"]["total_images"]
    )

    global_score = _compute_global_score(
        image_delta,
        anomaly_drift,
        centroid_drift,
    )

    return {
        "dataset_a": str(dataset_a),
        "dataset_b": str(dataset_b),
        "anomaly_drift": anomaly_drift,
        "centroid_drift": centroid_drift,
        "global_drift": global_score,
    }
