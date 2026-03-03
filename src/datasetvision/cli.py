"""
DatasetVision CLI - Premium Research Dataset Governance Tool
"""

from pathlib import Path
import typer
import logging
import math

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

from datasetvision.logging_config import configure_logging
from datasetvision.intelligence import (
    generate_intelligence_report,
    save_intelligence_json,
)
from datasetvision.html_report import generate_html_report

app = typer.Typer(help="DatasetVision - Research-Grade Dataset Governance CLI.")

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


def render_bar(value: int, max_value: int, width: int = 30) -> str:
    """
    Render proportional bar for CLI visualization.
    """
    if max_value == 0:
        return ""

    filled = int((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


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

    console.print("\n")
    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Research-Grade Dataset Governance Framework[/dim]",
                border_style="cyan",
            )
        )
    )

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold]Analyzing dataset..."),
        console=console,
    ) as progress:
        progress.add_task("analysis", total=None)
        report = generate_intelligence_report(dataset_folder)

    json_path = dataset_folder / "intelligence_report.json"
    html_path = dataset_folder / "intelligence_report.html"

    save_intelligence_json(report, json_path)
    generate_html_report(report, html_path)

    if json_output:
        console.print_json(data=report)
        return

    class_info = report["class_analysis"]
    imbalance = class_info.get("imbalance", {})
    noise_info = report["label_noise"]
    similarity = report["similarity_matrix"]

    console.print(Rule("[bold cyan]DATASET OVERVIEW[/bold cyan]"))

    console.print(
        Columns(
            [
                Panel(
                    f"[bold]{class_info['num_classes']}[/bold]\n[dim]Classes[/dim]",
                    border_style="cyan",
                ),
                Panel(
                    f"[bold]{noise_info['num_suspicious']}[/bold]\n[dim]Suspicious Labels[/dim]",
                    border_style="magenta",
                ),
            ]
        )
    )

    console.print(Rule("[bold cyan]CLASS DISTRIBUTION[/bold cyan]"))

    table = Table(show_header=False)
    max_count = max(stats["count"] for stats in class_info["classes"].values())

    for cls, stats in class_info["classes"].items():
        bar = render_bar(stats["count"], max_count)
        table.add_row(
            f"[cyan]{cls}[/cyan]",
            bar,
            f"[bold]{stats['count']}[/bold]",
        )

    console.print(table)

    console.print(Rule("[bold cyan]IMBALANCE ANALYSIS[/bold cyan]"))

    severity = imbalance.get("severity_score", 0)
    ratio = imbalance.get("imbalance_ratio", 1.0)

    severity_labels = {
        0: ("BALANCED", "green"),
        1: ("MILD IMBALANCE", "yellow"),
        2: ("MODERATE IMBALANCE", "orange1"),
        3: ("SEVERE IMBALANCE", "red"),
    }

    label, color = severity_labels.get(severity, ("UNKNOWN", "white"))

    console.print(
        Panel(
            f"[bold {color}]{label}[/bold {color}]\n"
            f"[dim]Imbalance Ratio:[/dim] {round(ratio, 2)}",
            border_style=color,
        )
    )

    console.print(Rule("[bold cyan]LABEL NOISE[/bold cyan]"))

    if noise_info["num_suspicious"] == 0:
        console.print("[bold green]✓ No suspicious label noise detected.[/bold green]")
    else:
        console.print(
            f"[bold red]⚠ {noise_info['num_suspicious']} potentially mislabeled images detected.[/bold red]"
        )

    console.print(Rule("[bold cyan]CROSS-CLASS SIMILARITY[/bold cyan]"))

    sim_table = Table(show_header=True, header_style="bold magenta")
    classes = list(similarity.keys())
    sim_table.add_column("Class")

    for cls in classes:
        sim_table.add_column(cls)

    for cls_a in classes:
        row = [cls_a]
        for cls_b in classes:
            val = similarity[cls_a][cls_b]
            row.append(str(round(val, 2)) if val is not None else "-")
        sim_table.add_row(*row)

    console.print(sim_table)

    console.print(Rule("[bold cyan]REPORT OUTPUT[/bold cyan]"))
    console.print(f"[green]JSON:[/green] {json_path}")
    console.print(f"[green]HTML:[/green] {html_path}")
    console.print("\n")
