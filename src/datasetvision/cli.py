"""
DatasetVision CLI - Research-grade dataset governance tool.
"""

from pathlib import Path
import typer
import logging

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.text import Text

from datasetvision.logging_config import configure_logging
from datasetvision.intelligence import (
    generate_intelligence_report,
    save_intelligence_json,
)
from datasetvision.html_report import generate_html_report

app = typer.Typer(help="Research-grade dataset governance CLI.")

console = Console()
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
def intelligence(
    dataset_folder: Path,
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output raw JSON only.",
    ),
) -> None:
    """
    Run full dataset intelligence analysis.
    """

    if not dataset_folder.exists():
        console.print("[bold red]Dataset folder does not exist.[/bold red]")
        raise typer.Exit(code=1)

    console.print(
        Panel.fit(
            "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Research-Grade Dataset Governance[/dim]",
            border_style="cyan",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing dataset...", total=None)
        report = generate_intelligence_report(dataset_folder)
        progress.update(task, completed=100)

    json_path = dataset_folder / "intelligence_report.json"
    html_path = dataset_folder / "intelligence_report.html"

    save_intelligence_json(report, json_path)
    generate_html_report(report, html_path)

    if json_output:
        console.print_json(data=report)
        return

    console.print(Rule("[bold cyan]CLASS SUMMARY[/bold cyan]"))

    class_info = report["class_analysis"]
    imbalance = class_info.get("imbalance", {})
    noise_info = report["label_noise"]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Class", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Mean Size", justify="center")

    for cls, stats in class_info["classes"].items():
        table.add_row(
            cls,
            str(stats["count"]),
            str(stats["mean_size"]),
        )

    console.print(table)

    console.print(Rule("[bold cyan]IMBALANCE STATUS[/bold cyan]"))

    severity = imbalance.get("severity_score", 0)

    if severity == 0:
        status = Text("BALANCED", style="bold green")
    elif severity == 1:
        status = Text("MILD IMBALANCE", style="bold yellow")
    elif severity == 2:
        status = Text("MODERATE IMBALANCE", style="bold dark_orange")
    else:
        status = Text("SEVERE IMBALANCE", style="bold red")

    console.print(status)

    console.print(Rule("[bold cyan]LABEL NOISE[/bold cyan]"))

    suspicious_count = noise_info["num_suspicious"]

    if suspicious_count == 0:
        console.print("[bold green]No suspicious label noise detected.[/bold green]")
    else:
        console.print(
            f"[bold red]{suspicious_count} potentially mislabeled images detected.[/bold red]"
        )

    console.print(Rule("[bold cyan]REPORT FILES[/bold cyan]"))
    console.print(f"[green]JSON:[/green] {json_path}")
    console.print(f"[green]HTML:[/green] {html_path}")
