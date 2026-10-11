# Engineering receipt — MinerU sealed JSON date remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-json-date-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: sealed PowerShell receipt reads preserve exact JSON date strings and
  fail early when that parser capability is unavailable
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not live runtime,
reconstruction, publication or release acceptance.

## Defect and correction

PowerShell 7.6.2's default `ConvertFrom-Json` converted the uv receipt's
`checked_at_utc` ISO string into `System.DateTime`. Exact type validation then
correctly rejected the altered in-memory representation, even though the
receipt JSON and seal were valid.

`ConvertFrom-MinerUStrictJson` now uses
`ConvertFrom-Json -DateKind String`; `Read-MinerUStrictJson` is the shared file
entry point. All PowerShell-side sealed uv and managed-Python receipt reads use
this helper. Ordinary pip report, inventory, config and provider JSON remain
ordinary data paths and do not participate in receipt seal canonicalization.

`Assert-MinerUJsonDateStringSupport` enforces PowerShell 7.5 or newer and
feature-detects the `DateKind` parameter before any repository-local root is
resolved. The README documents this exact runtime floor and why older versions,
including Windows PowerShell 5.1, are unsupported. Timestamp validation remains
strictly string-typed; receipt seal canonicalization was not weakened or
changed.

## Dynamic evidence

An actual PowerShell 7 test constructs a realistic nested uv receipt, seals it,
serializes it to JSON, parses it through the production strict helper, and
proves:

- `checked_at_utc` remains `System.String`;
- its exact value remains `2026-09-14T00:00:00Z`;
- the receipt seal still validates;
- the realistic one-key archive-hash shape remains valid.

The same test injects command metadata without `DateKind` and proves the
capability guard rejects it. A Windows PowerShell 5.1 process dynamically
proves the explicit 7.5+ fail-fast message.

## Files changed

- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/README.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

The existing actual receipt and `.tools` tree were not read or mutated. No
installation, deletion, model, lock, real-source, remote, canonical-document or
critic-receipt change occurred.

## Verification

- Strict JSON date/seal round-trip test: PASS on actual PowerShell 7.
- Unsupported parser capability and Windows PowerShell 5.1 floor tests: PASS.
- PowerShell parser: PASS for `profile-common.ps1` and
  `bootstrap-python.ps1`.
- Focused pytest: `68 passed in 21.41s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS.

## Remaining gate

Independent implementation review is required before the orchestrator resumes
the separately authorized live bootstrap flow.
