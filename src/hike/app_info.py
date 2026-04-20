"""Application metadata that should not depend on the Textual runtime."""

##############################################################################
# Local imports.
from . import __version__
from .build_info import build_info

##############################################################################
APP_NAME = "Hike"
APP_DESCRIPTION = "A Markdown browser for the terminal."
APP_VERSION = __version__
APP_BUILD_INFO = build_info()
HELP_TITLE = f"{APP_NAME} v{APP_VERSION}"
HELP_ABOUT = """
`Hike` is a terminal-based Markdown viewer originally created by
[Dave Pearson](https://www.davep.org/). This fork is Free Software and can be
[found on GitHub](https://github.com/tobiashochguertel/hike).
"""
HELP_LICENSE = """
Hike - A Markdown viewer for the terminal.  \n
Original project Copyright (C) 2025 Dave Pearson  \n
Fork-specific changes Copyright (C) 2026 Tobias Hochguertel

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""


### app_info.py ends here
