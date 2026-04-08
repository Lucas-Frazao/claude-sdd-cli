# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] -- 2026-04-08

### Changed

- Transformed from human-sdd-cli to claude-sdd-cli: AI plans via Copilot, Claude CLI implements

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
