"""Tests for the no-code validator."""

from claude_sdd_cli.validators import validate_no_code


class TestCodeFenceDetection:
    def test_clean_prose_passes(self):
        text = """# My Plan

This is a clean plan with no code. It describes architecture in prose.

## Data Model

| Entity | Attributes | Description |
|--------|-----------|-------------|
| User   | name, email | A registered user |

The system should handle errors gracefully.
"""
        result = validate_no_code(text)
        assert result.passed
        assert len(result.violations) == 0

    def test_python_code_fence_fails(self):
        text = """# Plan

Here is some code:

```python
def hello():
    print("world")
```

End of plan.
"""
        result = validate_no_code(text)
        assert not result.passed
        assert result.error_count >= 1
        assert any(v.rule == "no-code-fences" for v in result.violations)

    def test_javascript_code_fence_fails(self):
        text = """```javascript
const x = 42;
```"""
        result = validate_no_code(text)
        assert not result.passed

    def test_bash_code_fence_fails(self):
        text = """```bash
pip install something
```"""
        result = validate_no_code(text)
        assert not result.passed

    def test_sql_code_fence_fails(self):
        text = """```sql
SELECT * FROM users;
```"""
        result = validate_no_code(text)
        assert not result.passed

    def test_unlabeled_code_fence_passes(self):
        """Unlabeled code fences (no language tag) are allowed for prose formatting."""
        text = """```
This is just a text block, not code.
```"""
        result = validate_no_code(text)
        assert result.passed

    def test_unclosed_code_fence_fails(self):
        text = """```python
def broken():
    pass
"""
        result = validate_no_code(text)
        assert not result.passed


class TestExecutableLineDetection:
    def test_python_import_fails(self):
        text = "import os\n"
        result = validate_no_code(text)
        assert not result.passed
        assert any("import" in v.detail.lower() for v in result.violations)

    def test_python_from_import_fails(self):
        text = "from pathlib import Path\n"
        result = validate_no_code(text)
        assert not result.passed

    def test_python_function_def_fails(self):
        text = "def my_function(arg1, arg2):\n"
        result = validate_no_code(text)
        assert not result.passed

    def test_python_class_def_fails(self):
        text = "class MyClass:\n"
        result = validate_no_code(text)
        assert not result.passed

    def test_js_const_fails(self):
        text = "const router = express.Router()\n"
        result = validate_no_code(text)
        assert not result.passed

    def test_sql_statement_fails(self):
        text = "SELECT id, name FROM users WHERE active = true\n"
        result = validate_no_code(text)
        assert not result.passed

    def test_shebang_fails(self):
        text = "#!/usr/bin/env python3\n"
        result = validate_no_code(text)
        assert not result.passed

    def test_normal_prose_passes(self):
        text = """The developer should implement a function that validates user input.
This function should accept a string and return a boolean indicating validity.
Consider edge cases such as empty strings and very long inputs.
"""
        result = validate_no_code(text)
        assert result.passed

    def test_pip_install_fails(self):
        text = "pip install flask\n"
        result = validate_no_code(text)
        assert not result.passed


class TestConfigDetection:
    def test_package_json_scripts_fails_strict(self):
        text = '  "scripts": {\n'
        result = validate_no_code(text, strict=True)
        assert not result.passed

    def test_package_json_scripts_warns_lenient(self):
        text = '  "scripts": {\n'
        result = validate_no_code(text, strict=False)
        assert result.passed  # warnings don't fail
        assert result.warning_count >= 1

    def test_pyproject_section_fails_strict(self):
        text = "[tool.pytest]\n"
        result = validate_no_code(text, strict=True)
        assert not result.passed

    def test_dockerfile_directive_fails(self):
        text = "RUN apt-get update\n"
        result = validate_no_code(text)
        assert not result.passed


class TestValidationResult:
    def test_summary_passed(self):
        result = validate_no_code("Just prose here.")
        assert "PASSED" in result.summary()

    def test_summary_failed(self):
        result = validate_no_code("import os\n")
        assert "FAILED" in result.summary()

    def test_multiple_violations(self):
        text = """import os
def main():
    pass
class App:
    pass
"""
        result = validate_no_code(text)
        assert not result.passed
        assert result.error_count >= 3
