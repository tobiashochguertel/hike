"""Functions for testing location types."""

##############################################################################
# Python imports.
from collections.abc import Sequence
from functools import singledispatch
from pathlib import Path

##############################################################################
# httpx imports.
from httpx import URL, AsyncClient, HTTPStatusError, RequestError

##############################################################################
from typing_extensions import TypeIs

##############################################################################
# Local imports.
from .. import USER_AGENT
from ..types import HikeLocation
from .config import Configuration

##############################################################################
_DEFAULT_CONFIGURATION = Configuration()


##############################################################################
def markdown_extensions_from_configuration(
    configuration: Configuration,
) -> tuple[str, ...]:
    """Return normalized markdown extensions from configuration."""
    return tuple(extension.lower() for extension in configuration.markdown_extensions)


##############################################################################
def markdown_content_types_from_configuration(
    configuration: Configuration,
) -> tuple[str, ...]:
    """Return configured markdown content types as a tuple."""
    return tuple(configuration.markdown_content_types)


##############################################################################
def _resolved_markdown_extensions(
    markdown_extensions: Sequence[str] | None,
) -> tuple[str, ...]:
    """Return the explicit or default markdown extensions."""
    return (
        tuple(extension.lower() for extension in markdown_extensions)
        if markdown_extensions is not None
        else markdown_extensions_from_configuration(_DEFAULT_CONFIGURATION)
    )


##############################################################################
def _resolved_markdown_content_types(
    markdown_content_types: Sequence[str] | None,
) -> tuple[str, ...]:
    """Return the explicit or default markdown content types."""
    return (
        tuple(markdown_content_types)
        if markdown_content_types is not None
        else markdown_content_types_from_configuration(_DEFAULT_CONFIGURATION)
    )


##############################################################################
@singledispatch
def maybe_markdown(
    location: object,
    markdown_extensions: Sequence[str] | None = None,
) -> bool:
    """Does the given location look like it might be a Markdown file?

    Args:
        location: The location to test.
        markdown_extensions: Optional explicit markdown extensions to use.

    Returns:
        `True` if the location looks like it's Markdown, `False` if not.
    """
    return False


##############################################################################
@maybe_markdown.register
def _(location: Path, markdown_extensions: Sequence[str] | None = None) -> bool:
    return location.suffix.lower() in _resolved_markdown_extensions(markdown_extensions)


##############################################################################
@maybe_markdown.register
def _(location: str, markdown_extensions: Sequence[str] | None = None) -> bool:
    return maybe_markdown(Path(location), markdown_extensions)


##############################################################################
@maybe_markdown.register
def _(location: URL, markdown_extensions: Sequence[str] | None = None) -> bool:
    return maybe_markdown(location.path, markdown_extensions)


##############################################################################
async def can_be_negotiated_to_markdown(
    location: HikeLocation,
    markdown_content_types: Sequence[str] | None = None,
) -> bool:
    """Can the given location be negotiated to Markdown?

    Args:
        location: The location to test.
        markdown_content_types: Optional explicit accepted markdown content types.

    Returns:
        `True` if the location can be negotiated to Markdown, `False` if
        not.
    """
    if isinstance(location, Path):
        return False
    accepted_content_types = _resolved_markdown_content_types(markdown_content_types)
    async with AsyncClient() as client:
        try:
            response = await client.head(
                location,
                follow_redirects=True,
                headers={
                    "user-agent": USER_AGENT,
                    "Accept": ",".join((*accepted_content_types, "*/*;q=0.1")),
                },
            )
        except RequestError:
            return False
    try:
        response.raise_for_status()
    except HTTPStatusError:
        return False
    if content_type := response.headers.get("content-type"):
        return any(
            content_type.startswith(accepted_type)
            for accepted_type in accepted_content_types
        )
    return False


##############################################################################
def looks_urllike(candidate: str) -> bool:
    """Does the given value look like a URL?

    Args:
        candidate: The candidate to test.

    Returns:
        `True` if the string looks like a URL, `False` if not.
    """
    return (url := URL(candidate)).is_absolute_url and url.scheme in ("http", "https")


##############################################################################
def is_editable(location: HikeLocation) -> TypeIs[Path]:
    """Is the given location one that can be edited?

    Args:
        location: The location to test.

    Returns:
        `True` if the location can be edited, `False` if not.
    """
    return isinstance(location, Path)


### location_types.py ends here
