# Engineering receipt — MinerU uv companion remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-uv-companion-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: the exact pinned uv Windows executable triad is now required,
  wheel-bound, receipted and revalidated
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not live runtime,
reconstruction, publication or release acceptance.

## Defect and correction

The uv `0.12.13` Windows amd64 wheel legitimately installed `uv.exe`,
`uvw.exe` and `uvx.exe`. Recovery's closed Scripts allowlist omitted `uvw.exe`,
so it rejected valid live state before writing a receipt.

The bootstrap definition now names all three fixed companion paths. Recovery
requires every companion as a contained leaf and permits no additional Scripts
payload beyond the closed standard-venv list. It still executes only `uv.exe`;
`uvw.exe` and `uvx.exe` are identity evidence, never version authorities.

Each companion is independently bound to the pinned wheel's installed
`uv-0.12.13.dist-info/RECORD`: the exact relative row, SHA-256 in RECORD's
base64url form, and byte size must match the current file. The sealed uv receipt
now carries an exact ordered `uv_executables` array for `uv.exe`, `uvw.exe`, and
`uvx.exe`, each with name, bytes and lowercase SHA-256. Normal installation and
explicit recovery construct that same receipt through one helper.

Uv receipt validation requires the exact nested three-row shape and compares
all current identities to both RECORD and the sealed receipt. Managed-Python
validation uses the same full-set validator after checking its linked uv
receipt file identity and seal, so a changed companion invalidates the managed
runtime linkage.

## Adversarial evidence

Temporary-tree tests prove:

- the exact triad recovers successfully in order;
- a missing `uvw.exe` fails before receipt creation;
- an extra executable in Scripts fails before receipt creation;
- a companion changed after RECORD generation fails before receipt creation;
- a companion changed after receipt creation is rejected by the same validator
  used by managed-Python linkage.

No test reads or writes the repository `.tools` tree.

## Files changed

- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/bootstrap-python.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

No live installation, deletion or `.tools` mutation occurred. Locks, models,
real source, sealed runs, canonical documents and critic receipts were not
changed.

## Verification

- Companion-focused temporary-tree tests: PASS.
- PowerShell parser: PASS for `profile-common.ps1` and
  `bootstrap-python.ps1`.
- Focused pytest: `61 passed in 15.72s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS.

## Remaining gate

Independent implementation review is required before the orchestrator resumes
the separately authorized live recovery.
