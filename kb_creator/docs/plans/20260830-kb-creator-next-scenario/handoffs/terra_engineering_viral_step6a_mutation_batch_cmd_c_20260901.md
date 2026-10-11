# Terra engineering receipt: Viral Step 6A CMD batch C

Timestamp: 2026-09-01 Europe/Moscow.  Assignment state: `COMPLETE` for the
assigned CMD-C surface only; this is not Step-6A acceptance or a release
decision.  Orchestrator policy owner remains main chat `gpt-5.6-sol` / medium.
Scoped override: none.  Terra policy role: reusable code/test engineering /
medium; actual runtime token telemetry: unavailable.

## Scope and result

Implemented the 15 descriptive CMD-C cases, replacing the former generic
`CMD-sheet-selector-NN` placeholders.  The one shared strict verifier now
enforces COMMANDS v3 physical 31-sheet count/set/id/path/grid/hash, ordered
2x2 flattened pages 1..124, sheet and global page-render path/hash/mapping,
and `verify_deterministic=true`.  Each case uses its own COMMANDS JSON
mutation callable, literal `(inventory, qa)` transport reseal, one
`_test_verify` call, and the existing closed 16-field `MutationAudit` route.

The ordered cases and earliest codes are:

```text
CMD-sheet-count-wrong                 E_COMMAND_SHEET_COUNT
CMD-sheet-coverage-wrong              E_COMMAND_SHEET_COVERAGE
CMD-sheet-missing                     E_COMMAND_SHEET_SET
CMD-sheet-duplicate                   E_COMMAND_SHEET_SET
CMD-sheet-id-wrong                    E_COMMAND_SHEET_ID
CMD-sheet-path-sequence-wrong         E_COMMAND_SHEET_PATH
CMD-sheet-grid-wrong                  E_COMMAND_SHEET_GRID
CMD-sheet-hash-wrong                  E_COMMAND_SHEET_HASH
CMD-flattened-page-missing            E_COMMAND_SHEET_PAGES
CMD-flattened-page-duplicate          E_COMMAND_SHEET_PAGES
CMD-flattened-page-order-wrong        E_COMMAND_SHEET_PAGE_ORDER
CMD-render-path-wrong                 E_COMMAND_RENDER_PATH
CMD-render-hash-wrong                 E_COMMAND_RENDER_HASH
CMD-page-render-mapping-disagrees     E_COMMAND_PAGE_RENDER_MAP
CMD-verify-determinism-false          E_COMMAND_DETERMINISM
```

The audit rows are emitted by `apply_case` in the required closed 16-field
shape.  Final ordered audit-row digest and byte serialization are unavailable
from this bounded engineering pass; downstream QA must recompute them from the
real fixture objects before any Step-6A integration.

## Material identity

| Surface | Before SHA-256 | After SHA-256 |
|---|---|---|
| `kb_creator/scripts/scenario_source_reconstruction.py` | `231C976E57D6DC1051C326C479EC42D87525DDB8565741A0D64A0E96B37352C7` | `2309CD5015B89908A5B751916F46B4C601AFB8E121EB338FC6450B7BAAE49FAC` |
| `kb_creator/tests/test_scenario_source_reconstruction.py` | `59C148D64F5CAB7B6D50723A4C10D5AD292FC0449D839CDB963DFE6F2403F1EF` | `7B9AEC1EF0BA2870E2021544912538FE3234DAF92D0E38E34F16285118649DCF` |

CMD-B completion admission was verified at
`terra_engineering_viral_step6a_mutation_batch_cmd_b_completion_20260901.md`:
`7140FA097F85CD806E6F0BF09715E53C96D459660FF681B3AD22B0E581175343`.
The assignment packet hash was
`CE82ABB7C62C2C1F7B5AE98B9397E241C3CD33586A012B29F77AA29BF204D4E9`.

Exact attributable path diff: modified the two listed material files and
added this receipt only.  No candidate, source, recovery, protected-119,
Git, cache, live build/remediate, cleanup, commit, or push surface was edited.

## Verification evidence

All commands ran from `D:\NRI\.worktrees\kb-creator-viral` with `python -B`
and `-p no:cacheprovider`; native exit was `0` for the commands with final
captured output below.

```text
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
371 tests collected in 0.08s

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider -k "CMD-flattened-page-duplicate or CMD-flattened-page-order-wrong or CMD-render-path-wrong or CMD-render-hash-wrong or CMD-page-render-mapping-disagrees or CMD-verify-determinism-false"
6 passed, 365 deselected in 19.18s

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider -k "bld"
3 passed, 368 deselected in 8.33s
```

The preceding bounded CMD-C chunks established all 15/15 exact-code passes:
the first nine, isolated `CMD-flattened-page-missing` (`1 passed`), and the
remaining six quoted above.  Command stdout/stderr hashes are unavailable
because this pass captured terminal output directly rather than persisting a
log (logs are outside the assigned write allowlist).

Pre-existing baseline residue observed without mutation: root `.pytest_cache`
and `kb_creator/scripts/__pycache__/scenario_contract.cpython-313.pyc`,
`kb_creator/tests/__pycache__/test_scenario_contract.cpython-313-pytest-9.0.2.pyc`,
`kb_creator/tests/__pycache__/test_scenario_source_reconstruction.cpython-313-pytest-9.0.2.pyc`.
They were not created, edited, or removed by this pass; new attributable
residue is zero.

## Risks, blocker, and next action

There is no CMD-C implementation blocker.  The receipt is deliberately not a
release or integration verdict.  Before downstream integration, QA must run
the full cache-disabled 371/119/490 command matrix, independently reconstruct
the 15 complete audit objects and their packet-formula canonical-byte/digest,
and perform the required live preflight/verify checks.  Independent critic
review remains required before any release decision.

Elapsed time: approximately 30 minutes.  Token use: unavailable.
