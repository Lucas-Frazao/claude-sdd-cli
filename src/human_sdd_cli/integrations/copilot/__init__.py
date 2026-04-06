"""Copilot integration -- GitHub Copilot in VS Code.

Copilot has several unique behaviors:
- Commands use ``.agent.md`` extension
- Each command gets a companion ``.prompt.md`` file in ``.github/prompts/``
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
        "commands_subdir": "agents",
        "install_url": None,
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".github/agents",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".agent.md",
    }
    context_file = ".github/copilot-instructions.md"

    def command_filename(self, template_name: str) -> str:
        """Copilot commands use ``.agent.md`` extension."""
        return f"hsdd.{template_name}.agent.md"

    def prompt_filename(self, template_name: str) -> str:
        """Companion prompt file name."""
        return f"hsdd.{template_name}.prompt.md"

    def _locate_commands_dir(self) -> Path | None:
        """Find the command templates directory.

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

    def list_command_templates(self) -> list[Path]:
        """Return sorted list of command template files."""
        commands_dir = self._locate_commands_dir()
        if not commands_dir:
            return []
        return sorted(commands_dir.glob("*.md"))

    def _process_template(self, content: str) -> str:
        """Process a command template for Copilot agent format.

        - Strip script blocks from frontmatter
        - Replace path references to use .hsdd/ prefix
        - Replace {ARGS} with $ARGUMENTS
        """
        # Replace relative path references to use .hsdd/ prefix
        content = re.sub(r'(?m)^(scripts/)', r'.hsdd/scripts/', content)
        content = re.sub(r'(?m)^(templates/)', r'.hsdd/templates/', content)
        content = re.sub(r'(?m)^(memory/)', r'.hsdd/memory/', content)
        content = content.replace('../../memory/', '.hsdd/memory/')
        content = content.replace('../../scripts/', '.hsdd/scripts/')
        content = content.replace('../../templates/', '.hsdd/templates/')

        # Replace {ARGS} placeholder
        content = content.replace('{ARGS}', '$ARGUMENTS')

        return content

    def setup(
        self,
        project_root: Path,
        **opts: Any,
    ) -> list[Path]:
        """Install copilot commands, companion prompts, and VS Code settings.

        Reads command templates, processes them, writes as .agent.md files,
        then adds companion .prompt.md files and VS Code settings.
        """
        templates = self.list_command_templates()
        if not templates:
            return []

        dest = project_root / self.registrar_config["dir"]
        dest.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []

        # 1. Process and write command files as .agent.md
        for src_file in templates:
            raw = src_file.read_text(encoding="utf-8")
            processed = self._process_template(raw)
            dst_name = self.command_filename(src_file.stem)
            dst_file = dest / dst_name
            dst_file.write_text(processed, encoding="utf-8")
            created.append(dst_file)

        # 2. Generate companion .prompt.md files
        prompts_dir = project_root / ".github" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        for src_file in templates:
            cmd_name = f"hsdd.{src_file.stem}"
            prompt_content = f"---\nagent: {cmd_name}\n---\n"
            prompt_file = prompts_dir / f"{cmd_name}.prompt.md"
            prompt_file.write_text(prompt_content, encoding="utf-8")
            created.append(prompt_file)

        # 3. Write .vscode/settings.json
        settings_src = self._vscode_settings_path()
        if settings_src and settings_src.is_file():
            dst_settings = project_root / ".vscode" / "settings.json"
            dst_settings.parent.mkdir(parents=True, exist_ok=True)
            if dst_settings.exists():
                self._merge_vscode_settings(settings_src, dst_settings)
            else:
                shutil.copy2(settings_src, dst_settings)
                created.append(dst_settings)

        # 4. Write copilot-instructions.md
        context_path = project_root / self.context_file
        context_path.parent.mkdir(parents=True, exist_ok=True)
        if not context_path.exists():
            context_path.write_text(
                self._generate_copilot_instructions(project_root),
                encoding="utf-8",
            )
            created.append(context_path)

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

This project follows **Human-Authored Specification-Driven Development (HSDD)**.

## Core Principle: AI Plans, Human Codes

You (the AI assistant) are a **planning copilot**. You help the developer think
through requirements, identify ambiguity, structure plans, and review work.

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

## Available Commands

Use these commands in Copilot Chat:

- `/hsdd.specify` -- Create a feature specification from a natural language description
- `/hsdd.plan` -- Generate a technical planning package (prose only)
- `/hsdd.tasks` -- Create a human execution checklist
- `/hsdd.clarify` -- Find ambiguity and contradictions in specs
- `/hsdd.review` -- Compare implementation against spec
- `/hsdd.trace` -- Map requirements to tasks and check coverage
- `/hsdd.check-no-code` -- Validate no AI code leaked into artifacts
- `/hsdd.constitution` -- Create or update the project constitution

## Project Structure

- `.hsdd/memory/constitution.md` -- Project constitution (8 articles)
- `.hsdd/templates/` -- Markdown templates for specs, plans, tasks, etc.
- `specs/` -- Feature specifications and planning artifacts
- `.github/agents/` -- Copilot agent command files
- `.github/prompts/` -- Companion prompt files

## The 8 Articles

1. Specification-First Principle
2. Human Authorship Mandate
3. AI Planning-Only Mandate
4. Ambiguity Marking Requirement
5. Traceability Requirement
6. Review-Before-Regeneration Principle
7. No Executable AI Output Rule
8. Transparency and Auditability
"""
