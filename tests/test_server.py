import asyncio

from zotero_mcp.server import mcp

EXPECTED_TOOLS = {
    "search_items",
    "get_item",
    "get_item_children",
    "list_collections",
    "get_collection_items",
    "list_tags",
    "get_bibliography",
    "list_saved_searches",
    "execute_saved_search",
    "get_attachment_file_path",
    "read_document",
    "convert_document",
}


def test_server_registers_all_tool_modules():
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert EXPECTED_TOOLS <= names
