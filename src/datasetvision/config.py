"""
Configuration loader for DatasetVision governance policies.
"""

from pathlib import Path
from typing import Dict, Any
import yaml


DEFAULT_CONFIG: Dict[str, Any] = {
    "governance": {
        "max_imbalance_severity": 2,
        "allow_label_noise": False,
        "max_noise_count": 0,
        "strict": True,
    }
}


def load_config(dataset_path: Path) -> Dict[str, Any]:
    """
    Load datasetvision.yaml if present.
    Otherwise return default configuration.
    """

    config_path = dataset_path / "datasetvision.yaml"

    if not config_path.exists():
        return DEFAULT_CONFIG

    with config_path.open("r") as f:
        user_config = yaml.safe_load(f) or {}

    # Merge with defaults
    merged = DEFAULT_CONFIG.copy()
    merged.update(user_config)

    return merged
