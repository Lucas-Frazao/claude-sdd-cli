---
name: csdd-clarify
description: "Identify underspecified areas in the current feature spec by asking up to 5 targeted clarification questions and encoding answers back into the spec. Use after /csdd-specify and before /csdd-plan."
argument-hint: "[feature name or spec path]"
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant. Do NOT generate any code, code fences, or implementation snippets. All output must be prose, Markdown tables, and structured text.

Goal: Detect and reduce ambiguity or missing decision points in the active feature specification and record the clarifications directly in the spec file.

Note: This clarification workflow is expected to run (and be completed) BEFORE invoking `/csdd-plan`. If the user explicitly states they are skipping clarification, you may proceed, but must warn that downstream rework risk increases.

Execution steps:

1. Locate the current feature spec file in the `specs/` directory. If no spec exists, instruct user to run `/csdd-specify` first.

2. Load the current spec file. Perform a structured ambiguity & coverage scan using this taxonomy. For each category, mark status: Clear / Partial / Missing.

   Functional Scope & Behavior:
   - Core user goals & success criteria
   - Explicit out-of-scope declarations
   - User roles / personas differentiation

   Domain & Data Model:
   - Entities, attributes, relationships
   - Identity & uniqueness rules
   - Lifecycle/state transitions

   Interaction & UX Flow:
   - Critical user journeys / sequences
   - Error/empty/loading states

   Non-Functional Quality Attributes:
   - Performance targets
   - Scalability expectations
   - Security & privacy requirements

   Edge Cases & Failure Handling:
   - Negative scenarios
   - Conflict resolution

   Constraints & Tradeoffs:
   - Technical constraints
   - Explicit tradeoffs or rejected alternatives

3. Generate (internally) a prioritized queue of candidate clarification questions (maximum 5). Apply these constraints:
    - Maximum of 5 total questions across the whole session
    - Each question must be answerable with EITHER:
       - A short multiple-choice selection (2-5 options), OR
       - A one-word / short-phrase answer (<=5 words)
    - Only include questions whose answers materially impact architecture, data modeling, task decomposition, or validation
    - Ensure category coverage balance

4. Sequential questioning loop (interactive):
    - Present EXACTLY ONE question at a time
    - For multiple-choice questions:
       - Analyze all options and determine the most suitable option
       - Present your recommended option prominently with reasoning
       - Render all options as a Markdown table
       - After the table: `You can reply with the option letter, accept the recommendation by saying "yes", or provide your own short answer.`
    - After the user answers:
       - Validate the answer maps to one option or fits the constraint
       - Record it and move to the next queued question
    - Stop when: all critical ambiguities resolved, user signals completion, or 5 questions reached

5. Integration after EACH accepted answer:
    - Ensure a `## Clarifications` section exists in the spec
    - Append: `- Q: <question> -> A: <final answer>`
    - Apply the clarification to the most appropriate section(s)
    - If the clarification invalidates an earlier ambiguous statement, replace it
    - Save the spec file after each integration

6. Validation after each write:
   - Clarifications section contains one bullet per accepted answer
   - Total asked questions <= 5
   - Updated sections contain no lingering vague placeholders the new answer resolved
   - Markdown structure valid

7. Write the updated spec back to the spec file.

8. Report completion:
   - Number of questions asked & answered
   - Path to updated spec
   - Sections touched
   - Coverage summary table
   - Suggested next command (`/csdd-plan`)

Behavior rules:
- If no meaningful ambiguities found, respond: "No critical ambiguities detected." and suggest proceeding
- If spec file missing, instruct user to run `/csdd-specify` first
- Never exceed 5 total asked questions
- Do NOT generate any code, code fences, or implementation snippets
