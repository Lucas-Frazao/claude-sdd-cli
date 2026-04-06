"""Configuration system — merges project and user config files."""

import sys
from pathlib import Path
from typing import Any

# Use built-in tomllib on 3.11+, tomli on 3.10
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


USER_CONFIG_DIR = Path.home() / ".config" / "human-sdd-cli"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.toml"


def _read_toml(path: Path) -> dict[str, Any]:
    """Read a TOML file and return its contents as a dict."""
    if tomllib is None:
        return {}
    if not path.exists():
        return {}
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(root: Path | None = None) -> dict[str, Any]:
    """Load merged configuration from user and project config files.

    Precedence (lowest to highest):
      1. Built-in defaults (empty)
      2. User config: ~/.config/human-sdd-cli/config.toml
      3. Project config: <root>/.sdd/config.toml

    CLI flags and env vars are applied by the caller and take precedence
    over everything returned here.
    """
    config: dict[str, Any] = {}

    # User-level config
    user_config = _read_toml(USER_CONFIG_FILE)
    config = _deep_merge(config, user_config)

    # Project-level config
    if root is not None:
        project_config_path = Path(root) / ".sdd" / "config.toml"
        project_config = _read_toml(project_config_path)
        config = _deep_merge(config, project_config)

    return config
