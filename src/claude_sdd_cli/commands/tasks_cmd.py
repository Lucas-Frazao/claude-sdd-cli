"""sdd tasks — Create a Claude CLI execution checklist from planning artifacts."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from claude_sdd_cli.ai import AIOrchestrator
from claude_sdd_cli.parsers import load_feature_artifact

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
@click.option("--no-ai", is_flag=True, help="Skip AI, create blank template only.")
def tasks_cmd(feature: str, path: str, model: str, no_ai: bool):
    """Generate a Claude CLI execution checklist from planning artifacts."""
    root = Path(path).resolve()
    feature_dir = _find_feature_dir(root, feature)

    console.print(Panel(
        f"[bold cyan]Generating tasks for:[/] {feature_dir.name}",
        title="sdd tasks",
    ))

    if no_ai:
        content = _blank_tasks_template(feature_dir.name)
    else:
        # Collect all available artifacts
        artifacts_text = ""
        for artifact in ["spec", "plan", "data-model", "research", "quickstart"]:
            try:
                text = load_feature_artifact(feature_dir, artifact)
                artifacts_text += f"\n## {artifact.upper()}.MD\n\n{text}\n"
            except FileNotFoundError:
                pass

        # Load contracts
        contracts_dir = feature_dir / "contracts"
        if contracts_dir.exists():
            for f in sorted(contracts_dir.glob("*.md")):
                artifacts_text += f"\n## CONTRACT: {f.stem}\n\n{f.read_text()}\n"

        if not artifacts_text.strip():
            raise click.ClickException(
                "No planning artifacts found. Run `sdd plan` first."
            )

        console.print("[dim]Generating task breakdown...[/]")
        ai = AIOrchestrator(model=model, audit_dir=feature_dir)

        prompt = f"""Based on the following planning artifacts, create a detailed implementation checklist for Claude CLI.

ARTIFACTS:
{artifacts_text}

Create the task list using this EXACT format. Use ONLY checklists and prose descriptions.
Do NOT include any code, code fences, commands, or executable content.

# Implementation Tasks: {feature_dir.name}

## Setup Tasks
(Tasks for project setup, directory structure, dependencies)
- [ ] TASK-001: Description (traces: REQ-XXX)

## Data Model Tasks
(Tasks for implementing data entities and storage)
- [ ] TASK-XXX: Description (traces: REQ-XXX)

## Core Logic Tasks
(Tasks for implementing the main feature logic)
- [ ] TASK-XXX: Description (traces: REQ-XXX)

## Integration Tasks
(Tasks for connecting components, APIs, interfaces)
- [ ] TASK-XXX: Description (traces: REQ-XXX)

## Validation Tasks
(Tasks for testing and verifying the implementation)
- [ ] TASK-XXX: Description (traces: REQ-XXX)

## Documentation Tasks
(Tasks for documenting the implementation)
- [ ] TASK-XXX: Description (traces: REQ-XXX)

## Review Tasks
(Tasks for final review and cleanup)
- [ ] TASK-XXX: Description (traces: REQ-XXX)

IMPORTANT RULES:
- Number tasks sequentially: TASK-001, TASK-002, etc.
- Each task must trace to at least one requirement using (traces: REQ-XXX)
- Note dependencies between tasks in the description
- Flag tasks that can be done in parallel with a [PARALLEL] marker
- Keep tasks concrete and actionable
- Do NOT suggest any code, commands, or executable content

## Claude CLI Implementation Notes
(Context and guidance for Claude CLI to implement these tasks effectively)
- Include specific file paths where code should be written
- Reference the requirement each task fulfills
- Note key context from the spec/plan that Claude CLI needs
"""
        try:
            content = ai.generate(prompt, feature=feature_dir.name)
        except ValueError as e:
            console.print(f"[bold red]Constitution violation:[/] {e}")
            return

    tasks_path = feature_dir / "tasks.md"
    tasks_path.write_text(content)
    console.print(f"  [green]✓[/] Created {tasks_path.relative_to(root)}")

    console.print()
    console.print("[bold green]Task breakdown created.[/] Next steps:")
    console.print(f"  1. Review: {tasks_path.relative_to(root)}")
    console.print("  2. Send tasks to Claude CLI for implementation")
    console.print(f"  3. After implementing, run [bold]sdd review --feature {feature_dir.name}[/]")


def _blank_tasks_template(feature_name: str) -> str:
    return f"""# Implementation Tasks: {feature_name}

## Setup Tasks
- [ ] TASK-001: [NEEDS CLARIFICATION] (traces: REQ-001)

## Data Model Tasks
- [ ] TASK-002: [NEEDS CLARIFICATION] (traces: REQ-001)

## Core Logic Tasks
- [ ] TASK-003: [NEEDS CLARIFICATION] (traces: REQ-001)

## Integration Tasks
- [ ] TASK-004: [NEEDS CLARIFICATION] (traces: REQ-001)

## Validation Tasks
- [ ] TASK-005: [NEEDS CLARIFICATION] (traces: REQ-001)

## Documentation Tasks
- [ ] TASK-006: [NEEDS CLARIFICATION] (traces: REQ-001)

## Review Tasks
- [ ] TASK-007: [NEEDS CLARIFICATION] (traces: REQ-001)
"""
