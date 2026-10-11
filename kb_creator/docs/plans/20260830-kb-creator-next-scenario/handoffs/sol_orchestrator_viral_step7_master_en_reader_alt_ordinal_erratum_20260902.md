# Viral Step 7 reader-alt ordinal erratum

This integration erratum corrects one mapping sentence in
`sol_orchestrator_viral_step7_master_en_asset_alt_config_assignment_20260902.md`
(SHA-256
`064910D0173911EF3DF754F14AAD8471E76ACB87BBA05488B9312E1FDB76F203`)
and supersedes the orchestrator's earlier `placement_index + 1` message.

The authoritative architecture receipt already defines ordinal as the one-based
**reader-asset order**, not the raw placement index. Evidence-only assets are
interleaved in the full asset sequence, so reader `placement_index` values are
not contiguous.

The exact mapping is:

1. select only assets whose representation is `reader`;
2. sort those 107 rows by their existing numeric `placement_index` ascending;
3. require the 107 placement indices to be unique and preserve them unchanged;
4. bind the alt ledger with `enumerate(sorted_reader_assets, start=1)`;
5. require enumerated ordinal closure exactly 1..107.

Do not compute ledger ordinal as `placement_index + 1`. Do not reorder the full
asset list or renumber any placement index. All 35 owner changes, all 107 exact
alt strings and every other packet constraint remain unchanged.

This erratum authorizes only continuation of the already bounded asset/alt config
subphase; it grants no other write, candidate, build, test, release or acceptance.
