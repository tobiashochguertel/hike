"""Provides a switchable local browser for tree and flat-list modes."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on
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
    flat-list modes.
    """

    BINDINGS = [
        HelpfulBinding(
            "m",
            "toggle_mode",
            "Mode",
            show=False,
            tooltip="Toggle the local browser between tree and flat-list modes",
        ),
    ]

    mode: var[LocalBrowserMode] = var(LocalBrowserMode.FLAT_LIST)
    """The active local browser mode."""

    @dataclass
    class LayoutHintChanged(Message):
        """Message sent when the browser width hint may have changed."""

        local_browser: LocalBrowser
        """The local browser widget sending the message."""

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
        self._initial_mode = mode or local_browser_mode_from_configuration(
            LocalBrowserMode.FLAT_LIST.value
        )
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.mode = self._initial_mode

    def compose(self) -> ComposeResult:
        """Compose the local browser widgets."""
        yield LocalView(self._root, options=self._options)
        yield LocalFlatView(self._root, options=self._options)

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

    def set_root(self, root: Path) -> None:
        """Set the local browser root for both modes."""
        self._root = root.expanduser().resolve()
        self.query_one(LocalView).set_root(self._root)
        self.query_one(LocalFlatView).set_root(self._root)
        self._request_layout_hint_refresh()

    def configure(self, options: LocalDiscoveryOptions) -> None:
        """Update the discovery options used by both modes."""
        self._options = options
        self.query_one(LocalView).configure(options)
        self.query_one(LocalFlatView).configure(options)
        self._request_layout_hint_refresh()

    def reload(self) -> None:
        """Reload both local browser modes."""
        self.query_one(LocalView).reload()
        self.query_one(LocalFlatView).reload()
        self._request_layout_hint_refresh()

    def highlight_path(self, path: Path) -> None:
        """Highlight a local path in both browser modes."""
        resolved = path.expanduser().resolve()
        self.query_one(LocalView).highlight_path(resolved)
        self.query_one(LocalFlatView).highlight_path(resolved)
        self._request_layout_hint_refresh()

    def set_mode(self, mode: LocalBrowserMode, *, persist: bool = True) -> None:
        """Set the active local browser mode."""
        self.mode = mode
        if persist:
            with update_app_configuration(self) as config:
                config.local_browser_view_mode = mode.value

    def action_toggle_mode(self) -> None:
        """Toggle the local browser mode."""
        self.toggle_mode()

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
