# Engineer receipt: reconstruction promotion path remediation

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PF-reconstruction-promotion-path-remediation`
- Role: engineering contributor
- Requested policy role/model/effort: `gpt-5.6-sol`, `high` (user-scoped override)
- Actual platform model/effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `user-overridden-platform-unverified`
- Scoped override: engineering implementation for this goal uses
  `gpt-5.6-sol` at `high`
- Timestamp: `2026-09-14T11:49:16Z`
- Elapsed time: approximately 15 minutes
- Token use: unavailable

## Scope and result

Closed the bounded P1 lexical portable-path defect reported by QA. The
promotion bridge now accepts only an exact normalized forward-slash relative
serialization. It rejects raw empty and dot components before any path is
joined or resolved, so repeated separators, leading or embedded `./`, and
trailing separators cannot alias a canonical package path.

The original Windows guards remain active for absolute paths, drive-relative
paths, UNC/backslash forms, ADS/colon syntax, NUL, traversal, reserved device
names, and trailing dot or space components. No acceptance, publication run,
live reconstruction artifact, canonical plan/context/status, README, Git
state, or scenario content was changed.

## Files changed

- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_path_remediation_20260914.md`

`kb_creator/tests/test_reconstruction_promotion.py` was verified but did not
require modification.

## Defect-class and validator audit

- Seed cases `content//x.json` and `content/./x.json` now fail with
  `unsafe_promotion_path`.
- Equivalent aliases were added to the adversarial matrix: triple separators,
  trailing single/double separators, leading `./`, terminal `/.`, and embedded
  dot components.
- `_safe_inventory` routes every file-inventory path through
  `_safe_relative`; this covers packaged stage outputs, original candidate,
  content, package closure, and observed deterministic package inventories.
- `_identity_at` routes manifest, review, stage, QA, fidelity, inventory-role,
  and acceptance identity records through `_safe_relative` before resolution.
- Candidate asset-manifest `stored_path` values use `_safe_relative` directly.
- Generated identity records use `_record`, which validates the generated
  relative serialization. Fixed role paths and portable provenance page paths
  are compared to exact canonical literals or to already validated identity
  records, leaving no normalization-based alias route in the promotion module.

## Verification evidence

- Full adversarial QA suite:
  `25 passed in 3.54s`.
- Promotion bridge plus adversarial suites with skip reason:
  `40 passed, 1 skipped in 23.29s`.
- Combined bridge/reconstruction/publication targeted suites
  (`test_reconstruction_promotion_adversarial.py`,
  `test_reconstruction_promotion.py`,
  `test_reconstruction_control_plane.py`,
  `test_publication_control_plane.py`, `test_publication_contracts.py`, and
  `test_publication_registry_e2e.py`):
  `97 passed, 1 skipped in 127.51s`.
- `py_compile` passed for the promotion module and both promotion test files.

## Residual blockers and next action

- The sole skip is the pre-existing host limitation at
  `test_reconstruction_promotion.py:376`: this Windows host does not permit an
  unprivileged symlink fixture. Runtime non-reparse checks remain active.
- Junction/mount/reparse race evidence on a host that can create those objects
  remains outside this bounded lexical remediation.
- No P1 remains in the tested lexical normalization-alias class. Independent
  implementation review is still required before a fresh live Dissociation
  reconstruction run or user acceptance; this engineering receipt is not an
  acceptance or release decision.

Next action: assign the remediated bridge and the expanded adversarial suite to
the independent critic for the required implementation closure review.
