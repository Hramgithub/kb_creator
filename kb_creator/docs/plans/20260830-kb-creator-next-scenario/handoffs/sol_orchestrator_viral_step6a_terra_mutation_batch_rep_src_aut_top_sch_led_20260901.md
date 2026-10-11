# Terra engineering assignment: Viral Step 6A mutation batch REP/SRC/AUT/TOP/SCH/LED

## Baseline and authority

- Role: `gpt-5.6-terra / medium`, Fast/priority policy.
- Accepted authority: architecture packet sections 7.3, 8.1, 11 and 12.
- Current library SHA-256:
  `EB3421D2205E1D54D4A7B4EA54BA7E09B7B8E057C704D8CED0D0748AA97CCB71`.
- Current focused-test SHA-256:
  `C345128969C76B9DB4FB5963866D0D44C07C9AFC9DDEAA9A1CF3D0394DF66A6F`.
- The preceding broad phase-2 attempt created no final receipt; these hashes are
  an orchestrator-recorded incomplete checkpoint, not accepted evidence.

## Exclusive writes

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. new receipt
   `terra_engineering_viral_step6a_mutation_batch_rep_src_aut_top_sch_led_20260901.md`.

Everything else is read-only. No live command, source/candidate/recovery/CLI/
contract/QA/COMMANDS production mutation, cache cleanup, Git mutation, commit or
push is authorized.

## Required batch

Complete exactly these accepted families and their packet-enumerated ids/codes:

- `REP` 2;
- `SRC` 18;
- `AUT` 30;
- `TOP` 21;
- `SCH` 33 expanded authority rows;
- `LED` 6.

For all 110 rows:

1. use the exact descriptive id and exact earliest error code from section 8.1;
2. implement a real case-specific semantic selector and distinct callable that
   mutates that exact physical/provider/repository value, not COMMANDS by proxy;
3. store a literal reseal tuple and literal allowed transport selectors;
4. apply exactly one semantic mutation, perform only declared transport reseals,
   call the shared real `_test_verify` exactly once and assert the exact code;
5. emit a closed `MutationAudit` row with before/after selector hashes,
   `changed_before_reseal`, `changed_by_reseal`, declared reseals, call count,
   zero outside reads, undeclared changes and residue;
6. add or complete production verifier branches so these exact earliest codes
   arise naturally in the accepted phase order; never derive expected code from
   the observed exception;
7. implement the physical `ClassificationOverride` reparse cases without a
   privilege-dependent skip.

Do not rename, synthesize or implement other family rows in this batch except
for shared audit/reseal infrastructure strictly required by these 110 rows.
Preserve exact total collection 371 and phase-1 strict graph behavior.

## Evidence

- Use `python -B` and pytest `-p no:cacheprovider`.
- Prove exact batch id list/counts, zero generic/synthetic ids within the six
  families, all 110 targeted executions and audit rows, plus all three BLD smoke
  nodes and total collect 371.
- Do not run the entire remaining-family suite.
- Receipt result is `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION` only if all 110
  rows pass. Otherwise `BLOCKED` with exact unfinished ids/symbols.
- Receipt includes canonical machine-readable audit rows/digest for these 110,
  commands/native exits, stdout/stderr hashes, before/after identities and
  protected-surface/path-diff evidence.
