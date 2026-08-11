"""Read-only tools wrapping the Zotero Local API."""

from __future__ import annotations

from typing import Literal
from urllib.parse import unquote

from zotero_mcp.app import mcp
from zotero_mcp.client import client


def resolve_attachment_path(item_key: str, library: str = "user") -> str:
    """Get the local filesystem path of an attachment's file."""
    response = client.get(f"/items/{item_key}/file", library=library)
    if response.status_code != 302:
        raise ValueError(f"Item {item_key} has no local file attachment.")
    location = response.headers.get("Location", "")
    if not location.startswith("file://"):
        raise ValueError(f"Unexpected file location for {item_key}: {location!r}")
    return unquote(location.removeprefix("file://"))


@mcp.tool()
def list_groups() -> list[dict]:
    """List the group libraries available to the locally logged-in user."""
    groups = client.get_json("/groups")
    return [group["data"] for group in groups]


@mcp.tool()
def search_items(
    query: str,
    qmode: Literal["titleCreatorYear", "everything"] = "titleCreatorYear",
    item_type: str | None = None,
    tag: str | None = None,
    limit: int = 25,
    start: int = 0,
    library: str = "user",
) -> list[dict]:
    """Search the library by title/creator/year or full text.

    Args:
        query: Search text.
        qmode: "titleCreatorYear" (default) or "everything" for full-text search.
            "everything" uses Zotero's own local quicksearch, which can be looser
            than expected — e.g. it may surface unrelated items for a query with
            no real matches, or miss content that hasn't been indexed yet. Treat
            surprising "everything" results with suspicion rather than as a
            definitive answer.
        item_type: Optional item type filter (e.g. "book", "journalArticle").
        tag: Optional tag filter.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    params = {"q": query, "qmode": qmode, "limit": limit, "start": start}
    if item_type:
        params["itemType"] = item_type
    if tag:
        params["tag"] = tag
    items = client.get_json("/items", params, library=library)
    return [item["data"] for item in items]


@mcp.tool()
def get_item(
    item_key: str, include_bib: bool = False, style: str = "apa", library: str = "user"
) -> dict:
    """Get the full data for a single item.

    Args:
        item_key: The item's Zotero key.
        include_bib: If true, also include a formatted citation and bibliography entry.
        style: CSL style to use for the citation/bibliography when include_bib is true.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    params = {"include": "bib,citation", "style": style} if include_bib else None
    item = client.get_json(f"/items/{item_key}", params, library=library)
    result = dict(item["data"])
    if include_bib:
        result["bib"] = item.get("bib")
        result["citation"] = item.get("citation")
    return result


@mcp.tool()
def get_item_children(item_key: str, library: str = "user") -> list[dict]:
    """List the notes and attachments attached to an item.

    Args:
        item_key: The item's Zotero key.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    children = client.get_json(f"/items/{item_key}/children", library=library)
    return [child["data"] for child in children]


@mcp.tool()
def list_top_level_items(
    library: str = "user", limit: int = 25, start: int = 0
) -> list[dict]:
    """List top-level items in the library (excludes notes/attachments and trash).

    Args:
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
    """
    items = client.get_json(
        "/items/top", {"limit": limit, "start": start}, library=library
    )
    return [item["data"] for item in items]


@mcp.tool()
def list_trashed_items(
    library: str = "user", limit: int = 25, start: int = 0
) -> list[dict]:
    """List items in the trash.

    Args:
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
    """
    items = client.get_json(
        "/items/trash", {"limit": limit, "start": start}, library=library
    )
    return [item["data"] for item in items]


@mcp.tool()
def list_publications(limit: int = 25, start: int = 0) -> list[dict]:
    """List items in "My Publications". Personal-library only; no group equivalent.

    Args:
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
    """
    items = client.get_json("/publications/items", {"limit": limit, "start": start})
    return [item["data"] for item in items]


@mcp.tool()
def list_collections(
    top_level_only: bool = False,
    limit: int = 100,
    start: int = 0,
    library: str = "user",
) -> list[dict]:
    """List collections in the library.

    Args:
        top_level_only: If true, only return top-level collections (no subcollections).
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` collections.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    path = "/collections/top" if top_level_only else "/collections"
    collections = client.get_json(
        path, {"limit": limit, "start": start}, library=library
    )
    return [collection["data"] for collection in collections]


@mcp.tool()
def get_collection(collection_key: str, library: str = "user") -> dict:
    """Get the full data for a single collection.

    Args:
        collection_key: The collection's Zotero key.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    collection = client.get_json(f"/collections/{collection_key}", library=library)
    return collection["data"]


@mcp.tool()
def get_subcollections(
    collection_key: str, limit: int = 100, start: int = 0, library: str = "user"
) -> list[dict]:
    """List the direct subcollections of a collection.

    Args:
        collection_key: The parent collection's Zotero key.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` collections.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    collections = client.get_json(
        f"/collections/{collection_key}/collections",
        {"limit": limit, "start": start},
        library=library,
    )
    return [collection["data"] for collection in collections]


@mcp.tool()
def get_collection_items(
    collection_key: str,
    top_level_only: bool = False,
    limit: int = 25,
    start: int = 0,
    library: str = "user",
) -> list[dict]:
    """List items in a collection.

    Args:
        collection_key: The collection's Zotero key.
        top_level_only: If true, exclude child items (e.g. notes/attachments).
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` items.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    suffix = "/top" if top_level_only else ""
    items = client.get_json(
        f"/collections/{collection_key}/items{suffix}",
        {"limit": limit, "start": start},
        library=library,
    )
    return [item["data"] for item in items]


@mcp.tool()
def get_collection_tags(
    collection_key: str, limit: int = 100, start: int = 0, library: str = "user"
) -> list[str]:
    """List tags used on items in a collection.

    Args:
        collection_key: The collection's Zotero key.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` tags.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    tags = client.get_json(
        f"/collections/{collection_key}/tags",
        {"limit": limit, "start": start},
        library=library,
    )
    return [tag["tag"] for tag in tags]


@mcp.tool()
def list_tags(
    filter: str | None = None, limit: int = 100, start: int = 0, library: str = "user"
) -> list[str]:
    """List tags used in the library.

    Args:
        filter: Optional substring to filter tag names by.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` tags.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    params = {"limit": limit, "start": start}
    if filter:
        params["q"] = filter
    tags = client.get_json("/tags", params, library=library)
    return [tag["tag"] for tag in tags]


@mcp.tool()
def get_item_tags(
    item_key: str, limit: int = 100, start: int = 0, library: str = "user"
) -> list[str]:
    """List tags attached to a single item.

    Args:
        item_key: The item's Zotero key.
        limit: Maximum number of results (1-100).
        start: Offset into the results, for paging past the first `limit` tags.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    tags = client.get_json(
        f"/items/{item_key}/tags", {"limit": limit, "start": start}, library=library
    )
    return [tag["tag"] for tag in tags]


@mcp.tool()
def get_bibliography(
    item_keys: list[str],
    style: str = "apa",
    locale: str = "en-US",
    library: str = "user",
) -> str:
    """Generate a formatted bibliography for one or more items.

    Args:
        item_keys: Zotero keys of the items to include.
        style: CSL style name (e.g. "apa", "chicago-note-bibliography").
        locale: Locale for the bibliography (e.g. "en-US").
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
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
        library=library,
    )
    return response.text


@mcp.tool()
def get_attachment_file_path(item_key: str, library: str = "user") -> str:
    """Get the local filesystem path of an attachment's file.

    Args:
        item_key: The attachment item's Zotero key.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    return resolve_attachment_path(item_key, library=library)


@mcp.tool()
def get_item_types() -> list[dict]:
    """List the item types supported by Zotero (e.g. "book", "journalArticle")."""
    return client.get_json("/itemTypes", library=None)
