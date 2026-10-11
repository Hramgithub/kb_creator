# Terra engineering receipt — Viral Step 6A full visual and merge bundle

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-full-visual-merge-bundle`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 24 minutes
- Token use: unavailable

## Scope and result

Implemented generic visual/merge-bundle tooling only. It has not been executed against the raw Viral full root. No Poppler rendering of the 372 real pages, no GPU MinerU, no AI merge, source/candidate/receipt/comparison mutation, Git operation, production output or PDF authoring occurred.

Result: `READY_FOR_LUNA_EXECUTION`.

## Changed files and material identities

- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
  - SHA-256 `3D0458C7D60D8E6A8ADEF58CB49F1041E316A5D05473ADACB1BC120095527F6F`
  - verifies caller-supplied raw receipt, source PDF and comparison JSON hashes before any output write;
  - fails closed on non-empty output roots except exact owned/inventoried resume;
  - renders all selected layout pages at caller DPI with caller-supplied Poppler, makes labeled ordered triptychs and 2x2 contact sheets, creates visual inventories, neutral per-page packets and both source-order/priority-order indexes;
  - preserves every normalized block, bbox, text and asset reference and reports signals rather than selecting content or calling differences errors.
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
  - SHA-256 `CAB10BF2C3BC1330D673AC41B622D1AE9AE7AA817271658D0949FF67F24DF109`
  - compact synthetic coverage of role boundaries, full block/asset/pairwise preservation, transparent priority signals, exact triptych labels, 124-page/31-sheet coverage, safe resume/refusal and path containment.

Bound raw input identities frozen for the Luna command:

- raw receipt: `luna_qa_viral_step6a_mineru_three_view_full_execution_20260901.md`, SHA-256 `20B34FCA18064BBABE0D94BAC49D3475DB74F922E901FBB20A9808EA676154A3`;
- retained source: SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- raw comparison: SHA-256 `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0`.

## Verification evidence

```powershell
python -B -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q
# exit 0: 5 passed in 0.89s

python -B -m py_compile kb_creator/scripts/build_mineru_visual_merge_bundle.py kb_creator/tests/test_mineru_visual_merge_bundle.py
# exit 0

git diff --check -- kb_creator/scripts/build_mineru_visual_merge_bundle.py kb_creator/tests/test_mineru_visual_merge_bundle.py
# exit 0
```

Tests create only synthetic PNG/JSON fixtures under pytest temporary roots. They do not invoke Poppler, MinerU or a real run root.

## Frozen Luna command

Run from `D:\NRI\.worktrees\kb-creator-viral`; this is the first and only authorized command that writes the fresh post-process candidate root.

```powershell
$raw = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full'
$post = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate'
$source = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf'
$receipt = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_mineru_three_view_full_execution_20260901.md'
$pdftoppm = 'C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'

python -B kb_creator/scripts/build_mineru_visual_merge_bundle.py --raw-root $raw --output-root $post --raw-receipt $receipt --raw-receipt-sha256 20B34FCA18064BBABE0D94BAC49D3475DB74F922E901FBB20A9808EA676154A3 --source $source --source-sha256 0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05 --comparison "$raw\comparison\comparison.json" --comparison-sha256 5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0 --pdftoppm $pdftoppm --dpi 110 --expected-pages 124
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

The command creates 372 individual PNGs, 124 triptychs, 31 contact sheets, a complete `visual_manifest.json`, 124 JSON/Markdown packets and both merge indexes. It records exact Poppler commands/version and the recursive generated-file inventory in `evidence/execution.json`. Luna records the shell command/exit and visually inspects the 31 contact sheets; it does not change packets or choose final text.

## Next action

Luna may run the frozen command once against the fresh post-process root, then perform its bounded visual inspection. AI-assisted reconciliation is a later separate step and is not authorized by this engineering receipt.
