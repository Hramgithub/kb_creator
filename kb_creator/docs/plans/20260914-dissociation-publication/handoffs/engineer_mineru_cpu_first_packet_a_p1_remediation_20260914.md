# Engineering receipt — MinerU CPU-first Packet A P1 remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-first-packet-a-p1-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded for this assignment by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Scoped override: active — user-directed engineering execution with
  `gpt-5.6-sol` at `high`
- Scope: remediate only the four P1 findings in
  `critic_mineru_cpu_first_packet_a_review_20260914.md`
- Result: all four P1 implementation defects remediated with adversarial tests;
  focused suite passes
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Elapsed time: approximately `00:18:00`
- Token use: unavailable

This receipt is implementation evidence only. It is not independent review,
runtime acceptance, reconstruction acceptance, publication acceptance, release
approval, or authority to execute the real source.

## P1 remediation

### 1. Exact provider state coupling

`mineru_provider_capabilities.v1.schema.json` now uses mutually exclusive
`oneOf` branches for each state:

- CPU `ready` requires `verified_cpu_profile` plus a verification identity;
- CPU `invalid` permits only `cpu_profile_not_verified` or
  `cpu_profile_invalid`, with a null receipt;
- optional CUDA `ready` requires `verified_cuda_profile` plus a verification
  identity;
- optional CUDA `unavailable` permits only the four hardware/capability absence
  reasons, with a null receipt;
- optional CUDA `invalid` permits only `cuda_profile_not_verified` or
  `cuda_profile_invalid`, with a null receipt.

Adversarial schema tests now reject every critic cross-product: verified reason
with invalid/unavailable state, a hardware reason with invalid state, and an
invalid-profile reason with unavailable state.

### 2. Independent ready-receipt validation at probe boundary

`profile_receipt.py` now provides a `validate-verify` command. Before
`probe-capability.ps1` emits a ready provider or captures the file identity, it
runs that validator with the profile-local Python, expected profile and pinned
model manifest. Failure, missing Python/helper/manifest, bad seal or missing
evidence produces no ready identity.

The validator independently requires:

- exact top-level receipt shape and valid internal `receipt_sha256`;
- exact profile/state and pinned MinerU/Torch/torchvision/transformers/
  onnxruntime versions;
- exactly 40 CPU or 55 CUDA model rows equal to the pinned manifest;
- profile-correct assembled-VLM evidence;
- lock/config/install identities;
- all seven loaded/usable model-component proofs;
- exact ordered profile smoke set and required output artifacts;
- exact critical wheel order, versions and non-empty provenance/tag evidence.

Tests reproduce both an edited receipt with a stale seal and a resealed
ready-looking minimal receipt. Both are rejected. A resealed receipt missing a
model row is also rejected.

### 3. Exact profile smoke set before sealing

`write-verify` validates its `--smoke` arguments before dependency/model work.
The only accepted ordered sets are:

- CPU: `pipeline_txt`, `pipeline_ocr`;
- CUDA: `hybrid_high`, `vlm_local`.

Missing, duplicate, extra and reordered routes now fail. The validator repeats
the same exact-set check when an existing receipt is consumed. VLM retains
`method: null`, `cli_method_argument: omitted` and
`effective_method_scope: not_applicable`.

### 4. Non-null usable model components

Presence-only `hasattr` checks were removed. `build_model_load_proof` now gets
each component object, requires it to be non-null, requires its profile-specific
inference method to be callable, and records component type plus usable method.
The checked pairs are layout/predict, formula/predict, OCR/ocr, table
classification/predict, table orientation/predict, wired table/predict and
wireless table/predict. Tests prove objects whose attributes exist but are null
are rejected, while usable component objects produce complete evidence.

## Files changed

- `kb_creator/contracts/mineru_provider_capabilities.v1.schema.json`
- `MinerU/scripts/profile_receipt.py`
- `MinerU/scripts/probe-capability.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this remediation receipt

No other implementation, test, plan, context, status, critic receipt, lock,
model, sealed-run or `.tools` file was changed.

## Verification

- Focused pytest:

```text
40 passed in 4.58s
```

Command scope:

```text
kb_creator/tests/test_mineru_cpu_profile_packet_a.py
kb_creator/tests/test_mineru_three_view_tools.py
```

- PowerShell parser: PASS for the changed `probe-capability.ps1`.
- Provider schema loaded and valid/invalid fixtures were exercised through
  `jsonschema` in the focused suite.
- Python helper was imported and its seal, evidence, smoke and component-proof
  validators were executed directly by adversarial tests.
- No dependency was installed, no `.tools` path was mutated, no model byte was
  touched, and no source PDF or remote/API execution occurred.

## Remaining gate

Packet A still requires an independent implementation re-review of this
remediation. Live setup and synthetic MinerU inference remain separately
blocked on explicit orchestrator authorization and the documented local
bootstrap prerequisite.
