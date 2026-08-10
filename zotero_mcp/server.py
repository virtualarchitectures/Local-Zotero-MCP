"""Entry point: assembles the MCP server from its tool modules."""

from zotero_mcp.app import mcp
from zotero_mcp import documents, library  # noqa: F401  (imported to register tools)

__all__ = ["mcp"]
