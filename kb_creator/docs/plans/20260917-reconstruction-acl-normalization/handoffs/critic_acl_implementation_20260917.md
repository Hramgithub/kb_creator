# Implementation review receipt: Stage 06 ACL normalization

- Goal ID: `20260917-reconstruction-acl-normalization`
- Step ID: `5-independent-review`
- Review kind: `implementation`
- Role: independent critic (`gpt-5.5`, policy effort `medium`)
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-17T13:35:56+03:00`
- Elapsed time: approximately 25 minutes
- Token use: unavailable to the critic runtime; main thread telemetry at receipt time reported `102475` tokens used
- Implementer/designer participation declaration: I did not implement or materially design the candidate under review. I edited no implementation, canonical plan/context/status, release, source, or candidate files. This receipt is the only file changed by this review.
- Scope: implementation review only. No release decision or release approval is made.

## Files checked

- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260917-reconstruction-acl-normalization/plan.md`
- `kb_creator/docs/plans/20260917-reconstruction-acl-normalization/context.md`
- `kb_creator/docs/plans/20260917-reconstruction-acl-normalization/handoffs/architect_acl_integration_20260917.md`
- `kb_creator/docs/plans/20260917-reconstruction-acl-normalization/handoffs/qa_acl_windows_20260917.md`
- `kb_creator/pipeline/reconstruction_replay_resume.py`
- `kb_creator/scripts/normalize_publication_access.py`
- `kb_creator/tests/test_reconstruction_replay_resume.py`
- `kb_creator/tests/test_normalize_publication_access.py`

## Evidence checked

- `reconstruction_replay_resume.py` imports `normalize_publication_access_if_managed` and includes `kb_creator/scripts/normalize_publication_access.py` in `DOWNSTREAM_IMPLEMENTATION`.
- Stage 06 is the only replay stage wired with `post_publish=normalize_publication_access_if_managed`; Stage 05 has no access callback.
- Fresh Stage 06 publishes the output with `os.replace(temp_output, output)`, then runs `_validate_post_publish_access`, then writes/publishes the stage manifest and only after that returns a success result.
- `_validate_post_publish_access` accepts only `normalized` or the declared skip reasons `non_windows_host` and `outside_managed_working_tree`, then recomputes `deterministic_inventory(output)` and fails if candidate bytes changed.
- Fresh post-publish failures call `_quarantine_fresh_stage`; tests cover unexpected state, callback exception, byte mutation, and absence of canonical output/manifest after failure.
- Existing output/manifest reruns validate the pair, run the access gate on the final path, then validate the pair again; tests cover preserving an existing pair on rerun access failure.
- `normalize_publication_access.py` confines non-wrapper normalization to `kb_creator/working`, skips non-Windows hosts explicitly, and the managed wrapper skips isolated external test trees.
- On Windows, the helper enables inheritance, grants additive `RX` to `USERDOMAIN\USERNAME`, uses `/grant` rather than `/grant:r`, does not change ownership, and excludes `.obsidian` from the target list.
- QA receipt reports managed synthetic Stage 06 with `AreAccessRulesProtected=False`, `KAMAZNOTEBOOK\user` Allow `ReadAndExecute`, no Deny ACE for that user, successful file read, and stable hash. It also reports the existing Dream candidate readable and byte-stable. It does not claim Codex UI bridge navigation was independently proven.

## Commands run

- `& '.\.tools\MinerU\.venv\Scripts\python.exe' -B -m pytest kb_creator\tests\test_reconstruction_replay_resume.py kb_creator\tests\test_normalize_publication_access.py -q`
  - Result: failed during environment setup for one CLI import because that venv lacks `pytest`.
- With `.tools\python-test-deps` only in `PYTHONPATH`:
  - Result: `21 passed, 1 failed`; the failure was `ModuleNotFoundError: No module named 'PIL'` while importing shared CLI render QA code, not an ACL behavior failure.
- With `.tools\python-test-deps` plus `.tools\MinerU\.venv\Lib\site-packages` in `PYTHONPATH`:
  - `pytest kb_creator\tests\test_reconstruction_replay_resume.py kb_creator\tests\test_normalize_publication_access.py -q`
  - Result: `22 passed in 5.59s`.
- Expanded relevant suite:
  - `pytest kb_creator\tests\test_reconstruction_replay_resume.py kb_creator\tests\test_normalize_publication_access.py kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py kb_creator\tests\test_materialize_mineru_ai_merge.py kb_creator\tests\test_mineru_visual_merge_bundle.py -q`
  - Result: `161 passed in 23.19s`.
- `git diff --check`
  - Result: clean.

## Severity findings

- P0: none.
- P1: none.
- P2: `normalize_publication_access._desktop_user_principal` rejects missing values, sandbox usernames, control/newline/colon/quote characters, and backslash in `USERNAME`, but does not reject a backslash in `USERDOMAIN`. The architecture receipt asked for separator-invalid values to fail closed. On normal Windows `USERDOMAIN` this is unlikely to fire, and `icacls` failure would still fail the pipeline, so this is not a blocker for the candidate. Recommended follow-up: add explicit backslash validation for `USERDOMAIN` and a unit test for bad domain and bad username independently.
- P2: The implementation uses the friendly `USERDOMAIN\USERNAME` principal instead of resolving and passing a SID. The architecture receipt allows friendly-name invocation if `icacls` is the authoritative resolution check and nonzero exits fail closed, which this code does. Residual risk is localized-name/identity ambiguity; live QA mitigates the current host.
- P2: Current fresh verification independently re-ran 22 focused tests and a 161-test relevant expanded subset. The plan's recorded `279 passed, 1 skipped` broader suite was not re-executed by this critic and remains accepted as prior orchestrator evidence, not fresh critic evidence.
- P2: QA did not prove Codex UI bridge navigation, only filesystem ACL/readability and stable bytes. This is correctly declared as a limitation and should not be promoted to a UI-open claim.

## Blockers

None for implementation acceptance. No unresolved P0/P1 findings were found in the reviewed scope.

## Recommendation

`APPROVE_IMPLEMENTATION_WITH_P2_FOLLOW_UPS`.

The candidate satisfies the required implementation contract for Stage 06: post-final-rename and pre-manifest access gate, fail-closed quarantine for fresh outputs, rerun preservation, declared skip states, byte inventory recheck, exact desktop-principal additive RX grant without broad group, `/grant:r`, or ownership transfer, `.obsidian` exclusion, producer-closure binding, and focused regression coverage. This is not a release receipt and does not transfer orchestration ownership.

## Correction delta review

- Timestamp: `2026-09-17T13:38:10+03:00`
- Scope: reviewed only the correction delta for the prior P2 about ambiguous `USERDOMAIN`; no code, canonical plan/context/status, release, source, or candidate files were edited by this critic.
- Files checked:
  - `kb_creator/scripts/normalize_publication_access.py`
  - `kb_creator/tests/test_normalize_publication_access.py`
  - this receipt
- Evidence:
  - `_desktop_user_principal` now rejects a backslash in both `USERDOMAIN` and `USERNAME`, while preserving the prior fail-closed checks for missing values, sandbox usernames, and invalid control/quote/colon characters.
  - `test_windows_normalizer_rejects_ambiguous_domain` covers `USERDOMAIN="BAD\\DOMAIN"` and expects `PublicationAccessError`.
  - Focused replay/access suite now reports `23 passed in 6.03s`.
  - `git diff --check` remains clean.
- Remaining limitations:
  - Codex UI bridge navigation remains an explicit limitation; the prior QA evidence proves filesystem ACL/readability and stable bytes, not an opened Codex panel.
  - SID migration was not implemented and remains optional hardening, not a blocker under the architecture receipt's friendly-principal allowance.
- Updated findings:
  - P0: none.
  - P1: none.
  - P2: none blocking. The previous P2 for `USERDOMAIN` separator validation is closed by this correction.
- Final recommendation: `APPROVE_IMPLEMENTATION`. This is still not a release receipt and does not transfer orchestration ownership.
