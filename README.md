# Human-Authored SDD CLI

**A specification-driven development CLI that keeps you as the sole code author.**

AI helps you think — you write every line of code.

---

## What Is This?

This project adapts the spec-first workflow from [spec-kit](https://github.com/github/spec-kit) with one foundational change: **the AI never writes code**. Specifications remain the source of truth. AI produces specs, plans, task breakdowns, and reviews — all in prose. You implement everything yourself.

The result is a disciplined workflow where every feature starts with a specification, gets planned in prose, becomes a human task checklist, and gets reviewed against the spec after you build it.

## Why?

The original SDD philosophy argues that specifications should drive development, not the reverse. That philosophy is powerful. But when coupled with automatic code generation, it can reduce developer understanding, weaken authorship, and hide flawed specs behind AI-produced code.

This tool preserves the strongest idea from SDD — that specifications should drive development — while solving a real concern: **preserving developer understanding and authorship.**

It is designed for:

- **Solo developers** who want strong planning support without AI coding.
- **Students** who want to learn architecture and implementation deeply.
- **Engineers** who want an auditable, specification-first workflow.
- **Teams** experimenting with AI-assisted planning but with strict code authorship rules.

## Quick Start

### Install

```
pip install -e .
```

### Initialize a project

```
sdd init --name "my-project"
```

This creates your workspace with templates, a constitution, and documentation.

### Specify a feature

```
sdd specify --idea "User authentication with email and password"
```

The AI helps write a structured spec. Ambiguity gets marked with `[NEEDS CLARIFICATION]` instead of guessed.

### Generate a plan

```
sdd plan --feature 001-user-authentication
```

Produces `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` — all in prose.

### Create a task checklist

```
sdd tasks --feature 001-user-authentication
```

A sequenced, traceable implementation checklist for you, the human developer.

### Implement everything yourself

This is the whole point. The CLI does not help here.

### Review your work against the spec

```
sdd review --feature 001-user-authentication --notes "Implemented login and signup endpoints"
```

### Check traceability

```
sdd trace --feature 001-user-authentication
```

### Validate no AI-generated code leaked in

```
sdd check-no-code --feature 001-user-authentication
```

### Find ambiguity

```
sdd clarify --feature 001-user-authentication
```

## Commands

| Command | Purpose |
|---------|---------|
| `sdd init` | Initialize workspace with templates and constitution |
| `sdd specify` | Turn an idea into a structured specification |
| `sdd plan` | Generate a technical planning package (prose only) |
| `sdd tasks` | Create a human implementation checklist |
| `sdd review` | Compare your implementation against the spec |
| `sdd clarify` | Find ambiguity and contradictions in docs |
| `sdd trace` | Map requirements to tasks and check coverage |
| `sdd check-no-code` | Validate artifacts contain no executable code |
| `sdd auth login` | Authenticate with GitHub Copilot |
| `sdd auth status` | Show current authentication status |
| `sdd auth logout` | Remove stored Copilot credentials |

Every AI-powered command supports `--no-ai` for offline use.

## The Constitution

Every project initialized with `sdd init` gets a constitution with these articles:

1. **Specification-First** — Specs before code.
2. **Human Authorship** — You write all executable artifacts.
3. **AI Planning-Only** — AI clarifies, researches, plans, and reviews.
4. **Ambiguity Marking** — Unclear requirements get `[NEEDS CLARIFICATION]`.
5. **Traceability** — Tasks map to requirements, reviews map to specs.
6. **Review Over Regeneration** — Gaps produce follow-up tasks, not code.
7. **No Executable AI Output** — Code fences and snippets are rejected.
8. **Transparency** — Audit trail for all AI interactions.

## Workflow

```
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │   Init   │────▶│ Specify  │────▶│   Plan   │────▶│  Tasks   │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                           │
                                                           ▼
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Trace   │◀────│  Review  │◀────│  YOU     │◀────│ Implement│
  └──────────┘     └──────────┘     │  CODE    │     └──────────┘
                                    └──────────┘
```

## Project Structure

```
your-project/
├── .sdd                         # Marker file
├── docs/
│   ├── constitution.md          # Project rules
│   ├── philosophy.md            # Why this workflow exists
│   └── workflow.md              # How to use it
├── templates/                   # Reusable Markdown templates
│   ├── spec-template.md
│   ├── plan-template.md
│   ├── tasks-template.md
│   ├── constitution-template.md
│   ├── review-template.md
│   └── research-template.md
└── specs/
    └── 001-feature-name/
        ├── spec.md              # Specification
        ├── plan.md              # Technical plan (prose)
        ├── research.md          # Trade-offs and context
        ├── data-model.md        # Entities described in prose
        ├── quickstart.md        # Validation scenarios
        ├── tasks.md             # Human checklist
        ├── review.md            # Spec compliance review
        ├── traceability.md      # Requirement coverage report
        └── contracts/           # Interface contracts (prose)
```

## Configuration

### OpenAI (default)

Set your OpenAI API key:

```
export OPENAI_API_KEY="sk-..."
```

### GitHub Copilot as AI Provider

If you have a GitHub Copilot subscription, you can use it instead of an OpenAI API key.

**Prerequisites:**
- A GitHub account with an active Copilot subscription (Individual, Business, or Enterprise).

**Quick start:**

```
sdd auth login
```

This opens your browser for GitHub device flow authentication. Enter the displayed code, authorize, and you're set.

Once authenticated, all AI commands automatically use the Copilot provider:

```
sdd specify --idea "User authentication with OAuth"
sdd plan --feature 001-user-auth
```

Check your auth status or log out:

```
sdd auth status
sdd auth logout
```

### Provider Selection

The CLI auto-detects the provider: if `OPENAI_API_KEY` is set, it uses OpenAI; if a cached Copilot token exists, it uses Copilot. Override with:

```
sdd specify --idea "my feature" --provider copilot
sdd specify --idea "my feature" --provider openai
```

Or set it via environment variable:

```
export SDD_PROVIDER=copilot
```

Or in a project config file `.sdd/config.toml`:

```
[ai]
provider = "copilot"
default_model = "gpt-4o"
```

### Model Selection

Use a different model:

```
sdd specify --idea "my feature" --model gpt-4o
```

Default models per provider: `gpt-4o-mini` for OpenAI, `gpt-4o` for Copilot.

## No-Code Enforcement

The validator detects:

- **Fenced code blocks** with language tags (Python, JS, Rust, Go, SQL, Bash, and 20+ more)
- **Executable line patterns** (imports, function definitions, class definitions, SQL statements, shell commands)
- **Config fragments** (package.json, pyproject.toml, Dockerfile, Kubernetes, Terraform)
- **Unclosed code blocks**

Every AI response passes through this validator before being saved. Violations are rejected and logged to the audit trail.

## Differentiation from spec-kit

| Area | spec-kit | human-sdd-cli |
|------|----------|----------------|
| Source of truth | Specification | Specification |
| AI role | Planning + code generation | Planning and review only |
| Code authorship | AI may generate code | Human writes all code |
| Constitution | Architectural discipline | Same + human-authorship mandate |
| Tasks output | Ready for an AI agent | Ready for a human developer |
| Output validation | None | No-code validator on every artifact |
| Review model | Regeneration flow | Gap analysis without code fixes |

## Development

```
git clone https://github.com/frazaluc/human-sdd-cli.git
cd human-sdd-cli
pip install -e ".[dev]"
pytest
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for architecture details and contribution patterns.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

This project will not accept contributions that generate executable code or bypass the constitution.

## License

[MIT](LICENSE)
