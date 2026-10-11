# Viral remediation v2 verifier mutation-suite closure

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_v2_output_verifier_20260903.md`
- Completion token: `READY_FOR_VIRAL_V2_POLICY`

## Objective and ownership

Add a representative synthetic v2 candidate fixture and the complete missing
independent mutation suite. Verifier and builder implementations are read-only.

Exclusive paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_mutations_20260903.md`

You are not alone in the worktree. Preserve every other edit and change only
these two paths.

## Required tests

Create one otherwise valid synthetic v2 candidate containing all relevant
constructs/assets and independently mutate it to prove rejection of:

1. missing/extra/tampered inventory row, size or SHA-256;
2. event/provenance order drift;
3. container end/bounds drift and table header/row/cell shape drift;
4. reader title drift and anchor/run-in outline pollution;
5. before/after/inside placement drift and copied-asset hash drift;
6. malformed EOL and excessive ordinary blank runs;
7. excluded-page text/event/xref/asset leakage;
8. missing/changed fragment identity, source-backed recovery or generated
   navigation provenance.

Assert the verifier source still has no builder import/use. Retain all v1 tests.
Run the full verifier test module and real v1 verifier preflight. Write the exact
immutable receipt and return `READY_FOR_VIRAL_V2_POLICY` only if every mutation
class passes.

No code/config/evidence/source/reconstruction/real candidate/Git/Step 8A edits.
