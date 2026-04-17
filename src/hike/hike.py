"""The main application class."""

##############################################################################
##############################################################################
# Textual imports.
from textual import events
from textual.app import InvalidThemeError

##############################################################################
# Textual enhanced imports.
from textual_enhanced.app import EnhancedApp

##############################################################################
# Local imports.
from .app_info import HELP_ABOUT, HELP_LICENSE, HELP_TITLE
from .data import (
    load_configuration,
    update_configuration,
)
from .screens import Main
from .startup import OpenOptions


##############################################################################
class Hike(EnhancedApp[None]):
    """The main application class."""

    HELP_TITLE = HELP_TITLE
    HELP_ABOUT = HELP_ABOUT
    HELP_LICENSE = HELP_LICENSE

    COMMANDS = set()

    def __init__(self, arguments: OpenOptions) -> None:
        """Initialise the application.

        Args:
            The command line arguments passed to the application.
        """
        self._arguments = arguments
        """The command line arguments passed to the application."""
        super().__init__()

    def on_load(self, event: events.Load) -> None:
        """Apply config-backed runtime settings before application mode starts."""
        del event
        configuration = load_configuration()
        theme_name = self._arguments.theme or configuration.theme
        if theme_name is not None:
            try:
                self.theme = theme_name
            except InvalidThemeError:
                pass
        if configuration.bindings:
            self.set_keymap(configuration.bindings)

    def watch_theme(self) -> None:
        """Save the application's theme when it's changed."""
        with update_configuration() as config:
            config.theme = self.theme

    def get_default_screen(self) -> Main:
        """Get the default screen for the application.

        Returns:
            The main screen.
        """
        return Main(self._arguments)

    def action_help_quit(self) -> None:
        """Override Textual's default handling of ctrl+c."""
        if load_configuration().allow_traditional_quit:
            self.exit()
        else:
            super().action_help_quit()


### hike.py ends here
