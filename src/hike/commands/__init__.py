"""Provides application-wide command-oriented messages."""

##############################################################################
# Local imports.
from .main import (
    BookmarkLocation,
    ChangeCommandLineLocation,
    ChangeNavigationSide,
    CopyLocationToClipboard,
    CopyMarkdownToClipboard,
    Edit,
    JumpToCommandLine,
    JumpToDocument,
    Reload,
    SaveCopy,
    SearchBookmarks,
    SearchHistory,
    ToggleNavigation,
)
from .navigation import (
    Backward,
    Forward,
    JumpToBookmarks,
    JumpToHistory,
    JumpToLocalBrowser,
    JumpToSidebarView,
    JumpToTableOfContents,
    ToggleLocalBrowserMode,
)

##############################################################################
# Exports.
__all__ = [
    "Backward",
    "BookmarkLocation",
    "ChangeCommandLineLocation",
    "ChangeNavigationSide",
    "CopyLocationToClipboard",
    "CopyMarkdownToClipboard",
    "Edit",
    "Forward",
    "JumpToBookmarks",
    "JumpToCommandLine",
    "JumpToDocument",
    "JumpToHistory",
    "JumpToLocalBrowser",
    "JumpToSidebarView",
    "JumpToTableOfContents",
    "ToggleLocalBrowserMode",
    "Reload",
    "SaveCopy",
    "SearchBookmarks",
    "SearchHistory",
    "ToggleNavigation",
]

### __init__.py ends here
