"""Tests for CLI service helpers."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.cli.services import run_hike, theme_names
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


### test_cli_services.py ends here
