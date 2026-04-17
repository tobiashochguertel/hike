"""Tests for startup target handling and argv normalization."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from hike.cli.app import normalize_argv
from hike.startup import (
    StartupTargetKind,
    classify_startup_target,
)


##############################################################################
def test_normalize_argv_promotes_empty_invocation_to_open() -> None:
    """Running `hike` with no subcommand should launch the open command."""
    assert normalize_argv([]) == ["open"]


##############################################################################
def test_normalize_argv_promotes_positional_target_to_open(tmp_path: Path) -> None:
    """A bare target should become `hike open TARGET`."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n", encoding="utf-8")

    assert normalize_argv([str(target)]) == ["open", str(target)]


##############################################################################
def test_normalize_argv_preserves_known_subcommands() -> None:
    """Real subcommands should not be rewritten."""
    assert normalize_argv(["config", "show"]) == ["config", "show"]


##############################################################################
def test_normalize_argv_collapses_legacy_command_tail() -> None:
    """Legacy `--command foo bar` syntax should still normalize cleanly."""
    assert normalize_argv(["--command", "gh", "davep/hike"]) == [
        "open",
        "--command",
        "gh davep/hike",
    ]


##############################################################################
def test_normalize_argv_preserves_root_help() -> None:
    """Root help should stay on the root command so subcommands remain visible."""
    assert normalize_argv(["--help"]) == ["--help"]
    assert normalize_argv(["--config", "custom.yaml", "--help"]) == [
        "--config",
        "custom.yaml",
        "--help",
    ]


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
