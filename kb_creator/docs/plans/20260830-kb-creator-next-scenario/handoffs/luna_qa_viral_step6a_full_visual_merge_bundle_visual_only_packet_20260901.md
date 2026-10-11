# Luna QA packet — Viral Step 6A full bundle visual-only correction

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Executor: bounded QA (`gpt-5.6-luna`, high)  
Status: `AUTHORIZED_FOR_VISUAL_ONLY_QA`

## Purpose

Complete the visual portion of the accepted full three-view bundle without
running MinerU, the bundler, tests, PowerShell, Python, or any other command.
The earlier parser failure is irrelevant to this packet: the orchestrator has
already completed the missing read-only machine audit.

## Bound read-only bundle

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate`

The orchestrator's current audit proves:

- 124 page packets cover source pages 1..124 exactly once;
- all three raw block sets are preserved exactly by object-set SHA
  (`1845`, `1914`, `1876` blocks);
- all three asset-reference sets are preserved exactly (`190`, `104`, `178`);
- all bbox matches and left/right unmatched objects for all three view pairs
  are preserved exactly;
- manifest inventory is `777/777`, missing `0`, extra `0`, byte mismatches `0`,
  hash mismatches `0`;
- generated counts are 372 rendered pages, 124 triptychs, 31 contact sheets,
  and 124 merge packets.

Do not repeat these checks.

## Only permitted inspection actions

Use the direct local image-viewing tool only. Do not open a terminal and do not
run any shell, script, test, parser, browser, or bundler command.

1. Inspect at high detail every PNG in:
   `visual/contact_sheets/` — exactly the 31 ordered sheets from
   `pages-001-004.png` through `pages-121-124.png`.
2. Inspect at high detail the following individual triptychs in
   `visual/triptychs/`:
   `page-001.png`, `page-005.png`, `page-053.png`, `page-059.png`,
   `page-074.png`, `page-075.png`, `page-084.png`, `page-085.png`,
   `page-088.png`, `page-098.png`, `page-102.png`, `page-104.png`,
   `page-109.png`, `page-110.png`, `page-111.png`, `page-113.png`,
   `page-115.png`, `page-117.png`, `page-119.png`, `page-121.png`.
3. Open additional individual triptychs only when a contact sheet is visually
   ambiguous. Record every additional page number and the reason.

The stable left-to-right order is:

`original_hybrid | original_pipeline_ocr | raster_hybrid`.

For every contact sheet, confirm that all four source pages are present and
legible enough to compare. Record page-specific signals that matter for later
merge: visibly missing or extra regions, different segmentation of text/art,
overlay-box omissions, cropping, blank output, severe distortion, or a view
that preserves material the other two do not. A difference is a review signal,
not automatically an extraction error.

## Acceptance and receipt

Write only this new receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_full_visual_merge_bundle_visual_only_20260901.md`

The receipt must contain:

- `PASS`, `FAIL`, or `BLOCKED`;
- confirmation that all 31 contact sheets were directly viewed;
- the 20 required individual triptychs and any additional ones viewed;
- concise page-specific cross-view findings, including pages 53 and 109;
- any pages requiring merge-time escalation;
- confirmation that no command and no non-receipt write was performed.

Do not modify the bundle, raw extraction, source, scripts, tests, plans,
canonical context/status, Git, MASTER_EN, MASTER_RU, HTML, PDF, or production.

