# Critic receipt: MinerU CPU-first architecture review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-first-execution-architecture-review`
- Review kind: `architecture`
- Process scope included: yes, only where dependency/setup/run governance
  affects architecture acceptance
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-14T16:03:37+03:00`
- Elapsed time: approximately `00:04:00`
- Token use: unavailable for actual platform; active runtime goal reported
  `136481` tokens before receipt write

This is an independent architecture/process critique only. It is not
implementation, reconstruction acceptance, publication acceptance, release
approval, orchestration transfer, or authorization to run the real source.

## Scope

Reviewed the accepted local MinerU execution decision and the CPU-first
architecture candidate against pinned MinerU 3.4.4 source metadata, current
generic reconstruction/promotion code, contracts, SETUP/README policy, and the
sealed historical no-CUDA skip run.

Forbidden scope was honored: no production code, tests, dependency locks,
models, source files, run outputs, canonical plan/context/status/release files,
Git index, or Git history were edited. This receipt is the only file written.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `SETUP.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_local_execution_decision_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_mineru_cpu_first_execution_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_reconstruction_promotion_bridge_20260914.md`
- `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01/run.json`
- `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01/skip.json`
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/stage_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json`
- `kb_creator/contracts/reconstruction_source_identity.v1.schema.json`
- `kb_creator/contracts/review_queue.v1.schema.json`
- `kb_creator/contracts/scenario_reconstruction_contract.v1.schema.json`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/__main__.py`
- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- `MinerU/README.md`
- `MinerU/SOURCE_VERSION.md`
- `MinerU/requirements.windows-cu128.lock.txt`
- `MinerU/models/manifest.json`
- `MinerU/config/mineru.template.json`
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/initialize.ps1`
- `MinerU/scripts/verify.ps1`
- `MinerU/scripts/probe-capability.ps1`
- `MinerU/src/pyproject.toml`
- `MinerU/src/README.md`
- `MinerU/src/mineru/cli/client.py`
- `MinerU/src/mineru/cli/common.py`
- `MinerU/src/mineru/backend/pipeline/pipeline_analyze.py`
- `MinerU/src/mineru/backend/pipeline/batch_analyze.py`
- `MinerU/src/mineru/backend/pipeline/model_init.py`
- `MinerU/src/mineru/utils/config_reader.py`
- `MinerU/src/mineru/utils/models_download_utils.py`

## Evidence

- Governance requires independent critic receipts to declare review kind,
  participation, findings, evidence, blockers, recommendation, elapsed time,
  token use, timestamp, orchestrator policy owner, assignment state, and scoped
  override. This receipt follows that shape and does not transfer ownership.
- The accepted execution decision requires exactly three mandatory local CPU
  MinerU pipeline views: original `txt`, original `ocr`, and raster `ocr`.
  Optional `hybrid-engine`/`vlm-engine` may be provider-level skipped when GPU
  is unavailable; remote/API/handoff execution is forbidden.
- MinerU 3.4.4 source metadata supports Python `>=3.10,<3.14`, declares
  `pipeline` dependencies including `torch`, `torchvision`, `transformers`, and
  `onnxruntime`, and documents `pipeline` as CPU-capable.
- Live package-index probes from the current Python 3.12.14 environment found
  the candidate's critical CPU pins available: `torch==2.8.0+cpu`,
  `torchvision==0.23.0+cpu`, `onnxruntime==1.28.0`,
  `transformers==4.57.6`, `pypdf==6.16.0`, and `reportlab==5.0.0`.
- MinerU CLI source exposes `--method` choices `auto/txt/ocr`, `--backend`
  values including local `pipeline`, `vlm-engine`, `hybrid-engine` and remote
  `*-http-client`, default language `ch`, zero-based `--start/--end`, and
  `--formula`/`--table` booleans. The candidate correctly forbids `auto` as an
  evidence view, binds `ocr_language: en`, and rejects HTTP-client/URL inputs.
- MinerU pipeline source maps `--method ocr` to `ocr_enable=True` and `txt` to
  `False`. Together with separate original/raster input identities, the three
  mandatory views are sufficiently independent for a review baseline if each
  view receipt records method, effective OCR enablement, source lineage, and
  output inventory.
- MinerU default output path writes Markdown, `_content_list.json`,
  `_content_list_v2.json`, `_middle.json`, model output, origin PDF, and layout
  visualization for pipeline output. Layout drawing is warning-tolerant inside
  MinerU, so the outer wrapper's requirement that a required view fail if
  `_layout.pdf` is absent is necessary and valid.
- Current generic implementation remains legacy-shaped: `build_run_spec`
  hard-codes `mineru_three_view_v1` and
  `["hybrid_high", "pipeline_ocr", "hybrid_high"]`; unavailable CUDA makes the
  whole run `skipped`; production adapters call
  `original_hybrid`, `original_pipeline_ocr`, and `raster_hybrid`; visual
  bundle constants are still the legacy three names. The candidate correctly
  identifies this as remediation, not accepted implementation.
- The sealed old run is v1, globally skipped, and tied to portable identity
  `72095696C9C0E304E3F8D8CED9B387C21272203592567ACAEF1D984AB63CF292`.
  Its `skip.json` skips all six stages because of `mineru_cuda`. It must stay
  immutable and unpromotable.
- `MinerU/models/manifest.json` has 55 total rows: 40 `models/pipeline/**`
  rows and 15 `models/vlm/**` rows. CPU setup must filter the 40 pipeline rows
  exactly and must not require VLM assembly as a CPU prerequisite.
- The pipeline model YAML
  `models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml`
  is checked out as `text: auto`, has current filesystem size `2344759`, and
  current SHA-256
  `355B1D9364ED6130DF42C73DC2503BAA9628E3708DEEB8F964782165DCDF6245`; the
  manifest declares size `2244564` and SHA-256
  `87b5f3d7f2b2fe553627d77b37f496608ca150ebd0ef62d362591edca47b5538`.
  The candidate correctly treats this as a pre-run model-byte blocker.
- `reconstruction-upstream-v1` preservation is architecturally valid if and
  only if package validation dispatches strict internal validation by run
  schema/profile. The external v1 manifest records stage chain and run
  identity, not a provider promise; therefore an additive RunSpec v2 can remain
  behind the same package boundary without silently changing accepted v1
  package semantics.

## Findings

### P0

None against the architecture candidate.

The current checkout still has P0 pre-run blockers, but the candidate already
names them and keeps them out of acceptance: no fresh CPU profile/lock exists,
current reconstruction code is still global-CUDA/legacy-three-view shaped, and
one CPU pipeline model file is not byte-stable against its manifest. These are
implementation prerequisites, not architecture defects.

### P1

None found.

The challenged areas are adequately specified at architecture level:

- `torch==2.8.0+cpu` and `torchvision==0.23.0+cpu` are available from the
  PyTorch CPU index for the current Python 3.12.14 probe environment.
- Formula/table CPU feasibility is not assumed as acceptance; it is correctly
  made a mandatory synthetic smoke and model-identity gate before source run.
- Original `txt`, original `ocr`, and raster `ocr` have enough independent
  controls when bound to explicit method, `ocr_enable`, input lineage, and page
  coverage.
- MinerU 3.4.4 output artifact expectations match the source path, with the
  necessary extra fail-closed wrapper check for layout PDFs.
- Preserving upstream v1 is valid under strict profile-dispatched validation
  and no relaxation of legacy v1 validators.

### P2

1. Optional VLM method recording should be made explicit in the view schema and
   tests.

   The candidate says `original_vlm` has method "not applicable" and invokes
   `vlm-engine` without `--method`, while MinerU's CLI default method is
   `auto`. That is acceptable because method is adapted only for pipeline and
   hybrid paths, but a future receipt reader could misread a default `auto`
   field as an evidence method. Require VLM view receipts to record
   `method: null`, `cli_method_argument: omitted`, and
   `effective_method_scope: not_applicable`, and require tests that no VLM
   default `auto` can satisfy or replace the three CPU evidence views.

2. Packet A should record wheel tag and platform tags, not only package
   versions.

   The live index probe supports the candidate's CPU pins, but implementation
   acceptance should capture the installed wheel filenames or direct URL
   identities and the Python/platform compatibility tags for `torch`,
   `torchvision`, and `onnxruntime`. This is a hardening note because the
   candidate already requires exact lock/distribution inventory and `pip
   check`; the extra tag evidence will make later Windows/Python drift easier
   to audit.

3. CPU smoke should define bounded success evidence for formula/table model
   loading.

   The candidate correctly keeps `--formula True --table True` and requires a
   synthetic pipeline/txt and pipeline/ocr smoke. Add to Packet A acceptance
   that the smoke receipt must report whether formula, table classification,
   wired/wireless table, OCR, and layout model components were actually loaded
   or not exercised by the synthetic page. If the synthetic page does not
   trigger those paths, model-load probes must cover them separately before the
   real source run.

## Blockers

No P0/P1 architecture blocker prevents accepting this specification as the
basis for implementation packets.

Execution remains blocked until the candidate's own P0 prerequisites are
implemented and independently reviewed:

- fresh repository-local CPU profile and complete CPU lock under `.tools`;
- provider-scoped capability receipt replacing the run-global CUDA gate;
- exact byte-stable 40-row pipeline model verification, including the current
  CRLF-expanded YAML remediation without changing manifest authority;
- RunSpec/view-set/view manifest implementation for the three mandatory CPU
  views and optional provider-level GPU skips;
- dynamic comparison, review queue, fidelity, materialization, resume and
  promotion compatibility tests;
- immutable old skip run remains unread-only historical evidence and is never
  resumed, converted, or promoted.

## Recommendation

Approve the MinerU CPU-first architecture for Packet A implementation, with
the P2 hardening notes above carried into Packet A/B tests.

Do not start the real Dissociation source run yet. The next allowed action is
bounded implementation of Packet A only: dependency/profile/capability/model
byte remediation under `.tools`, followed by independent implementation review.
Packet B and Packet C should remain separate so comparison/promotion
compatibility does not blur into runtime setup.
