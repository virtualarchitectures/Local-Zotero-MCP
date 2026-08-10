import httpx

from zotero_mcp import library


def test_search_items_unwraps_data(monkeypatch, make_client, sample_item):
    def handler(request):
        assert request.url.path == "/api/users/0/items"
        assert request.url.params["q"] == "doe"
        assert request.url.params["start"] == "0"
        return httpx.Response(200, json=[sample_item])

    monkeypatch.setattr(library, "client", make_client(handler))
    results = library.search_items("doe")
    assert results == [sample_item["data"]]


def test_search_items_pagination(monkeypatch, make_client):
    def handler(request):
        assert request.url.params["limit"] == "10"
        assert request.url.params["start"] == "20"
        return httpx.Response(200, json=[])

    monkeypatch.setattr(library, "client", make_client(handler))
    library.search_items("doe", limit=10, start=20)


def test_get_item_with_bib(monkeypatch, make_client, sample_item):
    item_with_bib = dict(sample_item, bib="<div>bib html</div>", citation="(Doe)")

    def handler(request):
        assert request.url.path == "/api/users/0/items/ABCD1234"
        assert request.url.params["include"] == "bib,citation"
        return httpx.Response(200, json=item_with_bib)

    monkeypatch.setattr(library, "client", make_client(handler))
    result = library.get_item("ABCD1234", include_bib=True)
    assert result["title"] == "A Paper"
    assert result["bib"] == "<div>bib html</div>"
    assert result["citation"] == "(Doe)"


def test_list_tags(monkeypatch, make_client):
    def handler(request):
        assert request.url.path == "/api/users/0/tags"
        assert request.url.params["start"] == "0"
        return httpx.Response(200, json=[{"tag": "history"}, {"tag": "physics"}])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.list_tags() == ["history", "physics"]


def test_get_attachment_file_path(monkeypatch, make_client):
    def handler(request):
        return httpx.Response(
            302,
            headers={
                "Location": "file:///home/user/Zotero/storage/ABCD1234/"
                "Smith%20et%20al.%20-%20A%20Paper.pdf"
            },
        )

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.get_attachment_file_path("ABCD1234") == (
        "/home/user/Zotero/storage/ABCD1234/Smith et al. - A Paper.pdf"
    )
