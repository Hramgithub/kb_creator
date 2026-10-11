# Number 7 Dream full structural-fidelity audit

## Scope and counting policy

All 26 source-page visuals were compared with the matching Stage 06 Markdown.
Counts below are distinct semantic units, not raw OCR lines: one multi-page list
is one unit, one handout boundary is one unit, and each independently named
stat block is one unit. OCR wording errors are excluded.

## Result

- Pages checked: `26/26`.
- Affected pages: `15` (`1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 17, 18, 19`).
- Confirmed structural defect units: `30`.
- Unaffected by the audited defect classes: pages `3, 12, 13, 16, 20-26`.

| Class | Units | Pages | Confirmed cases |
|---|---:|---|---|
| Title/heading hierarchy | 7 | 1, 2, 5, 6, 7, 8, 9 | split cover title; missing Credits heading; five flattened parent/child outlines |
| Handout/callout boundary | 9 | 7, 9, 10, 14, 15, 19 | eight handout occurrences plus Keeper's Note sidebar |
| List structure | 4 | 4-5, 11, 14, 19 | construct glitches, Wellness Centre events, Handout 5 bullets, appendix note bullets |
| Quoted speech structure | 3 | 17 | opening monologue and two conditional monologues |
| Stat-block structure | 7 | 18 | Stanwick, Elsie, Enlightened Regular, Enlightened Heavy, Migo-man, Migo, Hunting Horror |
| **Total** | **30** | **15 pages** | |

Page 17 integration note: the three italic quote units are the opening “We meet
at last” monologue and the two conditional speeches. The final “In either
case…” paragraph is narration, not a fourth quote. This integration corrects
the label (not the count) in the bounded A2 receipt.

## Earliest failing boundary

The source `content_list_v2` and `middle.json` do not classify the page 14
letter as a quote: its elements are ordinary `paragraph`/`text` blocks with
geometry. Stage 03/04 preserves text, bbox and coarse block type but has no
typed semantic-container inventory. Reviewed page decisions therefore contain
flat Markdown. Stage 05 proves lexical/spatial coverage and can report
completeness `1.0` without proving quote/list/handout/stat-block semantics.
Stage 06 then materializes that flat decision Markdown exactly.

The neutral MASTER_EN v3 route is not a recovery layer. It accepts an already
accepted RECONSTRUCTED_EN, does not consume the source PDF, and performs exact
projection. Older Viral v2 publication code could author typed structures from
separate reviewed metadata; that behaviour is not present in the neutral v3
path used for new scenarios.

## Required systemic closure

The shared reconstruction authority must carry visually reviewed semantic
container assertions from Stage 04/page decisions, validate them in Stage 05,
and require the declared Markdown representation in Stage 06. Number 7 Dream
must then use an immutable successor decision set and a fresh Stage 05-06 replay.
No edit to the existing v12 decisions or sealed candidate is permitted.

