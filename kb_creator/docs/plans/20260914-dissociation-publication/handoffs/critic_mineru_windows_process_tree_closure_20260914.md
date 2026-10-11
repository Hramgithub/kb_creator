# Independent critic closure: MinerU Windows process-tree remediation

- Goal: `20260914-dissociation-publication`
- Review artifact: `critic_mineru_windows_process_tree_closure_20260914.md`
- Review kind: implementation
- Candidate state reviewed: non-frozen remediation candidate for the Windows process-tree failure observed in `20260914-cpu-first-02`
- Fresh run under decision: `20260914-cpu-first-03`
- Timestamp: 2026-09-14T21:23:47.6264845+03:00
- Reviewer role declared by assignment: independent critic, `gpt-5.5` at medium reasoning
- Actual platform model disclosure: not independently available inside this agent; no claim beyond assigned role
- Implemented candidate: no
- Materially designed candidate: no
- Orchestrator policy owner: main-chat orchestrator, `gpt-5.6-sol` at medium per `docs/governance/nri_goal_governance.md`
- Assignment state: recovery closure review after prior attempts; scoped to the Win32 process-tree remediation
- Scoped override: no implementation edits, no `.tools` mutation, no real PDF/MinerU run, no network, no GPU, no remote/API, no commit; only this immutable receipt was written
- Elapsed review time at receipt drafting: approximately 4 minutes in the current recovered turn, plus prior static/test work in this review context
- Token use at receipt drafting: goal snapshot reported 104,765 tokens used

## Authority reviewed

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/orchestrator_mineru_cpu_second_real_attempt_failure_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_windows_process_tree_remediation_20260914.md`
- Prior closures:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_packet_b_closure_20260914.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_runtime_home_diagnostics_closure_20260914.md`
- Repository governance:
  - `AGENTS.md`
  - `docs/governance/nri_goal_governance.md`

## Files checked

- `kb_creator/pipeline/windows_process_tree.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/pipeline/process.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_finalize_mineru_reconstruction.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- `kb_creator/tests/test_pipeline_identity.py`
- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/mineru_view_execution.v1.schema.json`
- `kb_creator/contracts/mineru_view_set.v1.schema.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`

## Evidence

### Static inspection

- `windows_process_tree.py` creates the target process suspended with `CREATE_SUSPENDED`, configures a dedicated unnamed Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, constrains inherited handles with `PROC_THREAD_ATTRIBUTE_HANDLE_LIST`, assigns the root process to the job, then resumes the initial thread.
- The helper uses `subprocess.list2cmdline([spec["executable"], *spec["arguments"]])` for Windows command-line quoting and does not route through a shell.
- The helper validates that spec/result/log paths are runtime-contained, that stdout/stderr are distinct runtime-local files, that argv/env strings contain no NUL bytes, and that timeout values are bounded.
- The wrapper writes per-invocation spec/result/stdout/stderr files under the profile runtime, reads stdout/stderr with a 65,536-byte stable byte cap, then emits bounded/sanitized failure evidence.
- The wrapper uses a closed allowlist environment and remaps `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, cache paths, temp paths, and model caches inside the profile runtime.
- `reconstruction.py` includes `kb_creator/pipeline/windows_process_tree.py` in the RunSpec implementation inventory and rejects stale implementation on resume.
- Stage process failures are sealed as `kb_creator.stage_failure.v1` and moved with the failed staging tree to the run-local failure/quarantine path.

### Commands run

Focused process-tree/Packet B module:

```text
$env:PYTHONPATH = '.tools\python-test-deps'
python -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py -q
21 passed in 28.61s
```

Full relevant suite:

```text
$env:PYTHONPATH = '.tools\python-test-deps'
python -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py kb_creator/tests/test_reconstruction_control_plane.py kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_mineru_visual_merge_bundle.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_materialize_mineru_ai_merge.py kb_creator/tests/test_finalize_mineru_reconstruction.py kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py kb_creator/tests/test_pipeline_identity.py -q
219 passed, 1 skipped in 78.87s
```

Compile:

```text
python -m compileall -q kb_creator\pipeline\windows_process_tree.py kb_creator\pipeline\process.py kb_creator\pipeline\reconstruction.py kb_creator\tests\test_mineru_cpu_packet_b.py
PASS
```

PowerShell parser:

```text
Parser::ParseFile("kb_creator/scripts/run_mineru_three_view.ps1", ...)
PowerShell parser ok
```

Schema parse:

```text
json.loads(...) for run_spec.v2, mineru_view_execution.v1, mineru_view_set.v1, mineru_multi_view_comparison.v2
schema json parse ok 4
```

Diff check:

```text
git diff --check
PASS with existing line-ending warnings only
```

Additional independent evidence supplied by orchestrator during this review:

```text
test_windows_tree_runner_active_timeout_is_distinct_from_cleanup failed in another full module rerun:
actual owned_processes_seen=2, expected 1; cleanup still reported completed.
```

I did not run a real MinerU/PDF extraction, GPU work, network call, remote/API operation, install/download, or Git commit.

## Findings

### P0

None found.

### P1

1. `AssignProcessToJobObject` is called without an explicit `ctypes` ABI declaration.

   Evidence:
   - `kb_creator/pipeline/windows_process_tree.py` declares `argtypes`/`restype` for `CreateJobObjectW`, `SetInformationJobObject`, `QueryInformationJobObject`, `TerminateJobObject`, `CreateFileW`, `InitializeProcThreadAttributeList`, `UpdateProcThreadAttribute`, `ResumeThread`, `WaitForSingleObject`, `GetExitCodeProcess`, `TerminateProcess`, `CloseHandle`, and `CreateProcessW.argtypes`.
   - The same ABI block does not declare `kernel32.AssignProcessToJobObject.argtypes` or `kernel32.AssignProcessToJobObject.restype`.
   - The helper then calls `kernel32.AssignProcessToJobObject(job, process_handle)`.

   Impact:
   - The explicit review criterion includes correct `ctypes` ABI for the suspended process -> Job Object assignment path.
   - On 64-bit Windows, an undeclared `ctypes` function uses default integer conversions that are not a correct contract for pointer-sized `HANDLE` parameters. Tests can pass when handles happen to be representable, but the implementation has not satisfied the ABI invariant required before a fresh real run.
   - This is a fail-closed concern for the exact remediation boundary: if assignment is unreliable, descendant cleanup and KILL_ON_JOB_CLOSE evidence are not dependable enough to authorize the next real Dissociation run.

   Required closure:
   - Add explicit `kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)` and `kernel32.AssignProcessToJobObject.restype = wintypes.BOOL`.
   - Re-run focused process-tree tests, full relevant suite, compile, parser, schema parse, and diff-check.
   - Re-review before authorizing `20260914-cpu-first-03`.

### P2

1. The active-timeout synthetic test has timing/topology-sensitive exact process-count evidence.

   Evidence:
   - My local focused run passed `21 passed`.
   - My local full relevant suite passed `219 passed, 1 skipped`.
   - The orchestrator reported an independent rerun where only `test_windows_tree_runner_active_timeout_is_distinct_from_cleanup` failed because `owned_processes_seen` was `2` rather than the expected `1`; cleanup still completed.

   Impact:
   - This does not by itself prove a cleanup leak or real-run blocker.
   - It weakens the exact-count assertion as a stable proof on Windows, where wrapper/venv shims and process timing may add one owned process before timeout accounting.

   Suggested closure:
   - Change the test evidence to assert the semantic contract: `state == active_timeout`, `timed_out is True`, `cleanup_completed is True`, unrelated sentinel survival where relevant, and no owned process remains after cleanup. Avoid exact `owned_processes_seen == 1` unless the fixture topology is made deterministic.

2. Carried prior Packet B P2 remains open: the legacy `-MinerURoot` wrapper mode still accepts CPU-first-only profile names in top-level `ValidateSet`, then maps non-hybrid values through the legacy pipeline route. This is not new in the Win32 remediation and does not affect the v2 RunSpec CPU-first path, but it remains a minor user-facing CLI footgun.

## P0/P1 criteria assessment

- Suspended `CreateProcessW` -> dedicated Job Object -> resume: implemented structurally, but not accepted because `AssignProcessToJobObject` lacks explicit ABI binding.
- Correct `ctypes` ABI/handle inheritance/constrained handle list: not satisfied because of the missing `AssignProcessToJobObject` ABI. Handle-list inheritance is otherwise present.
- No shell/user command fragments; hostile args literal: satisfied by static inspection and tests.
- Runtime-contained stdout/stderr file capture, bounded/sanitized evidence, no inherited anonymous pipe EOF hang: satisfied by static inspection and tests.
- Active vs cleanup timeout distinction: satisfied semantically in implementation; test exact count is P2-flaky.
- Root exit + owned descendant cleanup, unrelated sentinel survives, no global name/PID heuristic: satisfied by synthetic tests in my run; blocked only by ABI issue above.
- Nested job/current Codex Windows behavior: helper uses a new unnamed Job and fails closed on helper exceptions; no live nested-Codex real MinerU run performed under review constraints.
- Failure modes fail closed and sealed evidence survives quarantine: satisfied by static inspection and tests.
- Helper identity in RunSpec/resume: satisfied.
- v1/success compatibility: no regression found in tests reviewed.

## Blockers

- P1: missing explicit `ctypes` ABI for `AssignProcessToJobObject`.

## Recommendation

NO-GO for a fresh real Dissociation run id `20260914-cpu-first-03` on the current CPU-only station.

The remediation is close and the synthetic/full suite evidence is otherwise strong, but the core Win32 assignment call does not meet the required ABI standard. Fix that narrow P1, rerun the same evidence set, and obtain a fresh independent closure receipt before starting the real run.
