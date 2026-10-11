# Viral v2 reconstruction-package identity — engineering receipt

- Goal: `20260830-kb-creator-next-scenario`, Step 7 MASTER_EN.
- Role: `nri-engineer` / `gpt-5.6-terra`, medium.
- Orchestrator policy owner: main chat / `gpt-5.6-sol`, medium.
- Assignment state: completed implementation; fresh independent review remains required.
- Scoped override: none.
- Timestamp: `2026-09-03T04:45:00+03:00`.

## Scope and result

Implemented exactly the v2-only aggregate reconstruction identity specified by
`sol_architect_viral_v2_reconstruction_identity_20260903.md` (approved SHA-256
`83C917A4A75DBFA8F1EC88ACC5C7248B6D6F772534DD4905DAB9971035664F5D`).

`document.reconstruction_inventory` is no longer admitted by the v2 closed
schema. Its replacement is the closed five-key `document.reconstruction_package`:
safe repository-relative root, file count, total raw bytes, exact aggregate
algorithm text, and uppercase aggregate digest. Builder and verifier each
implement their own recursive all-file scan. It includes an input filename
`INVENTORY.json` if one appears, rejects reparse/symlink/special/empty-directory
topology, and compares count, bytes, then digest before page bindings.

The helper now computes the same aggregate and has no config-output side effect:
its module entrypoint prints a prospective value rather than writing
`publication_config_v2.json`. This task does not remove its separately known
full-partition blocker and does not authorize config or candidate creation.

## Changed paths

- `kb_creator/scripts/build_scenario_master_en.py`
  `D9E60B48A0FF5882FA743EEB1C9560B3CE16B13EAE28873F72006F1BE623E952`
- `kb_creator/scripts/verify_scenario_master_en.py`
  `203084EF6D4A96F696DDB4ECF5C29DF170DEFF35D5A96EED85DE70BF1C5F2A6A`
- `kb_creator/scripts/author_viral_master_en_v2_config.py`
  `3FD74EF9933C2D327A64250F719EAD454A6C998279A61C5F9075E66EA71F1FD7`
- `kb_creator/tests/test_build_scenario_master_en.py`
  `76D513D4F8CA5AD7C5AEA07296343BF79FA6224C22EC09202DA743685DD3BFCA`
- `kb_creator/tests/test_verify_scenario_master_en.py`
  `2B8ACB4E76544C535691BF99A5D677080BB3119CCE2FE5357D51E8B37A612C6D`

No v1 config, accepted v4 reconstruction, source PDF, ledgers, candidate/scratch
root, canonical plan/context, index, commit or push was changed.

## Verification and evidence

- Real accepted v4 independently produces `(377, 41079424,
  68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83)`
  in builder, verifier, and helper aggregate paths.
- New builder and verifier tests exercise that known answer, closed-object
  rejection, stale count/bytes/digest precedence, input `INVENTORY.json` as
  ordinary aggregate material, and empty-directory topology rejection.
- `python -m unittest -v kb_creator.tests.test_build_scenario_master_en
  kb_creator.tests.test_verify_scenario_master_en` passed (the two focused
  modules, including the new cases).
- Full focused baseline command completed successfully:
  `python -m unittest -q kb_creator.tests.test_build_scenario_master_en
  kb_creator.tests.test_verify_scenario_master_en
  kb_creator.tests.test_build_master_en_visual_qa_bundle
  kb_creator.tests.test_propose_scenario_semantic_units`.
  Current discovered count for those four modules is 70; this checkout does not
  expose the historical 86-test count stated in the packet.
- `python -m py_compile` passed for all three changed scripts.
- Real frozen v1 builder and independent verifier preflights both returned
  `preflight_passed`; frozen v1 config SHA remains
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Helper identity probe returned the fixed accepted-v4 aggregate; before/after
  `publication_config_v2.json` existence was `False`/`False`.

## Blockers and next action

No identity-contract blocker remains. The independent architecture blocker
remains: ledgers cover only a special-structure overlay, not a complete source
partition, so config authoring and candidate execution remain closed. Next
action is fresh independent implementation review of this bounded change; do
not reopen config authoring solely on this receipt.

## Accounting

- Elapsed time: approximately 35 minutes.
- Token use: unavailable (platform counter not exposed).

`READY_FOR_V2_RECONSTRUCTION_IDENTITY_REVIEW`
