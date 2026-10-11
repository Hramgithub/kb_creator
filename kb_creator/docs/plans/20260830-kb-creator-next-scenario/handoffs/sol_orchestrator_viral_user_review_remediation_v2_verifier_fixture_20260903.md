# Viral remediation v2 verifier baseline fixture

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-fixture`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_FOR_V2_VERIFIER_MUTATIONS_1_4`

## Objective and exclusive ownership

Create only one builder-valid, representative synthetic v2 candidate fixture
and prove the frozen independent verifier accepts it. Do not add negative
mutations yet.

Owned paths:

- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_verifier_fixture_20260903.md`

You are not alone in the worktree. Preserve all other changes.

## Fixture requirements

The fixture must be produced through the real builder route into a temporary
absent root and contain: audit 124 / reader 122 / excluded 2; generated
navigation; full title plus anchor/run-in hierarchy; table and at least one
other bounded structured unit; before/after/inside reader assets plus one
suppressed asset; fragment identities; source-backed recovery; no acceptance
or review-only file. Invoke the frozen verifier as an external implementation
and assert a clean pass. Keep helpers reusable for later mutation tests.

Run the complete verifier test module and real v1 verifier preflight. Write the
receipt and return the token only when the valid baseline passes.

No builder/verifier/config/real evidence/source/candidate/Git edits.
