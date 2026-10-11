# Number 7 Dream OCR-equivalence remediation — inline tag correction receipt

- Timestamp: `2026-09-17T01:50:00+03:00`.
- Goal: `20260916-dream-reconstruction`.
- Scope: bounded Stage 05 audit-normalization correction only. The materializer and its HTML validator were intentionally not changed.
- Result: `_normalized()` now strips only case-insensitive, literal opening/closing `<sup>` and `<sub>` tags before NFKC/casefold/alphanumeric normalization. This permits MinerU text such as `7<sup>th</sup>` and `<sub>p</sub>erform` to compare against plain Markdown while leaving unrelated HTML and tag attributes as reader text rather than silently erasing them.
- Files changed: `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`; `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`; this immutable correction receipt.
- Verification/evidence: bundled Python `py_compile` passed; direct assertions passed for superscript equality, subscript equality, non-stripping of `<em>`, and non-stripping of `<sup class="x">`; `git diff --check` passed.
- Blockers: the local bundled runtime does not include `pytest` or `jsonschema`, so the standard focused and expanded suite remains for the orchestrator's verified runtime.
- Next action: rerun the Dream production Stage 05 audit and resume; keep materializer HTML rejection enabled.
- Elapsed time: approximately 6 minutes.
- Token use: exact role token count unavailable.
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred.
- Assignment state: complete.
- Scoped override: none.
