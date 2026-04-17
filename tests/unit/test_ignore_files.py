"""Tests for ignore file handling."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from hike.data.ignore_files import is_ignored


##############################################################################
def test_gitignore_hides_directory(tmp_path: Path) -> None:
    """A root .gitignore should hide ignored directories."""
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    ignored = tmp_path / "node_modules"
    ignored.mkdir()

    assert is_ignored(ignored, root=tmp_path)


##############################################################################
def test_gitignore_hides_files_within_ignored_directory(tmp_path: Path) -> None:
    """Files inside an ignored directory should also be hidden."""
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    ignored = tmp_path / "node_modules"
    ignored.mkdir()
    package = ignored / "package.json"
    package.write_text("{}", encoding="utf-8")

    assert is_ignored(package, root=tmp_path)


##############################################################################
def test_ignore_file_hides_matching_markdown_file(tmp_path: Path) -> None:
    """A plain .ignore file should be respected too."""
    (tmp_path / ".ignore").write_text("drafts/\n", encoding="utf-8")
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    markdown = drafts / "README.md"
    markdown.write_text("# Draft\n", encoding="utf-8")

    assert is_ignored(markdown, root=tmp_path)


##############################################################################
def test_ancestor_gitignore_applies_to_nested_browser_root(tmp_path: Path) -> None:
    """Opening a nested docs directory should still use project-level ignores."""
    project = tmp_path / "project"
    docs = project / "docs"
    generated = docs / "generated"
    project.mkdir()
    docs.mkdir()
    generated.mkdir()
    (project / ".gitignore").write_text("docs/generated/\n", encoding="utf-8")

    assert is_ignored(generated, root=docs)


##############################################################################
def test_paths_not_matched_by_ignore_files_remain_visible(tmp_path: Path) -> None:
    """Normal Markdown files should remain visible."""
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    markdown = tmp_path / "README.md"
    markdown.write_text("# Visible\n", encoding="utf-8")

    assert not is_ignored(markdown, root=tmp_path)


### test_ignore_files.py ends here
