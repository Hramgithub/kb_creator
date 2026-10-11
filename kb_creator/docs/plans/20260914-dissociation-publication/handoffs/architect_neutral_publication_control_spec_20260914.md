# Architect receipt and specification - neutral publication control plane

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4P-neutral-publication-control-spec`
- Role: architect
- Requested model: `gpt-5.6-sol`
- Requested reasoning effort: `high`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform
  identity unverified
- Scoped override: none for this architecture task. The goal's user-scoped
  `gpt-5.6-sol/high` override applies to engineering only and does not transfer
  orchestration ownership.
- Scope: implementation-ready architecture for the minimum scenario-neutral
  publication control plane from an accepted reconstruction through an
  identity-bound production-package candidate. This receipt specifies only;
  it does not implement, execute, accept, release, install tools, mutate a
  source, or change canonical goal state.
- Result: specification complete for independent architecture/process review
  and then phased engineering. It preserves the Wave 0 reconstruction boundary,
  uses additive publication contracts, wraps rather than replaces proven
  renderers, makes `DOCX` the sole PDF authority, and keeps user acceptance
  external and explicit.
- Timestamp: `2026-09-14T05:03:11+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:18:00`
- Token use: unavailable

## Files checked or changed

Checked:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md` (active Dissociation goal and pipeline review)
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_generic_reconstruction_control_plane_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/explorer_publication_reuse_map_20260914.md`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/contracts/scenario_reconstruction_contract.v1.schema.json`
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/stage_manifest.v1.schema.json`
- `kb_creator/pipeline/identity.py`
- `kb_creator/pipeline/manifests.py`
- `kb_creator/pipeline/process.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/__main__.py`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/scripts/prepare_translation_batches.py`
- `kb_creator/scripts/merge_translation_batches.py`
- `kb_creator/scripts/split_translation_batch_to_units.py`
- `kb_creator/scripts/merge_micro_translation_batch.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/production_docx.py`
- `kb_creator/scripts/build_viral_production.py`
- `kb_creator/scripts/build_innsmouth_html_from_master_ru.py`
- `kb_creator/scripts/build_innsmouth_pdf_from_accepted_html.py`
- `translator/translator.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_scenario_artview.py`
- `kb_creator/tests/test_production_docx.py`
- `kb_creator/tests/test_build_viral_production.py`
- `kb_creator/tests/test_build_innsmouth_html_from_master_ru.py`
- `kb_creator/tests/test_build_innsmouth_pdf_from_accepted_html.py`
- repository-local tool inventory under `.tools/`

Changed:

- added this immutable receipt/specification only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_neutral_publication_control_spec_20260914.md`

No canonical plan, context, status, source, contract, schema, code, test,
generated artifact, production artifact, acceptance, release, `.codex`, or Git
state was changed by this assignment.

## Verification/evidence

- The explorer reuse map was present and read in full before this specification
  was written.
- Current code confirms that `translator/translator.py::build_production_html`
  is a reusable HTML renderer but its gates are mutable configuration Booleans.
- Current code confirms that `production_docx.py::build_docx` already preserves
  HTML structure, images, tables, callouts, links, and bookmarks, while its A4
  styling and Viral metadata are currently implicit defaults.
- Current code confirms there is no generic automatic DOCX-to-PDF adapter.
- Current Viral and Innsmouth automatic PDF routes consume HTML/browser input;
  exact containment targets are listed in Section 7.
- Current ArtView decision validation is hash-bound, while its v2 build checks
  and production application still contain Viral-specific identities/counts.
- Repository-local Poppler is present under `.tools/poppler`; the existing
  system Word COM capability is an assignment-provided fact that must be
  re-probed and identity-bound by implementation preflight.
- The completed receipt was checked for required governance metadata, corrected
  chain language, ArtView/config requirements, P0/P1 invariants, section
  presence, and target-path identity. No implementation or runtime test was
  performed because this assignment is specification-only.

## Executive decision

Add a publication control plane beside, not inside, Wave 0 reconstruction. Its
only entry authority is an accepted `RECONSTRUCTED_EN` package and its matching
acceptance receipt. Its authoritative chain is:

```text
accepted RECONSTRUCTED_EN
  -> MASTER_EN candidate + QA
  -> explicit user acceptance of MASTER_EN
  -> MASTER_RU translation packets
  -> reviewed translation submission
  -> MASTER_RU candidate + QA
  -> explicit user acceptance of MASTER_RU
  -> ArtView review bundle
  -> accepted ArtView decisions
  -> ArtView application + effective-config seal
  -> explicit user acceptance of ArtView
  -> HTML candidate + structural/visual QA
  -> explicit user acceptance of HTML
  -> DOCX candidate + OOXML/render QA
  -> explicit user acceptance of DOCX
  -> PDF generated from that exact accepted DOCX only
  -> complete PDF render/visual QA
  -> explicit user acceptance of PDF
  -> production-package candidate
  -> offline verification
  -> stop; independent release review remains external
```

No stage may infer acceptance from a passing report, an `accepted` Boolean in a
render config, a file's presence, a prior scenario, or an agent conclusion.

## 1. Boundary from reconstruction

The existing `python -m kb_creator` reconstruction runner and these schemas
remain reconstruction-only:

- `scenario_reconstruction_contract.v1.schema.json`;
- `run_spec.v1.schema.json`;
- `stage_manifest.v1.schema.json`;
- `review_queue.v1.schema.json`;
- `reconstruction_decision_set.v1.schema.json`.

Do not extend their target or stage enums for publication. A publication run
must not invoke MinerU, reuse a reconstruction cache key, mutate a reconstruction
candidate, or treat `candidate_ready_for_reconstruction_qa` as acceptance.

The publication preflight consumes:

1. an immutable accepted reconstruction package inventory;
2. an explicit acceptance receipt bound to that exact inventory and
   `RECONSTRUCTED_EN` bytes;
3. a neutral publication contract and every referenced source config;
4. local runtime/tool bindings.

Changing any of these inputs requires a new publication run identity.

## 2. Additive data contracts

Do not modify or reuse `scenario_contract.v1.schema.json`. It omits DOCX,
requires PDF from `accepted_html`, and fixes `viral_print`; changing it would
mix a historical compatibility contract with the corrected chain.

### 2.1 `scenario_publication_contract.v1.schema.json`

Add `kb_creator/contracts/scenario_publication_contract.v1.schema.json` as the
portable, declarative publication authority. It is closed
(`additionalProperties: false`) and contains:

```text
schema = kb_creator.scenario_publication_contract.v1
contract_revision = 1
scenario {id, title_en, title_ru, language_source, language_target}
upstream {reconstruction_contract_sha256, required_artifact_roles}
artifact_names {master_en, master_ru, html, docx, pdf}
master_en {profile, config identity, required machine QA}
master_ru {profile, shared terminology identities, packet policy, required QA}
artview {profile identity, required bundle roles, decision schema/version}
html {adapter, render config identity, required QA}
docx {adapter, build config identity, required QA}
pdf {adapter = word_com_docx_export_v1, export policy, required QA}
package {required roles, stable names, verifier version}
tool_policy {repository_tool_root = .tools, allowed_system_tools}
```

The contract contains policies and identities, never local absolute paths,
acceptance states, scenario-derived counts copied from Viral, browser PDF
commands, or mutable gate Booleans. Cardinalities and page/asset roles must be
derived from the accepted upstream inventory and declarative scenario config.

Allowed system tools in v1 are exactly `powershell` and `microsoft_word_com`.
They are pre-existing system capabilities, not installed by this pipeline.
Every Python environment, Python package set, Poppler binary, or other tool
installed for the pipeline must resolve beneath repository `.tools/`.

### 2.2 `publication_run_spec.v1.schema.json`

Add `kb_creator/contracts/publication_run_spec.v1.schema.json`. It follows the
portable/local split already proven by reconstruction and contains:

- `run_id`, `target = production_candidate`, `profile`;
- publication contract identity;
- accepted reconstruction inventory and acceptance-receipt identities;
- ordered stage graph;
- identities of all source configs and the sealed effective config;
- implementation inventory;
- tool semantic identities;
- `portable_identity_sha256`;
- a `local` section containing checkout, run root, upstream package, acceptance
  root, `.tools` root, executable paths, and Word COM path.

`portable_identity_sha256` excludes only the `local` object. It includes the
semantic Word version, export policy, font inventory identity, configuration
inventory, adapters, and code inventory. Local binding validation is still
mandatory before every stage.

### 2.3 `publication_stage_manifest.v1.schema.json`

Add `kb_creator/contracts/publication_stage_manifest.v1.schema.json`; do not
broaden the MinerU stage schema. Mirror the current sealed
`reproducible`/`execution` shape, with this exact stage-name enum:

```text
master_en_candidate
master_ru_packets
master_ru_candidate
artview_bundle
artview_apply
html_candidate
docx_candidate
pdf_candidate
production_package
offline_verify
```

Every successful manifest records:

- run portable identity;
- exact upstream manifest seals;
- every input and acceptance/decision file identity;
- adapter logical name, version, and script identity;
- effective config identity;
- tool identities and implementation inventory identity;
- deterministic output inventory and evidence inventory;
- cache key;
- non-reproducible timestamps/process diagnostics separately.

Only a fully successful, atomically published stage receives a `succeeded`
manifest. Waiting, blocked, skipped, partial, or failed work is not cacheable.

### 2.4 `artifact_acceptance.v1.schema.json`

Add `kb_creator/contracts/artifact_acceptance.v1.schema.json` for
`reconstructed_en`, `master_en`, `master_ru`, `artview`, `html`, `docx`, and
`pdf`. Each receipt is closed and sealed, and binds:

- scenario id and artifact kind;
- candidate artifact/inventory identity;
- producer stage-manifest identity;
- all required QA and visual-review evidence identities;
- explicit decision `accepted`;
- decision timestamp and a non-empty user decision reference;
- recorder role; and
- receipt SHA-256.

The publication runner validates receipts but never creates them during
`run` or `resume`. A separate `publication record-acceptance` command may write
one only when the main orchestrator has a current explicit user instruction.
It is not called by the stage engine, cannot accept a failed/incomplete review,
and cannot overwrite a receipt.

ArtView also requires its native accepted decision document. The ArtView
acceptance receipt binds that document, its candidate manifest, and the bundle
inventory; it does not replace row-level decisions.

### 2.5 Translation and ArtView decision documents

Add only the missing portable envelopes:

- `master_ru_submission.v1.schema.json`: ordered unit ids, source-unit hashes,
  Russian payload hashes, batch identities, reviewer closure, and aggregate
  seal. It binds the accepted MASTER_EN receipt and the exact packet manifest.
- `scenario_artview_profile.v3.schema.json` and
  `scenario_artview_decisions.v3.schema.json`: scenario-neutral input bindings,
  derived expected cardinalities, row decisions, presentation decisions, and
  full reviewed closure. Existing v2 data remains a Viral compatibility path.

Do not create a schema for each individual QA report. QA reports are typed
evidence referenced by the stage manifest; only cross-stage authority receives
a separate schema.

### 2.6 Effective configuration

Preflight resolves the contract and all referenced configs into one sealed
`effective_publication_config.json`. It includes:

- normalized effective values;
- source config inventory and precedence;
- ArtView profile;
- HTML renderer config;
- DOCX profile and document metadata;
- Word PDF export policy;
- HTML/DOCX/PDF QA policy;
- package inventory policy;
- requested fonts and resolved font-file identities;
- a `config_inventory_sha256` and document seal.

Every derived adapter config is also inventoried. The final package must contain
the source configs, sealed effective config, and all derived adapter configs;
there is no hidden runtime-only configuration.

### 2.7 `production_package_manifest.v1.schema.json`

Add a closed, self-sealed package manifest containing:

- scenario and package state `candidate_for_release_review`;
- the publication run identity;
- artifact-role-to-path mapping;
- exact inventory of every regular package file except the manifest itself;
- all stage-manifest and acceptance-receipt identities;
- full configuration inventory;
- pipeline/schema/verifier snapshot identities;
- upstream reconstruction/source identities without copying the immutable
  source PDF;
- explicit `release_state = not_reviewed`.

The manifest must not embed or reserve a mutable release receipt. The later
governance release receipt binds this frozen package manifest from outside the
candidate. Mutating the package after that review would invalidate the review.

## 3. Fixed stage graph and gates

### Stage 00 - publication preflight (read-only)

Validate schemas, seals, safe paths, upstream acceptance, config closure,
required artifact roles, tool containment/capability, Word COM availability,
font resolution, and the complete prospective stage graph. Reject all errors
before creating the run root. `preflight` never writes a diagnostic file.

P0 rejection cases include:

- any absent, stale, unaccepted, or mismatched reconstruction authority;
- any absolute/escaping/reparse path in portable input;
- an existing run root;
- any installed pipeline tool outside `.tools/`;
- a PDF adapter other than `word_com_docx_export_v1`;
- any PDF config key or command containing `source_html`, `engine_command`,
  `print-to-pdf`, browser/Chromium/Edge PDF generation, or an HTML input role;
- a missing mandatory ArtView/config/package role.

### Stage 10 - `master_en_candidate`

Inputs are the accepted reconstruction package/receipt, publication contract,
and MASTER_EN config. The adapter produces an immutable candidate directory,
provenance, asset manifest, source-disposition evidence, machine QA, and stage
manifest. It then stops with `awaiting_master_en_acceptance` (exit `10`).

The generic path must derive topology, counts, exclusions, anchors, assets, and
required visual units from configuration/upstream evidence. The hard-coded
Viral constants in `build_scenario_master_en.py` (`N`, `viral` anchor regex,
124/122 pages, excluded pages 123-124, fixed QA counts) are unreachable from a
v3 neutral contract.

### Stage 20 - `master_ru_packets`

Requires the exact accepted MASTER_EN receipt. It wraps the existing unit
split/batch primitives and emits source-hash-bound translation packets and a
packet manifest. It stops with `awaiting_master_ru_submission` (exit `10`).

### Stage 21 - `master_ru_candidate`

Validates the submitted translations against the packet manifest, assembles in
declared order, and enforces Markdown structure, anchors/targets, images,
numeric/dice expressions, and shared CoC terminology. It emits provenance,
QA, and a stage manifest, then stops with
`awaiting_master_ru_acceptance` (exit `10`). No manual edit to generated
`MASTER_RU.md` is an accepted input; corrections change a translation unit or
config and rebuild.

### Stage 30 - `artview_bundle`

Requires accepted MASTER_RU and builds the complete ArtView review bundle from
the source/reconstruction asset graph. It emits candidate manifest, review HTML,
all candidate/context binaries, decision template, bundle inventory, and stage
manifest, then stops with `awaiting_artview_decisions` (exit `10`).

`scenario_artview.py::build` must derive row, region/full-page, production-state,
and excluded-page expectations from the profile/manifests. Viral-specific
asset ids, the 94/84/10 counts, and pages 123-124 remain only in the v2 legacy
profile branch.

### Stage 31 - `artview_apply`

Requires a v3 accepted decision document and explicit ArtView acceptance
receipt bound to Stage 30. It reuses decision validation semantics, copies only
selected binaries to a stage-local asset tree, produces the exact reader
projection consumed by HTML, writes `ARTVIEW_APPLIED.json`, and seals the
effective visual config. It does not edit either master.

### Stage 40 - `html_candidate`

Requires accepted MASTER_RU, accepted ArtView decisions/receipt, Stage 31, and
the exact effective config. The adapter invokes the existing HTML renderer:

```text
<repo .tools publication python>
  translator/translator.py
  build-production-html
  --config <stage-local-derived-config.json>
  --force
```

The adapter, not the legacy renderer, owns authority checks. Only after those
checks pass does it write a stage-local compatibility config. Any legacy gate
Booleans in that file are derived shims from validated receipts, not external
authority. The HTML renderer reads the Stage 31 projection and writes only to
the isolated stage directory. Capture its report, verify all local asset refs,
run semantic/accessibility/link checks, inventory outputs, and publish
atomically. Stop with `awaiting_html_acceptance` (exit `10`).

Do not call or expose `translator.build_production_pdf` or the
`build-production-pdf` subcommand from the neutral control plane.

### Stage 50 - `docx_candidate`

Requires the exact accepted HTML receipt and Stage 40 manifest. Call the
parameterized `production_docx.py::build_docx` with explicit metadata/layout
config. Verify the OOXML archive, relationships, embedded image identities,
headings/bookmarks, TOC/internal links, tables, callouts, page setup, and core
properties against HTML-derived expectations.

Use Word COM to create a stage-local DOCX QA preview PDF, then render every
preview page to PNG through repository `.tools/poppler`. The preview is QA
evidence only and is generated from DOCX, so it does not violate the PDF
authority rule. Stop with `awaiting_docx_acceptance` (exit `10`).

### Stage 60 - `pdf_candidate`

Requires the exact accepted DOCX receipt and Stage 50 manifest. The only input
document role is `accepted_docx`. Invoke a generic PowerShell adapter using a
fresh hidden Word instance:

```text
Documents.Open(ReadOnly = true, AddToRecentFiles = false)
ExportAsFixedFormat(
  ExportFormat = 17,                 # wdExportFormatPDF
  OptimizeFor = 0,                   # wdExportOptimizeForPrint
  Range = 0,                         # wdExportAllDocument
  Item = 0,                          # wdExportDocumentContent
  IncludeDocProps = true,
  CreateBookmarks = 1,               # heading bookmarks
  DocStructureTags = true,
  BitmapMissingFonts = true,
  UseISO19005_1 = false
)
Close(false); Quit()
```

Output is first written beside the eventual target under a unique stage temp
name. The adapter waits for a stable non-empty file, opens it with `pypdf`, runs
machine QA, and atomically renames only on success. `finally` must close the
document/application and release COM objects. It never opens HTML and never
accepts an arbitrary command template.

Render every final PDF page to PNG with repository-local Poppler. Emit page
dimensions, page count, text/occupancy checks, blank/near-blank/orphan signals,
outline/link checks, render inventory, and a complete per-page review index.
PDF acceptance must bind the PDF, machine report, full PNG inventory, and a
closed human visual-review record. Stop with `awaiting_pdf_acceptance` (exit
`10`).

### Stage 70 - `production_package`

Requires accepted receipts for MASTER_EN, MASTER_RU, ArtView, HTML, DOCX, and
PDF. Assemble into a new absent stage directory, verify the complete package,
then atomically publish a run-local immutable package candidate. It does not
promote to a stable user-facing directory and does not claim release.

Minimum package topology:

```text
MASTER_EN.md
MASTER_RU.md
<stable-scenario-name>_RU.html
<stable-scenario-name>_RU.docx
<stable-scenario-name>_RU.pdf
assets/
artview/
  candidate_manifest.json
  artview.html
  ARTVIEW_DECISIONS.accepted.json
  ARTVIEW_APPLIED.json
  ...all bundle binaries and inventory...
configs/
  scenario_publication_contract.json
  effective_publication_config.json
  config_inventory.json
  source/
  derived/
acceptance/
evidence/stages/
evidence/qa/html/
evidence/qa/docx/
evidence/qa/pdf/
pipeline/code/
pipeline/schemas/
pipeline/verify_production_package.py
README.md
PRODUCTION_MANIFEST.json
```

The accepted reconstruction remains an immutable upstream package; include its
acceptance and inventory evidence, not a duplicate of the external source PDF.

### Stage 71 - `offline_verify`

Run the copied verifier against the staged package before publication. The
verifier is read-only by default, Python-standard-library-only, and requires no
network, repository import, Word, Poppler, or JSON Schema package. It:

- validates the self-sealed manifest shape/version;
- rejects reparse points, path escapes, duplicates, absent, extra, or changed
  regular files;
- hashes every inventoried file;
- validates stage and acceptance seals with the copied schemas' required
  closed-field checks implemented in the verifier;
- walks lineage from accepted reconstruction through accepted DOCX to PDF;
- proves the PDF manifest's sole document input is the accepted DOCX and that
  its adapter is `word_com_docx_export_v1`;
- proves ArtView bundle/decisions/application and every effective config are
  present;
- reports `candidate_for_release_review`, never `accepted` or `released`.

The verifier prints deterministic JSON to stdout and writes nothing unless an
explicit report path beneath a run-local evidence directory is supplied.

## 4. Identity, resume, and cache rules

### Run layout

```text
<run-root>/
  run.json
  effective_publication_config.json
  inputs/                 # identity records or authorized snapshots
  outputs/<stage-id>/
  evidence/stages/<stage-id>.manifest.json
  evidence/reviews/
  quarantine/
  candidate_package/
```

The run root must be absent for `run`. Existing roots are accepted only by the
explicit `resume` operation after full identity revalidation.

### Cache key

For each stage:

```text
SHA256(canonical JSON of {
  stage_name, stage_version,
  publication_run_portable_identity_sha256,
  ordered upstream manifest seals,
  ordered input/acceptance/decision identities,
  effective_config_sha256,
  normalized options,
  adapter logical name/version/script SHA,
  tool semantic identities,
  implementation_inventory_sha256
})
```

Outputs and execution timestamps are not cache-key inputs; outputs are verified
before reuse through the stage manifest's full inventory.

### Resume rules

Before each resume or cache reuse, revalidate:

- run seal and local bindings;
- contract, upstream, acceptance, decision, and config bytes;
- tool versions/paths and `.tools` containment;
- Word executable/version and resolved font inventory for DOCX/PDF stages;
- implementation inventory;
- every upstream stage seal and output inventory;
- that the supplied external document is exactly the one expected by the next
  gate.

A mismatch exits `24`, performs no canonical output write, and requires a new
run. A stage failure moves only that invocation's private temp directory to
run-local quarantine and never creates a successful manifest. No shared cache,
cross-run copying, fallback to a previous scenario, or `--force` overwrite is
allowed in v1.

Word-generated PDF bytes may vary across Word/OS/font builds. V1 therefore
claims exact reproducibility only for a bound render environment; it records
the produced bytes as evidence and invalidates reuse on environment drift. It
does not claim platform-independent PDF byte determinism.

## 5. Adapter changes and reuse

### MASTER_EN

Keep `build_scenario_master_en.py` as the materializer, but add a neutral v3
config branch. Extract/derive all scenario counts and page scopes; do not relax
the frozen v1/v2 validators. Reuse its safe-path, inventory, atomic staging,
typed-event, provenance, and conservation machinery. The verifier must receive
the same v3 config and independently recompute the relevant invariants.

### MASTER_RU

Add `kb_creator/scripts/scenario_master_ru.py` with
`prepare`, `validate-submission`, and `assemble`. Wrap, without rewriting, the
algorithms in:

- `prepare_translation_batches.py::batch_units` and
  `expand_units_for_translation`;
- `merge_translation_batches.py::validate_batch`;
- existing unit split/micro-merge CLIs where needed.

The new wrapper owns accepted MASTER_EN binding, ordered assembly, aggregate
submission seal, Markdown/mechanics parity, terminology evidence, atomic
candidate materialization, and stage-readable JSON output.

### ArtView

Preserve v2 behavior for Viral. Add a v3 profile branch to
`scenario_artview.py::build`, `decision_bindings`, and `validate_decisions`.
Derive all identities/counts/roles from manifests. Extract generic application
logic now embedded in
`build_viral_production.py::materialize_artview_decisions` into an additive
scenario-neutral function/module; keep the legacy caller as a compatibility
wrapper rather than making the generic runner import Viral code.

### HTML

Do not fork the renderer. The adapter calls
`translator/translator.py::build_production_html` through its existing CLI and
validates its result/report. `translator` remains legacy implementation
evidence, so the generic stage owns all authority, containment, identity, and
manifest behavior and snapshots the exact renderer file used.

### DOCX

Modify `production_docx.py` minimally:

- `configure_document(doc, profile=None)` accepts page size, margins, font
  families/sizes, paragraph spacing, heading styles, and footer policy;
- `build_docx(html_path, output_path, *, config=None)` accepts explicit
  document metadata and layout profile;
- CLI adds optional `--config`;
- the current no-config call preserves byte/semantic behavior and current
  Viral defaults, including existing callers/tests;
- the neutral runner always supplies explicit config and never uses the Viral
  default metadata at lines 949-951;
- `patch_existing_docx` remains a legacy/manual compatibility operation and is
  not a publication-stage mutation path.

### DOCX -> PDF

Add `kb_creator/scripts/export_docx_to_pdf.ps1`. It has typed parameters for
DOCX input, PDF output, evidence output, timeout, and fixed export policy. It
rejects non-`.docx` input, existing output, a target outside the assigned stage,
and every direct-HTML/browser parameter. It records the input SHA, Word path,
Word version, fixed export arguments, output SHA/bytes, and cleanup result.

Microsoft Word COM and PowerShell are explicitly allowed existing system tools;
the pipeline installs neither. All newly installed Python dependencies and
Poppler/runtime tools live below `.tools/`.

## 6. User acceptance boundaries

The runner always stops before these gates:

| Gate | Required user-visible evidence | Downstream authority |
| --- | --- | --- |
| RECONSTRUCTED_EN | reconstruction package, fidelity/QA, inventory | publication preflight |
| MASTER_EN | candidate, provenance, semantic/assets QA, reader review | MASTER_RU packets |
| MASTER_RU | candidate, translation/mechanics/terminology QA | ArtView bundle |
| ArtView | complete bundle, row decisions, presentation preview | ArtView apply/HTML |
| HTML | served HTML, structural report, asset/link checks, visual review | DOCX |
| DOCX | editable DOCX, OOXML report, full rendered preview | PDF |
| PDF | final PDF, machine report, every page PNG, visual review record | package |

Passing tests, successful adapters, agent review, or a receipt written without
current explicit user authorization cannot cross a gate. A rejected candidate
is immutable evidence; corrections start a new downstream candidate/run
identity from the earliest changed input.

The independent critic release review occurs only after Stage 71 freezes a
package candidate. This architecture receipt is neither acceptance nor release.

## 7. Legacy direct-route containment

The following remain compatibility-only and are forbidden dependencies of the
new runner:

- `translator/translator.py::build_production_pdf` and its
  `build-production-pdf` CLI (HTML/browser -> PDF);
- `build_innsmouth_pdf_from_accepted_html.py`;
- `build_viral_production.py::browser_command`;
- the direct PDF calls in `build_viral_production.py::render_only` and `build`;
- historical configs containing `production_pdf.source_html` or browser
  `--print-to-pdf` commands.

Do not delete or silently change these routes in the initial implementation;
their current tests are compatibility evidence for existing packages. The new
publication adapter registry is a closed constant and has no arbitrary command
hook. A focused test must fail if any neutral publication module imports or
invokes the legacy PDF builders or if a publication PDF manifest/config names
HTML as an input.

Migration or deprecation of existing Viral/Innsmouth packages is a separate
goal. They do not become evidence that the new route is valid.

### Compatibility policy

- All new schemas, CLI commands, and pipeline modules are additive.
- Existing reconstruction CLI commands and schemas retain their exact meaning.
- `production_docx.build_docx(html, output)` without explicit config retains
  current behavior; only the new publication runner requires explicit config.
- Existing Viral/Innsmouth scripts and their direct-PDF tests remain unchanged
  and scenario-scoped until a separately reviewed migration.
- Historical packages are verified by their historical verifiers. They are not
  grandfathered into `production_package_manifest.v1` and cannot pass the new
  verifier without a real accepted DOCX-only lineage.
- No automatic fallback selects a legacy contract, renderer, count, asset role,
  filename, or acceptance when a neutral publication contract is incomplete.

## 8. Tool and runtime policy

Add tracked setup/verification wrappers only if dependencies are missing:

- `kb_creator/tools/publication/setup.ps1` defaults exclusively to
  `<repo>/.tools/publication`;
- `kb_creator/tools/publication/verify.ps1` is read-only and reports closed JSON;
- Python executable and site packages must resolve below
  `.tools/publication/.venv`;
- Poppler resolves below `.tools/poppler`;
- temporary dependency caches set by setup resolve below `.tools/publication`.

No script may install to user, system, product, source, or global environment.
Existing Word and PowerShell are discovered, never installed, and recorded as
the only system-tool exceptions. Browser tooling is not a PDF dependency.

## 9. Production package and offline verifier invariants

P0 package roles are exactly one each unless explicitly marked as a recursive
inventory:

- MASTER_EN and acceptance;
- MASTER_RU and acceptance;
- complete ArtView bundle inventory, candidate manifest, accepted decisions,
  application receipt, effective visual config, and ArtView acceptance;
- HTML, DOCX, PDF, their acceptance receipts, and their QA/stage evidence;
- every source/effective/derived config;
- every referenced reader asset;
- publication contract, run identity, used code/schema snapshots;
- package README, verifier, and self-sealed production manifest.

The verifier rejects unlisted files, including informal copies such as
`*_final`, `* - copy`, or alternate DOCX/PDF outputs. Stable artifact names come
from the contract. Versioning belongs to run ids, manifests, hashes, and Git,
not filenames.

Package verification proves identity and closure, not editorial correctness,
human visual quality, or release. Those are proven only by the bound review
evidence and independent release process.

## 10. Phased engineering ownership

### Packet A - P0 contracts and control-plane skeleton

Owner: future bounded engineer under the goal's recorded engineering override.

Add:

- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/publication_run_spec.v1.schema.json`
- `kb_creator/contracts/publication_stage_manifest.v1.schema.json`
- `kb_creator/contracts/artifact_acceptance.v1.schema.json`
- `kb_creator/contracts/master_ru_submission.v1.schema.json`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`

Modify narrowly:

- `kb_creator/__main__.py` to add the nested
  `publication preflight|run|resume|record-acceptance|verify-package` commands
  without changing existing reconstruction commands;
- `kb_creator/pipeline/__init__.py` only for publication exports if required.

Packet A uses injected synthetic adapters, proves the full fixed graph/gates,
and writes no Dissociation production artifact.

### Packet B - neutral content and ArtView adapters

Add:

- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`
- `kb_creator/contracts/scenario_artview_decisions.v3.schema.json`
- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/tests/test_scenario_artview_v3.py`

Modify narrowly:

- `kb_creator/scripts/build_scenario_master_en.py` (add v3 only);
- `kb_creator/scripts/verify_scenario_master_en.py` (independent v3 validation);
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/scripts/scenario_artview.py` (add v3 branch);
- `kb_creator/tests/test_scenario_artview.py` only for preserved v2 parity.

Do not change the four low-level translation batch scripts unless a focused
test proves a generic defect in the primitive itself.

### Packet C - corrected render and package chain

Add:

- `kb_creator/scripts/export_docx_to_pdf.ps1`
- `kb_creator/scripts/publication_render_qa.py`
- `kb_creator/scripts/verify_production_package.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/tests/test_publication_docx_adapter.py`
- `kb_creator/tests/test_publication_docx_to_pdf.py`
- `kb_creator/tests/test_publication_render_qa.py`
- `kb_creator/tests/test_production_package_verifier.py`
- `kb_creator/tools/publication/setup.ps1` and `verify.ps1` only if the
  repository-local environment needs provisioning.

Modify narrowly:

- `kb_creator/scripts/production_docx.py`;
- `kb_creator/tests/test_production_docx.py`.

Do not modify `translator/translator.py` in this packet; use its HTML CLI as an
adapter. Do not modify the legacy Viral/Innsmouth PDF routes.

### Postponed beyond these packets

- any Dissociation live publication run or generated candidate;
- content/translation/visual decisions and user acceptance;
- stable production-directory promotion;
- Viral/Innsmouth migration or removal of legacy direct PDF routes;
- cross-platform DOCX rendering or LibreOffice support;
- shared/distributed cache, workflow server, database, web dashboard, or job
  scheduler;
- publication formats other than HTML, DOCX, and PDF;
- Git commit/push and release review.

## 11. P0 and P1 invariants

### P0 - safety and authority; no live run with any failure

- [ ] Publication preflight is demonstrably read-only and rejects all invalid
      inputs before run-root creation.
- [ ] Reconstruction candidates cannot enter publication without an exact
      accepted reconstruction receipt.
- [ ] Every downstream stage requires the exact acceptance/decision document
      for its upstream candidate.
- [ ] PDF accepts exactly one document input of kind `accepted_docx`; HTML and
      arbitrary command templates are schema- and code-level impossibilities.
- [ ] Neutral modules never invoke legacy direct HTML-to-PDF routes.
- [ ] ArtView bundle, accepted decision manifest/application, and all effective
      configs are mandatory package roles.
- [ ] Run/stage/receipt/package seals and full inventories are revalidated on
      every resume.
- [ ] Existing outputs are never overwritten; partial results cannot acquire a
      successful manifest.
- [ ] All installed dependencies resolve under `.tools`; only existing Word and
      PowerShell are explicit system exceptions.
- [ ] The offline verifier rejects missing, extra, modified, escaping, or
      reparse package content and reports no release claim.

### P1 - correctness and compatibility; close before Dissociation use

- [ ] Neutral MASTER_EN v3 derives page/count/topology facts and cannot reach
      Viral constants.
- [ ] MASTER_RU submission preserves unit order, Markdown structure,
      anchors/links/images, dice/numeric tokens, and shared terminology.
- [ ] ArtView v3 derives all row/page/cardinality facts and preserves complete
      reviewed decision closure.
- [ ] HTML adapter binds accepted MASTER_RU, ArtView decisions/application, and
      effective config before invoking the renderer.
- [ ] Explicit DOCX config changes metadata/layout while the no-config path
      preserves existing Viral tests and callers.
- [ ] Real Word COM integration produces PDF from a synthetic DOCX, records
      tool/export identity, and closes Word on both pass and failure.
- [ ] DOCX preview and final PDF render every page through `.tools` Poppler and
      emit complete visual-review inventories.
- [ ] Synthetic end-to-end execution stops at every user gate and reaches only
      `candidate_for_release_review` after all exact receipts are supplied.
- [ ] Tampering with any master, decision, config, tool identity, DOCX, PDF,
      stage manifest, receipt, or package file blocks resume/verify.
- [ ] Existing reconstruction tests and existing Viral/Innsmouth compatibility
      tests remain green.

## 12. Required focused tests

At minimum, future engineering must add tests for:

1. closed-schema positives and unknown-field negatives;
2. preflight zero-write behavior for every failure class;
3. safe-path/reparse/output containment;
4. exact fixed order and one-stage-per-resume behavior;
5. missing, stale, wrong-kind, duplicate, or mismatched acceptance documents;
6. config/tool/implementation drift invalidating cache reuse;
7. injected-adapter end to end with a stop at each acceptance gate;
8. direct-route rejection before any write and an assertion that the neutral
   adapter registry has no legacy PDF callable;
9. HTML adapter config derivation and asset/link closure;
10. parameterized DOCX metadata/page setup plus legacy default parity;
11. PowerShell Word adapter argument/cleanup behavior with injected COM, plus a
    Word-host smoke test when available;
12. DOCX-only final PDF lineage and final PDF atomic replacement;
13. all-page render inventory and blank/clipping/orphan signal generation;
14. package exact inventory, mandatory ArtView/config roles, offline copied
    verifier success, and single-byte/extra-file/reparse tamper failures;
15. no release/acceptance inference in any stage result.

The critic must review actual adapter invocation paths, not only injected
fixtures. A real-tool smoke may be host-conditional, but the direct-route and
lineage tests are never skippable.

## 13. Explicitly rejected overengineering

- One universal contract spanning reconstruction, translation, art, rendering,
  packaging, and release.
- Mutation of historical `ScenarioContract.v1` or MinerU stage manifests.
- A generic DAG engine, plugin marketplace, arbitrary shell-command stages, or
  dynamically loaded adapters.
- Shared/content-addressed cache across runs or hosts in v1.
- A database, queue service, daemon, web dashboard, or remote orchestrator.
- Reimplementing the HTML renderer, DOCX converter, ArtView extractor, or
  translation batch primitives before wrapping them.
- Installing LibreOffice, Chromium, or another PDF engine.
- Supporting multiple DOCX-to-PDF engines in v1.
- Cross-platform byte-identical Word PDF claims.
- Embedding a mutable release receipt inside the frozen package candidate.
- Migrating or deleting Viral/Innsmouth legacy routes as a prerequisite for the
  neutral path.

## 14. Acceptance checklist for this architecture and next action

An independent architecture/process critic should accept this specification
only if it confirms:

- [ ] additive publication contracts preserve the reconstruction boundary;
- [ ] user acceptance remains explicit, hash-bound, and external to stage
      success;
- [ ] the sole final PDF lineage is accepted DOCX -> Word COM -> PDF;
- [ ] the HTML renderer is reused without importing its obsolete PDF route;
- [ ] the DOCX parameterization preserves existing callers;
- [ ] ArtView and every effective config are unavoidable package inputs;
- [ ] identity/resume/cache rules fail closed under stale external decisions and
      Word/font/tool drift;
- [ ] the package verifier is genuinely offline and cannot claim release;
- [ ] Packet A/B/C ownership is narrow enough to implement and review without
      scenario-specific executable code;
- [ ] all P0/P1 invariants and legacy containment tests are implementable from
      the named files/functions.

Blockers:

- No architecture blocker remains after independent criticism.
- Live reconstruction remains blocked on a CUDA-capable host, and publication
  content stages remain gated on accepted upstream artifacts. Neither blocks
  implementing and testing the neutral control plane with synthetic fixtures.
- Word COM is a Windows/system dependency. The user reports it available; its
  exact path/version/font environment must still be captured by preflight.

Next action:

1. Obtain an independent `gpt-5.5` architecture/process review of this receipt.
2. If no P0/P1 design finding remains, dispatch Packet A exactly as scoped.
3. Review Packet A implementation independently before Packet B/C or any live
   Dissociation publication input.
4. Keep final acceptance and release pending.
