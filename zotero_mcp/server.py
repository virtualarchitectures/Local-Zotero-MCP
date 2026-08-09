"""MCP server exposing read-only access to the local Zotero library."""

from __future__ import annotations

from typing import Literal

from mcp.server import MCPServer

from zotero_mcp.client import client

mcp = MCPServer("zotero")


@mcp.tool()
def search_items(
    query: str,
    qmode: Literal["titleCreatorYear", "everything"] = "titleCreatorYear",
    item_type: str | None = None,
    tag: str | None = None,
    limit: int = 25,
    start: int = 0,
) -> list[dict]:
    """Search the library by title/creator/year or full text.

    Args:
        query: Search text.
        qmode: "titleCreatorYear" (default) or "everything" for a full-text search.
        item_type: Optional item type filter (e.g. "book", "journalArticle").
        tag: Optional tag filter.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
    """
    params = {"q": query, "qmode": qmode, "limit": limit, "start": start}
    if item_type:
        params["itemType"] = item_type
    if tag:
        params["tag"] = tag
    items = client.get_json("/items", params)
    return [item["data"] for item in items]


@mcp.tool()
def get_item(item_key: str, include_bib: bool = False, style: str = "apa") -> dict:
    """Get the full data for a single item.

    Args:
        item_key: The item's Zotero key.
        include_bib: If true, also include a formatted citation and bibliography entry.
        style: CSL style to use for the citation/bibliography when include_bib is true.
    """
    params = {"include": "bib,citation", "style": style} if include_bib else None
    item = client.get_json(f"/items/{item_key}", params)
    result = dict(item["data"])
    if include_bib:
        result["bib"] = item.get("bib")
        result["citation"] = item.get("citation")
    return result


@mcp.tool()
def get_item_children(item_key: str) -> list[dict]:
    """List the notes and attachments attached to an item."""
    children = client.get_json(f"/items/{item_key}/children")
    return [child["data"] for child in children]


@mcp.tool()
def list_collections(
    top_level_only: bool = False, limit: int = 100, start: int = 0
) -> list[dict]:
    """List collections in the library.

    Args:
        top_level_only: If true, only return top-level collections (no subcollections).
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` collections.
    """
    path = "/collections/top" if top_level_only else "/collections"
    collections = client.get_json(path, {"limit": limit, "start": start})
    return [collection["data"] for collection in collections]


@mcp.tool()
def get_collection_items(
    collection_key: str,
    top_level_only: bool = False,
    limit: int = 25,
    start: int = 0,
) -> list[dict]:
    """List items in a collection.

    Args:
        collection_key: The collection's Zotero key.
        top_level_only: If true, exclude child items (e.g. notes/attachments).
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
    """
    suffix = "/top" if top_level_only else ""
    items = client.get_json(
        f"/collections/{collection_key}/items{suffix}",
        {"limit": limit, "start": start},
    )
    return [item["data"] for item in items]


@mcp.tool()
def list_tags(filter: str | None = None, limit: int = 100, start: int = 0) -> list[str]:
    """List tags used in the library.

    Args:
        filter: Optional substring to filter tag names by.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` tags.
    """
    params = {"limit": limit, "start": start}
    if filter:
        params["q"] = filter
    tags = client.get_json("/tags", params)
    return [tag["tag"] for tag in tags]


@mcp.tool()
def get_bibliography(
    item_keys: list[str], style: str = "apa", locale: str = "en-US"
) -> str:
    """Generate a formatted bibliography for one or more items.

    Args:
        item_keys: Zotero keys of the items to include.
        style: CSL style name (e.g. "apa", "chicago-note-bibliography").
        locale: Locale for the bibliography (e.g. "en-US").
    """
    response = client.get(
        "/items",
        {
            "itemKey": ",".join(item_keys),
            "format": "bib",
            "style": style,
            "locale": locale,
            "linkwrap": 0,
        },
    )
    return response.text


@mcp.tool()
def list_saved_searches(limit: int = 100, start: int = 0) -> list[dict]:
    """List saved searches defined in the library.

    Args:
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` searches.
    """
    searches = client.get_json("/searches", {"limit": limit, "start": start})
    return [search["data"] for search in searches]


@mcp.tool()
def execute_saved_search(search_key: str, limit: int = 25, start: int = 0) -> list[dict]:
    """Run a saved search and return the matching items.

    Args:
        search_key: The saved search's Zotero key.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
    """
    items = client.get_json(
        f"/searches/{search_key}/items", {"limit": limit, "start": start}
    )
    return [item["data"] for item in items]


@mcp.tool()
def get_attachment_file_path(item_key: str) -> str:
    """Get the local filesystem path of an attachment's file.

    Args:
        item_key: The attachment item's Zotero key.
    """
    response = client.get(f"/items/{item_key}/file")
    if response.status_code != 302:
        raise ValueError(f"Item {item_key} has no local file attachment.")
    location = response.headers.get("Location", "")
    if not location.startswith("file://"):
        raise ValueError(f"Unexpected file location for {item_key}: {location!r}")
    return location.removeprefix("file://")
