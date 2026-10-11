# Viral v2 A3 critic-probe test-closure receipt

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a3-critic-probe-test-closure`.
- Role: `nri-engineer` / requested `gpt-5.6-terra` / medium.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: `matched` by packet; actual platform runtime/model is not independently verifiable from this receipt.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T08:49:03.2607318+03:00` (Europe/Moscow).
- Elapsed time: approximately 24 minutes.
- Token use: unavailable.

## Scope

Bounded test closure only: the two focused test modules and this receipt.  Production,
canonical plan/context/status, candidates, scratch, output, Git, and downstream
artifacts were out of scope.  The packet requires an immediate stop with a minimal
reproduction and no production edit when a direct required probe proves a production
defect.

## Result

`PRODUCTION_DEFECT_V2_COMPLETE_AUTHORING_PHASE_A3_TEST_CLOSURE`

The frozen builder accepts a top-level v2 configuration after the required xref
`migration_row_id` is changed from `xrefs:a3-xref` to `xrefs:drift`.  The same public
`build_candidate()` call that must reject this A3 migration drift instead returns
normally; the test assertion fails with `AssertionError: ValueError not raised`.
This is a direct reproduction of the packet's required xref migration-drift rejection,
not an internal-helper-only probe.  No production file was edited.

The destination assertion in the test confirms that all rejected variants leave no
candidate directory.  For the accepted migration-drift variant, the test intentionally
fails before asserting an expected rejection; no candidate output was retained by the
isolated run.

## Files checked or changed

- Changed: `kb_creator/tests/test_build_scenario_master_en.py`.
  - Added `A3BuilderPublicClosureTests`: isolated public preflight/build probes for
    A3 xref source slices/text/target/migration, all illegal and valid source-operation
    pairs, contains and asset-owner closure, and all eight typed payload kinds.
  - Every builder-negative helper invokes `build_candidate()` and asserts its unique
    candidate destination remains absent.
- Checked, unchanged: `kb_creator/tests/test_verify_scenario_master_en.py`.
- Checked, unchanged and hash-fixed:
  - `kb_creator/scripts/build_scenario_master_en.py`:
    `5984748E8591EBD6CA2E94CBD1D7DE8528C8E2126D2BD1D9C22DBAD725441673`.
  - `kb_creator/scripts/verify_scenario_master_en.py`:
    `2824437D111E78B1DFC259EEB0C356866978F0F013FBE2B2AD375C126523A0B1`.

## Verification and evidence

- `python -B -m py_compile kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py`: exit `0`.
- Direct reproduction, twice after fixture correction:
  `python -B -m unittest -v kb_creator.tests.test_build_scenario_master_en.A3BuilderPublicClosureTests.test_a3_xref_public_positive_and_all_critic_drift_variants`
  - first isolated run found one accepted mutation;
  - labelled rerun identifies exactly `mutation='migration'`, failing because
    `ValueError` was not raised.
- The same test's positive full A3 xref shape passed public builder preflight before
  the mutation loop; extra slice, missing slice, foreign slice, visible-text drift,
  and target drift reached their intended rejection assertions.  Migration drift did
  not reject.
- Scoped `git diff --check -- kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py`: exit `0`.
- Post-probe production SHA-256 values match the packet exactly (listed above).
- The isolated probe uses UUID-named disposable inputs and candidate names.  The
  failed test cleanup left no retained `kb_creator/working/synthetic` candidate beyond
  the pre-existing `master_en` container; no v2 config/candidate/accepted-v4 inventory
  was created or retained.

## Blocker

The required public A3 migration-drift rejection is absent in the builder.  Because
the packet makes production fixed and requires stopping on a direct defect, the
verifier mirror, full matrix, repeated four-module baselines, and frozen-v1 preflights
were not run.  They must not be represented as passed.

## Next action

Architecture/orchestration should assign a narrowly scoped production remediation
that binds `xref.migration_row_id` to the corresponding materialized migration target
in the builder and independently verifies the analogous verifier seam.  After that
production change, start a fresh test-closure packet from fixed hashes; do not resume
this stopped packet as READY.

