"""Helpers for CLI startup options and startup targets."""

##############################################################################
# Python imports.
from __future__ import annotations

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


### startup.py ends here
