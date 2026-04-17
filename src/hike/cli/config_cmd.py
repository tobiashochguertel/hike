"""Configuration management CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

from datetime import datetime
from json import dumps
from pathlib import Path

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
    render_default_configuration,
    set_configuration_value,
    unset_configuration_value,
    validate_configuration_file,
)
from .common import apply_runtime_path_overrides, config_path_option, env_path_option

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
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite an existing configuration file after creating a backup.",
    ),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Create a commented default configuration file."""
    apply_runtime_path_overrides(config_path, env_path)
    target = configuration_file()
    if target.exists():
        if not force:
            _fail(
                f"Configuration file already exists: {target}",
                code=1,
            )
        backup = target.with_name(
            f"{target.name}.bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        target.replace(backup)
        typer.echo(f"Backed up existing configuration to {backup}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_default_configuration(), encoding="utf-8")
    typer.echo(f"Created configuration file: {target}")


##############################################################################
@app.command("show")
def show_config(
    format_name: str = typer.Option(
        "yaml",
        "--format",
        help="Output format.",
        show_default=True,
        case_sensitive=False,
    ),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Display the current configuration."""
    apply_runtime_path_overrides(config_path, env_path)
    try:
        validate_configuration_file()
    except FileNotFoundError as error:
        _fail(f"Configuration file not found: {error.filename}", code=1)
    except ValidationError as error:
        _fail(str(error), code=3)
    typer.echo(dump_configuration(format_name), nl=False)


##############################################################################
@app.command("get")
def get_config(
    property_path: str = typer.Argument(..., help="Dot/bracket property path to read."),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Read a single configuration property."""
    apply_runtime_path_overrides(config_path, env_path)
    try:
        value = get_configuration_value(property_path)
    except KeyError:
        _fail(f"Configuration property not found: {property_path}", code=1)
    typer.echo(value if isinstance(value, str) else dumps(value))


##############################################################################
@app.command("set")
def set_config(
    property_path: str = typer.Argument(
        ..., help="Dot/bracket property path to update."
    ),
    value: str = typer.Argument(..., help="Value to set, parsed with YAML rules."),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Set a configuration property."""
    apply_runtime_path_overrides(config_path, env_path)
    try:
        set_configuration_value(property_path, value)
    except (KeyError, ValueError) as error:
        _fail(str(error), code=3)
    except ValidationError as error:
        _fail(str(error), code=1)
    typer.echo(f"Set {property_path}")


##############################################################################
@app.command("unset")
def unset_config(
    property_path: str = typer.Argument(
        ..., help="Dot/bracket property path to remove."
    ),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Unset a configuration property."""
    apply_runtime_path_overrides(config_path, env_path)
    try:
        unset_configuration_value(property_path)
    except KeyError:
        _fail(f"Configuration property not found: {property_path}", code=1)
    except ValidationError as error:
        _fail(str(error), code=1)
    typer.echo(f"Unset {property_path}")


##############################################################################
@app.command("validate")
def validate_config(
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Validate the active configuration file."""
    apply_runtime_path_overrides(config_path, env_path)
    try:
        configuration = validate_configuration_file()
    except FileNotFoundError as error:
        _fail(f"Configuration file not found: {error.filename}", code=1)
    except ValidationError as error:
        _fail(str(error), code=3)
    typer.echo(f"Configuration is valid: {configuration_file()}")
    if configuration.theme is not None:
        typer.echo(f"Theme: {configuration.theme}")


##############################################################################
@app.command("path")
def config_path(
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Print the effective configuration file path."""
    apply_runtime_path_overrides(config_path, env_path)
    typer.echo(configuration_file())


### config_cmd.py ends here
