# Independent critic closure: MinerU uv companion remediation

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-local-bootstrap-uv-companion-remediation`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T18:01:11.0605308+03:00
- Elapsed time before receipt write: about 3 minutes
- Token use before receipt write: 94,559

## Files and evidence inspected

- Handoff:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_uv_companions_remediation_20260914.md`
- Implementation:
  - `MinerU/scripts/profile-common.ps1`
  - `MinerU/scripts/bootstrap-python.ps1`
- Tests:
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`

I did not install/download dependencies, delete/recreate bootstrap state, run real source/Dissociation, use remote/API/GPU hosts, commit, edit implementation, or inspect/mutate actual live bootstrap/profile state. The only `.tools` use was the existing pytest harness execution required by the assignment.

## Commands reproduced

```powershell
Get-Content -Raw 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_uv_companions_remediation_20260914.md'
```

Result: engineering claimed the pinned Windows uv wheel installs `uv.exe`, `uvw.exe`, and `uvx.exe`; remediation should require and receipt exactly that ordered triad, with RECORD-bound identity, no extra companion payload, and managed-Python revalidation through the same validator.

```powershell
rg -n "uv.exe|uvw.exe|uvx.exe|companion|RECORD|Record|dist-info|Recover-MinerUUvBootstrap|New-MinerUUvBootstrapReceiptValue|UvCompanion|Scripts|allowedScripts|Write-MinerUJsonAtomic|Assert-UvBootstrapReceipt|uv_executable|uv_companions|receipt|managed" MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: located the companion definitions, RECORD evidence binding, receipt validator, recovery path, bootstrap receipt validator, managed-Python revalidation, and companion temp tests.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `61 passed in 16.49s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "companion or recovery" -vv
```

Result: `12 passed, 29 deselected in 8.31s`; selected tests covered valid recovery, prior tamper cases, missing companion, extra companion, tampered companion, post-receipt companion tamper revalidation, and explicit recovery switch plumbing.

```powershell
$files=@('MinerU/scripts/bootstrap-python.ps1','MinerU/scripts/profile-common.ps1')
foreach($file in $files){
  $tokens=$null; $errors=$null
  [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $file), [ref]$tokens, [ref]$errors) | Out-Null
  if($errors.Count -gt 0){ Write-Output "$file parse FAIL"; $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }
  else { Write-Output "$file parse PASS" }
}
```

Result:

- `MinerU/scripts/bootstrap-python.ps1 parse PASS`
- `MinerU/scripts/profile-common.ps1 parse PASS`

```powershell
git diff --check -- MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: exit 0.

```powershell
git diff -- MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: no tracked diff output because these files are untracked in this checkout; direct content inspection above was used for implementation evidence.

```powershell
rg -n "pip3\.12\.exe|pip3\.13\.exe|3\.10 through 3\.13|Bootstrap Python version|CPython 3\.10|allowedScripts" MinerU/scripts/profile-common.ps1 MinerU/README.md MinerU/scripts/bootstrap-python.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result:

- `MinerU/scripts/bootstrap-python.ps1` accepts `-BootstrapPythonPath` as 64-bit CPython 3.10 through 3.13.
- `MinerU/scripts/profile-common.ps1` accepts bootstrap Python version 3.10 through 3.13.
- `MinerU/README.md` documents any external 64-bit CPython 3.10--3.13.
- `Recover-MinerUUvBootstrap` Scripts allowlist includes `pip3.12.exe` only, not `pip3.10.exe`, `pip3.11.exe`, or `pip3.13.exe`.

Additional temp-only adversarial check:

```powershell
# Created an isolated temp recovery tree with:
# - external bootstrap CPython identity mocked as 3.13.7 x64
# - exact uv.exe/uvw.exe/uvx.exe triad, RECORD-bound
# - standard venv launchers including pip.exe, pip3.exe, pip3.13.exe, pythonw.exe
# - exact uv==0.12.13 lock, valid pip report, valid pyvenv.cfg, valid mocked uv/pip list/pip check
# Then called Recover-MinerUUvBootstrap against that temp tree only.
```

Result:

```text
Unexpected executable/script in the uv venv Scripts directory: pip3.13.exe
```

This temp fixture did not read or mutate repository `.tools`.

```powershell
rg -n "Invoke-MinerUNative.*Uvw|Invoke-MinerUNative.*Uvx|FilePath \$Bootstrap\.UvwExe|FilePath \$Bootstrap\.UvxExe|FilePath \$Bootstrap\.UvExe|uv_executables|Get-MinerUUvExecutableEvidence" MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1
```

Result: no invocation of `uvw.exe` or `uvx.exe` found; companion executables are identity evidence only. `uv.exe` remains the version authority.

## Closure assessment

- Required ordered uv executable set: partial pass. `Get-MinerUUvExecutableDefinitions` returns `uv.exe`, `uvw.exe`, `uvx.exe` in fixed order, and receipt validation requires exactly three rows with `name`, `bytes`, and lowercase SHA-256.
- Companion containment: pass. Each companion path is asserted under the uv bootstrap root before identity evidence is accepted.
- RECORD hash and size binding: pass for the three uv executables. Each row must match `../../../Scripts/<name>`, SHA-256 in RECORD base64url form, and byte size.
- Same receipt builder for normal install and recovery: pass. Both normal install and recovery call `New-MinerUUvBootstrapReceiptValue`, which now includes `uv_executables`.
- Exact nested receipt validation: pass. `Assert-UvBootstrapReceipt` requires `uv_executables`; `Assert-MinerUUvExecutableReceiptSet` validates row shape, order, and current identity.
- Post-receipt/managed-Python revalidation: pass. `Get-MinerUManagedPython` validates the linked uv receipt file identity and seal, then calls `Assert-MinerUUvExecutableReceiptSet`.
- Only `uv.exe` executed: pass. Static scan found no invocation path for `uvw.exe` or `uvx.exe`; tests would throw on unexpected native calls.
- No extras: pass for extra uv companion executable under the official temp tests, but fail for normal CPython-versioned pip launchers outside 3.12; see P1.

## Findings

### P0

None.

### P1

1. Recovery rejects valid CPython 3.13 venv Scripts payload even though CPython 3.13 is accepted and documented.

   Evidence:

   - `bootstrap-python.ps1` and `profile-common.ps1` accept external bootstrap CPython 3.10 through 3.13.
   - `MinerU/README.md` documents any external 64-bit CPython 3.10--3.13 for first bootstrap/recovery.
   - Recovery's closed Scripts allowlist is:
     `activate`, `activate.bat`, `activate.fish`, `Activate.ps1`, `deactivate.bat`, `pip.exe`, `pip3.exe`, `pip3.12.exe`, `python.exe`, `pythonw.exe`, `uv.exe`, `uvw.exe`, `uvx.exe`.
   - A temp-only fixture with otherwise valid CPython 3.13.7 recovery state and standard `pip3.13.exe` failed with:
     `Unexpected executable/script in the uv venv Scripts directory: pip3.13.exe`.

   Impact:

   - This is fail-closed and does not create a false valid receipt, so it is not P0.
   - It can block live recovery for a valid supported bootstrap runtime, especially if the interrupted first bootstrap used CPython 3.13.
   - The official companion tests did not catch this because their valid fixture omits versioned pip launchers other than the uv triad.

   Required remediation:

   - Either make the Scripts allowlist match the supported external CPython range and `pyvenv.cfg` version, for example allowing only the corresponding `pip3.10.exe`/`pip3.11.exe`/`pip3.12.exe`/`pip3.13.exe`, or narrow the supported/documented external recovery/runtime range.
   - Add a temp fixture that includes realistic standard venv launchers for at least CPython 3.13 and rejects mismatched/extra versioned pip launchers.

### P2

None.

## Blockers and exclusions

- No live install/download/bootstrap was run.
- No actual repository `.tools` recovery/profile state was inspected, repaired, deleted, or otherwise mutated.
- No real source/Dissociation run, remote/API/GPU execution, commit, or implementation edit was performed.

## Recommendation

No-go for generic live recovery under the current advertised contract:

```powershell
.\scripts\setup.ps1 -RecoverBootstrap -BootstrapPythonPath "<same-bootstrap-python.exe>"
```

The remediation is close, and it correctly fixed the uv executable triad identity model, but the CPython-versioned pip launcher allowlist must be closed against the documented 3.10--3.13 bootstrap range before approving a generic live recovery retry. A narrower retry may be considered only if the orchestrator has independent evidence that the original bootstrap Python was CPython 3.12 and the live partial venv contains no legitimate versioned pip launcher outside the current allowlist.
