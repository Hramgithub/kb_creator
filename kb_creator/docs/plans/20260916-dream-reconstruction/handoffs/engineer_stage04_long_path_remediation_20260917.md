# Engineering handoff — Stage 04 long-path remediation

- Goal ID: `20260916-dream-reconstruction`
- Step ID: `4-stage04-path-remediation`
- Role: engineering (`gpt-5.6-terra`, policy effort `medium`)
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-17T00:38:43+03:00`
- Elapsed time: approximately 16 minutes
- Token use: unavailable

## Scope

Owned only the Stage 04 Poppler adapter and its focused test module. No source,
run evidence, contracts, canonical plan/context/status, release files, or
scenario-specific logic was changed.

## Result

Implemented a generic Poppler external-argv adapter. On Windows it transforms
absolute drive paths to `\\?\\C:\\...` and UNC paths to `\\?\\UNC\\...`, preserves an
already extended path, and applies the adapter to both the layout-PDF input and
the render-output prefix. Non-Windows paths remain ordinary resolved absolute
paths. Original layout paths, hashes, geometry identities, inventories, and
internal `Path` operations are unchanged, so no duplicate layout PDF is staged
or retained in the final bundle.

Per-view renderer failures now include bounded child stdout/stderr, the view,
exit code, and logical input/output-path lengths. The v2 validator now expects
the operational extended input argv while retaining manifest provenance for the
original layout identity.

The task packet initially requested a bounded copied input bridge. After the
architect receipt confirmed Poppler accepts the same valid PDF through the
Win32 extended-path spelling, this implementation used the recommended no-copy
adapter instead; it is the smaller generic remediation and avoids an extra
artifact lifecycle.

## Files changed or checked

- Changed: `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- Changed: `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- Checked: `kb_creator/docs/plans/20260916-dream-reconstruction/PLAN.md`
- Checked: `kb_creator/docs/plans/20260916-dream-reconstruction/context.md`
- Checked: `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/architect_stage04_failure_review_20260917.md`

## Verification and evidence

- Focused test command using bundled Python plus repository pytest site-packages: `python -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q` -> `11 passed`.
- The focused suite includes a real Windows `pdftoppm` render of a valid synthetic PDF at a resolved input path longer than 260 characters; it produced the exact `page-001.png` set for all required views.
- Added direct cases for drive, UNC, already-extended, and non-Windows adapter behavior; argv adaptation for both input and output; and bounded renderer stderr propagation.
- `py_compile` passed for the changed script and test module.
- `git diff --check` passed for both changed files.
- Attempted `test_mineru_geometry_normalization.py` and `test_reconstruction_control_plane.py`, but collection is blocked before tests by `ModuleNotFoundError: No module named 'jsonschema'` in available test environments.

## Blockers and next action

No implementation blocker. The two extended focused suites need an environment
with `jsonschema` for their collection. Orchestrator should independently
review the change, then use a fresh absent run root for the next supported
Stage 01-04 execution; the historical failed run remains immutable. Partial
Stage 01-03 replay is not implemented and must not be inferred from this fix.
