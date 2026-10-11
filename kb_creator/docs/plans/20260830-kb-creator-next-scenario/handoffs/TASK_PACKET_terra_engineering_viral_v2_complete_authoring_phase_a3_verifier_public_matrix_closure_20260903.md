# Task packet — Viral v2 A3 verifier public-matrix closure

## Ownership and fixed state

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only `kb_creator/tests/test_verify_scenario_master_en.py` and one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_verifier_public_matrix_closure_20260903.md`.
- Builder test and both production scripts are fixed. Do not edit them.
- Preserve unrelated edits. Do not touch plan/context, prior receipts, scratch,
  helper/config, candidates, immutable inputs, Git, MASTER_RU, Step 8A,
  HTML/PDF or output.

Bound SHA-256:

- Partial retry receipt:
  `A71656BC312F153A0655666088AEFEBFA8BAA83497987766F4D5B132D35F93F2`.
- Builder: `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`.
- Verifier: `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Builder tests:
  `D7ADB3EC1BC1E38C37B1662F4FA067D2FF9B8564B66670EBBF6EDCFFF63ED965`.
- Starting verifier tests:
  `6E402CA6D3F8421A2D6B8F6244CAFF77546ADBFC1F856BF830F69045CFB22960`.
- Current loader count: 100; all existing baselines pass.

Refuse on any fixed-file hash drift.

## Required independent verifier matrix

Use verifier public top-level preflight/contract path, not builder validator
helpers and not verifier internal schema helpers alone. Add full positive and
single-mutation negative cases for:

- all valid and illegal event-type/source-operation pairs, explicit
  heading-plus-suppress rejection;
- contains exact closure versus unknown, duplicate, incomplete, cross-owner,
  cross-page, reorder and wrong span/child kind;
- asset-owned image-reference positive versus event text, foreign/reused span,
  owner/classification mismatch and invalid placement;
- all eight closed typed schemas as complete source-bound positives;
- equipment/creature/map/pair title-only or missing required fields, extra
  invented fields, foreign/unbound leaves, order/count/membership drift,
  creature nested tables and pair back semantics;
- map/pair without required reader asset ids;
- retain and extend full A3 xref/hierarchy migration public coverage.

Each negative must reach and assert the intended verifier code/seam. Restore
and exceed the prior 102-test loader count with stronger public tests; do not
reactivate invalid legacy positives. If any required mutation is accepted,
stop with minimal public reproduction and do not edit production.

## Verification

Run py-compile, verifier matrix, focused suite, exact normal/reverse
four-module baselines twice, both frozen-v1 preflights, scoped diff, fixed-file
hash recheck and forbidden-output checks. No scratch may remain and the six
pre-existing `.v2-inputs-*` roots are untouched.

End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_REREVIEW`, or
- `PRODUCTION_DEFECT_V2_COMPLETE_AUTHORING_PHASE_A3_VERIFIER_MATRIX`.
