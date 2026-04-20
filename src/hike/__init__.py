"""Hike -- A Markdown viewer for the terminal."""

##############################################################################
# Python imports.
from importlib.metadata import version
from typing import Final

##############################################################################
# Main app information.
__author__ = "Dave Pearson"
__copyright__ = (
    "Copyright 2025, Dave Pearson; fork changes Copyright 2026, Tobias Hochguertel"
)
__credits__ = ["Dave Pearson", "Tobias Hochguertel"]
__maintainer__ = "Tobias Hochguertel"
__email__ = "davep@davep.org"
__version__ = version("hike")
__licence__ = "GPLv3+"

##############################################################################
USER_AGENT: Final[str] = (
    f"Hike v{__version__} (https://github.com/tobiashochguertel/hike)"
)
"""The user agent string for the viewer."""

### __init__.py ends here
