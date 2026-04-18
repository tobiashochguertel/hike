"""Typed request models for the Typer CLI layer."""

##############################################################################
# Python imports.
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


##############################################################################
@dataclass(frozen=True)
class OpenCommandRequest:
    """The parsed `hike open` request before runtime conversion."""

    target: str | None
    command: str | None
    navigation: bool | None
    theme: str | None
    binding_set: str | None
    root: Path | None
    ignore: bool | None
    hidden: bool | None
    exclude: tuple[str, ...]


### contracts.py ends here
