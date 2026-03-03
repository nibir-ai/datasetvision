"""
CLI entrypoint for datasetvision.
"""

from pathlib import Path
import json
import typer
import logging

from datasetvision.logging_config import configure_logging
from datasetvision.scanner import scan_dataset, save_scan_report
from datasetvision.duplicates import (
    find_exact_duplicates,
    find_near_duplicates,
)
from datasetvision.stats import compute_stats
from datasetvision.reporting import generate_markdown_report
from datasetvision.class_analysis import analyze_class_distribution
from datasetvision.label_noise import detect_label_noise

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
def scan(dataset_folder: Path) -> None:
    logger.info("Starting dataset scan")

    results = scan_dataset(dataset_folder)
    output = dataset_folder / "scan_report.json"
    save_scan_report(results, output)

    typer.echo(f"Scan complete. Saved to {output}")


@app.command()
def duplicates(
    dataset_folder: Path,
    threshold: int = typer.Option(
        5,
        help="Hamming distance threshold for near-duplicate detection.",
    ),
) -> None:
    logger.info("Running duplicate detection")

    exact = find_exact_duplicates(dataset_folder)
    near = find_near_duplicates(dataset_folder, threshold=threshold)

    typer.echo(json.dumps({"exact": exact, "near": near}, indent=2))


@app.command()
def stats(dataset_folder: Path) -> None:
    logger.info("Computing dataset statistics")

    result = compute_stats(dataset_folder)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def classes(dataset_folder: Path) -> None:
    logger.info("Analyzing class distribution")

    result = analyze_class_distribution(dataset_folder)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def noise(dataset_folder: Path) -> None:
    """
    Detect potential label noise.
    """

    logger.info("Running label noise detection")

    result = detect_label_noise(dataset_folder)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def report(dataset_folder: Path) -> None:
    logger.info("Generating Markdown report")

    scan_file = dataset_folder / "scan_report.json"
    if not scan_file.exists():
        typer.echo("Run scan first.")
        raise typer.Exit(code=1)

    data = json.loads(scan_file.read_text())
    output = dataset_folder / "report.md"
    generate_markdown_report(data, output)

    typer.echo(f"Report generated at {output}")
