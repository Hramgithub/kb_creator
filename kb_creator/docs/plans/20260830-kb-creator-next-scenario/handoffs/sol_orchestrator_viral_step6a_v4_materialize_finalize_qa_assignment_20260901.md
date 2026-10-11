# Viral Step 6A v4 materialize/finalize QA assignment

Date: 2026-09-01  
Owner: bounded `gpt-5.6-luna` QA execution at `high`  
Working directory: `D:\NRI\.worktrees\kb-creator-viral`

## Purpose

Execute the already frozen generic materializer and finalizer once each against
the reviewed 124-page v4 decisions. This is execution and evidence capture only.
It contains no engineering, content design, source interpretation or repair.

No MinerU/OCR/AI extraction and no 371/119/490 mutation-matrix run is allowed.

## Frozen inputs

| Input | Bytes / identity |
|---|---|
| `kb_creator/scripts/materialize_mineru_ai_merge.py` | 16,423 / SHA-256 `D632FD2203C1CB68AD01DBD369E7FD530146A5D423F786FDEB64848F0F331076` |
| `kb_creator/scripts/finalize_mineru_reconstruction.py` | 19,997 / SHA-256 `E943D82F41651A6CBEDDAE7D199B0B755133EFB304D14DD2E2B1770FAF39C367` |
| `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py` | 10,560 / SHA-256 `E5BDE87435D19EAD63FB4D5BAC2CCE1E4FE139B00B97FA6110CF5880EA5D0A08` |
| `kb_creator/contracts/viral.json` | 4,582 / SHA-256 `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf` | 20,718,150 / SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| v4 decisions `.../20260901_step6a_ai_merge_decisions_v4/pages` | 124 JSON; inventory rows `name<TAB>bytes<TAB>SHA256<LF>` are 10,401 bytes / SHA-256 `0213B2F046A76BE0BAF80F83FEF9D3AFC5180F61152DDCCEFCA8098E5F36C763` |
| v4 reviewed fidelity allowlist | 417 bytes / SHA-256 `D84CB591732F2396DAE65E0B4A2C749E1E7E6EDC492E9144026013B8CEB649BF` |
| body correction receipt | SHA-256 `E04FD7310A4B30D901CDB648890E4AE3488ED2FBFE5E5EFF48BF7A3F9102D48D` |
| appendix correction receipt | SHA-256 `D783114736A20DD2589B52E4666B0CCB2377FD4E91D41DEF8B5C9A1D2134FDA2` |

The orchestrator has re-proved that v4 differs from v3 on exactly
`{20,34,42,44,45,49,50,55,62,65,66,67,69,74,75,80}` and that the other
108 page decisions are byte-identical. The focused fidelity audit passes all
124 pages with zero errors and the sole reviewed p62 `ý -> ÿ` count-7 row.

## Write scope

The two output roots must be absent before execution and are the only material
write roots:

- `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v4`
- `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`

The only additional write is the final receipt:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_reconstructed_en_package_v4_execution_20260901.md`

If either output root exists, stop `BLOCKED` without deleting, cleaning or
overwriting it. Do not write a separate raw transcript. Do not modify decisions,
allowlist, source, frozen three-view/bundle roots, v1-v3 evidence, code, tests,
contract, plan/context, p124 publication assets, accepted/production roots or Git.

## Exact execution sequence

1. Recheck both output roots are absent and recheck every frozen byte/hash above.
2. Run once:

   `python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v4\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v4`

3. Only after exit 0, run once:

   `python -B kb_creator\scripts\finalize_mineru_reconstruction.py --contract kb_creator\contracts\viral.json --source kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --candidate-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v4 --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_reconstructed_en_package_v4`

4. Run the focused audit without an output write and capture its machine result:

   `python -B kb_creator\scripts\audit_mineru_ai_merge_fidelity.py --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v4\pages --merge-packets-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate\merge_packets --reviewed-allowlist kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_fidelity_v4_allowlist.json`

5. Run only the three focused suites, with bytecode and pytest cache disabled:

   `python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_materialize_mineru_ai_merge.py kb_creator/tests/test_finalize_mineru_reconstruction.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`

## Required read-only QA

- Both commands exit 0 and stdout status values match the v3 command contract.
- Candidate has 124 page files/markers, 124 decision copies and 121 closed assets.
- Every candidate decision is byte-identical to its reviewed v4 input.
- Package inherits every candidate path byte-identically and adds only the
  finalizer-declared reconstruction outputs.
- `RECONSTRUCTED_EN.md` has 124 ordered source markers and contains the exact
  repaired tokens/tables/statblocks/titles/note from both correction receipts.
- Source/contract/provenance identities and all seven reconstruction gates pass.
- `SELECTED_OVERLAY.pdf` is 124 Letter pages, rotation 0, and byte-identical to
  v3 overlay SHA-256
  `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`.
- Record deterministic portable inventory byte counts and SHA-256 for candidate
  and package, plus identities of `RECONSTRUCTED_EN.md`, overlay, manifests,
  provenance and QA files.
- Confirm no p124 publication asset was created and no out-of-scope file changed.

## Receipt result

Use `PASS`, `FAIL` or `BLOCKED`. Include exact commands, native exits/stdout/stderr,
focused-test count, inventories/hashes, the checks above, changed files and any
blocker. Do not repair a failing output; report it for engineering ownership.

