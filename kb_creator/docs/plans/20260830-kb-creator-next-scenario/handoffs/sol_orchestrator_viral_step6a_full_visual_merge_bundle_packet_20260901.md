# Viral Step 6A - full visual and AI-merge review bundle

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Status: `AUTHORIZED_FOR_TERRA_ENGINEERING`

## Bound raw extraction

Read-only full root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full`

Machine QA receipt SHA-256:

`20B34FCA18064BBABE0D94BAC49D3475DB74F922E901FBB20A9808EA676154A3`

The three profiles are complete and must not be rerun:

- `original_hybrid`: 124/124, 211 files;
- `original_pipeline_ocr`: 124/124, 112 files;
- `raster_hybrid`: 124/124, 199 files;
- comparator: `pass`, no failures;
- all three layout PDFs: 124 Letter pages;
- referenced asset closure: no missing assets.

This raw root and its receipt are immutable inputs to post-processing.

## Fresh post-process root

All new output belongs under one fresh root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate`

Required layout:

```text
20260901_step6a_mineru_three_view_postprocess_candidate/
  visual/
    original_hybrid/pages/
    original_pipeline_ocr/pages/
    raster_hybrid/pages/
    triptychs/
    contact_sheets/
    visual_manifest.json
  merge_packets/
    pages/page-001.json
    pages/page-001.md
    ... page-124 ...
    merge_index.json
    merge_index.md
  evidence/
```

## Terra engineering ownership

Terra/medium owns one reusable script under `kb_creator/scripts/`, focused
tests under `kb_creator/tests/`, and one new engineering receipt. The script
must accept explicit raw/post-process roots and tool paths; it may not hard-code
Viral, `D:\NRI` or the eight-page sample.

The script must:

1. verify raw receipt/source/comparison identities supplied on the command line
   before writing;
2. refuse a non-empty output root unless a safe exact resume proves the same
   owned bundle;
3. locate the exact three layout PDFs and render all 124 pages of each at
   `110 DPI` with Poppler, retaining 372 individual PNGs;
4. create 124 labeled side-by-side triptychs in stable order
   `original_hybrid | original_pipeline_ocr | raster_hybrid`;
5. create 31 labeled 2x2 contact sheets covering source pages 1..124 exactly
   once in order;
6. record byte/hash/dimension/page/view identities for all visual files;
7. create 124 page merge packets from the comparison JSON and three raw view
   artifacts. Each packet must retain every normalized block, bbox, text and
   asset reference by view, plus per-view type counts, text lengths and
   pairwise block matches/unmatched rows;
8. add source-page semantic role from the canonical ranges: front matter 1-5,
   introduction/investigator material 6-16, One Night in Perla 17-25,
   island/main scenario 26-68, handouts 69-103, Keeper maps 104-110, pre-gens
   111-123, back cover 124;
9. compute transparent review signals, not truth claims: normalized text
   similarity, text-length divergence, block-type divergence, asset-count
   divergence, missing overlay-box candidates and visual-first pages;
10. write a stable merge index sorted by source page and a second priority view
    sorted by review signal strength;
11. never choose final text, drop a block, copy an asset into production or
    claim that a cross-view difference is an error;
12. emit exact commands, tool versions and recursive inventories for later
    Luna execution evidence.

Focused tests must cover page-role boundaries, preservation of every block and
asset reference, stable pairwise packet routing, priority signals, exact
triptych/view labels, 124-page contact-sheet coverage on synthetic images,
safe-root refusal/resume and path containment. Tests must remain compact; no
large mutation matrix is authorized.

## Luna execution-only next gate

After Terra freezes the script/tests/command, Luna/high may only execute it and
capture evidence. Luna then inspects all 31 triptych contact sheets. Every page
must be visually represented. Pages with a strong signal or ambiguous sheet
view must be opened at individual/triptych high detail. Luna records visual
signals for later AI merge and does not edit packets or choose final content.

## Later AI merge

Only after this bundle passes machine and visual QA may the orchestrator assign
page packets for AI-assisted reconciliation into the new MASTER_EN candidate.
The merge must preserve source-page provenance and unresolved alternatives;
historical translations remain reference-only. No MASTER_RU, HTML, final PDF,
production, commit or push is authorized by this packet.

