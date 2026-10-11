# Task packet — Viral v2 A3 critic-probe test closure

## Ownership

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone. Preserve unrelated edits.
- Production is fixed for this assignment: do not edit
  `kb_creator/scripts/build_scenario_master_en.py` or
  `kb_creator/scripts/verify_scenario_master_en.py` unless a new direct probe
  proves a production defect; stop and report that proof before any such edit.
- Own only the two focused test modules and one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_critic_probe_test_closure_20260903.md`.
- Do not touch plan/context, prior receipts, scratch, helper/config, candidates,
  immutable evidence, Git, MASTER_RU, Step 8A, HTML/PDF or production output.

## Fixed identities

- Independent changes-required receipt SHA-256:
  `67BB38E33B7191D4061A6380A252ED9119A1931DFEF4273426D82616E520C6B7`.
- Builder SHA-256:
  `5984748E8591EBD6CA2E94CBD1D7DE8528C8E2126D2BD1D9C22DBAD725441673`.
- Verifier SHA-256:
  `2824437D111E78B1DFC259EEB0C356866978F0F013FBE2B2AD375C126523A0B1`.
- Starting builder-test SHA-256:
  `A6A3CD6CD72801BB66BB47BCC92E139AA23B987757F0F3DD39510E41E9BF7D36`.
- Starting verifier-test SHA-256:
  `64F72B68F89202D39B6FEB4E45FE1D7C4E65EDDA44DB7C1B3C3A6DE853D76876`.
- Current focused and normal four-module baseline: 97/97, `OK`.

Refuse on production hash drift.

## Required test closure

Add direct end-to-end tests in both modules. Traverse public top-level
`v2_config`/`v2_contract` and build/verify paths; helper-only assertions do not
count. Every builder rejection must assert candidate destination absence.

Cover all original critic ACCEPT probes and variants:

1. Full A3 xref with `source_slices` and `migration_row_id` passes top-level;
   legacy/extra/missing/foreign slice, visible-text, target and migration drift
   fail.
2. Every illegal event-type/source-operation pair fails, explicitly including
   heading plus `suppress`; valid pairs pass.
3. `contains` unknown, duplicate, missing/incomplete, cross-owner, cross-page,
   reordered and wrong child-event/span kind fail; exact closure passes.
4. Asset source span pointing to event text, another asset, reused span,
   missing owner, wrong classification or placement fails; exact asset-owned
   image-reference span passes.
5. Title-only equipment/creature and map/pair without reader asset ids reject.
   For equipment, creature, map and pair test each required omission, extra or
   invented field, binding omission/foreign owner, reorder/count/membership
   drift. Add full positive end-to-end fixtures for all eight typed schemas,
   including creature nested tables and pair semantic back text.

Keep test isolation under normal and reverse order. Do not weaken intended
error assertions by accepting an earlier unrelated failure.

## Verification and receipt

Run py-compile; focused tests; exact normal and reverse four-module baselines
twice in fresh processes; both frozen-v1 real preflights; scoped diff check;
production hash recheck; forbidden-output/scratch checks. Do not create real v2
config/candidate/accepted-v4 inventory or mutate the six pre-existing
`.v2-inputs-*` roots.

Record exact commands, counts, final hashes and probe matrix. End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_REREVIEW`, or
- `PRODUCTION_DEFECT_V2_COMPLETE_AUTHORING_PHASE_A3_TEST_CLOSURE` with minimal
  reproduction and no production edit.
