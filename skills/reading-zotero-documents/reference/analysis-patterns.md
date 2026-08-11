# Full-text analysis patterns

## Contents
- Evidence extraction
- Comparative deep dive
- Methodology learning

## Evidence extraction

**When:** the user needs specific evidence or quotes about a claim.

1. Identify the 5–10 most relevant papers (via `searching-zotero-library`).
2. For each: locate the attachment, `read_document(remove_headers_footers=True)`, paging through
   with `start_page` if the paper is long.
3. Extract per paper: main arguments/claims, supporting evidence, methodology used, key quotes
   (note the page — `read_document`'s `start_page`/`end_page` tell you which page range a quote
   came from), and any limitations the authors acknowledge.
4. Synthesize across papers into an evidence map: which findings are corroborated by multiple
   papers, which are contradicted, and which are one-off.

## Comparative deep dive

**When:** the user wants a detailed comparison of approaches or theories across papers.

1. Identify 3–5 papers representing distinct perspectives.
2. Read each in full (page through with `start_page`/`max_pages` as needed).
3. Extract per paper: core theoretical assumptions, methodological approach, key findings, how
   the paper frames the problem.
4. Build a comparison table across papers.
5. Note where the papers agree, disagree, and are simply silent on a point.

## Methodology learning

**When:** the user wants to understand how to apply a specific method.

1. Search for papers using that method (`searching-zotero-library`).
2. Narrow to well-written exemplars — clear methods sections, not just any hit.
3. Read the methods section of 3–5 papers.
4. Extract common patterns: research design choices, data collection procedures, analysis
   approach, and pitfalls the authors call out.
5. Summarize as a methodology guide with concrete examples drawn from the papers.
