# Task packet — Viral v2 B1c3 implementation rereview

## Role and scope

- Role: fresh `nri-independent-critic` / GPT-5.5 / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Independently rereview only the remediated B1c3 implementation, with emphasis
  on the prior three P1 acceptance paths. Do not implement or redesign.
- Own only receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_b1c3_implementation_rereview_20260903.md`.
- Everything else is read-only.

## Bound identities

- Prior critic `CHANGES_REQUIRED` receipt:
  `384176ADD1A6F8DE77033E10BD1471CC8236719035E63A3B1E3433A56DC76C69`.
- Remediation receipt:
  `4EB25D4BBFAD3F3B9BB64779D5E258C56E1777B499E0F2F1240E94301C3EACF0`.
- Approved architecture / architecture review:
  `A859B3B2B3B413D7626CE7FD478D9519F798D282ED0E4CB7CFEF863C74769D58`,
  `E42532BADBC83A6DDE2A5C8569B856856DC9741AFA2F603A7BD08D6265F2A760`.
- Remediated six files:

```text
author helper   5F0B1E7FEDE3B589012306C561125B87ED9BCBAEA0A18BED5E3853ECAC9AD666
author tests    AC8395CA15B1889359F794FE617C0F4F912155C1EF7D471761B9057CA1C1CF98
builder         A1602EEC138FDD54CB16BC0C53629347603B624AA6014609961B00B1C9250F28
builder tests   BE1AFABE94AAA7CFC07DB26529B362D418D18C228A7F11CDC61D59F276546207
verifier        6783D5ACE3133F9CD9BF698AAD554D54A0FD3BA8952170DA9024BDF997590FCB
verifier tests  8D1DF368C878FA59E3C05D5E5712B72D9EAAFCE88AC094102C73AEF68C61AEEB
```

The orchestrator independently reproduced 116/116 combined tests, exact
unmutated asset-provenance seams, canonical absent and temp count zero. Refuse
on drift.

## Required rereview

Repeat the prior direct public mutation probes against both builder and
verifier; do not accept test presence as proof:

- every generated event/entry field: label, target, decision, entry count,
  family, source xref id, migration row id, owner, placement, page and order;
- missing/duplicate/reordered generated item and wrong family cardinality;
- empty/borrowed/foreign generated migration target;
- reversed, missing or extra p037 split target and any lexical/target/order
  weakening of the null-decision mechanical exception;
- borrowed p057 target or hidden internal link through `emit_link:false`;
- source-xref event anchor/owner drift with otherwise valid slices;
- alias root fallback, cycle/fan-out and materialized target duplication/orphan.

Independently confirm that validator ordering rejects each mutation before the
asset gate and produces no candidate, while the unmutated object still reaches
exactly builder `v2 asset provenance mismatch` and verifier
`E_V2_ASSET: provenance`. Recompute the complete 166/42/41/1/194/236/235/237
inventory, four owner-heading placements and 34-event topology. Verify builder
and verifier do not share implementation authority and that frozen-v1 is the
source of generated/source semantics. Run the assigned 116-test baseline and
forbidden-output/temp checks.

Classify P0/P1/P2. Any surviving prior mutation, common-mode trusted author
field, target borrowing, owner drift, count mismatch, different first seam or
post-rejection output is P1 or higher.

End with exactly one terminal decision:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C3_IMPLEMENTATION`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C3_IMPLEMENTATION`.
