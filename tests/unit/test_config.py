"""Tests for configuration path overrides and discovery defaults."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from hike.data.config import (
    Configuration,
    configuration_file,
    load_configuration,
    save_configuration,
    set_configuration_file,
)
from hike.data.discovery import local_discovery_options


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


### test_config.py ends here
