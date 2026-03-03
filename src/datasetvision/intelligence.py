"""
Comprehensive dataset intelligence engine.
"""

from pathlib import Path
from typing import Dict, Any
import json
import logging
from datetime import datetime

from datasetvision.class_analysis import analyze_class_distribution
from datasetvision.label_noise import detect_label_noise
from datasetvision.hashing import perceptual_hash, hamming_distance
from datasetvision.utils import get_image_files
from datasetvision.fingerprint import generate_dataset_fingerprint

logger = logging.getLogger(__name__)

REPORT_SCHEMA_VERSION = "2.0"


def generate_intelligence_report(dataset_path: Path) -> Dict[str, Any]:
    """
    Generate comprehensive dataset governance report.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_path} does not exist")

    fingerprint = generate_dataset_fingerprint(dataset_path)
    class_info = analyze_class_distribution(dataset_path)
    noise_info = detect_label_noise(dataset_path)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": datetime.utcnow().isoformat(),
        "dataset_fingerprint": fingerprint,
        "class_analysis": class_info,
        "label_noise": noise_info,
    }


def save_intelligence_json(report: Dict[str, Any], output_path: Path) -> None:
    """
    Save intelligence report as JSON.
    """
    with output_path.open("w") as f:
        json.dump(report, f, indent=4, sort_keys=True)
