# Task packet — Viral v2 Phase B1b source graph and hierarchy

## Role and scope

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only the author helper, its focused test module and receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_b1b_source_graph_20260903.md`.
- Canonical config and all candidates remain forbidden. Temporary test data may
  exist only under OS temp and must be removed.
- Do not edit builder/verifier/other tests, plan/context, inputs/evidence,
  frozen configs, scratch, Git, MASTER_RU, Step 8A, HTML/PDF/output.

## Bound checkpoint

- B1 receipt SHA-256:
  `23611C725DA8D3CC2ADD3199B42DE0D0E0942014D1CC65B7DE8C57649E213A9D`.
- Starting helper:
  `C96EFC5787ECFD3EE72D7F007F1B05591F5991D3BAB35719AF30CBFB030992F3`.
- Starting tests:
  `8CA23E77954698AE7186DE9D5B5D4EDA96B4D0A533A58782B10E5350A5F08F83`.
- Parent Phase B packet, architecture and A3 approval remain fully binding.

Refuse on drift.

## Required implementation

Extend the B1 foundation with deterministic, tested source-graph materialization:

- normalize all three approved ledgers and split the B1 4,860-slot/346,793-byte
  raw partition only at exact approved boundaries;
- emit ordinary retained source events for every unclaimed authorial span, so
  prose before/between/after overlays cannot disappear;
- materialize the complete 168-row hierarchy from frozen v1 plus exact reviewed
  changes: full source/reader titles, levels, parents, source pages,
  heading/anchor-only/inline-run-in representation and migration ids;
- produce globally monotonic events using source page/start/rank/stable ordinal,
  with exclusive source-span ownership and exact operation/type pairing;
- convert all approved overlay units into the closed A3 typed schemas and exact
  payload bindings: callouts, ordered callout, tables, equipment, creatures,
  run-ins, map and six physical pairs;
- include sealed title/source recoveries and required transformations, including
  full headings and `Cursed Plague Zombies`, with exact evidence identities;
- no placeholder/fallback/summary prose and no lexical title shortening;
- preserve p123/124 as audit-only with zero hierarchy/event/payload leakage.

This slice may keep `author_to()` fail-closed at a new explicit
`E_V2_AUTHOR_ASSET_XREF_MATERIALIZATION_REQUIRED` seam, but only after the full
source partition, hierarchy, events, payload bindings and recoveries are built
and returned by tested public functions. Do not pretend the partial graph is a
full config or call builder/verifier preflight yet.

## Tests and evidence

Add real-input tests for deterministic graph bytes/data, 100% source ownership,
no gaps/overlaps/duplicates, global monotonic order, all 168 hierarchy rows,
full title fidelity, representation/parent closure, ordinary prose survival,
every typed kind/required fixture, exact payload-binding reconstruction,
recoveries, p123/124 exclusion and placeholder bans. Add mutations for ledger
boundary/hash/order, dropped ordinary span, duplicate owner, hierarchy/title/
parent/representation drift, typed omission/invention and recovery evidence.

Run author tests, current 104-test baseline, py-compile, frozen-v1 preflights,
fixed hashes, diff and forbidden-output checks. Canonical config remains absent.

End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C_ASSET_XREF`, or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_B1B` with concrete code/tests and exact
  remaining seam. Do not return analysis-only status.
