"""The main screen for the application."""

##############################################################################
# Python imports.
from collections.abc import Callable
from contextlib import AbstractContextManager
from functools import partial
from pathlib import Path

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import copy as copy_to_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalGroup
from textual.widgets import Footer, Header, Markdown

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command, Help, Quit
from textual_enhanced.dialogs import ModalInput
from textual_enhanced.screen import EnhancedScreen
from textual_enhanced.tools import add_key

##############################################################################
# Textual fspicker imports.
from textual_fspicker import FileOpen, FileSave, Filters

##############################################################################
# Local imports.
from .. import __version__
from ..command_catalog import MAIN_COMMAND_MESSAGES
from ..commands import (
    Backward,
    BookmarkLocation,
    CopyLocationToClipboard,
    CopyMarkdownToClipboard,
    Edit,
    Forward,
    JumpToBookmarks,
    JumpToHistory,
    JumpToLocalBrowser,
    JumpToSidebarView,
    JumpToTableOfContents,
    Reload,
    SaveCopy,
)
from ..data import (
    Configuration,
    can_be_negotiated_to_markdown,
    load_bookmarks,
    load_command_history,
    load_history,
    maybe_markdown,
    save_bookmarks,
    save_command_history,
    save_history,
)
from ..data.discovery import LocalDiscoveryOptions, local_discovery_options
from ..data.layout import LayoutMode, LayoutState, effective_layout_state, layout_policy
from ..data.location_types import (
    markdown_content_types_from_configuration,
    markdown_extensions_from_configuration,
)
from ..messages import (
    ClearHistory,
    CopyToClipboard,
    DeduplicateHistory,
    HandleInput,
    OpenFrom,
    OpenFromForge,
    OpenFromHistory,
    OpenLocation,
    RemoveHistoryEntry,
    SetLocalViewRoot,
)
from ..providers import BookmarkCommands, HistoryCommands, MainCommands
from ..runtime.config_access import load_app_configuration, update_app_configuration
from ..startup import OpenOptions, StartupTargetKind, classify_startup_target
from ..support import view_in_browser
from ..widgets import CommandLine, Navigation, Viewer


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"Hike v{__version__}"

    DEFAULT_CSS = """
    Main {
        #workspace {
            hatch: right $surface;
            .panel {
                border-left: solid $panel;
                &:focus, &:focus-within {
                    border-left: solid $border;
                }
            }
        }

        .panel {
            background: $surface;
            &:focus-within {
                background: $panel 80%;
            }
            * {
                scrollbar-background: $surface;
                scrollbar-background-hover: $surface;
                scrollbar-background-active: $surface;
            }
            &:focus-within * {
                scrollbar-background: $panel;
                scrollbar-background-hover: $panel;
                scrollbar-background-active: $panel;
            }
        }

        Navigation {
            display: none;
        }
        &.layout-split Navigation,
        &.layout-sidebar-only Navigation {
            display: block;
        }
        &.layout-sidebar-only Viewer {
            display: none;
        }
    }
    """

    HELP = """
    ## Main application keys and commands

    The following key bindings and commands are available:
    """

    COMMAND_MESSAGES = MAIN_COMMAND_MESSAGES

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)
    COMMANDS = {MainCommands}

    AUTO_FOCUS = "CommandLine Input"

    def __init__(self, arguments: OpenOptions, *, configuration: Configuration) -> None:
        """Initialise the main screen.

        Args:
            arguments: The arguments passed to the application on the command line.
        """
        self._arguments = arguments
        """The arguments passed on the command line."""
        self._initial_configuration = configuration
        """The configuration snapshot available during screen construction."""
        self._startup_target = classify_startup_target(
            getattr(arguments, "target", None)
        )
        """The classified startup target."""
        self._initial_local_root = self._resolve_initial_local_root()
        """The initial root directory for the local browser."""
        self._layout_state = LayoutState()
        """The effective layout state."""
        self._mode_override: LayoutMode | None = None
        """An optional single-pane mode override for responsive layouts."""
        self._local_options = LocalDiscoveryOptions()
        """The effective local browser discovery options."""
        super().__init__()

    def _configuration(self) -> Configuration:
        """Return the active configuration for this screen."""
        return load_app_configuration(self)

    def _update_configuration(self) -> AbstractContextManager[Configuration]:
        """Return a context manager for updating configuration."""
        return update_app_configuration(self)

    def _navigation(self) -> Navigation:
        """Return the navigation widget."""
        return self.query_one(Navigation)

    def _viewer(self) -> Viewer:
        """Return the viewer widget."""
        return self.query_one(Viewer)

    def _command_line(self) -> CommandLine:
        """Return the command line widget."""
        return self.query_one(CommandLine)

    def _is_narrow_layout(self, width: int | None = None) -> bool:
        """Return `True` when the current terminal should use single-pane mode."""
        return layout_policy(self._configuration()).responsive.is_narrow(
            self.size.width if width is None else width
        )

    def _store_navigation_enabled(self, enabled: bool) -> None:
        """Persist whether navigation should be available in wide layouts."""
        with self._update_configuration() as config:
            config.navigation_visible = enabled

    def _resolve_initial_local_root(self) -> Path:
        """Resolve the initial root directory for the local browser."""
        if self._arguments.root is not None:
            return Path(self._arguments.root).expanduser().resolve()
        if self._startup_target.kind is StartupTargetKind.FILE and isinstance(
            self._startup_target.value, Path
        ):
            return self._startup_target.value.parent
        if self._startup_target.kind is StartupTargetKind.DIRECTORY and isinstance(
            self._startup_target.value, Path
        ):
            return self._startup_target.value
        return (
            Path(self._initial_configuration.local_start_location)
            .expanduser()
            .resolve()
        )

    def _resolve_layout_state(
        self,
        *,
        navigation_override: bool | None = None,
        mode_override: LayoutMode | None = None,
        sidebar_content_width: int | None = None,
    ) -> LayoutState:
        """Resolve the effective layout state for the current terminal size."""
        configuration = self._configuration()
        return effective_layout_state(
            configuration,
            terminal_width=self.size.width,
            navigation_override=navigation_override,
            mode_override=mode_override,
            sidebar_content_width=sidebar_content_width,
            current_sidebar_width=self._layout_state.sidebar_width,
            policy=layout_policy(configuration),
        )

    def _refresh_layout_state(self, *, navigation_override: bool | None = None) -> None:
        """Recompute and apply the current layout state."""
        self._apply_layout_state(
            self._resolve_layout_state(
                navigation_override=navigation_override,
                mode_override=self._mode_override,
                sidebar_content_width=self._navigation().content_width_hint(),
            )
        )

    def _apply_layout_state(self, layout_state: LayoutState) -> None:
        """Apply the computed layout state to the mounted widgets."""
        self._layout_state = layout_state
        self.set_class(layout_state.mode is LayoutMode.SPLIT, "layout-split")
        self.set_class(
            layout_state.mode is LayoutMode.CONTENT_ONLY, "layout-content-only"
        )
        self.set_class(
            layout_state.mode is LayoutMode.SIDEBAR_ONLY, "layout-sidebar-only"
        )
        self._navigation().apply_layout_state(layout_state)
        self._command_line().dock_top = layout_state.command_line_on_top
        if (
            layout_state.mode is LayoutMode.CONTENT_ONLY
            and self._navigation().has_focus_within
        ):
            self.call_after_refresh(self._viewer().focus)

    def _set_navigation_visible(
        self, visible: bool, *, persist_navigation: bool = True
    ) -> Navigation:
        """Update navigation visibility through the layout policy."""
        if persist_navigation:
            self._store_navigation_enabled(visible)
        if self._is_narrow_layout():
            self._mode_override = (
                LayoutMode.SIDEBAR_ONLY if visible else LayoutMode.CONTENT_ONLY
            )
            self._refresh_layout_state()
            return self._navigation()
        self._mode_override = None
        self._refresh_layout_state(navigation_override=visible)
        return self._navigation()

    def _show_navigation(
        self, jump_to: Callable[[Navigation], None] | None = None
    ) -> Navigation:
        """Ensure the navigation panel is visible and optionally jump within it."""
        navigation = self._set_navigation_visible(True)
        if jump_to is not None:
            jump_to(navigation)
        return navigation

    def _show_document(self, *, focus: bool = True) -> None:
        """Ensure the document pane is visible in responsive layouts."""
        if self._is_narrow_layout():
            self._set_navigation_visible(False, persist_navigation=False)
        if focus:
            self._viewer().focus()

    def _show_sidebar_view(self) -> None:
        """Ensure the active sidebar view is visible and focused."""
        navigation = self._show_navigation()
        navigation.call_after_refresh(navigation.run_action, "move_into_panel")

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        with VerticalGroup():
            with Horizontal(id="workspace"):
                yield Navigation(
                    classes="panel",
                    local_root=self._initial_local_root,
                    local_options=self._local_options,
                    local_browser_mode=self._initial_configuration.local_browser_view_mode,
                )
                yield Viewer(classes="panel")
            yield CommandLine(classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        """Configure the screen once the DOM is mounted."""
        config = self._configuration()
        self._local_options = local_discovery_options(self._arguments, config)
        if self._arguments.navigation is not None:
            self._store_navigation_enabled(self._arguments.navigation)
        self._refresh_layout_state()
        self._navigation().bookmarks = (bookmarks := load_bookmarks())
        self._navigation().configure_local_view(self._local_options)
        BookmarkCommands.bookmarks = bookmarks
        self._viewer().history = load_history()
        self._command_line().history = load_command_history()
        self._handle_startup_input()

    def on_resize(self) -> None:
        """Keep the layout state in sync with terminal width changes."""
        if self.is_mounted:
            if not self._is_narrow_layout():
                self._mode_override = None
            self._refresh_layout_state()

    def _handle_startup_input(self) -> None:
        """Handle any startup target or startup command."""
        startup_command = self._arguments.command
        if startup_command:
            self.call_after_refresh(
                self.post_message,
                HandleInput(" ".join(startup_command)),
            )
            return
        startup_target = self._startup_target
        if startup_target.kind is StartupTargetKind.NONE:
            return
        if startup_target.kind is StartupTargetKind.FILE and isinstance(
            startup_target.value, Path
        ):
            self.call_after_refresh(
                self.post_message,
                OpenLocation(startup_target.value),
            )
            return
        if startup_target.kind is StartupTargetKind.URL and isinstance(
            startup_target.value, URL
        ):
            self.call_after_refresh(
                self.post_message,
                OpenLocation(startup_target.value),
            )
            return
        if startup_target.kind is StartupTargetKind.DIRECTORY and isinstance(
            startup_target.value, Path
        ):
            self.call_after_refresh(self._show_navigation, Navigation.jump_to_local)
            return
        self.notify(
            f"Could not locate {startup_target.value!r}",
            title="Startup target error",
            severity="error",
            timeout=8,
        )

    @on(Help)
    async def _show_help(self) -> None:
        """Handle the help action."""
        await self.run_action("help_command")

    @on(HandleInput)
    def _handle_input(self, message: HandleInput) -> None:
        """Handle input as if the user had typed it in.

        Args:
            message: The message requesting the input be handled.
        """
        self.query_one(CommandLine).handle_input(message.user_input)

    @on(CopyToClipboard)
    def _copy_text_to_clipbaord(self, message: CopyToClipboard) -> None:
        """Copy some text into the clipboard.

        Args:
            message: The message requesting the text be copied.
        """
        # First off, use Textual's own copy to clipboard facility. Generally
        # this will work in most terminals, and if it does it'll likely work
        # best, getting the text through remote connections to the user's
        # own environment.
        self.app.copy_to_clipboard(message.text)
        # However, as a backup, use pyerclip too. If the above did fail due
        # to the terminal not supporting the operation, this might.
        try:
            copy_to_clipboard(message.text)
        except PyperclipException:
            pass
        # Give the user some feedback.
        self.notify("Copied")

    @on(OpenLocation)
    async def _open_markdown(self, message: OpenLocation) -> None:
        """Open a file for viewing.

        Args:
            message: The message requesting the file be opened.
        """
        configuration = self._configuration()
        if maybe_markdown(
            message.to_open,
            markdown_extensions_from_configuration(configuration),
        ) or await can_be_negotiated_to_markdown(
            message.to_open,
            markdown_content_types_from_configuration(configuration),
        ):
            self.query_one(Viewer).goto_anchor_after_load(
                message.anchor
            ).location = message.to_open
            self._show_document(focus=configuration.focus_viewer_on_load)
        else:
            view_in_browser(message.to_open)

    @on(OpenFrom)
    @work
    async def _browse_for_file(self, message: OpenFrom) -> None:
        """Browse for a markdown file with a file open dialog.

        Args:
            message: The message requesting the operation.
        """
        if chosen := await self.app.push_screen_wait(
            FileOpen(
                message.location,
                filters=Filters(
                    (
                        "Markdown",
                        lambda path: maybe_markdown(
                            path,
                            markdown_extensions_from_configuration(
                                self._configuration()
                            ),
                        ),
                    ),
                    ("All files", lambda _: True),
                ),
                cancel_button=partial(add_key, key="Esc", context=self),
            )
        ):
            self.post_message(OpenLocation(chosen))

    @on(OpenFromHistory)
    def _open_from_history(self, message: OpenFromHistory) -> None:
        """Open a location from the history.

        Args:
            message: The message requesting the history open.
        """
        self.query_one(Viewer).goto(message.location)
        self._show_document()

    @on(OpenFromForge)
    @work
    async def _open_from_forge(self, message: OpenFromForge) -> None:
        """Open a file from a git forge.

        Args:
            message: The message requesting the operation.
        """
        if (url := await message.url(self._configuration().main_branches)) is None:
            self.notify(
                "The file you were after could not be located.\n\n"
                "Check the spelling of the owner, repository and file; "
                "also consider what branch it might be on.",
                title=f"No suitable {message.forge} target found",
                severity="error",
                timeout=8,
            )
        else:
            self.post_message(OpenLocation(url))

    @on(RemoveHistoryEntry)
    def _remove_location_from_history(self, message: RemoveHistoryEntry) -> None:
        """Remove a specific location from history.

        Args:
            message: The message requesting the location be removed.
        """
        self.query_one(Viewer).remove_from_history(message.location)

    @on(ClearHistory)
    def _clear_down_history(self) -> None:
        """Clear all items from history."""
        self.query_one(Viewer).clear_history()

    @on(DeduplicateHistory)
    def _deduplicate_history(self) -> None:
        """Deduplicate the history."""
        self.query_one(Viewer).deduplicate_history()

    @on(SetLocalViewRoot)
    def _set_local_root(self, message: SetLocalViewRoot) -> None:
        """Change the root directory of the local file browser.

        Args:
            message: The message requesting the root be changed.
        """
        self.query_one(Navigation).set_local_view_root(message.root)

    @on(Markdown.TableOfContentsUpdated)
    def _update_navigation_contents(
        self, message: Markdown.TableOfContentsUpdated
    ) -> None:
        """Handle the table of contents being updated.

        Args:
            message: The message broadcasting that the ToC is updated.
        """
        self.query_one(Navigation).table_of_contents = message.table_of_contents

    @on(Navigation.LayoutHintChanged)
    def _refresh_navigation_width(self, _: Navigation.LayoutHintChanged) -> None:
        """Recompute the sidebar width from the active navigation content."""
        self._refresh_layout_state()

    @on(Markdown.TableOfContentsSelected)
    def _jump_to_content(self, message: Markdown.TableOfContentsSelected) -> None:
        """Jump to a specific location in the current document.

        Args:
            message: The message request the jump.
        """
        self.query_one(Viewer).jump_to_content(message.block_id)
        self._show_document()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action is possible to perform right now.

        Args:
            action: The action to perform.
            parameters: The parameters of the action.

        Returns:
            `True` if it can perform, `False` or `None` if not.
        """
        if not self.is_mounted:
            # Surprisingly it seems that Textual's "dynamic bindings" can
            # cause this method to be called before the DOM is up and
            # running. This breaks the rule of least astonishment, I'd say,
            # but okay let's be defensive... (when I can come up with a nice
            # little MRE I'll report it).
            return True
        if action == Forward.action_name():
            return self.query_one(Viewer).history.can_go_forward or None
        if action == Backward.action_name():
            return self.query_one(Viewer).history.can_go_backward or None
        if action == Edit.action_name():
            return self.query_one(Viewer).is_editable or None
        if action in (
            command.action_name()
            for command in (
                BookmarkLocation,
                CopyLocationToClipboard,
                CopyMarkdownToClipboard,
                Reload,
                SaveCopy,
            )
        ):
            return self.query_one(Viewer).location is not None
        return True

    def action_reload_command(self) -> None:
        """Reload the current document."""
        self._show_document()
        self.query_one(Viewer).reload()

    def action_search_bookmarks_command(self) -> None:
        """Search the bookmarks in the command palette."""
        self.show_palette(BookmarkCommands)

    def action_search_history_command(self) -> None:
        """search the history in the command palette."""
        self.show_palette(HistoryCommands)

    def action_toggle_navigation_command(self) -> None:
        """Toggle the display of the navigation panel."""
        if self._is_narrow_layout():
            showing_sidebar = self._layout_state.mode is LayoutMode.SIDEBAR_ONLY
            self._set_navigation_visible(
                not showing_sidebar,
                persist_navigation=False,
            )
            if showing_sidebar:
                self._viewer().focus()
            else:
                navigation = self._navigation()
                navigation.call_after_refresh(navigation.run_action, "move_into_panel")
            return
        self._set_navigation_visible(not self._configuration().navigation_visible)

    def action_toggle_local_browser_mode_command(self) -> None:
        """Toggle the local browser between tree and flat-list modes."""
        navigation = self._show_navigation(Navigation.jump_to_local)
        navigation.toggle_local_browser_mode()

    def action_change_navigation_side_command(self) -> None:
        """Change the side that the navigation panel lives on."""
        with self._update_configuration() as config:
            config.navigation_on_right = not config.navigation_on_right
        self._refresh_layout_state()

    def action_change_command_line_location_command(self) -> None:
        """Change the location of the command line."""
        with self._update_configuration() as config:
            config.command_line_on_top = not config.command_line_on_top
        self._refresh_layout_state()

    def action_jump_to_command_line_command(self) -> None:
        """Jump to the command line."""
        if self.AUTO_FOCUS:
            self.query_one(self.AUTO_FOCUS).focus()

    def action_jump_to_document_command(self) -> None:
        """Jump to the document."""
        self._show_document()

    def action_backward_command(self) -> None:
        """Move backward through history."""
        self._show_document()
        self.query_one(Viewer).backward()

    def action_forward_command(self) -> None:
        """Move forward through history."""
        self._show_document()
        self.query_one(Viewer).forward()

    @work
    async def action_bookmark_location_command(self) -> None:
        """Add the current location to the bookmarks."""
        if (location := self.query_one(Viewer).location) is None:
            self.notify(
                "Please visit a file or URL to bookmark it.", severity="warning"
            )
            return
        if location in self.query_one(Navigation).bookmarks:
            self.notify(
                "This location is already in your bookmarks", severity="warning"
            )
            return
        if title := await self.app.push_screen_wait(
            ModalInput("Enter a title for the bookmark")
        ):
            self.query_one(Navigation).add_bookmark(title, location)
            self.notify("Bookmark added")

    @on(Quit)
    def action_quit_command(self) -> None:
        """Quit the application."""
        self.app.exit()

    @on(JumpToTableOfContents)
    def action_jump_to_table_of_contents_command(self) -> None:
        """Jump to the table of contents."""
        self._show_navigation(Navigation.jump_to_content)

    @on(JumpToLocalBrowser)
    def action_jump_to_local_browser_command(self) -> None:
        """Jump to the local browser."""
        self._show_navigation(Navigation.jump_to_local)

    @on(JumpToSidebarView)
    def action_jump_to_sidebar_view_command(self) -> None:
        """Jump to the currently active sidebar view."""
        self._show_sidebar_view()

    @on(JumpToBookmarks)
    def action_jump_to_bookmarks_command(self) -> None:
        """Jump to the bookmarks."""
        self._show_navigation(Navigation.jump_to_bookmarks)

    @on(JumpToHistory)
    def action_jump_to_history_command(self) -> None:
        """Jump to the history."""
        self._show_navigation(Navigation.jump_to_history)

    def action_copy_location_to_clipboard_command(self) -> None:
        """Copy the current location to the clipboard."""
        self.post_message(CopyToClipboard(str(self.query_one(Viewer).location)))

    def action_copy_markdown_to_clipboard_command(self) -> None:
        """Copy the current markdown to the clipboard."""
        self.post_message(CopyToClipboard(self.query_one(Viewer).source))

    def action_edit_command(self) -> None:
        """Edit the current markdown document, if possible."""
        self._show_document()
        self.query_one(Viewer).edit()

    @work
    async def action_save_copy_command(self) -> None:
        """Save a copy of the current document to a new file."""
        if (suggested := self.query_one(Viewer).filename) is None:
            return
        if save_to := await self.app.push_screen_wait(
            FileSave(
                default_file=suggested,
                cancel_button=partial(add_key, key="Esc", context=self),
            )
        ):
            try:
                save_to.write_text(self.query_one(Viewer).source, encoding="utf-8")
            except OSError as error:
                self.notify(str(error), title="Save Error", severity="error", timeout=8)
                return
            self.notify(f"Saved {save_to}")
            self.query_one(Navigation).refresh_local_view()

    @on(Viewer.HistoryUpdated)
    def _update_history(self, message: Viewer.HistoryUpdated) -> None:
        """Update the view of history when it changes.

        Args:
            message: The message to say that history changed.
        """
        HistoryCommands.history = message.viewer.history
        self.query_one(Navigation).update_history(message.viewer.history)
        save_history(message.viewer.history)

    @on(Viewer.HistoryVisit)
    def _move_history(self, message: Viewer.HistoryVisit) -> None:
        """React to a new location in history being visited."""
        if (location := message.viewer.history.current_location) is not None:
            self.query_one(Navigation).highlight_history(location)

    @on(Navigation.BookmarksUpdated)
    def _update_bookmarks(self, message: Navigation.BookmarksUpdated) -> None:
        """Handle the bookmarks being updated."""
        save_bookmarks(message.navigation.bookmarks)
        BookmarkCommands.bookmarks = message.navigation.bookmarks

    @on(CommandLine.HistoryUpdated)
    def _save_command_line_history(self, message: CommandLine.HistoryUpdated) -> None:
        """Save the command line history to storage when it changes.

        Args:
            message: The message requesting the same.
        """
        save_command_history(message.command_line.history)


### main.py ends here
