# Terra receipt — Viral metadata-derived asset order

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-metadata-asset-order-20260903`
- Contributor role: `nri-engineer`
- Requested model / effort: repository profile `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `matched`
- Scoped override: `none`
- Timestamp: `2026-09-03T22:56:35+03:00`
- Elapsed time: approximately `00:36:00`
- Token use: unavailable

## Scope

Implemented only the author-side metadata resolver and its focused tests in
the assigned `kb_creator` worktree. No builder or verifier was edited. No
source PDF, accepted reconstruction, v1/v2 candidate, frozen input, Git state,
or manual all-art placement ledger was changed.

## Result

`resolve_asset_source_order()` derives each reader asset's source key from its
exact `ASSET_MANIFEST` identity and the asset block in that manifest's selected
comparison view. It never compares `raw_index` values across views. It ignores
Markdown image syntax while matching complete next comparison text blocks to
accepted source events, and returns an explicit ambiguity instead of using a
damaged marker offset or page-end fallback. Shared resolved gaps retain their
selected-view raw-index ordinal.

`asset_source_order_readiness()` exposes the real-input result through the
current author module for the next authoring seam. It reports `80` exact
text-anchor resolutions, `9` physical-page-unit-order resolutions, and `4`
explicit `ambiguous_exact_following_text_anchor` rows (`93` reader rows total).
Physical/facsimile rows retain accepted source page/unit order and do not gain
a normal text anchor.

The same change normalizes the two sealed boundary-ledger dialects at
`approved_ledgers()`: v2 `segments`, `owner`, `title`, `termination`, and
`order_key` are mapped to the existing canonical reader fields while preserving
their original hash-bound files and raw `ledger_kind`. This prevents the prior
silent omission of all v2 page 41–122 intervals. Known v2 typed aliases
`logical_table`, `callout_series`, and `run_in_series` are retained as raw kind
provenance and mapped only for the existing typed graph vocabulary.

## Files changed or checked

- Changed: `kb_creator/scripts/author_viral_master_en_v2_config.py`
- Changed: `kb_creator/tests/test_author_viral_master_en_v2_config.py`
- Added: this immutable receipt.
- Checked read-only: current author/tests; sealed v4 `ASSET_MANIFEST.json`;
  three-view `comparison.json`; all three sealed boundary ledgers; accepted
  owner/placement decision for the existing Plots-before-Prologue rule.

## Verification and evidence

Command:

```powershell
python -m unittest -q kb_creator.tests.test_author_viral_master_en_v2_config
```

Result: exit code `0`; focused author suite passes, including new v2-ledger
normalization, selected-view-only synthetic resolver, and real-input audit
coverage.

Real-input seed evidence:

- p46 `f0ecf365`: `original_hybrid` block `784`, resolved before
  `event-p046-000000` (the conserved fragment containing `7. Cremation Pit`);
- p65 `8e99d692`, p66 `81953e33` and `6e1d78ee`: resolved by selected-view
  following-text evidence before their current source events;
- p78 `8dfcf412`: `original_hybrid` block `1236`, resolved before
  `event-p078-000000` (Handout 10 preceding the Handout 11/Enoch material);
- ledger interval audit now contains v2-backed pages through `122` rather than
  silently stopping with the first v1 ledger.

## Blockers and limitations

The resolver correctly leaves four rows ambiguous rather than inventing a
placement. In particular, p31 `b90cb9a3` and p32 `da0cac1c` have multiple exact
current-event occurrences of `Prologue`; the existing reviewed rule that city
then boat precede `Prologue` remains authoritative. The current coarse author
graph has no unique immediate semantic event for that accepted relation.

This is not a candidate acceptance and does not materialize asset events. It
also does not replace the later semantic event/owner splitting required to turn
the conservative readiness result into a closed public placement graph.

## Next action

The next bounded integration step should consume
`asset_source_order_readiness()` while creating the reviewed semantic event
boundaries. It must bind p31 city then p32 boat to the unique newly materialized
`Prologue` predecessor gap, retain source order, and close only the four
explicitly reported ambiguities with existing reviewed evidence. Do not add a
manual all-art ledger or fall back to Markdown marker offsets.
