# Amended Terra dispatch: Viral Step 6A QAV-D2

This dispatch binds the accepted INV/QAV inventory-metadata taxonomy amendment.
Terra owns all code, test, fixture, mutation-audit, and engineering-evidence work
in this batch. Luna is not assigned to implementation: a later Luna QA task may
only execute already prepared QA scripts/commands and capture their raw evidence.

## Admission authority

- Parent packet:
  `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- Parent independent review:
  `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`.
- SCH/QAV taxonomy amendment / independent review:
  `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A` /
  `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`.
- INV/QAV inventory-metadata amendment:
  `779B641EBD2DC55F3A4725AA0345D5286CB41CE608A4465B8B5AE43DC9156606`.
- Fresh independent GPT-5.5/high ACCEPT review:
  `12007AAFBA3838FE76EF0FFD54BBF2C4253197D08DFF41F8A63C4FD32A5A04EB`;
  findings P0/P1/P2: none.
- INV receipt:
  `A559B08DFF5A4EB75F41AD075ECB91E74797956502A210B08B62C78FCFE78518`.
- QAV-D1 receipt:
  `12A38CB2267EDF6E85184BC8728A4BCCC8B1E14424F14D4BB8BE984FD37DA4E7`.
- Frozen pre-D2 library baseline:
  `FCAE2693C03A35382CADF35B6474E7A173670D65FD6D428726E56E71FF4BDA46`.
- Frozen pre-D2 focused-test baseline:
  `3A7DB49164A11DF5C7EB5663639914668ACE1AAA22F72AEC2F69F66B0E474357`.
- The D2 receipt is absent before dispatch.

Any authority or baseline mismatch before the first write is a stop condition.

## Exact D2 implementation matrix

Keep these as the final four QAV members, in this order. Each has a fresh
fixture, a distinct named callable, exactly one `_test_verify`, one full
16-field audit object, empty transport/reseal tuples, and no QA regeneration.

1. `QAV-inventory-rule-wrong`
   - selector: `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule`;
   - mutation: replace the exact canonical literal with
     `all_regular_except_qa`;
   - earliest code: `E_QA_INVENTORY_RULE`.
2. `QAV-inventory-count-wrong`
   - selector: `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count`;
   - mutation: set exact integer `500`;
   - earliest code: `E_INV_CARDINALITY`.
3. `QAV-inventory-digest-wrong`
   - selector: `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256`;
   - mutation: set exact string `"0" * 64`;
   - earliest code: `E_INV_DIGEST`.
4. `QAV-inventory-array-wrong`
   - selector:
     `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md`;
   - mutation: remove only the row whose `path == "RECONSTRUCTED_EN.md"`,
     without changing declared count or digest;
   - earliest code: `E_INV_ORDINARY_ROW_MISSING`.

Required callable names are `mutate_QAV_inventory_rule_wrong`,
`mutate_QAV_inventory_count_wrong`, `mutate_QAV_inventory_digest_wrong`, and
`mutate_QAV_inventory_array_wrong`. Case/family/audit/pytest/environment data
must never enter `_strict_verify` or influence production error selection.

## Canonical rule and dead-code retirement

The library defines and both TEST and production-shaped writers emit exactly:

`every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json`

Phase 8 checks that exact literal and emits only `E_QA_INVENTORY_RULE` for a
mismatch. Do not accept or normalize the short legacy string. Preserve phase-6
INV authority and its order. Remove the later unreachable
`E_QA_INVENTORY_ARRAY`, `E_QA_INVENTORY_COUNT`, and
`E_QA_INVENTORY_DIGEST` branches, expectations, and redundant candidate-record
recomputation from the two mutable material files.

## Exact alias ceiling and count invariants

Exactly five cross-family identical-state alias pairs are permitted globally:

1. `SCH-QA-required-top-member-missing` / `QAV-top-asset_count-missing`;
2. `SCH-qa-unexpected-top-member` / `QAV-top-extra`;
3. `INV-cardinality-wrong` / `QAV-inventory-count-wrong`;
4. `INV-digest-wrong` / `QAV-inventory-digest-wrong`;
5. `INV-ordinary-row-missing` / `QAV-inventory-array-wrong`.

All ten members retain distinct case ids, callable objects/names, fixtures,
audit objects, and audit rows. Rerun all ten after D2 plus
`QAV-inventory-rule-wrong`. No sixth pair is allowed. Counts remain INV `18`,
QAV `90`, negative `368`, BLD `3`, focused `371`.

## Three-path write scope

Terra may modify only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. absent-before
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_d2_20260901.md`.

Everything else is read-only. No candidate, source, live command, protected
119, combined 490, plan/context/status, prior receipt, governance, cache,
cleanup, Git, commit, push, promotion, publication, or release mutation is
authorized. Preserve the recorded pre-existing cache identities and prove zero
newly attributable residue.

## Completion evidence

Run the exact acceptance commands from amendment section 10 with `python -B`
and pytest cache disabled. Required native results are D2 `4 passed`, INV alias
`3 passed`, shape alias `4 passed`, representative `3 passed`, BLD `3 passed`,
and exactly `371 tests collected`. The retired-code search must return no match.

The immutable Terra receipt must contain all four closed audit objects in
registry order, their canonical UTF-8/LF bytes and SHA-256, the separate
five-pair callable-identity table, exact commands/exits/output hashes,
material/cache pre/post identities, exact changed paths, elapsed time, and
token use or `unavailable`. Complete only if every requirement passes;
otherwise write a truthful BLOCKED receipt and stop without widening scope.

This is engineering completion only. Independent QA execution, final
implementation/process criticism, semantic review, MASTER_EN, candidate
acceptance, production, and release all remain downstream.
