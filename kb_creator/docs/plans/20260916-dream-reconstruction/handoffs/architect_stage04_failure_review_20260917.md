# Architect review — Stage 04 visual-merge failure

## Receipt

- Goal ID: `20260916-dream-reconstruction`
- Step ID: `4-stage04-root-cause`
- Role: architect (`gpt-5.6-sol`, policy effort `high`)
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `completed`
- Scoped override: `none`
- Timestamp: `2026-09-17T00:33:32+03:00`
- Elapsed time: approximately 18 minutes
- Token use: unavailable
- Scope: read-only diagnosis of the sealed Stage 04 failure, visual-bundle producer, control plane, replay boundary, and focused tests
- Result: `ROOT_CAUSE_CONFIRMED`; generic Windows long-path remediation is required before another production attempt.

## Files and evidence checked

- `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-first-01/failures/04-visual-merge-bundle/stage-failure.json`
- The sealed outputs/manifests presence boundary for Stages 01-04 in that run
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/pipeline/reconstruction_replay_resume.py`
- `kb_creator/contracts/reconstruction_stage_dependency_registry.v1.json`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_reconstruction_replay.py`
- Active goal plan/context/status and `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`

No code, contract, run data, source, canonical plan/context/status, or release artifact was changed.

## Finding by severity

### P1 — confirmed root cause

Stage 04 passes ordinary absolute Windows paths to Poppler. The two original-PDF MinerU layout paths are each 302 characters, beyond the legacy Win32 `MAX_PATH` boundary. `pdftoppm` therefore exits 1 while opening the first layout PDF even though the PDF is valid.

Evidence:

- Failure command: `pdftoppm -r 110 -png -f 1 -l 26 <302-character original_pipeline_txt layout> <186-character output prefix>`.
- `original_pipeline_txt` layout: 3,585,109 bytes, path length 302.
- `original_pipeline_ocr` layout: 3,585,109 bytes, path length 302.
- `raster_pipeline_ocr` layout: 28,999,186 bytes, path length 198.
- Poppler `pdfinfo` cannot open the 302-character path in ordinary form, but opens the same bytes through the Win32 extended-length `\\?\` form and reports 26 pages, 612 x 792 points, rotation 0.
- The 198-character raster layout opens normally.
- The failed output prefix is only 186 characters (193 including `-26.png`), so the failing boundary is the long input path, not output creation.
- `render_layouts()` currently stringifies both layout and output paths without a Windows extended-length adapter.

This is a generic portability defect: any valid MinerU artifact whose resolved path exceeds the Poppler build's ordinary Win32 path limit can fail the same way. It is not a source-PDF, MinerU-output, geometry, contract, or content defect.

### P2 — failure diagnostics lose the child cause

`render_layouts()` invokes Poppler with `capture_output=True`, but does not catch `CalledProcessError`. The Python traceback retained in `stage-failure.json` shows only exit 1; Poppler's captured stderr is discarded. Path-length evidence was therefore needed to reconstruct the direct cause.

## Minimal generic remediation specification

### Required code boundary

Own only `kb_creator/scripts/build_mineru_visual_merge_bundle.py` and its focused tests for the minimal fix.

1. Add a pure path-to-external-argv adapter used only at the Poppler boundary.
2. On Windows, require an absolute path and convert local drive paths to `\\?\C:\...`; convert UNC paths to `\\?\UNC\server\share\...`; preserve an already extended path without double-prefixing. On non-Windows, return the ordinary absolute path unchanged.
3. Apply the adapter to both the layout-PDF argument and render-output prefix. Keep all internal `Path` operations, hashing, inventories, and manifest path semantics unchanged.
4. Record the actual executed argv in run-local diagnostics as today; the extended-length spelling is operational evidence, not portable authority.
5. Catch `subprocess.CalledProcessError` at the per-view render boundary and raise a bounded diagnostic that retains view id, exit code, logical input/output lengths, and bounded stdout/stderr. Do not convert a renderer failure into a skip.
6. Do not shorten, copy, rename, or mutate MinerU artifacts as a workaround. Do not add scenario-specific path aliases or hard-coded `Number 7 Dream` handling.

### Tests

Add focused cases to `test_mineru_visual_merge_bundle.py`:

1. Windows local-drive conversion, UNC conversion, idempotence for an existing extended path, and non-Windows pass-through.
2. Captured render argv proves both long input and output-prefix arguments use the adapter while options/page bounds remain unchanged.
3. A Windows integration regression using the repository Poppler and a valid synthetic PDF at a resolved path longer than 260 characters; rendering must produce the exact expected page set.
4. A renderer-failure test proves bounded Poppler stderr is present in the raised diagnostic.
5. Existing exact page-order, geometry, v2 visual-bundle validation, and control-plane failure-quarantine tests remain green.

Suggested focused verification set:

- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_mineru_geometry_normalization.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`

## Resume and replay implications

### Current supported behavior

- Run `20260917-cpu-first-01` is immutable failure evidence. Stages 01-03 have both output and stage manifests; Stage 04 has neither, and its sealed failure exists under `failures/04-visual-merge-bundle`.
- In-place retry is not supported: `_invoke_stage()` rejects an existing failure path, and a code fix changes implementation identity. The failure directory must not be removed to force a retry.
- Full Stage 04 replay is not possible because the replay route requires a complete successful Stage 01-04 prefix, including Stage 04 output/manifest and review queue.
- Although replay aliases include `03-compare-views`, `replay_run_engine()` explicitly rejects every prefix count other than four with `partial_prefix_execution_not_implemented`. Therefore the current code cannot replay sealed Stages 01-03 and then execute a fresh Stage 04.
- With only the minimal long-path fix, the next supported action is a completely fresh run root and re-execution of Stages 01-04, including MinerU.

### Can a fresh replay through Stage 03 avoid rerunning MinerU?

Architecturally yes, but not with the current implementation. A separately authorized generic enhancement could replay the validated Stage 01-03 prefix into a fresh run identity and execute Stage 04 with the fixed current producer. The dependency registry already isolates `build_mineru_visual_merge_bundle.py` to Stage 04, so a Stage 04-only producer change does not invalidate the source Stage 01-03 closure.

That enhancement is larger than the minimal renderer-path fix and must fail closed:

1. Validate source run, contract, source, tools, Stage 01-03 manifests/inventories, and per-stage implementation closure exactly as replay preflight does.
2. Rebase only Stages 01-03 into a new absent run root; never copy the failed Stage 04 attempt or any failure artifact as operational output.
3. Execute Stage 04 normally with the current implementation/tool identity, then create its fresh manifest and review queue.
4. Record a bridge that states Stages 01-03 were replayed, Stage 04 producer was invoked, decisions were not replayed, and acceptance was not inferred.
5. Add adversarial tests for Stage 01-03 drift, Stage 04 source-output absence, destination collision, partial publish cleanup, stale identities, and forbidden decision/acceptance replay.

Until that enhancement is independently implemented and reviewed, claiming that Stage 03 replay avoids the MinerU rerun would be false.

## Acceptance criteria

1. The long-path Poppler regression renders successfully on Windows using a path longer than 260 characters.
2. Short-path and non-Windows behavior remains unchanged.
3. Poppler failure evidence contains bounded child stderr and identifies the failing view.
4. Focused visual-bundle, geometry, and control-plane tests pass.
5. The historical failed run remains byte-unchanged.
6. A production attempt uses a new absent run root; no acceptance or publication state is inferred.
7. MinerU reuse is allowed only if the separately reviewed Stage 01-03 replay-plus-Stage-04-execute path exists and passes its own replay tests; otherwise rerun Stages 01-04.

## Blockers and next action

- Blocker: generic Windows Poppler path adaptation is not implemented.
- Next action: bounded engineering implements the Stage 04 path adapter and diagnostics with focused tests. The orchestrator then chooses either the currently supported fresh full run or a separately scoped partial-prefix replay implementation if avoiding the MinerU rerun justifies the additional control-plane work.

