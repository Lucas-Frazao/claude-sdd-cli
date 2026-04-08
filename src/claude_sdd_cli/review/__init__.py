"""Review layer — compares implementation against specs and plans."""

from pathlib import Path
from typing import Optional

from claude_sdd_cli.parsers import parse_requirements, find_open_questions


def build_review_prompt(feature_dir: Path, implementation_notes: str = "") -> str:
    """Construct the review prompt from artifacts in the feature directory.

    Parameters
    ----------
    feature_dir : Path
        Path to the feature directory containing spec.md, plan.md, etc.
    implementation_notes : str
        Optional developer-provided description of what they implemented.
    """
    parts = [
        "You are reviewing a Claude CLI implementation against its specification and plan.",
        "Your job is to identify gaps, contradictions, and missing requirements.",
        "You MUST NOT suggest code fixes or output any code.",
        "Produce your review as prose with sections for: gaps, contradictions, "
        "questions, and follow-up tasks.",
        "",
    ]

    # Load available artifacts
    for artifact in ["spec", "plan", "data-model", "quickstart"]:
        path = feature_dir / f"{artifact}.md"
        if path.exists():
            content = path.read_text()
            parts.append(f"## {artifact.upper()}.MD\n\n{content}\n")

    # Load contracts
    contracts_dir = feature_dir / "contracts"
    if contracts_dir.exists():
        for contract_file in sorted(contracts_dir.glob("*.md")):
            parts.append(f"## CONTRACT: {contract_file.stem}\n\n{contract_file.read_text()}\n")

    # Add implementation notes
    if implementation_notes:
        parts.append(f"## DEVELOPER IMPLEMENTATION NOTES\n\n{implementation_notes}\n")
    else:
        parts.append(
            "## DEVELOPER IMPLEMENTATION NOTES\n\n"
            "(No implementation notes provided. Review the spec and plan for internal "
            "consistency and highlight what the developer should verify.)\n"
        )

    parts.append(
        "\n---\nProduce your review now. Format as:\n"
        "1. Summary of what the spec requires\n"
        "2. Gaps found (requirements not addressed)\n"
        "3. Contradictions (spec vs plan vs notes)\n"
        "4. Open questions for the developer\n"
        "5. Follow-up tasks (as a checklist)\n"
        "6. Overall pass/fail assessment\n"
    )

    return "\n".join(parts)
