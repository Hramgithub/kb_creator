# Terra engineering assignment: Viral Step 6A CMD batch A

Sequential implementation under accepted packet sections 5.3, 6-7, 8.3 CMD,
11 and 12. This is CMD subset A only.

## Baseline and writes

- Library: `3FC00FDBC18870CE081EA3C9590291B217919B6E40DAE5F2703601584E842025`.
- Tests: `6AAB4AFFB2515C33C941152361ED3132DA4E35D34BEAF21457DBEBBDB081523E`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_cmd_a_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write.

## Implement exact CMD subset A: 24

Implement:

- action/state 5: action missing/duplicate/extra/reordered and state promoted;
- flag 12: missing and true for each of the six exact false fields;
- runtime arguments 6: missing/wrong for `source_flag`, `run_root_flag`,
  `source_relative_path`;
- external locator used 1.

Use the exact descriptive ids/codes from packet section 8.3. Every row mutates
its real physical COMMANDS v3 selector with a distinct callable. Apply exact
literal inventory/QA reseals without repairing the target. Extend the shared
production verifier for exact action order, state, false flags, runtime
arguments and external-source prohibition. No shared generic proxy.

Each uses one `_test_verify`, exact earliest code and full closed audit with
real hashes, PASS, zero outside/undeclared/residue. Preserve completed families
and total collect 371; do not implement CMD counts/sheets in this subset. Run
24 rows in explicit chunks, representative regression, BLD 3 and collect via
Python `-B`/no-cache. Receipt embeds all 24 full objects and one canonical
digest. Complete only 24/24; no redesign/live/cleanup.
