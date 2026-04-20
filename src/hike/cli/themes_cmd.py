"""Theme-related CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Typer imports.
import typer

##############################################################################
# Local imports.
from .services import theme_names

##############################################################################
app = typer.Typer(
    help="Inspect available Textual themes.",
    add_completion=True,
    no_args_is_help=True,
)


##############################################################################
@app.command("list")
def list_themes() -> None:
    """List available themes."""
    for theme in theme_names():
        typer.echo(theme)


### themes_cmd.py ends here
