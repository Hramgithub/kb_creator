# Terra correction receipt — Viral Step 6A full visual and merge bundle

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-full-visual-merge-bundle-correction`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 13 minutes
- Token use: unavailable

## Scope and result

This correction preserves the original visual-bundle receipt immutable and fixes two raw-comparator/schema P1s before Luna execution. No real Poppler, raw root, postprocess output, GPU MinerU, AI merge, Git or canonical-state action occurred.

Result: `READY_FOR_LUNA_EXECUTION`.

## Corrected identities

- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
  - SHA-256 `7B9C7695DFC65D2AD0FD01230AA81C8F9D6CDDFC2990DD822C8F3EE47647B301`
  - Poppler pages now parse `_render-N.png` suffixes numerically and require the exact unique integer sequence `1..expected_pages` before renaming. Lexicographic ordering cannot route page 10 before page 2.
  - `bbox_matches` now route via pair-name view maps and `left_raw_index`/`right_raw_index`; both rows must resolve and agree on one `source_page`, otherwise the bundle fails closed. The original match row is preserved unchanged in exactly that page packet.
  - manifest explicitly defines its inventory as every generated file except the two self-referential records `visual/visual_manifest.json` and `evidence/execution.json`; the latter inventories all other output records.
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
  - SHA-256 `B50B0DDA6D4ED21076AE5BE47C176EA379A80BCAC2AB59C18CAB38D10035C8DE`
  - fixture now uses the actual comparator `bbox_matches` shape without `source_page`, proves the sole match is routed once and never dropped, and covers numeric Poppler sequence handling with `1,2,10,100,124` names plus an exact full `1..124` case.

## Verification evidence

```powershell
python -B -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q
# exit 0: 6 passed in 0.89s

python -B -m py_compile kb_creator/scripts/build_mineru_visual_merge_bundle.py kb_creator/tests/test_mineru_visual_merge_bundle.py
# exit 0

git diff --check -- kb_creator/scripts/build_mineru_visual_merge_bundle.py kb_creator/tests/test_mineru_visual_merge_bundle.py
# exit 0
```

Only synthetic PNG/JSON pytest fixtures were created.

## Frozen Luna command

The command from the preceding receipt is retained with the corrected script identity:

```powershell
$raw = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full'
$post = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate'
$source = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf'
$receipt = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_mineru_three_view_full_execution_20260901.md'
$pdftoppm = 'C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
python -B kb_creator/scripts/build_mineru_visual_merge_bundle.py --raw-root $raw --output-root $post --raw-receipt $receipt --raw-receipt-sha256 20B34FCA18064BBABE0D94BAC49D3475DB74F922E901FBB20A9808EA676154A3 --source $source --source-sha256 0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05 --comparison "$raw\comparison\comparison.json" --comparison-sha256 5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0 --pdftoppm $pdftoppm --dpi 110 --expected-pages 124
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Luna executes it once only against the fresh postprocess root and then reviews contact sheets. Any failure returns to Terra without packet edits or AI decisions.
