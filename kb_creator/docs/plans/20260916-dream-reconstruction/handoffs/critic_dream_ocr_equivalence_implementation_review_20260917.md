# Number 7 Dream OCR-equivalence remediation implementation review

## Receipt

- Timestamp: `2026-09-17T02:28:00+03:00`.
- Goal: `20260916-dream-reconstruction`.
- Review kind: `implementation`.
- Candidate state: non-frozen implementation candidate; not a release review.
- Implemented or materially designed candidate: no.
- Role / requested effort: independent critic, repository policy `gpt-5.5` at `medium`; actual platform model/effort unavailable.
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; orchestration ownership was not transferred.
- Assignment state: complete.
- Scoped override: none.
- Scope: review the OCR-equivalence remediation against `architect_dream_ocr_equivalence_remediation_20260917.md`, current implementation/schema/test changes, and Number 7 Dream decisions-v6 Stage 05 evidence. No implementation, decisions, run evidence, plan, context, status, release, Git, publication, or acceptance files were edited.
- Files changed by this reviewer: this immutable receipt only.
- Blockers: none.
- Recommendation: accept for integration and replay Stage 05/06 continuation. This is not user acceptance and not release approval.
- Elapsed time: approximately 35 minutes across the interrupted review turn.
- Token use: exact role token count unavailable.

## Files checked

- `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/architect_dream_ocr_equivalence_remediation_20260917.md`
- `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/engineer_dream_ocr_equivalence_remediation_20260917.md`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json`
- `kb_creator/contracts/ai_merge_fidelity_audit.v3.schema.json`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-03-decisions-v6/decision_set.json`
- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-03-decisions-v6/reviewed_allowlist.v3.json`
- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-03/outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json` through `page-026.json` via direct audit input
- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-03/outputs/04-visual-merge-bundle/visual/geometry_plan.json`
- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-03/outputs/04-visual-merge-bundle/visual/visual_manifest.json`

## Evidence

- Implementation diff preserves the strict OCR lexical policy constants and moves exact whole-unit equivalence from `exact_unique_cross_view_geometry_v1` to `exact_unique_cross_view_geometry_v2`.
- `_exact_equivalent()` now filters duplicate same-text candidates by existing whole-unit geometry bounds and accepts only exactly one qualified selected canonical candidate.
- Reviewed OCR classes are a separate closed key shape requiring `equivalence_policy`, page-matching `source_visual`, closed `canonical_proof`, exact visual identity, original text source view canonical unit, failed strict bounds for reviewed alternates, fixed geometry, and non-empty rationale.
- Allowlist schema v3 keeps the existing bounded OCR class as one branch and adds a closed reviewed branch with no caller-supplied tolerances.
- Audit schema v3 was updated for the new whole-unit policy constant.
- Focused local pytest command passed: `77 passed in 0.72s` for `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`.
- Number 7 Dream decisions-v6 allowlist summary: schema `kb_creator.ai_merge_fidelity_reviewed_allowlist.v3`; 75 exclusions; 1 visual assertion; 36 OCR classes; 15 reviewed OCR classes; 21 bounded OCR classes; 0 page-23 OCR classes, so the raw-index swap is handled by automatic exact equivalence rather than a redundant reviewed override.
- Direct read-only `audit_v3_content()` over the real 26 merge packets and decisions-v6, with Stage 04 geometry and visual manifest identities, passed and validated against `ai_merge_fidelity_audit.v3.schema.json`: `pages=26`, `errors=0`, `unaccounted=0`, `min_completeness=1.0`, `max_completeness=1.0`, `classes=36`, `assertions=1`, `passed=true`.
- Orchestrator-reported broader evidence was inspected but not independently rerun in full: focused `86 passed`; expanded `359 passed, 1 skipped`; direct Number 7 Dream decisions-v6 audit `26 pages`, completeness `1.0`, `0 errors`.

## Findings

- P0: none.
- P1: none.
- P2: none.

## Notes and residual risk

- The audit report schema remains intentionally coarse for nested `units`, `visual_assertions`, and `ocr_equivalence_classes` report rows. That is consistent with the pre-existing v3 schema style and does not weaken the closed input allowlist branch reviewed here.
- The remaining risk is human visual-verdict error in reviewed OCR classes. The current implementation mitigates it with exact unit identities, proof hash, source-page render identity, triptych identity, page/region geometry, strict-first rejection, duplicate-membership rejection, and unused-row rejection.
