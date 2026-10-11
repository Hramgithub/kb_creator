# Engineering receipt — MinerU bootstrap Python-version allowlist remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-python-version-allowlist-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: recovery now accepts the exact standard pip launcher layout for
  every supported external CPython minor and rejects mismatches
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not live runtime,
reconstruction, publication or release acceptance.

## Defect and correction

Recovery independently allowed an external 64-bit CPython from 3.10 through
3.13, but its closed Scripts allowlist hard-coded `pip3.12.exe`. A valid
CPython 3.13.7 venv therefore produced standard `pip3.13.exe` and was rejected
before receipt creation.

After validating the supplied bootstrap runtime identity, recovery now parses
that exact version as `System.Version` and derives one required launcher name:
`pip<major>.<minor>.exe`. The closed standard pip set is exactly `pip.exe`,
`pip3.exe`, and that derived launcher. Each required name must occur exactly
once, and the case-sensitive Scripts allowlist rejects every other versioned
pip executable. All uv companion and RECORD identity requirements are
unchanged.

## Dynamic evidence

Isolated temporary-tree recovery tests provide standard launcher layouts for
CPython `3.10.14`, `3.11.9`, `3.12.14`, and `3.13.7`; all four recover and seal
successfully. An otherwise valid 3.13 fixture containing an additional
`pip3.9.exe` is rejected before writing a receipt. Existing uv triad/RECORD,
report, pyvenv, inventory and fail-before-write attacks remain in the focused
suite.

## Files changed

- `MinerU/scripts/profile-common.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

The actual `.tools` tree was not read, mutated, deleted or recreated. No
installation, model, lock, real-source, remote, canonical-document or critic
receipt change occurred.

## Verification

- Version-specific dynamic recovery tests: PASS for 3.10/3.11/3.12/3.13.
- Mismatched versioned pip launcher attack: PASS (rejected without receipt).
- `profile-common.ps1` PowerShell parser: PASS.
- Focused pytest: `66 passed in 19.55s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS.

## Remaining gate

Independent implementation review is required before resuming the separately
authorized live recovery.
