"""Provides a tree widget for browsing the local filesystem."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

##############################################################################
# Rich imports.
from rich.cells import cell_len

##############################################################################
# Textual imports.
from textual import on
from textual.await_complete import AwaitComplete
from textual.message import Message
from textual.widgets import DirectoryTree, Tree
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode

##############################################################################
# Local imports.
from ...data.discovery import LocalDiscoveryOptions, should_include_path
from ...data.local_browser import stable_root_label
from ...messages import OpenLocation


##############################################################################
def _tree_node_depth(node: TreeNode[Any]) -> int:
    """Return the visible depth of a tree node."""
    depth = 0
    current = node.parent
    while current is not None and current.parent is not None:
        depth += 1
        current = current.parent
    return depth


##############################################################################
def _visible_tree_width(node: TreeNode[Any]) -> int:
    """Measure the visible width of a tree node and any expanded children."""
    label = node.label if isinstance(node.label, str) else node.label.plain
    width = cell_len(label) + 6 + (_tree_node_depth(node) * 2)
    if node.is_expanded:
        for child in node.children:
            width = max(width, _visible_tree_width(child))
    return width


##############################################################################
class LocalView(DirectoryTree):
    """A tree browser for the local filesystem."""

    @dataclass
    class LayoutHintChanged(Message):
        """Message sent when the visible tree width may have changed."""

        local_view: LocalView
        """The local tree widget sending the message."""

    def __init__(
        self,
        path: str | Path,
        *,
        options: LocalDiscoveryOptions | None = None,
        display_root: str | None = None,
    ) -> None:
        """Initialise the local browser tree."""
        resolved = Path(path).expanduser().resolve()
        self._options = options or LocalDiscoveryOptions()
        self._display_root = display_root or stable_root_label(resolved)
        super().__init__(resolved)
        self.show_root = False
        self.border_title = self._display_root

    async def watch_path(self) -> None:
        """Watch for changes to the root path of the local tree."""
        has_cursor = self.cursor_node is not None
        self.reset_node(
            self.root,
            self._display_root,
            DirEntry(self.PATH(self.path)),
        )
        await self.reload()
        if has_cursor:
            self.cursor_line = 0
        self.scroll_to(0, 0, animate=False)
        self._request_layout_hint_refresh()

    def _request_layout_hint_refresh(self) -> None:
        """Request a refresh of the sidebar width hint."""
        self.call_after_refresh(self.post_message, self.LayoutHintChanged(self))

    def set_root(self, root: Path) -> None:
        """Set the root directory shown by the tree."""
        resolved = root.expanduser().resolve()
        self._display_root = stable_root_label(resolved)
        self.border_title = self._display_root
        self.path = resolved

    async def _reveal_path(self, path: Path) -> bool:
        """Expand and highlight a visible path within the tree."""
        target = path.expanduser().resolve()
        root = Path(self.path).resolve()
        try:
            relative_target = target.relative_to(root)
        except ValueError:
            return False

        current = self.root
        await self._add_to_load_queue(current)
        next_path = root
        for segment in relative_target.parts:
            next_path = next_path / segment
            child = next(
                (
                    node
                    for node in current.children
                    if node.data is not None and node.data.path.resolve() == next_path
                ),
                None,
            )
            if child is None:
                return False
            current = child
            if current.allow_expand:
                current.expand()
                await self._add_to_load_queue(current)

        self.move_cursor(current, animate=False)
        self.select_node(current)
        return True

    def highlight_path(self, path: Path) -> None:
        """Schedule a highlight update for the given tree path."""
        self.run_worker(
            self._reveal_path(path),
            name="local-view-highlight",
            group="local-view-highlight",
            exclusive=True,
        )

    def reload(self) -> AwaitComplete:
        """Reload the tree and schedule a width-hint refresh."""
        reloaded = super().reload()
        self.set_timer(0.05, self._request_layout_hint_refresh)
        return reloaded

    def configure(self, options: LocalDiscoveryOptions) -> None:
        """Update the discovery options for the local browser."""
        self._options = options
        if self.is_mounted:
            self.reload()
            self._request_layout_hint_refresh()

    def content_width_hint(self) -> int | None:
        """Return the preferred width of the currently-visible tree."""
        if not self.root.children:
            return None
        return max(_visible_tree_width(child) for child in self.root.children)

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter a directory for things that look like Markdown."""
        return (
            path
            for path in paths
            if should_include_path(
                path,
                root=Path(self.path),
                options=self._options,
            )
        )

    @on(Tree.NodeExpanded)
    @on(Tree.NodeCollapsed)
    def _tree_layout_changed(self, _: Message) -> None:
        """Refresh the width hint after asynchronous node changes settle."""
        self._request_layout_hint_refresh()
        self.set_timer(0.05, self._request_layout_hint_refresh)

    @on(DirectoryTree.FileSelected)
    def view_file(self, message: DirectoryTree.FileSelected) -> None:
        """Open the selected file."""
        message.stop()
        self.post_message(OpenLocation(message.path))


### local_view.py ends here
