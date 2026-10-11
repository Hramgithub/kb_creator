# Luna QA packet — Viral visual-only scratch-preview correction

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Executor: bounded QA (`gpt-5.6-luna`, high)  
Status: `AUTHORIZED_FOR_VISUAL_ONLY_QA`

The immutable bundle PNGs are valid (`PIL verify OK`) but direct `view_image`
cannot access/process their worktree paths. The orchestrator created mechanical
2048-pixel-wide previews only under the session's writable visualization
scratch. The original bundle was not modified. A contact sheet and page-053
triptych from this preview set were successfully opened through `view_image`.

Read-only preview roots:

- contact sheets:
  `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-visual-qa\viewer_previews_v1\contact_sheets`
- required triptychs:
  `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-visual-qa\viewer_previews_v1\triptychs`

Inspect through direct `view_image` only the same 31 contact-sheet filenames and
20 triptych filenames enumerated in the parent inline assignment. Do not run a
command or perform discovery. Stable order remains
`original_hybrid | original_pipeline_ocr | raster_hybrid`.

Preserve the prior BLOCKED receipt. Create only this correction receipt through
the file patch tool:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_full_visual_merge_bundle_scratch_preview_correction_20260901.md`

The receipt must record verdict, `31/31` and `20/20` viewing counts, additional
views if any, page-specific signals including pages 53 and 109, merge-time
escalation pages, and confirmation of no command/non-receipt write.

