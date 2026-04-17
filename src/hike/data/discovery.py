"""Helpers for local browser discovery rules."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, cast

##############################################################################
# pathspec imports.
from pathspec import GitIgnoreSpec

##############################################################################
# Local imports.
from .config import Configuration
from .ignore_files import is_ignored
from .location_types import maybe_markdown


##############################################################################
@dataclass(frozen=True, slots=True)
class LocalDiscoveryOptions:
    """Runtime options for the local browser."""

    use_ignore_files: bool = True
    show_hidden: bool = False
    exclude_patterns: tuple[str, ...] = ()


def local_discovery_options(
    arguments: object, configuration: Configuration
) -> LocalDiscoveryOptions:
    """Build the effective local browser discovery options."""
    cli_arguments = cast(Any, arguments)
    ignore = cast(bool | None, cli_arguments.ignore)
    hidden = cast(bool | None, cli_arguments.hidden)
    exclude = cast(tuple[str, ...] | list[str], cli_arguments.exclude)
    return LocalDiscoveryOptions(
        use_ignore_files=configuration.local_use_ignore_files
        if ignore is None
        else ignore,
        show_hidden=configuration.local_show_hidden if hidden is None else hidden,
        exclude_patterns=(
            *configuration.local_exclude_patterns,
            *tuple(exclude),
        ),
    )


##############################################################################
@cache
def _exclude_spec(patterns: tuple[str, ...]) -> GitIgnoreSpec | None:
    """Compile the given exclude patterns."""
    return GitIgnoreSpec.from_lines(patterns) if patterns else None


##############################################################################
def is_excluded(path: Path, *, root: Path, patterns: tuple[str, ...]) -> bool:
    """Test if a path matches ad-hoc exclude patterns."""
    spec = _exclude_spec(patterns)
    if spec is None:
        return False
    relative_path = path.resolve().relative_to(root.resolve()).as_posix()
    return spec.match_file(relative_path) or (
        path.is_dir() and spec.match_file(f"{relative_path}/")
    )


##############################################################################
def should_include_path(
    path: Path, *, root: Path, options: LocalDiscoveryOptions
) -> bool:
    """Apply Hike's local browser discovery rules to a path."""
    if not options.show_hidden and path.name.startswith("."):
        return False
    if options.use_ignore_files and is_ignored(path, root=root):
        return False
    if is_excluded(path, root=root, patterns=options.exclude_patterns):
        return False
    return path.is_dir() or maybe_markdown(path)


### discovery.py ends here
