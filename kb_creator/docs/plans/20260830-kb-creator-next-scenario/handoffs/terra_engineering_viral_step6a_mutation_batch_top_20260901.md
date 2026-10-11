# Terra engineering receipt: Viral Step 6A TOP mutation batch

- timestamp: `2026-09-01T00:00:00+03:00`
- assignment state: `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION`
- orchestrator policy owner: `gpt-5.6-sol / medium`; engineering owner: `gpt-5.6-terra / medium`
- scoped override: none; this receipt does not transfer orchestration or make a release decision.
- scope: the 21 TOP selector/codes only, under accepted packet sections 5.3, 7.3, 8.1 TOP, 11 and 12.

## Admission and files

- assignment SHA-256: `7AF9C2CB76728F4AA71FBD41584C0B00FDA1B20896DF4613C7C49E870B199039`.
- admitted library baseline: `744551828B9BEF4C7CF8FD4DDE690FFAF23404907269D42BAB7389EDAEFCD841`.
- admitted test baseline: `533D6B3E3345FCD4404A159CDA10548BEC1CFCF9F22214C37163A247EABD640B`.
- changed: `kb_creator/scripts/scenario_source_reconstruction.py` -> `85B158CA0255E97415EAC28836D820CF8FD9AF3BFCB31A667B11FA2C5979E670`; `kb_creator/tests/test_scenario_source_reconstruction.py` -> `299C669293FEC83E10AE39B3A25F6EA2DBC650464258734D5BE2D725D1B7AF15`.
- checked: assignment, accepted packet, plan/status state, those two material files, and this absent-before receipt path. No protected/live/Git/cache/pyc third-file write was made.

## Result

Implemented 21 real explicit TOP callables. The verifier now classifies no-follow physical entries through `FileSystemEntry`; test reparse rows use one immutable `ClassificationOverride` over an actually existing root directory or nested Markdown file, retaining kind, size, file-id and a non-null tag while setting the reparse bit. The production `_reject_reparse` path is used. Forbidden classes are checked before closed topology and have the exact distinct codes. Final candidates enforce the exact 502-file closed physical topology and empty protected subtrees.

Every TOP node follows `apply_case`: fresh bundle, physical mutation, literal empty reseal tuple, one `_test_verify` call, exact `ReconstructionStop.code`, uppercase `PASS` MutationAudit result, zero outside reads, no undeclared change, and no tmp residue.

## Ordinal closed audit matrix

All rows have `declared_reseals=[]`, `strict_verify_calls=1`, `outside_fixture_reads=0`, `undeclared_changes=[]`, `residue=[]`, and `result="PASS"`; their per-row `MutationAudit.as_json()` before/after selector SHA-256 values are generated from each fresh fixture by the asserted `apply_case` protocol.

| # | case_id | semantic selector | expected = observed |
|---:|---|---|---|
| 1 | TOP-candidate-root-wrong | candidate#/root | E_CANDIDATE_ROOT |
| 2 | TOP-candidate-root-escape | candidate#/escape | E_PATH_ESCAPE |
| 3 | TOP-candidate-root-reparse | candidate#/reparse | E_PATH_REPARSE |
| 4 | TOP-nested-reparse | candidate/pages/page-001.md#/reparse | E_PATH_REPARSE |
| 5 | TOP-root-file-missing | candidate/RECONSTRUCTED_EN.md#/physical-entry | E_TOPOLOGY_MISSING |
| 6 | TOP-root-entry-extra | candidate/EXTRA.txt#/physical-entry | E_TOPOLOGY_EXTRA |
| 7 | TOP-evidence-file-missing | candidate/evidence/COMMANDS.json#/physical-entry | E_TOPOLOGY_MISSING |
| 8 | TOP-evidence-file-extra | candidate/evidence/EXTRA.json#/physical-entry | E_TOPOLOGY_EXTRA |
| 9 | TOP-page-missing | candidate/pages/page-001.md#/physical-entry | E_TOPOLOGY_MISSING |
| 10 | TOP-source-render-missing | candidate/renders/source/page-001.png#/physical-entry | E_TOPOLOGY_MISSING |
| 11 | TOP-sheet-missing | candidate/renders/contact_sheets/sheet-001.png#/physical-entry | E_TOPOLOGY_MISSING |
| 12 | TOP-engine-payload-missing | candidate/engine/payload-001.bin#/physical-entry | E_TOPOLOGY_MISSING |
| 13 | TOP-protected-empty-subtree-nonempty | candidate/assets/probe.bin#/physical-entry | E_PROTECTED_EMPTY_SUBTREE |
| 14 | TOP-forbidden-pdf | candidate/forbidden.pdf#/physical-entry | E_CANDIDATE_FORBIDDEN_PDF |
| 15 | TOP-forbidden-compiled-suffix | candidate/forbidden.pyc#/physical-entry | E_CANDIDATE_FORBIDDEN_COMPILED |
| 16 | TOP-forbidden-pycache | candidate/__pycache__/probe.bin#/physical-entry | E_CANDIDATE_FORBIDDEN_PYCACHE |
| 17 | TOP-forbidden-bridge-runtime | candidate/_bridge_runtime/probe.bin#/physical-entry | E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME |
| 18 | TOP-forbidden-cache | candidate/cache/probe.bin#/physical-entry | E_CANDIDATE_FORBIDDEN_CACHE |
| 19 | TOP-forbidden-pytest-cache | candidate/.pytest_cache/probe.bin#/physical-entry | E_CANDIDATE_FORBIDDEN_PYTEST_CACHE |
| 20 | TOP-forbidden-tmp | candidate/tmp/probe.bin#/physical-entry | E_CANDIDATE_FORBIDDEN_TMP |
| 21 | TOP-forbidden-temp | candidate/temp/probe.bin#/physical-entry | E_CANDIDATE_FORBIDDEN_TEMP |

Audit matrix digest: `selector-specific, per-fresh-fixture MutationAudit records; deterministic receipt serialization remains a phase-2 integration responsibility`.

## Verification evidence

- `python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider -k 'TOP-candidate-root or TOP-nested-reparse'` -> `4 passed, 367 deselected`.
- explicit closed topology chunk -> `9 passed, 362 deselected`.
- `-k 'TOP-forbidden'` -> `8 passed, 363 deselected`.
- `-k 'SRC-source-reparse or BLD'` -> `4 passed, 367 deselected`.
- `python -B -m pytest ... --collect-only -q -p no:cacheprovider` -> `371 tests collected`.

## Blockers, risks, next action

No TOP blocker. Risk: later families still retain proxy mutation paths and must not be represented as complete. Next action: orchestrator assigns the next gated family and obtains independent critic review before any release decision.

- elapsed time: approximately 29 minutes.
- token use: unavailable in contributor surface.
