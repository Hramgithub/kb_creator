# A8 run-18 ArtView UI QA receipt

- Scope: read-only QA of run 18 Stage 30 manifest, generated `outputs/30-artview-bundle/artifacts/artview.html`, candidate/QA artifacts, and accepted master receipts/files. No code, candidate, status, or plan changes; no release decision.
- Result: PASS for assigned checks. Candidate schema v4 contains 20 review rows and exactly one required cover (`source-cover-page-001`). Producer `qa.json` reports `pass`, with all four checks true.
- UI checks: the generated HTML does not contain `Бинарное решение`, `Примечания`, or `Строка проверена человеком`. `imageCard` renders selectable cards as labels with radio inputs and change handlers; current-file and candidate cards route through `selectImage`. Decision schema is dynamically read from `manifest.decision_contract.schema`; embedded value is `kb_creator.scenario_artview_decisions.v4`. Selected CSS applies green `--ok` border/outline and green focus styling (`.image-card.selected,.image-card.selected:focus-within`).
- Identity and output integrity: accepted MASTER_EN is SHA-256 `C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA`; accepted MASTER_RU is SHA-256 `904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`. Current run files match both acceptance receipts. Stage 30 succeeded with exit code 0. Its output record for `artview.html` is 48,131 bytes, SHA-256 `E8C10251AB910C6911126FCA27A477BE45EC45C3C2C286052A8A2F4C67DDD152`; the generated file has the same size and hash, so there is no evidence of a post-production manual edit.
- Files checked: `publication/20260918-publication-18/evidence/stages/30-artview-bundle.manifest.json`; `publication/20260918-publication-18/outputs/30-artview-bundle/artifacts/{artview.html,candidate_manifest.json,qa.json}`; `publication/20260918-publication-18/acceptance/{master_en.acceptance.json,master_ru.acceptance.json}`; `publication/20260918-publication-18/outputs/{10-master-en-candidate/artifacts/MASTER_EN.md,21-master-ru-candidate/artifacts/MASTER_RU.md}`.
- Verification/evidence: candidate and QA JSON parsed; accepted master SHA-256 values recalculated; HTML file SHA-256 and byte count matched Stage 30 manifest; requested labels searched across generated HTML; card generation/event handlers, schema binding, and selected/focus CSS inspected.
- Blockers: none within the assigned A8 scope.
- Next action: return this receipt to the orchestrator for the planned independent review/user decision gates; this QA does not authorize either gate.
- Elapsed time: approximately 3 minutes.
- Token use: unavailable from this bounded QA execution.
- Timestamp: `2026-09-18 16:27 UTC`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium (per assigned plan).
- Assignment state: A8 bounded QA complete; orchestration and release ownership remain with the main orchestrator.
- Scoped override: A8 only—verify the specified run-18 Stage 30 output/UI and write this receipt; no implementation, generated-output modification, plan/status change, or release decision.
