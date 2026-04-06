"""sdd auth — Manage GitHub Copilot authentication."""

import time

import click
from rich.console import Console

console = Console()


@click.group()
def auth_cmd():
    """Manage GitHub Copilot authentication."""


@auth_cmd.command("login")
def auth_login():
    """Authenticate with GitHub Copilot via device flow."""
    from human_sdd_cli.auth.device_flow import run_device_flow
    from human_sdd_cli.auth.exceptions import CopilotAuthError
    from human_sdd_cli.auth.token_manager import save_token

    try:
        oauth_token, copilot_data = run_device_flow()
        save_token(oauth_token, copilot_data["token"], copilot_data["expires_at"])
        console.print("[bold green]Logged in successfully.[/bold green] Token stored.")
    except CopilotAuthError as e:
        console.print(f"[bold red]Authentication failed:[/bold red] {e}")
        raise SystemExit(1)


@auth_cmd.command("status")
def auth_status():
    """Show current authentication status."""
    from human_sdd_cli.auth.token_manager import load_token, is_copilot_token_valid

    token_data = load_token()
    if token_data is None:
        console.print("[yellow]Not authenticated.[/yellow] Run [bold]sdd auth login[/bold] to authenticate.")
        return

    if is_copilot_token_valid(token_data):
        expires_at = token_data.get("copilot_token_expires_at", 0)
        remaining = int(expires_at - time.time())
        minutes = remaining // 60
        seconds = remaining % 60
        console.print(f"[bold green]Authenticated.[/bold green] Copilot token expires in {minutes}m {seconds}s.")
    else:
        console.print(
            "[yellow]Copilot token expired.[/yellow] "
            "It will be refreshed automatically on next use."
        )

    created = token_data.get("created_at")
    if created:
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(created, tz=timezone.utc)
        console.print(f"[dim]Token originally obtained: {dt:%Y-%m-%d %H:%M:%S UTC}[/dim]")


@auth_cmd.command("logout")
def auth_logout():
    """Remove stored Copilot credentials."""
    from human_sdd_cli.auth.token_manager import delete_token

    if delete_token():
        console.print("[green]Logged out.[/green] Stored credentials removed.")
    else:
        console.print("[yellow]No stored credentials found.[/yellow]")
