import asyncio

from zotero_mcp.server import mcp

EXPECTED_TOOLS = {
    "list_groups",
    "search_items",
    "get_item",
    "get_item_children",
    "list_top_level_items",
    "list_trashed_items",
    "list_publications",
    "list_collections",
    "get_collection",
    "get_subcollections",
    "get_collection_items",
    "get_collection_tags",
    "list_tags",
    "get_item_tags",
    "get_bibliography",
    "get_attachment_file_path",
    "get_item_types",
    "read_document",
    "convert_document",
}


def test_server_registers_all_tool_modules():
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert EXPECTED_TOOLS <= names
