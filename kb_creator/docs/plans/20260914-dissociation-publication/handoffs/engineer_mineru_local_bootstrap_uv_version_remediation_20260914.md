# Engineering receipt — MinerU uv version-output remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-uv-version-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: official uv build-metadata output accepted without widening the
  pinned-version boundary
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not runtime acceptance,
reconstruction acceptance, publication acceptance or release approval.

## Defect and correction

The installed executable returned the official output
`uv 0.12.13 (0ebbd9274 2026-09-10 x86_64-pc-windows-msvc)` with exit code zero,
while bootstrap validation accepted only the legacy short form
`uv 0.12.13`. The result was a pre-Python-install failure after creation of the
uv venv/report but before its receipt.

`Test-MinerUUvVersionOutput` now parses the version token as `System.Version`
and requires its normalized three-component representation to equal the exact
pinned `0.12.13`. It accepts either the complete short form or one anchored
official parenthetical containing exactly a nine-character lowercase commit,
a semantically valid ISO date, and the required Windows x64 MSVC target. No
leading/trailing text or alternate version is accepted. Both post-install and
receipt-revalidation call sites use this shared parser. Receipt version and
executable-identity requirements are unchanged.

## Adversarial evidence

A dynamic PowerShell test sources the actual helper and accepts the short form
plus the observed official output. It rejects `0.12.12`, `0.12.130`, prefixed
junk, trailing junk, wrong commit length, an impossible date, the wrong target,
and a valid-looking parenthetical followed by a suffix.

## Files changed

- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/bootstrap-python.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

The existing partial `.tools/uv/bootstrap-uv-0.12.13` state was not read,
deleted, repaired or mutated. No install/download, real source run, model,
sealed-run, canonical-document or critic-receipt change occurred.

## Verification

- PowerShell parser: PASS for the changed scripts.
- Dynamic semantic-version adversarial test: PASS.
- Focused pytest: `48 passed in 8.36s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS.

## Remaining gate

The orchestrator may decide whether to resume the separately authorized live
bootstrap. This remediation itself performs no live execution.
