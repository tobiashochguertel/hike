"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .bookmarks import Bookmark, Bookmarks, load_bookmarks, save_bookmarks
from .command_history import load_command_history, save_command_history
from .config import (
    Configuration,
    configuration_file,
    configuration_schema,
    dump_configuration,
    get_configuration_value,
    load_configuration,
    render_default_configuration,
    save_configuration,
    set_configuration_file,
    set_configuration_value,
    unset_configuration_value,
    update_configuration,
    validate_configuration_file,
)
from .history import load_history, save_history
from .location_types import (
    can_be_negotiated_to_markdown,
    is_editable,
    looks_urllike,
    maybe_markdown,
)
from .settings import (
    RuntimeSettings,
    environment_file,
    environment_variable_names,
    load_environment_values,
    load_runtime_settings,
    runtime_settings_schema,
    set_environment_file,
)

##############################################################################
# Exports.
__all__ = [
    "Bookmark",
    "Bookmarks",
    "can_be_negotiated_to_markdown",
    "Configuration",
    "configuration_file",
    "configuration_schema",
    "dump_configuration",
    "environment_file",
    "environment_variable_names",
    "get_configuration_value",
    "is_editable",
    "load_bookmarks",
    "load_command_history",
    "load_configuration",
    "load_environment_values",
    "load_history",
    "load_runtime_settings",
    "looks_urllike",
    "maybe_markdown",
    "render_default_configuration",
    "RuntimeSettings",
    "save_bookmarks",
    "save_command_history",
    "save_configuration",
    "save_history",
    "set_configuration_file",
    "set_configuration_value",
    "set_environment_file",
    "runtime_settings_schema",
    "unset_configuration_value",
    "update_configuration",
    "validate_configuration_file",
]

### __init__.py ends here
