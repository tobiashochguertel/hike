"""Shared command catalog data for the main Hike application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit

##############################################################################
# Local imports.
from .commands import (
    Backward,
    BookmarkLocation,
    ChangeCommandLineLocation,
    ChangeNavigationSide,
    CopyLocationToClipboard,
    CopyMarkdownToClipboard,
    Edit,
    Forward,
    JumpToBookmarks,
    JumpToCommandLine,
    JumpToDocument,
    JumpToHistory,
    JumpToLocalBrowser,
    JumpToSidebarView,
    JumpToTableOfContents,
    Reload,
    SaveCopy,
    SearchBookmarks,
    SearchHistory,
    ToggleLocalBrowserMode,
    ToggleNavigation,
)

##############################################################################
MAIN_COMMAND_MESSAGES: tuple[type[Command], ...] = (
    Help,
    ToggleNavigation,
    Edit,
    ChangeTheme,
    Quit,
    Backward,
    BookmarkLocation,
    ChangeCommandLineLocation,
    ChangeNavigationSide,
    CopyLocationToClipboard,
    CopyMarkdownToClipboard,
    Forward,
    JumpToBookmarks,
    JumpToCommandLine,
    JumpToDocument,
    JumpToHistory,
    JumpToLocalBrowser,
    JumpToSidebarView,
    JumpToTableOfContents,
    Reload,
    SaveCopy,
    SearchBookmarks,
    SearchHistory,
    ToggleLocalBrowserMode,
)


### command_catalog.py ends here
