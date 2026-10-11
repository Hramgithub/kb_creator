# Critic receipt - reconstruction promotion v2 capability gap implementation

- Timestamp: `2026-09-15T11:39:40+03:00`
- Goal id / step: `20260914-dissociation-publication` / `4PF-v2-capability-and-replay-promotion-gap`
- Review kind: `implementation`
- Role: independent critic, policy target `gpt-5.5` at `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: review only the three implementation-scope files and write this receipt; no release review
- Scope: implementation review for live run09 promotion materialization readiness; no candidate/run/source edits, no MinerU/CPU, no materialize, no acceptance, no commit/push
- Verdict for live run09 materialize: **NO-GO pending reproducible focused test execution**
- Recommendation: do not run live run09 `materialize` until the focused regression suite can be independently reproduced in the repo-local test environment, or the orchestrator explicitly accepts that verification gap. The implementation itself passed syntax/import inspection and real run09 read-only preflight.
- Elapsed time: approximately 33 minutes
- Token use: unavailable

## Authority Inputs

- Architecture receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_v2_capability_gap_20260915.md`
  - SHA-256 verified: `407630BFAFF25CA145D801CE88DEF489CB494280475BC5BA77E0577DC30CE9B1`
- Engineer receipt: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_capability_gap_20260915.md`
- Candidate file identities:
  - `kb_creator/pipeline/reconstruction_promotion.py`: `88903` bytes, SHA-256 `36E080C211AF8EAAF9D8C7DFBC4DA84A240681E827915B5D4E11670F42FC5DF4`
  - `kb_creator/tests/test_reconstruction_promotion.py`: `24948` bytes, SHA-256 `24B0F0893C3EE273A27AA015B1F36DBD3636C28BF541D1A46E96C0F9A5A513B2`
  - `kb_creator/tests/test_reconstruction_promotion_adversarial.py`: `10686` bytes, SHA-256 `4A1D31B3FDB76B767C08BC83AC78EC7813084E21034C656DEB5BD9DEED8A7285`

## Files Checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_reconstruction_promotion_v2_capability_gap_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_reconstruction_promotion_v2_capability_gap_20260915.md`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- Supporting validator context in `kb_creator/pipeline/reconstruction.py`, `kb_creator/pipeline/reconstruction_replay_resume.py`, and `kb_creator/pipeline/mineru_cpu_first.py`
- Read-only run09 authority root: `kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09`

## Findings

### P0

None.

### P1

1. Focused regression suite is not independently reproducible in the current repo-local test environment.
   - The engineer receipt reports `.tools/MinerU/.venv/Scripts/python.exe -m pytest -q -rs ...` as `92 passed, 1 skipped`.
   - Current reproduction with `.tools/MinerU/.venv\Scripts\python.exe`, `.tools\python\cpython-3.12.14-windows-x86_64-none\python.exe`, `.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe`, and `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` all failed with `No module named pytest`.
   - Repo-local `.tools\python-test-deps\bin\pytest.exe` exists but failed with `ModuleNotFoundError: No module named '_pytest'`.
   - Because this packet explicitly required focused test reproduction before live run09 materialize, this is a blocking verification gap for the live write step.

### P2

1. The added adversarial tests are narrower than the architecture receipt's exact test matrix. They cover real run09 read-only preflight, a few v2 capability mutations, and one replay-marker dispatch case, but do not visibly cover every requested replay authority mutation, optional-ready CUDA positive row, deleted bridge as a direct-v2 fallback attack, acceptance preflight reuse, or extra flat/nested candidate branch attacks. The implementation may still fail closed, but the committed test surface does not prove the full matrix.

## Evidence

### Implementation Review

- `reconstruction_promotion.py` now has explicit `legacy_v1`, `direct_v2`, and `replay_v2` dispatch.
- Replay detection is fail-closed from `replay/`, `review/validated-submission-v2`, Stage01-04 replay stage manifests, or Stage05/06 replay downstream manifests.
- Legacy v1 behavior is preserved: root `skip.json`, unavailable capability, injected capability, and non-available capability remain rejecting paths.
- v2 capability semantics enforce fixed provider order `pipeline_cpu`, `hybrid_cuda`, `vlm_cuda`; CPU must be ready; optional CUDA may be ready or unavailable only for supported reasons without a verification receipt.
- Replay v2 preflight composes existing replay validators:
  - `validate_replayed_prefix`
  - `validate_replay_review_queue`
  - `load_replay_submission`
  - `_validate_downstream_stage` for Stage05 and Stage06
  - `build_replay_audit` equality against stored Stage05 audit
  - flat Stage06 candidate/provenance validation
- Package validation recognizes replay prefix stages and replay downstream stages, copies intake/bridge/rebase evidence, validates no acceptance inference, and normalizes Stage05/06 manifest digests through the existing public stage-record shape.
- `record_reconstruction_acceptance` reruns `_promotion_preflight` before validating package and writing the exclusive acceptance receipt.

### Read-Only Run09 Preflight

Command:

```text
.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe -c "from pathlib import Path; import json; from kb_creator.pipeline.reconstruction_promotion import preflight_reconstruction_promotion; root=Path('kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09'); promotion=root/'promotion'; print('before='+str(promotion.exists())); result=preflight_reconstruction_promotion(root); print(json.dumps(result, sort_keys=True)); print('after='+str(promotion.exists()))"
```

Result:

```json
before=False
{"candidate_inventory_sha256": "550BEBDF33074F17DB316C55A447873595B3C507AEC87C0E30D2CF4354AA57EF", "run_identity_sha256": "887CEEAA0613404B6481221E06A61AEB20A492021E5A7BB8AF27646A493BC620", "run_kind": "replay_v2", "schema": "kb_creator.reconstruction_promotion_preflight.v1", "state": "promotion_preflight_passed"}
after=False
```

Independent final `Test-Path kb_creator\working\dissociation\reconstruction\20260915-cpu-replay-09\promotion` returned `False`.

### Syntax And Probe Checks

- Syntax check passed for all three candidate files with `.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe`.
- Temporary-copy probes, not live run09:
  - corrupted run identity failed closed as `reconstruction_stage_chain_invalid: invalid run authority`
  - deleted replay bridge failed closed as `reconstruction_stage_chain_invalid: invalid_json: ...\replay\bridge.json`
  - corrupted capability reason without recomputing run identity failed closed as `reconstruction_stage_chain_invalid: invalid run authority`

## Commands Attempted

Passed:

```text
.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe -c "import ast,pathlib; [ast.parse(...)] ; print('syntax-ok')"
.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe -c "... preflight_reconstruction_promotion(run09) ..."
Get-FileHash kb_creator\pipeline\reconstruction_promotion.py, kb_creator\tests\test_reconstruction_promotion.py, kb_creator\tests\test_reconstruction_promotion_adversarial.py -Algorithm SHA256
```

Failed due to missing/broken test runner:

```text
.tools\MinerU\.venv\Scripts\python.exe -m pytest -q -rs kb_creator\tests\test_reconstruction_promotion.py kb_creator\tests\test_reconstruction_promotion_adversarial.py
.tools\python\cpython-3.12.14-windows-x86_64-none\python.exe -m pytest -q -rs kb_creator\tests\test_reconstruction_promotion.py kb_creator\tests\test_reconstruction_promotion_adversarial.py
.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe -m pytest -q -rs kb_creator\tests\test_reconstruction_promotion.py kb_creator\tests\test_reconstruction_promotion_adversarial.py
C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q -rs kb_creator\tests\test_reconstruction_promotion.py kb_creator\tests\test_reconstruction_promotion_adversarial.py
.tools\python-test-deps\bin\pytest.exe -q -rs kb_creator\tests\test_reconstruction_promotion.py kb_creator\tests\test_reconstruction_promotion_adversarial.py
```

## Blockers

- Blocker for live run09 materialization authorization: focused regression tests could not be independently reproduced from existing repo-local Python/test tooling in this session.

## Recommendation

Do not proceed to live run09 materialization from this receipt alone. First restore or identify the repo-local pytest environment that can reproduce the focused regression command, then rerun:

```text
pytest -q -rs kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py
```

If that suite reproduces the engineer receipt and run09 read-only preflight remains `promotion_preflight_passed` with `promotion/` absent before and after, this critic sees no code-level P0/P1 blocker in the inspected implementation for the materialize step. This is not a release review and does not authorize acceptance, MASTER_EN, publication, or release inference.
