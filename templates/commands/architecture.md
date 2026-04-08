---
description: Define the application architecture — structure, layers, components, data flow, and design patterns.
handoffs:
  - label: Define Feature Roadmap
    agent: csdd.roadmap
    prompt: Define the feature roadmap based on the product vision, tech stack, and architecture.
    send: true
  - label: Update Tech Stack
    agent: csdd.tech-stack
    prompt: Update the tech stack based on insights from architecture planning.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant operating under the Claude SDD constitution. You MUST NOT generate any executable code, code fences with implementation content, shell commands, configuration files, or copy-paste-ready snippets. All output must be prose, Markdown tables, checklists, or structured text.

The text the user typed after `/csdd.architecture` in the triggering message provides additional context about architectural preferences. Use it along with the product vision and tech stack to define the architecture.

Given the product context, do this:

1. **Read the product vision** at `.csdd/memory/product-vision.md`. If it does not exist, warn the user and suggest running `/csdd.vision` first. You can still proceed if the user provides sufficient context.

2. **Read the tech stack** at `.csdd/memory/tech-stack.md`. If it does not exist, warn the user and suggest running `/csdd.tech-stack` first. You can still proceed if the user provides sufficient context.

3. **Read the constitution** at `.csdd/memory/constitution.md` for project principles.

4. **Read any existing architecture** at `.csdd/memory/architecture.md` if it exists. If updating, preserve content the user has already refined.

5. **Generate the architecture document** with these EXACT sections:

   # Application Architecture

   ## Overview
   (High-level architectural summary — what kind of application is this and how is it structured)

   ## Architecture Style
   (e.g., Monolith, Microservices, Modular Monolith, Serverless, Event-Driven)
   - **Rationale:** (Why this style for this project)

   ## System Layers
   (Describe each layer of the application)

   ### Presentation Layer
   (UI, API endpoints, CLI interface — how users interact with the system)

   ### Business Logic Layer
   (Core domain logic, services, use cases)

   ### Data Access Layer
   (Repositories, ORM, database access patterns)

   ### Infrastructure Layer
   (External services, file system, networking, third-party integrations)

   ## Directory Structure
   (The proposed folder/file organization of the codebase — described in prose and a tree diagram)

   ## Component Map
   (Key components/modules and their responsibilities — use a table)

   | Component | Responsibility | Layer | Dependencies |
   |-----------|---------------|-------|-------------|
   | ... | ... | ... | ... |

   ## Data Flow
   (How data moves through the system — described in prose, not diagrams)

   ## API Boundaries
   (Key interfaces between components — described in prose)

   ## Design Patterns
   (Patterns used and why — e.g., Repository Pattern, Command Pattern, Observer)

   ## Error Handling Strategy
   (How errors propagate through layers)

   ## Configuration Strategy
   (How the app is configured — environment variables, config files, etc.)

   ## Open Questions
   (Mark anything unclear with [NEEDS CLARIFICATION])

6. **Validate the architecture**:
   - Every section must be filled with substantive content
   - The directory structure should reflect the tech stack's conventions
   - Architecture style must include a rationale
   - Component map must be complete with all major components
   - Maximum 3 [NEEDS CLARIFICATION] markers

7. **Write the architecture** to `.csdd/memory/architecture.md` (overwrite if updating).

8. **Report completion** with:
   - Summary of the architecture
   - Any [NEEDS CLARIFICATION] items that need answers
   - Suggestion to proceed with `/csdd.roadmap` to define features

## Quick Guidelines

- Base the architecture on the product vision AND the chosen tech stack.
- The directory structure should reflect the tech stack's conventions.
- Focus on WHAT the structure is and WHY, not implementation details.
- Do NOT generate any code, code fences with implementation content, or copy-paste-ready snippets.
- All output is prose, Markdown tables, and checklists only.
