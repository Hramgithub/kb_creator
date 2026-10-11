# Engineering receipt — MinerU repository-local Python bootstrap

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-python-bootstrap`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded for this assignment by the scoped user override)
- Actual requested model/effort: `gpt-5.6-sol`, `high`
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Scoped override: active — user-directed engineering execution with
  `gpt-5.6-sol` at `high`
- Result: bounded bootstrap implementation and focused tests complete; live
  installation remains intentionally unexecuted
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not independent review,
runtime acceptance, reconstruction acceptance, publication acceptance, release
approval, or authority to execute the real source.

## Implemented boundary

`requirements.bootstrap.lock.txt` contains the sole exact bootstrap dependency,
`uv==0.12.13`. `bootstrap-python.ps1` accepts a caller-selected 64-bit CPython
3.10--3.13 only to create the versioned uv environment below
`.tools/uv/bootstrap-uv-0.12.13`. It installs the binary uv wheel with
`--no-deps`, `--only-binary=:all:` and a pip report, then seals identities for
the lock, report, uv executable and downloaded artifact provenance.

The receipted repository-local uv installs CPython `3.12.14` x64 below
`.tools/python`. A second atomic, sealed receipt binds the exact Python
executable to the exact uv installation receipt. Validation checks containment,
receipt shape and seal, file identities, uv provenance linkage, and the live
CPython implementation/version/architecture before returning the production
interpreter.

`setup.ps1` now auto-discovers this receipted runtime. When it is absent, setup
can invoke the bootstrap using `-BootstrapPythonPath`; the external interpreter
is never used as the base of a MinerU profile venv. An explicitly supplied
`-ManagedPythonPath` must exactly match the receipted repository-local runtime.

Partial, unreceipted or tampered bootstrap state fails closed. Explicit repair
switches are narrowly scoped: `-RecreateBootstrap` may remove only the fixed
versioned uv bootstrap directory, while `-RecreateManagedPython` may remove only
the CPython `3.12.14` Windows x64 payload directories and their exact receipt.

## Files changed

- `MinerU/requirements.bootstrap.lock.txt`
- `MinerU/scripts/bootstrap-python.ps1`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/setup.ps1`
- `MinerU/README.md`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- this receipt

No Packet A/P1 provider contract, probe, verification helper, model, existing
profile lock, sealed run, canonical plan/context/status, `.codex` configuration,
or live `.tools` payload was changed by this bounded extension.

## Verification

- PowerShell parser: PASS for `bootstrap-python.ps1`, `profile-common.ps1`, and
  `setup.ps1`.
- Focused pytest: `44 passed in 4.53s` for
  `test_mineru_cpu_profile_packet_a.py` and `test_mineru_three_view_tools.py`.
- Tests cover the single exact uv pin, bootstrap/production interpreter
  separation, repository-local install/cache paths, pip report/provenance,
  atomic sealed receipts, receipt/executable tamper coupling, and narrow force
  semantics.
- Scoped `git diff --check`: PASS; Git emitted only its existing Windows
  line-ending advisory for `setup.ps1`.

No dependency was downloaded or installed, no real MinerU source was run, no
actual `.tools` directory was mutated, and no remote/API/handoff operation was
performed.

## Remaining gate

Independent implementation review is required. A live bootstrap/setup run must
remain a separate, explicitly authorized execution step and must use an
operator-selected external CPython path only for the initial uv bootstrap.
