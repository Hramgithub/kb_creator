# T7d — Stage 40 semantic statblock ordinal root-cause receipt

- Timestamp: `2026-09-18T14:00:22+03:00`
- Scope: read-only root-cause audit of run `20260918-publication-13` Stage 40 failure `renderer semantic statblock ordinal mismatch`.
- Assignment state: `complete`
- Orchestrator policy owner: `/root`; orchestration ownership was not transferred.
- Scoped override: architecture/root-cause only; this receipt is the only file written.
- Elapsed time: approximately 25 minutes.
- Token use: approximately 8k architecture-agent tokens.

## Verdict

Run13 has seven correctly rendered semantic statblock cards, with the seven exact sealed IDs in correct document order and on page 018. The failure is a false negative in the Stage 40 HTML validator: its page extraction regex is not nesting-aware.

The failing validator snapshot searched a page with:

`<section ... id="page-018" ...>([\s\S]*?)</section>`

and then searched that captured group for the page's Nth statblock. Because every statblock is itself a nested `<section>`, the lazy match ends at the closing tag of the first `stanwick-statblock`, not at the closing tag of `page-018`. A direct reproduction over the quarantined HTML captured only 944 characters, found one card, contained `stanwick-statblock`, and did not contain `elsie-statblock`. Thus ordinal 1 passes, while ordinal 2 is the first false `ordinal mismatch`.

## Evidence

- Sealed projection: `kb_creator/working/number-7-dream/publication/20260918-publication-13/quarantine/40-html-candidate/evidence/html_semantic_projection.json` (minified line 1) declares seven page-018 rows with ordinals 1–7 and IDs, in order: `stanwick`, `elsie`, `regular`, `heavy`, `migo-man`, `migo`, `hunting-horror` statblocks.
- Rendered page: `.../quarantine/40-html-candidate/artifacts/Number_7_Dream_RU.html:692-740` contains one outer page-018 section and seven nested semantic statblock sections. Openings are at lines 697, 701, 707, 711, 716, 722, and 732; page 018 closes at line 740.
- A whole-document tag scan returns exactly those seven `data-semantic-id` values in the same order.
- The run13 validator snapshot used non-nesting-aware page extraction and per-slice ordinal checking at then-current `kb_creator/pipeline/publication_adapters.py:1047-1057`; its critical lazy page regex and `len(page_cards) < ordinal` branch were at lines 1049-1054. These lines were replaced concurrently while this audit was running.
- No evidence indicates a renderer, projection, MASTER_RU, ArtView, or semantic-lineage ordering defect.

## Required invariant

For each sealed projection row `(page, ordinal, id)`, the final DOM must contain exactly one element satisfying all of:

1. tag is `section` or `div`;
2. class token contains `statblock-card`;
3. `data-semantic-kind` is exactly `statblock`;
4. `data-semantic-id` is exactly the projected ID;
5. its nearest enclosing `section.production-page` owns the projected `data-page`;
6. it is the projected 1-based ordinal among semantic statblock cards in DOM order within that page.

The global set/order must have no missing, duplicate, extra, or out-of-page semantic card. A projected card must not use `blockquote`, `review-callout`, or another obsolete/invalid container. Attribute order must not affect validation.

## Robust scenario-neutral validation

Preferred implementation: one `html.parser.HTMLParser` pass with a nesting stack.

- Push non-void start tags with a normalized attribute map; reject duplicate attributes relevant to ownership.
- Track `section.production-page[data-page]` frames and reject nested or duplicate page containers.
- On a semantic statblock start tag, resolve the nearest page frame, increment a per-page ordinal, and emit `(page, ordinal, id)` in document order.
- Reject a semantic statblock outside a production page, without an ID, nested inside another semantic statblock, in an invalid/obsolete container, or with malformed nesting.
- Canonicalize expected projection order by `(page, ordinal)` or explicitly validate that projection rows are already canonical and per-page ordinals are contiguous from 1. Do not depend on reconstruction decision dictionary insertion order.
- Validate `expected_statblock_ids == [row.id for canonical projected rows]`, then compare the complete actual tuple list to the complete expected tuple list.
- Keep count, ownership, ordinal, and ID as one atomic parser result; do not mix a global regex count with separate page regex slices.

A safe fallback is segmentation from one generated `<!-- pdf-page-NNN -->` marker to the next page marker, then card scanning within that segment. It must never segment on the first `</section>`. The nesting-aware parser is preferable because it directly proves nearest-page ownership and malformed nesting.

## Concurrent implementation observed

Another worker modified the shared working tree during this audit. Current `publication_adapters.py:343-408` contains `_SemanticCards(HTMLParser)` and current `:411-417` compares parser output with projected page/ID order; Stage 40 calls it at current `:1121`. Current tests at `kb_creator/tests/test_publication_html_adapter.py:375-402` cover two nested cards, attribute-order independence, wrong page/ID/order, obsolete callout, and malformed nesting.

Read-only verification against the exact run13 quarantined HTML and `html_semantic_projection.json` returned:

`exact-run13-semantic-parser: PASS`

Those concurrent changes were not authored by this task. The parser direction is correct. Before integration, add or confirm the ordinal/canonical-order and duplicate/nested-page fail-closed cases below. Full pytest was not run here: bundled runtime `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` reports `No module named pytest`.

## Regression cases / acceptance criteria

- Positive: two and seven sibling nested `<section class="statblock-card">` elements within one production page validate ordinals 1..N.
- Positive: multiple pages reset ordinal to 1 per page and compare in canonical page/ordinal order.
- Positive: `class`, `data-semantic-kind`, and `data-semantic-id` may occur in any attribute order.
- Negative: swapped IDs with unchanged count; wrong page; skipped/repeated ordinal; duplicate ID; missing ID; extra card; card outside a production page.
- Negative: duplicate or nested production-page containers; nested semantic cards; malformed close-tag nesting.
- Negative: `blockquote.statblock-card`, `.review-callout.statblock-card`, wrong tag, or wrong semantic kind.
- Projection integrity: reject non-contiguous ordinals, duplicate `(page, ordinal)`, noncanonical rows unless canonicalized deterministically, and disagreement between `expected_statblock_ids` and projected rows.
- Exact run13 regression: parse the quarantined-equivalent page-018 fixture with all seven IDs and require the exact tuple sequence, not only count.
- Integration: rebuild Stage 40 in a fresh identity-bound publication run; accept only when the HTML adapter receipt binds the parser-validated output and downstream structural/visual QA passes. Do not edit or promote the run13 quarantine manually.

## Files checked / changed

Checked:

- `kb_creator/working/number-7-dream/publication/20260918-publication-13/quarantine/40-html-candidate/{artifacts/Number_7_Dream_RU.html,evidence/html_semantic_projection.json,evidence/production_html_report.json}`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- active goal plan/status context already assigned by the orchestrator.

Changed only this receipt. No root-cause blocker remains. Next action: engineer completes the parser invariants/tests, runs the focused and publication suites with the approved pytest runtime, then the orchestrator starts a fresh Stage 40 run.
