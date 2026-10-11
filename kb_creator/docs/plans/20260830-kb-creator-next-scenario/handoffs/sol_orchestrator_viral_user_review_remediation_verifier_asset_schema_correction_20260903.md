# Viral v2 verifier asset-schema correction

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-verifier-asset-schema-correction`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_v2_verifier_fixture_extension_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_FIXTURE`

## Objective and ownership

Correct exactly the verifier's stale v2 asset config schema and add independent
policy validation. Do not change builder or the expanded fixture in this pass.

Owned paths:

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_verifier_asset_schema_correction_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required correction

- A reader asset requires the exact closed config fields:
  `asset_id`, `reader_value`, `placement`, `anchor`, `page`,
  `duplication_resolution`, `quality_stage`, `source_path`, `bytes`, `sha256`,
  `semantic_role`.
- An evidence-only asset uses the closed five-field base form and may not carry
  reader binary/policy fields.
- Independently validate closed enums, exact single placement class, source
  containment, positive bytes, SHA-256 form, reader page/event scope and asset
  uniqueness; do not copy builder validation code.
- Candidate manifest/output verification must still prove reader copied identity
  and suppressed absence.
- v1 behavior and verifier independence remain unchanged.

Add focused valid/invalid schema/policy tests. Run verifier module,
`py_compile`, real v1 preflight and static no-builder-import check. Write the
exact receipt. Do not resume the large fixture/mutations yet.

No builder/config/evidence/source/real candidate/Git/Step 8A changes.
