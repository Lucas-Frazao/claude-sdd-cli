"""Tests for the traceability layer."""

import tempfile
from pathlib import Path

from claude_sdd_cli.tracing import build_trace_report


class TestTraceReport:
    def _make_feature(self, spec_content: str, tasks_content: str) -> Path:
        """Create a temporary feature directory with spec and tasks."""
        tmpdir = Path(tempfile.mkdtemp())
        feature_dir = tmpdir / "specs" / "001-test"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text(spec_content)
        (feature_dir / "tasks.md").write_text(tasks_content)
        return feature_dir

    def test_full_coverage(self):
        spec = """# Functional Requirements
- REQ-001: User can log in
- REQ-002: User can log out
"""
        tasks = """# Tasks
- [x] TASK-001: Implement login (traces: REQ-001)
- [x] TASK-002: Implement logout (traces: REQ-002)
"""
        feature_dir = self._make_feature(spec, tasks)
        report = build_trace_report(feature_dir, "test")
        assert report.coverage == 100.0
        assert all(e.status == "covered" for e in report.entries)

    def test_partial_coverage(self):
        spec = """# Functional Requirements
- REQ-001: User can log in
- REQ-002: User can log out
- REQ-003: User can reset password
"""
        tasks = """# Tasks
- [x] TASK-001: Implement login (traces: REQ-001)
- [ ] TASK-002: Implement logout (traces: REQ-002)
"""
        feature_dir = self._make_feature(spec, tasks)
        report = build_trace_report(feature_dir, "test")
        # REQ-001 covered, REQ-002 in-progress, REQ-003 unimplemented
        assert report.coverage < 100.0

    def test_no_tasks(self):
        spec = """# Functional Requirements
- REQ-001: Something
"""
        tasks = "# Tasks\nNothing here."
        feature_dir = self._make_feature(spec, tasks)
        report = build_trace_report(feature_dir, "test")
        assert report.coverage == 0.0
        assert report.entries[0].status == "unimplemented"

    def test_markdown_output(self):
        spec = """# Functional Requirements
- REQ-001: User can log in
"""
        tasks = """# Tasks
- [x] TASK-001: Implement login (traces: REQ-001)
"""
        feature_dir = self._make_feature(spec, tasks)
        report = build_trace_report(feature_dir, "test")
        md = report.to_markdown()
        assert "# Traceability Report" in md
        assert "REQ-001" in md
        assert "100%" in md
