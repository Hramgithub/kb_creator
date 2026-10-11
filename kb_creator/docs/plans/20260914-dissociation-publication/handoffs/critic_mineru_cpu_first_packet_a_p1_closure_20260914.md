# Critic receipt — MinerU CPU-first Packet A P1 closure review

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `4-mineru-cpu-first-packet-a-p1-closure-review`
- Review kind: `implementation`
- Candidate state: non-frozen implementation candidate; not a release review
- Role: independent critic
- Requested policy role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed the candidate under review: no
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; role ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review. The Packet A engineering override remains scoped to implementation only.
- Timestamp: `2026-09-14T17:01:08+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:01:08`
- Token use: active runtime goal reported `26663` tokens before receipt write

This receipt is an immutable P1 closure review only. It is not runtime
acceptance, reconstruction acceptance, publication acceptance, release approval,
or authority to run the real Dissociation source.

## Scope

Reviewed only the four P1 areas from
`critic_mineru_cpu_first_packet_a_review_20260914.md` and the remediation
receipt `engineer_mineru_cpu_first_packet_a_p1_remediation_20260914.md`.

Changed implementation files checked:

- `kb_creator/contracts/mineru_provider_capabilities.v1.schema.json`
- `MinerU/scripts/profile_receipt.py`
- `MinerU/scripts/probe-capability.ps1`
- `kb_creator/tests/test_mineru_cpu_profile_packet_a.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`

Forbidden scope was honored: no dependency installation, no `.tools` mutation,
no real source run, no remote/API/GPU host, no sealed-run mutation, no Git
index/history operation, and no implementation edit was performed. This
receipt is the only file written.

## Closure evidence

- P1-1, schema state/reason coupling: closed. The provider capability schema
  now uses mutually exclusive `oneOf` branches. CPU `ready` requires
  `verified_cpu_profile` and a verification receipt; CPU `invalid` permits
  only `cpu_profile_not_verified` or `cpu_profile_invalid` with null receipt.
  Optional CUDA `ready`, `unavailable`, and `invalid` likewise have
  state-specific reason sets and receipt requirements. Focused tests reproduce
  the prior cross-product attacks and reject them.
- P1-2, provider-ready trust boundary: closed. `probe-capability.ps1` now calls
  `profile_receipt.py validate-verify` using the profile-local Python before
  it captures `Get-MinerUFileIdentity` for a ready provider. The Python
  validator checks exact top-level receipt shape, internal `receipt_sha256`,
  expected profile/state, versions, model rows against the pinned manifest,
  assembled VLM rules, lock/config/install identities, model-load proof,
  exact smokes, and critical wheel evidence.
- P1-3, exact smoke set before ready receipt: closed.
  `parse_smoke_arguments` now requires exact ordered smoke names per profile:
  CPU `pipeline_txt`, `pipeline_ocr`; CUDA `hybrid_high`, `vlm_local`.
  Missing, duplicate, extra, and reordered CPU smokes are covered by tests.
  Existing receipt validation repeats the exact ordered smoke check.
- P1-4, model-load proof strength: closed. `build_model_load_proof` no longer
  uses `hasattr(model, ...)`. It requires each component object to be non-null
  and to expose the expected callable method: layout/predict, formula/predict,
  OCR/ocr, table classification/predict, table orientation/predict, wired
  table/predict, and wireless table/predict. Tests reject present-but-null
  components and accept usable fake components.
- CPU-first/provider-local skip regression: no regression found. Static tests
  still assert CPU setup precedes hardware probe, `pipeline_cpu` cannot be
  skipped, `providers.json` replaces `capability.json`, and setup/verify do
  not emit global `SKIPPED` language.
- VLM method omission: no regression found. The verified smoke contract keeps
  `vlm_local` as `method: null`, `cli_method_argument: omitted`, and
  `effective_method_scope: not_applicable`; `verify.ps1` still omits
  `--method` for `vlm-engine`.
- Model identity: no regression found. Read-only manifest audit reported 40/40
  pipeline rows matching exact byte count and SHA-256. The formula YAML remains
  `2244564` bytes with SHA-256
  `87b5f3d7f2b2fe553627d77b37f496608ca150ebd0ef62d362591edca47b5538` and
  zero CRLF sequences.
- Sealed run: no mutation found in this review. The historical
  `20260914-no-cuda-skip-01` `run.json` and `skip.json` were inspected only for
  existence/metadata.

## Reproduced tests and checks

Focused test harness:

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -m pytest `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result:

```text
40 passed in 4.53s
```

Additional checks:

```powershell
$tokens=$null; $errors=$null
[System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'MinerU/scripts/probe-capability.ps1'),
  [ref]$tokens,
  [ref]$errors
)
```

Result: `probe-capability.ps1 parse PASS`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools\MinerU\.venv\Scripts\python.exe' -c "import importlib.util; import pathlib; spec=importlib.util.spec_from_file_location('r', pathlib.Path('MinerU/scripts/profile_receipt.py')); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('profiles', m.PROFILE_SMOKES); print('components', m.COMPONENT_METHODS)"
```

Result:

```text
profiles {'mineru-pipeline-cpu-windows-v1': ('pipeline_txt', 'pipeline_ocr'), 'mineru-local-windows-cu128-v1': ('hybrid_high', 'vlm_local')}
components {'layout': ('layout_model', 'predict'), 'formula': ('mfr_model', 'predict'), 'ocr': ('ocr_model', 'ocr'), 'table_classification': ('table_cls_model', 'predict'), 'table_orientation': ('img_orientation_cls_model', 'predict'), 'wired_table': ('wired_table_model', 'predict'), 'wireless_table': ('wireless_table_model', 'predict')}
```

```powershell
rg -n "validate-verify|parse_smoke_arguments|build_model_load_proof|oneOf|verified_cpu_profile|verified_cuda_profile|hasattr\(model|method.*omitted|SKIPPED|capability\.json|http-client|api-url|--url" `
  MinerU/scripts/profile_receipt.py `
  MinerU/scripts/probe-capability.ps1 `
  kb_creator/contracts/mineru_provider_capabilities.v1.schema.json `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result confirmed the remediated validator/proof paths, adversarial tests, no
`hasattr(model, ...)`, no global setup/verify `SKIPPED`, and no tested
production HTTP-client/API URL path.

```powershell
git diff --check -- `
  kb_creator/contracts/mineru_provider_capabilities.v1.schema.json `
  MinerU/scripts/profile_receipt.py `
  MinerU/scripts/probe-capability.ps1 `
  kb_creator/tests/test_mineru_cpu_profile_packet_a.py `
  kb_creator/tests/test_mineru_three_view_tools.py
```

Result: PASS, no whitespace errors.

## Findings

### P0

None.

### P1

None. The four prior P1 findings are closed by implementation and adversarial
tests.

### P2

None introduced in the reviewed P1 closure scope.

The earlier environmental note still applies outside this closure scope: live
setup requires the documented bootstrap prerequisite (`uv` or repository-local
CPython `3.12.14`) and explicit orchestrator authorization. That is not a P1
closure defect.

## Blockers

No implementation-review blocker remains for Packet A P1 closure.

Live runtime acceptance is still a separate step. It must install/verify the
fresh CPU profile below `.tools`, produce install and verify receipts, run the
synthetic MinerU smokes, produce provider capabilities, and receive its own
evidence review before any real Dissociation source run.

## Recommendation

Approve Packet A implementation for orchestrator-authorized live setup only.

Do not start a real Dissociation source run from this receipt. Packet A is now
closed at the static/adversarial implementation level; runtime acceptance
depends on the next live setup and verification evidence.
