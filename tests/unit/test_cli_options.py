"""Tests for Typer CLI startup options."""

##############################################################################
# Python imports.
from pathlib import Path
from typing import cast

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Typer imports.
from typer.testing import CliRunner

##############################################################################
# Local imports.
from hike.cli.app import app
from hike.startup import OpenOptions

##############################################################################
_RUNNER = CliRunner()


##############################################################################
class _FakeHike:
    """Small fake application used to capture launch options in tests."""

    HELP_LICENSE = "Fake license"
    captured: dict[str, object] = {}

    def __init__(self, options: OpenOptions) -> None:
        self.options = options
        _FakeHike.captured["options"] = options

    def run(self) -> None:
        """Capture that the TUI would have launched."""
        _FakeHike.captured["ran"] = True


##############################################################################
def _install_open_spy(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Patch the open command so tests can inspect the captured options."""
    captured: dict[str, object] = {}
    _FakeHike.captured = captured
    monkeypatch.setattr("hike.cli.app.Hike", _FakeHike)
    monkeypatch.setattr(
        "hike.cli.app.apply_runtime_path_overrides",
        lambda config_path, env_path: captured.update(
            {
                "config_path": config_path,
                "env_path": env_path,
            }
        ),
    )
    return captured


##############################################################################
def test_open_command_accepts_root_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The local browser root should be configurable from the CLI."""
    root = tmp_path / "docs"
    root.mkdir()
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(app, ["open", "--root", str(root)])

    assert result.exit_code == 0
    assert captured["ran"] is True
    assert cast(OpenOptions, captured["options"]).root == str(root)


##############################################################################
def test_open_command_rejects_missing_root_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI should reject a root override that is not a directory."""
    _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(app, ["open", "--root", str(tmp_path / "missing")])

    assert result.exit_code != 0
    assert "--root must point to an existing directory" in result.output


##############################################################################
def test_open_command_accepts_discovery_toggles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Boolean discovery flags should be exposed on the CLI."""
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(app, ["open", "--no-ignore", "--hidden"])

    assert result.exit_code == 0
    assert cast(OpenOptions, captured["options"]).ignore is False
    assert cast(OpenOptions, captured["options"]).hidden is True


##############################################################################
def test_open_command_accepts_repeatable_excludes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exclude globs should be repeatable."""
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(
        app,
        ["open", "--exclude", "node_modules/", "--exclude", "**/generated/"],
    )

    assert result.exit_code == 0
    assert cast(OpenOptions, captured["options"]).exclude == (
        "node_modules/",
        "**/generated/",
    )


##############################################################################
def test_open_command_applies_runtime_path_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Alternate config and env paths should be accepted."""
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(
        app,
        [
            "open",
            "--config",
            "custom-hike.yaml",
            "--env-file",
            "custom-hike.env",
        ],
    )

    assert result.exit_code == 0
    assert captured["config_path"] == Path("custom-hike.yaml")
    assert captured["env_path"] == Path("custom-hike.env")


##############################################################################
def test_open_command_accepts_startup_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A startup command should be split into the tuple passed to the app."""
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(app, ["open", "--command", "gh davep/hike"])

    assert result.exit_code == 0
    assert cast(OpenOptions, captured["options"]).command == ("gh", "davep/hike")


##############################################################################
def test_open_command_rejects_target_and_command_together(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Startup targets and startup commands should be mutually exclusive."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n")
    _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(
        app,
        ["open", str(target), "--command", "gh davep/hike"],
    )

    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


### test_cli_options.py ends here
