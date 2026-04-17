"""Code relating to the application's configuration file."""

##############################################################################
# Python imports.
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from functools import cache
from json import dumps, loads
from pathlib import Path

##############################################################################
# Local imports.
from .locations import config_dir

##############################################################################
_configuration_override: Path | None = None
"""An optional override for the configuration file path."""


##############################################################################
@dataclass
class Configuration:
    """The configuration data for the application."""

    theme: str | None = None
    """The theme for the application."""

    navigation_visible: bool = True
    """Should the navigation panel be visible?"""

    navigation_on_right: bool = False
    """Should the navigation panel live on the right?"""

    sidebar_default_width_percent: int = 22
    """The default sidebar width as a percentage of terminal width."""

    sidebar_min_width: int = 24
    """The minimum width of the sidebar in terminal cells."""

    sidebar_max_width: int = 60
    """The maximum width of the sidebar in terminal cells."""

    sidebar_auto_fit: bool = True
    """Should the sidebar auto-fit to the active navigation content?"""

    markdown_extensions: list[str] = field(default_factory=lambda: [".md", ".markdown"])
    """The file extensions to consider to be Markdown files."""

    markdown_content_types: list[str] = field(
        default_factory=lambda: ["text/plain", "text/markdown", "text/x-markdown"]
    )
    """The content types to consider when looking for remote Markdown content."""

    command_line_on_top: bool = False
    """Should the command line live at the top of the screen?"""

    responsive_auto_switch_narrow: bool = True
    """Should Hike switch to a single-pane layout on narrow terminals?"""

    responsive_narrow_width: int = 100
    """The terminal width threshold for responsive single-pane mode."""

    responsive_narrow_mode: str = "content-only"
    """The default single-pane view to show on narrow terminals."""

    main_branches: list[str] = field(default_factory=lambda: ["main", "master"])
    """The branches considered to be main branches on forges."""

    obsidian_vaults: str = "~/Library/Mobile Documents/iCloud~md~obsidian/Documents"
    """The path to the root of all Obsidian vaults."""

    local_start_location: str = "~"
    """The start location for the local file system browser."""

    local_use_ignore_files: bool = True
    """Should the local browser respect ignore files?"""

    local_show_hidden: bool = False
    """Should the local browser show hidden files and directories?"""

    local_exclude_patterns: list[str] = field(default_factory=list)
    """Extra exclude globs for the local browser."""

    bindings: dict[str, str] = field(default_factory=dict)
    """Command keyboard binding overrides."""

    focus_viewer_on_load: bool = True
    """Should the viewer get focus when a file is loaded?"""

    show_front_matter: bool = True
    """Should the viewer allow for the viewing of front matter?"""

    allow_traditional_quit: bool = False
    """Ignore Textual's safety net for Ctrl+c?"""


##############################################################################
def _normalize_configuration_path(path: str | Path) -> Path:
    """Normalise a configuration file path."""
    normalized = Path(path).expanduser()
    if not normalized.is_absolute():
        normalized = Path.cwd() / normalized
    return normalized


##############################################################################
def set_configuration_file(path: str | Path | None) -> Path:
    """Set the configuration file path override.

    Args:
        path: The new configuration file path, or `None` to clear the override.

    Returns:
        The effective configuration file path.
    """
    global _configuration_override
    load_configuration.cache_clear()
    _configuration_override = (
        None if path is None else _normalize_configuration_path(path)
    )
    return configuration_file()


##############################################################################
def configuration_file() -> Path:
    """The path to the file that holds the application configuration.

    Returns:
        The path to the configuration file.
    """
    return _configuration_override or (config_dir() / "configuration.json")


##############################################################################
def save_configuration(configuration: Configuration) -> Configuration:
    """Save the given configuration.

    Args:
        The configuration to store.

    Returns:
        The configuration.
    """
    load_configuration.cache_clear()
    configuration_file().parent.mkdir(parents=True, exist_ok=True)
    configuration_file().write_text(
        dumps(asdict(configuration), indent=4), encoding="utf-8"
    )
    return load_configuration()


##############################################################################
@cache
def load_configuration() -> Configuration:
    """Load the configuration.

    Returns:
        The configuration.

    Note:
        As a side-effect, if the configuration doesn't exist a default one
        will be saved to storage.

        This function is designed so that it's safe and low-cost to
        repeatedly call it. The configuration is cached and will only be
        loaded from storage when necessary.
    """
    source = configuration_file()
    return (
        Configuration(**loads(source.read_text(encoding="utf-8")))
        if source.exists()
        else save_configuration(Configuration())
    )


##############################################################################
@contextmanager
def update_configuration() -> Iterator[Configuration]:
    """Context manager for updating the configuration.

    Loads the configuration and makes it available, then ensures it is
    saved.

    Example:
        ```python
        with update_configuration() as config:
            config.meaning = 42
        ```
    """
    configuration = load_configuration()
    try:
        yield configuration
    finally:
        save_configuration(configuration)


### config.py ends here
