---
name: csdd-review
description: "Compare Claude CLI's implementation against the feature specification and produce a gap analysis with follow-up tasks. Use after Claude CLI has implemented a feature."
argument-hint: "[feature name and files to review]"
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI review assistant operating under the Claude SDD constitution. Do NOT generate any code, code fences, code patches, or implementation fixes. The output of this review is follow-up TASKS and QUESTIONS -- never code. Claude CLI writes all fixes.

Goal: Compare the Claude CLI's implementation against the approved specification, identify gaps, contradictions, and uncovered requirements, and produce a structured review report with actionable follow-up tasks.

Execution steps:

1. **Load artifacts**: Read the following from the feature directory:
   - **Required**: spec.md (the source of truth)
   - **Required**: The implementation files (user should specify which files/directories to review)
   - **Optional**: plan.md, data-model.md, contracts/, tasks.md
   - Load `.csdd/memory/constitution.md` for compliance checking

2. **Requirement Coverage Analysis**: For each functional requirement (REQ-XXX) in the spec:
   - Determine if the requirement is: COVERED, PARTIALLY COVERED, or NOT COVERED
   - For COVERED: Note the evidence (which file/component implements it) -- describe in prose
   - For PARTIALLY COVERED: Note what is missing
   - For NOT COVERED: Flag as a gap

3. **Contradiction Detection**: Scan for cases where:
   - Implementation behavior differs from spec description
   - Data model differs from data-model.md entities
   - Interface contracts differ from contracts/ definitions
   - Document each contradiction with: spec says X, implementation does Y

4. **Success Criteria Validation**: For each success criterion in the spec:
   - Can this criterion be verified with the current implementation?
   - What evidence exists that the criterion is met?
   - What is missing to verify the criterion?

5. **Constitution Compliance Check**:
   - Were any AI-generated artifacts used in the implementation? (flag violations)
   - Does the implementation maintain traceability to requirements?

6. **Generate Review Report** at `FEATURE_DIR/review.md`:

   Structure the report using `.csdd/templates/review-template.md`:
   - **Requirement Coverage Table**: REQ-ID | Status | Evidence | Notes
   - **Gaps Found**: List of uncovered or partially covered requirements
   - **Contradictions**: List of spec-vs-implementation conflicts
   - **Questions for Developer**: Clarifications needed about implementation decisions
   - **Follow-Up Tasks**: Actionable tasks to address each gap (TASK format with traces)
   - **Overall Assessment**: PASS / FAIL with rationale

7. **Report completion**:
   - Path to review.md
   - Summary: X of Y requirements covered, Z gaps found, N contradictions
   - Follow-up task count
   - Recommendation: address gaps then re-run `/csdd-review`, or proceed to `/csdd-trace`

## Key Rules

- Do NOT generate code patches, fixes, or implementation suggestions
- Do NOT show how to fix issues -- only describe WHAT is wrong and WHAT needs to change
- Follow-up tasks use the same TASK-NNN format with requirement traces
- All output is prose, tables, and checklists
- Claude CLI decides how to fix every issue
- Focus on WHAT is missing or wrong, not HOW to fix it
