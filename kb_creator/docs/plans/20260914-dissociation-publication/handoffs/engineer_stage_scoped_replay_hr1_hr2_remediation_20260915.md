# Packet H HR1/HR2 remediation receipt

## Assignment

- **Date:** 2026-09-15
- **Role / scoped override:** engineering, `gpt-5.6-sol` at `high`.
- **Scope:** bounded remediation of P1-HR1HR2-01 through P1-HR1HR2-03 and P2-HR1HR2-04 from `critic_stage_scoped_replay_hr1_hr2_implementation_20260915.md`.
- **Boundary:** HR1/HR2 only. No HR3/G1/G2, live replay, run/decision/`.tools` mutation, upstream S1-S4 producer edit, network, GPU, remote/API, or commit.
- **Result:** focused remediation is coherent and green. It is ready for another independent HR1/HR2 implementation review; live replay and HR3 remain NO-GO pending that review.

## Changes

1. `reconstruction_replay.py`
   - `verify_replay_source()` now rejects every 01-03 prefix with `partial_prefix_not_runnable` before filesystem/runtime access. The only advertised/runnable Packet H prefix is the complete contiguous 01-04 prefix.
   - `_rebase_comparison()` no longer converts any origin wrapper root or artifact string to `Path`, calls `resolve()`, or derives a relative path from it. It builds the seven closed operational artifact roles exclusively from each sealed fresh view receipt's relative `output_inventory`.
   - The transformer compares origin root/artifact strings for exact equality with expected strings constructed from the trusted source-run root plus sealed relative inventory. Internally consistent drive, UNC, device, traversal-shaped, nonexistent, or otherwise poisoned old root/path pairs fail closed and are never dereferenced.
   - Skipped-view receipts are rebuilt against fresh Stage02 receipts and their seals; stale source receipt authority is rejected.
   - Comparison v3 now has a runtime exact-shape validator for the top level, per-view roots, seven artifact roles, scoped typed refs, blocks/semantic evidence, skipped rows, pairwise rows/conflicts, seal, and recomputed semantic projection.
   - Generic Stage04 replay envelopes were removed. Geometry v2, visual bundle v3, and visual execution v1 now have dedicated typed transformers.
   - Geometry v2 binds fresh Stage01 preparation, Stage02 view set, Stage03 comparison, fresh per-view layout refs, source/renderer identities, geometry policy, tolerances, targets/transforms, and exact copied rendered-page identities. It recomputes and validates its semantic projection and seal.
   - Visual v3 binds fresh view-set/comparison/preparation/geometry authorities, fresh scoped layout refs, source/contract identities, copied payload inventory, and replay-only execution evidence. It replaces the geometry inventory row with the new typed wrapper identity and recomputes projection/seal.
   - Visual execution v1 carries no old commands or path authority; it binds the origin wrapper identity, renderer identity/recipe, exact copied PNG inventory, replay status, projection, and seal.
   - Replay validation now opens only fresh typed references, verifies their bytes/SHA and nested receipt/comparison/geometry seals, recomputes comparison/geometry/visual projections, and validates replay execution shape.

2. Closed replay schemas
   - `mineru_multi_view_comparison.v3.schema.json`: closed per-view, seven-role artifact, skipped receipt, block/evidence, asset, pairwise match/unmatched/conflict, origin, and typed-reference shapes; no generic nested authority object remains.
   - `mineru_geometry_plan.v2.schema.json`: field-level closed preparation/comparison/view-set/source/renderer/layout/geometry/target/transform/rendered-page/origin/execution shapes.
   - `mineru_visual_merge_bundle.v3.schema.json`: field-level closed input, layout, execution, inventory, geometry, and origin shapes.
   - `visual_replay_execution.v1.schema.json`: field-level closed renderer, copied-render inventory, origin, replay execution, projection, and seal shapes.

3. `test_reconstruction_replay.py`
   - Replaced the obsolete generic-envelope assertion with typed Stage04 transformer coverage.
   - Upgraded the synthetic 01-04 replay fixture to realistic seven-role view artifacts plus sealed geometry/visual/execution inputs.
   - Added direct poison attacks for drive, UNC, device, traversal-shaped and nonexistent origin roots and artifact paths.
   - Added a positive proof that all operational Stage03 refs come from sealed relative inventory and a static guard against the former `Path(...).resolve().relative_to(...)` pattern.
   - Added every 01-03 alias to a pre-filesystem partial-prefix rejection matrix.

## Verification

- Coherence compile:
  - `python -m py_compile kb_creator/pipeline/reconstruction_replay.py kb_creator/tests/test_reconstruction_replay.py`
  - **passed**.
- Focused suite using the existing repo-local CPython and `PYTHONPATH=.tools/python-test-deps`:
  - `python -m pytest -q kb_creator/tests/test_reconstruction_replay.py`
  - **72 passed in 3.42s**.
- Schema parsing:
  - the four remediated JSON schemas parsed with PowerShell `ConvertFrom-Json`.
- JSON Schema metaschema validation:
  - `Draft202012Validator.check_schema(...)` for all four remediated schemas.
  - **4 passed**.
- Owned-file trailing-whitespace check: **clean**.
- `git status --short` confirms only the already untracked replay-owned implementation/schema/test files in this receipt's code scope. Because these files are untracked in the shared worktree, ordinary `git diff --check` emits no content; the explicit owned-file whitespace scan was used instead.
- Broad regression was intentionally not rerun in this recovery turn, per orchestrator instruction. The pre-remediation Packet H receipt's broad result is not claimed as evidence for these new bytes.

## Safety and remaining gate

- No source-run wrapper string is operational path authority in the remediated Stage03 transformer.
- Operational Stage04 wrappers are typed rather than opaque semantic envelopes, and old command/path material remains only in the sealed origin vault.
- No upstream producer-closure file, immutable run, decision root, `.tools` content, or canonical plan/status/context file was changed.
- **P0:** none observed in the focused boundary.
- **P1:** independent implementation review must confirm the remediated transformer/schema parity before HR3 or any live replay.
- **P2:** bounded recovery did not repeat the broad suite or live run-07 eligibility proof. Those remain later closure evidence, not blockers to submitting this focused remediation for review.

## Exact changed files

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/contracts/mineru_multi_view_comparison.v3.schema.json`
- `kb_creator/contracts/mineru_geometry_plan.v2.schema.json`
- `kb_creator/contracts/mineru_visual_merge_bundle.v3.schema.json`
- `kb_creator/contracts/visual_replay_execution.v1.schema.json`
- `kb_creator/tests/test_reconstruction_replay.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_stage_scoped_replay_hr1_hr2_remediation_20260915.md`

## Next action

Run a new independent HR1/HR2 implementation closure against this receipt. Do not start HR3 or create a live replay target unless that review closes all P0/P1 findings.
