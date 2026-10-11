# QA receipt: reconstruction promotion bridge

- Goal: `20260914-dissociation-publication`
- Assignment: bounded QA, reconstruction promotion deferred attack matrix
- Scope: `kb_creator/tests/test_reconstruction_promotion_adversarial.py` and
  existing `test_reconstruction_promotion.py`; production code and canonical
  plan/status/context were not modified.
- Result: QA incomplete; 2 lexical path-validation defects remain. No release
  or acceptance decision.
- Files checked: architect bridge spec, engineer bridge receipt,
  `kb_creator/pipeline/reconstruction_promotion.py`, focused bridge tests,
  relevant contracts and plan.
- Verification: focused suite before final assertion adjustment: `13 passed,
  1 skipped, 3 failed`; after adjustment, expected result remains `14 passed,
  1 skipped, 2 failed` because the two failures intentionally expose defects:
  `_safe_relative("content//x.json")` and `_safe_relative("content/./x.json")`
  return successfully. Existing bridge suite had `15 passed, 1 skipped` per
  engineer receipt; this QA run did not alter production behavior.
- Defects: P1 candidate/package portable-path boundary accepts empty or dot
  path components after `PurePosixPath` normalization. Minimal repro is the
  two direct calls above; expected `ReconstructionPromotionError` with
  `unsafe_promotion_path`.
- Additional coverage added: ADS/drive-relative/UNC/backslash/device/trailing
  whitespace and case-collision paths; extra package and inventory drift;
  stage producer mutation; decision snapshot byte drift. These passed or
  failed closed as expected. Reparse/junction/native race remains host-limited;
  existing symlink test is an explicit host skip.
- Blockers: the two P1 findings require production remediation and rerun;
  no release decision is possible. Full five-stage/extra-stage and complete
  candidate mutation matrix remains bounded rather than exhaustive.
- Next action: engineering owner should close the lexical component checks;
  then rerun this focused suite and independent review. QA does not repair.
- Elapsed time: approximately 20 minutes.
- Token use: unavailable.
- Timestamp: `2026-09-14T12:10:00Z`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium.
- Assignment state: `user-overridden-platform-unverified` (bounded QA role;
  actual platform identity unavailable).
- Scoped override: none for QA; repository role contract assigns
  `gpt-5.6-luna` at low effort.
