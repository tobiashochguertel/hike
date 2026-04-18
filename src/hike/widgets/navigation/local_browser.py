"""Provides a switchable local browser for tree and flat-list modes."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
import asyncio
from dataclasses import dataclass
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import var

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding

##############################################################################
# Local imports.
from ...data.discovery import LocalDiscoveryOptions
from ...data.local_browser import (
    LocalBrowserMode,
    local_browser_mode_from_configuration,
)
from ...data.local_index import (
    LocalIndexBuildRequest,
    LocalIndexService,
    LocalIndexSnapshot,
    LocalIndexStatus,
    preferred_startup_path,
)
from ...runtime.config_access import update_app_configuration
from .local_flat_view import LocalFlatView
from .local_view import LocalView


##############################################################################
class LocalBrowser(Vertical):
    """A switchable local browser for tree and flat-list modes."""

    DEFAULT_CSS = """
    LocalBrowser {
        height: 1fr;

        LocalView, LocalFlatView {
            display: none;
        }

        &.--tree LocalView {
            display: block;
        }

        &.--flat-list LocalFlatView {
            display: block;
        }
    }
    """

    HELP = """
    ## Local Browser

    Press `m` while focused on the local browser to toggle between the tree and
    flat-list modes. Press `Backspace` to move the local browser root to the
    parent directory.
    """

    BINDINGS = [
        HelpfulBinding(
            "m",
            "toggle_mode",
            "Mode",
            show=False,
            tooltip="Toggle the local browser between tree and flat-list modes",
        ),
        HelpfulBinding(
            "backspace",
            "go_parent",
            "Parent",
            show=False,
            tooltip="Change the local browser root to the parent directory",
        ),
    ]

    mode: var[LocalBrowserMode] = var(LocalBrowserMode.FLAT_LIST)
    """The active local browser mode."""

    @dataclass
    class LayoutHintChanged(Message):
        """Message sent when the browser width hint may have changed."""

        local_browser: LocalBrowser
        """The local browser widget sending the message."""

    @dataclass
    class SnapshotUpdated(Message):
        """Message sent when the shared local index changes state."""

        local_browser: LocalBrowser
        """The local browser widget sending the message."""
        snapshot: LocalIndexSnapshot
        """The latest shared local-index snapshot."""

    def __init__(
        self,
        path: Path,
        *,
        options: LocalDiscoveryOptions | None = None,
        mode: LocalBrowserMode | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the local browser."""
        self._root = path.expanduser().resolve()
        self._options = options or LocalDiscoveryOptions()
        self._index = LocalIndexService(self._root, self._options)
        self._snapshot = self._index.loading_snapshot()
        self._initial_mode = mode or local_browser_mode_from_configuration(
            LocalBrowserMode.FLAT_LIST.value
        )
        self._reload_generation = 0
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.mode = self._initial_mode

    @property
    def root(self) -> Path:
        """Return the current local browser root."""
        return self._root

    def compose(self) -> ComposeResult:
        """Compose the local browser widgets."""
        yield LocalView(self._root)
        yield LocalFlatView(self._root)

    def on_mount(self) -> None:
        """Start the shared local-index load after the browser mounts."""
        self.reload()

    def on_unmount(self) -> None:
        """Cancel any in-flight local-index build during shutdown/teardown."""
        self.cancel_pending_work()

    def cancel_pending_work(self) -> None:
        """Cancel any in-flight local-index build owned by this browser."""
        self._reload_generation += 1
        self._index.cancel()
        self.workers.cancel_group(self, "local-browser-index")

    def _watch_mode(self) -> None:
        """React to changes in the active local browser mode."""
        self.set_class(self.mode is LocalBrowserMode.TREE, "--tree")
        self.set_class(self.mode is LocalBrowserMode.FLAT_LIST, "--flat-list")
        self._request_layout_hint_refresh()

    def _request_layout_hint_refresh(self) -> None:
        """Request a refresh of the sidebar width hint."""
        self.call_after_refresh(self.post_message, self.LayoutHintChanged(self))

    def content_width_hint(self) -> int | None:
        """Return the preferred width of the active browser mode."""
        if self.mode is LocalBrowserMode.TREE:
            return self.query_one(LocalView).content_width_hint()
        return self.query_one(LocalFlatView).content_width_hint()

    def _apply_snapshot(self, snapshot: LocalIndexSnapshot) -> None:
        """Apply one shared local-index snapshot to both sidebar views."""
        self._snapshot = snapshot
        self.query_one(LocalView).set_snapshot(snapshot)
        self.query_one(LocalFlatView).set_snapshot(snapshot)
        self.post_message(self.SnapshotUpdated(self, snapshot))
        self._request_layout_hint_refresh()

    @work(exclusive=True, group="local-browser-index")
    async def _reload_index(
        self,
        generation: int,
        request: LocalIndexBuildRequest,
    ) -> None:
        """Build the shared local index off the UI thread and apply it."""
        snapshot = await asyncio.to_thread(self._index.build_snapshot, request)
        if (
            snapshot is None
            or request.cancel_event.is_set()
            or generation != self._reload_generation
            or not self.is_mounted
        ):
            return
        self._apply_snapshot(snapshot)

    def set_root(self, root: Path) -> None:
        """Set the local browser root for both modes."""
        self._root = root.expanduser().resolve()
        self._index.set_root(self._root)
        self.query_one(LocalView).set_root(self._root)
        self.query_one(LocalFlatView).set_root(self._root)
        if self.is_mounted:
            self.reload()

    def configure(self, options: LocalDiscoveryOptions) -> None:
        """Update the discovery options used by both modes."""
        self._options = options
        self._index.configure(options)
        if self.is_mounted:
            self.reload()

    def reload(self) -> None:
        """Reload the shared index and fan it out to both local browser modes."""
        self._reload_generation += 1
        self.workers.cancel_group(self, "local-browser-index")
        request = self._index.begin_build()
        self._apply_snapshot(self._index.loading_snapshot(request.root))
        self._reload_index(self._reload_generation, request)

    def highlight_path(self, path: Path) -> None:
        """Highlight a local path in both browser modes."""
        resolved = path.expanduser().resolve()
        self.query_one(LocalView).highlight_path(resolved)
        self.query_one(LocalFlatView).highlight_path(resolved)
        self._request_layout_hint_refresh()

    def index_loading(self) -> bool:
        """Return `True` while the shared local index is still loading."""
        return self._snapshot.status is LocalIndexStatus.LOADING

    def preferred_startup_path(self, patterns: tuple[str, ...]) -> Path | None:
        """Select the preferred startup path from the shared local index."""
        if self.index_loading():
            return None
        return preferred_startup_path(self._snapshot, patterns)

    def go_parent(self) -> Path | None:
        """Change the local browser root to its parent directory."""
        parent = self._root.parent
        if parent == self._root:
            return None
        self.set_root(parent)
        return parent

    def set_mode(self, mode: LocalBrowserMode, *, persist: bool = True) -> None:
        """Set the active local browser mode."""
        self.mode = mode
        if persist:
            with update_app_configuration(self) as config:
                config.local_browser_view_mode = mode.value

    def action_toggle_mode(self) -> None:
        """Toggle the local browser mode."""
        self.toggle_mode()

    def action_go_parent(self) -> None:
        """Change the local browser root to its parent directory."""
        self.go_parent()

    def toggle_mode(self, *, persist: bool = True) -> LocalBrowserMode:
        """Toggle the local browser mode and return the new mode."""
        mode = (
            LocalBrowserMode.FLAT_LIST
            if self.mode is LocalBrowserMode.TREE
            else LocalBrowserMode.TREE
        )
        self.set_mode(mode, persist=persist)
        return mode

    @on(LocalView.LayoutHintChanged)
    @on(LocalFlatView.LayoutHintChanged)
    def _browser_content_changed(self, _: Message) -> None:
        """Refresh the sidebar width hint when browser content changes."""
        self._request_layout_hint_refresh()


### local_browser.py ends here
