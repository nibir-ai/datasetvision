"""
Comprehensive dataset intelligence engine.
Includes anomaly intelligence layer.
"""

from pathlib import Path
from typing import Dict, Any
import json
import logging
from datetime import datetime

from datasetvision.class_analysis import analyze_class_distribution
from datasetvision.label_noise import detect_label_noise
from datasetvision.fingerprint import generate_dataset_fingerprint
from datasetvision.anomaly import analyze_class_anomalies

logger = logging.getLogger(__name__)

REPORT_SCHEMA_VERSION = "3.0"


def generate_intelligence_report(dataset_path: Path) -> Dict[str, Any]:
    """
    Generate full deterministic dataset governance report.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    fingerprint = generate_dataset_fingerprint(dataset_path)
    class_info = analyze_class_distribution(dataset_path)
    noise_info = detect_label_noise(dataset_path)
    anomaly_info = analyze_class_anomalies(dataset_path)

    report: Dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at_utc": datetime.utcnow().isoformat(),
        "dataset_fingerprint": fingerprint,
        "class_analysis": class_info,
        "label_noise": noise_info,
        "class_anomalies": anomaly_info,
    }

    return report


def save_intelligence_json(report: Dict[str, Any], output_path: Path) -> None:
    with output_path.open("w") as f:
        json.dump(report, f, indent=4, sort_keys=True)
