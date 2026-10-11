# Task packet — Viral v2 Phase A2 full-suite remediation

## Role and exact failure

- Role: same `nri-engineer` / GPT-5.6-terra / medium owner.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Preserve unrelated/user edits; do not revert others.
- Orchestrator independently ran:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`
  at the A2 receipt hashes. Result: `Ran 77 tests`, exit `1`.
- Failures:
  1. `test_v2_builder_baseline_candidate_is_accepted` errors with
     `v2 migration orphan target mismatch` from builder `v2_migration`.
  2. `test_v2_negative_duplicate_binding_fragment_and_excluded_page` expects
     the later `placement target` mutation but is preempted by the same orphan
     target failure.

## Scope

Own only the same four code/test files plus a new immutable remediation receipt:
`terra_engineering_viral_v2_complete_authoring_phase_a2_test_remediation_20260903.md`.
Do not edit or replace the original A2 receipt. Do not start A3, helper/config,
candidate, immutable input/evidence, plan/context, Git or downstream work.

## Required correction

- Root-cause the fixture/closure mismatch and repair it without weakening the
  A2 orphan-target, decision-reference, exact-count, pending-A3 or fail-closed
  gates.
- Synthetic builder-produced baseline fixtures must explicitly close every
  materialized hierarchy/asset/xref target through a source migration row or
  valid `new_reviewed_targets` decision. Do not silently exempt existing tests.
- Negative tests must reach and assert their intended mutation, rather than
  fail earlier on an unrelated invalid baseline fixture.
- Check whether the original engineer command was run before final fixture
  bytes; record the evidence discrepancy factually.

## Required verification

- py-compile all four files;
- exact 77-test two-module suite passes;
- established four-module baseline passes;
- both real frozen-v1 preflights pass;
- scoped `git diff --check` passes;
- real v2 config, accepted-v4 input INVENTORY, A2 probe candidates/scratch are
  absent.

Receipt terminal line:
`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REVIEW` only if all checks pass;
otherwise `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_REMEDIATION`.
