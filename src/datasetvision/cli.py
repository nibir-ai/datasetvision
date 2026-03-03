"""
DatasetVision CLI - Premium Dataset Governance Interface
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

app = typer.Typer(help="DatasetVision - Research-Grade Dataset Governance CLI.")

console = Console()
logger = logging.getLogger(__name__)


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    configure_logging(verbose)


def render_gradient_bar(value: int, max_value: int, width: int = 32) -> Text:
    """
    Render smooth gradient-style proportional bar.
    """
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
    """
    Visual severity meter.
    """
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
                "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Dataset Governance Intelligence[/dim]",
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

    console.print(Rule("[bold cyan] CLASS DISTRIBUTION [/bold cyan]"))

    max_count = max(stats["count"] for stats in class_info["classes"].values())
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Class", style="cyan")
    table.add_column("Distribution")
    table.add_column("Count", justify="right")

    for cls, stats in class_info["classes"].items():
        table.add_row(
            cls,
            render_gradient_bar(stats["count"], max_count),
            f"[bold]{stats['count']}[/bold]",
        )

    console.print(table)

    console.print(Rule("[bold cyan] IMBALANCE [/bold cyan]"))
    console.print(severity_meter(imbalance.get("severity_score", 0)))

    console.print(Rule("[bold cyan] LABEL NOISE [/bold cyan]"))

    if noise_info["num_suspicious"] == 0:
        console.print("[bold green]✓ Dataset appears clean.[/bold green]")
    else:
        console.print(
            f"[bold red]⚠ {noise_info['num_suspicious']} potential mislabels detected.[/bold red]"
        )

    console.print(Rule("[bold cyan] SIMILARITY MATRIX [/bold cyan]"))

    sim_table = Table(box=box.MINIMAL_DOUBLE_HEAD)
    classes = list(similarity.keys())
    sim_table.add_column("")

    for cls in classes:
        sim_table.add_column(cls, justify="center")

    for cls_a in classes:
        row = [f"[cyan]{cls_a}[/cyan]"]
        for cls_b in classes:
            val = similarity[cls_a][cls_b]
            if val is None:
                row.append("-")
            else:
                if val < 10:
                    style = "green"
                elif val < 20:
                    style = "yellow"
                else:
                    style = "red"
                row.append(f"[{style}]{round(val,1)}[/{style}]")
        sim_table.add_row(*row)

    console.print(sim_table)

    console.print(Rule("[bold cyan] OUTPUT [/bold cyan]"))
    console.print(f"[green]JSON →[/green] {json_path}")
    console.print(f"[green]HTML →[/green] {html_path}")
    console.print()
