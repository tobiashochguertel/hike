"""Helpers for CLI startup options and startup targets."""

##############################################################################
# Python imports.
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

##############################################################################
# Httpx imports.
from httpx import URL

##############################################################################
# Pydantic imports.
from pydantic import BaseModel, ConfigDict, Field

##############################################################################
# Local imports.
from .data import RuntimeContext, looks_urllike
from .data.config import Configuration
from .data.discovery import LocalDiscoveryOptions


##############################################################################
class OpenOptions(BaseModel):
    """Typed options for launching the Hike TUI."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    target: str | None = Field(
        default=None,
        description="Startup file, directory, or URL to open.",
    )
    command: tuple[str, ...] | None = Field(
        default=None,
        description="Startup internal command to run when the TUI launches.",
    )
    navigation: bool | None = Field(
        default=None,
        description="Override navigation visibility on startup.",
    )
    theme: str | None = Field(
        default=None,
        description="Override the configured Textual theme for this launch.",
    )
    root: str | None = Field(
        default=None,
        description="Override the initial local browser root directory.",
    )
    ignore: bool | None = Field(
        default=None,
        description="Override ignore-file filtering in the local browser.",
    )
    hidden: bool | None = Field(
        default=None,
        description="Override hidden-file visibility in the local browser.",
    )
    exclude: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Additional exclude globs for the local browser.",
    )
    runtime_context: RuntimeContext | None = Field(
        default=None,
        description="Resolved runtime paths for config and env discovery.",
    )


##############################################################################
class StartupTargetKind(StrEnum):
    """The kinds of startup targets Hike can handle directly."""

    NONE = "none"
    FILE = "file"
    DIRECTORY = "directory"
    URL = "url"
    MISSING = "missing"


##############################################################################
class StartupTarget(BaseModel):
    """The classified startup target."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    kind: StartupTargetKind
    value: Path | URL | str | None = None


##############################################################################
@dataclass(frozen=True, slots=True)
class StartupPlan:
    """The resolved startup behavior for an `open` invocation."""

    local_root: Path
    open_target: Path | URL | None = None
    selected_path: Path | None = None
    command_input: str | None = None
    resolve_from_index: bool = False
    focus_local_browser: bool = False
    error_message: str | None = None


##############################################################################
def classify_startup_target(target: str | None) -> StartupTarget:
    """Classify a startup target from the command line."""
    if target is None:
        return StartupTarget(kind=StartupTargetKind.NONE)
    if looks_urllike(target):
        return StartupTarget(kind=StartupTargetKind.URL, value=URL(target))
    path = Path(target).expanduser()
    if path.is_file():
        return StartupTarget(kind=StartupTargetKind.FILE, value=path.resolve())
    if path.is_dir():
        return StartupTarget(kind=StartupTargetKind.DIRECTORY, value=path.resolve())
    return StartupTarget(kind=StartupTargetKind.MISSING, value=target)


##############################################################################
def _runtime_cwd(options: OpenOptions) -> Path:
    """Return the cwd associated with the open request."""
    if options.runtime_context is not None:
        return options.runtime_context.cwd
    return Path.cwd()


##############################################################################
def _default_local_root(
    options: OpenOptions,
    configuration: Configuration,
) -> Path:
    """Resolve the configured default local browser root."""
    configured = Path(configuration.local_start_location).expanduser()
    if not configured.is_absolute():
        configured = _runtime_cwd(options) / configured
    return configured.resolve()


##############################################################################
def _resolve_local_root(
    options: OpenOptions,
    configuration: Configuration,
    startup_target: StartupTarget,
) -> Path:
    """Resolve the initial local browser root for the startup request."""
    if options.root is not None:
        return Path(options.root).expanduser().resolve()
    if startup_target.kind is StartupTargetKind.FILE and isinstance(
        startup_target.value, Path
    ):
        return startup_target.value.parent
    if startup_target.kind is StartupTargetKind.DIRECTORY and isinstance(
        startup_target.value, Path
    ):
        return startup_target.value
    return _default_local_root(options, configuration)


def resolve_startup_plan(
    options: OpenOptions,
    configuration: Configuration,
    local_options: LocalDiscoveryOptions,
) -> StartupPlan:
    """Resolve the startup behavior for an `open` request."""
    startup_target = classify_startup_target(options.target)
    local_root = _resolve_local_root(options, configuration, startup_target)

    if options.command:
        return StartupPlan(
            local_root=local_root,
            command_input=" ".join(options.command),
        )

    if startup_target.kind is StartupTargetKind.MISSING:
        return StartupPlan(
            local_root=local_root,
            error_message=f"Could not locate {startup_target.value!r}",
        )

    if startup_target.kind is StartupTargetKind.FILE and isinstance(
        startup_target.value, Path
    ):
        return StartupPlan(
            local_root=local_root,
            open_target=startup_target.value,
            selected_path=startup_target.value,
        )

    if startup_target.kind is StartupTargetKind.URL and isinstance(
        startup_target.value, URL
    ):
        return StartupPlan(local_root=local_root, open_target=startup_target.value)

    if startup_target.kind in (
        StartupTargetKind.NONE,
        StartupTargetKind.DIRECTORY,
    ):
        if configuration.startup_auto_open:
            return StartupPlan(local_root=local_root, resolve_from_index=True)
        return StartupPlan(local_root=local_root, focus_local_browser=True)

    return StartupPlan(local_root=local_root, focus_local_browser=True)


### startup.py ends here
