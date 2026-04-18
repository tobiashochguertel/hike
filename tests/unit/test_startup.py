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
from hike.data.config import Configuration
from hike.data.discovery import local_discovery_options
from hike.data.runtime_context import resolve_runtime_context
from hike.screens.main import Main
from hike.startup import (
    OpenOptions,
    StartupTargetKind,
    classify_startup_target,
    resolve_startup_plan,
)


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
def test_classify_startup_target_handles_relative_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Relative file targets should resolve from cwd."""
    target = tmp_path / "README.md"
    target.write_text("# Hello\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    startup = classify_startup_target("README.md")

    assert startup.kind is StartupTargetKind.FILE
    assert startup.value == target.resolve()


##############################################################################
def test_classify_startup_target_handles_relative_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Relative directory targets should resolve from cwd."""
    target = tmp_path / "docs"
    target.mkdir()
    monkeypatch.chdir(tmp_path)

    startup = classify_startup_target("docs")

    assert startup.kind is StartupTargetKind.DIRECTORY
    assert startup.value == target.resolve()


##############################################################################
def test_main_uses_file_parent_as_initial_local_root(tmp_path: Path) -> None:
    """A file startup target should keep the browser rooted beside that file."""
    target = tmp_path / "docs" / "README.md"
    target.parent.mkdir()
    target.write_text("# Hello\n", encoding="utf-8")

    screen = Main(OpenOptions(target=str(target)), configuration=Configuration())

    assert screen._startup_plan.local_root == target.parent.resolve()


##############################################################################
def test_resolve_startup_plan_uses_cwd_for_open_without_target(tmp_path: Path) -> None:
    """`hike open` should defer startup file selection to the shared index."""
    options = OpenOptions(runtime_context=resolve_runtime_context(cwd=tmp_path))
    configuration = Configuration()

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.local_root == tmp_path.resolve()
    assert plan.resolve_from_index is True
    assert plan.open_target is None
    assert plan.selected_path is None


##############################################################################
def test_resolve_startup_plan_prefers_index_before_readme(tmp_path: Path) -> None:
    """Startup auto-open should defer filename priority to the shared index."""
    options = OpenOptions(runtime_context=resolve_runtime_context(cwd=tmp_path))
    configuration = Configuration()

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.resolve_from_index is True
    assert plan.open_target is None
    assert plan.selected_path is None


##############################################################################
def test_resolve_startup_plan_uses_first_visible_file_when_no_pattern_matches(
    tmp_path: Path,
) -> None:
    """No-match fallback should now be resolved from the shared index."""
    options = OpenOptions(runtime_context=resolve_runtime_context(cwd=tmp_path))
    configuration = Configuration(startup_auto_open_patterns=["welcome*.md"])

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.resolve_from_index is True
    assert plan.open_target is None
    assert plan.selected_path is None


##############################################################################
def test_resolve_startup_plan_respects_custom_priority_patterns(tmp_path: Path) -> None:
    """Pattern priority should be resolved later from the shared index."""
    options = OpenOptions(runtime_context=resolve_runtime_context(cwd=tmp_path))
    configuration = Configuration(
        startup_auto_open_patterns=["welcome*.md", "README.md"]
    )

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.resolve_from_index is True
    assert plan.open_target is None


##############################################################################
def test_resolve_startup_plan_can_disable_auto_open(tmp_path: Path) -> None:
    """Startup auto-open can be turned off in configuration."""
    readme = tmp_path / "README.md"
    readme.write_text("# Hello\n", encoding="utf-8")
    options = OpenOptions(runtime_context=resolve_runtime_context(cwd=tmp_path))
    configuration = Configuration(startup_auto_open=False)

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.local_root == tmp_path.resolve()
    assert plan.open_target is None
    assert plan.focus_local_browser is True


##############################################################################
def test_resolve_startup_plan_preserves_commands(tmp_path: Path) -> None:
    """Startup commands should bypass auto-open location resolution."""
    options = OpenOptions(
        command=("gh", "davep/hike"),
        runtime_context=resolve_runtime_context(cwd=tmp_path),
    )
    configuration = Configuration()

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.command_input == "gh davep/hike"
    assert plan.open_target is None


##############################################################################
def test_resolve_startup_plan_preserves_url_targets(tmp_path: Path) -> None:
    """URL startup targets should still open directly without sidebar selection."""
    options = OpenOptions(
        target="https://example.com/README.md",
        runtime_context=resolve_runtime_context(cwd=tmp_path),
    )
    configuration = Configuration()

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert str(plan.open_target) == "https://example.com/README.md"
    assert plan.selected_path is None


##############################################################################
def test_resolve_startup_plan_honors_explicit_root_override(tmp_path: Path) -> None:
    """An explicit root should drive deferred startup selection."""
    docs = tmp_path / "docs"
    docs.mkdir()
    options = OpenOptions(
        root=str(docs),
        runtime_context=resolve_runtime_context(cwd=tmp_path),
    )
    configuration = Configuration()

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert plan.local_root == docs.resolve()
    assert plan.resolve_from_index is True
    assert plan.open_target is None


##############################################################################
def test_resolve_startup_plan_marks_missing_target_as_error(tmp_path: Path) -> None:
    """Missing paths should surface a startup error."""
    missing = tmp_path / "missing.md"
    options = OpenOptions(
        target=str(missing),
        runtime_context=resolve_runtime_context(cwd=tmp_path),
    )
    configuration = Configuration()

    plan = resolve_startup_plan(
        options,
        configuration,
        local_discovery_options(options, configuration),
    )

    assert "Could not locate" in (plan.error_message or "")


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
