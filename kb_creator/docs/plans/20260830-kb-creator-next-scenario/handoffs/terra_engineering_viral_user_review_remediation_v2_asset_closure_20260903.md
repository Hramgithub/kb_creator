# Viral remediation v2 asset-closure receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-asset-closure`
- Contributor role: `nri-engineer`
- Requested model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `partial_asset_closure`
- Scoped override: none
- Timestamp: `2026-09-03T00:25:00+03:00`
- Elapsed time: approximately `00:07:00`
- Token use: unavailable

## Changed paths

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- this immutable receipt

## Result and verification

The v2 builder now validates reader asset policy fields and closed values for
duplication resolution, quality stage, semantic role and one declared placement
class. It validates repository-contained source path/bytes/SHA-256, copies only
reader-value binaries into the private staging candidate, rechecks copied
identity, records copied identity in the v2 manifest and excludes evidence-only
assets from both copied assets and reader Markdown. It rejects invalid placement
targets and reader assets on excluded pages.

```powershell
python -B -m pytest -q kb_creator/tests/test_build_scenario_master_en.py
# 46 passed in 9.71s

python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py
# passed
```

The synthetic regression verifies successful byte-identical reader-binary copy,
reader Markdown reference and illegal quality-stage rejection. Existing atomic
candidate, typed serializer and sealed-v1 tests remain in the same suite.

## Precise residual gap

`READY_FOR_V2_OUTPUT_VERIFIER` is not returned. Placement presently validates a
single declared target and emits assets through the asset event; it does not yet
prove actual before/after/inside placement relative to a distinct event, detect
multiply bound reader assets, or cover all three placement classes. The package
also lacks required two-absent-root byte comparison and negative tests for
fragment identity drift/excluded-page event leakage. These are builder-only
asset/determinism gaps; no verifier or real Viral policy/evidence/candidate was
modified.

Completion token: `PARTIAL_V2_ASSET_PLACEMENT_AND_DETERMINISM_GAP`
