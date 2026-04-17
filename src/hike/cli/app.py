"""Typer-based CLI for Hike."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Sequence
from inspect import cleandoc
from pathlib import Path
from shlex import split as split_shell_words

##############################################################################
# Typer imports.
import typer

##############################################################################
# Local imports.
from .. import __version__
from ..hike import Hike
from ..startup import OpenOptions
from .bindings_cmd import app as bindings_app
from .bindings_cmd import list_bindings
from .common import apply_runtime_path_overrides, config_path_option, env_path_option
from .config_cmd import app as config_app
from .env_cmd import app as env_app
from .schema_cmd import app as schema_app
from .themes_cmd import app as themes_app
from .themes_cmd import list_themes

##############################################################################
app = typer.Typer(
    name="hike",
    help="A Markdown browser for the terminal.",
    add_completion=True,
)

app.add_typer(config_app, name="config")
app.add_typer(schema_app, name="schema")
app.add_typer(env_app, name="env")
app.add_typer(bindings_app, name="bindings")
app.add_typer(themes_app, name="themes")

_SUBCOMMANDS = {"open", "config", "schema", "env", "bindings", "themes", "license"}
_OPTIONS_WITH_VALUES = {
    "--config",
    "--env-file",
    "--theme",
    "--root",
    "--exclude",
    "--command",
    "-t",
    "-c",
}
_FLAGS = {
    "--version",
    "--license",
    "--licence",
    "--bindings",
    "--navigation",
    "--no-navigation",
    "--ignore",
    "--no-ignore",
    "--hidden",
    "--no-hidden",
}


##############################################################################
def normalize_argv(argv: Sequence[str]) -> list[str]:
    """Normalize argv so `hike PATH` behaves like `hike open PATH`."""
    args = list(argv)
    if not args:
        return ["open"]
    help_present = False
    index = 0
    while index < len(args):
        token = args[index]
        if token in _SUBCOMMANDS:
            return args
        if token in {"--help", "-h"}:
            help_present = True
            index += 1
            continue
        if token in {"--command", "-c"}:
            command = " ".join(args[index + 1 :]).strip()
            if not command:
                return ["open", *args]
            return ["open", *args[: index + 1], command]
        if token in _OPTIONS_WITH_VALUES:
            index += 2
            continue
        if token in _FLAGS or token.startswith("-"):
            index += 1
            continue
        return ["open", *args]
    if help_present:
        return args
    return ["open", *args]


##############################################################################
@app.command("license")
def show_license() -> None:
    """Show Hike's license text."""
    typer.echo(cleandoc(Hike.HELP_LICENSE))


##############################################################################
@app.command("open")
def open_command(
    target: str | None = typer.Argument(
        None,
        help="Startup file, directory, or URL to open.",
    ),
    command: str | None = typer.Option(
        None,
        "--command",
        "-c",
        help="Run an internal Hike command on startup. Quote values containing spaces.",
        show_default=False,
    ),
    navigation: bool | None = typer.Option(
        None,
        "--navigation/--no-navigation",
        help="Show or hide the navigation panel on startup.",
        show_default=False,
    ),
    theme: str | None = typer.Option(
        None,
        "--theme",
        "-t",
        help="Set the theme for the application. Use '?' to list themes.",
        show_default=False,
    ),
    root: Path | None = typer.Option(
        None,
        "--root",
        help="Set the initial local browser root directory.",
        show_default=False,
    ),
    ignore: bool | None = typer.Option(
        None,
        "--ignore/--no-ignore",
        help="Enable or disable ignore-file filtering in the local browser.",
        show_default=False,
    ),
    hidden: bool | None = typer.Option(
        None,
        "--hidden/--no-hidden",
        help="Show or hide dotfiles in the local browser.",
        show_default=False,
    ),
    exclude: list[str] = typer.Option(
        [],
        "--exclude",
        help="Add an exclude glob for the local browser (repeatable).",
        show_default=False,
    ),
    bindings: bool = typer.Option(
        False,
        "--bindings",
        help="List commands that can have their bindings changed.",
    ),
    license_text: bool = typer.Option(
        False,
        "--license",
        "--licence",
        help="Show license information instead of launching the TUI.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version information and exit.",
    ),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Launch the Hike TUI."""
    apply_runtime_path_overrides(config_path, env_path)
    if version:
        typer.echo(f"hike v{__version__}")
        raise typer.Exit()
    if license_text:
        show_license()
        raise typer.Exit()
    if bindings:
        list_bindings(config_path=config_path, env_path=env_path)
        raise typer.Exit()
    if theme == "?":
        list_themes()
        raise typer.Exit()
    if root is not None and not root.expanduser().is_dir():
        raise typer.BadParameter("--root must point to an existing directory")
    if target is not None and command is not None:
        raise typer.BadParameter("TARGET and --command are mutually exclusive")
    options = OpenOptions(
        target=target,
        command=None if command is None else tuple(split_shell_words(command)),
        navigation=navigation,
        theme=theme,
        root=None if root is None else str(root),
        ignore=ignore,
        hidden=hidden,
        exclude=tuple(exclude),
    )
    Hike(options).run()


### app.py ends here
