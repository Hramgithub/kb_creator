# Innsmouth EN Pipeline Independent Review - 2026-08-29

## Handoff Receipt

- review_kind: release
- verdict: APPROVE
- reviewer role: independent critic, read-only implementation review
- implemented_or_materially_designed_candidate: no
- timestamp: 2026-08-29 01:22:28 +03:00
- elapsed_time: approx 25 minutes active review time in this recovery turn
- token_use: unavailable; current goal tool returned no active goal
- orchestrator_policy_owner: gpt-5.6-sol medium
- assignment_state: completed
- scoped_override: one permitted write only, this immutable review report; no commit or push

## Files Checked

- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- `kb_creator/tests/test_build_innsmouth_reconstructed_en.py`
- `kb_creator/scripts/build_innsmouth_master_en.py`
- `kb_creator/tests/test_build_innsmouth_master_en.py`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/plan.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/context.md`
- `kb_creator/PROJECT_STATUS.md`
- Stage B candidate: `D:/NRI/MinerU/output/innsmouth_full_all_46_20260815/The Innsmouth terror/hybrid_auto/RECONSTRUCTED_EN_package_r2_20260829/`
- Stage C candidate: `D:/NRI/MinerU/output/innsmouth_full_all_46_20260815/The Innsmouth terror/hybrid_auto/MASTER_EN_package_strict_pipeline_candidate_r1_20260829/`
- accepted comparison authority: `kb_creator/inputs/innsmouth/master_en/packet7_user_review_20260826/MASTER_EN.md`

## Evidence

Full real-input test suite:

```powershell
$env:NRI_INNSMOUTH_READING_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_en_reading_candidate.md'
$env:NRI_INNSMOUTH_READING_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\images'
$env:NRI_INNSMOUTH_OCR_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\assets'
$env:NRI_INNSMOUTH_SOURCE_PDF='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_origin.pdf'
$env:NRI_INNSMOUTH_PACKET5B='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\MASTER_EN.md'
$env:NRI_INNSMOUTH_RECONSTRUCTED_EN='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\RECONSTRUCTED_EN_package_r2_20260829\RECONSTRUCTED_EN.md'
python -m pytest kb_creator/tests/test_build_innsmouth_reconstructed_en.py kb_creator/tests/test_build_innsmouth_master_en.py -q -rs
```

Result:

```text
17 passed in 3.95s
```

Control run without env paths:

```text
12 passed, 5 skipped in 0.07s
```

The skipped tests were all real-input gates requiring explicit env paths. They were not accepted as release evidence until rerun with the pinned paths above.

Stage B candidate evidence:

- `RECONSTRUCTED_EN.md`: 138388 bytes
- SHA-256: `72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13`
- QA sidecar SHA-256: `D8103F92052F86945BABA9E964AE805C435C42AFA19C47E4BD8C59E998DEC106`
- QA state: `RECONSTRUCTED_EN_R0_READY_FOR_QA`
- stage contract: `full_source_reconstruction_without_publication_suppression`
- counts: 46 page markers, pages `0..45`, 135 image links/assets, 53 tables, 169 headings, 0 `table-evidence` comments
- excluded pages: none
- missing assets: none
- asset inventory: 135 files, SHA-256 `421467CBDB51E96D6025EE733EB7E67CB61C6C6F15BA52C2F0DAE248801BE66A`
- source candidate SHA-256: `1504A9C71CA995748E4125B7303C0D3064E588ABB226EBB5AB99A5F5763C993C`
- source PDF SHA-256: `5850B26A077390ABFF4A321E754A3709D6148FA4AC7A9F4D63BDBEFF6949B1BB`

Stage C candidate evidence:

- `MASTER_EN.md`: 130028 bytes
- SHA-256: `4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50`
- QA sidecar SHA-256: `A14F134C705821A58BAA437D2F45FDA22F0E27B5E39D978334F9AEED749C7A8E`
- QA state: `MASTER_EN_READER_PACKAGE_READY`
- stage contract: `reader_editorial_projection_only`
- included pages: 43 pages, `0..42`
- excluded pages: `43,44,45`
- publication-base counts: 43 page markers, 38 image links, 51 tables, 155 headings
- final counts: 0 page markers, 0 `table-evidence` comments, 38 image links, 51 tables, 155 headings, 50 anchors, 79 fragments, 0 broken fragments, 33 ordinary `[link]` refs, 3 remaining external page references
- asset inventory: 38 files, SHA-256 `C1A9AB2F89650201C91FA74EAB809E16724D0C608534CFBFAA478AEEBA9CAE3A`
- navigation QA: 34 leaf TOC links, 11 group TOC links, 1 visible Handout-number link, 50 target anchors
- technical comment cleanup: 43 page comments removed, 0 table comments removed from this candidate stream

Accepted comparison authority:

- `MASTER_EN.md`: 133032 bytes
- SHA-256: `41E84FAA5A247434133D2A3B0A40245C4842C4F906E7D5D117B9353DE05C1D18`
- raw accepted counts before cleanup: 43 `mineru-page` comments, 51 `table-evidence` comments, 38 image links, 51 tables, 155 headings, 50 anchors, 79 fragments, 0 broken fragments, 33 ordinary links, 3 external page references
- Stage C nonblank reader lines equal accepted authority after stripping technical comments from the accepted authority: `True`
- Fire Station punctuation-preservation seed exists: `True`
- Handout 1-b visible-number link exists: `True`

Overwrite refusal checks:

```text
ValueError refusing to overwrite existing MASTER_EN package: D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_strict_pipeline_candidate_r1_20260829
ValueError refusing to overwrite an existing RECONSTRUCTED_EN package root
```

Forbidden lineage search:

- no old RU, cleaned EN v6, legacy `unit_id/source_hash` bridge, or historical RU prose source is used by the two implementation scripts or two tests
- docs explicitly record those inputs as excluded

## Severity Findings

No P0/P1/P2 blockers found.

## Non-Blocking Findings

1. The default pytest invocation without env vars gives a partial signal only: `12 passed, 5 skipped`. Release evidence must always use the explicit env-bound command recorded above.
2. `MASTER_EN.qa.json` records `technical_comment_cleanup.table_comments_removed = 0` because Stage B no longer carries `table-evidence` comments. This is consistent with the new stage boundary, but downstream readers should compare final Stage C to the accepted authority only after stripping accepted technical comments.

## Release Gate Verification

- Candidate revision/manifest: candidate is not committed; identity is pinned by candidate file SHA-256 plus QA sidecars above.
- Freeze evidence: source PDF, MinerU reading candidate, Stage B candidate, Stage C candidate, accepted authority, and asset inventories are hash-pinned.
- QA references: real-input pytest suite and candidate sidecars listed above.
- Declared exclusions: Stage C intentionally excludes source pages `43..45`; three external Keeper Rulebook page references remain literal.
- Invalidates on mutation: any mutation to either script, either test, source PDF, reading candidate, Packet5b oracle, Stage B candidate, Stage C candidate, accepted authority, or candidate assets invalidates this review and requires rerunning the full env-bound test command plus candidate QA counters.

## Recommendation

APPROVE the separated EN pipeline implementation for user promotion review.

The reviewed pipeline keeps the intended boundary clean:

`source PDF -> MinerU reading extraction -> RECONSTRUCTED_EN -> MASTER_EN`

Stage B performs source reconstruction with all source pages retained. Stage C performs only explicit reader/editorial projection and produces a reader-facing `MASTER_EN` with no technical comments, exact accepted-reader-line parity, resolved navigation, and pinned assets.

No commit or push was performed by this review.

---

# Current-Run Immutable Receipt Addendum - 2026-08-29 01:27:00 +03:00

## Handoff Receipt

- review_kind: release
- candidate_state: non-frozen Git candidate; hash-pinned generated artifacts reviewed
- verdict: APPROVE
- reviewer role: independent critic, read-only
- implemented_or_materially_designed_candidate: no
- timestamp: 2026-08-29 01:27:00 +03:00
- elapsed_time: approx 12 minutes active current-run review time
- token_use: unavailable; no active goal record exposed by `get_goal`
- orchestrator_policy_owner: gpt-5.6-sol medium
- assignment_state: completed
- scoped_override: permitted write only to this receipt file; no implementation/source/candidate/canonical plan/status/release edits; no commit or push

## Files Checked

- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- `kb_creator/tests/test_build_innsmouth_reconstructed_en.py`
- `kb_creator/scripts/build_innsmouth_master_en.py`
- `kb_creator/tests/test_build_innsmouth_master_en.py`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`
- Stage B artifact: `D:/NRI/MinerU/output/innsmouth_full_all_46_20260815/The Innsmouth terror/hybrid_auto/RECONSTRUCTED_EN_package_r2_20260829/`
- Stage C artifact: `D:/NRI/MinerU/output/innsmouth_full_all_46_20260815/The Innsmouth terror/hybrid_auto/MASTER_EN_package_strict_pipeline_candidate_r1_20260829/`
- Accepted comparison authority: `kb_creator/inputs/innsmouth/master_en/packet7_user_review_20260826/MASTER_EN.md`

## Evidence

- `git status --short --branch`: implementation scripts/tests and boundary audit are uncommitted; canonical `PROJECT_STATUS.md`, `context.md`, and `plan.md` are modified but were not edited by this review.
- Stage B `RECONSTRUCTED_EN.md`: 138388 bytes, SHA-256 `72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13`.
- Stage B `RECONSTRUCTED_EN.qa.json`: SHA-256 `D8103F92052F86945BABA9E964AE805C435C42AFA19C47E4BD8C59E998DEC106`; QA reports 46 page markers, pages `0..45`, 135 image links/assets, 53 tables, 169 headings, 0 excluded pages, 0 missing assets, final asset inventory SHA-256 `421467CBDB51E96D6025EE733EB7E67CB61C6C6F15BA52C2F0DAE248801BE66A`.
- Stage C `MASTER_EN.md`: 130028 bytes, SHA-256 `4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50`.
- Stage C `MASTER_EN.qa.json`: SHA-256 `A14F134C705821A58BAA437D2F45FDA22F0E27B5E39D978334F9AEED749C7A8E`; QA reports 38 image links/assets, 51 tables, 155 headings, 50 anchors, 79 fragments, 0 broken fragments, 33 ordinary page-token links, 0 page markers, and 0 table-evidence comments.
- Artifact directory counts independently checked: Stage B `images` contains 135 files; Stage C `assets` contains 38 files.
- Focused real-input suite command:

```powershell
$env:NRI_INNSMOUTH_READING_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_en_reading_candidate.md'; $env:NRI_INNSMOUTH_READING_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\images'; $env:NRI_INNSMOUTH_OCR_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\assets'; $env:NRI_INNSMOUTH_SOURCE_PDF='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_origin.pdf'; $env:NRI_INNSMOUTH_PACKET5B='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\MASTER_EN.md'; $env:NRI_INNSMOUTH_RECONSTRUCTED_EN='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\RECONSTRUCTED_EN_package_r2_20260829\RECONSTRUCTED_EN.md'; python -m pytest kb_creator\tests\test_build_innsmouth_reconstructed_en.py kb_creator\tests\test_build_innsmouth_master_en.py -q -rs
```

```text
17 passed in 3.95s
```

- Direct `pytest ...` was attempted first and failed because `pytest` was not on PATH; `python -m pytest` succeeded.
- Line-reference evidence: Stage B pins source/PDF/asset inventories in `build_innsmouth_reconstructed_en.py` lines 98-101 and verifies them at lines 144, 183, 227, and 632. Stage B overwrite refusal is at line 597. Stage C pins the accepted reconstructed input and retained asset inventory in `build_innsmouth_master_en.py` lines 19-20 and 66, verifies final counts at line 415, and refuses overwrite at line 488. Accepted nonblank-line parity is asserted in `test_build_innsmouth_master_en.py` lines 72 and 111-114.
- Forbidden-lineage search across the four assigned scripts/tests found no substantive use of `MASTER_RU`, `unit_id`, historical packet builders, or RU bridge inputs; only local variable names containing `source_hash` and comment-cleanup code matched broad search terms.

## Severity Findings

No P0/P1/P2 findings.

## Nonblocking Findings

- The uncommitted/non-frozen candidate is suitable for implementation acceptance evidence, but this receipt is invalidated by any mutation to either builder, either focused test, the Stage B/Stage C artifacts, the pinned source inputs, the Packet 5b oracle, the accepted comparison authority, or referenced assets.
- Because the candidate is non-frozen in Git, this APPROVE is not a user-promotion action and does not transfer orchestration ownership. It supports orchestrator/user promotion review only.
- The suite depends on explicit environment variables for real-input coverage; launcher-only `pytest` is unavailable in this shell.

## Blockers

None.

## Recommendation

APPROVE the separated EN pipeline candidate for implementation acceptance and user promotion review. Do not treat this as automatic promotion, RU synchronization approval, commit approval, or a transfer of orchestration ownership.

---

# Evidence Correction Addendum - 2026-08-29 01:28:26 +03:00

This addendum supersedes the OCR asset path in the prior command examples in this receipt. The canonical real-input OCR recovery asset path is:

```text
D:\NRI\MinerU\output\innsmouth_ocr_control_full_46_20260823\The Innsmouth terror_origin\ocr\images
```

The Packet5b assets path remains a comparison/package oracle path only; it is not the canonical OCR recovery asset input for Stage B production evidence.

Corrected real-input test command:

```powershell
$env:NRI_INNSMOUTH_READING_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_en_reading_candidate.md'; $env:NRI_INNSMOUTH_READING_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\images'; $env:NRI_INNSMOUTH_OCR_ASSETS='D:\NRI\MinerU\output\innsmouth_ocr_control_full_46_20260823\The Innsmouth terror_origin\ocr\images'; $env:NRI_INNSMOUTH_SOURCE_PDF='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_origin.pdf'; $env:NRI_INNSMOUTH_PACKET5B='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\MASTER_EN.md'; $env:NRI_INNSMOUTH_RECONSTRUCTED_EN='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\RECONSTRUCTED_EN_package_r2_20260829\RECONSTRUCTED_EN.md'; python -m pytest kb_creator\tests\test_build_innsmouth_reconstructed_en.py kb_creator\tests\test_build_innsmouth_master_en.py -q -rs
```

Corrected rerun result:

```text
17 passed in 3.78s
```

Final verdict remains APPROVE for implementation acceptance and user promotion review, with the same invalidation rule on any mutation and no transfer of orchestration ownership.
