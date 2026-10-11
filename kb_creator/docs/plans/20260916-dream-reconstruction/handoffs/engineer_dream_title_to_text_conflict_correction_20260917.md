# Number 7 Dream title-to-text conflict correction — engineering receipt

- Timestamp: `2026-09-17T01:55:00+03:00`.
- Goal: `20260916-dream-reconstruction`.
- Scope: bounded materializer conflict-resolution correction only. No source, run, decision, status, Git, publication, acceptance, or release artifact was changed.
- Result: implemented a fail-closed resolver for `title_to_text_downgrade` only. It resolves exactly one selected, nonempty conflicting text unit only when that exact text is an ATX heading in the decision Markdown, `review.visual_reviewed` is true, and `review.notes` contains the exact pre-existing `title override: <text>; reason: ...` evidence. All other conflict kinds and every missing/ambiguous evidence case retain the existing unresolved-conflict block.
- Files changed: `kb_creator/scripts/materialize_mineru_ai_merge.py`; `kb_creator/tests/test_materialize_mineru_ai_merge.py`; this immutable correction receipt.
- Verification/evidence: bundled Python `py_compile` passed. Direct focused checks passed for the approved exact heading override and for rejection of missing heading, unreviewed decision, malformed override evidence, another conflict kind, and two selected conflicting units. `git diff --check` passed.
- Blockers: the local bundled runtime lacks `pytest`; the orchestrator must run the standard focused and expanded materializer/replay suites with the verified project runtime.
- Next action: run the Dream replay-v3 preflight/resume with its page-10 decision evidence and confirm the candidate reaches the next gate without changing any non-title conflict behavior.
- Elapsed time: approximately 12 minutes.
- Token use: exact role token count unavailable.
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred.
- Assignment state: complete.
- Scoped override: none.
