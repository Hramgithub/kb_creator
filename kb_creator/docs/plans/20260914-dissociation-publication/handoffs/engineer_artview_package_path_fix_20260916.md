# Engineering receipt: ArtView package path preservation

Date: 2026-09-16
Role: engineering (`gpt-5.6-sol`, high; user override)
Status: implemented and verified; no commit

## Root cause

Stage 70 copied the single accepted ArtView decisions JSON to the fixed package
path `acceptance/artview.decisions.json`. The immutable ArtView acceptance
receipt retained the original run-relative evidence path, such as
`submissions/artview/artview-decisions.accepted.json`. The offline verifier's
exact-once identity comparison therefore failed on `path` even though bytes and
SHA-256 were unchanged.

## Fix

`assemble_production_package` now:

- resolves the accepted decisions through the strict identity/path validator;
- requires exactly one evidence JSON with the v3 decisions schema;
- materializes it inside the package at the same safe run-relative path stored
  in the acceptance receipt;
- points the `artview_decisions` package role to that preserved path; and
- leaves the acceptance receipt unchanged, preserving path/bytes/SHA identity.

Unsafe paths, including `../` escape attempts, are rejected before the decision
file is copied.

## Verification

- focused Stage 70/ArtView set: `5 passed in 28.04s`;
- complete `test_publication_control_plane.py`: `34 passed in 83.16s`;
- `git diff --check` for the two implementation/test files: pass.

The regression covers the real Stage 70 assembler with
`submissions/artview/artview-decisions.accepted.json`, asserts exact packaged
identity and absence of the old flattened copy, and asserts rejection of an
otherwise identity-correct `../outside-artview-decisions.json` record.

## Files changed by this task

- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_artview_package_path_fix_20260916.md`

No run23 output, acceptance, source artifact, or configuration was modified.
