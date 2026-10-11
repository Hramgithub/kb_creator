# Viral remediation v2 negative mutation tests closure

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-negative-tests`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_v2_placement_determinism_20260903.md`
- Completion token: `READY_FOR_V2_OUTPUT_VERIFIER`

## Objective and ownership

Add exactly the three missing dedicated negative mutation tests. The builder
implementation is read-only in this continuation.

Exclusive paths:

- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_negative_tests_20260903.md`

You are not alone in the worktree. Preserve every other change and do not
revert, clean or edit outside these two paths.

## Required tests

1. Duplicate/conflicting reader-asset binding is rejected.
2. Missing/changed/empty source fragment-range identity is rejected.
3. Any v2 event on or referencing an excluded reader page is rejected while
   the audit disposition remains valid.

Each test must independently mutate an otherwise valid synthetic v2 fixture and
assert a specific failure. Run the complete builder test module. Write the exact
receipt and return `READY_FOR_V2_OUTPUT_VERIFIER` only if all pass.

No code/config/evidence/source/candidate/verifier/Git/Step 8A changes are
allowed.
