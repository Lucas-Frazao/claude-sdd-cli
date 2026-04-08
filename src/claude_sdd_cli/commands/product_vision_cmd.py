"""sdd vision — Define the product vision for the project."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.ai import AIOrchestrator

console = Console()


@click.command()
@click.option("--description", "-d", prompt="Describe your product", help="Product description or idea.")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default="gpt-4o-mini", help="LLM model to use.")
@click.option("--no-ai", is_flag=True, help="Skip AI generation, create blank template only.")
def product_vision_cmd(description: str, path: str, model: str, no_ai: bool):
    """Define the product vision — what it is, who it's for, and why it matters."""
    root = Path(path).resolve()
    csdd_dir = root / ".csdd"

    if not csdd_dir.is_dir():
        raise click.ClickException("No .csdd/ directory found. Run 'csdd init' first.")

    memory_dir = csdd_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    vision_path = memory_dir / "product-vision.md"

    console.print(Panel(
        f"[bold cyan]Defining product vision[/]\n"
        f"[dim]{description[:120]}[/]",
        title="sdd vision",
    ))

    if no_ai:
        content = _default_vision_template(description)
    else:
        console.print("[dim]Generating product vision with AI...[/]")
        ai = AIOrchestrator(
            model=model,
            audit_dir=memory_dir,
        )

        # Load constitution for context
        constitution = ""
        constitution_path = memory_dir / "constitution.md"
        if constitution_path.exists():
            constitution = constitution_path.read_text()

        prompt = f"""Based on the following product description, create a comprehensive product vision document.

PRODUCT DESCRIPTION: {description}

{"CONSTITUTION:" + chr(10) + constitution if constitution else ""}

Write the vision using these EXACT Markdown headings. Write in prose, tables, and checklists only.
Do NOT include any code, code fences, or executable snippets.

# Product Vision

## Product Name
(A clear, descriptive name for the product)

## Problem Statement
(What problem does this product solve? Who experiences this problem? Why is it important?)

## Target Users
(Who are the primary users? Describe personas or user segments.)

## Value Proposition
(What value does this product deliver? Why would someone use it over alternatives?)

## Product Description
(What is this product at a high level? What does it do?)

## Guiding Principles
(3-5 non-negotiable principles that guide all product decisions)

## Success Metrics
(How will you measure whether the product is successful? Use measurable outcomes.)

## Scope Boundaries
(What is explicitly out of scope for this product?)

## Open Questions
(Mark anything unclear with [NEEDS CLARIFICATION])
"""

        try:
            content = ai.generate(prompt, feature="product-vision")
        except ValueError as e:
            console.print(f"[bold red]Constitution violation:[/] {e}")
            return

    # Write the vision
    vision_path.write_text(content)
    console.print(f"  [green]✓[/] Created {vision_path.relative_to(root)}")

    # Summary
    console.print()
    console.print("[bold green]Product vision created.[/] Next steps:")
    console.print(f"  1. Review and refine: {vision_path.relative_to(root)}")
    console.print("  2. Answer any [NEEDS CLARIFICATION] items")
    console.print("  3. Run [bold]sdd roadmap --description '...'[/] to define your feature roadmap")


def _default_vision_template(description: str) -> str:
    return f"""# Product Vision

## Product Name
[NEEDS CLARIFICATION] — Provide a product name.

## Problem Statement
{description}

[NEEDS CLARIFICATION] — Expand this into a detailed problem statement.

## Target Users
- [NEEDS CLARIFICATION] — Define primary user personas.

## Value Proposition
[NEEDS CLARIFICATION] — What unique value does this product deliver?

## Product Description
{description}

[NEEDS CLARIFICATION] — Expand into a comprehensive product description.

## Guiding Principles
1. [NEEDS CLARIFICATION] — Define guiding principles.

## Success Metrics
- [NEEDS CLARIFICATION] — Define measurable success criteria.

## Scope Boundaries
- [NEEDS CLARIFICATION] — Define what is out of scope.

## Open Questions
- [NEEDS CLARIFICATION] — What are the key open questions?
"""
