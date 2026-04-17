"""Typer-based CLI for Hike."""

##############################################################################
# Python imports.
from __future__ import annotations

from pathlib import Path

##############################################################################
# Typer imports.
import typer

##############################################################################
# Local imports.
from ..app_info import APP_DESCRIPTION, APP_NAME
from .bindings_cmd import app as bindings_app
from .bindings_cmd import list_bindings
from .common import config_path_option, env_path_option, resolve_cli_runtime_context
from .config_cmd import app as config_app
from .contracts import OpenCommandRequest
from .env_cmd import app as env_app
from .schema_cmd import app as schema_app
from .services import (
    build_open_options,
    license_text,
    run_hike,
    theme_names,
    version_text,
)
from .themes_cmd import app as themes_app

##############################################################################
app = typer.Typer(
    name=APP_NAME.lower(),
    help=APP_DESCRIPTION,
    add_completion=True,
    invoke_without_command=True,
)

app.add_typer(config_app, name="config")
app.add_typer(schema_app, name="schema")
app.add_typer(env_app, name="env")
app.add_typer(bindings_app, name="bindings")
app.add_typer(themes_app, name="themes")


##############################################################################
@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version information and exit.",
        is_eager=True,
    ),
) -> None:
    """Manage Hike from a structured Typer CLI."""
    if version:
        typer.echo(version_text())
        raise typer.Exit()
    if ctx.invoked_subcommand is None and not ctx.args:
        typer.echo(ctx.get_help(), nl=False)
        raise typer.Exit()


##############################################################################
@app.command("license")
def show_license() -> None:
    """Show Hike's license text."""
    typer.echo(license_text())


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
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Launch the Hike TUI."""
    if license_text:
        show_license()
        raise typer.Exit()
    if bindings:
        list_bindings(config_path=config_path, env_path=env_path)
        raise typer.Exit()
    if theme == "?":
        for item in theme_names():
            typer.echo(item)
        raise typer.Exit()
    try:
        runtime_context = resolve_cli_runtime_context(config_path, env_path)
        options = build_open_options(
            OpenCommandRequest(
                target=target,
                command=command,
                navigation=navigation,
                theme=theme,
                root=root,
                ignore=ignore,
                hidden=hidden,
                exclude=tuple(exclude),
            ),
            runtime_context=runtime_context,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
    run_hike(options)


### app.py ends here
