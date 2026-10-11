# Engineering receipt — MinerU single-key receipt-shape remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-single-key-shape-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: closed shape validation now preserves zero/one/many key cardinality
  and accepts the valid sealed uv receipt shape
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not live runtime,
reconstruction, publication or release acceptance.

## Defect and correction

Recovery successfully wrote the atomic uv receipt, but immediate
self-validation failed on the valid one-key `archive_hashes` object. The
conditional that selected dictionary keys or object properties emitted its
single result through the PowerShell pipeline, collapsing the intended array
to a scalar string without a reliable `Count` property.

`Assert-MinerUExactObjectShape` now wraps the entire conditional enumeration in
`@(...)`, explicitly stringifies each key, and therefore preserves an array for
zero, one, or many keys.

The uv receipt's exact nested-shape logic was extracted into the sourceable
`Assert-MinerUUvReceiptShape` helper. It retains strict bootstrap-Python,
identity, executable-triad, artifact-provenance, one-key archive-hash, string,
hash, architecture and supported-version validation. Runtime validation still
adds the internal seal, current file/RECORD identities, pip report and uv
version checks.

## Dynamic evidence

An actual PowerShell 7 test sources the production helper and exercises both
`PSCustomObject` and ordered-dictionary inputs:

- exact one-key objects pass;
- zero-key objects reject without scalar property errors;
- multi-key objects reject without scalar property errors;
- a realistic uv receipt whose `archive_hashes` contains exactly `sha256`
  passes the extracted receipt-shape validator.

## Files changed

- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/bootstrap-python.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

The existing actual receipt and `.tools` tree were not read or mutated. No
installation, deletion, model, lock, real-source, remote, canonical-document or
critic-receipt change occurred.

## Verification

- Cardinality and realistic receipt dynamic test: PASS.
- PowerShell parser: PASS for `profile-common.ps1` and
  `bootstrap-python.ps1`.
- Focused pytest: `68 passed in 20.89s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS.

## Remaining gate

Independent implementation review is required before the orchestrator resumes
the separately authorized live bootstrap flow.
