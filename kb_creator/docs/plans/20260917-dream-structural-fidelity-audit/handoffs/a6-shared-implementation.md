# A6 shared structural-contract implementation receipt

- Goal: `20260917-dream-structural-fidelity-audit`
- Step: A6
- Role: engineering implementation; policy owner: `gpt-5.6-sol` at medium
- Assignment state: completed; runtime model identity is platform-unverified.
- Scoped override: none.
- Timestamp: 2026-09-17T15:03:01+03:00.
- Elapsed time: approximately 55 minutes. Token use: unavailable.

## Scope and result

Implemented the opt-in, fail-closed reviewed semantic-container path without
editing any Dream decisions, replay roots, candidates, acceptance evidence, or
legacy v1/v3 artifacts.

`reconstruction_decision_set.v2` selects the profile
`visually_reviewed_semantic_containers_v1`; v1 rejects a mixed page decision,
while v2 requires every page decision to provide
`page_semantic_structure.v1`. Shared
`pipeline/semantic_structure.py` computes the existing compact-boundary
transform once, validates visual identity, selected packet block references,
line/hash spans, Markdown representation, nesting/parentage/continuation, and
overlap/cycle closure. Stage05 dispatches v3/v4 by decision-set schema; v4
composes the existing v3 lexical ledger with this validator. Stage06 repeats
the validation, checks the v4 structure identity, and writes hash-bound
`SEMANTIC_STRUCTURE.json`.

For an asset-backed semantic unit, the closed rule is now explicit: an inline
asset needs its placeholder inside the unit span; a matching
`reference_only` asset is preserved as evidence but is not rendered. This lets
one reviewed statblock table replace its raster crop without duplicating reader
content.

Stage03 normalization now preserves only closed v2 table evidence: table
caption plus HTML `th`/`td` cell text in source order, uniquely matched by an
exact same-page v1 table bbox. It retains the raster asset and does not infer a
statblock/callout. Paths, HTML tags, table type and nesting metadata are not
included in reader text.

## Files changed / added

- Added contracts: `reconstruction_decision_set.v2.schema.json`,
  `page_semantic_structure.v1.schema.json`,
  `ai_merge_fidelity_audit.v4.schema.json`,
  `reconstruction_semantic_structure.v1.schema.json`.
- Added `kb_creator/pipeline/semantic_structure.py` and
  `kb_creator/tests/test_semantic_structure.py`.
- Updated reconstruction decision validation, replay Stage05 dispatch and
  downstream closure, fidelity audit, Stage06 materializer, Stage03
  comparison normalization, comparison-v3 schema, and focused comparison test.
- Did not revert or alter unrelated in-flight OCR-equivalence/ACL changes.

## Verification / evidence

- `python -m py_compile` for all changed Python modules: passed.
- `pytest -q kb_creator/tests/test_semantic_structure.py
  kb_creator/tests/test_materialize_mineru_ai_merge.py`: **52 passed**.
- Focused v2-table normalization tests: **2 passed**.
- The wider audit/replay collection could not run in the available pytest venv:
  it lacks `jsonschema`; the full replay test has one unrelated CLI import
  dependency on `PIL`. No dependency was installed or changed.

## Exact authoring interface for A7

Each of all 26 successor decision files must add:

```json
"semantic_structure": {
  "schema": "kb_creator.page_semantic_structure.v1",
  "review": {"state": "complete", "visual": {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-014.png", "bytes": 123, "sha256": "UPPERCASE_SHA256"}},
  "units": [{"id": "page014-handout", "kind": "handout", "representation": "blockquote", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}], "markdown_span": {"start_line": 1, "end_line": 9, "sha256": "UPPERCASE_SHA256"}, "container_parent": null, "semantic_parent": null, "continuation_of": null, "heading_level": null, "item_count": null}]
}
```

The exact effective Markdown is decision Markdown after an optional existing
`block_boundaries` transform; spans are one-based inclusive LF lines and their
hash is the UTF-8 SHA-256 of the inclusive lines joined with LF and no terminal
LF. `kind`/`representation` pairs are closed: blockquote/callout/handout →
`blockquote`; list → `unordered_list` or `ordered_list`; statblock →
`blockquote` or `table`; heading → `atx_heading`. Use `reference_only` for a
selected table crop that semantic table Markdown replaces.

The decision-set root must use schema
`kb_creator.reconstruction_decision_set.v2` and add
`"semantic_structure_profile":"visually_reviewed_semantic_containers_v1"`.

## Blockers and next action

No code blocker. A7 must create a fresh replay-06 and fresh v2 decision set;
replay-05/v12 remain immutable. Before full execution, run the audit/replay
suite in an environment containing `jsonschema` and `PIL`, then perform the
independent implementation review. Documentation owner should link this
contract from KB Creator README/pipeline summary and record the new Stage06
sidecar in goal status.

## Follow-up: cross-column visual assertion and source-span closure

Added `column_before_anchor` to the existing v3 visual-assertion relation set.
It is valid only for an exact same-page/same-view region wholly left of its
selected anchor (`region.x2 <= anchor.x1`); it deliberately allows vertical
wrap across columns, while retaining the existing normalized-Markdown
immediate-before-anchor hash and visual-identity proof. `before_anchor` and
`anchor_prefix` retain their prior predicates, so historical allowlists remain
compatible.

The semantic validator now also requires every text-bearing source block to
occur exactly once in its declared normalized span, in declared source order.
The normalization matches v3: Unicode NFKC, casefold, alphanumeric stream,
with inline `sup`/`sub` tags ignored. Asset-only, `reference_only` table crops
remain identity evidence rather than forced reader text. It rejects reordered
unit spans, unbound arbitrary selected-block citations, non-preceding
same-page continuations, implicit/crossing overlap, and cycles through every
container/semantic/continuation relation.

Focused semantic suite remains **3 passed** after the closure follow-up;
Python compilation of the changed validator/audit modules passes. The v3
allowlist assertion tests require the full test environment with `jsonschema`.
