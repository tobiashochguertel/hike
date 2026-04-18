"""Tests for CLI service helpers."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.build_info import BuildInfo
from hike.cli.services import (
    binding_summaries,
    keybinding_set_summaries,
    run_hike,
    theme_names,
    version_text,
)
from hike.data.config import Configuration
from hike.startup import OpenOptions


##############################################################################
def test_theme_names_use_static_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Theme listings should come from the static theme catalog."""
    monkeypatch.setattr(
        "hike.theme_catalog.BUILTIN_THEMES",
        {
            "zebra": object(),
            "textual-ansi": object(),
            "alpha": object(),
        },
    )

    assert theme_names() == ["alpha", "zebra"]


##############################################################################
def test_run_hike_delegates_to_runtime_bootstrap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TUI launches should cross the dedicated runtime bootstrap seam."""
    captured: dict[str, OpenOptions] = {}

    monkeypatch.setattr(
        "hike.runtime.bootstrap.launch_hike",
        lambda options: captured.setdefault("options", options),
    )

    run_hike(OpenOptions(target="docs"))

    assert captured["options"] == OpenOptions(target="docs")


##############################################################################
def test_version_text_includes_build_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Version output should include build metadata when available."""
    monkeypatch.setattr(
        "hike.cli.services.APP_BUILD_INFO",
        BuildInfo(
            version="1.5.0",
            git_sha="abc123",
            git_branch="feature/all-requested-features",
            build_timestamp="2026-04-18T08:30:00+02:00",
        ),
    )
    monkeypatch.setattr("hike.cli.services.APP_VERSION", "1.5.0")

    assert version_text() == "\n".join(
        [
            "hike v1.5.0",
            "commit: abc123",
            "branch: feature/all-requested-features",
            "built: 2026-04-18T08:30:00+02:00",
        ]
    )


##############################################################################
def test_binding_services_reflect_selected_keybinding_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Binding summaries should reflect the active preset and custom sets."""
    monkeypatch.setattr(
        "hike.cli.services.load_configuration",
        lambda _context=None: Configuration(
            binding_set="mnemonic",
            binding_sets={"project": {"Quit": "ctrl+x"}},
            bindings={"JumpToBookmarks": "shift+f6"},
        ),
    )

    summaries = {
        summary.command_name: summary.current_key for summary in binding_summaries()
    }
    sets = {summary.name: summary for summary in keybinding_set_summaries()}

    assert summaries["ToggleNavigation"] == "ctrl+shift+n"
    assert summaries["Quit"] == "ctrl+q"
    assert summaries["JumpToBookmarks"] == "shift+f6"
    assert sets["default"].source == "built-in"
    assert sets["mnemonic"].active is True
    assert sets["project"].source == "custom"


### test_cli_services.py ends here
