# Task packet — Viral v2 B1c3 critic remediation

## Role and exclusive ownership

- Role: fresh `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only the existing six B1c3 author/builder/verifier implementation and
  test files plus receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_b1c3_critic_remediation_20260903.md`.
- Do not edit architecture/critic receipts, plan/context, canonical config,
  candidates, inputs/evidence, other code/tests, Git, assets or downstream.
- You are not alone in the worktree; preserve current work and do not revert
  others.

## Bound checkpoint

- Critic receipt / terminal `CHANGES_REQUIRED`:
  `384176ADD1A6F8DE77033E10BD1471CC8236719035E63A3B1E3433A56DC76C69`.
- Approved architecture / architecture approval:
  `A859B3B2B3B413D7626CE7FD478D9519F798D282ED0E4CB7CFEF863C74769D58`,
  `E42532BADBC83A6DDE2A5C8569B856856DC9741AFA2F603A7BD08D6265F2A760`.
- Starting six files:

```text
author helper   A2F07B072A427FC08E1DE7CD18028F6FE5AA422F557868D2011A51746CAC3DAF
author tests    8E4CDC327170E3CF0273DFD7CF9EF26DC039064CB0913AC3C01C2937A7016326
builder         3677F290D70575EB9868E194A9922A76ACFC4ACE49AB512D0A8EE5DEFDB84004
builder tests   26A463A84AAF1E92532EF8F4A26677A07192157EE7C7B287126CED01269FF4C6
verifier        C111A0C8B73F59BA7948521C02ADD30ECF34C9BDBA5DF1B21B1C1DD4B36B9225
verifier tests  5382C96AB1D2826FF7C0121A96EDCE5F3D27A9DDAAB3DE2C4F263BE18E214BED
```

Refuse on drift. Canonical v2 config and UUID-temp configs are absent.

## Required remediation — all three P1s

### P1 generated-navigation semantics

- Fix author placement: each of exactly four generated events uses its exact
  approved owner and is placed after that owner's heading event, with derived
  page/order; root/page-1 fallback is forbidden.
- In builder and verifier independently reload/derive the frozen-v1 xref row
  catalog and final hierarchy migration/alias closure, then validate every
  generated event and entry field: family, owner, event id, page, placement,
  count, order, source xref id, exact label, exact target, decision `OUT-002`,
  and migration row id.
- Require exactly 135/41/6/12 entries, 194 total, no source spans/payload
  bindings, no duplicate/omitted/reordered/free entry, and zero generated
  representation for the two OUT-026 advertising rows.

### P1 migration materialization and exact target binding

- Add every `generated_navigation_items:<frozen-id>` to independent
  materialized-target closure; require each of the 194 once.
- Close all 237 input xref migration rows against exact frozen identities and
  exact outcomes/targets/decision refs.
- `retained_unchanged` source rows must target exactly
  `xrefs:<same-id>`; `p057-keeper-rulebook` cannot borrow another target.
- The null-decision `p037-handout-21` split must have exactly the two approved
  ordered targets and no extra/reversed/missing target.
- Generated rows must target exactly their same-id generated namespace with
  `OUT-002`; the two advertising rows are targetless with `OUT-026`.
- Reject orphan, duplicate, borrowed, foreign-namespace and pending targets.

### P1 source xref owner binding

- Independently derive each source row/segment frozen owner and require the
  declared `source_event_id` event anchor to equal it exactly.
- Root fallback, adjacency inheritance and merely slice-valid foreign owner are
  forbidden; keep existing exact text/slice/page/event checks.

## Required tests and exit

Turn every direct critic mutation into independently equivalent builder and
verifier tests: generated label, target, decision, entry_count, family,
source_xref_id, migration_row_id, placement, page; empty generated migration
targets; reversed/extra p037 targets; borrowed p057 target; source event anchor
drift. Add missing/duplicate/order/owner/family-count and foreign namespace
mutations where necessary to prove the complete approved contract. Positive
tests must assert correct generated placement/page and exact migration closure.

Run all six py-compiles, focused modules, full combined baseline (starting 114),
both frozen-v1 preflights, guarded UUID-temp builder/verifier v2 preflights,
deterministic serialization, scoped diff/hash and forbidden-output checks.

Both unmutated public v2 preflights must still reach exactly:

```text
builder:  v2 asset provenance mismatch
verifier: E_V2_ASSET: provenance
```

Every critic mutation must fail earlier with the appropriate independent B1c3
error and create no output. Do not begin asset work or weaken/reorder the later
asset gate.

End only with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C3_REREVIEW`, or
- a genuinely new technical blocker with exact reproduction and clean
  forbidden outputs. Progress-only completion is forbidden.
