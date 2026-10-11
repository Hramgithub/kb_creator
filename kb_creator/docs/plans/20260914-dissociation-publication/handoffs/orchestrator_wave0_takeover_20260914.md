# Orchestrator Wave 0 takeover receipt

Date: `2026-09-14`

Scope: bounded completion of the generic reconstruction control plane after
the original engineering contributor exhausted three continuation turns. This
receipt does not accept reconstruction, authorize live MinerU, or implement any
publication stage.

## Result

- Added a neutral reconstruction-only contract schema and separate RunSpec,
  StageManifest, ReviewQueue, and ReconstructionDecisionSet schemas.
- Added `python -m kb_creator` with only `reconstructed_en` as an executable
  target; downstream and direct HTML-to-PDF targets fail before run-root writes.
- Wrapped the existing prepare, MinerU, compare, visual-bundle, fidelity-audit,
  and materialization tools as a fixed six-stage graph.
- Generalized raster preparation to arbitrary uniform MediaBox geometry,
  preserved full MediaBox content when CropBox is smaller, and normalized page
  rotation exactly once.
- Made visual merge roles come from the neutral contract on control-plane runs;
  the legacy 124-page Viral table remains only for the old direct CLI path.
- Added immutable run/stage identities, exact output inventories, strict
  run-local resume checks, decision-bound stage inputs, tool/source/contract/
  implementation revalidation, path containment, and failed-output quarantine.
- Added Git allowlist entries for the new reusable Python package; no generated
  run or scenario-specific executable was added.

## Verification

- `py_compile`: pass.
- Focused suites after critic remediation: `83 passed in 9.58s`.
- `git diff --check`: pass before this receipt; must be rerun after review fixes.

## Boundaries and next action

The external `Dissociation.PDF` remains unchanged and no live reconstruction
run exists. The current implementation is only a candidate for Step 3R. Obtain
an independent `gpt-5.5` implementation verdict, close all P0/P1 findings, and
then materialize the scenario contract from the already recorded six-page
reconnaissance.

## Independent-review remediation

The first Step 3R review found that the production fidelity adapter passed the
packet `pages/` directory instead of the parent containing `merge_index.json`.
The adapter now passes `merge_packets`, and a direct production-adapter argv
test covers the boundary. Review-queue issue kinds are now derived from
contract strategies/traits, MediaBox-versus-CropBox evidence, and merge-packet
signals. Both changes remain subject to the critic's short closure review.
