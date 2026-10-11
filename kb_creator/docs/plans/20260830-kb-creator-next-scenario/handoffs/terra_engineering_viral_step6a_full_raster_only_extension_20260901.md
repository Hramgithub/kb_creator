# Terra engineering receipt — Viral Step 6A full raster-only input extension

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-full-raster-only-input-extension`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: PDF artifact marker had already succeeded for this active PDF task in Luna receipt `4425D646...6C903E`; this extension did not rerun it.
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 12 minutes
- Token use: unavailable

## Scope and result

Implemented the bounded generic `raster_only` preparation mode for the later full-document three-view run. It creates exactly one image-only PDF and mapping manifest. It does not create, copy or rewrite a vector PDF; original-hybrid and original-pipeline must use the retained source PDF directly.

No GPU MinerU run, source/sample/candidate/predecessor mutation, plan/context/verifier change, commit or push occurred.

## Changed files and identities

- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
  - SHA-256: `325661B2CD1452CDA426930D634917807871FDE0B8781E9769F2602E649BFF9A`
  - adds `--raster-only` and manifest mode `raster_only`;
  - does not create a vector file or `vector_pdf` output record in that mode;
  - validates selected mode before any resume, requires the exact expected output-key set, and continues to prove output identities before resume.
- `kb_creator/tests/test_mineru_three_view_tools.py`
  - SHA-256: `858D94BB957539E73C1FC141324B4BB176719403886853A53568C9E38F9C315E`
  - adds focused coverage for `1..N` mapping, no vector artifact/output record, text-free raster pages, deterministic repeat, normal refusal of a non-empty root, exact resume, and wrong-mode resume rejection.

## Verification evidence

The established Luna marker receipt authorizes PDF fixture creation for this active task; it was not rerun.

```powershell
python -B -m pytest kb_creator/tests/test_mineru_three_view_tools.py -q
# exit 0: 11 passed in 2.01s

python -B -m py_compile kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/tests/test_mineru_three_view_tools.py
# exit 0

git diff --check -- kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/tests/test_mineru_three_view_tools.py
# exit 0
```

The tests use only pytest-managed temporary PDF fixtures and never invoke MinerU, GPU hardware or any goal run root.

## Frozen full preparation command

Run from `D:\NRI\.worktrees\kb-creator-viral`. The future full root must be fresh; do not use `--resume` for the first run.

```powershell
$root = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full'
$source = 'D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf'
New-Item -ItemType Directory -Force -Path "$root\evidence", "$root\runs" | Out-Null
python -B kb_creator/scripts/prepare_mineru_three_view_inputs.py --source $source --output-dir "$root\inputs" --source-sha256 0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05 --pages 1-124 --dpi 200 --basename viral_full --raster-only *>&1 | Tee-Object "$root\evidence\prepare_raster_only.console.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Expected inputs after success:

```text
inputs/
  viral_full_raster.pdf
  sample_pages.json
```

The manifest must have `mode: raster_only`, `124` ordered source mappings and exactly one `outputs.raster_pdf` record. `viral_full_vector.pdf` must not exist. The later original-hybrid and original-pipeline profiles read `$source`; only raster-hybrid reads `$root\inputs\viral_full_raster.pdf`.

## Next action

The orchestrator may freeze the three full-run commands around this preparation command. Luna remains execution-only; any engineering failure returns to Terra unchanged.
