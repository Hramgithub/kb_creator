# Engineering receipt — MinerU uv RECORD path remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-record-path-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: uv companion RECORD paths are now derived from actual installation
  geometry and retain exact row/hash/size validation
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not live runtime,
reconstruction, publication or release acceptance.

## Defect and correction

The live uv wheel RECORD correctly used `../../Scripts/uv.exe`,
`../../Scripts/uvw.exe`, and `../../Scripts/uvx.exe`. Recovery hard-coded an
extra parent segment and therefore rejected valid state before receipt creation.

`Get-MinerUUvExecutableEvidence` now discovers the exact
`uv-0.12.13.dist-info` directory, uses its parent `site-packages` installation
base, and computes each executable row with
`System.IO.Path.GetRelativePath`. Windows separators are normalized to the
forward slashes used by wheel RECORD. The result is then matched
case-sensitively as before; no directory depth is hard-coded.

Companion containment, ordered uv/uvw/uvx triad, RECORD SHA-256, byte-size,
sealed receipt, and managed-Python linkage checks are unchanged.

## Dynamic evidence

The temporary recovery fixture now uses realistic
`Lib/site-packages/uv-0.12.13.dist-info/RECORD` geometry with
`../../Scripts/...` rows and succeeds. An adversarial copy with all rows changed
to `../../../Scripts/...` is rejected without writing a receipt.

## Files changed

- `MinerU/scripts/profile-common.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

The actual `.tools` tree was not read or mutated. No installation, deletion,
model, lock, real-source, remote, canonical-document or critic-receipt change
occurred.

## Verification

- Realistic RECORD geometry test: PASS.
- Wrong-depth RECORD attack: PASS (rejected without receipt).
- `profile-common.ps1` PowerShell parser: PASS.
- Focused pytest: `67 passed in 20.46s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS.

## Remaining gate

Independent implementation review is required before the orchestrator resumes
the separately authorized live recovery.
