# Research analysis patterns

## Contents
- Thematic clustering
- Gap analysis
- Research trajectory analysis
- Reading-list prioritization
- Finding highly-cited items
- Tag-based discovery

All patterns below operate on a working set gathered with `search_items` or
`get_collection_items` — none of them reach outside the user's own Zotero library.

## Thematic clustering

**When:** the user has 10+ papers and wants to understand the landscape.

1. Gather results, including abstracts (`search_items` returns `abstractNote`, or use
   `get_item(item_key)` per item if the search result omitted it).
2. Read titles/abstracts and identify recurring themes, theoretical approaches, or methods.
3. Group papers by theme with counts.
4. Describe each cluster with representative papers and note relationships between clusters.

```
Found 3 main themes in 18 papers:

Theme 1: Adaptation through policy (7 papers)
- Focus: top-down institutional approaches
- Key papers: [Author1 2021], [Author2 2020]

Theme 2: Community-based adaptation (8 papers)
- Focus: bottom-up local initiatives
- Key papers: [Author3 2022], [Author4 2019]

Theme 3: Techno-managerial solutions (3 papers)
- Focus: engineering and infrastructure
- Key papers: [Author5 2023]
```

## Gap analysis

**When:** the user wants to know what's thin or missing in their own library on a topic.

1. Map what's well-covered: themes, methods, time periods, regions (from titles/abstracts).
2. Identify sparse areas within that same set.
3. Check for methodological imbalance (e.g. all-quantitative, all-qualitative).
4. Note missing perspectives, populations, or geographies visible from the data you have.
5. Suggest targeted searches to fill each gap — e.g. "you have nothing from 2015–2018, want me
   to search that period specifically?"

Frame every finding as a property of the user's library, not of the field: "you have 15 papers on
X, all from 2018 onward" rather than "the field is missing pre-2018 work." If the user wants to
know what's missing from the field itself, say that requires an external literature index this
MCP doesn't have access to.

## Research trajectory analysis

**When:** the user wants to understand how their reading (or a field, as represented in their
library) evolved over time.

1. Sort the working set by `date`.
2. Identify early items and how the questions/methods shift across the range.
3. Note apparent turning points and the current frontier of what's in the library.

```
Evolution of [topic] papers in your library:

Early period (2010–2015): 5 papers
- Focus: problem definition and measurement

Middle period (2016–2019): 12 papers
- Focus: causal mechanisms and theory-building
- Shift: from correlation to causation

Recent period (2020–2024): 15 papers
- Focus: solutions and interventions
- Methods: more experimental, mixed-methods
```

## Reading-list prioritization

**When:** a result set is too large to read everything.

Rank by, in order:
1. Direct relevance to the user's specific question.
2. Citation count from the `extra` field, where present — see Ranking signals in SKILL.md.
3. Foundational vs. recent — aim for a mix, don't default to "newest first."
4. Tag signals the user already uses (e.g. `"seminal"`, `"key"`).
5. Methodological fit for what the user needs.
6. Diversity of perspective.

Not every item will have a recorded citation count — treat those as unknown and rank them on the
remaining criteria; don't push them to the bottom by default just because criterion 2 is blank.

Present as tiers:
- **Essential (5–7 papers)** — start here.
- **Important (8–12 papers)** — read next.
- **Supplementary (rest)** — for completeness.

## Finding highly-cited items

**When:** the user asks for the "most-cited," "seminal," or "highest-impact" items in a set, and
wants to know what's already recorded as such within their own library.

1. Gather the working set (`search_items` or `get_collection_items`).
2. For each item, check `extra` for a citation-count line (see Ranking signals in SKILL.md).
3. Tier the items that have a count:
   - **1000+ citations** — foundational
   - **100–999** — highly influential
   - **10–99** — established
   - **<10** — emerging / recent
4. List items with no recorded count separately as "citation count not recorded," rather than
   omitting them or treating them as zero — a missing count means unknown, not uncited.
5. Say explicitly that this reflects whatever was recorded in the library, at whatever date and
   from whatever source it was recorded — it's not a live lookup, so a count can be stale, and
   counts from different sources (Crossref, Google Scholar, etc.) aren't strictly comparable.

## Tag-based discovery

Tags are an alternative way to explore and filter a library, and often the best signal for
"important" available locally.

1. `list_tags()` to see how the library is organized.
2. Identify interesting tags (e.g. `"seminal"`, `"methodology"`, `"to-read"`).
3. `search_items(query=..., tag=...)` or browse `get_collection_tags(collection_key)` to narrow
   within a tag.

**Use tags when:** the user has organized their library with tags, is looking for items with a
specific status (e.g. `"to-read"`), or wants to filter to a curated subset.
