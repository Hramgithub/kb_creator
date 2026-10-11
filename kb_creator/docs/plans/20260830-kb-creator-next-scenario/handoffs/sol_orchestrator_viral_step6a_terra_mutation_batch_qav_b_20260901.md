# Terra engineering assignment: Viral Step 6A QAV batch B

Sequential implementation under the accepted parent packet plus accepted
SCH/QAV taxonomy amendment. This batch owns only four QA authority-hash bindings
and nine exact QA scalar values. Terra owns engineering; Luna does not implement
code, tests, fixtures, or mutation audit.

## Baseline and writes

- Library: `0F891304301007D14D6BCB10DBA8526DC14988591C000D75755ADFD4CFE63627`.
- Tests: `6FED8CE2797E8237A2187681A59C2AC1A7DFC5C3221E3F51103B2C22993DAEC4`.
- QAV-A receipt:
  `5A08C25D42FCCAE87C154FCBC505125F4D71BEF9196FECA1BEC8D2CE9FFEE5EC`.
- Editable: those two material files and one new absent-before receipt
  `terra_engineering_viral_step6a_mutation_batch_qav_b_20260901.md` only.
- Everything else is read-only; no live, candidate, protected-119, cache, Git,
  commit, push, cleanup, or unrelated write. Preserve the pre-existing cache
  baseline and prove zero newly attributable residue.

## Implement exact QAV subset B: 13

Authority-hash bindings (4):

- `QAV-authority-contract -> E_QA_CONTRACT_HASH` at
  `candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256`;
- `QAV-authority-source -> E_QA_SOURCE_HASH` at `#/source_sha256`;
- `QAV-authority-recovery-manifest -> E_QA_RECOVERY_MANIFEST_HASH` at
  `#/recovery_manifest_sha256`;
- `QAV-authority-recovery-evidence -> E_QA_RECOVERY_EVIDENCE_HASH` at
  `#/recovery_evidence_sha256`.

Scalar values (9): for each exact field
`page_count, handout_count, block_count, asset_count, contact_sheet_count,
navigation_anchor_count, referenced_asset_count, unreferenced_asset_count,
open_blocker_count`, implement
`QAV-scalar-<field>-wrong -> E_QA_SCALAR_<FIELD>` on its real root-QA selector.

Each case uses a distinct physical root-QA callable and literal reseal `()`.
Extend the one shared production verifier in binding phase order after closed
shape/schema admission; use exact authority bytes/hashes and production-derived
scalar facts. No case/family routing, generic proxy, expected-code derivation,
QAV-C/D, REG, or unrelated verifier change.

Each row executes one `_test_verify`, obtains its declared exact earliest code,
and emits a full real closed 16-field Section-11 audit with `PASS` and zero
outside reads, undeclared changes, or fixture residue. Run all 13 in bounded
chunks, representative QAV-A/SCH-alias/CMD/clean regression, BLD 3, and collect
exactly 371 using Python `-B` with disabled pytest cache.

Before creating the immutable receipt, validate all 13 full objects and compute
packet-formula canonical bytes/digest in memory. The receipt embeds objects,
rows/digest, commands/native exits/output hashes, material/cache pre/post,
exact changed paths, and token availability. Complete only 13/13; otherwise
honest BLOCKED. Do not run full 119/490/live or claim Step-6A/release acceptance.
