# Terra engineering receipt: Viral Step 6A QAV-D2

- Result: `COMPLETE_4_OF_4_PENDING_INDEPENDENT_QA_AND_CRITIC`.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; assignment state: platform-unverified; scoped override: none.
- Scope: only the canonical QA inventory-rule and four final D2 QAV physical mutations. No protected/live/candidate/Git/release work.
- Elapsed: approximately 20 minutes. Token use: unavailable.

## Admission and material identity

Verified pre-write library/test hashes: `FCAE2693C03A35382CADF35B6474E7A173670D65FD6D428726E56E71FF4BDA46` / `3A7DB49164A11DF5C7EB5663639914668ACE1AAA22F72AEC2F69F66B0E474357`; amendment/review hashes: `779B641EBD2DC55F3A4725AA0345D5286CB41CE608A4465B8B5AE43DC9156606` / `12007AAFBA3838FE76EF0FFD54BBF2C4253197D08DFF41F8A63C4FD32A5A04EB`; D2 receipt absent before creation.

Post-write library/test hashes: `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4` / `D3FA871BBA3DED04ECD216544B7A9A7EEECB95D4769DDF45612B412990F9D192`.

Changed paths: only `kb_creator/scripts/scenario_source_reconstruction.py`, `kb_creator/tests/test_scenario_source_reconstruction.py`, and this absent-before receipt. Pre-existing `.pyc` cache identity was preserved; no new attributable residue.

## Implementation and audit

Both writers emit the exact canonical literal `every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json`. Phase 8 rejects any other value with `E_QA_INVENTORY_RULE`. The unreachable late QAV inventory array/count/digest branches and their codes were retired; phase-6 INV remains earliest authority.

All full 16-field D2 `MutationAudit` objects were constructed in registry order with distinct named callables, fresh fixtures, literal empty reseal/transport tuples, one strict verification call, zero outside reads, no undeclared changes/residue, matching expected/observed code, and `PASS`:

| Case | Selector | Expected / observed |
|---|---|---|
| QAV-inventory-rule-wrong | `#/output_inventory_rule` | `E_QA_INVENTORY_RULE` |
| QAV-inventory-count-wrong | `#/output_inventory_count` | `E_INV_CARDINALITY` |
| QAV-inventory-digest-wrong | `#/output_inventory_sha256` | `E_INV_DIGEST` |
| QAV-inventory-array-wrong | `#/output_inventory/RECONSTRUCTED_EN.md` | `E_INV_ORDINARY_ROW_MISSING` |

Canonical UTF-8/LF audit rows use the accepted six-field tab formula: 4 rows, 534 bytes, SHA-256 `2F58364620D69FBFC6EC19A43C3877E81FAAC9123D027EF945D8BDA813DC6EA0`.

The exact five cross-family alias pairs were proved with ten distinct callable identities: SCH/QAV root-missing, SCH/QAV extra-root, INV/QAV cardinality, INV/QAV digest, and INV/QAV ordinary-row-missing. Counts: INV `18`, QAV `90`, negative `368`, unique mutation callables `368`, focused `371`.

## Native evidence

- D2 nodes: `4 passed`.
- All ten alias members plus D2 rule: `8 passed` (the three INV and four shape alias members, plus the rule, as dispatched).
- Representative D1/CMD: `3 passed`.
- BLD: `3 passed, 368 deselected`.
- Focused collection: `371 tests collected`.
- Retired-code search for `E_QA_INVENTORY_(ARRAY|COUNT|DIGEST)`: no match.

No blocker for this bounded engineering batch. Next action: independent bounded QA, then independent implementation/process criticism; release and semantic acceptance remain out of scope.
