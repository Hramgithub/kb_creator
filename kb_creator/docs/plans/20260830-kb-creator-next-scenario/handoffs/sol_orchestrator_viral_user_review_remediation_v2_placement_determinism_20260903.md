# Viral remediation v2 placement and determinism closure

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-placement-determinism`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_v2_asset_closure_20260903.md`
- Completion token: `READY_FOR_V2_OUTPUT_VERIFIER`

## Objective

Close the four exact remaining builder gaps and no others: actual
before/after/inside placement, duplicate binding rejection, two-root byte
determinism, and negative fragment/excluded-event leakage tests.

You are not alone in the worktree. Preserve all prior work; edit only the three
exclusive paths.

## Exclusive ownership

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_placement_determinism_20260903.md`

## Required closure

1. Materialized Markdown proves each reader asset is immediately before or
   after its distinct declared event, or inside the exact declared structured
   unit; placement cannot be satisfied merely by an asset event's own position.
2. Reject zero, duplicate and conflicting reader bindings and any target whose
   representation/scope cannot contain the placement.
3. Build an identical synthetic v2 package into two absent roots and prove all
   non-inventory file bytes/hashes match; inventories must be semantically
   equivalent and free of target-root/time/device noise.
4. Reject missing/changed source fragment-range identity and any event/text/
   xref/asset reference to excluded reader pages while preserving audit rows.
5. Retain all prior v1, serializer, atomic and asset-copy behavior.

Add focused positive and negative tests for all four items. Do not broaden the
implementation beyond this list.

## Forbidden

No verifier/config/evidence/source/reconstruction/real candidate/Step 8A/Git/
cleanup/deletion/unrelated path changes.

## Evidence

Run builder tests and `py_compile`, then write the exact immutable receipt.
Return `READY_FOR_V2_OUTPUT_VERIFIER` only if all four closures pass.
