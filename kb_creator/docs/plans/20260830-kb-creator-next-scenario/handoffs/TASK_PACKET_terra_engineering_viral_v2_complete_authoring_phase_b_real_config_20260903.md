# Task packet — Viral v2 complete authoring Phase B real config

## Role and ownership

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone; preserve unrelated/user edits.
- Own only:
  - `kb_creator/scripts/author_viral_master_en_v2_config.py`;
  - `kb_creator/tests/test_author_viral_master_en_v2_config.py`;
  - absent canonical output
    `kb_creator/working/viral/master_en/publication_config_v2.json`;
  - receipt
    `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_b_real_config_20260903.md`.
- Temporary author outputs are allowed only as unique absent files directly
  under `kb_creator/working/viral/master_en/` and must be removed before handoff.
- Do not edit builder/verifier/visual-QA or existing tests, plan/context, frozen
  inputs/evidence/v1 configs, Candidate C, retained scratch roots, Git,
  MASTER_RU, Step 8A, HTML/PDF, production or any candidate directory.

## Bound approved state

- Architecture receipt SHA-256:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A3 independent approval receipt SHA-256:
  `C6F947123151E3B5F315F7B13D05FD81D43B536BC0CDD0506ED3290ABC26B181`.
- Builder/verifier SHA-256:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`,
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Focused-test SHA-256:
  `EE0F021497A15879A878A83703427DC42DB5AD7D364D87829669A41606BCA376`,
  `1828EE86ED5C994D9C33C1A9AEBC5315E45861B750076EE1E31477F9FB4C8417`.
- Frozen working/reference v1 config SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Accepted reconstruction aggregate: 377 files, 41,079,424 bytes,
  SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Source PDF SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Boundary ledgers:
  - 001--040 `8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF`;
  - 041--068 `8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13`;
  - 069--122 `14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1`;
  - approval `4992A0CC7BA402F999177988241A3D679A7E7B437AD1F9FD8AB0663783547FE3`.

Refuse on any bound hash/identity drift. Read the full architecture, committed
user-review registry, accepted ledger approval, A3 approval and current closed
builder/verifier schemas/tests before editing.

## Required author implementation

The existing helper is an obsolete ledger-only prototype with invented
`Source-backed...` placeholders and old typed field names. Rewrite it; do not
patch placeholders into apparent validity.

Author one deterministic closed v2 config that:

- partitions every accepted reconstruction byte/decoded character for pages
  1--122, including ordinary prose before/between/after reviewed overlays;
- retains the 124-page audit with exactly 1--122 reader and 123--124
  `excluded_advertising`, zero text/event/hierarchy/xref/asset/review leakage;
- derives global event order only from source page/start/rank/stable ordinal;
- fully migrates each frozen-v1 domain exactly once: hierarchy 168, assets 123,
  xrefs 237, source disposition 124, handouts 41, structures 29;
- uses exact decision evidence and exact `hierarchy:<anchor>` /
  `xrefs:<xref_id>` migration identities;
- preserves every full authorial source heading and exact source-bound ordinary
  text; reviewed title differences use sealed recoveries/transformations only;
- implements all registry-required structures: bounded Appearance/Gear/
  Keeper's Notes/Sight/advice callouts; Stream Schedule; all logical tables and
  continuations; Hospital hierarchy/run-ins; DSS equipment card; Devourer and
  Reliquae statblocks with nested infection tables; invisible Infection anchor;
  source-backed `Cursed Plague Zombies`; full-page map p106/107; six exact
  p111--122 front/back pairs; all other reviewed headings/xrefs/assets;
- emits full closed A3 typed payload schemas with every authorial leaf bound to
  exact source slices or one sealed recovery; no invented/fallback/placeholder
  prose is permitted;
- closes all asset outcomes/owners/source spans/placements and derives reader
  assets from all 123 migration outcomes; suppressed/evidence/platform/promo
  assets emit no reader marker; city then boat precede Prologue;
- produces dynamic visual-review units covering every emitted heading,
  structured kind, xref/recovery and reader asset;
- explicitly leaves OUT-008 and ENH-001 deferred and makes no Step 8A binary
  quality choice.

The helper must be deterministic, fail closed, have no network dependency and
never write except an explicitly supplied absent output path. It independently
rereads and hash-binds source PDF, reconstruction, v1 config, ledgers and
decision evidence. It may not import builder validation helpers as authoring
truth; final builder/verifier preflights remain independent gates.

## Author tests before canonical output

Create focused tests covering real-input determinism plus mutation failures for
every bound identity, partition gap/overlap/order/EOL, missing ordinary prose,
heading/title/parent/representation drift, each typed kind, recovery evidence,
xref migration, asset owner/placement/p123 leakage, migration count/duplicate,
placeholder literals and output overwrite/atomicity.

Run author tests plus the current 104-test builder/verifier baseline and both
frozen-v1 preflights. Only after all are green:

1. author twice to two distinct absent temporary files;
2. prove byte equality and SHA-256 equality;
3. run builder and independent verifier `--preflight-only` on both;
4. atomically create the single absent canonical config from one verified byte
   stream without overwriting;
5. run both preflights again on canonical bytes;
6. remove temporary outputs and prove no candidate/scratch/output root exists.

Do not materialize a candidate.

## Receipt and terminal state

Record exact changed files, hashes, config counts, commands, tests, preflight
outputs, frozen-input checks, deterministic equality, defect-fixture presence,
forbidden-output checks and blockers. End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B_REVIEW`, or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_B` with exact uncompleted scope, or
- `BLOCKED_V2_COMPLETE_AUTHORING_PHASE_B` only for unresolvable source proof;
  never guess or weaken the contract.
