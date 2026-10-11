# Independent critic P1 closure: MinerU Windows process-tree remediation

- Goal: `20260914-dissociation-publication`
- Review artifact: `critic_mineru_windows_process_tree_p1_closure_20260914.md`
- Review kind: implementation
- Candidate state reviewed: non-frozen P1/P2 remediation candidate after `critic_mineru_windows_process_tree_closure_20260914.md`
- Fresh run under decision: `20260914-cpu-first-03`
- Timestamp: 2026-09-14T21:37:13.4413333+03:00
- Reviewer role declared by assignment: independent critic, `gpt-5.5` at medium reasoning
- Actual platform model disclosure: unavailable inside this agent; no claim beyond assigned role
- Implemented candidate: no
- Materially designed candidate: no
- Orchestrator policy owner: main-chat orchestrator, `gpt-5.6-sol` at medium per `docs/governance/nri_goal_governance.md`
- Assignment state: P1 closure review after engineer remediation
- Scoped override: no implementation edits, no `.tools` mutation, no real PDF/MinerU run, no network, no GPU, no remote/API, no Git operation beyond local read-only diff/status checks; only this immutable receipt was written
- Elapsed review time at receipt drafting: approximately 4 minutes in the active goal
- Token use at receipt drafting: goal snapshot reported 63,829 tokens used

## Authority reviewed

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_windows_process_tree_p1_remediation_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_windows_process_tree_closure_20260914.md`
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
- `kb_creator/README.md`

## Static evidence

### Kernel32 ABI

- `kb_creator/pipeline/windows_process_tree.py` now defines a single `KERNEL32_ABI` table.
- Independent extraction of all `kernel32.<name>(...)` calls from the helper source exactly matched the ABI table:
  - `AssignProcessToJobObject`
  - `CloseHandle`
  - `CreateFileW`
  - `CreateJobObjectW`
  - `CreateProcessW`
  - `DeleteProcThreadAttributeList`
  - `GetExitCodeProcess`
  - `InitializeProcThreadAttributeList`
  - `QueryInformationJobObject`
  - `ResumeThread`
  - `SetInformationJobObject`
  - `TerminateJobObject`
  - `TerminateProcess`
  - `UpdateProcThreadAttribute`
  - `WaitForSingleObject`
- `AssignProcessToJobObject` is explicitly declared as `(wintypes.HANDLE, wintypes.HANDLE) -> wintypes.BOOL`.
- `CreateProcessW` is explicitly declared with a `wintypes.BOOL` return type.
- `DeleteProcThreadAttributeList` is explicitly declared with `None` return type.
- `_load_kernel32()` fails closed before process creation when `os.name != "nt"`, `sizeof(HANDLE) != sizeof(void*)`, or `sizeof(BOOL) != 4`.
- Local ABI probe output:

```text
used_equals_abi True
assign ((<class 'ctypes.c_void_p'>, <class 'ctypes.c_void_p'>), <class 'ctypes.c_long'>)
handle_size 8 voidp_size 8 bool_size 4
```

### Process-tree and handle semantics

- The helper creates the child suspended with `CREATE_SUSPENDED`, configures an unnamed dedicated Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, assigns the root process with `AssignProcessToJobObject`, then resumes the main thread.
- Inheritance is constrained through `PROC_THREAD_ATTRIBUTE_HANDLE_LIST`; the inherited list is exactly stdin from `NUL`, stdout file, and stderr file.
- User arguments are passed through `subprocess.list2cmdline([spec["executable"], *spec["arguments"]])`; no shell dispatch or user command fragments were found.
- The helper writes stdout/stderr to runtime-contained files, not anonymous pipes.
- The helper validates runtime containment, distinct stdout/stderr paths, absolute executable/working directory, NUL-free argv/env, case-insensitive env key uniqueness, and bounded active/cleanup timeout values.
- Cleanup distinguishes `active_timeout` from `cleanup_timeout`; timeout/cleanup evidence is semantic and no longer depends on incidental process-count equality.
- On helper errors, result state is `helper_error` or wrapper validation rejects invalid coupling; wrapper treats invalid helper result as exit `125` and failure, not skip.

### Wrapper and resume identity

- `run_mineru_three_view.ps1` keeps the CPU-first path under `-ToolRoot`, remaps `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, temp/cache/model paths into the verified profile runtime, and does not include proxy/API/PYTHONPATH variables in the closed environment.
- `run_mineru_three_view.ps1` validates `kb_creator.windows_process_tree_result.v2` and only accepts coupled states:
  - completed + cleanup completed
  - active timeout + cleanup completed
  - cleanup timeout + cleanup incomplete
  - helper error + cleanup incomplete
- Failure evidence remains sealed as `kb_creator.mineru_closed_invocation_failure.v2`.
- `reconstruction.py` includes `kb_creator/pipeline/windows_process_tree.py` in the RunSpec implementation inventory and rejects stale implementation on resume.
- Stage process failures are sealed as `kb_creator.stage_failure.v1` and retained under the run-local failure/quarantine path.

### Legacy wrapper boundary

- `pipeline_txt` and `vlm_local` remain valid only for CPU-first `-ToolRoot` execution.
- Before legacy initialization, the wrapper rejects non-historical profiles with:

```text
Profile '<profile>' requires CPU-first -ToolRoot execution; legacy -MinerURoot accepts only hybrid_high or pipeline_ocr.
```

- The historical legacy `-MinerURoot` route remains available for `hybrid_high` and `pipeline_ocr`.

## Verification commands

Targeted remediation subset:

```text
$env:PYTHONPATH = '.tools\python-test-deps'
python -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py -q -k "kernel32 or active_timeout or grandchild or hostile or wrapper_dispatch"
6 passed, 20 deselected in 9.76s
```

Focused Packet B module:

```text
$env:PYTHONPATH = '.tools\python-test-deps'
python -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py -q
26 passed in 35.84s
```

Full relevant suite:

```text
$env:PYTHONPATH = '.tools\python-test-deps'
python -m pytest kb_creator/tests/test_mineru_cpu_packet_b.py kb_creator/tests/test_reconstruction_control_plane.py kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_mineru_visual_merge_bundle.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_materialize_mineru_ai_merge.py kb_creator/tests/test_finalize_mineru_reconstruction.py kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py kb_creator/tests/test_pipeline_identity.py -q
224 passed, 1 skipped in 91.38s
```

Compile:

```text
python -m compileall -q kb_creator\pipeline\windows_process_tree.py kb_creator\pipeline\process.py kb_creator\pipeline\reconstruction.py kb_creator\tests\test_mineru_cpu_packet_b.py
PASS
```

PowerShell parser:

```text
[System.Management.Automation.Language.Parser]::ParseFile('kb_creator/scripts/run_mineru_three_view.ps1', ...)
PowerShell parser ok
```

Schema parse:

```text
json.loads(...) for run_spec.v2, mineru_view_execution.v1, mineru_view_set.v1, mineru_multi_view_comparison.v2
schema json parse ok 4
```

Scoped diff-check:

```text
git diff --check -- kb_creator\pipeline\windows_process_tree.py kb_creator\scripts\run_mineru_three_view.ps1 kb_creator\tests\test_mineru_cpu_packet_b.py kb_creator\README.md kb_creator\docs\plans\20260914-dissociation-publication\handoffs\engineer_mineru_windows_process_tree_p1_remediation_20260914.md
PASS; Git emitted only its informational LF-to-CRLF warning for kb_creator/scripts/run_mineru_three_view.ps1
```

No real MinerU/PDF extraction, GPU operation, network, remote/API call, install/download, implementation edit, `.tools` mutation, or Git commit was performed.

## Findings

### P0

None found.

### P1

None found.

The previous P1 is closed. `AssignProcessToJobObject` now has explicit `(HANDLE, HANDLE) -> BOOL` binding and all used Kernel32 calls are covered by a single exact ABI table with fail-closed ABI/platform checks before process creation.

### P2

None found.

The prior P2 timeout-count issue is closed by removing incidental process-count evidence from the result contract and by checking stable semantics across three timeout attempts. The prior legacy wrapper profile footgun is closed by rejecting `pipeline_txt` and `vlm_local` in legacy `-MinerURoot` mode while preserving `hybrid_high` and `pipeline_ocr`.

## Criteria assessment

- Explicit `argtypes`/`restype` for all used Kernel32 calls: pass.
- `AssignProcessToJobObject` specifically bound as `(HANDLE, HANDLE) -> BOOL`: pass.
- Fail-closed unsupported ABI/platform handling: pass.
- Suspended process creation, dedicated Job Object, KILL_ON_JOB_CLOSE, assign, then resume: pass.
- Constrained handle inheritance through `HANDLE_LIST`: pass.
- Runtime-local stdout/stderr file capture without inherited anonymous pipe EOF hang: pass.
- Active timeout vs cleanup timeout distinction: pass.
- Root/owned descendant cleanup and unrelated sentinel survival: pass by synthetic tests.
- No global process-name/PID heuristic: pass by static inspection and tests.
- Repeatable topology-stable timeout tests: pass; active-timeout case is parameterized for three attempts and no longer asserts exact incidental process count.
- Legacy wrapper rejects CPU-first-only profiles without `-ToolRoot`: pass.
- Historical legacy profiles preserved: pass.
- Helper identity in RunSpec/resume and v1/success compatibility: pass.

## Blockers

None.

## Recommendation

GO for a fresh local CPU-only Dissociation run id `20260914-cpu-first-03`, within the existing run authority and without resuming either failed run `20260914-cpu-first-01` or `20260914-cpu-first-02`.
