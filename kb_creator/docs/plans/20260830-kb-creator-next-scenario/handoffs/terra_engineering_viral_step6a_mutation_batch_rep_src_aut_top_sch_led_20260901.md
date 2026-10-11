# Terra engineering receipt: Viral Step 6A mutation batch REP/SRC/AUT/TOP/SCH/LED

- scope: bounded reusable-engineering inspection and attempted admission for the assigned 110 selector-specific mutation rows only.  The only write is this absent-before receipt.  The two material files, candidate, source, recovery, CLI, contract tests, production `COMMANDS`, Git state, and all other protected surfaces remain unchanged.
- result: `BLOCKED`.
- assignment: `sol_orchestrator_viral_step6a_terra_mutation_batch_rep_src_aut_top_sch_led_20260901.md`, SHA-256 `490428F85E21774F04E49A9647693B8CC3F4396C1CB2D2E9897AF8BBA3BE0F4C`.
- baseline admission: library SHA-256 `EB3421D2205E1D54D4A7B4EA54BA7E09B7B8E057C704D8CED0D0748AA97CCB71`; focused test SHA-256 `C345128969C76B9DB4FB5963866D0D44C07C9AFC9DDEAA9A1CF3D0394DF66A6F`; both match exactly.
- files checked: the assignment; accepted architecture packet sections 7.3, 8.1, 11, and 12; canonical plan/context; phase-1 completion receipt; the two assigned material files.
- files changed: this receipt only.

## Technical blocker

The admitted baseline has not implemented the required batch seam.  All 368 existing case entries are created through one shared `_mutator(case_id, selector)` which writes a synthetic `case_<id>` member to `candidate/evidence/COMMANDS.json`; the selected 110 rows therefore do not mutate the declared source, authority, topology, schema, or ledger selector.  `test_selector_specific_mutation` merely hashes `COMMANDS` before/after; it never calls `_test_verify`, has no literal per-case reseal transport, produces no `MutationAudit`, and does not assert `ReconstructionStop.code`.

The shared verifier likewise has no production branches for the required majority of section 8.1 codes.  It presently compresses COMMANDS failures to `E_COMMAND_ACTIONS` or `E_COMMAND_COUNTS_PAGES`, topology failures to a few broad classes, and schema/graph checks to broad shape/cardinality failures.  Adding a code derived from the observed exception, a `COMMANDS` proxy, or an expected-code marker would violate sections 7.3/8.1/11 and the assignment.  The required physical `ClassificationOverride` is absent, so the two reparse rows cannot be implemented without a real provider-level classification seam.

This is a material implementation gap, not an ordinary test failure that can safely be papered over in this receipt.  No synthetic substitute was added.

## Exact unfinished rows

All 110 assigned rows remain unfinished: 2 `REP`; all 18 `SRC-*`; all 30 `AUT-*`; all 21 `TOP-*`; the 33 expanded `SCH-*` rows (schema-wrong and required-top-member-missing for each of `CONTRACT`, `SIDECAR`, `RECOVERY_MANIFEST`, `RECOVERY_EVIDENCE`, `QA`, `SOURCE_IDENTITY`, `PAGE_PROVENANCE`, `CONTENT_PROVENANCE`, `ASSET_PROVENANCE`, `ENTITY_INVENTORY`, `HANDOUT_INVENTORY`, `NAVIGATION_INVENTORY`, `CONTENT_MODE_REVIEW`, `REFERENCE_ONLY_AUDIT`, `BLOCKER_LEDGER`, `COMMANDS`, plus `SCH-qa-unexpected-top-member`); and all 6 `LED-*` rows.  Their exact ids and expected earliest codes remain the immutable section 8.1 table of the accepted packet; none were executed as a compliant mutation/audit row.

## Evidence

The permitted offline commands were run with bytecode and pytest-cache suppression:

```text
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
=> native exit 0; 371 collected

python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider -k 'REP or SRC or AUT or TOP or SCH or LED'
=> the existing 110 selected phase-1 proxy nodes execute, but they are not compliant evidence: they do not invoke _test_verify or emit MutationAudit rows.
```

No live/protected command, build, remediate, Git operation, cache cleanup, candidate/source/recovery mutation, or third material-file action occurred.  No canonical 110-row audit JSON/digest is claimed, because producing one without the required real executions would be false evidence.  Command stdout/stderr hashes for the truncated host capture are unavailable.

## Required next action

Return to architecture/orchestration for a revised, independently reviewed implementation packet that either supplies the missing production-shaped verification branches and provider-level reparse-classification interface within the existing two-file allowlist, or explicitly narrows/resequences the batch.  A successor engineering task can then replace the proxy registry with 110 real callable selector mutations, literal reseal tuples, one-call verification assertions, and complete audit rows.  Do not treat this receipt as a release, QA, integration, or acceptance decision.

- elapsed time: approximately 19 minutes.
- token use: unavailable.
- timestamp: `2026-09-01T00:00:00+03:00` (host wall-clock timestamp unavailable in this task surface).
- orchestrator policy owner: main chat `gpt-5.6-sol / medium`.
- assignment state: Terra reusable engineering admission blocked; orchestration ownership remains with the main chat.
- scoped override: `gpt-5.6-terra / medium`, Fast/priority policy only; actual runtime exposure unavailable.
