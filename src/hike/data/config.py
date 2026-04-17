"""Code relating to Hike's typed configuration file."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import cache
from io import StringIO
from json import JSONDecodeError, dumps, loads
from pathlib import Path
from types import UnionType
from typing import Any, Union, cast, get_args, get_origin

##############################################################################
# Pydantic imports.
from pydantic import BaseModel, ConfigDict, Field

##############################################################################
# Ruamel imports.
from ruamel.yaml import YAML

##############################################################################
# Local imports.
from .locations import config_dir
from .settings import load_runtime_settings

##############################################################################
_CONFIG_FILENAME = "config.yaml"
_PROJECT_CONFIG_FILENAME = "hike.config.yaml"
_LEGACY_CONFIG_FILENAME = "configuration.json"
_LEGACY_DOTFILE_NAME = ".hike.yaml"

_configuration_override: Path | None = None
"""An optional override for the configuration file path."""


##############################################################################
class Configuration(BaseModel):
    """The typed configuration data for the application."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    theme: str | None = Field(
        default=None,
        description="The Textual theme for the application.",
    )
    navigation_visible: bool = Field(
        default=True,
        description="Show the navigation sidebar by default on wide terminals.",
    )
    navigation_on_right: bool = Field(
        default=False,
        description="Dock the navigation sidebar on the right side of the screen.",
    )
    sidebar_default_width_percent: int = Field(
        default=22,
        description="Default sidebar width as a percentage of the terminal width.",
    )
    sidebar_min_width: int = Field(
        default=24,
        description="Minimum sidebar width in terminal cells.",
    )
    sidebar_max_width: int = Field(
        default=60,
        description="Maximum sidebar width in terminal cells.",
    )
    sidebar_max_width_percent: int = Field(
        default=45,
        description="Maximum sidebar width as a percentage of the terminal width.",
    )
    sidebar_auto_fit: bool = Field(
        default=True,
        description="Automatically grow or shrink the sidebar to fit visible content.",
    )
    markdown_extensions: list[str] = Field(
        default_factory=lambda: [".md", ".markdown"],
        description="File extensions that should be treated as Markdown documents.",
    )
    markdown_content_types: list[str] = Field(
        default_factory=lambda: ["text/plain", "text/markdown", "text/x-markdown"],
        description="HTTP content types that should be treated as Markdown.",
    )
    command_line_on_top: bool = Field(
        default=False,
        description="Place the command line at the top of the screen instead of the bottom.",
    )
    responsive_auto_switch_narrow: bool = Field(
        default=True,
        description="Automatically switch to a single-pane layout on narrow terminals.",
    )
    responsive_narrow_width: int = Field(
        default=100,
        description="Terminal width threshold where Hike switches to narrow responsive mode.",
    )
    responsive_narrow_mode: str = Field(
        default="content-only",
        description="Default pane shown when narrow responsive mode activates.",
    )
    main_branches: list[str] = Field(
        default_factory=lambda: ["main", "master"],
        description="Branch names that should be considered main branches on forges.",
    )
    obsidian_vaults: str = Field(
        default="~/Library/Mobile Documents/iCloud~md~obsidian/Documents",
        description="Directory that contains Obsidian vaults for the forge/open commands.",
    )
    local_start_location: str = Field(
        default="~",
        description="Default starting directory for the local Markdown browser.",
    )
    local_use_ignore_files: bool = Field(
        default=True,
        description="Respect .gitignore and .ignore files in the local browser.",
    )
    local_show_hidden: bool = Field(
        default=False,
        description="Show hidden files and directories in the local browser.",
    )
    local_exclude_patterns: list[str] = Field(
        default_factory=list,
        description="Additional glob patterns to exclude from the local browser.",
    )
    local_browser_view_mode: str = Field(
        default="flat-list",
        description="Default rendering mode for the local browser.",
    )
    bindings: dict[str, str] = Field(
        default_factory=dict,
        description="Keyboard binding overrides keyed by Hike command class name.",
    )
    focus_viewer_on_load: bool = Field(
        default=True,
        description="Move focus to the document viewer when a Markdown file loads.",
    )
    show_front_matter: bool = Field(
        default=True,
        description="Show front matter blocks in the document viewer when present.",
    )
    allow_traditional_quit: bool = Field(
        default=False,
        description="Allow Ctrl+C to quit immediately instead of showing Textual help.",
    )


##############################################################################
def _yaml() -> YAML:
    """Create a configured YAML serializer."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


##############################################################################
def _normalize_configuration_path(path: str | Path) -> Path:
    """Normalise a configuration file path."""
    normalized = Path(path).expanduser()
    if not normalized.is_absolute():
        normalized = Path.cwd() / normalized
    return normalized


##############################################################################
def project_configuration_file() -> Path:
    """Return the project-local configuration file path."""
    return Path.cwd() / _PROJECT_CONFIG_FILENAME


##############################################################################
def default_configuration_file() -> Path:
    """Return the default user-scoped configuration file path."""
    return config_dir() / _CONFIG_FILENAME


##############################################################################
def legacy_configuration_file() -> Path:
    """Return the legacy JSON configuration path."""
    return config_dir() / _LEGACY_CONFIG_FILENAME


##############################################################################
def _explicit_configuration_file() -> Path | None:
    """Return an explicitly selected configuration file path, if any."""
    if _configuration_override is not None:
        return _configuration_override
    settings = load_runtime_settings()
    if settings.config_path is not None:
        return _normalize_configuration_path(settings.config_path)
    return None


##############################################################################
def _legacy_dotfile() -> Path:
    """Return the legacy dotfile configuration path."""
    return Path.home() / _LEGACY_DOTFILE_NAME


##############################################################################
def set_configuration_file(path: str | Path | None) -> Path:
    """Set the configuration file path override."""
    global _configuration_override
    load_configuration.cache_clear()
    _configuration_override = (
        None if path is None else _normalize_configuration_path(path)
    )
    return configuration_file()


##############################################################################
def configuration_file() -> Path:
    """Return the effective configuration file path."""
    if explicit := _explicit_configuration_file():
        return explicit
    for candidate in (
        project_configuration_file(),
        default_configuration_file(),
        _legacy_dotfile(),
        legacy_configuration_file(),
    ):
        if candidate.exists():
            return candidate
    return default_configuration_file()


##############################################################################
def configuration_init_paths() -> tuple[Path, Path | None]:
    """Return the preferred init target and any existing file that should be replaced."""
    if explicit := _explicit_configuration_file():
        return explicit, explicit if explicit.exists() else None

    project = project_configuration_file()
    if project.exists():
        return project, project

    default = default_configuration_file()
    if default.exists():
        return default, default

    for legacy in (_legacy_dotfile(), legacy_configuration_file()):
        if legacy.exists():
            return default, legacy

    return default, None


##############################################################################
def _load_json_configuration(path: Path) -> dict[str, Any]:
    """Load legacy JSON configuration data."""
    raw = path.read_text(encoding="utf-8")
    try:
        loaded = loads(raw)
    except JSONDecodeError:
        # Older typed-config builds could mistakenly write YAML into the legacy
        # JSON path during `config init --force`; accept that shape so users can
        # recover without manually editing files first.
        loaded = _yaml().load(raw)
    if not isinstance(loaded, dict):
        raise ValueError(f"Configuration root must be an object: {path}")
    return cast(dict[str, Any], loaded)


##############################################################################
def _load_yaml_configuration(path: Path) -> dict[str, Any]:
    """Load YAML configuration data."""
    loaded = _yaml().load(path.read_text(encoding="utf-8"))
    return {} if loaded is None else loaded


##############################################################################
def _load_configuration_data(path: Path) -> dict[str, Any]:
    """Load configuration data from the given path."""
    if path.suffix.lower() == ".json":
        return _load_json_configuration(path)
    return _load_yaml_configuration(path)


##############################################################################
def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    """Write YAML configuration data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        _yaml().dump(data, handle)


##############################################################################
def save_configuration(configuration: Configuration) -> Configuration:
    """Save the given configuration."""
    load_configuration.cache_clear()
    target = configuration_file()
    data = configuration.model_dump(mode="json", exclude_none=False)
    if target.suffix.lower() == ".json":
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dumps(data, indent=4), encoding="utf-8")
    else:
        _write_yaml(target, data)
    return load_configuration()


##############################################################################
@cache
def load_configuration() -> Configuration:
    """Load the current configuration."""
    source = configuration_file()
    if not source.exists():
        return Configuration()
    return Configuration.model_validate(_load_configuration_data(source))


##############################################################################
@contextmanager
def update_configuration() -> Iterator[Configuration]:
    """Context manager for updating the configuration."""
    configuration = load_configuration()
    try:
        yield configuration
    finally:
        save_configuration(configuration)


##############################################################################
def configuration_schema() -> dict[str, Any]:
    """Return the JSON schema for the configuration model."""
    return Configuration.model_json_schema()


##############################################################################
def dump_configuration(format_name: str = "yaml") -> str:
    """Dump the active configuration in the requested format."""
    data = load_configuration().model_dump(mode="json", exclude_none=False)
    match format_name:
        case "json":
            return dumps(data, indent=2) + "\n"
        case "yaml":
            buffer = StringIO()
            _yaml().dump(data, buffer)
            return buffer.getvalue()
        case _:
            raise ValueError(f"Unsupported configuration format: {format_name}")


##############################################################################
def validate_configuration_file(path: str | Path | None = None) -> Configuration:
    """Validate the configuration file at the given path or the active path."""
    source = (
        configuration_file() if path is None else _normalize_configuration_path(path)
    )
    if not source.exists():
        raise FileNotFoundError(source)
    return Configuration.model_validate(_load_configuration_data(source))


##############################################################################
def _type_name(annotation: Any) -> tuple[str, list[str] | None]:
    """Return a human-readable type name and optional allowed values."""
    origin = get_origin(annotation)
    if origin is None:
        if annotation is str:
            return "string", None
        if annotation is bool:
            return "boolean", None
        if annotation is int:
            return "integer", None
        if annotation is float:
            return "number", None
        if annotation is dict[str, str] or annotation is dict:
            return "mapping", None
        if annotation is list[str] or annotation is list:
            return "list", None
        if annotation is type(None):
            return "null", None
        return getattr(annotation, "__name__", str(annotation)), None
    if origin in {Union, UnionType}:
        parts: list[str] = []
        allowed: list[str] = []
        for item in get_args(annotation):
            item_type, item_allowed = _type_name(item)
            if item_type not in parts:
                parts.append(item_type)
            if item_allowed is not None:
                allowed.extend(item_allowed)
        return " | ".join(parts), allowed or None
    if str(origin).endswith("Literal"):
        values = [str(value) for value in get_args(annotation)]
        return "string", values
    if origin is list:
        return f"list[{_type_name(get_args(annotation)[0])[0]}]", None
    if origin is dict:
        return "mapping", None
    return str(origin), None


##############################################################################
def _yaml_fragment(name: str, value: Any) -> list[str]:
    """Dump a single top-level field as YAML lines."""
    buffer = StringIO()
    _yaml().dump({name: value}, buffer)
    return buffer.getvalue().rstrip().splitlines()


##############################################################################
def render_default_configuration() -> str:
    """Render a commented default configuration file."""
    lines = [
        "# ---------------------------------------------------------------------------",
        "# Hike configuration — generated by `hike config init`",
        "# Edit values below and run `hike config validate` after changes.",
        "# ---------------------------------------------------------------------------",
        "",
    ]
    defaults = Configuration().model_dump(mode="json", exclude_none=False)
    for name, field in Configuration.model_fields.items():
        type_name, allowed = _type_name(field.annotation)
        description = field.description or f"Configure `{name}`."
        default = defaults.get(name)
        lines.append(f"# {description}")
        lines.append(f"# Type:    {type_name}")
        if allowed:
            lines.append(f"# Allowed: {' | '.join(allowed)}")
        if default is None:
            lines.append(
                "# OPTIONAL — uncomment and set a value to override the default"
            )
            lines.append(f"# {name}: null")
        else:
            lines.append(f"# Default: {default!r}")
            lines.extend(_yaml_fragment(name, default))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


##############################################################################
def _parse_property_path(path: str) -> list[str | int]:
    """Parse a dot/bracket property path."""
    tokens: list[str | int] = []
    current = ""
    index = 0
    while index < len(path):
        character = path[index]
        if character == ".":
            if current:
                tokens.append(current)
                current = ""
            index += 1
            continue
        if character == "[":
            if current:
                tokens.append(current)
                current = ""
            end = path.find("]", index)
            if end == -1:
                raise ValueError(f"Invalid property path: {path}")
            raw = path[index + 1 : end]
            tokens.append(int(raw) if raw.isdigit() else raw)
            index = end + 1
            continue
        current += character
        index += 1
    if current:
        tokens.append(current)
    if not tokens:
        raise ValueError("Property path must not be empty")
    return tokens


##############################################################################
def _load_raw_configuration() -> dict[str, Any]:
    """Return the current configuration as a mutable raw mapping."""
    source = configuration_file()
    if source.exists():
        return _load_configuration_data(source)
    return {}


##############################################################################
def _get_value(data: Any, path: list[str | int]) -> Any:
    """Resolve a nested property path from data."""
    current = data
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list):
                raise KeyError(part)
            current = current[part]
            continue
        if not isinstance(current, dict):
            raise KeyError(part)
        current = current[part]
    return current


##############################################################################
def _set_value(data: Any, path: list[str | int], value: Any) -> None:
    """Set a nested property path within data."""
    current = data
    for part in path[:-1]:
        if isinstance(part, int):
            if not isinstance(current, list):
                raise KeyError(part)
            current = current[part]
            continue
        current = current.setdefault(part, {})
    final = path[-1]
    if isinstance(final, int):
        if not isinstance(current, list):
            raise KeyError(final)
        while len(current) <= final:
            current.append(None)
        current[final] = value
        return
    if not isinstance(current, dict):
        raise KeyError(final)
    current[final] = value


##############################################################################
def _unset_value(data: Any, path: list[str | int]) -> None:
    """Unset a nested property path within data."""
    current = data
    for part in path[:-1]:
        if isinstance(part, int):
            if not isinstance(current, list):
                raise KeyError(part)
            current = current[part]
            continue
        if not isinstance(current, dict):
            raise KeyError(part)
        current = current[part]
    final = path[-1]
    if isinstance(final, int):
        if not isinstance(current, list):
            raise KeyError(final)
        del current[final]
        return
    if not isinstance(current, dict):
        raise KeyError(final)
    del current[final]


##############################################################################
def _coerce_value(raw: str) -> Any:
    """Coerce a CLI value using YAML parsing rules."""
    parsed = _yaml().load(raw)
    return (
        raw if parsed is None and raw.strip().lower() not in {"null", "~"} else parsed
    )


##############################################################################
def get_configuration_value(path: str) -> Any:
    """Return a single configuration property."""
    return _get_value(
        load_configuration().model_dump(mode="json"), _parse_property_path(path)
    )


##############################################################################
def set_configuration_value(path: str, raw_value: str) -> Configuration:
    """Set a single configuration property and validate the result."""
    data = _load_raw_configuration()
    _set_value(data, _parse_property_path(path), _coerce_value(raw_value))
    return save_configuration(Configuration.model_validate(data))


##############################################################################
def unset_configuration_value(path: str) -> Configuration:
    """Unset a configuration property and validate the result."""
    data = _load_raw_configuration()
    _unset_value(data, _parse_property_path(path))
    return save_configuration(Configuration.model_validate(data))


### config.py ends here
