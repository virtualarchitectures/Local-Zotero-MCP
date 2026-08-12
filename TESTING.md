# Manual testing: Claude Plugin skills

A checklist for manually exercising the four Zotero skills against a real Zotero library. This
complements `uv run pytest` (which mocks the Zotero HTTP layer and never touches the plugin or
skills) — run this whenever `skills/`, `.mcp.json`, or `.claude-plugin/plugin.json` change.

Run this from a **separate Claude Code session** than the one used to develop the plugin, so
you're testing a clean load rather than a session that already has development context.

## Setup

1. Zotero desktop app running, with **Settings → Advanced → "Allow other applications on this
   computer to communicate with Zotero"** enabled.
2. Optional but recommended: add a line like `Citation Count: 342 (Crossref)` to one test item's
   **Extra** field in Zotero. Without this, the citation-ranking logic in
   `analyzing-zotero-research` can only be exercised on its "not recorded" path.
3. Launch the plugin from the repo directory:
   ```bash
   claude --plugin-dir /path/to/Local-Zotero-MCP
   ```
   If you already have a standalone `zotero` MCP server configured (e.g. from following the
   README's Claude Desktop setup), Claude Code will skip the plugin's copy in favor of it since
   they run the identical command — this is expected and doesn't affect anything below. Run
   `claude mcp list` to check, or `claude mcp remove zotero` first if you want to confirm the
   plugin's own `.mcp.json` loads.
4. Sanity-check the load:
   - `/plugin` → `local-zotero-mcp` listed and enabled, no errors in the Errors tab.
   - `/context` → all four skills listed under Custom Skills with sensible descriptions, and the
     `zotero` MCP server shows its tools connected.

## 1. `searching-zotero-library`

- "Search my Zotero for papers about `<a topic you have several items on>`" — calls
  `search_items`; check the result formatting matches result count (full detail for ≤10,
  condensed for 11–20, overview for 21+).
- "Find everything in my Zotero mentioning `<phrase likely only in body text, not title>`" —
  should use `qmode="everything"`.
- "What collections do I have?" / "What tags do I use?" / "What's in my Zotero trash?" — should
  route to the browsing reference (`list_collections`, `list_tags`, `list_trashed_items`).
- After a results dump, check it proactively suggests a next step (theme breakdown, narrower
  search, etc.) rather than just stopping.

## 2. `reading-zotero-documents`

- "Read the PDF for `<item with an attachment>` and summarize it" — chains `get_item_children` →
  `get_attachment_file_path` (if needed) → `read_document`.
- "That paper's long, keep going from where you left off" — calls `read_document` again with a
  higher `start_page`.
- "Save me a clean text copy of that PDF with running headers stripped" — calls
  `convert_document(output_format="txt", remove_headers_footers=True)`.
- "Compare the methodology sections of `<paper A>`, `<paper B>`, and `<paper C>`" — reads all
  three and produces a comparison table (Comparative Deep Dive pattern).

## 3. `generating-zotero-bibliographies`

- "Give me an APA citation for `<item>`."
- "Generate a Chicago-style bibliography for `<item A>`, `<item B>`, `<item C>`."
- "Build me a cited reading list for everything in my `<collection name>` collection" — gathers
  keys via `get_collection_items` then calls `get_bibliography` once with all of them, not once
  per item.

## 4. `analyzing-zotero-research`

- "What are the main themes in my library on `<topic>`?" — thematic clustering.
- "Is my coverage of `<topic>` missing anything?" — gap analysis. Watch the phrasing: should say
  things like "thin in your library," never "missing from the field."
- "How has my reading on `<topic>` evolved over time?" — trajectory analysis, sorted by date.
- "I have too many results on `<topic>` — give me a prioritized reading list" — tiered
  essential/important/supplementary output.
- "What are the most-cited papers I have on `<topic>`?" — reads `extra` on each item, tiers the
  ones with a citation count correctly, and lists items with no count as "not recorded" (not
  omitted, not treated as zero).
- Ask directly for the citation count of an item you know has **no** `extra` data — should say
  unknown/not recorded, never invent a number.

## 5. Guardrail regression checks

These correspond to specific failures caught during earlier testing rounds — always re-run them
after touching a skill's `SKILL.md` or reference files.

**No silent web search as a Semantic Scholar substitute.** Ask:
> "Are there important papers on `<topic>` I'm missing that aren't in my library at all?"

Expected: `analyzing-zotero-research` states plainly that it only sees your Zotero library and
has no external index to check against, and does **not** call `WebSearch`/`WebFetch`. It should
ask before doing an open-web check, not do one automatically. (Previously, the skill worked
around the "no Semantic Scholar" constraint by launching several `WebSearch` calls to verify
field papers — the constraint only covered the *claim*, not the *action*.)

**No silent document conversion as a search-verification workaround.** Ask something with an
unlikely/nonsense full-text phrase, e.g.:
> "Find everything in my Zotero mentioning `<a phrase you're confident matches nothing>`"

Expected: if `qmode="everything"` returns implausible results (unrelated items, or roughly the
whole library), the skill says the full-text search may be unreliable for that query and suggests
narrowing it — it does **not** silently call `convert_document`/`read_document` across candidate
PDFs to grep them by hand. (Previously, the skill did exactly that: converted several PDFs to
text to manually verify a `qmode="everything"` result set it didn't trust.)

**Tool-call audit.** Across all sections above, check the tool-call log for any calls outside the
`zotero` MCP server (`WebSearch`, `WebFetch`, arbitrary `Bash`/file-write activity beyond an
explicitly requested `convert_document` save). Everything should stay confined to the local
`zotero` MCP tools unless you explicitly asked for something else.

## 6. Packaging sanity

Not plugin-specific, but worth re-checking after a version bump or dependency change:

```bash
uv run pytest
uv build && unzip -l dist/*.whl && tar tzf dist/*.tar.gz   # confirm skills/, .claude-plugin/,
                                                             # and .mcp.json are NOT included
claude plugin validate . --strict
```

## Reporting a failure

Note the exact prompt used and what happened (which tools were called, in what order, and the
resulting text). That's what's needed to patch the relevant `SKILL.md` or reference file.
