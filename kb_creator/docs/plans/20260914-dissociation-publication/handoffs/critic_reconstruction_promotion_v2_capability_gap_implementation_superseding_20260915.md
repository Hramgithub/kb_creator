# Superseding critic receipt - reconstruction promotion v2 capability gap implementation

- Timestamp: `2026-09-15T11:42:57+03:00`
- Supersedes: `critic_reconstruction_promotion_v2_capability_gap_implementation_20260915.md`
- Supersession reason: the prior NO-GO was caused by my command-path error. `.tools/python-test-deps` is a flat import root and must be injected through `PYTHONPATH`; `.tools/python-test-deps/bin/pytest.exe` is not a standalone runner.
- Goal id / step: `20260914-dissociation-publication` / `4PF-v2-capability-and-replay-promotion-gap`
- Review kind: `implementation`
- Role: independent critic, policy target `gpt-5.5` at `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: review only the three implementation-scope files and write this superseding receipt; no release review
- Scope: implementation review for live run09 promotion materialization readiness; no candidate/run/source edits, no MinerU/CPU, no materialize, no acceptance, no commit/push
- Verdict for live run09 materialize: **GO**
- Recommendation: the orchestrator may proceed to the explicit live run09 `materialize` step if still desired. This does not authorize reconstruction acceptance, MASTER_EN, publication, release, commit, or push.
- Blockers: none
- Elapsed time for restart pass: approximately 8 minutes
- Token use: unavailable

## Authority Inputs

- Architecture receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_v2_capability_gap_20260915.md`
  - SHA-256 verified: `407630BFAFF25CA145D801CE88DEF489CB494280475BC5BA77E0577DC30CE9B1`
- Engineer receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_capability_gap_20260915.md`
- Active context note checked: `kb_creator/docs/plans/20260914-dissociation-publication/context.md` lines 128-130 document `.tools/python-test-deps` as an isolated ignored test dependency directory for repository-local MinerU Python.
- Candidate file identities:
  - `kb_creator/pipeline/reconstruction_promotion.py`: SHA-256 `36E080C211AF8EAAF9D8C7DFBC4DA84A240681E827915B5D4E11670F42FC5DF4`
  - `kb_creator/tests/test_reconstruction_promotion.py`: SHA-256 `24B0F0893C3EE273A27AA015B1F36DBD3636C28BF541D1A46E96C0F9A5A513B2`
  - `kb_creator/tests/test_reconstruction_promotion_adversarial.py`: SHA-256 `4A1D31B3FDB76B767C08BC83AC78EC7813084E21034C656DEB5BD9DEED8A7285`

## Files Checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_v2_capability_gap_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_capability_gap_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_reconstruction_promotion_v2_capability_gap_implementation_20260915.md`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- Supporting validator context in `kb_creator/pipeline/reconstruction.py`, `kb_creator/pipeline/reconstruction_replay_resume.py`, and `kb_creator/pipeline/mineru_cpu_first.py`
- Read-only run09 authority root: `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09`

## Findings

### P0

None.

### P1

None. The prior P1 is withdrawn: focused regression tests reproduced successfully once `.tools/python-test-deps` was injected through `PYTHONPATH`.

### P2

None. The test suite plus code inspection cover the requested live-run09 gate sufficiently for the next materialize step. This is still not a release review and not an acceptance authorization.

## Verification

### Focused Regression Suite

Command from repo root:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py
```

Result:

```text
92 passed, 1 skipped in 37.35s
SKIPPED [1] kb_creator\tests\test_reconstruction_promotion.py:378: host does not permit an unprivileged symlink fixture
```

### Real Run09 Read-Only Preflight

Command from repo root:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c "from pathlib import Path; import json; from kb_creator.pipeline.reconstruction_promotion import preflight_reconstruction_promotion; root=Path('kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09'); promotion=root/'promotion'; print('before='+str(promotion.exists())); result=preflight_reconstruction_promotion(root); print(json.dumps(result, sort_keys=True)); print('after='+str(promotion.exists()))"
```

Result:

```json
before=False
{"candidate_inventory_sha256": "550BEBDF33074F17DB316C55A447873595B3C507AEC87C0E30D2CF4354AA57EF", "run_identity_sha256": "887CEEAA0613404B6481221E06A61AEB20A492021E5A7BB8AF27646A493BC620", "run_kind": "replay_v2", "schema": "kb_creator.reconstruction_promotion_preflight.v1", "state": "promotion_preflight_passed"}
after=False
```

Independent `Test-Path kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion` returned `False`.

## Implementation Assessment

- Exact support matrix: legacy v1, direct v2, and replay v2 have explicit dispatch and validation paths.
- Fail-closed dispatch markers: any replay marker selects replay-v2 validation; malformed or missing replay authority fails closed rather than falling back to direct-v2.
- v2 capability semantics: fixed provider order and required CPU-ready / optional CUDA-ready-or-supported-unavailable semantics are enforced.
- Optional CUDA: unavailable optional providers with supported reason and no receipt do not block run09 preflight.
- Ready-provider/tool drift: ready provider profiles and common tools are checked against current identities for replay-v2 without applying direct-run implementation inventory to replay runs.
- Replay canonical validators: replay prefix, review queue, validated submission, Stage05, Stage06, and audit-v3 recomputation are reused rather than reimplemented loosely.
- v3 audit/provenance: read-only run09 preflight validates the stored audit/provenance authorities and flat Stage06 candidate inventory.
- Flat candidate: run09 preflight binds candidate inventory SHA-256 `550BEBDF33074F17DB316C55A447873595B3C507AEC87C0E30D2CF4354AA57EF`.
- Replay evidence/package closure and acceptance preflight reuse: code inspection and focused tests cover replay evidence copying/validation and the acceptance path rerunning preflight before writing a receipt.
- Deterministic errors and legacy preservation: focused/adversarial tests pass; no regression found in legacy safeguards.

## Non-Actions Confirmed

- No implementation edits.
- No run07/run08/run09/candidate/source mutation.
- No MinerU/CPU extraction.
- No live run09 materialize.
- No acceptance receipt.
- No commit or push.

## Recommendation

Proceed only to the explicit live run09 materialize step, if the orchestrator chooses to do so. Stop again before any reconstruction acceptance, MASTER_EN generation, publication, release review, commit, or push.
