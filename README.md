# Local Zotero MCP

An [MCP](https://modelcontextprotocol.io/) server that gives an LLM read-only
access to your local [Zotero](https://www.zotero.org/) library via the
desktop app's [Local API](https://www.zotero.org/support/dev/web_api/v3/local_api).
It talks to Zotero over `http://127.0.0.1:23119`, so nothing leaves your
machine and no API keys are required.

## Requirements

- Zotero desktop app, running, with
  **Settings > Advanced > "Allow other applications on this computer to
  communicate with Zotero"** enabled.
- [uv](https://docs.astral.sh/uv/) installed.

## Quickstart

No cloning or installing required — `uvx` fetches the published package
from PyPI and runs it. Add this to your Claude Desktop config
(`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "zotero": {
      "command": "uvx",
      "args": ["--from", "local-zotero-mcp", "zotero-mcp"]
    }
  }
}
```

Restart Claude Desktop and the Zotero tools should be available.
`uvx` caches the environment after the first run, so subsequent launches are
fast; add `--refresh` to `args` if you want to force-pull the latest version.

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
| `read_document` | Read the text content of a PDF or EPUB attachment |
| `convert_document` | Convert a PDF or EPUB attachment to TXT or PDF and save it to a location you specify |

## Local development

Clone the repo and install it locally:

```bash
uv sync
```

Run it directly from the checkout:

```bash
uv run zotero-mcp
```

Point Claude Desktop at your local checkout instead of GitHub with:

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

Run the tests:

```bash
uv run pytest
```

Tests mock the Zotero HTTP responses, so a running Zotero instance isn't
required. To smoke-test against your own Zotero library:

```bash
uv run mcp dev zotero_mcp/server.py
```
