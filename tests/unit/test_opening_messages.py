"""Tests for opening-related message helpers."""

##############################################################################
# Python imports.
from __future__ import annotations

from types import SimpleNamespace

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# httpx imports.
from httpx import HTTPStatusError, Request, RequestError, Response

##############################################################################
# Local imports.
from hike.messages.opening import OpenFromForge


##############################################################################
class _FakeResponse:
    """Minimal fake response object."""

    def __init__(self, *, should_raise: bool = False) -> None:
        self._should_raise = should_raise

    def raise_for_status(self) -> None:
        """Raise when configured to simulate a missing branch."""
        if self._should_raise:
            request = Request("HEAD", "https://example.com/README.md")
            response = Response(404, request=request)
            raise HTTPStatusError("missing", request=request, response=response)


##############################################################################
class _FakeAsyncClient:
    """Minimal async client for forge URL tests."""

    def __init__(
        self, responses: list[_FakeResponse], calls: list[SimpleNamespace]
    ) -> None:
        self._responses = responses
        self._calls = calls

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def head(
        self,
        url: str,
        *,
        follow_redirects: bool,
        headers: dict[str, str],
    ) -> _FakeResponse:
        self._calls.append(
            SimpleNamespace(
                url=url,
                follow_redirects=follow_redirects,
                headers=headers,
            )
        )
        return self._responses.pop(0)


##############################################################################
@pytest.mark.anyio
async def test_open_from_forge_tries_supplied_candidate_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Forge URL lookup should use the candidate branches supplied by the caller."""
    calls: list[SimpleNamespace] = []
    monkeypatch.setattr(
        "hike.messages.opening.AsyncClient",
        lambda: _FakeAsyncClient(
            [_FakeResponse(should_raise=True), _FakeResponse()],
            calls,
        ),
    )
    message = OpenFromForge(
        forge="GitHub",
        raw_url_format=(
            "https://raw.githubusercontent.com/{owner}/{repository}/{branch}/{file}"
        ),
        owner="textualize",
        repository="textual",
    )

    url = await message.url(("trunk", "main"))

    assert (
        str(url)
        == "https://raw.githubusercontent.com/textualize/textual/main/README.md"
    )
    assert [call.url for call in calls] == [
        "https://raw.githubusercontent.com/textualize/textual/trunk/README.md",
        "https://raw.githubusercontent.com/textualize/textual/main/README.md",
    ]


##############################################################################
@pytest.mark.anyio
async def test_open_from_forge_prefers_explicit_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit branch on the message should override candidate branches."""
    calls: list[SimpleNamespace] = []
    monkeypatch.setattr(
        "hike.messages.opening.AsyncClient",
        lambda: _FakeAsyncClient([_FakeResponse()], calls),
    )
    message = OpenFromForge(
        forge="GitHub",
        raw_url_format=(
            "https://raw.githubusercontent.com/{owner}/{repository}/{branch}/{file}"
        ),
        owner="textualize",
        repository="textual",
        branch="release",
        filename="guide.md",
    )

    url = await message.url(("main", "master"))

    assert (
        str(url)
        == "https://raw.githubusercontent.com/textualize/textual/release/guide.md"
    )
    assert [call.url for call in calls] == [
        "https://raw.githubusercontent.com/textualize/textual/release/guide.md"
    ]


##############################################################################
@pytest.mark.anyio
async def test_open_from_forge_stops_on_request_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transport failures should abort forge URL lookup."""

    class _FailingAsyncClient:
        async def __aenter__(self) -> _FailingAsyncClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def head(self, *_: object, **__: object) -> _FakeResponse:
            raise RequestError("boom")

    monkeypatch.setattr(
        "hike.messages.opening.AsyncClient",
        _FailingAsyncClient,
    )
    message = OpenFromForge(
        forge="GitHub",
        raw_url_format=(
            "https://raw.githubusercontent.com/{owner}/{repository}/{branch}/{file}"
        ),
        owner="textualize",
        repository="textual",
    )

    assert await message.url(("main", "master")) is None


### test_opening_messages.py ends here
