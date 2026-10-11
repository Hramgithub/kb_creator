# Engineer receipt: reconstruction promotion schema path parity

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PF-reconstruction-promotion-schema-path-parity`
- Role: engineering
- Requested policy role/model/effort: `gpt-5.6-sol`, `high` under the
  user-scoped engineering override for this goal
- Actual platform model/effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `user-overridden-platform-unverified`
- Scoped override: engineering role only, `gpt-5.6-sol` at `high`
- Timestamp: `2026-09-14T12:51:57Z`
- Elapsed time: approximately 22 minutes
- Token use: unavailable

## Scope and result

Closed the independent critic's sole P2 finding for standalone JSON Schema
consumers of the three reconstruction-promotion contracts. The schemas now use
the same canonical portable-relative-path constraints as runtime
`_safe_relative`: a path must be non-empty and trimmed, use forward-slash
separators, contain no empty, `.` or `..` component, and contain no absolute,
drive/ADS/colon, backslash/UNC, NUL, Windows reserved-device, or component
trailing-dot/space form.

The inventory retains its exact four fixed role paths. The source-identity
contract and source basenames use the same portable-path definition plus their
existing single-component restriction. Valid normalized package paths remain
admitted, including nested paths, dot-prefixed ordinary names, internal spaces,
and non-reserved names such as `com10` and `lpt0`.

No production runtime, reconstruction run, source input, acceptance artifact,
publication artifact, dependency, canonical plan/context/status, README, live
artifact, or Git state was changed.

## Files changed by this step

- `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_source_identity.v1.schema.json`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- this receipt

`kb_creator/tests/test_reconstruction_promotion.py` was read and executed but
not edited by this step.

## Verification

- Real `jsonschema 4.25.1` was imported from
  `.tools/python-test-deps/jsonschema/__init__.py` by the repository-local
  `.tools/MinerU/.venv/Scripts/python.exe`.
- All three edited schema files parse as JSON and pass
  `Draft202012Validator.check_schema` in the parity tests.
- Focused runtime/schema path matrix:
  `64 passed, 7 deselected in 1.49s`.
- Complete reconstruction-promotion suite:
  `86 passed, 1 skipped in 37.57s`.
- Expanded reconstruction-promotion, reconstruction control-plane,
  publication control-plane/contracts/registry, contract-authoring, and
  scenario-contract compatibility suite at the same schema implementation:
  `317 passed, 2 skipped in 183.40s`.
- After that expanded run, two test-only terminal/leading whitespace aliases
  were added to the matrix; the final focused and complete promotion results
  above include those additions.

The adversarial matrix covers empty and outer-whitespace paths, drive-relative
and drive-absolute forms, UNC/backslash forms, POSIX absolute paths, colon/ADS,
NUL, reserved Windows device names, trailing dot/space, repeated separators,
trailing separators, leading `./`, embedded `.` and `..`, and leading
traversal. Each alias is rejected by runtime and independently by each of the
three complete schemas. A complementary allow matrix protects normalized paths
from accidental over-restriction.

## Blockers and next action

No engineering blocker remains in this bounded P2 scope. The bridge may return
to the independent critic for closure confirmation. This receipt is schema and
test evidence only; it is not reconstruction acceptance, publication
acceptance, or a release decision.
