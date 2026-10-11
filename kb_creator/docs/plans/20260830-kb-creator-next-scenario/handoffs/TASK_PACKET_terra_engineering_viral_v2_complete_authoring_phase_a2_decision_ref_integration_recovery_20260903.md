# Task packet — Viral v2 A2 decision-ref integration recovery

## Exact reproduced failure

- Same `nri-engineer` / GPT-5.6-terra / medium and worktree.
- Orchestrator full four-module run at completion receipt SHA
  `AACFEDD1350C2B82F08806764145602599715357B3A0AA71379D32F927727BDB`
  returned `Ran 77 tests`, exit `1`: 15 errors and 1 failure.
- Root cause 1: `decision_evidence` rows now contain closed `kind`, but
  builder/verifier `v2_migration()` pass the whole row to the existing identity
  helper, which correctly accepts only `path/bytes/sha256`; every input-binding
  route fails with evidence closed-schema mismatch.
- Root cause 2: builder/verifier test hashes remained
  `BD9B...61B05` / `5C38...06F9`; no promised boundary/closure/common-token/
  near-match mutation tests were added. The suite stayed at 77.

## Scope

Own the two scripts, two focused tests and one new receipt
`terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_integration_recovery_20260903.md`.
Preserve unrelated edits. Do not touch prior receipts, helper/config/evidence,
inputs, A3/candidates/plan/context/Git/downstream output.

## Required recovery

1. Keep `kind` in the outer closed evidence row but pass only the exact identity
   projection `{path, bytes, sha256}` to existing identity helpers. Do not
   weaken those helpers or accept extra identity keys globally.
2. Add real, independently equivalent builder and verifier tests for all four
   evidence kinds: semantic review, registry Markdown, boundary ledger and
   closure report.
3. Cover valid exact IDs and negatives for common `reader`/`viral`, prefix,
   suffix, case mutation, free-text/reason/evidence-only occurrence, unsupported
   kind/schema/extra key, invalid JSON/UTF-8, empty catalog, duplicate catalog,
   missing same-file target unit, injected unknown row key and incompatible
   cross-file duplicate/collision.
4. Update every existing synthetic evidence row to include `kind` and a real
   closed evidence fixture. Preserve intended later-failure assertions.
5. Do not claim success until the exact expanded test count is captured from:
   - two focused modules;
   - four-module baseline;
   plus py-compile, both real-v1 preflights and scoped diff-check.
6. Verify no real v2 config, accepted-v4 input INVENTORY, probe/staging/candidate
   remains from this recovery.

Terminal line `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` only if the
expanded suite is greater than 77 and all required commands exit 0. Otherwise
`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_INTEGRATION_RECOVERY`.
