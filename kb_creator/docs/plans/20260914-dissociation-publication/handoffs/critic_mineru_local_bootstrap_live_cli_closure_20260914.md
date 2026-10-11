# Critic receipt — MinerU live-bootstrap CLI binding closure

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-live-cli-remediation-closure-review`
- Review kind: `implementation`
- Candidate state: non-frozen implementation candidate; not a release review
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; role ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review. The engineering override remains scoped to implementation only.
- Timestamp: `2026-09-14T17:28:12+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:00:24`
- Token use: active runtime goal reported `11462` tokens before receipt write

This receipt is an immutable urgent implementation closure review for the live
CLI binding remediation only. It is not runtime acceptance, reconstruction
acceptance, publication acceptance, release approval, or authority to run the
real Dissociation source.

## Scope

Reviewed:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_live_cli_remediation_20260914.md`
- `MinerU/scripts/setup.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`

Regression scope checked against:

- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/README.md`
- `MinerU/models/manifest.json`
- sealed historical run metadata under
  `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01`

Forbidden scope was honored: no install, no download, no deletion, no `.tools`
mutation, no implementation edit, no real source run, no remote/API execution,
no commit, and no canonical plan/context/status/release edit. This receipt is
the only file written.

## Closure evidence

- First live error logic is closed. The failed string-array splat pattern was
  replaced by a hashtable named splat:
  `@{ ToolRoot = $roots.ToolRoot }`, with `BootstrapPythonPath`,
  `RecreateBootstrap`, and `RecreateManagedPython` added by property name.
  This prevents `-BootstrapPythonPath` from binding as a positional string to
  the child script.
- Dynamic PowerShell binding was reproduced. The focused test
  `test_setup_style_named_splat_binds_bootstrap_child_parameters` creates a
  temporary child `.ps1`, passes path values containing spaces plus both
  switches through the same hashtable pattern, and verifies all named
  parameters bind correctly.
- The single-path/receipt containment contract is unchanged and still stronger
  after bootstrap return. `setup.ps1` captures child output as an array,
  requires exactly one non-empty string, contains it below `.tools/python`,
  calls `Get-MinerUManagedPython`, and requires the returned receipted path to
  match exactly before profile venv creation.
- Native-output capture remains intact. `bootstrap-python.ps1` routes direct
  bootstrap native calls through `Invoke-MinerUNativeCaptured`; the temporary
  `.cmd` stdout-contamination test still passes in the full focused suite.
- Existing pip-report/provenance receipt closure remains intact in the checked
  files: uv bootstrap validation requires the live pip report, bytes/hash
  match, one exact `uv==0.12.13` row, and provenance match to URL, wheel
  filename and archive SHA-256.
- CPU-first/provider-local behavior did not regress. `setup.ps1` still installs
  `pipeline-cpu-v1` before hardware probe and still requires exactly one ready
  `pipeline_cpu`; no global setup `SKIPPED` path was introduced.
- Model identity did not regress. A read-only audit reported 40/40 pipeline
  model manifest rows matching exact bytes and SHA-256.
- Sealed historical no-CUDA run safety was preserved. `run.json` and
  `skip.json` were inspected only for metadata and not mutated.

## Reproduced checks

Full focused harness:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result:

```text
47 passed in 7.07s
```

Dynamic child-script named-splat test:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py::test_setup_style_named_splat_binds_bootstrap_child_parameters -vv
```

Result:

```text
1 passed in 1.43s
```

Temporary `.cmd` stdout-contamination test was included in the full focused
suite. The test creates `noisy-native.cmd`, verifies `Invoke-MinerUNativeCaptured`
returns one result object, and stores both stdout records only in `Lines`.

PowerShell parser:

```powershell
[System.Management.Automation.Language.Parser]::ParseFile(...) for:
  MinerU/scripts/setup.ps1
```

Result: `setup.ps1` parse PASS.

Scoped diff check:

```powershell
git diff --check -- MinerU/scripts/setup.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: PASS; Git emitted only the known Windows line-ending advisory for
`MinerU/scripts/setup.ps1`.

One additional `rg` regex probe was malformed by the reviewer and is not used
as evidence. The direct file reads and reproduced tests above cover the binding
and output contracts.

## Findings

### P0

None.

### P1

None.

### P2

None in the reviewed urgent CLI binding scope.

## Blockers

No implementation-review blocker remains for retrying the live
bootstrap/setup command under the existing orchestrator authorization.

The retry still must produce actual runtime evidence: repository-local uv and
CPython receipts, CPU profile install/verify receipts, synthetic MinerU smoke
evidence, and provider capability receipt. This closure does not authorize or
accept a real Dissociation source run.

## Recommendation

Go for retry of the live bootstrap/setup command on the current PC under the
existing explicit execution authorization.

Do not run the real Dissociation source from this receipt.
