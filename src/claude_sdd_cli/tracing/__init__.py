"""Traceability layer — links requirements to tasks and implementation."""

from dataclasses import dataclass, field
from pathlib import Path

from claude_sdd_cli.parsers import parse_requirements, parse_tasks, Requirement, Task


@dataclass
class TraceEntry:
    """A single requirement-to-task trace."""
    requirement_id: str
    requirement_text: str
    linked_tasks: list[str] = field(default_factory=list)
    status: str = "unimplemented"  # unimplemented | in-progress | covered


@dataclass
class TraceReport:
    """Full traceability report for a feature."""
    feature: str
    entries: list[TraceEntry] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        if not self.entries:
            return 0.0
        covered = sum(1 for e in self.entries if e.status == "covered")
        return covered / len(self.entries) * 100

    def to_markdown(self) -> str:
        lines = [
            f"# Traceability Report: {self.feature}",
            "",
            f"**Coverage:** {self.coverage:.0f}% ({sum(1 for e in self.entries if e.status == 'covered')}/{len(self.entries)} requirements covered)",
            "",
            "| Requirement | Description | Linked Tasks | Status |",
            "|---|---|---|---|",
        ]
        for entry in self.entries:
            tasks_str = ", ".join(entry.linked_tasks) if entry.linked_tasks else "—"
            lines.append(f"| {entry.requirement_id} | {entry.requirement_text[:60]} | {tasks_str} | {entry.status} |")

        lines.append("")

        # Unimplemented requirements
        unimpl = [e for e in self.entries if e.status == "unimplemented"]
        if unimpl:
            lines.append("## Unimplemented Requirements")
            lines.append("")
            for e in unimpl:
                lines.append(f"- **{e.requirement_id}**: {e.requirement_text}")
            lines.append("")

        return "\n".join(lines)


def build_trace_report(feature_dir: Path, feature_name: str) -> TraceReport:
    """Build a traceability report from spec.md and tasks.md in a feature directory."""
    spec_path = feature_dir / "spec.md"
    tasks_path = feature_dir / "tasks.md"

    requirements = []
    if spec_path.exists():
        requirements = parse_requirements(spec_path.read_text())

    tasks = []
    if tasks_path.exists():
        tasks = parse_tasks(tasks_path.read_text())

    # Build a lookup: requirement_id -> list of task IDs
    req_to_tasks: dict[str, list[str]] = {r.id: [] for r in requirements}
    for task in tasks:
        for req_id in task.traces_to:
            if req_id in req_to_tasks:
                req_to_tasks[req_id].append(task.id)

    entries = []
    for req in requirements:
        linked = req_to_tasks.get(req.id, [])
        if linked:
            done = all(
                t.status == "done"
                for t in tasks
                if t.id in linked
            )
            status = "covered" if done else "in-progress"
        else:
            status = "unimplemented"

        entries.append(TraceEntry(
            requirement_id=req.id,
            requirement_text=req.text,
            linked_tasks=linked,
            status=status,
        ))

    return TraceReport(feature=feature_name, entries=entries)
