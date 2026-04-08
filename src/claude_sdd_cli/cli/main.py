"""Main CLI entry point for the Claude SDD tool."""

import click

from claude_sdd_cli import __version__
from claude_sdd_cli.commands.init_cmd import init_cmd
from claude_sdd_cli.commands.product_vision_cmd import product_vision_cmd
from claude_sdd_cli.commands.feature_roadmap_cmd import feature_roadmap_cmd
from claude_sdd_cli.commands.specify_cmd import specify_cmd
from claude_sdd_cli.commands.plan_cmd import plan_cmd
from claude_sdd_cli.commands.tasks_cmd import tasks_cmd
from claude_sdd_cli.commands.review_cmd import review_cmd
from claude_sdd_cli.commands.clarify_cmd import clarify_cmd
from claude_sdd_cli.commands.trace_cmd import trace_cmd
from claude_sdd_cli.commands.tech_stack_cmd import tech_stack_cmd
from claude_sdd_cli.commands.architecture_cmd import architecture_cmd


@click.group()
@click.version_option(version=__version__, prog_name="sdd")
def cli():
    """Claude SDD -- Specification-Driven Development CLI.

    A planning copilot that helps write specs, plans, and tasks —
    then Claude CLI implements them.
    """


cli.add_command(init_cmd, "init")
cli.add_command(product_vision_cmd, "vision")
cli.add_command(tech_stack_cmd, "tech-stack")
cli.add_command(architecture_cmd, "architecture")
cli.add_command(feature_roadmap_cmd, "roadmap")
cli.add_command(specify_cmd, "specify")
cli.add_command(plan_cmd, "plan")
cli.add_command(tasks_cmd, "tasks")
cli.add_command(review_cmd, "review")
cli.add_command(clarify_cmd, "clarify")
cli.add_command(trace_cmd, "trace")


if __name__ == "__main__":
    cli()
