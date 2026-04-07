"""Tests for CopilotIntegration — verifies agent files are created and failures are loud."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from human_sdd_cli.integrations.copilot import CopilotIntegration


class TestCopilotSetup:
    """Tests for CopilotIntegration.setup()."""

    def test_setup_creates_agent_files(self):
        """setup() must create at least one .agent.md file in .github/agents/."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            # Pre-create the .hsdd structure (as init would)
            (project / ".hsdd" / "memory").mkdir(parents=True)
            (project / ".hsdd" / "templates").mkdir(parents=True)

            created = integration.setup(project)

            agents_dir = project / ".github" / "agents"
            agent_files = list(agents_dir.glob("hsdd.*.agent.md"))
            assert len(agent_files) > 0, "No .agent.md files were created"
            assert len(created) > 0

    def test_setup_creates_prompt_files(self):
        """setup() must create companion .prompt.md files in .github/prompts/."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            integration.setup(project)

            prompts_dir = project / ".github" / "prompts"
            prompt_files = list(prompts_dir.glob("hsdd.*.prompt.md"))
            assert len(prompt_files) > 0, "No .prompt.md files were created"

    def test_setup_creates_copilot_instructions(self):
        """setup() must create .github/copilot-instructions.md."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            integration.setup(project)

            instructions = project / ".github" / "copilot-instructions.md"
            assert instructions.is_file(), "copilot-instructions.md was not created"
            content = instructions.read_text()
            assert "HSDD" in content or "hsdd" in content

    def test_setup_agent_files_have_correct_extension(self):
        """Every agent file must end with .agent.md."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            integration.setup(project)

            agents_dir = project / ".github" / "agents"
            for f in agents_dir.iterdir():
                if f.is_file():
                    assert f.name.endswith(".agent.md"), (
                        f"Agent file {f.name} does not have .agent.md extension"
                    )

    def test_setup_prompt_files_reference_correct_agent(self):
        """Each .prompt.md must contain an 'agent:' frontmatter key matching its filename."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            integration.setup(project)

            prompts_dir = project / ".github" / "prompts"
            for f in prompts_dir.glob("*.prompt.md"):
                content = f.read_text()
                # Filename is like hsdd.constitution.prompt.md
                # Agent name should be hsdd.constitution
                expected_agent = f.name.replace(".prompt.md", "")
                assert f"agent: {expected_agent}" in content, (
                    f"Prompt file {f.name} does not reference agent '{expected_agent}'"
                )

    def test_setup_raises_when_templates_missing(self):
        """setup() must raise FileNotFoundError when command templates cannot be found."""
        integration = CopilotIntegration()

        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            # Patch both locators to return None (simulating broken install)
            with patch.object(integration, "_locate_commands_dir", return_value=None):
                with pytest.raises(FileNotFoundError, match="command templates"):
                    integration.setup(project)

    def test_setup_is_idempotent(self):
        """Running setup() twice should not break anything."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            first_run = integration.setup(project)
            second_run = integration.setup(project)

            # Both should produce files without error
            assert len(first_run) > 0
            assert len(second_run) > 0

    def test_constitution_agent_exists(self):
        """The specific hsdd.constitution.agent.md must be created (the file that triggered this fix)."""
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            integration.setup(project)

            constitution_agent = project / ".github" / "agents" / "hsdd.constitution.agent.md"
            assert constitution_agent.is_file(), (
                "hsdd.constitution.agent.md was not created — "
                "this is the file needed for /hsdd.constitution in Copilot Chat"
            )

    def test_all_expected_agents_created(self):
        """All 10 standard HSDD agent commands must be created."""
        expected_commands = {
            "check-no-code", "clarify", "constitution", "plan",
            "review", "roadmap", "specify", "tasks", "trace", "vision",
        }
        integration = CopilotIntegration()
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".hsdd" / "memory").mkdir(parents=True)

            integration.setup(project)

            agents_dir = project / ".github" / "agents"
            created_commands = set()
            for f in agents_dir.glob("hsdd.*.agent.md"):
                # hsdd.constitution.agent.md -> constitution
                cmd = f.name.replace("hsdd.", "").replace(".agent.md", "")
                created_commands.add(cmd)

            missing = expected_commands - created_commands
            assert not missing, f"Missing agent files for commands: {missing}"
