# Terra engineering assignment: Viral Step 6A TOP mutation batch

Sequential implementation under accepted packet sections 5.3, 7.3, 8.1 TOP,
11 and 12.

## Baseline and writes

- Library:
  `744551828B9BEF4C7CF8FD4DDE690FFAF23404907269D42BAB7389EDAEFCD841`.
- Focused tests:
  `533D6B3E3345FCD4404A159CDA10548BEC1CFCF9F22214C37163A247EABD640B`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_top_20260901.md` only.
- No other/live/protected/cache/Git write.

## Implement TOP 21

Implement the exact packet ids/codes:

- root/reparse 4;
- closed topology 9;
- forbidden classes 8.

Each row must have a distinct real physical/path/classification mutation and
exact semantic selector; no COMMANDS proxy. Candidate root, escape, missing,
extra, protected-empty and forbidden-suffix/class checks must arise from the
production verifier in binding phase order. The two reparse rows must use a
real physical entry plus immutable `ClassificationOverride`, preserving
kind/size/file-id and never privilege-skip.

Use literal reseals/allowed transports (normally none because topology precedes
inventory), exactly one `_test_verify`, exact earliest code and a full closed
`MutationAudit` with real before/after hashes, `PASS`, no outside read,
undeclared changes or residue. Preserve REP/SRC/AUT and 371 collection.

Run TOP 21 in runner-safe explicit chunks, representative completed-family
regression, BLD 3/3 and collect 371 via Python `-B`, no-cache. Receipt embeds
all 21 full ordinal audit objects/digest. Complete only if 21/21 pass; otherwise
BLOCKED with exact ids/symbols. No redesign, live command or cleanup.
