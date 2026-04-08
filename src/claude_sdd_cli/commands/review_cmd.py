"""sdd review — Review implementation against the specification."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.ai import AIOrchestrator
from claude_sdd_cli.review import build_review_prompt

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
@click.option("--notes", "-n", default="", help="Implementation notes from the developer.")
@click.option("--notes-file", type=click.Path(exists=True), help="File containing implementation notes.")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default="gpt-4o-mini", help="LLM model to use.")
def review_cmd(feature: str, notes: str, notes_file: str, path: str, model: str):
    """Review Claude CLI implementation against the spec and plan."""
    root = Path(path).resolve()
    feature_dir = _find_feature_dir(root, feature)

    console.print(Panel(
        f"[bold cyan]Reviewing feature:[/] {feature_dir.name}",
        title="sdd review",
    ))

    # Gather implementation notes
    impl_notes = notes
    if notes_file:
        impl_notes = Path(notes_file).read_text()
    if not impl_notes:
        impl_notes = click.prompt(
            "Describe what you implemented (or press Enter to skip)",
            default="",
        )

    # Build the review prompt
    prompt = build_review_prompt(feature_dir, impl_notes)

    console.print("[dim]Running spec compliance review...[/]")
    ai = AIOrchestrator(model=model, audit_dir=feature_dir)

    try:
        review_content = ai.generate(
            prompt,
            feature=feature_dir.name,
            extra_system=(
                "You are a strict design reviewer. "
                "Identify gaps between the spec and what was implemented. "
                "Produce follow-up tasks as checklists. "
                "NEVER suggest code, patches, or fixes. "
                "Only describe WHAT is missing, not HOW to fix it in code."
            ),
        )
    except ValueError as e:
        console.print(f"[bold red]Constitution violation:[/] {e}")
        return

    review_path = feature_dir / "review.md"
    review_path.write_text(review_content)
    console.print(f"  [green]✓[/] Created {review_path.relative_to(root)}")

    # Also print a summary to the console
    console.print()
    console.print(Panel(review_content[:2000], title="Review Summary", expand=False))

    console.print()
    console.print("[bold green]Review complete.[/] Check the full report:")
    console.print(f"  {review_path.relative_to(root)}")
