# Viral Step 6A - MinerU three-view rescope

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`, high for this architecture step)  
Status: `AUTHORIZED_FOR_TERRA_ENGINEERING`

## Decision

Step 6A is re-centered on reconstruction quality for the retained Viral PDF.
The already completed 371-test verifier suite is optional framework-hardening
evidence. It is not a per-document extraction gate and it must not be rerun
without a material verifier change or a newly identified verifier risk.

The production extraction model is three deliberately different MinerU views
of the same physical book:

1. original PDF through `hybrid-engine`, effort `high`;
2. original PDF through `pipeline`, method `ocr`;
3. image-only PDF through `hybrid-engine`, effort `high`.

The views are compared by source-page identity, `page_idx`, block type, `bbox`,
text and extracted assets. A later AI-assisted merge selects or reconciles the
strongest page/block evidence. Repeating one identical MinerU mode to search
for randomness is out of scope.

## Immutable source

- path:
  `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`;
- bytes: `20,718,150`;
- SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- pages: `124`, PDF 1.7, Letter, unrotated;
- external Yandex location is provenance only and must not become a runtime
  dependency.

The source is read-only. Historical EN/RU or production output is reference
evidence only and may not seed the new masters.

## Existing hybrid salvage - exact current state

Read-only root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate/engine/mineru_hybrid_high/Call_of_Cthulhu_Viral/hybrid_auto`

It contains `209` files:

- `204` JPEG assets (`10,270,968` bytes total);
- `Call_of_Cthulhu_Viral.md`;
- `Call_of_Cthulhu_Viral_content_list.json`;
- `Call_of_Cthulhu_Viral_content_list_v2.json`;
- `Call_of_Cthulhu_Viral_middle.json`;
- `Call_of_Cthulhu_Viral_model.json`.

The v1 content list has `1,840` blocks and complete `page_idx 0..123`
coverage. Its block counts are `1,442 text`, `112 image`, `78 table`,
`67 list`, `27 footer`, `20 header`, and `94 page_number`.

This salvage is useful comparison evidence, but it is not a complete raw view:
it does not retain MinerU's layout/overlay PDF or origin PDF. It therefore may
not be promoted as the final original-hybrid run. Neither this root nor the
protected reconstruction candidate may be changed.

## Bounded sample gate

Before any new full 124-page extraction, build a deterministic 8-page sample
from these one-based source pages, in this exact order:

| Sample page | Source PDF page | Risk represented |
|---:|---:|---|
| 1 | 5 | dense two-column contents; current hybrid classifies 12 table blocks |
| 2 | 12 | dense two-column prose, callout boxes and reading order |
| 3 | 53 | full-page art; current hybrid has one image and zero text |
| 4 | 69 | handout boundary and image-first page |
| 5 | 104 | Keeper map with meaningful embedded labels/text |
| 6 | 109 | composite Keeper map with multiple independent images/labels |
| 7 | 115 | pre-generated investigator sheet; dense table/form semantics |
| 8 | 123 | mixed product images, stylized text and QR code |

Create two sample inputs plus a mapping manifest:

- `viral_sample_vector.pdf`: selected original PDF page objects in the table's
  order, without OCR or content rewriting;
- `viral_sample_raster.pdf`: the same selected pages rendered at `200 DPI` and
  placed one image per Letter page, with no retained text layer;
- `sample_pages.json`: source hash, ordered `sample_page -> source_page`
  mapping, render DPI, dimensions, input/output hashes and tool versions.

Immediately before the first PDF creation command, the PDF skill marker must
be run successfully exactly once for this two-PDF creation operation with
`--expected-output-count 2 --output-format pdf`.

## Fresh working root

The only authorized new run root for this sample is:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_sample`

Required layout:

```text
20260901_step6a_mineru_three_view_sample/
  inputs/
    viral_sample_vector.pdf
    viral_sample_raster.pdf
    sample_pages.json
  runs/
    original_hybrid/
    original_pipeline_ocr/
    raster_hybrid/
  comparison/
  evidence/
```

No predecessor root may be deleted, cleaned, renamed, reused as output, or
modified. Normal runtime cleanup of tool-owned temporary directories remains
part of normal execution and does not require a separate destructive-action
ceremony.

## Required raw artifacts per view

Each view must retain the complete MinerU output, not a curated salvage:

- Markdown/text;
- `content_list.json` and `content_list_v2.json`;
- `middle.json` and any backend model JSON;
- extracted image assets;
- layout/overlay PDF;
- origin PDF when MinerU emits it;
- span PDF when the pipeline backend emits it;
- exact command, exit code, stdout/stderr hashes, runtime/tool versions, input
  hash and output inventory.

Absence of the layout/overlay PDF is a failed sample contract, even when text
and JSON exist.

## Terra engineering ownership

Terra/medium owns reusable preparation and comparison engineering only:

- a deterministic generic sample/full input preparer under
  `kb_creator/scripts/`;
- a three-view normalizer/comparator under `kb_creator/scripts/`;
- minimal focused tests under `kb_creator/tests/`;
- one engineering receipt in this handoff directory.

The tooling must:

1. verify source identity before writing;
2. refuse an existing/non-empty output root unless an explicit safe resume
   contract proves it is the same owned run;
3. produce the vector sample, raster sample and mapping manifest;
4. normalize MinerU v1/v2 content by mapped source page;
5. report per-view page coverage, block counts, text lengths, image references,
   missing/extra blocks and approximate bbox matches;
6. never claim that a difference is automatically an error;
7. emit a compact machine-readable comparison plus a readable Markdown report;
8. support the later full `1..124` run without embedding Viral-only page logic
   in the generic comparison core.

Minimal tests should cover source-hash rejection, page mapping, image-only PDF
having no text layer, manifest round-trip, content-list page normalization and
one representative block/asset diff. Do not generate hundreds of mutation
tests and do not alter the frozen verifier suite.

Terra may not run the GPU extraction itself. Luna/high owns execution after the
scripts and exact commands are frozen.

## Luna execution-only ownership

Luna may only execute the prepared commands and capture raw results. Luna may
not edit code, tests, fixtures, manifests, comparison rules or receipt design;
it may not interpret a failure into a repair.

The sample execution sequence is:

1. prepare and verify both sample PDFs;
2. run original-vector sample with hybrid/high;
3. run original-vector sample with pipeline/OCR;
4. run raster sample with hybrid/high;
5. run the frozen comparator;
6. render all produced overlay PDFs and visually inspect all eight pages for
   each view;
7. return raw evidence and stop.

Any engineering defect returns to Terra. No full 124-page run starts until the
three-view sample has complete artifacts and the mapping/comparator behaves as
specified.

## Acceptance of the sample gate

The gate passes only when:

- both sample PDFs have exactly eight Letter pages in the required order;
- their hashes and source-page mapping are recorded;
- the raster PDF has no usable text layer;
- all three MinerU commands exit `0`;
- every view maps exactly eight pages with no missing `page_idx`;
- every view retains its overlay PDF and structured metadata/text/assets;
- the comparator reports differences without silently discarding any block or
  asset;
- visual QA covers all 24 overlay pages (`8 pages x 3 views`);
- all writes are confined to the fresh sample root plus the assigned receipt.

The sample gate does not decide the final merged truth. It only proves that the
three evidence channels and their comparison transport work before the costly
full-document run.

## Forbidden actions

- no commit or push;
- no mutation of the retained source or predecessor candidate/failure roots;
- no use of historical translation as a new master;
- no manual editing of MinerU output to make the sample pass;
- no 119/490/live verifier rerun as a substitute for extraction work;
- no Luna-authored engineering or repair;
- no production, MASTER_RU, HTML or final PDF work during this sample gate.

