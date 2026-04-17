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

##############################################################################
_ENV_FILENAME = ".env"

_environment_override: Path | None = None
"""An optional override for the environment file path."""


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
def _normalize_path(path: str | Path) -> Path:
    """Normalise a runtime path setting."""
    normalized = Path(path).expanduser()
    if not normalized.is_absolute():
        normalized = Path.cwd() / normalized
    return normalized


##############################################################################
def project_environment_file() -> Path:
    """Return the project-local .env file path."""
    return Path.cwd() / _ENV_FILENAME


##############################################################################
def default_environment_file() -> Path:
    """Return the default user-scoped .env file path."""
    return config_dir() / _ENV_FILENAME


##############################################################################
def set_environment_file(path: str | Path | None) -> Path:
    """Set the environment-file override."""
    global _environment_override
    load_runtime_settings.cache_clear()
    _environment_override = None if path is None else _normalize_path(path)
    return environment_file()


##############################################################################
def _base_runtime_settings() -> RuntimeSettings:
    """Load runtime settings from process environment only."""
    return RuntimeSettings()


##############################################################################
def runtime_settings_from_file(path: Path) -> RuntimeSettings:
    """Load runtime settings from a specific env file."""
    return RuntimeSettings(_env_file=str(path))  # type: ignore[call-arg]


##############################################################################
def environment_file() -> Path:
    """Return the effective environment-file path."""
    if _environment_override is not None:
        return _environment_override
    base = _base_runtime_settings()
    if base.env_path is not None:
        return _normalize_path(base.env_path)
    for candidate in (project_environment_file(), default_environment_file()):
        if candidate.exists():
            return candidate
    return default_environment_file()


##############################################################################
@cache
def load_runtime_settings() -> RuntimeSettings:
    """Load runtime settings from the process environment and optional env file."""
    source = environment_file()
    if source.exists():
        return runtime_settings_from_file(source)
    return _base_runtime_settings()


##############################################################################
def runtime_settings_schema() -> dict[str, Any]:
    """Return the JSON schema for the runtime settings."""
    return RuntimeSettings.model_json_schema()


##############################################################################
def load_environment_values(path: str | Path | None = None) -> dict[str, str]:
    """Load key/value pairs from an environment file."""
    source = environment_file() if path is None else _normalize_path(path)
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
