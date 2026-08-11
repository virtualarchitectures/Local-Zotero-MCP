---
name: generating-zotero-bibliographies
description: Generates formatted citations and bibliographies for items in the user's local Zotero library, and builds reading lists with proper references, via the zotero MCP server. Use when the user asks for a citation, works-cited list, bibliography, or formatted reading list in a specific citation style.
---

# Generating Zotero bibliographies

Requires the Zotero desktop app running locally with the Local API enabled (see the
`searching-zotero-library` skill for the setting).

## Single or batch citations

```
get_bibliography(item_keys=["ABC123"])
get_bibliography(item_keys=["ABC123", "DEF456", "GHI789"], style="chicago-note-bibliography")
get_bibliography(item_keys=[...], style="apa", locale="en-US")
```

`get_bibliography` returns pre-formatted HTML/text for the given items — pass every item key you
need at once rather than calling it once per item; it's a single request either way. Find item
keys via the `searching-zotero-library` skill first (`search_items`, `get_collection_items`,
etc.).

For a single item, `get_item(item_key, include_bib=True, style=...)` also returns a citation and
bibliography entry alongside the item's full data — use that instead when you already need the
item's other fields too, to avoid a second call.

## Citation styles

`style` accepts any CSL style name installed in the user's Zotero (e.g. `"apa"`, `"chicago-note-
bibliography"`, `"mla"`, `"harvard1"`, `"vancouver"`). If a style name is rejected, ask the user
which style they use, or fall back to `"apa"` and say so — don't guess silently.

## Building a reading list

To produce a reading list rather than a flat bibliography: gather the item keys for the papers in
scope (a search result set or a collection via `get_collection_items`), then call
`get_bibliography` once with all of them. If the user wants the list grouped or ordered (by
theme, priority, or chronology), do that grouping yourself before presenting — `get_bibliography`
returns entries in the order the keys were given, so pass them in the order you want.
