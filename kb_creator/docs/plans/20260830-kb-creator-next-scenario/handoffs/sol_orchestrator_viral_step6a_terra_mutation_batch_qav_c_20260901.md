# Terra engineering assignment: Viral Step 6A QAV batch C

Sequential implementation under the accepted parent packet and SCH/QAV
taxonomy amendment. This batch owns only the QA `counts` map. Terra owns all
engineering; Luna does not implement code, tests, fixtures, or mutation audit.

## Baseline and writes

- Library: `5351BDFCA2A5CCE91205DF485A05FB4E7BA5B5EBBC691F837E13832EC1949154`.
- Tests: `8EA8E4E96A24249D8E365B750D3552EF3B4AB611E5A0036DE02BE27096709BB9`.
- QAV-B receipt:
  `652DEEDC0DD415853FB7193148DBABC5041C06909DAE0AC83C1C0295E01B8DEA`.
- Editable: those two material files and one new absent-before receipt
  `terra_engineering_viral_step6a_mutation_batch_qav_c_20260901.md` only.
- Everything else is read-only; no live, candidate, protected-119, cache, Git,
  commit, push, cleanup, or unrelated write. Preserve pre-existing cache and
  prove zero newly attributable residue.

## Implement exact QAV subset C: 28

For each exact QA count key
`assets, back_cover, contact_sheets, engine_images, engine_payload, handouts,
maps, navigation_anchors, open_blockers, pages, pregens, referenced_assets,
renders, unreferenced_assets`, replace generic selector placeholders with the
two exact descriptive physical cases:

- `QAV-counts-<key>-missing -> E_QA_COUNTS_<KEY>`;
- `QAV-counts-<key>-wrong -> E_QA_COUNTS_<KEY>`.

Each case uses a distinct callable on
`candidate/RECONSTRUCTED_EN.qa.json#/counts/<key>` and literal reseal `()`.
Extend the one shared production verifier with a closed 14-key count map and
exact production-derived values in binding ordinal order. Missing and wrong
must stop at the declared per-key code. Do not route by family/case id, use a
generic mutation proxy, derive expected code from the exception, or implement
QAV-D/REG/unrelated checks.

Every row executes one `_test_verify` and emits a full real 16-field audit with
exact code, `PASS`, and zero outside reads, undeclared changes, or fixture
residue. Run all 28 in bounded chunks, representative QAV-A/B/SCH/CMD/clean
regressions, BLD 3, and collect exactly 371 using Python `-B` with pytest cache
disabled.

Before creating the immutable receipt, validate all 28 objects and compute the
packet-formula canonical bytes/digest in memory. The receipt embeds objects,
rows/digest, commands/native exits/output hashes, material/cache pre/post,
exact changed paths, and token availability. Complete only 28/28; otherwise
honest BLOCKED. Do not run full 119/490/live or claim Step-6A/release acceptance.
