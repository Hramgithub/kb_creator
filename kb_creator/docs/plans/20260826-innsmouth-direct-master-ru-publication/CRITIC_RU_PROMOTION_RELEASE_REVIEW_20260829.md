# Immutable handoff receipt: MASTER_RU promotion release review

- review_kind: release
- reviewer role: independent `gpt-5.5` critic, medium
- implemented_or_materially_designed_candidate: no
- orchestration ownership: not transferred; repository policy owner remains `gpt-5.6-sol`
- assignment state: non-frozen pre-commit Git save-point candidate; promoted RU package is present as an untracked repository input candidate
- scoped override: critic may write only this receipt; no production, test, plan, context, project status, or release candidate implementation edits
- verdict: REMEDIATION_REQUIRED for the RU save-point only; HTML/PDF not reviewed
- timestamp: 2026-08-29T02:56:17.2881457+03:00
- elapsed_time: approx 18 minutes
- token_use: exact unavailable in subagent runtime; approx 12000

## Files checked

- `kb_creator/scripts/freeze_innsmouth_master_ru_repo_input.py`
- `kb_creator/tests/test_freeze_innsmouth_master_ru_repo_input.py`
- `kb_creator/tests/test_innsmouth_source_to_artifacts.py`
- `kb_creator/inputs/innsmouth/master_ru/README.md`
- `kb_creator/inputs/innsmouth/master_ru/PIPELINE.md`
- `kb_creator/inputs/innsmouth/master_ru/accepted_20260829/MASTER_RU.md`
- `kb_creator/inputs/innsmouth/master_ru/accepted_20260829/MASTER_RU.acceptance.json`
- `kb_creator/inputs/innsmouth/master_ru/accepted_20260829/assets/*`
- `kb_creator/inputs/innsmouth/master_en/accepted_20260829/MASTER_EN.acceptance.json`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/plan.md`
- `kb_creator/docs/plans/20260826-innsmouth-direct-master-ru-publication/context.md`

## Candidate revision and Git scope

- worktree: `D:\NRI\.worktrees\innsmouth-master-en-main`
- branch: `codex/innsmouth-master-en-main`
- HEAD: `a7b2b21587a852cf7503f0d20d07f09a331c5b7a` (`a7b2b215 Promote strict Innsmouth MASTER_EN pipeline`)
- status: branch is ahead of origin by 1 commit; scoped dirty tree contains the expected modified docs/status/TOC test plus untracked RU input package, RU promotion script, and RU promotion tests.
- `git diff --check`: passed with no output.
- no commit, staging, push, or implementation edit was performed by this critic.

## Evidence

- Promoted RU identity independently checked with `Get-Item` and `Get-FileHash`:
  - `MASTER_RU.md`: 195411 bytes, SHA-256 `013220A6115EBFF7AFAF557E501FF737517ADEC392DD7835664284188D47F03F`
  - `MASTER_RU.acceptance.json`: 3116 bytes, SHA-256 `ECEE676CED495EF070ECB3DD822BEED00E1C06516A74174005EAA26821FF8050`
  - accepted working source: 195422 bytes, SHA-256 `BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9`
- `--verify` rerun from `kb_creator/`: passed and printed `INNSMOUTH_ACCEPTED_MASTER_RU_REPO_INPUT_OK`; reported 38 assets, asset inventory SHA-256 `c1a9ab2f89650201c91fa74eab809e16724d0c608534cfbfaa478aeeba9cae3a`, 51 tables, 155 headings, 50 anchors, 79 fragments, and 0 broken fragments.
- `--preflight` rerun from `kb_creator/`: passed and printed `INNSMOUTH_MASTER_RU_PROMOTION_PREFLIGHT_OK`; it pinned the accepted working RU source and generated the promoted RU identity above.
- Focused RU promotion regression: `python -B -m pytest -q -p no:cacheprovider tests\test_freeze_innsmouth_master_ru_repo_input.py` -> `6 passed`.
- Focused RU promotion plus TOC assertion: `python -B -m pytest -q -p no:cacheprovider tests\test_freeze_innsmouth_master_ru_repo_input.py tests\test_innsmouth_source_to_artifacts.py` -> `53 passed`.
- Unified EN/RU promotion-relevant suite: `python -B -m pytest -q -p no:cacheprovider tests\test_freeze_innsmouth_master_ru_repo_input.py tests\test_freeze_innsmouth_master_en_repo_input.py tests\test_innsmouth_master_en_repo_input.py tests\test_innsmouth_source_to_artifacts.py tests\test_build_innsmouth_reconstructed_en.py tests\test_build_innsmouth_master_en.py` -> `72 passed, 6 skipped`.
- EN/RU asset byte identity: `Compare-Object` over sorted asset names plus SHA-256 values returned no differences.
- Scoped marker scans:
  - promoted `MASTER_RU.md` had no `mineru-page`, `table-evidence`, `unit_id`, `cleaned`, or Windows absolute-path matches.
  - manifest scan found no Windows absolute paths or working paths; it does contain the expected rule key `historical_ru_or_en_bridge_forbidden`.
  - secret-pattern scan found no credential-shaped matches; only ordinary prose words containing `token` appeared in status/context text.
- TOC assertion change now checks structured `{title, level, href}` entries and current final child handout title in `test_innsmouth_source_to_artifacts.py`.

## Severity findings

### P0

None.

### P1

1. `--verify` does not fully invalidate manifest metadata/rules mutation, so the release freeze contract is incomplete.

   `acceptance_manifest()` emits release-significant metadata and rules: `schema`, `accepted_on`, `acceptance_authority`, and the three `rules` flags. However, `verify_promoted()` only checks `state`, source candidate identity, promoted Markdown identity/file hash, EN provenance, glossary provenance, structural counts, terminology replacements, and asset inventory. It does not compare the manifest bytes to the declared SHA-256 `ECEE676CED495EF070ECB3DD822BEED00E1C06516A74174005EAA26821FF8050`, does not require canonical JSON byte equality, and does not validate `schema`, `accepted_on`, `acceptance_authority`, or `rules`.

   Evidence:
   - `kb_creator/scripts/freeze_innsmouth_master_ru_repo_input.py:231-256` defines the full deterministic manifest, including `schema`, date, authority, and rules.
   - `kb_creator/scripts/freeze_innsmouth_master_ru_repo_input.py:259-306` verifies only selected semantic fields and omits the manifest's own byte identity plus several release-significant root fields.
   - `kb_creator/tests/test_freeze_innsmouth_master_ru_repo_input.py:64-151` covers promotion, overwrite refusal, wrong candidate identity, technical comments/counts/fragments, asset tampering, glossary drift, and obsolete terminology, but not mutation of manifest schema/date/authority/rules or canonical manifest bytes.

   Release impact: a mutated acceptance manifest can remain verifier-accepted if the checked package subfields still match, which violates the requested release-review requirement to verify manifest/freeze evidence and invalidation on mutation.

### P2

None.

### P3

1. The assignment packet reported a unified result of `72 passed, 14 skipped`; this critic's unified rerun produced `72 passed, 6 skipped` under the command listed above. The pass count matches and no test failed, but the skip count should be recorded exactly with the command used.

## Blockers

- Blocked for release approval until the P1 verifier gap is remediated or explicitly waived by the orchestrator/user for this RU save-point.

## Recommendation

REMEDIATION_REQUIRED.

Minimum remediation: make `verify_promoted()` fail closed on the acceptance manifest itself by checking canonical byte identity or exact regenerated canonical JSON, and assert the root release metadata/rules (`schema`, `accepted_on`, `acceptance_authority`, `rules`) in both verifier code and negative tests. After remediation, rerun `--verify`, focused RU promotion tests, TOC assertion coverage, and the unified EN/RU promotion-relevant suite before asking for commit authorization.
