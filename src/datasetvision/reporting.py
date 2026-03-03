"""
Markdown reporting module.
"""

from pathlib import Path
from typing import Dict, Any


def generate_markdown_report(
    scan_results: Dict[str, Any],
    output_path: Path,
) -> None:
    """
    Generate a Markdown summary report from scan results.
    """

    lines = [
        "# DatasetVision Report",
        "",
        f"**Total Images:** {scan_results.get('total_images', 0)}",
        "",
        f"**Corrupted Images:** {len(scan_results.get('corrupted', []))}",
        f"**Blank Images:** {len(scan_results.get('blank', []))}",
        f"**Extreme Aspect Ratio Images:** {len(scan_results.get('extreme_aspect_ratio', []))}",
        "",
        "## Notes",
        "",
        "- Corrupted images could not be read by OpenCV.",
        "- Blank images have extremely low pixel variance.",
        "- Extreme aspect ratio threshold: >5 or <0.2.",
    ]

    output_path.write_text("\n".join(lines))
