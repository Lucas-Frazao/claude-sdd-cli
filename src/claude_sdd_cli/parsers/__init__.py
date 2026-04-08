"""Parsers for reading structured markdown artifacts."""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Requirement:
    """A single requirement extracted from a spec."""
    id: str
    text: str
    needs_clarification: bool = False


@dataclass
class Task:
    """A single task extracted from tasks.md."""
    id: str
    text: str
    status: str = "pending"  # pending | done
    traces_to: list[str] = field(default_factory=list)  # requirement IDs


def parse_requirements(spec_text: str) -> list[Requirement]:
    """Extract requirements from a spec.md file.

    Looks for lines starting with '- REQ-' or numbered list items under
    Functional/Non-functional Requirements headings.
    """
    requirements = []
    req_pattern = re.compile(r"^[-*]\s+(REQ-\d+)\s*[:\-]\s*(.+)$", re.MULTILINE)

    for match in req_pattern.finditer(spec_text):
        req_id = match.group(1)
        text = match.group(2).strip()
        needs_clarification = "[NEEDS CLARIFICATION]" in text
        requirements.append(Requirement(id=req_id, text=text, needs_clarification=needs_clarification))

    # Also capture generic numbered items under requirement headings
    if not requirements:
        in_req_section = False
        counter = 1
        for line in spec_text.splitlines():
            if re.match(r"^#+\s*.*(requirement|criteria).*$", line, re.IGNORECASE):
                in_req_section = True
                continue
            if re.match(r"^#+\s+", line) and in_req_section:
                in_req_section = False
                continue
            if in_req_section:
                item = re.match(r"^[-*\d.]+\s+(.+)$", line)
                if item:
                    text = item.group(1).strip()
                    needs_clarification = "[NEEDS CLARIFICATION]" in text
                    requirements.append(Requirement(
                        id=f"REQ-{counter:03d}",
                        text=text,
                        needs_clarification=needs_clarification,
                    ))
                    counter += 1

    return requirements


def parse_tasks(tasks_text: str) -> list[Task]:
    """Extract tasks from a tasks.md file.

    Looks for checklist items: - [ ] TASK-001: description
    """
    tasks = []
    task_pattern = re.compile(
        r"^[-*]\s+\[([ xX])\]\s+(TASK-\d+)\s*[:\-]\s*(.+)$",
        re.MULTILINE,
    )

    for match in task_pattern.finditer(tasks_text):
        done = match.group(1).lower() == "x"
        task_id = match.group(2)
        text = match.group(3).strip()

        # Extract trace references like (traces: REQ-001, REQ-002)
        trace_match = re.search(r"\(traces?:\s*([^)]+)\)", text)
        traces = []
        if trace_match:
            traces = [t.strip() for t in trace_match.group(1).split(",")]
            text = text[:trace_match.start()].strip()

        tasks.append(Task(
            id=task_id,
            text=text,
            status="done" if done else "pending",
            traces_to=traces,
        ))

    return tasks


def find_open_questions(text: str) -> list[tuple[int, str]]:
    """Find all [NEEDS CLARIFICATION] markers in text. Returns (line_number, line)."""
    results = []
    for i, line in enumerate(text.splitlines(), start=1):
        if "[NEEDS CLARIFICATION]" in line:
            results.append((i, line.strip()))
    return results


def load_feature_artifact(feature_dir: Path, artifact: str) -> str:
    """Load a named artifact (spec, plan, tasks, etc.) from a feature directory."""
    path = feature_dir / f"{artifact}.md"
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return path.read_text()
