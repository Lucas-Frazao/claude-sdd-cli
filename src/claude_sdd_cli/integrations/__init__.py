"""Integration registry for Claude SDD CLI.

Only the Claude VS Code extension is supported. The previous GitHub Copilot
integration has been removed — this project is exclusively for use with
Claude in the VS Code extension.
"""

from claude_sdd_cli.integrations.claude_vscode import ClaudeVSCodeIntegration

__all__ = ["ClaudeVSCodeIntegration"]
