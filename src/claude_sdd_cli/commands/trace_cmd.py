"""sdd trace — Create traceability reports."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.tracing import build_trace_report

console = Console()


def _find_feature_dir(root: Path, feature: str) -> Path:
    specs_dir = root / "specs"
    exact = specs_dir / feature
    if exact.is_dir():
        return exact
    for d in sorted(specs_dir.iterdir()):
        if d.is_dir() and feature in d.name:
            return d
    raise click.ClickException(f"Feature not found: {feature}")


@click.command()
@click.option("--feature", "-f", required=True, help="Feature name or number.")
@click.option("--path", "-p", default=".", help="Project root directory.")
def trace_cmd(feature: str, path: str):
    """Generate a traceability report mapping requirements to tasks."""
    root = Path(path).resolve()
    feature_dir = _find_feature_dir(root, feature)

    console.print(Panel(
        f"[bold cyan]Tracing feature:[/] {feature_dir.name}",
        title="sdd trace",
    ))

    report = build_trace_report(feature_dir, feature_dir.name)
    markdown = report.to_markdown()

    trace_path = feature_dir / "traceability.md"
    trace_path.write_text(markdown)
    console.print(f"  [green]✓[/] Created {trace_path.relative_to(root)}")

    # Print summary
    console.print()
    console.print(f"[bold]Coverage:[/] {report.coverage:.0f}%")

    if report.coverage < 100:
        unimpl = [e for e in report.entries if e.status == "unimplemented"]
        if unimpl:
            console.print(f"[yellow]Unimplemented requirements: {len(unimpl)}[/]")
            for entry in unimpl[:10]:
                console.print(f"  - {entry.requirement_id}: {entry.requirement_text[:80]}")
    else:
        console.print("[bold green]All requirements have linked tasks.[/]")
