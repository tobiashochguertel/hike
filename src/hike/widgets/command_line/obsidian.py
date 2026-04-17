"""Provides a command for browsing Obsidian vaults."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual.widget import Widget

##############################################################################
# Local imports.
from ...messages import SetLocalViewRoot
from ...runtime.config_access import load_app_configuration
from .base_command import InputCommand


##############################################################################
class ObsidianCommand(InputCommand):
    """Change the root directory to your Obsidian vaults"""

    COMMAND = "`obsidian`"
    ALIASES = "`obs`"

    @classmethod
    def handle(cls, text: str, for_widget: Widget) -> bool:
        """Handle the command.

        Args:
            text: The text of the command.
            for_widget: The widget to handle the command for.

        Returns:
            `True` if the command was handled; `False` if not.
        """
        if (
            cls.is_command(text)
            and (
                vaults := Path(
                    load_app_configuration(for_widget).obsidian_vaults
                ).expanduser()
            )
            and vaults.exists()
            and vaults.is_dir()
        ):
            for_widget.post_message(SetLocalViewRoot(vaults.resolve()))
            return True
        return False


### obsidian.py ends here
