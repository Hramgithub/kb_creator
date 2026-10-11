# Terra engineering assignment: Viral Step 6A SEM mutation batch

Sequential implementation under accepted packet sections 5.3, 6-7, 8.2 SEM,
11 and 12.

## Baseline and writes

- Library: `560E39658784BCDB76FFB4F9321C0DDC06B3F71B802861308E1BA42F417F3644`.
- Tests: `C455F53E36563391389C3B0B97C2352467F431F4345FA9E901B8C3EC2F6D17D8`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_sem_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write.

## Implement exact SEM 18

Implement every packet id/code for entity/handout ordinal and id integrity,
entity-handout equality, required count/label/page range/entity closure; mode
page set/duplicate/review state; reference-only rows/history; map/pregen/
back-cover/handout role counts.

Each case mutates the real ENTITY_INVENTORY, HANDOUT_INVENTORY,
CONTENT_MODE_REVIEW, REFERENCE_ONLY_AUDIT or page-role selector with a distinct
callable. Apply only exact literal inventory/QA transport changes and do not
repair the target. Extend production verifier for 39 equal entity/handout rows,
ordinals, five page modes, zero historical/reference-only additions and exact
role partition. No COMMANDS proxy.

Each uses one `_test_verify`, exact earliest code and full closed audit with
real hashes, PASS, zero outside/undeclared/residue. Preserve completed families
and collect 371. Run SEM 18 in explicit chunks, representative regression,
BLD 3 and collect via Python `-B`/no-cache. Receipt embeds all 18 full objects
and one canonical digest. Complete only 18/18; no redesign/live/cleanup.
