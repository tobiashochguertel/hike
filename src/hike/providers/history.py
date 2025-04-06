"""Bookmark search and visit commands for the command palette."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from functools import total_ordering
from typing import Final

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Rich imports.
from rich.emoji import Emoji

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import CommandHit, CommandHits, CommandsProvider

##############################################################################
# Local imports.
from ..messages import OpenLocation
from ..types import HikeHistory, HikeLocation

##############################################################################
# Icons.
LOCAL_FILE: Final[str] = Emoji.replace(":page_facing_up:")
"""Icon to use for a local file."""
REMOTE_FILE: Final[str] = Emoji.replace(":globe_with_meridians:")
"""icon to sue for a remote file."""


##############################################################################
@dataclass(frozen=True)
@total_ordering
class Historical:
    """Holds a location from history."""

    location: HikeLocation
    """The location."""

    @property
    def name(self) -> str:
        """A name for the location."""
        if isinstance(self.location, URL):
            return self.location.path
        return str(self.location)

    @property
    def context(self) -> str:
        """The context for the location."""
        if isinstance(self.location, URL):
            return f"{REMOTE_FILE} Remote on {self.location.host}"
        return f"{LOCAL_FILE} Local file"

    def __gt__(self, value: object, /) -> bool:
        if isinstance(value, Historical):
            return self.name.casefold() > value.name.casefold()
        raise NotImplementedError

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Historical):
            return self.name == value.name
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name


##############################################################################
class HistoryCommands(CommandsProvider):
    """A command palette provider related to history."""

    history: HikeHistory = HikeHistory()
    """The history."""

    @classmethod
    def prompt(cls) -> str:
        """The prompt for the command provider."""
        return "Search history..."

    def commands(self) -> CommandHits:
        """Provide the history-based command data for the command palette.

        Yields:
            The commands for the command palette.
        """
        for location in sorted(set(Historical(location) for location in self.history)):
            # TODO: Improve what's shown in the palette.
            yield CommandHit(
                location.name,
                location.context,
                OpenLocation(location.location),
            )


### history.py ends here
