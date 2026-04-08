"""sdd check-no-code — Validate that AI artifacts contain no executable code."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from claude_sdd_cli.validators import validate_no_code

console = Console()


@click.command()
@click.option("--feature", "-f", default=None, help="Feature name (scans its folder).")
@click.option("--file", "target_file", default=None, type=click.Path(exists=True), help="Single file to scan.")
@click.option("--path", "-p", default=".", help="Project root directory.")
@click.option("--strict/--lenient", default=True, help="Strict mode treats config fragments as errors.")
def check_no_code_cmd(feature: str, target_file: str, path: str, strict: bool):
    """Validate that AI-generated artifacts contain no executable code."""
    root = Path(path).resolve()
    files_to_check: list[Path] = []

    if target_file:
        files_to_check.append(Path(target_file).resolve())
    elif feature:
        specs_dir = root / "specs"
        feature_dir = None
        for d in sorted(specs_dir.iterdir()):
            if d.is_dir() and feature in d.name:
                feature_dir = d
                break
        if not feature_dir:
            raise click.ClickException(f"Feature not found: {feature}")
        files_to_check.extend(sorted(feature_dir.rglob("*.md")))
    else:
        # Scan all specs
        specs_dir = root / "specs"
        if specs_dir.exists():
            files_to_check.extend(sorted(specs_dir.rglob("*.md")))

    if not files_to_check:
        console.print("[yellow]No files to check.[/]")
        return

    console.print(Panel(
        f"[bold cyan]Checking {len(files_to_check)} file(s) for code violations[/]",
        title="sdd check-no-code",
    ))

    total_errors = 0
    total_warnings = 0

    for file_path in files_to_check:
        content = file_path.read_text()
        result = validate_no_code(content, strict=strict)

        rel = file_path.relative_to(root) if file_path.is_relative_to(root) else file_path

        if result.passed and not result.violations:
            console.print(f"  [green]✓[/] {rel}")
        elif result.passed:
            console.print(f"  [yellow]●[/] {rel} ({result.warning_count} warning(s))")
            total_warnings += result.warning_count
        else:
            console.print(f"  [red]✗[/] {rel} ({result.error_count} error(s), {result.warning_count} warning(s))")
            total_errors += result.error_count
            total_warnings += result.warning_count

            # Show violation details
            table = Table(show_header=True, box=None, padding=(0, 1))
            table.add_column("Line", style="yellow", justify="right")
            table.add_column("Rule", style="red")
            table.add_column("Detail", style="white")
            for v in result.violations:
                table.add_row(str(v.line_number), v.rule, v.detail)
            console.print(table)

    # Summary
    console.print()
    if total_errors == 0:
        console.print(
            f"[bold green]PASSED[/] — {len(files_to_check)} file(s) checked, "
            f"{total_warnings} warning(s)"
        )
    else:
        console.print(
            f"[bold red]FAILED[/] — {total_errors} error(s), "
            f"{total_warnings} warning(s) across {len(files_to_check)} file(s)"
        )
        raise SystemExit(1)
