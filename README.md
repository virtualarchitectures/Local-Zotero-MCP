# Local Zotero MCP

An [MCP](https://modelcontextprotocol.io/) server that gives an LLM read-only
access to your local [Zotero](https://www.zotero.org/) library via the
desktop app's [Local API](https://www.zotero.org/support/dev/web_api/v3/local_api).
It talks to Zotero over `http://127.0.0.1:23119`, so nothing leaves your
machine and no API keys are required.

## Requirements

- Zotero desktop app, running, with
  **Settings → Advanced → "Allow other applications on this computer to
  communicate with Zotero"** enabled.
- Python 3.10+

## Install

```bash
uv sync
```

or

```bash
pip install -e .
```

## Run

```bash
uv run zotero-mcp
```

This starts the server on stdio, for use with an MCP client such as Claude
Desktop or Claude Code.

### Claude Desktop config

```json
{
  "mcpServers": {
    "zotero": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/Local-Zotero-MCP", "zotero-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|---|---|
| `search_items` | Search the library by title/creator/year or full text |
| `get_item` | Get full data for an item, optionally with citation/bibliography |
| `get_item_children` | List an item's notes and attachments |
| `list_collections` | List collections |
| `get_collection_items` | List items in a collection |
| `list_tags` | List tags |
| `get_bibliography` | Generate a formatted bibliography for one or more items |
| `list_saved_searches` | List saved searches |
| `execute_saved_search` | Run a saved search and return matching items |
| `get_attachment_file_path` | Get the local file path of an attachment |

This server is read-only: it does not create, edit, or delete anything in
your library.

## Development

```bash
uv run pytest
```

Tests mock the Zotero HTTP responses, so a running Zotero instance isn't
required. To smoke-test against your real library:

```bash
uv run mcp dev zotero_mcp/server.py
```
