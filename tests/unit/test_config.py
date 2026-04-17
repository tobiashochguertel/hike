"""Tests for configuration path overrides and discovery defaults."""

##############################################################################
# Python imports.
from pathlib import Path
from types import SimpleNamespace

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Typer imports.
from typer.testing import CliRunner

##############################################################################
# Local imports.
from hike.cli.app import app as cli_app
from hike.data.config import (
    Configuration,
    configuration_file,
    load_configuration,
    render_default_configuration,
    save_configuration,
    set_configuration_file,
)
from hike.data.discovery import local_discovery_options
from hike.data.layout import LayoutMode, layout_policy
from hike.data.local_browser import (
    LocalBrowserMode,
    local_browser_mode_from_configuration,
)
from hike.hike import Hike
from hike.startup import OpenOptions

##############################################################################
_RUNNER = CliRunner()


##############################################################################
def _patch_config_locations(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Path:
    """Point configuration resolution at a temporary test location."""
    config_root = tmp_path / ".config" / "hike"
    config_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("hike.data.config.config_dir", lambda: config_root)
    monkeypatch.setattr(
        "hike.data.config._legacy_dotfile", lambda: tmp_path / ".hike.yaml"
    )
    monkeypatch.setattr(
        "hike.data.config.load_runtime_settings",
        lambda: SimpleNamespace(config_path=None),
    )
    return config_root


##############################################################################
def test_set_configuration_file_uses_override(tmp_path: Path) -> None:
    """The configuration path should be overridable from the CLI."""
    override = tmp_path / "custom" / "hike.json"

    try:
        set_configuration_file(override)

        assert configuration_file() == override
    finally:
        set_configuration_file(None)


##############################################################################
def test_save_configuration_creates_override_parent_directory(tmp_path: Path) -> None:
    """Saving to an override path should create its parent directory."""
    override = tmp_path / "custom" / "hike.json"

    try:
        set_configuration_file(override)
        save_configuration(Configuration())

        assert override.is_file()
    finally:
        set_configuration_file(None)


##############################################################################
def test_discovery_options_use_configuration_defaults(tmp_path: Path) -> None:
    """Configuration defaults should feed into the local browser options."""
    override = tmp_path / "config.json"

    try:
        set_configuration_file(override)
        save_configuration(
            Configuration(
                local_use_ignore_files=False,
                local_show_hidden=True,
                local_exclude_patterns=["generated/", "node_modules/"],
            )
        )
        config = load_configuration()

        args = type(
            "Args",
            (),
            {"ignore": None, "hidden": None, "exclude": []},
        )()
        options = local_discovery_options(args, config)

        assert options.use_ignore_files is False
        assert options.show_hidden is True
        assert options.exclude_patterns == ("generated/", "node_modules/")
    finally:
        set_configuration_file(None)


##############################################################################
def test_layout_policy_uses_configuration_defaults() -> None:
    """Layout policy should be derived from persisted configuration values."""
    policy = layout_policy(
        Configuration(
            sidebar_default_width_percent=30,
            sidebar_min_width=20,
            sidebar_max_width=48,
            sidebar_max_width_percent=35,
            sidebar_auto_fit=False,
            responsive_auto_switch_narrow=False,
            responsive_narrow_width=88,
            responsive_narrow_mode="sidebar-only",
        )
    )

    assert policy.sidebar.default_width_percent == 30
    assert policy.sidebar.min_width == 20
    assert policy.sidebar.max_width == 48
    assert policy.sidebar.max_width_percent == 35
    assert policy.sidebar.auto_fit is False
    assert policy.responsive.auto_switch_narrow is False
    assert policy.responsive.narrow_width == 88
    assert policy.responsive.narrow_mode is LayoutMode.SIDEBAR_ONLY


##############################################################################
def test_layout_policy_rejects_invalid_narrow_mode() -> None:
    """Invalid responsive layout modes should fail fast."""
    with pytest.raises(ValueError, match="responsive_narrow_mode"):
        layout_policy(Configuration(responsive_narrow_mode="broken"))


##############################################################################
def test_local_browser_mode_configuration_accepts_flat_list() -> None:
    """The configured local browser mode should be parseable."""
    assert (
        local_browser_mode_from_configuration(
            Configuration(local_browser_view_mode="flat-list").local_browser_view_mode
        )
        is LocalBrowserMode.FLAT_LIST
    )


##############################################################################
def test_hike_applies_theme_and_binding_overrides_from_configuration(
    tmp_path: Path,
) -> None:
    """Runtime startup should consume persisted theme and binding overrides."""
    override = tmp_path / "config.yaml"

    try:
        set_configuration_file(override)
        save_configuration(
            Configuration(
                theme="textual-light",
                bindings={"JumpToBookmarks": "shift+f6"},
            )
        )

        app = Hike(OpenOptions())

        assert app.theme == "textual-light"
        assert app._keymap["JumpToBookmarks"] == "shift+f6"
    finally:
        set_configuration_file(None)


##############################################################################
def test_load_configuration_accepts_yaml_in_legacy_json_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Broken YAML-in-JSON legacy configs should still be readable."""
    config_root = _patch_config_locations(monkeypatch, tmp_path)
    legacy = config_root / "configuration.json"
    legacy.write_text(
        "navigation_visible: false\nmain_branches:\n  - trunk\n",
        encoding="utf-8",
    )

    try:
        load_configuration.cache_clear()
        config = load_configuration()
    finally:
        load_configuration.cache_clear()
        set_configuration_file(None)

    assert config.navigation_visible is False
    assert config.main_branches == ["trunk"]


##############################################################################
def test_config_init_migrates_legacy_json_to_default_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`config init --force` should migrate legacy JSON configs to YAML."""
    config_root = _patch_config_locations(monkeypatch, tmp_path)
    legacy = config_root / "configuration.json"
    legacy.write_text('{"navigation_visible": false}\n', encoding="utf-8")
    monkeypatch.setattr(
        "hike.cli.app.load_hike_class",
        lambda: pytest.fail("Config init should not load the TUI"),
    )

    try:
        result = _RUNNER.invoke(cli_app, ["config", "init", "--force"])
    finally:
        load_configuration.cache_clear()
        set_configuration_file(None)

    target = config_root / "config.yaml"
    backups = list(config_root.glob("configuration.json.bak-*"))

    assert result.exit_code == 0
    assert target.is_file()
    assert not legacy.exists()
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == '{"navigation_visible": false}\n'
    assert "# Hike configuration" in target.read_text(encoding="utf-8")


##############################################################################
def test_render_default_configuration_uses_readable_optional_type_names() -> None:
    """Optional fields should render human-readable union type comments."""
    rendered = render_default_configuration()

    assert "# Type:    string | null" in rendered


### test_config.py ends here
