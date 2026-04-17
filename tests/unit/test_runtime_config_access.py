"""Tests for app-facing runtime config helpers."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

##############################################################################
# Textual imports.
from textual.dom import DOMNode

##############################################################################
# Local imports.
from hike.data import Configuration
from hike.runtime.config_access import load_app_configuration, update_app_configuration


##############################################################################
class _FakeApp:
    """Tiny fake Hike app for config-access tests."""

    def __init__(self, configuration: Configuration) -> None:
        self._configuration = configuration

    def configuration(self) -> Configuration:
        return self._configuration

    @contextmanager
    def update_configuration(self) -> Iterator[Configuration]:
        yield self._configuration


##############################################################################
class _FakeNode:
    """Minimal DOM-like node carrying an app reference."""

    def __init__(self, app: _FakeApp) -> None:
        self.app = app


##############################################################################
def test_load_app_configuration_delegates_to_hike_app() -> None:
    """Widgets and screens should read config through the app boundary."""
    configuration = Configuration(theme="textual-light")

    assert (
        load_app_configuration(cast(DOMNode, _FakeNode(_FakeApp(configuration))))
        is configuration
    )


##############################################################################
def test_update_app_configuration_delegates_to_hike_app() -> None:
    """Widgets and screens should update config through the app boundary."""
    configuration = Configuration(local_browser_view_mode="tree")
    node = cast(DOMNode, _FakeNode(_FakeApp(configuration)))

    with update_app_configuration(node) as editable:
        editable.local_browser_view_mode = "flat-list"

    assert configuration.local_browser_view_mode == "flat-list"


### test_runtime_config_access.py ends here
