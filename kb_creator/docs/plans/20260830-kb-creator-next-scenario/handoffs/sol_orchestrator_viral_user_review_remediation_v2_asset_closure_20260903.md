# Viral remediation v2 asset closure continuation

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-asset-closure`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_v2_serializers_20260903.md`
- Completion token: `READY_FOR_V2_OUTPUT_VERIFIER`

## Objective

Complete the remaining v2 builder side: event-relative asset placement, binary
copy/identity closure, duplicate/suppression/quality-stage policy, excluded-page
leakage guards and deterministic two-build equality. Do not edit the verifier
or any real Viral policy/evidence/candidate.

You are not alone in the worktree. Preserve all previous edits and touch only
the three paths below.

## Exclusive ownership

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_asset_closure_20260903.md`

## Required behavior

- Bind every reader asset exactly `before_event`, `after_event` or
  `inside_structured_unit` using declared stable ids; reject missing, excluded,
  non-reader or multiply bound placement targets.
- Copy only declared reader binaries into the candidate. Record source and
  copied size/SHA-256; inventory and manifest must close exactly.
- Enforce closed `reader_value`, `duplication_resolution` and `quality_stage`
  enums. Evidence-only, platform-logo, promotional-badge, residue and duplicate
  child crops never enter reader Markdown or candidate assets.
- Permit Step 7 provisional full-page binaries for map/pregen units, but do not
  perform final XObject selection or any Step 8A decision.
- Reject any text/event/asset/reference from excluded reader pages 123--124
  while retaining their exact audit disposition rows.
- Reject missing or unstable source fragment/range identity.
- Build the same synthetic v2 package twice into two absent roots and assert
  byte equality for every non-inventory file plus equivalent recomputed
  inventories; timestamps/run-local absolute paths must not contaminate output.
- Preserve atomic absent-root behavior, typed serializers and sealed v1 route.

Add success and mutation tests for all placement classes, missing/duplicate
bindings, copy hash mismatch, suppression leakage, illegal enum, excluded-page
leakage, fragment identity drift and two-build determinism.

## Forbidden

No verifier, real config/evidence/source/reconstruction/candidate, Step 8A,
MASTER_RU/HTML/PDF, Git, deletion, cleanup or unrelated path changes.

## Evidence

Run the complete builder test module and `py_compile`. Write the exact immutable
receipt with changed paths and focused coverage. Return
`READY_FOR_V2_OUTPUT_VERIFIER` only when the builder side is complete; otherwise
return the exact asset/determinism gap.
