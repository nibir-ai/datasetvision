"""
CLI entrypoint for datasetvision.
"""

from pathlib import Path
import json
import typer

from datasetvision.scanner import scan_dataset, save_scan_report
from datasetvision.duplicates import find_exact_duplicates, find_near_duplicates
from datasetvision.stats import compute_stats
from datasetvision.reporting import generate_markdown_report

app = typer.Typer(help="Offline dataset auditing tool.")


@app.command()
def scan(dataset_folder: Path) -> None:
    """Scan dataset for integrity issues."""
    results = scan_dataset(dataset_folder)
    output = dataset_folder / "scan_report.json"
    save_scan_report(results, output)
    typer.echo(f"Scan complete. Saved to {output}")


@app.command()
def duplicates(dataset_folder: Path) -> None:
    """Detect duplicate images."""
    exact = find_exact_duplicates(dataset_folder)
    near = find_near_duplicates(dataset_folder)
    typer.echo(json.dumps({"exact": exact, "near": near}, indent=2))


@app.command()
def stats(dataset_folder: Path) -> None:
    """Compute dataset statistics."""
    result = compute_stats(dataset_folder)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def report(dataset_folder: Path) -> None:
    """Generate Markdown report."""
    scan_file = dataset_folder / "scan_report.json"
    if not scan_file.exists():
        typer.echo("Run scan first.")
        raise typer.Exit(code=1)

    data = json.loads(scan_file.read_text())
    output = dataset_folder / "report.md"
    generate_markdown_report(data, output)
    typer.echo(f"Report generated at {output}")
