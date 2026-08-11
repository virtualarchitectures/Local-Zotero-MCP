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

No cloning or installing required - `uvx` fetches the published package
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

Every library-scoped tool takes an optional `library` argument - `"user"`
(default) for your personal library, or a group ID to read a group library
synced locally. Use `list_groups` to find group IDs.

| Tool | Description |
|---|---|
| `list_groups` | List group libraries available to the local Zotero install |
| `search_items` | Search the library by title/creator/year or full text |
| `get_item` | Get full data for an item, optionally with citation/bibliography |
| `get_item_children` | List an item's notes and attachments |
| `list_top_level_items` | List top-level items in the library |
| `list_trashed_items` | List items in the trash |
| `list_publications` | List items in "My Publications" |
| `list_collections` | List collections |
| `get_collection` | Get full data for a single collection |
| `get_subcollections` | List the direct subcollections of a collection |
| `get_collection_items` | List items in a collection |
| `get_collection_tags` | List tags used on items in a collection |
| `list_tags` | List tags |
| `get_item_tags` | List tags attached to a single item |
| `get_bibliography` | Generate a formatted bibliography for one or more items |
| `get_attachment_file_path` | Get the local file path of an attachment |
| `get_item_types` | List item types supported by Zotero |

The two tools below have no equivalent in the Zotero Web API - they read the
attachment file resolved by `get_attachment_file_path` and process it locally
with [PyMuPDF](https://pymupdf.readthedocs.io/). Both accept
`remove_headers_footers`: when true, lines that repeat near the top/bottom of
most pages (running titles, page numbers, etc.) are detected and stripped
from the returned/saved text. For `convert_document` this only applies to
`output_format="txt"` - PDF output preserves the original pages as-is.

| Tool | Description |
|---|---|
| `read_document` | Read the text content of a PDF or EPUB attachment |
| `convert_document` | Convert a PDF or EPUB attachment to TXT or PDF and save it to a location you specify |

## Claude Plugin

This repo also ships as a [Claude Code plugin](https://code.claude.com/docs/en/plugins) bundling
four Agent Skills for Zotero-based research, on top of the same MCP tools listed above:

| Skill | Covers |
|---|---|
| `searching-zotero-library` | Searching and browsing items, collections, tags, groups |
| `reading-zotero-documents` | Full-text PDF/EPUB reading, quoting, and comparison |
| `generating-zotero-bibliographies` | Formatted citations and reading lists |
| `analyzing-zotero-research` | Thematic clustering, gap analysis, trajectory tracing, reading-list prioritization |

The plugin's `.mcp.json` runs the server the same way as the Quickstart above (`uvx --from
local-zotero-mcp zotero-mcp`), so it always tracks the published PyPI package.

To try it locally, clone the repo and run:

```bash
claude --plugin-dir /path/to/Local-Zotero-MCP
```

Then invoke a skill directly, e.g. `/local-zotero-mcp:searching-zotero-library`, or just ask
Claude a research question about your library and let it pick the right skill.

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
