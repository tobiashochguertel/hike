"""Compatibility helpers for supported Python versions."""

##############################################################################
# Python imports.
from enum import Enum


##############################################################################
class StrEnum(str, Enum):
    """Simple `StrEnum`-compatible base for all supported Python versions."""


### compat.py ends here
