# Engineering receipt — MinerU live-bootstrap CLI remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-live-cli-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Result: pre-install CLI binding defect fixed and dynamically verified
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not runtime acceptance,
reconstruction acceptance, publication acceptance or release approval.

## Defect and correction

The first authorized setup invocation failed before installation because
`setup.ps1` constructed bootstrap arguments as a string array. PowerShell
script splatting treated the strings such as `-BootstrapPythonPath` as
positional values rather than named parameter tokens.

`setup.ps1` now constructs a hashtable named splat. `ToolRoot` is always keyed;
`BootstrapPythonPath`, `RecreateBootstrap` and `RecreateManagedPython` are added
by name only when supplied. The existing output contract remains unchanged:
setup requires exactly one non-empty string, checks containment below
`.tools/python`, and requires an exact independently receipted path before any
profile venv creation.

## Dynamic regression evidence

A focused test writes and invokes a minimal temporary child `.ps1` with the
same four-parameter signature as `bootstrap-python.ps1`. Using the exact
hashtable construction pattern, it verifies that path values containing spaces
bind to `ToolRoot` and `BootstrapPythonPath`, and both recreation switches bind
as true. This exercises PowerShell parameter binding rather than relying only
on source-string assertions.

## Files changed

- `MinerU/scripts/setup.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

No installation, download, deletion, recreation or further `.tools` mutation
was performed. Models, source, sealed runs, locks, canonical documents and
critic receipts were not changed.

## Verification

- `setup.ps1` PowerShell parser: PASS.
- Focused pytest: `47 passed in 7.07s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Dynamic named-splat child invocation: PASS, including path values with spaces
  and both switches.

## Remaining gate

The corrected live setup command may be retried only by the orchestrator under
the existing explicit execution authorization and independent-review gates.
