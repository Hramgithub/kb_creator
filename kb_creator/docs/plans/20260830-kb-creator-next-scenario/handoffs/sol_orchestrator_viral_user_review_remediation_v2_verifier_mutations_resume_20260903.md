# Viral remediation v2 verifier mutations resume

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations-resume`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Corrected contract receipt: `terra_engineering_viral_user_review_remediation_verifier_contains_correction_20260903.md`
- Completion token: `READY_FOR_VIRAL_V2_POLICY`

## Objective and ownership

Resume the previously blocked mutation suite now that `contains` is compatible.
Builder and verifier implementations are read-only.

Exclusive paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_mutations_resume_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required evidence

Create a builder-valid representative synthetic v2 candidate fixture and eight
independent mutation classes exactly as specified in
`sol_orchestrator_viral_user_review_remediation_v2_verifier_mutations_20260903.md`:
inventory/hash, event order, bounds/table shape, title/outline, placement/asset
hash, EOL/blank runs, excluded leakage, and missing/changed provenance.

Assert verifier independence from builder, retain all v1 tests, run the complete
verifier module and real v1 verifier preflight. Write the exact immutable
receipt. Return `READY_FOR_VIRAL_V2_POLICY` only with all eight classes passing.

No implementation/config/evidence/source/reconstruction/real candidate/Git/
Step 8A changes.
