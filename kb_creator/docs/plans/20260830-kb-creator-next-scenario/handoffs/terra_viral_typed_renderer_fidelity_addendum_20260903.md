# Viral typed-renderer fidelity addendum

- Goal / step: `20260830-kb-creator-next-scenario` / typed renderer fidelity integration correction.
- Contributor role / requested effort: Terra reusable code and test engineering / `medium`.
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Actual platform model / effort: unavailable.
- Timestamp: `2026-09-03T23:03:25+03:00`.
- Elapsed time: approximately 00:09:00.
- Token use: unavailable.

## Correction

Supersedes only the placement fallback in the preceding receipt. A reader asset
without an explicit placement now fails `v2 asset placement missing`; it is not
silently emitted at its declared event position. Shared-target placement order
is now keyed by each asset event's `order_key`, rather than asset-array order.
The independent verifier separately reconstructs the same required source-event
order from config and rejects candidate range order drift with
`E_V2_ASSET: placement-source-order`.

## Files changed or checked

- Changed: `kb_creator/scripts/build_scenario_master_en.py`
- Changed: `kb_creator/scripts/verify_scenario_master_en.py`
- Changed: `kb_creator/tests/test_build_scenario_master_en.py`
- Checked, not changed: author/config/source/reconstruction/v1/candidate paths;
  no Git operation and no real candidate build.

The new focused regression reverses same-target asset declaration rows while
holding source asset events fixed, and proves output remains in source-event
order. It also proves an omitted placement fails explicitly.

## Verification, blockers, next action

```powershell
python -B -m unittest kb_creator.tests.test_build_scenario_master_en.ViralV2B1c4AssetAuditTests.test_v2_chunk_ledger_relocation_ranges_and_literal_preservation kb_creator.tests.test_build_scenario_master_en.ViralV2B1c4AssetAuditTests.test_v2_heading_levels_and_canonical_asset_marker kb_creator.tests.test_verify_scenario_master_en.ViralV2B1c4VerifierAuditTests.test_v2_builder_baseline_candidate_is_accepted
# Ran 3 tests in 2.662s — OK
git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
```

The same source-backed author resolver must supply explicit canonical
placements before canonical reader asset events can be materialized. This is
intentionally an integration dependency, not a renderer fallback.
