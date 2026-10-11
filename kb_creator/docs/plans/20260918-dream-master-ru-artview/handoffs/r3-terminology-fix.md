# R3 terminology and mechanics fix receipt

- Timestamp: 2026-09-18T02:09:11+03:00
- Goal: `20260918-dream-master-ru-artview`
- Step: `R3-systemic-terminology-fix`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Assignment role/state: engineering (`gpt-5.6-terra` at `medium`), completed
- Scoped override: none
- Scope: scenario-neutral MASTER_RU producer/verifier terminology and mechanics checks only; no working-run artifacts, translation payloads, configurations, acceptance, or canonical plan/status files.

## Result

- Skill-context classification now excludes lowercase prose and ASCII-hyphenated lexical compounds, while retaining labelled skill fields and fail-closed ambiguity for unclear capitalized uses.
- Mechanic context now recognizes `A Spot Hidden will reveal ...` and multi-skill `using Track, Survival or Spot Hidden roles` forms.
- A bad term is only reported if a matching occurrence is not wholly contained in one of its accepted targets; thus `Вождение` is valid inside `Вождение автомобиля` but remains invalid standalone.
- OCR `1 am` / `1 have` at a line or blockquote start is excluded from numeric mechanics extraction; genuine numeric mechanics are retained.
- Producer and independent verifier received matched implementations and parity regressions.

## Files changed

- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/verify_scenario_master_ru.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/docs/plans/20260918-dream-master-ru-artview/handoffs/r3-terminology-fix.md`

## Verification and evidence

- `py_compile` passed for both changed scripts using the repository pytest environment.
- Focused suite passed: `44 passed, 1 skipped, 1 deselected, 43 subtests passed` for `test_scenario_master_ru.py` and `test_verify_scenario_master_ru.py`, excluding only a pre-existing schema-validator test.
- Full selected suite first reached `44 passed, 1 skipped, 43 subtests passed` plus one environment-only failure: `ModuleNotFoundError: No module named 'jsonschema'` in `test_author_submission_is_byte_deterministic_and_schema_valid`.
- `git diff --check` passed.

## Blockers and next action

- Platform-unverified: the local pytest environment lacks `jsonschema`, so the one schema-validation assertion could not run. This does not affect the changed classifier/mechanics paths.
- Next action: orchestrator integrates these scripts, reruns packet/submission materialization, then asks an independent QA role to verify the Number 7 Dream translation candidate.

- Elapsed time: approximately 20 minutes.
- Token use: approximately 7k.
