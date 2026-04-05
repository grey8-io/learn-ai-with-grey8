"""Click CLI entry point for the ACE framework."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


@click.group()
@click.version_option(package_name="learn-ai-ace")
def cli() -> None:
    """ACE — Autonomous Curriculum Engine.

    Automates content creation, quality control, and curriculum improvement
    using local LLMs via Ollama.
    """


@cli.command()
@click.option(
    "--spec",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to a YAML spec file describing what to generate.",
)
def generate(spec: Path) -> None:
    """Generate curriculum content from a YAML spec."""
    from ace.generator.generate import generate_from_spec

    console.print(
        Panel(f"[bold green]Generating content from[/] {spec}", title="ACE Generate")
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating content...", total=None)
        summary = generate_from_spec(spec)
        progress.update(task, completed=True)

    table = Table(title="Generation Summary")
    table.add_column("Item", style="cyan")
    table.add_column("Count", justify="right", style="green")

    for key, value in summary.items():
        table.add_row(key, str(value))

    console.print(table)
    console.print("[bold green]Done![/]")


@cli.command()
@click.option(
    "--path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to a curriculum directory to curate.",
)
def curate(path: Path) -> None:
    """Run quality checks on a curriculum path."""
    from ace.curator.curate import curate_path

    console.print(
        Panel(f"[bold blue]Curating content at[/] {path}", title="ACE Curate")
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running quality checks...", total=None)
        report = curate_path(path)
        progress.update(task, completed=True)

    # Display issues table
    if report.issues:
        table = Table(title="Issues Found")
        table.add_column("Severity", style="bold")
        table.add_column("Location")
        table.add_column("Message")

        for issue in report.issues:
            severity_style = {
                "error": "red",
                "warning": "yellow",
                "info": "blue",
            }.get(issue.severity, "white")
            table.add_row(
                f"[{severity_style}]{issue.severity.upper()}[/]",
                issue.location,
                issue.message,
            )

        console.print(table)
    else:
        console.print("[bold green]No issues found![/]")

    # Display suggestions
    if report.suggestions:
        console.print(Panel("\n".join(f"- {s}" for s in report.suggestions), title="Suggestions"))

    console.print(f"\n[bold]Score:[/] {report.score}/100")


@cli.command()
@click.option(
    "--check",
    is_flag=True,
    default=False,
    help="Dry-run mode: report drift without fixing. Exits with code 1 if out of sync.",
)
@click.option(
    "--repo-root",
    type=click.Path(exists=True, path_type=Path),
    default=Path("."),
    help="Repository root directory (default: current directory).",
)
def sync(check: bool, repo_root: Path) -> None:
    """Sync manifest, README, and docs with the curriculum on disk."""
    from ace.sync import sync_all

    mode = "check" if check else "sync"
    console.print(
        Panel(f"[bold cyan]Running curriculum {mode}[/] at {repo_root}", title="ACE Sync")
    )

    report = sync_all(repo_root, dry_run=check)

    # Display results
    if report.files_added:
        table = Table(title="Lessons Added to Manifest")
        table.add_column("Lesson ID", style="green")
        for f in report.files_added:
            table.add_row(f)
        console.print(table)

    if report.files_removed:
        table = Table(title="Lessons Removed from Manifest")
        table.add_column("Lesson ID", style="red")
        for f in report.files_removed:
            table.add_row(f)
        console.print(table)

    if report.issues:
        table = Table(title="Integrity Issues")
        table.add_column("Issue", style="yellow")
        for issue in report.issues:
            table.add_row(issue)
        console.print(table)

    if report.manifest_updated:
        console.print("[cyan]manifest.json[/] was updated" if not check else "[cyan]manifest.json[/] is out of sync")
    if report.readme_updated:
        console.print("[cyan]README.md[/] table was updated" if not check else "[cyan]README.md[/] table is out of sync")
    if report.getting_started_updated:
        console.print("[cyan]GETTING_STARTED.md[/] was updated" if not check else "[cyan]GETTING_STARTED.md[/] is out of sync")

    if not report.has_drift:
        console.print("[bold green]Everything is in sync![/]")
    elif check:
        console.print("[bold red]Drift detected. Run `ace sync` to fix.[/]")
        raise SystemExit(1)
    else:
        console.print("[bold green]Sync complete![/]")


@cli.command()
@click.option(
    "--output",
    required=True,
    type=click.Path(path_type=Path),
    help="Path where the analytics report will be written.",
)
def reflect(output: Path) -> None:
    """Generate an analytics report on the curriculum."""
    from ace.reflector.reflect import generate_report

    console.print(
        Panel(f"[bold magenta]Generating report to[/] {output}", title="ACE Reflect")
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing curriculum...", total=None)
        generate_report(output)
        progress.update(task, completed=True)

    console.print(f"[bold green]Report written to[/] {output}")
