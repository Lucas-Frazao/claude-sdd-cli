---
description: Generate an actionable, dependency-ordered tasks.md checklist for Claude CLI based on available design artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant. The tasks you generate are for Claude CLI to implement. Do NOT generate any code, code fences, or implementation snippets. Each task describes WHAT to implement and WHERE, not HOW. Claude CLI writes every line of code.

1. **Load design documents**: Read from the feature directory:
   - **Required**: plan.md (technical direction), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (interface contracts), research.md (decisions), quickstart.md (validation scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what is available.

2. **Execute task generation workflow**:
   - Load plan.md and extract technical direction, project structure guidance
   - Load spec.md and extract user stories with their priorities
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map interface contracts to user stories
   - Generate tasks organized by phase (see Task Generation Rules below)
   - Generate dependency graph showing completion order
   - Validate task completeness (each user story has all needed tasks)

3. **Generate tasks.md**: Use `.csdd/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Data model tasks (if applicable)
   - Phase 3: Core logic tasks
   - Phase 4: Integration tasks
   - Phase 5: Validation tasks (what to test, not how)
   - Phase 6: Documentation tasks
   - Phase 7: Review tasks (run `csdd review`)
   - All tasks must follow the strict checklist format (see below)
   - Clear file paths for each task
   - Requirement traceability (traces: REQ-XXX)

4. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per phase
   - Requirement coverage (which REQs are traced)
   - Suggested implementation order

## Task Generation Rules

**CRITICAL**: Tasks are for Claude CLI. They describe WHAT to build, not HOW.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] TASK-NNN: Description with file path (traces: REQ-XXX)
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (TASK-001, TASK-002...) in execution order
3. **Description**: Clear action with exact file path where work happens
4. **Traceability**: MUST end with `(traces: REQ-XXX)` mapping to requirement(s)

**Examples**:

- CORRECT: `- [ ] TASK-001: Set up project directory structure per plan (traces: REQ-001)`
- CORRECT: `- [ ] TASK-005: Implement user model in src/models/user.py (traces: REQ-002, REQ-003)`
- WRONG: `- [ ] Create User model` (missing ID, traces, file path)
- WRONG: `TASK-001: Create model` (missing checkbox)

### What Tasks MUST Include

- WHAT to implement (entity, component, feature)
- WHERE to implement it (file path)
- WHICH requirement it fulfills (traces)

### What Tasks MUST NOT Include

- Code snippets or implementation details
- Specific algorithms or data structures to use
- Framework-specific patterns or API calls
- Configuration values or environment variables
- Any executable content

### Task Organization

1. **Setup Tasks**: Project structure, dependencies description
2. **Data Model Tasks**: One task per entity from data-model.md
3. **Core Logic Tasks**: Business logic per user story
4. **Integration Tasks**: Connecting components
5. **Validation Tasks**: What to test (not how to write tests)
6. **Documentation Tasks**: What to document
7. **Review Tasks**: Run spec compliance review

### Validation Checkpoints

Between major phases, include validation checkpoint tasks:
- `- [ ] TASK-NNN: Validate Phase X outputs against spec requirements (traces: REQ-XXX)`

These remind Claude CLI to check work against the spec before proceeding.
