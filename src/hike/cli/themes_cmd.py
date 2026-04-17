"""Theme-related CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Typer imports.
import typer

from ..hike import Hike

##############################################################################
# Local imports.
from ..startup import OpenOptions

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
    for theme in sorted(Hike(OpenOptions()).available_themes):
        if theme != "textual-ansi":
            typer.echo(theme)


### themes_cmd.py ends here
