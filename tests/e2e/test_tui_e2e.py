"""End-to-end tests for the Textual TUI."""

##############################################################################
# Python imports.
from __future__ import annotations

from pathlib import Path
from typing import cast

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.data.config import Configuration, save_configuration
from hike.data.layout import LayoutMode
from hike.data.local_browser import LocalBrowserMode
from hike.data.runtime_context import RuntimeContext, resolve_runtime_context
from hike.hike import Hike
from hike.screens.main import Main
from hike.startup import OpenOptions
from hike.widgets import Viewer
from hike.widgets.navigation.local_browser import LocalBrowser
from hike.widgets.navigation.local_flat_view import LocalFlatView


##############################################################################
def _context_for(path: Path, *, cwd: Path | None = None) -> RuntimeContext:
    """Create a runtime context for TUI integration tests."""
    return resolve_runtime_context(
        config_path=path,
        cwd=path.parent if cwd is None else cwd,
    )


##############################################################################
@pytest.mark.anyio
async def test_tui_directory_startup_focuses_visible_local_browser(
    tmp_path: Path,
) -> None:
    """Opening a directory should land focus in the visible local browser."""
    config_path = tmp_path / "config.yaml"
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "README.md").write_text("# Docs\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(Configuration(), context)
    app = Hike(OpenOptions(target=str(docs_root), runtime_context=context))

    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()

        assert app.screen.query_one(LocalFlatView).has_focus


##############################################################################
@pytest.mark.anyio
async def test_tui_file_startup_opens_document_after_first_refresh(
    tmp_path: Path,
) -> None:
    """A file target should open cleanly during startup."""
    config_path = tmp_path / "config.yaml"
    readme = tmp_path / "README.md"
    readme.write_text("# Hello\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(Configuration(), context)
    app = Hike(OpenOptions(target=str(readme), runtime_context=context))

    async with app.run_test(size=(120, 32)) as pilot:
        await pilot.pause()

        viewer = app.screen.query_one(Viewer)

        assert viewer.location == readme
        assert viewer.query_one("#document").has_focus


##############################################################################
@pytest.mark.anyio
async def test_tui_narrow_layout_switches_between_document_and_sidebar(
    tmp_path: Path,
) -> None:
    """Pilot key presses should switch between content and sidebar views."""
    config_path = tmp_path / "config.yaml"
    readme = tmp_path / "README.md"
    readme.write_text("# Hello\n\n## Section\n\nBody.\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(Configuration(), context)
    app = Hike(OpenOptions(target=str(tmp_path), runtime_context=context))

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        screen = cast(Main, app.screen)
        viewer = screen.query_one(Viewer)
        local_browser = screen.query_one(LocalBrowser)
        local_flat_view = screen.query_one(LocalFlatView)

        assert local_flat_view.has_focus
        assert screen._layout_state.mode.value == LayoutMode.SIDEBAR_ONLY.value

        await pilot.press("enter")
        await pilot.pause()

        assert viewer.location == readme
        assert screen._layout_state.mode.value == LayoutMode.CONTENT_ONLY.value
        assert viewer.query_one("#document").has_focus

        await pilot.press("ctrl+n")
        await pilot.pause()

        assert screen._layout_state.mode.value == LayoutMode.SIDEBAR_ONLY.value

        await pilot.press("ctrl+shift+l")
        await pilot.pause()

        assert local_browser.mode is LocalBrowserMode.TREE

        await pilot.press("ctrl+slash")
        await pilot.pause()

        assert screen._layout_state.mode.value == LayoutMode.CONTENT_ONLY.value
        assert viewer.query_one("#document").has_focus


### test_tui_e2e.py ends here
