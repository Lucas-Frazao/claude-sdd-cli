"""Template loading and population utilities."""

from pathlib import Path
from typing import Optional

TEMPLATE_DIR = Path(__file__).parent / "files"
BUNDLED_TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"


def _resolve_template_dir() -> Path:
    """Resolve template directory, preferring bundled templates."""
    if BUNDLED_TEMPLATE_DIR.exists():
        return BUNDLED_TEMPLATE_DIR
    return TEMPLATE_DIR


def load_template(name: str) -> str:
    """Load a markdown template by name (without extension)."""
    template_dir = _resolve_template_dir()
    path = template_dir / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text()


def populate_template(template: str, variables: dict) -> str:
    """Replace {{variable}} placeholders in a template."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def list_templates() -> list[str]:
    """List all available template names."""
    template_dir = _resolve_template_dir()
    if not template_dir.exists():
        return []
    return sorted(p.stem for p in template_dir.glob("*.md"))


def copy_templates_to(target_dir: Path, templates: Optional[list[str]] = None) -> list[Path]:
    """Copy templates to a target directory. Returns list of copied paths."""
    template_dir = _resolve_template_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    if templates is None:
        templates = list_templates()

    copied = []
    for name in templates:
        src = template_dir / f"{name}.md"
        if src.exists():
            dest = target_dir / f"{name}.md"
            dest.write_text(src.read_text())
            copied.append(dest)

    return copied
