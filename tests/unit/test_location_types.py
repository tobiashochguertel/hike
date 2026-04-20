"""Tests for the location type testing code."""

##############################################################################
# Python imports.
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# httpx imports.
from httpx import URL, RequestError
from pytest import mark

##############################################################################
# Local imports.
from hike.data import can_be_negotiated_to_markdown, looks_urllike, maybe_markdown
from hike.data.config import Configuration
from hike.data.location_types import (
    markdown_content_types_from_configuration,
    markdown_extensions_from_configuration,
)
from hike.types import HikeLocation


##############################################################################
@mark.parametrize(
    "to_test, expected",
    (
        (Path("test.md"), True),
        (Path("test.markdown"), True),
        (Path("test.txt"), False),
        (URL("http://example.com/test.md"), True),
        (URL("http://example.com/test.markdown"), True),
        (URL("http://example.com/test.txt"), False),
        (URL("https://example.com/test.md"), True),
        (URL("https://example.com/test.markdown"), True),
        (URL("https://example.com/test.txt"), False),
    ),
)
def test_maybe_markdown(to_test: HikeLocation, expected: bool) -> None:
    """We should be able to make a good guess at what's a Markdown location."""
    assert maybe_markdown(to_test) is expected


##############################################################################
def test_maybe_markdown_accepts_explicit_extensions() -> None:
    """Explicit markdown extensions should override the default guesses."""
    configuration = Configuration(markdown_extensions=[".mdx"])

    assert maybe_markdown(
        Path("guide.mdx"),
        markdown_extensions_from_configuration(configuration),
    )
    assert not maybe_markdown(
        Path("guide.md"),
        markdown_extensions_from_configuration(configuration),
    )


##############################################################################
@mark.parametrize(
    "to_test, expected",
    (
        ("http://example.com/", True),
        ("https://example.com/", True),
        ("http://example", True),
        ("https://example", True),
        ("example.com/", False),
        ("example.com/", False),
        ("", False),
        ("http", False),
        ("https", False),
        ("http://", False),
        ("https://", False),
    ),
)
def test_looks_urllike(to_test: str, expected: bool) -> None:
    """We should be able to make a good guess at what's a URL."""
    assert looks_urllike(to_test) is expected


##############################################################################
class _FakeResponse:
    """Minimal fake HEAD response."""

    def __init__(self, *, content_type: str) -> None:
        self.headers = {"content-type": content_type}

    def raise_for_status(self) -> None:
        """Pretend the request succeeded."""


##############################################################################
class _FakeAsyncClient:
    """Minimal async client used for negotiation tests."""

    def __init__(self, response: _FakeResponse, calls: list[SimpleNamespace]) -> None:
        self._response = response
        self._calls = calls

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def head(
        self,
        location: HikeLocation,
        *,
        follow_redirects: bool,
        headers: dict[str, str],
    ) -> _FakeResponse:
        self._calls.append(
            SimpleNamespace(
                location=location,
                follow_redirects=follow_redirects,
                headers=headers,
            )
        )
        return self._response


##############################################################################
@pytest.mark.anyio
async def test_can_be_negotiated_to_markdown_uses_explicit_content_types(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negotiation should use the explicitly supplied content types."""
    calls: list[SimpleNamespace] = []
    configuration = Configuration(markdown_content_types=["text/markdown-custom"])
    monkeypatch.setattr(
        "hike.data.location_types.AsyncClient",
        lambda: _FakeAsyncClient(
            _FakeResponse(content_type="text/markdown-custom; charset=utf-8"),
            calls,
        ),
    )

    assert await can_be_negotiated_to_markdown(
        URL("https://example.com/guide"),
        markdown_content_types_from_configuration(configuration),
    )
    assert calls[0].headers["Accept"] == "text/markdown-custom,*/*;q=0.1"


##############################################################################
@pytest.mark.anyio
async def test_can_be_negotiated_to_markdown_handles_request_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negotiation should fail closed when the HTTP request fails."""

    class _FailingAsyncClient:
        async def __aenter__(self) -> _FailingAsyncClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def head(self, *_: object, **__: object) -> _FakeResponse:
            raise RequestError("boom")

    monkeypatch.setattr(
        "hike.data.location_types.AsyncClient",
        _FailingAsyncClient,
    )

    assert not await can_be_negotiated_to_markdown(URL("https://example.com/guide"))


### test_location_types.py ends here
