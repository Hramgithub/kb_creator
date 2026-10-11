# Task packet: Viral v2 complete authoring Phase A

## Role and exclusive ownership

- Owner: reuse the same `nri-engineer` (`gpt-5.6-terra`, medium).
- Orchestrator: main chat (`gpt-5.6-sol`, medium).
- You are not alone in the worktree. Preserve concurrent receipts and do not
  revert other files.

Implement Phase A of architecture receipt
`sol_architect_viral_v2_complete_publication_authoring_20260903.md`, SHA-256
`39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`,
on top of approved identity receipt SHA-256
`0B4F6D13D082284CA7186816FF80843DB11B2F4BFB66DFB956438D6B6E334D71`.

Owned Phase A paths only:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a_20260903.md`

Do not edit the author helper/test or create `publication_config_v2.json` in
Phase A. Same engineer retains later exclusive ownership after this checkpoint.

## Required Phase A implementation

1. Extend closed v2 schema with `migration` input/domain ledgers and
   `source_partition.pages/spans`, exact event source provenance
   (`source_span_ids`, `source_operation`, `payload_bindings`), sealed recoveries
   and full hierarchy fields as specified.
2. Builder and verifier independently re-resolve bound inputs and validate raw
   UTF-8 byte partitions, per-page adjacency/coverage/hashes, line/EOL totals,
   event ownership/order, payload authorial leaf bindings, recovery/title
   transformations, six-domain migration closure and 123-row asset migration.
3. Preserve exact v1 route, approved reconstruction-package identity and
   candidate-output inventory semantics.
4. Update synthetic v2 fixtures to the new schema and add compact positive and
   negative cases proving: full tiny-page partition; missing byte/nonblank/blank
   byte; overlap/duplicate/reorder; unbound/invented payload leaf; migration
   missing/duplicate row; hierarchy drift; asset missing/duplicate/p123 leak;
   output-ledger-valid/source-partition-invalid and inverse.
5. Do not make current partial helper acceptable. Real Viral config/candidate
   execution remains forbidden.

## Checkpoint verification

Run both focused modules, current 73-test four-module baseline, py_compile and
both real v1 preflights. Record exact counts/hashes. Confirm frozen identities,
no config v2, no candidate D and no input inventory. Return
`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B` only if all Phase A acceptance tests
pass; otherwise precise blocker. No Git.
