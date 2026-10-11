# Task packet — Viral v2 Phase B1c3 xref/navigation engineering

## Role and exclusive ownership

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only:
  - `kb_creator/scripts/author_viral_master_en_v2_config.py`;
  - `kb_creator/tests/test_author_viral_master_en_v2_config.py`;
  - `kb_creator/scripts/build_scenario_master_en.py`;
  - `kb_creator/tests/test_build_scenario_master_en.py`;
  - `kb_creator/scripts/verify_scenario_master_en.py`;
  - `kb_creator/tests/test_verify_scenario_master_en.py`;
  - receipt
    `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_b1c3_xref_engineering_20260903.md`.
- Do not edit plan/context, other code/tests, canonical config, candidates,
  immutable inputs/evidence, Git or downstream.
- You are not alone in the worktree; preserve and adapt to others' edits only
  inside the exact owned paths. Never revert unrelated work.

## Bound approved checkpoint

- B1c3 architecture receipt:
  `A859B3B2B3B413D7626CE7FD478D9519F798D282ED0E4CB7CFEF863C74769D58`.
- Independent architecture approval:
  `E42532BADBC83A6DDE2A5C8569B856856DC9741AFA2F603A7BD08D6265F2A760`.
- Starting author helper/tests:
  `AA5D7DA9A22E81AF79F1DC6056FDAD74675E4B45B9C57716E7E3444763C40C8D`,
  `2489E4E11B6366DF07004374E88379EA646CA52A2605C7A77AA41180D86ACE84`.
- Starting builder/tests:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`,
  `EE0F021497A15879A878A83703427DC42DB5AD7D364D87829669A41606BCA376`.
- Starting independent verifier/tests:
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`,
  `1828EE86ED5C994D9C33C1A9AEBC5315E45861B750076EE1E31477F9FB4C8417`.

Refuse on drift. Canonical `publication_config_v2.json`, candidates and temp
artifacts are absent and must remain absent after every command.

## Required implementation

Implement the approved B1c3 receipt exactly; it is normative in full. Do not
replace it with a smaller compatible model.

Required closed outcomes:

1. deterministically refine the four coarse multi-owner events into exactly 34
   replacement events without byte loss/reuse and bind each exact xref line to
   its frozen owner;
2. author exactly 42 strict source-backed xref operations from 41 frozen
   `line_exact` rows: 41 emitted links and exact non-link
   `p057-keeper-rulebook`; split `p037-handout-21` into the two approved ordered
   segment ids;
3. remove only the two OUT-026 advertising hierarchy targets so final reader
   hierarchy is 166 while migration input remains 168;
4. add the narrow conditional `emit_link` source-xref contract independently
   to builder and verifier without weakening exact source slice/event/owner
   checks;
5. add exactly four closed `generated_navigation` events with 194 entries in
   the approved 135/41/6/12 family counts, owners, order and generated placement;
6. derive every generated label/target independently from its frozen-v1 row and
   hierarchy migration; no free label, target, source slice or root fallback;
7. render and independently verify 194 generated links, 41 source links and one
   non-link: 236 materialized operations and 235 emitted internal links;
8. close all 237 frozen xref migration rows exactly: 40
   `retained_unchanged`, one narrowly mechanical null-decision `split`, 194
   `replaced` with `OUT-002`, two targetless `excluded_advertising` with
   `OUT-026`; audit both `xrefs:` and `generated_navigation_items:` targets;
9. derive metrics from materialized/candidate bytes, never from trusted author
   constants; keep builder and verifier implementations independent.

The only permitted null-decision split is the exact one-to-one ordered
projection of every pre-existing frozen segment with unchanged text, target and
link policy. General semantic split bypass is forbidden.

## Tests and stop conditions

Add focused positive coverage for all exact counts, owners, p037 order,
non-link behavior, 166 hierarchy targets, 34-event topology, 237-row migration,
235 candidate links, aliases and deterministic bytes. Add independently
equivalent builder/verifier mutations for source text/slice/event/owner,
unsplit/reversed p037, linked external row, advertising leakage, every generated
entry field/order/family/source-id/decision, forbidden generated slices,
missing/duplicate items, alias cycle/fan-out/root fallback, foreign/borrowed
migration target, unsplit multi-owner event, straddling/reused bytes, stale
counts and post-rejection output creation.

Run:

- py-compile for all six owned Python files;
- focused author, builder and verifier modules;
- the combined author/builder/verifier baseline (starting count 114);
- both frozen-v1 public preflights;
- both public v2 UUID-temp preflights;
- deterministic serialization, scoped `git diff --check`, hash and forbidden
  output/temp checks.

Expected exact next public-v2 seam after complete B1c3:

```text
builder:  v2 asset provenance mismatch
verifier: E_V2_ASSET: provenance
```

Any earlier/different public failure, count drift, source ambiguity, builder /
verifier disagreement, weakened gate, or residual temp/canonical/candidate is a
blocker. Do not begin asset placement, typed payload, visual-review or recovery
work and do not fill anything with synthetic spans.

End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C3_IMPLEMENTATION_REVIEW`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C3_XREF_ENGINEERING` with
  exact remaining code-backed seam. Analysis-only completion is forbidden.
