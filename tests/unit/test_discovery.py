"""Tests for local browser discovery options."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from hike.data.discovery import (
    LocalDiscoveryOptions,
    should_include_path,
)


##############################################################################
def test_hidden_files_can_be_shown(tmp_path: Path) -> None:
    """The hidden-file toggle should control dotfile visibility."""
    hidden = tmp_path / ".hidden.md"
    hidden.write_text("# Hidden\n", encoding="utf-8")

    assert not should_include_path(
        hidden, root=tmp_path, options=LocalDiscoveryOptions(show_hidden=False)
    )
    assert should_include_path(
        hidden, root=tmp_path, options=LocalDiscoveryOptions(show_hidden=True)
    )


##############################################################################
def test_ignore_files_can_be_disabled(tmp_path: Path) -> None:
    """Ignore support should be toggleable from the CLI."""
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    ignored = tmp_path / "node_modules"
    ignored.mkdir()

    assert not should_include_path(
        ignored,
        root=tmp_path,
        options=LocalDiscoveryOptions(use_ignore_files=True),
    )
    assert should_include_path(
        ignored,
        root=tmp_path,
        options=LocalDiscoveryOptions(use_ignore_files=False),
    )


##############################################################################
def test_exclude_patterns_hide_matching_paths(tmp_path: Path) -> None:
    """Ad-hoc exclude globs should hide matching paths."""
    excluded = tmp_path / "generated"
    excluded.mkdir()

    assert not should_include_path(
        excluded,
        root=tmp_path,
        options=LocalDiscoveryOptions(exclude_patterns=("generated/",)),
    )


##############################################################################
def test_non_matching_markdown_files_remain_visible(tmp_path: Path) -> None:
    """Normal Markdown files should remain visible."""
    markdown = tmp_path / "README.md"
    markdown.write_text("# Visible\n", encoding="utf-8")

    assert should_include_path(
        markdown,
        root=tmp_path,
        options=LocalDiscoveryOptions(exclude_patterns=("generated/",)),
    )


### test_discovery.py ends here
