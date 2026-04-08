"""sdd roadmap — Define the feature roadmap for the product."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.ai import AIOrchestrator

console = Console()


@click.command()
@click.option("--description", "-d", default=None, help="Additional context about what the product should do.")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default="gpt-4o-mini", help="LLM model to use.")
@click.option("--no-ai", is_flag=True, help="Skip AI generation, create blank template only.")
def feature_roadmap_cmd(description: str, path: str, model: str, no_ai: bool):
    """Define ALL features needed to realize the product vision."""
    root = Path(path).resolve()
    csdd_dir = root / ".csdd"

    if not csdd_dir.is_dir():
        raise click.ClickException("No .csdd/ directory found. Run 'csdd init' first.")

    memory_dir = csdd_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    roadmap_path = memory_dir / "feature-roadmap.md"

    # Load product vision for context
    vision_content = ""
    vision_path = memory_dir / "product-vision.md"
    if vision_path.exists():
        vision_content = vision_path.read_text()
    else:
        console.print("[yellow]⚠ No product vision found. Run 'csdd vision' first for best results.[/]")

    # Load tech stack for context
    tech_stack_content = ""
    tech_stack_path = memory_dir / "tech-stack.md"
    if tech_stack_path.exists():
        tech_stack_content = tech_stack_path.read_text()

    # Load architecture for context
    architecture_content = ""
    architecture_path = memory_dir / "architecture.md"
    if architecture_path.exists():
        architecture_content = architecture_path.read_text()

    console.print(Panel(
        "[bold cyan]Defining feature roadmap[/]\n"
        + (f"[dim]{description[:120]}[/]" if description else "[dim]Based on product vision[/]"),
        title="sdd roadmap",
    ))

    if no_ai:
        content = _default_roadmap_template(description or "")
    else:
        console.print("[dim]Generating feature roadmap with AI...[/]")
        ai = AIOrchestrator(
            model=model,
            audit_dir=memory_dir,
        )

        # Load constitution for context
        constitution = ""
        constitution_path = memory_dir / "constitution.md"
        if constitution_path.exists():
            constitution = constitution_path.read_text()

        context_parts = []
        if vision_content:
            context_parts.append(f"PRODUCT VISION:\n{vision_content}")
        if tech_stack_content:
            context_parts.append(f"TECH STACK:\n{tech_stack_content}")
        if architecture_content:
            context_parts.append(f"ARCHITECTURE:\n{architecture_content}")
        if constitution:
            context_parts.append(f"CONSTITUTION:\n{constitution}")
        if description:
            context_parts.append(f"ADDITIONAL CONTEXT:\n{description}")

        context = "\n\n".join(context_parts)

        prompt = f"""Based on the following product context, define a comprehensive feature roadmap listing ALL features
needed to make this product a reality.

{context}

Write the roadmap using these EXACT Markdown headings. Write in prose, tables, and checklists only.
Do NOT include any code, code fences, or executable snippets.

# Feature Roadmap

## Overview
(Brief summary of the product and how features are organized)

## Feature List

For EACH feature, use this exact format:

### FEAT-NNN: Feature Name
- **Priority:** High | Medium | Low
- **Category:** (e.g., Core, User Experience, Infrastructure, Integration, Security, Analytics)
- **Description:** (1-2 sentence description of what this feature does)
- **User Value:** (Why this feature matters to the user)
- **Dependencies:** (Other FEAT-NNN items this depends on, or "None")
- **Complexity:** Small | Medium | Large

List features in recommended implementation order, grouped by priority. Number them
sequentially as FEAT-001, FEAT-002, etc.

## Implementation Phases
(Group features into logical implementation phases or milestones)

### Phase 1: Foundation
(Core features that must be built first)

### Phase 2: Core Experience
(Features that deliver the primary value)

### Phase 3: Polish and Scale
(Features that enhance, optimize, or extend)

## Open Questions
(Mark anything unclear with [NEEDS CLARIFICATION])

IMPORTANT:
- List ALL features, not just the obvious ones. Think about infrastructure, error handling,
  user onboarding, monitoring, deployment, and administrative features.
- Each feature should be scoped to be implementable independently through the
  specify -> clarify -> plan -> tasks -> review pipeline.
- Features should be small enough to spec individually but large enough to deliver user value.
"""

        try:
            content = ai.generate(prompt, feature="feature-roadmap")
        except ValueError as e:
            console.print(f"[bold red]Constitution violation:[/] {e}")
            return

    # Write the roadmap
    roadmap_path.write_text(content)
    console.print(f"  [green]✓[/] Created {roadmap_path.relative_to(root)}")

    # Summary
    console.print()
    console.print("[bold green]Feature roadmap created.[/] Next steps:")
    console.print(f"  1. Review and refine: {roadmap_path.relative_to(root)}")
    console.print("  2. Answer any [NEEDS CLARIFICATION] items")
    console.print("  3. For each feature, run the spec pipeline:")
    console.print("     [bold]sdd specify --idea 'FEAT-001: ...'[/]")
    console.print("     [bold]sdd clarify --feature 001-...[/]")
    console.print("     [bold]sdd plan --feature 001-...[/]")
    console.print("     [bold]sdd tasks --feature 001-...[/]")
    console.print("     Then CLAUDE CLI IMPLEMENTS the feature")
    console.print("     [bold]sdd review --feature 001-...[/]")


def _default_roadmap_template(description: str) -> str:
    return f"""# Feature Roadmap

## Overview
{description or "[NEEDS CLARIFICATION] — Describe the product and its goals."}

## Feature List

### FEAT-001: [Feature Name]
- **Priority:** High
- **Category:** Core
- **Description:** [NEEDS CLARIFICATION]
- **User Value:** [NEEDS CLARIFICATION]
- **Dependencies:** None
- **Complexity:** Medium

### FEAT-002: [Feature Name]
- **Priority:** High
- **Category:** Core
- **Description:** [NEEDS CLARIFICATION]
- **User Value:** [NEEDS CLARIFICATION]
- **Dependencies:** FEAT-001
- **Complexity:** Medium

## Implementation Phases

### Phase 1: Foundation
- FEAT-001: [Feature Name]

### Phase 2: Core Experience
- FEAT-002: [Feature Name]

### Phase 3: Polish and Scale
[NEEDS CLARIFICATION] — Define phase 3 features.

## Open Questions
- [NEEDS CLARIFICATION] — What are the key open questions?
"""
