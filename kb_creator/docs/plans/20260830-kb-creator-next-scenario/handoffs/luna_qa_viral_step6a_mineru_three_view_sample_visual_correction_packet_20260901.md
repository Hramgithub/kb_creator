# Luna visual correction packet - Viral Step 6A three-view sample

Date: 2026-09-01  
Owner: `gpt-5.6-luna`, high, execution-only visual QA  
Status: `AUTHORIZED`

## Boundary

The immutable first receipt remains:

`luna_qa_viral_step6a_mineru_three_view_sample_execution_20260901.md`

SHA-256:
`4425D6469E172BA992BD48A8409348D9271102AB253DA7B3C646840BED6C903E`.

It proves marker, sample preparation, all three MinerU profiles, comparator and
focused tests succeeded. Its only blocker occurred after all 24 overlay PNGs
had already been rendered: a trailing PowerShell token failed and prevented a
render console capture. The PNGs exist as three exact sets of eight.

## Authorized correction

Do not rerun marker, preparation, MinerU, comparator, tests or `pdftoppm`.
Perform only read-only validation of the already existing files under:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_sample/evidence/rendered`

For each of `original_hybrid`, `original_pipeline_ocr`, and `raster_hybrid`:

1. require exactly eight PNG files;
2. record filename, byte size, SHA-256 and pixel dimensions;
3. open and visually inspect every PNG at high detail;
4. map rendered page `1..8` to source pages
   `5, 12, 53, 69, 104, 109, 115, 123`;
5. record whether layout boxes preserve the visible page, whether meaningful
   text/image/table regions are present, and any view-specific omissions,
   spurious regions, clipping, overlap or illegibility;
6. compare the three overlays for every source page without automatically
   declaring ordinary differences to be defects.

Write exactly one new receipt:

`luna_qa_viral_step6a_mineru_three_view_sample_visual_correction_20260901.md`

The new receipt must state `PASS` only if all 24 PNGs are readable and all 24
pages were actually inspected. A visual extraction difference may be an
expected cross-view signal and should be recorded for later merge; a missing,
unreadable or uninspected page is `BLOCKED`.

## Write allowlist and forbidden actions

The only authorized write is the new correction receipt. The sample root and
all code/tests/source/prior roots/candidate/plan/context/config/production/Git
are read-only. No repair, rerender, profile rerun, new evidence file, commit or
push is allowed.

