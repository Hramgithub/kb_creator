# Critic closure receipt: generic MASTER_RU Stage 20/21 P1.1-P1.3

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `generic-master-ru-stage20-21-p1-remediation`
- Review kind: `implementation`
- Role: independent critic
- Requested critic role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: none
- Timestamp: `2026-09-15T13:26:10+03:00`
- Elapsed time: approximately 6 minutes
- Token use: unavailable
- Scope: implementation closure for generic MASTER_RU Stage 20/21 P1.1-P1.3
- This is not a release review.

## Verdict

**GO** for a fresh Stage 10 run after the orchestrator chooses a new absent run
root and repeats the required preflight/run sequence.

This closure does not authorize accepting MASTER_EN, running Stage 20/21 on the
current stale-implementation run, translating content, recording acceptance,
running Stage 20+, release review, commit, or push.

## Authority and receipt checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_dissociation_master_ru_stage20_execution_20260915.md`
  - SHA-256: `9BC7B733D63965486791FFA564BF209374B578133923894639DB8971BA341B68`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_master_ru_submission_hardbreak_independent_qa_20260915.md`
  - SHA-256: `5ED96F1F183FC3E30B769B2B55959B14E95159ED16EC0FA831B3BA492AB00B04`

## Owned files checked

- `kb_creator/scripts/scenario_master_ru.py`
  - SHA-256: `2B0B5CE22665A618C880AE53C6ECC0E245179A92EAC28AC7430D14F419744DA2`
- `kb_creator/scripts/verify_scenario_master_ru.py`
  - SHA-256: `90B18E798E29AFD2CA9338C4B73088421167BC0987B3E9ACF8DD76550203B610`
- `kb_creator/pipeline/publication_adapters.py`
  - SHA-256: `0999DDBA41473B22A103798EBC759C437DE58A6FD72C79B48619C1D4300F012B`
- `kb_creator/pipeline/publication.py`
  - SHA-256: `32A39B5FFFEB46CE1E8225AA4C3D860A26A829F1AFD76A997429CA2533E42B0C`
- `kb_creator/tests/test_scenario_master_ru.py`
  - SHA-256: `63A7A4F69025BBD06C89C015E05DE42C35CA501EDC856F4B989DF58AD34A4082`
- `kb_creator/tests/test_verify_scenario_master_ru.py`
  - SHA-256: `1F712F4C08BB9A783D86D50063F439D9FC1F6D77C9570F18FD4D1D49564C7A2D`
- `kb_creator/tests/test_publication_registry_e2e.py`
  - SHA-256: `3DE1686873F19385CBE04C56638823558A2CC4EC1D9C5A494DB708266D765895`

The seven owned paths are untracked in this checkout, so there is no committed
base suitable for a meaningful Git diff. I inspected the current file contents,
file identities, and reproduced behavior.

## Evidence

- `scenario_master_ru author-submission` exists and accepts only
  `--packet-root`, `--batch-root`, `--destination`, and `--authority-root`.
  It derives authority from the validated packet/submission inputs, requires the
  exact expected translated batch file set, validates closed batch/unit identity
  and nonempty RU text, recomputes all unit/batch/submission identities, calls
  the same complete runtime submission validator before publish, writes through
  a same-parent staging file, removes staging on failure, rejects path escape,
  rejects reparse roots, and never overwrites an existing destination.
- `_structure_signature()` now includes ordered line classes, per-line two-space
  hard-break booleans, explicit `<br>` counts, fenced-code delimiter kind/width,
  and emphasis delimiter structure in addition to the existing Markdown,
  mechanics, link/image, heading, table, list and marker checks.
- The synthetic hard-break regression proves the compact ten-hard-break
  statblock passes and an otherwise identical zero-hard-break attack fails
  before writing a submission.
- The read-only live Stage 10 census found `87` units in the current
  `MASTER_EN.md`, with exactly `[('unit-00087', 10)]` for nonzero hard-break
  units.
- `verify_scenario_master_ru.py` imports only Python standard-library modules;
  it does not import `kb_creator` or producer helpers. It independently
  rederives packet/submission/candidate/provenance/asset/terminology/QA/
  inventory identities and emits a non-accepting
  `verified_candidate_pending_user_acceptance` receipt.
- Stage 21 adapter calls `verify_candidate()` immediately after `assemble()` and
  before moving the build into `artifacts`; it writes
  `evidence/MASTER_RU.verification.json`, validates status/scenario/candidate/
  submission/packet/contract/inventory/required-QA identities, and quarantine
  behavior is covered by a monkeypatched verifier failure test.
- Publication implementation inventory now includes
  `kb_creator/scripts/verify_scenario_master_ru.py`; the registry E2E asserts
  its presence in `run.json`.
- `record_artifact_acceptance()` requires exact dual evidence for contracts
  whose MASTER_RU `required_qa` includes `independent_translation_qa`: both
  `MASTER_RU.qa.json` and `MASTER_RU.verification.json` from the producer stage.
  Producer-only, verifier-only, stale/non-pass verification and substituted
  evidence are rejected; exact dual evidence succeeds only with explicit user
  decision text.
- Source search found no `dissociation`, `Dissociation`, `unit-00087`, or
  `HUMAN RESISTANCE` constants in the four owned implementation files. The
  remediation is generic.
- Legacy helper/routes are not widened by the new verifier; legacy contracts
  without the declared `independent_translation_qa` requirement keep their
  existing acceptance route.
- No live publication, acceptance, run mutation, translation, MinerU/CPU,
  Word/Poppler production execution, commit, or push was performed.

## Commands and results

```powershell
Get-FileHash kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_dissociation_master_ru_stage20_execution_20260915.md,kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_master_ru_submission_hardbreak_independent_qa_20260915.md,kb_creator/scripts/scenario_master_ru.py,kb_creator/scripts/verify_scenario_master_ru.py,kb_creator/pipeline/publication_adapters.py,kb_creator/pipeline/publication.py,kb_creator/tests/test_scenario_master_ru.py,kb_creator/tests/test_verify_scenario_master_ru.py,kb_creator/tests/test_publication_registry_e2e.py -Algorithm SHA256
```

Result: hashes listed above; authority and engineer receipt hashes match the
assignment.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_scenario_master_ru.py kb_creator/tests/test_verify_scenario_master_ru.py kb_creator/tests/test_publication_registry_e2e.py kb_creator/tests/test_publication_control_plane.py
```

Result: `65 passed, 1 skipped, 17 subtests passed in 94.73s`. The skip is
Windows `WinError 1314` for symlink creation in the reparse-root test.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m pytest -q -rs kb_creator/tests/test_publication_contracts.py kb_creator/tests/test_publication_html_adapter.py kb_creator/tests/test_publication_docx_adapter.py kb_creator/tests/test_publication_docx_to_pdf.py kb_creator/tests/test_publication_render_qa.py
```

Result: `17 passed, 1 skipped in 19.99s`. The skip is the already documented
Word COM activation limitation in this logon session; no production Word or
Poppler route was run.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -m py_compile kb_creator/scripts/scenario_master_ru.py kb_creator/scripts/verify_scenario_master_ru.py kb_creator/pipeline/publication_adapters.py kb_creator/pipeline/publication.py kb_creator/tests/test_scenario_master_ru.py kb_creator/tests/test_verify_scenario_master_ru.py kb_creator/tests/test_publication_registry_e2e.py
```

Result: PASS.

```powershell
& '.tools/PortableGit/cmd/git.exe' diff --check -- kb_creator/scripts/scenario_master_ru.py kb_creator/scripts/verify_scenario_master_ru.py kb_creator/pipeline/publication_adapters.py kb_creator/pipeline/publication.py kb_creator/tests/test_scenario_master_ru.py kb_creator/tests/test_verify_scenario_master_ru.py kb_creator/tests/test_publication_registry_e2e.py
```

Result: PASS.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c '<read-only Stage10 unit/hard-break census>'
```

Result:

```text
master_exists=True
master_bytes=20863
unit_count=87
nonzero_hardbreak_units=[('unit-00087', 10)]
total_hardbreaks=10
```

## Findings

- P0: none.
- P1: none. P1.1, P1.2 and P1.3 are closed by inspected implementation and
  reproduced tests.
- P2: host-conditional skips remain as environment facts, not inferred passes:
  Windows symlink privilege for one reparse-root test, and Word COM activation
  unavailable in this logon for one DOCX-to-PDF test. Neither blocks this
  generic MASTER_RU closure.

## Blockers

None for the scoped generic implementation.

The current publication run remains stale/non-resumable for this remediation
because its sealed implementation identity predates these changes. Use a fresh
absent run root for the next live Stage 10.

## Recommendation

Proceed to a fresh Stage 10 run only. Then independently verify/present the new
MASTER_EN candidate and wait for explicit user acceptance before any Stage 20
execution.

