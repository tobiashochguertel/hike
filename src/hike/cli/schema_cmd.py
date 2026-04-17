"""Schema inspection CLI commands."""

##############################################################################
# Python imports.
from __future__ import annotations

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
from ..data import RuntimeContext, configuration_schema, runtime_settings_schema
from ..data.config import validate_configuration_file
from ..data.settings import (
    load_runtime_settings,
    runtime_settings_from_file,
)
from .common import config_path_option, env_path_option, resolve_cli_runtime_context

##############################################################################
app = typer.Typer(
    help="Inspect and export JSON schemas for Hike configuration.",
    add_completion=True,
    no_args_is_help=True,
)

_SCHEMA_TYPES = ("config", "env")


##############################################################################
def _fail(message: str, code: int = 1) -> None:
    """Exit the CLI with an error message."""
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=code)


##############################################################################
def _schema_for(schema_type: str) -> dict[str, object]:
    """Return the schema for the requested schema type."""
    match schema_type:
        case "config":
            return configuration_schema()
        case "env":
            return runtime_settings_schema()
        case _:
            raise ValueError(f"Unknown schema type: {schema_type}")


##############################################################################
def _schema_export_path(
    schema_type: str,
    *,
    context: RuntimeContext | None = None,
) -> Path:
    """Return the default export path for a schema type."""
    store = load_runtime_settings(context).schema_store_path.expanduser()
    return store / f"hike.{schema_type}.schema.json"


##############################################################################
@app.command("list")
def list_schemas() -> None:
    """List the available schema types."""
    for schema_type in _SCHEMA_TYPES:
        typer.echo(schema_type)


##############################################################################
@app.command("show")
def show_schema(
    schema_type: str = typer.Argument(..., help="Schema type: config or env."),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Print a JSON schema to stdout."""
    resolve_cli_runtime_context(config_path, env_path)
    try:
        schema = _schema_for(schema_type)
    except ValueError as error:
        _fail(str(error), code=2)
    typer.echo(dumps(schema, indent=2))


##############################################################################
@app.command("validate")
def validate_schema_target(
    file: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    schema_type: str = typer.Option(..., "--type", help="Schema type: config or env."),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Validate a file against one of Hike's types."""
    runtime_context = resolve_cli_runtime_context(config_path, env_path)
    try:
        match schema_type:
            case "config":
                validate_configuration_file(file, context=runtime_context)
            case "env":
                runtime_settings_from_file(file)
            case _:
                raise ValueError(f"Unknown schema type: {schema_type}")
    except FileNotFoundError as error:
        _fail(f"File not found: {error.filename}", code=1)
    except (ValidationError, ValueError) as error:
        _fail(str(error), code=3)
    typer.echo(f"Valid {schema_type} file: {file}")


##############################################################################
@app.command("export")
def export_schemas(
    out: Path | None = typer.Option(
        None,
        "--out",
        help="Directory to write exported schemas into.",
        show_default=False,
    ),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Export all supported schemas as JSON files."""
    runtime_context = resolve_cli_runtime_context(config_path, env_path)
    export_root = (
        out.expanduser().resolve()
        if out is not None
        else load_runtime_settings(runtime_context)
        .schema_store_path.expanduser()
        .resolve()
    )
    export_root.mkdir(parents=True, exist_ok=True)
    for schema_type in _SCHEMA_TYPES:
        target = export_root / f"hike.{schema_type}.schema.json"
        target.write_text(dumps(_schema_for(schema_type), indent=2), encoding="utf-8")
        typer.echo(target)


##############################################################################
@app.command("path")
def schema_path(
    schema_type: str = typer.Argument(..., help="Schema type: config or env."),
    config_path: Path | None = config_path_option(),
    env_path: Path | None = env_path_option(),
) -> None:
    """Print the default export path for a schema type."""
    runtime_context = resolve_cli_runtime_context(config_path, env_path)
    if schema_type not in _SCHEMA_TYPES:
        _fail(f"Unknown schema type: {schema_type}", code=2)
    typer.echo(_schema_export_path(schema_type, context=runtime_context))


### schema_cmd.py ends here
