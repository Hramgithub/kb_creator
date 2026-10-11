# R3 terminology and mechanics fix receipt v2

- Timestamp: 2026-09-18T02:14:00+03:00
- Goal: `20260918-dream-master-ru-artview`
- Step: `R3-systemic-terminology-fix` follow-up
- Supersedes: `handoffs/r3-terminology-fix.md`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Assignment role/state: engineering (`gpt-5.6-terra` at `medium`), completed
- Scoped override: none
- Scope: producer/verifier terminology and mechanics checks plus focused tests only; no working-run artifacts, translation payloads, configurations, acceptance, or canonical plan/status files.

## Result

- Superseding fix: OCR pronoun artifacts `1 am`, `1 have`, and internal prose `1 asked` are removed from numeric-mechanics extraction wherever they occur as standalone tokens. Genuine numeric mechanics remain preserved.
- Superseding fix: an article + capitalized skill + short modifier phrase + mechanic outcome, for example `A Spot Hidden from one of the investigators will notice ...`, is now a required skill context.
- The modifier route is deliberately limited to `from|by|with|for|among`, a bounded punctuation-free phrase, and mechanic outcomes. Capitalized uses outside these patterns remain fail-closed ambiguous.
- Both producer and independent verifier retain matching behavior and shared regressions.

## Files checked or changed

- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/verify_scenario_master_ru.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/docs/plans/20260918-dream-master-ru-artview/handoffs/r3-terminology-fix.md` (prior receipt retained)
- `kb_creator/docs/plans/20260918-dream-master-ru-artview/handoffs/r3-terminology-fix-v2.md`

## Verification and evidence

- `py_compile` passed for both changed scripts.
- Direct new regression selection: `2 passed, 14 subtests passed`.
- Focused producer/verifier suite: `44 passed, 1 skipped, 1 deselected, 44 subtests passed`.
- `git diff --check` passed.

## Blockers and next action

- Platform-unverified: the local pytest environment still lacks `jsonschema`, so the previously identified schema-validation assertion remains unavailable; it is outside this change path.
- Next action: orchestrator reruns Number 7 Dream submission validation/materialization and assigns independent QA on the regenerated candidate.

- Elapsed time: approximately 7 minutes.
- Token use: approximately 3k.
