# Luna execution receipt — Viral Step 6A AI merge v3 and reconstruction finalizer

- Result: **EXECUTION PASS** (bounded frozen-command execution only; not acceptance or release)
- Goal: `20260830-kb-creator-next-scenario`
- Assignment state: completed; downstream visual QA and review remain with the orchestrator.
- Scope: exactly the two packet-authorized commands in `D:\NRI\.worktrees\kb-creator-viral`; two fresh output roots and this receipt only.
- Role: `gpt-5.6-luna`, bounded frozen-command execution / QA capture, high reasoning effort.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`.
- Scoped override: none; requested packet profile was followed, platform identity unverified.
- Packet SHA-256: `B87BF6DBA4978F8FE9E447AEC891694FADE5A5A1B23CFC94AB76BA240E43C4BD`.
- Timestamp: `2026-09-01T17:03:16+03:00` (Europe/Moscow).
- Elapsed time: command 1 approximately 1.72 s; command 2 approximately 4.67 s; post-command read-only checks approximately 20 s.
- Token use: unavailable.

## Exact commands

Working directory: `D:\NRI\.worktrees\kb-creator-viral`

1. `python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v3\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v3`

   - Native exit code: **0**; elapsed approximately **1.72 s**.
   - Native stdout: `{"status": "candidate_ready_for_reconstruction_qa", "pages": 124, "assets": 121, "unique_asset_bytes": 121}`
   - Native stderr: **empty**.

2. `python -B kb_creator\scripts\finalize_mineru_reconstruction.py --contract kb_creator\contracts\viral.json --source kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --candidate-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v3 --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_reconstructed_en_package_v3`

   - Native exit code: **0**; elapsed approximately **4.67 s**.
   - Native stdout: `{"status": "candidate_ready_for_reconstruction_review", "pages": 124, "overlay_pages": 124}`
   - Native stderr: **empty**.

## Output identities and evidence

- Candidate root: `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v3`
  - 373 files; 13,142,501 bytes.
  - Ordinal trailing-LF inventory SHA-256: `B0D74C6560648454DD3B12E02446969A11851BD722B41F0222FFA9DE32121EA1`.
  - `RECONSTRUCTED_EN.md`: 346,580 bytes, `5D28F097708CB9D58A5A0D4C72CC93E9985FC7CDB00C22EFDB0A22C9931B79ED`.
  - `MERGE_PROVENANCE.json`: 231,701 bytes, `A99FE5C16A149621142F28DC8FA638FAAF4DCA4345F7DAE9624EC270B98C2870`.
  - `ASSET_MANIFEST.json`: 50,739 bytes, `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9`.
  - `OVERLAY_SELECTION.json`: 10,992 bytes, `B17EF5E777FDDA7E51BADCD3E939B8BFBEC67AFB35FF016FB6AB1B7F7C07353D`.
- Package root: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3`
  - 377 files; 41,068,701 bytes.
  - Ordinal trailing-LF inventory SHA-256: `46E61F5DB9853E795C636147C63230936221F056DE1A9C25B19A4C8DEAEA215E`.
  - `RECONSTRUCTION_PROVENANCE.json`: 228,782 bytes, `7872946148455CA277E2639C0E9D19894BD7BF9ACEC28E4AD971A11111B10DA7`.
  - `RECONSTRUCTION_QA.json`: 643 bytes, `F88E0474D19982B0634AE66DB7A10F865EA3EDB1DB491AF55E6E3CC5F03EDCC0`.
  - `RECONSTRUCTION_QA.md`: 206 bytes, `162039F13D25D3E25B7D2C60B20845F615425AAE95CF1A8F869025C586195851`.
  - `SELECTED_OVERLAY.pdf`: 27,696,569 bytes, `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`.

## Read-only verification

- Package candidate-derived files: 373/373 present and byte-identical; mismatches 0.
- `SELECTED_OVERLAY.pdf`: 124 pages; media box `(0, 0, 612, 792)` for all pages; rotation domain `{0}`.
- `RECONSTRUCTION_QA.json`: status `candidate_ready_for_reconstruction_review`; all seven gate rows exactly `status=pass`, `errors=[]`: `source_identity`, `page_coverage`, `role_partition`, `text_ocr_provenance`, `required_entity_closure`, `asset_closure`, `no_open_blockers`.
- `RECONSTRUCTION_PROVENANCE.json`: source binding is 124 pages / 20,718,150 bytes / SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`; page records 124; physical handout labels 41; unique numeric ordinals 1..39.
- Both roots have exact packet-expected top-level entries; no extra output roots inside either root.
- Nonempty unresolved JSON lists: none in either root. Placeholder-token files (`TODO`, `TBD`, `PLACEHOLDER`, `[[...]]`): none in either root.
- Reparse points: none. Finalizer/materializer stage residues matching both fresh roots: none.
- PDF create marker: not invoked during this execution; no repeat.

## Files checked and preservation

- Checked only the assigned packet, its two fresh output roots, generated QA/provenance artifacts, and the source binding reported by the finalizer.
- No edits to decisions, scripts, tests, source, contract, raw/bundle roots, prior candidates/receipts, canonical plan/context/status, production, or Git.
- No MinerU, tests, verifier, 371/119/490 run, visual interpretation, repair, cleanup, acceptance, promotion, publication, or commit was performed.

## Blockers and next action

- Blockers observed: none for the two frozen commands or deterministic identity checks.
- Next action: orchestrator performs the separately assigned machine audit and visual reconstruction QA; this receipt does not approve acceptance or release.

