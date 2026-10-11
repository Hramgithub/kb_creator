# Viral v2 verifier candidate semantic-gates correction

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-verifier-semantic-gates`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_v2_verifier_mutations_1_4_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_MUTATIONS_1_4`

## Objective and ownership

Add exactly the three missing independent candidate-level semantic gates exposed
by mutation classes 2--4. Do not change builder or real artifacts.

Owned paths:

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_verifier_semantic_gates_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required gates

1. Reconstruct expected event order keys/content from config and independently
   compare config, candidate provenance sequence and actual Markdown positions;
   reject reordered, duplicated, missing or content-mismatched events.
2. Independently parse candidate tables and bounded structured blocks; verify
   exact declared container start/end, contains order, header/row/cell counts,
   and that following parent prose is outside the block.
3. Cross-bind complete `reader_title`, heading representation and anchor/run-in
   representation to actual Markdown outline and provenance; reject title drift
   and outline pollution.

Do not import builder or reuse its serializers. Add focused valid/failure tests,
run full verifier tests, `py_compile`, real v1 preflight and static independence
check. Write the receipt and return the token only when all three gates pass.

No builder/config/evidence/source/real candidate/Git/Step 8A changes.
