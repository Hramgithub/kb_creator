# Independent critic review: MinerU safe partial-bootstrap recovery

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-local-partial-bootstrap-recovery`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T17:50:33.0086955+03:00
- Elapsed time before receipt write: about 3 minutes 7 seconds
- Token use before receipt write: 60,202

## Files and evidence inspected

- Handoff/spec evidence:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_recovery_20260914.md`
- Implementation and docs:
  - `MinerU/scripts/bootstrap-python.ps1`
  - `MinerU/scripts/profile-common.ps1`
  - `MinerU/scripts/setup.ps1`
  - `MinerU/scripts/initialize.ps1`
  - `MinerU/scripts/verify.ps1`
  - `MinerU/scripts/probe-capability.ps1`
  - `MinerU/scripts/profile_receipt.py`
  - `MinerU/README.md`
- Contracts/tests/regression anchors:
  - `kb_creator/contracts/mineru_provider_capabilities.v1.schema.json`
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`
  - `MinerU/models/manifest.json`

I did not install/download dependencies, run real Dissociation sources, use remote/API/GPU hosts, commit, edit implementation, or read/mutate/delete actual partial `.tools` recovery state. The only `.tools` access was the explicitly assigned existing test harness: `.tools/MinerU/.venv/Scripts/python.exe` and `.tools/python-test-deps`.

## Commands reproduced

```powershell
rg -n "RecoverBootstrap|RecreateBootstrap|Recover-PartialUvBootstrap|BootstrapPythonPath|pyvenv|PIP_NO_INDEX|PYTHONDONTWRITEBYTECODE|reparse|startup|sitecustomize|usercustomize|uv==0\.12\.13|pip check|PowerShell 7|PSVersion|Write-MinerUJsonAtomic|bootstrapOutput|Count -ne 1|Managed Python output|unexpected" MinerU/scripts/bootstrap-python.ps1 MinerU/scripts/profile-common.ps1 MinerU/scripts/setup.ps1 MinerU/README.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: recovery hooks, explicit switch plumbing, mutual exclusion, exact lock/version/report checks, offline env controls, atomic write, and README recovery contract were present.

```powershell
rg -n "def test_.*recover|RecoverBootstrap|recovery|missing report|tampered|wrong uv|wrong venv|base executable|venv command|PowerShell 7|Windows PowerShell" kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: valid fixture, six adversarial fixture cases, explicit switch test, and Windows PowerShell 5.1 rejection test located.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `57 passed in 13.39s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "recovery or RecoverBootstrap" -vv
```

Result: `8 passed, 29 deselected in 5.28s`; selected tests covered:

- `test_explicit_bootstrap_recovery_seals_valid_temp_tree`
- `test_explicit_bootstrap_recovery_rejects_tampering_without_receipt[missing_report]`
- `test_explicit_bootstrap_recovery_rejects_tampering_without_receipt[tampered_report]`
- `test_explicit_bootstrap_recovery_rejects_tampering_without_receipt[uv_version]`
- `test_explicit_bootstrap_recovery_rejects_tampering_without_receipt[pyvenv]`
- `test_explicit_bootstrap_recovery_rejects_tampering_without_receipt[base_executable]`
- `test_explicit_bootstrap_recovery_rejects_tampering_without_receipt[path]`
- `test_recovery_switch_is_explicit_and_named_through_setup`

```powershell
$files=@('MinerU/scripts/bootstrap-python.ps1','MinerU/scripts/profile-common.ps1','MinerU/scripts/setup.ps1','MinerU/scripts/initialize.ps1','MinerU/scripts/verify.ps1','MinerU/scripts/probe-capability.ps1')
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
- `MinerU/scripts/setup.ps1 parse PASS`
- `MinerU/scripts/initialize.ps1 parse PASS`
- `MinerU/scripts/verify.ps1 parse PASS`
- `MinerU/scripts/probe-capability.ps1 parse PASS`

```powershell
git diff --check -- MinerU/scripts/bootstrap-python.ps1 MinerU/scripts/profile-common.ps1 MinerU/scripts/setup.ps1 MinerU/README.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: exit 0; only Git line-ending advisory for `MinerU/scripts/setup.ps1` (`LF will be replaced by CRLF the next time Git touches it`).

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py::test_windows_powershell_51_fails_with_explicit_runtime_floor -vv
```

Result: `1 passed in 1.19s`.

```powershell
$manifest = Get-Content -Raw 'MinerU/models/manifest.json' | ConvertFrom-Json
$files=@($manifest.files)
$pipeline=@($files | Where-Object { $_.path -like 'models/pipeline/*' })
$vlm=@($files | Where-Object { $_.path -like 'models/vlm/*' })
[pscustomobject]@{
  total_files=$files.Count
  pipeline_files=$pipeline.Count
  vlm_files=$vlm.Count
  assembled_vlm_size=$manifest.assembled_vlm.size
  formula_yaml=@($files | Where-Object { $_.path -eq 'models/pipeline/models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M_inference.yml' }).Count
} | ConvertTo-Json -Compress
```

Result: `{"total_files":55,"pipeline_files":40,"vlm_files":15,"assembled_vlm_size":2312126640,"formula_yaml":1}`.

```powershell
$p='kb_creator/Working/Dissociation/_runs/20260914-no-cuda-skip-01'
if(Test-Path -LiteralPath $p){ Get-Item -LiteralPath $p | Select-Object FullName,LastWriteTime | ConvertTo-Json -Compress } else { 'sealed run path absent on this checkout' }
```

Result: `sealed run path absent on this checkout`. I therefore did not inspect or mutate that sealed run in this review.

## Recovery contract assessment

- Explicit-only recovery: passed. `setup.ps1` and `bootstrap-python.ps1` expose `[switch]$RecoverBootstrap`; setup passes it by named splat only when supplied. No automatic recovery branch was found.
- Mutual exclusion with recreate: passed. `bootstrap-python.ps1` throws when `$RecoverBootstrap -and $RecreateBootstrap`.
- Fixed root/no existing receipt gate: passed. `Recover-MinerUUvBootstrap` requires the exact `.tools/uv/bootstrap-uv-0.12.13` root to exist and rejects an existing uv receipt before validation.
- `-BootstrapPythonPath` requirement: passed. Recovery requires a supplied external bootstrap Python path and validates it as 64-bit CPython 3.10 through 3.13.
- External bootstrap Python cannot become production profile base: passed. `setup.ps1` captures exactly one string from `bootstrap-python.ps1`, then independently constrains it under `$bootstrap.PythonRoot` and revalidates it against `Get-MinerUManagedPython`; the external bootstrap path is only recorded in the uv receipt.
- `pyvenv.cfg` linkage: passed. Recovery requires exactly `home`, `include-system-site-packages`, `version`, `executable`, and `command`, and checks they match the supplied external CPython and fixed uv venv path.
- No reparse/startup/unexpected payload: passed. Recovery rejects root and venv reparse points, `sitecustomize.py`, `usercustomize.py`, unexpected `.pth`, unexpected root files, and unexpected files in the uv venv `Scripts` directory.
- Exact uv lock/report/version/inventory: passed. The lock must be the single row `uv==0.12.13`; pip report must contain exactly one uv 0.12.13 install row with HTTPS `win_amd64` wheel provenance and lowercase SHA-256; uv version output must match pinned semantic version; installed distributions are limited to `pip`, `setuptools`, and `uv`, with exactly one uv 0.12.13.
- Offline pip check/restored env: passed. Recovery sets `PIP_NO_INDEX=1` and `PYTHONDONTWRITEBYTECODE=1` for inventory/check and restores prior process values in `finally`.
- Atomic write ordering: passed. `Write-MinerUJsonAtomic -Path $Bootstrap.UvReceipt` occurs only after recovery validations and receipt construction.
- Single output contract: passed. `setup.ps1` requires one non-empty string from `bootstrap-python.ps1`, rejects output contamination, then verifies containment and receipt identity.
- PowerShell 7 floor: passed. `Get-MinerUProfileRoots` throws before using modern .NET path APIs on Windows PowerShell 5.1; targeted test reproduced.
- Narrow force deletion: no regression found. Recovery performs no deletion; recreate deletion remains scoped by `Remove-ContainedTree` containment checks.
- CPU-first/provider-local skip: no regression found. `setup.ps1` still installs/verifies `pipeline-cpu-v1` before hardware probing; GPU/CUDA installation remains optional and provider-scoped.
- VLM method omission: no regression found. `verify.ps1` still omits `--method` for `vlm-engine`.
- Model identity: no regression found in scoped checks. Manifest has 55 total files, with the CPU pipeline subset still 40 rows and formula YAML present exactly once.
- Secret/network/external service path: no recovery-specific external service path found. Profile verification still rejects external LLM config and strips proxy/API env for runtime execution. Bootstrap/profile installation commands still intentionally use package indexes only for live install paths, which this review did not run.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Blockers and exclusions

- No live install/download/bootstrap was run by design.
- Actual partial `.tools` state was not inspected, repaired, deleted, or otherwise touched by design.
- The sealed run path `kb_creator/Working/Dissociation/_runs/20260914-no-cuda-skip-01` is absent in this checkout, so this review can only state that no access or mutation occurred here.
- No remote/API/GPU host validation was performed.

## Recommendation

Go for orchestrator-authorized live recovery retry:

```powershell
.\scripts\setup.ps1 -RecoverBootstrap -BootstrapPythonPath "<same-bootstrap-python.exe>"
```

This approval is scoped to the explicit recovery path only. It does not authorize destructive bootstrap recreation, profile recreation, real Dissociation execution, remote/API/GPU execution, or mutation of sealed runs.
