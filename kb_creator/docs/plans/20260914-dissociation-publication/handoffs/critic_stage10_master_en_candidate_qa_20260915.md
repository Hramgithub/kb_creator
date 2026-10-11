# Critic QA receipt: Dissociation Stage 10 MASTER_EN candidate

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `stage10-master-en-candidate-qa`
- Review kind: `implementation`
- Role: bounded independent QA critic
- Requested critic role/model/effort: `gpt-5.5`, `medium`
- Actual platform model/effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: none
- Timestamp: `2026-09-15T12:41:06+03:00`
- Elapsed time: approximately 7 minutes
- Token use: unavailable
- Scope: read-only QA of live Stage 10 MASTER_EN candidate under
  `kb_creator/working/dissociation/publication/20260915-publication-01`
- This is not a release review.

## Verdict

**GO** to present the Stage 10 MASTER_EN candidate to the user for explicit
MASTER_EN acceptance.

This receipt does not authorize recording acceptance, resuming Stage 20+,
running Word/Poppler/MinerU/CPU, committing, pushing, packaging, or release
approval.

## Files and identities checked

- Run root:
  `kb_creator/working/dissociation/publication/20260915-publication-01`
- `run.json`
  - SHA-256: `A4BC5DBACD44D925AEE51804F28D75AFA4B63ACAF887D2528701579671FE5DA2`
  - portable identity: `F291449833998F9F0A2CF52443D6951BBE63805B4164CFA9B93FAF5CC600C782`
- `effective_publication_config.json`
  - SHA-256: `0597381625786F6B32A39BCCA0ABD3BDC0546B3162CC54EF63167A6FB611B3E8`
- Stage manifest:
  `evidence/stages/10-master-en-candidate.manifest.json`
  - file SHA-256: `66BA594E64809EB3EA68C2A24A7AE8BDC35F050E6CD8FFCD21166A177D47C63E`
  - reproducible seal: `8D68C86F3DC022C97D21F8D6E7D06CE2D4D2F1D17F2D0A5520B3B86043185D84`
- Candidate `MASTER_EN.md`
  - bytes: `20863`
  - SHA-256: `2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`
- Candidate `INVENTORY.json`
  - file SHA-256: `4D2682E8F838EB8043DEE71FE7387699E32F8A497379F4F4F958FCF77A2275C3`
  - inventory SHA-256: `9CE64E8BDBF7A7CC985537B063FD1EBC8CBF7F8A537ED0DF5E2D6B7AC941DAE4`
- `MASTER_EN.qa.json`
  - SHA-256: `CA5B6863A401650CBF442FD9D21E2422AD7A46942C47508C2826FF63DB8F11E2`
- `MASTER_EN.verification.json`
  - SHA-256: `D892D874DD5F5843B2D9BCAC493D79B38F29A6C428A365AEED232D0E8AA4DE97`
- Accepted reconstruction upstream:
  - `RECONSTRUCTED_EN.md` source bytes: `21048`
  - `RECONSTRUCTED_EN.md` source SHA-256:
    `2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D`
  - upstream inventory file SHA-256:
    `9B7F6D45EABDD4136350912B0BDCD320A2808B9516BAEA1CBFAD7924616B2A80`
  - upstream inventory seal:
    `7D6E05DA0E0F4CF71A5A89A2EEFC76C90D70EF001D5837DAEFF28BF59689C964`
  - acceptance receipt file SHA-256:
    `1B4F237A74DB6D5AAC9EED7D1124F01B7510F4B315C92F9C0B4D70E9CBC48852`
  - acceptance receipt seal:
    `10F058EE1D6FE1691E59EEB4B02354AC6862417FE193A5BA7991C03450223D22`
- Publication contract:
  `kb_creator/contracts/dissociation.publication.json`
  - SHA-256: `7F1B02F3C18B6C4FE998D121328ACCDB5A449D12C850368732BA2ACAA6EE0367`

## Evidence

- `run.json` portable identity recomputes exactly to
  `F291449833998F9F0A2CF52443D6951BBE63805B4164CFA9B93FAF5CC600C782`.
- `effective_publication_config.json` equals the control-plane derived
  effective config from the bound publication contract.
- Publication preflight, run against the same contract/config/upstream
  authorities and an absent sibling probe root, returned:

```json
{
  "schema": "kb_creator.publication_preflight.v1",
  "state": "ready",
  "target": "production_candidate",
  "contract_sha256": "7F1B02F3C18B6C4FE998D121328ACCDB5A449D12C850368732BA2ACAA6EE0367",
  "reconstruction_inventory_sha256": "7D6E05DA0E0F4CF71A5A89A2EEFC76C90D70EF001D5837DAEFF28BF59689C964",
  "reconstruction_acceptance_sha256": "10F058EE1D6FE1691E59EEB4B02354AC6862417FE193A5BA7991C03450223D22"
}
```

The probe root did not exist before or after, confirming the preflight call was
read-only.

- Control-plane `_load_run()` and `_validate_stage(..., index=0, upstream=[])`
  both passed for the live run root.
- Stage 10 reproducible seal recomputed exactly. Stage output inventory and
  stage evidence inventory recomputed exactly with the publication control-plane
  inventory helper.
- Candidate inventory recomputed exactly: 7 regular candidate files excluding
  `INVENTORY.json`, digest
  `9CE64E8BDBF7A7CC985537B063FD1EBC8CBF7F8A537ED0DF5E2D6B7AC941DAE4`.
- `MASTER_EN.md` is an exact LF serialization of accepted
  `RECONSTRUCTED_EN.md`; the only byte-level change is CRLF to LF. The accepted
  source has CRLF, the candidate has no carriage returns.
- Candidate metrics:
  - source page markers: 6, exactly pages 001-006;
  - headings: 21;
  - excluded pages: 0;
  - anchors: 0;
  - asset references: 2.
- Both candidate assets are byte-identical to accepted upstream assets:
  - `assets/e30a388dc2a17e216a53a2a673ea583c3b71be6567fe97f9e35805de71e760ac.jpg`
    - bytes `257805`
    - SHA-256 `E30A388DC2A17E216A53A2A673EA583C3B71BE6567FE97F9E35805DE71E760AC`
  - `assets/f96ad0f20513f4737474915670fe2a1f361bf60c12fd6ae0f210cf2132127de4.jpg`
    - bytes `236058`
    - SHA-256 `F96AD0F20513F4737474915670FE2A1F361BF60C12FD6AE0F210CF2132127DE4`
- `MASTER_EN.qa.json` reports:
  - status `pass`;
  - candidate state `awaiting_master_en_acceptance`;
  - errors `[]`;
  - derived metrics `{anchors: 0, assets: 2, excluded_pages: 0, headings: 21, source_pages: 6}`.
- `MASTER_EN.verification.json` reports:
  - status `verified_candidate_pending_process_and_external_gates`;
  - same derived metrics as QA;
  - exact identities for candidate inventory, `INVENTORY.json`, `MASTER_EN.md`
    and derived runtime config.
- Final HUMAN RESISTANCE section:
  - found at line 173 as heading
    `## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)`;
  - the 11 nonblank body rows are consecutive with no blank paragraphs between
    stat rows;
  - 10 Markdown hard-break lines end in two spaces;
  - the standard blank line after the Markdown heading is present and is
    source-identical under the exact CRLF-to-LF projection.
- No downstream publication output exists: `outputs/` contains only
  `10-master-en-candidate`.
- No Stage 20+ manifest exists: `evidence/stages/` contains only
  `10-master-en-candidate.manifest.json`.
- No MASTER_EN acceptance exists: `acceptance/` is absent and no acceptance
  files were found.

## Commands and results

```powershell
Get-FileHash "$run/run.json","$run/effective_publication_config.json","$run/outputs/10-master-en-candidate/artifacts/MASTER_EN.md","$run/outputs/10-master-en-candidate/artifacts/INVENTORY.json","$run/outputs/10-master-en-candidate/evidence/MASTER_EN.qa.json","$run/outputs/10-master-en-candidate/evidence/MASTER_EN.verification.json","$run/evidence/stages/10-master-en-candidate.manifest.json" -Algorithm SHA256
```

Result: hashes listed above; `MASTER_EN.md` matched expected
`2AD1E9175A3B53B7C85CCA5824B2FAA60D4A82C38928F487E6BB7700B5617CA6`.

```powershell
$env:PYTHONPATH=(Resolve-Path '.tools/python-test-deps').Path
& '.tools/MinerU/.venv/Scripts/python.exe' -B -c '<read-only run/stage/projection/preflight QA probe>'
```

Result: all critical read-only checks passed after recomputing with the
publication control-plane helpers. No run/config/contract/acceptance file was
created or changed.

## Findings

- P0: none.
- P1: none.
- P2: none.

## Recommendation

Present the Stage 10 MASTER_EN candidate to the user for explicit acceptance.

If the user accepts, acceptance must be recorded by the orchestrator using the
existing Stage 10 evidence set. This QA receipt itself does not infer or record
acceptance.

