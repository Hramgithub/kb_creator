# Independent critic receipt - Viral Step 6A AI merge candidate v2 reconstruction review

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-reconstruction-review-v2`
- Review kind: `implementation`
- Review boundary: reconstruction candidate content/process gate, not release
- Role: independent critic `gpt-5.5`, requested effort `high`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate under review: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, policy effort `medium`
- Assignment state: requested role/profile; platform identity unverified
- Scoped override: none
- Timestamp: `2026-09-01 16:30:03 +03:00`
- Elapsed time: approximately 40 minutes
- Token use: unavailable

## Scope

Read-only review of frozen candidate:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v2`

Assignment packet:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\gpt55_critic_viral_step6a_ai_merge_candidate_v2_reconstruction_review_packet_20260901.md`

Packet SHA-256 verified as:

`14C9A8157E44DBD39B582158C0E934CCF3129F621EEC426BB9CB067E8E5B6807`

Strict write boundary honored. This receipt is the only file written. I did not edit the candidate, decisions, source, raw or postprocess roots, code, tests, plan, context, status, contract, release files, Git, or production files. I did not run MinerU, 371/119/490, builds, verifiers, or downstream stages.

## Candidate Identity

Confirmed:

- source PDF SHA-256: `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`
- source PDF bytes: `20718150`
- candidate files/bytes: `373` / `13141502`
- `RECONSTRUCTED_EN.md` SHA-256: `321B1D10006C9FCA679813AA11B5EC24924E73BEB473E3DD6F4EA73897C54735`
- `MERGE_PROVENANCE.json` SHA-256: `CCEF71DF54A866FB751678D8874823A3D9B84D612166BAE559960DEE2101239F`
- `ASSET_MANIFEST.json` SHA-256: `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9`
- `OVERLAY_SELECTION.json` SHA-256: `B17EF5E777FDDA7E51BADCD3E939B8BFBEC67AFB35FF016FB6AB1B7F7C07353D`

Candidate inventory note:

- direct recompute with PowerShell default/culture sort matches the packet inventory SHA-256 `76C4C8599B9321FFCF0983C548A7A2A94D8B3BC259D93E3EF2343CB58DB471B1`;
- direct recompute with ordinal sort yields `CC8D4D20CDEDC4EE70B2EB1AAE3CF657DF2BC5DCA82A4E1885EF4675A05997A2`;
- therefore the frozen identity is reproducible from this machine, but the audit text's "ordinal" inventory wording is not reproducible as written.

## Files Checked

- `kb_creator/contracts/viral.json`
- `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`
- candidate `RECONSTRUCTED_EN.md`
- candidate `MERGE_PROVENANCE.json`
- candidate `ASSET_MANIFEST.json`
- candidate `OVERLAY_SELECTION.json`
- candidate `pages/page-001.md` through `pages/page-124.md` by count/search, with direct inspection of known risk pages and handout pages
- candidate `decisions/page-001.json` through `decisions/page-124.json` by count/search, with direct inspection of representative boundary/risk pages
- frozen raw root comparison: `20260901_step6a_mineru_three_view_full\comparison\comparison.json`
- handoff packet `gpt55_critic_viral_step6a_ai_merge_candidate_v2_reconstruction_review_packet_20260901.md`
- visual QA receipt `luna_qa_viral_step6a_full_visual_merge_bundle_scratch_preview_correction_20260901.md`
- full three-view QA receipt `luna_qa_viral_step6a_mineru_three_view_full_execution_20260901.md`
- v2 materialization receipt `luna_qa_viral_step6a_ai_merge_materialization_v2_20260901.md`
- orchestrator audit receipt `sol_orchestrator_viral_step6a_ai_merge_candidate_v2_audit_20260901.md`
- plan/context read-only for assignment state and active boundary only

## Gate Results

1. `source_identity`: pass. Contract/source hash and byte count match the retained source, and the full three-view receipt rechecked the same source identity.
2. `page_coverage`: pass. Candidate has 124 page markdown files and 124 decision files; `RECONSTRUCTED_EN.md` has 124 unique source markers with no missing or duplicate pages.
3. `role_partition`: fail, P1. The candidate does not use the contract role partition vocabulary for most pages.
4. `text_ocr_provenance`: pass with residual review risk. `MERGE_PROVENANCE.json` has 124 pages, zero unresolved pages, 1,804 selected block references, and every selected block reference resolves to the frozen raw comparison with matching source page. No CJK/Hangul OCR residue was found in `RECONSTRUCTED_EN.md`.
5. `required_entity_closure`: fail, P1. The handout page range does not prove exactly 39 numbered player handouts.
6. `asset_closure`: pass. `ASSET_MANIFEST.json` lists 121 assets; all 121 files exist and match declared hashes. Across root and page markdown there are 238 image links and zero missing targets.
7. `no_open_blockers`: fail because P1 role partition and required handout closure findings remain open.

## Risk-Class Evidence

- Multi-column reading order: selected-block provenance is present and resolves to raw views; no zero-block pages or malformed selected block records were found.
- Pages 53 and 109 cross-view differences: decisions explicitly record page 53 choosing `original_hybrid` because pipeline OCR isolates only a fragment; page 109 chooses `original_pipeline_ocr` because it preserves the near-full-page composite map. These are acceptable reconstruction decisions on the evidence reviewed.
- Handouts 69-103: page coverage and assets exist, but numbered handout identity is incomplete. Pages 70-86 contain handout-like content without `Handout #` markers; pages 87-103 begin at `Handout #19`.
- Maps 104-110: all seven pages are present with 1/1/2/1/1/1/1 image counts and map headings or map assets. Page 109's composite map is explicitly decided.
- Pregenerated investigators 111-123: all 13 pages are present, including six full-page investigator/template fronts and supporting background/reference assets.
- Cover/back cover: pages 1 and 124 are present; page 124 has `back_cover` role, while page 1 is incorrectly recorded as `front_matter` instead of contract role `cover`.
- Page 121 blank-form signal: decision explicitly records the blank investigator template as intentional, not missing extraction.

## Findings

### P0

None.

### P1

1. Contract role partition is not closed.

   Evidence: `viral.json` requires roles `cover` page 1, `credits` page 2, `front_matter` pages 3-4, `contents` page 5, `scenario_body` pages 6-68, `player_handouts` pages 69-103, `keeper_maps` pages 104-110, `pregenerated_investigators` pages 111-123, and `back_cover` page 124. Candidate provenance/decisions instead record page 1 as `front_matter`, page 2 as `front_matter`, page 5 as `front_matter`, pages 6-16 as `introduction_investigator_material`, pages 17-25 as `one_night_in_perla`, pages 26-68 as `island_main_scenario`, pages 69-103 as `handouts`, and pages 111-123 as `pre_generated_investigators`.

   Impact: the `role_partition` acceptance gate cannot prove the contract's declared page-role partition. This is not a publication-editing concern; it is candidate metadata/provenance mismatch at reconstruction boundary.

   Owning decision pages: `page-001.json`, `page-002.json`, `page-005.json`, `page-006.json` through `page-103.json`, and `page-111.json` through `page-123.json`, unless the orchestrator creates and reviews an explicit role-alias contract before a successor candidate.

2. Required numbered player handout closure is not proven.

   Evidence: within candidate pages 69-103, direct search finds unique handout markers only for `19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39`; missing are `1` through `18`. Pages 70-86 contain handout-like player material such as `The Sight: Player Reference Sheet`, email handouts, maps, and iPad/script content, but they do not declare `Handout #1` through `Handout #18`. Page 87 begins with `Handout #19`.

   Impact: the `required_entity_closure` gate requires exactly 39 numbered player handouts. The candidate has only 21 numbered handout identities in the handout page range, so exact closure cannot be accepted from the candidate evidence.

   Owning decision pages: primarily `page-070.json` through `page-086.json`, with `page-069.json` as the section opener if the successor decision set needs an explicit range/index convention.

### P2

1. Candidate inventory algorithm is ambiguous in the orchestrator audit evidence.

   Evidence: the packet/orchestrator identity `76C4C8599B9321FFCF0983C548A7A2A94D8B3BC259D93E3EF2343CB58DB471B1` is reproduced with PowerShell default/culture sorting. Using the audit-described ordinal sort over the same `373` files and `13141502` bytes produces `CC8D4D20CDEDC4EE70B2EB1AAE3CF657DF2BC5DCA82A4E1885EF4675A05997A2`.

   Impact: this does not by itself prove content mutation, because file count, byte total, and root artifact hashes match. It is a process reproducibility defect that should be corrected in the next audit/freeze wording or inventory implementation.

### P3

1. `MERGE_PROVENANCE.json` does not embed source identity fields directly.

   Evidence: source identity is proven through `viral.json`, the source file, the full three-view receipt, and the candidate audit receipt; the candidate provenance root itself has `raw_comparison` but no direct source hash/page-count fields.

   Impact: acceptable for this read-only review because external bound evidence covers the gate, but a successor candidate would be easier to audit if source identity were embedded in provenance.

## Blockers

The frozen v2 candidate cannot be accepted as `RECONSTRUCTED_EN` while P1 findings remain open. Because the candidate is frozen, fixes must be made through successor decisions/materialization and a fresh candidate root, not by editing v2 in place.

No tool/runtime blocker prevented this review. Sandboxed read commands failed with a managed Windows sandbox backend error, so equivalent read-only checks were rerun with approved elevated execution.

## Recommendation

`reject_reconstruction_candidate`

Rationale: source identity, page coverage, text/OCR traceability, known-risk visual decisions, and asset closure are materially strong, but two required contract gates fail: exact role partition and exactly 39 numbered player handouts. These are reconstruction-boundary defects, not later publication edits.

Next action: create a successor decision set/candidate that either uses the contract role vocabulary exactly or introduces a reviewed role-alias contract, and that explicitly closes `Handout #1` through `Handout #39` within the player-handout range. Then rerun the read-only reconstruction gate review against the successor candidate.

## Changed Files

- Created this receipt only:
  `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\gpt55_critic_viral_step6a_ai_merge_candidate_v2_reconstruction_review_20260901.md`

Any mutation of the frozen candidate after this timestamp invalidates this review receipt and requires a new review.
