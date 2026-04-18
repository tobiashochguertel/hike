"""End-to-end tests for the Typer CLI surface."""

##############################################################################
# Python imports.
from __future__ import annotations

from pathlib import Path

##############################################################################
# Typer imports.
from typer.testing import CliRunner

##############################################################################
# Local imports.
from hike.cli.app import app

##############################################################################
_RUNNER = CliRunner()


##############################################################################
def test_cli_root_help_lists_real_commands() -> None:
    """The root Typer help should expose the full command tree."""
    result = _RUNNER.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "open" in result.stdout
    assert "config" in result.stdout
    assert "schema" in result.stdout
    assert "bindings" in result.stdout
    assert "themes" in result.stdout


##############################################################################
def test_cli_config_round_trip_works_with_real_files(tmp_path: Path) -> None:
    """Config init, set, get, and validate should work against a real file."""
    config_path = tmp_path / "custom" / "hike.yaml"

    init_result = _RUNNER.invoke(
        app,
        ["--config", str(config_path), "config", "init"],
    )
    set_result = _RUNNER.invoke(
        app,
        [
            "--config",
            str(config_path),
            "config",
            "set",
            "theme",
            "textual-light",
        ],
    )
    get_result = _RUNNER.invoke(
        app,
        ["--config", str(config_path), "config", "get", "theme"],
    )
    validate_result = _RUNNER.invoke(
        app,
        ["--config", str(config_path), "config", "validate"],
    )

    assert init_result.exit_code == 0
    assert config_path.is_file()
    assert "Created configuration file:" in init_result.stdout
    assert set_result.exit_code == 0
    assert "Set theme" in set_result.stdout
    assert get_result.exit_code == 0
    assert get_result.stdout.strip() == "textual-light"
    assert validate_result.exit_code == 0
    assert "Configuration is valid:" in validate_result.stdout


##############################################################################
def test_cli_schema_and_metadata_commands_work_end_to_end(tmp_path: Path) -> None:
    """Schema export plus metadata subcommands should work without monkeypatching."""
    export_root = tmp_path / "schemas"

    schema_result = _RUNNER.invoke(
        app,
        ["schema", "export", "--out", str(export_root)],
    )
    themes_result = _RUNNER.invoke(app, ["themes", "list"])
    bindings_result = _RUNNER.invoke(app, ["bindings", "list"])

    assert schema_result.exit_code == 0
    assert (export_root / "hike.config.schema.json").is_file()
    assert (export_root / "hike.env.schema.json").is_file()
    assert themes_result.exit_code == 0
    assert "textual-dark" in themes_result.stdout
    assert bindings_result.exit_code == 0
    assert "JumpToSidebarView" in bindings_result.stdout
    assert "ToggleLocalBrowserMode" in bindings_result.stdout


##############################################################################
def test_cli_root_metadata_flags_work_end_to_end() -> None:
    """Version and license flags should be available on the root command."""
    version_result = _RUNNER.invoke(app, ["--version"])
    license_result = _RUNNER.invoke(app, ["--license"])

    assert version_result.exit_code == 0
    assert "hike v1.5.0" in version_result.stdout
    assert "commit:" in version_result.stdout
    assert "branch:" in version_result.stdout
    assert license_result.exit_code == 0
    assert "GNU General Public License" in license_result.stdout


### test_cli_e2e.py ends here
