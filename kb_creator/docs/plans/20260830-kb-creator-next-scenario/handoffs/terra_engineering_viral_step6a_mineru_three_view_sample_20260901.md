# Terra engineering receipt — Viral Step 6A three-view sample

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-mineru-three-view-sample-engineering`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 22 minutes
- Token use: unavailable

## Scope and result

Implemented the authorized reusable three-view preparation and comparison transport only. No source, predecessor, candidate, verifier, production or MinerU run root was changed. No GPU MinerU execution was started.

Result: `READY_FOR_LUNA_EXECUTION`, subject to the PDF-authoring test limitation below. The tools support both the exact 8-page sample mapping and a later full-document mapping such as `--pages 1-124`; the comparison core contains no Viral-specific page list.

## Changed files

- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
  - validates input SHA-256 before writing;
  - rejects a non-empty destination unless `--resume` proves the same manifest and output hashes;
  - creates a vector page-selection PDF and a 200-DPI image-only Letter PDF;
  - emits `sample_pages.json` with ordered source-page mapping, source/output identities, dimensions, DPI and tool versions.
- `kb_creator/scripts/compare_mineru_three_views.py`
  - requires v1/v2 content lists and Markdown, inventories overlay/origin/span PDFs;
  - normalizes `page_idx` through the manifest to source-page identity;
  - reports coverage, block counts, text lengths, image references and pairwise IoU block matches/unmatched blocks without treating a difference as a repair instruction;
  - writes machine-readable `comparison.json` and concise `comparison.md`, and exits nonzero if coverage or overlay contract is missing.
- `kb_creator/tests/test_mineru_three_view_tools.py`
  - focused coverage for source-hash rejection, ordered page mapping, text-free raster PDF, safe resume, MinerU normalization and preserved representative asset/block difference.

## Verification evidence

Commands actually run from the successor worktree:

```powershell
python -B -m py_compile kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/scripts/compare_mineru_three_views.py kb_creator/tests/test_mineru_three_view_tools.py
# exit 0

python -B -m pytest kb_creator/tests/test_mineru_three_view_tools.py -k normalization -q
# exit 0: 1 passed, 4 deselected in 0.02s

python -B kb_creator/scripts/prepare_mineru_three_view_inputs.py --help
python -B kb_creator/scripts/compare_mineru_three_views.py --help
# both exit 0

git -C D:\NRI\.worktrees\kb-creator-viral diff --check -- kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/scripts/compare_mineru_three_views.py kb_creator/tests/test_mineru_three_view_tools.py
# exit 0
```

The full five-test file was intentionally not executed here: it creates temporary test PDFs. The PDF skill requires a successful `mark_artifact_operation_started.mjs` immediately before the first PDF-authoring command; the required marker executable was not present at the documented relative location or discoverable under the local user profile. No PDF was therefore authored in this engineering session. This is a verification limitation, not a pipeline/output failure; Luna must run the marker once immediately before the first frozen preparation command, then the full focused suite can be rerun in an environment where that marker is available.

## Frozen Luna execution commands

Run from `D:\NRI\.worktrees\kb-creator-viral`. Before command 1, run the PDF skill marker successfully **once** with `--operation-kind create --expected-output-count 2 --output-format pdf`.

```powershell
$root = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_sample'
$source = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf'
New-Item -ItemType Directory -Force -Path "$root\evidence", "$root\runs" | Out-Null
python -B kb_creator/scripts/prepare_mineru_three_view_inputs.py --source $source --output-dir "$root\inputs" --source-sha256 0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05 --pages 5,12,53,69,104,109,115,123 --dpi 200 --basename viral_sample *>&1 | Tee-Object "$root\evidence\prepare.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& 'D:\NRI\MinerU\scripts\run-hybrid.ps1' -InputPath "$root\inputs\viral_sample_vector.pdf" -OutputPath "$root\runs\original_hybrid" *>&1 | Tee-Object "$root\evidence\original_hybrid.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& 'D:\NRI\MinerU\.venv\Scripts\mineru.exe' -p "$root\inputs\viral_sample_vector.pdf" -o "$root\runs\original_pipeline_ocr" -m ocr -b pipeline *>&1 | Tee-Object "$root\evidence\original_pipeline_ocr.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& 'D:\NRI\MinerU\scripts\run-hybrid.ps1' -InputPath "$root\inputs\viral_sample_raster.pdf" -OutputPath "$root\runs\raster_hybrid" *>&1 | Tee-Object "$root\evidence\raster_hybrid.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -B kb_creator/scripts/compare_mineru_three_views.py --manifest "$root\inputs\sample_pages.json" --original-hybrid "$root\runs\original_hybrid" --original-pipeline-ocr "$root\runs\original_pipeline_ocr" --raster-hybrid "$root\runs\raster_hybrid" --output-dir "$root\comparison" *>&1 | Tee-Object "$root\evidence\compare.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

After each command Luna must record exact exit code, command text, SHA-256 of the console capture, input hash, and recursive output inventory under `$root\evidence`. It must then render and inspect all three produced `*_layout.pdf` files (24 overlay pages total) before returning a receipt. The expected overlay locations are under the MinerU-created nested run directories; the comparator discovers them recursively and fails the sample contract when any one is absent.

## Blockers and next action

No engineering or source blocker was found. The only open limitation is that this session cannot locate the mandatory PDF skill marker, so it did not run the PDF-creating focused tests. The next action is Luna's bounded execution of the frozen commands, including one successful marker invocation, followed by a fresh full focused test run and raw evidence capture. Any script failure or contract mismatch returns to Terra; Luna must not repair it.
