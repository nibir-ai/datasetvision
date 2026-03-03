"""
CLI entrypoint for datasetvision.
"""

from pathlib import Path
import json
import typer
import logging

from datasetvision.logging_config import configure_logging
from datasetvision.intelligence import (
    generate_intelligence_report,
    save_intelligence_json,
)
from datasetvision.html_report import generate_html_report

app = typer.Typer(help="Offline dataset auditing tool.")

logger = logging.getLogger(__name__)


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging.",
    ),
) -> None:
    configure_logging(verbose)


@app.command()
def intelligence(dataset_folder: Path) -> None:
    """
    Run full dataset intelligence analysis.
    """

    logger.info("Running full intelligence analysis")

    report = generate_intelligence_report(dataset_folder)

    json_path = dataset_folder / "intelligence_report.json"
    html_path = dataset_folder / "intelligence_report.html"

    save_intelligence_json(report, json_path)
    generate_html_report(report, html_path)

    typer.echo(f"Intelligence report saved to:")
    typer.echo(f" - {json_path}")
    typer.echo(f" - {html_path}")
