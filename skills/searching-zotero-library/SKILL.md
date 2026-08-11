---
name: searching-zotero-library
description: Searches and browses the user's local Zotero library — items, collections, tags, groups, trash, and "My Publications" — via the zotero MCP server. Use when the user asks to search their Zotero library, find papers or references on a topic, look up a specific item, or browse their collections or tags.
---

# Searching the Zotero library

Requires the Zotero desktop app running locally with **Settings > Advanced > "Allow other
applications on this computer to communicate with Zotero"** enabled. All tools below take an
optional `library` argument — `"user"` (default) for the personal library, or a group ID (from
`list_groups`) for a synced group library.

## Quick start

Use `search_items` for most queries:

```
search_items(query="climate change")
search_items(query="ocean acidification", qmode="everything")   # full-text search
search_items(query="adaptation", item_type="journalArticle")
search_items(query="review", tag="to-read")
search_items(query="climate", limit=20, start=20)                # page 2
```

| Param | Notes |
|---|---|
| `qmode` | `"titleCreatorYear"` (default) or `"everything"` for full-text search of indexed PDFs |
| `item_type` | e.g. `"journalArticle"`, `"book"`, `"bookSection"`, `"conferencePaper"`, `"report"`, `"thesis"`, `"preprint"` — full list via `get_item_types` |
| `tag` | Exact tag match; see `list_tags` to discover tag names |
| `limit` / `start` | Page through results 1–100 at a time |

If a `qmode="titleCreatorYear"` search comes up short or empty, retry with
`qmode="everything"` before telling the user there are no results — it only searches
metadata, not full text.

## Drilling into a result

- `get_item(item_key)` — full item data. Pass `include_bib=True` for a formatted citation.
- `get_item_children(item_key)` — an item's notes and attachments (find attachment keys here
  before reading a PDF — see the `reading-zotero-documents` skill).
- `get_attachment_file_path(item_key)` — local filesystem path of an attachment.

## Browsing instead of searching

For collections, subcollections, tags, groups, trash, and "My Publications", see
[reference/browsing.md](reference/browsing.md).

## Presenting results and suggesting next steps

See [reference/output-guidelines.md](reference/output-guidelines.md) for how to format result
counts of different sizes and what proactive follow-ups to offer (thematic clustering, gap
analysis, etc. — see the `analyzing-zotero-research` skill).
