# Viral Step 6A — 124-page AI reconciliation packet

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Contributors: bounded `gpt-5.6-sol`, high  
Status: `AUTHORIZED_FOR_PAGE_DECISIONS`

## Bound inputs

Read-only raw root:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full`

Read-only packet bundle:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate`

Viewer-compatible triptychs for every source page:

`C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-visual-qa\viewer_previews_v1\triptychs\page-NNN.png`

Visual QA receipt SHA-256:

`5985CF1CF5C0EDA79C79D740793B1F2FA1F639DCCA08BF9B0AA46323A83F6157`

It records PASS for 31/31 contact sheets and 20/20 priority triptychs;
merge-time escalation pages are 53 and 109; page 121 is a non-blocking
template/overlay signal.

## Purpose

Reconcile the three deliberately different MinerU results into one faithful
source reconstruction decision per page. This is `RECONSTRUCTED_EN`, not
publication editing or `MASTER_EN`: preserve source content and reading order,
including headings, lists, tables, stat blocks, handouts, maps and pre-generated
investigators. Do not suppress material for reader policy and do not translate.

Historical translations and the old incomplete reconstruction candidate are
not inputs. Do not open or cite them.

## Parallel ownership

Decision root:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions\pages`

Each contributor owns only its non-overlapping decision files and one receipt:

- range A: pages 001–044; receipt
  `handoffs/sol_ai_viral_step6a_pages_001_044_20260901.md`;
- range B: pages 045–086; receipt
  `handoffs/sol_ai_viral_step6a_pages_045_086_20260901.md`;
- range C: pages 087–124; receipt
  `handoffs/sol_ai_viral_step6a_pages_087_124_20260901.md`.

You are not alone in the worktree. Do not revert, reformat or edit any file
outside your exact range and receipt. Do not modify packets, raw outputs,
scripts, tests, plans, context, source, Git, MASTER_EN/RU, HTML, PDF or
production.

## Required review per page

1. Read the exact `merge_packets/pages/page-NNN.json` packet.
2. Directly view the exact 2048px triptych `page-NNN.png` at high detail.
3. Compare all three views in stable order
   `original_hybrid | original_pipeline_ocr | raster_hybrid`.
4. Choose and combine evidence; never select a view mechanically by count.
5. Write one closed decision JSON. Record a genuine unresolved item instead of
   inventing or silently dropping uncertain content.

For source assets, prefer `original_hybrid` when it retains the same original
PDF material at useful quality. Use pipeline/OCR for text it uniquely recovers
and raster hybrid only when it restores material absent or materially damaged
in the original hybrid. These are defaults, not truth claims.

Role guidance:

- narrative/front matter: reconstruct clean English Markdown in visual reading
  order; omit running headers/footers and printed page numbers but retain all
  semantic content;
- tables/stat blocks: preserve row/label/value structure when readable; use a
  selected visual asset when faithful structured text cannot be proven;
- handouts: retain the handout visual and reconstruct its readable text when
  the OCR views support it;
- maps: preserve all distinct map panels/labels as visual assets; do not invent
  unseen map text;
- pre-generated investigators/templates: preserve the complete sheet/page
  visual; add structured text only where the three views make it reliable;
- covers, art-only and back-cover pages: preserve the full-page visual with
  concise non-technical alt text.

Pages 53 and 109 require explicit cross-view reasoning in their decision
`review.notes`. Page 121 must explicitly acknowledge the blank-template signal.

## Decision schema

Write UTF-8 JSON with exactly these keys:

```json
{
  "schema": "kb_creator.mineru_ai_page_decision.v1",
  "source_page": 1,
  "semantic_role": "front_matter",
  "overlay_preference": "original_hybrid",
  "selected_blocks": [
    {"view": "original_hybrid", "raw_index": 0, "purpose": "text"}
  ],
  "markdown": "faithful reconstructed English",
  "assets": [
    {"view": "original_hybrid", "source_path": "images/example.jpg",
     "logical_name": "page-001-cover.jpg", "placement": "full_page"}
  ],
  "unresolved": [],
  "review": {"visual_reviewed": true, "notes": "concise evidence note"}
}
```

Closed values:

- overlay: one of the packet's three view names;
- purpose: `text`, `structure`, `asset`, `visual`;
- placement: `inline`, `full_width`, `full_page`, `handout`, `map`,
  `reference_only`.

Every selected raw index must exist on that exact page/view. Every asset path
must exactly match an asset reference of a selected block from the same view.
Prefix every logical asset name with `page-NNN-` and retain a safe extension so
names cannot collide across ranges.

Reference selected assets in Markdown only through
`{{asset:<logical_name>}}`, for example:

```markdown
![Marco's email handout]({{asset:page-074-marco-email-1.jpg}})
```

Every asset except `reference_only` must have at least one exact placeholder.
Empty Markdown is permitted only for a selected `reference_only` asset. Do not
write source-page markers; the materializer adds them. Do not put absolute
paths, technical merge commentary, HTML or scripts in Markdown.

## Receipt

The one range receipt records page count/domain, all triptychs viewed,
decisions written, asset count, unresolved page list, high-risk pages and any
blocker. Do not paste full page text or raw command transcripts into it. Do not
run MinerU, the materializer, full tests, verifier suites, commit or push.

