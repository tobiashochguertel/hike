"""A MarkdownIt plugin for parsing [[WikiLinks]]."""

##############################################################################
# Python imports.
from pathlib import PurePosixPath
from re import Pattern, compile
from typing import Final

##############################################################################
# MarkdownIt imports.
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

##############################################################################
_DETECT_WIKILINK: Final[Pattern[str]] = compile(r"\[\[(?P<content>[^\]]+)\]\]")
"""Regular expression for detecting wikilinks."""


##############################################################################
def _make_href(target: str) -> str:
    """Make a URL for the given wikilink target.

    Args:
        target: The target of the wikilink.

    Returns:
        A URL for the given wikilink target.
    """
    filename, _, anchor = target.strip().partition("#")
    if filename and not PurePosixPath(filename).suffix:
        filename = f"{filename}.md"
    if filename and not anchor:
        return filename
    if anchor and not filename:
        return f"#{anchor}"
    return f"{filename}#{anchor}"


##############################################################################
def _handle_wikilink(state: StateInline, silent: bool) -> bool:
    """MarkdownIt rule for parsing wikilinks.

    Args:
        state: The current inline parser state.
        silent: Should we only work in detect mode?

    Returns:
        Whether a wikilink was successfully parsed.
    """
    if (link := _DETECT_WIKILINK.match(state.src, state.pos)) is None:
        return False
    if not (content := link["content"].strip()):
        return False
    target, _, text = content.partition("|")
    if "\n" in target:
        return False
    if silent:
        return True
    token = state.push("link_open", "a", 1)
    token.attrs = {"href": _make_href(target)}
    token.markup = "[["
    token.info = "wikilink"
    display_token = state.push("text", "", 0)
    display_token.content = (text or target).strip()
    state.push("link_close", "a", -1)
    state.pos = link.end()
    return True


##############################################################################
def wikilink_plugin(markdown: MarkdownIt) -> None:
    """MarkdownIt plugin to add wikilink support.

    Args:
        md: The MarkdownIt instance to extend.
    """
    markdown.inline.ruler.push("wikilink", _handle_wikilink)


### wikilinks.py ends here
