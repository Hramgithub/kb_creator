# Terra engineering receipt — finalizer production-shape delta

## Scope and result

Applied the final narrow production-shape delta to the generic reconstruction
finalizer and its focused tests only.  No real v3 decision/candidate/package
was opened or modified.  The existing receipts remain immutable.

## Changed files

- `kb_creator/scripts/finalize_mineru_reconstruction.py`
  - SHA-256: `E943D82F41651A6CBEDDAE7D199B0B755133EFB304D14DD2E2B1770FAF39C367`
- `kb_creator/tests/test_finalize_mineru_reconstruction.py`
  - SHA-256: `A50932DA655345AA74A1AD6CD63E114BF40FECC54EEAF857D113266188849F32`

Immutable predecessor remediation receipt:

- `terra_engineering_viral_step6a_reconstruction_finalizer_remediation_20260901.md`
  - SHA-256: `8D152D9B9D6B149CE6ADB4AEB31B7B71D04D41879B6257DE1EE058D838921C90`

## Finding closure

| Finding | Closure |
| --- | --- |
| Decision/provenance projection | Decision blocks may retain `purpose`; finalizer normalizes them to exact `{view, raw_index}` and requires merge provenance to contain exactly that projection. Unknown views, malformed references, mismatch, and duplicate raw references still fail. |
| Contract geometry | Requires real contract `source.media_box_points` and `source.rotation_degrees`; verifies every source and every layout page against `(0,0,width,height)` and rotation, then reopens selected overlay and verifies the chosen layout and declared geometry again. |
| Named roots | Candidate identity now records SHA-256 and byte count for each present named root: `RECONSTRUCTED_EN.md`, `MERGE_PROVENANCE.json`, `ASSET_MANIFEST.json`, and `OVERLAY_SELECTION.json`, in addition to prior ordinal inventory identities and selected overlay identity. |

## Verification/evidence

The PDF operation marker was **not repeated**; it had succeeded exactly once
earlier in this task chain.

All commands exited 0:

```powershell
python -B -m py_compile kb_creator/scripts/finalize_mineru_reconstruction.py kb_creator/tests/test_finalize_mineru_reconstruction.py
python -B -m pytest kb_creator/tests/test_finalize_mineru_reconstruction.py -q
# 22 passed in 8.48s
git diff --check -- kb_creator/scripts/finalize_mineru_reconstruction.py kb_creator/tests/test_finalize_mineru_reconstruction.py
```

The compact synthetic suite includes a production-shaped success path where a
decision has `purpose: structure` while merge provenance carries only the
two-field projection, a projection-mismatch failure, and wrong-layout-geometry
failure.  It remains temp-fixture-only.  No MinerU, real build, 371/119/490,
or Git operation ran.

## Blockers and next action

No engineering blocker.  A separate bounded execution/review can now exercise
the frozen real candidate; this receipt makes no release or acceptance decision.

## Administration

- Timestamp: 2026-09-01 Europe/Moscow
- Elapsed time: approximately 12 minutes
- Token use: unavailable
- Orchestrator policy owner: main `/root` Sol/orchestrator
- Assignment state: completed, bounded delta receipt captured
- Scoped override: none beyond the packet; prior exact italic Handout marker
  override remains implemented and in force.
