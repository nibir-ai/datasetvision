"""
Advanced dataset drift comparison engine.
Includes global scoring, per-class breakdown,
and anomaly drift intelligence.
"""

from pathlib import Path
from typing import Dict, Any

from datasetvision.intelligence import generate_intelligence_report


def _compute_class_drift(class_a: Dict[str, Any], class_b: Dict[str, Any]) -> Dict[str, Any]:
    classes_a = class_a.get("classes", {})
    classes_b = class_b.get("classes", {})

    all_classes = sorted(set(classes_a.keys()) | set(classes_b.keys()))
    result: Dict[str, Any] = {}

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

        result[cls] = {
            "old_count": old_count,
            "new_count": new_count,
            "delta": delta,
            "percent_change": round(percent_change, 2),
            "severity": severity,
        }

    return result


def _compute_anomaly_drift(anom_a: Dict[str, Any], anom_b: Dict[str, Any]) -> Dict[str, Any]:
    all_classes = sorted(set(anom_a.keys()) | set(anom_b.keys()))
    drift: Dict[str, Any] = {}

    for cls in all_classes:
        old_outliers = anom_a.get(cls, {}).get("outlier_count", 0)
        new_outliers = anom_b.get(cls, {}).get("outlier_count", 0)

        delta = new_outliers - old_outliers

        severity = "STABLE"
        if delta > 5:
            severity = "SPIKE"
        elif delta > 0:
            severity = "INCREASE"
        elif delta < 0:
            severity = "DECREASE"

        drift[cls] = {
            "old_outliers": old_outliers,
            "new_outliers": new_outliers,
            "delta": delta,
            "severity": severity,
        }

    return drift


def _compute_global_score(raw: Dict[str, Any], class_drift: Dict[str, Any], anomaly_drift: Dict[str, Any]) -> Dict[str, Any]:
    image_delta_norm = min(abs(raw["image_count_delta"]) / 100, 1)
    imbalance_norm = min(abs(raw["imbalance_severity_delta"]) / 3, 1)
    noise_norm = min(abs(raw["noise_delta"]) / 10, 1)

    class_shift_norm = 0
    if class_drift:
        avg_shift = sum(abs(v["percent_change"]) for v in class_drift.values()) / len(class_drift)
        class_shift_norm = min(avg_shift / 100, 1)

    anomaly_shift_norm = 0
    if anomaly_drift:
        avg_anomaly = sum(abs(v["delta"]) for v in anomaly_drift.values()) / len(anomaly_drift)
        anomaly_shift_norm = min(avg_anomaly / 10, 1)

    score = (
        0.25 * image_delta_norm +
        0.25 * class_shift_norm +
        0.2 * imbalance_norm +
        0.15 * noise_norm +
        0.15 * anomaly_shift_norm
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
    report_a = generate_intelligence_report(dataset_a)
    report_b = generate_intelligence_report(dataset_b)

    fingerprint_a = report_a["dataset_fingerprint"]
    fingerprint_b = report_b["dataset_fingerprint"]

    class_a = report_a["class_analysis"]
    class_b = report_b["class_analysis"]

    noise_a = report_a["label_noise"]
    noise_b = report_b["label_noise"]

    anomaly_a = report_a.get("class_anomalies", {})
    anomaly_b = report_b.get("class_anomalies", {})

    raw_metrics = {
        "fingerprint_changed": fingerprint_a["dataset_hash"] != fingerprint_b["dataset_hash"],
        "image_count_delta": fingerprint_b["total_images"] - fingerprint_a["total_images"],
        "imbalance_severity_delta": class_b.get("imbalance", {}).get("severity_score", 0)
        - class_a.get("imbalance", {}).get("severity_score", 0),
        "noise_delta": noise_b.get("num_suspicious", 0)
        - noise_a.get("num_suspicious", 0),
        "class_count_delta": class_b.get("num_classes", 0)
        - class_a.get("num_classes", 0),
    }

    class_drift = _compute_class_drift(class_a, class_b)
    anomaly_drift = _compute_anomaly_drift(anomaly_a, anomaly_b)
    global_score = _compute_global_score(raw_metrics, class_drift, anomaly_drift)

    return {
        "dataset_a": str(dataset_a),
        "dataset_b": str(dataset_b),
        "raw_metrics": raw_metrics,
        "class_drift": class_drift,
        "anomaly_drift": anomaly_drift,
        "global_drift": global_score,
    }
