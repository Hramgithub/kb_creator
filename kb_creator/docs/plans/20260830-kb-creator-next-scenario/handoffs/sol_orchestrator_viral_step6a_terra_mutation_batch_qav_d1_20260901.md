# Terra engineering assignment: Viral Step 6A QAV batch D1

Sequential implementation under the accepted parent packet and SCH/QAV
taxonomy amendment. This batch owns only nine QA gates (missing plus wrong or
closed) and two false booleans. The four QA inventory-metadata cases are held
for separate D2 analysis/engineering. Terra owns implementation; Luna does not.

## Baseline and writes

- Library: `80FDFB895172EF58A02EB4019405DC4BD8F9DF9059533501B9A9A1002F108BC6`.
- Tests: `123AEF20B933B6E528F217481A5052F14BE6D8E0AECDCA1B53A4544FC8D88D7B`.
- QAV-C receipt:
  `346AEB9D11EB6749471DDB9218F4CB6AC86C5F8B1982F8ACED5EE6E79D61D0C6`.
- Editable: those two material files and one new absent-before receipt
  `terra_engineering_viral_step6a_mutation_batch_qav_d1_20260901.md` only.
- Everything else is read-only; no live, candidate, protected-119, cache, Git,
  commit, push, cleanup, or unrelated write. Preserve pre-existing cache and
  prove zero newly attributable residue.

## Implement exact QAV subset D1: 20

Use the exact nine production-shaped gate keys/values in ordinal order:

- `asset_conservation=pass`;
- `contact_sheet_coverage=pass`;
- `navigation_anchors=pass`;
- `page_1_5_modes=needs_review`;
- `page_coverage=pass`;
- `promotion=blocked_candidate_only`;
- `recovery_admission=pass`;
- `source_identity=pass`;
- `visual_review=needs_review`.

For each key create one distinct physical
`QAV-gate-<key>-missing -> E_QA_GATE_<KEY>` case. For the six `pass` gates,
create `QAV-gate-<key>-wrong -> E_QA_GATE_<KEY>` by setting a nonaccepted
value. For `page_1_5_modes`, `promotion`, and `visual_review`, create
`QAV-gate-<key>-closed -> E_QA_GATE_<KEY>` by fabricating closure. These are 18
cases total on `candidate/RECONSTRUCTED_EN.qa.json#/gate_results/<key>`.

Also implement:

- `QAV-historical-material-true -> E_QA_HISTORY`;
- `QAV-main-scripts-invoked-true -> E_QA_MAIN_SCRIPTS`.

Every case uses a distinct callable and literal reseal `()`. Extend the one
shared production verifier with the closed nine-key gate map, exact no-closure
values, then both false booleans in binding order. The TEST fixture/writer must
use those production-shaped facts, not its former two-gate summary. No
family/case routing, proxy mutator, expected-code derivation, QAV-D2 inventory
metadata, REG, or unrelated check.

Each node executes one `_test_verify` and emits a full real 16-field audit with
exact code, `PASS`, and zero outside reads, undeclared changes, or fixture
residue. Run all 20 in bounded chunks, representative QAV-A/B/C/SCH/CMD/clean
regressions, BLD 3, and collect exactly 371 with Python `-B` and cache disabled.

Before immutable receipt creation, validate all 20 objects and packet-formula
canonical bytes/digest in memory. Receipt embeds objects, rows/digest,
commands/native exits/output hashes, material/cache pre/post, exact changed
paths, and token availability. Complete only 20/20; otherwise honest BLOCKED.
No QAV-D2, 119/490/live, Step-6A, release, or semantic acceptance claim.
