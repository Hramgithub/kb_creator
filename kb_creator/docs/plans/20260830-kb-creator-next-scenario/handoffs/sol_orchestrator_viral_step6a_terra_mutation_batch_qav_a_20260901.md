# Terra engineering assignment: Viral Step 6A QAV batch A

Sequential implementation under accepted packet sections 5.3, 6-7, 8.3 QAV,
11 and 12. This batch owns only QA top-level closed shape and state. Terra owns
engineering; Luna does not implement code, tests, fixtures, or mutation audit.

## Baseline and writes

- Library: `2309CD5015B89908A5B751916F46B4C601AFB8E121EB338FC6450B7BAAE49FAC`.
- Tests: `7B9AEC1EF0BA2870E2021544912538FE3234DAF92D0E38E34F16285118649DCF`.
- CMD-C audit completion receipt:
  `D5761C6151EC00F43AA1A00A67A031D3DFF23F31980B0680D645CBCF3DA4A120`.
- Editable: those two material files and one new absent-before receipt
  `terra_engineering_viral_step6a_mutation_batch_qav_a_20260901.md` only.
- Everything else is read-only; no live, candidate, protected-119, cache, Git,
  commit, push, cleanup, or unrelated write. Preserve pre-existing cache
  identities and prove zero newly attributable residue.

## Implement exact QAV subset A: 25

For every exact current QA top-level field, implement one physical missing case
`QAV-top-<field>-missing -> E_QA_SHAPE`:

`asset_count, block_count, contact_sheet_count, contract_sha256, counts,
gate_results, handout_count, historical_material_opened, main_scripts_invoked,
navigation_anchor_count, open_blocker_count, output_inventory,
output_inventory_count, output_inventory_rule, output_inventory_sha256,
page_count, recovery_evidence_sha256, recovery_manifest_sha256,
referenced_asset_count, schema, source_sha256, state,
unreferenced_asset_count`.

Also implement:

- `QAV-top-extra -> E_QA_SHAPE`;
- `QAV-state-promoted -> E_QA_STATE`.

Each case uses a distinct callable against the real physical root
`candidate/RECONSTRUCTED_EN.qa.json` selector. Because root QA is excluded from
its own inventory, use only the literal reseal policy declared by the accepted
registry; do not invent a transport reseal or repair the target. Extend the one
shared production verifier with exact closed top-level shape before any QA
field-specific check, followed by exact state enforcement. No generic proxy,
derived expected code, QAV-B/C/D, REG, or unrelated verifier change.

Each row executes one `_test_verify`, obtains its exact earliest code, and emits
the full closed 16-field Section-11 audit with real hashes, `PASS`, and zero
outside reads, undeclared changes, or fixture residue. Run all 25 in bounded
explicit chunks, representative completed CMD/clean-path regression, BLD 3,
and collect exactly 371 using Python `-B` and disabled pytest cache.

Before creating the immutable receipt, validate all 25 full objects and compute
the packet-formula canonical bytes/digest from the final ordered rows in memory.
The standalone receipt records the objects, canonical rows/bytes/digest,
commands/native exits and output hashes, material pre/post hashes, pre-existing
cache before/after, exact changed paths, and token availability. Complete only
25/25; otherwise write an honest BLOCKED receipt. No live execution, full
119/490, promotion, cleanup, Step-6A acceptance, or release claim.
