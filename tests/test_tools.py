import httpx
import pytest

from zotero_mcp import server
from zotero_mcp.client import BASE_URL, ZoteroClient

ITEM = {
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


def make_client(handler) -> ZoteroClient:
    zc = ZoteroClient()
    zc._http = httpx.Client(
        base_url=BASE_URL,
        transport=httpx.MockTransport(handler),
        follow_redirects=False,
    )
    return zc


def test_search_items_unwraps_data(monkeypatch):
    def handler(request):
        assert request.url.path == "/api/users/0/items"
        assert request.url.params["q"] == "doe"
        assert request.url.params["start"] == "0"
        return httpx.Response(200, json=[ITEM])

    monkeypatch.setattr(server, "client", make_client(handler))
    results = server.search_items("doe")
    assert results == [ITEM["data"]]


def test_search_items_pagination(monkeypatch):
    def handler(request):
        assert request.url.params["limit"] == "10"
        assert request.url.params["start"] == "20"
        return httpx.Response(200, json=[])

    monkeypatch.setattr(server, "client", make_client(handler))
    server.search_items("doe", limit=10, start=20)


def test_get_item_with_bib(monkeypatch):
    item_with_bib = dict(ITEM, bib="<div>bib html</div>", citation="(Doe)")

    def handler(request):
        assert request.url.path == "/api/users/0/items/ABCD1234"
        assert request.url.params["include"] == "bib,citation"
        return httpx.Response(200, json=item_with_bib)

    monkeypatch.setattr(server, "client", make_client(handler))
    result = server.get_item("ABCD1234", include_bib=True)
    assert result["title"] == "A Paper"
    assert result["bib"] == "<div>bib html</div>"
    assert result["citation"] == "(Doe)"


def test_list_tags(monkeypatch):
    def handler(request):
        assert request.url.path == "/api/users/0/tags"
        assert request.url.params["start"] == "0"
        return httpx.Response(200, json=[{"tag": "history"}, {"tag": "physics"}])

    monkeypatch.setattr(server, "client", make_client(handler))
    assert server.list_tags() == ["history", "physics"]


def test_get_attachment_file_path(monkeypatch):
    def handler(request):
        return httpx.Response(
            302, headers={"Location": "file:///home/user/Zotero/paper.pdf"}
        )

    monkeypatch.setattr(server, "client", make_client(handler))
    assert server.get_attachment_file_path("ABCD1234") == "/home/user/Zotero/paper.pdf"


def test_connection_error_raises_friendly_message(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    monkeypatch.setattr(server, "client", make_client(handler))
    with pytest.raises(ValueError, match="Could not reach Zotero"):
        server.search_items("doe")
