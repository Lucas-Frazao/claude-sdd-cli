---
description: Execute the implementation planning workflow using the plan template to generate design artifacts -- ALL IN PROSE, no code.
handoffs:
  - label: Create Tasks
    agent: hsdd.tasks
    prompt: Break the plan into tasks for the human developer
    send: true
scripts:
  sh: scripts/bash/setup-plan.sh --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant operating under the Human-Authored SDD constitution. Do NOT generate any code, code fences, or implementation snippets. All design artifacts (research.md, data-model.md, contracts/, quickstart.md) must be written entirely in prose, Markdown tables, and structured text. The human developer writes ALL code.

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH.

2. **Load context**: Read FEATURE_SPEC and `.hsdd/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**:
   - For each NEEDS CLARIFICATION -> research task
   - For each dependency -> best practices task (described in prose)
   - For each integration -> patterns task (described in prose)

2. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]
   - All in prose -- no code samples, no config snippets

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** -> `data-model.md`:
   - Entity name, fields, relationships -- described in prose and tables
   - Validation rules from requirements -- described in natural language
   - State transitions if applicable -- described as prose or table
   - Do NOT include schema definitions, SQL, or ORM code

2. **Define interface contracts** (if project has external interfaces) -> `/contracts/`:
   - Identify what interfaces the project exposes
   - Document the contract format in prose (inputs, outputs, behaviors, error cases)
   - Describe endpoints, parameters, and responses in natural language tables
   - Do NOT include code, API schemas, or configuration files

3. **Generate quickstart.md**:
   - Validation scenarios described in prose
   - Expected behaviors and edge cases in natural language
   - Do NOT include test code or executable scripts

**Output**: data-model.md, /contracts/*, quickstart.md -- ALL PROSE, NO CODE

## Key Rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
- Do NOT generate any code, code fences, or implementation snippets
- All design artifacts must be written in prose, Markdown tables, and structured text
- The human developer writes all implementation code based on these prose artifacts
- Focus on WHAT needs to be built and WHY, not HOW to implement it
