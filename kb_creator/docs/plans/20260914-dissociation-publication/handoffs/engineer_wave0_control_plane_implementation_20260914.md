# Engineering handoff receipt — Wave 0 reconstruction control plane

- Goal id: `20260914-dissociation-publication`
- Step id: `2-3-wave0-neutral-contract-and-control-plane`
- Role / requested model / effort: engineering / `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`
- Scoped override: none
- Timestamp: 2026-09-14T03:00:00+03:00
- Scope: neutral reconstruction-only contracts/control-plane primitives, fixed `reconstructed_en` preflight/run entrypoints, geometry and visual-bundle role parameterization, and focused synthetic tests. No scenario contract/data, source, candidate, publication, acceptance, release, status/plan/context, README, or Git changes.

## Result

Implemented the bounded Wave 0 foundation.

- Added `ScenarioReconstructionContract.v1`, separate from the publication-contaminated legacy v1 contract.
- Added closed schema files for run specs, stage manifests, review queues, and external reconstruction decision sets.
- Added `python -m kb_creator doctor|preflight|run`. `preflight` is non-mutating; all targets except `reconstructed_en` fail before run-root creation; `run` seals `run.json` only after source/contract identity and safe-new-root validation.
- Added stdlib canonical identity, subprocess, manifest, contract, queue, and closed-decision-set primitives. Decision sets bind queue/contract/source hashes, exact decision identities, safe relative paths, full page coverage, empty unresolved lists, and visual review.
- Generalized the preparer away from Letter-only admission. It records uniform MediaBox/rotation, rejects mixed geometry before output, and rasterizes using the full in-memory MediaBox rather than CropBox; historic Letter naming/CLI remains intact.
- Parameterized `build_mineru_visual_merge_bundle.py` with an optional neutral reconstruction contract. Contract-driven calls derive page count and roles from gap-free contract ranges; direct legacy calls retain their fallback.

## Files changed

- `kb_creator/contracts/scenario_reconstruction_contract.v1.schema.json`
- `kb_creator/contracts/{run_spec,stage_manifest,review_queue,reconstruction_decision_set}.v1.schema.json`
- `kb_creator/__main__.py`
- `kb_creator/pipeline/{__init__,identity,process,manifests,reconstruction}.py`
- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/tests/{test_pipeline_identity,test_reconstruction_control_plane}.py`
- this receipt

## Verification / evidence

Executed with the provided bundled Python and isolated dependency path:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\tmp\kb_creator_test_deps;C:\_Hobby\_work\NRI'
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest -q kb_creator/tests/test_pipeline_identity.py kb_creator/tests/test_reconstruction_control_plane.py kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_mineru_visual_merge_bundle.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_materialize_mineru_ai_merge.py
```

Result: `68 passed in 9.93s`.

The new tests prove neutral v1 rejection, deterministic identity, non-mutating preflight, and parameterized unsupported-target no-write behavior. Existing component suites passed for preparation, visual merge bundle, fidelity audit, and materialization.

## Limitations / blockers / next action

- The command surface currently implements the sealed entry boundary (`doctor`, `preflight`, and safe `run` creation) plus reusable queue/decision primitives. Wiring all six adapters into the fixed execution/resume graph remains the next bounded implementation increment; no live MinerU or Dissociation run was attempted.
- The neutral schema files are present and the Python validator is intentionally stdlib/narrow; schema-engine validation is not introduced in this slice.
- Request independent implementation review before authorizing a live reconstruction run. The reviewer should specifically inspect full-MediaBox rotated output behavior and verify that the runner path supplies the contract to the visual-bundle adapter when adapter orchestration is added.

- Elapsed time: approximately 10 minutes.
- Token use: unavailable.
