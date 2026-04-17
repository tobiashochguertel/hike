"""The main entry point for the application."""

##############################################################################
# Python imports.
from __future__ import annotations

import sys
from collections.abc import Sequence

##############################################################################
# Local imports.
from .cli.app import app


##############################################################################
def main(argv: Sequence[str] | None = None) -> None:
    """Run the Hike CLI."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ["--help"]

    app(args=args, prog_name="hike")


##############################################################################
if __name__ == "__main__":
    main()


### __main__.py ends here
