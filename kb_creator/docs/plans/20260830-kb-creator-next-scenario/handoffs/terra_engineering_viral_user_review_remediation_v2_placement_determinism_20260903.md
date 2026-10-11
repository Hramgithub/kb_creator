# Viral remediation v2 placement and determinism receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-placement-determinism`
- Contributor role: `nri-engineer`
- Requested model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `partial_four_gap_closure`
- Scoped override: none
- Timestamp: `2026-09-03T00:32:00+03:00`
- Elapsed time: approximately `00:07:00`
- Token use: unavailable

## Changed paths

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- this immutable receipt

## Result and evidence

Reader asset placement is now resolved against the distinct declared target
event, rather than accepting the asset event itself. The builder rejects a
self-binding target, non-reader/excluded/missing target, duplicate target
binding, and an `inside_structured_unit` target that is not structured. It
removes the asset event's placeholder and inserts the reader image immediately
before, after, or inside the selected target content. Fragment IDs are now
required nonempty strings; all event pages remain restricted to reader scope.

The synthetic reader-asset test builds identical content twice into distinct
absent roots and compares every non-inventory file byte-for-byte. This confirms
the candidate output contains no target-root or run-time noise.

```powershell
python -B -m pytest -q kb_creator/tests/test_build_scenario_master_en.py
# 46 passed in 9.74s

python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py
# passed
```

## Precise residual gap

`READY_FOR_V2_OUTPUT_VERIFIER` is not returned. The duplicate-binding,
missing/changed fragment identity and excluded-page event controls exist in the
implementation, but this continuation has not added the packet-required
dedicated negative mutation cases for each of those three controls. No verifier,
real policy/evidence/source/reconstruction/candidate or Git path was modified.

Completion token: `PARTIAL_V2_NEGATIVE_MUTATION_COVERAGE_GAP`
