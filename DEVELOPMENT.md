# Development Guide

## Prerequisites

- Python 3.10 or later
- pip

## Setup

Clone the repository and install in editable mode with dev dependencies:

```
git clone https://github.com/frazaluc/claude-sdd-cli.git
cd claude-sdd-cli
pip install -e ".[dev]"
```

## Running Tests

```
pytest
```

With coverage:

```
pytest --cov=claude_sdd_cli --cov-report=term-missing
```

## Project Layout

```
src/claude_sdd_cli/
├── __init__.py          # Package metadata and version
├── cli/
│   └── main.py          # Click CLI entry point and command registration
├── commands/
│   ├── init_cmd.py      # sdd init
│   ├── specify_cmd.py   # sdd specify
│   ├── plan_cmd.py      # sdd plan
│   ├── tasks_cmd.py     # sdd tasks
│   ├── review_cmd.py    # sdd review
│   ├── clarify_cmd.py   # sdd clarify
│   └── trace_cmd.py     # sdd trace
├── ai/
│   └── __init__.py      # LLM orchestration, system prompt, audit trail
├── templates/
│   └── __init__.py      # Template loading, population, and copying
├── validators/
│   └── __init__.py      # No-code detection (regex + heuristic scanning)
├── parsers/
│   └── __init__.py      # Markdown artifact parsing (requirements, tasks)
├── tracing/
│   └── __init__.py      # Requirement-to-task traceability engine
└── review/
    └── __init__.py      # Review prompt construction from planning artifacts
```

## Architecture Decisions

### Separation of layers

Each internal module has a single responsibility:

- **CLI layer** (`cli/`, `commands/`) -- User interaction via Click. No business logic.
- **AI layer** (`ai/`) -- Prompt construction, LLM calls, constitution enforcement.
- **Validation layer** (`validators/`) -- Stateless code detection. No I/O.
- **Document layer** (`templates/`, `parsers/`) -- Reading and writing Markdown.
- **Tracing layer** (`tracing/`) -- Cross-artifact analysis.
- **Review layer** (`review/`) -- Prompt assembly for spec compliance reviews.

### Why Click?

Click provides declarative command definitions, built-in `--help`, option parsing, and prompt support. It keeps the CLI layer thin.

### Why Rich?

Rich provides styled console output (panels, tables, colored text) without external terminal dependencies.

### No-code validator design

The validator is intentionally conservative:

- **Fenced code blocks** with language tags are always errors.
- **Executable line patterns** (imports, function defs, etc.) are errors.
- **Config fragments** are errors in strict mode, warnings in lenient mode.
- **Unlabeled code fences** are allowed -- they are commonly used for prose formatting.

False positives are expected and should be fixed by tightening regex patterns, not by weakening the validator.

## Adding a New Command

1. Create `src/claude_sdd_cli/commands/your_cmd.py` with a `@click.command()` function.
2. Import and register it in `src/claude_sdd_cli/cli/main.py`.
3. Add tests in `tests/test_cli.py`.

## Adding Validator Patterns

1. Add a new regex tuple to `_EXECUTABLE_PATTERNS` or `_CONFIG_PATTERNS` in `validators/__init__.py`.
2. Add a test case in `tests/test_validators.py`.
3. Watch for false positives against natural English prose.
