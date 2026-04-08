"""Validation layer — enforces the no-code constitution."""

import re
from dataclasses import dataclass, field


@dataclass
class Violation:
    """A single policy violation found in AI output."""
    line_number: int
    line_content: str
    rule: str
    severity: str  # "error" or "warning"
    detail: str


@dataclass
class ValidationResult:
    """Result of a no-code validation scan."""
    passed: bool
    violations: list[Violation] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warning")

    def summary(self) -> str:
        if self.passed:
            return "PASSED — no executable code detected."
        lines = [f"FAILED — {self.error_count} error(s), {self.warning_count} warning(s)"]
        for v in self.violations:
            lines.append(
                f"  [{v.severity.upper()}] Line {v.line_number}: {v.rule}\n"
                f"    > {v.line_content.strip()[:120]}\n"
                f"    {v.detail}"
            )
        return "\n".join(lines)


# ── Detection patterns ───────────────────────────────────────────────

# Fenced code blocks: ```python, ```js, ```bash, etc.
_CODE_FENCE_OPEN = re.compile(
    r"^```\s*(python|javascript|typescript|js|ts|java|c|cpp|c\+\+|csharp|cs|"
    r"go|rust|ruby|php|swift|kotlin|scala|bash|sh|zsh|shell|powershell|sql|"
    r"html|css|yaml|yml|json|toml|xml|dockerfile|makefile|hcl|terraform|lua|"
    r"perl|r|dart|elixir|clojure|groovy|zig|nim|v|jsx|tsx)\s*$",
    re.IGNORECASE,
)
_CODE_FENCE_CLOSE = re.compile(r"^```\s*$")

# Highly executable single-line patterns
_EXECUTABLE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^\s*import\s+\w+"), "Python import statement"),
    (re.compile(r"^\s*from\s+\w+\s+import\s+"), "Python from-import statement"),
    (re.compile(r"^\s*def\s+\w+\s*\("), "Python function definition"),
    (re.compile(r"^\s*class\s+\w+[\s(:]"), "Python/Java class definition"),
    (re.compile(r"^\s*(const|let|var)\s+\w+\s*="), "JavaScript variable declaration"),
    (re.compile(r"^\s*function\s+\w+\s*\("), "JavaScript function definition"),
    (re.compile(r"^\s*(pub\s+)?fn\s+\w+"), "Rust function definition"),
    (re.compile(r"^\s*func\s+\w+"), "Go function definition"),
    (re.compile(r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s+", re.IGNORECASE), "SQL statement"),
    (re.compile(r"^\s*#!\s*/"), "Shebang line"),
    (re.compile(r"^\s*(RUN|CMD|ENTRYPOINT|COPY|ADD)\s+", re.IGNORECASE), "Dockerfile directive"),
    (re.compile(r"^\s*FROM\s+\S+:\S+"), "Dockerfile FROM directive"),
    (re.compile(r"^\s*FROM\s+\S+\s+AS\s+", re.IGNORECASE), "Dockerfile multi-stage FROM"),
    (re.compile(r"^\s*\$\s+\w+"), "Shell command"),
    (re.compile(r"^\s*(pip|npm|yarn|cargo|go)\s+(install|add|build|run)\s+"), "Package manager command"),
    (re.compile(r"^\s*@(app|router|blueprint)\.(get|post|put|delete|patch)\s*\("), "Web framework route"),
]

# Config-file fragments
_CONFIG_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'^\s*"(scripts|dependencies|devDependencies)"\s*:'), "package.json fragment"),
    (re.compile(r"^\s*\[tool\.\w+\]"), "pyproject.toml section"),
    (re.compile(r"^\s*services:\s*$"), "docker-compose fragment"),
    (re.compile(r"^\s*apiVersion:\s*"), "Kubernetes manifest"),
    (re.compile(r"^\s*resource\s+\""), "Terraform resource block"),
]


def validate_no_code(text: str, *, strict: bool = True) -> ValidationResult:
    """Scan *text* for executable code. Returns a ValidationResult.

    Parameters
    ----------
    text : str
        The AI-generated artifact content.
    strict : bool
        If True, config fragments are errors. If False, they are warnings.
    """
    violations: list[Violation] = []
    lines = text.splitlines()
    in_code_block = False
    code_block_start = 0

    for i, line in enumerate(lines, start=1):
        # ── Code fence detection ──
        if not in_code_block and _CODE_FENCE_OPEN.match(line):
            in_code_block = True
            code_block_start = i
            violations.append(Violation(
                line_number=i,
                line_content=line,
                rule="no-code-fences",
                severity="error",
                detail="Fenced code block with a language tag detected.",
            ))
            continue

        if in_code_block:
            if _CODE_FENCE_CLOSE.match(line):
                in_code_block = False
            continue  # skip content inside fences — the fence itself is the violation

        # ── Executable single-line patterns ──
        for pattern, description in _EXECUTABLE_PATTERNS:
            if pattern.match(line):
                violations.append(Violation(
                    line_number=i,
                    line_content=line,
                    rule="no-executable-lines",
                    severity="error",
                    detail=f"Detected: {description}",
                ))
                break  # one violation per line is enough

        # ── Config fragments ──
        for pattern, description in _CONFIG_PATTERNS:
            if pattern.match(line):
                violations.append(Violation(
                    line_number=i,
                    line_content=line,
                    rule="no-config-fragments",
                    severity="error" if strict else "warning",
                    detail=f"Detected: {description}",
                ))
                break

    # Unclosed code block
    if in_code_block:
        violations.append(Violation(
            line_number=code_block_start,
            line_content=lines[code_block_start - 1],
            rule="no-code-fences",
            severity="error",
            detail="Code block opened but never closed.",
        ))

    passed = all(v.severity != "error" for v in violations)
    return ValidationResult(passed=passed, violations=violations)
