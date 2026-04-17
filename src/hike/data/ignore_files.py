"""Helpers for respecting ignore files in the local browser."""

##############################################################################
# Python imports.
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

##############################################################################
# pathspec imports.
from pathspec import GitIgnoreSpec

##############################################################################
IGNORE_FILE_NAMES = (".gitignore", ".ignore")
"""The ignore file names supported by Hike's local browser."""


##############################################################################
@dataclass(frozen=True, slots=True)
class IgnoreFile:
    """A compiled ignore file."""

    directory: Path
    spec: GitIgnoreSpec


##############################################################################
def _ancestor_directories(path: Path) -> tuple[Path, ...]:
    """Return a path's ancestors ordered from shallowest to deepest."""
    resolved = path.resolve()
    return tuple(reversed((resolved, *resolved.parents)))


##############################################################################
@cache
def load_ignore_files(root: Path) -> tuple[IgnoreFile, ...]:
    """Load supported ignore files for a given browser root.

    The current implementation searches for `.gitignore` and `.ignore` files in
    the browser root and its ancestors so that opening a nested docs directory
    inside a repository still respects the repository-level ignore rules.

    Args:
        root: The root directory of the local browser.

    Returns:
        The compiled ignore files for the root.
    """
    ignore_files: list[IgnoreFile] = []
    for directory in _ancestor_directories(root):
        for file_name in IGNORE_FILE_NAMES:
            ignore_file = directory / file_name
            if ignore_file.is_file():
                ignore_files.append(
                    IgnoreFile(
                        directory=directory,
                        spec=GitIgnoreSpec.from_lines(
                            ignore_file.read_text(encoding="utf-8").splitlines()
                        ),
                    )
                )
    return tuple(ignore_files)


##############################################################################
def is_ignored(path: Path, *, root: Path) -> bool:
    """Should the given path be hidden by the local browser?

    Args:
        path: The path being considered for display.
        root: The root directory of the local browser.

    Returns:
        `True` if the path should be hidden, `False` otherwise.
    """
    resolved = path.resolve()
    for ignore_file in load_ignore_files(root.resolve()):
        try:
            relative = resolved.relative_to(ignore_file.directory)
        except ValueError:
            continue
        relative_path = relative.as_posix()
        if not relative_path or relative_path == ".":
            continue
        if ignore_file.spec.match_file(relative_path):
            return True
        if path.is_dir() and ignore_file.spec.match_file(f"{relative_path}/"):
            return True
    return False


##############################################################################
def visible_paths(paths: Iterable[Path], *, root: Path) -> Iterable[Path]:
    """Filter a directory listing using Hike's local browser rules.

    Args:
        paths: The paths to consider.
        root: The root directory of the local browser.

    Returns:
        The visible paths.
    """
    return (path for path in paths if not is_ignored(path, root=root))


### ignore_files.py ends here
