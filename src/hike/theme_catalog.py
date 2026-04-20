"""Static theme metadata shared by CLI and runtime code."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Textual imports.
from textual.theme import BUILTIN_THEMES


##############################################################################
def theme_names() -> list[str]:
    """Return the sorted list of built-in theme names shown by the CLI."""
    return sorted(theme for theme in BUILTIN_THEMES if theme != "textual-ansi")


### theme_catalog.py ends here
