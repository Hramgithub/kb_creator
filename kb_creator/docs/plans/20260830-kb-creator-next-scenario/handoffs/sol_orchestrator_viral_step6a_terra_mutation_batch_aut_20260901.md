# Terra engineering assignment: Viral Step 6A AUT mutation batch

This is sequential implementation under the accepted architecture packet,
especially sections 5.3, 7.3, 8.1 AUT and 11.

## Baseline and writes

- Library SHA-256:
  `C413F87F95C33B577F34E5A5CD80611166D8A62B1152D67AD361399AA34CA82E`.
- Test SHA-256:
  `C3B4EA8129FD39DF6AD3D76558D93D9E89207D6A401AD26462AF4D7F3573B95A`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_aut_20260901.md` only.
- Everything else is read-only. No live/external/cache/Git/protected write.

## Implement exactly AUT 30

Implement every exact AUT id/code from packet section 8.1:

- 5 contract/snapshot rows;
- 11 source-identity rows;
- 14 recovery rows.

For each row, replace the shared COMMANDS proxy with a distinct callable that
changes its real physical/raw/JSON selector. Add the production verifier branch
needed to emit the binding earliest code in the accepted phase order. Use
literal reseal and allowed-transport tuples; never repair the semantic target.
`apply_case` must record exact selector before/after hashes, declared and actual
reseals, one real `_test_verify` call, exact code, zero outside reads,
undeclared changes and residue. Recovery cases operate on the physical 211-file
fixture and prove row/path/bytes/hash/duplicate/forbidden/payload binding.

Preserve completed REP/SRC behavior, every other family row and exact 371
collection. Run all 30 AUT nodes, REP/SRC regression smoke, BLD 3/3 and
collection using `python -B` and pytest `-p no:cacheprovider`. The receipt
contains all 30 canonical audit records/digest plus commands and identities.
Result is `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION` only when every AUT case
passes; otherwise `BLOCKED` with exact ids/symbols. No architecture redesign.
