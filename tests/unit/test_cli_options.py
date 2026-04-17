"""Tests for CLI discovery options."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.__main__ import get_args


##############################################################################
def test_get_args_accepts_root_override(tmp_path: Path) -> None:
    """The local browser root should be configurable from the CLI."""
    root = tmp_path / "docs"
    root.mkdir()

    args = get_args(["--root", str(root)])

    assert args.root == str(root)


##############################################################################
def test_get_args_rejects_missing_root_directory(tmp_path: Path) -> None:
    """The CLI should reject a root override that is not a directory."""
    with pytest.raises(SystemExit):
        get_args(["--root", str(tmp_path / "missing")])


##############################################################################
def test_get_args_accepts_discovery_toggles() -> None:
    """Boolean discovery flags should be exposed on the CLI."""
    args = get_args(["--no-ignore", "--hidden"])

    assert args.ignore is False
    assert args.hidden is True


##############################################################################
def test_get_args_accepts_repeatable_excludes() -> None:
    """Exclude globs should be repeatable."""
    args = get_args(["--exclude", "node_modules/", "--exclude", "**/generated/"])

    assert args.exclude == ["node_modules/", "**/generated/"]


##############################################################################
def test_get_args_accepts_config_override() -> None:
    """An alternate configuration file should be selectable."""
    args = get_args(["--config", "custom-hike.json"])

    assert args.config == "custom-hike.json"


### test_cli_options.py ends here
