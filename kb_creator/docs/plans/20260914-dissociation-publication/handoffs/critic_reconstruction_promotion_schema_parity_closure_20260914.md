# Critic receipt: reconstruction promotion schema path parity closure

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4PF-reconstruction-promotion-schema-path-parity-closure`
- Review kind: `implementation`
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-14T12:56:29Z`
- Elapsed time: approximately 12 minutes
- Token use: unavailable; no active runtime goal was exposed to this reviewer

## Scope

Reviewed the bounded P2 closure for JSON Schema Draft 2020-12/runtime path
parity in the reconstruction-promotion bridge. This review covered the current
worktree candidate only and did not edit implementation, schemas, tests, source,
run artifacts, acceptance artifacts, publication artifacts, canonical plan,
canonical context, project status, release files, or Git state.

This is not reconstruction acceptance, not publication acceptance, not a release
review, and not a transfer of orchestration ownership.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_bridge_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_reconstruction_promotion_bridge_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_schema_parity_20260914.md`
- `kb_creator/contracts/reconstruction_upstream_inventory.v1.schema.json`
- `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
- `kb_creator/contracts/reconstruction_source_identity.v1.schema.json`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`

## Evidence

- Static review confirmed runtime `_safe_relative` requires a non-empty trimmed
  string, forward slash separators, no absolute or drive-rooted form, no
  backslash, colon, ADS, NUL, empty component, `.`, `..`, Windows reserved device
  basename, or trailing dot/space component.
- Static review confirmed the three promotion schemas now share a closed
  `relative_path` pattern that rejects the same lexical alias classes, including
  the prior `content//x.json` schema gap.
- Static review confirmed the inventory schema still exposes exactly four fixed
  artifact roles and paths: `reconstructed_en`,
  `reconstruction_manifest`, `reconstruction_qa`, and `source_identity`.
- Static review confirmed normalized intended portable paths remain admitted by
  the tests and pattern, including nested paths, `.hidden`, internal spaces,
  `contributor.json`, `com10.json`, `lpt0.json`, and `name..json`.
- Static review confirmed the promotion runtime still validates package topology,
  exact four-role mapping, package closure, source identity, six ordered stages,
  QA/fidelity evidence, separate acceptance receipt, and publication preflight
  consumption of an exact accepted bridge.
- Focused test command:
  `$env:PYTHONPATH='.tools/python-test-deps'; & '.tools/MinerU/.venv/Scripts/python.exe' -m pytest kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- Focused test result: `86 passed, 1 skipped in 40.78s`.
- Test environment: Windows, repository-local `.tools/MinerU/.venv/Scripts/python.exe`,
  Python `3.12.14`, pytest `9.1.1`, `PYTHONPATH=.tools/python-test-deps`.
- The one skipped test is the existing host-conditional symlink/reparse fixture
  case; it does not change the lexical schema/runtime closure decision.

## Findings

### P0

None found.

### P1

None found.

### P2

None found in the assigned schema/runtime path-parity closure scope.

The earlier P2 is closed: the standalone Draft 2020-12 schemas and runtime guard
now reject empty path components and the other reviewed noncanonical portable
path aliases while preserving allowed normalized paths.

## Blockers

No blocker remains in this bounded closure scope.

Residual limitations outside this closure remain unchanged: this is not a live
Dissociation reconstruction run, not user reconstruction acceptance, not
publication acceptance, and not release approval.

## Recommendation

Accept the 4PF P2 schema/runtime path-parity closure. The reconstruction
promotion bridge may proceed under the prior implementation-review limits:
materialization still stops at `candidate_awaiting_reconstruction_acceptance`,
acceptance remains a separate main-orchestrator/user decision, publication
preflight still requires the exact accepted bridge, and any later candidate
mutation requires fresh review evidence where applicable.
