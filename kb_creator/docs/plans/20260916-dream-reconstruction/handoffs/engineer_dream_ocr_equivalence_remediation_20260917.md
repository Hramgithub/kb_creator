# Number 7 Dream OCR-equivalence remediation — engineering receipt

- Timestamp: `2026-09-17T01:47:11+03:00`.
- Goal: `20260916-dream-reconstruction`.
- Scope: bounded replay-v3 Stage 05 consumer/schema/test remediation only: geometry-disambiguated exact cross-view equivalence, closed `reviewed_visual_full_unit_v1` OCR classes, and the required selection of blank asset-bearing table blocks. No source, decisions, run evidence, candidate, plan/context/status, Git, publication, acceptance, or release files were changed.
- Result: implemented. Exact whole-unit matching now accepts exactly one geometry-qualified selected canonical candidate and records policy `exact_unique_cross_view_geometry_v2`; ambiguous candidates remain unresolved. Reviewed OCR classes are an additional closed shape with exact unit identities, original-text source render, page triptych, proof hash, assertion membership, strict-first/redundancy rejection, and fixed geometry. Blank packet blocks are selectable only when the exact matched block has a non-empty `assets` list; arbitrary non-text selections remain rejected.
- Files changed: `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`; `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json`; `kb_creator/contracts/ai_merge_fidelity_audit.v3.schema.json`; `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`; this receipt.
- Verification/evidence: bundled Python `py_compile` passed; both changed JSON schemas parsed; focused direct invocation of the four new regression cases passed (duplicate text resolved by geometry, ambiguity rejected, reviewed gross-OCR proof accepted and stale proof rejected, asset-bearing blank table accepted while a plain blank non-text block is rejected); `git diff --check` passed.
- Blockers: local bundled Python has neither `pytest` nor `jsonschema`, so the normal focused and expanded pytest/replay suites were not runnable in this environment. The orchestrator will run them with the previously verified project runtime before integrating decisions-v5.
- Next action: run focused plus expanded audit/replay suites, independently review the implementation, then run the Dream v5 direct Stage 05 audit against the sealed Stage 01-04 prefix. Correct any decision evidence failures without weakening global thresholds.
- Elapsed time: approximately 25 minutes.
- Token use: exact role token count unavailable.
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; orchestration ownership was not transferred.
- Assignment state: complete.
- Scoped override: none.
