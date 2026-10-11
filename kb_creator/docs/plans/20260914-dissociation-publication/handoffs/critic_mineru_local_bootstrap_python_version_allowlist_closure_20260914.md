# Independent critic closure: MinerU bootstrap Python-version allowlist remediation

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-local-bootstrap-python-version-allowlist-remediation`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T18:07:23.1497604+03:00
- Elapsed time before receipt write: about 1 minute 51 seconds
- Token use before receipt write: 53,565

## Files and evidence inspected

- Handoff:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_python_version_allowlist_remediation_20260914.md`
- Implementation:
  - `MinerU/scripts/profile-common.ps1`
- Tests:
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`
- Regression context:
  - `MinerU/scripts/bootstrap-python.ps1`
  - `MinerU/README.md`

I did not install/download dependencies, delete/recreate bootstrap state, run real source/Dissociation, use remote/API/GPU hosts, commit, edit implementation, or inspect/mutate actual live bootstrap/profile state. The only `.tools` access was the existing pytest harness execution required by the assignment.

## Commands reproduced

```powershell
Get-Content -Raw 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_python_version_allowlist_remediation_20260914.md'
```

Result: engineering reported that recovery now derives `pip<major>.<minor>.exe` from the validated external CPython version, requires exactly `pip.exe`, `pip3.exe`, and that derived launcher, and rejects mismatched versioned pip launchers.

```powershell
rg -n "Get-MinerUAllowedUvVenvScriptNames|allowedScripts|pip3\.|versioned pip|Bootstrap Python version|3\.10|3\.11|3\.12|3\.13|uv.exe|uvw.exe|uvx.exe|RECORD|Write-MinerUJsonAtomic|Recover-MinerUUvBootstrap" MinerU/scripts/profile-common.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: located the updated version-derived Scripts allowlist, dynamic recovery tests, uv triad/RECORD binding, and fail-before-write recovery path.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `66 passed in 20.81s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "versioned_pip or mismatched_pip_launcher or companion or recovery" -vv
```

Result: `17 passed, 29 deselected in 12.68s`; selected tests included:

- valid recovery with CPython `3.10.14`
- valid recovery with CPython `3.11.9`
- valid recovery with CPython `3.12.14`
- valid recovery with CPython `3.13.7`
- mismatched `pip3.9.exe` rejection before receipt
- missing companion rejection before receipt
- extra companion rejection before receipt
- companion RECORD tamper rejection before receipt
- post-receipt companion tamper revalidation
- prior recovery tamper/fail-before-write cases and explicit switch plumbing

```powershell
$files=@('MinerU/scripts/profile-common.ps1')
foreach($file in $files){
  $tokens=$null; $errors=$null
  [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $file), [ref]$tokens, [ref]$errors) | Out-Null
  if($errors.Count -gt 0){ Write-Output "$file parse FAIL"; $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }
  else { Write-Output "$file parse PASS" }
}
```

Result: `MinerU/scripts/profile-common.ps1 parse PASS`.

```powershell
git diff --check -- MinerU/scripts/profile-common.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: exit 0.

```powershell
rg -n "Invoke-MinerUNative.*Uvw|Invoke-MinerUNative.*Uvx|FilePath \$Bootstrap\.UvwExe|FilePath \$Bootstrap\.UvxExe|FilePath \$Bootstrap\.UvExe|uv_executables|Get-MinerUUvExecutableEvidence" MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1
```

Result: no invocation of `uvw.exe` or `uvx.exe` found; companion executables remain identity evidence only.

```powershell
$bootstrap=Get-Content -Raw 'MinerU/scripts/bootstrap-python.ps1'
$common=Get-Content -Raw 'MinerU/scripts/profile-common.ps1'
[pscustomobject]@{
  bootstrap_atomic_writes=($bootstrap | Select-String -Pattern 'Write-MinerUJsonAtomic' -AllMatches).Matches.Count
  common_atomic_writes=($common | Select-String -Pattern 'Write-MinerUJsonAtomic' -AllMatches).Matches.Count
  uvw_invocations=($common + $bootstrap | Select-String -Pattern 'FilePath \$Bootstrap\.UvwExe|FilePath \$Bootstrap\.UvxExe' -AllMatches).Matches.Count
} | ConvertTo-Json -Compress
```

Result: `{"bootstrap_atomic_writes":2,"common_atomic_writes":2,"uvw_invocations":0}`.

Additional scratch check: I attempted an independently constructed temp-only CPython-version matrix. The mismatched launcher fixture rejected before receipt as expected, but the valid scratch cases failed on my `pyvenv.cfg` construction shape rather than on the remediation logic. I therefore treated the reproduced checked-in dynamic tests above as the authoritative evidence for the required 3.10/3.11/3.12/3.13 valid fixtures.

## Closure assessment

- Exact derived pip launcher set: passed. After external bootstrap identity validation, recovery parses `$externalData.version`, derives `pip<major>.<minor>.exe`, requires exactly `pip.exe`, `pip3.exe`, and the derived launcher, and rejects any other Scripts file case-sensitively.
- Supported 3.10--3.13 bootstrap range: passed in reproduced checked-in dynamic tests for `3.10.14`, `3.11.9`, `3.12.14`, and `3.13.7`.
- Mismatched launcher rejection: passed. The targeted suite rejects `pip3.9.exe` before receipt creation.
- uv triad unchanged: passed. `Get-MinerUUvExecutableDefinitions` remains the ordered set `uv.exe`, `uvw.exe`, `uvx.exe`.
- RECORD hash and size binding unchanged: passed. Each uv executable is still matched to `../../../Scripts/<name>` in `uv-0.12.13.dist-info/RECORD`, with base64url SHA-256 and exact byte size.
- Fail-before-write unchanged: passed. Recovery reaches `Write-MinerUJsonAtomic -Path $Bootstrap.UvReceipt` only after root/receipt, path containment, Scripts allowlist, `pyvenv.cfg`, lock, pip report, uv version, inventory, and offline `pip check` validations.
- Same receipt builder normal/recovery unchanged: passed. Both normal bootstrap and recovery still use `New-MinerUUvBootstrapReceiptValue`.
- Post-receipt/managed-Python revalidation unchanged: passed. `Get-MinerUManagedPython` still validates linked uv receipt identity/seal and calls `Assert-MinerUUvExecutableReceiptSet`.
- Only `uv.exe` executed: passed. No invocation path for `uvw.exe` or `uvx.exe` was found.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Blockers and exclusions

- No live install/download/bootstrap was run.
- No actual repository `.tools` recovery/profile state was inspected, repaired, deleted, or otherwise mutated.
- No real source/Dissociation run, remote/API/GPU execution, commit, or implementation edit was performed.
- One independent scratch fixture attempt produced invalid `pyvenv.cfg` shape for valid cases and was excluded from decision evidence; the checked-in dynamic tests reproduced the requested version matrix successfully.

## Recommendation

Go for orchestrator-authorized live recovery retry:

```powershell
.\scripts\setup.ps1 -RecoverBootstrap -BootstrapPythonPath "<same-bootstrap-python.exe>"
```

This go decision is scoped to the explicit nondestructive recovery path. It does not authorize destructive bootstrap recreation, profile recreation, real Dissociation execution, remote/API/GPU execution, or mutation of sealed runs.
