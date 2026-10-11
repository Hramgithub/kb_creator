# Terra engineering receipt: Viral Step 6A REP/SRC mutation batch

- scope: the assigned 20 REP/SRC negative nodes only, the two assigned material
  files, and this new receipt. No plan, context, project status, source,
  sidecar, candidate, recovery, cache, Git, or protected/live surface was
  written by this batch.
- result: `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION`. All 20 assigned nodes
  use a distinct real repository/source/sidecar mutation, literal reseal tuple,
  exactly one real `_test_verify` call, and exact `ReconstructionStop.code`.
  This does not claim completion of the other 348 negative nodes or a release.
- assignment: `sol_orchestrator_viral_step6a_terra_mutation_batch_rep_src_20260901.md`,
  SHA-256 `175DE9BC099FD9B25D1B02ADA1C5D0D5F2D783B14AD9E359F0D03A6FFB300229`.
- accepted design read: remediation packet sections 5.3, 7.3, 8.1 REP/SRC,
  and 11; no new architecture packet was requested or created.
- baselines confirmed before write: library
  `EB3421D2205E1D54D4A7B4EA54BA7E09B7B8E057C704D8CED0D0748AA97CCB71`;
  test `C345128969C76B9DB4FB5963866D0D44C07C9AFC9DDEAA9A1CF3D0394DF66A6F`.
- changed files:
  - `kb_creator/scripts/scenario_source_reconstruction.py`
  - `kb_creator/tests/test_scenario_source_reconstruction.py`
  - this receipt
- final hashes: library
  `C413F87F95C33B577F34E5A5CD80611166D8A62B1152D67AD361399AA34CA82E`;
  test `C3B4EA8129FD39DF6AD3D76558D93D9E89207D6A401AD26462AF4D7F3573B95A`.

## Result and implementation evidence

The library now admits a sealed test source through a physical source/sidecar
verifier seam in phase 3 after repository admission and before candidate
topology. It checks physical entry/type/reparse classification, source path,
bytes and hash, raw sidecar seal, working-source fields, page geometry and
rotation, and all specified policy flags. The reparse row uses a real physical
entry plus the sealed fixture filesystem-provider classification override; it
does not privilege-skip symlink creation.

The test material defines `apply_case` and `reseal_transport`. Each assigned
case snapshots fixture state, performs one named semantic mutation, uses its
literal tuple, invokes `_test_verify` once, asserts the exact code, and returns
the frozen `MutationAudit` record. Sidecar semantic rows declare
`(SIDECAR, PROFILE)` and only re-seal `sidecar#/raw_sha256`; repository and
direct-path rows declare `()`.

Canonical audit digest is SHA-256 of ordinal UTF-8/LF lines
`case_id|expected_code|semantic_selector`:
`7DCBA9FFA59F41DB825D9CCB6CEC1004E441FB75C53CF4D4303A43A71384100B`.

```jsonl
{"case_id":"REP-branch-wrong","expected":"E_REPO_BRANCH","observed":"E_REPO_BRANCH","selector":"repository#/branch","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"REP-head-wrong","expected":"E_REPO_HEAD","observed":"E_REPO_HEAD","selector":"repository#/head","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-source-byte-identical-alias","expected":"E_SOURCE_PATH","observed":"E_SOURCE_PATH","selector":"source#/path","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-source-external-locator","expected":"E_SOURCE_EXTERNAL_FORBIDDEN","observed":"E_SOURCE_EXTERNAL_FORBIDDEN","selector":"sidecar#/external_locator","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-source-missing","expected":"E_PATH_MISSING","observed":"E_PATH_MISSING","selector":"source#/physical-entry","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-source-bytes-wrong","expected":"E_SOURCE_BYTES","observed":"E_SOURCE_BYTES","selector":"source#/bytes","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-source-hash-wrong","expected":"E_SOURCE_HASH","observed":"E_SOURCE_HASH","selector":"source#/sha256","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-source-reparse","expected":"E_PATH_REPARSE","observed":"E_PATH_REPARSE","selector":"source#/reparse","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-missing","expected":"E_PATH_MISSING","observed":"E_PATH_MISSING","selector":"sidecar#/physical-entry","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-raw-hash-wrong","expected":"E_SIDECAR_HASH","observed":"E_SIDECAR_HASH","selector":"sidecar#/raw_sha256","reseal":[],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-working-path-wrong","expected":"E_SIDECAR_WORKING_PATH","observed":"E_SIDECAR_WORKING_PATH","selector":"sidecar#/working_source/path","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-working-bytes-wrong","expected":"E_SIDECAR_WORKING_BYTES","observed":"E_SIDECAR_WORKING_BYTES","selector":"sidecar#/working_source/bytes","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-working-hash-wrong","expected":"E_SIDECAR_WORKING_HASH","observed":"E_SIDECAR_WORKING_HASH","selector":"sidecar#/working_source/sha256","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-page-count-wrong","expected":"E_SIDECAR_PAGE_COUNT","observed":"E_SIDECAR_PAGE_COUNT","selector":"sidecar#/working_source/page_count","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-media-box-wrong","expected":"E_SIDECAR_MEDIA_BOX","observed":"E_SIDECAR_MEDIA_BOX","selector":"sidecar#/working_source/media_box","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-rotation-wrong","expected":"E_SIDECAR_ROTATION","observed":"E_SIDECAR_ROTATION","selector":"sidecar#/working_source/rotations","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-runtime-dependency-true","expected":"E_SIDECAR_RUNTIME_DEPENDENCY","observed":"E_SIDECAR_RUNTIME_DEPENDENCY","selector":"sidecar#/policy/runtime_dependency","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-external-path-allowed","expected":"E_SIDECAR_EXTERNAL_ALLOWED","observed":"E_SIDECAR_EXTERNAL_ALLOWED","selector":"sidecar#/policy/external_path_allowed","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-subsequent-path-wrong","expected":"E_SIDECAR_SUBSEQUENT_PATH","observed":"E_SIDECAR_SUBSEQUENT_PATH","selector":"sidecar#/policy/subsequent_path","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
{"case_id":"SRC-sidecar-origin-marked-source","expected":"E_SIDECAR_ORIGIN_POLICY","observed":"E_SIDECAR_ORIGIN_POLICY","selector":"sidecar#/policy/origin","reseal":["sidecar","profile"],"verify_calls":1,"result":"pass"}
```

## Verification

All commands used the offline bundled interpreter, `-B`, and
`-p no:cacheprovider`:

```text
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -vv -p no:cacheprovider -k 'REP or SRC'
=> 20 REP/SRC negative rows passed with exact codes; the same expression also
   selects the three BLD names because `SRC` is present in the test module path.

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -vv -p no:cacheprovider -k 'bld'
=> 3 passed, 368 deselected

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
=> 371 tests collected
```

Protected-surface evidence: `git status --short --branch` retained the
pre-existing unrelated modified governance/configuration files and untracked
work in this shared worktree. This batch added only the two assigned untracked
material paths and this new receipt; no tracked diff was created by this batch.
Branch/HEAD read-only identity: `codex/kb-creator-viral` /
`54607bd3b9362adbb0c4bca64e8751482797f380`.

## Handoff

- blockers: none for the assigned REP/SRC batch. Remaining scope is Phase 2
  integration of the other 348 negative rows; it is explicitly not complete.
- next action: bounded QA independently inspect the 20 callable identities,
  literal tuples, audit rows, exact-code assertions, and the 371 collection;
  then submit the required independent critic review.
- elapsed time: approximately 29 minutes.
- token use: unavailable from this runtime.
- timestamp: `2026-09-01T03:36:11.7908392+03:00`.
- orchestrator policy owner: `gpt-5.6-sol` at medium; this Terra engineer does
  not transfer orchestration ownership.
- assignment state: completed assigned implementation; acceptance/release is
  pending independent QA and critic review.
- scoped override: none.
