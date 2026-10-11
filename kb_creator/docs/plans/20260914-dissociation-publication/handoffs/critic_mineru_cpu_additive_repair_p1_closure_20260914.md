# Independent critic closure: MinerU CPU additive repair P1/P2 remediation

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-cpu-additive-profile-repair-p1-remediation`
- Review kind: implementation
- Candidate state: non-frozen implementation remediation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Prior no-go reviewed: `critic_mineru_cpu_additive_repair_closure_20260914.md`
- Engineering remediation receipt reviewed: `engineer_mineru_cpu_additive_repair_p1_remediation_20260914.md`
- Timestamp: 2026-09-14T19:13:48.3224959+03:00
- Elapsed time before receipt write: about 2 minutes 7 seconds
- Token use before receipt write: 43,012

## Scope and files checked

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_additive_repair_p1_remediation_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_additive_repair_closure_20260914.md`
- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/profile_receipt.py`
- `MinerU/requirements.windows-cpu-pipeline.lock.txt`
- `MinerU/README.md`
- `SETUP.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`

I reviewed only the remediation of the previously reported P1/P2 and the changed scoped files. I did not install or download packages, run live `setup.ps1`, mutate `.tools`, inspect or alter real local receipts/profile state, run real PDF/source/Dissociation, use remote/API/GPU hosts, edit implementation, commit, or touch release/canonical state.

## Commands and evidence reproduced

```powershell
Get-Content -LiteralPath 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_additive_repair_p1_remediation_20260914.md' -Raw
```

Result: engineering claims remediation of the previous P1 by rejecting all bound bootstrap/create/recreate inputs in `-RepairProfile`, validating existing CPU profile plus managed Python/uv receipts before repair, preserving `-ManagedPythonPath` only as an exact receipted reference, running repair before profile creation/recreate paths, and disabling optional CUDA installation in repair mode. It also claims `SETUP.md` now uses provider-local `providers.json` semantics.

```powershell
git diff -- MinerU/scripts/setup.ps1 SETUP.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py MinerU/README.md MinerU/scripts/profile-common.ps1 MinerU/scripts/profile_receipt.py MinerU/requirements.windows-cpu-pipeline.lock.txt
git status --short -- MinerU/scripts/setup.ps1 SETUP.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py MinerU/README.md MinerU/scripts/profile-common.ps1 MinerU/scripts/profile_receipt.py MinerU/requirements.windows-cpu-pipeline.lock.txt kb_creator/docs/plans/20260914-dissociation-publication/handoffs
```

Result: scoped worktree remains non-frozen with implementation changes in the expected files and untracked handoff/test/lock/helper files. I preserved all existing edits.

```powershell
Select-String -Path 'MinerU/scripts/setup.ps1' -Pattern 'RepairProfile|RecoverBootstrap|RecreateBootstrap|RecreateManagedPython|RecreateProfiles|BootstrapPythonPath|ManagedPythonPath|bootstrap-python|Install-MinerUProfile|probe-capability' -Context 0,2
```

Result: `setup.ps1` now has an early `if ($RepairProfile)` conflict gate for `RecoverBootstrap`, `RecreateBootstrap`, `RecreateManagedPython`, `RecreateProfiles`, and `BootstrapPythonPath`; then a repair-only preflight branch before generic directory/bootstrap setup.

```powershell
$setup = Get-Content -LiteralPath 'MinerU/scripts/setup.ps1' -Raw
$result = [ordered]@{
  repair_conflicts_recover = $setup.Contains('"RecoverBootstrap"')
  repair_conflicts_recreate_bootstrap = $setup.Contains('"RecreateBootstrap"')
  repair_conflicts_recreate_managed = $setup.Contains('"RecreateManagedPython"')
  repair_conflicts_recreate_profiles = $setup.Contains('"RecreateProfiles"')
  repair_conflicts_bootstrap_path = $setup.Contains('"BootstrapPythonPath"')
  repair_branch_before_new_item = ($setup.IndexOf('if ($RepairProfile) {') -ge 0 -and $setup.IndexOf('if ($RepairProfile) {') -lt $setup.IndexOf('New-Item -ItemType Directory -Force -Path $roots.ToolRoot'))
  gpu_guard_excludes_repair = $setup.Contains('if (-not $RepairProfile -and $hardware.gpu_state -eq "candidate")')
  repair_uses_bootstrap_child = ($setup.Substring($setup.IndexOf('if ($RepairProfile) {'), [Math]::Min(2500, $setup.Length - $setup.IndexOf('if ($RepairProfile) {'))).Contains('bootstrap-python.ps1'))
  repair_allows_managed_path_check = $setup.Contains('Assert-MinerURequestedManagedPythonPath -ReceiptedPython $managedPython -RequestedPythonPath $ManagedPythonPath')
}
$result | ConvertTo-Json -Compress
```

Result:

```json
{"repair_conflicts_recover":true,"repair_conflicts_recreate_bootstrap":true,"repair_conflicts_recreate_managed":true,"repair_conflicts_recreate_profiles":true,"repair_conflicts_bootstrap_path":true,"repair_branch_before_new_item":true,"gpu_guard_excludes_repair":true,"repair_uses_bootstrap_child":false,"repair_allows_managed_path_check":true}
```

```powershell
$lines = Get-Content -LiteralPath 'MinerU/scripts/setup.ps1'
foreach($range in @(@(17,58),@(95,147),@(208,218))){
  for($i=$range[0];$i -le $range[1];$i++){ '{0}: {1}' -f $i, $lines[$i-1] }
  ''
}
```

Result: manually inspected the exact conflict gate, preflight checks for existing CPU install receipt/profile Python/no verify receipt/managed Python receipt/uv receipt, `Get-MinerUManagedPython`, optional exact `ManagedPythonPath` assertion, sealed `plan-repair`, `--no-deps` delta install, `pip check`, `finalize-repair`, and `if (-not $RepairProfile -and $hardware.gpu_state -eq "candidate")` CUDA guard.

```powershell
$lines = Get-Content -LiteralPath 'MinerU/scripts/profile-common.ps1'
for($i=120;$i -le 145;$i++){ '{0}: {1}' -f $i, $lines[$i-1] }
```

Result: `Assert-MinerURequestedManagedPythonPath` resolves both paths and accepts only exact full-path equality to the already receipted managed Python executable, using ordinal-ignore-case comparison on Windows; any distinct path is rejected.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "repair_setup or provider_local or additive_repair or ManagedPythonPath" -vv
```

Result: `26 passed, 49 deselected in 5.40s`. This reproduced dynamic repair conflict/missing-runtime checks, provider-local documentation assertions, and additive repair adversarial coverage selected by the current test names. The cases included five forbidden bootstrap/create/recreate inputs, missing CPU profile, missing managed-Python receipt, missing uv receipt, and no bootstrap marker/directory mutation in those failure paths.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py::test_managed_python_override_accepts_only_the_exact_receipted_path -vv
```

Result: `1 passed in 0.84s`; the exact receipted path is accepted and a distinct path is rejected.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `95 passed in 26.37s`.

```powershell
$files=@('MinerU/scripts/setup.ps1','MinerU/scripts/profile-common.ps1')
foreach($file in $files){
  $tokens=$null; $errors=$null
  [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $file), [ref]$tokens, [ref]$errors) | Out-Null
  if($errors.Count){ Write-Output "$file parse FAIL"; $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }
  Write-Output "$file parse PASS"
}
```

Result:

- `MinerU/scripts/setup.ps1 parse PASS`
- `MinerU/scripts/profile-common.ps1 parse PASS`

```powershell
git diff --check -- MinerU/scripts/setup.ps1 MinerU/scripts/profile-common.ps1 MinerU/scripts/profile_receipt.py MinerU/README.md SETUP.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py MinerU/requirements.windows-cpu-pipeline.lock.txt
```

Result: exit 0; Git emitted only its Windows line-ending advisory for `MinerU/scripts/setup.ps1`.

```powershell
Select-String -Path 'SETUP.md' -Pattern 'capability.json|SKIPPED|providers.json|pipeline_cpu|hybrid_cuda|vlm_cuda|unavailable' -Context 0,1
```

Result: the relevant MinerU section now points to `$repo\.tools\MinerU\capabilities\providers.json`, states `pipeline_cpu` is required and must be `ready`, marks only optional `hybrid_cuda`/`vlm_cuda` as `unavailable` on no-NVIDIA hosts, and explicitly says this never becomes a global `SKIPPED` result. No stale `capability.json` hit remains in that section.

## Closure assessment against prior findings

### Prior P1: repair not isolated from bootstrap/create/recreate controls

Closed.

Evidence:

- `setup.ps1` rejects bound `-RepairProfile` with `-RecoverBootstrap`, `-RecreateBootstrap`, `-RecreateManagedPython`, `-RecreateProfiles`, or `-BootstrapPythonPath` before profile/root directory creation and before the generic bootstrap branch.
- The repair branch checks for an existing CPU install receipt, existing CPU profile Python, absent verify receipt, existing managed-Python receipt, and existing uv bootstrap receipt.
- The repair branch calls `Get-MinerUManagedPython` and `Assert-MinerUPathContained`; if `-ManagedPythonPath` is supplied, it is only accepted when it resolves to the exact receipted repository-local CPython path.
- The generic bootstrap child call appears only in the non-repair branch. A static substring check of the early repair branch found no `bootstrap-python.ps1`.
- Optional CUDA profile installation is guarded by `if (-not $RepairProfile -and $hardware.gpu_state -eq "candidate")`.
- Dynamic tests confirm conflicting inputs and missing prerequisite states fail without invoking the bootstrap child marker or changing the fixture tree.

Residual note: after successful repair, `setup.ps1` still runs CPU verification and provider probe paths as part of ordinary setup completion. I do not classify that as a defect in the previous P1 because the reviewed prohibition was against bootstrap/create/recreate/CUDA side effects, not against CPU verification/provider receipt publication after a successful repair. The live operator should still expect `-RepairProfile` to perform repair plus the normal CPU verify/provider-ready gate.

### Prior P2: stale provider/capability documentation

Closed.

Evidence:

- `SETUP.md` now documents provider-scoped `$repo\.tools\MinerU\capabilities\providers.json`.
- It states `pipeline_cpu` is required and `ready`.
- It states optional `hybrid_cuda` and `vlm_cuda` are locally `unavailable` on no-NVIDIA hosts and do not invalidate CPU or create a global `SKIPPED`.
- Regression tests include `test_setup_documentation_uses_provider_local_capability_semantics`, reproduced in the focused run.

## Severity findings

### P0

None.

### P1

None.

### P2

None.

## Blockers and exclusions

- No remaining blocker found for the scoped P1/P2 remediation.
- I did not perform the live local repair.
- I did not install/download dependencies, mutate `.tools`, delete/recreate bootstrap/profile state, touch sealed run evidence, run real PDF/source/Dissociation, use remote/API/GPU hosts, edit implementation, or commit.
- This is an implementation closure review for the additive repair remediation only, not a release review and not a final publication acceptance.

## Recommendation

Go for live local additive repair, subject to normal operator controls and separate live-run evidence capture:

```powershell
.\scripts\setup.ps1 -RepairProfile
```

The previous P1/P2 no-go findings are closed by current implementation evidence and reproduced tests. The live command should be treated as a repair-plus-CPU-verification/setup-continuation operation: it must not bootstrap/create/recreate runtimes or install optional CUDA in repair mode, but it is expected to run the CPU verification and provider-ready gates after successful repair.
