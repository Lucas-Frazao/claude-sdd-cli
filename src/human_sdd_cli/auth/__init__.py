"""GitHub Copilot authentication — public API."""

from human_sdd_cli.auth.exceptions import (
    CopilotAuthError,
    CopilotNotEnabledError,
    DeviceFlowExpiredError,
    TokenRefreshError,
)
from human_sdd_cli.auth.token_manager import (
    delete_token,
    get_valid_token,
    has_cached_token,
    load_token,
)

__all__ = [
    "get_copilot_token",
    "has_cached_token",
    "load_token",
    "delete_token",
    "CopilotAuthError",
    "CopilotNotEnabledError",
    "DeviceFlowExpiredError",
    "TokenRefreshError",
]


def get_copilot_token() -> str:
    """Get a valid Copilot API token. Handles refresh transparently."""
    return get_valid_token()
