# Terra correction receipt — Viral Step 6A AI-merge materializer asset links

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-ai-merge-materializer-asset-link-correction`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Correction packet SHA-256: `B1730EAFDC73BAD1C51901A361B5E0DE4D5E2DE09E88ECB605A661677B914FEB`
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 12 minutes
- Token use: unavailable

## Scope and result

The first materializer receipt remains immutable. This correction closes its P1 reader-link gap: selected decision assets now have an explicit, validated Markdown-to-final-output path.

No real candidate, MinerU execution, full suite, commit or push was run.

## Corrected files

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - SHA-256 `139055C96B0E25E5B34FCE10200C98ADBBEF5C10F0673CF5CDC5E8E45B8FDE0A`
  - accepts only literal `{{asset:<logical_name>}}` references, rejects malformed/unknown templates, and validates every non-`reference_only` selected asset appears in its decision Markdown;
  - substitutes after asset validation and content-addressed copy: page Markdown uses `../assets/<sha>.<ext>`, combined root Markdown uses `assets/<sha>.<ext>`;
  - keeps original decision bytes and every logical-name manifest row, while same-byte logical assets still share one physical file;
  - empty Markdown is now allowed only when at least one selected asset is `reference_only`; full-page/handout/map assets require a real placeholder.
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - SHA-256 `AF49AF3890D1B235B63D255B043BCED1DC6728EAEB5E2659D27A350B062FC475`
  - adds page/root relative-link assertions; unknown, missing and malformed placeholder negatives; reference-only empty-page coverage; and preserved same-byte/two-logical-name dedup coverage.

## Verification evidence

```powershell
python -B -m pytest kb_creator/tests/test_materialize_mineru_ai_merge.py -q
# exit 0: 10 passed in 0.35s

python -B -m py_compile kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0

git diff --check -- kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0
```

All evidence uses synthetic temporary JSON/assets; no real candidate command is authorized or frozen here.

## Next action

After the separate page-decision set and candidate-root authorization, Luna may run the corrected materializer exactly once. It must preserve decisions and not repair packet/asset/link failures.
