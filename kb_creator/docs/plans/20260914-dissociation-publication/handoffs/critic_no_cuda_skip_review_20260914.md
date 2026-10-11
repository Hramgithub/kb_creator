# Independent critic receipt - no-CUDA skip review

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-runtime-capability-skip-control-review`
- Review kind: `implementation`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design the candidate under review.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: read-only review of no-NVIDIA/MinerU capability skip behavior in MinerU setup/verify/probe scripts, reconstruction control-plane skip handling, run/skip schemas, tests, engineer receipt, and the real Dissociation skipped run root.
- Changed by this review: added this receipt only.
- Timestamp: `2026-09-14T04:46:38+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:18:00`
- Token use: unavailable

## Verdict

Approved for the no-CUDA skip boundary. There are no remaining P0/P1/P2 findings in this scoped review.

The real host's missing NVIDIA/CUDA capability is modeled as an explicit `SKIPPED` non-error, not as reconstruction success, not as acceptance, and not as a candidate. Live GPU/MinerU reconstruction remains unavailable on this host until capability changes and a fresh run root is created.

## Files checked

- `MinerU/scripts/probe-capability.ps1`
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/verify.ps1`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/run_skip.v1.schema.json`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_pipeline_identity.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_no_cuda_skip_control_20260914.md`
- real run root: `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01`
- local capability receipt: `.tools/MinerU/capability.json`

## Evidence

- Setup probes before installation. `MinerU/scripts/setup.ps1` calls `probe-capability.ps1` before `-m venv` or any `pip install`; on `state == "unavailable"` it prints `MinerU setup: SKIPPED` and returns before environment creation or CUDA package installation.
- Verify preserves the GPU path. `MinerU/scripts/verify.ps1` only skips when the capability receipt is `unavailable`; otherwise it still requires the venv, initializes MinerU, checks model files, imports Torch/MinerU, requires `torch.cuda.is_available()`, and validates pinned CUDA package versions.
- Tool placement is bounded. The setup/verify/probe default `ToolRoot` is workspace-local `.tools/MinerU`; unavailable capability does not require or resolve Python/PowerShell/Poppler/MinerU executable bindings.
- Control-plane preflight binds capability. `kb_creator/pipeline/reconstruction.py` reads `.tools/MinerU/capability.json`, requires schema `nri.mineru_cuda_capability.v1`, records the receipt byte/hash identity, returns `state: skipped` for unavailable capability, and emits empty `toolchain`/`executable_paths` for the skip path.
- Skipped run is fail-closed. `run_engine()` writes `run.json` and sealed `skip.json` only. `_validate_skip()` verifies the skip seal, capability identity, expected skipped stage list, and absence of `stages`, `outputs`, and `review`. `resume_engine()` rejects continuation for an unavailable-capability run.
- Real skip root contains only `run.json` and `skip.json`. The checked root has no `stages`, `outputs`, `review`, or `candidate` directories.
- Real skip evidence is identity-bound. `run.json` binds source `Dissociation.PDF` byte count `2159317`, SHA-256 `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`, six-page MediaBox `[595, 841]`, neutral contract hash, implementation inventory, local `.tools/MinerU` root, empty toolchain, and capability receipt hash `3E4E4DD38D18097E5CAB59EF2EAFBD107EEADCF6379E58A7572A37CBC28A58B9`.
- `skip.json` is sealed and lists all six reconstruction stages as `skipped`; `02-mineru-three-view` carries `nvidia_device_not_detected`, and later stages carry `dependency_skipped`.
- I ran `resume` against the real skipped run with dummy decision paths. It failed before decision access with: `run was skipped because MinerU CUDA capability is unavailable; start a new run after capability changes`.
- Current `.tools/MinerU/capability.json` reports `state: unavailable`, `reason_code: nvidia_device_not_detected`, no NVIDIA device detected, no `nvidia_smi_path`, and no devices.

## Tests run

Command:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI'
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m pytest -q kb_creator\tests\test_pipeline_identity.py kb_creator\tests\test_reconstruction_control_plane.py kb_creator\tests\test_mineru_three_view_tools.py kb_creator\tests\test_mineru_visual_merge_bundle.py kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py kb_creator\tests\test_materialize_mineru_ai_merge.py
```

Result: `88 passed in 10.37s`.

Additional command:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps;C:\_Hobby\_work\NRI'
& 'C:\_Hobby\_work\NRI\.tools\MinerU\.venv\Scripts\python.exe' -m kb_creator resume --run-root kb_creator\working\dissociation\reconstruction\20260914-no-cuda-skip-01 --decisions kb_creator\working\dissociation\reconstruction\20260914-no-cuda-skip-01\missing_decisions.json --decisions-root kb_creator\working\dissociation\reconstruction\20260914-no-cuda-skip-01 --target reconstructed_en
```

Result: exit `1`, expected blocked JSON: `run was skipped because MinerU CUDA capability is unavailable; start a new run after capability changes`.

I did not rerun `probe-capability.ps1`, `setup.ps1`, or `verify.ps1` during this critic pass because the probe rewrites `.tools/MinerU/capability.json`; changing that local receipt would intentionally invalidate the already reviewed skipped-run identity.

## Findings

- P0: none.
- P1: none.
- P2: none.

## Recommendation

Accept this bounded no-CUDA skip control. The orchestrator may record the host skip outcome and proceed only with non-GPU-safe planning or wait for a CUDA-capable host/fresh capability receipt. Do not treat `SKIPPED` exit `0` as reconstruction success, candidate readiness, user acceptance, or release evidence.

## Next action

If NVIDIA/CUDA capability becomes available, rerun the capability probe and start a new reconstruction run root; do not resume the no-CUDA skipped run.
