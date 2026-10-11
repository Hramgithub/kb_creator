# Engineering receipt — MinerU local bootstrap remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-python-bootstrap-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded for this assignment by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Scoped override: active — user-directed engineering execution with
  `gpt-5.6-sol` at `high`
- Scope: remediate the two P1 and two P2 findings in
  `critic_mineru_local_bootstrap_review_20260914.md`
- Result: all four findings remediated; focused verification passes
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not independent review,
runtime acceptance, reconstruction acceptance, publication acceptance, release
approval, or authority to execute the real source.

## Remediation

### P1 — single bootstrap success value

All native commands in `bootstrap-python.ps1` now run through
`Invoke-MinerUNativeCaptured`. The helper captures stdout and stderr as a
single result object's `Lines` property plus `ExitCode`; installer progress can
no longer leak into the script success stream. The bootstrap script emits only
the final managed-Python path on successful completion.

`setup.ps1` converts bootstrap success output to an array and requires exactly
one non-empty string. It then asserts containment below `.tools/python`, calls
the independent managed-runtime receipt validator, and requires exact path
identity before any profile venv creation.

An executable temporary `.cmd` harness emits two stdout records. The focused
test proves the capture helper returns one object containing those two records,
instead of leaking either record into its caller's success stream. Static
guards additionally prove setup rejects multi-record, empty, non-string,
escaping, or non-receipted bootstrap output.

### P1 — pip report and provenance binding

`Assert-UvBootstrapReceipt` now requires the live
`pip-install-report.json`, verifies its exact bytes and SHA-256 against the
sealed receipt, selects exactly one `uv` row at version `0.12.13`, and derives
the report URL, wheel filename and archive SHA-256 from that row. All three
values must exactly match the sealed `artifact_provenance` object. A missing,
changed or semantically mismatched report fails closed.

### P2 — closed nested receipt schemas

Shared validators now enforce exact key sets, object types, positive integer
byte counts, lowercase SHA-256 values and non-empty string types. The uv receipt
strictly validates nested bootstrap-Python identity, lock/report/executable
identities, artifact provenance and archive hashes, plus CPython architecture
and supported version range. The managed-Python receipt strictly validates its
executable identity, uv-receipt linkage and exact install-evidence object.

### P2 — portable README

Legacy durable drive-letter examples were replaced with `<NRI>` and
repository-relative input/output paths without changing the documented
`run-hybrid.ps1` behavior.

## Files changed

- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/setup.ps1`
- `MinerU/README.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this remediation receipt

No dependency lock, provider/profile contract, model, sealed run, canonical
plan/context/status, critic receipt, `.codex` configuration or live `.tools`
payload was changed by this remediation.

## Verification

- PowerShell parser: PASS for `bootstrap-python.ps1`, `profile-common.ps1`, and
  `setup.ps1`.
- Focused pytest: `46 passed in 6.16s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- The executable stdout-contamination harness passes independently.
- Scoped `git diff --check`: PASS; Git emitted only its existing Windows
  line-ending advisory for `setup.ps1`.
- No live installation/download, real MinerU source execution, remote/API
  action or actual `.tools` mutation occurred.

## Remaining gate

The remediated implementation requires independent re-review. Live bootstrap
and setup remain a separate explicitly authorized step.
