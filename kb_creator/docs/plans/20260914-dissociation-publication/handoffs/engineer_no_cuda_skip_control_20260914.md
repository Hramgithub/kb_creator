# Engineering handoff receipt — MinerU capability skip control

- Goal id: `20260914-dissociation-publication`
- Step id: `4-runtime-capability-skip-control`
- Role / requested model / effort: engineering / `gpt-5.6-sol` / `high`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `user-overridden-platform-unverified`
- Scoped override: engineering for this goal only, `gpt-5.6-sol` at `high`
- Timestamp: 2026-09-14T04:45:00+03:00
- Scope: generic no-NVIDIA/CUDA setup and reconstruction-control behavior only.

## Result and semantics

- `probe-capability.ps1` records a machine-readable
  `.tools/MinerU/capability.json` before venv creation or CUDA pip install.
  A successful `nvidia-smi` query records an `available` candidate; missing
  hardware, driver, executable, or a failed query records `unavailable`.
- On `unavailable`, `setup.ps1` and `verify.ps1` return success with an explicit
  `SKIPPED` result. They do not enter CUDA installation or dependency
  verification. On `available`, the existing pinned installation and strict
  Torch/CUDA/package verification remain fail-closed.
- Production preflight binds the exact capability receipt into portable run
  identity. `unavailable` is reported as `state: skipped`; it is not a tool
  error and missing MinerU/Python/Poppler executables are not required for that
  path.
- A skipped run contains only `run.json` and sealed `skip.json`. The MinerU
  stage records the capability reason; later stages record
  `dependency_skipped`. There are no succeeded stage manifests, outputs,
  review queue, fidelity report, candidate, or acceptance claim.
- Resume revalidates source, contract, implementation, and the exact capability
  receipt, validates the sealed skip evidence, then rejects continuation. A
  capability change invalidates the old binding and requires a fresh run root;
  a skip cannot masquerade as cached completion.

## Files changed

- `MinerU/scripts/probe-capability.ps1` (new)
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/verify.ps1`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/run_skip.v1.schema.json` (new)
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- this receipt

## Verification

- Real host probe: `unavailable / nvidia_device_not_detected`, exit `0`.
- Real `setup.ps1`: `MinerU setup: SKIPPED`, exit `0`, no pip phase.
- Real `verify.ps1`: `MinerU verification: SKIPPED`, exit `0`.
- PowerShell parser: PASS for probe, setup, and verify scripts.
- Python `py_compile`: PASS for pipeline and modified tests.
- Focused reconstruction suite, using interpreter and test dependencies under
  `NRI/.tools`: `88 passed in 9.61s`.

## Risks and next action

- `nvidia-smi` proves only a CUDA installation candidate. The existing GPU-host
  verification remains authoritative and intentionally fails if Torch cannot
  use CUDA or pinned packages drift.
- The capability receipt is local mutable evidence. Re-running the probe changes
  its identity by design and therefore requires a new reconstruction run.
- Orchestrator should run the real Dissociation CLI preflight/run to materialize
  the run-local skip evidence, then update canonical plan/context/status.
- No source PDF, generated scenario output, canonical goal state, Git state, or
  unrelated configuration was changed.

- Elapsed time: approximately 20 minutes.
- Token use: unavailable.
