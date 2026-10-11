# Terra engineering assignment: Viral Step 6A INV mutation batch

Sequential implementation under accepted packet sections 5.3, 6-7, 8.2 INV,
11 and 12.

## Baseline and writes

- Library: `1A6D616D9632325FF2F5ECF25A566F26BE2618BD54AC3E5818FC60C223F5F303`.
- Tests: `4256AEBB4E4CFC603AAE45F32B4FA8C8CAB7ECBDABA85139B0BE9FE5C71DFC67`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_inv_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write.

## Implement exact INV 18

Implement every packet id/code for ordinary/evidence/sheet row removal, stale
extra path, duplicate, QA included, cardinality/order, row bytes/hash/hash
format, digest, four path-syntax variants, row shape, and live file changed
behind the row.

Every case needs a distinct mutation of physical candidate bytes or the real
QA inventory selector, not COMMANDS proxy. Apply only literal permitted
transport changes: preserve the targeted inventory semantic failure and update
only immediate QA transport when the accepted protocol requires it. Enforce
ordinal path syntax/order, exact 500-row QA inventory authority, uppercase
hashes and live byte/hash verification in the production verifier.

Each uses one `_test_verify`, exact earliest code and a full closed audit with
real selector hashes, PASS, no outside/undeclared/residue. Preserve completed
families and collect 371. Run INV 18 in explicit chunks, representative
regression, BLD 3 and collect via Python `-B`/no-cache. Receipt embeds all 18
objects/digest. Complete only 18/18; no redesign/live/cleanup.
