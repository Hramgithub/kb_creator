# Viral v2 verifier inline-run-in admission correction

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-verifier-inline-run-in-admission`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_v2_verifier_mutations_1_4_retry_20260903.md`
- Completion token: `READY_TO_CLOSE_V2_VERIFIER_MUTATIONS_1_4`

## Objective and ownership

Correct only the stale structured-kind admission so an otherwise valid
`inline_run_in` reaches the already-implemented run-in boundary/hierarchy gate.

Owned paths:

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_verifier_inline_run_in_admission_20260903.md`

Add `inline_run_in` to the closed supported kind set; retain its existing exact
anchor/label/body parser and hierarchy representation checks. Add a valid case
and a polluted-outline failure. Run full verifier tests, `py_compile`, real v1
preflight and no-builder-import check. Write the receipt.

No builder/config/evidence/source/real candidate/Git/Step 8A changes.
