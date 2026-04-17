"""Helpers for local browser discovery rules."""

##############################################################################
# Python imports.
from argparse import Namespace
from dataclasses import dataclass
from functools import cache
from pathlib import Path

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


##############################################################################
def local_discovery_options(
    arguments: Namespace, configuration: Configuration
) -> LocalDiscoveryOptions:
    """Build the effective local browser discovery options."""
    return LocalDiscoveryOptions(
        use_ignore_files=configuration.local_use_ignore_files
        if arguments.ignore is None
        else arguments.ignore,
        show_hidden=configuration.local_show_hidden
        if arguments.hidden is None
        else arguments.hidden,
        exclude_patterns=(
            *configuration.local_exclude_patterns,
            *tuple(arguments.exclude),
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
