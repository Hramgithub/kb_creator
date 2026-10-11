# Engineering receipt: local DOCX-to-PDF fallback

Date: 2026-09-16
Role: engineering (`gpt-5.6-sol`, high; user override)
Status: implemented and verified; no commit

## Result

KB Creator now has a generic, explicit local LibreOffice route for both:

- Stage 50 transient DOCX render QA; and
- Stage 60 final PDF export from the exact accepted DOCX.

The route is selected with `--libreoffice` and is mutually exclusive with
`--word`. It does not introduce an HTML/browser PDF route.

The bound executable must resolve below repository `.tools`. The verified local
binding is:

- path: `.tools/LibreOffice/26.8.0/program/soffice.exe`
- release/build: `26.8.0;buildid=bce0998afefdbc355585ca324285661a2170ba77`
- SHA-256: `A2823391857DB1DD8EBBD8234267F9EC58EC7E5B5FC434665C0ECEC4671CB988`

The executable SHA-256 is part of the publication run tool identity. Final
export evidence also binds the executable path, bytes, SHA-256, release/build,
the exact DOCX input identity, and the exact PDF output identity.

## Fail-closed behavior

- LibreOffice outside `.tools` is rejected.
- Exactly one of Word or LibreOffice must be bound.
- Each conversion uses a unique run-local LibreOffice user profile.
- Export waits for a stable, non-empty PDF even when `soffice.exe` launches a
  worker process.
- The conversion workspace and profile must be absent before success.
- Stage 50 deletes its transient PDF bridge and retains only PNG/JSON QA.
- Stage 60 permits exactly one persistent PDF and records
  `document_input_role = accepted_docx`.
- The generic logical adapter is `docx_pdf_export_v1`; the evidence names the
  actual engine (`libreoffice`, `microsoft_word_com`, or injected test).

## Dissociation policy preservation

The current Dissociation DOCX config remains hash-bound in the contract:

- bytes: `1573`
- SHA-256: `9327D4A3F81610E7A889995DA559DF0644EA0AE4BF993F5862DF942119EE41C5`
- `footer.page_numbers = false`

The contract passed live preflight with SHA-256
`0404D3A2AE4A9F507E0A3BCA33735440067B8CD5A2F8F5EDF2FAB4D159928773`.

## Verification

- `py_compile`: pass for CLI, control plane, adapters, render QA, local exporter,
  and offline verifier.
- focused exporter/contract/authoring suite: `67 passed, 1 skipped`.
- publication control plane: `33 passed`.
- Stage 50/60 DOCX adapter suite: `3 passed`.
- publication registry E2E: `10 passed`.
- `git diff --check`: pass.
- real local export smoke, using a copied quarantined run-17 DOCX:
  - input: 537,192 bytes,
    SHA-256 `8542C27FC45B7AFB98C5DD7FC42520504800BF19D11FD39B86830EF2D74BA122`;
  - output: 799,350 bytes,
    SHA-256 `CFA8380FC6AF62452D4133F7FBCD59C8776BD1B44B2C7CFEE7948F363F3A908E`;
  - isolated profile/workspace cleanup: pass;
  - smoke workspace removed after verification.

## Files changed by this task

- `kb_creator/__main__.py`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/publication_adapters.py` (only the runtime/export sections;
  unrelated concurrent edits were preserved)
- `kb_creator/scripts/publication_render_qa.py`
- `kb_creator/scripts/export_docx_to_pdf_local.py` (new)
- `kb_creator/scripts/author_scenario_publication_contract.py`
- `kb_creator/scripts/verify_production_package.py`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/contracts/publication_stage_manifest.v1.schema.json`
- `kb_creator/contracts/dissociation.publication.json`
- `kb_creator/inputs/dissociation/publication/v1/publication-blueprint.json`
- `kb_creator/tests/test_local_docx_pdf_export.py` (new)
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `kb_creator/tests/test_author_scenario_publication_contract.py`

## Remaining action

Start a fresh publication run because the implementation inventory and contract
identity changed. Bind the local engine with:

`--libreoffice .tools/LibreOffice/26.8.0/program/soffice.exe`

No installation, download, remote execution, or scenario-specific manual
artifact edit was performed by this task.

## P1 remediation: deep Stage 50 paths

Real run `20260916-publication-21` exposed a Windows path-length failure in the
first implementation. The quarantined DOCX is valid and only 147 characters at
its source path, but the former temporary workspace lived beside
`local/private/50-docx-candidate/bridge.pdf`. A representative LibreOffice
profile-internal path reached 275 characters. LibreOffice then waited until the
180-second timeout and produced no PDF in the exact output set.

The generic exporter now creates each conversion workspace with `mkdtemp` below
the short repository-local runtime root:

`.tools/runtime/kb_creator/docx_pdf/lo-<unique>`

The root is fail-closed:

- it must remain under the resolved repository `.tools` root;
- every existing ancestor is checked for symlink/reparse content;
- each invocation receives a unique directory, preventing cross-run collision;
- the unique workspace contains both the LibreOffice profile and conversion
  output;
- the full unique workspace is removed before success;
- only the intended PDF is atomically moved back into the assigned stage root.

The original accepted DOCX remains the actual LibreOffice input, so the accepted
DOCX lineage and evidence identity did not change.

Remediation verification:

- regression tests cover a deliberately deep stage path, two consecutive
  collision-free workspaces, complete cleanup, and reparse-ancestor rejection;
- exporter plus Stage 50 transient cleanup suite: `6 passed`;
- real smoke used a read-only copy of the run-21 quarantined DOCX at a
  181-character input/output stage path;
- export completed in 17.5 seconds;
- output: 799,104 bytes,
  SHA-256 `720A2B78AF841AFCA78BF0867F9D95A972EB1574291F6C5B9222E1A06AE05586`;
- runtime workspace child count after export: zero;
- smoke stage PDF count: exactly one (the requested final smoke output);
- the smoke workspace was removed after verification.
