"""
DatasetVision CLI - Smart Governance + Drift Intelligence
"""

from pathlib import Path
import typer
import logging

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.align import Align
from rich.table import Table
from rich import box

from datasetvision.logging_config import configure_logging
from datasetvision.intelligence import generate_intelligence_report
from datasetvision.drift import compare_datasets

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    configure_logging(verbose)


@app.command()
def intelligence(dataset_folder: Path):
    if not dataset_folder.exists():
        console.print("[red]Dataset folder does not exist.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Anomaly-Aware Intelligence[/dim]",
                box=box.ROUNDED,
                border_style="cyan",
            )
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Running intelligence engine..."),
        console=console,
    ):
        report = generate_intelligence_report(dataset_folder)

    anomalies = report.get("class_anomalies", {})

    console.print(Rule("[bold cyan] CLASS ANOMALIES [/bold cyan]"))

    if not anomalies:
        console.print("[green]No anomaly data available.[/green]")
    else:
        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("Class", style="cyan")
        table.add_column("Outliers")
        table.add_column("Total")
        table.add_column("Severity")

        for cls, stats in anomalies.items():
            severity_color = {
                "HEALTHY": "green",
                "MILD": "yellow",
                "MODERATE": "orange1",
                "SEVERE": "red",
            }.get(stats["severity"], "white")

            table.add_row(
                cls,
                str(stats["outlier_count"]),
                str(stats["total_images"]),
                f"[{severity_color}]{stats['severity']}[/{severity_color}]",
            )

        console.print(table)

    console.print()


@app.command()
def drift(dataset_a: Path, dataset_b: Path):
    if not dataset_a.exists() or not dataset_b.exists():
        console.print("[red]Dataset paths invalid.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASET DRIFT ANALYSIS[/bold cyan]",
                box=box.ROUNDED,
                border_style="cyan",
            )
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]Computing drift..."),
        console=console,
    ):
        drift_report = compare_datasets(dataset_a, dataset_b)

    global_drift = drift_report["global_drift"]
    anomaly_drift = drift_report["anomaly_drift"]

    console.print(Rule("[bold cyan] GLOBAL DRIFT [/bold cyan]"))
    console.print(
        f"[bold]{global_drift['severity']}[/bold] (score={global_drift['score']})"
    )

    console.print(Rule("[bold cyan] ANOMALY DRIFT [/bold cyan]"))

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Class", style="cyan")
    table.add_column("Old")
    table.add_column("New")
    table.add_column("Δ")
    table.add_column("Severity")

    for cls, stats in anomaly_drift.items():
        severity_color = {
            "STABLE": "green",
            "INCREASE": "yellow",
            "SPIKE": "red",
            "DECREASE": "cyan",
        }.get(stats["severity"], "white")

        table.add_row(
            cls,
            str(stats["old_outliers"]),
            str(stats["new_outliers"]),
            str(stats["delta"]),
            f"[{severity_color}]{stats['severity']}[/{severity_color}]",
        )

    console.print(table)
    console.print()
