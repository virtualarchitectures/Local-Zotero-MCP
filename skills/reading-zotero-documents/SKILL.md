---
name: reading-zotero-documents
description: Reads and analyzes the full text of PDF and EPUB attachments in the user's local Zotero library — pulling quotes, extracting evidence, summarizing, and comparing arguments or methodology across papers — via the zotero MCP server. Use when the user wants the actual content of a paper, not just its metadata or abstract — detailed analysis, specific evidence or quotes, or a comparison of multiple papers' arguments or methods.
---

# Reading Zotero documents

Requires the Zotero desktop app running locally with the Local API enabled (see the
`searching-zotero-library` skill for the setting). These tools read the resolved attachment file
directly with PyMuPDF — they work on any PDF/EPUB attachment, not just ones Zotero has indexed
for full-text search.

## Workflow

1. Find the attachment's item key: `get_item_children(item_key)` on the parent item, and pick
   the child with `itemType: "attachment"` and a PDF/EPUB `contentType`. If you already have an
   attachment key directly (e.g. from a prior search), skip this step.
2. Read it:
   ```
   read_document(item_key=attachment_key)
   read_document(item_key=attachment_key, remove_headers_footers=True)
   read_document(item_key=attachment_key, start_page=21, max_pages=20)   # page through a long doc
   ```
   `read_document` returns `{total_pages, start_page, end_page, text}`. Default `max_pages` is
   20 — call again with a higher `start_page` to keep reading.
3. To save a copy instead of reading inline, use `convert_document(item_key, output_path,
   output_format="txt"|"pdf")`. `remove_headers_footers` only applies to `output_format="txt"`;
   PDF output always preserves the original pages as-is.

`remove_headers_footers` detects lines that repeat near the top/bottom of most pages (running
titles, page numbers, journal watermarks) and strips them. Turn it on when doing anything that
reads across many pages at once — quoting, summarizing, comparing — since repeated headers
otherwise pollute the extracted text. Leave it off if the user wants a faithful, unedited dump of
a page's content.

## Deciding whether to read the full text at all

**Read the PDF when:** the user wants detailed analysis of arguments/evidence, specific
quotes or figures, a methodology comparison, or the abstract genuinely doesn't answer the
question.

**Stay with metadata (`search_items` / `get_item`) when:** the user wants a landscape overview,
is identifying themes across many papers, or is still in an early exploration phase. Reading full
text for 20+ papers back-to-back is usually the wrong call — narrow to the 3–5 most relevant
first.

**Never read or convert documents just to double-check a search result.** If `search_items`
(especially `qmode="everything"`) looks unreliable, that's a search-tool limitation to flag to
the user, not something to work around by converting a batch of PDFs to text and grepping them —
that burns tokens and writes files to disk for no benefit the user asked for. Ask before reading
or converting more than one or two documents purely for verification purposes.

## Deeper analysis patterns

For evidence extraction, comparative deep dives across multiple papers, and methodology
learning, see [reference/analysis-patterns.md](reference/analysis-patterns.md).
