# Engineer receipt: MinerU CPU runtime home and failure diagnostics remediation

Date: 2026-09-14

## Assignment

- Role: engineering.
- Assigned model/reasoning: `gpt-5.6-sol` / `high` under the user-scoped override (the repository-policy engineering default is `gpt-5.6-terra` / `medium`).
- Scope: bounded Packet B remediation for repository-local runtime home paths and retained closed-process failure evidence.

## Result

Complete. The CPU-first MinerU wrapper now launches each required view with a fully allowlisted environment whose writable home, roaming/local application data, cache, model-cache, config, and temporary paths are all strictly contained below `.tools/MinerU/runtime/<profile>`. It creates those roots before launch and does not inherit the real user profile, proxy/API variables, `PYTHONPATH`, or user cache paths. A closed-environment dynamic test proves that Python `Path.home()` resolves to the synthetic runtime home.

Nonzero child exits now produce deterministic, bounded, control-character-sanitized `failure.json` evidence containing the closed argv, allowlisted environment, profile, exit code, stdout/stderr, truncation flags, and an integrity hash. The wrapper drains stdout and stderr concurrently to avoid pipe deadlock. The v2 control plane also writes a sealed `stage-failure.json` before quarantine, so Stage 02 remains a failure (never a skip) and its evidence remains diagnosable below the failed run root. Successful views keep their prior output/receipt contract and do not gain a failure artifact.

No live MinerU run, PDF processing, dependency installation, network access, GPU/remote/API operation, `.tools` mutation, sealed-run mutation, or commit was performed.

## Changed files

- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/pipeline/process.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/README.md`
- this receipt

## Verification

- Focused Packet B test module: `17 passed`.
- Full relevant Packet B regression set: `191 passed, 1 skipped` in 53.99 seconds.
- Python compilation: passed for `process.py`, `reconstruction.py`, and `test_mineru_cpu_packet_b.py`.
- PowerShell parser: passed for `run_mineru_three_view.ps1`.
- Schema JSON parse: passed for RunSpec v2, MinerU view execution v1, view-set v1, and multi-view comparison v2.
- Scoped `git diff --check`: passed (Git emitted only its informational LF-to-CRLF working-copy warning for the PowerShell file).

The adversarial coverage includes hostile inherited user/profile/cache/proxy/API/`PYTHONPATH` values, contained `Path.home()`, runtime path escape checks, large/control-character child output, nonzero exit evidence surviving quarantine, seal validation, and an unaffected success path.

## Risks and next action

Implementation verification is green; independent critic review remains the release gate. After that review, the orchestrator may start a new immutable live run with a new run id/root. The failed `20260914-cpu-first-01` run remains untouched.
