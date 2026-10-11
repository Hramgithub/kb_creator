# Engineering receipt — MinerU CPU additive repair P1 remediation

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-additive-repair-p1-remediation`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Input review: `critic_mineru_cpu_additive_repair_closure_20260914.md`
- Result: P1 bootstrap/create isolation and P2 provider documentation corrected
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not a live repair, CPU
smoke, reconstruction, publication, independent closure, or release decision.

## P1 correction

`setup.ps1 -RepairProfile` now rejects every bound bootstrap/create/recreate
input before resolving profile state or creating directories:

- `-RecoverBootstrap`;
- `-RecreateBootstrap`;
- `-RecreateManagedPython`;
- `-RecreateProfiles`;
- `-BootstrapPythonPath`.

The check uses bound-parameter presence, so even an explicitly false recreate
switch or an empty bootstrap path cannot silently enter the repair contract.
`-ManagedPythonPath` remains permitted only as an exact path reference to the
already validated, repository-contained, receipted managed CPython. It cannot
create or substitute a runtime.

Before any generic `New-Item`, bootstrap child call, or managed/profile Python
creation, repair mode now requires:

- the existing CPU profile Python and install receipt;
- no CPU verify receipt;
- the existing managed-Python receipt;
- the linked uv bootstrap receipt;
- successful full managed-Python receipt, executable, uv linkage, containment,
  and runtime validation.

The repair branch executes before every profile recreate/venv-create branch.
Its sealed `plan-repair` validation runs with isolated Python before the first
repair directory is created. Runtime/cache directories are created only after
the sealed plan has been written successfully. Optional CUDA installation is
explicitly disabled in repair mode, so no later GPU venv can be created.

## P2 correction

`SETUP.md` now points to
`$repo\.tools\MinerU\capabilities\providers.json` and states the provider-local
contract: `pipeline_cpu` is required and `ready`; absent optional `hybrid_cuda`
and `vlm_cuda` providers are locally `unavailable`, do not invalidate the CPU
provider, and do not turn the whole run into a global `SKIPPED` result.

## Files changed

- `MinerU/scripts/setup.ps1`
- `MinerU/scripts/profile-common.ps1`
- `SETUP.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

No lock, model, MinerU source, `.tools`, sealed-run, canonical goal/status,
critic receipt, unrelated work, or `.codex` configuration was changed. No live
setup/repair, package install/download, deletion, PDF/source, GPU, remote/API,
or commit action was run.

## Verification

- Dynamic temp-copy repair control flow: PASS for all five conflicting inputs;
  every case exited before bootstrap and preserved the complete fixture tree.
- Dynamic missing-prerequisite control flow: PASS for absent CPU profile,
  managed-Python receipt, and uv bootstrap receipt; no directory or bootstrap
  marker was created.
- Dynamic `ManagedPythonPath` test: exact receipted path accepted and distinct
  path rejected.
- Provider-local documentation assertions: PASS.
- PowerShell parser: PASS for `setup.ps1` and `profile-common.ps1`.
- Full focused regression: `95 passed in 26.28s` for
  `test_mineru_cpu_profile_packet_a.py` and
  `test_mineru_three_view_tools.py`.
- Scoped `git diff --check`: PASS; Git emitted only its existing Windows
  LF-to-CRLF advisory for `setup.ps1`.

## Remaining gate

Independent critic closure is required. Only after closure should the
orchestrator authorize the separate live local `setup.ps1 -RepairProfile` and
the required CPU model-load plus `pipeline/txt` and `pipeline/ocr` smoke.
