# A1 — Cover / ArtView root-cause and remediation contract

## Receipt

- Goal id: `20260918-dream-cover-artview-closure`
- Step id: `A1`
- Role: architecture / root-cause analysis
- Policy target: `gpt-5.6-sol`, high reasoning
- Actual model / effort: unavailable / unavailable
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Scoped override: none
- Scope: read-only audit of PDF visual discovery, reconstruction visual
  obligations, ArtView v3 source/profile/application contracts, Stage 40 cover
  binding, QA, and a compatible rebuild that preserves accepted MASTER bytes.
- Result: root cause confirmed; scenario-neutral remediation contract specified.
- Files changed: this receipt only.
- Blockers: none for engineering. User review remains mandatory for every newly
  discovered ArtView row, including the cover; no acceptance can be inferred.
- Next action: orchestrator assigns A2/A3 engineering against this contract,
  then starts a fresh successor publication run.
- Elapsed time: approximately 25 minutes.
- Token use: unavailable.
- Timestamp: `2026-09-18T14:58:13.7568871+03:00`.

## Finding

The user expectation is correct: ArtView is intended to expose source-PDF art
for human selection. The live v3 implementation does not currently satisfy
that promise. It is a closed, profile-driven copier and reviewer, not a PDF
visual-discovery stage.

The defect is a chain of three independently permissive boundaries:

1. The reconstruction contract declares page 1 as `content_mode=visual` with
   `full_page_art` and `visual_preserve`, but the accepted page-1 decision has
   `assets: []`. Stage 04 retained a page render only as review evidence; Stage
   05/06 did not require either a selected asset or an explicit downstream
   visual-discovery obligation for that role.
2. The checked-in ArtView v3 profile has 19 authored rows, all backed by
   `accepted_reconstruction_asset` entries on pages 4–26. Its closed input
   schema has no immutable source-PDF input and no discovery manifest. Stage 30
   validates and copies only those rows. It therefore proved closure of the
   authored subset, not completeness against the source PDF.
3. HTML policy v1 declares only `cover.source_page=1`. It has no accepted
   ArtView binding. Stage 40 validates page role/order and local references but
   does not require `frontmatter_manifest.cover.asset` to be non-null. Run14
   consequently passed while page 001 remained text-only.

This explains why earlier cover handling appeared to work: in Dissociation the
cover already existed as an accepted reconstruction asset and Markdown image
reference. That exercised asset transport, not independent PDF discovery. The
Number 7 Dream cover exposed the hidden dependency.

The source is not ambiguous. The accepted source identity records the exact
26-page PDF (`C03AD...97D0`), and PDF object inspection reports page-1 image
objects including a 1837x2450 raster. The clean page is visually composite:
photo, title/text and logo are separate PDF content. The Stage-04 PNG is an
annotated review overlay and must not be reused as reader art.

## Earliest failing layer and ownership

| Boundary | Required ownership | Current failure | Required result |
| --- | --- | --- | --- |
| Reconstruction contract | Declare visual obligations | `visual_preserve` can end with `assets: []` silently | Selected reconstruction asset **or** closed `deferred_to_source_visual_discovery` obligation |
| PDF visual discovery | Inventory immutable source independently of Markdown | No v3 source-PDF input or extraction pass | Complete raw-object ledger plus semantic review-unit ledger |
| ArtView | Human choice over every reviewable visual unit | Reviews only authored profile rows | Every semantic unit is reviewed, excluded, or explicitly blocked |
| Stage 31 | Preserve exact selection and semantic placement | Carries binary/presentation only | Carries exact selected binary plus placement role/target |
| Stage 40 | Bind required cover and fail closed | `cover.source_page` only; null asset accepted | Exact accepted cover binding and exactly one rendered cover |
| QA | Prove source visual and output closure | Count-based pass over incomplete declaration | Independent source/decision/DOM closure and visual review |

## Proposed source-visual contract

Implement a versioned successor rather than weakening the closed v3 schemas.
The concrete names may be adjusted during engineering, but the information and
fail-closed behavior below are mandatory. ArtView is a deterministic one-shot
tool from the immutable PDF: a normal Stage-30 invocation performs discovery
and produces the complete review bundle. A hand-authored list of reader rows is
not an admissible discovery input.

### 1. Run-local PDF visual discovery

Stage 30 must first create a sealed `source_visual_inventory` from the exact
immutable PDF whose bytes, SHA-256, page count, media box and rotation equal
the accepted `SOURCE_IDENTITY.json`. The actual source path is an execution
input; the sealed identity is authority. A path match without byte/hash match
is invalid.

The inventory has two closed layers:

- `raw_objects`: every page image/XObject occurrence, including xref/object
  identity, dimensions, color space, masks/SMasks, bbox/transform where
  available, decoded binary identity and provider evidence;
- `visual_units`: semantic candidates composed from one or more raw objects or
  a deterministic clean page/crop render. Each unit records `review_id`, source
  page/region, component ids, derivation, exact binary, context render,
  classification, and publication placement eligibility.

Every raw object occurrence must belong to exactly one disposition: component
of a reviewable visual unit, or objectively technical PDF mechanics such as a
mask/SMask, colorspace helper, image tile that cannot stand alone, clipping
artifact, or zero-content object. No size-, page-role-, Markdown-,
reconstruction-, decorative-value-, or duplicate-based silent dropping is
allowed. Byte-identical occurrences may share stored binary bytes, but every
visible occurrence remains explicit in the discovery ledger and ArtView row
set so the human controls its placement independently. Low-confidence
classification becomes an ArtView row, not an automatic exclusion.

Discovery and publication selection are separate contracts:

- discovery deterministically exposes every non-technical source visual and
  seals the technical-mechanics ledger;
- ArtView decisions, made by the human, choose the binary, include/exclude it,
  and set presentation/placement;
- no authored profile row, reconstruction reference, or renderer policy may
  preselect the reader subset.

Provider policy should preserve the existing preference order:

1. complete native XObject;
2. independently validated native/composed object;
3. deterministic clean page crop;
4. deterministic clean full-page render when the page itself is the semantic
   unit.

For a composite cover, the current candidate should be a clean full-page
render from the immutable PDF, produced without Stage-04 annotations. Native
objects remain bound provenance/alternatives; the largest object alone must
not be assumed to contain vector title text or logos.

### 2. ArtView successor profile and decisions

The successor profile must describe extraction mechanics and bind these
additional authorities; it must not enumerate discovered rows:

- exact source identity and immutable PDF bytes;
- sealed source-visual inventory;
- accepted reconstruction inventory/contract, for semantic page roles and
  already placed assets;
- accepted MASTER_RU and its asset manifest.

Rows must use a stable logical `review_id`/`placement_id` distinct from the
selected binary SHA. Each row carries:

- `source_page`, `source_region`, group and accessible label;
- provenance kind (`accepted_reconstruction_asset`, `native_pdf_object`,
  `composed_pdf_unit`, `clean_page_render`, or `clean_page_crop`);
- semantic role and placement target;
- current candidate, context and alternatives;
- whether a publication policy requires the row.

At minimum placement targets include:

- `markdown_asset` for assets already referenced by accepted MASTER_RU;
- `source_page_cover` for a cover owned by a page role rather than Markdown;
- `source_page_before` / `source_page_after` or a sealed heading anchor for
  newly discovered inline art;
- `evidence_only` for technical/reference visuals that must not render.

Every non-technical discovered visual unit/occurrence must have an ArtView row.
All content exclusions, including decorative art, duplicates and unwanted
logos, are human decisions in ArtView. All rows require explicit human review.
A required cover cannot close as `exclude`,
`needs_manual_work`, or `reopen_masters`; those states block Stage 31/40.

Do not auto-accept a changed graph. A generic carry-forward helper may copy the
19 prior decisions into a **draft** successor only when each old row's source
and candidate identities, alternatives, placement, and presentation contract
are exact. New discovery rows remain unreviewed. The result is never an
ArtView acceptance receipt.

### 3. Stage-31 projection

The reader projection and effective visual config must retain, for every
included selection:

- stable review/placement id;
- exact selected binary identity and source choice;
- semantic role and placement target;
- source page/region;
- presentation parameters.

The application inventory must cover every included binary exactly once and
must preserve evidence-only dispositions without copying them into reader
assets. A required publication placement with no included binary is an error.

### 4. Stage-40 cover policy and binding

Add a versioned HTML publication policy whose cover is not merely a page
number. It must identify the required accepted ArtView placement, for example:

```json
{
  "source_page": 1,
  "placement_id": "source-cover-page-001",
  "required": true,
  "render_mode": "replace_source_page",
  "fit": "contain"
}
```

`replace_source_page` is appropriate for the clean composite page render: it
renders exactly one cover visual and does not duplicate reconstructed cover
text already present inside that render. If engineering chooses an extracted
background-only object instead, use a separate explicit `page_background`
mode and preserve the text overlay; mode must never be inferred from image
dimensions.

Before invoking the renderer, Stage 40 must resolve the placement through the
exact accepted decisions, Stage-31 projection and applied asset inventory. It
must materialize/rebase the binary under Stage-40 `artifacts/assets`, inject
the derived renderer config, and reject missing, excluded, ambiguous, stale or
multiply matched cover bindings.

After rendering, fail unless all are true:

- `frontmatter_manifest.cover.asset` is non-null and names the expected
  placement, asset and runtime source;
- the exact local asset exists and matches the Stage-31 identity;
- the DOM contains exactly one cover semantic container and exactly one cover
  image/background reference according to `render_mode`;
- replacement mode leaves no duplicate visible source-page cover text;
- the declared frontmatter order remains cover, credits, source TOC, body.

The generic translator may format a valid resolved cover, but it must not
discover or choose one. Discovery belongs before human ArtView review; binding
belongs in the Stage-40 adapter.

## Compatibility and rebuild sequence

1. Keep replay-21, accepted reconstruction, run14 and both accepted masters
   immutable. Run14 remains defect evidence and must not be resumed.
2. Implement and test source-PDF discovery, successor ArtView contracts,
   Stage-31 placement propagation, HTML policy/binding and fail-closed QA.
3. Update the live Number 7 Dream ArtView/HTML configs and author a fresh
   publication contract because config and implementation identities change.
4. Start a fresh publication run. Reproduce MASTER_EN and MASTER_RU
   byte-for-byte and use only existing exact-equivalence acceptance/rebind
   mechanisms; assert their accepted SHA-256 values remain
   `C3B4F13E...9367AA` and `904133D5...0FDAB2`.
5. Run the complete PDF visual discovery over all 26 pages. Compare the new
   visual-unit ledger against the 19 prior rows and the full raw-object ledger.
6. Carry forward exact unchanged decisions only into a draft. Present the
   cover and every other newly discovered reviewable unit to the user. Record
   a new ArtView acceptance only after explicit export/decision.
7. Apply Stage 31, build fresh Stage 40, then run bounded QA and independent
   review on the exact HTML hash.
8. Stop at HTML acceptance. Do not create Stage 50/DOCX/PDF/package and do not
   commit or push.

## Required tests

### Discovery and completeness

- Synthetic composite PDF: photo XObject + logo/mask + vector/text on a cover;
  invoke Stage 30 once with no authored rows; assert every raw object occurrence
  is inventoried and classified exactly once, all non-technical visuals appear
  in ArtView, and a clean full-page semantic unit is produced.
- Multi-page PDF with duplicate xrefs, masks, tiny technical objects, crops and
  one ambiguous object; assert only proved technical mechanics can be omitted
  from review, duplicate occurrences remain visible/reviewable, and ambiguity
  becomes a review row.
- Source-PDF byte/hash/page mismatch, changed render provider/settings, missing
  decoded object or unclassified raw object must fail before ArtView output.
- A reconstruction role declaring `visual_preserve` may not close with neither
  selected assets nor an explicit downstream discovery obligation in future
  reconstruction runs.
- Stage 30 must reject a profile/inventory that omits a reviewable visual unit
  or the required cover unit.

### Decisions and migration

- Old 19-row accepted graph plus one new cover row: exact rows may carry into a
  draft, cover remains unresolved, accepted state is impossible.
- Any changed old binary, alternative, placement or presentation contract
  prevents carry-forward for that row.
- Required cover exclusion/manual/reopen choice blocks application/publication.

### Stage 31/40

- Included cover selection retains exact identity and placement through
  decisions, reader projection, effective config, application and Stage 40.
- HTML policy rejects a cover page without `placement_id`, required flag or
  explicit render mode.
- Missing/excluded/stale/duplicate cover asset and
  `frontmatter_manifest.cover.asset = null` all fail closed.
- Positive composite-cover fixture renders exactly one local cover visual,
  correct flow and no duplicate cover text.
- Existing 19 body images, 18 source TOC links, seven neutral statblocks,
  Appendix C hierarchy and local-reference closure remain unchanged.
- Accepted MASTER_EN and MASTER_RU hashes are asserted byte-identical before
  Stage 30 and again in final QA; no Stage-50+ output exists.

## Acceptance criteria for A2/A3

- ArtView is a deterministic one-shot PDF-to-review-bundle operation with no
  hand-authored discovery row list.
- ArtView completeness is proven against immutable PDF visual inventory, not
  against authored rows or Markdown references.
- Every PDF raw visual object is accounted for and every reviewable semantic
  unit is shown to the user.
- Only objective PDF technical mechanics may be automatically omitted; every
  content-level exclusion is an explicit human ArtView decision.
- The Number 7 Dream clean composite cover is an explicit ArtView row and a
  required publication placement.
- Stage 40 cannot produce a passing candidate with a null/missing cover asset.
- No accepted reconstruction or MASTER bytes are edited.
- Focused and regression tests pass, with adversarial negative cases listed
  above.
- Documentation explains the split: PDF discovery finds candidates,
  reconstruction/role contracts supply semantic context, ArtView supplies
  human decisions, Stage 31 carries placement, and Stage 40 only materializes
  an accepted binding.

## Files checked

- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260918-dream-cover-artview-closure/plan.md`
- `kb_creator/docs/plans/20260918-dream-cover-artview-closure/context.md`
- `kb_creator/contracts/number-7-dream.reconstruction.json`
- `kb_creator/contracts/number-7-dream.publication-v2.json`
- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`
- `kb_creator/contracts/scenario_artview_decisions.v3.schema.json`
- `kb_creator/inputs/number-7-dream/publication/v1/configs/artview/profile.json`
- `kb_creator/inputs/number-7-dream/publication/v1/configs/artview/source-graph.json`
- `kb_creator/inputs/number-7-dream/publication/v1/configs/html.json`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/pipeline/publication_adapters.py`
- `translator/translator.py`
- replay-21 page-1 decision, merge packet, visual manifest and asset manifest
- run14 ArtView bundle/apply evidence, Stage-40 frontmatter manifest and HTML
- Dissociation cover profile/output as comparison evidence
