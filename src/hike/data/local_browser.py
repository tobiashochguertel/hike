"""Helpers for Hike's local file browser modes."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from ..compat import StrEnum


##############################################################################
class LocalBrowserMode(StrEnum):
    """The supported local browser rendering modes."""

    TREE = "tree"
    FLAT_LIST = "flat-list"


##############################################################################
def local_browser_mode_from_configuration(mode: str) -> LocalBrowserMode:
    """Parse the configured local browser mode."""
    try:
        return LocalBrowserMode(mode)
    except ValueError as error:
        raise ValueError(
            "local_browser_view_mode must be one of "
            f"{', '.join(browser_mode.value for browser_mode in LocalBrowserMode)}"
        ) from error


##############################################################################
def stable_root_label(root: Path, *, reference: Path | None = None) -> str:
    """Create a stable, relative label for a local browser root."""
    resolved_root = root.resolve()
    resolved_reference = (
        Path.cwd().resolve() if reference is None else reference.resolve()
    )
    try:
        relative = resolved_root.relative_to(resolved_reference)
    except ValueError:
        return resolved_root.name or str(resolved_root)
    return "." if not relative.parts else relative.as_posix()


### local_browser.py ends here
