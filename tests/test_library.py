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


def test_search_items_group_library(monkeypatch, make_client):
    def handler(request):
        assert request.url.path == "/api/groups/999/items"
        return httpx.Response(200, json=[])

    monkeypatch.setattr(library, "client", make_client(handler))
    library.search_items("doe", library="999")


def test_list_groups(monkeypatch, make_client):
    def handler(request):
        assert request.url.path == "/api/users/0/groups"
        return httpx.Response(
            200, json=[{"data": {"id": 999, "name": "Reading Group"}}]
        )

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.list_groups() == [{"id": 999, "name": "Reading Group"}]


def test_list_top_level_items(monkeypatch, make_client, sample_item):
    def handler(request):
        assert request.url.path == "/api/users/0/items/top"
        return httpx.Response(200, json=[sample_item])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.list_top_level_items() == [sample_item["data"]]


def test_list_trashed_items(monkeypatch, make_client, sample_item):
    def handler(request):
        assert request.url.path == "/api/users/0/items/trash"
        return httpx.Response(200, json=[sample_item])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.list_trashed_items() == [sample_item["data"]]


def test_list_publications(monkeypatch, make_client, sample_item):
    def handler(request):
        assert request.url.path == "/api/users/0/publications/items"
        return httpx.Response(200, json=[sample_item])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.list_publications() == [sample_item["data"]]


def test_get_collection(monkeypatch, make_client):
    collection = {"key": "COLL123", "data": {"key": "COLL123", "name": "History"}}

    def handler(request):
        assert request.url.path == "/api/users/0/collections/COLL123"
        return httpx.Response(200, json=collection)

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.get_collection("COLL123") == collection["data"]


def test_get_subcollections(monkeypatch, make_client):
    collection = {"key": "SUB123", "data": {"key": "SUB123", "name": "Sub"}}

    def handler(request):
        assert request.url.path == "/api/users/0/collections/COLL123/collections"
        return httpx.Response(200, json=[collection])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.get_subcollections("COLL123") == [collection["data"]]


def test_get_collection_tags(monkeypatch, make_client):
    def handler(request):
        assert request.url.path == "/api/users/0/collections/COLL123/tags"
        return httpx.Response(200, json=[{"tag": "history"}])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.get_collection_tags("COLL123") == ["history"]


def test_get_item_tags(monkeypatch, make_client):
    def handler(request):
        assert request.url.path == "/api/users/0/items/ABCD1234/tags"
        return httpx.Response(200, json=[{"tag": "history"}])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.get_item_tags("ABCD1234") == ["history"]


def test_get_item_types(monkeypatch, make_client):
    def handler(request):
        assert request.url.path == "/api/itemTypes"
        return httpx.Response(200, json=[{"itemType": "book"}])

    monkeypatch.setattr(library, "client", make_client(handler))
    assert library.get_item_types() == [{"itemType": "book"}]


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
