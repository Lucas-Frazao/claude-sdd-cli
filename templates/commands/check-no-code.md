---
description: Validate that no AI-generated artifacts contain executable code, enforcing the Human Authorship mandate.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: This command exists to enforce the foundational principle of Human-Authored SDD: AI NEVER writes code. This command scans all AI-generated artifacts and flags any violations of Article 7 (No Executable AI Output Rule).

Goal: Scan all AI-generated planning artifacts in the feature directory for code violations and report findings.

Execution steps:

1. **Identify scan targets**: Locate all AI-generated artifacts in the feature directory:
   - spec.md
   - plan.md
   - research.md
   - data-model.md
   - contracts/*.md
   - quickstart.md
   - tasks.md
   - review.md
   - traceability.md
   - clarification-analysis.md
   - Any other .md files in the feature directory

2. **Scan each file** for these violation categories:

   **Category A: Code Fences with Language Tags**
   - Detect fenced code blocks with language identifiers:
     python, javascript, typescript, java, go, rust, c, cpp, ruby, php, swift, kotlin,
     sql, bash, shell, sh, zsh, powershell, yaml, toml, json, xml, html, css, scss,
     dockerfile, terraform, hcl, graphql, protobuf
   - Exception: Markdown code fences used for formatting (e.g., showing task format) are allowed
     if they contain only template/placeholder text, not executable code

   **Category B: Executable Line Patterns**
   - Import/include statements (import, require, include, using, from...import)
   - Function/method definitions (def, function, fn, func, sub, proc)
   - Class definitions (class, struct, interface, enum, trait)
   - Variable declarations with assignments in code syntax
   - SQL statements (SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP)
   - Shell commands (apt, pip, npm, docker, kubectl, terraform, git commands in executable context)
   - Package manager commands in executable context

   **Category C: Configuration Fragments**
   - Package.json content
   - pyproject.toml content (beyond prose references)
   - docker-compose.yml content
   - Kubernetes manifests
   - Terraform/HCL blocks
   - CI/CD pipeline definitions (.github/workflows, .gitlab-ci, Jenkinsfile)

   **Category D: Copy-Paste-Ready Snippets**
   - Code that could be directly copied into a source file
   - Environment variable definitions (export KEY=VALUE)
   - API endpoint definitions in code format
   - Database migration scripts

3. **Classify each finding**:
   - **ERROR**: Clear executable code that violates Article 7
   - **WARNING**: Borderline content that might be code (e.g., pseudocode that resembles real code too closely)
   - **INFO**: Allowed template/format examples

4. **Generate report**:

   For each file scanned:
   - File path
   - Scan result: CLEAN / VIOLATIONS FOUND
   - For each violation:
     - Line number
     - Content (quoted)
     - Category (A/B/C/D)
     - Severity (ERROR/WARNING)
     - Rule violated (Article 7, specific clause)

5. **Summary**:
   - Total files scanned
   - Clean files count
   - Files with violations count
   - Total errors / warnings
   - Overall verdict: PASS (0 errors) / FAIL (>= 1 error)

6. **If violations found**:
   - List specific remediation needed for each (described in prose)
   - Recommend re-running the originating command with stricter constitution enforcement
   - Note: The human developer should review and either remove the violating content or rewrite the artifact

## Key Rules

- This command itself must NOT generate any code
- It only produces a prose report of findings
- Violations indicate the AI planning commands need improvement, not that the human did anything wrong
- The constitution is the source of truth for what constitutes a violation
