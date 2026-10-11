# Innsmouth EN Pipeline R2 Independent Review - 2026-08-29

## Handoff Receipt

- review_kind: release
- candidate_state: non-frozen Git candidate; r2 generated package is hash-pinned
- verdict: REMEDIATION_REQUIRED
- reviewer role: independent critic, read-only
- implemented_or_materially_designed_candidate: no
- timestamp: 2026-08-29 01:38:24 +03:00
- elapsed_time: approx 14 minutes active r2 review time
- token_use: unavailable; no active goal record exposed by `get_goal`
- orchestrator_policy_owner: gpt-5.6-sol medium
- assignment_state: completed_with_remediation_required
- scoped_override: permitted write only to this r2 review receipt; no implementation/source/candidate/canonical plan/status/release edits; no commit or push

## Files Checked

- `kb_creator/scripts/build_innsmouth_master_en.py`
- `kb_creator/tests/test_build_innsmouth_master_en.py`
- `kb_creator/scripts/freeze_innsmouth_master_en_repo_input.py`
- `kb_creator/tests/test_freeze_innsmouth_master_en_repo_input.py`
- `kb_creator/scripts/build_innsmouth_reconstructed_en.py`
- `kb_creator/tests/test_build_innsmouth_reconstructed_en.py`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/plan.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/context.md`
- `kb_creator/PROJECT_STATUS.md`
- Stage C r2 artifact: `D:/NRI/MinerU/output/innsmouth_full_all_46_20260815/The Innsmouth terror/hybrid_auto/MASTER_EN_package_strict_pipeline_candidate_r2_20260829/`
- Stage B artifact consumed by Stage C: `D:/NRI/MinerU/output/innsmouth_full_all_46_20260815/The Innsmouth terror/hybrid_auto/RECONSTRUCTED_EN_package_r2_20260829/`
- Accepted comparison authority: `kb_creator/inputs/innsmouth/master_en/packet7_user_review_20260826/MASTER_EN.md`

## Blockers

P1 - `freeze_innsmouth_master_en_repo_input.py` does not hard-compare the candidate `MASTER_EN.qa.json` `input` provenance against canonical Stage B identities inside the freeze gate.

Evidence: `inspect_candidate()` validates the caller-supplied expected MASTER/QA hashes and rejects absolute paths, then checks only logical Stage B paths at lines 76-80 before copying `input_identity` into the report at line 97. The acceptance manifest then embeds that same `source_reconstructed_en` payload at line 112. The tests assert only `source_reconstructed_en.asset_inventory.asset_count == 135` at `test_freeze_innsmouth_master_en_repo_input.py:54`; they do not prove rejection of wrong Stage B Markdown SHA, Stage B QA SHA, Stage B byte counts, or Stage B 135-asset inventory SHA in `qa.input`.

Impact: the actual r2 candidate QA currently contains the correct Stage B identities, and the Stage C builder independently verifies Stage B Markdown/QA/assets before package creation. However, the freeze/promotion gate still trusts a passed expected QA hash as sufficient provenance authority. A tampered candidate QA with wrong `qa.input` provenance could be accepted if the caller supplied its matching expected QA hash and the remaining package checks passed. That can produce a false acceptance manifest, so release-gate acceptance is not clean.

Required remediation: in `inspect_candidate()`, compare `qa.input.markdown.byte_count`, `qa.input.markdown.sha256`, `qa.input.qa.byte_count`, `qa.input.qa.sha256`, `qa.input.asset_inventory.asset_count`, and `qa.input.asset_inventory.inventory_sha256` to the canonical Stage B constants used by `build_innsmouth_master_en.py`, and add negative tests for each mismatch.

## Nonblocking Findings

- The r2 `MASTER_EN.md` reader artifact itself matches the prior reviewed content identity and all navigation/content invariants.
- The r2 QA sidecar contains no device-specific absolute path matches by direct `Select-String` scan.
- Direct `pytest` is unavailable as a shell command in this environment; `python -m pytest` is available and was used.
- The candidate is uncommitted and unpushed, so this review cannot be used as a frozen Git revision receipt. It can only review the hash-pinned non-frozen artifact state.

## Evidence

Worktree status:

```text
## codex/innsmouth-master-en-main...origin/codex/innsmouth-master-en-main
 M kb_creator/PROJECT_STATUS.md
 M kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/context.md
 M kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/plan.md
?? kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/CRITIC_EN_PIPELINE_REVIEW_20260829.md
?? kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md
?? kb_creator/scripts/build_innsmouth_master_en.py
?? kb_creator/scripts/build_innsmouth_reconstructed_en.py
?? kb_creator/scripts/freeze_innsmouth_master_en_repo_input.py
?? kb_creator/tests/test_build_innsmouth_master_en.py
?? kb_creator/tests/test_build_innsmouth_reconstructed_en.py
?? kb_creator/tests/test_freeze_innsmouth_master_en_repo_input.py
```

No actual repository promotion was found:

```text
Test-Path kb_creator\inputs\innsmouth\master_en\accepted_20260829 -> False
Test-Path kb_creator\inputs\innsmouth\master_en\accepted_20260829\MASTER_EN.acceptance.json -> False
```

Stage C r2 candidate:

- `MASTER_EN.md`: `130028` bytes, SHA-256 `4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50`
- `MASTER_EN.qa.json`: `14362` bytes, SHA-256 `CED340C73D98B889269C915359FEDE44866CA04ED9216474C366BAE8284149CF`
- `assets/`: 38 files
- QA state: `MASTER_EN_READER_PACKAGE_READY`
- QA input currently records Stage B Markdown `138388` bytes / `72cf965df27c28d5d3927867e0a08c8655f5a7a117e108716fa84521649a8f13`, Stage B QA `74886` bytes / `d8103f92052f86945baba9e964ae805c435c42afa19c47e4bd8c59e998dec106`, and Stage B asset inventory `135` / `421467cbdb51e96d6025ee733eb7e67cb61c6c6f15ba52c2f0dae248801be66a`.
- Final counts: 38 image links, 51 tables, 155 headings, 50 anchors, 79 fragments, 0 broken fragments, 33 ordinary page-token links, 3 external page references, 0 page markers, 0 table-evidence comments.

Stage C builder evidence:

- `build_innsmouth_master_en.py:20` pins Stage B Markdown SHA-256.
- `build_innsmouth_master_en.py:22` pins Stage B QA SHA-256.
- `build_innsmouth_master_en.py:224` checks Stage B Markdown bytes/hash.
- `build_innsmouth_master_en.py:237` checks Stage B QA bytes/hash.
- `build_innsmouth_master_en.py:250-253` checks the 135-asset reconstructed inventory and matching Stage B QA inventory.
- `build_innsmouth_master_en.py:415` enforces final MASTER_EN navigation/content counts.

Canonical real-input suite:

```powershell
$env:NRI_INNSMOUTH_READING_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_en_reading_candidate.md'; $env:NRI_INNSMOUTH_READING_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\images'; $env:NRI_INNSMOUTH_OCR_ASSETS='D:\NRI\MinerU\output\innsmouth_ocr_control_full_46_20260823\The Innsmouth terror_origin\ocr\images'; $env:NRI_INNSMOUTH_SOURCE_PDF='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_origin.pdf'; $env:NRI_INNSMOUTH_PACKET5B='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\MASTER_EN.md'; $env:NRI_INNSMOUTH_RECONSTRUCTED_EN='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\RECONSTRUCTED_EN_package_r2_20260829\RECONSTRUCTED_EN.md'; $env:NRI_INNSMOUTH_MASTER_EN_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_strict_pipeline_candidate_r2_20260829'; python -m pytest kb_creator\tests\test_build_innsmouth_reconstructed_en.py kb_creator\tests\test_build_innsmouth_master_en.py kb_creator\tests\test_freeze_innsmouth_master_en_repo_input.py -q -rs
```

```text
21 passed in 4.14s
```

Freeze preflight command:

```powershell
python kb_creator\scripts\freeze_innsmouth_master_en_repo_input.py --preflight --candidate "D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_strict_pipeline_candidate_r2_20260829" --expected-master-sha256 4A3DDE7AC0EA7A6815AE7FE3CAD38062CC828CF5880D549026E99D5496389A50 --expected-qa-sha256 CED340C73D98B889269C915359FEDE44866CA04ED9216474C366BAE8284149CF
```

```text
INNSMOUTH_MASTER_EN_PROMOTION_PREFLIGHT_OK
```

Forbidden lineage search across the assigned scripts/tests found no substantive use of `MASTER_RU`, historical packet builders, old cleaned EN, or the `unit_id/source_hash` bridge. Only local variable names containing `source_hash` in the Stage B builder matched the broad search.

## Release Gate Verification

- Candidate revision or manifest: no committed revision; reviewed r2 by file/package SHA-256 identities above.
- Freeze evidence: Stage B and Stage C artifacts are hash-pinned, and Stage C generation now verifies Stage B Markdown, QA and 135 assets. Freeze/promotion evidence is incomplete because the freeze gate does not independently hard-compare `qa.input` to canonical Stage B identities.
- QA references: r2 `MASTER_EN.qa.json`; `MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md`; canonical real-input suite `21 passed in 4.14s`; preflight command output above.
- Declared exclusions: Stage C excludes source pages `43..45`; three Keeper Rulebook external page references remain literal; RU sync, HTML, PDF, commit and push are out of scope.
- Invalidation on mutation: any mutation to reviewed scripts/tests, Stage B package, Stage C r2 package, pinned source/MinerU/OCR inputs, Packet 5b oracle, accepted comparison authority, candidate assets, or freeze manifest behavior invalidates this receipt and requires fresh tests plus independent review.

## Recommendation

REMEDIATION_REQUIRED.

The r2 artifact content and Stage C build path are acceptable on the evidence reviewed, and the canonical suite passes. Do not user-promote or freeze the candidate until the freeze gate hard-compares `qa.input` against canonical Stage B Markdown, QA and 135-asset identities and adds negative tests for mismatched provenance. This review supports remediation planning only; it is not implementation acceptance, user promotion, RU synchronization approval, commit approval, push approval, or orchestration ownership transfer.

---

# P1 Closure Addendum - 2026-08-29 01:42:47 +03:00

## Handoff Receipt

- review_kind: release
- closure_scope: P1 freeze-gate provenance remediation only
- verdict: APPROVE
- reviewer role: independent critic, read-only
- implemented_or_materially_designed_candidate: no
- timestamp: 2026-08-29 01:42:47 +03:00
- elapsed_time: approx 6 minutes active closure review time
- token_use: unavailable; no active goal record exposed by `get_goal`
- orchestrator_policy_owner: gpt-5.6-sol medium
- assignment_state: completed
- scoped_override: appended this closure addendum only; no implementation/source/candidate/canonical plan/status/release edits; no commit or push

## Closure Evidence

The prior P1 is closed. `freeze_innsmouth_master_en_repo_input.py` now defines `EXPECTED_SOURCE_RECONSTRUCTED_EN` from the canonical Stage B constants and full reconstructed asset inventory:

- Stage B Markdown path `RECONSTRUCTED_EN.md`, byte count `138388`, SHA-256 from `master.RECONSTRUCTED_EN_SHA256`;
- Stage B QA path `RECONSTRUCTED_EN.qa.json`, byte count `74886`, SHA-256 from `master.RECONSTRUCTED_EN_QA_SHA256`;
- Stage B asset inventory count `135`, SHA-256 from `master.reconstructed.FINAL_ASSET_INVENTORY_SHA256`.

`verify_source_reconstructed_identity()` now rejects any `qa.input` value not exactly equal to that canonical object with `MASTER_EN QA canonical Stage B provenance mismatch`. `inspect_candidate()` calls it before returning `source_reconstructed_en` and before manifest creation can copy provenance into `MASTER_EN.acceptance.json`.

Test coverage now includes:

- `test_rejects_tampered_stage_b_provenance`, which mutates the Stage B asset inventory hash and expects rejection;
- `test_accepts_only_exact_stage_b_provenance`, which accepts only the exact canonical object;
- the real candidate preflight and temporary promotion/verify rehearsal.

Canonical closure suite:

```powershell
$env:NRI_INNSMOUTH_READING_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_en_reading_candidate.md'; $env:NRI_INNSMOUTH_READING_ASSETS='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\images'; $env:NRI_INNSMOUTH_OCR_ASSETS='D:\NRI\MinerU\output\innsmouth_ocr_control_full_46_20260823\The Innsmouth terror_origin\ocr\images'; $env:NRI_INNSMOUTH_SOURCE_PDF='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\The Innsmouth terror_origin.pdf'; $env:NRI_INNSMOUTH_PACKET5B='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_packet5_u11b_residual_nonsemantic_art_and_handout_reflow_candidate_20260825\MASTER_EN.md'; $env:NRI_INNSMOUTH_RECONSTRUCTED_EN='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\RECONSTRUCTED_EN_package_r2_20260829\RECONSTRUCTED_EN.md'; $env:NRI_INNSMOUTH_MASTER_EN_CANDIDATE='D:\NRI\MinerU\output\innsmouth_full_all_46_20260815\The Innsmouth terror\hybrid_auto\MASTER_EN_package_strict_pipeline_candidate_r2_20260829'; python -m pytest kb_creator\tests\test_build_innsmouth_reconstructed_en.py kb_creator\tests\test_build_innsmouth_master_en.py kb_creator\tests\test_freeze_innsmouth_master_en_repo_input.py -q -rs
```

```text
23 passed in 4.14s
```

No actual repository promotion was found after the suite:

```text
Test-Path kb_creator\inputs\innsmouth\master_en\accepted_20260829 -> False
Test-Path kb_creator\inputs\innsmouth\master_en\accepted_20260829\MASTER_EN.acceptance.json -> False
```

Final `git status --short --branch` still shows the same dirty/untracked review scope and no commit or push evidence:

```text
## codex/innsmouth-master-en-main...origin/codex/innsmouth-master-en-main
 M kb_creator/PROJECT_STATUS.md
 M kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/context.md
 M kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/plan.md
?? kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/CRITIC_EN_PIPELINE_R2_REVIEW_20260829.md
?? kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/CRITIC_EN_PIPELINE_REVIEW_20260829.md
?? kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/MASTER_EN_PIPELINE_BOUNDARY_AUDIT_20260829.md
?? kb_creator/scripts/build_innsmouth_master_en.py
?? kb_creator/scripts/build_innsmouth_reconstructed_en.py
?? kb_creator/scripts/freeze_innsmouth_master_en_repo_input.py
?? kb_creator/tests/test_build_innsmouth_master_en.py
?? kb_creator/tests/test_build_innsmouth_reconstructed_en.py
?? kb_creator/tests/test_freeze_innsmouth_master_en_repo_input.py
```

## Remaining Findings

No P0/P1/P2 findings remain in the reviewed closure scope.

This closure approves the r2 EN pipeline implementation and freeze-gate remediation for implementation acceptance and user promotion review only. It is not automatic user promotion, RU synchronization approval, commit approval, push approval, or orchestration ownership transfer.

Any mutation to the reviewed scripts/tests, Stage B package, Stage C r2 package, pinned source/MinerU/OCR inputs, Packet 5b oracle, accepted comparison authority, candidate assets, or freeze manifest behavior invalidates this closure and requires fresh tests plus independent review.
