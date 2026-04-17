"""Runtime bootstrap helpers for launching Hike."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Local imports.
from ..hike import Hike
from ..startup import OpenOptions


##############################################################################
def launch_hike(options: OpenOptions) -> None:
    """Create and run the Hike Textual application."""
    Hike(options).run()


### bootstrap.py ends here
