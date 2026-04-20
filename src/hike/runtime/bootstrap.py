"""Runtime bootstrap helpers for launching Hike."""

##############################################################################
# Python imports.
from __future__ import annotations

##############################################################################
# Local imports.
from ..data import use_runtime_context
from ..hike import Hike
from ..startup import OpenOptions


##############################################################################
def launch_hike(options: OpenOptions) -> None:
    """Create and run the Hike Textual application."""
    with use_runtime_context(options.runtime_context):
        Hike(options).run()


### bootstrap.py ends here
