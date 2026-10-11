# Terra correction receipt — Viral Step 6A materializer Markdown classifier

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-ai-merge-materializer-markdown-classifier-correction`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Correction packet SHA-256: `651E18CDD4C5162B7D4016B934F2F63DC26516C0F3138294A9B65A3C5D0AE1C0`
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 11 minutes
- Token use: unavailable

## Scope and result

The prior receipts remain immutable. This correction fixes the reproduced real-admission classifier false positives without changing frozen decisions or creating the absent target root.

No real candidate materialization, MinerU, verifier/full suite, commit or push was run.

## Corrected files

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - SHA-256 `1B0D3E55886DD120D8A8023048F739FA83355D29EEEF7B76CCD9966CB4BA55E9`
  - replaces the broad path/HTML regex with boundary-aware classifiers;
  - permits ordinary reader punctuation, dice/Sanity notation, URLs and escaped Markdown while still rejecting true device-specific, UNC and POSIX absolute paths, actual HTML tags/scripts and generated source-page markers;
  - wraps every page-decision validation failure as `page-NNN.json: <original reason>`.
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - SHA-256 `AA6D00F0A47A1E03B9CA8220A0C03E4FB54CCF66F64F8A561A2F0CA0AF92AA94`
  - adds eight permitted reader-text regressions and seven true-path/tag/marker rejects with exact page context.

## Verification evidence

```powershell
python -B -m pytest kb_creator/tests/test_materialize_mineru_ai_merge.py -q
# exit 0: 25 passed in 0.62s

python -B -m py_compile kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0

git diff --check -- kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0
```

Only temporary synthetic fixtures were used. The next authorized action remains one corrected real materializer execution by Luna after orchestration binds the frozen decisions and absent target root.
