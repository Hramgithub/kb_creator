# Independent critic closure: MinerU uv RECORD path remediation

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-local-bootstrap-record-path-remediation`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T18:12:53.2886615+03:00
- Elapsed time before receipt write: about 1 minute 8 seconds
- Token use before receipt write: 32,728

## Files and evidence inspected

- Handoff:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_record_path_remediation_20260914.md`
- Implementation:
  - `MinerU/scripts/profile-common.ps1`
- Tests:
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`

I did not install/download dependencies, delete/recreate bootstrap state, run real source/Dissociation, use remote/API/GPU hosts, commit, edit implementation, or inspect/mutate actual live bootstrap/profile state. The only `.tools` access was the existing pytest harness execution required by the assignment.

## Commands reproduced

```powershell
Get-Content -Raw 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_record_path_remediation_20260914.md'
```

Result: engineering reported that uv companion RECORD paths are now derived from actual `site-packages` / `uv-0.12.13.dist-info` geometry instead of hard-coded with an extra parent segment.

```powershell
rg -n "RECORD|recordRelative|RelativePath|GetRelativePath|dist-info|site-packages|Scripts|\\.\\./\\.\\./Scripts|\\.\\./\\.\\./\\.\\./Scripts|wrong.*depth|record_path|record path|uv.exe|uvw.exe|uvx.exe|sha256|bytes|c(e|n)q" MinerU/scripts/profile-common.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: located the `GetRelativePath`-based implementation and tests using realistic `../../Scripts/...` rows plus a wrong-depth `../../../Scripts/...` attack.

```powershell
$lines=Get-Content 'MinerU/scripts/profile-common.ps1'
for($i=295;$i -le 327;$i++){ '{0}: {1}' -f $i,$lines[$i-1] }
```

Result: `Get-MinerUUvExecutableEvidence`:

- discovers exactly one `uv-0.12.13.dist-info` directory under the actual `Lib\site-packages` base;
- derives `$recordBase = Split-Path -Parent $recordRoots[0].FullName`;
- computes `[System.IO.Path]::GetRelativePath($recordBase, $definition.Path).Replace("\", "/")`;
- matches RECORD rows case-sensitively with `-ceq`;
- validates base64url SHA-256 and exact byte size for each uv executable.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `67 passed in 21.11s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "wrong_record_depth or recovery" -vv
```

Result: `17 passed, 30 deselected in 12.22s`; selected tests included:

- realistic RECORD geometry success with `../../Scripts/uv.exe`, `../../Scripts/uvw.exe`, and `../../Scripts/uvx.exe`;
- wrong-depth `../../../Scripts/...` RECORD rejection before receipt creation;
- valid CPython 3.10/3.11/3.12/3.13 recovery;
- uv companion missing/extra/tamper failures;
- mismatched pip launcher failure;
- explicit recovery switch plumbing.

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
Select-String -Path 'MinerU/scripts/profile-common.ps1' -SimpleMatch -Pattern '$recordBase = Split-Path -Parent $recordRoots[0].FullName','[System.IO.Path]::GetRelativePath($recordBase, $definition.Path).Replace("\", "/")','Where-Object { $_.path -ceq $recordRelativePath }','[int64]::TryParse($recordRow[0].size','Write-MinerUJsonAtomic -Path $Bootstrap.UvReceipt','FilePath $Bootstrap.UvwExe','FilePath $Bootstrap.UvxExe' | ForEach-Object { '{0}: {1}' -f $_.LineNumber,$_.Line }
```

Result:

- line 313: record base derived from actual installed dist-info parent;
- line 314: relative path computed from that base and normalized to `/`;
- line 315: case-sensitive RECORD row match;
- line 326: exact parsed byte-size check;
- line 513: uv receipt atomic write remains after recovery validation;
- no `FilePath $Bootstrap.UvwExe` or `FilePath $Bootstrap.UvxExe` hits.

## Closure assessment

- Relative RECORD path geometry: passed. The implementation no longer hard-codes `../../../Scripts`; it derives the path from actual installed `site-packages` geometry and normalizes Windows separators.
- Realistic `../../Scripts` success: passed in reproduced targeted tests.
- Wrong-depth reject: passed in reproduced targeted tests; altered `../../../Scripts/...` rows fail before receipt creation.
- Case/hash/size preservation: passed. RECORD path matching remains case-sensitive, and companion identity remains bound to SHA-256 base64url and exact byte size.
- Ordered uv triad preservation: passed. The companion set remains `uv.exe`, `uvw.exe`, `uvx.exe` in fixed order.
- Containment: passed. Each companion path is still asserted under the uv bootstrap root before RECORD evidence is accepted.
- Fail-before-write preservation: passed. Recovery reaches `Write-MinerUJsonAtomic -Path $Bootstrap.UvReceipt` only after RECORD/path/hash/size and other recovery validations.
- Only `uv.exe` executed: passed. No invocation path for `uvw.exe` or `uvx.exe` was found.
- Python-version allowlist regression: no regression found in reproduced targeted tests; valid CPython 3.10/3.11/3.12/3.13 cases still pass.

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

## Recommendation

Go for orchestrator-authorized live recovery retry:

```powershell
.\scripts\setup.ps1 -RecoverBootstrap -BootstrapPythonPath "<same-bootstrap-python.exe>"
```

This go decision is scoped to the explicit nondestructive recovery path. It does not authorize destructive bootstrap recreation, profile recreation, real Dissociation execution, remote/API/GPU execution, or mutation of sealed runs.
