"""Tests for the Claude VS Code extension integration.

These tests exercise the slash-command installation pipeline that the user
actually relies on: when ``csdd init --ai claude-vscode`` (or ``csdd
integrate claude-vscode``) runs, the project must end up with
``.claude/commands/<name>.md`` files that the Claude Code VS Code extension
can discover as ``/<name>`` slash commands.

The failure these tests are designed to catch is the one reported after
PR #7: ``/vision`` did nothing because the previous integration installed
commands under ``.github/skills/<name>/SKILL.md`` (a GitHub Copilot Agent
Skills convention), which the Claude VS Code extension does not read.
"""

from pathlib import Path

import pytest

from claude_sdd_cli.integrations.claude_vscode import (
    EXPECTED_COMMANDS,
    ClaudeVSCodeIntegration,
)


EXPECTED_SIMPLIFIED_COMMANDS = {
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
}


@pytest.fixture
def integration():
    return ClaudeVSCodeIntegration()


@pytest.fixture
def project_root(tmp_path):
    (tmp_path / ".csdd").mkdir()
    return tmp_path


class TestClaudeVSCodeIntegration:
    """The integration installs slash commands where Claude actually reads them."""

    def test_setup_creates_claude_commands_directory(self, integration, project_root):
        integration.setup(project_root)

        commands_dir = project_root / ".claude" / "commands"
        assert commands_dir.is_dir(), (
            "Claude Code reads slash commands from .claude/commands/ — the "
            "integration must create this directory."
        )

    def test_setup_installs_all_eleven_simplified_commands(
        self, integration, project_root
    ):
        integration.setup(project_root)

        installed = {
            f.stem
            for f in (project_root / ".claude" / "commands").glob("*.md")
        }
        missing = EXPECTED_SIMPLIFIED_COMMANDS - installed
        assert not missing, (
            f"Missing slash-command files: {sorted(missing)}. "
            "Each missing name will silently fail in the Claude chat panel."
        )

    def test_vision_command_file_exists(self, integration, project_root):
        """Regression test for the reported bug: /vision did nothing."""
        integration.setup(project_root)

        vision_md = project_root / ".claude" / "commands" / "vision.md"
        assert vision_md.is_file(), (
            "/vision was broken because .claude/commands/vision.md was never "
            "installed. The Claude VS Code extension discovers slash commands "
            "from .claude/commands/<name>.md; without this file, typing "
            "/vision in the chat panel does nothing."
        )

    def test_vision_command_has_yaml_frontmatter(self, integration, project_root):
        integration.setup(project_root)

        text = (project_root / ".claude" / "commands" / "vision.md").read_text()
        assert text.startswith("---\n"), (
            "Slash-command files must begin with YAML frontmatter so the "
            "Claude picker shows a description."
        )
        assert "description:" in text.split("---", 2)[1]

    def test_command_files_use_arguments_placeholder(
        self, integration, project_root
    ):
        """Each command should accept user input via $ARGUMENTS."""
        integration.setup(project_root)

        for name in EXPECTED_SIMPLIFIED_COMMANDS:
            md = project_root / ".claude" / "commands" / f"{name}.md"
            assert "$ARGUMENTS" in md.read_text(), (
                f"/{name} command file is missing $ARGUMENTS placeholder — "
                "user input typed after the slash command will be lost."
            )

    def test_command_files_do_not_use_copilot_handoffs_frontmatter(
        self, integration, project_root
    ):
        """The Copilot-specific 'handoffs:' frontmatter must be gone.

        It's not part of Claude Code's slash-command spec and signals that
        the file is still in the legacy Copilot Agent Skill format.
        """
        integration.setup(project_root)

        commands_dir = project_root / ".claude" / "commands"
        for md in commands_dir.glob("*.md"):
            text = md.read_text()
            assert "handoffs:" not in text, (
                f"{md.name} still contains Copilot 'handoffs:' frontmatter — "
                "strip it; the Claude extension does not understand it."
            )
            assert "\nscripts:" not in text, (
                f"{md.name} still contains Copilot 'scripts:' frontmatter — "
                "strip it; the Claude extension does not understand it."
            )

    def test_setup_writes_claude_md_at_project_root(self, integration, project_root):
        """Claude Code reads project context from CLAUDE.md, not from
        .github/copilot-instructions.md."""
        integration.setup(project_root)

        assert (project_root / "CLAUDE.md").is_file(), (
            "Claude Code auto-loads CLAUDE.md from the project root; without "
            "it, Claude has no project context."
        )

    def test_setup_does_not_create_legacy_copilot_paths(
        self, integration, project_root
    ):
        """The Copilot/Agent-Skills layout must NOT be created.

        These paths were the cause of /vision not working — they belong to
        GitHub Copilot, not the Claude VS Code extension.
        """
        integration.setup(project_root)

        assert not (project_root / ".github" / "skills").exists(), (
            ".github/skills/ is the Copilot Agent Skills convention and must "
            "not be created by the Claude VS Code integration."
        )
        assert not (
            project_root / ".github" / "copilot-instructions.md"
        ).exists(), (
            "copilot-instructions.md is the Copilot context file; this "
            "project uses CLAUDE.md instead."
        )

    def test_setup_writes_vscode_settings(self, integration, project_root):
        integration.setup(project_root)

        settings = project_root / ".vscode" / "settings.json"
        assert settings.is_file()

    def test_setup_is_idempotent(self, integration, project_root):
        first = integration.setup(project_root)
        first_paths = {p for p in first}
        # Snapshot vision.md content
        vision_md = project_root / ".claude" / "commands" / "vision.md"
        original = vision_md.read_text()

        # Run again — should not error, should not corrupt files
        integration.setup(project_root)
        assert vision_md.read_text() == original
        # All 11 commands still present
        installed = {
            f.stem for f in (project_root / ".claude" / "commands").glob("*.md")
        }
        assert EXPECTED_SIMPLIFIED_COMMANDS.issubset(installed)

    def test_expected_commands_constant_matches_set(self):
        """The integration's EXPECTED_COMMANDS tuple must list all 11
        simplified commands."""
        assert set(EXPECTED_COMMANDS) == EXPECTED_SIMPLIFIED_COMMANDS


class TestCommandTemplates:
    """The shipped command templates are the source of truth."""

    def test_all_simplified_commands_have_a_template_on_disk(self, integration):
        template_files = {p.stem for p in integration.list_command_templates()}
        missing = EXPECTED_SIMPLIFIED_COMMANDS - template_files
        assert not missing, f"Missing command templates: {sorted(missing)}"
