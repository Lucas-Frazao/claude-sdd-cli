"""Token persistence, caching, and automatic refresh for Copilot auth."""

import json
import os
import stat
import time
from pathlib import Path
from typing import Optional

from human_sdd_cli.auth.exceptions import CopilotAuthError, TokenRefreshError

TOKEN_DIR = Path.home() / ".config" / "human-sdd-cli"
TOKEN_FILE = TOKEN_DIR / "copilot-token.json"

# Copilot tokens expire in ~25 minutes; refresh 2 minutes early
_EXPIRY_BUFFER_SECONDS = 120


def _ensure_token_dir() -> None:
    """Create the token directory with restrictive permissions."""
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)


def save_token(oauth_token: str, copilot_token: str, expires_at: int) -> None:
    """Persist tokens to disk with secure file permissions."""
    _ensure_token_dir()
    data = {
        "oauth_token": oauth_token,
        "copilot_token": copilot_token,
        "copilot_token_expires_at": expires_at,
        "created_at": int(time.time()),
    }
    TOKEN_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 0600


def load_token() -> Optional[dict]:
    """Load cached tokens from disk. Returns None if no cache exists."""
    if not TOKEN_FILE.exists():
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text())
        if "oauth_token" not in data or "copilot_token" not in data:
            return None
        return data
    except (json.JSONDecodeError, KeyError):
        return None


def delete_token() -> bool:
    """Delete the cached token file. Returns True if a file was deleted."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        return True
    return False


def is_copilot_token_valid(token_data: dict) -> bool:
    """Check if the cached Copilot token is still valid."""
    expires_at = token_data.get("copilot_token_expires_at", 0)
    return time.time() < (expires_at - _EXPIRY_BUFFER_SECONDS)


def has_cached_token() -> bool:
    """Check if a cached token file exists (regardless of validity)."""
    return TOKEN_FILE.exists() and load_token() is not None


def get_valid_token() -> str:
    """Get a valid Copilot API token, refreshing or re-authenticating as needed.

    Returns the Copilot bearer token string.
    """
    # Lazy import to avoid circular dependencies
    from human_sdd_cli.auth.device_flow import exchange_for_copilot_token, run_device_flow

    token_data = load_token()

    if token_data is not None:
        # Case 1: Copilot token is still valid
        if is_copilot_token_valid(token_data):
            return token_data["copilot_token"]

        # Case 2: Copilot token expired but OAuth token may still work
        try:
            copilot_data = exchange_for_copilot_token(token_data["oauth_token"])
            save_token(
                token_data["oauth_token"],
                copilot_data["token"],
                copilot_data["expires_at"],
            )
            return copilot_data["token"]
        except CopilotAuthError:
            # OAuth token is also invalid; fall through to full re-auth
            pass

    # Case 3: No token or all tokens invalid — run full device flow
    try:
        oauth_token, copilot_data = run_device_flow()
        save_token(oauth_token, copilot_data["token"], copilot_data["expires_at"])
        return copilot_data["token"]
    except CopilotAuthError as e:
        raise TokenRefreshError(f"Failed to authenticate with Copilot: {e}") from e


def force_refresh() -> str:
    """Force a token refresh, ignoring cached validity.

    Tries to re-exchange the OAuth token first, then falls back to device flow.
    """
    from human_sdd_cli.auth.device_flow import exchange_for_copilot_token, run_device_flow

    token_data = load_token()

    if token_data is not None:
        try:
            copilot_data = exchange_for_copilot_token(token_data["oauth_token"])
            save_token(
                token_data["oauth_token"],
                copilot_data["token"],
                copilot_data["expires_at"],
            )
            return copilot_data["token"]
        except CopilotAuthError:
            pass

    oauth_token, copilot_data = run_device_flow()
    save_token(oauth_token, copilot_data["token"], copilot_data["expires_at"])
    return copilot_data["token"]
