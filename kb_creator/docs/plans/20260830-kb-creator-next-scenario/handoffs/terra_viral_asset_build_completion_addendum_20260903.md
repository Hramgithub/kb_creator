# Viral canonical asset-build completion addendum

- Goal / step: `20260830-kb-creator-next-scenario` / canonical v2 asset materialization.
- Contributor role / requested effort: Terra reusable code and test engineering / `medium`.
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`.
- Assignment state: `integration-ready-pending-author-input`.
- Scoped override: none.
- Actual platform model / effort: unavailable.
- Timestamp: `2026-09-03T23:55:00+03:00`.
- Elapsed time: approximately 00:18:00.
- Token use: unavailable.

## Completion delta

The builder now materializes an approved `reviewed_provisional_full_page`
`binary: null` asset in private candidate staging via its declared one-page
`pdftoppm` recipe, validates the PNG dimensions, and records only the resolved
candidate output identity in the v2 manifest. Markdown uses the deterministic
`assets/<asset_id>.png` path without modifying config.

The independent verifier now checks every such reader row against the candidate
manifest/output: deterministic output path, bytes/SHA-256, PNG decoding,
declared output dimensions, physical source page, and zero-based page index.
It remains independent of builder helpers. The canonical asset schema also
separates six immutable provenance fields from author-owned placement metadata.

## Evidence

```powershell
python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py
python -B -m pytest -q kb_creator/tests/test_build_scenario_master_en.py::ViralV2B1c4AssetAuditTests::test_v2_heading_levels_and_canonical_asset_marker kb_creator/tests/test_verify_scenario_master_en.py::ViralV2B1c4VerifierAuditTests::test_v2_builder_baseline_candidate_is_accepted
# 2 passed in 3.29s
```

## Remaining integration condition

The author is still emitting source-backed `anchor`, one-key `placement`, and
`source_order` rows. Root owns actual author-config preflight and the combined
module suite; no real candidate was built here. This addendum supersedes the
previous receipt's claim that recipe implementation had not begun.

