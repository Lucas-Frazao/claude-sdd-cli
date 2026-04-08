"""Copilot integration -- GitHub Copilot in VS Code.

Copilot has several unique behaviors:
- Skills use ``SKILL.md`` inside ``.github/skills/<name>/`` directories
- Each skill becomes a ``/<name>`` slash command in Copilot Chat
- Installs ``.vscode/settings.json`` with prompt file recommendations
- Context file lives at ``.github/copilot-instructions.md``
"""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path
from typing import Any


class CopilotIntegration:
    """Integration for GitHub Copilot in VS Code."""

    key = "copilot"
    config = {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "commands_subdir": "skills",
        "install_url": None,
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".github/skills",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": "SKILL.md",
    }
    context_file = ".github/copilot-instructions.md"

    def _locate_skill_templates_dir(self) -> Path | None:
        """Find the skill templates directory.

        Checks for bundled core_pack first (wheel install), then falls back
        to the source repo templates/skills/ directory.
        """
        # Check for bundled core_pack (wheel install)
        core_pack = Path(__file__).parent.parent / "core_pack" / "skills"
        if core_pack.is_dir():
            return core_pack

        # Fallback to source repo
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        source_skills = repo_root / "templates" / "skills"
        if source_skills.is_dir():
            return source_skills

        return None

    def _locate_commands_dir(self) -> Path | None:
        """Find the command templates directory (legacy, for backwards compat).

        Checks for bundled core_pack first (wheel install), then falls back
        to the source repo templates/commands/ directory.
        """
        # Check for bundled core_pack (wheel install)
        core_pack = Path(__file__).parent.parent / "core_pack" / "commands"
        if core_pack.is_dir():
            return core_pack

        # Fallback to source repo
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

    def list_skill_templates(self) -> list[Path]:
        """Return sorted list of skill template directories."""
        skills_dir = self._locate_skill_templates_dir()
        if not skills_dir:
            return []
        return sorted(
            d for d in skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        )

    def list_command_templates(self) -> list[Path]:
        """Return sorted list of command template files (legacy)."""
        commands_dir = self._locate_commands_dir()
        if not commands_dir:
            return []
        return sorted(commands_dir.glob("*.md"))

    def setup(
        self,
        project_root: Path,
        **opts: Any,
    ) -> list[Path]:
        """Install copilot skills, VS Code settings, and copilot instructions.

        Reads skill templates (SKILL.md directories), copies them to
        .github/skills/<name>/SKILL.md, then adds VS Code settings and
        copilot-instructions.md.
        """
        created: list[Path] = []

        # 1. Install skills from skill templates
        skill_templates = self.list_skill_templates()
        if skill_templates:
            created.extend(self._install_skills(project_root, skill_templates))

        # 2. Write .vscode/settings.json
        settings_src = self._vscode_settings_path()
        if settings_src and settings_src.is_file():
            dst_settings = project_root / ".vscode" / "settings.json"
            dst_settings.parent.mkdir(parents=True, exist_ok=True)
            if dst_settings.exists():
                self._merge_vscode_settings(settings_src, dst_settings)
            else:
                shutil.copy2(settings_src, dst_settings)
                created.append(dst_settings)

        # 3. Write copilot-instructions.md
        context_path = project_root / self.context_file
        context_path.parent.mkdir(parents=True, exist_ok=True)
        if not context_path.exists():
            context_path.write_text(
                self._generate_copilot_instructions(project_root),
                encoding="utf-8",
            )
            created.append(context_path)

        return created

    def _install_skills(
        self, project_root: Path, skill_templates: list[Path]
    ) -> list[Path]:
        """Copy skill template directories to .github/skills/."""
        dest = project_root / self.registrar_config["dir"]
        dest.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []

        for skill_dir in skill_templates:
            skill_name = skill_dir.name
            dst_skill_dir = dest / skill_name
            dst_skill_dir.mkdir(parents=True, exist_ok=True)

            # Copy all files in the skill directory
            for src_file in skill_dir.iterdir():
                if src_file.is_file():
                    dst_file = dst_skill_dir / src_file.name
                    shutil.copy2(src_file, dst_file)
                    created.append(dst_file)

        return created

    def _vscode_settings_path(self) -> Path | None:
        """Return path to the bundled vscode-settings.json template."""
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
    def _generate_copilot_instructions(project_root: Path) -> str:
        """Generate copilot-instructions.md content."""
        project_name = project_root.name
        return f"""# Copilot Instructions -- {project_name}

This project follows **Claude SDD (Specification-Driven Development)**.

## Core Principle: Copilot Plans, Claude CLI Codes

You (the AI assistant) are a **planning copilot**. You help the developer think
through requirements, identify ambiguity, structure plans, and review work.
Implementation tasks are sent to Claude CLI.

**You MUST NOT generate any executable code.** This includes:
- No code in any programming language
- No code fences with implementation content
- No shell commands or scripts
- No configuration files (Dockerfiles, CI/CD, etc.)
- No copy-paste-ready snippets

**You MAY produce:**
- Prose descriptions and explanations
- Markdown tables and checklists
- Structured specifications and plans
- Task breakdowns with requirement traceability
- Review reports and gap analyses

## Workflow

The recommended workflow is:

1. `/csdd-constitution` -- Define project principles (done during init)
2. `/csdd-vision` -- Define the product vision
3. `/csdd-tech-stack` -- Define the technology stack
4. `/csdd-architecture` -- Define the application architecture
5. `/csdd-roadmap` -- Define ALL features needed to realize the product
6. For EACH feature from the roadmap:
   - `/csdd-specify` -- Create a feature specification
   - `/csdd-clarify` -- Find ambiguity and contradictions
   - `/csdd-plan` -- Generate a technical planning package
   - `/csdd-tasks` -- Create a human execution checklist
   - CLAUDE CLI IMPLEMENTS the feature
   - `/csdd-review` -- Compare implementation against spec
   - `/csdd-trace` -- Map requirements to tasks

## Available Skills (Slash Commands)

Type `/` in Copilot Chat and select a skill:

- `/csdd-vision` -- Define the product vision (what, who, why)
- `/csdd-tech-stack` -- Define the technology stack (languages, frameworks, databases, tooling)
- `/csdd-architecture` -- Define the application architecture (structure, layers, components)
- `/csdd-roadmap` -- Define ALL features needed to realize the product
- `/csdd-specify` -- Create a feature specification from a natural language description
- `/csdd-plan` -- Generate a technical planning package (prose only)
- `/csdd-tasks` -- Create a human execution checklist
- `/csdd-clarify` -- Find ambiguity and contradictions in specs
- `/csdd-review` -- Compare implementation against spec
- `/csdd-trace` -- Map requirements to tasks and check coverage
- `/csdd-constitution` -- Create or update the project constitution

## Project Structure

- `.csdd/memory/constitution.md` -- Project constitution (8 articles)
- `.csdd/memory/product-vision.md` -- Product vision document
- `.csdd/memory/tech-stack.md` -- Technology stack decisions
- `.csdd/memory/architecture.md` -- Application architecture
- `.csdd/memory/feature-roadmap.md` -- Feature roadmap
- `.csdd/templates/` -- Markdown templates for specs, plans, tasks, etc.
- `specs/` -- Feature specifications and planning artifacts
- `.github/skills/` -- Copilot skill files (slash commands)

## The 8 Articles

1. Specification-First Principle
2. Claude CLI Implementation Mandate
3. AI Planning-Only Mandate
4. Ambiguity Marking Requirement
5. Traceability Requirement
6. Review-Before-Regeneration Principle
7. No Executable Planning AI Output Rule
8. Transparency and Auditability
"""
