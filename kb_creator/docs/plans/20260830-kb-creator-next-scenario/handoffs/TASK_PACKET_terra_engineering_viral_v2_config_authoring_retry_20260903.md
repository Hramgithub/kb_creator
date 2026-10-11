# Task packet: Viral MASTER_EN v2 config authoring retry

## Role and scope

- Fresh `nri-engineer` (`gpt-5.6-terra`, medium).
- Own only the paths listed below. Do not orchestrate, stage, commit, push,
  mutate immutable inputs, or build scratch/Candidate D output roots.
- You are not alone in the codebase; preserve all unrelated edits.

## Goal

Resume the previously blocked v2 config task now that the reviewed boundary
ledger prerequisite is independently approved. Author the real Viral
`publication_config_v2.json` and run config/builder/verifier preflights only.

## Mandatory inputs

Read the original config packet and blocked receipt, the committed user-review
registry, remediation architecture, current builder/verifier v2 schemas/tests,
frozen v1 config, accepted reconstruction v4, semantic evidence, and:

- 001--040 ledger SHA-256
  `8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF`;
- 041--068 ledger SHA-256
  `8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13`;
- 069--122 ledger SHA-256
  `14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1`;
- approving independent rereview receipt SHA-256
  `4992A0CC7BA402F999177988241A3D679A7E7B437AD1F9FD8AB0663783547FE3`.

The ledgers use two compatible field spellings (`source_segments` in the first,
`segments` in the others); normalize explicitly. Sort every unit/event by
declared source order key and source range, never by JSON append order. Hard-stop
on identity/hash/bounds/overlap/order mismatch.

## Owned paths

- `kb_creator/working/viral/master_en/publication_config_v2.json`
- If essential, reusable helper only:
  `kb_creator/scripts/author_viral_master_en_v2_config.py`
- If helper added, focused tests only:
  `kb_creator/tests/test_author_viral_master_en_v2_config.py`
- Receipt only:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_config_authoring_retry_20260903.md`

No other path may change. Builder/verifier/visual-QA code and existing tests are
frozen in this packet.

## Required result

Implement every requirement of the original config packet and accepted
architecture from the three exact ledgers. In particular:

- globally monotonic source-ordered typed events with complete source-title
  fidelity and no duplicate/overlapping emissions;
- bounded Appearance/Gear/Keeper's Notes/Sight/advice callouts;
- all logical tables, stream schedule, hospital hierarchy/run-ins, equipment
  card, creature statblocks, invisible Infection anchor, source-backed recovery;
- exact asset owner/placement, p106/107 map unit and six p111--122 pregen pairs;
- exact 124-page audit/122-page reader disposition, with p123--124 zero leakage;
- OUT-008 and ENH-001 deferred; Step 8A binary choice absent;
- dynamic visual-review units cover every emitted kind.

Bind exact ledger hashes and independent approval receipt in config provenance or
equivalent closed identities allowed by the current schema; do not invent an
unsupported top-level key. Preserve frozen working/reference v1 config hash
`C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Verification

- JSON parse/schema validation.
- Builder v2 preflight and independent verifier v2 preflight without candidate
  materialization. If the CLIs cannot preflight without a root, use their
  documented validation APIs/tests; do not create scratch/Candidate D.
- Focused helper tests if helper is introduced.
- Explicit counts for hierarchy/events/assets/source dispositions/review units,
  and proof of source-order monotonicity, no overlapping emission, no p123/124
  leakage, and all required defect fixtures present.
- Receipt records commands, results, hashes, counts and exact changed paths.

Success token: `READY_FOR_VIRAL_V2_CONFIG_IMPLEMENTATION_REVIEW`. On any schema
or source ambiguity, return `BLOCKED_VIRAL_V2_CONFIG_AUTHORING_RETRY` with exact
evidence; do not weaken policy or guess.
