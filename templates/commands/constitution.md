---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
handoffs:
  - label: Build Specification
    agent: hsdd.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.hsdd/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

**CRITICAL CONSTRAINT**: You are an AI planning assistant. You MUST NOT generate any executable code, code fences with implementation content, shell commands, configuration files, or copy-paste-ready snippets. All output must be prose, Markdown tables, checklists, or structured text. This applies to the constitution and all dependent artifacts.

**Note**: If `.hsdd/memory/constitution.md` does not exist yet, it should have been initialized from `.hsdd/templates/constitution-template.md` during project setup. If it's missing, copy the template first.

The constitution MUST include these 8 foundational articles:

1. **Article 1: Specification-First Principle** -- Every feature begins with a structured specification before implementation starts.
2. **Article 2: Human Authorship Mandate** -- All executable project artifacts must be authored by the human developer. AI may not generate implementation code, test code, infrastructure code, migration code, build scripts, configuration code, or any other executable artifact.
3. **Article 3: AI Planning-Only Mandate** -- AI participation is restricted to requirement clarification, research, planning, task decomposition, review commentary, consistency checking, and traceability support.
4. **Article 4: Ambiguity Marking Requirement** -- When requirements are ambiguous or underspecified, mark them with [NEEDS CLARIFICATION] rather than guessing.
5. **Article 5: Traceability Requirement** -- Each task must map to one or more requirements. Each review finding must reference a requirement, contract, or planning decision.
6. **Article 6: Review-Before-Regeneration Principle** -- When gaps are found, the output is follow-up tasks and questions -- not code patches.
7. **Article 7: No Executable AI Output Rule** -- Any AI-generated artifact containing executable code, code fences with implementation content, or copy-paste-ready source/config/test content must be rejected or quarantined.
8. **Article 8: Transparency and Auditability** -- Every planning decision should be traceable to a user requirement or explicit assumption.

Follow this execution flow:

1. Load the existing constitution at `.hsdd/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions).
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text.
   - Preserve heading hierarchy.
   - Ensure each Principle section: succinct name line, paragraph capturing non-negotiable rules, explicit rationale.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist:
   - Read `.hsdd/templates/plan-template.md` and ensure any rules align with updated principles.
   - Read `.hsdd/templates/spec-template.md` for scope/requirements alignment.
   - Read `.hsdd/templates/tasks-template.md` and ensure task categorization reflects principle-driven task types.
   - Read each command file in `.hsdd/templates/commands/*.md` to verify no outdated references remain.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file):
   - Version change: old -> new
   - List of modified principles (old title -> new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language.

7. Write the completed constitution back to `.hsdd/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message.

Do not create a new template; always operate on the existing `.hsdd/memory/constitution.md` file.

Do NOT generate any code, code fences, or implementation snippets in any output.
