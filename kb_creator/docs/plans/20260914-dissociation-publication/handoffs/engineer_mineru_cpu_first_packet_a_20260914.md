# Engineering handoff receipt — MinerU CPU-first Packet A

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-first-packet-a`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded for this assignment by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Scoped override: active — user-directed engineering execution with
  `gpt-5.6-sol` at `high`
- Scope: generic repository-local MinerU CPU/CUDA profile separation,
  provider-scoped capability evidence, dependency/model identity controls,
  setup verification and focused tests only
- Result: implementation and static/unit verification are ready for independent
  review. Live profile installation and synthetic MinerU inference remain
  deliberately pending because the orchestrator explicitly prohibited
  dependency installation and `.tools` mutation in this implementation turn.
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Elapsed time: approximately `00:45:00`
- Token use: unavailable

This receipt is not runtime acceptance, reconstruction acceptance, publication
acceptance, release approval, or authority to execute the real Dissociation
source.

## Implemented boundary

- Added a complete pinned Windows CPU pipeline lock with
  `torch==2.8.0+cpu`, `torchvision==0.23.0+cpu`,
  `transformers==4.57.6`, `onnxruntime==1.28.0`,
  `PyMuPDF==1.28.2`, `pypdf==6.16.0` and `reportlab==5.0.0`.
- Added a separate optional CUDA provider lock retaining the reviewed CUDA
  pins and intentionally excluding `torchaudio`. The old CUDA lock remains
  unchanged as legacy evidence.
- Reworked setup into separate fresh profile roots below `.tools/MinerU`:
  `profiles/pipeline-cpu-v1` and `profiles/windows-cu128-v1`, with separate
  runtime/cache/config/receipt roots. The legacy `.tools/MinerU/.venv`,
  `.runtime` and `capability.json` are not resolved by new code.
- The mandatory CPU profile is installed and verified before GPU hardware is
  probed. Missing NVIDIA no longer skips setup or CPU verification. Optional
  CUDA installation is attempted only after a positive local hardware probe.
- Added exact installed-distribution checks, `pip check`, lock/source/
  interpreter identities, pip installation reports, direct wheel URL/archive
  hashes, wheel tags and CPython compatible platform tags.
- Added mandatory exact verification of all 40 pipeline model manifest rows.
  CPU verification does not assemble or require the VLM model. CUDA
  initialization remains a separate profile and verifies the assembled VLM.
- Added synthetic `pipeline --method txt` and `pipeline --method ocr` profile
  verification with English OCR, formulas and tables enabled. Before a verify
  receipt is sealed, the code instantiates the pipeline model and proves that
  layout, OCR, formula, table classification, table orientation, wired-table
  and wireless-table components actually loaded.
- Added optional CUDA synthetic local hybrid and VLM routes. The VLM verify
  receipt records `method: null`, `cli_method_argument: omitted` and
  `effective_method_scope: not_applicable`; the CLI argv contains no
  `--method` for VLM. Packet B must carry the same rule into its view schema.
- Added `nri.mineru_provider_capabilities.v1` with exact ordered providers
  `pipeline_cpu`, `hybrid_cuda`, `vlm_cuda`. Required CPU can be `ready` or
  fail-closed `invalid`, never `unavailable`; only optional providers can carry
  hardware-unavailable evidence. Ready providers require an exact local verify
  receipt identity.
- Child runtime environment strips proxy/API URL/model-source/device/PYTHONPATH
  leakage and binds HF, ModelScope, temp and cache paths below the profile
  runtime. Offline model loading and bounded CPU concurrency are explicit.
- Updated the MinerU README to describe CPU-first setup and provider-scoped
  capability semantics. No remote host, Bogdan path, external MinerU HTTP
  service, HTTP-client backend or scenario-named executable was added.

## Authorized model-byte remediation

The orchestrator forwarded explicit user authorization for this exact repair.
The scoped root `.gitattributes` rule is:

```text
MinerU/models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml -text
```

Before the write, the exact file was reverified as:

- bytes: `2344759`
- SHA-256: `355B1D9364ED6130DF42C73DC2503BAA9628E3708DEEB8F964782165DCDF6245`

A byte-level CRLF-to-LF transform was computed in memory and written only after
its prospective identity matched the manifest. The final file is:

- bytes: `2244564`
- SHA-256: `87B5F3D7F2B2FE553627D77B37F496608CA150EBD0EF62D362591EDCA47B5538`
- CRLF sequences: `0`

No other model payload was modified. A full post-write audit verified all 40
pipeline manifest rows by exact byte count and SHA-256.

## Files changed

- `.gitattributes`
- `MinerU/README.md`
- `MinerU/requirements.windows-cpu-pipeline.lock.txt` (new)
- `MinerU/requirements.windows-cu128-provider.lock.txt` (new)
- `MinerU/models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml`
- `MinerU/scripts/profile-common.ps1` (new)
- `MinerU/scripts/profile_receipt.py` (new)
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/initialize.ps1`
- `MinerU/scripts/verify.ps1`
- `MinerU/scripts/probe-capability.ps1`
- `kb_creator/contracts/mineru_provider_capabilities.v1.schema.json` (new)
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py` (new)
- `kb_creator/tests/test_mineru_three_view_tools.py`
- this receipt

`MinerU/scripts/run-hybrid.ps1` and unrelated dirty/untracked repository files
were not changed by this Packet A implementation.

## Verification performed

- PowerShell parser: PASS for `setup.ps1`, `initialize.ps1`, `verify.ps1`,
  `probe-capability.ps1` and `profile-common.ps1`.
- Python syntax/import exercised by the focused test suite: PASS.
- Focused tests:

```text
28 passed in 5.73s
```

Command scope:

```text
kb_creator/tests/test_mineru_cpu_profile_packet_a.py
kb_creator/tests/test_mineru_three_view_tools.py
```

- Pipeline model manifest audit: PASS, `40/40` exact size and SHA-256.
- Git diff whitespace check over Packet A tracked paths: PASS (Git emitted only
  expected checkout line-ending warnings for ordinary text/PowerShell files).
- A read-only pip `--dry-run --ignore-installed` resolution against pinned
  MinerU `src[pipeline]` confirmed the CPU dependency closure and critical
  Windows/CPython wheel availability. Its transient report and temporary pip
  cache were removed. Nothing was installed.

## Preserved evidence and prohibited actions

- No real Dissociation source was opened or executed through MinerU.
- No dependency, venv, model or runtime was installed and `.tools` was not
  mutated by Packet A.
- No remote computer, task handoff, Bogdan host, API or external MinerU service
  was used.
- The sealed historical `20260914-no-cuda-skip-01` run and legacy v1 validators
  were not modified, resumed, converted or promoted.
- No Git index, commit or history operation was performed.

## Pending evidence and next action

The following architecture acceptance evidence is intentionally still pending:

1. independent Packet A implementation review with no P0/P1 finding;
2. explicit orchestrator authorization for a fresh live setup after review;
3. clean CPU profile installation below `.tools`, exact install receipt,
   `pip check`, both synthetic MinerU smokes and model-load receipt;
4. absent-GPU provider receipt showing `pipeline_cpu: ready` and only
   `hybrid_cuda` / `vlm_cuda: unavailable`;
5. independent review of that live verification evidence before Packet B or
   any fresh real-source run.

Until those steps close, Packet A is implementation-ready but runtime
acceptance remains pending and real source execution remains blocked.
