# Viral remediation v2 materializer receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-materializer`
- Contributor role: `nri-engineer`
- Requested model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `partial_builder_only`
- Scoped override: none
- Timestamp: `2026-09-03T00:10:00+03:00`
- Elapsed time: approximately `00:07:00`
- Token use: unavailable

## Changed paths

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- this immutable receipt

## Result and evidence

The builder now dispatches a v2 schema to an isolated synthetic candidate
materializer, retaining the sealed v1 code path. The v2 route creates only an
absent target via private staging and atomic rename, writes canonical-LF reader
Markdown, v2 source disposition, provenance, asset manifest, QA metrics and a
recomputed inventory. It emits no acceptance sidecar. Provenance retains the
source-ordered typed events, source-range identity hashes, generated-navigation
operation and source-backed-recovery operation when declared. Audit/reader/
excluded counts come from the v2 declaration and output metrics.

The synthetic test proves an atomic absent-root build, target-exists refusal,
inventory generation, reader-value suppression, 124/122/2 dispositions and
absence of an acceptance sidecar.

```powershell
python -B -m pytest -q kb_creator/tests/test_build_scenario_master_en.py
# 44 passed in 10.22s

python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py
# passed
```

No verifier, real Viral config/evidence/source/reconstruction/candidate, Git
surface, Step 8A output, or protected path was modified.

## Builder-only residual gap

`READY_FOR_V2_OUTPUT_VERIFIER` is not returned. The current v2 materializer
serializes a structured unit as a validated declared string; it does not yet
enforce or test the internal row/cell shape and termination semantics for every
required table, callout, ordered-list callout, equipment card, creature
statblock, full-page map and physical page pair. Asset records are declared and
reader-value suppression is tested, but exact before/between/after event
placement, binary copy closure and duplication/quality-stage enforcement remain
unimplemented. The required mutation coverage for fragment identity, excluded
page leakage, table rows/cells and deterministic two-build byte equality is
therefore incomplete.

Completion token: `PARTIAL_V2_MATERIALIZER_CONTAINER_AND_ASSET_GAP`
