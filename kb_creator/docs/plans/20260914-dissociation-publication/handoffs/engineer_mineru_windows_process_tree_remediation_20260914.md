# Engineer receipt: MinerU Windows process-tree remediation

Date: 2026-09-14

## Assignment

- Role: engineering.
- Assigned model/reasoning: `gpt-5.6-sol` / `high` under the user-scoped override (the repository-policy engineering default is `gpt-5.6-terra` / `medium`).
- Scope: bounded Packet B remediation for deterministic Windows child-process completion and owned-tree cleanup.

## Result

Complete. CPU-first MinerU execution no longer captures the launcher through anonymous stdout/stderr pipes. A stdlib-only helper starts the exact reviewed executable with a closed argument vector and allowlisted environment using `CreateProcessW` in a suspended state, restricts inherited handles to `NUL` plus distinct runtime-contained stdout/stderr files, assigns the root to a new Windows Job Object, and only then resumes it. No command shell or user-supplied command string is used.

After the reviewed root exits, the helper terminates and verifies only processes owned by that Job Object. The CLI version/help probes have a 120-second active timeout; extraction has a six-hour active timeout; owned-tree cleanup has a separate 30-second timeout. Active timeout, cleanup timeout, helper failure, and a nonzero child exit remain failures and are never converted to provider skips. Success requires a zero child exit and zero remaining owned processes before normal Stage 02 artifact validation.

Per-invocation spec, result, and log files are strictly below `.tools/MinerU/runtime/<profile>/invocations`, are read with bounded UTF-8 replacement decoding and stable LF normalization, and are removed deterministically. Persistent failure evidence is bounded, sanitized, sealed, and records the runner state, timeout state, cleanup proof, exit code, closed argv/profile, and allowlisted environment. Successful artifact inventories remain unchanged.

The new helper is included in the RunSpec v2 implementation inventory, so helper drift invalidates run creation/resume identity checks. Legacy v1 execution was not changed.

No `.tools` content, MinerU source/model/profile receipt, failed run root, real PDF, network, GPU/remote/API state, canonical plan/context/status, or Git commit was touched.

## Changed files

- `kb_creator/pipeline/windows_process_tree.py` (new)
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/README.md`
- this receipt

## Verification

- Focused Packet B module: `21 passed`.
- Full relevant Packet B regression set: `195 passed, 1 skipped` in 65.29 seconds.
- Python compilation: passed for the process-tree helper, process adapter, reconstruction control plane, and focused tests.
- PowerShell parser: passed for `run_mineru_three_view.ps1`.
- Schema JSON parse: passed for RunSpec v2, MinerU view execution v1, view-set v1, and multi-view comparison v2.
- Scoped `git diff --check`: passed; Git emitted only its informational LF-to-CRLF working-copy warning for the PowerShell file.

Dynamic Windows tests prove that a launcher can write output/artifacts, spawn a grandchild that inherits its file handles, and exit while the wrapper returns within a bound; the owned grandchild is gone and an unrelated sentinel process remains alive. Additional cases cover active timeout versus cleanup, nonzero exit, large stdout/stderr, hostile spaces/metacharacters without shell interpretation, runtime path escape rejection, deterministic temp cleanup, wrapper success/failure evidence, cleared hostile environment, and legacy regression coverage.

## Risk and next action

The Win32 ABI and nested Job Object behavior were exercised on the current Windows host. Independent critic review remains the release gate. Do not start another live run until that review accepts this remediation; failed runs `20260914-cpu-first-01` and `20260914-cpu-first-02` remain immutable and non-promotable.
