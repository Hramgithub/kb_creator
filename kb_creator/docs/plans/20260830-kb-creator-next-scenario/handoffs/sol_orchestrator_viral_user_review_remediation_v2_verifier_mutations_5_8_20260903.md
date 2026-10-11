# Viral v2 verifier mutation classes 5--8

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations-5-8`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior gates: mutation classes 1--4 closed by retry + inline-run-in receipts
- Completion token: `READY_FOR_VIRAL_V2_POLICY`

## Objective and ownership

Add and close the final four candidate-level mutation classes against fresh
copies of the valid representative fixture. Production implementations are
read-only.

Owned paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_mutations_5_8_20260903.md`

You are not alone in the worktree. Preserve all other changes.

## Required mutations

5. before/after/inside placement drift and copied-reader-asset bytes/SHA drift;
6. malformed CR/CRCRLF and excessive ordinary blank runs while literal content
   remains allowed;
7. text, event, xref and asset leakage from excluded reader pages 123--124;
8. missing/changed fragment/range identity, missing source-backed-recovery
   provenance and missing/duplicated generated-navigation provenance.

Each mutation must start from a valid candidate, reseal outer inventory as
needed, and assert its intended specific verifier gate. Retain all previous
tests, run the complete verifier module and real v1 preflight. Write the exact
receipt and return `READY_FOR_VIRAL_V2_POLICY` only when all four classes pass.

No builder/verifier/config/real candidate/Git/Step 8A edits. If a semantic gate
is truly absent, return its exact implementation gap rather than weakening the
test.
