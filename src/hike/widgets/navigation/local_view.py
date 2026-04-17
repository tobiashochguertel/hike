"""Provides a widget for browsing the local filesystem."""

##############################################################################
# Python imports.
from collections.abc import Iterable
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on
from textual.widgets import DirectoryTree

##############################################################################
# Local imports.
from ...data.discovery import LocalDiscoveryOptions, should_include_path
from ...messages import OpenLocation


##############################################################################
class LocalView(DirectoryTree):
    """A browser for the local filesystem."""

    def __init__(
        self,
        path: str | Path,
        *,
        options: LocalDiscoveryOptions | None = None,
    ) -> None:
        """Initialise the local browser."""
        super().__init__(path)
        self._options = options or LocalDiscoveryOptions()

    def configure(self, options: LocalDiscoveryOptions) -> None:
        """Update the discovery options for the local browser."""
        self._options = options
        if self.is_mounted:
            self.reload()

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter a directory for things that look like Markdown.

        Args:
            paths: The paths to filter down.

        Returns:
            The paths filtered as useful for Markdown viewing.
        """
        return (
            path
            for path in paths
            if should_include_path(
                path,
                root=Path(self.path),
                options=self._options,
            )
        )

    @on(DirectoryTree.FileSelected)
    def view_file(self, message: DirectoryTree.FileSelected) -> None:
        """View the selected file.

        Args:
            message: The message requesting that the file be viewed.
        """
        message.stop()
        self.post_message(OpenLocation(message.path))


### local_view.py ends here
