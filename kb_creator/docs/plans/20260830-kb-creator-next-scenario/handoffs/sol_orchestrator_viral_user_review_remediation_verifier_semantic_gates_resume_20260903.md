# Viral v2 verifier semantic-gates resume after ledger

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-verifier-semantic-gates-resume`
- Owner: current fresh `nri-engineer`, `gpt-5.6-terra` / `medium`
- Ledger receipt: `terra_engineering_viral_user_review_remediation_builder_typed_chunk_ledger_retry_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_MUTATIONS_1_4`

## Objective and ownership

Implement the three independent candidate semantic gates previously blocked by
missing emitted-event evidence. The builder is now read-only.

Owned paths:

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_verifier_semantic_gates_resume_20260903.md`

You are not alone in the worktree. Preserve all existing edits and change only
these paths.

## Required gates

1. Independently validate every ledger row against final `MASTER_EN.md`: exact
   char/UTF-8 byte range, SHA-256, monotonic order, declared-content identity,
   emitted/suppressed state, structured `contains`, reader asset relocation and
   no illegal overlap.
2. Independently parse tables and bounded structures from the ledger slices;
   compare header/row/cell counts, exact container start/end, children order and
   parent-stream continuation with config declarations.
3. Cross-bind complete reader titles and hierarchy representation to final
   Markdown outline, anchors/run-ins and provenance; reject title drift,
   missing heading and outline pollution.

Do not import/reuse builder code or serializers. Add focused valid and failure
tests using the representative fixture. Run full verifier tests, `py_compile`,
real v1 preflight and static no-builder-import check. Write the exact receipt and
return the token only when all three gates pass.

No builder/config/evidence/source/real candidate/Git/Step 8A changes.
