# Viral v2 source identities and page dispositions

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-source-dispositions`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_FOR_V2_VISUAL_REVIEW_UNITS`

## Objective and ownership

Implement only source-PDF/reconstruction binding and exact 124 page
dispositions in builder+independent verifier. Do not add visual review units or
external reports yet.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_source_dispositions_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required migration

- Extend the v2 document object with closed `source_pdf` and
  `reconstruction_inventory` identities (`path`, `bytes`, `sha256`), validated
  independently against CLI inputs.
- Add required top-level `source_disposition` with the exact 124 ordered rows
  and fields defined in the parent QA-contract packet. Bind each
  `page_markdown` identity to the accepted reconstruction page.
- Enforce pages 1--122 reader/true and 123--124
  `excluded_advertising`/false/date `2026-09-02`/nonempty reason.
- Reject any hierarchy/event/xref/recovery/asset on excluded pages.
- Candidate `SOURCE_DISPOSITION.json` serializes all rows plus derived summary;
  verifier independently binds it to config, reconstruction and candidate
  reader absence.
- Migrate all synthetic v2 fixtures atomically; v1 remains unchanged.

Add positives and mutations for source identity, row count/order/duplicates,
page identity, exact excluded policy and content leakage. Run both full modules,
both `py_compile`, both real v1 preflights, independence and diff checks. Write
the exact receipt and return the token only when the route is green.

No visual-QA/review-unit/report/real config/evidence/candidate/Git/Step 8A edits.
