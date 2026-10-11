# Independent critic architecture review: visual-merge dimension normalization

- Goal: `20260914-dissociation-publication`
- Review artifact: `critic_visual_merge_dimension_normalization_architecture_20260914.md`
- Review kind: architecture
- Candidate reviewed: `architect_visual_merge_dimension_normalization_20260914.md`
- Decision scope: bounded implementation authority only; not a release review and not live-run authorization
- Timestamp: 2026-09-14T22:02:03.9374344+03:00
- Reviewer role declared by assignment: independent critic, `gpt-5.5` at medium reasoning
- Actual platform model disclosure: unavailable inside this agent; no claim beyond assigned role
- Implemented candidate: no
- Materially designed candidate: no
- Orchestrator policy owner: main-chat orchestrator, `gpt-5.6-sol` at medium per `docs/governance/nri_goal_governance.md`
- Assignment state: architecture review of a proposed generic remediation spec
- Scoped override: no implementation edits, no `.tools` mutation, no live `20260914-cpu-first-03`/`-04` run, no real MinerU/PDF pipeline execution, no network, no GPU, no remote/API, no commit; only this immutable receipt was written
- Elapsed review time at receipt drafting: approximately 3 minutes in the active goal
- Token use at receipt drafting: goal snapshot reported 125,174 tokens used

## Authority and inputs checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_visual_merge_dimension_normalization_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_cpu_third_real_attempt_failure_20260914.md`
- Immutable run evidence under `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-03/`:
  - `run.json`
  - `outputs/01-prepare-inputs/command.json`
  - `outputs/01-prepare-inputs/prepared/sample_pages.json`
  - `outputs/01-prepare-inputs/prepared/source_raster.pdf`
  - `outputs/02-mineru-three-view/view-set.json`
  - Stage 02 view receipts and layout PDFs for the three succeeded CPU views
  - `stages/01-prepare-inputs/stage.json`
  - `stages/02-mineru-three-view/stage.json`
  - `stages/03-compare-views/stage.json`
  - `outputs/03-compare-views/comparison.json`
  - `failures/04-visual-merge-bundle/stage-failure.json`
- Relevant reusable code:
  - `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
  - `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
  - `kb_creator/pipeline/mineru_cpu_first.py`
  - `kb_creator/pipeline/reconstruction.py`
- Relevant tests:
  - `kb_creator/tests/test_mineru_three_view_tools.py`
  - `kb_creator/tests/test_mineru_visual_merge_bundle.py`
  - `kb_creator/tests/test_mineru_cpu_packet_b.py`
- Existing schemas:
  - `kb_creator/contracts/run_spec.v2.schema.json`
  - `kb_creator/contracts/mineru_view_execution.v1.schema.json`
  - `kb_creator/contracts/mineru_view_set.v1.schema.json`
  - `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`

## Evidence checked

### Run `20260914-cpu-first-03`

- `run.json` records:
  - schema `kb_creator.run_spec.v2`
  - profile `mineru_cpu_first_three_view_v1`
  - run identity `DE82763058E1D5FFEDF991755D2D79ED4618D63507F41BB81870152EF394BAA1`
  - source identity `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`, `2,159,317` bytes, six pages
  - source MediaBox dimensions `595 x 841`, rotation `0`
  - options `raster_dpi=200`, `review_dpi=110`, `source_box=MediaBox`
  - three required CPU views followed by two optional CUDA views
- Stage 01 `sample_pages.json` records every selected page with:
  - MediaBox `[0, 0, 595, 841]`
  - CropBox `[0, 0, 595, 770]`
  - displayed page size `[595, 841]`
  - raster pixel dimensions `[1653, 2337]`
  - `raster_has_text_layer=false`
  - raster PDF identity `EDE12A820242009DC98B1450B2AAB163F8A0489A4B4F74E6FCE980ACDCFBB548`
- `view-set.json` records required succeeded views in exact CPU order:
  - `original_pipeline_txt`
  - `original_pipeline_ocr`
  - `raster_pipeline_ocr`
  - optional CUDA views are output-free skips.
- Stage 04 failed closed with sealed `kb_creator.stage_failure.v1` and `failure_sha256` `DE64F261B772CDE8E185BB669B42E4096A15086529A3E01B079B7D382B97A4FB`.
- Stage 04 failure traceback ends at `build_triptychs()` with `ValueError: rendered view dimensions differ`.
- `local/staging/04-visual-merge-bundle` is absent after failure cleanup; `failures/04-visual-merge-bundle/` contains only `stage-failure.json`.

### Independent PDF metadata check

Read-only `pypdf` inspection confirmed:

```text
stage_failure_seal_ok DE64F261B772CDE8E185BB669B42E4096A15086529A3E01B079B7D382B97A4FB
source pages 6 bytes 2159317 unique MediaBox 595 x 841, CropBox 595 x 770, rotation 0, UserUnit 1, target at 110 DPI 910 x 1285
source_raster pages 6 bytes 32689131 unique MediaBox/CropBox 595.08 x 841.32, rotation 0, UserUnit 1, target at 110 DPI 910 x 1286
txt_layout pages 6 bytes 2456234 unique MediaBox 595 x 841, CropBox 595 x 770, rotation 0, UserUnit 1, target at 110 DPI 910 x 1285
ocr_layout pages 6 bytes 2456234 unique MediaBox 595 x 841, CropBox 595 x 770, rotation 0, UserUnit 1, target at 110 DPI 910 x 1285
raster_layout pages 6 bytes 32704174 unique MediaBox/CropBox 595.08002 x 841.32001, rotation 0, UserUnit 1, target at 110 DPI 910 x 1286
stage04_staging_exists False
failure_files ['failures/04-visual-merge-bundle/stage-failure.json']
```

This independently validates the proposed root cause: Stage 01 correctly sampled the displayed source MediaBox but persisted the rounded pixel grid as PDF physical size (`pixels * 72 / dpi`), which MinerU then preserved into the raster OCR layout. Stage 04 rendered all layout PDFs at the same review DPI and the current triptych builder treated the first rendered view's exact pixel dimensions as universal authority.

### Current code evidence

- `prepare_mineru_three_view_inputs.py` currently sets the raster PDF page size from `pixmap.width * 72.0 / dpi` and `pixmap.height * 72.0 / dpi`, explaining the `595.08 x 841.32` raster PDF canvas.
- The preparer records MediaBox/CropBox/displayed dimensions and raster pixel dimensions, and already avoids source mutation by temporarily setting the in-memory cropbox to MediaBox for rendering.
- `build_mineru_visual_merge_bundle.py` currently renders layouts using `pdftoppm -r <dpi> -png -f 1 -l <pages>` without `-cropbox`, then `build_triptychs()` requires exact equal image sizes and raises on mismatch.
- CPU-first Stage 04 already takes `succeeded_views` dynamically from the v2 comparison and preserves the stable first-three CPU baseline for triptych review.
- `mineru_cpu_first.validate_stage_output()` currently validates Stage 01 lineage and Stage 04 packet semantics but does not yet validate a v2 geometry plan; the architecture correctly scopes this as implementation work.

### Baseline checks run

Targeted baseline tests:

```text
$env:PYTHONPATH = '.tools\python-test-deps'
python -m pytest kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_mineru_visual_merge_bundle.py kb_creator/tests/test_mineru_cpu_packet_b.py -q
53 passed in 42.11s
```

Compile:

```text
python -m compileall -q kb_creator\scripts\prepare_mineru_three_view_inputs.py kb_creator\scripts\build_mineru_visual_merge_bundle.py kb_creator\pipeline\mineru_cpu_first.py kb_creator\pipeline\reconstruction.py
PASS
```

Schema parse:

```text
json.loads(...) for run_spec.v2, mineru_view_execution.v1, mineru_view_set.v1, mineru_multi_view_comparison.v2
schema json parse ok 4
```

Diff check:

```text
git diff --check -- architect_visual_merge_dimension_normalization_20260914.md prepare_mineru_three_view_inputs.py build_mineru_visual_merge_bundle.py mineru_cpu_first.py reconstruction.py
PASS
```

No real MinerU/PDF pipeline execution, render rerun, live run-root mutation, network, GPU, remote/API call, install/download, or commit was performed.

## Architecture assessment

The proposed architecture is source-authoritative and generic enough for bounded implementation.

Accepted points:

- Root cause is exact and supported by immutable run evidence.
- Geometry authority is correctly moved to sealed Stage 01 per-page source MediaBox/displayed dimensions, not to any MinerU view, first rendered view, largest canvas, CropBox, or raster pixel grid.
- Stage 01 correction is the right layer: render samples may still use the exact ceiling pixel rule, but the raster PDF physical canvas must be the authoritative source displayed MediaBox.
- The architecture explicitly forbids text-layer creation in the raster derivative and requires post-write verification of image-only raster PDF lineage.
- Stage 04 preflight is strict and occurs before Poppler rendering.
- The tolerance contract is appropriately narrow: `0.001 pt` absolute dimension tolerance, `0.000005` relative aspect tolerance, and zero pixel tolerance.
- It explicitly forbids padding, cropping, post-render resize, stretch, min/max selection, one-pixel tolerance, Poppler crop flags, and scale-to-size flags.
- Rotations and arbitrary uniform geometry are handled generically: uniform page size/rotation required, right-angle rotations only, non-unit UserUnit rejected until specified, raster views flattened to rotation `0`, original layouts may either preserve or flatten right-angle orientation.
- Dynamic view handling is correct: minimum three required CPU views, optional ready/succeeded views extend the same geometry plan in sealed order, skipped views remain output-free.
- Stable CPU triptych remains the first three required CPU views.
- v2 evidence/schema/resume/cache binding requirements are explicit and materially close the current v1 blind spot.
- `geometry-failure.json` is required to be sealed, output-free, deterministic, and quarantined with the normal stage failure.
- Resume revalidates the full geometry graph and rejects provider-set enrichment, stale paths, v1 evidence reuse, and mutation of the failed `-03` run.
- The implementation scope is bounded to reusable geometry path, direct contracts, validators, and focused compatibility tests; it does not authorize MinerU source/model/profile edits, source PDF mutation, immutable run-root mutation, publication bridge changes, or scenario-specific routing.
- Existing v1/Viral/Innsmouth compatibility is explicitly preserved by requiring unchanged legacy `mineru_visual_merge_bundle.v1`, fixed legacy `VIEWS`, and current compatibility suites.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Blockers

None for bounded implementation.

Live execution remains blocked by process, not by architecture: do not resume `20260914-cpu-first-03`, and do not start `20260914-cpu-first-04` until the bounded implementation is completed, synthetically/adversarially verified, and independently closed.

## Recommendation

GO for bounded implementation of `architect_visual_merge_dimension_normalization_20260914.md`.

NO-GO for any live `20260914-cpu-first-03` resume or fresh `20260914-cpu-first-04` run from this architecture receipt alone.
