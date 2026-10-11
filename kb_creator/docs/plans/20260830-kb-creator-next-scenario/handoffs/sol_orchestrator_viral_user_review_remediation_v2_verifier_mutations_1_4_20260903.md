# Viral v2 verifier mutation classes 1--4

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations-1-4`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Baseline receipt: `terra_engineering_viral_user_review_remediation_v2_verifier_fixture_resume_20260903.md`
- Completion token: `READY_FOR_V2_VERIFIER_MUTATIONS_5_8`

## Objective and ownership

Add exactly mutation classes 1--4 against fresh copies of the valid expanded
fixture. Production implementations are read-only.

Owned paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_mutations_1_4_20260903.md`

You are not alone in the worktree. Preserve all other changes.

## Required mutations

1. missing/extra/tampered inventory row, size and SHA-256;
2. event/provenance order drift with downstream inventory resealed so the
   semantic order gate, not the outer hash gate, is exercised;
3. structured container end/bounds drift and table header/row/cell shape drift,
   resealed as needed;
4. reader full-title drift and anchor/run-in outline pollution, resealed as
   needed.

Each class must independently start from a valid builder-produced candidate,
assert the baseline passes, mutate one concern and assert a specific verifier
failure. Run the full verifier test module and real v1 preflight. Write the
receipt and return the token only when all four classes pass.

No builder/verifier/config/real candidate/Git/Step 8A changes.
