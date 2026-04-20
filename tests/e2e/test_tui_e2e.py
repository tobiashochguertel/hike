"""End-to-end tests for the Textual TUI."""

##############################################################################
# Python imports.
from __future__ import annotations

import time
from pathlib import Path
from threading import Event
from typing import cast

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from hike.data.config import Configuration, save_configuration
from hike.data.layout import LayoutMode
from hike.data.local_browser import LocalBrowserMode
from hike.data.local_index import LocalIndexBuildRequest, LocalIndexService
from hike.data.runtime_context import RuntimeContext, resolve_runtime_context
from hike.hike import Hike
from hike.screens.main import Main
from hike.startup import OpenOptions
from hike.widgets import Viewer
from hike.widgets.navigation.local_browser import LocalBrowser
from hike.widgets.navigation.local_flat_view import LocalFlatView
from hike.widgets.navigation.local_view import LocalView


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
    """Opening a directory should auto-open and select the preferred file."""
    config_path = tmp_path / "config.yaml"
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    readme = docs_root / "README.md"
    readme.write_text("# Docs\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(Configuration(), context)
    app = Hike(OpenOptions(target=str(docs_root), runtime_context=context))

    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        await pilot.pause()

        viewer = app.screen.query_one(Viewer)
        local_flat_view = app.screen.query_one(LocalFlatView)

        assert viewer.location == readme
        assert local_flat_view.highlighted == local_flat_view.get_option_index(
            str(readme)
        )


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
        local_flat_view = app.screen.query_one(LocalFlatView)

        assert viewer.location == readme
        assert viewer.query_one("#document").has_focus
        assert local_flat_view.highlighted == local_flat_view.get_option_index(
            str(readme)
        )


##############################################################################
@pytest.mark.anyio
async def test_tui_open_without_target_uses_cwd_and_auto_opens_default_file(
    tmp_path: Path,
) -> None:
    """`hike open` without a target should use cwd and auto-open a default file."""
    config_path = tmp_path / "config.yaml"
    readme = tmp_path / "README.md"
    readme.write_text("# Home\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(Configuration(), context)
    app = Hike(OpenOptions(runtime_context=context))

    async with app.run_test(size=(120, 32)) as pilot:
        await pilot.pause()
        await pilot.pause()

        viewer = app.screen.query_one(Viewer)
        local_flat_view = app.screen.query_one(LocalFlatView)

        assert viewer.location == readme
        assert local_flat_view.highlighted == local_flat_view.get_option_index(
            str(readme)
        )


##############################################################################
@pytest.mark.anyio
async def test_tui_startup_prefers_index_before_readme(
    tmp_path: Path,
) -> None:
    """Startup auto-open should prefer INDEX.md before README.md."""
    config_path = tmp_path / "config.yaml"
    index = tmp_path / "INDEX.md"
    readme = tmp_path / "README.md"
    index.write_text("# Index\n", encoding="utf-8")
    readme.write_text("# Readme\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(Configuration(), context)
    app = Hike(OpenOptions(runtime_context=context))

    async with app.run_test(size=(120, 32)) as pilot:
        await pilot.pause()
        await pilot.pause()

        viewer = app.screen.query_one(Viewer)
        local_flat_view = app.screen.query_one(LocalFlatView)

        assert viewer.location == index
        assert local_flat_view.highlighted == local_flat_view.get_option_index(
            str(index)
        )


##############################################################################
@pytest.mark.anyio
async def test_tui_tree_mode_startup_highlights_selected_file(
    tmp_path: Path,
) -> None:
    """Tree mode should also highlight the startup file in the sidebar."""
    config_path = tmp_path / "config.yaml"
    readme = tmp_path / "README.md"
    readme.write_text("# Home\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(
        Configuration(local_browser_view_mode=LocalBrowserMode.TREE.value),
        context,
    )
    app = Hike(OpenOptions(runtime_context=context))

    async with app.run_test(size=(120, 32)) as pilot:
        await pilot.pause()
        await pilot.pause()

        local_browser = app.screen.query_one(LocalBrowser)
        local_view = app.screen.query_one(LocalView)

        assert local_browser.mode is LocalBrowserMode.TREE
        assert local_view.cursor_node is not None
        assert local_view.cursor_node.data is not None
        assert local_view.cursor_node.data.path.resolve() == readme.resolve()


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
    save_configuration(Configuration(startup_auto_open=False), context)
    app = Hike(OpenOptions(target=str(tmp_path), runtime_context=context))

    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        screen = cast(Main, app.screen)
        viewer = screen.query_one(Viewer)
        local_browser = screen.query_one(LocalBrowser)
        local_flat_view = screen.query_one(LocalFlatView)

        assert local_flat_view.has_focus
        assert screen._layout_state.mode.value == LayoutMode.SIDEBAR_ONLY.value

        local_flat_view.highlighted = local_flat_view.get_option_index(str(readme))
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


##############################################################################
@pytest.mark.anyio
async def test_tui_flat_list_shows_loading_placeholder_during_slow_scan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Slow flat-list scans should no longer block the first rendered frame."""
    config_path = tmp_path / "config.yaml"
    readme = tmp_path / "README.md"
    readme.write_text("# Hello\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(
        Configuration(
            local_browser_view_mode=LocalBrowserMode.FLAT_LIST.value,
            startup_auto_open=False,
        ),
        context,
    )

    original_build_snapshot = LocalIndexService.build_snapshot

    def slow_build_snapshot(
        self: LocalIndexService,
        request: LocalIndexBuildRequest | None = None,
    ) -> object:
        time.sleep(0.5)
        return original_build_snapshot(self, request)

    monkeypatch.setattr(
        LocalIndexService,
        "build_snapshot",
        slow_build_snapshot,
    )
    app = Hike(OpenOptions(target=str(readme), runtime_context=context))

    async with app.run_test(size=(120, 32)) as pilot:
        await pilot.pause()

        viewer = app.screen.query_one(Viewer)
        local_flat_view = app.screen.query_one(LocalFlatView)
        prompts = [
            str(local_flat_view.get_option_at_index(index).prompt)
            for index in range(local_flat_view.option_count)
        ]

        assert viewer.location == readme
        assert local_flat_view.option_count >= 1
        assert any(prompt.strip() for prompt in prompts)


##############################################################################
@pytest.mark.anyio
async def test_tui_quit_cancels_inflight_local_index_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Quitting should cancel a slow local-index build instead of waiting for it."""
    config_path = tmp_path / "config.yaml"
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "README.md").write_text("# Hello\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(
        Configuration(
            local_browser_view_mode=LocalBrowserMode.FLAT_LIST.value,
            startup_auto_open=False,
        ),
        context,
    )

    started = Event()
    cancelled = Event()

    def slow_build_snapshot(
        self: LocalIndexService,
        request: LocalIndexBuildRequest | None = None,
    ) -> object:
        started.set()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if request is not None and request.cancel_event.is_set():
                cancelled.set()
                return None
            time.sleep(0.01)
        return self.loading_snapshot()

    monkeypatch.setattr(
        LocalIndexService,
        "build_snapshot",
        slow_build_snapshot,
    )
    app = Hike(OpenOptions(target=str(docs_root), runtime_context=context))

    exit_started = 0.0
    async with app.run_test(size=(120, 32)) as pilot:
        for _ in range(20):
            if started.is_set():
                break
            await pilot.pause()
        assert started.is_set()

        exit_started = time.monotonic()
        await pilot.press("ctrl+q")

    assert cancelled.is_set()
    assert time.monotonic() - exit_started < 1


##############################################################################
@pytest.mark.anyio
async def test_tui_flat_list_can_return_to_parent_directory(
    tmp_path: Path,
) -> None:
    """Flat-list local navigation should support moving back to the parent root."""
    config_path = tmp_path / "config.yaml"
    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "README.md").write_text("# Docs\n", encoding="utf-8")
    context = _context_for(config_path, cwd=tmp_path)
    save_configuration(
        Configuration(
            local_browser_view_mode=LocalBrowserMode.FLAT_LIST.value,
            startup_auto_open=False,
        ),
        context,
    )
    app = Hike(OpenOptions(target=str(tmp_path), runtime_context=context))

    async with app.run_test(size=(120, 32)) as pilot:
        await pilot.pause()
        await pilot.pause()

        local_browser = app.screen.query_one(LocalBrowser)
        local_flat_view = app.screen.query_one(LocalFlatView)

        assert local_browser.root == tmp_path.resolve()

        local_flat_view.highlighted = local_flat_view.get_option_index(str(docs_root))
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()

        assert local_browser.root == docs_root.resolve()
        assert "../" in str(local_flat_view.get_option_at_index(0).prompt)

        await pilot.press("backspace")
        await pilot.pause()
        await pilot.pause()

        assert local_browser.root == tmp_path.resolve()


### test_tui_e2e.py ends here
