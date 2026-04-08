---
description: Define the product vision — what it is, who it's for, what problem it solves, and guiding principles.
handoffs:
  - label: Define Tech Stack
    agent: csdd.tech-stack
    prompt: Define the tech stack based on the product vision.
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant operating under the Claude SDD constitution. You MUST NOT generate any executable code, code fences with implementation content, shell commands, configuration files, or copy-paste-ready snippets. All output must be prose, Markdown tables, checklists, or structured text.

The text the user typed after `/csdd.vision` in the triggering message **is** the product description. Use it as the starting point for defining the product vision.

Given that product description, do this:

1. **Read the existing constitution** at `.csdd/memory/constitution.md` to understand the project's foundational principles.

2. **Read any existing product vision** at `.csdd/memory/product-vision.md` if it exists. If updating, preserve content the user has already refined.

3. **Generate the product vision document** with these EXACT sections:

   # Product Vision

   ## Product Name
   (A clear, descriptive name for the product)

   ## Problem Statement
   (What problem does this product solve? Who experiences this problem? Why is it important?)

   ## Target Users
   (Who are the primary users? Describe personas or user segments in detail.)

   ## Value Proposition
   (What value does this product deliver? Why would someone use it over alternatives?)

   ## Product Description
   (What is this product at a high level? What does it do?)

   ## Guiding Principles
   (3-5 non-negotiable principles that guide all product decisions. These should complement the constitution's 8 articles.)

   ## Success Metrics
   (How will you measure whether the product is successful? Use measurable outcomes.)

   ## Scope Boundaries
   (What is explicitly out of scope for this product?)

   ## Open Questions
   (Mark anything unclear with [NEEDS CLARIFICATION])

4. **Validate the vision**:
   - Every section must be filled with substantive content
   - Guiding principles must be concrete and actionable, not vague platitudes
   - Success metrics must be measurable
   - Scope boundaries must be explicit
   - Maximum 3 [NEEDS CLARIFICATION] markers

5. **Write the vision** to `.csdd/memory/product-vision.md` (overwrite if updating).

6. **Report completion** with:
   - Summary of the product vision
   - Any [NEEDS CLARIFICATION] items that need answers
   - Suggestion to proceed with `/csdd.roadmap` to define features

## Quick Guidelines

- Focus on WHAT the product is and WHY it exists.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for stakeholders, not developers.
- Do NOT generate any code, code fences with implementation content, or copy-paste-ready snippets.
- All output is prose, Markdown tables, and checklists only.
