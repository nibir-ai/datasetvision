"""
Governance policy enforcement engine.
"""

from typing import Dict, Any


def evaluate_policies(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate governance policies against report.
    """

    violations = []

    imbalance = report["class_analysis"].get("imbalance", {})
    severity = imbalance.get("severity_score", 0)

    if severity >= 2:
        violations.append("Class imbalance severity too high")

    noise_count = report["label_noise"].get("num_suspicious", 0)

    if noise_count > 0:
        violations.append("Potential label noise detected")

    return {
        "violations": violations,
        "policy_passed": len(violations) == 0,
    }

