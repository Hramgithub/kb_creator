# Engineering recovery packet: Viral Step 6A executable enforcement

## Scope, authority, and outcome

- Goal / step: `20260830-kb-creator-next-scenario` / `6A-executable-enforcement-remediation`.
- Result: `READY_FOR_FRESH_BOUNDED_EXECUTOR`; this is an implementation-mechanical advisory packet, not an acceptance, QA result, release decision, or new architecture.
- Engineering role: `gpt-5.6-terra / medium`; Fast/priority processing is the scoped assignment policy. Actual platform model, reasoning effort, and runtime priority are unavailable to this agent.
- Orchestrator policy owner: main chat `gpt-5.6-sol / medium`.
- Assignment state: bounded engineering assistance; scoped override: Fast/priority processing only.
- Permitted mutation made by this assignment: this absent-before handoff only. Code, tests, candidate, source, recovery, CLI, QA, COMMANDS, plan/context/status, governance/config, Git, and prior receipts stayed read-only. No tests, live `build`, live `remediate`, external source, network, MinerU/OCR/GPU/model, or historical/translation access was run.

The fresh executor must start from the exact partial baseline below, preserve all unrelated worktree changes, and modify only the same two implementation/test files plus its successor receipt. It must not use this packet to weaken, redesign, or substitute the accepted architecture.

## Bound evidence and baseline

Verified accepted artifacts:

| Artifact | SHA-256 |
|---|---|
| accepted architecture packet `sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md` | `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A` |
| accepted design review | `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279` |
| immutable BLOCKED executor receipt | `04F560C6302A1A31ADABF031E682DF99B888F29EB31CB4058A3F3C20D818293C` |
| recovery amendment | `D00FDA5FAC18DD4AD2E37685F6D97339DD168C439956047919110F0DE3B6C031` |
| accepted recovery review | `06C42437C159DDC651504776472F365194F56FE840756D4BB9F62B90B444C8C9` |

Verified recovery baseline:

- `kb_creator/scripts/scenario_source_reconstruction.py`: `71AA57FBE3596E8197D712BB98F777F1B3BF415BC294942FEA23C1A2F6DC2E65`.
- `kb_creator/tests/test_scenario_source_reconstruction.py`: `58CB22083CFF5B7627C2CF8316E107CE1788EE96B141756CCAD6233BA037166D`.
- Handoff destination was absent before this assignment. Worktree status was already dirty with repository-policy and untracked kb_creator files; none was reverted, staged, or otherwise changed here.

## Current implementation mapping

| Accepted requirement | Current symbols / test function | Classification | Mechanical disposition |
|---|---|---|---|
| Sealed production/test profiles and provider binding | `EnforcementProfile`, `EnforcementContext`, `_profile_seal`, `PRODUCTION_PROFILE`, `PRODUCTION_CONTEXT`, `_admit_context` | partial | Retain data-model direction, but extend the context with explicit repository-root observation and sealed provider capabilities. The test profile must be accepted only by underscored entry points; no production-kind test context may be positive. |
| One public/test route through `_execute` and `_strict_verify` | public `preflight/build/remediate/verify`, `_execute`, `_strict_verify`, `_test_verify` | misleading | `_strict_verify` branches to `_verify_test_fixture`, while `_test_preflight` calls production `_preflight_core` and `_test_build` bypasses `_execute`. Replace the test summary branch with the same phased verifier parameterized by a sealed data-only context. Make `_test_preflight`, `_test_verify`, `_test_build` route through `_execute`; preserve public four-`Path` signatures. |
| Strict ordered earliest-error contract | `_verify_test_fixture` field loop; `_core`, `_verify_core`, `_source_gate`, `_recovery_gate` | partial | Production has useful order but inconsistent `ReconstructionStop` strings and broad errors; fixture verification collapses entire families. Implement named ordered phase functions and one `ReconstructionStop.code` per required selector, invoked in the packet order. Every mutation test must assert the first code only. |
| Physical 502 / 501 / 500 production-shaped fixture | `_test_fixture`, `_write_non_qa_bundle`, `_finalize_test_bundle` | misleading | Current fixture writes `bundle.json`, 485 payload bytes, and 16 `authorities/*.json`; it merely declares `fixture_files=502`. The writer also uses `test.*` schemas and cannot produce the real topology. Replace both factory and writer with shared `make_valid_input()` / `_write_non_qa_bundle()` that physically produce the production root, 500 non-QA files, `COMMANDS` as 501, QA as 502, and real 16 authorities. |
| All 16 authorities and closed schemas | `REQUIRED_TEST_AUTHORITIES`, `SCHEMAS`, `_verify_test_fixture`, `_core`, `_verify_core` | partial | The ordered labels exist, and production `SCHEMAS` names 16 documents, but fixture authorities are summaries. Retain the order/constants, replace `authorities/*.json` with production paths and schemas, and enforce each closed top-level shape plus row variants. |
| 368 selector-specific descriptive negative callable registry | `_CASE_COUNTS`, generated `_CASE_IDS`, `_test_fixture`, one parametrized `test_step6a_enforcement_case` | misleading | Counts match, but IDs are generic (`CMD-001`), family prefix chooses one field, and many nodes use source-string assertions. Replace with explicit `MutationCase` entries containing descriptive `case_id`, selector, mutator callable, literal reseal tuple, expected code, and callable identity. No counted `POS`, prefix inference, or observed-code derivation. |
| Deterministic reseal audit | payload `mutation` / `declared_reseal` | absent | Add test-only `reseal_transport(bundle, case)` with literal per-case authorities, protection of the selected JSON pointer, ordinal UTF-8/LF audit rows, before/after semantic hashes, strict-call count, undeclared-change list, and zero outside-fixture reads. |
| `ValidatedReconstructionInput` as the writer input | placeholder `ValidatedReconstructionInput` declaration only | absent | Add the accepted immutable input types (`SourceObservation`, `PayloadFile`, `ContentBlockInput`, `PageInput`, `AssetInput`, `ValidatedReconstructionInput`) and validate all cardinalities/bindings before any write. No dict/candidate copy may feed the writer. |
| Single real writer/finalizer | `_write_non_qa_bundle`, `_finalize_test_bundle`, `_finalize` | misleading | There are two test finalizers and `_finalize` is unused/returns a dummy manifest. Replace with `_write_non_qa_bundle(input, root)` and `_finalize_and_verify(input, owned, context)`; the latter writes COMMANDS once, derives the 501-row inventory, computes QA twice in memory, writes QA once, then calls `_strict_verify`. |
| Real BLD-001/002/003 | BLD branches in `test_step6a_enforcement_case`, `_test_build`, `_build_core` | misleading | Existing BLD uses toy payloads, does not prove staging/marker/file-id transitions, and parity compares two builds. Split into named tests `test_bld_fresh_root_success`, `test_bld_existing_target_refusal_no_mutation`, and `test_bld_finalizer_parity` using the real fixture/writer/finalizer. |
| `OwnedTempRoot`, marker/nonce/file-id, no-replace publication | `OwnedTempRoot`, `BuildVerificationToken`, `_build_core`, `rename_no_replace`, `remove_owned_tree` | partial/misleading | Types are incomplete and unused; UUID staging has no marker, no profile/file-id binding, `Path.rename` is unproven, and exception cleanup is unsafe. Replace with owned-root admission/classification helpers and provider `rename_no_replace`; never use `os.replace`. |
| Safe cleanup | `remove_owned_tree` | misleading | Recursing `rglob` does not bind parent/final/nonce/file-id and can race. Replace with `remove_owned_tree(OwnedTempRoot, context)` that reclassifies no-follow descendants, stops `E_BUILD_TEMP_OWNERSHIP` on any mismatch, and never deletes a final root or retries broadly. |
| Live production `verify()` full graph / branch / HEAD | `_strict_verify` production branch, `_verify_core`, `_core`, `_source_gate`, `_recovery_gate` | partial | Retain live-only production paths and strict root identity. Move branch/HEAD, source/sidecar, recovery, 16 authorities, topology, inventory, page/content/asset/entity/handout/nav/mode/reference/role/COMMANDS/QA validation into the same ordered phased verifier used by the fixture. |

## Reuse versus replacement

Reuse only after re-auditing with the new route: `ReconstructionStop`; `ProfileKind`; profile seal/binding primitives; `OperationPaths`; `FileSystemEntry` (if expanded to no-follow file-id/reparse classification); `candidate_records`, `manifest_digest`, `json_bytes`, `_contained`, `_reject_reparse`, `exact_root`; production graph constants/real schemas; and live-only `_source_gate`, `_recovery_gate`, `_core`, `_verify_core` logic as source for phase-specific checks.

Replace: `_verify_test_fixture`; synthetic `_test_fixture`; generic `_CASE_IDS`; family-to-one-field mutation mapping; all static/source-string case proof; `_write_non_qa_bundle` toy payload writer; `_finalize_test_bundle`; unused `_finalize`; direct `_build_core` branching; `rename_no_replace`; and `remove_owned_tree` recursion. No third code file is needed: the accepted critic explicitly judged the existing library/test allowlist sufficient.

## Required implementation sequence in the two files

1. In `scenario_source_reconstruction.py`, normalize `ReconstructionStop` to expose a stable `.code`; introduce the accepted input records plus `MutationCase`-agnostic shared verifier data (authority order, canonical paths, expected shapes/counts). Keep all public signatures exactly four `Path` arguments.
2. Add sealed providers and `EnforcementContext` fields for repository root observation, no-follow filesystem classification, `rename_no_replace`, and local fixture root. Implement `_admit_context` so only module `PRODUCTION_CONTEXT` reaches public routes and TEST only reaches `_test_*` routes.
3. Refactor `_strict_verify(paths, context, ...)` into a single ordered phase dispatcher. Both live and fixture contexts use it; context providers differ only in admitted data access. Preserve phase order from the accepted packet: profile/route, repository root/branch/HEAD, source/sidecar, contract/snapshot/recovery, root/reparse/topology, schemas, ledger, inventory, page/content/nav/asset/entity/handout/mode/reference/role, COMMANDS, QA. Do not permit a reduced summary verifier.
4. Implement `ValidatedReconstructionInput` validation and `_write_non_qa_bundle(input, root)` for the actual 500-file root: named root entries, production schemas, 124 pages/renders, 31 sheets, 204 engine assets, real evidence/authority JSON. Then implement exactly one `_finalize_and_verify` to create 501 `COMMANDS`, derive canonical 501 inventory, derive QA twice, write QA as 502, and invoke `_strict_verify`.
5. Implement `OwnedTempRoot` lifecycle: same-parent admission, exclusive hidden sibling `.<final>.tmp-<pid>-<nonce>`, exclusive marker containing normalized paths/profile seal/nonce/directory file id; prepublish strict verify; destination recheck; provider no-replace rename; former-temp file-id check; postpublish strict verify; marker removal only after success. Existing target is `E_BUILD_OVERWRITE`; appearing target is `E_BUILD_PUBLISH_RACE`.
6. Replace cleanup with `remove_owned_tree(owned, context)`. It may clean only the provably owned temp and marker before publish after exact no-follow/reparse/file-id/nonce/profile/final-missing checks. Any anomaly is `E_BUILD_TEMP_OWNERSHIP`, stops immediately, leaves evidence, and never touches final/parent. No `shutil.rmtree`, `os.replace`, wildcard, followed-link, final-root, or computed-directory cleanup.
7. In `test_scenario_source_reconstruction.py`, build `make_valid_input(tmp_path)` from deterministic small bytes only. It must never read production candidate/source/recovery/Git and must materialize a fresh physical 500/501/502 bundle with all 16 authorities in their real locations and schemas. Use an injected immutable `ClassificationOverride` for reparse cases instead of creating a Windows link.
8. Declare all 368 `MutationCase` rows explicitly (or expand from explicit declarative selector tables before collection) with the exact accepted descriptive names and family arithmetic: `REP=2, SRC=18, AUT=30, TOP=21, SCH=33, LED=6, INV=18, PAG=28, NAV=15, AST=21, SEM=18, CMD=61, QAV=90, REG=2, INJ=5`. Each row owns one semantic selector and mutator callable, expected earliest code, literal reseal tuple, and callable identity; the registry must reject duplicate/generic/missing IDs and counted POS.
9. Add `mutate_case`, `reseal_transport`, and audit assertions. Ordinary cases change only the selector before reseal; transport edits are limited to the case tuple; invoke `_test_verify` exactly once; assert expected/observed code equality; record the machine-readable audit fields required by section 11. Audit rows sort ordinally and serialize UTF-8/LF.
10. Add the three separately named real BLD tests. BLD-001 proves owned stage/pre/post strict verification/no-replace/postverify/cleanup; BLD-002 snapshots nonempty existing target bytes/kind/file-id and proves no sibling/marker; BLD-003 compares one `_test_build` against independently generated `_write_non_qa_bundle` + `_finalize_and_verify`, including relative bytes, COMMANDS, QA, 502/501/500 manifests, payloads, and ownership transitions.

## Honest fixture and verifier mechanics

`make_valid_input` must construct data, not clone candidate bytes or make a summary. It should assemble immutable `ValidatedReconstructionInput` values with deterministic small Markdown/PNG-like byte payloads, 124 page records, 388 content blocks, 204 assets (112 referenced / 92 unreferenced), 39 entities and handouts, 31 sheets, four open blockers, correct role counts, and all named evidence records. `_write_non_qa_bundle` then produces the physical 500 regular files in the production root layout. It must use the same real JSON schemas/closed shapes expected by `_strict_verify`; only byte payload size can be synthetic.

The finalizer writes actual `evidence/COMMANDS.json` as file 501, enumerates exactly 501 non-QA regular files in ordinal logical-path order, and writes root `RECONSTRUCTED_EN.qa.json` as file 502. The strict fixture route resolves only from the sealed fixture root/provider and records `outside_fixture_reads=0`; it must never consult `repo_root`, subprocess Git, production candidate, source PDF, recovery path, environment, CLI, or provider-prefix shortcuts. `candidate_manifest` assertions must show 500 before finalization, 501 after COMMANDS, and 502 after QA.

The production verifier keeps its live authority checks but uses the same phase functions and errors. It must validate branch/HEAD, the source/sidecar/contract/recovery bindings, complete 16-authority graph, forbidden classes, topology, inventory, page/content/master/nav/asset/entity/handout/mode/reference/role closure, COMMANDS, QA, and no fabricated closure. Error order is contractual: never rearrange checks merely to make a mutation test convenient; each case mutates only enough to reach its named earliest code.

## Intermediate checkpoints and final commands

Run only after the fresh executor has completed each checkpoint; no live build/remediate is allowed.

1. Registry checkpoint: collect focused tests and prove 371 nodes with 368 descriptive negatives and 3 BLD nodes; separately validate unique IDs, callable identity, family totals, literal reseals, and no `POS`.
2. Fixture checkpoint: one valid TEST bundle verifies through `_test_verify`; inspect physical 500/501/502 counts and all 16 authority shapes; run one selector per major phase plus reparse classification, then the entire registry/audit.
3. Writer/ownership checkpoint: run all three BLD tests under `tmp_path`; prove no temp sibling/marker/cache residue on success, and retained evidence only on ownership failure.
4. Production-preservation checkpoint: hash protected candidate/source/recovery/CLI/contract-test/visual/QA/COMMANDS surfaces before and after; run only preflight and two verifies after the exact suites pass.

Exact final command set from the accepted packet:

```powershell
Set-Location 'D:\NRI\.worktrees\kb-creator-viral'

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider

python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider

python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider

python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate

python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate

python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

Required evidence remains exact: `371 collected / 371 passed`; `119 collected / 119 passed`; `490 collected / 490 passed`; native exit 0 for preflight and two verifies; byte-identical verify stdout and SHA-256; unchanged protected hashes; zero `.pyc`, pytest cache, fixture, temp sibling, owner marker, probe, or log residue.

## Non-negotiable stops

Write a truthful BLOCKED successor receipt rather than narrowing work if any requirement cannot fit the two-file allowlist; a third code file becomes necessary; a protected baseline changes; the 16-authority production-shaped fixture cannot be made hermetic; error order cannot match; a case lacks a real mutator/literal reseal/audit; a generic ID, count-only/static-source assertion, summary fixture/verifier, toy writer, split route, provider-prefix admission, public override, relaxed/skip mode, `os.replace`, `shutil.rmtree`, broad cleanup, candidate/source read, live build/remediate, or residue appears.

No design contradiction was found: the accepted independent review explicitly found the two-file allowlist sufficient. The current partial implementation is not compliant evidence even if its claimed 371/119/490 counts are green.

## Handoff audit

- Files checked: root `AGENTS.md`; `kb_creator/PROJECT_STATUS.md`; governance; goal plan/context; all five authority artifacts above; current two baseline files; read-only worktree status.
- Files changed: this handoff only.
- Sole-write audit: destination was absent before creation; no code/test/Git/candidate/source/recovery/QA/COMMANDS or canonical plan/status/governance file was changed.
- Blocker state: no design blocker; implementation remains pending a fresh bounded Luna executor.
- Next action: orchestrator dispatches the fresh executor under the recovery amendment from the exact baseline hashes, then requires fresh Luna-high QA and independent GPT-5.5-high implementation/process review. No semantic/release advancement is authorized.
- Elapsed time: unavailable.
- Token use: unavailable.
- Timestamp: 2026-09-01T03:10:00+03:00.
