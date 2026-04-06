"""sdd plan — Convert an approved spec into a technical planning package."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from human_sdd_cli.ai import AIOrchestrator
from human_sdd_cli.parsers import load_feature_artifact, find_open_questions

console = Console()


def _find_feature_dir(root: Path, feature: str) -> Path:
    """Resolve a feature directory from a name or partial match."""
    specs_dir = root / "specs"
    # Exact match
    exact = specs_dir / feature
    if exact.is_dir():
        return exact
    # Partial match
    for d in sorted(specs_dir.iterdir()):
        if d.is_dir() and feature in d.name:
            return d
    raise click.ClickException(f"Feature not found: {feature}")


@click.command()
@click.option("--feature", "-f", required=True, help="Feature name or number (e.g. 001-user-auth).")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default=None, help="LLM model (default: gpt-4o-mini for OpenAI, gpt-4o for Copilot).")
@click.option("--provider", "-P", default="auto", type=click.Choice(["auto", "openai", "copilot"]),
              help="AI provider (auto-detected if omitted).")
@click.option("--no-ai", is_flag=True, help="Skip AI generation, create blank templates only.")
def plan_cmd(feature: str, path: str, model: str, provider: str, no_ai: bool):
    """Generate a technical planning package from an approved specification."""
    root = Path(path).resolve()
    feature_dir = _find_feature_dir(root, feature)

    console.print(Panel(
        f"[bold cyan]Planning feature:[/] {feature_dir.name}",
        title="sdd plan",
    ))

    # Load the spec
    try:
        spec_content = load_feature_artifact(feature_dir, "spec")
    except FileNotFoundError:
        raise click.ClickException(f"No spec.md found in {feature_dir}")

    # Warn about open questions
    open_qs = find_open_questions(spec_content)
    if open_qs:
        console.print(f"[yellow]⚠ Found {len(open_qs)} open question(s) in spec:[/]")
        for line_no, line in open_qs[:5]:
            console.print(f"  Line {line_no}: {line[:100]}")
        if not click.confirm("Continue planning with unresolved questions?", default=True):
            return

    if no_ai:
        _create_blank_plan_artifacts(feature_dir)
    else:
        _create_ai_plan_artifacts(feature_dir, spec_content, model, provider)

    console.print()
    console.print("[bold green]Planning package created.[/] Next steps:")
    console.print(f"  1. Review all artifacts in {feature_dir.name}/")
    console.print(f"  2. Run [bold]sdd tasks --feature {feature_dir.name}[/]")


def _create_blank_plan_artifacts(feature_dir: Path):
    """Create blank planning templates."""
    artifacts = {
        "plan.md": "# Technical Plan\n\n[NEEDS CLARIFICATION] — Fill in after reviewing spec.\n",
        "research.md": "# Research Notes\n\n## Trade-offs\n\n## Alternatives Considered\n\n## References\n",
        "data-model.md": "# Data Model\n\n## Entities\n\n## Relationships\n\n## Constraints\n",
        "quickstart.md": "# Quickstart / Validation Scenarios\n\n## Happy Path\n\n## Error Cases\n",
    }
    contracts_dir = feature_dir / "contracts"
    contracts_dir.mkdir(exist_ok=True)

    for filename, content in artifacts.items():
        path = feature_dir / filename
        path.write_text(content)
        console.print(f"  [green]✓[/] Created {filename}")

    (contracts_dir / "README.md").write_text(
        "# Contracts\n\nPlace prose-based interface contracts here.\n"
    )
    console.print("  [green]✓[/] Created contracts/")


def _create_ai_plan_artifacts(feature_dir: Path, spec_content: str, model: str, provider: str):
    """Generate planning artifacts using AI."""
    ai = AIOrchestrator(provider=provider, model=model, audit_dir=feature_dir)

    # ── plan.md ──
    console.print("[dim]Generating plan.md...[/]")
    plan_prompt = f"""Based on the following specification, create a technical planning document.

SPECIFICATION:
{spec_content}

Write the plan using these EXACT Markdown headings. Use ONLY prose, tables, and checklists.
Do NOT include any code, code fences, or executable content.

# Technical Plan

## Summary
(Brief technical summary of what needs to be built)

## Constraints
(Technical and business constraints)

## Architecture Options
(Describe 2-3 architectural approaches in prose with trade-offs)

## Chosen Direction
(Which approach and why)

## Data Model
(Describe entities, attributes, and relationships in prose/tables — NO schema code)

## External Interfaces
(APIs, services, or systems this will interact with — described in prose)

## Risks
(Technical risks and mitigation strategies)

## Validation Approach
(How the developer will verify the implementation works)

## Human Implementation Guidance
(High-level guidance for the developer — what to build first, key decisions to make)
"""
    try:
        plan_content = ai.generate(plan_prompt, feature=feature_dir.name)
        (feature_dir / "plan.md").write_text(plan_content)
        console.print("  [green]✓[/] Created plan.md")
    except ValueError as e:
        console.print(f"  [red]✗[/] plan.md rejected: {e}")

    # ── research.md ──
    console.print("[dim]Generating research.md...[/]")
    research_prompt = f"""Based on this specification, produce a research document covering
trade-offs, alternative approaches, relevant prior art, and context a developer
should know before implementing.

SPECIFICATION:
{spec_content}

Use these headings. Prose and tables only. NO code.

# Research Notes

## Context and Background

## Trade-offs

## Alternatives Considered

## Relevant Prior Art

## Key Decisions to Research Further
"""
    try:
        research_content = ai.generate(research_prompt, feature=feature_dir.name)
        (feature_dir / "research.md").write_text(research_content)
        console.print("  [green]✓[/] Created research.md")
    except ValueError as e:
        console.print(f"  [red]✗[/] research.md rejected: {e}")

    # ── data-model.md ──
    console.print("[dim]Generating data-model.md...[/]")
    dm_prompt = f"""Based on this specification, describe the data model in prose and tables.

SPECIFICATION:
{spec_content}

# Data Model

## Entities
(List each entity with its attributes described in a table — columns: Attribute, Type, Description, Constraints)

## Relationships
(Describe how entities relate to each other in prose)

## Constraints and Invariants
(Business rules that the data model must enforce, described in prose)

Do NOT include any SQL, ORM code, migration code, or schema definitions.
"""
    try:
        dm_content = ai.generate(dm_prompt, feature=feature_dir.name)
        (feature_dir / "data-model.md").write_text(dm_content)
        console.print("  [green]✓[/] Created data-model.md")
    except ValueError as e:
        console.print(f"  [red]✗[/] data-model.md rejected: {e}")

    # ── quickstart.md ──
    console.print("[dim]Generating quickstart.md...[/]")
    qs_prompt = f"""Based on this specification, produce validation scenarios the developer
can use to verify their implementation.

SPECIFICATION:
{spec_content}

# Validation Scenarios

## Happy Path Scenarios
(Step-by-step scenarios described in prose — Given/When/Then format)

## Error and Edge Case Scenarios
(How the system should behave under invalid inputs or edge cases)

## Performance Validation
(How to verify non-functional requirements)

Describe all scenarios in natural language. Do NOT write test code or assertions.
"""
    try:
        qs_content = ai.generate(qs_prompt, feature=feature_dir.name)
        (feature_dir / "quickstart.md").write_text(qs_content)
        console.print("  [green]✓[/] Created quickstart.md")
    except ValueError as e:
        console.print(f"  [red]✗[/] quickstart.md rejected: {e}")

    # ── contracts/ ──
    contracts_dir = feature_dir / "contracts"
    contracts_dir.mkdir(exist_ok=True)
    console.print("[dim]Generating contracts...[/]")
    contracts_prompt = f"""Based on this specification, describe the key interface contracts
for this feature. Each contract should define the expected behavior of a boundary
or interface in prose.

SPECIFICATION:
{spec_content}

For each contract, use this format:

## Contract: [Name]

**Purpose:** (What this interface does)

**Inputs:** (What it accepts, described in prose)

**Outputs:** (What it produces, described in prose)

**Invariants:** (Rules that must always hold)

**Error Behavior:** (How failures are handled)

Produce 2-4 contracts. Use ONLY prose and tables. No code, no type signatures, no schemas.
"""
    try:
        contracts_content = ai.generate(contracts_prompt, feature=feature_dir.name)
        (contracts_dir / "interfaces.md").write_text(contracts_content)
        console.print("  [green]✓[/] Created contracts/interfaces.md")
    except ValueError as e:
        console.print(f"  [red]✗[/] contracts rejected: {e}")
