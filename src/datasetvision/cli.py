"""
DatasetVision CLI - Industry-Grade Dataset Governance Tool
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
from rich.align import Align
from rich.columns import Columns
from rich import box

from datasetvision.logging_config import configure_logging
from datasetvision.intelligence import (
    generate_intelligence_report,
    save_intelligence_json,
)
from datasetvision.html_report import generate_html_report
from datasetvision.policy import evaluate_policies

app = typer.Typer(help="DatasetVision - Industry Dataset Governance CLI.")

console = Console()
logger = logging.getLogger(__name__)


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    configure_logging(verbose)


def render_gradient_bar(value: int, max_value: int, width: int = 32) -> Text:
    if max_value == 0:
        return Text("")

    filled = int((value / max_value) * width)
    bar = Text()

    for i in range(width):
        if i < filled:
            bar.append("█", style="cyan")
        else:
            bar.append("░", style="grey50")

    return bar


def severity_meter(score: int) -> Panel:
    levels = {
        0: ("BALANCED", "green"),
        1: ("MILD", "yellow"),
        2: ("MODERATE", "orange1"),
        3: ("SEVERE", "red"),
    }

    label, color = levels.get(score, ("UNKNOWN", "white"))

    meter = Text()
    for i in range(4):
        if i <= score:
            meter.append("● ", style=color)
        else:
            meter.append("○ ", style="grey50")

    return Panel(
        Align.center(Text(label, style=f"bold {color}") + Text("\n") + meter),
        border_style=color,
        box=box.ROUNDED,
    )


@app.command()
def intelligence(
    dataset_folder: Path,
    json_output: bool = typer.Option(False, "--json"),
) -> None:

    if not dataset_folder.exists():
        console.print("[bold red]Dataset folder does not exist.[/bold red]")
        raise typer.Exit(code=1)

    console.print()
    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Industry Dataset Governance Framework[/dim]",
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
    ) as progress:
        progress.add_task("analysis", total=None)
        report = generate_intelligence_report(dataset_folder)

    # Governance Enforcement
    policy_result = evaluate_policies(report)

    json_path = dataset_folder / "intelligence_report.json"
    html_path = dataset_folder / "intelligence_report.html"

    save_intelligence_json(report, json_path)
    generate_html_report(report, html_path)

    if json_output:
        console.print_json(data=report)
        if not policy_result["policy_passed"]:
            raise typer.Exit(code=1)
        return

    class_info = report["class_analysis"]
    imbalance = class_info.get("imbalance", {})
    noise_info = report["label_noise"]

    console.print(Rule("[bold cyan] OVERVIEW [/bold cyan]"))

    overview = Columns(
        [
            Panel(
                Align.center(f"[bold]{class_info['num_classes']}[/bold]\n[dim]Classes[/dim]"),
                border_style="cyan",
                box=box.ROUNDED,
            ),
            Panel(
                Align.center(f"[bold]{noise_info['num_suspicious']}[/bold]\n[dim]Noise Flags[/dim]"),
                border_style="magenta",
                box=box.ROUNDED,
            ),
        ],
        expand=True,
    )

    console.print(overview)

    console.print(Rule("[bold cyan] IMBALANCE [/bold cyan]"))
    console.print(severity_meter(imbalance.get("severity_score", 0)))

    console.print(Rule("[bold cyan] GOVERNANCE STATUS [/bold cyan]"))

    if policy_result["policy_passed"]:
        console.print("[bold green]✓ All governance policies passed.[/bold green]")
    else:
        console.print("[bold red]✖ Governance violations detected:[/bold red]")
        for violation in policy_result["violations"]:
            console.print(f"[red]  - {violation}[/red]")

        raise typer.Exit(code=1)

    console.print(Rule("[bold cyan] OUTPUT [/bold cyan]"))
    console.print(f"[green]JSON →[/green] {json_path}")
    console.print(f"[green]HTML →[/green] {html_path}")
    console.print()

