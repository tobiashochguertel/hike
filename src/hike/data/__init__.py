"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .bookmarks import Bookmark, Bookmarks, load_bookmarks, save_bookmarks
from .command_history import load_command_history, save_command_history
from .config import (
    Configuration,
    load_configuration,
    save_configuration,
    set_configuration_file,
    update_configuration,
)
from .history import load_history, save_history
from .location_types import (
    can_be_negotiated_to_markdown,
    is_editable,
    looks_urllike,
    maybe_markdown,
)

##############################################################################
# Exports.
__all__ = [
    "Bookmark",
    "Bookmarks",
    "can_be_negotiated_to_markdown",
    "Configuration",
    "is_editable",
    "load_bookmarks",
    "load_command_history",
    "load_configuration",
    "load_history",
    "looks_urllike",
    "maybe_markdown",
    "save_bookmarks",
    "save_command_history",
    "save_configuration",
    "save_history",
    "set_configuration_file",
    "update_configuration",
]

### __init__.py ends here
