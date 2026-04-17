"""The main entry point for the application."""

##############################################################################
# Python imports.
from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from collections.abc import Sequence
from inspect import cleandoc
from operator import attrgetter
from pathlib import Path

##############################################################################
# Local imports.
from . import __doc__, __version__
from .data import set_configuration_file
from .hike import Hike


##############################################################################
def get_args(argv: Sequence[str] | None = None) -> Namespace:
    """Get the command line arguments.

    Returns:
        The arguments.
    """

    parser = ArgumentParser(
        prog="hike",
        description=__doc__,
        epilog=f"v{__version__}",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information",
        action="version",
        version=f"%(prog)s v{__version__}",
    )
    parser.add_argument(
        "--license",
        "--licence",
        help="Show license information",
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--bindings",
        help="List commands that can have their bindings changed",
        action="store_true",
    )
    parser.add_argument(
        "--navigation",
        help="Show or hide the navigation panel on startup",
        action=BooleanOptionalAction,
    )
    parser.add_argument(
        "-t",
        "--theme",
        help="Set the theme for the application (set to ? to list available themes)",
    )
    parser.add_argument(
        "--config",
        help="Use an alternate configuration file.",
    )
    parser.add_argument(
        "--root",
        help="Set the initial local browser root directory.",
    )
    parser.add_argument(
        "--ignore",
        help="Enable or disable ignore-file filtering in the local browser",
        action=BooleanOptionalAction,
    )
    parser.add_argument(
        "--hidden",
        help="Show or hide dotfiles in the local browser",
        action=BooleanOptionalAction,
    )
    parser.add_argument(
        "--exclude",
        help="Add an exclude glob for the local browser (repeatable)",
        action="append",
        default=[],
        metavar="GLOB",
    )
    parser.add_argument(
        "-c",
        "--command",
        help="Run an internal Hike command on startup.",
        metavar="COMMAND",
        nargs="+",
    )
    parser.add_argument(
        "target",
        help="A startup file, directory or URL to open.",
        metavar="TARGET",
        nargs="?",
    )

    args = parser.parse_args(argv)
    if args.root is not None and not Path(args.root).expanduser().is_dir():
        parser.error("--root must point to an existing directory")
    if args.target is not None and args.command is not None:
        parser.error("TARGET and --command are mutually exclusive")
    return args


##############################################################################
def show_bindable_commands() -> None:
    """Show the commands that can have bindings applied."""
    from rich.console import Console
    from rich.markup import escape

    from .screens import Main

    console = Console(highlight=False)
    for command in sorted(Main.COMMAND_MESSAGES, key=attrgetter("__name__")):
        if command().has_binding:
            console.print(
                f"[bold]{escape(command.__name__)}[/] [dim italic]- {escape(command.tooltip())}[/]"
            )
            console.print(
                f"    [dim italic]Default: {escape(command.binding().key)}[/]"
            )


##############################################################################
def show_themes() -> None:
    """Show the available themes."""
    for theme in sorted(Hike(Namespace(theme=None)).available_themes):
        if theme != "textual-ansi":
            print(theme)


##############################################################################
def main() -> None:
    """The main entry point."""
    args = get_args()
    if args.config is not None:
        set_configuration_file(args.config)
    if args.license:
        print(cleandoc(Hike.HELP_LICENSE))
    elif args.bindings:
        show_bindable_commands()
    elif args.theme == "?":
        show_themes()
    else:
        Hike(args).run()


##############################################################################
if __name__ == "__main__":
    main()


### __main__.py ends here
