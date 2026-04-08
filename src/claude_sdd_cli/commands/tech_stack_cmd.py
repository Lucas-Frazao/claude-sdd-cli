"""sdd tech-stack — Define the technology stack for the project."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.ai import AIOrchestrator

console = Console()


@click.command()
@click.option("--description", "-d", default=None, help="Additional context about technology preferences.")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--model", "-m", default="gpt-4o-mini", help="LLM model to use.")
@click.option("--no-ai", is_flag=True, help="Skip AI generation, create blank template only.")
def tech_stack_cmd(description: str, path: str, model: str, no_ai: bool):
    """Define the technology stack — languages, frameworks, databases, and tooling."""
    root = Path(path).resolve()
    csdd_dir = root / ".csdd"

    if not csdd_dir.is_dir():
        raise click.ClickException("No .csdd/ directory found. Run 'csdd init' first.")

    memory_dir = csdd_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    tech_stack_path = memory_dir / "tech-stack.md"

    # Load product vision for context
    vision_content = ""
    vision_path = memory_dir / "product-vision.md"
    if vision_path.exists():
        vision_content = vision_path.read_text()
    else:
        console.print("[yellow]⚠ No product vision found. Run 'csdd vision' first for best results.[/]")

    console.print(Panel(
        "[bold cyan]Defining tech stack[/]\n"
        + (f"[dim]{description[:120]}[/]" if description else "[dim]Based on product vision[/]"),
        title="sdd tech-stack",
    ))

    if no_ai:
        content = _default_tech_stack_template(description or "")
    else:
        console.print("[dim]Generating tech stack with AI...[/]")
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
        if constitution:
            context_parts.append(f"CONSTITUTION:\n{constitution}")
        if description:
            context_parts.append(f"ADDITIONAL CONTEXT:\n{description}")

        context = "\n\n".join(context_parts)

        prompt = f"""Based on the following product context, define the technology stack for this project.

{context}

Write the tech stack using these EXACT Markdown headings. Write in prose, tables, and checklists only.
Do NOT include any code, code fences, or executable snippets.

# Tech Stack

## Overview
(Brief summary of the chosen technology stack and rationale)

## Programming Language(s)
- **Primary Language:** (e.g., Python 3.12)
- **Secondary Languages:** (if any)
- **Rationale:** (Why this language for this project)

## Framework(s)
- **Backend Framework:** (e.g., FastAPI, Django, Express)
- **Frontend Framework:** (e.g., React, Vue, Svelte — or N/A)
- **Rationale:** (Why these frameworks)

## Database & Storage
- **Primary Database:** (e.g., PostgreSQL, SQLite, MongoDB)
- **Caching:** (e.g., Redis — or N/A)
- **File Storage:** (e.g., S3, local — or N/A)
- **Rationale:** (Why these choices)

## Package Management & Build
- **Package Manager:** (e.g., uv, pip, npm, cargo)
- **Build System:** (e.g., hatch, webpack, cargo)
- **Dependency Pinning Strategy:** (e.g., lockfile, version ranges)

## Testing
- **Test Framework:** (e.g., pytest, jest, go test)
- **Coverage Tool:** (e.g., pytest-cov, istanbul)
- **Testing Strategy:** (unit, integration, e2e approach)

## DevOps & Deployment
- **CI/CD:** (e.g., GitHub Actions, GitLab CI)
- **Hosting/Infrastructure:** (e.g., AWS, Vercel, self-hosted)
- **Containerization:** (e.g., Docker — or N/A)

## Development Tools
- **Linter/Formatter:** (e.g., ruff, eslint, prettier)
- **Type Checking:** (e.g., mypy, TypeScript)
- **Other Tools:** (any other relevant tooling)

## Constraints & Compatibility
(Minimum versions, platform requirements, browser support, etc.)

## Open Questions
(Mark anything unclear with [NEEDS CLARIFICATION])

IMPORTANT:
- Base technology choices on the product vision and its requirements.
- Justify every choice with a rationale tied to the product's needs.
- Be specific about versions where possible.
- Mark anything uncertain with [NEEDS CLARIFICATION].
"""

        try:
            content = ai.generate(prompt, feature="tech-stack")
        except ValueError as e:
            console.print(f"[bold red]Constitution violation:[/] {e}")
            return

    # Write the tech stack
    tech_stack_path.write_text(content)
    console.print(f"  [green]✓[/] Created {tech_stack_path.relative_to(root)}")

    # Summary
    console.print()
    console.print("[bold green]Tech stack defined.[/] Next steps:")
    console.print(f"  1. Review and refine: {tech_stack_path.relative_to(root)}")
    console.print("  2. Answer any [NEEDS CLARIFICATION] items")
    console.print("  3. Run [bold]csdd architecture --description '...'[/] to define the application architecture")


def _default_tech_stack_template(description: str) -> str:
    return f"""# Tech Stack

## Overview
{description or "[NEEDS CLARIFICATION] — Describe the chosen technology stack and rationale."}

## Programming Language(s)
- **Primary Language:** [NEEDS CLARIFICATION]
- **Secondary Languages:** [NEEDS CLARIFICATION]
- **Rationale:** [NEEDS CLARIFICATION]

## Framework(s)
- **Backend Framework:** [NEEDS CLARIFICATION]
- **Frontend Framework:** [NEEDS CLARIFICATION]
- **Rationale:** [NEEDS CLARIFICATION]

## Database & Storage
- **Primary Database:** [NEEDS CLARIFICATION]
- **Caching:** [NEEDS CLARIFICATION]
- **File Storage:** [NEEDS CLARIFICATION]
- **Rationale:** [NEEDS CLARIFICATION]

## Package Management & Build
- **Package Manager:** [NEEDS CLARIFICATION]
- **Build System:** [NEEDS CLARIFICATION]
- **Dependency Pinning Strategy:** [NEEDS CLARIFICATION]

## Testing
- **Test Framework:** [NEEDS CLARIFICATION]
- **Coverage Tool:** [NEEDS CLARIFICATION]
- **Testing Strategy:** [NEEDS CLARIFICATION]

## DevOps & Deployment
- **CI/CD:** [NEEDS CLARIFICATION]
- **Hosting/Infrastructure:** [NEEDS CLARIFICATION]
- **Containerization:** [NEEDS CLARIFICATION]

## Development Tools
- **Linter/Formatter:** [NEEDS CLARIFICATION]
- **Type Checking:** [NEEDS CLARIFICATION]
- **Other Tools:** [NEEDS CLARIFICATION]

## Constraints & Compatibility
[NEEDS CLARIFICATION] — Define minimum versions, platform requirements, etc.

## Open Questions
- [NEEDS CLARIFICATION] — What are the key open questions about the tech stack?
"""
