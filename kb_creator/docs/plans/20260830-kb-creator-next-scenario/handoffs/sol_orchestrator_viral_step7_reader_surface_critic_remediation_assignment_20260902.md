# Viral Step 7 — reader-surface critic remediation

## Ownership and frozen inputs

- Engineer: `nri-engineer`, `gpt-5.6-terra`, medium.
- Orchestrator keeps integration/release authority. The engineer is not alone in
  the checkout and must not revert or clean unrelated work.
- Frozen config: 707368 bytes / SHA-256
  `EEE2B0BBE8EB0F8862F09C884818B1C20C8DC023FCC01B504E963AFD3346438E`.
- Frozen accepted reconstruction v4 inventory SHA-256
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Rejected implementation review receipt SHA-256
  `5B3DD4244CFB5B7CF5DB89C6D704ED944CFC77FE704024BAB496168204AA755B`.
- Candidate C remains absent. Candidate A/B and all frozen inputs are read-only.

## Write scope

Only:

1. `kb_creator/scripts/build_scenario_master_en.py`
2. `kb_creator/scripts/verify_scenario_master_en.py`
3. `kb_creator/tests/test_build_scenario_master_en.py`
4. `kb_creator/tests/test_verify_scenario_master_en.py`
5. One new receipt:
   `terra_engineering_viral_step7_reader_surface_critic_remediation_20260902.md`

Do not edit config, accepted v4, source, candidates, prior receipts,
plan/context/status, Git or downstream outputs. Do not run MinerU or historical
371/119/490 suites. Do not build Candidate C or scratch candidates.

## Required remediation

### 1. Verifier-owned public contract

Implement a verifier-local closed `reader_surface` parser/resolver. It must not
import builder internals or trust builder success. Independently enforce:

- exact top/nested keys and schema version;
- selector shapes and positive occurrence rules;
- production counts 25 semantic / 22 suppression / 107 reader alts;
- exact LF-normalized raw endpoints/hashes, semantic order and normal-claim
  owner containment;
- suppression owner/occurrence/disposition/replacement/full-range hash and
  non-overlap;
- exact heading policy and emitted owner-local heading invariants;
- alt policy and asset-ID binding, excluding evidence-only rows;
- absence of residual configured technical description/suppression text.

### 2. Candidate-local reader-surface evidence

Add one closed provenance section, for example `reader_surface`, rather than
scattered implicit success. It must be sufficient for independent recomputation
and later full-reader QA and contain deterministic evidence for:

- all 25 semantic rows: ID/order/page/expected owner, exact source char+UTF-8
  byte range/hash, and the normal claim relationship;
- all 22 suppressions: ID/page/owner, exact source char+byte range/raw SHA,
  disposition, replacement asset ID, and proof the raw range is absent from
  reader prose while the declared replacement relationship is preserved;
- source-heading outcomes: owner, source location/form/level and emitted
  location/form/level or strong-label overflow/duplicate result;
- all 107 reader alt outcomes by full asset ID, emitted path/alt and policy
  result; evidence-only assets must not consume a reader ordinal.

The verifier must recompute these outcomes from immutable pages, config and
candidate and require exact closed equality. Do not merely copy config rows.

### 3. Provenance input identities

Recursively close and validate `provenance.inputs` and `producer`:

- contract/config/source path, bytes and SHA against the actual CLI inputs;
- accepted reconstruction identity against config and the verified package;
- builder script path/SHA against the current repository builder identity;
- no extra/missing nested keys.

Add resealed candidate mutations for each identity class.

### 4. Suppression-aware conservation

Pass the already resolved suppression ledger into conservation. Prove every
suppression is non-overlapping, contained in exactly one declared owner claim,
and accounted exactly once; fail on missing/duplicate/outside-owner ranges or an
unaccounted reader deletion. Expose deterministic authorized suppression count
and/or bytes plus zero unauthorized blocks in QA/provenance, and make verifier
recompute it. Do not hardcode zero without consuming the ledger.

### 5. Compact targeted tests

Keep tests behavior-oriented and compact. Add builder and especially verifier
negative cases for:

- unknown keys at every reader-surface nesting level and invalid selector forms;
- wrong semantic count/order/hash/owner and normal-claim containment;
- wrong/zero/duplicate/overlap suppression endpoint/hash/owner/replacement;
- banned/empty/provenance alt, evidence-only ordinal confusion and asset-ID swap;
- mutated suppression/semantic/heading/alt sidecar outcomes;
- mutated contract/config/source/reconstruction/builder identities;
- suppression missing from conservation or outside its owner;
- representative p8/p55/p68/p46 and heading regressions from the architecture.

The verifier tests must directly mention and mutate the new public contract.

### 6. Staging cleanup regression

The builder currently leaves dot-prefixed staging roots when a candidate build
fails after staging creation. Ensure a build removes only the staging directory
it created on exception, never an existing candidate or sibling. Add a focused
test. Do not delete the four existing staging roots during this task; they are
outside this write scope and require separate integration handling.

## Verification and receipt

Run only the two focused test modules, `py_compile`, and scoped
`git diff --check`. The suite may grow beyond 53 but must stay compact; do not
create a generated mutation matrix. Record exact hashes, commands/results,
coverage mapping for every critic finding, remaining risks, and
`PASS_REMEDIATION` or `BLOCKED_REMEDIATION`. A pass reopens only a second
independent implementation review, not candidate creation.
