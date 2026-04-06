"""GitHub Device Flow OAuth for Copilot authentication."""

import os
import time
import webbrowser

import requests
from rich.console import Console

from human_sdd_cli.auth.exceptions import (
    CopilotAuthError,
    CopilotNotEnabledError,
    DeviceFlowExpiredError,
)

GITHUB_DEVICE_CODE_URL = "https://github.com/login/device/code"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"

DEFAULT_CLIENT_ID = "Iv1.b507a08c87ecfe98"

_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "user-agent": "GithubCopilot/1.155.0",
    "editor-version": "Neovim/0.6.1",
    "editor-plugin-version": "copilot.vim/1.16.0",
}

console = Console()


def get_client_id() -> str:
    """Return the OAuth client ID, configurable via env var."""
    return os.environ.get("SDD_COPILOT_CLIENT_ID", DEFAULT_CLIENT_ID)


def request_device_code(client_id: str | None = None) -> dict:
    """Request a device code from GitHub.

    Returns dict with: device_code, user_code, verification_uri, expires_in, interval.
    """
    cid = client_id or get_client_id()
    resp = requests.post(
        GITHUB_DEVICE_CODE_URL,
        headers=_HEADERS,
        json={"client_id": cid, "scope": "read:user"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "device_code" not in data:
        raise CopilotAuthError(f"Unexpected response from device code endpoint: {data}")
    return data


def poll_for_access_token(
    device_code: str, interval: int = 5, expires_in: int = 900, client_id: str | None = None
) -> str:
    """Poll GitHub until the user completes auth. Returns the OAuth access token."""
    cid = client_id or get_client_id()
    deadline = time.monotonic() + expires_in

    while time.monotonic() < deadline:
        time.sleep(interval)
        resp = requests.post(
            GITHUB_TOKEN_URL,
            headers=_HEADERS,
            json={
                "client_id": cid,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if "access_token" in data:
            return data["access_token"]

        error = data.get("error", "")
        if error == "authorization_pending":
            continue
        elif error == "slow_down":
            interval = data.get("interval", interval + 5)
            continue
        elif error == "expired_token":
            raise DeviceFlowExpiredError("Device code expired. Please try again.")
        elif error == "access_denied":
            raise CopilotAuthError("Authorization was denied by the user.")
        else:
            raise CopilotAuthError(f"Unexpected error during polling: {error}")

    raise DeviceFlowExpiredError("Device flow timed out. Please try again.")


def exchange_for_copilot_token(oauth_token: str) -> dict:
    """Exchange an OAuth token for a Copilot session token.

    Returns dict with: token, expires_at (epoch seconds).
    """
    resp = requests.get(
        COPILOT_TOKEN_URL,
        headers={
            "authorization": f"token {oauth_token}",
            "user-agent": "GithubCopilot/1.155.0",
            "editor-version": "Neovim/0.6.1",
            "editor-plugin-version": "copilot.vim/1.16.0",
        },
        timeout=30,
    )

    if resp.status_code == 401:
        raise CopilotAuthError("OAuth token is invalid or expired. Please re-authenticate.")
    if resp.status_code == 403:
        raise CopilotNotEnabledError(
            "GitHub Copilot is not enabled for this account. "
            "Ensure you have an active Copilot subscription."
        )
    resp.raise_for_status()

    data = resp.json()
    if "token" not in data:
        raise CopilotAuthError(f"Unexpected response from Copilot token endpoint: {data}")
    return {"token": data["token"], "expires_at": data.get("expires_at", 0)}


def run_device_flow(client_id: str | None = None) -> tuple[str, dict]:
    """Run the full device flow interactively.

    Returns (oauth_token, copilot_token_data).
    copilot_token_data has keys: token, expires_at.
    """
    cid = client_id or get_client_id()

    # Step 1: Request device code
    device_data = request_device_code(cid)
    user_code = device_data["user_code"]
    verification_uri = device_data["verification_uri"]
    interval = device_data.get("interval", 5)
    expires_in = device_data.get("expires_in", 900)

    # Step 2: Display code and open browser
    console.print()
    console.print(f"[bold]Open [cyan]{verification_uri}[/cyan] and enter code: [yellow]{user_code}[/yellow][/bold]")
    console.print()

    try:
        webbrowser.open(verification_uri)
    except Exception:
        pass  # Browser opening is best-effort

    console.print("[dim]Waiting for authorization...[/dim]")

    # Step 3: Poll for access token
    oauth_token = poll_for_access_token(
        device_data["device_code"], interval=interval, expires_in=expires_in, client_id=cid
    )

    # Step 4: Exchange for Copilot token
    copilot_data = exchange_for_copilot_token(oauth_token)

    console.print("[bold green]Authentication successful![/bold green]")
    return oauth_token, copilot_data
