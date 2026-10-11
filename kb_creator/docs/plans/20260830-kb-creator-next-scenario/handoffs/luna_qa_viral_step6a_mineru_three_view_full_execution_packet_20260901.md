# Luna execution packet - Viral Step 6A full three-view extraction

Date: 2026-09-01  
Owner: `gpt-5.6-luna`, high, execution-only QA  
Status: `AUTHORIZED`

## Objective

Execute the full 124-page three-view MinerU extraction after the completed
sample gate. This packet covers raw extraction and machine validation only.
Full visual review and AI-assisted merge are later gates and must not cause a
MinerU profile to be repeated.

## Bound state

- retained source:
  `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`;
- source bytes: `20,718,150`;
- source SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- pages: `124` Letter pages;
- sample machine gate: comparator `pass`, focused tests `10/10`;
- sample visual gate receipt SHA-256:
  `9A8A0980C6478F4FE32CDF026735DC17EFD680E02B355630483C705E33F96249`;
- full raster-only Terra receipt SHA-256:
  `2D63E9FF22E8A21892E7584D4AE6F495D5D2112146771F7ACF352443A6F31F7A`;
- preparer SHA-256:
  `325661B2CD1452CDA426930D634917807871FDE0B8781E9769F2602E649BFF9A`;
- comparator SHA-256:
  `78FDB0908011E91DFB9A95FEE28A575EBDCE68146900AD265BC215A6AC59C976`;
- MinerU wrapper SHA-256:
  `262E1CA20B42EF4B87C30A90CC56589CEE6DFC759FF762A5FAB430EEAEF07269`;
- focused tests SHA-256:
  `858D94BB957539E73C1FC141324B4BB176719403886853A53568C9E38F9C315E`;
- installed MinerU verification: PASS, MinerU 3.4.4, Torch 2.8.0+cu128,
  CUDA 12.8, RTX 5080;
- full root was absent at dispatch and drive D had `816.53 GiB` free.

Fresh root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full`

## First authoring boundary

Create the root's empty `evidence` and `runs` directories first. Then,
immediately before the raster-only preparer, run this full-operation PDF marker
successfully exactly once:

```powershell
& 'C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' 'C:\Users\BogdanD\.codex\plugins\cache\openai-primary-runtime\pdf\26.826.12353\skills\pdf\container_tools\mark_artifact_operation_started.mjs' --operation-kind create --expected-output-count 1 --output-format pdf
```

The immediately following command must be the raster-only preparer. It must
create only `viral_full_raster.pdf` plus `sample_pages.json`; no vector PDF is
authorized because both original profiles read the retained source directly.

## Exact profiles and order

Run from `D:\NRI\.worktrees\kb-creator-viral`, one command at a time, with raw
console captured immediately. Use the exact preparation command from
`terra_engineering_viral_step6a_full_raster_only_extension_20260901.md`, then:

```powershell
$root = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full'
$source = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf'
$minerRoot = 'D:\NRI\MinerU'

& .\kb_creator\scripts\run_mineru_three_view.ps1 -Profile hybrid_high -MinerURoot $minerRoot -InputPath $source -OutputPath "$root\runs\original_hybrid" *>&1 | Tee-Object "$root\evidence\original_hybrid.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\kb_creator\scripts\run_mineru_three_view.ps1 -Profile pipeline_ocr -MinerURoot $minerRoot -InputPath $source -OutputPath "$root\runs\original_pipeline_ocr" *>&1 | Tee-Object "$root\evidence\original_pipeline_ocr.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\kb_creator\scripts\run_mineru_three_view.ps1 -Profile hybrid_high -MinerURoot $minerRoot -InputPath "$root\inputs\viral_full_raster.pdf" -OutputPath "$root\runs\raster_hybrid" *>&1 | Tee-Object "$root\evidence\raster_hybrid.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -B kb_creator/scripts/compare_mineru_three_views.py --manifest "$root\inputs\sample_pages.json" --original-hybrid "$root\runs\original_hybrid" --original-pipeline-ocr "$root\runs\original_pipeline_ocr" --raster-hybrid "$root\runs\raster_hybrid" --output-dir "$root\comparison" *>&1 | Tee-Object "$root\evidence\compare.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -B -m pytest kb_creator/tests/test_mineru_three_view_tools.py -q *>&1 | Tee-Object "$root\evidence\terra_focused_tests.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

## Machine acceptance

After the commands, without modifying outputs:

1. record every exact command, native exit code, elapsed time and console
   capture bytes/SHA-256;
2. prove manifest mode `raster_only`, mappings `1..124`, and only one input PDF
   output record;
3. prove `viral_full_vector.pdf` does not exist;
4. prove every profile reports `124/124` and maps exact `page_idx 0..123`;
5. require Markdown, v1/v2 content lists, middle JSON, layout PDF and all
   referenced assets for every profile; require origin PDF when emitted and
   span PDF when emitted by pipeline;
6. use `pdfinfo` to require exactly 124 pages in all three layout PDFs;
7. record recursive file/byte/SHA-256 inventories for inputs, each run,
   comparison and evidence;
8. require comparator `status: pass`, `failures: []`;
9. require the full focused test file to pass;
10. write the single receipt:
   `luna_qa_viral_step6a_mineru_three_view_full_execution_20260901.md`.

Do not render or visually inspect the 372 layout pages in this packet; that
work will reuse these exact immutable PDFs in a separate visual gate.

## Stop and write policy

At the first failed command or violated machine contract, stop, preserve the
failure and write the same receipt with `BLOCKED`. Do not repair, restart a
completed profile or weaken the contract.

Write allowlist:

- the fresh full root;
- the single receipt named above;
- normal MinerU-owned runtime cache/temp/config and automatic cleanup.

All code/tests/source/sample/prior roots/candidate/plan/context/config,
MASTER_EN/RU, HTML, final PDF, production and Git are read-only. No verifier
371/119/490, commit or push work is allowed.

