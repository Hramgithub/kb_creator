# Task packet — independent Viral v2 complete authoring Phase A3 review

## Role and scope

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- This is an independent implementation review, not implementation ownership
  and not a release review.
- Do not edit production code, tests, plan/context, helper/config, immutable
  inputs/evidence, candidates, Git, MASTER_RU, Step 8A, HTML/PDF or production.
- Write exactly one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a3_review_20260903.md`.

## Bound evidence

- Architecture receipt SHA-256:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A2 independent approval SHA-256:
  `F1F0877A90A2B66453C024B2C63BEADD85049FA97A29663F6DA12E96F66AF996`.
- A3 engineering receipt SHA-256:
  `7ABD62C980DC04CC2820C094F0A08B395E8907DCA45A9C9729E96239C9E0E9F0`.
- Builder SHA-256:
  `1D2AD6F46F38C7669763A689E04901B99D491F444FD72C0B544E3CC487484F8C`.
- Verifier SHA-256:
  `224C812F73B3C04F9E983759351B07695D0928CA83B39A2A15982333C9B43BAB`.
- Builder tests SHA-256:
  `84EDE819E5D407D9D6287491657DB930769F613B3785D84EADFACCCFFA2FC199`.
- Verifier tests SHA-256:
  `2A7403E71DFB60CF5A0E6E6C8D93BFB62B964995C3F5E52000C7AA80E202B93E`.
- Orchestrator reproduction: py-compile passed and exact four-module baseline
  ran 95 tests in 56.399 seconds, `OK`.

Refuse review if any bound hash differs. Treat the prior A3 READY receipt with
SHA `FE3006E...` as invalid historical evidence; only the bound replacement is
reviewable.

## Required independent review

Read the A3 task packet, architecture receipt, A2 approval and bound A3
engineering receipt completely. Inspect builder and verifier independently;
the verifier must not import builder validation helpers.

Adversarially prove or reject all A3 seams:

- exclusive source-span ownership, strict derived ordering, multi-span
  same-logical-unit rules, foreign intervening content and free-order-key bans;
- exhaustive authorial-leaf payload bindings, exact decoded subranges, joiner,
  duplicate/missing/foreign-owner pointer and extra-authorial-field rejection;
- sealed recovery identity, source/evidence hashes, placement, decision ref and
  reviewed title transformations;
- hierarchy closure, levels, parent order, cycles/orphans, source versus reader
  title, heading/anchor-only/inline-run-in representation and event parity;
- all eight typed kinds, table/card/statblock omission, duplication, reorder,
  count drift, nested infection tables and placeholder bans;
- xref visible-text source slices, target and migration decisions;
- asset source spans, before/after/inside placement, reader policy, full-page
  maps, physical-page pairs and zero page-123/124 leakage;
- complete source partition ownership and builder destination absence after
  every rejected mutation.

Do not infer coverage from test names. Add temporary review-only probes outside
the repository when needed and remove them. Run py-compile, exact focused and
four-module baselines in normal and reverse order, both frozen-v1 preflights,
scoped diff check and forbidden-output checks. Confirm no real v2 config,
candidate, accepted-v4 inventory or review scratch remains.

## Decision

Report P0/P1/P2 findings with exact evidence. Phase B author helper/config and
candidate work may open only if no P0/P1 remains and every required A3 seam is
actually implemented and independently enforced in both modules.

End with exactly one terminal line:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A3`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A3`.
