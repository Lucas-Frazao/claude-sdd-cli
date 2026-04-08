---
description: Create or update the feature specification from a natural language feature description.
handoffs:
  - label: Build Technical Plan
    agent: csdd.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: csdd.clarify
    prompt: Clarify specification requirements
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant operating under the Claude SDD constitution. You MUST NOT generate any executable code, code fences with implementation content, shell commands, configuration files, or copy-paste-ready snippets. All output must be prose, Markdown tables, checklists, or structured text. Focus on WHAT and WHY, never HOW to implement.

The text the user typed after `/csdd.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the branch:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Examples:
     - "I want to add user authentication" -> "user-auth"
     - "Implement OAuth2 integration for the API" -> "oauth2-api-integration"
     - "Create a dashboard for analytics" -> "analytics-dashboard"

2. **Create the feature branch** by running the script with `--short-name` (and `--json`). In sequential mode, do NOT pass `--number` -- the script auto-detects the next available number:

   - Bash example: `{SCRIPT} --json --short-name "user-auth" "Add user authentication"`

   **IMPORTANT**:
   - Do NOT pass `--number` -- the script determines the correct next number automatically
   - Always include `--json` so the output can be parsed reliably
   - You must only ever run this script once per feature
   - The JSON output will contain BRANCH_NAME and SPEC_FILE paths

3. Load `.csdd/templates/spec-template.md` to understand required sections.

4. Follow this execution flow:

    1. Parse user description from Input
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Stories section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description while preserving section order and headings.

6. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria:

   a. **Validate** against these items:
      - No implementation details (languages, frameworks, APIs)
      - Focused on user value and business needs
      - Written for non-technical stakeholders
      - All mandatory sections completed
      - Requirements are testable and unambiguous
      - Success criteria are measurable and technology-agnostic
      - Edge cases are identified
      - Scope is clearly bounded

   b. **Handle Validation Results**:
      - **If items fail**: List the failing items, update the spec to address each issue, re-validate (max 3 iterations)
      - **If [NEEDS CLARIFICATION] markers remain** (max 3):
        Present options to user in this format:

        ```markdown
        ## Question [N]: [Topic]

        **Context**: [Quote relevant spec section]

        **What we need to know**: [Specific question]

        **Suggested Answers**:

        | Option | Answer | Implications |
        |--------|--------|--------------|
        | A      | [First suggested answer] | [What this means] |
        | B      | [Second suggested answer] | [What this means] |
        | C      | [Third suggested answer] | [What this means] |

        **Your choice**: _[Wait for user response]_
        ```

7. Report completion with branch name, spec file path, and readiness for the next phase (`/csdd.clarify` or `/csdd.plan`).

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- Do NOT generate any code, code fences with implementation content, or copy-paste-ready snippets.
- All output is prose, Markdown tables, and checklists only.

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should be made testable and unambiguous

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective
4. **Verifiable**: Can be tested without knowing implementation details

**Good examples**:
- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"

**Bad examples** (implementation-focused):
- "API response time is under 200ms"
- "Database can handle 1000 TPS"
- "React components render efficiently"
