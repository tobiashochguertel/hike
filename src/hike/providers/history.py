"""Bookmark search and visit commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import CommandHit, CommandHits, CommandsProvider

##############################################################################
# Local imports.
from ..messages import OpenLocation
from ..types import HikeHistory


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
        # TODO: Unique and sort.
        for location in self.history:
            # TODO: Improve what's shown in the palette.
            yield CommandHit(
                f"{location}",
                "",
                OpenLocation(location),
            )


### history.py ends here
