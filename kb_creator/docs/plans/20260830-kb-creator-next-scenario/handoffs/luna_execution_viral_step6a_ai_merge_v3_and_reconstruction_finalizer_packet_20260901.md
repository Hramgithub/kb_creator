# Luna execution packet — Viral Step 6A v3 materialization and finalizer

## Assignment

- Goal: `20260830-kb-creator-next-scenario`.
- Role: bounded frozen-command execution and receipt capture only.
- Requested profile: `gpt-5.6-luna`, reasoning `high`, accelerated service when
  available.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Do not engineer, edit, repair, reinterpret or accept content.

Execute exactly two frozen commands in order. Stop after the first nonzero exit.
Do not run MinerU, tests, 371/119/490 or any extra build.

## Frozen identities and preflight

- v3 decisions: 124 JSON / 589384 bytes; ordered decision-set digest
  `0C44B3B7404CC2FD55B33146609E10A3622C8C45400CEA43E13940CE25F92D7A`;
  content receipt SHA-256
  `179F289C1177F70B4049FF96306611087A6BE20498D9C35755B0A92B31E81E67`.
- materializer SHA-256
  `D632FD2203C1CB68AD01DBD369E7FD530146A5D423F786FDEB64848F0F331076`.
- finalizer SHA-256
  `E943D82F41651A6CBEDDAE7D199B0B755133EFB304D14DD2E2B1770FAF39C367`.
- finalizer focused tests: 22 passed; production-shape receipt SHA-256
  `5FD7C039BFB9B7BE6C903B98BC4FD7E57584CD68C122129B90E3C930BC3A44AE`.
- source SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
  20718150 bytes, 124 pages.
- both exact output roots were confirmed absent before assignment.
- the mandatory PDF create marker already ran successfully exactly once before
  finalizer tests. Do not run it again.

## Allowed writes

Only:

1. `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v3`;
2. `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3`;
3. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_execution_viral_step6a_ai_merge_v3_and_reconstruction_finalizer_20260901.md`.

No cleanup or overwrite is authorized. The scripts own their narrow staging
cleanup. If command 2 fails, retain the completed candidate v3 and report the
failure; do not delete or patch anything.

## Command 1 — materialize v3

```powershell
python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v3\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v3
```

Capture native stdout, stderr, exit code and elapsed time separately. Expected
stdout status is `candidate_ready_for_reconstruction_qa`, with 124 pages and 121
assets/unique asset bytes.

## Command 2 — finalize reconstruction package

Run only after command 1 exits 0:

```powershell
python -B kb_creator\scripts\finalize_mineru_reconstruction.py --contract kb_creator\contracts\viral.json --source kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --candidate-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v3 --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_reconstructed_en_package_v3
```

Capture native stdout, stderr, exit code and elapsed time separately. Expected
stdout status is `candidate_ready_for_reconstruction_review`, 124 pages and 124
overlay pages. This is not acceptance.

## Read-only post-command receipt evidence

If both commands succeed, record without altering outputs:

- file count, total bytes and Python/codepoint ordinal trailing-LF inventory
  digest for each output root;
- SHA-256/bytes for candidate and package named root artifacts;
- package `SELECTED_OVERLAY.pdf` page count/hash/bytes/media-box/rotation domain;
- exact status and seven gate rows from `RECONSTRUCTION_QA.json`;
- exact handout physical-label count and unique numeric ordinals from
  `RECONSTRUCTION_PROVENANCE.json`;
- confirmation that package candidate-derived files are byte-identical to the
  candidate root for every predecessor path;
- absence of unresolved lists, unresolved placeholders, extra output roots,
  reparse points and stage residues;
- confirmation that the PDF marker was not repeated.

Do not visually interpret the PDF in this execution packet. Full render/visual
QA will be assigned separately after orchestrator machine audit.

## Forbidden actions

- No edits to decisions, scripts, tests, source, contract, raw/bundle roots,
  prior candidates/receipts, plan/context/status, production or Git.
- No retry with changed arguments and no manual repair/cleanup.
- No acceptance, promotion, MASTER_EN, translation, HTML, publication or commit.

## Return

Return only: result, two command exit summaries, exact output identities, receipt
path/hash and any blocker.
