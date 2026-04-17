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
from hike.data import resolve_runtime_context
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
    monkeypatch.setattr(
        "hike.cli.app.run_hike",
        lambda options: (
            captured.update({"options": options, "ran": True}),
            None,
        )[1],
    )
    monkeypatch.setattr(
        "hike.cli.app.resolve_cli_runtime_context",
        lambda config_path, env_path: (
            captured.update({"config_path": config_path, "env_path": env_path}),
            resolve_runtime_context(config_path=config_path, env_path=env_path),
        )[1],
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
    assert cast(
        OpenOptions, captured["options"]
    ).runtime_context == resolve_runtime_context(
        config_path="custom-hike.yaml",
        env_path="custom-hike.env",
    )


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


##############################################################################
def test_root_cli_help_lists_commands_without_launching_tui(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Root help should stay on the command tree and avoid launching the TUI."""
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Usage: hike [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "open" in result.output
    assert "config" in result.output
    assert "ran" not in captured


##############################################################################
def test_root_cli_version_does_not_launch_tui(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The root callback should expose `--version` without loading the TUI."""
    monkeypatch.setattr(
        "hike.cli.app.run_hike",
        lambda _options: pytest.fail("Root --version should not load the TUI"),
    )

    result = _RUNNER.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "hike v" in result.output


##############################################################################
def test_open_command_theme_question_uses_theme_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--theme ?` should list themes without launching the TUI."""
    monkeypatch.setattr("hike.cli.app.theme_names", lambda: ["dark", "light"])
    monkeypatch.setattr(
        "hike.cli.app.run_hike",
        lambda _options: pytest.fail("Theme listing should not launch the TUI"),
    )

    result = _RUNNER.invoke(app, ["open", "--theme", "?"])

    assert result.exit_code == 0
    assert result.output.splitlines() == ["dark", "light"]


##############################################################################
def test_root_cli_rejects_bare_target_without_open_subcommand(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A startup target should require the explicit `open` subcommand."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n", encoding="utf-8")
    captured = _install_open_spy(monkeypatch)

    result = _RUNNER.invoke(app, [str(target)])

    assert result.exit_code != 0
    assert "No such command" in result.output
    assert "ran" not in captured


### test_cli_options.py ends here
