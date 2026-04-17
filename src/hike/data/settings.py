"""Runtime settings and environment-file support for Hike."""

##############################################################################
# Python imports.
from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any, cast

##############################################################################
# Dotenv imports.
from dotenv import dotenv_values

##############################################################################
# Pydantic imports.
from pydantic import AliasChoices, Field

##############################################################################
# Pydantic settings imports.
from pydantic_settings import BaseSettings, SettingsConfigDict

##############################################################################
# Local imports.
from .locations import config_dir
from .runtime_context import (
    RuntimeContext,
    current_runtime_context,
    resolve_runtime_context,
)

##############################################################################
_ENV_FILENAME = ".env"


##############################################################################
class RuntimeSettings(BaseSettings):
    """Environment-backed runtime settings for the Hike CLI."""

    model_config = SettingsConfigDict(
        env_prefix="",
        extra="ignore",
        case_sensitive=False,
    )

    config_path: Path | None = Field(
        default=None,
        description="Override the configuration file used by Hike.",
        validation_alias=AliasChoices("HIKE_CONFIG_PATH"),
        json_schema_extra={"env_names": ["HIKE_CONFIG_PATH"]},
    )
    env_path: Path | None = Field(
        default=None,
        description="Override the environment file used by Hike.",
        validation_alias=AliasChoices("HIKE_ENV_PATH"),
        json_schema_extra={"env_names": ["HIKE_ENV_PATH"]},
    )
    debug: bool = Field(
        default=False,
        description="Enable debug-oriented CLI behavior and verbose runtime diagnostics.",
        validation_alias=AliasChoices("HIKE_DEBUG"),
        json_schema_extra={"env_names": ["HIKE_DEBUG"]},
    )
    schema_store_path: Path = Field(
        default=Path("~/dotfiles/json-schemas"),
        description="Directory where exported JSON schemas should be written.",
        validation_alias=AliasChoices(
            "HIKE_SCHEMA_STORE_PATH", "JSON_SCHEMA_STORE_LOCAL"
        ),
        json_schema_extra={
            "env_names": ["HIKE_SCHEMA_STORE_PATH", "JSON_SCHEMA_STORE_LOCAL"]
        },
    )


##############################################################################
def _normalize_path(path: str | Path, *, cwd: Path | None = None) -> Path:
    """Normalise a runtime path setting."""
    normalized = Path(path).expanduser()
    if not normalized.is_absolute():
        normalized = (Path.cwd() if cwd is None else cwd) / normalized
    return normalized


##############################################################################
def _active_context(context: RuntimeContext | None = None) -> RuntimeContext:
    """Return the explicit or ambient runtime context."""
    active = current_runtime_context() if context is None else context
    return resolve_runtime_context() if active is None else active


##############################################################################
def project_environment_file(context: RuntimeContext | None = None) -> Path:
    """Return the project-local .env file path."""
    active = _active_context(context)
    return active.cwd / _ENV_FILENAME


##############################################################################
def default_environment_file() -> Path:
    """Return the default user-scoped .env file path."""
    return config_dir() / _ENV_FILENAME


def _base_runtime_settings() -> RuntimeSettings:
    """Load runtime settings from process environment only."""
    return RuntimeSettings()


##############################################################################
def runtime_settings_from_file(path: Path) -> RuntimeSettings:
    """Load runtime settings from a specific env file."""
    return RuntimeSettings(_env_file=str(path))  # type: ignore[call-arg]


##############################################################################
def environment_file(context: RuntimeContext | None = None) -> Path:
    """Return the effective environment-file path."""
    active = _active_context(context)
    if active.env_path is not None:
        return active.env_path
    base = _base_runtime_settings()
    if base.env_path is not None:
        return _normalize_path(
            base.env_path,
            cwd=active.cwd,
        )
    for candidate in (project_environment_file(active), default_environment_file()):
        if candidate.exists():
            return candidate
    return default_environment_file()


##############################################################################
@cache
def _load_runtime_settings_cached(
    context: RuntimeContext | None,
) -> RuntimeSettings:
    """Load runtime settings from the process environment and optional env file."""
    source = environment_file(context)
    if source.exists():
        return runtime_settings_from_file(source)
    return _base_runtime_settings()


##############################################################################
def clear_runtime_settings_cache() -> None:
    """Clear cached runtime settings."""
    _load_runtime_settings_cached.cache_clear()


##############################################################################
def load_runtime_settings(context: RuntimeContext | None = None) -> RuntimeSettings:
    """Load runtime settings from the process environment and optional env file."""
    return _load_runtime_settings_cached(_active_context(context))


##############################################################################
def runtime_settings_schema() -> dict[str, Any]:
    """Return the JSON schema for the runtime settings."""
    return RuntimeSettings.model_json_schema()


##############################################################################
def load_environment_values(
    path: str | Path | None = None,
    context: RuntimeContext | None = None,
) -> dict[str, str]:
    """Load key/value pairs from an environment file."""
    active = _active_context(context)
    source = (
        environment_file(active)
        if path is None
        else _normalize_path(path, cwd=active.cwd)
    )
    if not source.exists():
        return {}
    return {
        key: value for key, value in dotenv_values(source).items() if value is not None
    }


##############################################################################
def environment_variable_names(field_name: str) -> tuple[str, ...]:
    """Return the supported environment variable names for a runtime field."""
    field = RuntimeSettings.model_fields[field_name]
    extra = cast(dict[str, Any], field.json_schema_extra or {})
    names = cast(list[str], extra.get("env_names", []))
    return tuple(str(name) for name in names)


### settings.py ends here
