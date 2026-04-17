"""Binding-related CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

from operator import attrgetter
from pathlib import Path

##############################################################################
# Typer imports.
import typer

##############################################################################
# Local imports.
from ..data import load_configuration
from ..screens import Main
from .common import (
    apply_runtime_path_overrides,
    config_path_option,
    console,
    env_path_option,
)

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
    overrides = load_configuration().bindings
    for command in sorted(Main.COMMAND_MESSAGES, key=attrgetter("__name__")):
        if command().has_binding:
            current = overrides.get(command.__name__, command.binding().key)
            console.print(
                f"[bold]{command.__name__}[/] [dim]- {command.tooltip()}[/]\n"
                f"    Default: [cyan]{command.binding().key}[/]  "
                f"Current: [green]{current}[/]"
            )


### bindings_cmd.py ends here
