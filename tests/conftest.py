"""Shared fixtures for zotero_mcp tests."""

import httpx
import pytest

from zotero_mcp.client import BASE_URL, ZoteroClient

SAMPLE_ITEM = {
    "key": "ABCD1234",
    "version": 42,
    "library": {"type": "user", "id": 0},
    "links": {},
    "meta": {},
    "data": {
        "key": "ABCD1234",
        "version": 42,
        "itemType": "journalArticle",
        "title": "A Paper",
        "creators": [{"creatorType": "author", "name": "J. Doe"}],
    },
}


def _make_client(handler) -> ZoteroClient:
    zc = ZoteroClient()
    zc._http = httpx.Client(
        base_url=BASE_URL,
        transport=httpx.MockTransport(handler),
        follow_redirects=False,
    )
    return zc


@pytest.fixture
def make_client():
    """Factory fixture: build a ZoteroClient backed by a mock transport handler."""
    return _make_client


@pytest.fixture
def sample_item():
    return SAMPLE_ITEM
