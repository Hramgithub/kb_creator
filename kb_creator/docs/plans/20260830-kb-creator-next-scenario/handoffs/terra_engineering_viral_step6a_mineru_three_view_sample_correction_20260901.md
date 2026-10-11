# Terra correction receipt — Viral Step 6A three-view sample

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-mineru-three-view-sample-engineering-correction`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 16 minutes
- Token use: unavailable

## Scope and result

This receipt supersedes only the three bounded P1 gaps reported against the preceding Terra receipt; the preceding receipt remains immutable.

Result: corrected tooling is `READY_FOR_LUNA_EXECUTION`, subject to the known mandatory-PDF-marker limitation. No GPU MinerU invocation, source/candidate/predecessor mutation, verifier work, production output, commit or push occurred.

## Corrected files

- `kb_creator/scripts/run_mineru_three_view.ps1` (new reusable execution wrapper)
  - accepts `-MinerURoot`, `-InputPath`, `-OutputPath` and either `hybrid_high` or `pipeline_ocr` profile;
  - invokes the supplied MinerU root's `scripts/initialize.ps1`, uses its `.venv\\Scripts\\mineru.exe` and config path, and establishes the same runtime model/cache/temp/proxy/LMDeploy/static-launcher environment as the established `run-hybrid.ps1`;
  - invokes hybrid as `hybrid-engine/high` and pipeline as `pipeline/ocr`; has no Viral or `D:\\NRI` literal.
- `kb_creator/scripts/compare_mineru_three_views.py`
  - now requires each view's `_middle.json` in addition to v1/v2 content and Markdown;
  - inventories every `img_path`/asset reference with bytes and SHA-256;
  - rejects absolute, drive-qualified or `..` asset paths and fails on missing referenced files;
  - retains block and asset differences as comparison evidence rather than auto-repairing or treating ordinary differences as failure.
- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
  - keeps static PDF metadata, ReportLab `invariant=1`, no dynamic manifest timestamp, supporting byte-repeatability.
- `kb_creator/tests/test_mineru_three_view_tools.py`
  - adds deterministic repeat identity test for vector PDF, raster PDF and manifest;
  - adds missing/escaping asset negatives and static wrapper-contract coverage; no test executes MinerU/GPU.

## Verification evidence

Commands actually executed from the successor worktree:

```powershell
python -B -m py_compile kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/scripts/compare_mineru_three_views.py kb_creator/tests/test_mineru_three_view_tools.py
# exit 0

python -B -m pytest kb_creator/tests/test_mineru_three_view_tools.py -k 'normalization or wrapper' -q
# exit 0: 2 passed, 8 deselected in 0.03s

$errors = $null; $tokens = $null
[void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path 'kb_creator/scripts/run_mineru_three_view.ps1'), [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { exit 1 }
# exit 0: PowerShell parse OK

git diff --check -- kb_creator/scripts/run_mineru_three_view.ps1 kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/scripts/compare_mineru_three_views.py kb_creator/tests/test_mineru_three_view_tools.py
# exit 0
```

The tests that author temporary PDF files (including byte-repeatability) were not run. The mandatory PDF artifact marker was still not discoverable in this environment, so no PDF was created in contravention of that contract.

## Frozen Luna execution commands

Run from `D:\NRI\.worktrees\kb-creator-viral`. Immediately before the first command below, Luna must run the PDF skill marker **once successfully** for `create`, expected output count `2`, format `pdf`. Then execute the preparation command as that first PDF-authoring command.

```powershell
$root = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_sample'
$source = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf'
$minerRoot = 'D:\NRI\MinerU'
New-Item -ItemType Directory -Force -Path "$root\evidence", "$root\runs" | Out-Null

python -B kb_creator/scripts/prepare_mineru_three_view_inputs.py --source $source --output-dir "$root\inputs" --source-sha256 0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05 --pages 5,12,53,69,104,109,115,123 --dpi 200 --basename viral_sample *>&1 | Tee-Object "$root\evidence\prepare.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\kb_creator\scripts\run_mineru_three_view.ps1 -Profile hybrid_high -MinerURoot $minerRoot -InputPath "$root\inputs\viral_sample_vector.pdf" -OutputPath "$root\runs\original_hybrid" *>&1 | Tee-Object "$root\evidence\original_hybrid.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\kb_creator\scripts\run_mineru_three_view.ps1 -Profile pipeline_ocr -MinerURoot $minerRoot -InputPath "$root\inputs\viral_sample_vector.pdf" -OutputPath "$root\runs\original_pipeline_ocr" *>&1 | Tee-Object "$root\evidence\original_pipeline_ocr.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\kb_creator\scripts\run_mineru_three_view.ps1 -Profile hybrid_high -MinerURoot $minerRoot -InputPath "$root\inputs\viral_sample_raster.pdf" -OutputPath "$root\runs\raster_hybrid" *>&1 | Tee-Object "$root\evidence\raster_hybrid.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -B kb_creator/scripts/compare_mineru_three_views.py --manifest "$root\inputs\sample_pages.json" --original-hybrid "$root\runs\original_hybrid" --original-pipeline-ocr "$root\runs\original_pipeline_ocr" --raster-hybrid "$root\runs\raster_hybrid" --output-dir "$root\comparison" *>&1 | Tee-Object "$root\evidence\compare.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -B -m pytest kb_creator/tests/test_mineru_three_view_tools.py -q *>&1 | Tee-Object "$root\evidence\terra_focused_tests.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Luna must capture command text, exit code, console SHA-256, input SHA-256 and recursive inventories. It must then render/inspect all 24 pages in the three produced layout PDFs. Any command failure returns to Terra unchanged; Luna does not modify code, fixtures or comparison results.

## Next action

Luna may execute the frozen sample sequence after a verified marker invocation. The full 124-page run remains gated on all three sample views preserving their mandatory raw artifacts, the comparator report and visual QA.
