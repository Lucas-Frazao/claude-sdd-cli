"""sdd clarify — Run ambiguity analysis on existing docs."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from claude_sdd_cli.ai import AIOrchestrator
from claude_sdd_cli.parsers import find_open_questions

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
@click.option("--model", "-m", default="gpt-4o-mini", help="LLM model to use.")
@click.option("--no-ai", is_flag=True, help="Only scan for existing markers, skip AI analysis.")
def clarify_cmd(feature: str, path: str, model: str, no_ai: bool):
    """Analyze specs and plans for ambiguity, vagueness, and contradictions."""
    root = Path(path).resolve()
    feature_dir = _find_feature_dir(root, feature)

    console.print(Panel(
        f"[bold cyan]Clarifying feature:[/] {feature_dir.name}",
        title="sdd clarify",
    ))

    # Scan all markdown files for [NEEDS CLARIFICATION]
    all_markers: list[tuple[str, int, str]] = []
    for md_file in sorted(feature_dir.rglob("*.md")):
        rel = md_file.relative_to(feature_dir)
        markers = find_open_questions(md_file.read_text())
        for line_no, line in markers:
            all_markers.append((str(rel), line_no, line))

    if all_markers:
        table = Table(title="Existing [NEEDS CLARIFICATION] Markers")
        table.add_column("File", style="cyan")
        table.add_column("Line", style="yellow", justify="right")
        table.add_column("Content", style="white")
        for file, line_no, content in all_markers:
            table.add_row(file, str(line_no), content[:100])
        console.print(table)
    else:
        console.print("[green]No existing [NEEDS CLARIFICATION] markers found.[/]")

    if no_ai:
        return

    # AI-powered deeper ambiguity analysis
    artifacts_text = ""
    for md_file in sorted(feature_dir.rglob("*.md")):
        rel = md_file.relative_to(feature_dir)
        content = md_file.read_text()
        artifacts_text += f"\n## FILE: {rel}\n\n{content}\n"

    if not artifacts_text.strip():
        console.print("[yellow]No artifacts to analyze.[/]")
        return

    console.print()
    console.print("[dim]Running AI ambiguity analysis...[/]")
    ai = AIOrchestrator(model=model, audit_dir=feature_dir)

    prompt = f"""Analyze the following project artifacts for ambiguity, vagueness,
contradictions, and underspecified requirements.

ARTIFACTS:
{artifacts_text}

Produce your analysis using these headings. Use ONLY prose, tables, and checklists.
Do NOT include any code.

# Ambiguity Analysis: {feature_dir.name}

## Vague Requirements
(Requirements that are too broad, unmeasurable, or hand-wavy)

## Contradictions
(Places where one artifact says X and another says Y)

## Missing Details
(Important aspects that are not covered at all)

## Assumptions That Need Confirmation
(Things the spec seems to assume but never states explicitly)

## Suggested Clarifying Questions
(Specific questions the developer should answer before proceeding)
"""

    try:
        analysis = ai.generate(prompt, feature=feature_dir.name)
    except ValueError as e:
        console.print(f"[bold red]Constitution violation:[/] {e}")
        return

    # Save the analysis
    clarify_path = feature_dir / "clarification-analysis.md"
    clarify_path.write_text(analysis)
    console.print(f"  [green]✓[/] Created {clarify_path.relative_to(root)}")

    console.print()
    console.print(Panel(analysis[:2000], title="Clarification Analysis", expand=False))
