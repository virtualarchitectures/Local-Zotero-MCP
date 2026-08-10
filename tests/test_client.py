import httpx
import pytest

from zotero_mcp.client import NOT_RUNNING_MESSAGE


def test_get_raises_friendly_message_on_connection_error(make_client):
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    client = make_client(handler)
    with pytest.raises(ValueError, match=NOT_RUNNING_MESSAGE):
        client.get("/items")


def test_get_raises_on_error_status(make_client):
    def handler(request):
        return httpx.Response(404, text="Not Found")

    client = make_client(handler)
    with pytest.raises(ValueError, match="Zotero returned 404 for /items/MISSING"):
        client.get("/items/MISSING")


def test_get_passes_through_redirect(make_client):
    def handler(request):
        return httpx.Response(302, headers={"Location": "file:///tmp/foo.pdf"})

    client = make_client(handler)
    response = client.get("/items/ABCD1234/file")
    assert response.status_code == 302
    assert response.headers["Location"] == "file:///tmp/foo.pdf"


def test_get_json_parses_body(make_client):
    def handler(request):
        return httpx.Response(200, json={"hello": "world"})

    client = make_client(handler)
    assert client.get_json("/ping") == {"hello": "world"}
