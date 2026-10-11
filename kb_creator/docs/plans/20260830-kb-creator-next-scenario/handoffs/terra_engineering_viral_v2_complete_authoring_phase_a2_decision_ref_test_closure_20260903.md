# Viral v2 A2 structured decision-id test closure receipt

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a2-decision-ref-test-closure`.
- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Orchestrator policy owner: `gpt-5.6-sol` / medium.
- Assignment state: `matched` by task packet; platform runtime/model is not independently verifiable from this receipt.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T07:50:00+03:00` (Europe/Moscow).
- Elapsed time: approximately 20 minutes.
- Token use: unavailable.

## Scope and result

Scoped test closure stopped at the first newly proven production defect, as required by the packet. Production scripts were read-only and were not edited. Two focused, independent regression tests were added to assert that an exact structured decision id may have only one identity-bound evidence origin.

Both current validators accept the same `viral-logical_table-p020-l025` catalog id from two distinct identity-bound semantic-review-v2 files. The second file is outside the immutable reconstruction-package fixture and has its own exact path/bytes/SHA-256 binding, so this is a true incompatible cross-file decision-catalog collision rather than a package-inventory mutation.

The required complete four-kind builder/verifier matrix, expanded suite count, full baseline, real preflights, diff check, and forbidden-output audit were intentionally not run after this first blocking defect. The packet explicitly requires stopping and reporting when a new test proves a production defect.

## Files checked or changed

- Checked, unchanged: `kb_creator/scripts/build_scenario_master_en.py`.
- Checked, unchanged: `kb_creator/scripts/verify_scenario_master_en.py`.
- Changed: `kb_creator/tests/test_build_scenario_master_en.py`.
- Changed: `kb_creator/tests/test_verify_scenario_master_en.py`.
- Added (this immutable receipt): `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_test_closure_20260903.md`.

## Starting identity verification

The actual A2 source/test files matched the task packet before edits:

- builder: `B50870D615BA590FFC4D5A6A5490085C2F91365ADAD0400277F915B692DD91AB`;
- verifier: `3733F6BF50F580FAACFFC7ADFAB33EBFD098F9AEFA580039F537223846177BA6`;
- builder tests: `BD9B8234F6ADA84A7E339EEC9EF7A0AD1F8A00EB01C4A4DC8780B458FFA61B05`;
- verifier tests: `5C38DDBD0E3F6808598A97ADCA095A7F4F46ED9259900B6D788A235CE06206F9`.

## Verification and evidence

The targeted command was:

```text
python -B -m unittest -v kb_creator.tests.test_build_scenario_master_en.BuilderPreflightTests.test_v2_decision_evidence_rejects_cross_file_duplicate_catalog_id kb_creator.tests.test_verify_scenario_master_en.VerifierPreflightTests.test_independent_v2_decision_evidence_rejects_cross_file_duplicate_catalog_id
```

Exit: `1`; `Ran 2 tests in 0.753s`; both assertions failed because no `ValueError` was raised.

Builder reproduction: `BuilderPreflightTests.test_v2_decision_evidence_rejects_cross_file_duplicate_catalog_id` expected `ValueError` matching `decision evidence catalog mismatch`; no exception was raised.

Verifier reproduction: `VerifierPreflightTests.test_independent_v2_decision_evidence_rejects_cross_file_duplicate_catalog_id` expected `ValueError` matching `E_V2_MIGRATION`; no exception was raised.

This follows the validators' current `refs.update(ids)` behavior, which erases source provenance and cannot reject cross-file catalog collisions.

## Blocker and next action

Blocker: `CHANGES_REQUIRED`. The A2 contract requires duplicate catalog ids and incompatible cross-file collisions to fail closed. Both production validators currently admit them.

Next action: assign a new, explicitly scoped production remediation for both validators that preserves decision-id provenance across evidence files and rejects duplicate/conflicting ids before `refs` membership evaluation. Then retain or repair these two regression tests, add the remaining equivalent four-kind matrix, and rerun the full packet verification set. No A3/config/candidate action is authorized by this receipt.

Terminal status:

`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_TEST_CLOSURE`
