"""Provides the navigation panel widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from pathlib import Path
from typing import Any

##############################################################################
# Rich imports.
from rich.cells import cell_len

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import var
from textual.widgets import Markdown, TabbedContent, TabPane, Tabs, Tree
from textual.widgets._tree import TreeNode
from textual.widgets.markdown import MarkdownTableOfContents, TableOfContentsType

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding

##############################################################################
# Local imports.
from ...commands import JumpToCommandLine
from ...data import Bookmark, Bookmarks, load_configuration
from ...data.discovery import LocalDiscoveryOptions
from ...data.layout import LayoutState
from ...data.local_browser import (
    LocalBrowserMode,
    local_browser_mode_from_configuration,
)
from ...types import HikeHistory, HikeLocation
from .bookmarks_view import BookmarksView
from .history_view import HistoryView
from .local_browser import LocalBrowser


##############################################################################
def _tree_node_depth(node: TreeNode[Any]) -> int:
    """Return the depth of a tree node within its tree."""
    depth = 0
    current = node.parent
    while current is not None:
        depth += 1
        current = current.parent
    return depth


##############################################################################
def _visible_tree_width(node: TreeNode[Any]) -> int:
    """Measure the visible width of a tree node and any expanded children."""
    label = node.label if isinstance(node.label, str) else node.label.plain
    width = cell_len(label) + 4 + (_tree_node_depth(node) * 2)
    if node.is_expanded:
        for child in node.children:
            width = max(width, _visible_tree_width(child))
    return width


##############################################################################
class Navigation(Vertical):
    """The navigation panel."""

    DEFAULT_CSS = """
    Navigation {
        width: 22%;
        min-width: 24;
        dock: left;
        background: transparent;

        &.--dock-right {
            dock: right;
        }

        #tabs-list {
            background: $panel;
        }

        /* https://github.com/Textualize/textual/issues/5488 */
        MarkdownTableOfContents, &:focus-within MarkdownTableOfContents {
            background: transparent;
            width: 1fr;
            Tree {
                background: transparent;
            }
        }

        /* https://github.com/Textualize/textual/issues/5488 */
        HistoryView, &:focus-within HistoryView,
        LocalBrowser, &:focus-within LocalBrowser,
        BookmarksView, &:focus-within BookmarksView {
            background: transparent;
        }
    }
    """

    BINDINGS = [
        ("escape", "return_to_tabs_or_bounce_out"),
        ("down", "move_into_panel"),
        HelpfulBinding(
            "ctrl+left",
            "switch('previous_tab')",
            tooltip="Move to the previous navigation tab",
        ),
        HelpfulBinding(
            "ctrl+right",
            "switch('next_tab')",
            tooltip="Move to the next navigation tab",
        ),
        ("h", "tab_left"),
        ("j", "also_down"),
        ("k", "also_up"),
        ("l", "tab_right"),
    ]

    HELP = """
    ## The Navigation Panel

    Here you'll find panels for the current document's table of contents; a
    local file browser (use the `chdir` command in the command line at the
    bottom of the screen to change the root directory); a simple bookmark
    manager and your browsing history.

    ### Useful keys
    """

    dock_right: var[bool] = var(False)
    """Should the navigation dock to the right?"""

    table_of_contents: var[TableOfContentsType | None] = var(None)
    """The currently-displayed table of contents."""

    bookmarks: var[Bookmarks] = var(Bookmarks)
    """The bookmarks."""

    def __init__(
        self,
        *,
        local_root: Path | None = None,
        local_options: LocalDiscoveryOptions | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the navigation panel."""
        self._local_root = (
            Path(load_configuration().local_start_location).expanduser().resolve()
            if local_root is None
            else local_root.expanduser().resolve()
        )
        self._local_options = local_options or LocalDiscoveryOptions()
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def action_return_to_tabs_or_bounce_out(self) -> None:
        """Return focus to the tabs, or to the input."""
        if self.screen.focused == (tabs := self.query_one(Tabs)):
            self.post_message(JumpToCommandLine())
        else:
            tabs.focus()

    def action_move_into_panel(self) -> None:
        """Drop focus down into a panel."""
        if (active := self.query_one(TabbedContent).active_pane) is not None:
            for widget in active.query("*"):
                if widget.can_focus:
                    widget.focus()
                    return

    async def action_switch(self, switcher: str) -> None:
        await self.query_one(Tabs).run_action(switcher)
        self.call_after_refresh(self.run_action, "move_into_panel")

    def _watch_dock_right(self) -> None:
        """React to the dock toggle being changed."""
        self.set_class(self.dock_right, "--dock-right")

    def apply_layout_state(self, layout_state: LayoutState) -> None:
        """Apply the computed layout state to the navigation panel."""
        self.dock_right = layout_state.navigation_dock_right
        self.styles.width = layout_state.sidebar_width

    @dataclass
    class LayoutHintChanged(Message):
        """Message sent when the sidebar width hint may have changed."""

        navigation: Navigation
        """The navigation widget sending the message."""

    def _request_layout_hint_refresh(self) -> None:
        """Request the screen to refresh the computed sidebar width."""
        self.call_after_refresh(self.post_message, self.LayoutHintChanged(self))

    def content_width_hint(self) -> int | None:
        """Return the preferred width of the active navigation pane."""
        if (active := self.query_one(TabbedContent).active_pane) is None:
            return None
        match active.id:
            case "content":
                return _visible_tree_width(
                    self.query_one("MarkdownTableOfContents Tree", Tree).root
                )
            case "local":
                return self.query_one(LocalBrowser).content_width_hint()
            case "bookmarks":
                return self.query_one(BookmarksView).content_width_hint()
            case "history":
                return self.query_one(HistoryView).content_width_hint()
        return None

    def _maybe_enable_tab(self, tab: str, data: object) -> bool:
        """Enable/disable a tab based on there being data.

        Args:
            tab: The name of the tab.
            data: The data to test.

        Returns:
            `True` if the tab was enabled, `False` if disabled.
        """
        tabs = self.query_one(TabbedContent)
        if data:
            tabs.enable_tab(tab)
            return True
        tabs.disable_tab(tab)
        if tabs.active == tab:
            tabs.active = "local"
        return False

    def _watch_table_of_contents(self) -> None:
        """React to the table of content being updated."""
        self.query_one(
            MarkdownTableOfContents
        ).table_of_contents = self.table_of_contents
        if self._maybe_enable_tab("content", self.table_of_contents):
            self.query_one("MarkdownTableOfContents Tree", Tree).cursor_line = 0
        self._request_layout_hint_refresh()

    def _watch_bookmarks(self) -> None:
        """React to the bookmarks being changed."""
        self.query_one(BookmarksView).update(self.bookmarks)
        self._maybe_enable_tab("bookmarks", self.bookmarks)
        self._request_layout_hint_refresh()

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        with TabbedContent():
            with TabPane("Content", id="content"):
                yield MarkdownTableOfContents(Markdown())
            with TabPane("Local", id="local"):
                yield LocalBrowser(
                    self._local_root,
                    options=self._local_options,
                    mode=local_browser_mode_from_configuration(
                        load_configuration().local_browser_view_mode
                    ),
                )
            with TabPane("Bookmarks", id="bookmarks"):
                yield BookmarksView()
            with TabPane("History", id="history"):
                yield HistoryView()

    def update_history(self, history: HikeHistory) -> None:
        """Update the history display.

        Args:
            history: The history to display.
        """
        self.query_one(HistoryView).update(history)
        self._maybe_enable_tab("history", history)
        self._request_layout_hint_refresh()

    def highlight_history(self, history: int) -> None:
        """Highlight a specific entry in history.

        Args:
            The ID of the item of history to highlight.
        """
        self.query_one(HistoryView).highlight_location(history)

    def set_local_view_root(self, root: Path) -> None:
        """Set the root directory for the local file browser.

        Args:
            root: The new root directory.
        """
        self.query_one(LocalBrowser).set_root(root)
        self._request_layout_hint_refresh()

    def configure_local_view(self, options: LocalDiscoveryOptions) -> None:
        """Update the local browser's discovery options."""
        self._local_options = options
        self.query_one(LocalBrowser).configure(options)
        self._request_layout_hint_refresh()

    def refresh_local_view(self) -> None:
        """Refresh the local view."""
        self.query_one(LocalBrowser).reload()
        self._request_layout_hint_refresh()

    def toggle_local_browser_mode(self) -> LocalBrowserMode:
        """Toggle the local browser mode."""
        mode = self.query_one(LocalBrowser).toggle_mode()
        self._request_layout_hint_refresh()
        return mode

    @dataclass
    class BookmarksUpdated(Message):
        """Message sent when the bookmarks are updated."""

        navigation: Navigation
        """The navigation widget sending the message."""

    def add_bookmark(self, title: str, location: HikeLocation) -> None:
        """Add a bookmark.

        Args:
            title: The title of the bookmark.
            location: The location to bookmark.
        """
        self.bookmarks = [Bookmark(title, location), *self.bookmarks]
        self.post_message(self.BookmarksUpdated(self))

    @on(BookmarksView.Renamed)
    def _bookmark_renamed(self, message: BookmarksView.Renamed) -> None:
        """Handle a bookmark being renamed.

        Args:
            message: The message requesting the deletion.
        """
        try:
            bookmark = self.bookmarks.index(message.renamed_from)
        except ValueError:
            self.notify(
                "Could not find the bookmark to modify it",
                title="Bookmark error",
                severity="error",
            )
            return
        (new_bookmarks := self.bookmarks.copy())[bookmark] = message.renamed_to
        self.bookmarks = new_bookmarks
        self.post_message(self.BookmarksUpdated(self))

    @on(BookmarksView.Deleted)
    def _bookmark_deleted(self, message: BookmarksView.Deleted) -> None:
        """handle a bookmark being deleted.

        Args:
            message: The message requesting the deletion.
        """
        try:
            bookmark = self.bookmarks.index(message.deleted)
        except ValueError:
            self.notify(
                "Could not find the bookmark to delete it",
                title="Bookmark error",
                severity="error",
            )
            return
        del (new_bookmarks := self.bookmarks.copy())[bookmark]
        self.bookmarks = new_bookmarks
        self.post_message(self.BookmarksUpdated(self))

    def _activate(self, panel: str) -> None:
        self.query_one(TabbedContent).active = panel
        self.call_next(self.run_action, "move_into_panel")

    @on(TabbedContent.TabActivated)
    def _active_tab_changed(self, _: TabbedContent.TabActivated) -> None:
        """React to the active navigation pane changing."""
        self._request_layout_hint_refresh()

    @on(LocalBrowser.LayoutHintChanged)
    def _local_browser_changed(self, _: LocalBrowser.LayoutHintChanged) -> None:
        """React to the local browser content or mode changing."""
        self._request_layout_hint_refresh()

    @on(Tree.NodeExpanded)
    @on(Tree.NodeCollapsed)
    def _tree_layout_changed(self, _: Message) -> None:
        """Refresh the width hint when tree content changes."""
        self._request_layout_hint_refresh()

    def jump_to_content(self) -> None:
        """Jump into the content panel, if possible."""
        if self.table_of_contents:
            self._activate("content")

    def jump_to_local(self) -> None:
        """Jump into the local browser panel, if possible."""
        self._activate("local")

    def jump_to_bookmarks(self) -> None:
        """Jump into the bookmarks panel, if possible."""
        if self.bookmarks:
            self._activate("bookmarks")

    def jump_to_history(self) -> None:
        """Jump into the history panel, if possible."""
        if self.query_one(HistoryView).option_count:
            self._activate("history")

    async def action_also_down(self) -> None:
        """Hack in some extra cursor down support."""
        if isinstance(self.screen.focused, Tree):
            await self.screen.focused.run_action("cursor_down")
        else:
            await self.run_action("move_into_panel")

    async def action_also_up(self) -> None:
        """Hack in some extra cursor up support."""
        if isinstance(self.screen.focused, Tree):
            await self.screen.focused.run_action("cursor_up")

    async def action_tab_left(self) -> None:
        """Hack in some extra cursor left support."""
        if query := self.query("Tabs:focus"):
            await query[0].run_action("previous_tab")

    async def action_tab_right(self) -> None:
        """Hack in some extra cursor right support."""
        if query := self.query("Tabs:focus"):
            await query[0].run_action("next_tab")


### navigation.py ends here
