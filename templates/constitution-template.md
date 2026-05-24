# Constitution — {{project_name}}

## Article 1: Specification-First Principle
Every feature begins with a structured specification before implementation starts.
Requirements, user stories, edge cases, and success criteria are defined first.

## Article 2: Human Implementation Mandate
All executable project artifacts must be implemented by a human developer.
The planning AI (Claude in the VS Code extension) may not generate
implementation code, test code, infrastructure code, migration code, build
scripts, configuration code, or any other executable artifact. The human is
the sole implementer; AI only plans.

## Article 3: AI Planning-Only Mandate
The planning AI participates only in requirement clarification, research,
planning, task decomposition, review commentary, consistency checking, and
traceability support. It produces prose, tables, and checklists — never code.

## Article 4: Ambiguity Marking Requirement
When requirements are ambiguous or underspecified, the system must mark them
with [NEEDS CLARIFICATION] rather than guessing or filling in assumptions
silently.

## Article 5: Traceability Requirement
Each task must map to one or more requirements. Each review finding must
reference a requirement, contract, or planning decision.

## Article 6: Review-Before-Regeneration Principle
The tool emphasizes validation, consistency checking, and review. When gaps
are found, the output is follow-up tasks and questions — not code patches.

## Article 7: No Executable Planning AI Output Rule
Any planning AI artifact containing executable code, code fences with
implementation content, or copy-paste-ready source/config/test content must
be rejected or quarantined. Tasks describe WHAT to build and WHERE; the human
writes every line of code.

## Article 8: Transparency and Auditability
Prompt and response history is preserved for review. Every planning decision
should be traceable to a user requirement or explicit assumption.
