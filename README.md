# Human-Authored SDD CLI

**A specification-driven development CLI that keeps you as the sole code author.**

AI plans, you code. Every line.

---

## What Is This?

This tool brings spec-driven development to GitHub Copilot with one foundational rule: **the AI never writes code**. Specifications drive development. AI produces specs, plans, task breakdowns, and reviews -- all in prose. You implement everything yourself.

The result is a disciplined workflow where every feature starts with a specification, gets planned in prose, becomes a human task checklist, and gets reviewed against the spec after you build it.

## Install

```bash
# Install globally via uv
uv tool install human-sdd-cli --from git+https://github.com/Lucas-Frazao/human-sdd-cli.git

# Or for development
git clone https://github.com/Lucas-Frazao/human-sdd-cli.git
cd human-sdd-cli
uv pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize a project

```bash
hsdd init my-project
```

This creates:
- `.hsdd/` directory with constitution, templates, and scripts
- `.github/agents/` with Copilot agent commands (`hsdd.*.agent.md`)
- `.github/prompts/` with companion prompt files
- `.github/copilot-instructions.md` with project context
- `.vscode/settings.json` with prompt file recommendations

### 2. Open in VS Code with Copilot

Open the project in VS Code and use Copilot Chat with these commands:

| Command | What it does |
|---------|-------------|
| `/hsdd.specify` | Create a feature specification from a natural language description |
| `/hsdd.plan` | Generate a technical planning package (prose only, no code) |
| `/hsdd.tasks` | Create a human execution checklist |
| `/hsdd.clarify` | Find ambiguity and contradictions in specs |
| `/hsdd.review` | Compare your implementation against the spec |
| `/hsdd.trace` | Map requirements to tasks and check coverage |
| `/hsdd.check-no-code` | Validate no AI code leaked into artifacts |
| `/hsdd.constitution` | Create or update the project constitution |

### 3. The Workflow

```
  /hsdd.specify ──> /hsdd.plan ──> /hsdd.tasks ──> YOU CODE ──> /hsdd.review ──> /hsdd.trace
```

1. **Specify**: Describe your feature in natural language. AI creates a structured spec.
2. **Plan**: AI generates research, data models, contracts -- all in prose, no code.
3. **Tasks**: AI creates a sequenced, traceable checklist for you.
4. **You Code**: Write every line yourself. That's the point.
5. **Review**: AI compares your implementation against the spec. Produces follow-up tasks, not patches.
6. **Trace**: Verify every requirement has corresponding tasks and implementation.

## Project Structure

After `hsdd init`, your project looks like:

```
my-project/
├── .hsdd/
│   ├── memory/
│   │   └── constitution.md          # The 8 Articles
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── constitution-template.md
│   │   ├── review-template.md
│   │   └── research-template.md
│   ├── scripts/
│   │   └── bash/
│   │       ├── common.sh
│   │       ├── create-new-feature.sh
│   │       └── setup-plan.sh
│   └── init-options.json
├── .github/
│   ├── agents/
│   │   ├── hsdd.specify.agent.md
│   │   ├── hsdd.plan.agent.md
│   │   ├── hsdd.tasks.agent.md
│   │   ├── hsdd.clarify.agent.md
│   │   ├── hsdd.review.agent.md
│   │   ├── hsdd.trace.agent.md
│   │   ├── hsdd.check-no-code.agent.md
│   │   └── hsdd.constitution.agent.md
│   ├── prompts/
│   │   ├── hsdd.specify.prompt.md
│   │   ├── hsdd.plan.prompt.md
│   │   └── ...
│   └── copilot-instructions.md
├── .vscode/
│   └── settings.json
└── specs/
    └── 001-feature-name/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        ├── tasks.md
        ├── review.md
        ├── traceability.md
        └── contracts/
```

## The Constitution

Every project gets a constitution with 8 non-negotiable articles:

1. **Specification-First** -- Specs before code.
2. **Human Authorship** -- You write all executable artifacts.
3. **AI Planning-Only** -- AI clarifies, researches, plans, and reviews.
4. **Ambiguity Marking** -- Unclear requirements get `[NEEDS CLARIFICATION]`.
5. **Traceability** -- Tasks map to requirements, reviews map to specs.
6. **Review Over Regeneration** -- Gaps produce follow-up tasks, not code.
7. **No Executable AI Output** -- Code fences and snippets are rejected.
8. **Transparency** -- Audit trail for all AI interactions.

## CLI Commands

```bash
hsdd init <project-name>   # Initialize a new project
hsdd init --here            # Initialize in current directory
hsdd integrate copilot      # Re-run Copilot integration
hsdd check                  # Verify project setup
hsdd version                # Show version
```

## How It Differs from spec-kit

| Area | spec-kit | human-sdd-cli |
|------|----------|----------------|
| Source of truth | Specification | Specification |
| AI role | Planning + code generation | Planning and review only |
| Code authorship | AI may generate code | Human writes all code |
| Constitution | Architectural discipline | Same + human-authorship mandate |
| Tasks output | Ready for an AI agent | Ready for a human developer |
| Output validation | None | No-code validator on every artifact |
| Review model | Regeneration flow | Gap analysis without code fixes |
| Namespace | `speckit.*` | `hsdd.*` |

## Why?

Specifications should drive development. But when coupled with automatic code generation, AI can reduce developer understanding, weaken authorship, and hide flawed specs behind generated code.

This tool preserves the strongest idea from SDD -- that specifications should drive development -- while ensuring **developer understanding and authorship**.

Built for:
- **Solo developers** who want strong planning support without AI coding
- **Students** who want to learn architecture and implementation deeply
- **Engineers** who want an auditable, specification-first workflow
- **Teams** experimenting with AI-assisted planning with strict code authorship rules

## Development

```bash
git clone https://github.com/Lucas-Frazao/human-sdd-cli.git
cd human-sdd-cli
uv pip install -e ".[dev]"
pytest
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

This project will not accept contributions that generate executable code or bypass the constitution.

## License

[MIT](LICENSE)
