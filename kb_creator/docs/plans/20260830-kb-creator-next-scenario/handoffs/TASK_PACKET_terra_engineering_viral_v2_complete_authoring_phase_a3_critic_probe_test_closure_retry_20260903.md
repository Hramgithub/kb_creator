# Task packet — Viral v2 A3 critic-probe test closure retry

## Fixed scope

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Production is fixed. Own only the two focused test modules and one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_critic_probe_test_closure_retry_20260903.md`.
- Do not edit production unless a required public probe proves a new defect;
  then stop with minimal repro and no production edit.
- Preserve unrelated edits. Do not touch plan/context, prior receipts, scratch,
  helper/config, candidates, immutable inputs, Git, MASTER_RU, Step 8A,
  HTML/PDF or production output.

## Bound identities

- Critic changes-required receipt:
  `67BB38E33B7191D4061A6380A252ED9119A1931DFEF4273426D82616E520C6B7`.
- First test-closure defect receipt:
  `1C0A0A84C42B686C778D595A445995D78E5DEDEB15A30F46F11A4BA6C576188B`.
- Xref remediation receipt:
  `BBDD39B0DC37CA452D2A7C6DD6A2E1A78CE0CB0EDC70EFFD2280C8C33355DCD6`.
- Fixed builder:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`.
- Fixed verifier:
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Starting builder tests:
  `0F89CAE64C6EF7EE2621F1BBB2DB8B6C0309DD8D9406ADDF8D79D7B1A3F74937`.
- Starting verifier tests:
  `80BDF2A05D5E0B7049D1B2A059D3D12DCDE51321AF681FC0E79AFCEC788B993D`.
- Four-module loader count is currently 102 and normal/reverse pass.

Refuse on production hash drift.

## Required closure

Complete the matrix stopped by the first proven defect. Existing xref public
tests count only if they include positive full shape plus missing/extra/foreign
slice, text, target, exact migration, wrong-domain and hierarchy drift.

Add independent public-path coverage in both test modules for:

- every valid and illegal event-type/source-operation pair;
- `contains` exact positive plus unknown, duplicate, incomplete, cross-owner,
  cross-page, reordered and wrong span/child-event kind;
- asset exact positive plus event-text span, foreign asset, reused span,
  missing/mismatched owner, wrong classification and placement;
- all eight typed schemas as complete positive end-to-end fixtures;
- equipment/creature/map/pair required-field omission, extra/invented field,
  unbound/foreign authorial leaf, order/count/membership drift; creature nested
  table and pair semantic-back-text closure;
- every original critic ACCEPT probe: title-only equipment/creature and map or
  pair without reader asset ids must reject in both public paths.

Tests must reach the intended seam. Builder negatives assert destination
absence. Verifier must not rely on builder validator helpers.

Run py-compile, targeted matrix, full focused, exact normal/reverse four-module
baselines twice in fresh processes, both frozen-v1 preflights, scoped diff,
production hash recheck and forbidden-output checks. Do not create or retain
new scratch; do not mutate the six pre-existing `.v2-inputs-*` roots.

End receipt with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_REREVIEW`, or
- `PRODUCTION_DEFECT_V2_COMPLETE_AUTHORING_PHASE_A3_TEST_CLOSURE_RETRY` with
  minimal reproduction and no production edit.
