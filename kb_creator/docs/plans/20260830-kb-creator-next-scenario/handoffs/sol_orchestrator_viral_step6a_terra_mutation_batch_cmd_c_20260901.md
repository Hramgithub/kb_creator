# Terra engineering assignment: Viral Step 6A CMD batch C

Sequential implementation under accepted packet sections 5.3, 6-7, 8.3 CMD,
11 and 12. This is the final CMD sheet/action subset C only. Terra/medium owns
engineering; Luna is not an implementation owner.

## Baseline and writes

- Library: `231C976E57D6DC1051C326C479EC42D87525DDB8565741A0D64A0E96B37352C7`.
- Tests: `59C148D64F5CAB7B6D50723A4C10D5AD292FC0449D839CDB963DFE6F2403F1EF`.
- CMD-B completion receipt:
  `7140FA097F85CD806E6F0BF09715E53C96D459660FF681B3AD22B0E581175343`.
- Editable: those two material files and one new absent-before receipt
  `terra_engineering_viral_step6a_mutation_batch_cmd_c_20260901.md` only.
- Everything else is read-only; no live, candidate, protected-119, cache, Git,
  commit, push, cleanup, or unrelated write. Preserve pre-existing cache byte-
  and path-identical; prove zero newly attributable residue.

## Implement exact CMD subset C: 15

Implement the exact descriptive ids/codes and physical selectors:

1. `CMD-sheet-count-wrong -> E_COMMAND_SHEET_COUNT`;
2. `CMD-sheet-coverage-wrong -> E_COMMAND_SHEET_COVERAGE`;
3. `CMD-sheet-missing -> E_COMMAND_SHEET_SET`;
4. `CMD-sheet-duplicate -> E_COMMAND_SHEET_SET`;
5. `CMD-sheet-id-wrong -> E_COMMAND_SHEET_ID`;
6. `CMD-sheet-path-sequence-wrong -> E_COMMAND_SHEET_PATH`;
7. `CMD-sheet-grid-wrong -> E_COMMAND_SHEET_GRID`;
8. `CMD-sheet-hash-wrong -> E_COMMAND_SHEET_HASH`;
9. `CMD-flattened-page-missing -> E_COMMAND_SHEET_PAGES`;
10. `CMD-flattened-page-duplicate -> E_COMMAND_SHEET_PAGES`;
11. `CMD-flattened-page-order-wrong -> E_COMMAND_SHEET_PAGE_ORDER`;
12. `CMD-render-path-wrong -> E_COMMAND_RENDER_PATH`;
13. `CMD-render-hash-wrong -> E_COMMAND_RENDER_HASH`;
14. `CMD-page-render-mapping-disagrees -> E_COMMAND_PAGE_RENDER_MAP`;
15. `CMD-verify-determinism-false -> E_COMMAND_DETERMINISM`.

Every case must have a distinct callable mutating its real physical COMMANDS
v3 sheet/record/determinism selector. Apply only its literal allowed transport
reseals, never repair the target, and extend the one shared production verifier
with exact ordinal enforcement of 31 2x2 sheets, pages 1..124 exactly once,
sheet ids/paths/grid/hashes, render paths/hashes/page mapping, and deterministic
verify truth. Replace any generic `CMD-sheet-selector-NN` registry placeholder
with the exact descriptive ids above; generic ids or shared proxy mutations do
not count. Do not implement QAV or REG in this batch.

Each row executes one `_test_verify`, obtains the declared earliest code, and
emits the full closed 16-field Section-11 audit with real hashes, `PASS`, and
zero outside reads, undeclared changes, or fixture residue. Run all 15 in
bounded explicit chunks, representative completed-CMD/clean-path regression,
BLD 3, and collect exactly 371 with Python `-B` and cache disabled.

Before creating the immutable receipt, validate all 15 full objects and compute
the packet-formula canonical bytes/digest from the final ordered rows in memory.
The standalone receipt records objects, rows/digest, commands/native exits,
stdout/stderr hashes, material pre/post hashes, pre-existing cache before/after,
exact changed paths, and token availability. Complete only 15/15; otherwise
write an honest BLOCKED receipt. No live execution, redesign, promotion,
cleanup, Step-6A acceptance, or release claim.
