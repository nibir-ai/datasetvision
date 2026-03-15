"""
HTML report generator for dataset intelligence.
"""

from pathlib import Path
from typing import Dict, Any


def generate_html_report(report: Dict[str, Any], output_path: Path) -> None:
    """
    Generate simple HTML visualization of intelligence report.
    """

    html = f"""
    <html>
    <head>
        <title>DatasetVision Intelligence Report</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #333; }}
            pre {{ background: #f4f4f4; padding: 15px; }}
        </style>
    </head>
    <body>
        <h1>DatasetVision Intelligence Report</h1>

        <h2>Class Analysis</h2>
        <pre>{report['class_analysis']}</pre>

        <h2>Label Noise</h2>
        <pre>{report['label_noise']}</pre>

        <h2>Class Anomalies</h2>
        <pre>{report.get('class_anomalies', 'N/A')}</pre>
    </body>
    </html>
    """

    output_path.write_text(html)
