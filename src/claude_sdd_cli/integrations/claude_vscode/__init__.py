"""Claude VS Code extension integration.

The Claude Code VS Code extension discovers project-scoped slash commands from
``.claude/commands/<name>.md``. Each markdown file becomes a ``/<name>`` slash
command in the chat panel. The first line of the YAML frontmatter
(``description``) is what the picker shows.

Project-level context that Claude should always load is written to
``CLAUDE.md`` in the project root — the canonical Claude Code context file.

The integration also writes ``.vscode/settings.json`` with chat-tooling
recommendations.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

EXPECTED_COMMANDS: tuple[str, ...] = (
    "vision",
    "tech-stack",
    "architecture",
    "roadmap",
    "specify",
    "plan",
    "tasks",
    "clarify",
    "review",
    "trace",
    "constitution",
)


class ClaudeVSCodeIntegration:
    """Install Claude-VS-Code slash commands and project context."""

    key = "claude-vscode"
    config = {
        "name": "Claude (VS Code extension)",
        "commands_dir": ".claude/commands",
        "context_file": "CLAUDE.md",
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".claude/commands",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = "CLAUDE.md"

    def _locate_commands_dir(self) -> Path | None:
        """Find the command templates directory.

        Checks for bundled ``core_pack`` first (wheel install), then falls
        back to the source repo ``templates/commands/`` directory.
        """
        core_pack = Path(__file__).parent.parent / "core_pack" / "commands"
        if core_pack.is_dir():
            return core_pack

        repo_root = Path(__file__).parent.parent.parent.parent.parent
        source_commands = repo_root / "templates" / "commands"
        if source_commands.is_dir():
            return source_commands

        return None

    def _locate_templates_dir(self) -> Path | None:
        """Find the templates directory (for vscode-settings.json etc)."""
        core_pack = Path(__file__).parent.parent / "core_pack" / "templates"
        if core_pack.is_dir():
            return core_pack

        repo_root = Path(__file__).parent.parent.parent.parent.parent
        source_templates = repo_root / "templates"
        if source_templates.is_dir():
            return source_templates

        return None

    def list_command_templates(self) -> list[Path]:
        """Return sorted list of command template ``.md`` files."""
        commands_dir = self._locate_commands_dir()
        if not commands_dir:
            return []
        return sorted(commands_dir.glob("*.md"))

    def setup(
        self,
        project_root: Path,
        **opts: Any,
    ) -> list[Path]:
        """Install slash-command files, VS Code settings, and CLAUDE.md.

        Reads command templates from ``templates/commands/`` and copies each
        ``<name>.md`` to ``.claude/commands/<name>.md`` in the project.
        """
        created: list[Path] = []

        command_templates = self.list_command_templates()
        if command_templates:
            created.extend(self._install_commands(project_root, command_templates))

        settings_src = self._vscode_settings_path()
        if settings_src and settings_src.is_file():
            dst_settings = project_root / ".vscode" / "settings.json"
            dst_settings.parent.mkdir(parents=True, exist_ok=True)
            if dst_settings.exists():
                self._merge_vscode_settings(settings_src, dst_settings)
            else:
                shutil.copy2(settings_src, dst_settings)
                created.append(dst_settings)

        context_path = project_root / self.context_file
        if not context_path.exists():
            context_path.write_text(
                self._generate_claude_md(project_root),
                encoding="utf-8",
            )
            created.append(context_path)

        return created

    def _install_commands(
        self, project_root: Path, command_templates: list[Path]
    ) -> list[Path]:
        """Copy ``<name>.md`` files into ``.claude/commands/``."""
        dest = project_root / self.registrar_config["dir"]
        dest.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []

        for src_file in command_templates:
            dst_file = dest / src_file.name
            shutil.copy2(src_file, dst_file)
            created.append(dst_file)

        return created

    def _vscode_settings_path(self) -> Path | None:
        tpl_dir = self._locate_templates_dir()
        if tpl_dir:
            candidate = tpl_dir / "vscode-settings.json"
            if candidate.is_file():
                return candidate
        return None

    @staticmethod
    def _merge_vscode_settings(src: Path, dst: Path) -> None:
        """Merge settings from *src* into existing *dst* JSON file.

        Top-level keys from *src* are added only if missing in *dst*.
        For dict-valued keys, sub-keys are merged the same way.
        """
        try:
            existing = json.loads(dst.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        new_settings = json.loads(src.read_text(encoding="utf-8"))

        if not isinstance(existing, dict) or not isinstance(new_settings, dict):
            return

        changed = False
        for key, value in new_settings.items():
            if key not in existing:
                existing[key] = value
                changed = True
            elif isinstance(existing[key], dict) and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in existing[key]:
                        existing[key][sub_key] = sub_value
                        changed = True

        if not changed:
            return

        dst.write_text(
            json.dumps(existing, indent=4) + "\n", encoding="utf-8"
        )

    @staticmethod
    def _generate_claude_md(project_root: Path) -> str:
        """Generate the CLAUDE.md project-context file."""
        project_name = project_root.name
        return f"""# CLAUDE.md — {project_name}

This project follows **Claude SDD (Specification-Driven Development)** and is
intended for use with **Claude in the VS Code extension**. Each
`.claude/commands/<name>.md` file becomes a `/<name>` slash command in the
Claude chat panel.

## Core Principle: Claude Plans, You Implement

You (Claude) are a **planning assistant**. You help the developer think
through requirements, identify ambiguity, structure plans, and review work.
**The human writes all implementation code.**

**You MUST NOT generate any executable code.** This includes:
- No code in any programming language
- No code fences with implementation content
- No shell commands or scripts
- No configuration files (Dockerfiles, CI/CD, etc.)
- No copy-paste-ready snippets
- No patches or diffs

**You MAY produce:**
- Prose descriptions and explanations
- Markdown tables and checklists
- Structured specifications, plans, and acceptance criteria
- Task breakdowns with requirement traceability and file paths (WHAT and WHERE, not HOW)
- Review reports and gap analyses (as follow-up tasks, never patches)

## Workflow

1. `/constitution` — Define project principles (done during init)
2. `/vision` — Define the product vision
3. `/tech-stack` — Define the technology stack
4. `/architecture` — Define the application architecture
5. `/roadmap` — Define ALL features needed to realize the product
6. For EACH feature from the roadmap:
   - `/specify` — Create a feature specification
   - `/clarify` — Find ambiguity and contradictions
   - `/plan` — Generate a technical planning package (prose only)
   - `/tasks` — Create a human implementation checklist
   - THE HUMAN IMPLEMENTS the feature by hand
   - `/review` — Compare implementation against spec
   - `/trace` — Map requirements to tasks

## Available Slash Commands

Type `/` in the Claude chat panel to discover these commands:

- `/vision` — Define the product vision (what, who, why)
- `/tech-stack` — Define the technology stack (languages, frameworks, databases, tooling)
- `/architecture` — Define the application architecture (structure, layers, components)
- `/roadmap` — Define ALL features needed to realize the product
- `/specify` — Create a feature specification from a natural language description
- `/plan` — Generate a technical planning package (prose only)
- `/tasks` — Create a human implementation checklist
- `/clarify` — Find ambiguity and contradictions in specs
- `/review` — Compare implementation against spec
- `/trace` — Map requirements to tasks and check coverage
- `/constitution` — Create or update the project constitution

## Project Structure

- `.csdd/memory/constitution.md` — Project constitution (8 articles)
- `.csdd/memory/product-vision.md` — Product vision document
- `.csdd/memory/tech-stack.md` — Technology stack decisions
- `.csdd/memory/architecture.md` — Application architecture
- `.csdd/memory/feature-roadmap.md` — Feature roadmap
- `.csdd/templates/` — Markdown templates for specs, plans, tasks, etc.
- `specs/` — Feature specifications and planning artifacts
- `.claude/commands/` — Slash-command markdown files (one per command)

## The 8 Articles

1. Specification-First Principle
2. Human Implementation Mandate
3. AI Planning-Only Mandate
4. Ambiguity Marking Requirement
5. Traceability Requirement
6. Review-Before-Regeneration Principle
7. No Executable Planning AI Output Rule
8. Transparency and Auditability
"""
