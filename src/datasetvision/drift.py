"""
Advanced dataset drift comparison engine.
Now integrates embedding centroid drift into global severity scoring.
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np

from datasetvision.intelligence import generate_intelligence_report


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
    raw: Dict[str, Any],
    class_drift: Dict[str, Any],
    anomaly_drift: Dict[str, Any],
    centroid_drift: Dict[str, Any],
) -> Dict[str, Any]:

    image_delta_norm = min(abs(raw.get("image_count_delta", 0)) / 100, 1)
    imbalance_norm = min(abs(raw.get("imbalance_severity_delta", 0)) / 3, 1)
    noise_norm = min(abs(raw.get("noise_delta", 0)) / 10, 1)

    # Class distribution shift
    class_shift_norm = 0
    if class_drift:
        avg_shift = sum(abs(v["percent_change"]) for v in class_drift.values()) / len(class_drift)
        class_shift_norm = min(avg_shift / 100, 1)

    # Anomaly count shift
    anomaly_shift_norm = 0
    if anomaly_drift:
        avg_anomaly = sum(abs(v["delta"]) for v in anomaly_drift.values()) / len(anomaly_drift)
        anomaly_shift_norm = min(avg_anomaly / 10, 1)

    # Centroid semantic shift
    centroid_shift_norm = 0
    if centroid_drift:
        avg_centroid = sum(v["centroid_distance"] for v in centroid_drift.values()) / len(centroid_drift)
        centroid_shift_norm = min(avg_centroid / 0.5, 1)

    # Weighted score
    score = (
        0.20 * image_delta_norm +
        0.20 * class_shift_norm +
        0.15 * imbalance_norm +
        0.10 * noise_norm +
        0.15 * anomaly_shift_norm +
        0.20 * centroid_shift_norm
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
# MAIN COMPARISON
# ------------------------------------------------------------

def compare_datasets(dataset_a: Path, dataset_b: Path) -> Dict[str, Any]:

    report_a = generate_intelligence_report(dataset_a)
    report_b = generate_intelligence_report(dataset_b)

    anomaly_a = report_a.get("class_anomalies", {})
    anomaly_b = report_b.get("class_anomalies", {})

    centroid_drift = _compute_centroid_drift(anomaly_a, anomaly_b)

    # Raw metrics (minimal for now)
    raw_metrics = {
        "image_count_delta": report_b["dataset_fingerprint"]["total_images"]
        - report_a["dataset_fingerprint"]["total_images"],
        "imbalance_severity_delta": 0,
        "noise_delta": 0,
    }

    # Empty placeholders (can expand later)
    class_drift: Dict[str, Any] = {}
    anomaly_drift: Dict[str, Any] = {}

    global_score = _compute_global_score(
        raw_metrics,
        class_drift,
        anomaly_drift,
        centroid_drift,
    )

    return {
        "dataset_a": str(dataset_a),
        "dataset_b": str(dataset_b),
        "centroid_drift": centroid_drift,
        "global_drift": global_score,
    }
