"""Binding-related CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

from pathlib import Path

##############################################################################
# Typer imports.
import typer

##############################################################################
# Local imports.
from .common import (
    config_path_option,
    console,
    env_path_option,
    resolve_cli_runtime_context,
)
from .services import binding_summaries

##############################################################################
app = typer.Typer(
    help="Inspect configurable keybindings.",
    add_completion=True,
    no_args_is_help=True,
)


##############################################################################
@app.command("list")
def list_bindings(
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """List commands that support keybinding overrides."""
    runtime_context = resolve_cli_runtime_context(config_path, env_path)
    for summary in binding_summaries(runtime_context):
        console.print(
            f"[bold]{summary.command_name}[/] [dim]- {summary.tooltip}[/]\n"
            f"    Default: [cyan]{summary.default_key}[/]  "
            f"Current: [green]{summary.current_key}[/]"
        )


### bindings_cmd.py ends here
