# Viral v2 verifier baseline fixture extension

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-fixture-extension`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_FOR_V2_VERIFIER_MUTATIONS_1_4`

## Objective and ownership

Extend the existing accepted baseline fixture with exactly the missing
representative surfaces. Do not add negative mutations or change production
code.

Exclusive paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_fixture_extension_20260903.md`

You are not alone in the worktree. Preserve all other changes.

## Required extension

The same valid builder-produced fixture must include and the verifier must
accept:

- reader assets in all three classes: before, after and inside structured unit;
- at least one declared evidence-only/suppressed asset absent from reader and
  candidate assets;
- one valid table and at least one other bounded structured type;
- a valid `source_backed_recovery` provenance operation;
- existing 124/122/2, generated navigation, headings/anchors/run-ins and clean
  inventory guarantees.

Run the full verifier module. Write the exact receipt and return the token only
when this expanded baseline passes. No builder/verifier/config/real candidate/
Git/Step 8A edits.
