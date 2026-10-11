# Critic receipt — MinerU uv version-output remediation closure

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-local-bootstrap-uv-version-remediation-closure-review`
- Review kind: `implementation`
- Candidate state: non-frozen implementation candidate; not a release review
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; role ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review. The engineering override remains scoped to implementation only.
- Timestamp: `2026-09-14T17:34:07+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:00:44`
- Token use: active runtime goal reported `20108` tokens before receipt write

This receipt is an immutable closure review for uv version-output remediation
only. It is not runtime acceptance, reconstruction acceptance, publication
acceptance, release approval, or authority to run the real Dissociation source.

## Scope

Reviewed:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_local_bootstrap_uv_version_remediation_20260914.md`
- `MinerU/scripts/profile-common.ps1`
- `MinerU/scripts/bootstrap-python.ps1`
- uv-version focused additions in `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`

Regression scope checked:

- `MinerU/scripts/setup.ps1`
- `MinerU/models/manifest.json`
- sealed historical run metadata under
  `kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01`

Forbidden scope was honored: no partial `.tools` state was touched, no
install/download/delete/recreate action was run, no real source was executed,
no remote/API action was used, no implementation edit or commit was performed,
and no canonical plan/context/status/release file was edited. This receipt is
the only file written.

## Closure evidence

- The observed live uv output is accepted:
  `uv 0.12.13 (0ebbd9274 2026-09-10 x86_64-pc-windows-msvc)`.
- The short uv output is still accepted: `uv 0.12.13`.
- The boundary remains fail-closed. `Test-MinerUUvVersionOutput` requires:
  output starts with exact `uv `, version text has exactly three numeric
  components, parsed version equals pinned `0.12.13`, normalized
  `ToString(3)` equals the original token, and optional metadata is exactly one
  anchored parenthetical containing a nine-character lowercase hex commit, a
  valid ISO date, and target `x86_64-pc-windows-msvc`.
- Adversarial rejects are covered and reproduced for wrong version
  `0.12.12`, widened version `0.12.130`, prefixed junk, trailing junk, wrong
  commit length, impossible date, wrong Windows target, and suffix after a
  valid-looking parenthetical.
- Both uv version validation call sites use the shared parser:
  post-install verification and existing-receipt revalidation in
  `bootstrap-python.ps1`.
- Exact pinned semantic version and Windows x64 target remain bound in
  `profile-common.ps1`: `UvVersion = "0.12.13"`, uv root
  `.tools/uv/bootstrap-uv-0.12.13`, and the metadata regex requires
  `x86_64-pc-windows-msvc`.
- Receipt/executable identity gates are unaffected. Existing validation still
  checks uv receipt shape/seal, bootstrap lock, pip report bytes/SHA-256, exact
  uv row/provenance, uv executable bytes/SHA-256, managed Python receipt
  linkage, and tampered uv executable detection.
- Prior bootstrap gates remain intact: native output capture, single-path
  setup output, containment below `.tools/python`, exact receipted managed
  Python identity, narrow recreation, portable README, CPU-first setup, and
  provider-local skip behavior were not changed by this remediation.
- Model identity did not regress: a read-only status probe in this review found
  no `.tools` mutation, and previous same-turn model sanity remained 40/40
  pipeline rows matching exact bytes/SHA-256.
- Sealed historical no-CUDA run safety was preserved. `run.json` and
  `skip.json` were inspected only for metadata and not mutated.

## Reproduced checks

Full focused harness:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result:

```text
48 passed in 8.37s
```

Targeted uv parser test:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py::test_uv_version_parser_accepts_only_pinned_short_or_official_build_output -vv
```

Result:

```text
1 passed in 1.72s
```

PowerShell parser:

```powershell
[System.Management.Automation.Language.Parser]::ParseFile(...) for:
  MinerU/scripts/profile-common.ps1
  MinerU/scripts/bootstrap-python.ps1
```

Result:

```text
MinerU/scripts/profile-common.ps1 parse PASS
MinerU/scripts/bootstrap-python.ps1 parse PASS
```

Scoped diff check:

```powershell
git diff --check -- `
  MinerU/scripts/profile-common.ps1 `
  MinerU/scripts/bootstrap-python.ps1 `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py
```

Result: PASS.

Additional static probes confirmed the shared parser call sites, exact uv
version/root, required Windows x64 metadata target, pip-report/provenance
checks, uv executable identity checks, and that scoped `.tools` status was not
changed by this review.

## Findings

### P0

None.

### P1

None.

### P2

None in the reviewed uv version-output scope.

## Blockers

No implementation-review blocker remains for retrying the live bootstrap/setup
command under the existing orchestrator authorization.

The retry still must produce actual runtime evidence: repository-local uv and
CPython receipts, CPU profile install/verify receipts, synthetic MinerU smoke
evidence, and provider capability receipt. This closure does not authorize or
accept a real Dissociation source run.

## Recommendation

Go for retry of the live bootstrap/setup command on the current PC under the
existing explicit execution authorization.

Do not run the real Dissociation source from this receipt.
