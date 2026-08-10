from mcp.server import MCPServer

from zotero_mcp.app import mcp


def test_mcp_is_a_named_server():
    assert isinstance(mcp, MCPServer)
    assert mcp.name == "zotero"
