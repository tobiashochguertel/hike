"""Tests for startup target handling."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.__main__ import get_args
from hike.startup import (
    StartupTargetKind,
    classify_startup_target,
)


##############################################################################
def test_get_args_accepts_startup_target(tmp_path: Path) -> None:
    """A positional argument should be treated as a startup target."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n")

    args = get_args([str(target)])

    assert args.target == str(target)
    assert args.command is None


##############################################################################
def test_get_args_accepts_explicit_startup_command() -> None:
    """An internal command should be preserved behind --command."""
    args = get_args(["--command", "gh", "davep/hike"])

    assert args.target is None
    assert args.command == ["gh", "davep/hike"]


##############################################################################
def test_get_args_rejects_target_and_command_together(tmp_path: Path) -> None:
    """Startup targets and startup commands should be mutually exclusive."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n")

    with pytest.raises(SystemExit):
        get_args([str(target), "--command", "gh", "davep/hike"])


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
