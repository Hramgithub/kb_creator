# Independent critic closure: MinerU CPU additive profile repair

- Goal: `20260914-dissociation-publication`
- Packet/step reviewed: `4-mineru-cpu-additive-profile-repair`
- Review kind: implementation
- Candidate state: non-frozen implementation candidate
- Reviewer role: independent critic only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Requested critic policy role: `gpt-5.5` at `medium`
- Actual assignment state: platform/model identity not independently attestable from inside this worker; reviewed under assigned independent critic scope
- Scoped override: none
- Timestamp: 2026-09-14T18:59:54.8218179+03:00
- Elapsed time before receipt write: about 2 minutes 40 seconds
- Token use before receipt write: 83,644

## Files and evidence inspected

- Handoff:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_additive_repair_20260914.md`
- Implementation/docs:
  - `MinerU/requirements.windows-cpu-pipeline.lock.txt`
  - `MinerU/scripts/setup.ps1`
  - `MinerU/scripts/profile-common.ps1`
  - `MinerU/scripts/profile_receipt.py`
  - `MinerU/README.md`
  - `SETUP.md`
- Tests:
  - `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
  - `kb_creator/tests/test_mineru_three_view_tools.py`

I did not install/download dependencies, delete/recreate bootstrap state, run real PDF/source/Dissociation, use remote/API/GPU hosts, commit, edit implementation, or inspect/mutate actual live receipts/bootstrap/profile state. I executed the existing repository pytest harness to reproduce tests; no live setup/repair command was run.

## Commands reproduced

```powershell
rg -n "MinerU|additive|repair|cpu|20260914-dissociation-publication|Dissociation" 'C:\Users\user\.codex\memories\MEMORY.md'
```

Result: no relevant memory hits; review proceeded from repository evidence.

```powershell
Get-Content -Raw 'kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_additive_repair_20260914.md'
```

Result: engineering claimed a CPU-only explicit additive repair for an existing unverified CPU profile, with exact `six==1.17.0` lock addition, sealed pre-mutation plan, `--no-deps` delta install, deterministic pip report merge, receipt regeneration, and fail-closed behavior.

```powershell
Get-Content 'MinerU/requirements.windows-cpu-pipeline.lock.txt' | Select-Object -First 30
Select-String -Path 'MinerU/requirements.windows-cpu-pipeline.lock.txt' -Pattern '^six==|torch==|torchvision==|nvidia|cuda|lmdeploy|triton|vllm|mlx-vlm|torchaudio'
```

Result:

- `six==1.17.0` appears exactly once.
- CPU lock retains `torch==2.8.0+cpu` and `torchvision==0.23.0+cpu`.
- No CUDA/NVIDIA/lmdeploy/triton/vllm/mlx-vlm/torchaudio lock rows matched.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -c "from pathlib import Path; import importlib.util; spec=importlib.util.spec_from_file_location('h', Path('MinerU/scripts/profile_receipt.py')); h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h); lock=h.parse_lock(Path('MinerU/requirements.windows-cpu-pipeline.lock.txt')); print({'entries': len(lock), 'six': lock.get('six'), 'forbidden': sorted(h.CPU_FORBIDDEN & set(lock)), 'cuda_like': sorted(n for n in lock if 'cuda' in n.lower() or n.lower().startswith('nvidia-'))})"
```

Result: `{'entries': 86, 'six': '1.17.0', 'forbidden': [], 'cuda_like': []}`.

```powershell
$lines=Get-Content 'MinerU/scripts/setup.ps1'
foreach($r in @(@(1,65),@(66,130),@(131,175))){
  for($i=$r[0];$i -le $r[1];$i++){
    if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
  }
}
```

Result: inspected repair parameter plumbing, preflight, `Repair-MinerUProfileAdditively`, `Install-MinerUProfile`, and CPU-first setup flow.

```powershell
$lines=Get-Content 'MinerU/scripts/profile_receipt.py'
foreach($r in @(@(1,80),@(80,145),@(357,430),@(430,490),@(501,660),@(820,850))){
  for($i=$r[0];$i -le $r[1];$i++){
    if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
  }
}
```

Result: inspected lock parsing, inventory checks, LF-stable JSON writer, JSON payload identity, install receipt validation, pip report row validation, repair plan validation, additive plan build, deterministic report merge, `plan-repair`, and `finalize-repair`.

```powershell
$lines=Get-Content 'kb_creator/tests/test_mineru_cpu_profile_packet_a.py'
foreach($r in @(@(145,210),@(210,360),@(360,560),@(560,740))){
  for($i=$r[0];$i -le $r[1];$i++){
    if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
  }
}
```

Result: inspected CPU lock assertions, additive repair fixture, happy path, finalize reissue, failure preservation, removed/changed pin rejection, stale/tampered preflight, malformed/duplicate reports, missing/extra/duplicate delta rows, and setup static assertions.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py kb_creator/tests/test_mineru_three_view_tools.py
```

Result: `85 passed in 21.48s`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest kb_creator/tests/test_mineru_cpu_profile_packet_a.py -k "additive or RepairProfile or repair" -vv
```

Result: `17 passed, 48 deselected in 1.04s`. Selected tests covered:

- happy path and single-pin delta;
- finalize reissues exact full provenance and receipt;
- finalize validation failure preserves old artifacts;
- removed or changed pin rejection;
- receipt/inventory/source/verify/malformed-report/duplicate-report preflight attacks;
- missing/extra/duplicate delta report attacks;
- structurally malformed report rejection;
- plan failure preserving existing output;
- explicit fail-closed setup routing.

The engineering receipt claimed `18 passed, 47 deselected`; I reproduced 17 additive-selected tests with the current test names. The full 85-test suite still passed.

```powershell
$files=@('MinerU/scripts/setup.ps1','MinerU/scripts/profile-common.ps1')
foreach($file in $files){
  $tokens=$null; $errors=$null
  [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $file), [ref]$tokens, [ref]$errors) | Out-Null
  if($errors.Count -gt 0){ Write-Output "$file parse FAIL"; $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }
  else { Write-Output "$file parse PASS" }
}
```

Result:

- `MinerU/scripts/setup.ps1 parse PASS`
- `MinerU/scripts/profile-common.ps1 parse PASS`

```powershell
git diff --check -- MinerU/requirements.windows-cpu-pipeline.lock.txt MinerU/scripts/setup.ps1 MinerU/scripts/profile-common.ps1 MinerU/scripts/profile_receipt.py MinerU/README.md SETUP.md kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: exit 0; Git emitted only the line-ending advisory for `MinerU/scripts/setup.ps1`.

```powershell
Select-String -Path 'MinerU/scripts/setup.ps1' -SimpleMatch -Pattern '$RepairProfile -and $RecreateProfiles','$RepairProfile -and $RecoverBootstrap','$RepairProfile -and $RecreateBootstrap','$RepairProfile -and $RecreateManagedPython','if (-not $managedPython)','bootstrap-python.ps1','if ($RepairProfile -and $Profile -eq "pipeline-cpu-v1")'
```

Result:

- line 19 excludes `-RepairProfile` only with `-RecreateProfiles`;
- line 44 still enters the bootstrap child path whenever `$managedPython` is absent;
- line 50 calls `bootstrap-python.ps1`;
- line 146 runs additive repair only inside `Install-MinerUProfile` after earlier managed-Python resolution.

```powershell
$setup=Get-Content -Raw 'MinerU/scripts/setup.ps1'
[pscustomobject]@{
  has_repair_recreateprofiles_exclusion=$setup.Contains('$RepairProfile -and $RecreateProfiles')
  has_repair_recover_exclusion=$setup.Contains('$RepairProfile -and $RecoverBootstrap')
  has_repair_recreatebootstrap_exclusion=$setup.Contains('$RepairProfile -and $RecreateBootstrap')
  has_repair_recreatemanaged_exclusion=$setup.Contains('$RepairProfile -and $RecreateManagedPython')
  has_repair_bootstrappythonpath_exclusion=$setup.Contains('$RepairProfile -and $BootstrapPythonPath')
  bootstrap_branch_excludes_repair=$setup.Contains('if (-not $managedPython -and -not $RepairProfile)')
} | ConvertTo-Json -Compress
```

Result: `{"has_repair_recreateprofiles_exclusion":true,"has_repair_recover_exclusion":false,"has_repair_recreatebootstrap_exclusion":false,"has_repair_recreatemanaged_exclusion":false,"has_repair_bootstrappythonpath_exclusion":false,"bootstrap_branch_excludes_repair":false}`.

```powershell
$lines=Get-Content 'SETUP.md'
for($i=325;$i -le 370;$i++){
  if($i -le $lines.Count){ '{0}: {1}' -f $i,$lines[$i-1] }
}
```

Result: inspected additive repair operator docs and found stale provider/capability wording; see P2.

## Positive findings

- CPU lock remains CPU-only in inspected evidence: exact `six==1.17.0`, CPU torch/torchvision, no GPU-only packages matched.
- `profile_receipt.py` validates install receipt seal, receipt identity, actual inventory, profile Python identity, source identity, existing pip report identity, old report rows, additive-only lock delta, and canonical names before emitting a sealed plan.
- `plan-repair` writes the plan only after validation; tested plan failure preserved existing output.
- `setup.ps1` installs planned additions with literal `--no-deps` and `--report $deltaReport @pins`, then runs `pip check`.
- `finalize-repair` revalidates sealed plan, verify receipt absence, old install receipt identity, old pip report identity, lock identity/content, current inventory, and source identity before merge/publication.
- `merge_pip_reports` validates old and delta rows, rejects missing/extra/duplicate/mismatched rows, requires matching report metadata, and outputs deterministic distribution-name order.
- `write_json` uses `newline="\n"` and temp-file replacement, supporting LF-stable identity on Windows.
- No GPU/profile source/model mutation path was found inside additive repair itself.

## Findings

### P0

None.

### P1

1. `-RepairProfile` is not isolated from bootstrap/create/recreate controls, violating the explicit repair contract.

   Evidence:

   - `setup.ps1` only rejects `-RepairProfile` combined with `-RecreateProfiles`.
   - There is no rejection for `-RepairProfile` combined with `-RecoverBootstrap`, `-RecreateBootstrap`, `-RecreateManagedPython`, or `-BootstrapPythonPath`.
   - Before repair runs, `setup.ps1` still executes the generic managed-Python resolution branch:
     - `if (-not $managedPython) { ... bootstrap-python.ps1 ... }`
   - Static check result:
     `has_repair_recover_exclusion=false`,
     `has_repair_recreatebootstrap_exclusion=false`,
     `has_repair_recreatemanaged_exclusion=false`,
     `has_repair_bootstrappythonpath_exclusion=false`,
     `bootstrap_branch_excludes_repair=false`.

   Impact:

   - The packet requirement says repair must be explicit, CPU-only, and no bootstrap/create/recreate.
   - As written, a repair invocation can be combined with bootstrap/recreate flags, and even a plain `-RepairProfile` can enter the bootstrap child path before additive repair if managed-Python resolution is absent/invalid.
   - This is fail-closed in some states, but it is not the promised isolated repair primitive and could broaden live command side effects beyond additive CPU repair.

   Required remediation:

   - In `-RepairProfile` mode, reject all bootstrap/recreate inputs (`-RecoverBootstrap`, `-RecreateBootstrap`, `-RecreateManagedPython`, `-BootstrapPythonPath`) unless a future spec explicitly permits one.
   - Ensure `-RepairProfile` does not call `bootstrap-python.ps1`, create/recreate managed Python, or depend on managed-Python bootstrap resolution before repair. It should operate only on the existing contained CPU profile Python after the install-receipt/no-verify-receipt gate.
   - Add tests for forbidden flag combinations and for no bootstrap child invocation in repair mode.

### P2

1. `SETUP.md` still contains stale pre-Packet-A capability wording.

   Evidence:

   - `SETUP.md` lines 341--343 say the probe writes `$repo\.tools\MinerU\capability.json` and a host without NVIDIA records GPU enrichment as `SKIPPED`.
   - Current implementation/tests use provider-scoped `$repo\.tools\MinerU\capabilities\providers.json`, optional providers as `unavailable`, and explicit no global `SKIPPED` setup/verify behavior.

   Impact:

   - This does not directly change additive repair execution, so it is not a live repair blocker by itself.
   - It can mislead future operators/reviewers and should be cleaned before release or durable setup-doc reliance.

## Blockers and exclusions

- No live `setup.ps1 -RepairProfile` was run.
- No actual repository `.tools` receipts/bootstrap/profile state was inspected, repaired, deleted, or otherwise mutated.
- No package install/download, real PDF/source/Dissociation run, remote/API/GPU execution, commit, or implementation edit was performed.
- Because the CPU lock file is untracked in this checkout, I could not use `git diff` against HEAD to independently prove the historical lock delta. I verified the current lock contains exact `six==1.17.0`, remains CPU-only, and the repair planner enforces strict additive deltas from the sealed old receipt/inventory at runtime.

## Recommendation

No-go for generic live local:

```powershell
.\scripts\setup.ps1 -RepairProfile
```

The additive plan/finalize machinery is strong, and the reproduced tests pass, but live repair should wait until `-RepairProfile` is isolated from bootstrap/create/recreate flows. A later closure review should rerun the full focused suite plus explicit forbidden-combination/no-bootstrap-in-repair tests.
