# Luna execution packet - Viral Step 6A three-view sample

Date: 2026-09-01  
Owner: `gpt-5.6-luna`, high, execution-only QA  
Status: `AUTHORIZED`

## Objective

Execute the already designed and implemented 8-page three-view MinerU sample.
Do not design, edit or repair code, tests, manifests, comparison rules or
outputs. A failure is evidence returned to the orchestrator/Terra, not authority
for Luna to fix it.

## Bound inputs

- architecture packet:
  `sol_orchestrator_viral_step6a_mineru_three_view_rescope_20260901.md`;
- Terra correction receipt SHA-256:
  `D7B498D8023A977DE302F5CC6A039FC1E32DE82EFA8E5C6EBF7B5F62C1D8323A`;
- source SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- preparer SHA-256:
  `67873A607EA231719338E4984E598946511A4C47C263B5AB3EB8E864CBD65AB0`;
- comparator SHA-256:
  `78FDB0908011E91DFB9A95FEE28A575EBDCE68146900AD265BC215A6AC59C976`;
- MinerU wrapper SHA-256:
  `262E1CA20B42EF4B87C30A90CC56589CEE6DFC759FF762A5FAB430EEAEF07269`;
- focused tests SHA-256:
  `C6C60BB6DC777C412422B8757D239CC3D2034B97DDD43E60964D9B6E03672E56`.

The fresh sample root was confirmed absent immediately before dispatch:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_sample`

## First authoring boundary

Before any command that creates a PDF, run this marker successfully exactly
once:

```powershell
& 'C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' 'C:\Users\BogdanD\.codex\plugins\cache\openai-primary-runtime\pdf\26.826.12353\skills\pdf\container_tools\mark_artifact_operation_started.mjs' --operation-kind create --expected-output-count 2 --output-format pdf
```

The immediately following PDF-authoring command must be the preparer command
from the Terra correction receipt. Do not run any PDF-creating test before it.

## Exact execution sequence

Run the frozen commands in the `Frozen Luna execution commands` section of
`terra_engineering_viral_step6a_mineru_three_view_sample_correction_20260901.md`
in their listed order:

1. create the exact fresh root's evidence/runs directories;
2. create and verify the vector/raster sample inputs;
3. original vector sample through `hybrid_high`;
4. original vector sample through `pipeline_ocr`;
5. raster sample through `hybrid_high`;
6. comparator;
7. full focused `test_mineru_three_view_tools.py`;
8. inventory all sample files and hash console captures;
9. locate each `*_layout.pdf`, confirm it has 8 pages, render every page and
   visually inspect all 24 overlays;
10. write one receipt:
   `luna_qa_viral_step6a_mineru_three_view_sample_execution_20260901.md`.

Record exact command/exit code, raw stdout/stderr capture identity, tool/runtime
versions, input/output hashes, page/artifact counts, comparison status and a
page-by-page visual result. If any command fails, stop, preserve the exact
failure and write the same receipt with `BLOCKED`; do not repair or restart a
completed profile.

## Write allowlist

- the fresh sample root only;
- the single Luna receipt named above;
- normal installed MinerU-owned `.runtime` cache/temp/config writes and normal
  automatic cleanup.

## Forbidden

- no edits to scripts, tests, source, prior roots, candidate, plan/context,
  governance/config or production;
- no deletion or cleanup of predecessor evidence;
- no 371/119/490/live verifier run;
- no MASTER_EN/RU, HTML, final PDF, production, commit or push;
- no engineering interpretation or fix.

