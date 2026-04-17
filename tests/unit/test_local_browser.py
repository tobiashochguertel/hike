"""Tests for local browser helpers."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.data.discovery import LocalDiscoveryOptions
from hike.data.local_browser import (
    LocalBrowserMode,
    flatten_local_paths,
    local_browser_mode_from_configuration,
    stable_root_label,
)


##############################################################################
def test_stable_root_label_prefers_paths_relative_to_cwd(tmp_path: Path) -> None:
    """Roots inside the current working tree should get a stable relative label."""
    workspace = tmp_path / "workspace"
    root = workspace / "docs" / "guide"
    root.mkdir(parents=True)

    assert stable_root_label(root, reference=workspace) == "docs/guide"


##############################################################################
def test_stable_root_label_uses_basename_outside_reference(tmp_path: Path) -> None:
    """Roots outside the reference path should fall back to a stable basename."""
    root = tmp_path / "outside" / "docs"
    root.mkdir(parents=True)

    assert stable_root_label(root, reference=tmp_path / "workspace") == "docs"


##############################################################################
def test_flatten_local_paths_returns_relative_files_and_directories(
    tmp_path: Path,
) -> None:
    """Flat-list mode should include relative file and directory entries."""
    root = tmp_path / "docs"
    nested = root / "guide" / "deep"
    nested.mkdir(parents=True)
    (root / "index.md").write_text("# Home\n", encoding="utf-8")
    (nested / "page.md").write_text("# Page\n", encoding="utf-8")

    entries = flatten_local_paths(root, LocalDiscoveryOptions())

    assert [entry.display_path for entry in entries] == [
        "guide/",
        "index.md",
        "guide/deep/",
        "guide/deep/page.md",
    ]


##############################################################################
def test_flatten_local_paths_respects_discovery_filters(tmp_path: Path) -> None:
    """Flat-list mode should apply the same hidden and exclude filtering rules."""
    root = tmp_path / "docs"
    root.mkdir()
    (root / ".hidden.md").write_text("# Hidden\n", encoding="utf-8")
    (root / "visible.md").write_text("# Visible\n", encoding="utf-8")
    generated = root / "generated"
    generated.mkdir()
    (generated / "skip.md").write_text("# Skip\n", encoding="utf-8")

    entries = flatten_local_paths(
        root,
        LocalDiscoveryOptions(
            show_hidden=False,
            exclude_patterns=("generated/",),
        ),
    )

    assert [entry.display_path for entry in entries] == ["visible.md"]


##############################################################################
def test_flatten_local_paths_skips_empty_directories(tmp_path: Path) -> None:
    """Flat-list mode should hide directories with no visible markdown descendants."""
    root = tmp_path / "docs"
    empty = root / "empty"
    nested = root / "guide" / "deep"
    empty.mkdir(parents=True)
    nested.mkdir(parents=True)
    (nested / "page.md").write_text("# Page\n", encoding="utf-8")

    entries = flatten_local_paths(root, LocalDiscoveryOptions())

    assert [entry.display_path for entry in entries] == [
        "guide/",
        "guide/deep/",
        "guide/deep/page.md",
    ]


##############################################################################
def test_local_browser_mode_from_configuration_rejects_invalid_values() -> None:
    """Invalid browser modes should fail fast."""
    with pytest.raises(ValueError, match="local_browser_view_mode"):
        local_browser_mode_from_configuration("grid")


##############################################################################
def test_local_browser_mode_from_configuration_accepts_flat_list() -> None:
    """Valid configured browser modes should round-trip cleanly."""
    assert (
        local_browser_mode_from_configuration("flat-list") is LocalBrowserMode.FLAT_LIST
    )


### test_local_browser.py ends here
