# Terra engineering assignment: Viral Step 6A SCH mutation batch

Sequential implementation under accepted packet sections 5.3, 6, 7.3, 8.1
SCH, 11 and 12.

## Baseline and writes

- Library:
  `85B158CA0255E97415EAC28836D820CF8FD9AF3BFCB31A667B11FA2C5979E670`.
- Focused tests:
  `299C669293FEC83E10AE39B3A25F6EA2DBC650464258734D5BE2D725D1B7AF15`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_sch_20260901.md` only.
- No other/live/protected/cache/Git write.

## Implement SCH 33

Use the exact ordered authority labels:
`CONTRACT, SIDECAR, RECOVERY_MANIFEST, RECOVERY_EVIDENCE, QA,
SOURCE_IDENTITY, PAGE_PROVENANCE, CONTENT_PROVENANCE, ASSET_PROVENANCE,
ENTITY_INVENTORY, HANDOUT_INVENTORY, NAVIGATION_INVENTORY,
CONTENT_MODE_REVIEW, REFERENCE_ONLY_AUDIT, BLOCKER_LEDGER, COMMANDS`.

Implement the 16 exact `SCH-<label>-schema-wrong -> E_SCHEMA_<label>` rows,
16 exact `SCH-<label>-required-top-member-missing -> E_SHAPE_<label>` rows,
and `SCH-qa-unexpected-top-member -> E_SHAPE_QA`.

Every row mutates its real physical authority JSON selector with a distinct
callable. Literal reseals must follow the accepted phase order: external/raw
authorities receive only their specifically required authority/profile
transport; candidate schema/shape rows receive no inventory reseal because
phase 5 precedes phase 6. No semantic repair or COMMANDS proxy.

Complete verifier schema/shape branches for all 16 exact closed top-level and
row variants. Each case uses one `_test_verify`, exact earliest code and a full
closed `MutationAudit` with actual uppercase before/after hashes, `PASS`, no
outside/undeclared/residue.

Preserve completed families and collect 371. Run SCH in runner-safe chunks,
representative completed-family regression, BLD 3 and collect 371 using Python
`-B`/no-cache. The receipt embeds all 33 full ordinal audit objects and canonical
digest. Complete only 33/33; otherwise exact BLOCKED ids/symbols. No redesign,
live command or cleanup.
