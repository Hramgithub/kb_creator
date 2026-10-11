# Task packet: implement Viral v2 reconstruction-package identity

## Role and ownership

- Owner: `nri-engineer` (`gpt-5.6-terra`, medium).
- Orchestrator: main chat (`gpt-5.6-sol`, medium).
- You are not alone in the worktree. Do not revert or overwrite other agents'
  edits; accommodate concurrent receipt-only architecture work.

Read and implement exactly
`sol_architect_viral_v2_reconstruction_identity_20260903.md` (SHA-256
`83C917A4A75DBFA8F1EC88ACC5C7248B6D6F772534DD4905DAB9971035664F5D`).

## Owned paths

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/scripts/author_viral_master_en_v2_config.py` only for the new
  aggregate identity and explicit no-write behavior
- optional `kb_creator/tests/test_author_viral_master_en_v2_config.py`
- receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_reconstruction_identity_20260903.md`

## Required implementation

1. Replace v2 `document.reconstruction_inventory` with closed
   `document.reconstruction_package` exactly as specified. No alias/fallback.
2. Builder and verifier independently validate safe root, topology, all-file
   aggregate, CLI equality, counts/bytes/hash and page bindings in specified
   first-error order. Verifier must not import builder code.
3. V2 preflights compare the declaration; verifier report uses the verified
   aggregate. No input inventory file is read or created.
4. Preserve v1 code paths and candidate-output `INVENTORY.json` semantics.
5. Migrate synthetic v2 fixtures and add positive/negative matrix, including
   real v4 known-answer and immutable-tree mutations where safely disposable.
6. The author helper may compute/assert/return the aggregate identity but must
   not write `publication_config_v2.json`; its current completeness defect keeps
   config output closed.

## Verification

- Run full builder and verifier modules.
- Run helper tests if created.
- Run both real v1 builder/verifier preflights and prove v1 config SHA remains
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Run the existing focused 86-test baseline across builder, verifier, visual QA
  and semantic proposer, plus all newly added tests.
- Record exact commands, counts, hashes and any environmental limitation.

## Forbidden

Do not change v1 configs, accepted v4, source PDF, ledgers, review evidence,
`publication_config_v2.json`, candidates/scratch roots, plan/context, Git or any
MASTER_RU/Step 8A/HTML/PDF path. Do not implement the separate full-partition
architecture in this task.

## Output

Receipt must list exact changed files and return
`READY_FOR_V2_RECONSTRUCTION_IDENTITY_REVIEW` only if all acceptance criteria
pass; otherwise return a precise blocker. No staging, commit or push.
