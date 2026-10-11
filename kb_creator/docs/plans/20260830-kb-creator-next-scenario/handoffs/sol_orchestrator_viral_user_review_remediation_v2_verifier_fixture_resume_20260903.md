# Viral v2 representative verifier fixture resume

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-fixture-resume`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_FOR_V2_VERIFIER_MUTATIONS_1_4`

## Objective and ownership

Rerun the already-expanded representative fixture against the corrected builder
and verifier. Make only fixture-test adjustments strictly required to express
the already-authorized surfaces; do not change production code.

Owned paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_fixture_resume_20260903.md`

The passing baseline must cover all three placements, suppressed asset, table,
another bounded unit, recovery provenance, navigation, hierarchy forms,
124/122/2 and clean inventory. Run the full verifier module and real v1
preflight. Write the receipt and return the token only on a clean pass; report
the next exact contract mismatch if one remains.

No builder/verifier/config/real candidate/Git/Step 8A changes.
