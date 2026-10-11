# Luna execution packet — Viral Step 6A AI merge materialization

Date: 2026-09-01  
Owner: main-chat orchestrator (`gpt-5.6-sol`)  
Executor: bounded QA (`gpt-5.6-luna`, high)  
Status: `AUTHORIZED_ONE_COMMAND`

## Frozen admission

- materializer SHA-256:
  `139055C96B0E25E5B34FCE10200C98ADBBEF5C10F0673CF5CDC5E8E45B8FDE0A`;
- focused test SHA-256:
  `AF49AF3890D1B235B63D255B043BCED1DC6728EAEB5E2659D27A350B062FC475`;
- Terra correction receipt SHA-256:
  `218CC3A044900D0CF9B286FEC14100F5F1E5918889EF010F92A216177D172596`;
- visual QA receipt SHA-256:
  `5985CF1CF5C0EDA79C79D740793B1F2FA1F639DCCA08BF9B0AA46323A83F6157`;
- decision domain: exact `page-001.json` through `page-124.json`;
- decision files: 124, 587478 bytes, inventory SHA-256
  `728BEAEF00457CD142FD17CE90E01534835CA54AB647B118AC9DCCEC57337A06`;
- selected blocks: 1804; selected assets: 121; unresolved: 0;
- every decision records `visual_reviewed: true`; placeholder errors: 0;
- target output root is absent.

## Exact execution

Working directory:

`D:\NRI\.worktrees\kb-creator-viral`

Run exactly this one command, once:

```powershell
python -B kb_creator\scripts\materialize_mineru_ai_merge.py --bundle-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_postprocess_candidate --raw-root kb_creator\working\viral\source_reconstruction\20260901_step6a_mineru_three_view_full --decisions-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_decisions\pages --output-root kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate
```

Do not add redirection, pipelines, wrappers or combined commands. Capture native
stdout/stderr and exit code. On any nonzero exit or tool/transport failure,
stop without repair or rerun.

## Only write besides the materializer-owned candidate

Create one receipt through the file patch tool:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_qa_viral_step6a_ai_merge_materialization_20260901.md`

Record verdict, literal command, native exit, exact stdout/stderr, whether the
target was absent before execution, and confirmation of no other action.

Do not run tests, MinerU, verifier suites, hash/inventory commands, shell
discovery or repair. Do not edit decisions, packets, raw roots, code, plans,
context, MASTER_EN/RU, HTML, PDF, production or Git. The orchestrator performs
all post-run read-only checks.

