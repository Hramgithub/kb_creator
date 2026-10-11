# U8 normal fidelity QA receipt v05

- Timestamp: 2026-10-04 23:20:37 UTC / 2026-10-05 02:20:37 Europe/Moscow.
- Goal: `20261004-user-docx-review`; bounded QA of frozen U8v04 normal DOCX fidelity repair.
- Role: QA `gpt-6-luna` / medium (platform unverified). Policy owner/orchestrator `/root`, gpt-6-sol / medium. Scoped override: none.
- Assignment state: finite prepared regression and R1–R4 focused coverage complete. Not release acceptance; independent critic remains required.
- Elapsed time: approximately 6 minutes from assignment to handoff. Token use unavailable.

## Result

Rehashed the full 43-file freeze before/after tests: 43/43 match; zero mismatches; manifest SHA-256 `9A948C1264D64A48E551221E5604FC6435F2641A9B50AAEE13079C5F657C8BEC`. Rehashed the six reviewed originals, three fixed candidate DOCX, canonical glossary, and nine retired paths after tests; all hashes unchanged and 9/9 retired HTML/PDF paths absent.

Full prepared 19-module suite: **239 passed, 14 subtests, 1 pre-existing unrelated Microsoft Word COM skip, 0 failures/errors**, 140.07s. Four focused direct R1–R4/positive-control modules: **48 passed, 0 skips/failures/errors**, 11.18s. The permitted runner is the bundled Codex interpreter plus existing pytest 9.0.2 library under the local `.tools` site-packages path; no install or repository interpreter. Normal sandbox attempts hit actual pytest temp-directory cleanup WinError 5; exact scoped suites passed via elevated retry in distinct fresh roots. No failed root or log was reused, deleted, or overwritten.

## Evidence/files

- Detailed report and seam matrix: `audit/fidelity-qa-v05/U8-normal-fidelity-qa-v05.md`.
- Exact runner identity and full 19-module/focused four-module argv/log manifest: `audit/fidelity-qa-v05/pytest-run-manifest-v01.json`.
- Persistent outputs: `audit/fidelity-qa-v05/pytest-regression-elevated-v01.log` (SHA-256 `5138CD2EBF0FE8896DA71E72B29276004927146075FF84B6751428CAE4AC2F3E`); `audit/fidelity-qa-v05/pytest-r1-r4-elevated-v01.log` (SHA-256 `E46CDD83EB97068367803661FDED45D77270137408D1062D6A99C4B2F0DC9442`). Failed normal-sandbox logs and all dedicated scratch roots are retained in this owned audit directory.
- Class coverage includes: whole operand/protected-field binding and valid stat controls; page/story/book/entity/occurrence/source-render binding; actual accepted CSV and closed book overlay resolution plus rejected invented/review-required/unsupported authority; same-paragraph actual Word graphic order; valid positives; public prewrite rejection; exact-plan offline verification; four closed contract schemas. Exact test functions and scope limits are in the report.
- Current candidate book QA is inherited by exact identity only. No real current book normal-route replay or page re-review was performed. XML/test success does not promote `verified_pending_visual_review` / `needs_output_review` to visual or semantic acceptance.

## Next action

Main owns orchestration, reconciliation and release. Independent critic review is separate and required; no final approval or user acceptance is issued here. No code/tests/fixtures/schema/books/sources/latest/old evidence/canonical files were changed.
