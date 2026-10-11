# M3 architecture receipt: Number 7 Dream publication v1 authority

## Receipt

- Goal: `20260917-dream-master-en`; milestone: M3.
- Role: architecture / dependency and remediation specification.
- Policy role/model/effort: `gpt-5.6-sol`, `high`.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, `medium`; ownership was not transferred.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Timestamp: `2026-09-18T00:20:07+03:00`.
- Elapsed time: approximately 55 minutes.
- Token use: unavailable.
- Scope: exact Git-visible publication-v1 authority needed to author the generic contract and execute only Stage 10 `MASTER_EN` from the already accepted reconstruction.
- Result: **SPEC_READY**. No pipeline/config/contract/generated/canonical project artifact was changed.
- Files changed: this immutable receipt only.

## Decision and boundary

Author one declarative, scenario-specific data tree through the existing generic
contract author. Do not add Number 7 Dream Python or PowerShell. Stage 10 reads
only `configs/master_en.json`; the author and publication preflight nevertheless
identity-bind all seven config roles. The other six files are therefore valid
source templates/placeholders, not evidence that Stage 20+ is authorized or
accepted.

Run only `publication run`. Its first stage must stop with exit code `10` and
state `awaiting_master_en_acceptance`. Do not call `publication resume` or
`publication record-acceptance` in the same packet. Reconstruction acceptance
does not imply MASTER_EN acceptance.

## Frozen upstream

Use only:

- package root:
  `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-16/promotion/reconstruction-upstream-v1`;
- inventory seal:
  `FDE1E1C5FAC2746203909C518046DD46AB2895770E3A4EEAEDE4F9CDAAFA15DA`;
- acceptance seal:
  `BFEF49D286A4A25F61CDAD2E8F2A1E8D51660BE6327EFEADB4C797F8D1B4607B`;
- reconstruction contract canonical SHA-256:
  `A74582B223805E643EB6B7C03BD540DBB90CF2B0B124F9B1E220B6B7251B4A07`;
- accepted `RECONSTRUCTED_EN.md`: 76,478 bytes,
  `4DEE0DFBC694F1B9A48357A05F47EB34C2F6B1C5E107CC42475CE76444A9EAC9`;
- source: 26 pages, 26 ordered page markers, 81 Markdown headings and 19
  unique Markdown image references.

The reconstruction-contract value is the canonical JSON digest recorded by the
accepted package. The current pretty-printed Git-visible contract has a
different raw-file hash, which is not a lineage conflict.

## Git-visible topology

Create exactly:

```text
kb_creator/inputs/number-7-dream/publication/v1/
  publication-blueprint.json
  configs/
    master_en.json
    master_ru.json
    html.json
    docx.json
    pdf.json
    package.json
    artview/
      profile.json
      source-graph.json
      assets/<19 lowercase-sha256>.jpg

kb_creator/contracts/number-7-dream.publication.json
```

All paths stored in the blueprint are repository-root-relative. Consequently
both the author and publication control plane must receive repository root `.`
as `--config-root`; using the `v1` directory would duplicate path prefixes and
fail closed.

Do not copy terminology into this tree. Bind the current canonical shared
authority directly as
`CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`; the generic
author supplies its bytes and SHA-256.

## Exact blueprint values

`publication-blueprint.json` uses schema
`kb_creator.scenario_publication_blueprint.v1`, revision `1`, and:

| Field | Exact value |
|---|---|
| scenario id | `number-7-dream` |
| English title | `Number 7 Dream` |
| Russian publication title | `Сон № 7` |
| languages | `en` -> `ru` |
| MASTER_EN | `MASTER_EN.md` |
| MASTER_RU | `MASTER_RU.md` |
| HTML | `Number_7_Dream_RU.html` |
| DOCX | `Number_7_Dream_RU.docx` |
| PDF | `Number_7_Dream_RU.pdf` |
| MASTER_EN profile | `neutral_v3` |
| MASTER_RU profile/policy | `neutral_v1` / `ordered_hash_bound_units_v1` |
| ArtView decisions | `kb_creator.scenario_artview_decisions.v3`, version `3` |
| tool policy | `.tools`; `powershell`, `microsoft_word_com` |

`Сон № 7` is an explicit editorial declaration for the publication authority,
not a reconstructed source fact. If the orchestrator chooses another Russian
title, change it consistently in the blueprint, HTML and DOCX configs before
authoring; never patch the generated contract.

Config paths are the seven paths in the topology above. Upstream roles are in
this exact order: `reconstructed_en`, `reconstruction_manifest`,
`reconstruction_qa`, `source_identity`.

Required QA/policies are:

- MASTER_EN: `accepted_upstream_identity`, `exact_source_projection`,
  `source_disposition_closure`, `asset_manifest_closure`,
  `candidate_inventory_closure`, `independent_v3_verification`;
- MASTER_RU: `accepted_master_en_identity`, `ordered_unit_identity`,
  `markdown_structure_preservation`, `mechanics_preservation`,
  `terminology_authority`, `asset_identity`, `independent_translation_qa`;
- HTML: `accepted_master_ru_identity`, `accepted_artview_identity`,
  `local_reference_closure`, `structural_html`, `all_page_visual_review`;
- DOCX: `accepted_html_identity`, `ooxml_integrity`, `all_page_png`,
  `reader_layout`, `document_metadata`;
- PDF: `accepted_docx_identity`, `fresh_docx_export`, `all_page_png`,
  `no_direct_html_route`.

ArtView bundle roles are exactly `candidate_manifest`, `review_html`,
`accepted_decisions`, `application_receipt`, `effective_visual_config`,
`bundle_inventory`, `candidate_binaries`, `source_context`.

Package roles are exactly the control-plane mandatory set:
`master_en`, `master_en_acceptance`, `master_ru`, `master_ru_acceptance`,
`artview_bundle`, `artview_candidate_manifest`, `artview_decisions`,
`artview_application`, `artview_effective_config`, `artview_acceptance`,
`html`, `html_acceptance`, `docx`, `docx_acceptance`, `pdf`,
`pdf_acceptance`, `source_configs`, `effective_config`, `stage_evidence`,
`pipeline_snapshot`, `schema_snapshot`, `offline_verifier`; stable names are
true and verifier version is `1`.

PDF policy is the exact accepted-DOCX route: adapter `docx_pdf_export_v1`,
`document_input_role: accepted_docx`, `format: pdf`, `all_pages: true`,
`fresh_export: true`. HTML and browser PDF routes are forbidden.

## Exact stage-source configs

`configs/master_en.json`:

```json
{
  "schema": "kb_creator.master_en_publication.v3",
  "scenario_id": "number-7-dream",
  "inputs": {},
  "projection": {
    "output_name": "MASTER_EN.md",
    "excluded_source_pages": [],
    "page_marker_policy": "source_page_comment_v1",
    "anchor_policy": "preserve_v1",
    "asset_policy": "copy_markdown_references_v1"
  },
  "required_qa": [
    "accepted_upstream_identity",
    "exact_source_projection",
    "source_disposition_closure",
    "asset_manifest_closure",
    "candidate_inventory_closure",
    "independent_v3_verification"
  ]
}
```

There are no excluded pages: the accepted candidate covers all 26 source pages,
including credits, source TOC, appendices, handouts and pregenerated
characters. Stage 10 performs projection and page-boundary normalization only;
it must not perform reader cleanup, translation or HTML-era TOC replacement.

The remaining closed markers are:

```json
{"schema":"kb_creator.master_ru_adapter.v1","max_batch_chars":3000}
{"schema":"kb_creator.pdf_adapter.v1"}
{"schema":"kb_creator.package_adapter.v1"}
```

Use the first as `master_ru.json`, the second as `pdf.json`, and the third as
`package.json` (pretty-printing and a final newline are allowed).

`html.json` is a neutral, directly parseable future source config with titles
above and only these production settings: `print_columns: 1`,
`avoid_single_column_fragmentation_context: true`,
`keep_full_page_art_with_heading: true`,
`allow_long_callout_page_breaks: true`,
`allow_statblock_flow_beside_body_art: false`; typography is Georgia / Times New
Roman fallback, body `11.5pt`, line height `1.42`, print body `9.75pt`, print
line height `1.24`. Do not freeze a Russian heading-id hierarchy before an
accepted MASTER_RU exists; omit `toc_policy` so the neutral adapter uses its
generic generated-TOC policy. Do not add runtime paths, acceptance claims or a
PDF engine.

`docx.json` uses schema `kb_creator.production_docx_config.v1`: portrait A4
210x297 mm; margins top/bottom/left/right `16/17/18/18` mm; Georgia for body,
title, headings and footer; sizes body/title/footer `10.5/22/9` pt; body after
`4` pt and line spacing `1.15`; heading levels 1-6 are respectively
`18/16/14/12/11/10.5` pt, bold, with before/after spacing
`12/6`, `10/5`, `9/4`, `8/4`, `7/3`, `6/3`; footer page numbers false.
Metadata is title `Сон № 7`, subject
`Сценарий для Call of Cthulhu 7th Edition`, author `James Killick`, keywords
`Call of Cthulhu, сценарий, Сон № 7`, comments
`NRI KB Creator; generated from accepted publication authorities`.

These downstream files are hash-bound because contract v1 eagerly inventories
all roles. Stage 10 does not consume or semantically validate them. Any later
editorial change invalidates this contract/run identity and must be handled by
a freshly authored contract/run, not by editing files behind an existing run.

## ArtView source template and asset decision

Mirror **only the 19 assets referenced by accepted Markdown**, not all 29 files
in the accepted reconstruction asset manifest. The omitted ten are
`placement: reference_only` statblock snippets on source page 18. Their bytes
remain closed by the accepted reconstruction inventory and were deliberately
replaced by semantic text; copying them into ArtView would incorrectly expose
suppressed evidence as reader artwork.

For each of the 19 rows, copy the accepted binary byte-for-byte to
`configs/artview/assets/<stored basename>`. `source-graph.json` has schema
`kb_creator.scenario_artview_source_graph.v1`, scenario `number-7-dream`, and
one artifact per row with role `accepted_reconstruction_asset`, accepted
`logical_name`, source page parsed from it, local `assets/...` path, byte count
and full uppercase SHA-256 from accepted `content/ASSET_MANIFEST.json`.

The exact reader set is:

| asset id / local filename stem | page | placement | bytes | dimensions | group |
|---|---:|---|---:|---|---|
| `55ca597755b7df71c1e3699353265ee4ad9771ebbdb920410317e7073f6284fe` | 4 | inline | 49023 | 715x245 | `scenario_art` |
| `8fc42816bf72beda6938faad5a1aff6dea6de1bef286ee8d8822a8dac55bbbd6` | 5 | inline | 49082 | 715x245 | `scenario_art` |
| `d546ef251ace98df9136ea8c332883b06594c7082d32ed1ac80c4dbd915d9523` | 6 | inline | 31076 | 423x418 | `scenario_art` |
| `ffd474f4a049b1968c6f7b5f9068019b5cdec558e69b9a1e995aa21663395857` | 7 | inline | 30984 | 396x404 | `scenario_art` |
| `8d4e75a0cd6c3098cfd7b84b4fb603395e7269ec4249b8ab05734751a58edd70` | 7 | inline | 59762 | 692x395 | `scenario_art` |
| `456c573fb9955c8a3312cadf47a7559255d3416427b764e874d8d8d7d2b6a35c` | 8 | map | 77664 | 1370x726 | `maps` |
| `833474cc789c6f5e00034fe72dd8ad95c5c148dd553d5451056a0be134473525` | 9 | inline | 48035 | 715x242 | `scenario_art` |
| `ba5b7c947407c8409b5353e7a25196a98be9e9dc47a786ee0376cd8bc23348b4` | 11 | map | 117658 | 1340x787 | `maps` |
| `f16bfb5bbc3e13437865969cf46fecb192edeeab07978a0e1dabf1c60ed8345b` | 13 | inline | 110551 | 712x723 | `scenario_art` |
| `5f84fc66111294af52199ed1c80e48d71f9f8ddb412d52ee2cf42d04e31f7e4d` | 14 | inline | 163279 | 1535x573 | `scenario_art` |
| `9f377a1d675ff226c5405c3a6968540b6a32221c151152c82e7770a708f2b981` | 15 | map | 65579 | 1456x609 | `maps` |
| `2e39199dc3787b0600ac4f9843fd02de5f88dfb05be59acd833b9a17b5735421` | 17 | inline | 207987 | 1448x798 | `scenario_art` |
| `7d73dfea3baa03b388a63f836c0ca43f9238efee255ab26ffcdb49bfacf79890` | 20 | handout | 179661 | 1484x840 | `handouts` |
| `f21773feb120405acf2244939ea196833341dd24a2933ab9f08424aa1e44e5ac` | 21 | inline | 45533 | 534x534 | `pregenerated_characters` |
| `8cc466f9543ad6eb3be419b505950eb16cd7b0cf0b3b33cfa0162bfa0f4c97a9` | 22 | inline | 40846 | 503x507 | `pregenerated_characters` |
| `f51f17c46ef8227af096809e89eb784e968a715088739dc2b0b7f5778076e743` | 23 | inline | 38341 | 495x495 | `pregenerated_characters` |
| `6f1393bc7dc691b0b8f2a2039d1c502aea957d8b8b5617deb0e1a2a8cd804165` | 24 | inline | 36852 | 462x459 | `pregenerated_characters` |
| `30f29ef0afd70573f4f5411b933170a0faaafec268e1842bb6ded414c7ad1f95` | 25 | inline | 41174 | 470x487 | `pregenerated_characters` |
| `a334e31185e6dcb3c4ca4ff2f900efff0f4e77d7cd0c446fd7e4ba0392c35e1a` | 26 | inline | 40683 | 479x471 | `pregenerated_characters` |

`profile.json` uses schema `kb_creator.scenario_artview_profile.v3`, scenario id
`number-7-dream`, `output_root: artview-build`, excluded pages `[]`, and 19
rows in the table order. First author `source-graph.json`, then put its exact
path/bytes/SHA record into all four source-template input slots. This is
intentional: at Stage 30 the generic adapter replaces `master_ru`,
`master_ru_acceptance` and `master_ru_asset_manifest` with accepted run-local
identities; it retains `reconstruction_inventory` as this exact source graph.

For each row use the SHA stem as `asset_id`, `source-page-NNN` as `anchor`,
label `Source visual from page N`, the table page/group, identical `current`
and `context` records, media type `image/jpeg`, exact bytes/SHA/dimensions,
`alternatives: []`, and presentation defaults `{width_percent: 100,
alignment: center, wrap_text: false, wrap_tables: false}`. This deliberately
avoids guessing final wrapping before user ArtView review.

## Author, preflight and run commands

All commands run from repository root. Author into an absent target:

```powershell
& ".\.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe" -B `
  kb_creator\scripts\author_scenario_publication_contract.py `
  --blueprint kb_creator\inputs\number-7-dream\publication\v1\publication-blueprint.json `
  --config-root . `
  --output kb_creator\contracts\number-7-dream.publication.json
```

Create only parent `kb_creator/working/number-7-dream/publication`; keep run root
`kb_creator/working/number-7-dream/publication/20260918-publication-01` absent.
Then run the read-only preflight:

```powershell
& ".\.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe" -B -m kb_creator `
  publication preflight `
  --contract kb_creator\contracts\number-7-dream.publication.json `
  --upstream-inventory kb_creator\working\number-7-dream\reconstruction\20260917-cpu-replay-16\promotion\reconstruction-upstream-v1\RECONSTRUCTION_INVENTORY.json `
  --reconstruction-acceptance kb_creator\working\number-7-dream\reconstruction\20260917-cpu-replay-16\promotion\reconstruction-upstream-v1\RECONSTRUCTION_ACCEPTANCE.json `
  --config-root . `
  --run-root kb_creator\working\number-7-dream\publication\20260918-publication-01 `
  --tools-root .tools `
  --json
```

Preflight must return `state: ready`, exit `0`, both accepted upstream seals,
and must not create the run root. Execute only Stage 10:

```powershell
& ".\.tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe" -B -m kb_creator `
  publication run `
  --contract kb_creator\contracts\number-7-dream.publication.json `
  --upstream-inventory kb_creator\working\number-7-dream\reconstruction\20260917-cpu-replay-16\promotion\reconstruction-upstream-v1\RECONSTRUCTION_INVENTORY.json `
  --reconstruction-acceptance kb_creator\working\number-7-dream\reconstruction\20260917-cpu-replay-16\promotion\reconstruction-upstream-v1\RECONSTRUCTION_ACCEPTANCE.json `
  --config-root . `
  --run-root kb_creator\working\number-7-dream\publication\20260918-publication-01 `
  --tools-root .tools `
  --python .tools\MinerU\profiles\pipeline-cpu-v1\.venv\Scripts\python.exe `
  --powershell C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe `
  --pdftoppm .tools\poppler\poppler-26.02.0\Library\bin\pdftoppm.exe `
  --word "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE" `
  --run-id 20260918-publication-01 `
  --json
```

The four executables above exist in the current workspace/host. Resolving them
for the fixed registry does not activate Word/Poppler at Stage 10.

## Acceptance criteria

1. Blueprint and generated contract pass their Draft 2020-12 schemas and the
   generic author's closed validation; contract target was absent before author.
2. Contract scenario/upstream values match the accepted inventory and receipt;
   all seven config and terminology identities reopen under repository root.
3. The 19 mirrored binaries equal accepted bytes/SHA and decode to the table
   dimensions; no page-18 `reference_only` file enters the ArtView tree.
4. MASTER_EN config is exactly the neutral-v3 source template above, with zero
   excluded pages and the six required QA names in order.
5. Publication preflight returns ready without creating the run root.
6. Publication run creates exactly successful Stage 10 evidence, including
   independent `MASTER_EN.verification.json`, and no Stage 20 output.
7. The output preserves all 26 page dispositions, semantic Markdown and 19
   referenced assets by identity; independent verifier passes.
8. Final process result is exit `10`, `awaiting_master_en_acceptance`; no
   acceptance receipt, translation, ArtView decision, render or package exists.
9. New inputs/contract are Git-visible; generated `working/` output remains
   ignored and outside later commit scope.

## Risks and next action

- P1: contract v1 eagerly hashes later-stage configs although Stage 10 does not
  consume them. Do not edit them behind a run; re-author if downstream review
  changes one.
- P1: ArtView source profile is a source template, not directly runnable before
  the Stage 30 adapter replaces its three MASTER_RU bindings. Do not use a
  standalone ArtView build as the M4 validation command.
- P2: `Сон № 7` is an editorial choice. A different choice must be made before
  authoring and propagated consistently.
- P2: HTML's final translated heading hierarchy is intentionally not guessed at
  M3; Stage 40 remains subject to its own config/visual review.

Blockers: none for M4 authoring or Stage 10.

Next action: the orchestrator/executor authors the exact topology, validates
binary/config identities, runs the generic author and preflight, then executes
only Stage 10 and stops at the explicit MASTER_EN gate.

## Evidence inspected

Goal plan/context; blueprint and publication-contract schemas; generic contract
author; publication CLI/control plane/adapter registry; neutral MASTER_EN
builder/verifier; ArtView profile schema and runtime source-graph binding;
Dissociation v1 only as a mechanism example; current accepted Dream inventory,
acceptance, manifest, QA, Markdown, semantic sidecar and asset manifest; local
tool presence. No generated command or test suite was run.
