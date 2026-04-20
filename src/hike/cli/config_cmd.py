"""Configuration management CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

from json import dumps

##############################################################################
# Typer imports.
import typer

##############################################################################
# Pydantic imports.
from pydantic import ValidationError

##############################################################################
# Local imports.
from ..data import (
    configuration_file,
    dump_configuration,
    get_configuration_value,
    set_configuration_value,
    unset_configuration_value,
    validate_configuration_file,
)
from .common import runtime_context_from_typer_context
from .services import initialize_configuration

##############################################################################
app = typer.Typer(
    help="Manage Hike configuration files.",
    add_completion=True,
    no_args_is_help=True,
)


##############################################################################
def _fail(message: str, code: int = 1) -> None:
    """Exit the CLI with an error message."""
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=code)


##############################################################################
@app.command("init")
def init_config(
    ctx: typer.Context,
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite an existing configuration file after creating a backup.",
    ),
) -> None:
    """Create a commented default configuration file."""
    runtime_context = runtime_context_from_typer_context(ctx)
    try:
        result = initialize_configuration(force, runtime_context)
    except FileExistsError as error:
        _fail(f"Configuration file already exists: {error.filename}", code=1)
    if result.backup is not None:
        typer.echo(f"Backed up existing configuration to {result.backup}")
    typer.echo(f"Created configuration file: {result.target}")


##############################################################################
@app.command("show")
def show_config(
    ctx: typer.Context,
    format_name: str = typer.Option(
        "yaml",
        "--format",
        help="Output format.",
        show_default=True,
        case_sensitive=False,
    ),
) -> None:
    """Display the current configuration."""
    runtime_context = runtime_context_from_typer_context(ctx)
    try:
        validate_configuration_file(context=runtime_context)
    except FileNotFoundError as error:
        _fail(f"Configuration file not found: {error.filename}", code=1)
    except ValidationError as error:
        _fail(str(error), code=3)
    typer.echo(dump_configuration(format_name, context=runtime_context), nl=False)


##############################################################################
@app.command("get")
def get_config(
    ctx: typer.Context,
    property_path: str = typer.Argument(..., help="Dot/bracket property path to read."),
) -> None:
    """Read a single configuration property."""
    runtime_context = runtime_context_from_typer_context(ctx)
    try:
        value = get_configuration_value(property_path, context=runtime_context)
    except KeyError:
        _fail(f"Configuration property not found: {property_path}", code=1)
    typer.echo(value if isinstance(value, str) else dumps(value))


##############################################################################
@app.command("set")
def set_config(
    ctx: typer.Context,
    property_path: str = typer.Argument(
        ..., help="Dot/bracket property path to update."
    ),
    value: str = typer.Argument(..., help="Value to set, parsed with YAML rules."),
) -> None:
    """Set a configuration property."""
    runtime_context = runtime_context_from_typer_context(ctx)
    try:
        set_configuration_value(property_path, value, context=runtime_context)
    except (KeyError, ValueError) as error:
        _fail(str(error), code=3)
    except ValidationError as error:
        _fail(str(error), code=1)
    typer.echo(f"Set {property_path}")


##############################################################################
@app.command("unset")
def unset_config(
    ctx: typer.Context,
    property_path: str = typer.Argument(
        ..., help="Dot/bracket property path to remove."
    ),
) -> None:
    """Unset a configuration property."""
    runtime_context = runtime_context_from_typer_context(ctx)
    try:
        unset_configuration_value(property_path, context=runtime_context)
    except KeyError:
        _fail(f"Configuration property not found: {property_path}", code=1)
    except ValidationError as error:
        _fail(str(error), code=1)
    typer.echo(f"Unset {property_path}")


##############################################################################
@app.command("validate")
def validate_config(
    ctx: typer.Context,
) -> None:
    """Validate the active configuration file."""
    runtime_context = runtime_context_from_typer_context(ctx)
    try:
        configuration = validate_configuration_file(context=runtime_context)
    except FileNotFoundError as error:
        _fail(f"Configuration file not found: {error.filename}", code=1)
    except ValidationError as error:
        _fail(str(error), code=3)
    typer.echo(f"Configuration is valid: {configuration_file(runtime_context)}")
    if configuration.theme is not None:
        typer.echo(f"Theme: {configuration.theme}")


##############################################################################
@app.command("path")
def config_path(
    ctx: typer.Context,
) -> None:
    """Print the effective configuration file path."""
    runtime_context = runtime_context_from_typer_context(ctx)
    typer.echo(configuration_file(runtime_context))


### config_cmd.py ends here
