"""sdd init — Initialize a project for Claude SDD."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.templates import copy_templates_to, load_template, populate_template

console = Console()

DEFAULT_DIRS = [
    "docs",
    "docs/examples",
    "specs",
    "templates",
]

DOCS_FILES = {
    "docs/philosophy.md": "philosophy",
    "docs/workflow.md": "workflow",
}


@click.command()
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--name", "-n", prompt="Project name", help="Name of the project.")
def init_cmd(path: str, name: str):
    """Initialize a project workspace for spec-driven development."""
    root = Path(path).resolve()

    console.print(Panel(
        f"[bold cyan]Initializing SDD workspace:[/] {name}\n"
        f"[dim]{root}[/]",
        title="sdd init",
    ))

    # Create directories
    for d in DEFAULT_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/] Created {d}/")

    # Copy templates
    copied = copy_templates_to(root / "templates")
    for p in copied:
        console.print(f"  [green]✓[/] Copied template {p.name}")

    # Create constitution
    constitution_path = root / "docs" / "constitution.md"
    if not constitution_path.exists():
        try:
            content = load_template("constitution-template")
            content = populate_template(content, {"project_name": name})
        except FileNotFoundError:
            content = _default_constitution(name)
        constitution_path.write_text(content)
        console.print("  [green]✓[/] Created docs/constitution.md")
    else:
        console.print("  [yellow]●[/] docs/constitution.md already exists, skipping")

    # Create philosophy and workflow docs
    for rel_path, template_name in DOCS_FILES.items():
        full_path = root / rel_path
        if not full_path.exists():
            try:
                content = load_template(f"{template_name}-template")
            except FileNotFoundError:
                content = _default_doc(template_name, name)
            full_path.write_text(content)
            console.print(f"  [green]✓[/] Created {rel_path}")

    # Create .sdd marker file
    marker = root / ".sdd"
    marker.write_text(f"project: {name}\nversion: 0.1.0\n")
    console.print("  [green]✓[/] Created .sdd marker")

    console.print()
    console.print("[bold green]Workspace initialized.[/] Next steps:")
    console.print("  1. Review docs/constitution.md")
    console.print("  2. Run [bold]sdd specify --idea \"your feature idea\"[/]")


def _default_constitution(name: str) -> str:
    return f"""# Constitution — {name}

## Article 1: Specification-First Principle
Every feature begins with a structured specification before implementation starts.
Requirements, user stories, edge cases, and success criteria are defined first.

## Article 2: Claude CLI Implementation Mandate
All executable project artifacts must be implemented via Claude CLI. The planning AI (Copilot) may not generate implementation code, test code, infrastructure code, migration code, build scripts, configuration code, or any other executable artifact. Claude CLI is the sole implementer.

## Article 3: AI Planning-Only Mandate
The planning AI (Copilot) participation is restricted to requirement clarification, research, planning,
task decomposition, review commentary, consistency checking, and traceability support.

## Article 4: Ambiguity Marking Requirement
When requirements are ambiguous or underspecified, the system must mark them with
[NEEDS CLARIFICATION] rather than guessing or filling in assumptions silently.

## Article 5: Traceability Requirement
Each task must map to one or more requirements. Each review finding must reference
a requirement, contract, or planning decision.

## Article 6: Review-Before-Regeneration Principle
The tool emphasizes validation, consistency checking, and review.
When gaps are found, the output is follow-up tasks and questions — not code patches.

## Article 7: No Executable Planning AI Output Rule
Any planning AI (Copilot) artifact containing executable code, code fences with implementation
content, or copy-paste-ready source/config/test content must be rejected or quarantined.
Tasks are intended for Claude CLI to implement.

## Article 8: Transparency and Auditability
Prompt and response history is preserved for review. Every planning decision
should be traceable to a user requirement or explicit assumption.
"""


def _default_doc(doc_type: str, name: str) -> str:
    if doc_type == "philosophy":
        return f"""# Philosophy — {name}

This project follows **Claude SDD (Specification-Driven Development)**, a workflow
where specifications drive development, but Claude CLI implements all code based on planning artifacts.

## Why?

- Specifications should be the source of truth.
- AI (Copilot) strengthens thinking, Claude CLI implements.
- Clear specifications guide Claude CLI implementation.
- Planning support should be structured and disciplined, not automated.

## The AI's Role

The planning AI (Copilot) acts as a **planning copilot**: it helps you think through requirements,
identify ambiguity, structure plans, and review your work. It never writes code.
Claude CLI implements the tasks.

## The Developer's Role

Claude CLI handles all implementation. Every function, test, config, and migration is implemented by Claude CLI from the planning artifacts.
Copilot helps plan; Claude CLI builds.
"""
    else:  # workflow
        return f"""# Workflow — {name}

## Phase 1: Initialize
Run `sdd init` to create the workspace, templates, and constitution.

## Phase 2: Specify
Run `sdd specify --idea "your idea"` to generate a structured specification.
Answer clarifying questions. Mark ambiguity with [NEEDS CLARIFICATION].

## Phase 3: Refine
Review the spec. Answer open questions. Iterate until the spec is clear and testable.

## Phase 4: Plan
Run `sdd plan --feature <name>` to generate a technical planning package.
Produces plan.md, research.md, data-model.md, contracts, and quickstart.md.

## Phase 5: Tasks
Run `sdd tasks --feature <name>` to create a Claude CLI execution checklist.

## Phase 6: Implement
Claude CLI implements the code based on the task breakdown.

## Phase 7: Review
Run `sdd review --feature <name>` to compare your implementation against the spec.

## Phase 8: Trace
Run `sdd trace --feature <name>` to verify requirement coverage.
"""
