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
from datasetvision.scanner import scan_dataset, save_scan_report
from datasetvision.duplicates import find_exact_duplicates, find_near_duplicates
from datasetvision.policy import evaluate_policies
from datasetvision.html_report import generate_html_report

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    configure_logging(verbose)


# ------------------------------------------------------------
# INTELLIGENCE
# ------------------------------------------------------------

@app.command()
def intelligence(dataset_folder: Path):

    if not dataset_folder.exists():
        console.print("[red]Dataset folder does not exist.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASETVISION[/bold cyan]\n[dim]Anomaly-Aware Intelligence[/dim]",
                border_style="cyan",
                box=box.ROUNDED,
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
        return

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
    
    console.print(Rule("[bold cyan] GOVERNANCE POLICIES [/bold cyan]"))
    policy_results = evaluate_policies(report)
    
    if policy_results["policy_passed"]:
        console.print("[bold green]All governance policies passed![/bold green]")
    else:
        console.print("[bold red]Policy Violations:[/bold red]")
        for violation in policy_results["violations"]:
            console.print(f"- [red]{violation}[/red]")
    console.print()


# ------------------------------------------------------------
# DRIFT
# ------------------------------------------------------------

@app.command()
def drift(dataset_a: Path, dataset_b: Path):

    if not dataset_a.exists() or not dataset_b.exists():
        console.print("[red]Dataset paths invalid.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Align.center(
            Panel(
                "[bold cyan]DATASET DRIFT ANALYSIS[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
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
    centroid_drift = drift_report["centroid_drift"]

    # ------------------------------------------------------------
    # GLOBAL DRIFT
    # ------------------------------------------------------------

    console.print(Rule("[bold cyan] GLOBAL DRIFT [/bold cyan]"))
    console.print(
        f"[bold]{global_drift['severity']}[/bold] (score={global_drift['score']})"
    )

    # ------------------------------------------------------------
    # SEMANTIC DRIFT (NEW)
    # ------------------------------------------------------------

    console.print(Rule("[bold cyan] SEMANTIC DRIFT [/bold cyan]"))

    if not centroid_drift:
        console.print("[green]No centroid drift detected.[/green]")
    else:

        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("Class", style="cyan")
        table.add_column("Centroid Distance")
        table.add_column("Severity")

        for cls, stats in centroid_drift.items():

            severity_color = {
                "STABLE": "green",
                "MINOR_SHIFT": "yellow",
                "MODERATE_SHIFT": "orange1",
                "MAJOR_SHIFT": "red",
            }.get(stats["severity"], "white")

            table.add_row(
                cls,
                str(stats["centroid_distance"]),
                f"[{severity_color}]{stats['severity']}[/{severity_color}]",
            )

        console.print(table)

    # ------------------------------------------------------------
    # ANOMALY DRIFT
    # ------------------------------------------------------------

    console.print(Rule("[bold cyan] ANOMALY DRIFT [/bold cyan]"))

    if not anomaly_drift:
        console.print("[green]No anomaly changes detected.[/green]")
        return

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

# ------------------------------------------------------------
# SCANNER
# ------------------------------------------------------------

@app.command()
def scan(dataset_folder: Path, output: Path = typer.Option(None, "--output", "-o")):
    if not dataset_folder.exists():
        console.print("[red]Dataset folder does not exist.[/red]")
        raise typer.Exit(code=1)
    
    console.print(Rule("[bold cyan] DATASET SCAN [/bold cyan]"))
    
    with Progress(SpinnerColumn(), TextColumn("[bold]Scanning dataset..."), console=console) as progress:
        results = scan_dataset(dataset_folder)
    
    console.print(f"Total Images: {results['total_images']}")
    console.print(f"Corrupted: {len(results['corrupted'])}")
    console.print(f"Blank: {len(results['blank'])}")
    console.print(f"Extreme Aspect Ratio: {len(results['extreme_aspect_ratio'])}")
    
    if output:
        save_scan_report(results, output)
        console.print(f"[green]Scan report saved to {output}[/green]")


# ------------------------------------------------------------
# DUPLICATES
# ------------------------------------------------------------

@app.command()
def duplicates(dataset_folder: Path, exact: bool = typer.Option(True, "--exact/--near", help="Find exact or near duplicates")):
    if not dataset_folder.exists():
        console.print("[red]Dataset folder does not exist.[/red]")
        raise typer.Exit(code=1)
    
    console.print(Rule(f"[bold cyan] {'EXACT' if exact else 'NEAR'} DUPLICATES [/bold cyan]"))
    
    with Progress(SpinnerColumn(), TextColumn("[bold]Finding duplicates..."), console=console) as progress:
        if exact:
            results = find_exact_duplicates(dataset_folder)
        else:
            results = find_near_duplicates(dataset_folder)
    
    if not results:
        console.print("[green]No duplicates found![/green]")
        return
        
    for k, v in results.items():
        console.print(f"[bold yellow]Group[/bold yellow] (size {len(v)}):\n  " + "\n  ".join(map(str, v)))
    console.print()


# ------------------------------------------------------------
# HTML REPORT
# ------------------------------------------------------------

@app.command()
def report(dataset_folder: Path, output: Path):
    if not dataset_folder.exists():
        console.print("[red]Dataset folder does not exist.[/red]")
        raise typer.Exit(code=1)
        
    console.print(
        Align.center(
            Panel(
                "[bold cyan]HTML REPORT GENERATION[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )
    )
        
    with Progress(SpinnerColumn(), TextColumn("[bold]Generating HTML report..."), console=console) as progress:
        report_data = generate_intelligence_report(dataset_folder)
        generate_html_report(report_data, output)
        
    console.print(f"[green]HTML report successfully generated at {output}[/green]")

