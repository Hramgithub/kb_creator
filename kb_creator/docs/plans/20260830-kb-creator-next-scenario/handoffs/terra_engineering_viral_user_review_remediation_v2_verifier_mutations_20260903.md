# Viral remediation v2 verifier mutation-suite receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations`
- Contributor role: `nri-engineer`
- Requested model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `blocked_by_cross_component_contract_mismatch`
- Scoped override: none
- Timestamp: `2026-09-03T00:52:00+03:00`
- Elapsed time: approximately `00:05:00`
- Token use: unavailable

## Exact blocker

The requested representative fixture cannot be created under this tests-only
scope. The builder's v2 schema accepts the additional `contains` member and
requires it for every `structured_unit`; its source is at lines 75--77 of
`build_scenario_master_en.py`. The independent verifier's `v2_contract()` still
uses a closed event schema that permits only seven keys and rejects `contains`;
its source is line 66 of `verify_scenario_master_en.py`.

Therefore every builder-valid typed structured candidate is rejected by the
verifier before any of the eight proposed mutations can be exercised. Producing
a fixture without `contains` would not represent the required typed candidate
route. This packet expressly makes both implementations read-only, so repairing
the incompatible verifier schema is outside authority.

## Evidence

```powershell
python -B -m pytest -q kb_creator/tests/test_verify_scenario_master_en.py
# 14 passed in 19.88s

python -B kb_creator/scripts/verify_scenario_master_en.py ... --publication-config ...publication_config_v1.json ... --preflight-only
# preflight_passed; frozen v1 SHA-256 C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30
```

No test module was edited because adding the stipulated mutation fixture would
encode a knowingly invalid cross-component contract. No implementation, real
Viral config/evidence/source/reconstruction/candidate, Git or Step 8A artifact
was changed.

## Next action

Assign a narrowly scoped verifier implementation correction which accepts and
independently validates v2 `contains` for typed structured events. After that,
resume this tests-only packet and add the eight mutation classes against a real
builder-valid synthetic candidate.

Completion token: `BLOCKED_V2_BUILDER_VERIFIER_CONTAINS_SCHEMA_MISMATCH`
