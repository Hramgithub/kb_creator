# Config-author receipt: Dissociation publication v1

## Receipt metadata

- Goal id: `20260914-dissociation-publication`
- Step id: `stage10-publication-config-prerequisites`
- Role: bounded content/config author
- Policy role/model/effort: contributor role; platform model and effort unavailable
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred
- Assignment state: `platform-unverified`
- Scoped override: none
- Timestamp: `2026-09-15T12:15:00+03:00`
- Elapsed time: approximately 20 minutes
- Token use: unavailable
- Scope: only the new Dissociation publication v1 input tree, the absent generated contract target, and this receipt
- Result: declarative candidate packet authored and identity-checked; contract authoring and publication preflight stopped on an existing ArtView v3 JSON Schema defect

## Changed files

All files below are new. No existing source, reconstruction package, accepted
artifact, pipeline code, test, canonical plan/status/context, Git index, or
`.codex/config.toml` was changed.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `kb_creator/inputs/dissociation/publication/v1/publication-blueprint.json` | 3804 | `000997883BACB8F6B546CF04215353B9C10177A31BF7EAFEE675B59796F43D4E` |
| `kb_creator/inputs/dissociation/publication/v1/configs/master_en.json` | 554 | `B9F02C6440BB142ED281D9518049F798DE492AA8524AD7E1530BCC768BEDB52C` |
| `kb_creator/inputs/dissociation/publication/v1/configs/master_ru.json` | 77 | `A5C0BAFA954E957F47B0E880FAC1FB70DA857CD3364882CC5FFEFB194F900E7B` |
| `kb_creator/inputs/dissociation/publication/v1/configs/artview/profile.json` | 3018 | `D847123065C99DB39A41CD26949F0B74342E603AB2A604A5390CFEAB0376F18A` |
| `kb_creator/inputs/dissociation/publication/v1/configs/artview/source-graph.json` | 770 | `CB30B2059000464DA1CB8F8CE5A93E30EB86D0511D5F2A54720307D2C6F499B2` |
| `kb_creator/inputs/dissociation/publication/v1/configs/artview/assets/e30a388dc2a17e216a53a2a673ea583c3b71be6567fe97f9e35805de71e760ac.jpg` | 257805 | `E30A388DC2A17E216A53A2A673EA583C3B71BE6567FE97F9E35805DE71E760AC` |
| `kb_creator/inputs/dissociation/publication/v1/configs/artview/assets/f96ad0f20513f4737474915670fe2a1f361bf60c12fd6ae0f210cf2132127de4.jpg` | 236058 | `F96AD0F20513F4737474915670FE2A1F361BF60C12FD6AE0F210CF2132127DE4` |
| `kb_creator/inputs/dissociation/publication/v1/configs/html.json` | 727 | `0C3146621004964AF4E8FF969F7B4B40D6031C7D01CE86118DC3A99332CC53CD` |
| `kb_creator/inputs/dissociation/publication/v1/configs/docx.json` | 1572 | `A8441E66257CDA5565A7B6AF8C02E1CB54DE1AF4C56E3F80F6622B4C3981E85B` |
| `kb_creator/inputs/dissociation/publication/v1/configs/pdf.json` | 44 | `EF783EAA329FDD591FFE8E24CC553B671B7B12C8499B5248D92B03EA1FE720E0` |
| `kb_creator/inputs/dissociation/publication/v1/configs/package.json` | 48 | `57D85F492D42CF58BF3547662327007842A441D43009B45ADC7F4CF533C991B9` |
| `kb_creator/inputs/dissociation/publication/v1/terminology/CoC_Terminology_Decisions.csv` | 5559 | `7CE59014F5AFECE837128CEEA067610944335534C5B86542189FEFEFDDFA9F99` |
| `kb_creator/inputs/dissociation/publication/v1/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md` | 11884 | `BE7CCE74993263983670FF68459805CCB49DE873B1EB5B1B95E85442FF223304` |

This receipt is the only other changed file; its own identity is intentionally
not self-recorded.

## Rationale and identities

- Scenario id/title/languages are `dissociation`, `Dissociation`, explicitly
  authored Russian title `Диссоциация`, and `en` -> `ru`.
- The blueprint binds reconstruction contract SHA-256
  `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`
  and the exact ordered upstream roles `reconstructed_en`,
  `reconstruction_manifest`, `reconstruction_qa`, `source_identity`.
- Artifact basenames are `MASTER_EN.md`, `MASTER_RU.md`,
  `Dissociation_RU.html`, `Dissociation_RU.docx`, and
  `Dissociation_RU.pdf`.
- MASTER_EN is the closed source-template shape for `neutral_v3`, with
  `inputs: {}`, no excluded pages, exact source-page comments, preserved
  anchors, copied Markdown references, and required independent v3
  verification.
- MASTER_RU is closed `neutral_v1` with `max_batch_chars: 3000`, the ordered
  hash-bound unit policy, and exact copied terminology authorities.
- ArtView is v3 with two evidence-derived rows only: the accepted cover on
  source page 1 and accepted Alaska map on source page 5. Their current and
  context records use the exact accepted reconstruction binaries. There are
  zero alternatives and no decision or acceptance document.
- HTML contains only reader/print layout and typography policy. It contains no
  browser, print-to-PDF, or other direct-PDF engine.
- DOCX is explicit portrait A4 with Georgia reader typography, margins,
  spacing, levels 1-6, footer page numbers, and Dissociation metadata.
- PDF is only the closed `kb_creator.pdf_adapter.v1` marker; the blueprint
  requires exact accepted DOCX -> fresh Word COM PDF.
- Package is only the closed `kb_creator.package_adapter.v1` marker; the
  blueprint declares the exact 22 mandatory roles and no acceptance/release
  state.
- Repository tool root is `.tools`; only system PowerShell and Microsoft Word
  COM are allowed.

The copied terminology files match their canonical authorities byte-for-byte:

- `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`: 5559
  bytes, SHA-256
  `7CE59014F5AFECE837128CEEA067610944335534C5B86542189FEFEFDDFA9F99`;
- `kb_creator/docs/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md`: 11884
  bytes, SHA-256
  `BE7CCE74993263983670FF68459805CCB49DE873B1EB5B1B95E85442FF223304`.

## Validator commands and results

All Python checks used repository-local
`.tools/MinerU/profiles/pipeline-cpu-v1/.venv/Scripts/python.exe`. The isolated
repository-local `.tools/python-test-deps` directory was added to `sys.path`
only for `jsonschema`; the production profile itself does not contain that
optional package.

1. `scenario_publication_blueprint.v1.schema.json`: `PASS`, including
   `Draft202012Validator.check_schema()` and instance validation.
2. Source MASTER_EN adapter shape and policies: `PASS`. The full v3 builder
   parser is intentionally not applied to this source template because the
   Stage 10 adapter replaces `inputs: {}` with four exact run-local
   authorities before calling the builder.
3. Closed MASTER_RU adapter config and positive batch size: `PASS`.
4. `production_docx.validate_document_config()`: `PASS`.
5. HTML source policy parse plus serialized no-`pdf` check: `PASS`.
6. Exact PDF and package marker shapes: `PASS`.
7. ArtView source graph path/bytes/SHA membership plus Pillow media/dimension
   decode for current/context records: `PASS`; 2 rows, 0 alternatives, 0
   decisions, 0 acceptances.
8. Both terminology copies compared by byte count and SHA-256: `PASS`.
9. `scenario_artview_profile.v3.schema.json`: `FAIL` before instance
   validation. `Draft202012Validator.check_schema()` reports
   `jsonschema.exceptions.SchemaError`; its `safePath` pattern is not a valid
   regex for the repository's Python validator and the underlying error is
   `re.error: missing ), unterminated subpattern at position 14`.

The failing decoded pattern is:

```text
^(?![A-Za-z]:)(?![/\])(?!.*(?:^|[/\])\.\.(?:[/\]|$))[^\x00-\x1F]+$
```

This is the same existing schema-tooling defect previously recorded as P2 in
`critic_v2_materializer_comparison_authority_implementation_closure_20260915.md`.
It becomes a blocker here because this packet explicitly requires every
applicable schema validator to pass before contract authoring.

## Contract author and preflight state

The generic author command was **not run**. Its production Python would omit
JSON Schema validation when `jsonschema` is unavailable; using that behavior
after the explicit schema failure would bypass the required gate. Therefore:

- `kb_creator/contracts/dissociation.publication.json` remains absent;
- `kb_creator/working/dissociation/publication` remains absent;
- proposed run root
  `kb_creator/working/dissociation/publication/20260915-publication-01`
  remains absent;
- publication preflight was not run;
- no Stage 10 or later publication action was run.

## Blocker and next action

Blocker: correct and independently review the existing generic
`scenario_artview_profile.v3.schema.json` `safePath` regex. This contributor
does not own schemas or pipeline code and did not mutate either.

After that closure, rerun every validator, invoke only the generic contract
author into the still-absent target, create only the publication parent, and
run the exact read-only preflight for `20260915-publication-01`. Do not create
the run root, execute Stage 10, infer acceptance, render, commit, or push.
