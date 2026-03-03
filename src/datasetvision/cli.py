"""
DatasetVision CLI - Industry Dataset Governance Tool
Premium UX + Advisory Drift Engine
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
from datasetvision.intelligence import (
    generate_intelligence_report,
    save_intelligence_json,
)
from datasetvision.html_report import generate_html_report
from datasetvision.policy import evaluate_policies
from datasetvision.config import load_config
from datasetvision.drift import compare_datasets

app = typer.Typer(help="DatasetVision - Industry Dataset Governance CLI.")

console = Console()
logger = logging.getLogger(__name__)


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    configure_logging(verbose)


# ------------------------------------------------------------
# INTELLIGENCE COMMAND
# ------------------------------------------------------------

@app.command()
def intelligence(dataset_folder: Path) -> None:

    if not dataset_folder.exists():
        console.print("[bold red]Dataset folder does not exist.[/bold red]")
        raise typer.Exit(code=1)

    config = load_config(dataset_folder)

    console.print()
    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Governance Intelligence Engine[/dim]",
                border_style="cyan",
                padding=(1, 6),
                box=box.ROUNDED,
            )
        )
    )

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold] Running intelligence engine..."),
        console=console,
    ):
        report = generate_intelligence_report(dataset_folder)

    policy_result = evaluate_policies(report, config)

    json_path = dataset_folder / "intelligence_report.json"
    html_path = dataset_folder / "intelligence_report.html"

    save_intelligence_json(report, json_path)
    generate_html_report(report, html_path)

    console.print(Rule("[bold cyan] GOVERNANCE STATUS [/bold cyan]"))

    if policy_result["policy_passed"]:
        console.print("[bold green]✓ Policies passed.[/bold green]")
    else:
        console.print("[bold yellow]⚠ Policy violations detected.[/bold yellow]")
        for violation in policy_result["violations"]:
            console.print(f"[yellow]  - {violation}[/yellow]")

        if config["governance"].get("strict", True):
            console.print("[bold red]Strict mode enabled. Exiting with code 1.[/bold red]")
            raise typer.Exit(code=1)

    console.print(Rule("[bold cyan] OUTPUT [/bold cyan]"))
    console.print(f"[green]JSON →[/green] {json_path}")
    console.print(f"[green]HTML →[/green] {html_path}")
    console.print()


# ------------------------------------------------------------
# DRIFT COMMAND
# ------------------------------------------------------------

@app.command()
def drift(dataset_a: Path, dataset_b: Path) -> None:
    """
    Compare two dataset versions and report layered drift intelligence.
    """

    if not dataset_a.exists() or not dataset_b.exists():
        console.print("[bold red]One or both dataset paths do not exist.[/bold red]")
        raise typer.Exit(code=1)

    console.print()
    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASET DRIFT ANALYSIS[/bold cyan]\n[dim]Layered Drift Intelligence[/dim]",
                border_style="cyan",
                padding=(1, 6),
                box=box.ROUNDED,
            )
        )
    )

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold] Comparing datasets..."),
        console=console,
    ):
        drift_report = compare_datasets(dataset_a, dataset_b)

    raw = drift_report["raw_metrics"]
    class_drift = drift_report["class_drift"]
    global_drift = drift_report["global_drift"]

    console.print(Rule("[bold cyan] GLOBAL DRIFT SCORE [/bold cyan]"))

    severity = global_drift["severity"]
    score = global_drift["score"]

    severity_colors = {
        "LOW": "green",
        "MODERATE": "yellow",
        "HIGH": "orange1",
        "CRITICAL": "red",
    }

    color = severity_colors.get(severity, "white")

    console.print(
        Panel(
            f"[bold {color}]{severity}[/bold {color}]\n"
            f"[dim]Drift Score:[/dim] {score}",
            border_style=color,
            box=box.ROUNDED,
        )
    )

    console.print(Rule("[bold cyan] RAW METRICS [/bold cyan]"))

    for key, value in raw.items():
        if isinstance(value, bool):
            color = "red" if value else "green"
            console.print(f"[{color}]{key}: {value}[/{color}]")
        else:
            if value > 0:
                console.print(f"[yellow]{key}: +{value}[/yellow]")
            elif value < 0:
                console.print(f"[cyan]{key}: {value}[/cyan]")
            else:
                console.print(f"{key}: {value}")

    console.print(Rule("[bold cyan] PER-CLASS DRIFT [/bold cyan]"))

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Class", style="cyan")
    table.add_column("Old")
    table.add_column("New")
    table.add_column("Δ")
    table.add_column("%Δ")
    table.add_column("Severity")

    for cls, stats in class_drift.items():
        severity_color = {
            "LOW": "green",
            "MODERATE": "yellow",
            "HIGH": "red",
        }.get(stats["severity"], "white")

        table.add_row(
            cls,
            str(stats["old_count"]),
            str(stats["new_count"]),
            str(stats["delta"]),
            f"{stats['percent_change']}%",
            f"[{severity_color}]{stats['severity']}[/{severity_color}]",
        )

    console.print(table)
    console.print()
