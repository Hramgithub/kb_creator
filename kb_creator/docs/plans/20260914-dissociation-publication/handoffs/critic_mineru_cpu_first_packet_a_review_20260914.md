# Critic receipt — MinerU CPU-first Packet A implementation review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-first-packet-a-implementation-review`
- Review kind: `implementation`
- Candidate state: non-frozen implementation candidate; not a release review
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; role ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review. The Packet A engineering override recorded by the engineer remains scoped to implementation only.
- Timestamp: `2026-09-14T16:36:06+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:04:00`
- Token use: active runtime goal reported `66778` tokens before receipt write

This receipt is an immutable implementation review only. It is not runtime
acceptance, reconstruction acceptance, publication acceptance, release approval,
or authorization to run the real Dissociation source.

## Scope

Reviewed the Packet A implementation against:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_local_execution_decision_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_mineru_cpu_first_execution_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_first_architecture_review_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_first_packet_a_20260914.md`

Forbidden scope was honored: no dependency installation, no `.tools` mutation,
no real Dissociation run, no remote/API/GPU host, no sealed-run mutation, no
Git index/history operation, and no implementation edit was performed. This
receipt is the only file written.

## Files checked

- `.gitattributes`
- `.gitignore`
- `MinerU/README.md`
- `MinerU/requirements.windows-cpu-pipeline.lock.txt`
- `MinerU/requirements.windows-cu128-provider.lock.txt`
- `MinerU/models/manifest.json`
- `MinerU/models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/profile_receipt.py`
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/initialize.ps1`
- `MinerU/scripts/verify.ps1`
- `MinerU/scripts/probe-capability.ps1`
- `kb_creator/contracts/mineru_provider_capabilities.v1.schema.json`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `docs/governance/nri_goal_governance.md`

## Evidence

- CPU remains mandatory despite absent NVIDIA. `setup.ps1` installs and verifies
  `pipeline-cpu-v1` before the hardware probe and fails if `pipeline_cpu` is
  not ready. Static tests assert no `MinerU setup: SKIPPED` or `MinerU
  verification: SKIPPED` language remains in the new scripts.
- Optional provider-level GPU skip is represented through ordered providers
  `pipeline_cpu`, `hybrid_cuda`, and `vlm_cuda` in
  `nri.mineru_provider_capabilities.v1`. The old run-global `capability.json`
  path is not used by `probe-capability.ps1`.
- Profile, cache, pip, uv, HF, ModelScope, and temp roots are directed below
  repository `.tools`. `profile-common.ps1` rejects a `ToolRoot` outside
  `.tools`; `setup.ps1` writes `UV_PYTHON_INSTALL_DIR`, `UV_CACHE_DIR`, and
  `PIP_CACHE_DIR` below `.tools`; profile runtime paths are
  `.tools/MinerU/runtime/<profile>`.
- CPU lock critical pins are present: `torch==2.8.0+cpu`,
  `torchvision==0.23.0+cpu`, `transformers==4.57.6`,
  `onnxruntime==1.28.0`, `PyMuPDF==1.28.2`, `pypdf==6.16.0`, and
  `reportlab==5.0.0`. A focused text search found no CUDA/GPU-only package
  names in the CPU lock.
- Optional CUDA lock is separate and contains reviewed CUDA-provider pins such
  as `torch==2.8.0+cu128`, `torchvision==0.23.0+cu128`,
  `lmdeploy==0.11.1`, `triton-windows==3.4.0.post21`, and
  `torch-c-dlpack-ext==0.1.5`; `torchaudio` was not found in the CUDA-provider
  lock by the critical-pin search.
- Wheel/platform evidence is implemented in `profile_receipt.py`: install
  receipts record `compatible_tags`, wheel filenames, direct URLs, archive
  hashes, and wheel tags for critical wheels.
- VLM method handling matches the architecture P2 hardening note. `verify.ps1`
  invokes `vlm-engine` without `--method`; `profile_receipt.py` records
  `vlm_local` as `method: null`, `cli_method_argument: omitted`, and
  `effective_method_scope: not_applicable`.
- Formula/table/layout/OCR load proof exists, but the implementation uses
  `hasattr(model, ...)` only. That proves attributes are present, not that the
  loaded component objects are non-null or usable.
- Exact model manifest proof passed read-only: 40/40 pipeline manifest rows
  matched exact byte count and SHA-256. The normalized formula YAML is
  `2244564` bytes, SHA-256
  `87b5f3d7f2b2fe553627d77b37f496608ca150ebd0ef62d362591edca47b5538`, with
  zero CRLF sequences. The scoped `.gitattributes` `-text` rule exists for
  that file.
- Environment stripping covers proxy variables, external MinerU URL variables,
  model-source override, `PYTHONPATH`, user cache roots, and device override.
  Runtime config validation rejects enabled title-aided external LLM
  configuration, API key, or base URL.
- Static search of new Packet A scripts/tests found no Bogdan path, remote host
  address, external MinerU HTTP-client backend, `--api-url`, or `--url`
  production path.
- Current host bootstrap evidence: `Get-Command uv` returned no command,
  `.tools/python` currently has no `python.exe`, `py` reports no installed
  Python, and bundled Codex Python lacks `pytest` and `jsonschema`. The README
  documents `uv` or a repository-local CPython `3.12.14` as a setup
  prerequisite, so this is an environmental blocker for live setup on this
  host, not by itself an implementation defect.
- The sealed run `20260914-no-cuda-skip-01` was not touched during this review.

## Findings

### P0

None found in the reviewed Packet A implementation.

The implementation does not authorize source execution yet. Live CPU profile
installation, profile verification, synthetic MinerU smokes, and provider
receipt generation remain pending and must occur only after orchestrator
authorization.

### P1

1. Provider capability schema does not fail closed on state/reason coupling.

   `mineru_provider_capabilities.v1.schema.json` constrains ready providers to
   `verified_*` reasons, but does not constrain non-ready states to non-ready
   reasons. A `pipeline_cpu` record can be `state: invalid` with
   `reason_code: verified_cpu_profile`, and an optional provider can be
   `state: unavailable` or `invalid` with `reason_code:
   verified_cuda_profile`, as long as the receipt is null. This weakens the
   provider-scoped skip/invalid semantics the architecture requires and is not
   covered by the focused tests.

2. `probe-capability.ps1` trusts a ready verification receipt without
   validating its internal seal.

   `Get-ReadyVerificationIdentity` checks only `schema`, `profile`, and
   `state: ready`, then records the file identity. It does not recompute or
   verify the receipt's `receipt_sha256`, nor does it require the receipt to
   contain the expected lock/source/model/smoke evidence before declaring the
   provider ready. `profile_receipt.py` does validate the install receipt seal
   while writing verify receipts, but the provider capability boundary can be
   entered independently through an edited or synthetic ready-looking
   `verify-receipt.json`.

3. Verification receipts do not require the exact smoke set before sealing
   `state: ready`.

   `verify.ps1` constructs the intended route pairs, but
   `profile_receipt.py write-verify` accepts any one or more `--smoke`
   arguments, allows duplicate route names, and does not require CPU receipts
   to contain exactly `pipeline_txt` plus `pipeline_ocr` or CUDA receipts to
   contain exactly `hybrid_high` plus `vlm_local`. A direct helper invocation
   can therefore seal a ready receipt with incomplete smoke evidence.

4. Model-load proof is presence-based rather than loaded-object proof.

   The receipt helper records `hasattr(model, "layout_model")`,
   `hasattr(model, "mfr_model")`, `hasattr(model, "ocr_model")`,
   `hasattr(model, "table_cls_model")`, `hasattr(model,
   "img_orientation_cls_model")`, `hasattr(model, "wired_table_model")`, and
   `hasattr(model, "wireless_table_model")`. This can pass if attributes exist
   but are `None` or otherwise unloaded. The architecture review asked for
   component load evidence strong enough to prove formula/table/layout/OCR
   paths are actually available before the real source run.

### P2

1. `.gitattributes`, `.gitignore`, and several PowerShell files currently
   produce Git line-ending warnings during `git diff --check`/`--stat`.
   `git diff --check` returned success and no whitespace errors, but the
   checkout warning is noisy and should be resolved or documented before
   commit hygiene review.

2. Live setup on this host is not yet bootstrap-ready because neither `uv` nor
   repository-local CPython `3.12.14` is present. This is documented in the
   README and setup failure message, but the next live verification step will
   need that precondition closed before it can produce runtime evidence.

## Verification commands

Commands run read-only unless noted:

```powershell
git status --short --branch
Get-Content -Raw docs/governance/nri_goal_governance.md
Get-Content -Raw kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_local_execution_decision_20260914.md
Get-Content -Raw kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_mineru_cpu_first_execution_spec_20260914.md
Get-Content -Raw kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_first_architecture_review_20260914.md
Get-Content -Raw kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_first_packet_a_20260914.md
Get-Content -Raw .gitattributes
Get-Content -Raw .gitignore
Get-Content -Raw MinerU/README.md
Get-Content -Raw MinerU/scripts/profile-common.ps1
Get-Content -Raw MinerU/scripts/profile_receipt.py
Get-Content -Raw MinerU/scripts/setup.ps1
Get-Content -Raw MinerU/scripts/initialize.ps1
Get-Content -Raw MinerU/scripts/verify.ps1
Get-Content -Raw MinerU/scripts/probe-capability.ps1
Get-Content -Raw kb_creator/contracts/mineru_provider_capabilities.v1.schema.json
Get-Content -Raw kb_creator/tests/test_mineru_cpu_profile_packet_a.py
Get-Content -Raw kb_creator/tests/test_mineru_three_view_tools.py
rg -n "cuda|cu128|lmdeploy|triton|torch-c-dlpack-ext|vllm|mlx-vlm|torchaudio" MinerU/requirements.windows-cpu-pipeline.lock.txt
rg -n "^(torch|torchvision|transformers|onnxruntime|PyMuPDF|pypdf|reportlab|lmdeploy|triton-windows|torch-c-dlpack-ext|torchaudio)==" MinerU/requirements.windows-cpu-pipeline.lock.txt MinerU/requirements.windows-cu128-provider.lock.txt
rg -n "state|reason_code|verified_cpu_profile|verified_cuda_profile|unavailable|invalid|allOf|if|then" kb_creator/contracts/mineru_provider_capabilities.v1.schema.json
rg -n "hasattr\(model|model_load_proof|smoke|for item in args.smoke|method_contract|required_output_inventory|MineruPipelineModel" MinerU/scripts/profile_receipt.py MinerU/scripts/verify.ps1
rg -n "SKIPPED|skip|capability\.json|providers\.json|pipeline_cpu|hybrid_cuda|vlm_cuda|global|mineru_cuda" MinerU/scripts kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
rg -n "http-client|api-url|--url|hybrid-http-client|vlm-http-client|MINERU_API_URL|MINERU_SERVER_URL|base_url|api_key|title_aided|external" MinerU/scripts MinerU/config kb_creator/tests/test_mineru_cpu_profile_packet_a.py
Get-Command uv -ErrorAction SilentlyContinue
Get-ChildItem -LiteralPath .tools\python -Filter python.exe -File -Recurse -ErrorAction SilentlyContinue
[System.Management.Automation.Language.Parser]::ParseFile(...) for setup.ps1, initialize.ps1, verify.ps1, probe-capability.ps1, profile-common.ps1
git diff --check -- <Packet A paths>
git diff --stat -- <Packet A paths>
```

Focused pytest reproduction was attempted but could not run on this host:

```text
py -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
No installed Python found!

C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest ...
No module named pytest
```

Existing local MinerU/quarantine venvs also lacked `pytest` and `jsonschema`;
installing test dependencies was outside the review authorization.

## Blockers

- P1 schema state/reason coupling must be fixed before provider capability
  receipts can be accepted as fail-closed evidence.
- P1 provider-ready trust must validate the verification receipt seal and
  required evidence before a provider is marked ready.
- P1 verification receipt smoke sealing must require the exact profile-specific
  smoke set with no missing or duplicate route names.
- P1 model-load proof must become a stronger non-null/usable component proof
  before live source execution.
- Live runtime acceptance is blocked on current-host bootstrap prerequisites:
  provide `uv` or a repository-local CPython `3.12.14` under `.tools/python`,
  then run the fresh CPU setup/verification under explicit orchestrator
  authorization.

## Recommendation

Changes requested before Packet A acceptance, live setup evidence, Packet B
dispatch, or any fresh real-source run.

The implementation is directionally aligned on CPU-first profile separation,
model byte stability, optional CUDA boundary, VLM method omission, local cache
containment, and remote/service exclusion. The remaining defects are narrow
but sit directly on the fail-closed evidence boundary, so they should be
remediated and independently re-reviewed before the candidate is treated as
closed.
