# Claude SDD CLI

**A specification-driven development CLI for use with Claude in the VS Code extension. Claude plans; you implement.**

---

## What Is This?

This tool brings spec-driven development to **Claude in the VS Code extension** with one foundational rule: **the AI plans, the human implements**. Specifications drive development. Claude produces specs, plans, task breakdowns, and reviews — all in prose. You write every line of code yourself.

The result is a disciplined workflow where every feature starts with a specification, gets planned in prose, becomes a human-implementation checklist, and gets reviewed against the spec after you build it.

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
- `.claude/commands/<name>.md` — slash-command files (`/vision`, `/plan`, etc.) read by the Claude VS Code extension
- `CLAUDE.md` — project context loaded automatically by Claude
- `.vscode/settings.json` — VS Code workspace settings

### 2. Open in VS Code with the Claude extension

Open the project in VS Code, **reload the window** (Command Palette → `Developer: Reload Window`) if it was already open, then open the Claude chat panel and type `/` to discover the slash commands.

> The Claude extension scans `.claude/commands/` when the chat panel starts. Files written after the panel opened won't appear until you reload.

| Command | What it does |
|---------|-------------|
| `/vision` | Define the product vision — what it is, who it's for, why it matters |
| `/tech-stack` | Define the technology stack — languages, frameworks, databases, tooling |
| `/architecture` | Define the application architecture — structure, layers, components |
| `/roadmap` | Define ALL features needed to realize the product vision |
| `/specify` | Create a feature specification from a natural language description |
| `/plan` | Generate a technical planning package (prose only, no code) |
| `/tasks` | Create a human implementation checklist |
| `/clarify` | Find ambiguity and contradictions in specs |
| `/review` | Compare the implementation against the spec |
| `/trace` | Map requirements to tasks and check coverage |
| `/constitution` | Create or update the project constitution |

### 3. The Workflow

```
  /vision --> /tech-stack --> /architecture --> /roadmap --> For EACH feature:
      /specify --> /clarify --> /plan --> /tasks --> YOU IMPLEMENT BY HAND --> /review
```

1. **Vision**: Define the product vision — what it is, who it's for, and why.
2. **Tech Stack**: Define the technology stack — languages, frameworks, databases, and tooling.
3. **Architecture**: Define the application architecture — structure, layers, components, and data flow.
4. **Roadmap**: Define ALL features needed to build the product.
5. **For each feature from the roadmap:**
   1. **Specify**: Describe the feature. Claude creates a structured spec.
   2. **Clarify**: Claude finds ambiguity and contradictions in the spec.
   3. **Plan**: Claude generates research, data models, contracts — all in prose, no code.
   4. **Tasks**: Claude creates a sequenced, traceable checklist with acceptance criteria for you.
   5. **You implement**: You write every line of code by hand, guided by the planning artifacts.
   6. **Review**: Claude compares your implementation against the spec. Produces follow-up tasks, not patches.

## Project Structure

After `csdd init`, your project looks like:

```
my-project/
├── .csdd/
│   ├── memory/
│   │   ├── constitution.md          # The 8 Articles
│   │   ├── product-vision.md
│   │   ├── tech-stack.md
│   │   ├── architecture.md
│   │   └── feature-roadmap.md
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
├── .claude/
│   └── commands/
│       ├── vision.md
│       ├── tech-stack.md
│       ├── architecture.md
│       ├── roadmap.md
│       ├── specify.md
│       ├── plan.md
│       ├── tasks.md
│       ├── clarify.md
│       ├── review.md
│       ├── trace.md
│       └── constitution.md
├── CLAUDE.md
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

1. **Specification-First** — Specs before code.
2. **Human Implementation** — The human writes all code; AI never generates it.
3. **AI Planning-Only** — Claude clarifies, researches, plans, and reviews.
4. **Ambiguity Marking** — Unclear requirements get `[NEEDS CLARIFICATION]`.
5. **Traceability** — Tasks map to requirements, reviews map to specs.
6. **Review Over Regeneration** — Gaps produce follow-up tasks, not code.
7. **No Executable Planning AI Output** — Code fences and snippets are rejected from planning artifacts.
8. **Transparency** — Audit trail for all AI interactions.

## CLI Commands

```bash
csdd init <project-name>    # Initialize a new project
csdd init --here             # Initialize in current directory
csdd vision                  # Define the product vision
csdd tech-stack              # Define the technology stack
csdd architecture            # Define the application architecture
csdd roadmap                 # Define the feature roadmap
csdd specify                 # Create a feature specification
csdd clarify                 # Analyze specs for ambiguity
csdd plan                    # Generate a technical plan
csdd tasks                   # Create a human implementation checklist
csdd review                  # Review implementation against spec
csdd trace                   # Map requirements to tasks
csdd integrate claude-vscode # Re-run VS Code integration
csdd check                   # Verify project setup
csdd version                 # Show version
```

## Troubleshooting

### `/vision` (or any other slash command) does not appear in the Claude chat panel

The Claude Code VS Code extension reads project-scoped slash commands from `.claude/commands/<name>.md`. If a command does not appear when you type `/`, work through the checklist below — in order:

1. **From the project root, run `csdd check`.** It reports the installed CSDD version, whether `.claude/commands/` exists, which of the 11 expected `<name>.md` files are present, and whether their content matches the version bundled with the installed `csdd` package. It also flags stale `.github/skills/` directories left behind by pre-0.2.0 versions.

2. **If `.claude/commands/` is missing or empty, run `csdd integrate claude-vscode`.** This is also required after upgrading `csdd` — `csdd check` will tell you when installed command files have drifted from the bundled templates.

3. **Reload the VS Code window.** Open the command palette (`Cmd/Ctrl+Shift+P`) and run `Developer: Reload Window`. The Claude extension scans `.claude/commands/` when its chat panel starts; files written after the panel opened are not picked up until you reload.

4. **If you upgraded the `csdd` package recently, re-run the integration in every existing project.** Upgrading the CLI does not retroactively rewrite slash-command files that were copied into your projects.

5. **Confirm the `csdd` version.** Run `csdd version` — it must be 0.2.0 or later. Earlier releases installed commands under `.github/skills/<name>/SKILL.md`, which the Claude extension does not read. Upgrade with `uv tool install --reinstall claude-sdd-cli --from git+https://github.com/Lucas-Frazao/claude-sdd-cli.git`.

If you've done all of the above and a command still does not appear, open an issue with the output of `csdd check` and the contents of `.claude/commands/`.

## How It Differs from spec-kit

| Area | spec-kit | claude-sdd-cli |
|------|----------|----------------|
| Source of truth | Specification | Specification |
| AI role | Planning + code generation | Planning and review only |
| Code authorship | AI may generate code | The human implements all code |
| Constitution | Architectural discipline | Same + planning-only mandate |
| Tasks output | Ready for an AI agent | Ready for a human developer |
| Output validation | None | No-code validator on every artifact |
| Review model | Regeneration flow | Gap analysis without code fixes |
| Target surface | CLI agent | Claude in VS Code chat |

## Why?

Specifications should drive development. Coupled with structured planning artifacts — vision, tech stack, architecture, spec, plan, tasks — a developer can implement features deliberately, with full context and clear acceptance criteria, while keeping AI confined to thinking and planning.

This tool preserves the strongest idea from SDD — that specifications should drive development — while making the **human the sole implementer** and Claude a disciplined planning partner.

Built for:
- **Solo developers** who want strong planning support without AI-generated code
- **Students** who want to learn architecture and implementation deeply
- **Engineers** who want an auditable, specification-first workflow
- **Teams** using Claude in VS Code who want planning rigor without ceding code authorship

## Development

```bash
git clone https://github.com/Lucas-Frazao/claude-sdd-cli.git
cd claude-sdd-cli
uv pip install -e ".[dev]"
pytest
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

This project will not accept contributions that allow the AI to generate executable code or bypass the constitution.

## License

[MIT](LICENSE)
