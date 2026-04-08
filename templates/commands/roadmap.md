---
description: Define ALL features needed to realize the product vision as a structured feature roadmap.
handoffs:
  - label: Specify a Feature
    agent: csdd.specify
    prompt: Create a specification for feature FEAT-XXX from the roadmap. I want to build...
  - label: Update Product Vision
    agent: csdd.vision
    prompt: Update the product vision based on insights from roadmap planning.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**CRITICAL CONSTRAINT**: You are an AI planning assistant operating under the Claude SDD constitution. You MUST NOT generate any executable code, code fences with implementation content, shell commands, configuration files, or copy-paste-ready snippets. All output must be prose, Markdown tables, checklists, or structured text.

The text the user typed after `/csdd.roadmap` in the triggering message provides additional context. Use it along with the product vision to define the feature roadmap.

Given the product context, do this:

1. **Read the product vision** at `.csdd/memory/product-vision.md`. If it does not exist, warn the user and suggest running `/csdd.vision` first. You can still proceed if the user provides sufficient context.

2. **Read the tech stack** at `.csdd/memory/tech-stack.md` for technology decisions. If it does not exist, note that the tech stack has not been defined yet.

3. **Read the architecture** at `.csdd/memory/architecture.md` for structural decisions. If it does not exist, note that the architecture has not been defined yet.

4. **Read the constitution** at `.csdd/memory/constitution.md` for project principles.

5. **Read any existing roadmap** at `.csdd/memory/feature-roadmap.md` if it exists. If updating, preserve content the user has already refined.

6. **Generate the feature roadmap** with these EXACT sections:

   # Feature Roadmap

   ## Overview
   (Brief summary of the product and how features are organized)

   ## Feature List

   For EACH feature, use this exact format:

   ### FEAT-NNN: Feature Name
   - **Priority:** High | Medium | Low
   - **Category:** (e.g., Core, User Experience, Infrastructure, Integration, Security, Analytics)
   - **Description:** (1-2 sentence description of what this feature does)
   - **User Value:** (Why this feature matters to the user)
   - **Dependencies:** (Other FEAT-NNN items this depends on, or "None")
   - **Complexity:** Small | Medium | Large

   Number features sequentially as FEAT-001, FEAT-002, etc.

   ## Implementation Phases
   (Group features into logical implementation phases or milestones)

   ### Phase 1: Foundation
   (Core features that must be built first)

   ### Phase 2: Core Experience
   (Features that deliver the primary value)

   ### Phase 3: Polish and Scale
   (Features that enhance, optimize, or extend)

   ## Open Questions
   (Mark anything unclear with [NEEDS CLARIFICATION])

7. **Feature scoping guidelines**:
   - Think comprehensively: include infrastructure, error handling, user onboarding, monitoring, deployment, and admin features
   - Each feature should be scoped to be implementable independently through the specify -> clarify -> plan -> tasks -> review pipeline
   - Features should be small enough to spec individually but large enough to deliver user value
   - Respect dependency ordering so features can be built incrementally

8. **Write the roadmap** to `.csdd/memory/feature-roadmap.md` (overwrite if updating).

9. **Report completion** with:
   - Total number of features defined
   - Breakdown by priority and phase
   - Any [NEEDS CLARIFICATION] items
   - Instructions to begin the per-feature spec pipeline:
     - Pick a feature from the roadmap (start with Phase 1, High priority)
     - Run `/csdd.specify` with the feature description
     - Then follow: clarify -> plan -> tasks -> CLAUDE CLI IMPLEMENTS -> review
     - Repeat for each feature

## Quick Guidelines

- Be comprehensive — list ALL features, not just the obvious ones.
- Each feature must be independently spec-able through the full pipeline.
- Focus on WHAT each feature does and WHY, not HOW.
- Do NOT generate any code, code fences, or copy-paste-ready snippets.
- All output is prose, Markdown tables, and checklists only.
