# Task packet — Viral v2 Phase A3 critic remediation

## Role and ownership

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone; preserve unrelated/user edits.
- Own only `kb_creator/scripts/build_scenario_master_en.py`,
  `kb_creator/scripts/verify_scenario_master_en.py`, their two focused test
  modules, and one new receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_critic_remediation_20260903.md`.
- Do not edit the rejected review receipt, plan/context, helper/config,
  immutable evidence, scratch directories, candidates, Git, MASTER_RU,
  Step 8A, HTML/PDF or production.

## Bound state

- Architecture receipt:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- Rejected A3 engineering receipt:
  `7ABD62C980DC04CC2820C094F0A08B395E8907DCA45A9C9729E96239C9E0E9F0`.
- Independent changes-required receipt:
  `67BB38E33B7191D4061A6380A252ED9119A1931DFEF4273426D82616E520C6B7`.
- Starting production hashes: builder
  `1D2AD6F46F38C7669763A689E04901B99D491F444FD72C0B544E3CC487484F8C`,
  verifier
  `224C812F73B3C04F9E983759351B07695D0928CA83B39A2A15982333C9B43BAB`.
- Starting test hashes: builder
  `84EDE819E5D407D9D6287491657DB930769F613B3785D84EADFACCCFFA2FC199`,
  verifier
  `2A7403E71DFB60CF5A0E6E6C8D93BFB62B964995C3F5E52000C7AA80E202B93E`.
- Orchestrator reproduces 95/95 four-module tests before remediation.

Refuse to start on hash drift. Read the full critic receipt and architecture.
Do not weaken any existing A1b/A2/A3 invariant.

## Required remediation

Implement independently in builder and verifier:

1. Align top-level closed xref schema with A3: exact
   `source_slices` and `migration_row_id` are admitted and required, legacy
   under-specified rows rejected, and the same real row passes top-level plus
   A3 validation/build/verify.
2. Add a closed event-type/source-operation compatibility matrix. A heading
   cannot `suppress`; emitting, generated navigation, source recovery, anchor
   only, asset reference and suppression semantics must match event type and
   reader emission. Reject every illegal pair in both modules.
3. Close every `contains` entry to an actual event-owned partition span or
   real child event id, with exact ownership/order/type rules. Reject unknown,
   cross-owner, duplicate, reordered and incomplete membership.
4. Require each asset `source_span_ids` to name unique image-reference spans
   owned by that exact asset. Reject event-owned text spans, foreign assets,
   reuse and missing ownership while retaining exact before/after/inside
   placement and reader-policy rules.
5. Replace permissive typed payload checks with closed kind-specific schemas.
   At minimum enforce source-bound required fields for equipment title/stats/
   footnote/body; creature title/subtitle/characteristics/derived stats/
   attacks/abilities/nested tables; full-page map reader asset ids/accessibility
   key/legend/scale; physical-page-pair front/back asset membership and semantic
   back text. Missing source content is absent only where architecture marks it
   optional; required omission, invented field, extra field, reorder/count
   drift and unbound authorial leaves must fail.

Add direct reproductions for every critic ACCEPT probe and full positive
end-to-end miniature rows. Builder negative tests must assert destination
absence. Keep verifier independent from builder helpers.

## Verification

Run py-compile, focused tests, exact normal and reverse four-module baselines,
both frozen-v1 real preflights, scoped diff check and forbidden-output checks.
Do not create real v2 config/candidate/accepted-v4 inventory or retain scratch.
Do not delete or modify the six pre-existing `.v2-inputs-*` directories; they
are separately classified by orchestration.

Receipt must include final hashes, exact test counts/commands, mutation matrix,
destination-absence and forbidden-output evidence. End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_REREVIEW`, or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_A3_CRITIC_REMEDIATION` with exact gaps.
