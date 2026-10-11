# Independent critic closure: MinerU sealed JSON date remediation

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-local-bootstrap-json-date-remediation`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T18:27:27.7786082+03:00
- Elapsed time before receipt write: about 1 minute 12 seconds
- Token use before receipt write: 40,804

## Files and evidence inspected

- Handoff:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_json_date_remediation_20260914.md`
- Implementation/docs:
  - `MinerU/scripts/profile-common.ps1`
  - `MinerU/scripts/bootstrap-python.ps1`
  - `MinerU/README.md`
- Tests:
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`

I did not install/download dependencies, delete/recreate bootstrap state, run real source/Dissociation, use remote/API/GPU hosts, commit, edit implementation, or inspect/mutate actual live receipts/bootstrap/profile state. The only `.tools` use was the existing pytest harness execution required by the assignment.

## Commands reproduced

```powershell
Get-Content -Raw 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_json_date_remediation_20260914.md'
```

Result: engineering reported that sealed PowerShell receipt reads now preserve exact JSON date strings via `ConvertFrom-Json -DateKind String`, fail early when unavailable, and leave seal canonicalization unchanged.

```powershell
rg -n "Read-MinerUJsonPreservingStrings|ConvertFrom-Json|DateKind|checked_at_utc|receipt_sha256|Assert-MinerUReceiptSeal|Get-MinerUObjectSeal|PowerShell 7\\.5|PSVersion|Windows PowerShell|sealed|json date|JsonDate|Unsupported|Assert-UvBootstrapReceipt|Get-MinerUManagedPython" MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 MinerU/README.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: located the strict JSON parser guard/helper, sealed receipt read sites, ordinary JSON read sites, README runtime floor, and dynamic tests.

```powershell
$lines=Get-Content 'MinerU/scripts/profile-common.ps1'
foreach($r in @(@(1,42),@(380,425),@(586,700))){
  for($i=$r[0];$i -le $r[1];$i++){
    if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
  }
}
```

Result:

- `Get-MinerUProfileRoots` calls `Assert-MinerUJsonDateStringSupport` before resolving repository `.tools` roots.
- `Assert-MinerUJsonDateStringSupport` requires PowerShell `7.5` or newer and feature-detects the `DateKind` parameter.
- `ConvertFrom-MinerUStrictJson` uses `ConvertFrom-Json -DateKind String`.
- `Assert-MinerUUvReceiptShape` still requires string-typed `checked_at_utc` via `Assert-MinerUNonEmptyString`.
- `Get-MinerUObjectSeal` still removes `receipt_sha256` and canonicalizes with `ConvertTo-Json -Depth 16 -Compress`.
- `Get-MinerUManagedPython` reads both sealed managed-Python and linked uv receipts with `Read-MinerUStrictJson`.

```powershell
$lines=Get-Content 'MinerU/scripts/bootstrap-python.ps1'
for($i=39;$i -le 88;$i++){
  if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
}
```

Result:

- `Assert-UvBootstrapReceipt` reads the sealed uv receipt with `Read-MinerUStrictJson`.
- Runtime validation still checks uv receipt shape, executable set, seal, lock identity, pip report identity, pinned uv row, provenance, uv version, and Windows x64 wheel suffix.
- The pip report remains ordinary JSON via `ConvertFrom-Json`, as expected for a non-sealed data path.

```powershell
$lines=Get-Content 'kb_creator/tests/test_mineru_cpu_profile_packet_a.py'
foreach($r in @(@(770,800),@(796,890))){
  for($i=$r[0];$i -le $r[1];$i++){
    if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
  }
}
```

Result: dynamic test coverage includes Windows PowerShell 5.1 early failure, unsupported `DateKind` metadata rejection, strict JSON roundtrip preserving `checked_at_utc` as `System.String`, exact date value preservation, receipt seal validation, and realistic one-key `archive_hashes` shape validation.

```powershell
$lines=Get-Content 'MinerU/README.md'
for($i=30;$i -le 40;$i++){
  if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
}
```

Result: README documents Windows 11 x86-64, PowerShell 7.5+ with `ConvertFrom-Json -DateKind String`, and explains older PowerShell including 5.1 is unsupported because sealed receipts must avoid automatic ISO date conversion.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `68 passed in 22.08s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "exact_shape or windows_powershell or date or recovery" -vv
```

Result: `19 passed, 29 deselected in 14.10s`; selected tests included:

- strict JSON date/seal roundtrip with `checked_at_utc` type `System.String`;
- exact `checked_at_utc` value `2026-09-14T00:00:00Z`;
- receipt seal validation after strict parse;
- unsupported parser capability rejection;
- Windows PowerShell 5.1 early failure;
- exact-shape and all recovery temp cases.

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
git diff --check -- MinerU/scripts/profile-common.ps1 MinerU/scripts/bootstrap-python.ps1 MinerU/README.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: exit 0.

```powershell
Select-String -Path 'MinerU/scripts/profile-common.ps1','MinerU/scripts/bootstrap-python.ps1' -SimpleMatch -Pattern 'Assert-MinerUJsonDateStringSupport','ConvertFrom-Json -DateKind String','Read-MinerUStrictJson -Path $Bootstrap.PythonReceipt','Read-MinerUStrictJson -Path $Bootstrap.UvReceipt','Read-MinerUStrictJson -Path $bootstrap.UvReceipt','Get-Content -Raw -LiteralPath $bootstrap.UvPipReport | ConvertFrom-Json','Get-Content -Raw -LiteralPath $Bootstrap.UvPipReport | ConvertFrom-Json','ConvertTo-Json -Depth 16 -Compress','receipt_sha256','Assert-MinerUReceiptSeal -Value $receipt','Assert-MinerUReceiptSeal -Value $uvReceipt' | ForEach-Object { '{0}:{1}: {2}' -f $_.Path,$_.LineNumber,$_.Line }
```

Result:

- strict parser support guard is present;
- strict parser uses `ConvertFrom-Json -DateKind String`;
- sealed uv and managed-Python receipt reads use `Read-MinerUStrictJson`;
- pip report reads remain ordinary `ConvertFrom-Json`;
- seal canonicalization remains `ConvertTo-Json -Depth 16 -Compress` after excluding `receipt_sha256`;
- receipt seal validation remains in both bootstrap and managed-Python validation.

## Closure assessment

- Sealed receipt date preservation: passed. Reproduced dynamic test proves `checked_at_utc` survives JSON roundtrip as `System.String` with exact value `2026-09-14T00:00:00Z`.
- Unsupported `DateKind` capability rejection: passed. Dynamic test injects command metadata without `DateKind` and verifies rejection.
- Windows PowerShell 5.1 early failure: passed. Dynamic test verifies the explicit 7.5+/`DateKind` failure message.
- PowerShell 7.5+ floor explicit: passed. `Assert-MinerUJsonDateStringSupport` enforces `[Version]"7.5"` and README documents the floor.
- Strict parser scope: passed. Sealed uv and managed-Python receipt reads use `Read-MinerUStrictJson`; ordinary pip report, inventory, and bootstrap identity JSON reads remain ordinary data paths.
- Seal canonicalization unchanged: passed. `Get-MinerUObjectSeal` still excludes `receipt_sha256` and canonicalizes using compact JSON at depth 16.
- Runtime seal/file/RECORD/provenance checks unchanged: passed. `Assert-UvBootstrapReceipt` still performs shape, executable set, seal, lock identity, pip report identity, pinned uv row, provenance, uv version, and Windows x64 wheel validation.
- Prior recovery validations unchanged: passed through the targeted recovery subset.

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

This go decision is scoped to the ordinary setup continuation/revalidation path after the sealed JSON date remediation. It does not authorize destructive bootstrap recreation, profile recreation, real Dissociation execution, remote/API/GPU execution, or mutation of sealed runs.
