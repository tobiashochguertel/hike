"""Helpers for handling CLI startup targets."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Local imports.
from .data import looks_urllike


##############################################################################
class StartupTargetKind(StrEnum):
    """The kinds of startup targets Hike can handle directly."""

    NONE = "none"
    FILE = "file"
    DIRECTORY = "directory"
    URL = "url"
    MISSING = "missing"


##############################################################################
@dataclass(frozen=True, slots=True)
class StartupTarget:
    """The classified startup target."""

    kind: StartupTargetKind
    value: Path | URL | str | None = None


##############################################################################
def classify_startup_target(target: str | None) -> StartupTarget:
    """Classify a startup target from the command line.

    Args:
        target: The raw target supplied on the command line.

    Returns:
        The classified startup target.
    """
    if target is None:
        return StartupTarget(StartupTargetKind.NONE)
    if looks_urllike(target):
        return StartupTarget(StartupTargetKind.URL, URL(target))
    path = Path(target).expanduser()
    if path.is_file():
        return StartupTarget(StartupTargetKind.FILE, path.resolve())
    if path.is_dir():
        return StartupTarget(StartupTargetKind.DIRECTORY, path.resolve())
    return StartupTarget(StartupTargetKind.MISSING, target)


### startup.py ends here
