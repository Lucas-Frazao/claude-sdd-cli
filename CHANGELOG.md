# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **`/vision` and other slash commands now actually work in the Claude VS Code extension.** The previous release installed slash commands to `.github/skills/<name>/SKILL.md`, which is the GitHub Copilot Agent Skills convention — the Claude Code VS Code extension does not read that path. Commands are now installed to `.claude/commands/<name>.md`, the canonical Claude Code project-commands directory. Each markdown file becomes a `/<name>` slash command in the chat panel.

### ⚠ BREAKING CHANGES

- **Slash-command installation path changed** from `.github/skills/<name>/SKILL.md` to `.claude/commands/<name>.md`. After upgrading, re-run `csdd integrate claude-vscode` from the project root. The old `.github/skills/` and `.github/copilot-instructions.md` files can then be deleted manually.
- **Project context file renamed** from `.github/copilot-instructions.md` to `CLAUDE.md` (the canonical Claude Code context file). The new file is written at the project root.
- **GitHub Copilot support removed.** The `copilot` AI assistant key, the `CopilotIntegration` class, the `templates/skills/` directory, and the GitHub Copilot Agent Skill frontmatter (`handoffs:`, `scripts:`) have been removed. Only Claude in the VS Code extension is supported (`--ai claude-vscode`).
- **Command frontmatter cleaned up** to the Claude Code standard: `description` (one-line picker hint) and `argument-hint` (placeholder for the input). Copilot-specific `handoffs:` and `scripts:` blocks have been stripped.

### Changed

- `csdd init` and `csdd integrate claude-vscode` now install `.claude/commands/<name>.md` slash-command files and write `CLAUDE.md` at the project root.
- `csdd check` looks for slash commands under `.claude/commands/` and verifies all 11 expected commands are present.
- `README.md`, project-structure docs, and generated `CLAUDE.md` content updated to reflect the Claude-only positioning.
- `pyproject.toml` keywords drop `copilot` and add `vscode`.

## [0.2.0] -- 2026-04-08

### Changed

- Transformed from human-sdd-cli to claude-sdd-cli (early release; superseded by the slash-command pivot in 0.3.0).

## [0.1.0] -- 2026-04-05

### Added

- **CLI framework** with 7 commands: `init`, `specify`, `plan`, `tasks`, `review`, `clarify`, `trace`.
- **No-code validator** with regex and heuristic detection for code fences (20+ language tags), executable patterns (Python, JS, Rust, Go, SQL, Dockerfile), and config fragments.
- **AI orchestration layer** with constitution-enforced system prompt, OpenAI integration, and audit trail (JSONL).
- **Template system** with 6 reusable Markdown templates: spec, plan, tasks, constitution, review, research.
- **Traceability engine** that maps requirements to tasks and calculates coverage percentage.
- **Requirement and task parsers** for structured Markdown artifacts.
- **Review layer** that builds spec-compliance review prompts from planning artifacts.
- **Offline mode** (`--no-ai` flag) for all AI-powered commands.
- **Project constitution** with 8 articles encoding human-authorship and planning-only rules.
- **Documentation**: README, philosophy, workflow, contributing guide, code of conduct, security policy.
- **Test suite**: 41 tests covering validators, parsers, tracing, and CLI commands.
- **Example project**: sample spec for a task timer feature.
