# Critic receipt: ArtView v3 accepted-decision rebind

- Goal id: `20260914-dissociation-publication`
- Step id: generic ArtView v3 accepted-decision rebind
- Timestamp: `2026-09-15T21:37:07+03:00`
- Contributor role: independent critic / implementation review
- Requested model / effort: `gpt-5.5` / `medium`
- Actual platform model / effort: unavailable
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Scoped override: none for critic role
- Scope: review-only inspection of `kb_creator/scripts/scenario_artview.py`, `kb_creator/tests/test_scenario_artview_v3.py`, the engineer receipt, and read-only plan/context/governance evidence
- Forbidden scope honored: no publication run created or resumed; no browser/server opened; no acceptance/submission written; no implementation, test, canonical plan, context, status, source, or unrelated file modified

## Decision

GO for the generic ArtView v3 decision rebind implementation.

No P0, P1, or P2 findings were identified in the reviewed scope.

## Review evidence

Code inspection covered:

- authority-relative existing-file resolution and destination-absent resolution in `scenario_artview.py:1821` and `scenario_artview.py:1864`;
- strict v3 candidate/decision validation in `scenario_artview.py:2079`;
- selected-binary identity comparison in `scenario_artview.py:2134`;
- rebind orchestration, complete row graph equality, decision contract equality, derived-count equality, candidate inventory equality, target binding replacement, canonical reseal, destination `open("x")`, and post-write strict validation in `scenario_artview.py:2152`;
- CLI argument exposure for all source/target authority and path controls in `scenario_artview.py:2360`;
- focused positive and adversarial coverage in `test_scenario_artview_v3.py:371`, `:399`, `:434`, and `:455`.

Commands run:

```powershell
Get-Command python,py -All
python -m unittest kb_creator.tests.test_scenario_artview_v3
py -m unittest kb_creator.tests.test_scenario_artview_v3
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest kb_creator.tests.test_scenario_artview_v3
$env:PYTHONPATH='.tools/python-test-deps'; .\.tools\MinerU\.venv\Scripts\python.exe -B -m pytest kb_creator/tests/test_scenario_artview_v3.py -q
$env:PYTHONPATH='.tools/python-test-deps'; .\.tools\MinerU\.venv\Scripts\python.exe -B -m py_compile kb_creator/scripts/scenario_artview.py kb_creator/tests/test_scenario_artview_v3.py
$env:PYTHONPATH='.tools/python-test-deps'; .\.tools\MinerU\.venv\Scripts\python.exe kb_creator/scripts/scenario_artview.py rebind-decisions --help
```

Results:

- Default `python` was unavailable on `PATH`.
- `py` was present but reported `No installed Python found`.
- Bundled Codex Python imported the test module but lacked `jsonschema`, so the direct unittest run could not execute that suite.
- Repository-local `.tools/MinerU/.venv/Scripts/python.exe` with `PYTHONPATH=.tools/python-test-deps` passed: `20 passed, 255 subtests passed in 5.64s`.
- `py_compile` passed for the reviewed script and test module.
- `rebind-decisions --help` exposed all eight required path/authority arguments.

## Findings

- P0: none.
- P1: none.
- P2: none.

## Assessment

The rebind operation is appropriately fail-closed for the intended use:

- source and target paths are resolved through explicit authority roots and reject traversal, unsafe portable paths, existing reparse content, missing parents, wrong filenames for candidate manifests, and pre-existing destinations;
- source decisions must pass strict accepted validation before transfer;
- the target candidate graph is independently reconstructed and must pass strict validation before any decision transfer is trusted;
- the operation requires same scenario id, same row order/cardinality, byte-for-byte identical complete review rows, same decision contract, same derived counts, and same candidate-files inventory seal;
- every transferred final binary choice is resolved against both manifests and compared by full binary record, not just by `candidate_id`;
- the target document preserves the accepted decisions while replacing only bindings/review metadata that must belong to the target manifest, recomputes the canonical `decisions_sha256`, writes with destination-absent semantics, and validates the written document against the target graph.

The inventory equality check is SHA-256 based after each candidate graph is independently validated against its physical files and inventory document. I do not treat theoretical SHA-256 collision construction as a practical blocker for this scope; the implementation already rejects ordinary path, bytes, digest, projection, and tamper drift.

## Scope notes

The diff also contains earlier ArtView v3 interactive HTML/export changes adjacent to the rebind code. This receipt reviews them only insofar as the existing tests and decision schema affect rebind correctness; it is not a fresh UI/export implementation review.

## Blockers and next action

No implementation blocker remains for the generic decision rebind. The orchestrator may rely on this rebind layer for strict source-to-target ArtView v3 accepted-decision transfer, subject to the usual live-run authority checks and explicit user acceptance boundaries.

- Elapsed time: approximately 22 minutes
- Token use: unavailable
