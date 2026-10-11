# Architect receipt and specification - generic reconstruction control plane

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `3a-generic-reconstruction-control-plane-spec`
- Role: architect
- Requested model: `gpt-5.6-sol`
- Requested reasoning effort: `high`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform identity unverified
- Scoped override: none
- Scope: implementation-ready architecture for the minimum scenario-neutral control plane that reaches a reviewed `RECONSTRUCTED_EN` candidate by wrapping the existing MinerU three-view tools; no implementation, MinerU execution, source mutation/copy, generated candidate, canonical-state edit, acceptance, release, or Git action
- Result: specification complete and ready for independent architecture/process criticism, then a bounded engineering packet. The minimum slice keeps `ScenarioContract.v1` separate from a new `RunSpec.v1`, patches only the two proven components that block a third scenario, and stops before reconstruction acceptance or publication.
- Timestamp: `2026-09-14T03:17:00+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:12:00`
- Token use: unavailable

## Files checked or changed

Checked:

- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md` (active-goal section)
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_pdf_reconnaissance_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_generic_runner_gap_audit_20260914.md`
- `kb_creator/docs/reviews/KB_CREATOR_PIPELINE_AUTOMATION_REVIEW_20260913.md`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/scripts/scenario_contract.py`
- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- publication-boundary evidence in `kb_creator/scripts/build_viral_production.py`

Changed:

- added this immutable receipt/specification only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_generic_reconstruction_control_plane_spec_20260914.md`

No canonical plan/context/status, contract/schema, source, code, test, generated,
acceptance, release, or production file was changed by this assignment.

## Executive architecture decision

Build a small adapter-first control plane for target `reconstructed_en` only.
It owns run identity, safe paths, stage sequencing, subprocess capture, common
manifests, the review queue, and strict resume validation. It does not own
source-reconstruction semantics and does not replace the existing CLIs.

The fixed graph is:

```text
preflight (read-only)
  -> prepare_inputs
  -> mineru_three_view
  -> compare_views
  -> visual_merge_bundle + typed review_queue
  -> await external reviewed decisions
  -> fidelity_audit
  -> materialize_candidate
  -> stop at candidate_ready_for_reconstruction_qa
```

`candidate_ready_for_reconstruction_qa` is not accepted
`RECONSTRUCTED_EN`. Promotion/acceptance remains the following orchestrator and
user gate.

## 1. ScenarioContract.v1 versus RunSpec.v1

### Decision

Keep `ScenarioContract.v1` unchanged in this implementation slice and add a
separate `RunSpec.v1`.

`ScenarioContract.v1` remains durable, portable content authority for:

- scenario identity and languages;
- hash/byte/page/MediaBox/rotation source identity;
- physical page domain and required numbered-handout count;
- gap-free page roles, traits, and reconstruction strategies;
- reconstruction review requirement.

`RunSpec.v1` is run-local operational state for:

- exact ScenarioContract bytes/hash used by the run;
- resolved runtime source locator plus a newly observed identity;
- target (`reconstructed_en` only in Wave 0) and fixed graph profile;
- run root and run-local reuse policy;
- DPI and deterministic stage options;
- Python, PowerShell, MinerU, pypdf, PyMuPDF, ReportLab, and Poppler identities;
- hashes of the wrapper scripts and control-plane implementation;
- later external decision-set and reviewed-allowlist identities at the stage
  boundary, not by mutating the original run identity.

Do not add run roots, shell fragments, executables, tool paths, timestamps,
decision paths, or cache locations to `ScenarioContract.v1`. They are neither
portable scenario facts nor publication policy.

### RunSpec.v1 exact envelope

Use a closed JSON object with these top-level keys:

```text
schema                  "kb_creator.run_spec.v1"
run_id                  safe user-selected identifier
target                  constant "reconstructed_en"
profile                 constant "mineru_three_view_v1"
contract                {path_hint, bytes, sha256, contract_revision}
source                  {path_hint, bytes, sha256, page_count,
                         media_box_points, rotation_degrees}
scope                   {ordered_pages}
options                 {raster_dpi, review_dpi,
                         mineru_profiles, source_box, cache_mode}
toolchain               ordered typed tool records
implementation          ordered file inventory and inventory_sha256
portable_identity_sha256
local                   {contract_path, source_path, run_root, mineru_root,
                         executable_paths}
```

`portable_identity_sha256` is the SHA-256 of canonical JSON for every field
except `local` and itself. Paths in `local` are allowed to be absolute but are
never portable authority or part of a cache key. The source is re-read and
re-hashed immediately before the first external stage; the contract snapshot
is canonicalized with the existing `scenario_contract.py` implementation.

The run root is absent at `run` start. Once `run.json` exists, it is immutable.
`resume` supplies a separate decision-set input; it never rewrites `run.json`.

### Current v1 limitation and later migration

The existing v1 schema is sufficient only as reconstruction input for this
slice. It is not sufficient for the corrected publication chain because it:

- has no DOCX artifact or DOCX acceptance gate;
- makes PDF depend on `accepted_html`;
- fixes `policies.render.profile` to `viral_print`;
- does not require the ArtView bundle, accepted ArtView decision manifest, or
  every effective build/render config in production inventory.

The Wave-0 runner must ignore those downstream v1 fields and reject every
target after `reconstructed_en`. Before MASTER/publication orchestration, a
separately reviewed `ScenarioContract.v2` (or an equally explicit versioned
publication contract) is mandatory. Do not quietly reinterpret v1 to authorize
the new publication stages.

## 2. Source-page geometry policy

### Decision

Replace the preparer's US-Letter constant with a contract-bound, full-MediaBox
policy. `ScenarioContract.v1` can represent one uniform size and one uniform
rotation, so Wave 0 supports any positive uniform MediaBox dimensions and one
uniform rotation in `{0, 90, 180, 270}`. It fails before output for a mixed-size
or mixed-rotation source because v1 cannot describe that source faithfully.

For each selected physical page:

1. Read the full MediaBox coordinates and `/Rotate` from pypdf.
2. Require MediaBox width/height and rotation to equal the contract values.
3. Record the full MediaBox coordinates and CropBox coordinates in the prepare
   stage manifest. MediaBox width/height is authority; CropBox, TrimBox,
   BleedBox, and ArtBox are evidence only.
4. Render the full MediaBox, never the CropBox. If PyMuPDF defaults to CropBox,
   set the page's effective crop to its MediaBox in memory for the pixmap and
   restore it afterward. The source file is never written.
5. Normalize a non-zero MediaBox origin to `(0, 0)` in the raster output without
   stretching or clipping.
6. Apply source rotation exactly once. Raster pages have rotation `0` and
   displayed page dimensions of `[width, height]` for 0/180 degrees and
   `[height, width]` for 90/270 degrees.
7. At DPI `d`, require pixmap dimensions equal the transformed MediaBox bounds
   (`ceil(points * d / 72)` for an origin-zero axis) and record the observed
   dimensions.
8. Set each image-only PDF page to those exact displayed dimensions in points.
   The raster PDF must have no text layer.

For Dissociation this yields full pages `595 x 841` points at rotation `0`.
Its `595 x 770` CropBox is deliberately not used; using it would remove the
71-point running-header band. The vector path continues to preserve original
page dictionaries, but the new runner calls the preparer with `--raster-only`
and feeds the original hash-bound source directly to the two original views.

### Compatibility requirement

- Existing Letter/rotation-0 inputs continue to emit `612 x 792` raster pages,
  the same filenames, the same CLI arguments, the same manifest schema, and
  byte-deterministic outputs for identical inputs/options.
- Existing tests remain valid; new geometry tests extend them.
- Arbitrary mixed geometry is postponed to a contract version that can encode
  per-page boxes/rotations. Do not add an undocumented heuristic.

## 3. Stage graph and adapter mapping

### Stage 00 - preflight (no filesystem writes)

- Validate the contract through both the JSON Schema and
  `scenario_contract.py` profile `reconstruction_ready`.
- Re-observe source hash, bytes, page count, all page boxes, and rotations.
- Enforce the v1 uniform-geometry policy and exact physical page domain.
- Resolve required tools and collect versions/hashes.
- Validate that the requested run root is absent, its resolved parent is safe,
  and no writable path component is a symlink/junction/reparse point.
- Source and other read-only user inputs may be reparse-backed only when the
  exact file is readable and its full content/geometry identity matches; this
  is required for the accepted Yandex Disk source. Writable roots may not be
  reparse-backed.
- Print a closed JSON result only; exit without creating `run.json`.

### Stage 01 - prepare_inputs

Invoke the existing CLI after the bounded geometry patch:

```text
prepare_mineru_three_view_inputs.py
  --source <source>
  --output-dir <stage-output>/prepared
  --source-sha256 <contract sha>
  --pages 1-<page_count>
  --dpi <raster_dpi>
  --basename source
  --raster-only
```

Do not expose arbitrary page ordering through the new runner. The contract
mode is all source pages and the ordered domain is always contiguous.

### Stage 02 - mineru_three_view

Invoke `run_mineru_three_view.ps1` three times into three initially absent
output directories:

| View | Input | Profile |
|---|---|---|
| `original_hybrid` | exact source PDF | `hybrid_high` |
| `original_pipeline_ocr` | exact source PDF | `pipeline_ocr` |
| `raster_hybrid` | Stage-01 image-only PDF | `hybrid_high` |

Omit `StartPage`/`EndPage`; the contract covers the full document. Capture each
command, exit code, bounded stdout/stderr, redacted environment allowlist, and
MinerU/config identity. Re-hash the external source after the two source reads;
any change fails the stage.

### Stage 03 - compare_views

Invoke `compare_mineru_three_views.py` with the Stage-01 manifest and the three
Stage-02 roots. Require exit `0`, comparison status `pass`, exact page coverage,
one layout PDF per view, and a complete output inventory.

### Stage 04 - visual_merge_bundle and review_queue

Reuse `build_mineru_visual_merge_bundle.py`, but remove its new-scenario blocker
with one compatibility-preserving parameterization:

- accept an optional reviewed scenario-contract path in its Python API/CLI;
- when supplied, derive every page's `semantic_role` from the gap-free contract
  page roles and derive `expected_pages` from contract scope;
- when omitted, retain the current 124-page legacy role table and CLI behavior
  for parity only.

The new runner always supplies the contract. It also supplies Stage-02's
manifest as the hash-bound raw receipt, Stage-03 comparison/hash, source/hash,
and the resolved `pdftoppm`. The resulting layout renders, triptychs, contact
sheets, merge packets, and merge index remain run-local evidence.

The control plane then emits `review/review_queue.json` and
`review/decision_set.template.json` without making decisions. Exit `10` with
state `awaiting_review`.

### Stage 05 - fidelity_audit (resume only)

Validate the submitted decision set before invoking any existing CLI:

- decision set binds the exact review-queue hash, source hash, contract hash,
  and exact page-decision inventory;
- page decisions exactly cover the physical page domain;
- each decision uses `kb_creator.mineru_ai_page_decision.v1`;
- `unresolved` is empty and `review.visual_reviewed` is true for every page;
- the optional reviewed allowlist is explicitly inventoried and hash-bound.

Then invoke `audit_mineru_ai_merge_fidelity.py` with only the `pages/`
subdirectory, merge-packet root, optional allowlist, and an output report.
Require exit `0` and `passed: true`.

### Stage 06 - materialize_candidate

Invoke `materialize_mineru_ai_merge.py` with the Stage-04 bundle/raw roots,
the same exact `pages/` decisions root, and an initially absent candidate root.
Require `candidate_ready_for_reconstruction_qa`; inventory every output and
write the final StageManifest. A result of `candidate_needs_review` is a
fail-closed control-plane error because Stage 05 admitted only closed decisions.

The command exits `0` only for a structurally materialized, inventoried
candidate. It does not create an acceptance manifest.

## 4. Existing CLI preservation

The five routed reconstruction CLIs remain the behavioral authority:

| Existing CLI | Control-plane treatment | Allowed change in Wave 0 |
|---|---|---|
| `prepare_mineru_three_view_inputs.py` | subprocess adapter | replace Letter-only geometry with the exact policy above; keep arguments/output schema |
| `run_mineru_three_view.ps1` | subprocess adapter | none |
| `compare_mineru_three_views.py` | subprocess adapter | none |
| `audit_mineru_ai_merge_fidelity.py` | subprocess adapter | none |
| `materialize_mineru_ai_merge.py` | subprocess adapter | none |

Do not import their internal functions as the runner API and do not move their
logic into the new package. The subprocess boundary preserves current focused
tests and makes command/output parity observable.

`build_mineru_visual_merge_bundle.py` is an unavoidable sixth bridge because
the materializer requires its `merge_packets/merge_index.json`; it is currently
not generic due to hard-coded 124-page role ranges. Only its role/page-count
input is parameterized. Its rendering, packet, priority, resume, and inventory
logic is retained.

## 5. Common manifests and typed review queue

### StageManifest.v1

Every stage writes one closed `stage.json` only after outputs have been
verified. It has two sections so nondeterministic execution metadata cannot
pollute cache identity:

```text
schema                  "kb_creator.stage_manifest.v1"
reproducible:
  stage_id              ordinal + stable name
  stage_version
  state                 succeeded | awaiting_review | failed
  run_identity_sha256
  upstream              ordered [{stage_id, manifest_sha256}]
  inputs                ordered typed records with bytes/sha256
  options               closed stage-specific object
  adapter               {logical_name, script_sha256, argv_shape_version}
  tools                 ordered tool/version/hash records
  outputs               {root_hint, files[], inventory_sha256}
  evidence              run-relative paths/hashes
  cache_key
execution:
  started_at_utc
  completed_at_utc
  exit_code
  stdout_log
  stderr_log
  structured_diagnostics
reproducible_sha256
```

All reproducible paths use run-relative POSIX form. Absolute paths and
timestamps are excluded from `reproducible_sha256`. A stage with incomplete
outputs never receives `state: succeeded`.

### ReviewQueue.v1

Emit exactly one deterministic review item per physical source page because
the existing decision/materializer contract is per page. Do not create a
second incompatible decision domain for individual conflicts.

Top-level binding:

```text
schema, run_identity_sha256, contract_sha256, source_sha256,
comparison_sha256, visual_bundle_manifest_sha256,
required_decision_schema, items, queue_sha256
```

Each item is closed and contains:

```text
id                     page-001 style
source_page
contract_role
contract_traits
contract_strategies
merge_packet            {path, bytes, sha256}
visual_evidence          run-relative triptych/page/contact paths
issue_kinds
required_decision_file
state                    open
```

Allowed `issue_kinds` in v1:

```text
page_fidelity, reading_order, visual_preserve, ocr_region,
structured_statblock, form_like, semantic_conflict,
asset_ambiguity, geometry_box_difference, engine_diagnostic
```

`page_fidelity` is present on every page because reconstruction policy requires
review. The remaining kinds are derived only from contract traits/strategies,
observed MediaBox-versus-CropBox differences, comparison conflicts/unmatched
assets, and captured engine diagnostics. Priority scores order review; they
never close an item.

For Dissociation this necessarily flags the visual cover, two-column body
pages, the page-3 callout, the page-5 OCR/visual map asset, the page-6 statblock,
and the MediaBox/CropBox difference without embedding scenario-specific code.

### ReconstructionDecisionSet.v1

The reviewer submits a separate closed manifest containing:

```text
schema                  "kb_creator.reconstruction_decision_set.v1"
review_queue_sha256
contract_sha256
source_sha256
decisions               ordered [{source_page, path, bytes, sha256}]
reviewed_allowlist       null or {path, bytes, sha256}
submission_state        constant "submitted_for_validation"
```

Decision files live under `pages/`; the aggregate manifest lives beside that
directory so the existing audit's strict `*.json` scan sees only page files.
This aggregate binding is necessary: the current page-decision format binds
page/role/selected blocks but not the exact queue or packet set.

## 6. Run layout, resume, and cache identity

Minimum run layout:

```text
<run-root>/
  run.json
  stages/
    01-prepare-inputs/stage.json + outputs/
    02-mineru-three-view/stage.json + outputs/
    03-compare-views/stage.json + outputs/
    04-review-bundle/stage.json + outputs/
    05-fidelity-audit/stage.json + outputs/
    06-materialize-candidate/stage.json + outputs/
  review/
    review_queue.json
    decision_set.template.json
  candidate/             Stage-06 owned output
  local/                 bounded logs and nonportable diagnostics
  failures/              quarantined incomplete attempts
```

### Cache key

For each stage:

```text
SHA256(canonical_json({
  stage_id, stage_version, run_portable_identity,
  ordered_upstream_manifest_hashes,
  ordered_input_file_or_inventory_hashes,
  normalized_options,
  adapter_script_hash,
  control_plane_implementation_inventory_hash,
  effective_tool_versions_and_hashes,
  external_decision_or_allowlist_hashes
}))
```

### Minimum cache policy

Wave 0 supports only verified run-local reuse. It does not add a shared cache:
current comparison/materialization artifacts contain absolute local paths, so
cross-run reuse would claim portability that the existing outputs do not have.

On `resume`, a preceding stage is reused only when:

- `run.json` validates and its portable identity recomputes exactly;
- the stage manifest schema/hash and cache key recompute exactly;
- every upstream manifest hash matches;
- every declared output file exists with exact bytes/hash and no extras in the
  owned inventory;
- source, contract, implementation, tools, options, and external inputs match;
- no owned path is escaping or reparse-backed.

Any mismatch exits `24` and leaves the run untouched. The user must choose a
new empty run root; Wave 0 does not silently invalidate and overwrite a partial
graph. Failed subprocess output is quarantined and is never a predecessor.
Shared content-addressed cache, relocation, and automated downstream
invalidation are postponed until existing output schemas are path-portable.

### Exit codes

| Code | Meaning |
|---:|---|
| `0` | requested candidate target materialized and inventoried |
| `10` | review/decision closure required |
| `20` | invalid contract, RunSpec, queue, or decision set |
| `21` | required tool unavailable or incompatible |
| `22` | source/contract/upstream identity mismatch |
| `23` | comparison, fidelity, or output gate failed |
| `24` | unsafe resume or cache/provenance mismatch |
| `25` | occupied or escaping writable target |
| `30` | MinerU/renderer subprocess failure |
| `40` | unexpected internal failure |

## 7. Exact bounded engineering ownership

The future engineer owns only these files in the first implementation packet.

### Add

- `kb_creator/__main__.py` - `doctor`, `preflight`, `run`, and `resume`; only
  target `reconstructed_en` is accepted.
- `kb_creator/pipeline/__init__.py`
- `kb_creator/pipeline/identity.py` - canonical JSON, SHA-256 records,
  deterministic inventory, component-wise path containment/reparse checks, and
  atomic directory promotion.
- `kb_creator/pipeline/process.py` - bounded subprocess capture, environment
  allowlist/redaction, typed exit mapping.
- `kb_creator/pipeline/manifests.py` - stdlib closed validators/builders for the
  four new schemas and reproducible-hash calculation.
- `kb_creator/pipeline/reconstruction.py` - fixed graph and the six adapters
  above; no scenario facts.
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/stage_manifest.v1.schema.json`
- `kb_creator/contracts/review_queue.v1.schema.json`
- `kb_creator/contracts/reconstruction_decision_set.v1.schema.json`
- `kb_creator/tests/test_pipeline_identity.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`

### Modify narrowly

- `kb_creator/scripts/prepare_mineru_three_view_inputs.py` - geometry policy
  only; preserve CLI/output contract for Letter sources.
- `kb_creator/tests/test_mineru_three_view_tools.py` - non-Letter,
  asymmetric-CropBox, rotation, mixed-geometry rejection, and Letter parity.
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py` - optional
  contract-derived role/page map; retain legacy default.
- `kb_creator/tests/test_mineru_visual_merge_bundle.py` - six-page generic role
  mapping and legacy parity.

### Explicitly not owned in this packet

- `scenario_contract.v1.schema.json` and existing scenario contracts;
- `scenario_contract.py` behavior;
- the other four routed reconstruction CLIs/tests;
- `finalize_mineru_reconstruction.py` and its Viral handout constants;
- any MASTER_EN, MASTER_RU, ArtView, HTML, DOCX, PDF, production, acceptance,
  release, status, plan, or context implementation;
- legacy test consolidation or historical receipt cleanup.

## 8. Corrected publication boundary and existing conflicts

The authoritative future graph is:

```text
accepted MASTER_RU + accepted ArtView bundle/decision manifest
  + all effective build/render configs
    -> HTML
    -> DOCX
    -> PDF generated only from that accepted DOCX
    -> production package containing ArtView/decisions/configs
```

Direct HTML-to-PDF is forbidden for Dissociation and the new generic pipeline.
Wave 0 neither implements nor exposes any publication target, which prevents
the old route from leaking into this slice.

Existing assumptions that require a later, separately scoped remediation:

- `scenario_contract.v1.schema.json` omits DOCX and declares PDF's upstream
  gate as `accepted_html`.
- The same schema fixes render profile `viral_print` and does not require the
  ArtView bundle/accepted decision/effective-config inventory.
- `KB_CREATOR_PIPELINE_AUTOMATION_REVIEW_20260913.md` describes the older
  `HTML -> PDF` target graph and Wave 3 without a DOCX gate.
- `build_viral_production.py::render_only` calls
  `translator.build_production_pdf(...)` from HTML before building DOCX, and
  its CLI help still says `Rebuild HTML/PDF/DOCX`.
- `build_viral_production.py::browser_command` contains Chromium
  `--print-to-pdf` from an HTML URI. The later `finalize_word_pdf` route does
  validate a Word-exported PDF against DOCX, but coexistence of both routes is
  not an acceptable generic publication contract.

These are evidence for the later publication-contract wave, not authority to
modify publication code in the reconstruction packet.

## 9. Assumptions and risks

Assumptions:

- The reviewed Dissociation runtime contract will use physical pages `1-6`,
  MediaBox `[595, 841]`, rotation `0`, and the page roles from the PDF
  reconnaissance receipt.
- An existing MinerU installation can be discovered; the control plane does
  not install or bundle it.
- Human decisions continue to use the existing per-page decision schema.
- The run is local evidence. Portability begins only at a later accepted
  reconstruction/package boundary.

Risks and controls:

- A thin shell wrapper alone would preserve manual state gaps: common manifests
  and queue/decision binding are therefore mandatory.
- PyMuPDF's CropBox rendering default can silently clip Dissociation: the
  asymmetric-CropBox test is a release-blocking test for this slice.
- `build_mineru_visual_merge_bundle.py` currently carries Viral role ranges:
  new runs must require contract-derived roles; legacy fallback is parity only.
- Existing output JSON embeds absolute paths: shared cache is deliberately
  postponed.
- Current fidelity audit is lexical, not visual: every page still requires a
  reviewed queue item and materialization cannot imply acceptance.
- Tool configuration can drift: hash MinerU executable, initialization script,
  resolved config, wrapper, and reported version in Stage 02.
- The Yandex source is a reparse point: allow it only as an exact hash-bound
  read-only input; never use a reparse-backed writable run root.

## 10. Explicitly rejected overengineering

- No scenario-named executable or Dissociation branch in Python/PowerShell.
- No monolithic rewrite of the five proven CLIs.
- No full pipeline package, plugin system, database, event bus, scheduler, or
  worker pool.
- No shared/global cache until existing outputs are path-portable.
- No arbitrary DAG configuration; the reconstruction graph is fixed.
- No automatic AI merge decision, review auto-approval, or inferred user
  acceptance.
- No ScenarioContract.v2 in Wave 0 merely to carry runtime paths.
- No mixed-per-page geometry heuristic that v1 cannot declare.
- No MASTER/publication/finalizer generalization in the reconstruction packet.
- No direct HTML-to-PDF adapter, even temporarily.
- No cleanup/migration of historical scenarios, tests, plans, or receipts.

## 11. Acceptance checklist for independent criticism and implementation

Architecture/process review is ready to pass when the critic confirms:

- [ ] ScenarioContract/RunSpec authority is separated and no runtime path or
      executable leaks into portable scenario authority.
- [ ] Wave 0 cannot invoke a target after `reconstructed_en`.
- [ ] MediaBox, CropBox, rotation, and mixed-geometry behavior are unambiguous.
- [ ] The sixth merge-bundle dependency is acknowledged and its hard-coded
      roles cannot affect a contract-driven run.
- [ ] Queue and decision-set hashes prevent stale decisions from being reused.
- [ ] A passing stage cannot exist without complete output inventory and exact
      upstream/tool/implementation identity.
- [ ] Resume mismatches fail without overwriting any run output.
- [ ] Candidate materialization is not represented as reconstruction
      acceptance.
- [ ] The future publication chain is HTML -> DOCX -> PDF, with mandatory
      ArtView/decision/config package evidence and no direct HTML -> PDF route.

Bounded implementation is complete when:

- [ ] `doctor` and read-only `preflight` return closed machine JSON and
      `preflight` creates no files.
- [ ] A synthetic non-Letter PDF with a smaller asymmetric CropBox produces a
      full-MediaBox, text-free raster without clipping or stretching.
- [ ] Letter/rotation-0 behavior, names, schemas, and deterministic parity stay
      green.
- [ ] Uniform rotated pages are normalized exactly once; mixed size/rotation
      fails before output under v1.
- [ ] A synthetic two-page non-scenario contract runs through prepare,
      synthetic MinerU trees, compare, bundle, queue, decision validation,
      audit, and materialize.
- [ ] First run stops with exit `10`; a fully hash-bound closed decision set
      resumes to an inventoried candidate with exit `0`.
- [ ] Changed source, contract, queue, decision, allowlist, tool, script,
      upstream manifest, missing output, extra output, path escape, or reparse
      writable root fails with the specified nonzero class.
- [ ] Existing focused suites for all five CLIs remain green, and visual-bundle
      legacy parity remains green.
- [ ] No new file contains `Dissociation`, Viral/Innsmouth page counts/ranges,
      or a direct HTML-to-PDF route.
- [ ] No acceptance or production manifest is emitted by the Wave-0 runner.

## Blockers and next action

- Architecture blocker: none after independent criticism.
- Implementation environment blocker: the engineer audit could not run pytest
  because the inspected Python environments lacked pytest/PDF test
  dependencies. Select an approved environment with those dependencies before
  implementation verification; do not silently install into the repository.
- Publication blocker intentionally postponed: v1 cannot express DOCX and the
  corrected ArtView/config-bound publication graph.
- Next action: obtain an independent `gpt-5.5` architecture/process review of
  this receipt. If accepted, dispatch one bounded engineer with ownership only
  of the files in Section 7 and require the checklist evidence above.
