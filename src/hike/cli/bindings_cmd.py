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
    apply_runtime_path_overrides,
    config_path_option,
    console,
    env_path_option,
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
    apply_runtime_path_overrides(config_path, env_path)
    for summary in binding_summaries():
        console.print(
            f"[bold]{summary.command_name}[/] [dim]- {summary.tooltip}[/]\n"
            f"    Default: [cyan]{summary.default_key}[/]  "
            f"Current: [green]{summary.current_key}[/]"
        )


### bindings_cmd.py ends here
