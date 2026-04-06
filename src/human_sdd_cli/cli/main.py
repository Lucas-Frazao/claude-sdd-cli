"""Main CLI entry point for the Human-Authored SDD tool."""

import click

from human_sdd_cli import __version__
from human_sdd_cli.commands.init_cmd import init_cmd
from human_sdd_cli.commands.specify_cmd import specify_cmd
from human_sdd_cli.commands.plan_cmd import plan_cmd
from human_sdd_cli.commands.tasks_cmd import tasks_cmd
from human_sdd_cli.commands.review_cmd import review_cmd
from human_sdd_cli.commands.clarify_cmd import clarify_cmd
from human_sdd_cli.commands.trace_cmd import trace_cmd
from human_sdd_cli.commands.check_no_code_cmd import check_no_code_cmd
from human_sdd_cli.commands.auth_cmd import auth_cmd


@click.group()
@click.version_option(version=__version__, prog_name="sdd")
def cli():
    """Human-Authored Specification-Driven Development CLI.

    A planning copilot that helps you write specs, plans, and tasks —
    while YOU write every line of code.
    """


cli.add_command(init_cmd, "init")
cli.add_command(specify_cmd, "specify")
cli.add_command(plan_cmd, "plan")
cli.add_command(tasks_cmd, "tasks")
cli.add_command(review_cmd, "review")
cli.add_command(clarify_cmd, "clarify")
cli.add_command(trace_cmd, "trace")
cli.add_command(check_no_code_cmd, "check-no-code")
cli.add_command(auth_cmd, "auth")


if __name__ == "__main__":
    cli()
