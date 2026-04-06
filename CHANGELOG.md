# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-04-06

### Added

- **GitHub Copilot Chat API** as an AI provider (`--provider copilot`).
- `sdd auth login/status/logout` commands for Copilot authentication via GitHub Device Flow.
- Automatic token caching at `~/.config/human-sdd-cli/copilot-token.json` with secure permissions.
- Token auto-refresh: Copilot tokens (~25 min lifetime) are transparently re-exchanged.
- Provider auto-detection: Copilot token or OpenAI API key detected automatically.
- Project-level configuration via `.sdd/config.toml` and user-level config via `~/.config/human-sdd-cli/config.toml`.
- Configuration precedence: CLI flags > env vars > project config > user config > defaults.
- `--provider/-P` flag on all AI commands (`specify`, `plan`, `tasks`, `review`, `clarify`).

### Changed

- `--model` default is now provider-aware (`gpt-4o-mini` for OpenAI, `gpt-4o` for Copilot).
- `AIOrchestrator` accepts `provider` and `project_root` parameters.
- Version bumped to 0.2.0.

### Dependencies

- Added `requests>=2.28` for GitHub OAuth HTTP calls.
- Added `tomli>=2.0` for config file parsing on Python < 3.11.

## [0.1.0] — 2026-04-05

### Added

- **CLI framework** with 8 commands: `init`, `specify`, `plan`, `tasks`, `review`, `clarify`, `trace`, `check-no-code`.
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
