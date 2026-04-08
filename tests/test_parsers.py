"""Tests for the markdown artifact parsers."""

from claude_sdd_cli.parsers import (
    parse_requirements,
    parse_tasks,
    find_open_questions,
)


class TestParseRequirements:
    def test_explicit_req_ids(self):
        text = """# Functional Requirements
- REQ-001: The system must authenticate users via email
- REQ-002: The system must support password reset [NEEDS CLARIFICATION]
- REQ-003: The system must log all authentication attempts
"""
        reqs = parse_requirements(text)
        assert len(reqs) == 3
        assert reqs[0].id == "REQ-001"
        assert reqs[0].text == "The system must authenticate users via email"
        assert not reqs[0].needs_clarification
        assert reqs[1].needs_clarification

    def test_generic_list_items_under_requirement_heading(self):
        text = """# Functional Requirements
- Users must be able to sign up
- Users must be able to log in
- Users must be able to log out

# Something Else
- This should not be captured
"""
        reqs = parse_requirements(text)
        assert len(reqs) == 3
        assert reqs[0].id == "REQ-001"

    def test_empty_spec(self):
        reqs = parse_requirements("")
        assert len(reqs) == 0


class TestParseTasks:
    def test_checklist_with_traces(self):
        text = """# Tasks
- [ ] TASK-001: Set up project structure (traces: REQ-001, REQ-002)
- [x] TASK-002: Create database schema (traces: REQ-003)
- [ ] TASK-003: Implement auth flow (traces: REQ-001)
"""
        tasks = parse_tasks(text)
        assert len(tasks) == 3
        assert tasks[0].id == "TASK-001"
        assert tasks[0].status == "pending"
        assert tasks[0].traces_to == ["REQ-001", "REQ-002"]
        assert tasks[1].status == "done"
        assert tasks[2].traces_to == ["REQ-001"]

    def test_no_tasks(self):
        tasks = parse_tasks("# Nothing here\nJust prose.")
        assert len(tasks) == 0


class TestFindOpenQuestions:
    def test_finds_markers(self):
        text = """# Spec
Line one is fine.
Line two has [NEEDS CLARIFICATION] in it.
Line three is fine.
Another [NEEDS CLARIFICATION] here.
"""
        results = find_open_questions(text)
        assert len(results) == 2
        assert results[0][0] == 3  # line number
        assert "[NEEDS CLARIFICATION]" in results[0][1]

    def test_no_markers(self):
        results = find_open_questions("Everything is clear.")
        assert len(results) == 0
