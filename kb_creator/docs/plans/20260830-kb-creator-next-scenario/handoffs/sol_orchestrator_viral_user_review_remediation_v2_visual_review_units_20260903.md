# Viral v2 dynamic visual-review units

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-visual-review-units`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_FOR_V2_EXTERNAL_VERIFIER_REPORT`

## Objective and ownership

Add only the closed, dynamic `visual_review_units` contract needed by Slice 4.
Do not implement the external verifier report or visual-QA generator yet.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_visual_review_units_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required contract

Add required top-level `visual_review_units`. Each exact row contains:

- `review_id`, `kind`, `source_pages`, `event_ids`, `asset_ids`, `priority`,
  `contact_sheet_group`.

Closed kinds:

- `heading_outline`, `callout`, `ordered_list_callout`, `table`,
  `equipment_card`, `creature_statblock`, `inline_run_in`, `full_page_map`,
  `physical_page_pair`, `xref_recovery`, `asset_placement`.

Enforce unique nonempty ids; nonempty source pages limited to reader scope;
existing unique event/asset ids; at least one event or asset; boolean priority;
nonempty group. Kind-specific closure must bind to the matching event/structured
kind/asset placement. Every hierarchy heading, structured event, xref/recovery
and reader asset must be covered by at least one appropriate unit; suppressed
assets and pages 123--124 never become review choices.

Candidate QA JSON records only derived counts/groups/priority totals and a hash
of the canonical declaration; no fixed Viral counts. Independent verifier
recomputes and binds these metrics/declaration hash.

Update synthetic fixtures and add missing/duplicate/unknown/excluded/kind-
mismatch/uncovered/dynamic-count mutations. Retain all prior v1/v2 behavior.
Run both full modules, both `py_compile`, both v1 preflights, independence and
diff checks. Write the exact receipt and return the token only when complete.

No external report/visual-QA/real config/evidence/candidate/Git/Step 8A changes.
