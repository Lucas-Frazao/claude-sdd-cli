"""End-to-end tests for the ``csdd`` Typer CLI.

These exercise the real ``csdd init --ai claude-vscode`` and
``csdd integrate claude-vscode`` flows and assert that the slash commands
land where the Claude VS Code extension expects to find them.
"""

from pathlib import Path

from typer.testing import CliRunner

from claude_sdd_cli import app


EXPECTED_COMMANDS = {
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


def _invoke(runner, args):
    """Run the csdd app with stdin closed so any interactive prompts skip."""
    return runner.invoke(app, args, input="")


class TestCsddInit:
    def test_init_with_claude_vscode_installs_slash_commands(self, tmp_path):
        runner = CliRunner()
        project = tmp_path / "demo"

        result = _invoke(
            runner,
            ["init", str(project.name), "--ai", "claude-vscode", "--no-git"],
        )

        # Typer changes cwd-relative project resolution; manually verify by
        # walking the tmp_path tree (project_path = cwd / name when name is
        # not '.').
        candidate = Path.cwd() / project.name
        # The CLI resolves project_path = Path.cwd() / project_name, so the
        # project is created under the runner's cwd. Locate it.
        if not candidate.exists():
            candidate = project

        assert result.exit_code == 0, result.output

        commands_dir = candidate / ".claude" / "commands"
        try:
            assert commands_dir.is_dir(), (
                f"Expected {commands_dir} to exist after csdd init. "
                f"Output:\n{result.output}"
            )
            installed = {f.stem for f in commands_dir.glob("*.md")}
            missing = EXPECTED_COMMANDS - installed
            assert not missing, f"Missing commands: {sorted(missing)}"
            assert (candidate / "CLAUDE.md").is_file()
        finally:
            # Cleanup the project created in the runner cwd
            import shutil
            if candidate.exists() and candidate != project:
                shutil.rmtree(candidate, ignore_errors=True)

    def test_init_rejects_unknown_ai_value(self, tmp_path):
        runner = CliRunner()

        result = _invoke(
            runner,
            ["init", "demo-bad", "--ai", "copilot", "--no-git"],
        )

        assert result.exit_code != 0
        assert "Unknown AI assistant" in result.output or "copilot" in result.output


class TestCsddIntegrate:
    def test_integrate_claude_vscode_installs_slash_commands(self, tmp_path, monkeypatch):
        runner = CliRunner()
        # An existing project that has the .csdd marker
        (tmp_path / ".csdd").mkdir()

        monkeypatch.chdir(tmp_path)
        result = _invoke(runner, ["integrate", "claude-vscode"])

        assert result.exit_code == 0, result.output

        commands_dir = tmp_path / ".claude" / "commands"
        assert commands_dir.is_dir()
        installed = {f.stem for f in commands_dir.glob("*.md")}
        assert EXPECTED_COMMANDS.issubset(installed)
        assert (tmp_path / "CLAUDE.md").is_file()

    def test_integrate_rejects_copilot(self, tmp_path, monkeypatch):
        runner = CliRunner()
        (tmp_path / ".csdd").mkdir()
        monkeypatch.chdir(tmp_path)

        result = _invoke(runner, ["integrate", "copilot"])

        assert result.exit_code != 0
        assert "Unknown" in result.output or "claude-vscode" in result.output


class TestCsddCheck:
    def test_check_reports_all_commands_when_installed(self, tmp_path, monkeypatch):
        runner = CliRunner()
        # Build a project that has slash commands installed
        (tmp_path / ".csdd").mkdir()
        monkeypatch.chdir(tmp_path)
        _invoke(runner, ["integrate", "claude-vscode"])

        result = _invoke(runner, ["check"])

        assert result.exit_code == 0
        # The check command should mention 11 commands or that they're installed
        assert "11" in result.output or "slash commands installed" in result.output

    def test_check_flags_missing_commands(self, tmp_path, monkeypatch):
        runner = CliRunner()
        (tmp_path / ".csdd").mkdir()
        # Create an incomplete .claude/commands/ -- only vision.md
        commands = tmp_path / ".claude" / "commands"
        commands.mkdir(parents=True)
        (commands / "vision.md").write_text("---\ndescription: test\n---\n")
        monkeypatch.chdir(tmp_path)

        result = _invoke(runner, ["check"])

        # check should mention the missing commands
        assert "missing" in result.output.lower() or "trace" in result.output

    def test_check_flags_stale_command_file_content(self, tmp_path, monkeypatch):
        """A drifted vision.md (older bundled content) must be flagged.

        Reproduces the upgrade scenario: package upgraded, but the project
        still has the old slash-command files because ``csdd integrate`` was
        not re-run.
        """
        runner = CliRunner()
        (tmp_path / ".csdd").mkdir()
        monkeypatch.chdir(tmp_path)
        _invoke(runner, ["integrate", "claude-vscode"])

        vision_md = tmp_path / ".claude" / "commands" / "vision.md"
        vision_md.write_text(
            "---\ndescription: stale old content\n---\n\nold body $ARGUMENTS\n"
        )

        result = _invoke(runner, ["check"])
        assert "drifted" in result.output or "refresh" in result.output

    def test_check_flags_legacy_copilot_paths(self, tmp_path, monkeypatch):
        runner = CliRunner()
        (tmp_path / ".csdd").mkdir()
        (tmp_path / ".github" / "skills").mkdir(parents=True)
        (tmp_path / ".github" / "copilot-instructions.md").write_text("old\n")

        monkeypatch.chdir(tmp_path)
        result = _invoke(runner, ["check"])

        assert ".github/skills" in result.output or "stale" in result.output.lower()

    def test_integrate_prints_reload_instruction(self, tmp_path, monkeypatch):
        runner = CliRunner()
        (tmp_path / ".csdd").mkdir()
        monkeypatch.chdir(tmp_path)

        result = _invoke(runner, ["integrate", "claude-vscode"])

        assert result.exit_code == 0, result.output
        assert "Reload" in result.output or "reload" in result.output

    def test_integrate_warns_about_legacy_paths(self, tmp_path, monkeypatch):
        runner = CliRunner()
        (tmp_path / ".csdd").mkdir()
        (tmp_path / ".github" / "skills").mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = _invoke(runner, ["integrate", "claude-vscode"])

        assert ".github/skills" in result.output or "legacy" in result.output.lower()
