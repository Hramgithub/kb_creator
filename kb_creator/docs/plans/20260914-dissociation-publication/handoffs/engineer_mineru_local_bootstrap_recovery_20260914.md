# Engineering receipt — MinerU partial-bootstrap recovery

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-partial-bootstrap-recovery`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: explicit nondestructive partial-uv recovery implemented with
  fail-before-write validation and temporary-tree adversarial coverage
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not live runtime,
reconstruction, publication or release acceptance.

## Recovery contract

`bootstrap-python.ps1` and `setup.ps1` now expose explicit
`-RecoverBootstrap` plumbing. Recovery is mutually exclusive with
`-RecreateBootstrap`, requires `-BootstrapPythonPath`, and applies only when the
fixed `.tools/uv/bootstrap-uv-0.12.13` directory exists without an install
receipt. It is never selected automatically.

Before its only write—the atomic sealed uv receipt—recovery independently
validates:

- the supplied executable is 64-bit CPython 3.10 through 3.13 and records its
  exact bytes/SHA-256;
- the exact `pyvenv.cfg` key set, version, base executable, base home,
  system-site-packages isolation and venv creation command all link to that
  supplied executable and the fixed venv path;
- required venv Python and uv executables exist as contained files;
- root/venv paths contain no reparse points, startup customization or
  unexpected root/Scripts payloads;
- the lock contains exactly the single `uv==0.12.13` pin;
- the pip report contains exactly one uv `0.12.13` HTTPS Windows amd64 wheel
  row with lowercase archive SHA-256;
- uv reports the exact accepted pinned version;
- installed distributions contain exactly one uv `0.12.13` plus only pip and
  optional setuptools, without duplicates or extra distributions;
- offline `pip check` exits successfully.

Inventory and `pip check` run with `PIP_NO_INDEX=1` and
`PYTHONDONTWRITEBYTECODE=1`, with the caller's process values restored in a
`finally` block, so validation neither reaches a package index nor creates
bytecode before the receipt decision.

The receipt is constructed by the same helper used by the normal install path,
so schema, exact version, executable identity, lock/report identity and wheel
provenance remain identical. After receipt revalidation, normal managed-Python
installation can continue and the existing single-output-path contract remains
in force.

## Adversarial evidence

Tests build isolated temporary uv trees and inject deterministic native-command
results. The valid fixture writes and seals a receipt. Six invalid fixtures—
missing report, tampered report hash, wrong uv version, mismatched pyvenv
version, missing base executable, and wrong venv command path—all fail with no
receipt written. No test reads or writes the repository `.tools` tree.

The shared root resolver now fails immediately with a clear message below
PowerShell 7 because its containment logic uses modern .NET path APIs. README
prerequisites state this runtime floor and a dynamic Windows PowerShell 5.1
test verifies the explicit rejection instead of implying compatibility.

## Files changed

- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/setup.ps1`
- `MinerU/README.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

No lock, model, real source, sealed run, canonical plan/context/status, critic
receipt or `.codex` configuration was changed. The actual partial bootstrap
under `.tools` was not read, mutated, deleted or recreated.

## Verification

- PowerShell parser: PASS for `bootstrap-python.ps1`, `profile-common.ps1` and
  `setup.ps1`.
- Valid temporary-tree recovery test: PASS.
- Six fail-before-write recovery adversarial tests: PASS.
- Focused pytest: `57 passed in 13.19s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS; Git emitted only its existing Windows
  line-ending advisory for `setup.ps1`.

## Remaining gate

Independent implementation review is required. Live recovery remains a
separate orchestrator-controlled execution under the existing authorization.
