# Luna execution packet - Viral full visual/merge review bundle

Date: 2026-09-01  
Owner: `gpt-5.6-luna`, high, execution-only QA  
Status: `AUTHORIZED`

## Bound inputs

- immutable raw root:
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full`;
- raw Luna receipt SHA-256:
  `20B34FCA18064BBABE0D94BAC49D3475DB74F922E901FBB20A9808EA676154A3`;
- raw comparison SHA-256:
  `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0`;
- source SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- corrected bundler SHA-256:
  `7B9C7695DFC65D2AD0FD01230AA81C8F9D6CDDFC2990DD822C8F3EE47647B301`;
- corrected tests SHA-256:
  `B50B0DDA6D4ED21076AE5BE47C176EA379A80BCAC2AB59C18CAB38D10035C8DE`;
- Terra correction receipt SHA-256:
  `15B0F35DBFC9058951BEB2DD79E69080C1C9D72132A3AEDB1C91930171C40720`.

Fresh output root was absent at dispatch; drive D had `814.19 GiB` free:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate`

## Execution

From `D:\NRI\.worktrees\kb-creator-viral`, execute exactly once the frozen
command in
`terra_engineering_viral_step6a_full_visual_merge_bundle_correction_20260901.md`.
This operation reads existing PDFs and creates PNG/JSON/Markdown only; no PDF
artifact marker is required.

Then run the corrected focused test file exactly once:

```powershell
python -B -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q
```

At the first command failure, stop and write the receipt `BLOCKED`. Do not edit
or rerun the bundler, Poppler command, tests or any raw extraction profile.

## Machine acceptance

Require and record:

- 372 individual view renders: 124 for each exact view;
- numeric page identity 1..124 in every view;
- 124 triptychs with fixed left-to-right view labels;
- 31 contact sheets covering pages 1..124 exactly once and in order;
- 124 JSON and 124 Markdown page packets;
- every raw comparison block and asset reference preserved in exactly its
  source-page/view packet;
- every real `bbox_matches` row preserved exactly once after raw-index routing;
- source-order and priority-order indexes each containing all 124 pages once;
- visual manifest input hashes, Poppler version/commands, file hashes and
  dimensions;
- declared inventory rule: every generated file except only
  `visual/visual_manifest.json` and `evidence/execution.json`;
- focused tests `6 passed`;
- exact command, native exit, elapsed time, output-root file/byte counts and
  detached receipt hash.

## Visual acceptance

Open and actually inspect all 31 contact sheets at high detail. For every sheet
confirm that its four source pages are present and that the three columns remain
ordered/labeled and visually readable enough to compare overlay regions.

Also open individual triptychs at high detail for:

- the top 20 pages in `merge_index.json` priority order;
- known sample signals source pages 53 and 109;
- any additional page whose contact-sheet view is ambiguous, clipped,
  unreadable or suggests a missing/merged/split region.

Record page-specific cross-view signals for later AI merge. Differences are
evidence, not automatic defects. `PASS` requires all 31 sheets inspected and
every required individual triptych readable; a missing/unreadable/uninspected
page is `BLOCKED`.

## Write and role boundary

Write allowlist:

- the fresh postprocess root written only by the frozen bundler;
- one receipt:
  `luna_qa_viral_step6a_full_visual_merge_bundle_execution_20260901.md`.

Raw/full/sample/source/candidates/scripts/tests/packets/plan/context/config/Git
are read-only. Luna may not repair code, change packets, choose final text,
perform AI merge, rerun MinerU, invoke verifier 371/119/490, create MASTER_EN,
translate, publish, commit or push.

