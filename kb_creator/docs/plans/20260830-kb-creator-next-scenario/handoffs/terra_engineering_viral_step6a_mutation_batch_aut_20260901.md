# Terra engineering receipt: Viral Step 6A AUT mutation batch

- scope: exactly AUT's 30 contract/snapshot, source-identity, and recovery
  rows; only `scenario_source_reconstruction.py`,
  `test_scenario_source_reconstruction.py`, and this new receipt were written.
- result: `BLOCKED` — implementation is materially present, but the required
  single unified AUT and SRC terminal summaries were not obtained before this
  handoff. The command runner repeatedly returned a partial dot stream without
  a native exit code/final pytest summary after roughly thirteen cases.
- files changed: `kb_creator/scripts/scenario_source_reconstruction.py` and
  `kb_creator/tests/test_scenario_source_reconstruction.py`.
- files checked read-only: accepted assignment, remediation packet sections
  5.3, 7.3, 8.1, and 11; plan/status; the two baseline material files.

## Result and evidence

All 30 AUT ids now have named callable mutations rather than the shared
`COMMANDS` proxy. The five contract/snapshot rows mutate the operation
argument, raw contract seal, canonical field, snapshot field, or snapshot
binding. The eleven source-identity rows mutate exact source-identity JSON
pointers. The fourteen recovery rows operate on a physical 211-payload
fixture, its manifest/evidence seals, rows, bytes/hash/path/duplicate,
forbidden payload, bindings, allowlist, or promotion flag.

`apply_case` snapshots physical fixture state, captures actual selected-value
SHA-256 before/after values, invokes the real `_test_verify` once, records the
observed exact code, and records transport/residue fields in `MutationAudit`.
Recovery semantic cases use explicit tuples for manifest/evidence,
source-identity, inventory, QA, and profile transport; raw-hash rows use no
reseal. AUT is selected into the real `_execute` / `_strict_verify` route.

Completed offline evidence (`python -B`, `-p no:cacheprovider`):

- AUT contract/snapshot: `5 passed, 366 deselected`.
- AUT source identity: `11 passed, 360 deselected`.
- AUT recovery manifest/evidence/forbidden binding subset: `7 passed, 364
  deselected`.
- AUT recovery allowlist/promotion tail: `2 passed, 369 deselected`.
- BLD: `3 passed, 368 deselected`.
- collect-only: `371 tests collected`.
- REP-containing smoke: `6 passed, 365 deselected`; this expression also
  selected existing reparse/INJ names by pytest substring semantics.

No command or receipt reads or serializes an external locator. No candidate,
source, sidecar, recovery, protected CLI/tests, cache, Git, or live surface
was written.

## Blocker and next action

The missing completion evidence is exact: rerun, from this worktree, the
following two commands and retain their native exit code and final line before
declaring completion:

```text
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider -k 'AUT'
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider -k 'SRC-'
```

Then serialize the 30 `MutationAudit.as_json()` records and their ordinal
digest into a successor receipt, re-run the required REP/SRC smoke, BLD 3/3,
and 371 collection. Do not claim `COMPLETE_BATCH_PENDING_PHASE2_INTEGRATION`
until those exact terminal outputs are available and all 30 audit records have
been captured.

- baseline library SHA-256: `C413F87F95C33B577F34E5A5CD80611166D8A62B1152D67AD361399AA34CA82E`.
- baseline test SHA-256: `C3B4EA8129FD39DF6AD3D76558D93D9E89207D6A401AD26462AF4D7F3573B95A`.
- elapsed time: approximately 52 minutes.
- token use: unavailable from this runtime.
- timestamp: `2026-09-01T04:32:00+03:00`.
- orchestrator policy owner: `gpt-5.6-sol` at medium; Terra retains no
  orchestration ownership.
- assignment state: blocked after partial, evidence-backed implementation;
  independent QA and critic review remain pending.
- scoped override: none.
