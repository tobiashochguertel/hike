"""Tests for startup target handling."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.__main__ import main as cli_main
from hike.startup import StartupTargetKind, classify_startup_target


##############################################################################
class _FakeApp:
    """Small stub for testing the CLI entrypoint argument handling."""

    args: list[str] | None = None
    prog_name: str | None = None
    called_without_args: bool = False

    def __call__(self, *, prog_name: str, args: list[str] | None = None) -> None:
        """Capture the forwarded Typer arguments."""
        self.args = args
        self.prog_name = prog_name
        self.called_without_args = args is None


##############################################################################
def test_cli_main_maps_empty_invocation_to_root_help(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The installed entrypoint should follow Typer's direct-app pattern."""
    fake_app = _FakeApp()
    monkeypatch.setattr("hike.__main__.app", fake_app)

    cli_main()

    assert fake_app.called_without_args is True
    assert fake_app.args is None
    assert fake_app.prog_name == "hike"


##############################################################################
def test_cli_main_preserves_explicit_subcommands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit subcommands should reach Typer unchanged."""
    fake_app = _FakeApp()
    monkeypatch.setattr("hike.__main__.app", fake_app)

    cli_main(["open", "docs"])

    assert fake_app.args == ["open", "docs"]
    assert fake_app.prog_name == "hike"


##############################################################################
def test_classify_startup_target_handles_missing_target() -> None:
    """A missing startup target should be classified clearly."""
    startup = classify_startup_target(None)

    assert startup.kind is StartupTargetKind.NONE
    assert startup.value is None


##############################################################################
def test_classify_startup_target_handles_file(tmp_path: Path) -> None:
    """A file target should be resolved and classified as a file."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n")

    startup = classify_startup_target(str(target))

    assert startup.kind is StartupTargetKind.FILE
    assert startup.value == target.resolve()


##############################################################################
def test_classify_startup_target_handles_directory(tmp_path: Path) -> None:
    """A directory target should be resolved and classified as a directory."""
    target = tmp_path / "docs"
    target.mkdir()

    startup = classify_startup_target(str(target))

    assert startup.kind is StartupTargetKind.DIRECTORY
    assert startup.value == target.resolve()


##############################################################################
def test_classify_startup_target_handles_url() -> None:
    """A URL target should be preserved as a URL."""
    startup = classify_startup_target("https://example.com/README.md")

    assert startup.kind is StartupTargetKind.URL
    assert str(startup.value) == "https://example.com/README.md"


##############################################################################
def test_classify_startup_target_handles_missing_path(tmp_path: Path) -> None:
    """A non-existent target should not be mistaken for a command."""
    target = tmp_path / "missing.md"

    startup = classify_startup_target(str(target))

    assert startup.kind is StartupTargetKind.MISSING
    assert startup.value == str(target)


### test_startup.py ends here
