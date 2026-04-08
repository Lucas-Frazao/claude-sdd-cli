"""sdd architecture — Define the application architecture for the project."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.ai import AIOrchestrator

console = Console()


@click.command()
@click.option("--description", "-d", default=None, help="Additional context about architectural preferences.")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default="gpt-4o-mini", help="LLM model to use.")
@click.option("--no-ai", is_flag=True, help="Skip AI generation, create blank template only.")
def architecture_cmd(description: str, path: str, model: str, no_ai: bool):
    """Define the application architecture — structure, layers, components, and data flow."""
    root = Path(path).resolve()
    csdd_dir = root / ".csdd"

    if not csdd_dir.is_dir():
        raise click.ClickException("No .csdd/ directory found. Run 'csdd init' first.")

    memory_dir = csdd_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    architecture_path = memory_dir / "architecture.md"

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
    else:
        console.print("[yellow]⚠ No tech stack found. Run 'csdd tech-stack' first for best results.[/]")

    console.print(Panel(
        "[bold cyan]Defining application architecture[/]\n"
        + (f"[dim]{description[:120]}[/]" if description else "[dim]Based on product vision and tech stack[/]"),
        title="sdd architecture",
    ))

    if no_ai:
        content = _default_architecture_template(description or "")
    else:
        console.print("[dim]Generating application architecture with AI...[/]")
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
        if constitution:
            context_parts.append(f"CONSTITUTION:\n{constitution}")
        if description:
            context_parts.append(f"ADDITIONAL CONTEXT:\n{description}")

        context = "\n\n".join(context_parts)

        prompt = f"""Based on the following product context, define the application architecture.

{context}

Write the architecture using these EXACT Markdown headings. Write in prose, tables, and checklists only.
Do NOT include any code, code fences, or executable snippets.

# Application Architecture

## Overview
(High-level architectural summary — what kind of application is this and how is it structured)

## Architecture Style
(e.g., Monolith, Microservices, Modular Monolith, Serverless, Event-Driven)
- **Rationale:** (Why this style for this project)

## System Layers
(Describe each layer of the application)

### Presentation Layer
(UI, API endpoints, CLI interface — how users interact with the system)

### Business Logic Layer
(Core domain logic, services, use cases)

### Data Access Layer
(Repositories, ORM, database access patterns)

### Infrastructure Layer
(External services, file system, networking, third-party integrations)

## Directory Structure
(The proposed folder/file organization of the codebase — described in prose and a tree diagram)

## Component Map
(Key components/modules and their responsibilities — use a table)

| Component | Responsibility | Layer | Dependencies |
|-----------|---------------|-------|-------------|
| ... | ... | ... | ... |

## Data Flow
(How data moves through the system — described in prose, not diagrams)

## API Boundaries
(Key interfaces between components — described in prose)

## Design Patterns
(Patterns used and why — e.g., Repository Pattern, Command Pattern, Observer)

## Error Handling Strategy
(How errors propagate through layers)

## Configuration Strategy
(How the app is configured — environment variables, config files, etc.)

## Open Questions
(Mark anything unclear with [NEEDS CLARIFICATION])

IMPORTANT:
- Base the architecture on the product vision AND the chosen tech stack.
- The directory structure should reflect the tech stack's conventions.
- Justify architectural decisions with rationale tied to the product's needs.
- Mark anything uncertain with [NEEDS CLARIFICATION].
"""

        try:
            content = ai.generate(prompt, feature="architecture")
        except ValueError as e:
            console.print(f"[bold red]Constitution violation:[/] {e}")
            return

    # Write the architecture
    architecture_path.write_text(content)
    console.print(f"  [green]✓[/] Created {architecture_path.relative_to(root)}")

    # Summary
    console.print()
    console.print("[bold green]Application architecture defined.[/] Next steps:")
    console.print(f"  1. Review and refine: {architecture_path.relative_to(root)}")
    console.print("  2. Answer any [NEEDS CLARIFICATION] items")
    console.print("  3. Run [bold]csdd roadmap --description '...'[/] to define the feature roadmap")


def _default_architecture_template(description: str) -> str:
    return f"""# Application Architecture

## Overview
{description or "[NEEDS CLARIFICATION] — Describe the high-level architecture of the application."}

## Architecture Style
[NEEDS CLARIFICATION] — Choose an architecture style (e.g., Monolith, Microservices, Modular Monolith).
- **Rationale:** [NEEDS CLARIFICATION]

## System Layers

### Presentation Layer
[NEEDS CLARIFICATION] — Describe how users interact with the system.

### Business Logic Layer
[NEEDS CLARIFICATION] — Describe core domain logic and services.

### Data Access Layer
[NEEDS CLARIFICATION] — Describe database access patterns.

### Infrastructure Layer
[NEEDS CLARIFICATION] — Describe external services and integrations.

## Directory Structure
[NEEDS CLARIFICATION] — Define the proposed folder/file organization.

## Component Map

| Component | Responsibility | Layer | Dependencies |
|-----------|---------------|-------|-------------|
| [NEEDS CLARIFICATION] | [NEEDS CLARIFICATION] | [NEEDS CLARIFICATION] | [NEEDS CLARIFICATION] |

## Data Flow
[NEEDS CLARIFICATION] — Describe how data moves through the system.

## API Boundaries
[NEEDS CLARIFICATION] — Describe key interfaces between components.

## Design Patterns
[NEEDS CLARIFICATION] — Define patterns used and why.

## Error Handling Strategy
[NEEDS CLARIFICATION] — Describe how errors propagate through layers.

## Configuration Strategy
[NEEDS CLARIFICATION] — Describe how the app is configured.

## Open Questions
- [NEEDS CLARIFICATION] — What are the key open questions about the architecture?
"""
