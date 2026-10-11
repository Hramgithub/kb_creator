# Architect receipt and specification — MinerU 3.4.4 CPU-first local execution

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-first-execution-architecture`
- Role: architect
- Requested model: `gpt-5.6-sol`
- Requested reasoning effort: `high`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Scoped override: none for architecture. The goal's engineering-only
  `gpt-5.6-sol`/`high` user override remains owned and recorded by the
  orchestrator.
- Scope: implementation-ready, scenario-neutral remediation specification for
  MinerU `3.4.4` CPU-first reconstruction on the current PC only; dependency
  and model profiles, provider capabilities, RunSpec/stage/view contracts,
  adapters, comparison/review/fidelity behavior, resume/cache migration,
  compatibility, and tests
- Result: specification complete. The current global CUDA gate is the wrong
  boundary. A fresh run can remain a six-stage reconstruction run when Stage
  02 contains three mandatory local CPU MinerU views and provider-scoped
  optional local GPU results. Missing NVIDIA seals only the optional GPU view
  receipts as `SKIPPED`; it does not skip Stage 01, Stage 02, the run, review,
  fidelity, candidate materialization, or promotion.
- Timestamp: `2026-09-14T15:54:01+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:55:00`, including the superseded initial
  CPU-fallback analysis before the corrected assignment
- Token use: unavailable

This is an architecture/remediation receipt, not implementation, QA
acceptance, reconstruction acceptance, publication authority, or a release
decision.

## Accepted authority and non-negotiable boundary

The user-accepted execution policy in
`orchestrator_mineru_local_execution_decision_20260914.md` is authoritative:

1. MinerU remains the reconstruction engine. Poppler, PyMuPDF and other local
   libraries may prepare or render evidence, but they do not replace MinerU.
2. The required evidence baseline is exactly:
   - `original_pipeline_txt`: original immutable PDF, MinerU
     `--backend pipeline --method txt`;
   - `original_pipeline_ocr`: original immutable PDF, MinerU
     `--backend pipeline --method ocr`;
   - `raster_pipeline_ocr`: full-MediaBox raster derivative, MinerU
     `--backend pipeline --method ocr`.
3. `auto` is forbidden as an evidence-view method. It is a selector, not an
   independent view.
4. `original_hybrid_high` and `original_vlm` are optional local enrichment.
   They run only when their own verified provider capability is ready. A
   missing NVIDIA/CUDA capability gives those provider/view invocations a
   sealed successful `SKIPPED` result.
5. All processing stays on this current PC. Remote execution, another
   station, Bogdan, agent/task handoff for execution, cloud inference, an
   external MinerU HTTP endpoint, `vlm-http-client`, and
   `hybrid-http-client` are forbidden, not fallback choices.
6. The wrapper may use MinerU 3.4.4's own transient loopback child service as
   an internal CLI implementation detail. No URL or endpoint may be accepted
   from the scenario contract, RunSpec, environment, or CLI. The wrapper must
   never pass `--api-url`, `--url`, or an HTTP-client backend.
7. Every task-installed runtime, venv, wheel cache, Hugging Face cache,
   ModelScope cache, assembled model, temporary file and execution cache lives
   below the repository `.tools/` root. A system/Codex Python or `uv` may only
   bootstrap the repository-local runtime; it is not a bound production
   interpreter.
8. No scenario-named executable is permitted. A closed generic execution
   profile or reconstruction contract may select the CPU-first profile and OCR
   language, but may not supply a command, executable path, URL, import, or
   arbitrary provider.

## Current evidence and earliest failing layer

### Source and reconstruction facts

The six-page source is suitable for the three mandatory CPU views. Its
embedded text is substantial on pages 2-6, but raw extraction interleaves the
two columns. The required review baseline remains:

- page 1: visual cover and source parser anomaly;
- pages 2-6: explicit left/right reading-order closure;
- page 3: black `NAMES` / `OCCUPATIONS` card structure;
- page 5: full-width raster Alaska map/ad, regional text recovery and
  text-to-asset ownership;
- page 6: `HUMAN RESISTANCE` statblock structure;
- all pages: full `595 x 841` MediaBox authority, never the shorter CropBox.

The CPU three-view profile does not claim MinerU hybrid/VLM parity. It proves
only three explicit MinerU pipeline observations plus source render evidence.
GPU-enriched results, when present, remain additional alternatives, never the
truth source and never an acceptance signal.

### Runtime/tool evidence

- Pinned source: MinerU commit
  `79d6d8d79fb8f3ddba5cc34c07a16f0ec36f56c7`, package version `3.4.4`.
- Upstream local source explicitly documents `pipeline` as CPU-capable and
  exposes methods `txt` and `ocr`.
- The current `.tools/MinerU/.venv` uses Python `3.12.14`, but is a partial
  interrupted environment. It has neither `mineru`, `torch` nor `lmdeploy`.
  It is not a valid CPU or GPU execution profile and must not be repaired in
  place and then presented as a clean install.
- The existing `requirements.windows-cu128.lock.txt` is CUDA/all-extras
  shaped. It contains `torch==2.8.0+cu128`, `lmdeploy==0.11.1`,
  `triton-windows==3.4.0.post21` and other GPU/VLM dependencies. It cannot be
  the CPU baseline.
- Repository-local Poppler `26.02.0` and Tesseract `5.4.0.20240606` are
  present. Poppler is required for visual rendering. Tesseract is not one of
  the accepted MinerU views and must not silently become a fourth source view.
- PyMuPDF `1.28.2` is currently available only through the isolated
  `.tools/python-test-deps` path, not through the partial MinerU venv. The
  production CPU profile must carry its own pinned PyMuPDF because Stage 01
  uses it to create the full-MediaBox raster PDF.
- The current CUDA receipt correctly reports
  `nvidia_device_not_detected`, but it is a GPU-provider fact, not a run-global
  reconstruction capability.

### Model-byte blocker

The current pipeline model set has 40 manifest rows. Thirty-nine working files
match their declared byte count. The tracked file
`models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml`
is `2,344,759` bytes in the working tree with SHA-256
`355B1D9364ED6130DF42C73DC2503BAA9628E3708DEEB8F964782165DCDF6245`,
while `models/manifest.json` declares the Git-blob LF identity of `2,244,564`
bytes. Git currently applies `text: auto`; the file has 100,195 lines, which
accounts for the CRLF expansion. A strict runtime verification would fail even
though Git reports the checkout clean.

This is a P0 pre-source-run blocker. The implementation must make the pipeline
model tree byte-stable on checkout (recommended scoped `.gitattributes`
`-text` rule), restore/materialize the exact declared bytes, and verify every
CPU-required model before setup can report ready. It must not rewrite the
manifest to bless station-specific CRLF bytes, normalize bytes only during
verification, or weaken model identity checks.

## Target directory and installation topology

Use separate complete environments so optional GPU installation cannot replace
or contaminate the CPU PyTorch baseline:

```text
.tools/
  python/
    cpython-3.12.14-windows-x86_64/       # task-managed base runtime
  uv/
    cache/                                # only if uv is used
  pip-cache/
  MinerU/
    profiles/
      pipeline-cpu-v1/
        .venv/
        install-receipt.json
        verify-receipt.json
      windows-cu128-v1/
        .venv/
        install-receipt.json
        verify-receipt.json
    runtime/
      pipeline-cpu-v1/
        mineru.json
        tmp/
        hf/
        modelscope/
      windows-cu128-v1/
        mineru.json
        models/vlm/
        tmp/
        hf/
        modelscope/
    capabilities/
      hardware.json
      providers.json
```

The legacy `.tools/MinerU/.venv`, `.tools/MinerU/.runtime`, and
`.tools/MinerU/capability.json` remain readable evidence for the sealed v1
skip run. New setup and new runs must never resolve them as the CPU-first
profile.

### Mandatory profile: `mineru-pipeline-cpu-windows-v1`

Closed profile requirements:

- platform: Windows x86-64;
- Python: CPython `3.12.14`, installed under `.tools/python/`; exact executable
  bytes and `sys.version` recorded;
- MinerU: editable/no-deps install of the tracked `MinerU/src` at version
  `3.4.4`, bound to the source commit and a deterministic source inventory;
- dependency lock: new complete
  `MinerU/requirements.windows-cpu-pipeline.lock.txt`;
- required top-level dependency set: MinerU base dependencies plus the
  `pipeline` extra, with repository control dependencies
  `PyMuPDF==1.28.2`, `pypdf==6.16.0` and `reportlab==5.0.0` included in the
  same closed lock;
- core inference pins: `torch==2.8.0+cpu`,
  `torchvision==0.23.0+cpu`, `transformers==4.57.6`,
  `onnxruntime==1.28.0`; every transitive package is exactly pinned by the
  lock, and the lock SHA-256 is recorded;
- CPU wheel source: the pinned PyTorch CPU index for the two PyTorch wheels;
  all other indexes/sources are recorded in the install receipt. The installed
  distribution inventory and `pip check` must equal the reviewed lock;
- forbidden distributions in this profile: CUDA-tagged Torch wheels,
  `lmdeploy`, `triton-windows`, `torch-c-dlpack-ext`, `vllm`, `mlx-vlm`, and
  `torchaudio` (not required by MinerU's `pipeline` extra);
- required model authority: only the exact 40 `models/pipeline/**` rows after
  the byte-stability remediation; VLM assembly and VLM hashes are not CPU
  setup prerequisites;
- verification: imports MinerU/pipeline dependencies, proves MinerU `3.4.4`,
  proves `torch.version.cuda is None`, proves
  `torch.cuda.is_available() is False`, loads the local pipeline config/model
  paths, performs a synthetic one-page pipeline/txt and pipeline/ocr smoke
  test, and inventories the created output shape without using the real
  source.

The lock must be generated and reviewed from the pinned source metadata, then
installed with exact versions. A `pip freeze` captured after an ad hoc install
is evidence, not the authority from which to infer the lock.

### Optional profile: `mineru-local-windows-cu128-v1`

This is a separate complete venv, not a delta installed into the CPU venv.

- Python and MinerU source identities match the CPU profile.
- The reviewed full lock is derived from the current CUDA lock but limited to
  the local pipeline/VLM/hybrid requirements actually used by these providers.
- Required GPU pins preserve the proven profile:
  `torch==2.8.0+cu128`, `torchvision==0.23.0+cu128`,
  `lmdeploy==0.11.1`, `transformers==4.57.6`,
  `triton-windows==3.4.0.post21`, and
  `torch-c-dlpack-ext==0.1.5`. Do not carry `torchaudio` unless a direct
  import/use test proves it is required; MinerU's declared pipeline/VLM/
  lmdeploy extras do not require it.
- Verification requires a successful `nvidia-smi` query, imported package
  pins, `torch.cuda.is_available()`, selected device identity, exact pipeline
  models, exact assembled VLM model, config identity, and one synthetic local
  hybrid/VLM smoke. A detected NVIDIA device with a corrupt/mismatched
  installed profile is `invalid`, not `SKIPPED`.
- `MINERU_LMDEPLOY_DEVICE=cuda`, the reviewed Windows LMDeploy backend setting,
  and the current static-launcher compatibility control are explicit and
  identity-bound. No HTTP-client provider is installed or exposed.

Default `setup.ps1` behavior becomes: install/verify mandatory CPU first;
probe optional GPU second; if GPU hardware is absent, emit provider-level
unavailable receipts and exit success with CPU ready. It must never return a
global `MinerU setup: SKIPPED` merely because NVIDIA is absent.

## Provider capability contract

Retain `nri.mineru_cuda_capability.v1` and `kb_creator.run_skip.v1` only for
verification of historical v1 runs. New runs use a closed
`nri.mineru_provider_capabilities.v1` receipt with exactly three provider
records:

```json
{
  "schema": "nri.mineru_provider_capabilities.v1",
  "checked_at_utc": "...",
  "execution_boundary": "current_station_local_only",
  "providers": [
    {
      "provider_id": "pipeline_cpu",
      "required": true,
      "state": "ready",
      "reason_code": "verified_cpu_profile",
      "profile": "mineru-pipeline-cpu-windows-v1",
      "verification_receipt": {"path_hint": "...", "bytes": 1, "sha256": "..."}
    },
    {
      "provider_id": "hybrid_cuda",
      "required": false,
      "state": "unavailable",
      "reason_code": "nvidia_device_not_detected",
      "profile": "mineru-local-windows-cu128-v1",
      "verification_receipt": null
    },
    {
      "provider_id": "vlm_cuda",
      "required": false,
      "state": "unavailable",
      "reason_code": "nvidia_device_not_detected",
      "profile": "mineru-local-windows-cu128-v1",
      "verification_receipt": null
    }
  ],
  "receipt_sha256": "..."
}
```

Rules:

- `pipeline_cpu` must be `ready`; `unavailable`, absent or stale is a preflight
  error, never a skip.
- Optional providers may be `ready`, `unavailable`, or `invalid`. Only
  `unavailable` from an allowed capability reason (no NVIDIA device, missing
  driver/`nvidia-smi`, unsupported local GPU) becomes a successful skipped
  view. `invalid` means a provider that should be usable has dependency,
  model, config, hash or smoke-test drift and blocks preflight.
- Provider order and uniqueness are exact. Unknown providers, URLs, remote
  modes, empty evidence for `ready`, a receipt outside `.tools`, or a receipt
  changed after RunSpec creation fail closed.
- Run creation copies and seals the receipt into the new run. Resume uses the
  snapshot as execution authority and revalidates the installed profiles used
  by succeeded views. It does not rewrite/re-probe capabilities or add a newly
  available optional view to an existing run.

## RunSpec and fixed stage graph

Add `kb_creator.run_spec.v2` rather than changing the meaning of sealed v1
evidence. Its profile is the constant
`mineru_cpu_first_three_view_v1`. The six stage ids and high-level boundaries
remain stable:

```text
01 prepare_inputs
02 mineru_three_view
03 compare_views
04 visual_merge_bundle
-- exit 10 / needs_review --
05 fidelity_audit
06 materialize_candidate
```

The RunSpec v2 portable section contains:

- the existing exact scenario contract, source, page scope and implementation
  inventory;
- `execution_boundary` fixed to current-station/local-only and booleans
  forbidding remote endpoints and external services;
- `view_plan`, in this exact order:
  1. `original_pipeline_txt`, required, `pipeline_cpu`, original input,
     backend `pipeline`, method `txt`;
  2. `original_pipeline_ocr`, required, `pipeline_cpu`, original input,
     backend `pipeline`, method `ocr`;
  3. `raster_pipeline_ocr`, required, `pipeline_cpu`, raster input, backend
     `pipeline`, method `ocr`;
  4. `original_hybrid_high`, optional, `hybrid_cuda`, original input, backend
     `hybrid-engine`, method `txt`, effort `high`;
  5. `original_vlm`, optional, `vlm_cuda`, original input, backend
     `vlm-engine`, method not applicable.
- explicit required `ocr_language` from a closed MinerU language enum. For
  Dissociation the RunSpec value is `en`; do not rely on MinerU's `ch`
  default. The language is a generic runtime/profile input, not a scenario
  branch in code.
- the existing `raster_dpi`, `review_dpi`, `source_box: MediaBox` and
  run-local verified-cache policy;
- exact provider capability snapshot identity;
- tool/runtime identities grouped by provider, including Python executable,
  MinerU launcher, source inventory, dependency lock and installed
  distribution inventory, config, required model manifest, wrapper and
  Poppler/PyMuPDF identities actually used.

The local section supplies resolved paths only. Schemas and portable identity
contain no device-specific absolute path authority. Unknown view ids,
reordering, duplicated ids, an `auto` method, an HTTP backend, a URL field, or
an executable from a contract is rejected before run-root creation.

### Stage 01 — prepare inputs

- Runs with the verified CPU profile Python.
- Revalidates source/contract/implementation identities.
- Produces only the deterministic full-MediaBox raster PDF and preparation
  manifest; the original immutable PDF is referenced, not copied or changed.
- Records PyMuPDF, pypdf and ReportLab identities and exact page mapping.
- The raster must have no text layer, exact page count, correct displayed
  geometry and a hash-bound source lineage.

### Stage 02 — MinerU view set

Stage 02 is successful only if all three required CPU view manifests are
`succeeded` and each optional view manifest is terminal `succeeded` or allowed
`skipped`. It emits:

```text
outputs/02-mineru-three-view/
  view-set.json
  views/<view-id>/view.json
  views/<view-id>/artifacts/...          # only for succeeded views
```

Each `kb_creator.mineru_view_execution.v1` is independently sealed and
contains:

- view id, required flag, provider id and RunSpec identity;
- exact source/prepared-input file identity;
- closed backend/method/language/formula/table/effort values and an argv-shape
  version, not a raw user-supplied command;
- capability snapshot and provider verification receipt identities;
- Python/MinerU/config/model/lock/installed-distribution/wrapper identities;
- state `succeeded` with an exact output inventory, required MinerU artifacts,
  page coverage, exit code `0` and diagnostics; or state `skipped` with an
  allowed optional-GPU reason, `blocked_by` capability identity, no artifact
  root and no output inventory;
- a view cache key and view receipt SHA-256.

`view-set.json` records the ordered required set, all provider results and the
ordered succeeded-view set. It must prove exactly three succeeded required
views. A required-view skip, a skipped view with files, an optional skip after
an invocation error, or an output missing `_content_list.json`,
`_content_list_v2.json`, `_middle.json`, Markdown or `_layout.pdf` fails Stage
02. A provider reported `ready` that later exits nonzero is a stage failure,
not a capability skip.

### Stage 03 — comparison

Extend the comparator additively with an identity-bound `--view-set-manifest`
input. Keep the old three positional view options for legacy tests/runs, but
new production adapters use only the manifest mode.

The new comparison schema is `kb_creator.mineru_multi_view_comparison.v2`.
It:

- requires the exact three CPU baseline views and compares every required
  pair;
- includes every succeeded optional GPU view in pairwise comparison without
  requiring it for baseline status;
- records skipped optional views and their sealed receipt identities, but
  never invents blocks, layout PDFs or parity results for them;
- fails on missing/extra pages, missing required layout PDF, unsafe/missing
  asset references, duplicate artifacts, wrong input identity or non-exact
  original/raster lineage;
- calls the result `pass_for_review`, not `GPU parity`, `hybrid parity`,
  reconstruction success or acceptance.

### Stage 04 — visual merge bundle and review queue

The required three CPU views always produce the stable triptych used for page
review. Optional succeeded GPU views appear as separately labelled companion
panels or an additional comparison grid; they do not change the required
triptych's positions or suppress a CPU discrepancy.

Merge packets retain the existing dynamic `views` map and per-page block
references. Review-signal calculations use the required CPU set as the
baseline and report optional deltas separately. The existing decision-set and
per-page decision contracts can remain v1 because they already validate view
names against the actual packet instead of a hard-coded enum.

Every source page remains an open review item. For Dissociation, generic
contract-derived routing must require `reading_order` for pages 2-6,
`visual_preserve` for page 1 and all source visuals, `ocr_region` for page 5,
and `structured_statblock` for page 6. The page-3 card must appear through
page-fidelity/semantic-conflict evidence; if implementation adds a dedicated
`structured_card` issue kind, that requires a schema version/additive test and
must not be scenario-named.

No score, majority vote, identical CPU output or optional GPU agreement closes
a decision. Human page decisions still select exact block ids/assets, contain
reviewed Markdown, preserve unresolved items as blockers, and require visual
review.

### Stages 05-06 and promotion

The fidelity auditor remains lexical and decision-bound; it audits the exact
selected blocks from the dynamic merge packet. The materializer already uses
the packet's view map and should remain provider-neutral. It must not require
`original_hybrid` or claim that a CPU choice is a hybrid choice.

Preserve the public promotion interface if implementation evidence permits:

- commands remain `python -m kb_creator reconstruction-promotion materialize`
  and `record-acceptance`;
- six stage ids, candidate topology, decision submission, fidelity report,
  package role names and the separate acceptance receipt remain unchanged;
- the package-side v1 validator gains closed profile dispatch: strict existing
  validation for v1 MinerU runs and strict v2 validation for CPU-first runs.
  Do not loosen v1 exact-key or seal validation;
- `reconstruction-upstream-v1` may continue as the external package boundary
  because its schema records the six stage receipts and run identity without
  promising a particular MinerU provider. If a field is discovered to encode
  `mineru_three_view_v1` semantically rather than generically, create an
  additive upstream v2 and update publication preflight explicitly; do not
  mutate an accepted v1 meaning silently.

Promotion still requires all six succeeded stage manifests, closed decisions,
no unresolved items, passing fidelity and reconstruction QA. Provider-level
GPU `SKIPPED` is permitted only inside the successful Stage 02 view-set
evidence. No global run skip is promotable.

## Exact adapter invocation and environment

Extend the generic wrapper, without a scenario branch, with closed profiles
`pipeline_txt`, `pipeline_ocr`, `hybrid_high` and `vlm_local`. New Stage 02
adapter calls are mechanically constructed as follows (paths are resolved by
the control plane, never supplied by the scenario contract):

```text
original_pipeline_txt:
  mineru --path <exact-original-pdf> --output <empty-stage-view-root>
         --backend pipeline --method txt --lang <RunSpec-language>
         --formula True --table True --start 0 --end <page-count-1>

original_pipeline_ocr:
  mineru --path <exact-original-pdf> --output <empty-stage-view-root>
         --backend pipeline --method ocr --lang <RunSpec-language>
         --formula True --table True --start 0 --end <page-count-1>

raster_pipeline_ocr:
  mineru --path <exact-Stage-01-raster-pdf> --output <empty-stage-view-root>
         --backend pipeline --method ocr --lang <RunSpec-language>
         --formula True --table True --start 0 --end <page-count-1>

original_hybrid_high, only if ready:
  mineru --path <exact-original-pdf> --output <empty-stage-view-root>
         --backend hybrid-engine --method txt --effort high
         --formula True --table True --start 0 --end <page-count-1>

original_vlm, only if ready:
  mineru --path <exact-original-pdf> --output <empty-stage-view-root>
         --backend vlm-engine --formula True --table True
         --start 0 --end <page-count-1>
```

The wrapper must record the actual upstream `mineru --help`/version surface and
reject the run if these reviewed flags are no longer accepted. Start/end are
zero-based MinerU indices derived from the exact all-pages RunSpec domain.

For required CPU views set and record at minimum:

- `MINERU_DEVICE_MODE=cpu`;
- `MINERU_TOOLS_CONFIG_JSON` to the exact CPU config;
- `HF_HOME`, `HUGGINGFACE_HUB_CACHE`, `HF_XET_CACHE`,
  `MODELSCOPE_CACHE`, `TEMP` and `TMP` below the CPU runtime root;
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` after local model
  verification;
- bounded CPU execution defaults
  `MINERU_PROCESSING_WINDOW_SIZE=1` and
  `MINERU_API_MAX_CONCURRENT_REQUESTS=1`, recorded in RunSpec. A future
  reviewed profile may tune them; environment leakage may not.

Remove proxy variables from the child environment. Do not inherit an API URL,
server URL, model-source override, device override, Python path, user cache or
temporary directory. Allowlist the complete child environment and record it
with secrets redacted.

## Cache, resume and failure semantics

- The fixed graph remains run-local. No old output or cache is trusted merely
  because filenames match.
- Stage 01 cache key binds source, contract, selected pages, full-MediaBox
  raster options, preparer implementation and CPU preparation tool identities.
- Each Stage 02 view has its own cache key binding input PDF, view descriptor,
  provider capability snapshot, profile/lock/distribution/config/model/tool
  identities and wrapper/argv-shape version.
- Stage 02's aggregate key binds the ordered five view receipt seals. A skipped
  optional view therefore remains explicit reproducible evidence.
- Stages 03-06 bind the complete ordered view set, comparison/packet/decision
  identities and their existing implementation/tool inputs.
- Partial or failed provider output is quarantined under the new run; it can
  never be resealed as a skip. Required-view failure prevents comparison.
- First-pass success still returns `needs_review`, exit code `10`. Resume only
  consumes the exact sealed queue and closed decision submission.
- Resume revalidates source, contract, implementation, Stage 01-04 manifests,
  all succeeded-view profile/tool/model identities and the original capability
  snapshot. It never adds/removes a view after decisions exist.
- A GPU capability change after a CPU-only run does not invalidate review
  resume, because the sealed skipped provider was not used. To obtain GPU
  enrichment, start a fresh run. A change to a used CPU profile, model, tool,
  contract, source, queue or decision remains stale and fails closed.

## Safe migration from the sealed old skip run

`20260914-no-cuda-skip-01` must remain byte-for-byte immutable. Its
`run.json`, `skip.json`, RunSpec v1 identity
`72095696C9C0E304E3F8D8CED9B387C21272203592567ACAEF1D984AB63CF292`
and v1 CUDA receipt remain valid evidence of superseded behavior.

Migration is additive:

1. Keep v1 loaders/verifiers able to validate and reject promotion/resume of
   the old global-skip run.
2. Never rewrite, rename, delete, resume, convert, import stages from, or copy
   cache/output from that root.
3. Install and independently verify the fresh CPU profile under its new
   profile path.
4. Create a fresh RunSpec v2 and absent run root with a new run id on this same
   station.
5. The new run may reference the old run only as a human-readable supersession
   note outside reproducible identity; it cannot use it as upstream evidence.

The existing legacy GPU `mineru_three_view_v1` route remains readable and
testable. Its historical hard-coded view names and global CUDA semantics do
not enter a new CPU-first run. New code should use profile-dispatched adapters
and validators instead of changing constants so old sealed evidence acquires a
new meaning.

## Minimal implementation packets

### Packet A — install/profile and capability boundary

Owned files:

- add `MinerU/requirements.windows-cpu-pipeline.lock.txt`;
- add a reviewed complete optional CUDA profile lock, retaining the old lock
  as legacy evidence until parity is proven;
- add separate pipeline/VLM model manifest views or a deterministic validated
  filter over the existing manifest;
- modify `.gitattributes` only for byte-stable MinerU model payload checkout;
- modify `MinerU/scripts/setup.ps1`, `initialize.ps1`, `verify.ps1` and
  `probe-capability.ps1`;
- add provider-capability schema/tests and update setup tests.

Stop before any real source run. Completion evidence includes a clean fresh CPU
install below `.tools`, exact dependency/model verification, two synthetic
pipeline smokes, absent-GPU provider skips, no user/system cache writes and no
changes to the sealed old run.

### Packet B — RunSpec/view execution and comparison

Owned files:

- add RunSpec v2, provider capability and view/view-set schemas;
- modify `kb_creator/pipeline/reconstruction.py`, `kb_creator/__main__.py`, the
  generic MinerU wrapper, comparator and visual merge bundle;
- add comparison v2/schema if schema validation is introduced;
- update focused control-plane, three-view, visual-bundle, audit and
  materializer tests.

It preserves the six stages, legacy adapters and v1 verification. Completion
evidence is a synthetic full CPU run to exit `10`, closed-decision resume to a
candidate, optional-GPU skip evidence, and adversarial closure. It still does
not run the real Dissociation source.

### Packet C — promotion compatibility

Owned files are limited to the reconstruction promotion bridge, its schemas
only if strictly necessary, and focused promotion/publication-preflight tests.
Prefer closed profile dispatch while preserving the v1 external package and
CLI. Any need for an upstream v2 is a stop-and-return architecture decision,
not an opportunistic schema relaxation.

After all packets pass independent implementation review, a bounded executor
may start one fresh real source run on the current PC. No remote/handoff
execution is authorized.

## Focused and adversarial test specification

### P0 tests

- Fresh CPU setup occurs despite absent NVIDIA and creates only repository
  `.tools` runtime/cache paths.
- CPU verification proves MinerU `3.4.4`, CPU Torch, exact lock/distributions,
  exact 40 pipeline model rows, local config and both synthetic methods.
- The CRLF-expanded pipeline YAML is rejected; byte-stable exact materialization
  passes without changing the declared model authority.
- Required view plan is exactly the three accepted CPU views and contains no
  `auto`, URL or HTTP-client backend.
- With GPU unavailable, Stage 01 succeeds, all three CPU views succeed, both
  optional GPU views have sealed output-free `SKIPPED` receipts, Stage 02
  succeeds, Stage 03/04 run, and the run stops only at `needs_review`.
- A required CPU provider/view cannot be skipped. Missing CPU Torch, MinerU,
  model, PyMuPDF, config or lock identity blocks before run-root creation or
  quarantines the owning stage on execution drift.
- Original/txt and original/ocr bind the immutable source; raster/ocr binds
  the exact Stage 01 raster. Input substitution and original/raster swap fail.
- Every required view has exact page coverage and all required MinerU
  artifacts. Missing/extra page, missing layout, unsafe asset reference and
  partial output fail.
- Comparator/visual bundle produce a required CPU triptych for every page and
  do not claim hybrid/VLM/GPU parity when those views are skipped.
- Pages 1-6 enter the review queue; contract-derived issue kinds cover the
  two-column pages, cover, page-5 OCR/visual requirement and page-6 statblock.
- Closed decisions may select any succeeded packet view but cannot reference a
  skipped/unknown view or stale raw index. Fidelity and materialization remain
  exact and candidate status is not acceptance.
- Resume rejects source/contract/code/tool/lock/distribution/model/config/
  provider/view-set/queue/decision drift and refuses to add a newly available
  optional provider.
- Promotion accepts a fully closed CPU-first six-stage candidate through the
  same public commands, preserves separate explicit acceptance, and keeps the
  old globally skipped run unpromotable.
- Static/AST tests prove no remote host, Bogdan path, external API URL,
  `*-http-client`, scenario name or user-supplied executable is reachable from
  the new production path.

### P1 tests

- GPU-ready fixture adds hybrid/VLM results without changing the order or
  identities of the mandatory CPU baseline; their failures cannot be rewritten
  as capability skips.
- Capability receipts reject duplicate/unknown providers, unavailable required
  CPU, unsupported skip reasons, ready-without-verification, path escape,
  reparse/symlink escape and receipt mutation.
- Setup rejects use of the partial legacy venv, task caches outside `.tools`,
  dependency extras not in the lock, `pip check` failure and unexpected
  installed distributions.
- Environment poisoning through proxy, API URL, device, cache, temp,
  `PYTHONPATH`, model source or MinerU config variables is removed or rejected
  and recorded.
- Mixed MediaBox/rotation, CropBox rendering, text-bearing raster derivative,
  stale raster and changed page mapping fail before OCR.
- Dynamic comparison produces all required pairwise rows, optional rows only
  for succeeded providers, deterministic ordering and no divide-by-fixed-three
  or hard-coded legacy-view behavior.
- Visual-bundle legacy fixtures remain byte/semantic compatible where already
  asserted; old v1 run/skip validation remains green and immutable.
- Complete existing focused reconstruction and promotion suites pass, with the
  old tests that demand six global skips replaced—not merely supplemented—by
  provider-level skip tests.

## Acceptance criteria

### P0 — required before any real source execution

- [ ] CPU baseline and optional CUDA profile are separate, fully pinned,
      identity-bound and installed only below `.tools`.
- [ ] The mandatory CPU profile is freshly installed and verified; the partial
      legacy venv is not used as evidence.
- [ ] All 40 CPU model files match immutable declared bytes/hashes; the current
      CRLF mismatch is closed without weakening verification.
- [ ] RunSpec v2 fixes the exact three CPU views, forbids `auto`/remote/API
      inputs and binds `ocr_language: en` for the Dissociation run.
- [ ] Missing NVIDIA produces only two sealed optional provider/view skips;
      the six-stage run continues to `needs_review`.
- [ ] Comparison, review queue, decisions, fidelity, materialization and
      promotion consume the dynamic succeeded-view set without requiring
      `original_hybrid`.
- [ ] Source identity, MediaBox, page coverage, tool/model/config/lock identity,
      path containment, output inventories and resume invalidation remain
      fail-closed.
- [ ] No automatic merge, reconstruction acceptance, publication acceptance or
      release claim is introduced.
- [ ] An independent implementation critic reports no P0/P1 finding before the
      fresh real run root is created.

### P1 — required before reconstruction promotion

- [ ] Legacy v1 GPU/skip evidence remains verifiable and immutable; the old
      skip remains unresumable and unpromotable.
- [ ] Optional ready GPU views enrich but never replace the CPU baseline, and
      absent GPU never produces false parity language.
- [ ] Required page-specific fidelity risks are visible and closeable only by
      explicit reviewed decisions.
- [ ] Promotion/publication preflight compatibility is proven through focused
      synthetic E2E without weakening v1 validators.
- [ ] Implementation/source/contract/schema/tool/model snapshots sufficient to
      reproduce the CPU candidate are carried into the promotion package.

## Risks and controls

| Risk | Consequence | Required control |
|---|---|---|
| Treating CUDA as a run capability | Whole book incorrectly skips | Provider-scoped capabilities; CPU required |
| In-place repair of partial venv | Unreproducible dependency residue | Fresh profile path and exact installed inventory |
| CUDA wheel in CPU profile | CPU setup remains hardware-shaped | CPU index, `+cpu` pins, forbidden-package gate |
| Line-ending drift in model YAML | Clean Git checkout fails model identity | Byte-stable model attributes and exact checkout verification |
| MinerU default language `ch` | Poor English OCR | Required bound `ocr_language: en` |
| `auto` counted as a view | Duplicate/non-independent evidence | Fixed explicit txt/ocr view plan |
| Optional provider failure becomes skip | Real runtime defect hidden | Only capability-unavailable may skip; invocation failure blocks |
| Dynamic view support weakens coverage | Missing baseline view passes | Exact required-set and page-domain gates |
| GPU absence described as parity | Misleading QA/acceptance claim | `pass_for_review` wording and skipped-provider evidence |
| Newly available GPU changes resume | Decisions become stale | View set frozen at run creation; fresh run for enrichment |
| External endpoint leaks through MinerU CLI | Unauthorized remote processing | Closed local backends, env allowlist, no URL fields/flags |
| Promotion validator loosened for v2 | Historical package attacks pass | Profile-dispatched exact validators, no v1 relaxation |

## Files checked or changed

Checked:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `SETUP.md`
- `.tools/tool-manifest.json`
- `.tools/MinerU/capability.json`
- `.tools/MinerU/.venv/pyvenv.cfg` and read-only package/import inventory
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_local_execution_decision_20260914.md`
- prior PDF reconnaissance, generic control-plane, no-CUDA engineering and
  critic receipts in the same handoff directory
- sealed run `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01/{run.json,skip.json}`
- `MinerU/README.md`, `MinerU/SOURCE_VERSION.md`,
  `MinerU/requirements.windows-cu128.lock.txt`,
  `MinerU/config/mineru.template.json`, `MinerU/models/manifest.json`
- `MinerU/scripts/{setup,initialize,verify,probe-capability}.ps1`
- pinned MinerU `src/pyproject.toml`, CLI/backend/device/config sources and
  version declaration
- `kb_creator/__main__.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- reconstruction RunSpec, stage, queue, decision, skip and promotion schemas
- the five reconstruction scripts plus the visual merge bundle
- focused reconstruction, MinerU-tool, visual-bundle, materialization,
  fidelity and promotion tests

Changed:

- added only this immutable receipt:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_mineru_cpu_first_execution_spec_20260914.md`

No production code, test, dependency, model, source, generated output, sealed
run, canonical plan/context/status/release file, Git index or Git history was
changed.

## Verification/evidence, blockers and next action

Verification was read-only: local source/metadata inspection, current venv
import/version probe, repository-local Poppler/Tesseract version probe,
pipeline model size comparison, Git attribute/blob inspection, and sealed old
run inspection. No source PDF was executed through MinerU and no dependency was
installed.

Blockers:

1. The CPU profile lock and fresh local runtime do not yet exist.
2. The current run-global CUDA gate, fixed legacy view names and whole-run skip
   tests implement superseded policy.
3. One CPU pipeline model YAML is not byte-stable in the current checkout and
   does not match its manifest identity.
4. Promotion compatibility with a v2 run/stage/view identity must be proven by
   implementation tests; no validator weakening is allowed.

Next action: the main orchestrator should obtain an independent architecture/
process critique of this receipt, then dispatch Packet A only. After Packet A
is independently closed, dispatch Packet B and Packet C in order. Only after
all P0 criteria and independent implementation review pass may a fresh
Dissociation CPU-first run be started on this current PC. The old sealed skip
run remains immutable and no remote or handoff execution is permitted.
