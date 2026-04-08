---
description: Map requirements to tasks and check coverage percentage for full requirement traceability.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant. Do NOT generate any code, code fences, or implementation snippets. All output must be prose, Markdown tables, and structured text.

Goal: Build a complete traceability matrix mapping every requirement (REQ-XXX) from the spec to its corresponding tasks (TASK-NNN), implementation evidence, and review status.

Execution steps:

1. **Load artifacts**: Read from the feature directory:
   - **Required**: spec.md (requirements source)
   - **Required**: tasks.md (task definitions with traces)
   - **Optional**: review.md (review findings)
   - **Optional**: Implementation files (for evidence)

2. **Extract requirements**: Parse all REQ-XXX identifiers from spec.md:
   - Functional requirements (REQ-001, REQ-002, etc.)
   - Non-functional requirements (REQ-NF-001, etc.)
   - Record the requirement text for each ID

3. **Extract task mappings**: Parse all TASK-NNN entries from tasks.md:
   - Record the `(traces: REQ-XXX)` mapping for each task
   - Identify tasks with no trace (orphan tasks)

4. **Build traceability matrix**:

   | Requirement | Description | Linked Tasks | Task Status | Coverage |
   |-------------|-------------|--------------|-------------|----------|
   | REQ-001     | [text]      | TASK-001, TASK-003 | 1/2 done | Partial |
   | REQ-002     | [text]      | (none)       | --          | Missing  |
   | REQ-NF-001  | [text]      | TASK-005     | done        | Covered  |

5. **Calculate coverage metrics**:
   - Total requirements count
   - Requirements with linked tasks (covered)
   - Requirements without linked tasks (gaps)
   - Coverage percentage: (covered / total) * 100
   - Orphan tasks (tasks not linked to any requirement)

6. **Generate traceability report** at `FEATURE_DIR/traceability.md`:
   - Traceability matrix (table above)
   - Coverage summary: X% coverage (N of M requirements traced)
   - Gap list: Requirements with no linked tasks
   - Orphan tasks: Tasks with no requirement trace
   - Risk assessment: High (< 50%), Medium (50-80%), Low (> 80%)

7. **Report completion**:
   - Path to traceability.md
   - Coverage percentage
   - Number of gaps
   - Number of orphan tasks
   - Recommendation:
     - If gaps exist: create additional tasks via `/csdd.tasks`
     - If orphan tasks exist: review whether they map to undocumented requirements
     - If coverage > 80%: ready for implementation or review

## Key Rules

- Do NOT generate any code or implementation details
- All output is prose, Markdown tables, and structured text
- Traceability is about the RELATIONSHIP between artifacts, not implementation
- Focus on completeness and consistency of the planning artifacts
