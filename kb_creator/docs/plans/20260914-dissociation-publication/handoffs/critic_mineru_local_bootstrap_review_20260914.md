# Critic receipt — MinerU repository-local bootstrap review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-python-bootstrap-review`
- Review kind: `implementation`
- Candidate state: non-frozen implementation candidate; not a release review
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; role ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review. The engineering override remains scoped to implementation only.
- Timestamp: `2026-09-14T17:14:52+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:01:46`
- Token use: active runtime goal reported `46423` tokens before receipt write

This receipt is an immutable implementation review of the generic local
bootstrap extension only. It is not runtime acceptance, reconstruction
acceptance, publication acceptance, release approval, or authority to run the
real Dissociation source.

## Scope

Reviewed:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_20260914.md`
- `MinerU/requirements.bootstrap.lock.txt`
- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/setup.ps1`
- `MinerU/README.md`
- bootstrap-focused additions in `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`

Forbidden scope was honored: no dependency installation, no download, no real
`.tools` mutation, no real source run, no remote/API execution, no commit, no
canonical plan/context/status/release edit, and no implementation edit. This
receipt is the only file written.

## Positive evidence

- Bootstrap lock is exact and narrow: `requirements.bootstrap.lock.txt`
  contains only `uv==0.12.13`; the focused test parses it as
  `{"uv": "0.12.13"}`.
- Bootstrap topology is repository-local. `Get-MinerUBootstrapDefinition`
  places uv under `.tools/uv/bootstrap-uv-0.12.13`, uv cache under
  `.tools/uv/cache`, uv pip cache under `.tools/uv/pip-cache`, CPython under
  `.tools/python`, and the Python receipt at
  `.tools/python/cpython-3.12.14-windows-x86_64.receipt.json`.
- `Get-MinerUProfileRoots` rejects `ToolRoot` outside repository `.tools`, and
  `Remove-ContainedTree` refuses to remove its base root. Force deletion is
  limited to the fixed uv bootstrap directory and
  `cpython-3.12.14-windows-x86_64*` payload directories plus the exact Python
  receipt.
- External bootstrap Python is constrained to 64-bit CPython 3.10 through
  3.13 and is used only for `& $externalPython -m venv $bootstrap.UvVenv`.
  `setup.ps1` creates MinerU profile venvs only via `$managedPython`; it does
  not use `$BootstrapPythonPath` as a profile base.
- Managed Python validation requires CPython `3.12.14` x64, exact executable
  identity, containment under `.tools/python`, a sealed Python receipt, and a
  linked uv receipt/executable identity.
- Existing CPU-first/provider-local behavior is preserved. `setup.ps1` still
  installs `pipeline-cpu-v1` before the hardware probe, requires
  `pipeline_cpu` ready, and does not contain global setup `SKIPPED` behavior.
- Model identity did not regress: a read-only audit reported 40/40 pipeline
  model manifest rows matching exact bytes and SHA-256.
- The sealed historical `20260914-no-cuda-skip-01` run was inspected only for
  file metadata and was not mutated.

## Verification

Focused tests were reproduced with the assigned existing harness:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result:

```text
44 passed in 4.51s
```

PowerShell parser checks:

```powershell
[System.Management.Automation.Language.Parser]::ParseFile(...) for:
  MinerU/scripts/bootstrap-python.ps1
  MinerU/scripts/profile-common.ps1
  MinerU/scripts/setup.ps1
```

Result:

```text
MinerU/scripts/bootstrap-python.ps1 parse PASS
MinerU/scripts/profile-common.ps1 parse PASS
MinerU/scripts/setup.ps1 parse PASS
```

Scoped diff check:

```powershell
git diff --check -- `
  MinerU/requirements.bootstrap.lock.txt `
  MinerU/scripts/bootstrap-python.ps1 `
  MinerU/scripts/profile-common.ps1 `
  MinerU/scripts/setup.ps1 `
  MinerU/README.md `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: PASS; Git emitted only the existing Windows line-ending advisory for
`MinerU/scripts/setup.ps1`.

Adversarial output-stream check, in memory only:

```powershell
$captured = & {
  Write-Output 'native installer stdout'
  Write-Host 'host-only status'
  Write-Output 'C:\_Hobby\_work\NRI\.tools\python\cpython-3.12.14-windows-x86_64\python.exe'
}
$captured.GetType().FullName
@($captured).Count
```

Result:

```text
System.Object[]
2
```

This demonstrates the PowerShell capture hazard described in P1-1 below:
`Write-Host` is not captured, but native/stdout success output plus the final
path is captured as multiple records.

## Findings

### P0

None.

### P1

1. `setup.ps1` can capture a contaminated bootstrap result instead of a single
   managed Python path.

   `setup.ps1` assigns:

   ```powershell
   $managedPython = & (Join-Path $PSScriptRoot "bootstrap-python.ps1") @bootstrapArguments
   ```

   But `bootstrap-python.ps1` allows native command stdout from the live
   install path to flow through the success stream before its final
   `Write-Output $managedPython`. In particular, the script invokes
   `& $bootstrap.UvPython -m pip install ...` and
   `& $bootstrap.UvExe python install $bootstrap.PythonVersion` without
   redirecting or capturing stdout. If either command emits ordinary stdout,
   PowerShell captures an array rather than one executable path. The focused
   tests do not exercise this contract; they only assert static string
   presence. This blocks approval to run live bootstrap from `setup.ps1`
   because the first live run can install/bootstrap state and then fail or pass
   a malformed `$managedPython` into later profile creation.

2. The uv bootstrap receipt validation does not revalidate the pip report file
   identity that the receipt records.

   `Assert-UvBootstrapReceipt` checks receipt seal, top-level shape, uv
   version, lock identity, uv executable identity, runtime `uv --version`, and
   non-empty artifact provenance. It records `pip_report` in the receipt, but
   does not compare the current `pip-install-report.json` bytes/SHA-256 to
   `receipt.pip_report`. A tampered or missing pip report can therefore remain
   undetected as long as the sealed receipt and uv executable still match. This
   falls short of the assigned requirement that receipts validate
   file/report/provenance/seals.

### P2

1. Bootstrap validation checks top-level uv/Python receipt shapes but does not
   fully validate nested object keys and types for `bootstrap_python`,
   `artifact_provenance`, or the Python receipt `install` object. The current
   checks cover the critical executable/version/linkage identities, so this is
   a hardening issue rather than the blocker above.

2. Existing README examples still include legacy `D:\NRI` paths for
   `run-hybrid.ps1`. They are outside the new bootstrap section and appear
   pre-existing, but the generic bootstrap documentation itself correctly uses
   relative paths and `<NRI>` placeholders.

## Blockers

- P1 output-stream capture must be fixed and tested with a mock or harness that
  proves `setup.ps1` receives exactly one managed Python path even when
  bootstrap child commands emit stdout.
- P1 uv bootstrap receipt validation must verify the current pip report file
  identity against the sealed receipt.

## Recommendation

Changes requested. Do not run live bootstrap yet.

The design is otherwise aligned: the bootstrap is pinned to uv `0.12.13`,
targets CPython `3.12.14` x64 under repository `.tools`, keeps external Python
out of production profile venvs, preserves CPU-first/provider-local semantics,
and avoids global skip regression. The two P1 evidence/control issues sit on
the live setup boundary and should be remediated and independently re-reviewed
before the orchestrator authorizes a live bootstrap run.
