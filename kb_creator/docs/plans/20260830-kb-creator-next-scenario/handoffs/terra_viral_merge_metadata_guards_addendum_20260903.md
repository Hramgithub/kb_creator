# Terra receipt addendum — cross-view image/title guard

- Goal id: `20260830-kb-creator-next-scenario`
- Step: bounded upstream repair `PROC-019` / `PROC-020` correction
- Role / requested effort: `nri-engineer` / Terra medium
- Orchestrator policy owner: root `gpt-5.6-sol` / medium
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-03` (Europe/Moscow)

## Scope and result

Corrected the integration-found regression in the prior receipt. Image/title
overlap detection now checks same-page pairs within each view and across both
comparison views. Each conflict records independent `asset_side` and
`heading_side`, so raw-index collisions between views cannot collapse identity.
Materializer conflict selection maps each side back to its actual view.

The existing review-notes field now supplies the minimal explicit override
convention without a schema change. A title override is accepted only when
`review.visual_reviewed` is true and `review.notes` has the exact line:

```text
title override: <exact source title>; reason: <nonempty reviewed reason>
```

An unreviewed or reasonless magic note cannot suppress a selected-title guard.

## Files changed

- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`

## Verification and evidence

```powershell
python -B -m pytest -q kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_materialize_mineru_ai_merge.py
```

Result: `47 passed in 3.01s`.

Added focused regression coverage for the requested cross-view `Summary` seed:
an `original_pipeline_ocr` image and an `original_hybrid` heading with colliding
raw index `0` produce a conflict with `asset_side=right` and
`heading_side=left`; moving the image to another source page produces none.
Materializer tests prove the selected heading side blocks materialization while
an otherwise identical unselected conflict does not.

## Blockers and next action

No blocker. The correction remains an upstream safeguard only and does not
modify or certify the current immutable Viral reconstruction or `MASTER_EN`.
Root may continue independent integration and candidate verification.

- Elapsed time: approximately 10 minutes.
- Token use: unavailable.
