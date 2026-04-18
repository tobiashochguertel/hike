"""Binding-related CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Typer imports.
import typer

##############################################################################
# Local imports.
from .common import (
    console,
    runtime_context_from_typer_context,
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
    ctx: typer.Context,
) -> None:
    """List commands that support keybinding overrides."""
    runtime_context = runtime_context_from_typer_context(ctx)
    for summary in binding_summaries(runtime_context):
        console.print(
            f"[bold]{summary.command_name}[/] [dim]- {summary.tooltip}[/]\n"
            f"    Default: [cyan]{summary.default_key}[/]  "
            f"Current: [green]{summary.current_key}[/]"
        )


### bindings_cmd.py ends here
