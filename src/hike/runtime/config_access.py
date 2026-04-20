"""App-facing configuration helpers for screens and widgets."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import Protocol, cast

##############################################################################
# Textual imports.
from textual.dom import DOMNode

##############################################################################
# Local imports.
from ..data import Configuration


##############################################################################
class HikeApp(Protocol):
    """Minimal app protocol needed by runtime config helpers."""

    def configuration(self) -> Configuration: ...

    def update_configuration(self) -> AbstractContextManager[Configuration]: ...


##############################################################################
def hike_app(node: DOMNode) -> HikeApp:
    """Return the Hike application for a screen or widget."""
    return cast(HikeApp, node.app)


##############################################################################
def load_app_configuration(node: DOMNode) -> Configuration:
    """Load configuration through the running Hike application."""
    return hike_app(node).configuration()


##############################################################################
@contextmanager
def update_app_configuration(node: DOMNode) -> Iterator[Configuration]:
    """Update configuration through the running Hike application."""
    with hike_app(node).update_configuration() as configuration:
        yield configuration


### config_access.py ends here
