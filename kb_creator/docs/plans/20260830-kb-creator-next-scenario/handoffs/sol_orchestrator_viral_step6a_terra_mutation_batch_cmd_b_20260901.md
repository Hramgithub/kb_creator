# Terra engineering assignment: Viral Step 6A CMD batch B

Sequential implementation under accepted packet sections 5.3, 6-7, 8.3 CMD,
11 and 12. This is CMD counts subset B only. Terra/medium owns engineering;
Luna is not an implementation owner.

## Baseline and writes

- Library: `7ED7D2E3087BBF5F62FC1EECE9F4220D59B0D224C6C5F13E482B2255048AD456`.
- Tests: `0ADC426AE9ED31C5825D668E7D91D66B5DEDD7DAA3FD117A273DD15F89117AA2`.
- Editable: those two files and one new receipt
  `terra_engineering_viral_step6a_mutation_batch_cmd_b_20260901.md` only.
- Everything else is read-only; no live, candidate, protected-119, cache, Git,
  commit, push, broad cleanup, or unrelated file write.
- Preserve the immutable incomplete CMD-A receipt and its supplemental audit
  completion receipt; do not rewrite either.

## Implement exact CMD subset B: 22

For every exact COMMANDS v3 count key
`pages, renders, contact_sheets, handouts, maps, pregens, back_cover, assets,
referenced_assets, unreferenced_assets, markdown_references`, implement the two
descriptive cases:

- `CMD-count-<key>-missing -> E_COMMAND_COUNTS_<KEY>`;
- `CMD-count-<key>-wrong -> E_COMMAND_COUNTS_<KEY>`.

Every case mutates its real physical
`candidate/evidence/COMMANDS.json#/counts/<key>` selector with a distinct
callable. Apply only the exact literal `inventory, qa` transport reseals; do
not repair the target. Extend the shared production verifier with exact count
enforcement against the production-shaped fixture facts. Do not use a generic
proxy, derive expected codes from observed exceptions, or implement the 15 CMD
sheet/action cases in this batch.

Each case must execute one `_test_verify`, obtain its declared earliest code,
and emit the full closed 16-field Section-11 audit row with real hashes,
`result: PASS`, and zero outside reads, undeclared changes, or residue. Preserve
all completed families, exact collection `371`, and BLD `3`. Run all 22 rows in
bounded explicit chunks, a representative clean-path/completed-family
regression, BLD 3, and collect via Python `-B` with cache disabled.

The immutable receipt must embed all 22 complete canonical objects, their exact
ordered ids/codes, one recomputed canonical digest, pre/post hashes, commands,
native exits, counts, changed-path inventory, and explicit token availability.
Complete only on 22/22; otherwise write an honest BLOCKED receipt. No redesign,
live execution, promotion, cleanup, or release claim.
