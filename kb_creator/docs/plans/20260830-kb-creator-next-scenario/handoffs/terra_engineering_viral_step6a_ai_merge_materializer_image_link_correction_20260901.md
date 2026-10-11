# Terra correction receipt — Viral Step 6A materializer reader-visible image links

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-ai-merge-materializer-image-link-correction`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Correction packet SHA-256: `50DF476634BBCFC9871A0D905DBC0E782E97B025CC7952D7CBB1CBB7F1819E77`
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 9 minutes
- Token use: unavailable

## Scope and result

All prior receipts, rejected v1 candidate and frozen decisions remain untouched. This correction prevents a bare substituted asset path from being mistaken for a reader-visible image.

No real decision/candidate run, MinerU, verifier/full suite, commit or push occurred.

## Corrected files

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - SHA-256 `D632FD2203C1CB68AD01DBD369E7FD530146A5D423F786FDEB64848F0F331076`
  - every present `{{asset:<logical_name>}}` must be the exact target of `![nonempty alt]({{asset:<logical_name>}})`;
  - rejects bare placeholders, empty/whitespace alt text and link-only placeholders before staging;
  - every non-`reference_only` asset needs at least one valid image use; `reference_only` may be absent but must use valid image syntax if present;
  - retains existing relative page/root substitution, content-addressed deduplication, original decision bytes and page-context failures.
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - SHA-256 `F6917CC80C129527BDE95B15C85562921B7F9064221E63ED4839634C6D537DC3`
  - adds bare/empty-alt/link-only rejection and valid duplicate image use/reference-only absence regressions.

## Verification evidence

```powershell
python -B -m pytest kb_creator/tests/test_materialize_mineru_ai_merge.py -q
# exit 0: 29 passed in 0.78s

python -B -m py_compile kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0

git diff --check -- kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0
```

Tests used synthetic temporary JSON/assets only. The next real v2 decision/candidate execution remains an orchestrator/Luna-gated action.
