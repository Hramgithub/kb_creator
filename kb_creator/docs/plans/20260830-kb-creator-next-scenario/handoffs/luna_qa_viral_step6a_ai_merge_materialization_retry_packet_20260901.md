# Luna retry packet — Viral Step 6A AI merge materialization

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Executor: bounded QA (`gpt-5.6-luna`, high)  
Status: `AUTHORIZED_ONE_FRESH_RETRY`

## Preserved predecessor and remediation

The first receipt is immutable, SHA-256
`77F3C8EFF8F9253A524E2D13FA5E42DE5262B5E12135CD24146AC488FA952F94`.
It stopped before publication because ordinary source slash notation was
misclassified as an absolute path. Target root remains absent.

Frozen corrected identities:

- materializer:
  `1B0D3E55886DD120D8A8023048F739FA83355D29EEEF7B76CCD9966CB4BA55E9`;
- focused tests:
  `AA6D00F0A47A1E03B9CA8220A0C03E4FB54CCF66F64F8A561A2F0CA0AF92AA94`;
- Terra correction receipt:
  `9E47BEB9DE75475FF78120E13FCBFCBA7E74772A1C84D82D356ECE1443F12207`;
- decisions remain 124 files / inventory SHA-256
  `728BEAEF00457CD142FD17CE90E01534835CA54AB647B118AC9DCCEC57337A06`;
- target root is absent.

## Exact execution

Working directory:

`D:\NRI\.worktrees\kb-creator-viral`

Run exactly once:

```powershell
python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate
```

No redirection, pipeline, wrapper, repair or further rerun. On failure, stop.

Create only one new receipt through the file patch tool:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_ai_merge_materialization_retry_20260901.md`

Record native exit/stdout/stderr and preservation. Do not run tests, discovery,
hashes, MinerU, verifiers or downstream stages. Do not edit any input/code/plan,
context, Git or production path. The orchestrator performs post-run checks.

