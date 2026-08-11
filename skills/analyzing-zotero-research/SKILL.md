---
name: analyzing-zotero-research
description: Performs higher-level research analysis over a user's local Zotero library — thematic clustering, coverage-gap analysis, research-trajectory tracing, and reading-list prioritization — via the zotero MCP server. Use when the user wants to understand the landscape of a topic in their own library, find what's thin or missing in their reading, trace how their reading on a topic evolved over time, or prioritize what to read next.
---

# Analyzing Zotero research

Requires the Zotero desktop app running locally with the Local API enabled (see the
`searching-zotero-library` skill for the setting). This skill works entirely from what's already
in the user's Zotero library — there is no external literature index (no Semantic Scholar or
citation-graph integration) to cross-reference against, so never claim to find papers "missing
from the field"; only ever "missing from your library" or "thin in your library," and say
plainly when you can't tell the difference.

Start every analysis with a `search_items` or `get_collection_items` call to gather the working
set (see `searching-zotero-library`), then apply one of the patterns in
[reference/patterns.md](reference/patterns.md):

- **Thematic clustering** — group 10+ papers into themes with representative examples.
- **Gap analysis** — map what's well-covered vs. sparse (time periods, methods, regions,
  perspectives) within the library.
- **Trajectory analysis** — sort by date and trace how the user's reading on a topic evolved.
- **Reading-list prioritization** — tier a large result set into essential/important/
  supplementary reading.

## Ranking signals

There's still no live external citation index (no Semantic Scholar or citation-graph API), but
some items carry a citation count as static text already stored in the library, in the item's
`extra` field — usually written there by a Zotero citation-count plugin, or added manually.
`extra` is a plain field returned on every item by `search_items`, `get_item`, and
`get_collection_items`; no extra tool call is needed, just read it.

Use, in order of reliability:
1. **Citation count in `extra`**, when present — look for a line like `Citation Count: 123`,
   `Citations: 45`, or `Cited by: 200`, optionally with a source in parentheses (e.g.
   `(Crossref)`, `(Google Scholar)`). Coverage is partial — most items won't have one. Treat a
   missing count as *unknown*, not zero: don't rank an uncounted item last by default, fall
   through to the signals below for it instead. If different items in the same set cite
   different sources, say so rather than treating the numbers as directly comparable.
2. **Tags** — a user's own conventions (e.g. `"seminal"`, `"key"`, `"to-read"`) are a strong
   signal when present. Check with `list_tags()` / `get_item_tags()` before assuming a convention
   exists — don't invent one.
3. **Recency** — useful for trajectory analysis and for flagging outdated coverage, not for
   importance on its own.
4. **Collection membership** — items a user has deliberately organized into a named collection
   are implicitly curated; items only in "My Publications" or scattered top-level items are not.
5. **Completeness** — items with an attached, readable PDF are more useful for deep analysis than
   metadata-only entries; note this as a practical constraint, not a quality signal.

Never fabricate a citation count, impact score, or "seminal work" ranking for an item that has
none recorded in `extra` — report it as uncounted and fall back to the signals above instead.
