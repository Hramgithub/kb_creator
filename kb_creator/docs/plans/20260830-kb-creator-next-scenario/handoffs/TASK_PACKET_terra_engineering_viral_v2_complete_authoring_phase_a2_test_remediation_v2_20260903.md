# Task packet — Viral v2 Phase A2 second full-suite remediation

- Same `nri-engineer` / GPT-5.6-terra / medium owner and worktree.
- Own only `kb_creator/tests/test_build_scenario_master_en.py` plus new receipt
  `terra_engineering_viral_v2_complete_authoring_phase_a2_test_remediation_v2_20260903.md`.
- Do not alter builder/verifier production gates, verifier tests, prior receipts,
  A3/helper/config/candidates/inputs/evidence/plan/context/Git/downstream output.

Independent rerun at remediation-v1 bytes still returns `Ran 77 tests`, exit
`1`. Sole failure:

`BuilderPreflightTests.test_v2_negative_duplicate_binding_fragment_and_excluded_page`
expects `placement target` but is preempted by `v2 migration orphan target
mismatch`.

Root fixture detail: this builder test calls `bind_v2_inputs(cfg,'negative')`
before replacing `cfg['assets']`, then makes a duplicate variant with an added
asset/event. Reseal the baseline and/or mutation's `new_reviewed_targets`
explicitly after those target additions, using the same valid bound decision,
so the test reaches its intended placement ambiguity. Do not weaken orphan
closure or exempt this fixture.

Run py-compile, exact 77-test two-module suite, established four-module
baseline, both v1 preflights and scoped diff-check. Confirm all forbidden v2,
INVENTORY, candidate/scratch paths absent. Record why remediation-v1 corrected
only the verifier fixture while this builder fixture remained stale.

Terminal line: `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REVIEW` only if all
checks pass, otherwise `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_REMEDIATION_V2`.
