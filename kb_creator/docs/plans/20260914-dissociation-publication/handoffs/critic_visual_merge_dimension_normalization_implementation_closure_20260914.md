# Critic receipt — visual-merge dimension normalization implementation closure

Timestamp: 2026-09-14T23:32:31+03:00  
Goal: 20260914-dissociation-publication  
Assignment: independent implementation closure review for fresh local CPU run `20260914-cpu-first-04`  
Review kind: implementation  
Reviewer role: independent critic, `gpt-5.5` requested by assignment  
Implemented or materially designed candidate: no  
Orchestrator policy owner: main-chat orchestrator remains owner; critic role does not transfer orchestration ownership  
Assignment state: complete  
Scoped override: reviewer may write only this immutable handoff receipt; no implementation, `.tools`, source, run-root, live MinerU/PDF, network/GPU/remote/API, Git commit changes

## Authority read

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/contracts/dissociation.reconstruction.json`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_visual_merge_dimension_normalization_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_visual_merge_dimension_normalization_architecture_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_visual_merge_dimension_normalization_20260914.md`

## Files checked

Implementation and runtime:

- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`

Schemas:

- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/mineru_three_view_inputs.v2.schema.json`
- `kb_creator/contracts/mineru_geometry_plan.v1.schema.json`
- `kb_creator/contracts/mineru_visual_merge_bundle.v2.schema.json`
- `kb_creator/contracts/mineru_geometry_failure.v1.schema.json`

Tests:

- `kb_creator/tests/test_mineru_geometry_normalization.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- broader reconstruction/control-plane tests listed under evidence

Diff scope observed:

- tracked diff: `build_mineru_visual_merge_bundle.py`, `prepare_mineru_three_view_inputs.py`, `test_mineru_three_view_tools.py`, `test_mineru_visual_merge_bundle.py`
- additional scoped untracked candidate files: v2 schemas, `pipeline/mineru_cpu_first.py`, `pipeline/reconstruction.py`, `test_mineru_cpu_packet_b.py`, `test_mineru_geometry_normalization.py`

## Evidence

Static review:

- Stage01 CPU-first path now opts into `source_displayed_mediabox_v1`; legacy preparer default remains `legacy_pixel_grid_v1`.
- Stage01 records source MediaBox/CropBox, source rotation/UserUnit, displayed dimensions, raster pixel dimensions, raster PDF page size/rotation/UserUnit, and reopened raster-PDF verification with one image and no text layer.
- Stage01 guards finite/positive source geometry, right-angle rotation, non-unit UserUnit, and uniform page MediaBox/rotation before output materialization.
- Raster PDF construction uses full MediaBox rendering, embeds the sampled image on the source-displayed canvas, and verifies exact image-only topology after writing.
- Stage04 v2 path requires the exact prepared manifest and manifest sha, verifies the sealed view-set/comparison binding, builds `kb_creator.mineru_geometry_plan.v1` before rendering, and rejects stale/non-v2 resume evidence.
- Geometry plan binds run identity, preparation manifest, source, comparison, view-set receipt, renderer identity, succeeded view order, layout identities, observed geometry matrix, tolerances, and target pixels.
- Geometry preflight supports exactly 3, 4, or 5 succeeded views, with the required CPU triptych first and optional GPU companions afterward.
- Geometry failure writes sealed `geometry-failure.json` with `outputs_created: []`; `mineru_cpu_first` quarantine tests verify it is retained with `stage-failure.json` and not treated as skip/success.
- `validate_v2_bundle` recomputes/validates manifest and plan seals, full generated inventory, rendered PNG identities/dimensions/mode/order, exact topology, counts, and expected plan on resume.
- Runtime run spec v2 binds geometry policy/tolerances/rounding/renderer recipe and includes new schema files in implementation identity.
- Static anti-repair scan over scoped scripts found no `.resize(`, `.thumbnail(`, `ImageOps.fit`, `-cropbox`, or `-scale-to*` primitives; only explicit negative transform evidence remains: `pad=false`, `crop=false`, `post_render_resize=false`.
- Legacy path is preserved: non-CPU-first visual bundle remains v1, and preparer default remains v1 unless `--geometry-policy source_displayed_mediabox_v1` is supplied.

Command evidence:

```text
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps';
python -m pytest kb_creator\tests\test_mineru_geometry_normalization.py -q
28 passed in 3.65s
```

```text
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps';
python -m pytest kb_creator\tests\test_mineru_geometry_normalization.py kb_creator\tests\test_mineru_three_view_tools.py kb_creator\tests\test_mineru_visual_merge_bundle.py kb_creator\tests\test_mineru_cpu_packet_b.py -q
82 passed in 70.88s
```

```text
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps';
python -m pytest kb_creator\tests\test_mineru_geometry_normalization.py kb_creator\tests\test_mineru_three_view_tools.py kb_creator\tests\test_mineru_visual_merge_bundle.py kb_creator\tests\test_mineru_cpu_packet_b.py kb_creator\tests\test_mineru_cpu_profile_packet_a.py kb_creator\tests\test_reconstruction_control_plane.py kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py kb_creator\tests\test_materialize_mineru_ai_merge.py kb_creator\tests\test_finalize_mineru_reconstruction.py kb_creator\tests\test_reconstruction_promotion.py kb_creator\tests\test_reconstruction_promotion_adversarial.py kb_creator\tests\test_pipeline_identity.py kb_creator\tests\test_scenario_contract.py -q
447 passed, 1 skipped in 143.21s
```

```text
python -m compileall -q kb_creator\scripts\prepare_mineru_three_view_inputs.py kb_creator\scripts\build_mineru_visual_merge_bundle.py kb_creator\pipeline\mineru_cpu_first.py kb_creator\pipeline\reconstruction.py kb_creator\tests\test_mineru_geometry_normalization.py kb_creator\tests\test_mineru_cpu_packet_b.py
COMPILE_OK
```

```text
jsonschema.Draft202012Validator.check_schema(...) for:
- mineru_three_view_inputs.v2.schema.json
- mineru_geometry_plan.v1.schema.json
- mineru_visual_merge_bundle.v2.schema.json
- mineru_geometry_failure.v1.schema.json
- run_spec.v2.schema.json
JSONSCHEMA_CHECK_SCHEMA_OK 5
```

```text
[System.Management.Automation.Language.Parser]::ParseFile(...)
PS_PARSE_OK kb_creator\scripts\run_mineru_three_view.ps1
```

```text
git diff --check -- kb_creator\scripts\prepare_mineru_three_view_inputs.py kb_creator\scripts\build_mineru_visual_merge_bundle.py kb_creator\tests\test_mineru_three_view_tools.py kb_creator\tests\test_mineru_visual_merge_bundle.py
exit 0
```

```text
scoped trailing-whitespace scan over implementation, schemas, and tests
SCOPED_TRAILING_WS_OK
```

## Findings

### P0

None.

### P1

None.

### P2

1. Test environment discoverability: the default `python` and `py` launchers were unavailable, and the bundled Codex Python lacked `pytest`, `jsonschema`, and `fitz`; the existing repo-local dependency directory `C:\_Hobby\_work\NRI\.tools\python-test-deps` had to be added to one-shot `PYTHONPATH` to execute the suites. This is not an implementation correctness failure, but it is worth documenting for repeatability of critic/QA commands.

2. Minor code hygiene: `_write_geometry_failure` contains a duplicate unreachable `raise FileExistsError(...)` line after the first raise. It is harmless under current control flow and is not a blocker for `-04`, but can be cleaned in a later non-functional pass if desired.

## Blockers

None for a fresh local CPU-only run `20260914-cpu-first-04`.

Explicit non-evidence: this review did not run live MinerU, a real Dissociation PDF, GPU providers, network, remote/API calls, or Git commit, per assignment constraints.

## Recommendation

GO for a fresh local CPU-only run `20260914-cpu-first-04`.

Rationale: the implementation closes the observed `-03` Stage04 dimension mismatch class by making Stage01 source-displayed MediaBox geometry the direct authority for Stage04 preflight and rendered target pixels. The new v2 evidence chain rejects stale or drifted inputs, fails closed with sealed geometry evidence, preserves legacy v1/default behavior, and passed focused plus broader relevant synthetic suites on current code.

## Review accounting

Elapsed time: approximately 55 minutes in recovery context  
Token use: unavailable exact worker token accounting; approximate critic-side use 31k tokens  
Receipt written by critic only; no implementation files changed by critic.
