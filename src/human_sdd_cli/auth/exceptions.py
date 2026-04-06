"""Auth-specific exceptions for GitHub Copilot authentication."""


class CopilotAuthError(Exception):
    """Base exception for Copilot authentication errors."""


class DeviceFlowExpiredError(CopilotAuthError):
    """User did not complete device flow in time."""


class TokenRefreshError(CopilotAuthError):
    """OAuth token is no longer valid and needs re-authentication."""


class CopilotNotEnabledError(CopilotAuthError):
    """GitHub account does not have an active Copilot subscription."""
