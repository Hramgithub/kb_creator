# Engineer receipt: Dissociation merge decisions pages 001–003

Date: 2026-09-15

## Assignment

- Goal: `20260914-dissociation-publication`.
- Packet: bounded content/reconstruction decision packet A, source pages 001–003 only.
- Assigned/actual requested role: engineering, `gpt-5.6-sol` at `high` reasoning under the user-scoped override (repository-policy engineering default is `gpt-5.6-terra` / `medium`; platform identity remains unavailable).
- Ownership observed: only `20260914-cpu-first-04-decisions/pages/page-001.json` through `page-003.json` and this receipt were changed. Run `20260914-cpu-first-04`, its source/view/comparison/bundle evidence, pages 004–006, code, canonical plan/context/status, and user configuration were not modified.
- No acceptance, resume, live MinerU/source execution, network, GPU, remote/API, Git commit, or publication action was inferred or performed.

## Evidence reviewed

- Immutable run `20260914-cpu-first-04`: review queue, Stage 03 comparison, Stage 04 merge index and exact packets for pages 001–003, and all referenced block/asset records.
- Direct visual inspection at original cached resolution of:
  - `.tools/review-cache/dissociation-20260914-cpu-first-04/triptychs/page-001.jpg`
  - `.tools/review-cache/dissociation-20260914-cpu-first-04/triptychs/page-002.jpg`
  - `.tools/review-cache/dissociation-20260914-cpu-first-04/triptychs/page-003.jpg`
- All three succeeded CPU views were compared. The two original-PDF overlays agree visually; the raster OCR view supplied independent heading/geometry evidence and the only exact full-page cover asset.

## Decisions

### Page 001 — cover

- Overlay: `original_pipeline_txt`, which retains the source color/canvas without OCR tint.
- Provenance: author text `original_pipeline_txt:0`; full-page cover asset `raster_pipeline_ocr:0`.
- Markdown retains the exact displayed uppercase title and lowercase author credit, plus the full-page asset `dissociation-cover.jpg`.
- `unresolved: []`; `visual_reviewed: true`. This is a reconstruction decision, not user acceptance.

### Page 002 — scenario body

- Overlay/body provenance: `original_pipeline_txt`, because it preserves smart punctuation, paragraph divisions, and exact two-column reading order better than OCR.
- Reading order is the complete left column followed by the complete right column.
- The decorated drop-cap restores the visually confirmed leading `T`; the visually confirmed `mi-go` and unbroken `examine` are retained.
- The comparator-conflicted original `Involving the Investigators` title block is not selected. Independent `raster_pipeline_ocr:8` supplies exact heading provenance, with an explicit visually reviewed case correction recorded in `review.notes`.
- `unresolved: []`; `visual_reviewed: true`.

### Page 003 — scenario body

- Overlay/provenance: `original_pipeline_txt`; OCR is supporting visual evidence.
- Reading order is the left column, including a Markdown blockquote card for exact `NAMES:` and `OCCUPATIONS:` content, followed by the right column.
- Heading hierarchy and the visually split `three-inch` word are reconstructed; the final `malle-` remains deliberately incomplete at the exact source-page boundary for page 004 continuation.
- `unresolved: []`; `visual_reviewed: true`.

## Exact decision identities

- `page-001.json`: `147B2397D2DD594F0E4863AD6AB71E1F4A83DD7521124C78D47D129187A46E5C`
- `page-002.json`: `3E1CA05990CC2209DC1EC11BA5EC055E58C603020DD175816FB48D6499B8FEA6`
- `page-003.json`: `D18EC8A9671CE0D3D51705C79168828CE8CE389A822EBB3BE2B78AC9EFFCB5D8`

## Validation

- Production `_validate_decision` against the immutable packets, Stage 03 comparison, and Stage 02 raw artifacts: **3/3 passed**.
- Full six-page fidelity audit using the production CLI: **passed**, no errors or repeated substitutions.
  - page 001 recall `1.0` (short-cover threshold not applied);
  - page 002 recall `0.9977298524404086`, precision `0.9965986394557823`;
  - page 003 recall `0.9805352798053528`, precision `0.9950617283950617`.
- Full six-page disposable materialization using copied exact content-list/asset bytes and the real comparison graph under `.tools/review-cache/dissociation-20260914-cpu-first-04/`: **passed** with `candidate_ready_for_reconstruction_qa`, `6` pages, `2` selected assets and `2` unique asset blobs. Output: `materialize-validation-closed-pages-001-006/`.
- JSON decision shapes, exact selected references, headings, asset placeholder/source containment, and closed unresolved/review fields are therefore accepted by the current validator/materializer.

## External blocker discovered

The exact production materializer argv currently fails before reading decisions because `materialize_mineru_ai_merge.py::_load_bundle` searches `<Stage02 raw_root>/comparison/comparison.json`, while RunSpec v2 stores the immutable comparison at `outputs/03-compare-views/comparison.json`. The direct failure was:

`FileNotFoundError: ...outputs\\02-mineru-three-view\\comparison\\comparison.json`

The disposable validation mirror changed only local comparison path bindings so the current decision validator/materializer could be exercised without changing the immutable run. This proves the decisions, not the production resume wiring. The generic Stage02/Stage03 comparison-path gap must be fixed and independently reviewed before any real resume.

## Uncertainty and next action

- Pages 001–003 have no unresolved content uncertainty after visual review and three-view comparison.
- No user acceptance is claimed.
- Next: independent content/decision review, then generic production materializer-path remediation and closure. Do not resume run `20260914-cpu-first-04` until that separate blocker is closed.
