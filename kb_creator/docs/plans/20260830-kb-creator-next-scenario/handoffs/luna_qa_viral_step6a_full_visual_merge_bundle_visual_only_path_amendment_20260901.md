# Luna QA amendment — absolute paths for Viral visual-only QA

Date: 2026-09-01  
Parent packet: `luna_qa_viral_step6a_full_visual_merge_bundle_visual_only_packet_20260901.md`  
Status: `AUTHORIZED_PATH_CORRECTION_ONLY`

The first attempt made no write and performed no visual inspection because the
direct image viewer could not resolve repository-relative paths. This amendment
changes only path addressing. All action and write restrictions in the parent
packet remain in force.

## Absolute contact-sheet paths

Base directory:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate\visual\contact_sheets`

Use the direct image-viewing tool on each of these exact existing filenames:

```text
pages-001-004.png
pages-005-008.png
pages-009-012.png
pages-013-016.png
pages-017-020.png
pages-021-024.png
pages-025-028.png
pages-029-032.png
pages-033-036.png
pages-037-040.png
pages-041-044.png
pages-045-048.png
pages-049-052.png
pages-053-056.png
pages-057-060.png
pages-061-064.png
pages-065-068.png
pages-069-072.png
pages-073-076.png
pages-077-080.png
pages-081-084.png
pages-085-088.png
pages-089-092.png
pages-093-096.png
pages-097-100.png
pages-101-104.png
pages-105-108.png
pages-109-112.png
pages-113-116.png
pages-117-120.png
pages-121-124.png
```

## Absolute triptych paths

Base directory:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate\visual\triptychs`

Exact required filenames:

```text
page-001.png
page-005.png
page-053.png
page-059.png
page-074.png
page-075.png
page-084.png
page-085.png
page-088.png
page-098.png
page-102.png
page-104.png
page-109.png
page-110.png
page-111.png
page-113.png
page-115.png
page-117.png
page-119.png
page-121.png
```

For an additional ambiguous page `NNN`, the exact absolute filename pattern is
the triptych base directory plus `\page-NNN.png`.

## Exact receipt write

After direct visual inspection, use the file patch tool (not a shell) to create
only:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_full_visual_merge_bundle_visual_only_20260901.md`

No command, path discovery, test, script, rerun, or other write is permitted.

