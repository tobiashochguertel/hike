"""Service helpers used by the Typer CLI."""

##############################################################################
# Python imports.
from __future__ import annotations

from dataclasses import dataclass
from inspect import cleandoc
from operator import attrgetter
from pathlib import Path
from shlex import split as split_shell_words

##############################################################################
# Local imports.
from ..app_info import APP_BUILD_INFO, APP_VERSION, HELP_LICENSE
from ..command_catalog import MAIN_COMMAND_MESSAGES
from ..data import (
    Configuration,
    RuntimeContext,
    configuration_init_paths,
    load_configuration,
    render_default_configuration,
    resolve_runtime_context,
    save_configuration,
)
from ..keybinding_catalog import (
    keybinding_set_names as static_keybinding_set_names,
)
from ..keybinding_catalog import (
    keybinding_set_source,
    resolve_keybindings,
)
from ..startup import OpenOptions
from ..theme_catalog import theme_names as static_theme_names
from .contracts import OpenCommandRequest


##############################################################################
@dataclass(frozen=True)
class BindingSummary:
    """A user-facing description of a configurable keybinding."""

    command_name: str
    tooltip: str
    default_key: str
    current_key: str


##############################################################################
@dataclass(frozen=True)
class BindingSetSummary:
    """A user-facing description of an available keybinding set."""

    name: str
    source: str
    active: bool


##############################################################################
@dataclass(frozen=True)
class ConfigInitResult:
    """The result of initializing a configuration file."""

    target: Path
    backup: Path | None


##############################################################################
def version_text() -> str:
    """Return the CLI version string."""
    lines = [f"hike v{APP_VERSION}"]
    if APP_BUILD_INFO.git_sha is not None:
        lines.append(f"commit: {APP_BUILD_INFO.git_sha}")
    if APP_BUILD_INFO.git_branch is not None:
        lines.append(f"branch: {APP_BUILD_INFO.git_branch}")
    if APP_BUILD_INFO.build_timestamp is not None:
        lines.append(f"built: {APP_BUILD_INFO.build_timestamp}")
    return "\n".join(lines)


##############################################################################
def license_text() -> str:
    """Return the application license text."""
    return cleandoc(HELP_LICENSE)


##############################################################################
def theme_names() -> list[str]:
    """Return the sorted list of available theme names."""
    return static_theme_names()


##############################################################################
def keybinding_set_summaries(
    context: RuntimeContext | None = None,
) -> list[BindingSetSummary]:
    """Return the available keybinding sets and the active one."""
    configuration = load_configuration(context)
    return [
        BindingSetSummary(
            name=name,
            source=keybinding_set_source(name, configuration.binding_sets),
            active=name == configuration.binding_set,
        )
        for name in static_keybinding_set_names(configuration.binding_sets)
    ]


##############################################################################
def binding_summaries(
    context: RuntimeContext | None = None,
) -> list[BindingSummary]:
    """Return the configurable keybinding summaries."""
    configuration = load_configuration(context)
    keymap = resolve_keybindings(
        configuration.binding_set,
        custom_sets=configuration.binding_sets,
        overrides=configuration.bindings,
    )
    summaries: list[BindingSummary] = []
    for command in sorted(MAIN_COMMAND_MESSAGES, key=attrgetter("__name__")):
        if command().has_binding:
            summaries.append(
                BindingSummary(
                    command_name=command.__name__,
                    tooltip=command.tooltip(),
                    default_key=command.binding().key,
                    current_key=keymap.get(command.__name__, command.binding().key),
                )
            )
    return summaries


##############################################################################
def build_open_options(
    request: OpenCommandRequest,
    runtime_context: RuntimeContext | None = None,
) -> OpenOptions:
    """Build validated TUI startup options from CLI inputs."""
    if request.root is not None and not request.root.expanduser().is_dir():
        raise ValueError("--root must point to an existing directory")
    if request.target is not None and request.command is not None:
        raise ValueError("TARGET and --command are mutually exclusive")
    if (
        request.binding_set is not None
        and request.binding_set
        not in static_keybinding_set_names(
            load_configuration(runtime_context).binding_sets
        )
    ):
        raise ValueError(
            f"Unknown --binding-set {request.binding_set!r}; use `hike bindings sets` to inspect available sets."
        )
    return OpenOptions(
        target=request.target,
        command=(
            None
            if request.command is None
            else tuple(split_shell_words(request.command))
        ),
        navigation=request.navigation,
        theme=request.theme,
        binding_set=request.binding_set,
        root=None if request.root is None else str(request.root),
        ignore=request.ignore,
        hidden=request.hidden,
        exclude=request.exclude,
        runtime_context=runtime_context,
    )


##############################################################################
def run_hike(options: OpenOptions) -> None:
    """Launch the Textual application for the given startup options."""
    from ..runtime.bootstrap import launch_hike

    launch_hike(options)


##############################################################################
def initialize_configuration(
    force: bool,
    context: RuntimeContext | None = None,
) -> ConfigInitResult:
    """Create or replace the active configuration file."""
    active = resolve_runtime_context() if context is None else context
    target, existing = configuration_init_paths(active)
    if existing is not None and not force:
        raise FileExistsError(existing)

    backup: Path | None = None
    if existing is not None:
        from datetime import datetime

        backup = existing.with_name(
            f"{existing.name}.bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        existing.replace(backup)

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".json":
        save_configuration(
            Configuration(),
            resolve_runtime_context(
                config_path=target,
                env_path=active.env_path,
                cwd=active.cwd,
            ),
        )
    else:
        target.write_text(render_default_configuration(), encoding="utf-8")
    return ConfigInitResult(target=target, backup=backup)


### services.py ends here
