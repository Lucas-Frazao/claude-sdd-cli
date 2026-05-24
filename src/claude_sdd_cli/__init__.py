"""Claude SDD -- Specification-Driven Development CLI.

Claude plans, you implement. A planning assistant (Claude in the VS Code
extension) that helps you write specs, plans, and tasks -- then you implement
them by hand.

Usage:
    csdd init <project-name>
    csdd init --here
    csdd check

Or install globally:
    uv tool install claude-sdd-cli --from git+https://github.com/Lucas-Frazao/claude-sdd-cli.git
    csdd init my-project
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

import readchar

__version__ = "0.2.0"

BANNER = """
 ██████╗███████╗██████╗ ██████╗
██╔════╝██╔════╝██╔══██╗██╔══██╗
██║     ███████╗██║  ██║██║  ██║
██║     ╚════██║██║  ██║██║  ██║
╚██████╗███████║██████╔╝██████╔╝
 ╚═════╝╚══════╝╚═════╝ ╚═════╝
"""

TAGLINE = "Claude SDD -- Claude plans, you implement"

AI_ASSISTANTS = {
    "claude-vscode": "Claude (VS Code extension)",
}

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)"}


class StepTracker:
    """Track and render hierarchical steps, similar to spec-kit's StepTracker."""

    def __init__(self, title: str):
        self.title = title
        self.steps: list[dict[str, str]] = []
        self._refresh_cb = None

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({"key": key, "label": label, "status": "pending", "detail": ""})
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return
        self.steps.append({"key": key, "label": key, "status": status, "detail": detail})
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""
            status = step["status"]

            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                if detail_text:
                    line = f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree


def get_key():
    """Get a single keypress using readchar."""
    key = readchar.readkey()
    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return "up"
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return "down"
    if key == readchar.key.ENTER:
        return "enter"
    if key == readchar.key.ESC:
        return "escape"
    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt
    return key


def select_with_arrows(options: dict, prompt_text: str = "Select an option", default_key: str = None) -> str:
    """Interactive selection using arrow keys with Rich Live display."""
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row(">>", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row("", "[dim]Use arrows to navigate, Enter to select, Esc to cancel[/dim]")

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == "up":
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == "down":
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == "enter":
                        selected_key = option_keys[selected_index]
                        break
                    elif key == "escape":
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)
                    live.update(create_selection_panel(), refresh=True)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key


console = Console()


class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="csdd",
    help="Claude SDD CLI -- Claude plans, you implement.",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split("\n")
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()


@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        console.print(Align.center("[dim]Run 'csdd --help' for usage information[/dim]"))
        console.print()


def _locate_core_pack() -> Path | None:
    """Find bundled core_pack directory (wheel installs)."""
    candidate = Path(__file__).parent / "core_pack"
    if candidate.is_dir():
        return candidate
    return None


def _locate_source_root() -> Path | None:
    """Find source repo root (dev installs)."""
    candidate = Path(__file__).parent.parent.parent
    if (candidate / "templates").is_dir():
        return candidate
    return None


def _install_shared_infra(project_path: Path, tracker: StepTracker) -> None:
    """Copy .csdd/scripts/ and .csdd/templates/ to the project."""
    csdd_dir = project_path / ".csdd"

    # Copy scripts
    tracker.start("scripts", "Copying shell scripts")
    scripts_dest = csdd_dir / "scripts" / "bash"
    scripts_dest.mkdir(parents=True, exist_ok=True)

    core_pack = _locate_core_pack()
    source_root = _locate_source_root()

    if core_pack:
        scripts_src = core_pack / "scripts" / "bash"
    elif source_root:
        scripts_src = source_root / "scripts" / "bash"
    else:
        scripts_src = None

    if scripts_src and scripts_src.is_dir():
        for f in scripts_src.iterdir():
            if f.is_file():
                shutil.copy2(f, scripts_dest / f.name)
        _ensure_executable_scripts(scripts_dest)
        tracker.complete("scripts", "Shell scripts installed")
    else:
        tracker.skip("scripts", "No scripts found to install")

    # Copy templates
    tracker.start("templates", "Copying templates")
    templates_dest = csdd_dir / "templates"
    templates_dest.mkdir(parents=True, exist_ok=True)

    if core_pack:
        templates_src = core_pack / "templates"
    elif source_root:
        templates_src = source_root / "templates"
    else:
        templates_src = None

    if templates_src and templates_src.is_dir():
        for f in templates_src.iterdir():
            if f.is_file() and f.suffix == ".md":
                shutil.copy2(f, templates_dest / f.name)
        tracker.complete("templates", "Templates installed")
    else:
        tracker.skip("templates", "No templates found to install")


def _ensure_executable_scripts(scripts_dir: Path) -> None:
    """Make .sh scripts executable."""
    if sys.platform == "win32":
        return
    for f in scripts_dir.glob("*.sh"):
        f.chmod(f.stat().st_mode | 0o111)


def _ensure_constitution(project_path: Path, project_name: str, tracker: StepTracker) -> None:
    """Copy constitution template to .csdd/memory/constitution.md."""
    tracker.start("constitution", "Setting up constitution")
    memory_dir = project_path / ".csdd" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    constitution_path = memory_dir / "constitution.md"
    if constitution_path.exists():
        tracker.complete("constitution", "Already exists")
        return

    # Try to find the constitution template
    core_pack = _locate_core_pack()
    source_root = _locate_source_root()

    template_path = None
    if core_pack:
        candidate = core_pack / "templates" / "constitution-template.md"
        if candidate.is_file():
            template_path = candidate
    if not template_path and source_root:
        candidate = source_root / "templates" / "constitution-template.md"
        if candidate.is_file():
            template_path = candidate

    if template_path:
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("{{project_name}}", project_name)
        constitution_path.write_text(content, encoding="utf-8")
    else:
        constitution_path.write_text(
            _default_constitution(project_name), encoding="utf-8"
        )

    tracker.complete("constitution", "Created")


def _default_constitution(name: str) -> str:
    return f"""# Constitution -- {name}

## Article 1: Specification-First Principle
Every feature begins with a structured specification before implementation starts.
Requirements, user stories, edge cases, and success criteria are defined first.

## Article 2: Human Implementation Mandate
All executable project artifacts must be implemented by a human developer.
The planning AI (Claude in the VS Code extension) may not generate
implementation code, test code, infrastructure code, migration code, build
scripts, configuration code, or any other executable artifact. The human is
the sole implementer; AI only plans.

## Article 3: AI Planning-Only Mandate
The planning AI participates only in requirement clarification, research,
planning, task decomposition, review commentary, consistency checking, and
traceability support. It produces prose, tables, and checklists -- never code.

## Article 4: Ambiguity Marking Requirement
When requirements are ambiguous or underspecified, the system must mark them
with [NEEDS CLARIFICATION] rather than guessing or filling in assumptions
silently.

## Article 5: Traceability Requirement
Each task must map to one or more requirements. Each review finding must
reference a requirement, contract, or planning decision.

## Article 6: Review-Before-Regeneration Principle
The tool emphasizes validation, consistency checking, and review. When gaps
are found, the output is follow-up tasks and questions -- not code patches.

## Article 7: No Executable Planning AI Output Rule
Any planning AI artifact containing executable code, code fences with
implementation content, or copy-paste-ready source/config/test content must
be rejected or quarantined. Tasks describe WHAT to build and WHERE; the
human writes every line of code.

## Article 8: Transparency and Auditability
Prompt and response history is preserved for review. Every planning decision
should be traceable to a user requirement or explicit assumption.
"""


def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()
    if not path.is_dir():
        return False
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def init_git_repo(project_path: Path, quiet: bool = False) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path."""
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from CSDD template"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True, None
    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        return False, error_msg
    finally:
        os.chdir(original_cwd)


def _stage_csdd_files(project_path: Path) -> None:
    """Stage .csdd/, .github/, and .vscode/ files in an existing git repo.

    When ``csdd init --here`` runs inside an existing repo, the integration
    step creates new files that would otherwise remain untracked.  This
    function stages them so the user sees them in ``git status`` and won't
    accidentally forget to commit.
    """
    paths_to_stage = [".csdd", ".claude", ".vscode", "specs", "CLAUDE.md"]
    try:
        subprocess.run(
            ["git", "add", "--"] + paths_to_stage,
            check=True,
            capture_output=True,
            cwd=project_path,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Best-effort; don't fail init if staging fails


def _save_init_options(project_path: Path, options: dict) -> None:
    """Persist init CLI options in .csdd/init-options.json."""
    init_options_path = project_path / ".csdd" / "init-options.json"
    init_options_path.write_text(
        json.dumps(options, indent=2) + "\n", encoding="utf-8"
    )


@app.command()
def init(
    project_name: str = typer.Argument(None, help="Name of the project to create (or '.' for current dir)"),
    here: bool = typer.Option(False, "--here", help="Initialize in the current directory"),
    ai: str = typer.Option(
        None,
        "--ai",
        help="AI assistant to use (only 'claude-vscode' is supported).",
    ),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git initialization"),
):
    """Initialize a new Claude SDD project."""
    # Resolve project path
    if here or project_name == ".":
        project_path = Path.cwd()
        project_name = project_path.name
    elif project_name:
        project_path = Path.cwd() / project_name
    else:
        console.print("[red]Please provide a project name or use --here[/red]")
        raise typer.Exit(1)

    show_banner()

    # Only claude-vscode is supported; if the user passes anything else,
    # reject it with a clear message.
    if ai is None:
        ai = "claude-vscode"
    elif ai not in AI_ASSISTANTS:
        console.print(
            f"[red]Unknown AI assistant: {ai}[/red] "
            "Only 'claude-vscode' is supported."
        )
        raise typer.Exit(1)

    console.print(f"\n[cyan]AI assistant:[/cyan] {ai}")
    console.print(f"[cyan]Project:[/cyan] {project_name}")
    console.print(f"[cyan]Path:[/cyan] {project_path}")
    console.print()

    # Create project directory
    project_path.mkdir(parents=True, exist_ok=True)

    # Set up the step tracker
    tracker = StepTracker("Initializing CSDD project")
    tracker.add("dirs", "Create .csdd/ directory structure")
    tracker.add("scripts", "Install shell scripts")
    tracker.add("templates", "Install templates")
    tracker.add("constitution", "Set up constitution")
    tracker.add("integration", f"Set up {ai} integration")
    if not no_git:
        tracker.add("git", "Initialize git repository")
    tracker.add("options", "Save init options")

    with Live(tracker.render(), console=console, transient=False, auto_refresh=False) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render(), refresh=True))

        # 1. Create .csdd/ directory structure
        tracker.start("dirs", "Creating directories")
        csdd_dir = project_path / ".csdd"
        for subdir in ["memory", "templates", "scripts/bash"]:
            (csdd_dir / subdir).mkdir(parents=True, exist_ok=True)
        (project_path / "specs").mkdir(parents=True, exist_ok=True)
        tracker.complete("dirs", "Created")

        # 2. Install shared infrastructure (scripts + templates)
        _install_shared_infra(project_path, tracker)

        # 3. Set up constitution
        _ensure_constitution(project_path, project_name, tracker)

        # 4. Integration setup
        tracker.start("integration", f"Setting up {ai}")
        if ai == "claude-vscode":
            from claude_sdd_cli.integrations.claude_vscode import (
                ClaudeVSCodeIntegration,
            )

            integration = ClaudeVSCodeIntegration()
            created_files = integration.setup(project_path)
            tracker.complete("integration", f"{len(created_files)} files created")
        else:
            tracker.skip("integration", f"Unknown assistant: {ai}")

        # 5. Git initialization
        if not no_git:
            tracker.start("git", "Initializing repository")
            if is_git_repo(project_path):
                # Stage newly created files so they aren't forgotten
                _stage_csdd_files(project_path)
                tracker.complete("git", "Already a git repo (new files staged)")
            else:
                success, error = init_git_repo(project_path, quiet=True)
                if success:
                    tracker.complete("git", "Initialized")
                else:
                    tracker.error("git", error or "Failed")

        # 6. Save init options
        tracker.start("options", "Saving configuration")
        _save_init_options(project_path, {
            "ai_assistant": ai,
            "project_name": project_name,
            "version": __version__,
        })
        tracker.complete("options", "Saved")

    # Show next steps
    console.print()
    next_steps = Table.grid(padding=(0, 2))
    next_steps.add_column(style="cyan", justify="right")
    next_steps.add_column(style="white")

    if ai == "claude-vscode":
        next_steps.add_row("1.", "Open the project in VS Code")
        next_steps.add_row(
            "2.",
            "If VS Code was already open: run 'Developer: Reload Window' so "
            "the Claude extension picks up .claude/commands/",
        )
        next_steps.add_row("3.", "Open the Claude chat panel")
        next_steps.add_row("4.", "Type: /vision to define your product vision")
        next_steps.add_row("5.", "Type: /tech-stack to define your technology stack")
        next_steps.add_row("6.", "Type: /architecture to define your application architecture")
        next_steps.add_row("7.", "Type: /roadmap to define your feature roadmap")
        next_steps.add_row(
            "8.",
            "For each feature: /specify -> /clarify -> /plan -> /tasks -> "
            "YOU IMPLEMENT -> /review",
        )
    else:
        next_steps.add_row("1.", "Review .csdd/memory/constitution.md")
        next_steps.add_row("2.", "Run: csdd vision --description 'your product idea'")
        next_steps.add_row("3.", "Run: csdd tech-stack")
        next_steps.add_row("4.", "Run: csdd architecture")
        next_steps.add_row("5.", "Run: csdd roadmap")
        next_steps.add_row("6.", "For each feature: csdd specify -> clarify -> plan -> tasks -> YOU IMPLEMENT -> review")

    console.print(Panel(
        next_steps,
        title="[bold green]Next Steps[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


@app.command()
def integrate(
    ai: str = typer.Argument(
        "claude-vscode",
        help="AI assistant to integrate (only 'claude-vscode' is supported).",
    ),
):
    """Set up or re-run the Claude VS Code extension integration."""
    project_path = Path.cwd()

    if not (project_path / ".csdd").is_dir():
        console.print("[red]No .csdd/ directory found. Run 'csdd init' first.[/red]")
        raise typer.Exit(1)

    if ai != "claude-vscode":
        console.print(
            f"[red]Unknown AI assistant: {ai}[/red] "
            "Only 'claude-vscode' is supported."
        )
        raise typer.Exit(1)

    from claude_sdd_cli.integrations.claude_vscode import ClaudeVSCodeIntegration

    integration = ClaudeVSCodeIntegration()
    created = integration.setup(project_path)
    if is_git_repo(project_path):
        _stage_csdd_files(project_path)
    console.print(
        f"[green]Claude (VS Code) integration complete.[/green] "
        f"{len(created)} files created/updated."
    )
    for f in created:
        rel = f.relative_to(project_path)
        console.print(f"  [dim]{rel}[/dim]")

    _warn_about_legacy_paths(project_path)

    console.print()
    console.print(
        Panel(
            "[bold]Reload required for the Claude chat panel to pick up new "
            "slash commands.[/bold]\n\n"
            "In VS Code, run the command palette action "
            "[cyan]Developer: Reload Window[/cyan] (Cmd/Ctrl+Shift+P), or close "
            "and reopen the Claude chat panel. Then type [cyan]/[/cyan] in the "
            "chat — [cyan]/vision[/cyan], [cyan]/specify[/cyan], etc. should appear.\n\n"
            "If commands still do not appear, run [cyan]csdd check[/cyan] from "
            "this directory to verify the install.",
            title="[bold yellow]Next step[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )
    if is_git_repo(project_path):
        console.print(
            "[dim]New files have been staged. Run 'git commit' to save them.[/dim]"
        )


def _warn_about_legacy_paths(project_path: Path) -> None:
    """Warn if old Copilot-era paths still linger in the project.

    These were created by pre-0.2.0 versions of the integration and are now
    inert — but they confuse users who think the tool is still managing them.
    """
    legacy = [
        project_path / ".github" / "skills",
        project_path / ".github" / "copilot-instructions.md",
    ]
    found = [p for p in legacy if p.exists()]
    if not found:
        return
    console.print()
    console.print(
        "[yellow]Warning:[/yellow] legacy paths from an older version of this "
        "tool are still present and are no longer used:"
    )
    for p in found:
        rel = p.relative_to(project_path)
        console.print(f"  [dim]{rel}[/dim]")
    console.print(
        "[dim]Safe to delete. They were the old GitHub Copilot install location; "
        "Claude Code reads .claude/commands/ instead.[/dim]"
    )


@app.command()
def check():
    """Verify project setup and installed tools."""
    project_path = Path.cwd()

    console.print(
        f"[bold]Checking CSDD project setup...[/bold] "
        f"[dim](csdd v{__version__})[/dim]\n"
    )

    tracker = StepTracker("Project Check")
    tracker.add("csdd_dir", ".csdd/ directory")
    tracker.add("constitution", "Constitution")
    tracker.add("vision", "Product Vision")
    tracker.add("tech_stack", "Tech Stack")
    tracker.add("architecture", "Architecture")
    tracker.add("roadmap", "Feature Roadmap")
    tracker.add("templates", "Templates")
    tracker.add("scripts", "Scripts")
    tracker.add("commands", "Claude VS Code slash commands")
    tracker.add("commands_fresh", "Slash-command content is up to date")
    tracker.add("claude_md", "CLAUDE.md project context")
    tracker.add("legacy", "No legacy Copilot paths")
    tracker.add("git", "Git repository")

    # Check .csdd/
    if (project_path / ".csdd").is_dir():
        tracker.complete("csdd_dir", "Found")
    else:
        tracker.error("csdd_dir", "Not found -- run 'csdd init'")

    # Check constitution
    if (project_path / ".csdd" / "memory" / "constitution.md").is_file():
        tracker.complete("constitution", "Found")
    else:
        tracker.error("constitution", "Not found")

    # Check product vision
    if (project_path / ".csdd" / "memory" / "product-vision.md").is_file():
        tracker.complete("vision", "Found")
    else:
        tracker.skip("vision", "Not created yet -- run 'csdd vision'")

    # Check tech stack
    if (project_path / ".csdd" / "memory" / "tech-stack.md").is_file():
        tracker.complete("tech_stack", "Found")
    else:
        tracker.skip("tech_stack", "Not created yet -- run 'csdd tech-stack'")

    # Check architecture
    if (project_path / ".csdd" / "memory" / "architecture.md").is_file():
        tracker.complete("architecture", "Found")
    else:
        tracker.skip("architecture", "Not created yet -- run 'csdd architecture'")

    # Check feature roadmap
    if (project_path / ".csdd" / "memory" / "feature-roadmap.md").is_file():
        tracker.complete("roadmap", "Found")
    else:
        tracker.skip("roadmap", "Not created yet -- run 'csdd roadmap'")

    # Check templates
    templates_dir = project_path / ".csdd" / "templates"
    if templates_dir.is_dir() and any(templates_dir.glob("*.md")):
        count = len(list(templates_dir.glob("*.md")))
        tracker.complete("templates", f"{count} templates found")
    else:
        tracker.error("templates", "No templates found")

    # Check scripts
    scripts_dir = project_path / ".csdd" / "scripts" / "bash"
    if scripts_dir.is_dir() and any(scripts_dir.glob("*.sh")):
        count = len(list(scripts_dir.glob("*.sh")))
        tracker.complete("scripts", f"{count} scripts found")
    else:
        tracker.error("scripts", "No scripts found")

    # Check installed slash-command files
    commands_dir = project_path / ".claude" / "commands"
    expected_commands = {
        "vision", "tech-stack", "architecture", "roadmap", "specify",
        "plan", "tasks", "clarify", "review", "trace", "constitution",
    }
    if commands_dir.is_dir():
        found = {
            f.stem for f in commands_dir.glob("*.md")
        }
        missing = sorted(expected_commands - found)
        present = len(found & expected_commands)
        if missing:
            tracker.error(
                "commands",
                f"{present}/{len(expected_commands)} found, missing: "
                f"{', '.join(missing)}",
            )
        else:
            tracker.complete(
                "commands",
                f"{present}/{len(expected_commands)} slash commands installed",
            )
    else:
        tracker.error(
            "commands",
            "No .claude/commands/ directory -- run 'csdd integrate claude-vscode'",
        )

    # Check that installed command files are up to date with the bundled
    # templates -- this catches the case where the package was upgraded but
    # `csdd integrate claude-vscode` was never re-run in this project.
    if commands_dir.is_dir():
        from claude_sdd_cli.integrations.claude_vscode import (
            ClaudeVSCodeIntegration,
        )

        integration = ClaudeVSCodeIntegration()
        stale = _stale_command_files(integration, commands_dir)
        if stale:
            tracker.error(
                "commands_fresh",
                f"{len(stale)} file(s) drifted from bundled templates "
                f"({', '.join(sorted(stale))}). Run "
                "'csdd integrate claude-vscode' to refresh.",
            )
        else:
            tracker.complete("commands_fresh", "Matches bundled templates")
    else:
        tracker.skip("commands_fresh", "No commands installed yet")

    # Check CLAUDE.md
    if (project_path / "CLAUDE.md").is_file():
        tracker.complete("claude_md", "Found")
    else:
        tracker.error("claude_md", "CLAUDE.md missing -- run 'csdd integrate claude-vscode'")

    # Warn about legacy Copilot-era paths
    legacy_paths = [
        project_path / ".github" / "skills",
        project_path / ".github" / "copilot-instructions.md",
    ]
    legacy_present = [p for p in legacy_paths if p.exists()]
    if legacy_present:
        rels = ", ".join(
            str(p.relative_to(project_path)) for p in legacy_present
        )
        tracker.error(
            "legacy",
            f"Found stale: {rels}. Safe to delete (Claude Code does not read them).",
        )
    else:
        tracker.complete("legacy", "Clean")

    # Check git
    if is_git_repo(project_path):
        tracker.complete("git", "Available")
    else:
        tracker.skip("git", "Not a git repository")

    console.print(tracker.render())

    # Hint after the check report
    if commands_dir.is_dir() and not any(commands_dir.glob("*.md")):
        console.print()
        console.print(
            "[yellow]No slash-command files found.[/yellow] Run "
            "[cyan]csdd integrate claude-vscode[/cyan] to install them, then "
            "reload VS Code."
        )


def _stale_command_files(integration, installed_dir: Path) -> set[str]:
    """Return command-name stems whose installed content differs from bundled.

    A drift means the package was upgraded but the project never re-ran
    `csdd integrate claude-vscode`, so the user sees old command behavior.
    """
    stale: set[str] = set()
    templates = {p.stem: p for p in integration.list_command_templates()}
    for name, src in templates.items():
        installed = installed_dir / f"{name}.md"
        if not installed.is_file():
            continue
        try:
            if src.read_bytes() != installed.read_bytes():
                stale.add(name)
        except OSError:
            stale.add(name)
    return stale


@app.command()
def version():
    """Display version information."""
    console.print(f"[bold]csdd[/bold] v{__version__}")
    console.print("[dim]Claude SDD -- Specification-Driven Development CLI[/dim]")


def main():
    """Entry point for the CLI."""
    app()
