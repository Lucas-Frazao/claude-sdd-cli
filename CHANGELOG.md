# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### ⚠ BREAKING CHANGES

- **Slash commands renamed without aliases.** `/csdd.<name>` and `/csdd-<name>` no longer exist; the new names are `/<name>` (e.g. `/csdd.vision` → `/vision`, `/csdd.tech-stack` → `/tech-stack`, etc. for all 11 commands).
- **Skill directories renamed.** `.github/skills/csdd-<name>/SKILL.md` is now `.github/skills/<name>/SKILL.md`.
- **Default AI integration key changed** from `copilot` to `claude-vscode` (the `copilot` key is retained as a legacy alias that reuses the same installation mechanism).
- **Migration for existing projects**: re-run `csdd integrate claude-vscode` from the project root to install the new skill layout. The old `.github/skills/csdd-*/` directories can then be deleted manually. Without this step, chat slash commands will continue to use the old names and contradict the updated planning-only prompts.

### Changed

- **Simplified slash-command names**: `/csdd.vision` → `/vision`, `/csdd.tech-stack` → `/tech-stack`, etc. for all 11 commands.
- **VS Code Claude extension focus**: Project is now oriented around Claude in the VS Code extension; AI assistant key is `claude-vscode` (Copilot retained as a legacy option since both share the same `.github/skills/` mechanism).
- **Planning-only, human-implemented**: Constitution Article 2 renamed to "Human Implementation Mandate". All skill prompts, templates, and docs now explicitly forbid code, snippets, patches, and diffs — outputs are prose-only planning material (specs, plans, tasks with acceptance criteria, reviews).
- Updated AI assistant instructions file content to reflect the new naming and the human-implements mandate.
- `pyproject.toml` package description updated to "Claude plans; you implement."

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
