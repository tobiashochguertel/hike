"""The main entry point for the application."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Sequence

##############################################################################
# Local imports.
from .cli.app import app


##############################################################################
def main(argv: Sequence[str] | None = None) -> None:
    """Run the Hike CLI."""
    if argv is None:
        app(prog_name="hike")
        return

    app(args=list(argv), prog_name="hike")


##############################################################################
if __name__ == "__main__":
    main()


### __main__.py ends here
