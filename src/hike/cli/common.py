"""Shared helpers for Hike's Typer CLI."""

##############################################################################
# Python imports.
from __future__ import annotations

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
from ..data import set_configuration_file, set_environment_file

##############################################################################
_HIKE_CONFIG_PATH_ENV = "HIKE_CONFIG_PATH"
_HIKE_ENV_PATH_ENV = "HIKE_ENV_PATH"

console = Console()


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
def apply_runtime_path_overrides(
    config_path: Path | None,
    env_path: Path | None,
) -> None:
    """Apply CLI-level path overrides for config and env files."""
    set_environment_file(env_path)
    set_configuration_file(config_path)


### common.py ends here
