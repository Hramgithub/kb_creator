# Architecture receipt: source-authoritative visual-merge dimension normalization

Date: 2026-09-14

## Assignment and decision

- Goal: `20260914-dissociation-publication`.
- Work kind: read-only diagnosis and generic remediation specification; implementation was explicitly forbidden.
- Assigned role/model/reasoning: engineering specification under the user-scoped `gpt-5.6-sol` / `high` override (repository engineering default: `gpt-5.6-terra` / `medium`).
- Decision: **GO for the bounded implementation described below; NO-GO for resuming `20260914-cpu-first-03` or starting another real run until implementation, synthetic verification, and independent critic closure are complete.**

The failed run `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-03` was inspected read-only and remains immutable. No PDF/render pipeline, network, GPU, remote/API, source/output mutation, or Git operation was run.

## Exact failure evidence

- Run schema/profile: `kb_creator.run_spec.v2` / `mineru_cpu_first_three_view_v1`.
- Run identity: `DE82763058E1D5FFEDF991755D2D79ED4618D63507F41BB81870152EF394BAA1`.
- Immutable source: 2,159,317 bytes; SHA-256 `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`; six pages.
- Source authority recorded by RunSpec and Stage 01: every page has MediaBox `[0, 0, 595, 841]` pt, CropBox `[0, 0, 595, 770]` pt, rotation `0`, and displayed size `595 x 841` pt. Stage 01 explicitly uses MediaBox, not CropBox.
- Stage 01 at 200 DPI produced exactly `1653 x 2337` raster pixels per page. It then derived the raster-PDF page size from the rounded pixel grid: `1653 * 72 / 200 = 595.08` pt and `2337 * 72 / 200 = 841.32` pt. The raster PDF is 32,689,131 bytes, SHA-256 `EDE12A820242009DC98B1450B2AAB163F8A0489A4B4F74E6FCE980ACDCFBB548`.
- Stage 02 succeeded for the three required CPU views and Stage 03 sealed the same succeeded order: `original_pipeline_txt`, `original_pipeline_ocr`, `raster_pipeline_ocr`. Both optional GPU views were provider-local skips.
- The original txt and OCR layout PDFs are byte-identical: 2,456,234 bytes, SHA-256 `EF8FF82EE8F34C81D336B5E3908C70DA800343DE386F9CA5F06D92BE8984F7FB`. All six pages retain MediaBox `595 x 841` pt, CropBox `595 x 770` pt, rotation `0`, and UserUnit `1`.
- The raster OCR layout is 32,704,174 bytes, SHA-256 `E8E5219F6D45AFF2C082A5FAB64F660E4DBC2B0A108FCC16E02991122E3CD05A`. All six pages inherit MediaBox/CropBox `595.08002 x 841.32001` pt, rotation `0`, and UserUnit `1`.
- Stage 04 used review DPI `110` and the closed `pdftoppm -r 110 -png` recipe without `-cropbox`. Its exact MediaBox pixel canvases are therefore:
  - original txt/OCR: `ceil(595 * 110 / 72) x ceil(841 * 110 / 72) = 910 x 1285`;
  - raster OCR: `ceil(595.08002 * 110 / 72) x ceil(841.32001 * 110 / 72) = 910 x 1286`.
- `build_triptychs()` takes the first rendered image as an implicit authority and requires every other image to have exactly the same size. The one-row mismatch therefore raises `ValueError: rendered view dimensions differ` at line 181 before any bundle is promoted.
- The sealed failure is `kb_creator.stage_failure.v1`, SHA-256 seal `DE64F261B772CDE8E185BB669B42E4096A15086529A3E01B079B7D382B97A4FB`, and validates successfully. The internal Stage 04 temporary tree was deleted by the builder on exception, so the dimensions above are derived deterministically from the sealed 110-DPI command and exact inspected PDF geometry, not from surviving PNGs.

## Root cause

The source has not changed and the views did not omit pages. The defect is a geometry-authority leak between Stage 01 and Stage 04:

1. Stage 01 correctly rasterizes the full source MediaBox, rounding the sample grid upward to whole pixels.
2. It incorrectly reuses that rounded pixel grid to define the physical PDF page size instead of retaining the authoritative source displayed MediaBox.
3. MinerU preserves each input's physical page size in its layout PDF.
4. Stage 04 renders all layouts at one DPI and assumes the first rendered view's pixel dimensions are universal.

Thus a normal rasterization quantization (`595 x 841` pt -> `1653 x 2337` px) becomes a persistent physical-size drift (`+0.08 x +0.32` pt) and finally a one-pixel review-canvas mismatch. Changing the first view, taking min/max dimensions, or tolerating the final pixel difference would hide the authority error rather than fix it.

## Accepted normalization contract

### 1. Authority and Stage 01 correction

For RunSpec v2 CPU-first runs, the sole geometry authority is the sealed Stage 01 per-page source record derived from the immutable source MediaBox. It is never a MinerU view, the first succeeded view, the largest view, or the raster pixel grid.

Add an explicit CPU-first raster geometry policy, `source_displayed_mediabox_v1`. For each selected page it must:

1. require finite positive MediaBox dimensions, uniform MediaBox size and uniform rotation over the selected page set;
2. accept only rotations `0`, `90`, `180`, or `270`; other angles fail closed;
3. require UserUnit `1` for this policy (non-unit UserUnit is rejected until separately specified);
4. render the full MediaBox at the declared raster DPI using the existing exact ceiling pixel rule;
5. embed those unchanged raster samples as the sole page image on a PDF page whose physical MediaBox is exactly the source displayed MediaBox, not `pixels * 72 / DPI`;
6. flatten source rotation into the displayed orientation for the raster PDF, set output rotation to `0`, and set CropBox equal to MediaBox;
7. re-open the completed raster PDF and verify page count, exact physical geometry, rotation, CropBox, image-only property, and output identity before publishing Stage 01.

Mapping the already sampled image across its authoritative source extent is part of raster-PDF construction; it must not create a second raster resample. The current legacy preparer behavior remains available only through its existing legacy dispatch. CPU-first RunSpec v2 must select the new policy explicitly and record it.

### 2. Stage 04 geometry preflight

Before invoking Poppler, load the exact Stage 01 manifest through the identity already recorded in the sealed comparison, and also bind it directly as a Stage 04 input. Build a page-by-page geometry plan for every succeeded view in sealed `succeeded_views` order; three required CPU views are the minimum, while any ready optional views extend the same plan.

For each layout page:

- original-input views may either preserve the source rotation with the raw MediaBox dimensions or flatten it to rotation `0` with displayed dimensions;
- raster-input views must be flattened at rotation `0` with displayed dimensions;
- the effective displayed width, height, and aspect ratio must match the source-authoritative displayed MediaBox;
- CropBox is recorded for diagnosis but never selected as render authority;
- UserUnit must be `1`;
- page count and source-page order must be exact.

Use decimal/rational arithmetic, not binary-float equality. The only accepted PDF serialization tolerance is an absolute `0.001 pt` per effective dimension and a relative aspect-ratio delta no greater than `0.000005`. These tolerances admit harmless decimal serialization only; the observed `0.08/0.32 pt` drift is deliberately rejected. Pixel dimensions have no tolerance.

The canonical target canvas for each page is:

```text
target_width_px  = ceil(authoritative_displayed_width_pt  * review_dpi / 72)
target_height_px = ceil(authoritative_displayed_height_pt * review_dpi / 72)
```

For this run the target is exactly `910 x 1285` for all pages and all succeeded views.

### 3. Transform prohibitions and deterministic rendering

Stage 04 must not repair a mismatch by Pillow padding, cropping, `resize`, `thumbnail`, `fit`, stretching, min/max-canvas selection, or one-pixel tolerance. It must not pass Poppler crop or scale-to-size flags. Any view that cannot render to the exact target canvas under the same DPI fails Stage 04, including an optional view that was declared ready and succeeded at Stage 02.

The render recipe remains a shell-free ordered argv using the RunSpec-bound `pdftoppm` binary: exact DPI, PNG, MediaBox default (explicit absence of `-cropbox`), exact first/last page, exact layout identity, and deterministic numeric page ordering. Record binary SHA-256, reported Poppler version, argv shape/version, PNG mode, actual dimensions, bytes, and SHA-256. RGB conversion for compositing is allowed; geometry-changing operations are not.

The stable CPU triptych remains the first three required views in its existing order. Every optional succeeded view must receive the same geometry preflight and canonical per-page render; optional companion panels are added in sealed view order without replacing or resizing the CPU triptych. Skipped views remain output-free and are not rendered.

## Evidence, schemas, failure handling, and resume

The implementation packet should add or extend closed contracts as follows:

- RunSpec v2 options require the constant geometry policy and bind the exact preparation/normalization recipe.
- CPU-first Stage 01 emits a versioned preparation manifest that records source MediaBox coordinates, displayed dimensions, rotation policy, raster sample dimensions, exact raster-PDF physical canvas, DPI, and output identity. Legacy v1 keeps its existing manifest/dispatch.
- CPU-first Stage 04 emits `kb_creator.mineru_visual_merge_bundle.v2` plus a sealed geometry plan. The plan records its policy version, Stage 01 manifest identity, source/run identity, tolerances, rounding rule, review DPI, renderer identity, ordered succeeded views, layout identities, per-page observed PDF geometry, target pixels, actual PNG geometry/identity, and explicit `pad=false`, `crop=false`, `post_render_resize=false` declarations.
- Add a closed JSON schema for the v2 visual bundle/geometry record and include it in the RunSpec implementation inventory.
- Validate the v2 visual manifest from `mineru_cpu_first.validate_stage_output`; do not rely only on the outer stage output hash.
- On geometry rejection, write a sealed, output-free `geometry-failure.json` directly under the control-plane Stage 04 staging root before raising. It must contain the first deterministic mismatch plus the complete observed geometry matrix, input identities, policy, renderer identity, and no partial PNGs. Existing quarantine then preserves it beside `stage-failure.json`.

Resume must recompute and compare the full geometry graph: run/implementation identity, source and preparation manifest, view-set/comparison seals, exact succeeded-view set, every layout PDF identity, geometry policy/tolerances, DPI/Poppler identity, per-page plan, and complete output inventory. It must not trust absolute paths from prior local JSON, adopt newly available providers, reuse v1 evidence as v2, or resume `20260914-cpu-first-03`. Any mismatch requires a new absent run root.

## Required adversarial and compatibility tests

Implementation is not review-ready without synthetic tests for:

- the exact regression: source `595 x 841` pt at 200 DPI produces `1653 x 2337` samples but an exact `595 x 841` raster-PDF canvas, and all 110-DPI views render `910 x 1285`;
- arbitrary uniform Letter, landscape, fractional custom MediaBox, and non-zero MediaBox origins;
- source rotations `0/90/180/270`, accepted preserved-versus-flattened original layouts, and flattened raster layouts;
- rejection of non-right-angle/mixed rotations, mixed page sizes, non-unit UserUnit, zero/negative/NaN/infinite geometry, page-count/order drift, and a CropBox lure;
- dimension deltas just inside and just outside `0.001 pt`, aspect deltas around `0.000005`, and every one-pixel rendered mismatch;
- exactly 3, 4, and 5 succeeded views; stable CPU triptych plus ordered optional companions; skipped-view output remains absent;
- tampered Stage 01 manifest/seal, source identity, view receipt/layout identity, comparison/view-set, DPI, renderer binary/version, policy/tolerance, PNG dimensions/mode/hash, missing/duplicate/extra pages and files;
- geometry failure receipt sealing, deterministic first mismatch, no partial renders, and quarantine retention;
- resume rejection for all identity/policy/geometry/output drift and for provider-set enrichment;
- a static prohibition check for crop/pad/resize/scale flags in the v2 path;
- unchanged legacy `mineru_visual_merge_bundle.v1`, fixed legacy `VIEWS`, existing Viral fixtures, Innsmouth fixtures, and all current v1 reconstruction/audit/materialization tests.

## Bounded implementation scope

The implementation may change only the reusable geometry path and its direct contracts/tests: `prepare_mineru_three_view_inputs.py`, `build_mineru_visual_merge_bundle.py`, the CPU-first Stage 01/04 adapters and validators in `reconstruction.py` / `mineru_cpu_first.py`, narrowly required RunSpec/preparation/visual-bundle schemas, and focused three-view/visual-bundle/Packet B/legacy compatibility tests. It must not change MinerU source/models/profiles, source PDFs, immutable run roots, merge decisions, audit/materializer semantics, publication bridge, or scenario-specific routing.

The implementation is **GO** within that boundary. A new real Dissociation run is **NO-GO** until an engineer receipt demonstrates the full synthetic/adversarial matrix and an independent critic issues a fresh closure.
