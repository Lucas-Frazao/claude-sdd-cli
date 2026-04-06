"""sdd specify — Turn an idea into a structured specification."""

import re
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from human_sdd_cli.ai import AIOrchestrator
from human_sdd_cli.templates import load_template, populate_template
from human_sdd_cli.validators import validate_no_code

console = Console()


def _slugify(text: str) -> str:
    """Convert text to a URL/folder-friendly slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")[:60]


def _next_feature_number(specs_dir: Path) -> int:
    """Determine the next feature number from existing spec folders."""
    existing = [
        d.name for d in specs_dir.iterdir()
        if d.is_dir() and re.match(r"^\d{3}-", d.name)
    ] if specs_dir.exists() else []
    if not existing:
        return 1
    numbers = [int(d.split("-")[0]) for d in existing]
    return max(numbers) + 1


@click.command()
@click.option("--idea", "-i", prompt="Describe your feature idea", help="Feature idea or description.")
@click.option("--name", "-n", default=None, help="Feature name (auto-generated from idea if omitted).")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default=None, help="LLM model (default: gpt-4o-mini for OpenAI, gpt-4o for Copilot).")
@click.option("--provider", "-P", default="auto", type=click.Choice(["auto", "openai", "copilot"]),
              help="AI provider (auto-detected if omitted).")
@click.option("--no-ai", is_flag=True, help="Skip AI generation, create blank template only.")
def specify_cmd(idea: str, name: str, path: str, model: str, provider: str, no_ai: bool):
    """Generate a structured specification from a feature idea."""
    root = Path(path).resolve()
    specs_dir = root / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Determine feature naming
    feature_num = _next_feature_number(specs_dir)
    feature_slug = _slugify(name or idea)
    feature_name = f"{feature_num:03d}-{feature_slug}"
    feature_dir = specs_dir / feature_name
    feature_dir.mkdir(parents=True, exist_ok=True)

    console.print(Panel(
        f"[bold cyan]Specifying feature:[/] {feature_name}\n"
        f"[dim]Idea: {idea}[/]",
        title="sdd specify",
    ))

    if no_ai:
        # Just create the blank template
        try:
            template = load_template("spec-template")
        except FileNotFoundError:
            template = _default_spec_template()
        content = populate_template(template, {
            "feature_title": name or idea,
            "feature_number": feature_name,
            "idea_description": idea,
        })
    else:
        # Use AI to generate the specification
        console.print("[dim]Generating specification with AI...[/]")
        ai = AIOrchestrator(
            provider=provider,
            model=model,
            audit_dir=feature_dir,
        )

        prompt = f"""Create a structured software specification for the following feature idea.

FEATURE IDEA: {idea}

Use the following structure EXACTLY (as Markdown headings). Write in prose, tables, and checklists only.
Do NOT include any code, code fences, or executable snippets.

# Specification: {name or idea}

## Feature Number
{feature_name}

## Problem Statement
(Describe the problem this feature solves)

## User Stories
(List user stories in "As a ... I want ... so that ..." format)

## Functional Requirements
(List as: - REQ-001: Description)

## Non-Functional Requirements
(List as: - REQ-NF-001: Description)

## Success Criteria
(Measurable criteria for when this feature is complete)

## Edge Cases
(Known edge cases and how they should be handled in prose)

## Open Questions
(Mark anything unclear with [NEEDS CLARIFICATION])

## Out of Scope
(What this feature explicitly does NOT cover)

## Dependencies
(Other features, systems, or decisions this depends on)
"""

        try:
            content = ai.generate(prompt, feature=feature_name)
        except ValueError as e:
            console.print(f"[bold red]Constitution violation:[/] {e}")
            return

    # Write the spec
    spec_path = feature_dir / "spec.md"
    spec_path.write_text(content)
    console.print(f"  [green]✓[/] Created {spec_path.relative_to(root)}")

    # Summary
    console.print()
    console.print("[bold green]Specification created.[/] Next steps:")
    console.print(f"  1. Review and refine: {spec_path.relative_to(root)}")
    console.print("  2. Answer any [NEEDS CLARIFICATION] items")
    console.print(f"  3. Run [bold]sdd plan --feature {feature_name}[/]")


def _default_spec_template() -> str:
    return """# Specification: {{feature_title}}

## Feature Number
{{feature_number}}

## Problem Statement
{{idea_description}}

[NEEDS CLARIFICATION] — Expand this into a detailed problem statement.

## User Stories
- As a [user type], I want [goal] so that [reason]. [NEEDS CLARIFICATION]

## Functional Requirements
- REQ-001: [NEEDS CLARIFICATION]

## Non-Functional Requirements
- REQ-NF-001: [NEEDS CLARIFICATION]

## Success Criteria
- [ ] [NEEDS CLARIFICATION]

## Edge Cases
[NEEDS CLARIFICATION]

## Open Questions
- [NEEDS CLARIFICATION] — What are the primary user personas?
- [NEEDS CLARIFICATION] — What are the performance constraints?

## Out of Scope
[NEEDS CLARIFICATION]

## Dependencies
[NEEDS CLARIFICATION]
"""
