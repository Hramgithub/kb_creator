# Terra engineering receipt — Viral v2 B1c6 asset-provenance input binding

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1c6-asset-provenance-input-binding`.
- Role and ownership: reusable code/test engineering (`gpt-5.6-terra` / medium policy); orchestration remains main chat (`gpt-5.6-sol` / medium).
- Assignment state: matched; actual platform model/effort unavailable. Scoped override: none.
- Timestamp: 2026-09-03 Europe/Moscow. Elapsed time: approximately 35 minutes. Token use: unavailable.

## Scope and result

Changed only the assigned builder/verifier and their tests. Each implementation now dispatches by row shape, preserves the all-legacy fixture branch, rejects a mixed canonical/legacy collection, validates the canonical closed row shape, binds Markdown markers and visual manifest/comparison evidence independently, and advances the real 125-row input to the intentional placement seam. No author, B1c4/B1c5, plan/context/status, source, v1, config, candidate, output, render, or review artifact was edited.

The direct real-row diagnostic returned the symmetric result in both implementations:

`{'markdown_image_reference': 16, 'visual_region': 100, 'reviewed_provisional_full_page': 9}`, `reader: 93`.

## Files and hashes

Starting hashes matched the task packet for all four owned files.

| File | Final SHA-256 |
| --- | --- |
| `kb_creator/scripts/build_scenario_master_en.py` | `CD8A1C3322A70EBD48AAD8BBD58B04041E2E1F2C9C883CD201C7B9F8FC093E06` |
| `kb_creator/tests/test_build_scenario_master_en.py` | `3144EF154077276B989DFCE414161E3700A2193B6B28B88C92CB6D9F646FE6B3` |
| `kb_creator/scripts/verify_scenario_master_en.py` | `13C1BADF064FC7B86BA3EF08481D91B6B73261A0E2AA80E8022CA9600BD1A33B` |
| `kb_creator/tests/test_verify_scenario_master_en.py` | `31268EDB4E4C37564F3C9620758013619E8511848148AB8F98664927E6DB7191` |

## Verification evidence

- `python -m py_compile` over the four owned files: exit 0.
- `python -m unittest -q kb_creator.tests.test_author_viral_master_en_v2_config kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`: exit 0.
- Guarded public-v2 placement checks: exit 0; literal result: `Ran 2 tests in 26.193s` / `OK`. Builder raises `v2 asset placement mismatch`; verifier raises `E_V2_ASSET: placement`; both temporary inputs clean up.
- Real canonical helper diagnostics passed in each independently implemented helper with exact `16/100/9` and `93` reader rows.

## Blockers, risk, and next action

This is not ready for independent implementation review: the packet's full mandatory mutation matrix and frozen-v1/no-output command set were not completed, and the provisional render recipe currently validates identity/page/MediaBox-derived dimensions but needs the remaining closed recipe/rotation assertions and dedicated negative tests before review. No candidate/output was created by the commands above.

Exact next seam after completing those engineering requirements remains the unimplemented 93-reader placement union: builder `v2 asset placement mismatch`; verifier `E_V2_ASSET: placement`; first source-ordered id `viral-accepted-ed4012725c597dbcf6fca51e55faeb883a53f6f1d2c9ee7496c667460d37c860`.

`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ENGINEERING`
