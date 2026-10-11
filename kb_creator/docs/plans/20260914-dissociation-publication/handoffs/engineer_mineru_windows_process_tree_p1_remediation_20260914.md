# Engineer receipt: MinerU Windows process-tree P1 remediation

Date: 2026-09-14

## Assignment

- Role: engineering.
- Assigned model/reasoning: `gpt-5.6-sol` / `high` under the user-scoped override (the repository-policy engineering default is `gpt-5.6-terra` / `medium`).
- Authority: bounded remediation of `critic_mineru_windows_process_tree_closure_20260914.md` findings P1, P2a, and P2b.

## Result

Complete.

The Windows helper now defines one closed ABI table for every Kernel32 function it calls. `AssignProcessToJobObject` is explicitly bound as `(HANDLE, HANDLE) -> BOOL`; `CreateProcessW` now also has an explicit `BOOL` return type, and the void `DeleteProcThreadAttributeList` return is explicitly `None`. The loader rejects non-Windows platforms, unexpected pointer-width `HANDLE`, and non-four-byte `BOOL` before any process creation. A static test derives every `kernel32.<name>(...)` call from source and requires an exact match with the ABI table; a dynamic test inspects every loaded function's actual `argtypes` and `restype` and separately asserts the assignment signature.

The helper result no longer exposes an incidental process count. Timeout evidence promises only stable semantics: active timeout, owned-tree cleanup completion, exact owned PID termination, and unrelated sentinel survival. The timeout case is parameterized for three independent executions to exercise shim/base-process topology variance.

Wrapper dispatch is now closed at the mode boundary. `pipeline_txt` and `vlm_local` reject before legacy initialization whenever `-ToolRoot` is absent. Compatibility `-MinerURoot` accepts only the historical `hybrid_high` and `pipeline_ocr` profiles. Dynamic PowerShell tests prove both rejection and continued historical routing; the existing v1 regression suite remains green.

No `.tools` content, failed run root, real PDF, MinerU source/model/profile receipt, network, GPU/remote/API state, canonical plan/context/status, or Git commit was touched.

## Changed files

- `kb_creator/pipeline/windows_process_tree.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/README.md`
- this receipt

## Verification

- Targeted ABI/timeout/dispatch tests: `6 passed`.
- Focused Packet B module: `26 passed`.
- Full relevant suite, including finalize and v1 compatibility: `224 passed, 1 skipped` in 86.98 seconds.
- The active-timeout test ran three times inside each focused/full invocation; all repetitions passed without an exact process-count assumption.
- Python compilation: passed for the process-tree helper, process adapter, reconstruction control plane, and focused tests.
- PowerShell parser: passed for `run_mineru_three_view.ps1`.
- Schema JSON parse: passed for RunSpec v2, MinerU view execution v1, view-set v1, and multi-view comparison v2.
- Scoped `git diff --check`: passed; Git emitted only its informational LF-to-CRLF working-copy warning for the PowerShell file.

## Risk and next action

No implementation blocker remains in this bounded remediation. Independent critic closure is still required before a new live run; no live command is authorized or supplied by this receipt.
