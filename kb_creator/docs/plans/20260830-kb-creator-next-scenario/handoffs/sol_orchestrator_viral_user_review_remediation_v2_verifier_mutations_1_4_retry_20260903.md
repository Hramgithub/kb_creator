# Viral v2 verifier mutation classes 1--4 retry

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations-1-4-retry`
- Owner: current fresh `nri-engineer`, `gpt-5.6-terra` / `medium`
- Semantic-gates receipt: `terra_engineering_viral_user_review_remediation_verifier_semantic_gates_resume_20260903.md`
- Completion token: `READY_FOR_V2_VERIFIER_MUTATIONS_5_8`

## Objective and ownership

Close exactly mutation classes 1--4 now supported by the frozen verifier.

Owned paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_mutations_1_4_retry_20260903.md`

You are not alone in the worktree. Preserve all other changes.

Use fresh valid representative candidates and independent resealing as needed:

1. inventory missing/extra/tampered row, bytes and SHA;
2. provenance/actual event order drift;
3. container bounds and table header/row/cell drift;
4. full reader-title drift and anchor/run-in outline pollution.

Each class must assert its intended specific verifier gate rather than an outer
unrelated failure. Retain existing tests, run full verifier module and real v1
preflight. Write the exact receipt and return the token only when all four pass.

No builder/verifier/config/real candidate/Git/Step 8A edits.
