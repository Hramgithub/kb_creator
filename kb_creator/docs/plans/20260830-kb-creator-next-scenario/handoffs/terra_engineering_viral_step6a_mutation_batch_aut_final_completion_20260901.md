# Terra engineering receipt — Viral Step 6A AUT final mutation-batch completion

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-aut-final-completion`
- Role: reusable code/test engineering and implementation
- Policy model / effort: `gpt-5.6-terra / medium`
- Actual platform model / effort: `unavailable`
- Orchestrator policy owner: main chat `gpt-5.6-sol / medium`
- Assignment state: `matched`; platform runtime unverified
- Scoped override: `none`
- Timestamp: `2026-09-01T04:30:00+03:00`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`

## Scope and result

Result: `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION`.

The sole implementation change is the successful `MutationAudit` literal in
`kb_creator/tests/test_scenario_source_reconstruction.py`: `pass` became
the Section-11 binding literal `PASS`; the corresponding success assertion
changed to `PASS`. The failure state remains non-PASS (`residue`). The
library was read-only. No live/protected/Git/cache/.pyc/commit/push action was
performed.

## Immutable inputs and file identities

| Item | SHA-256 | Result |
|---|---|---|
| Library before and after: `kb_creator/scripts/scenario_source_reconstruction.py` | `744551828B9BEF4C7CF8FD4DDE690FFAF23404907269D42BAB7389EDAEFCD841` | unchanged |
| Focused test before correction | `C829BA0601ECCE677FA6627B06A46FEF6CE8A42890BCBF4AD3AD52855DC67F80` | matched required baseline |
| Focused test after correction | `533D6B3E3345FCD4404A159CDA10548BEC1CFCF9F22214C37163A247EABD640B` | expected two-literal change |
| Prior blocked implementation receipt | `93EFF6A299928423212C7A5261221DFBE0114147072E40B3FB4FEC5963211EC7` | unchanged |
| Prior blocked audit receipt | `2C6163A58CD24042245223E0EE9253553EFEA3BD3B1326537942F601DAD72149` | unchanged |

Files changed: this receipt and
`kb_creator/tests/test_scenario_source_reconstruction.py` only. Files checked:
the two material files, current task packet, Section 11 architecture packet,
the two prior immutable receipts, and scoped residue surface.

## Verification and native exits

All commands used `python -B`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, and
`-p no:cacheprovider`.

| Check | Partition | Native exit | Summary |
|---|---:|---:|---|
| AUT exact selected nodes | ordinal 1–10 | 0 | `10 passed in 22.91s` |
| AUT exact selected nodes | ordinal 11–20 | 0 | `10 passed in 22.95s` |
| AUT exact selected nodes | ordinal 21–30 | 0 | `10 passed in 23.34s` |
| REP/SRC exact selected nodes | REP 2 + SRC first 8 | 0 | `10 passed in 22.45s` |
| REP/SRC exact selected nodes | SRC final 10 | 0 | `10 passed in 22.20s` |
| BLD | three named BLD nodes | 0 | `3 passed in 6.23s` |
| focused collect-only | all focused nodes | 0 | `371 tests collected in 0.06s` |
| AUT helper | ordinals 1–10 | 0 | 10 complete closed PASS objects |
| AUT helper | ordinals 11–20 | 0 | 10 complete closed PASS objects |
| AUT helper | ordinals 21–30 | 0 | 10 complete closed PASS objects |

The helper was invoked against isolated OS temporary fixture roots, each removed
by `TemporaryDirectory.cleanup()`. No temporary fixture, probe, pytest cache,
or bytecode was created in the worktree. Scoped inspection found no new
temporary residue. Pre-existing `__pycache__` and historical
`_bridge_runtime/tmp` paths were not modified and are outside this task's
allowlist.

## Section-11 complete AUT audit objects

The following are all 30 `MutationAudit.as_json()` objects in exact registry
ordinal order. Every object has the closed 16-field shape; its real
before/after hashes are uppercase, `result` is `PASS`, one strict verifier
call occurred, and outside/undeclared/residue values are zero/empty.

```json
[
  {
    "case_id": "AUT-contract-argument-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "contract#/path",
    "semantic_before_sha256": "EAB01F0DE11BC5868A1EF1F03727C3F1BF25FFA67C2DD7AD30DCD502ACFB0CB0",
    "semantic_after_sha256": "3C9FDAE04EE8707B1E7911FCB968118CB8BA2AF3D1A73EABC24A861AEDD49422",
    "changed_before_reseal": [
      "contract#/path"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_CONTRACT_PATH",
    "observed_code": "E_CONTRACT_PATH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-contract-raw-hash-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "contract#/raw_sha256",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_after_sha256": "A319FAB8632FD32BC86D56CD604B0EC9D61A92A64B6012563D1DB35E45D6F2A7",
    "changed_before_reseal": [
      "contract#/raw_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_CONTRACT_HASH",
    "observed_code": "E_CONTRACT_HASH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-contract-canonical-content-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "contract#/scenario",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_after_sha256": "2186609E312A1BDEBBB7365A879D04060F05CF58DBE312FE66D73C7D74C33676",
    "changed_before_reseal": [
      "contract#/scenario"
    ],
    "declared_reseals": [
      "contract",
      "profile"
    ],
    "changed_by_reseal": [
      "contract#/raw_sha256"
    ],
    "expected_code": "E_CONTRACT_CANONICAL",
    "observed_code": "E_CONTRACT_CANONICAL",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-snapshot-bytes-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SCENARIO_CONTRACT.json#/scenario",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_after_sha256": "2186609E312A1BDEBBB7365A879D04060F05CF58DBE312FE66D73C7D74C33676",
    "changed_before_reseal": [
      "candidate/SCENARIO_CONTRACT.json#/scenario"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_CONTRACT_SNAPSHOT_BYTES",
    "observed_code": "E_CONTRACT_SNAPSHOT_BYTES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-snapshot-hash-binding-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/contract_snapshot_sha256",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "A572D91E2EC548ABD89664F42E8A32F955030A708104A7CF06C85BBEAB83F417",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/contract_snapshot_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_CONTRACT_SNAPSHOT_HASH",
    "observed_code": "E_CONTRACT_SNAPSHOT_HASH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-contract-sha",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/contract_sha256",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "65E061C13076B5352C25FFC31323AFF08327A2440F7F286B0B5A93455E740172",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/contract_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_CONTRACT",
    "observed_code": "E_SOURCE_IDENTITY_CONTRACT",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-source-bytes",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/bytes",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "46EED45BF4502DD4AE7B0AE15B0FD456ACC4476047ABC781C95B8C118B4E48B4",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/bytes"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_SOURCE_BYTES",
    "observed_code": "E_SOURCE_IDENTITY_SOURCE_BYTES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-source-sha",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/sha256",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "CA21CBBD560AE5B7663128EDDF13DD0155471F899C658E37EF7EFA80F646005B",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_SOURCE_HASH",
    "observed_code": "E_SOURCE_IDENTITY_SOURCE_HASH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-page-count",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/page_count",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "6EABDE6B620A81FCBB54777A4B0C37CD5202C6C3B93C23F0BD5C6A3D40D2E760",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/page_count"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_PAGE_COUNT",
    "observed_code": "E_SOURCE_IDENTITY_PAGE_COUNT",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-media-box",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/media_box",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "AE0482B46566DE4E0ED34F5DAB88999000E4B6CD15895D211EB1327FA8AAD17C",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/media_box"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_MEDIA_BOX",
    "observed_code": "E_SOURCE_IDENTITY_MEDIA_BOX",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-rotation",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/rotations",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "B38504D49302A070091FB7C12B93478DFE092BB3C75306BEB923E1C024A72F89",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/rotations"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_ROTATION",
    "observed_code": "E_SOURCE_IDENTITY_ROTATION",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-recovery-manifest-sha",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "31FBA965781DC18B6D597207C1330C736F283E78604BA93135D44A02DBC7187A",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_RECOVERY_MANIFEST",
    "observed_code": "E_SOURCE_IDENTITY_RECOVERY_MANIFEST",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-recovery-evidence-sha",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "32814D20C0D5EE3FC784B32E8840341156B6FDC060B01D9E05652A99A7BFEC96",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_RECOVERY_EVIDENCE",
    "observed_code": "E_SOURCE_IDENTITY_RECOVERY_EVIDENCE",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-recovery-root",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/recovery_root",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "2E923CD00603ECB8BB7E2622E6ADBAA9110FB029AE2B216DBE3ED92D7B3010E3",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/recovery_root"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_RECOVERY_ROOT",
    "observed_code": "E_SOURCE_IDENTITY_RECOVERY_ROOT",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-history-true",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/historical_material_opened",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "692F6D70411DA9DE36C79CA608496FFD73C39DF60ED4D607D1F027F36334168B",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/historical_material_opened"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_HISTORY",
    "observed_code": "E_SOURCE_IDENTITY_HISTORY",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-source-identity-state-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/state",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_after_sha256": "CFCC6E7563EB9B828E1100F3AAE6122DF2BC80E771BE6369DFC447CE8B3D006B",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/state"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_SOURCE_IDENTITY_STATE",
    "observed_code": "E_SOURCE_IDENTITY_STATE",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-root-wrong",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery#/path",
    "semantic_before_sha256": "F67713C0531745526E1040135C32617E833F373A70953688E1C1FA96E1E378D0",
    "semantic_after_sha256": "CD1BABE8953ABC48C8022C26E599326D12EBF5C71F427FBFDB351F0B2A660349",
    "changed_before_reseal": [
      "recovery#/path"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_RECOVERY_ROOT",
    "observed_code": "E_RECOVERY_ROOT",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-manifest-raw-hash",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "3DE0B82AA36DE8BED1D3A6A1731E9935CA1488DA3CBFACC2C5340EA7A810ADF4",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_RECOVERY_MANIFEST_HASH",
    "observed_code": "E_RECOVERY_MANIFEST_HASH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-evidence-raw-hash",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_after_sha256": "70C3C20C638F9BC68936BDCE612BFC99A18A100A640811E1CD7FF0F3EB8F9F5E",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_RECOVERY_EVIDENCE_HASH",
    "observed_code": "E_RECOVERY_EVIDENCE_HASH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-successor-file-count",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/successor_file_count",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "8342FE497F0A3D94165E6DF528420B525BA263C0E28E954E8A02F57620633BB8",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/successor_file_count"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_FILE_COUNT",
    "observed_code": "E_RECOVERY_FILE_COUNT",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-successor-total-bytes",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/successor_total_bytes",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "74FF69F45A2A134D2933600EDE920EF1A3DB0E8BA6BCF2352950738635EF317E",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/successor_total_bytes"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_TOTAL_BYTES",
    "observed_code": "E_RECOVERY_TOTAL_BYTES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-manifest-row-path",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/0/path",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "15D6AF325712490C99992A5E53291FE10298B9C7DEC626746903FAB61F1E74E4",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/0/path"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_ROW_PATH",
    "observed_code": "E_RECOVERY_ROW_PATH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-manifest-row-bytes",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/0/bytes",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "2D15FE67F6AE23F41DFAE1C8E1AFCDF7DC66F2994915C75C45A6190217491E9A",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/0/bytes"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_ROW_BYTES",
    "observed_code": "E_RECOVERY_ROW_BYTES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-manifest-row-hash",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/0/sha256",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "F88459EF8DDC96DBB43532C53C67FC6AE2C9BA043B1453FB59783848334715FE",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/0/sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_ROW_HASH",
    "observed_code": "E_RECOVERY_ROW_HASH",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-manifest-row-duplicate",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/1/path",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_after_sha256": "A86DC306658F81C6A15B6CDB1AA7C0DE8F32424D81C912F46298C8DDD5E5684F",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/1/path"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_ROW_DUPLICATE",
    "observed_code": "E_RECOVERY_ROW_DUPLICATE",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-forbidden-payload",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/forbidden.pdf",
    "semantic_before_sha256": "2BE4114D79C4727D21A16DD5547BDEE54061AB45D3E40C3B0A80A2A493847723",
    "semantic_after_sha256": "80CBAF94386B00B5734D9C567850CB5F66763F107BC735161C9827FF7E2CFC98",
    "changed_before_reseal": [
      "recovery/forbidden.pdf"
    ],
    "declared_reseals": [],
    "changed_by_reseal": [],
    "expected_code": "E_RECOVERY_FORBIDDEN",
    "observed_code": "E_RECOVERY_FORBIDDEN",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-evidence-source-binding",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/source_identity",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_after_sha256": "BC0B5C06F9F1AB5AA05A5796FA90E42618A52636CD5DB59FC518A11718600228",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/source_identity"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_SOURCE_BINDING",
    "observed_code": "E_RECOVERY_SOURCE_BINDING",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-evidence-payload-binding",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/payload",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_after_sha256": "2E8D245B9F2D6179CA1DB2FFA09CE77A560BE65531DAB4AE6A12EFAF700D6E02",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/payload"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_PAYLOAD_BINDING",
    "observed_code": "E_RECOVERY_PAYLOAD_BINDING",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-allowed-paths",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_after_sha256": "34C9E4DD95E7784647974CF7D9E8A8EDDB6DB4EB548FF8E53BF09C452081C8DF",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_ALLOWED_PATHS",
    "observed_code": "E_RECOVERY_ALLOWED_PATHS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "AUT-recovery-promotion-true",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/promotion",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_after_sha256": "3D3074D5FE0C7CB53FAA734433AC4FD72C24067AB8BBB075FE82930FFA44735A",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/promotion"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_RECOVERY_PROMOTION",
    "observed_code": "E_RECOVERY_PROMOTION",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  }
]
```

Canonical digest input is the 30 ordinal UTF-8/LF records:

`case_id<TAB>semantic_selector<TAB>comma_joined_reseals<TAB>expected_code<TAB>observed_code<TAB>PASS<LF>`

- rows: `30`
- byte length: `4505`
- SHA-256: `301BDCBB1C3D49EBEF8929CEE2DBEB67E428B02C7A7A11F2257B53D33817F911`

## Blockers and next action

Blockers: none for the AUT batch. This is not an integration, independent
review, release, promotion, `MASTER_EN`, commit, or push decision.

Next action: the orchestrator may integrate this completed batch with the
remaining Phase 2 evidence under the canonical plan and request the required
independent review. Do not treat this engineering receipt as a release decision.

- Elapsed time: approximately 24 minutes.
- Token use: unavailable from this runtime.

