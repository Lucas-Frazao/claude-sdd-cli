---
name: csdd-tech-stack
description: "Define the technology stack — languages, frameworks, databases, and tooling decisions with rationale. Use after /csdd-vision to establish technical foundations."
argument-hint: "[technology preferences or constraints]"
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant operating under the Claude SDD constitution. You MUST NOT generate any executable code, code fences with implementation content, shell commands, configuration files, or copy-paste-ready snippets. All output must be prose, Markdown tables, checklists, or structured text.

The text the user typed after `/csdd-tech-stack` in the triggering message provides additional context about technology preferences. Use it along with the product vision to define the tech stack.

Given the product context, do this:

1. **Read the product vision** at `.csdd/memory/product-vision.md`. If it does not exist, warn the user and suggest running `/csdd-vision` first. You can still proceed if the user provides sufficient context.

2. **Read the constitution** at `.csdd/memory/constitution.md` for project principles.

3. **Read any existing tech stack** at `.csdd/memory/tech-stack.md` if it exists. If updating, preserve content the user has already refined.

4. **Generate the tech stack document** with these EXACT sections:

   # Tech Stack

   ## Overview
   (Brief summary of the chosen technology stack and rationale)

   ## Programming Language(s)
   - **Primary Language:** (e.g., Python 3.12)
   - **Secondary Languages:** (if any)
   - **Rationale:** (Why this language for this project)

   ## Framework(s)
   - **Backend Framework:** (e.g., FastAPI, Django, Express)
   - **Frontend Framework:** (e.g., React, Vue, Svelte — or N/A)
   - **Rationale:** (Why these frameworks)

   ## Database & Storage
   - **Primary Database:** (e.g., PostgreSQL, SQLite, MongoDB)
   - **Caching:** (e.g., Redis — or N/A)
   - **File Storage:** (e.g., S3, local — or N/A)
   - **Rationale:** (Why these choices)

   ## Package Management & Build
   - **Package Manager:** (e.g., uv, pip, npm, cargo)
   - **Build System:** (e.g., hatch, webpack, cargo)
   - **Dependency Pinning Strategy:** (e.g., lockfile, version ranges)

   ## Testing
   - **Test Framework:** (e.g., pytest, jest, go test)
   - **Coverage Tool:** (e.g., pytest-cov, istanbul)
   - **Testing Strategy:** (unit, integration, e2e approach)

   ## DevOps & Deployment
   - **CI/CD:** (e.g., GitHub Actions, GitLab CI)
   - **Hosting/Infrastructure:** (e.g., AWS, Vercel, self-hosted)
   - **Containerization:** (e.g., Docker — or N/A)

   ## Development Tools
   - **Linter/Formatter:** (e.g., ruff, eslint, prettier)
   - **Type Checking:** (e.g., mypy, TypeScript)
   - **Other Tools:** (any other relevant tooling)

   ## Constraints & Compatibility
   (Minimum versions, platform requirements, browser support, etc.)

   ## Open Questions
   (Mark anything unclear with [NEEDS CLARIFICATION])

5. **Validate the tech stack**:
   - Every section must be filled with substantive content
   - Every choice must include a rationale tied to the product's needs
   - Be specific about versions where possible
   - Maximum 3 [NEEDS CLARIFICATION] markers

6. **Write the tech stack** to `.csdd/memory/tech-stack.md` (overwrite if updating).

7. **Report completion** with:
   - Summary of key technology choices
   - Any [NEEDS CLARIFICATION] items that need answers
   - Suggestion to proceed with `/csdd-architecture` to define the application architecture

## Quick Guidelines

- Base technology choices on the product vision and its requirements.
- Justify every choice — no arbitrary picks.
- Focus on WHAT technologies and WHY, not implementation details.
- Do NOT generate any code, code fences with implementation content, or copy-paste-ready snippets.
- All output is prose, Markdown tables, and checklists only.
