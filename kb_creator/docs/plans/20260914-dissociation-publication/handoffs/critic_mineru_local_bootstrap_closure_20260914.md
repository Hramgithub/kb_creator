# Critic receipt — MinerU local bootstrap remediation closure

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-python-bootstrap-remediation-closure-review`
- Review kind: `implementation`
- Candidate state: non-frozen implementation candidate; not a release review
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; role ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review. The engineering override remains scoped to implementation only.
- Timestamp: `2026-09-14T17:24:11+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:01:29`
- Token use: active runtime goal reported `28646` tokens before receipt write

This receipt is an immutable closure review of the bootstrap remediation only.
It is not runtime acceptance, reconstruction acceptance, publication
acceptance, release approval, or authority to run the real Dissociation source.

## Scope

Reviewed only the two P1 and two P2 findings from
`critic_mineru_local_bootstrap_review_20260914.md` and the remediation receipt
`engineer_mineru_local_bootstrap_remediation_20260914.md`.

Files checked:

- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/setup.ps1`
- `MinerU/README.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`

Forbidden scope was honored: no live install, no download, no `.tools`
mutation, no real source run, no remote/API execution, no commit, no canonical
plan/context/status/release edit, and no implementation edit. This receipt is
the only file written.

## Closure evidence

- P1-1, bootstrap success-stream contamination: closed.
  `bootstrap-python.ps1` now routes native executable calls through
  `Invoke-MinerUNativeCaptured`, which returns a single object with `ExitCode`
  and `Lines`. The bootstrap script emits only the final managed Python path
  on success. `setup.ps1` captures bootstrap output as an array and requires
  exactly one non-empty string, then validates that path is contained below
  `.tools/python` and equals the independently receipted managed runtime.
- P1-2, pip report and provenance binding: closed.
  `Assert-UvBootstrapReceipt` now requires the live
  `pip-install-report.json`, checks its bytes and SHA-256 against the sealed
  receipt, selects exactly one `uv` row at version `0.12.13`, derives URL,
  wheel filename and archive SHA-256 from that row, and requires exact match
  with sealed artifact provenance.
- P2-1, nested receipt validation: closed. Shared validators now enforce exact
  object shapes, positive integer byte counts, lowercase SHA-256 strings, and
  non-empty strings. The uv receipt validates nested bootstrap-Python evidence,
  artifact provenance and archive hashes; the managed-Python receipt validates
  uv linkage and exact install evidence.
- P2-2, portable README: closed. The reviewed README no longer contains
  `D:\NRI`, `D:\path`, `C:\_Hobby`, or `C:\Users\user`; examples use `<NRI>`
  and relative paths.
- Force deletion remains narrow. `Remove-ContainedTree` still refuses the base
  root and is used only for `.tools/uv/bootstrap-uv-0.12.13` and
  `cpython-3.12.14-windows-x86_64*` payload directories plus the exact Python
  receipt.
- CPU-first/provider-local setup did not regress. `setup.ps1` still installs
  `pipeline-cpu-v1` before the hardware probe, requires `pipeline_cpu` ready,
  and contains no global setup `SKIPPED` path.
- Model identity did not regress. A read-only audit reported 40/40 pipeline
  model manifest rows matching exact bytes and SHA-256.
- Sealed run safety was preserved. The historical
  `20260914-no-cuda-skip-01` `run.json` and `skip.json` were inspected only
  for metadata and not mutated.

## Reproduced checks

Focused test harness:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result:

```text
46 passed in 5.78s
```

Temporary `.cmd` stdout-contamination test:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py::test_native_capture_helper_contains_mock_stdout_as_data -vv
```

Result:

```text
1 passed in 1.57s
```

PowerShell parser:

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
  MinerU/scripts/bootstrap-python.ps1 `
  MinerU/scripts/profile-common.ps1 `
  MinerU/scripts/setup.ps1 `
  MinerU/README.md `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: PASS; Git emitted only the existing Windows line-ending advisory for
`MinerU/scripts/setup.ps1`.

Static probes confirmed:

- all direct bootstrap native calls are through `Invoke-MinerUNativeCaptured`;
- `setup.ps1` validates single bootstrap output, containment and independent
  managed receipt identity before profile creation;
- pip report existence, bytes/hash, exact uv row and provenance matching are
  enforced;
- README examples are portable.

## Findings

### P0

None.

### P1

None. Both prior P1 findings are closed by implementation and reproduced
tests.

### P2

None. Both prior P2 findings are closed in the reviewed scope.

## Blockers

No implementation-review blocker remains for live local bootstrap/setup.

This approval does not accept runtime evidence in advance. The live run still
must produce the repository-local uv receipt, CPython receipt, CPU profile
install/verify receipts, synthetic MinerU smoke evidence, and provider
capability receipt before any real Dissociation source execution is
considered.

## Recommendation

Go for orchestrator-authorized live bootstrap/setup on the current PC.

Do not run the real Dissociation source from this receipt. This closure
approves only the generic local bootstrap/setup implementation boundary and
the next live bootstrap/setup evidence-gathering step.
