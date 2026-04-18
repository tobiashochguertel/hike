"""Provides a flat list browser for local Markdown files."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from pathlib import Path

##############################################################################
# Rich imports.
from rich.cells import cell_len
from rich.emoji import Emoji

##############################################################################
# Textual imports.
from textual import on
from textual.content import Content
from textual.message import Message
from textual.widgets._option_list import OptionDoesNotExist
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ...data.local_browser import stable_root_label
from ...data.local_index import (
    LocalIndexNode,
    LocalIndexSnapshot,
    LocalIndexStatus,
    iter_flat_index_nodes,
)
from ...icons import LOCAL_FILE_ICON
from ...messages import OpenLocation, SetLocalViewRoot

##############################################################################
_DIRECTORY_ICON = Emoji.replace(":file_folder:")
_LOADING_OPTION_ID = "__loading__"


##############################################################################
class LocalFlatEntry(Option):
    """The rendered view of a flat local browser entry."""

    def __init__(self, entry: LocalIndexNode) -> None:
        """Initialise the entry view."""
        self.entry = entry
        display_path = entry.relative_path.as_posix()
        display_path = f"{display_path}/" if entry.is_dir else display_path
        super().__init__(
            Content.from_markup(
                f"{_DIRECTORY_ICON if entry.is_dir else LOCAL_FILE_ICON} "
                f"[bold]{display_path}[/]"
            ),
            id=str(entry.path),
        )


##############################################################################
class LocalFlatView(EnhancedOptionList):
    """A flat, relative-path browser for the local filesystem."""

    DEFAULT_CSS = """
    LocalFlatView {
        height: 1fr;
        border: none;
        text-wrap: nowrap;
        text-overflow: ellipsis;
        &:focus {
            border: none;
        }
    }
    """

    HELP = """
    ## Flat Local Browser

    This view shows Markdown files and directories as relative paths from the
    current local browser root.
    """

    BINDINGS = [
        HelpfulBinding(
            "enter",
            "select",
            "Open / enter",
            show=False,
            tooltip="Open a file or change the root to a selected directory",
        ),
    ]

    @dataclass
    class LayoutHintChanged(Message):
        """Message sent when the flat list width may have changed."""

        local_flat_view: LocalFlatView
        """The flat local browser widget sending the message."""

    def __init__(
        self,
        path: str | Path,
        display_root: str | None = None,
    ) -> None:
        """Initialise the flat local browser."""
        self._root = Path(path).expanduser().resolve()
        self._snapshot = LocalIndexSnapshot(
            root=self._root,
            status=LocalIndexStatus.LOADING,
        )
        self._display_root = display_root or stable_root_label(self._root)
        self._width_hint: int | None = None
        self._pending_highlight: Path | None = None
        self._is_loading = False
        super().__init__()
        self.border_title = self._display_root
        self._set_loading_state()

    def _request_layout_hint_refresh(self) -> None:
        """Request a refresh of the sidebar width hint."""
        self.call_after_refresh(self.post_message, self.LayoutHintChanged(self))

    def _set_loading_state(self) -> None:
        """Show an immediate placeholder while the flat list is loading."""
        self._is_loading = True
        self._width_hint = None
        self.clear_options()
        self.add_option(
            Option(
                Content.from_markup("[dim]Loading local files...[/]"),
                id=_LOADING_OPTION_ID,
            )
        )
        self._request_layout_hint_refresh()

    def _apply_entries(self, entries: tuple[LocalIndexNode, ...]) -> None:
        """Apply a freshly-loaded set of entries to the visible option list."""
        self._is_loading = False
        self._width_hint = max(
            (
                cell_len(entry.relative_path.as_posix()) + (3 if entry.is_dir else 2)
                for entry in entries
            ),
            default=None,
        )
        with self.preserved_highlight:
            self.clear_options().add_options(LocalFlatEntry(entry) for entry in entries)
        if self._pending_highlight is not None:
            pending_highlight = self._pending_highlight
            self._pending_highlight = None
            self.highlight_path(pending_highlight)
        self._request_layout_hint_refresh()

    def set_root(self, root: Path) -> None:
        """Set the root directory shown by the flat list."""
        self._root = root.expanduser().resolve()
        self._display_root = stable_root_label(self._root)
        self.border_title = self._display_root
        self._snapshot = LocalIndexSnapshot(
            root=self._root,
            status=LocalIndexStatus.LOADING,
        )
        self._set_loading_state()

    def set_snapshot(self, snapshot: LocalIndexSnapshot) -> None:
        """Render a new shared local-index snapshot."""
        self._snapshot = snapshot
        self._root = snapshot.root
        self._display_root = stable_root_label(self._root)
        self.border_title = self._display_root
        if snapshot.status is LocalIndexStatus.LOADING:
            self._set_loading_state()
            return
        self._apply_entries(iter_flat_index_nodes(snapshot))

    def reload(self) -> None:
        """Reset the widget to its loading placeholder state."""
        self._set_loading_state()

    def highlight_path(self, path: Path) -> bool:
        """Highlight the entry matching the given path, if it exists."""
        resolved = path.expanduser().resolve()
        if self._is_loading:
            self._pending_highlight = resolved
            return False
        try:
            highlighted = self.get_option_index(str(resolved))
        except OptionDoesNotExist:
            return False
        with self.prevent(EnhancedOptionList.OptionHighlighted):
            self.highlighted = highlighted
        return True

    def content_width_hint(self) -> int | None:
        """Return the preferred width of the current flat list."""
        return self._width_hint

    @on(EnhancedOptionList.OptionSelected)
    def _select_entry(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Open a file or enter a directory from the flat list."""
        message.stop()
        if not isinstance(message.option, LocalFlatEntry):
            return
        if message.option.entry.is_dir:
            self.post_message(SetLocalViewRoot(message.option.entry.path))
        else:
            self.post_message(OpenLocation(message.option.entry.path))


### local_flat_view.py ends here
