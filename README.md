# Claude SDD CLI

**A specification-driven development CLI where Copilot plans and Claude CLI implements.**

AI plans, Claude codes.

---

## What Is This?

This tool brings spec-driven development to GitHub Copilot with one foundational rule: **AI plans, Claude CLI implements from planning artifacts**. Specifications drive development. AI produces specs, plans, task breakdowns, and reviews -- all in prose. Claude CLI implements everything from the planning artifacts.

The result is a disciplined workflow where every feature starts with a specification, gets planned in prose, becomes a Claude CLI task checklist, and gets reviewed against the spec after Claude CLI builds it.

## Install

```bash
# Install globally via uv
uv tool install claude-sdd-cli --from git+https://github.com/Lucas-Frazao/claude-sdd-cli.git

# Or for development
git clone https://github.com/Lucas-Frazao/claude-sdd-cli.git
cd claude-sdd-cli
uv pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize a project

```bash
csdd init my-project
```

This creates:
- `.csdd/` directory with constitution, templates, and scripts
- `.github/agents/` with Copilot agent commands (`csdd.*.agent.md`)
- `.github/prompts/` with companion prompt files
- `.github/copilot-instructions.md` with project context
- `.vscode/settings.json` with prompt file recommendations

### 2. Open in VS Code with Copilot

Open the project in VS Code and use Copilot Chat with these commands:

| Command | What it does |
|---------|-------------|
| `/csdd.vision` | Define the product vision -- what it is, who it's for, why it matters |
| `/csdd.tech-stack` | Define the technology stack -- languages, frameworks, databases, tooling |
| `/csdd.architecture` | Define the application architecture -- structure, layers, components |
| `/csdd.roadmap` | Define ALL features needed to realize the product vision |
| `/csdd.specify` | Create a feature specification from a natural language description |
| `/csdd.plan` | Generate a technical planning package (prose only, no code) |
| `/csdd.tasks` | Create a Claude CLI execution checklist |
| `/csdd.clarify` | Find ambiguity and contradictions in specs |
| `/csdd.review` | Compare the implementation against the spec |
| `/csdd.trace` | Map requirements to tasks and check coverage |
| `/csdd.check-no-code` | Validate no AI code leaked into artifacts |
| `/csdd.constitution` | Create or update the project constitution |

### 3. The Workflow

```
  /csdd.vision --> /csdd.tech-stack --> /csdd.architecture --> /csdd.roadmap --> For EACH feature:
      /csdd.specify --> /csdd.clarify --> /csdd.plan --> /csdd.tasks --> CLAUDE CLI IMPLEMENTS --> /csdd.review
```

1. **Vision**: Define the product vision -- what it is, who it's for, and why.
2. **Tech Stack**: Define the technology stack -- languages, frameworks, databases, and tooling.
3. **Architecture**: Define the application architecture -- structure, layers, components, and data flow.
4. **Roadmap**: Define ALL features needed to build the product.
5. **For each feature from the roadmap:**
   1. **Specify**: Describe the feature. AI creates a structured spec.
   2. **Clarify**: AI finds ambiguity and contradictions in the spec.
   3. **Plan**: AI generates research, data models, contracts -- all in prose, no code.
   4. **Tasks**: AI creates a sequenced, traceable checklist for Claude CLI.
   5. **Claude CLI Implements**: Claude CLI implements from planning artifacts. That's the point.
   6. **Review**: AI compares the implementation against the spec. Produces follow-up tasks, not patches.

## Project Structure

After `csdd init`, your project looks like:

```
my-project/
├── .csdd/
│   ├── memory/
│   │   ├── constitution.md          # The 8 Articles
│   │   ├── product-vision.md        # Product vision document
│   │   ├── tech-stack.md            # Technology stack decisions
│   │   ├── architecture.md          # Application architecture
│   │   └── feature-roadmap.md       # Feature roadmap
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
│   │   ├── csdd.vision.agent.md
│   │   ├── csdd.tech-stack.agent.md
│   │   ├── csdd.architecture.agent.md
│   │   ├── csdd.roadmap.agent.md
│   │   ├── csdd.specify.agent.md
│   │   ├── csdd.plan.agent.md
│   │   ├── csdd.tasks.agent.md
│   │   ├── csdd.clarify.agent.md
│   │   ├── csdd.review.agent.md
│   │   ├── csdd.trace.agent.md
│   │   ├── csdd.check-no-code.agent.md
│   │   └── csdd.constitution.agent.md
│   ├── prompts/
│   │   ├── csdd.specify.prompt.md
│   │   ├── csdd.plan.prompt.md
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
2. **Claude CLI Implementation** -- Claude CLI implements all code from planning artifacts.
3. **AI Planning-Only** -- AI clarifies, researches, plans, and reviews.
4. **Ambiguity Marking** -- Unclear requirements get `[NEEDS CLARIFICATION]`.
5. **Traceability** -- Tasks map to requirements, reviews map to specs.
6. **Review Over Regeneration** -- Gaps produce follow-up tasks, not code.
7. **No Executable Planning AI Output** -- Code fences and snippets are rejected from planning artifacts.
8. **Transparency** -- Audit trail for all AI interactions.

## CLI Commands

```bash
csdd init <project-name>   # Initialize a new project
csdd init --here            # Initialize in current directory
csdd vision                 # Define the product vision
csdd tech-stack             # Define the technology stack
csdd architecture           # Define the application architecture
csdd roadmap                # Define the feature roadmap
csdd specify                # Create a feature specification
csdd clarify                # Analyze specs for ambiguity
csdd plan                   # Generate a technical plan
csdd tasks                  # Create a Claude CLI execution checklist
csdd review                 # Review implementation against spec
csdd trace                  # Map requirements to tasks
csdd check-no-code          # Validate no AI code in artifacts
csdd integrate copilot      # Re-run Copilot integration
csdd check                  # Verify project setup
csdd version                # Show version
```

## How It Differs from spec-kit

| Area | spec-kit | claude-sdd-cli |
|------|----------|----------------|
| Source of truth | Specification | Specification |
| AI role | Planning + code generation | Planning and review only |
| Code authorship | AI may generate code | Claude CLI implements all code |
| Constitution | Architectural discipline | Same + implementation from planning artifacts mandate |
| Tasks output | Ready for an AI agent | Ready for Claude CLI |
| Output validation | None | No-code validator on every artifact |
| Review model | Regeneration flow | Gap analysis without code fixes |
| Namespace | `speckit.*` | `csdd.*` |

## Why?

Specifications should drive development. When coupled with structured planning artifacts, Claude CLI can implement features with full context -- specifications, data models, contracts, and task breakdowns all guide the implementation.

This tool preserves the strongest idea from SDD -- that specifications should drive development -- while ensuring **structured, traceable implementation from planning artifacts**.

Built for:
- **Solo developers** who want strong planning support with Claude CLI implementation
- **Students** who want to learn architecture and implementation deeply
- **Engineers** who want an auditable, specification-first workflow
- **Teams** experimenting with AI-assisted planning where Claude CLI implements from structured artifacts

## Development

```bash
git clone https://github.com/Lucas-Frazao/claude-sdd-cli.git
cd claude-sdd-cli
uv pip install -e ".[dev]"
pytest
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

This project will not accept contributions that generate executable code or bypass the constitution.

## License

[MIT](LICENSE)
