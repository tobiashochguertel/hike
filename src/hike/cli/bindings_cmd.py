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
from .services import binding_summaries, keybinding_set_summaries

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
    active_set = next(
        summary.name
        for summary in keybinding_set_summaries(runtime_context)
        if summary.active
    )
    console.print(f"[dim]Active binding set:[/] [bold]{active_set}[/]\n")
    for summary in binding_summaries(runtime_context):
        console.print(
            f"[bold]{summary.command_name}[/] [dim]- {summary.tooltip}[/]\n"
            f"    Default: [cyan]{summary.default_key}[/]  "
            f"Current: [green]{summary.current_key}[/]"
        )


##############################################################################
@app.command("sets")
def list_binding_sets(
    ctx: typer.Context,
) -> None:
    """List the built-in and custom keybinding sets."""
    runtime_context = runtime_context_from_typer_context(ctx)
    for summary in keybinding_set_summaries(runtime_context):
        active = " [green](active)[/]" if summary.active else ""
        console.print(f"[bold]{summary.name}[/]{active} [dim]- {summary.source}[/]")


### bindings_cmd.py ends here
