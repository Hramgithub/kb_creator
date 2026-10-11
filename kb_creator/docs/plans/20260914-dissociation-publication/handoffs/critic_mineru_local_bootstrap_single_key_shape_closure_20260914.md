# Independent critic closure: MinerU single-key receipt-shape remediation

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-local-bootstrap-single-key-shape-remediation`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T18:20:15.4389786+03:00
- Elapsed time before receipt write: about 1 minute 9 seconds
- Token use before receipt write: 54,270

## Files and evidence inspected

- Handoff:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_single_key_shape_remediation_20260914.md`
- Implementation:
  - `MinerU/scripts/profile-common.ps1`
  - `MinerU/scripts/bootstrap-python.ps1`
- Tests:
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`

I did not install/download dependencies, delete/recreate bootstrap state, run real source/Dissociation, use remote/API/GPU hosts, commit, edit implementation, or inspect/mutate actual live receipts/bootstrap/profile state. The only `.tools` use was the existing pytest harness execution required by the assignment.

## Commands reproduced

```powershell
Get-Content -Raw 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_single_key_shape_remediation_20260914.md'
```

Result: engineering reported that `Assert-MinerUExactObjectShape` now preserves zero/one/many key cardinality by wrapping the full conditional enumeration in `@(...)`, and that uv receipt shape validation was extracted while retaining runtime seal/file/RECORD/provenance checks.

```powershell
rg -n "Assert-MinerUExactObjectShape|PSCustomObject|OrderedDictionary|IDictionary|psobject|Properties|single-key|archive_hashes|receipt_sha256|uv_executables|artifact_provenance|record|RECORD|provenance|seal|if \(|-or|-and|throw" MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: located the exact-shape helper, extracted uv receipt shape helper, bootstrap validator delegation, dynamic cardinality test, and runtime validation chain.

```powershell
$lines=Get-Content 'MinerU/scripts/profile-common.ps1'
foreach($r in @(@(169,190),@(337,410),@(420,435),@(560,685))){
  for($i=$r[0];$i -le $r[1];$i++){
    if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
  }
}
```

Result:

- `Assert-MinerUExactObjectShape` wraps the complete conditional dictionary/property enumeration in `$actual = @(...)`.
- Dictionary keys and PSCustomObject property names are explicitly stringified.
- `Assert-MinerUUvReceiptShape` validates the full nested uv receipt schema, including one-key `archive_hashes`.
- Receipt construction still emits `uv_executables` via `Get-MinerUUvExecutableEvidence` and `archive_hashes = [ordered]@{ sha256 = ... }`.
- Recovery writes `Write-MinerUJsonAtomic -Path $Bootstrap.UvReceipt` only after validation and receipt construction.
- Managed-Python validation still checks linked uv receipt file identity, seal/version, and `Assert-MinerUUvExecutableReceiptSet`.

```powershell
$lines=Get-Content 'MinerU/scripts/bootstrap-python.ps1'
for($i=39;$i -le 88;$i++){
  if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
}
```

Result:

- `Assert-UvBootstrapReceipt` now calls `Assert-MinerUUvReceiptShape -Value $receipt`.
- It then performs runtime/current-state checks: uv executable receipt set, receipt seal, lock file identity, pip report identity, pip report pinned uv row, provenance match, uv version, and Windows x64 wheel suffix.

```powershell
$lines=Get-Content 'kb_creator/tests/test_mineru_cpu_profile_packet_a.py'
for($i=790;$i -le 835;$i++){
  if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
}
```

Result: dynamic PowerShell test covers PSCustomObject and ordered-dictionary exact one-key success, zero-key rejection, multi-key rejection, and realistic uv receipt shape acceptance with `archive_hashes = { sha256 = ... }`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `68 passed in 22.65s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "exact_shape or recovery" -vv
```

Result: `18 passed, 30 deselected in 13.84s`; selected tests included the exact-shape cardinality/realistic uv receipt shape test plus all recovery temp cases.

```powershell
$files=@('MinerU/scripts/profile-common.ps1','MinerU/scripts/bootstrap-python.ps1')
foreach($file in $files){
  $tokens=$null; $errors=$null
  [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $file), [ref]$tokens, [ref]$errors) | Out-Null
  if($errors.Count -gt 0){ Write-Output "$file parse FAIL"; $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }
  else { Write-Output "$file parse PASS" }
}
```

Result:

- `MinerU/scripts/profile-common.ps1 parse PASS`
- `MinerU/scripts/bootstrap-python.ps1 parse PASS`

```powershell
git diff --check -- MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: exit 0.

```powershell
Select-String -Path 'MinerU/scripts/profile-common.ps1','MinerU/scripts/bootstrap-python.ps1' -SimpleMatch -Pattern '$actual = @(','Assert-MinerUUvReceiptShape -Value $receipt','Assert-MinerUUvExecutableReceiptSet -Bootstrap $bootstrap -Value $receipt.uv_executables','Assert-MinerUReceiptSeal -Value $receipt','$recordRelativePath = [System.IO.Path]::GetRelativePath','Write-MinerUJsonAtomic -Path $Bootstrap.UvReceipt','artifact_provenance','archive_hashes','uv_executables' | ForEach-Object { '{0}:{1}: {2}' -f $_.Path,$_.LineNumber,$_.Line }
```

Result: confirmed full conditional array preservation, extracted receipt shape validation, uv executable set validation, receipt seal validation, RECORD path derivation, atomic uv receipt write, and nested provenance/archive hash fields.

## Closure assessment

- Full conditional array preservation: passed. `$actual = @( if (...) { ... } else { ... } )` prevents scalar collapse for one-key objects.
- PSCustomObject and OrderedDictionary behavior: passed in dynamic test for exact one-key success and zero/many-key rejection.
- Realistic one-key uv receipt shape: passed in dynamic test through `Assert-MinerUUvReceiptShape`.
- Exact nested schema: passed. The extracted helper validates top-level uv receipt keys, bootstrap Python evidence, artifact provenance, one-key archive hashes, lock/pip report identities, executable triad shape, non-empty strings, lowercase hashes, architecture, and supported bootstrap Python version.
- Runtime seal/file/RECORD/provenance checks unchanged: passed. `Assert-UvBootstrapReceipt` still performs receipt seal, lock identity, pip report identity, pinned uv row, provenance match, uv version, and Windows x64 wheel checks after shape validation.
- uv triad and RECORD validation unchanged: passed. `Assert-MinerUUvExecutableReceiptSet` still compares sealed receipt rows to current RECORD-bound `uv.exe`, `uvw.exe`, and `uvx.exe` identities.
- Managed-Python revalidation unchanged: passed. `Get-MinerUManagedPython` still validates the linked uv receipt file identity/seal/version and re-runs `Assert-MinerUUvExecutableReceiptSet`.
- Fail-before-write semantics: passed. Recovery writes the uv receipt only after recovery validation and receipt construction; targeted recovery tests still reject adversarial cases without receipt.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Blockers and exclusions

- No live install/download/bootstrap was run.
- No actual repository `.tools` receipts/bootstrap/profile state was inspected, repaired, deleted, or otherwise mutated.
- No real source/Dissociation run, remote/API/GPU execution, commit, or implementation edit was performed.

## Recommendation

Go for ordinary setup continuation under orchestrator authorization.

This go decision is scoped to the ordinary setup continuation/revalidation path after the single-key shape remediation. It does not authorize destructive bootstrap recreation, profile recreation, real Dissociation execution, remote/API/GPU execution, or mutation of sealed runs.
