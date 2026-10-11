# Terra engineering packet — Viral Step 6A AI-merge materializer

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Engineer: `gpt-5.6-terra`, medium  
Status: `AUTHORIZED_FOR_ENGINEERING`

## Goal

Build the small reusable materializer needed after human/AI page decisions.
It does not decide content, run MinerU, or create the real Viral candidate.

You are not alone in the worktree. Preserve all current changes, do not revert
or reformat files owned by others, and accommodate the existing bundle schema.

## Exclusive write ownership

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_ai_merge_materializer_20260901.md`

All other paths are read-only. No real candidate output is authorized.

## Inputs and CLI

Provide an explicit CLI with:

- `--bundle-root`: the visual/merge packet bundle containing exactly 124
  `merge_packets/pages/page-NNN.json` files and `merge_index.json`;
- `--raw-root`: the bound three-view raw root whose comparison JSON and asset
  directories are referenced by the bundle;
- `--decisions-root`: exactly 124 AI decision JSON files;
- `--output-root`: absent or empty owned destination.

No hard-coded scenario id, `D:\NRI`, page count, or semantic ranges. Expected
page domain and view names come from the merge index/packets.

## Decision schema

Each `page-NNN.json` decision is closed and uses:

```json
{
  "schema": "kb_creator.mineru_ai_page_decision.v1",
  "source_page": 1,
  "semantic_role": "front_matter",
  "overlay_preference": "original_hybrid",
  "selected_blocks": [
    {"view": "original_hybrid", "raw_index": 0,
     "purpose": "text"}
  ],
  "markdown": "reader-neutral reconstructed English for this source page",
  "assets": [
    {"view": "original_hybrid", "source_path": "images/example.jpg",
     "logical_name": "page-001-cover.jpg", "placement": "full_page"}
  ],
  "unresolved": [],
  "review": {"visual_reviewed": true, "notes": ""}
}
```

Closed values:

- `overlay_preference`: one of the packet's three views;
- selected-block purpose: `text`, `structure`, `asset`, or `visual`;
- asset placement: `inline`, `full_width`, `full_page`, `handout`, `map`, or
  `reference_only`;
- `logical_name`: safe basename only, unique case-insensitively across the
  candidate;
- `unresolved`: list of non-empty strings;
- `review.visual_reviewed`: boolean; `review.notes`: string.

Unknown keys fail. Markdown must be a string, must not contain generated page
markers, absolute paths, technical merge commentary, or HTML/script content.
Empty Markdown is permitted only when at least one selected asset has
`full_page`, `handout`, `map`, or `reference_only` placement.

## Required validation

1. Exact page coverage with no missing, duplicate, or out-of-domain page.
2. Decision source page and semantic role match the bound packet.
3. Every selected `(view, raw_index)` exists exactly once in that page/view.
4. Every selected asset is an exact asset reference of a selected block from
   the same view and resolves beneath the bound raw view artifact directory.
5. Reject absolute/traversal/symlink paths and output-root escape.
6. Refuse a non-empty output root; publish by same-parent staging and atomic
   no-replace rename only after all validation succeeds.
7. Copy selected assets once, verify byte hash, and deduplicate identical bytes
   without silently merging different logical names.
8. Preserve decision JSON bytes in the output and record source packet,
   comparison, selected-block, asset and unresolved provenance.

## Output

```text
output-root/
  RECONSTRUCTED_EN.md
  pages/page-001.md ... page-NNN.md
  decisions/page-001.json ... page-NNN.json
  assets/
  MERGE_PROVENANCE.json
  ASSET_MANIFEST.json
  OVERLAY_SELECTION.json
```

The materializer adds stable `<!-- source-page-NNN -->` markers to page files
and the combined Markdown, concatenates in source-page order, records exact
counts/hashes, and reports `candidate_needs_review` when any decision has an
unresolved item; otherwise `candidate_ready_for_reconstruction_qa`. It does not
claim MASTER_EN acceptance and does not create a merged overlay PDF.

## Focused tests

Use compact temporary synthetic fixtures only. Cover happy-path assembly,
ordering/page markers, selected-block identity, asset closure/deduplication,
closed schema/path containment, empty-markdown visual page, unresolved-state
propagation, and no-replace output publication. No mutation matrix or full
repository suite is authorized.

Run only the focused test file and `py_compile`. Record exact commands, results,
changed files and SHA-256 identities in the receipt. Do not commit or push.

