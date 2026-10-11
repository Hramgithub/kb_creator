# Critic receipt - reconstruction promotion v2 materialize validation remediation closure

- Timestamp: `2026-09-15T11:53:21+03:00`
- Goal id / step: `20260914-dissociation-publication` / `4PF-v2-materialize-validation-remediation`
- Review kind: `implementation`
- Role: independent critic, policy target `gpt-5.5` at `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: review the materialize-validation remediation only; no release review
- Scope: three scoped promotion files plus read-only validation of the existing run09 package
- Verdict for recording acceptance on existing validated run09 package: **GO**
- Recommendation: the orchestrator may proceed to the separate explicit `record-acceptance` step against the existing validated run09 package if user authority is present. Do not rerun live materialization; do not infer acceptance, MASTER_EN, publication, release, commit, or push.
- Blockers: none
- Elapsed time: approximately 14 minutes
- Token use: unavailable

## Authority Inputs

- Architecture receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_v2_capability_gap_20260915.md`
- Prior engineer receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_capability_gap_20260915.md`
- Prior critic receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_reconstruction_promotion_v2_capability_gap_implementation_superseding_20260915.md`
- New engineer remediation receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_materialize_validation_remediation_20260915.md`

## Files Checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_v2_capability_gap_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_capability_gap_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_reconstruction_promotion_v2_capability_gap_implementation_superseding_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_materialize_validation_remediation_20260915.md`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- Existing package root: `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09/promotion/reconstruction-upstream-v1`

## Candidate File Identities

- `kb_creator/pipeline/reconstruction_promotion.py`: SHA-256 `85EB119B59F7ADCE3DA92DAB3273F2D4105F14BB6AE011D686948923FB0612E3`
- `kb_creator/tests/test_reconstruction_promotion.py`: SHA-256 `1D7210C21E0EFB1150AFADB77CC283421640A25B0920381524BA367A1A7E8935`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`: SHA-256 `1BCE1F73C55E9FC78DDF4E2691036A3E97F2194DF251BDCA5C86743F4A7ED99B`

These match the new engineer remediation receipt.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Implementation Assessment

- The reported P0 is fixed: packaged replay Stage01-04 validation now uses the canonical `kb_creator.stage_manifest.v2` whole-manifest seal through `validate_seal(stage, "reproducible_sha256")`, while legacy/direct stages keep the existing reproducible-body digest check.
- Stage05/06 replay downstream records still validate through `manifest_sha256`, preserving the prior replay-v2 normalization.
- The reported P1 is fixed: post-publish validation failures are now inside rollback handling.
- Rollback is identity-safe:
  - cleanup is limited to the fixed `promotion/reconstruction-upstream-v1` topology;
  - reparse/symlink paths are rejected;
  - the full deterministic package inventory must exactly match the just-published inventory before deletion;
  - a preexisting package is rejected before publish and is not eligible for rollback;
  - unrelated entries in an existing `promotion/` directory are preserved.
- `record_reconstruction_acceptance` still reruns `_promotion_preflight`, validates the package without acceptance, writes the acceptance receipt exclusively, and removes only the exact newly written receipt if final acceptance validation fails.

## Verification

### Focused Regression Suite

Command from repo root:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py
```

Result:

```text
95 passed, 1 skipped in 51.26s
SKIPPED [1] kb_creator\tests\test_reconstruction_promotion.py:378: host does not permit an unprivileged symlink fixture
```

### Targeted Rollback Probe

Command:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_reconstruction_promotion_adversarial.py::test_post_publish_validation_fault_rolls_back_only_current_package
```

Result:

```text
1 passed in 2.06s
```

This test injects a post-publish validator failure, verifies rollback removes only the package created by that invocation, preserves an unrelated `promotion/unrelated.keep`, rejects a preexisting package with `promotion_path_exists`, and verifies the preexisting sentinel remains unchanged.

### Existing Run09 Package Validation

Command:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c "from pathlib import Path; from kb_creator.pipeline.reconstruction_promotion import validate_reconstruction_package, ACCEPTANCE_NAME, INVENTORY_NAME; from kb_creator.pipeline.identity import file_identity; package=Path('kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09/promotion/reconstruction-upstream-v1'); before=file_identity(package/INVENTORY_NAME); inventory, acceptance=validate_reconstruction_package(package, require_acceptance=False); after=file_identity(package/INVENTORY_NAME); print('validation=pass'); print('inventory_sha256='+inventory['inventory_sha256']); print('inventory_file_sha256='+after['sha256']); print('inventory_unchanged='+str(before==after)); print('acceptance_is_none='+str(acceptance is None)); print('acceptance_exists='+str((package/ACCEPTANCE_NAME).exists())); print('manifest_file_sha256='+file_identity(package/'RECONSTRUCTION_MANIFEST.json')['sha256'])"
```

Result:

```text
validation=pass
inventory_sha256=7D6E05DA0E0F4CF71A5A89A2EEFC76C90D70EF001D5837DAEFF28BF59689C964
inventory_file_sha256=9B7F6D45EABDD4136350912B0BDCD320A2808B9516BAEA1CBFAD7924616B2A80
inventory_unchanged=True
acceptance_is_none=True
acceptance_exists=False
manifest_file_sha256=5427629F7D7BE0EB8D17D0E1EE98363F00B4040FD1CB135732A8AE8231603279
```

Independent `Test-Path kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion\reconstruction-upstream-v1\RECONSTRUCTION_ACCEPTANCE.json` returned `False`.

## Non-Actions Confirmed

- No implementation edits.
- No live materialize.
- No acceptance recording.
- No run07/run08/run09 candidate/source mutation.
- No MinerU/CPU execution.
- No commit or push.

## Closure

The remediation closes the materialize-validation failure and the post-publish rollback gap for the reviewed implementation scope. The existing run09 package is valid and unaccepted. The next permitted action is a separate explicit acceptance-recording step, subject to user/orchestrator authority.
