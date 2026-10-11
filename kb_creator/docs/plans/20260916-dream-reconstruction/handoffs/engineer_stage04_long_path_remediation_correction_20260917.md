# Engineering correction handoff — Stage 04 long-path remediation

- Goal ID: `20260916-dream-reconstruction`
- Step ID: `4-stage04-path-remediation-correction`
- Role: engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-17T00:47:55+03:00`
- Elapsed time: approximately 9 minutes
- Token use: unavailable

## Scope

Correction to the Stage 04 Poppler path adapter only. Owned files remain the
visual-bundle producer, its focused tests, and this immutable correction
receipt. No canonical plan/context/status, run data, sources, contracts, or
release artifacts were changed.

## Result

Restored closed backward validation compatibility for historical v2 manifests
that recorded ordinary absolute Windows Poppler argv paths. New executions
continue to emit extended-length Windows argv paths. The new equivalence helper
normalizes only absolute Windows drive, UNC, and their extended `\\?\\` / `\\?\\UNC\\`
spellings; relative paths and different logical locations are rejected.

The v2 validator now uses that equivalence for layout-input comparison and a
closed `_render` output-prefix check. This accepts a legacy ordinary argv only
when it names the same logical input/prefix as the extended form, rather than
loosening path validation generally.

## Files changed or checked

- Changed: `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- Changed: `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- Added: `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/engineer_stage04_long_path_remediation_correction_20260917.md`
- Checked: `kb_creator/tests/test_mineru_cpu_packet_b.py`

## Verification and evidence

- `PYTHONPATH=.tools/python-test-deps;. python -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q` -> `12 passed`.
- `PYTHONPATH=.tools/python-test-deps;. python -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py -q` -> `38 passed in 104.69s (0:01:44)`.
- The focused tests cover plain and extended drive/UNC equivalence, relative and distinct-path rejection, plain and extended `_render` prefixes, and the prior real Poppler long-path regression.
- `py_compile` passed for the changed producer and focused test module.
- `git diff --check` passed for the changed producer and test module.

## Blockers and next action

No implementation or verification blocker remains in this scoped correction.
The orchestrator can integrate/review the remediation and choose the next fresh
production run according to the existing Stage 04 recovery boundary. The
historical failed run remains immutable; this correction does not implement
partial-prefix replay.
