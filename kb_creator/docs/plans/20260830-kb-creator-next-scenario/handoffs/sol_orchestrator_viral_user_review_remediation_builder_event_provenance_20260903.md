# Viral v2 builder event-provenance completion

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-builder-event-provenance`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_verifier_semantic_gates_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_SEMANTIC_GATES`

## Objective and ownership

Complete candidate provenance so an independent verifier can bind every
declared event and structured child to exact final `MASTER_EN.md` bytes. Do not
change verifier or real artifacts.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_builder_event_provenance_20260903.md`

You are not alone in the worktree. Preserve all other changes.

## Required provenance

For every v2 event, emit independently consumable fields after final asset
placement:

- event id/type/page/order key/anchor/fragment id;
- representation and stable canonical declared-content SHA-256;
- exact source range identity already required;
- `contains` for structured units, absent elsewhere;
- emitted state; for reader-emitted events, exact final character and UTF-8 byte
  start/end plus SHA-256 of that final slice;
- explicit suppressed/non-reader state for non-emitted asset events;
- the final emitted identity for reader asset markers at their relocated
  position, not their old placeholder;
- no ambiguous first-occurrence binding: fail closed if the event slice cannot
  be uniquely/monotonically bound in declared source order.

The provenance must remain deterministic and contain no absolute path/time/root
noise. Add tests for normal text, repeated-looking content disambiguated by
monotonic order, structured contains, relocated reader asset, suppressed asset,
offset/hash consistency and deterministic two-root equality. Retain v1 and all
prior builder tests.

Run builder tests and `py_compile`. Write the exact receipt and return the token
only when final candidate bytes are fully bound.

No verifier/config/evidence/source/real candidate/Git/Step 8A changes.
