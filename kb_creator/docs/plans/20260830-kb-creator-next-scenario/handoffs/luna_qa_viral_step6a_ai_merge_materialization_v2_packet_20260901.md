# Luna QA packet — Viral Step 6A AI merge materialization v2

Date: 2026-09-01  
Goal id: `20260830-kb-creator-next-scenario`  
Step id: `viral-step6a-ai-merge-materialization-v2`  
Owner: main-chat orchestrator (`gpt-5.6-sol`, policy effort `medium`)  
Executor: bounded QA (`gpt-5.6-luna`, `high`)  
Status: `AUTHORIZED_ONE_FRESH_V2_RUN`

## Purpose and preserved evidence

Materialize the corrected 124-page AI decision set into one fresh reconstruction
candidate. This is execution-only QA. The executor may not design, repair or
reinterpret code, tests, decisions, fixtures or content.

The predecessor v1 candidate and its receipts are immutable rejected evidence:
its non-reference assets were substituted as bare paths rather than
reader-visible image links. Nothing in this packet permits changing or deleting
that predecessor.

## Frozen preflight

- materializer SHA-256:
  `D632FD2203C1CB68AD01DBD369E7FD530146A5D423F786FDEB64848F0F331076`;
- focused-test file SHA-256:
  `F6917CC80C129527BDE95B15C85562921B7F9064221E63ED4839634C6D537DC3`;
- Terra image-link correction receipt SHA-256:
  `B170742DAF2C13AF059923D1AC25E02207996CCA8D2E7B6237D2E15823711928`;
- Sol range-A decision correction receipt SHA-256:
  `08FE6FD49C83FFB4D7A042E4ABB4735AFEFEC2A84D7AF2C29802B67CD7A29386`;
- decisions: exactly `124` JSON files / `589051` bytes;
- ordered concatenated per-file SHA-256 hex digest:
  `AA13DF843FAC3473144D69678056BB30B7FFFFE53185408841D5672C38F47232`;
- SHA-256 of UTF-8 without BOM, LF-joined
  `name<TAB>bytes<TAB>sha256` rows:
  `65FDF7DF95EAD4021CB84AAD14B3644C115974108663288440CFA8D76DF587E2`;
- decision assets: `121`, of which `119` are non-reference assets and `2`
  are `reference_only`;
- unresolved decisions: `0`; non-visually-reviewed decisions: `0`;
- all `119` non-reference assets occur in exact
  `![nonempty alt]({{asset:logical_name}})` syntax; bare placeholders: `0`;
- fresh target
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v2`
  is absent.

## Exact execution

Working directory:

`D:\NRI\.worktrees\kb-creator-viral`

Run exactly once as one native command:

```powershell
python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions_v2\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v2
```

Do not add redirection, a pipeline, wrapper or a second command. On any nonzero
exit or unexpected output, stop immediately; do not inspect, repair, clean or
rerun.

## Allowed receipt

After the command, create only this one new receipt through the file patch tool:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_ai_merge_materialization_v2_20260901.md`

Record:

- the packet SHA-256 supplied by the orchestrator;
- literal command and working directory;
- native execution count, exit code, stdout and stderr;
- preservation statement;
- verdict `PASS` only when native exit is `0` and stdout reports
  `candidate_ready_for_reconstruction_qa`, `pages: 124`, `assets: 121`,
  `unique_asset_bytes: 121`.

Do not run tests, discovery, hashes, MinerU, verifiers, inventory checks or
downstream stages. Do not edit any input, decision, code, plan, context, Git,
production or predecessor path. The orchestrator owns every post-run audit.
