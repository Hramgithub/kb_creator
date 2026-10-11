# Viral v2 A3 xref migration remediation — engineering receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a3-xref-migration-remediation`.
- Role: `nri-engineer` / requested `gpt-5.6-terra` / medium.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: matched by task packet; actual platform runtime/model is not independently verifiable here.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T08:58:46.1616033+03:00` (Europe/Moscow).
- Elapsed time: approximately 31 minutes.
- Token use: unavailable (the platform did not expose an exact per-assignment counter).

## Scope and result

Bounded implementation completed in the two MASTER_EN validators and their two
focused test modules.  No plan/context/status, helper/config, candidate,
reconstruction, output, Git, MASTER_RU or Step 8A file was edited.

Both independently implemented migration validators now require every
materialized xref to name exactly `xrefs:<xref_id>` in `migration_row_id`, and
require that same exact identity to occur in the closed migration-ledger or
new-reviewed-target closure.  They no longer accept arbitrary nonempty ids,
another xref's id, a hierarchy-domain id, an unknown target, or a target merely
borrowed from aggregate closure.  The analogous hierarchy audit found the same
one-field weakness and independently closes it as exactly
`hierarchy:<anchor>`.

The public builder and independent verifier regression paths prove a complete
A3 xref passes, while migration drift, wrong-domain drift and hierarchy drift
are rejected.  Builder negative probes use `build_candidate()` and assert the
unique candidate destination is absent.

## Bound identities checked before editing

- Critic receipt: `67BB38E33B7191D4061A6380A252ED9119A1931DFEF4273426D82616E520C6B7`.
- Public-path defect receipt: `1C0A0A84C42B686C778D595A445995D78E5DEDEB15A30F46F11A4BA6C576188B`.
- Starting builder: `5984748E8591EBD6CA2E94CBD1D7DE8528C8E2126D2BD1D9C22DBAD725441673`.
- Starting verifier: `2824437D111E78B1DFC259EEB0C356866978F0F013FBE2B2AD375C126523A0B1`.
- Starting builder test: `1C09E5EE3922EF4826D2ED69FF673E06885CD22F2EFE17B0623F91EF5330E136`.
- Starting verifier test: `64F72B68F89202D39B6FEB4E45FE1D7C4E65EDDA44DB7C1B3C3A6DE853D76876`.

## Files changed

- `kb_creator/scripts/build_scenario_master_en.py`
  - independent exact xref and hierarchy materialized-target binding.
- `kb_creator/scripts/verify_scenario_master_en.py`
  - separately implemented equivalent xref and hierarchy materialized-target binding; no builder import.
- `kb_creator/tests/test_build_scenario_master_en.py`
  - extends the existing public A3 builder test with wrong-domain and hierarchy-drift probes; each negative asserts destination absence.
- `kb_creator/tests/test_verify_scenario_master_en.py`
  - adds an independent public verifier-preflight xref migration regression with positive, migration-drift, wrong-domain and hierarchy-drift cases.
- This immutable receipt.

## Verification and evidence

- `python -B -m py_compile kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py`: exit `0`.
- Direct public probes:
  `python -B -m unittest -v kb_creator.tests.test_build_scenario_master_en.A3BuilderPublicClosureTests.test_a3_xref_public_positive_and_all_critic_drift_variants kb_creator.tests.test_verify_scenario_master_en.A3VerifierContractTests.test_a3_xref_migration_identity_public_preflight`: `2` tests, exit `0`.
- Normal four-module matrix:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_propose_scenario_semantic_units`: exit `0`.
- Reverse four-module matrix:
  `python -B -m unittest -q kb_creator.tests.test_propose_scenario_semantic_units kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_scenario_master_en`: exit `0`.
- The same four modules load `102` tests after this addition.
- Frozen-v1 builder `--preflight-only`: exit `0`; contract `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`, reconstruction inventory `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`, source `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Frozen-v1 verifier `--preflight-only`: exit `0`; publication config `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check` over the four assigned modules: exit `0`.
- Verifier builder-import search: absent.
- Forbidden outputs absent after verification: `publication_config_v2.json`, accepted-v4 `INVENTORY.json`, and reconstructed-v4 root `INVENTORY.json`.

## Final scoped hashes

- Builder: `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`.
- Verifier: `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Builder tests: `0F89CAE64C6EF7EE2621F1BBB2DB8B6C0309DD8D9406ADDF8D79D7B1A3F74937`.
- Verifier tests: `80BDF2A05D5E0B7049D1B2A059D3D12DCDE51321AF681FC0E79AFCEC788B993D`.

## Blockers and next action

No blocker remains within this bounded scope.  The worktree contains extensive
pre-existing unrelated modifications and untracked task artifacts; they were
preserved.  This receipt does not make a release decision.

Next action: dispatch the fresh independent A3 implementation review against
the four final hashes, then continue only under the orchestrator's next gated
assignment.

`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3_TEST_CLOSURE_RETRY`
