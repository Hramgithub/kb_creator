# Task packet - Viral v2 B1c7 closed placement decision ledger

## Role and ownership

- Reuse the existing `nri-architect` role (`gpt-5.6-sol` / high contract).
- Orchestration remains with main chat (`gpt-5.6-sol` / medium).
- Architecture/data specification only. Do not edit production code, tests,
  canonical config, candidate, render, source, accepted reconstruction, v1,
  plan/context, protected roots, ignored debug roots or Git state.
- You are not alone in the worktree. Preserve all edits outside the two exact
  deliverables below and do not revert anyone else's changes.

## Bound inputs

Read and bind:

1. the first B1c7 receipt and its 93-row companion inventory;
2. `sol_orchestrator_viral_v2_complete_authoring_phase_b1c7_owner_placement_decisions_20260903.md`;
3. the original B1c7 task packet, live OUT registry and accepted-v4 evidence;
4. only the source PDF/overlay/pages needed to verify exact event boundaries.

The orchestrator decision artifact is authoritative for semantic alternatives
already resolved from fresh source-page inspection. If its event wording is
not directly representable, preserve the decision and specify the minimal
source-event split required; do not replace it with a coarse fallback.

## Required work

1. Produce a new immutable closed placement decision ledger containing all 125
   asset ids: 93 reader rows with one final owner/placement and 32 evidence-only
   rows with exact null placement.
2. Materialize the exact 79 `source_slot` plus 14 `physical_unit_slot` topology,
   or stop with a precise evidence-backed contradiction.
3. For every source slot, freeze immediate previous/next non-asset source event
   ids and the shared-gap ordinal. Define every required event split while
   conserving bytes, xref spans and approved provenance spans.
4. Freeze the seven owner refinements as `reviewed_owner_refinement`, retaining
   frozen-v1 owners as audit provenance without changing B1c4 binary identity.
5. Freeze the seven physical units, their reviewed-to-physical namespace map,
   ordered pages/sides and supplement relation.
6. Recompute counts and closure independently. No null target, unresolved
   status, donor placement, generated-navigation target, nearest-heading
   fallback or authored-array-order oracle may remain.
7. Run only guarded/no-write diagnostics. Prove the unmutated projection reaches
   the exact later migration evidence-schema pair and no output boundary.
8. Specify any minimal hierarchy/event-schema amendment and the exact six-file
   implementation scope. Do not implement it.

## Deliverables and ownership

You own only these new files:

- `sol_architect_viral_v2_complete_authoring_phase_b1c7_closed_placement_ledger_20260903.json`;
- `sol_architect_viral_v2_complete_authoring_phase_b1c7_decision_ledger_20260903.md`.

The Markdown receipt must hash the JSON ledger and all decisive inputs; report
counts, owner refinements, physical units, event-split totals, independent
mutation/test plan, P0/P1/P2 findings, exact next seam and no-output audit.

Terminal must be exactly one of:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C7_ARCHITECTURE_REVIEW`;
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C7_DECISION_LEDGER`.

No implementation begins before a fresh independent GPT-5.5/high architecture
review accepts this ledger and receipt.
