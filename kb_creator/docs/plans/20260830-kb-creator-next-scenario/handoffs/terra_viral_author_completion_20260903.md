# Terra receipt — Viral author completion checkpoint

- Goal id: `20260830-kb-creator-next-scenario`
- Step: Step 7 author recovery, deterministic source-order event refinement
- Role / requested effort: `nri-engineer` / Terra medium
- Orchestrator policy owner: root `gpt-5.6-sol` / medium
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-03` (Europe/Moscow)

## Scope and result

Implemented the first real author-side completion seam: every resolver-proven
internal anchor offset now deterministically splits its coarse text event at
the exact UTF-8 byte coordinate. The split retains all source bytes and does
not manufacture a placement, owner, or title. A heading fragment retains its
heading type only for the first split piece; following bytes remain source text
until reviewed typed authoring gives them a representation.

Re-running the existing source-order resolver over those refined events changes
the actual read-only Viral audit from:

```text
placement_ready=16, needs_event_split=50, resolved_physical_unit=14, ambiguous=13
```

to:

```text
placement_ready=66, needs_event_split=0, resolved_physical_unit=14, ambiguous=13
```

The refined event stream contains 680 events. The p46 `f0ecf365` Cremation Pit
asset now has a concrete split-derived `before_event` target while preserving
the selected-view order `[46, 784]`.

## Files changed

- `kb_creator/scripts/author_viral_master_en_v2_config.py`
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`

## Verification and evidence

```powershell
python -B -m pytest -q kb_creator/tests/test_author_viral_master_en_v2_config.py -k "not closed_projection_passes_both_public_top_level_schema_gates"
```

Result: `16 passed, 1 deselected in 21.84s`.

The deselected downstream schema gate currently fails before author-output
semantics because the concurrently owned builder now requires the new canonical
asset fields (`anchor`, `placement`, `source_order`) while the author has not
yet emitted them. This is an active integration seam, not a passing result.

## Remaining exact work / blocker

The 13 post-split cases are now an exact finite set, not a request for manual
all-art review: p17, p25, p31, p32, p49, p66, p100 (two), p102, p108, p109,
p110 and cover. Root supplied reviewed standalone-heading/physical-owner
directions for them; they still need author-side anchor and closed placement
projection together with reviewed heading/container materialization. No
canonical config or candidate was written.

The builder owner has confirmed the exact downstream row contract:

- immutable fields remain `asset_id`, `disposition`, `source_page`, `binary`,
  `provenance`, `migration_outcome`;
- reader rows need a declared hierarchy `anchor`, one-key event `placement`,
  and selected-view or physical-unit `source_order`;
- evidence-only rows set all three new fields to `null`.

Next action: complete typed heading/container projection and bind the reviewed
13-case anchor/physical map, then emit all asset fields and re-enable the full
author-plus-builder gate. This checkpoint does not claim a finished
`publication_config_v2.json`, candidate, or `MASTER_EN`.

- Elapsed time: approximately 35 minutes.
- Token use: unavailable.
