# Independent critic receipt - Stage 04 long-path implementation review

## Receipt

- Goal ID: `20260916-dream-reconstruction`
- Step ID: `4-stage04-fix-independent-review`
- Review kind: `implementation`
- Role: independent critic (`gpt-5.5`, policy effort `medium`)
- Actual platform model/effort: `unavailable`
- Implemented candidate: `false`
- Materially designed candidate: `false`
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `platform-unverified`
- Scoped override: `none`
- Timestamp: `2026-09-17T00:55:34+03:00`
- Elapsed time: approximately 25 minutes
- Token use: unavailable
- Scope: independent review of the Stage 04 Poppler long-path remediation in `kb_creator/scripts/build_mineru_visual_merge_bundle.py` and `kb_creator/tests/test_mineru_visual_merge_bundle.py`; no implementation, design, canonical plan/context/status, contract, source, run-output, release, or Git mutation.

## Files checked

- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260916-dream-reconstruction/plan.md`
- `kb_creator/docs/plans/20260916-dream-reconstruction/context.md`
- `kb_creator/contracts/number-7-dream.reconstruction.json`
- `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/architect_stage04_failure_review_20260917.md`
- `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/engineer_stage04_long_path_remediation_20260917.md`
- `kb_creator/docs/plans/20260916-dream-reconstruction/handoffs/engineer_stage04_long_path_remediation_correction_20260917.md`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-first-01/failures/04-visual-merge-bundle/stage-failure.json`

## Evidence

- Reviewed the current diff for the two implementation files: `2 files changed, 170 insertions(+), 4 deletions(-)`.
- Confirmed the sealed Stage 04 failure evidence remains present and shows Poppler was invoked on the ordinary long layout-PDF path before the fix.
- Rechecked the two failed source layout PDFs by path:
  - `original_pipeline_txt` layout path length: `302`; file exists; bytes: `3585109`.
  - `original_pipeline_ocr` layout path length: `302`; file exists; bytes: `3585109`.
- Verified `poppler_path_argument()`:
  - returns resolved absolute ordinary paths on non-Windows;
  - requires absolute Windows paths before adding an extended prefix;
  - converts drive paths to `\\?\C:\...`;
  - converts UNC paths to `\\?\UNC\server\share\...`;
  - preserves already extended Windows paths without double-prefixing.
- Verified `_logical_poppler_path()`, `poppler_paths_equivalent()`, and `poppler_render_prefix_is_valid()` preserve backward compatibility only for absolute logical equivalents and reject relative render prefixes.
- Verified new execution records extended absolute Poppler argv for both layout input and output prefix in `render_layouts()`, while internal layout identities and manifest `layouts[*].path` remain the original logical paths.
- Verified v2 validation still fail-closes on the exact MediaBox rendering recipe: command length, option sequence, page bounds, same logical input path, and `_render` output-prefix basename.
- Verified renderer failures are not converted into skips and now include bounded view id, exit code, logical path lengths, stdout, and stderr.
- Ran focused verification locally with repo-local runtimes:
  - `$env:PYTHONPATH='.tools\python-test-deps;.'; & '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_visual_merge_bundle.py -q` -> `12 passed in 4.59s`.
  - `$env:PYTHONPATH='.tools\python-test-deps;.'; & '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py -q` -> `38 passed in 103.94s (0:01:43)`.
  - `git diff --check -- kb_creator/scripts/build_mineru_visual_merge_bundle.py kb_creator/tests/test_mineru_visual_merge_bundle.py` -> no output.
- Read the orchestrator packet's reported broader evidence: expanded suite `230 passed`; failed live path length `302`. This receipt independently revalidated the focused suites and the path-length evidence above, but did not rerun the full 230-test expanded suite.
- Read the orchestrator checkpoint reporting a live disposable Stage 04 proof after remediation: `78` renders, `26` triptychs, `7` contacts, and `26` packets. This receipt did not independently rerun that disposable Stage 04 proof.

## Findings by severity

- P0: none found.
- P1: none found.
- P2: none found.

## Review checks

- Correct Win32 drive and UNC extended path conversion: passed.
- No path traversal or relative widening: passed. The new Windows adapter fails relative paths before argv execution, and legacy validator equivalence accepts only absolute logical equivalents.
- Existing manifest compatibility: passed. Legacy ordinary absolute Windows argv and new extended argv are accepted only when they name the same logical layout input and `_render` prefix; manifest layout identities remain unchanged.
- New execution always uses extended absolute Poppler paths on Windows: passed for `render_layouts()`, with caller paths resolved in `main()` before `build_bundle()`.
- Validator exact MediaBox argv remains fail-closed: passed.
- Bounded diagnostics and no secret/environment leak: passed for the changed renderer boundary. The new diagnostic reports view id, exit code, path lengths, and bounded child stdout/stderr only; it does not dump environment.
- Test coverage for real long-path Poppler and legacy forms: passed. The focused test module covers drive/UNC/extended/non-Windows conversion, legacy/extended equivalence, relative rejection in equivalence and prefix validation, adapted input/output argv, no-copy behavior, bounded renderer diagnostics, and a Windows-only real Poppler long-path render.
- Unexpected scope: none found in the reviewed diff.

## Blockers

None for this implementation review.

## Recommendation

Accept the Stage 04 long-path implementation remediation for integration. It is a narrow generic no-copy Poppler argv adapter with bounded diagnostics, closed backward manifest compatibility, and focused regression coverage. This is not a release decision and does not approve any reconstruction candidate, source acceptance, publication output, Git operation, or partial-prefix replay.

Next action remains with the orchestrator: proceed according to the existing Stage 04 recovery boundary using a fresh absent run root, or separately review any future Stage 01-03 replay-plus-Stage-04-execute enhancement before relying on it.
