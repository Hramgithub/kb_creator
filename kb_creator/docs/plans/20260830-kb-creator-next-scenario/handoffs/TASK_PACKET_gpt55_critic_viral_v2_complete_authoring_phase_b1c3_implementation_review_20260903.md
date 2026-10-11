# Task packet — independent implementation review of Viral v2 B1c3

## Role and scope

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Independently review the completed B1c3 xref/navigation implementation;
  do not implement or materially redesign it.
- Own only receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_b1c3_implementation_review_20260903.md`.
- All code/tests, plan/context, config/candidates, inputs/evidence, Git and
  downstream are read-only.

## Bound inputs

- Approved architecture receipt:
  `A859B3B2B3B413D7626CE7FD478D9519F798D282ED0E4CB7CFEF863C74769D58`.
- Architecture approval receipt:
  `E42532BADBC83A6DDE2A5C8569B856856DC9741AFA2F603A7BD08D6265F2A760`.
- Recovery implementation receipt:
  `4C1A5A127AED7A73976F5B1D248A50041394DFB5309BA8DE011773686DFBD66C`.
- Final six owned files:

```text
author helper   A2F07B072A427FC08E1DE7CD18028F6FE5AA422F557868D2011A51746CAC3DAF
author tests    8E4CDC327170E3CF0273DFD7CF9EF26DC039064CB0913AC3C01C2937A7016326
builder         3677F290D70575EB9868E194A9922A76ACFC4ACE49AB512D0A8EE5DEFDB84004
builder tests   26A463A84AAF1E92532EF8F4A26677A07192157EE7C7B287126CED01269FF4C6
verifier        C111A0C8B73F59BA7948521C02ADD30ECF34C9BDBA5DF1B21B1C1DD4B36B9225
verifier tests  5382C96AB1D2826FF7C0121A96EDCE5F3D27A9DDAAB3DE2C4F263BE18E214BED
```

The orchestrator independently reproduced 114/114 combined tests, canonical
v2 config absent and zero UUID temp configs. Refuse on bound drift.

## Required independent review

Do not rely on the receipt or green tests alone. Inspect and adversarially probe
both implementations against the complete approved architecture:

1. recompute exact inventories: 166 reader hierarchy, 42 source operations,
   41 source links, one exact non-link, four generated events, 194 generated
   items, 236 total operations, 235 internal links, 237 migration inputs;
2. prove exact source segment/slice/event/owner binding and no byte loss/reuse
   in the 34-event replacement topology, while preserving 16 asset-owned spans;
3. prove `emit_link:false` is limited to the exact external row and cannot hide
   an unresolved internal target;
4. prove generated labels, targets, order, owners, decision refs and counts are
   independently re-derived from frozen-v1 and final hierarchy migration;
5. prove the null-decision split exception is limited to the one exact frozen
   multi-segment row and cannot authorize lexical/target/order drift;
6. prove both excluded advertising rows/anchors are absent from reader output
   but conserved in migration under OUT-026;
7. prove migration materialized-target closure across `xrefs:` and
   `generated_navigation_items:` namespaces with no fallback/cycle/fan-out;
8. confirm builder and verifier implementations are independent and candidate
   bytes, not trusted config metrics, are authoritative for emitted links;
9. inspect the positive/negative matrix for all architecture-mandated mutation
   classes and run additional direct probes where coverage is doubtful;
10. independently run public UUID-temp v2 preflights and confirm exact first
    later seams `v2 asset provenance mismatch` / `E_V2_ASSET: provenance`, plus
    canonical/temp absence.

Classify every finding P0/P1/P2. Missing mandatory negative coverage, an
acceptance path that permits false source/generated semantics, builder/verifier
common-mode trust, wrong count/conservation, or a different public first seam is
at least P1. Do not approve a partial implementation because the next phase can
repair it.

End with exactly one terminal decision:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C3_IMPLEMENTATION`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C3_IMPLEMENTATION`.
