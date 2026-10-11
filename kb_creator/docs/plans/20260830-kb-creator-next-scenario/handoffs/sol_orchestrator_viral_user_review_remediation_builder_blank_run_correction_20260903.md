# Viral v2 builder blank-run correction

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-builder-blank-run-correction`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_verifier_asset_schema_correction_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_FIXTURE`

## Objective and ownership

Fix exactly the builder-created ordinary `\n\n\n` run exposed by the real
end-to-end fixture. Normalize at typed chunk/placement composition boundaries;
do not apply a final global regex to finished Markdown and do not alter literal
or fenced content.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_builder_blank_run_correction_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required correction

- Typed events and placement markers compose with exactly one ordinary blank
  line between blocks and one terminal LF.
- before/after/inside asset insertion may not create empty triple runs.
- Literal/fenced/body content is byte-preserved except declared EOL policy.
- Add a regression using the same mix that exposed the failure: bounded
  structures plus before/after/inside assets and suppressed asset.
- Retain v1 behavior, all typed serializers, asset identity and atomic output.

Run builder tests and `py_compile`. Write the exact receipt. Do not edit
verifier/config/evidence/source/real candidate/Git/Step 8A paths.
