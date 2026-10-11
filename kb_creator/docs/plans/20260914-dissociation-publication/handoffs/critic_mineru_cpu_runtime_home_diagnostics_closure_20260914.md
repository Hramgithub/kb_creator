# Independent implementation critic receipt - MinerU CPU runtime home diagnostics closure

## Receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `mineru-cpu-runtime-home-diagnostics-remediation`
- Review kind: `implementation`
- Candidate state reviewed: non-frozen remediation candidate for the failed
  first real CPU-first run attempt; not a release candidate
- Fresh run under consideration: `20260914-cpu-first-02`
- Role: independent remediation closure critic
- Policy critic role/model/effort: `gpt-5.5` at `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; orchestration ownership
  does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review
- Timestamp: `2026-09-14T20:42:39.0121610+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:03:28`
- Token use: unavailable in platform terms; local goal meter reported `175527`
  tokens at receipt write

This receipt is independent implementation criticism only. It is not a real
Dissociation source run, human merge decision, reconstruction acceptance,
publication acceptance, release review, release approval, Git action, or
orchestration ownership transfer.

## Authority reviewed

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_cpu_first_real_attempt_failure_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_runtime_home_diagnostics_remediation_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_packet_b_closure_20260914.md`
- assigned receipt path checked absent before writing:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_runtime_home_diagnostics_closure_20260914.md`

## Files checked

- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/pipeline/process.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/README.md`
- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/mineru_view_execution.v1.schema.json`
- `kb_creator/contracts/mineru_view_set.v1.schema.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`
- prior Packet B relevant test files included in the regression run:
  `test_reconstruction_control_plane.py`,
  `test_mineru_three_view_tools.py`,
  `test_mineru_visual_merge_bundle.py`,
  `test_audit_mineru_ai_merge_fidelity.py`,
  `test_materialize_mineru_ai_merge.py`,
  `test_finalize_mineru_reconstruction.py`,
  `test_reconstruction_promotion.py`,
  `test_reconstruction_promotion_adversarial.py`,
  `test_pipeline_identity.py`

Only this immutable receipt was written. No implementation, test, schema,
canonical plan/context/status/release, live `.tools`, immutable source,
generated source-output, failed real run root, Git index, commit, remote,
install, download, network, GPU, API, or real PDF action was performed.

## Evidence

Static review found the remediation closes the exact failure class from
`20260914-cpu-first-01`:

- The CPU-first wrapper creates a profile-runtime-contained synthetic home:
  `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `PYTHONUSERBASE`,
  `XDG_CACHE_HOME`, `TEMP`, `TMP`, Hugging Face caches and ModelScope cache all
  resolve below `.tools/MinerU/runtime/<profile>/`.
- The wrapper verifies runtime path containment before creating these
  directories and does not pass inherited real user profile, proxy/API, or
  `PYTHONPATH` values to the MinerU child.
- The MinerU child is launched with `UseShellExecute=false`,
  `.Environment.Clear()`, explicit `ArgumentList` construction, and a closed
  environment. Local-only backend/profile dispatch remains allowlisted.
- The CPU-first production adapter launches the outer PowerShell process with
  `inherit_environment=False`, passing only `SystemRoot`, `WINDIR`, `ComSpec`,
  and `PATHEXT`; the executable and script paths are already identity-bound in
  the v2 run.
- Nonzero child exits capture stdout and stderr through asynchronous
  `ReadToEndAsync()` drains, avoiding the classic full-pipe deadlock pattern.
- Failure output is bounded to 16384 characters per stream, control characters
  are sanitized, and truncation flags are recorded.
- Wrapper `failure.json` is written atomically via a temporary file and rename,
  sealed with `failure_sha256`, and lives under the attempted view output.
- The v2 control plane catches `pipeline_process.ProcessFailure`, writes sealed
  `kb_creator.stage_failure.v1` as `stage-failure.json`, then moves the whole
  failed staging tree to `failures/<stage>/`.
- No stage manifest or successful output root is left behind for the failed
  stage, so the failure evidence cannot be promoted or resumed as success.
- Nonzero execution remains a stage failure, not a provider skip. Optional GPU
  skips remain capability-unavailable only.
- Success path behavior remains unchanged: successful views do not contain a
  failure artifact, and v1 compatibility code remains present.

Commands run:

- Focused remediation module:
  `test_mineru_cpu_packet_b.py`
  -> `17 passed in 21.26s`.
- Full relevant Packet B/remediation regression set:
  `test_mineru_cpu_packet_b.py`,
  `test_reconstruction_control_plane.py`,
  `test_mineru_three_view_tools.py`,
  `test_mineru_visual_merge_bundle.py`,
  `test_audit_mineru_ai_merge_fidelity.py`,
  `test_materialize_mineru_ai_merge.py`,
  `test_finalize_mineru_reconstruction.py`,
  `test_reconstruction_promotion.py`,
  `test_reconstruction_promotion_adversarial.py`,
  `test_pipeline_identity.py`
  -> `215 passed, 1 skipped in 71.79s`.
- Python compilation:
  `kb_creator/pipeline/process.py`,
  `kb_creator/pipeline/reconstruction.py`,
  `kb_creator/scripts/run_mineru_three_view.ps1`,
  `kb_creator/tests/test_mineru_cpu_packet_b.py`
  -> PASS.
- PowerShell parser:
  `kb_creator/scripts/run_mineru_three_view.ps1`
  -> PASS.
- JSON parse:
  `run_spec.v2.schema.json`,
  `mineru_view_execution.v1.schema.json`,
  `mineru_view_set.v1.schema.json`,
  `mineru_multi_view_comparison.v2.schema.json`
  -> PASS.
- Scoped `git diff --check` on reviewed files:
  PASS; Git emitted only its Windows LF-to-CRLF advisory for
  `kb_creator/scripts/run_mineru_three_view.ps1`.

## Findings

### P0

None found.

### P1

None found.

### P2

1. Carried Packet B wrapper legacy-mode surface remains open.

   The prior Packet B closure recorded that the shared
   `run_mineru_three_view.ps1` top-level `ValidateSet` accepts
   `pipeline_txt` and `vlm_local`, while legacy `-MinerURoot` mode still maps
   every non-`hybrid_high` profile to legacy pipeline OCR. This remediation did
   not worsen that issue and the new CPU-first production path always supplies
   `-ToolRoot`, but the direct legacy CLI surface should still reject
   CPU-first-only profile names when `-ToolRoot` is absent.

## Blockers

No P0/P1 blocker remains for the runtime-home diagnostics remediation.

Non-blocking evidence caveats:

- This review did not run a live real Dissociation PDF through MinerU, by
  assignment.
- This review did not mutate or inspect live `.tools` runtime contents beyond
  read-only repository/test evidence.
- The successful pytest evidence used the existing flat
  `.tools/python-test-deps` package directory via
  `PYTHONPATH=.tools\python-test-deps`, matching the prior Packet B review
  environment.
- `kb_creator/pipeline/process.py`, `kb_creator/pipeline/reconstruction.py`,
  and `kb_creator/tests/test_mineru_cpu_packet_b.py` are untracked in the
  current Git status; this receipt reviews the live workspace candidate state,
  not a committed revision.

## Recommendation

GO for a fresh real local CPU-only Dissociation run with new run id
`20260914-cpu-first-02`, from this remediation scope.

The next run must start from a fresh absent run root, keep the failed
`20260914-cpu-first-01` root immutable as failure evidence, use the verified
CPU profile with `ocr_language: en`, remain current-station/local-only, and
continue to treat any required CPU invocation failure as fatal diagnostic
evidence rather than a skip.
