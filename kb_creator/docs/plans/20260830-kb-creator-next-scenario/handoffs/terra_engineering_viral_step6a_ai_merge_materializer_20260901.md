# Terra engineering receipt — Viral Step 6A AI-merge materializer

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-ai-merge-materializer`
- Role: reusable code/test engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: main-chat `gpt-5.6-sol`
- Assignment state: `matched` (platform model/effort independently unverified)
- Scoped override: none
- Packet SHA-256: `CFE271663C5FFB084706C5A4190624E5E471D0E38120D958122E464914D00BE1`
- Timestamp: 2026-09-01 (local session)
- Elapsed time: approximately 17 minutes
- Token use: unavailable

## Scope and result

Implemented a generic, decision-driven materializer. It validates and materializes reviewed page decisions; it does not choose text, invoke MinerU or create the real Viral candidate. No real candidate root, raw full root, GPU MinerU, full suite, Git, commit or push was used.

## Changed files

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - SHA-256 `C4AD1399489E44E75B90A339B9DE778493580229BF1D77A229F297724963C86F`
  - derives page domain/views from merge index and packets, enforces exact decision coverage and closed schema, validates selected raw blocks/assets under bound raw view roots, uses same-parent staging/no-replace publication, writes all required candidate/provenance/asset/overlay artifacts, preserves decision bytes and propagates unresolved review state.
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - SHA-256 `B5822026CFD13D78940735692CFFF11A6C8FC9DA9C39F2AC6DD3E0EF190CB799`
  - compact synthetic coverage of happy path/order/markers, decision byte preservation, selected-block identity, asset closure/hash deduplication, closed schema/path/HTML rules, valid empty visual page, unresolved status and no-replace output safety.

## Verification evidence

```powershell
python -B -m pytest kb_creator/tests/test_materialize_mineru_ai_merge.py -q
# exit 0: 7 passed in 0.25s

python -B -m py_compile kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0

git diff --check -- kb_creator/scripts/materialize_mineru_ai_merge.py kb_creator/tests/test_materialize_mineru_ai_merge.py
# exit 0
```

The test fixtures are temporary synthetic JSON/assets only. No real candidate materialization command is frozen by this receipt: it requires a later orchestrator-issued page-decision set and explicit candidate-root authorization.

## Next action

After AI/human decisions exist for every packet page, the orchestrator can bind exact bundle/raw/decision/candidate paths in a separate Luna execution packet. Luna may execute the prepared materializer but may not edit decisions, packets or code.
