# Terra engineering assignment: Viral Step 6A AST mutation batch

Sequential implementation under accepted packet sections 5.3, 6-7, 8.2 AST,
11 and 12.

## Baseline and writes

- Library: `BDEF2AE46D2A86F06AA0841E92B2B851055FFD234F269078B213D3BA07274BA5`.
- Tests: `F364D0BB6494F232490A3460C27C9F393A177C905EBF9BE589285D5C5E698055`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_ast_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write or pyc cleanup.

## Implement exact AST 21

Implement every packet id/code for asset set, duplicate id/path/hash, live
bytes/hash, engine missing/path/recovery binding, reference/unreferenced counts,
occurrence set/duplicate, Markdown path/target resolution, ownership, closure,
finding, engine-image cardinality and MIME.

Each case mutates its real physical ASSET_PROVENANCE/live asset/engine/recovery
or Markdown selector with a distinct callable. Apply only exact literal
transport reseals needed to pass inventory/QA/provenance without repairing the
target. Extend production verifier to enforce the 204 asset rows, 112+92
conservation, unique identities, occurrence resolution and recovery binding.
No COMMANDS proxy.

Each uses one `_test_verify`, exact earliest code and full closed audit with
real hashes, PASS, zero outside/undeclared/residue. Preserve completed families
and collect 371. Run AST 21 in explicit chunks, representative regression,
BLD 3 and collect via Python `-B`/no-cache. Receipt embeds all 21 full objects
and digest. Complete only 21/21; no redesign/live/cleanup.
