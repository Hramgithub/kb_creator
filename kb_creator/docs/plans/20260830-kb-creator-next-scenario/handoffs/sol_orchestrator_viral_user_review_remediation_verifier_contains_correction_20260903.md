# Viral v2 verifier `contains` contract correction

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-verifier-contains-correction`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_v2_verifier_mutations_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_MUTATIONS`

## Objective and exclusive ownership

Correct exactly one cross-component contract mismatch: the independent verifier
must accept `contains` only for v2 `structured_unit` events and independently
validate its closed, ordered child-identity semantics.

Owned paths:

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_verifier_contains_correction_20260903.md`

You are not alone in the worktree. Preserve all prior changes and touch no
other path.

## Required correction

- Closed event schema permits `contains` only when `type=structured_unit`.
- It is a nonempty ordered list of unique nonempty child identity strings.
- It must match the independently parsed/emitted structured children exactly;
  reject missing, extra, duplicate or reordered children.
- Non-structured events carrying `contains` are rejected.
- Verifier remains independent of builder; v1 behavior remains unchanged.

Add focused success/failure tests for this correction, run verifier tests,
`py_compile` and real v1 preflight. Write the exact receipt. Do not add the full
eight-class mutation matrix yet.

No builder/config/evidence/source/candidate/Git/Step 8A changes.
