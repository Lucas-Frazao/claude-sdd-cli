# Constitution — {{project_name}}

## Article 1: Specification-First Principle
Every feature begins with a structured specification before implementation starts.
Requirements, user stories, edge cases, and success criteria are defined first.

## Article 2: Claude CLI Implementation Mandate
All executable project artifacts must be implemented via Claude CLI.
The planning AI (Copilot) may not generate implementation code, test code, infrastructure code,
migration code, build scripts, configuration code, or any other executable artifact.
Claude CLI is the sole implementer.

## Article 3: AI Planning-Only Mandate
The planning AI (Copilot) participation is restricted to requirement clarification, research, planning,
task decomposition, review commentary, consistency checking, and traceability support.

## Article 4: Ambiguity Marking Requirement
When requirements are ambiguous or underspecified, the system must mark them with
[NEEDS CLARIFICATION] rather than guessing or filling in assumptions silently.

## Article 5: Traceability Requirement
Each task must map to one or more requirements. Each review finding must reference
a requirement, contract, or planning decision.

## Article 6: Review-Before-Regeneration Principle
The tool emphasizes validation, consistency checking, and review.
When gaps are found, the output is follow-up tasks and questions — not code patches.

## Article 7: No Executable Planning AI Output Rule
Any planning AI (Copilot) artifact containing executable code, code fences with implementation
content, or copy-paste-ready source/config/test content must be rejected or quarantined.
Tasks are intended for Claude CLI to implement.

## Article 8: Transparency and Auditability
Prompt and response history is preserved for review. Every planning decision
should be traceable to a user requirement or explicit assumption.
