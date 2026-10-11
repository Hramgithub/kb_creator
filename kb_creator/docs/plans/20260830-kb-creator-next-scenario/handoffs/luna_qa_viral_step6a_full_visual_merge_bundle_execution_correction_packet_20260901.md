# Luna correction packet - full visual/merge bundle execution

Date: 2026-09-01  
Status: `AUTHORIZED`

The immutable pre-execution BLOCKED receipt remains at SHA-256
`38A59ED438460C79340C345015FAAD1369A5BBE5FC26A9E5310591950CC8C7BA`.
It proves the fresh output root was still absent and that neither bundler,
Poppler nor tests had run. Its failure was an ad hoc PowerShell preflight parse
error before the frozen operation, not a material/tool failure.

Do not run another ad hoc preflight. The bundler itself verifies every bound
hash before its first output write. From the successor worktree, execute this
literal command once with escalated local shell permission and no pipe,
redirection, variables or command construction:

```powershell
python -B kb_creator/scripts/build_mineru_visual_merge_bundle.py --raw-root D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --output-root D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-receipt D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_mineru_three_view_full_execution_20260901.md --raw-receipt-sha256 20B34FCA18064BBABE0D94BAC49D3475DB74F922E901FBB20A9808EA676154A3 --source D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf --source-sha256 0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05 --comparison D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full\comparison\comparison.json --comparison-sha256 5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0 --pdftoppm C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe --dpi 110 --expected-pages 124
```

If it succeeds, run exactly:

```powershell
python -B -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q
```

Then perform all machine and visual acceptance from the parent execution
packet. Write only a new correction receipt:

`luna_qa_viral_step6a_full_visual_merge_bundle_execution_correction_20260901.md`

If either literal command fails, stop and record its exact tool result without
repair or rerun. All original read/write/role prohibitions remain in force.

