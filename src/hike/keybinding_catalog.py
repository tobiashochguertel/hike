"""Static keybinding set metadata shared by CLI and runtime code."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Mapping

##############################################################################
DEFAULT_KEYBINDING_SET = "default"
MNEMONIC_KEYBINDING_SET = "mnemonic"

_BUILTIN_KEYBINDING_SETS: dict[str, dict[str, str]] = {
    DEFAULT_KEYBINDING_SET: {},
    MNEMONIC_KEYBINDING_SET: {
        "Help": "?",
        "ToggleNavigation": "ctrl+shift+n",
        "ChangeNavigationSide": "ctrl+alt+n",
        "ChangeTheme": "ctrl+shift+t",
        "SearchBookmarks": "ctrl+shift+b",
        "SearchHistory": "ctrl+shift+h",
        "CopyLocationToClipboard": "ctrl+shift+y",
        "CopyMarkdownToClipboard": "ctrl+shift+m",
        "Edit": "ctrl+e",
        "Quit": "ctrl+q",
    },
}


##############################################################################
def builtin_keybinding_set_names() -> list[str]:
    """Return the sorted list of built-in keybinding set names."""
    return sorted(_BUILTIN_KEYBINDING_SETS)


##############################################################################
def keybinding_set_names(
    custom_sets: Mapping[str, Mapping[str, str]] | None = None,
) -> list[str]:
    """Return the sorted list of built-in and custom keybinding set names."""
    names = set(_BUILTIN_KEYBINDING_SETS)
    if custom_sets is not None:
        names.update(custom_sets)
    return sorted(names)


##############################################################################
def keybinding_set_source(
    name: str,
    custom_sets: Mapping[str, Mapping[str, str]] | None = None,
) -> str:
    """Describe whether a keybinding set is built-in, custom, or both."""
    built_in = name in _BUILTIN_KEYBINDING_SETS
    custom = custom_sets is not None and name in custom_sets
    if built_in and custom:
        return "built-in + custom"
    if built_in:
        return "built-in"
    if custom:
        return "custom"
    raise ValueError(f"Unknown keybinding set: {name}")


##############################################################################
def resolve_keybindings(
    selected_set: str | None = None,
    *,
    custom_sets: Mapping[str, Mapping[str, str]] | None = None,
    overrides: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Resolve the effective keymap for one selected keybinding set."""
    set_name = DEFAULT_KEYBINDING_SET if selected_set is None else selected_set
    keymap: dict[str, str] = {}
    known = False
    if set_name in _BUILTIN_KEYBINDING_SETS:
        keymap.update(_BUILTIN_KEYBINDING_SETS[set_name])
        known = True
    if custom_sets is not None and set_name in custom_sets:
        keymap.update(custom_sets[set_name])
        known = True
    if not known:
        raise ValueError(f"Unknown keybinding set: {set_name}")
    if overrides is not None:
        keymap.update(overrides)
    return keymap


### keybinding_catalog.py ends here
