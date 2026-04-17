"""Runtime helpers for lazily loading the TUI application."""

##############################################################################
# Python imports.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..hike import Hike


##############################################################################
def load_hike_class() -> type[Hike]:
    """Import and return the Hike application class on demand."""
    from ..hike import Hike

    return Hike


### runtime.py ends here
