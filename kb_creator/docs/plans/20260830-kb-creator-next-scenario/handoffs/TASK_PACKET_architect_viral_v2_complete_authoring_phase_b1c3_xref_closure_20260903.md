# Task packet — Viral v2 Phase B1c3 xref closure architecture

## Role and scope

- Role: `nri-architect` / GPT-5.6-sol / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Read-only analysis except one required receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_complete_authoring_phase_b1c3_xref_closure_20260903.md`.
- Do not edit code/tests, plan/context, config, candidates, immutable inputs,
  evidence, Git or downstream.
- You are not alone in the worktree; do not revert or overwrite other work.

## Bound checkpoint

- B1c2 receipt SHA-256:
  `AD46004F0C6C21942C051A183323CBDCB427CAE14BEB0DD678730751A64F7736`.
- Author helper SHA-256:
  `AA5D7DA9A22E81AF79F1DC6056FDAD74675E4B45B9C57716E7E3444763C40C8D`.
- Author tests SHA-256:
  `2489E4E11B6366DF07004374E88379EA646CA52A2605C7A77AA41180D86ACE84`.
- Approved builder/verifier SHA-256 values:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`
  and `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Canonical v2 config/candidates are absent and forbidden.

Refuse on bound-input drift.

## Proven problem

Both public top-level schemas accept `author()`, and 114 combined tests pass,
but both public preflights fail at the same first later seam:

```text
builder:  v2 xref text mismatch
verifier: E_V2_XREF: text
```

Current helper uses synthetic fallbacks for all 237 frozen-v1 xrefs: first
event/span of a page, `target_anchor=viral`, `reader_text=xref_id`, and wrong
materialized migration namespace. Therefore 237/237 text/slice bindings are
wrong.

Read-only diagnosis proves:

- 41 frozen `line_exact` rows contain 42 exact source-backed segments; each
  source line and segment is uniquely locatable in accepted page bytes;
- the row `p037-handout-21` must split into two final xrefs;
- 196 rows are generated navigation: 137 TOC, 41 handout index, 6 map index,
  12 pregen index;
- 127 generated visible texts have no exact occurrence anywhere in sealed
  reader pages and therefore cannot honestly receive source slices;
- two generated TOC rows target excluded advertising;
- four current source events contain exact xref slices belonging to multiple
  semantic owners, so event-boundary splitting or an equivalent closed topology
  is required;
- replacing `reader_text` with the current synthetic span text is forbidden:
  it merely advances to asset provenance while preserving false semantics.

## Required architecture decision

Resolve the apparent conflict between the approved v2 architecture section
"Start with all 237 v1 xrefs" and the A3 invariant that every materialized xref
has exact source-bound `reader_text`/`source_slices` and is emitted inside its
declared event.

The receipt must specify, with exact counts and deterministic rules:

1. final materialized xref inventory for the 42 source segments and all
   generated navigation families;
2. whether generated navigation is represented as source-backed xrefs,
   generated events with a distinct payload schema, or migration-only replaced
   rows, while preserving required reader navigation and link counts;
3. exact migration outcomes, target-id namespaces and decision refs for all 237
   frozen rows, including the split row and excluded-advertising targets;
4. exact owner/event/span splitting algorithm for the four multi-owner events;
5. target-anchor derivation and alias/rebinding rules;
6. required builder/verifier behavior without weakening their independent A3
   source-binding checks;
7. the minimal engineering file scope, ordered implementation stages, focused
   positive/negative tests and stop conditions;
8. which later public-preflight seam is expected after honest xref closure and
   what must remain out of scope.

Do not invent source text, source slices, headings or decision references. If a
schema extension is unavoidable, identify the exact closed fields and why the
current approved contract cannot represent truthful generated navigation.

End with one of:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C3_XREF_ENGINEERING`, or
- `BLOCKED_V2_COMPLETE_AUTHORING_PHASE_B1C3_XREF_ARCHITECTURE` with exact
  missing authority/evidence.
