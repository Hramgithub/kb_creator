# Task packet — independent B1c6 asset-provenance implementation review

## Review declaration

- Reviewer: fresh independent `gpt-5.5` / high critic.
- `review_kind`: `implementation`.
- Do not implement, materially redesign, or edit implementation/tests.
- Orchestration ownership remains with main chat (`gpt-5.6-sol` / medium).
- Candidate state: non-frozen implementation checkpoint; no canonical v2 config
  or built candidate exists.

## Bound approvals and receipts

- Architecture receipt SHA-256:
  `B37F37EF54885AEC1CFC4CEF557D31D326E603D5EA70F9BEA919C42C18162E5C`.
- Architecture approval receipt SHA-256:
  `F46457EB86DE9E5499C8272C6B72C23EAE0D80B42E24F591906B14589230B6E9`.
- Engineering task packet SHA-256:
  `7BD261B3FE9498D7BB86AEC242CDC1C90BC69763FD442A291BD415A6F0AA764D`.
- Initial honest CHANGES_REQUIRED engineering receipt SHA-256:
  `73C27869C6285E546C569FB03FE62AED90474215C6AE022545646BE0C3C638CD`.
- Final engineering receipt:
  `terra_engineering_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_final_continuation_20260903.md`,
  SHA-256
  `03CBFA8FEE1A4D4E0A1D60A1E37721F6E4AB2FE3B746AD6A38AC7852DEA1E05D`.

## Bound implementation hashes

| File | SHA-256 |
|---|---|
| `kb_creator/scripts/build_scenario_master_en.py` | `C496B8649E36C8D656C1CC93C25689B97E263339F7B12775A3D24C5CFBE80D3E` |
| `kb_creator/tests/test_build_scenario_master_en.py` | `BFBA044879B69C229EF578046D8190083E3B3A989C7DFF20442D8C2BF781F361` |
| `kb_creator/scripts/verify_scenario_master_en.py` | `E593D0B9EEA9CC1E71642DBC2527774FDB923D74914A52684391623CD9A8E5C1` |
| `kb_creator/tests/test_verify_scenario_master_en.py` | `2B3A1BA958CD65FE4E7E1930510300BF272BE836601EE917639677F7FD741B13` |
| unchanged author | `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C` |
| unchanged author tests | `58ED6C9FF6FC5A67130830F3F4731A5D68695E6F7E6877B0D6E09786D51D5EAE` |

## Root evidence to reproduce

- Focused B1c6 matrix: `Ran 4 tests in 95.861s / OK`.
- Exact scoped regression: `Ran 128 tests in 317.982s / OK`.
- Frozen-v1 builder/verifier preflight-only: both `preflight_passed` with
  accepted identities.
- Guarded public-v2 pair: `Ran 2 tests in 25.616s / OK`, stopping at builder
  `v2 asset placement mismatch` and verifier `E_V2_ASSET: placement`.
- Real binding: 125 total, exact 16 Markdown / 100 visual / 9 provisional,
  93 reader assets.
- No canonical v2 config, Candidate D, `__b1c6` target, phase temp, render,
  MASTER_EN or downstream output.

## Required independent review

1. Verify all bound hashes and inspect both implementations independently.
2. Confirm canonical/legacy routing is universal and homogeneous, with no
   scenario-name, test-only, environment, or call-path bypass and no canonical
   downgrade through legacy aliases.
3. Confirm safe binary resolution rejects path escape and reparse-point file or
   ancestor and binds path plus digest, bytes, magic MIME and dimensions.
4. Independently attack Markdown binding: donor/duplicate span, owner-kind,
   classification, page/ranges/UTF-8, marker digest, marker target and a foreign
   path carrying borrowed digest text.
5. Independently attack visual binding: manifest identity/row/path/digest,
   duplicate/missing row, comparison identity/status/schema, companion hash and
   source PDF, selected view/raw index/source membership, block type/page/bbox/
   hash and duplicate/missing block.
6. Independently attack provisional binding: PDF identity/path/bytes/digest,
   page/index, actual MediaBox/rotation, every closed recipe field, derived
   output MIME/dimensions and non-null binary. Confirm no rendering occurs.
7. Confirm builder and verifier do not share the author/B1c4 oracle and that
   tests reach the B1c6 helper rather than being intercepted by an earlier gate.
8. Confirm B1c4/B1c5 negative gates and frozen-v1/legacy positives remain intact.
9. Reproduce the exact 16/100/9 binding and 93-reader placement next seam; no
   later placement implementation may be present.
10. Confirm no protected historical candidate/staging root was changed or
    removed and no output/temp residue exists.

## Forbidden actions

- No implementation or test edits.
- No canonical config, candidate, render/review, MASTER_EN/RU, HTML or PDF.
- Do not change plan/context/status/governance or protected roots.
- Create only one immutable implementation-review receipt.

## Deliverable

The receipt must include `review_kind: implementation`, explicit statement
that no implementation or material design was performed, hashes/commands,
adversarial probes with exact builder/verifier outcomes, P0/P1/P2 findings,
no-output checks, and one terminal decision:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C6_IMPLEMENTATION`, or
- `REJECTED_V2_COMPLETE_AUTHORING_PHASE_B1C6_IMPLEMENTATION`.
