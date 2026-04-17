"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .bookmarks import Bookmark, Bookmarks, load_bookmarks, save_bookmarks
from .command_history import load_command_history, save_command_history
from .config import (
    Configuration,
    clear_configuration_cache,
    configuration_file,
    configuration_init_paths,
    configuration_schema,
    dump_configuration,
    get_configuration_value,
    load_configuration,
    render_default_configuration,
    save_configuration,
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
from .runtime_context import (
    RuntimeContext,
    resolve_runtime_context,
    use_runtime_context,
)
from .settings import (
    RuntimeSettings,
    clear_runtime_settings_cache,
    environment_file,
    environment_variable_names,
    load_environment_values,
    load_runtime_settings,
    runtime_settings_schema,
)

##############################################################################
# Exports.
__all__ = [
    "Bookmark",
    "Bookmarks",
    "can_be_negotiated_to_markdown",
    "clear_configuration_cache",
    "clear_runtime_settings_cache",
    "Configuration",
    "configuration_init_paths",
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
    "resolve_runtime_context",
    "RuntimeSettings",
    "RuntimeContext",
    "save_bookmarks",
    "save_command_history",
    "save_configuration",
    "save_history",
    "set_configuration_value",
    "runtime_settings_schema",
    "unset_configuration_value",
    "update_configuration",
    "use_runtime_context",
    "validate_configuration_file",
]

### __init__.py ends here
