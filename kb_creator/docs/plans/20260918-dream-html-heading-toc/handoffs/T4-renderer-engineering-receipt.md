# T4 renderer semantic presentation and frontmatter engineering receipt

- Goal / step: `20260918-dream-html-heading-toc` / `T4-renderer-engineering`.
- Scope: only reusable renderer implementation and focused Translator tests; no KB Creator adapter/config, scenario authority/data, generated output, canonical plan/status, commit, or push.
- Result: implemented typed statblock rendering, normalized renderer frontmatter-policy consumption, prose-credit rendering, and source-landing credits-before-TOC ordering.
- Files changed or checked: changed `translator/translator.py` and `translator/tests/test_recovery_support.py`; checked root/Translator instructions, active PLAN/CONTEXT, and R2/R3 receipts.
- Verification / evidence: `python.exe -m unittest translator.tests.test_recovery_support` passed **74 tests**; `python.exe -m py_compile translator/translator.py` passed; `git diff --check -- translator/translator.py translator/tests/test_recovery_support.py` passed. The wider pytest-dependent suites were not runnable in the bundled Python because `pytest` is absent (`ModuleNotFoundError`).
- Implementation evidence: `<!-- semantic-kind: statblock -->` now produces a neutral `<section class="statblock-card" data-semantic-kind="statblock">`; unknown semantic kinds raise `ValueError`; legacy `callout-class` stays an explicit blockquote compatibility route. TOC capture/render/filter/manifest and credits transformation consume `frontmatter_policy` when supplied. Policy `toc_policy.entries` supports the adapter's `source_text` / `target_id` mapping without lexical fallback. Explicit `credits_policy.mode=prose` plus `source_pages` preserves a framed prose credit page without requiring a table.
- Blockers / risks: adapter integration and its output gates remain owned by the adapter task. Existing worktree edits to these same files predated this assignment and were preserved; this receipt does not claim a release decision. Pytest-dependent suites need an environment with declared dev dependencies for full coverage.
- Next action: adapter owner runs the Stage-40 focused adapter tests against the agreed `frontmatter_policy` shape and typed directive, then QA verifies the integrated candidate DOM/manifest.
- Elapsed time: approximately 31 minutes.
- Token use: approximately 10k tokens (contributor estimate).
- Timestamp: `2026-09-18T10:58:08+03:00`.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium; orchestration ownership was not transferred.
- Assignment state: completed locally; platform model unverified.
- Scoped override: none.
