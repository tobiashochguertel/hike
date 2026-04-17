"""Helpers for Hike's local file browser modes."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from enum import StrEnum
from os import walk
from pathlib import Path

##############################################################################
# Local imports.
from .discovery import LocalDiscoveryOptions, should_include_path


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


##############################################################################
@dataclass(frozen=True, slots=True)
class LocalBrowserEntry:
    """An entry in the flat local browser list."""

    path: Path
    relative_path: Path
    is_dir: bool

    @property
    def display_path(self) -> str:
        """Return the path text shown in the flat list."""
        display = self.relative_path.as_posix()
        return f"{display}/" if self.is_dir else display


##############################################################################
def flatten_local_paths(
    root: Path,
    options: LocalDiscoveryOptions,
) -> tuple[LocalBrowserEntry, ...]:
    """Flatten the browsable subtree into a relative file/directory list."""
    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        return ()
    entries: list[LocalBrowserEntry] = []
    for current, directories, files in walk(resolved_root, topdown=True):
        current_path = Path(current)
        directories[:] = sorted(
            (
                directory
                for directory in directories
                if should_include_path(
                    current_path / directory,
                    root=resolved_root,
                    options=options,
                )
            ),
            key=str.casefold,
        )
        for directory in directories:
            path = current_path / directory
            entries.append(
                LocalBrowserEntry(
                    path=path,
                    relative_path=path.relative_to(resolved_root),
                    is_dir=True,
                )
            )
        for filename in sorted(files, key=str.casefold):
            path = current_path / filename
            if should_include_path(path, root=resolved_root, options=options):
                entries.append(
                    LocalBrowserEntry(
                        path=path,
                        relative_path=path.relative_to(resolved_root),
                        is_dir=False,
                    )
                )
    return tuple(entries)


### local_browser.py ends here
