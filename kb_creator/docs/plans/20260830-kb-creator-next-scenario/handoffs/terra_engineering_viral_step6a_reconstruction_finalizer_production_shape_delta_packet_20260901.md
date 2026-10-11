# Terra production-shape delta — Viral Step 6A reconstruction finalizer

## Boundary

Apply one final narrow engineering delta to the same finalizer script/test. The
first two receipts are immutable. Write only one new receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_finalizer_production_shape_delta_20260901.md`

Do not touch v3 decisions, candidates, packages, other files or Git. The PDF
marker already ran exactly once; do not repeat it.

## Finding 1 — production decision/provenance projection

Live v2 evidence proves the materializer's intentional schema projection:

- decision selected block:
  `{"view":"original_hybrid","raw_index":0,"purpose":"structure"}`;
- merge-provenance selected block:
  `{"view":"original_hybrid","raw_index":0}`.

The finalizer currently compares the full dictionaries, so it would reject a
valid real candidate. Normalize each decision selected block to exactly
`{"view", "raw_index"}` for comparison with merge provenance. Require the
provenance record to contain exactly that projection and no missing/duplicate
references. Continue preserving the full decision record, including `purpose`,
in the copied candidate. Continue resolving the normalized references against
the frozen comparison.

Add a production-shaped success test with decision `purpose` present and
provenance projection absent it, plus a mismatch failure test. Do not weaken
unknown-view, invalid-reference or duplicate checks.

## Finding 2 — actual contract geometry fields

The Viral contract declares page geometry under `source.media_box_points`
(`[612,792]`) and `source.rotation_degrees` (`0`); it has no
`overlay_page_geometry`. Validate every retained source page and every layout
PDF page against these real contract fields, accepting the corresponding media
box `(0,0,width,height)` and declared rotation. Reopen the selected overlay and
reprove the same geometry for all pages in addition to equality with the chosen
layout pages.

Add one focused failure case for wrong layout geometry or rotation. Keep
synthetic fixtures contract-shaped with these source fields.

## Finding 3 — named root hashes

In candidate identity, add SHA-256 and byte count for the four named root
artifacts when present: `RECONSTRUCTED_EN.md`, `MERGE_PROVENANCE.json`,
`ASSET_MANIFEST.json`, and `OVERLAY_SELECTION.json`. Preserve the existing
ordinal tree identities and selected-overlay identity.

## Verification and receipt

Run only the focused finalizer test file, `py_compile`, and `git diff --check`.
No marker repeat, MinerU, real build or 371/119/490. Record exact collected/pass
count, hashes, finding closure and the immutable predecessor-remediation receipt
hash. Return only the compact result.
