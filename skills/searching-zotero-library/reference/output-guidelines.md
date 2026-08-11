# Presenting search results and suggesting next steps

## Contents
- Formatting by result count
- Proactive analysis
- Common usage patterns

## Formatting by result count

**1–10 results — full details:** title (author, year), publication venue, abstract (first 2–3
sentences if long), DOI/URL, local file path if a PDF is attached. If the search wasn't
`qmode="everything"`, mention that a full-text search may surface more.

**11–20 results — condensed:** title, authors, year, publication venue, local file path.

**21+ results — overview:** total count, group by theme/type if there's an obvious grouping,
show the 5–10 most relevant, offer to narrow or show more.

**Always include:**
1. The total result count up front ("Found 12 journal articles").
2. Local file paths when a PDF is attached — the user can open it directly.
3. An offer to refine the search if results look too broad or too narrow.

Adapt to context — these are sensible defaults, not rigid rules.

## Proactive analysis

After presenting results, act like a diligent research assistant rather than a bare command
executor — but don't be pushy or overeager, and let the user set the level of assistance they
want.

**Always check for:**
- Themes or clusters in the results
- Temporal patterns (date ranges, gaps)
- Coverage gaps (methodologies, perspectives, missing expected authors)

**Suggest next steps based on what you notice**, e.g.:
- "These 15 papers cluster into 3 approaches: [A], [B], [C]. Want a breakdown of each?"
- "Most papers are 2020–2023. Want me to search for earlier foundational work?"
- "Only 4 of 12 papers have PDFs attached — want me to identify which are missing?"
- "Got 47 results — want to filter by item type, date, or tag?"
- "Only 2 results — try broader terms, drop filters, or search with `qmode='everything'`?"

For deeper analysis — thematic clustering, gap analysis, tracing how a topic evolved over time,
or building a prioritized reading list — hand off to the `analyzing-zotero-research` skill. Note
that all of this is scoped to the user's own library; there's no external literature index to
cross-reference against, so phrase gap analysis as "what's thin in your library" rather than
"what's missing from the field."

## Common usage patterns

**Basic exploratory search:**
```
User: "Search my Zotero for papers about ocean acidification"
1. search_items(query="ocean acidification", item_type="journalArticle")
2. Present results
3. "Found 12 papers. 3 focus on coral reefs, 8 on broader marine ecosystems, 1 on economic
   impacts. Most are 2018–2023. Want a breakdown of each cluster?"
```

**Full-text search surfacing a gap:**
```
User: "Find everything mentioning 'adaptation strategies'"
1. search_items(query="adaptation strategies", qmode="everything")
2. Present results
3. "Found 23 papers, but all from developed-country contexts. Want to check whether you have
   anything from developing-world contexts, or is that a genuine gap?"
```

**Advanced workflow handoff:**
```
User: "What do I have on neural networks? I need to understand the landscape."
1. search_items(query="neural networks")
2. Present results with initial pattern notes
3. "Found 18 papers. Want a thematic clustering, a trajectory analysis, or a prioritized
   reading list? (See the analyzing-zotero-research skill for these.)"
```
