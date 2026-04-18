"""Shared helpers for Hike's Typer CLI."""

##############################################################################
# Python imports.
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

##############################################################################
# Typer imports.
import typer

##############################################################################
# Rich imports.
from rich.console import Console

##############################################################################
# Local imports.
from ..data import RuntimeContext, resolve_runtime_context

##############################################################################
_HIKE_CONFIG_PATH_ENV = "HIKE_CONFIG_PATH"
_HIKE_ENV_PATH_ENV = "HIKE_ENV_PATH"

console = Console()


##############################################################################
@dataclass(frozen=True, slots=True)
class CLIContext:
    """Shared CLI context derived from root-level options."""

    config_path: Path | None
    env_path: Path | None
    runtime_context: RuntimeContext


##############################################################################
def config_path_option() -> Any:
    """Create the shared `--config` Typer option."""
    return typer.Option(
        None,
        "--config",
        help="Use an alternate configuration file.",
        envvar=_HIKE_CONFIG_PATH_ENV,
        show_default=False,
    )


##############################################################################
def env_path_option() -> Any:
    """Create the shared `--env-file` Typer option."""
    return typer.Option(
        None,
        "--env-file",
        help="Use an alternate .env file for runtime settings.",
        envvar=_HIKE_ENV_PATH_ENV,
        show_default=False,
    )


##############################################################################
def resolve_cli_runtime_context(
    config_path: Path | None,
    env_path: Path | None,
) -> RuntimeContext:
    """Resolve a runtime context from shared CLI path options."""
    return resolve_runtime_context(config_path=config_path, env_path=env_path)


##############################################################################
def set_cli_context(
    ctx: typer.Context,
    *,
    config_path: Path | None,
    env_path: Path | None,
) -> CLIContext:
    """Resolve and store the shared CLI context on the Typer context."""
    resolved = CLIContext(
        config_path=config_path,
        env_path=env_path,
        runtime_context=resolve_cli_runtime_context(config_path, env_path),
    )
    ctx.obj = resolved
    return resolved


##############################################################################
def cli_context_from_typer_context(ctx: typer.Context | None) -> CLIContext:
    """Return the stored CLI context or a default one."""
    if ctx is not None and isinstance(ctx.obj, CLIContext):
        return ctx.obj
    return CLIContext(
        config_path=None,
        env_path=None,
        runtime_context=resolve_runtime_context(),
    )


##############################################################################
def runtime_context_from_typer_context(ctx: typer.Context | None) -> RuntimeContext:
    """Return the runtime context stored on the Typer context."""
    return cli_context_from_typer_context(ctx).runtime_context


### common.py ends here
