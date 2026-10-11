# Scenario contract architecture for the second `kb_creator` scenario

Goal: `20260830-kb-creator-next-scenario`

Step: `3-generic-scenario-contract-specification`

Status: architecture candidate for independent Step 4 review; no implementation
is authorized by this document.

## Decision

Adopt one closed, declarative `ScenarioContract.v1` per scenario and keep the
pipeline stage graph fixed in trusted reusable code:

```text
immutable source PDF
  -> reconstructed_en
  -> master_en
  -> master_ru
  -> html
  -> pdf
  -> production
```

The contract declares only facts and reviewed policies that vary between
Innsmouth and Viral: scenario/source identity, full page topology, stable
artifact names, stage-specific expectations, terminology authorities,
presentation profiles, exact scoped exceptions, and acceptance requirements.
It must not contain Python, shell commands, arbitrary import paths, executable
templates, or a second configurable pipeline graph.

Build, freeze/promote, verify, canonical JSON, inventory hashing, no-overwrite
publication, upstream provenance validation, asset closure, and evidence
freshness remain generic code. Generated output byte counts and hashes do not
get copied back into the scenario contract; they are candidate and acceptance
manifest facts.

This is the minimum boundary proven by two scenarios. It does not attempt to
generalize books, campaigns, non-CoC systems, alternate translation graphs, or
arbitrary renderer plugins.

## Evidence and assumptions

### Authoritative evidence inspected

- `docs/governance/nri_goal_governance.md` defines immutable contributor
  receipts, canonical-state ownership, defect-class closure, and the independent
  release gate.
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md:15-39` defines the
  accepted stage chain and stage responsibilities;
  `:133-149` defines working/accepted/production state and separate
  build/freeze actions; `:184-197` identifies the current defect: reusable
  architecture is mixed into 23 Innsmouth-specific scripts with pinned paths,
  hashes, counts, and scenario structure.
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md` records the
  admitted Viral source identity, 124-page all-pages scope, page topology,
  zero/low-text and corrupt-glyph risks, and the prohibition on using historical
  EN/RU artifacts as new-master inputs.
- `kb_creator/scripts/build_innsmouth_reconstructed_en.py:21-105` mixes exact
  Innsmouth repairs, page counts, source hashes, and asset identities with
  generally reusable page splitting, asset inventory, and reconstruction
  reporting. Its `apply_source_structure_repairs` and page-indexed operations
  demonstrate that exact reconstruction exceptions need a data boundary, but
  not arbitrary executable config.
- `kb_creator/scripts/build_innsmouth_master_en.py:19-212` pins the accepted
  reconstruction identity, reader asset allowlist, TOC, anchors, internal
  references, handout mappings, and art-owner relocations in code.
- `kb_creator/scripts/freeze_innsmouth_master_en_repo_input.py` and
  `freeze_innsmouth_master_ru_repo_input.py` combine generic promotion rules
  (explicit hash, exact inventory, canonical manifest, no overwrite) with
  scenario identities, terminology replacements, anchor projections, and
  handout/art rules.
- `kb_creator/scripts/build_innsmouth_html_from_master_ru.py:26-92` combines the
  generic accepted-RU-to-HTML route with Innsmouth output names, art placement,
  layout IDs, and CSS. `freeze_innsmouth_html_repo_input.py:18-61` similarly
  combines generic exact verification with scenario counts and identities.
- `kb_creator/scripts/build_innsmouth_pdf_from_accepted_html.py:31-53` binds the
  accepted HTML identity and Innsmouth print settings; its tests prove that PDF
  presentation may add print-only layout but may not change upstream text.
- `kb_creator/scripts/build_innsmouth_production_package.py:19-118` pins four
  accepted roots, artifact identities, ten script names, and snapshot contents;
  `:183-217`, `:225-240`, and `:385-429` show reusable provenance, asset-closure,
  inventory, and seal mechanics; `:432-516` shows atomic no-overwrite build and
  fail-closed verification.
- Representative tests under `kb_creator/tests/test_build_innsmouth_*`,
  `test_freeze_innsmouth_*`, and
  `test_build_innsmouth_production_package.py` require determinism, exact
  upstream identity, refusal to overwrite, no missing/extra assets, semantic
  anchor integrity, physical PDF boundaries, exact TOC destinations, and
  rejection of mutations.
- `kb_creator/inputs/innsmouth/*/accepted_20260830_r6/*.acceptance.json`,
  `pdf/accepted_20260830_r7/PDF.acceptance.json`, and
  `production/PRODUCTION_MANIFEST.json` demonstrate the existing manifest data
  contracts. They are evidence, not schemas to copy verbatim.
- `translator/config/viral.package.json` was inspected only as legacy evidence.
  It binds the admitted source hash/size and demonstrates Viral-specific page
  roles, visual-first pages, 39 handouts, two statblock pages, OCR zones,
  two-column print choices, callout rules, list-continuation exceptions, and
  historical gates. It is not authority: it also contains old output paths,
  `production_approved: false`, an unresolved list repair, and inconsistent
  release/PDF requirements. No field is imported automatically.

### Confirmed Viral facts used by this design

- Scenario identity is exactly `Viral` / `viral`.
- The immutable external source is 20,718,150 bytes, SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
  124 unrotated English Letter pages.
- Scope is all pages: front matter, scenario body, 39 numbered player handouts,
  Keeper maps, pre-generated investigators, and back cover.
- Required publication chain is new `MASTER_EN`, new `MASTER_RU`, HTML, PDF,
  and stable unversioned production.
- Historical translations are reference evidence only.
- Leading reconstruction risks are multi-column order, 1,739 corrupt
  CJK/Hangul substitutions across 79 pages, 20 zero-text pages (page 1 and
  pages 105-123), 18 other low-text pages, and visual-first maps, handouts, and
  investigator sheets.

### Assumptions requiring review

1. The fixed seven-stage graph is product policy for the Viral proof. A future
   different graph requires a new architecture decision, not a free-form graph
   in `ScenarioContract.v1`.
2. Source PDF path is a locator, not identity. Builds may resolve an external
   path supplied by CLI/environment, but must verify the contract hash, byte
   count, and page count before reading it.
3. Exact stable Viral HTML/PDF filenames are not yet user-approved. The
   contract requires them before a render build; `Viral_RU.html` and
   `Viral_RU.pdf` are proposed defaults only.
4. Reconstruction may use OCR only with page/region provenance. It is not a
   license to replace source geometry or visual-only pages with invented text.
5. Exact generated counts that cannot be known before a build belong to the
   candidate/acceptance manifest. Source-known requirements (124 pages, 39
   handouts, declared page ranges) belong in the contract.

## Root cause and boundary

The current problem is not the number of scripts alone. Scenario facts and
generic lifecycle mechanics share the same modules and therefore share change
risk:

```text
Innsmouth facts
  paths + hashes + page repairs + TOC/anchors + art owners + counts + CSS
                              |
                              v
trusted mechanics
  parse + build + inventory + promote + verify + package + evidence
```

Copying and renaming the modules for Viral would duplicate both halves. Fixes
to identity checks, atomic promotion, or asset closure would then have to be
made in two script families; scenario corrections would be difficult to
distinguish from lifecycle changes.

The remediation boundary is:

```text
reviewed ScenarioContract.v1 data
  -> closed loader/validator
  -> fixed reusable stage handler
  -> candidate manifest
  -> explicit freeze/promote
  -> self-contained accepted package + acceptance manifest
```

## Responsibility matrix

| Concern | Generic reusable code | Scenario contract | Evidence/manifest |
|---|---|---|---|
| Stage order and allowed transitions | Fixed graph and transition validator | No custom graph | Candidate and acceptance state |
| Source resolution | CLI/path resolver; read-only open | External locator kind, hash, bytes, pages, media box | Intake verification receipt |
| State roots | Resolve `working`, `inputs/<id>/<stage>`, `production` | Scenario id only | Actual logical paths |
| Output naming | Enforce safe relative names and stable production names | Exact Markdown/HTML/PDF filenames | File inventory |
| Build/freeze/verify | Deterministic handlers, atomic staging, no overwrite | Stage gates and named strategy profiles | Candidate/acceptance manifests |
| Canonical identity | SHA-256, canonical JSON, inventory algorithms | Source identity and expected contract revision | Artifact, upstream, contract, QA hashes |
| Page coverage | Closed interval/coverage validator | Complete 1..N role partition | Per-page reconstruction inventory |
| Page meaning | Taxonomy enum | Role ranges and reviewed traits | Per-page QA results |
| Text reconstruction | Parser, page/region provenance, unexpected-script audit | Named extraction policy, allowed scripts, exact scoped repairs | Per-page/block source links |
| OCR | Engine adapter and provenance schema | Pages/regions/strategy and language; never executable command | Input image, engine/settings, output and review hashes |
| Publication projection | Common Markdown/anchor/link/table validators | Scope, exact semantic maps, suppressions and match counts | Transformation receipt and full-scope counts |
| Translation | Unit lineage and structural parity checks | `en -> ru`, authorities, reference-only sources, glossary paths | Unit/source hashes, terminology QA, user acceptance |
| Art/assets | Inventory, decode, reference and closure checks | Source roles, owner anchors, allowed placements | Asset manifest with provenance and hashes |
| HTML | Generic Markdown renderer and link/asset verifier | Named presentation profile plus exact owner/page exceptions | HTML QA and accepted RU identity |
| PDF | Generic browser/print adapter and physical-page verifier | Named print profile, page-break/full-width exceptions | PDF QA, render inventory, link destinations |
| Acceptance | Validate authority, explicit identities and evidence completeness | Required authority/gates per stage | Immutable acceptance manifest |
| Production | Stable assembly, one asset union, code/contract snapshot, exact inventory | Package display id and filenames | Production manifest |
| Release | Freeze validation and evidence collector | Intentional exclusions only | Independent critic release receipt |

No scenario contract field may weaken source identity, accepted-upstream
identity, no-overwrite promotion, generated-output immutability, full-scope
coverage, or independent release review.

## Proposed repository topology

The first implementation should use these paths:

```text
kb_creator/
  contracts/
    scenario_contract.v1.schema.json
    innsmouth.json                 # shadow compatibility contract
    viral.json                     # reviewed Viral intake contract
  scripts/
    scenario_contract.py           # stdlib loader + closed semantic validator
  tests/
    test_scenario_contract.py
```

Later reusable stage modules may be introduced under
`kb_creator/scripts/scenario_pipeline/`, but that package is not part of the
first slice. Existing Innsmouth scripts remain untouched and authoritative
until parity evidence exists. Viral must not receive
`build_viral_*`/`freeze_viral_*` copies.

Every accepted stage created by the generic route contains a byte-exact
`SCENARIO_CONTRACT.json` snapshot. Production contains that snapshot plus the
schema and the exact owning generic code. Historical acceptance is therefore
verifiable without assuming that the current working contract is unchanged.

## `ScenarioContract.v1` shape

Illustrative topology (values omitted where review is still required):

```json
{
  "schema": "kb_creator.scenario_contract.v1",
  "contract_revision": 1,
  "scenario": {
    "id": "viral",
    "title": "Viral",
    "product_type": "coc_scenario",
    "source_language": "en",
    "publication_languages": ["en", "ru"]
  },
  "source": {
    "kind": "external_pdf",
    "locator_hint": "Call_of_Cthulhu_Viral.pdf",
    "sha256": "0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05",
    "byte_count": 20718150,
    "page_count": 124,
    "page_number_base": 1,
    "media_box_points": [612, 792],
    "rotation_degrees": 0
  },
  "scope": {
    "mode": "all_source_pages",
    "first_page": 1,
    "last_page": 124,
    "required_entities": {"numbered_player_handouts": 39}
  },
  "page_roles": [],
  "artifacts": {
    "reconstructed_en": "RECONSTRUCTED_EN.md",
    "master_en": "MASTER_EN.md",
    "master_ru": "MASTER_RU.md",
    "html": "<review-required>",
    "pdf": "<review-required>",
    "production_manifest": "PRODUCTION_MANIFEST.json"
  },
  "policies": {
    "reconstruction": {},
    "publication": {},
    "translation": {},
    "visual": {},
    "navigation": {},
    "render": {}
  },
  "acceptance": {},
  "exceptions": []
}
```

### Required fields, types, and invariants

| Field | Type | Invariant |
|---|---|---|
| `schema` | enum string | Exactly `kb_creator.scenario_contract.v1` |
| `contract_revision` | integer | `>=1`; increase when reviewed contract data changes after first use |
| `scenario.id` | string | Lowercase `[a-z0-9]+(?:-[a-z0-9]+)*`; equals directory id |
| `scenario.title` | non-empty string | Human title only; never used as an unchecked path |
| `product_type` | enum | Only `coc_scenario` in v1 |
| languages | BCP-47-like enum | v1 admits source `en` and publication `en`,`ru` only |
| `source.kind` | enum | `external_pdf` only in v1 |
| `source.locator_hint` | basename string | No absolute durable path; runtime path is supplied separately |
| source identity | uppercase SHA-256, positive bytes/pages | All must match before any extraction |
| geometry | two positive numbers + rotation enum | Viral requires 612x792 pt, 0 degrees |
| `scope.mode` | enum | `all_source_pages` for Viral; cannot be weakened by exception |
| scope bounds | positive integers | Equal source page domain for all-pages mode |
| `page_roles` | array | Exactly one primary role covers every page; no gap/overlap |
| artifact names | safe relative basenames | No drive, `..`, slash, accepted/date/release suffix; unique |
| policy profiles | closed objects/enums | Unknown keys rejected; no commands/import paths/code |
| `acceptance` | fixed stage-key object | Every stage declares required automated gates and approval authority |
| `exceptions` | array of closed objects | Unique ids, exact stage/scope/operation/match count/rationale/evidence |

The JSON Schema rejects unknown top-level and nested keys
(`additionalProperties: false`). The Python semantic validator enforces
cross-field rules JSON Schema cannot express: complete page partition, unique
filenames, legal transition references, non-overlapping selectors, exception
match-count requirements, full-scope policy, and prohibited weakening.

## Page-role taxonomy

Use one primary source role per page. Text/visual behavior is an orthogonal
`content_mode`, not another role.

Primary roles proven necessary by Viral:

| Role | Viral evidence | Required closure |
|---|---|---|
| `cover` | page 1 | Visual representation, title/source provenance |
| `credits` | front matter | Semantic credits or reviewed visual preservation |
| `front_matter` | opening/content-warning material | Every block accounted for; publication suppressions explicit |
| `contents` | source contents | Source entries mapped to semantic reader navigation |
| `scenario_body` | pages 6-68 | Ordered text, tables, statblocks, rules, art |
| `player_handouts` | pages 69-103 | All 39 ids mapped; mixed text/image content retained |
| `keeper_maps` | pages 104-110 | Map identity, labels, usability, full visual closure |
| `pregenerated_investigators` | pages 111-123 | Complete sheets, stats, backstory and visual form |
| `back_cover` | page 124 | Visual/text preservation and intentional publication placement |

Allowed `content_mode` values are `text`, `mixed`, `visual`, and `unknown`.
`unknown` is permitted at intake only and blocks reconstruction acceptance.
Traits are a closed set: `multi_column`, `low_text`, `zero_text`,
`table_heavy`, `statblock`, and `form_like`. Traits trigger QA; they do not
authorize omission.

`full_art` and `statblock_card` from the legacy Viral config are not promoted
to primary roles: full art is a content mode/asset role, and a statblock is a
semantic block within its owning source page. This avoids overlapping page
taxonomies without losing the observed risk.

Initial Viral role ranges must cover exactly 1-124. The accepted context
supports `scenario_body` 6-68, `player_handouts` 69-103, `keeper_maps` 104-110,
`pregenerated_investigators` 111-123, and `back_cover` 124. Pages 1-5 require a
reviewed cover/credits/front-matter/contents partition before the concrete
contract passes the reconstruction-ready profile; no legacy mapping is copied
without current source evidence.

## Fixed stage contracts

| Stage | Required input identity | Candidate output | Freeze input | Accepted output / next consumer |
|---|---|---|---|---|
| `reconstructed_en` | Contract snapshot + source PDF hash/bytes/pages | Markdown, assets, per-page/block provenance, QA, candidate manifest | Exact candidate-manifest hash and completed full-scope QA | Immutable reconstruction package -> `master_en` |
| `master_en` | Accepted reconstruction manifest + bundled contract hash | Reader EN, selected assets, transformation receipt, QA | Exact candidate and explicit configured acceptance | `MASTER_EN` package -> `master_ru` |
| `master_ru` | Accepted current `MASTER_EN`, terminology authorities, new translation candidate | Reader RU, selected assets, unit/anchor/term QA | Exact candidate and explicit user reading acceptance | `MASTER_RU` package -> `html` |
| `html` | Accepted `MASTER_RU` manifest | Self-contained generated HTML, assets, link/layout QA | Exact candidate and explicit user visual/navigation acceptance | Accepted HTML -> `pdf` |
| `pdf` | Accepted HTML manifest | Generated PDF, print QA, render inventory, destination audit | Exact candidate and explicit user print acceptance | Accepted PDF -> `production` |
| `production` | Exact accepted EN/RU/HTML/PDF manifests | Stable package staged outside target | Exact candidate seal and production acceptance | Unversioned production + production manifest |

Every builder refuses an existing candidate root. Every freezer refuses an
existing accepted target and promotes through a sibling staging directory plus
atomic replace. Verifiers never repair and never write.

## State classes and identities

### State classes

```text
external source
  immutable authority, verified before read

working/<scenario>/<stage>/<run-id>/
  rebuildable candidate; never an authority

inputs/<scenario>/<stage>/accepted_<date>[_rN]/
  immutable, self-contained accepted input to the next stage

inputs/<scenario>/production/
  current stable user-facing snapshot; no version suffixes
```

### Build identity

A candidate manifest records:

- schema, scenario id, stage, run id, UTC timestamp;
- byte-exact bundled contract and `contract_sha256`;
- source or accepted-upstream manifest identity;
- owning code identities and relevant tool versions;
- output file identities and canonical inventory SHA-256;
- applied policy profile and exact exception application rows;
- QA artifact identities and gate results;
- state `candidate`, never `accepted`.

The builder must be deterministic for the same contract, upstream package,
owning code, and declared tools. Runtime absolute paths are excluded from
canonical identities and reports except in a non-authoritative diagnostic
field.

### Freeze identity

Freeze takes the expected candidate-manifest SHA-256 as an explicit argument;
`latest` or implicit discovery is invalid. It re-verifies every candidate file,
upstream manifest, contract snapshot, QA result, asset reference, and required
approval. It copies only the declared closed inventory to staging, creates a
canonical acceptance manifest, refuses overwrite, atomically publishes, then
runs verify.

The acceptance manifest records both the input candidate identity and the
accepted file identities. It never relies on a mutable output hash stored in
the working scenario contract.

### Verify identity

Verify starts from the accepted package's own acceptance manifest and bundled
contract snapshot. It rejects missing, changed, or extra files; non-canonical
JSON; wrong state/stage/scenario; contract digest mismatch; upstream provenance
mismatch; stale QA; asset/reference drift; and stage-specific gate failure.
Production verify additionally checks stable names, accepted-manifest closure,
the union asset inventory, owning-code/terminology/schema snapshots, and the
entire package inventory.

### Line-ending serialization prerequisite

Current live evidence found a cross-platform identity failure that must be
resolved before claiming Innsmouth regression green:

- Git attributes currently apply `* text=auto` and no HTML-specific LF rule;
  this worktree has `core.autocrlf=true`.
- The accepted and production Innsmouth HTML is 227,220 CRLF bytes with SHA-256
  `BC66D5A2380288B23B8FBED9E85533EE120010A85E408C8DA5E3925A34DF2B49`.
- Replacing its 1,106 CRLF pairs with LF in memory yields the manifest-bound
  226,114 bytes and SHA-256
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.
- `python -B kb_creator/scripts/build_innsmouth_production_package.py --verify`
  currently fails with `production package file identity mismatch` while Git
  reports no tracked change for the HTML.

The identity algorithm must remain raw-byte SHA-256; silently normalizing in a
verifier would no longer prove the package bytes. The bounded remediation is an
LF checkout rule scoped to `kb_creator/inputs/**/*.html` (or an independently
reviewed equivalent) plus a clean-checkout regression. Do not edit or
re-manifest accepted Innsmouth output to mask this condition.

## Text, OCR, translation, and reference policies

### Reconstruction text policy

- Source geometry and complete page order come from the verified PDF.
- Each output block records source page and, when available, bounding box or
  PDF object/xref provenance.
- Unexpected-script detection is fail-closed for an English source. Viral's
  known CJK/Hangul substitutions seed a full 124-page audit; a repaired sample
  is not closure.
- Multi-column pages require an order decision proven against the page visual.
- Hyphen joining, spacing repair, heading promotion, list continuation, table
  reconstruction, and statblock reconstruction are distinct operation types
  with exact before/after match counts.
- Technical provenance markers remain in reconstruction evidence but are
  removed only at the publication stage.
- Zero-text or visual pages cannot pass because they have no extracted text;
  they require a visual asset and a reviewed semantic/visual disposition.

### OCR policy

OCR is a controlled recovery strategy, not the default authority. Every OCR
row records source PDF identity, page, crop coordinates/full-page flag, rendered
input hash and DPI, language, engine/version, settings/profile, output hash,
replaced source span, and reviewer status. OCR may recover text but may not
invent visual layout, redraw maps, or silently replace embedded text across a
whole page. Zero or multiple selector matches fail.

The contract selects only named strategies such as `embedded_text`,
`reading_order`, `ocr_region`, or `visual_preserve`. It cannot provide an
engine command or arbitrary executable path.

### Publication text policy

`RECONSTRUCTED_EN` answers “what is in the source”; `MASTER_EN` answers “what
is published to the reader.” Source scope, TOC/semantic links, heading levels,
handout deduplication, art ownership, table/statblock presentation, and exact
front-matter suppressions are publication policy. Every source page/block is
accounted for as retained, transformed, relocated, or explicitly suppressed;
suppression requires an exception row and evidence.

Generated HTML and PDF are never edited manually. A defect is fixed in the
contract or owning reusable handler, then rebuilt and re-verified full-scope.

### Translation and reference policy

- The sole translation source is the current accepted `MASTER_EN` bound by its
  acceptance manifest.
- `MASTER_RU` units record current EN source hash and structural owner/anchor.
- Historical EN/RU files may be declared only under `reference_sources` with
  mode `terminology_or_comparison_only`. They cannot appear in a stage input,
  unit lineage, merge source, or acceptance provenance.
- Required authorities are the project CoC 7e terminology and a reviewed
  Viral-specific glossary. Their file hashes are acceptance inputs.
- Structural parity covers semantic units, headings/anchors, handout ids,
  tables, statblocks, links, and asset owners. Exact character counts are not a
  translation parity rule.
- Unresolved terms, untranslated source-mechanics terms, or units with a
  historical-source lineage block promotion.

## Visual and navigation policy

An asset manifest row contains: stable asset id; file identity; MIME/dimensions;
source PDF/page and region/xref/full-page provenance; derivation parent when
cropped/converted; semantic role; owner stage and owner anchor/page role;
allowed placement profile; and review status.

The reusable verifier enforces:

1. every reference resolves to one inventoried file;
2. every packaged asset is referenced or explicitly package-only;
3. referenced file bytes match the manifest;
4. every transformation has a source parent;
5. every source-required visual/page has a closure row;
6. an asset has one semantic owner unless a reviewed reuse exception lists all
   owners;
7. HTML assets equal the accepted RU referenced set unless an exact render-only
   exception exists;
8. production contains one union copy, not per-artifact duplicates;
9. no missing/extra files and no unresolved/pending visual review.

Navigation is semantic. Printed `page N` references do not become broken
reader links. Source TOC entries map to heading-bound anchors; standalone
invisible targets are rejected where a heading target is required. HTML checks
unique ids, fragments, order, assets, tables, handouts, and owner placement.
PDF checks physical title/front-matter/appendix boundaries, no empty pages,
render coverage, internal destinations landing on expected heading text within
a configured tolerance, and full visual inspection of all pages.

Viral-specific print choices—two columns, full-width handout/map/pregen
appendix, page breaks, and statblock-card placement—are named profile settings
plus exact selectors. They are not copied from legacy output as accepted facts;
they require current visual review.

## Exception controls

An exception is data, never code:

```json
{
  "id": "viral-reconstruction-list-continuation-001",
  "stage": "reconstructed_en",
  "kind": "list_continuation",
  "scope": {"pages": [0], "selector": "reviewed semantic selector"},
  "operation": "continue_numbering",
  "expected_matches": 1,
  "rationale": "source list continues across a page boundary",
  "evidence": ["review receipt or source-page reference"],
  "approval": "required"
}
```

The concrete page/selector above is illustrative, not an accepted Viral
exception. The legacy config's unresolved continuation cannot be imported.

Allowed exception kinds in v1 are limited to proven needs:
`text_repair`, `reading_order`, `list_continuation`, `publication_suppression`,
`semantic_link`, `asset_owner`, `render_placement`, and `page_break`.
Adding a new kind requires schema, handler, tests, and architecture review.

Every exception must be stage-scoped, source-scoped, reasoned, evidenced,
match-counted, and approval-gated. Application receipts list actual matched
pages/anchors/assets and before/after identities. Zero matches, extra matches,
or scope escape fail the build.

Forbidden exceptions include skipping source hash checks, weakening all-pages
coverage, accepting extra files, bypassing upstream acceptance, using old RU as
translation source, permitting manual generated-output edits, suppressing open
blockers, or bypassing independent release review.

## Acceptance gates and full-scope evidence

| Boundary | Automated gate | Human authority/evidence |
|---|---|---|
| Source intake | Hash/bytes/pages/geometry/encryption and contract validation | Confirmed scenario/source/scope decision |
| Reconstruction | 124/124 page inventory; complete role partition; glyph/order/OCR provenance; 39 handouts; maps/pregens/back cover; text/table/statblock/asset closure; zero unknown page modes/open blockers | Reviewed reconstruction QA; configured promotion authority |
| `MASTER_EN` | Accepted reconstruction provenance; every source block dispositioned; semantic links/anchors; handout map; tables/statblocks; assets; no technical reader noise | Explicit user reading acceptance |
| `MASTER_RU` | Current accepted EN lineage; unit/structure parity; glossary hashes; terminology and untranslated-term gates; assets/links | Explicit user reading acceptance |
| HTML | Exact accepted RU; deterministic output; zero broken fragments, missing/unused assets, duplicate ids, manual edits; TOC destinations and presentation counts from candidate evidence | Explicit user visual/navigation acceptance |
| PDF | Exact accepted HTML; print-only delta; all pages rendered; no blank pages; destinations/heading landing; physical section boundaries; full visual QA | Explicit user print acceptance |
| Production | Exact four accepted packages; stable names; one asset union; contract/schema/code/terminology snapshots; exact closed inventory; reproducible verify | Explicit production snapshot acceptance |
| Release | Frozen production manifest/SHA; no post-freeze mutation; all QA and intentional exclusions; implementer/designer declaration | Fresh independent `gpt-5.5` release review |

Full-scope QA treats every defect example as a seed. Each finding records defect
class, earliest failing layer, complete search scope, owning fix, rebuild id,
and closure evidence. Stage promotion fails while the blocker ledger has any
open in-scope item. Counts are derived from the complete candidate and frozen
into its manifest; generic code has no Innsmouth/Viral count constants.

## Production and release evidence

The production seal must contain:

- stable `MASTER_EN.md`, `MASTER_RU.md`, reviewed HTML and PDF names;
- one shared asset union with provenance/closure manifest;
- all four accepted input-manifest identities;
- byte-exact `SCENARIO_CONTRACT.json` and schema;
- exact owning generic stage code and required terminology snapshots;
- candidate and final package inventories with SHA-256;
- full-scope text, visual, navigation, OCR, translation, HTML and PDF QA
  identities;
- acceptance authorities/dates and intentional exclusions;
- environment/tool identities required for reproducibility, without local
  secrets or absolute-path authority.

The independent release receipt binds the frozen production manifest and
inventory hash. Any artifact, asset, contract, owning-code, terminology, or QA
mutation invalidates that receipt.

## Migration and integration strategy

1. **Validate the boundary without runtime migration.** Add the closed schema,
   loader, shadow Innsmouth contract, Viral contract, and contract tests. Do not
   change existing stage scripts or outputs.
2. **Resolve LF serialization regression.** Add an LF attribute scoped to
   `kb_creator/inputs/**/*.html`, prove the manifest-bound HTML bytes in a clean
   checkout, and run the existing production verifier. Do not re-freeze or edit
   Innsmouth packages.
3. **Extract generic lifecycle primitives.** Move/copy only well-proven pure
   mechanics—canonical JSON, file/inventory identity, safe path resolution,
   no-overwrite staging, manifest validation—into reusable modules with
   fixture tests. Existing scripts continue to call their current code until
   parity is proven.
4. **Migrate one boundary at a time.** For each stage, add a generic handler,
   run Innsmouth through a contract adapter against a temporary candidate, and
   compare manifest/content identities or documented semantic equivalence.
   Keep the accepted/production trees read-only.
5. **Preserve compatibility.** Existing Innsmouth script names remain usable.
   Only after parity may a legacy entry point become a thin wrapper around the
   generic handler. Do not rename/delete all 23 scripts in one change.
6. **Use only the generic route for Viral.** The CLI shape may become
   `kb_scenario.py --contract ... --stage ... --action build|freeze|verify`.
   There is no `build_viral_*` family.
7. **Snapshot the actual owner.** New production packages include the generic
   code, schema and exact contract; legacy translator modules are included only
   if the generic route actually imports them. The legacy Viral package is
   never a runtime dependency.

Innsmouth behavior is preserved until all existing Innsmouth tests and five
stage/production verifiers pass from a clean LF-stable checkout. Semantic
parity is insufficient for manifest-bound artifacts unless a reviewed
migration explicitly creates a new accepted candidate; no such re-acceptance
is in the current goal slice.

## First bounded implementation slice

### Owned change set for the future engineering step

Add:

1. `kb_creator/contracts/scenario_contract.v1.schema.json`
2. `kb_creator/contracts/innsmouth.json`
3. `kb_creator/contracts/viral.json`
4. `kb_creator/scripts/scenario_contract.py`
5. `kb_creator/tests/test_scenario_contract.py`

Modify:

6. `.gitattributes` — add an LF rule scoped to tracked HTML under
   `kb_creator/inputs/` after engineering confirms the exact Git pattern.

Do not change any existing Innsmouth stage script, accepted package,
production package, generated output, canonical goal state, or translator
config in this slice.

### Module responsibilities

`scenario_contract.py` uses Python stdlib only. It loads UTF-8 JSON, verifies
canonical/closed structure, applies semantic invariants, returns immutable
typed views or plain frozen structures, resolves runtime source paths without
including them in the contract digest, computes the canonical contract
SHA-256, and exposes validation profiles `intake` and
`reconstruction_ready`. It does not build, freeze, render, translate, or write.

`innsmouth.json` is a shadow compatibility fixture assembled only from current
accepted manifests and script constants. It is not wired into runtime. If a
required field lacks authoritative evidence, implementation stops rather than
guessing.

`viral.json` records only the confirmed intake and reviewed topology/policies.
It may retain `unknown` content modes under the intake profile; it may not pass
`reconstruction_ready` until pages 1-5 and all page modes/policies are closed.

### Tests to add

- schema and semantic validation passes for both reviewed contracts;
- unknown keys, unsafe ids/names, absolute durable locators, invalid hashes,
  wrong page counts, range gaps/overlaps, duplicate filenames, unrecognized
  roles/policies, executable fields, and forbidden exception kinds fail;
- Viral identity is exactly the admitted hash/bytes/124 pages and all-pages
  scope; page roles cover 1-124 once; 39 handouts are required;
- historical sources can be reference-only and cannot be stage inputs;
- contract canonicalization/digest is deterministic and independent of runtime
  absolute path;
- intake may contain declared unknown page modes but
  `reconstruction_ready` rejects them;
- the Innsmouth shadow fixture matches existing source/accepted manifest facts
  selected for compatibility, without becoming runtime authority;
- the existing Innsmouth test suite remains unchanged;
- a clean-checkout LF test proves tracked accepted/production HTML raw bytes
  match their manifests, followed by the existing production verifier.

### Acceptance evidence for the slice

1. Exact changed-file allowlist equals the six paths above.
2. New contract tests pass with no network and no generated repo output.
3. Existing Innsmouth focused/full regression passes unchanged.
4. Existing EN/RU/HTML/PDF/production verifiers pass in the LF-stable checkout.
5. Hash comparison proves all accepted/production Git blob identities remain
   unchanged; the slice does not re-freeze them.
6. `rg` finds no `build_viral_` or `freeze_viral_` script family and no import
   of `translator/config/viral.package.json`.
7. A fresh independent architecture/implementation review finds no scope
   expansion or policy bypass.

### Stop conditions

Stop and return to the orchestrator if:

- authoritative Innsmouth or Viral facts needed by a required field conflict
  or are absent;
- an LF attribute would alter Git blob content rather than only checkout
  serialization;
- any accepted/production Innsmouth file shows a Git-content mutation;
- the loader needs an executable/config plugin field or a dependency beyond
  stdlib solely to satisfy the proposed schema;
- a Viral policy cannot be expressed by the closed proven enum set;
- a contract exception would bypass identity, coverage, provenance, manual-edit
  prohibition, or release review;
- any existing Innsmouth regression remains red after the independently scoped
  LF fix;
- implementation would require source copy, extraction, OCR, translation,
  rendering, or generated output before Step 4 accepts the architecture.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Contract becomes a second program | Unreviewable behavior and injection surface | Closed enums, no commands/imports/templates, unknown keys fail |
| Counts are pinned too early | False gates based on legacy output | Source-known minima in contract; generated counts in candidate/acceptance manifests |
| Contract grows into legacy Viral config | Stale paths/gates and contradictory authority | Import nothing; admit each field from current evidence only |
| Over-generalizing page roles | Conflicting/overlapping classification | One primary role plus orthogonal mode/traits |
| Exception list hides systematic defects | One-off patches replace pipeline ownership | Exact match receipts, defect-class audit, new operation kind requires code/review |
| Current contract drift breaks old acceptance | Historical packages no longer verifiable | Bundle exact contract/schema in every accepted package |
| Platform line endings break byte identity | Clean Git state but verifier failure | LF checkout rule and raw-byte verification; no verifier normalization |
| Shadow Innsmouth contract becomes authority early | Regression or accidental re-freeze | No runtime wiring in first slice; existing scripts remain authority |
| Big-bang script replacement | Hard-to-review regression across 23 modules | Stage-by-stage adapter and parity evidence |
| Asset union assumptions copy 33/32 counts | Viral assets silently lost/extra | Compute closure from manifests; counts are scenario evidence, not generic constants |
| Historical RU contaminates new translation | New master lineage invalid | Reference-only type and lineage gate |
| Visual-only pages pass text QA | Maps/pregens/back cover omitted | Role/mode closure plus full-page visual inventory and visual QA |
| PDF QA checks only text | Broken maps, columns or handouts escape | Full render inventory, visual review, physical boundaries and link landings |

## Rejected alternatives

1. **Copy and rename 23 scripts for Viral.** Rejected because it duplicates
   lifecycle defects and violates the goal's Definition of Done.
2. **Use `translator/config/viral.package.json` as the new contract.** Rejected
   because translator is legacy evidence, the file has stale output topology
   and unresolved/contradictory state, and it exposes far more behavior than
   the proven boundary.
3. **Put the whole stage DAG and engine commands in JSON.** Rejected as
   premature generality and an executable configuration surface.
4. **Store accepted output hashes in the working scenario contract.** Rejected
   because build results would mutate policy data and historical acceptance
   would depend on current config.
5. **Normalize line endings inside verification.** Rejected because a
   byte-exact production manifest must prove actual bytes, not semantic text.
6. **Make every visual/statblock type a page role.** Rejected because those
   concerns overlap primary document topology; modes/traits and block/asset
   manifests model them without ambiguity.
7. **Delete or rename Innsmouth scripts during first implementation.** Rejected
   because compatibility has not been proven and accepted packages snapshot
   those owners.
8. **Adopt a global contract/goal database or migrate historical projects.**
   Rejected by goal governance and current scope.

## Unresolved decisions for Step 4/orchestrator

1. Approve or change the proposed stable Viral HTML/PDF filenames.
2. Confirm the exact pages 1-5 primary-role partition and all page content
   modes before `viral.json` is reconstruction-ready.
3. Decide whether reconstruction freeze requires explicit user promotion or a
   technical QA/orchestrator acceptance followed by user review at
   `MASTER_EN`; the contract supports either but must declare one authority.
4. Review the precise scoped `.gitattributes` pattern for LF HTML checkout and
   require clean-checkout evidence before implementation acceptance.
5. Decide whether `SCENARIO_CONTRACT.json` is copied into every accepted stage
   root (recommended) or embedded canonically in each acceptance manifest. The
   former is easier to inspect and hash independently.
6. Confirm whether production snapshots only actually imported translator
   modules (recommended) or preserves the current broader snapshot for
   compatibility until a later migration.

These decisions do not block independent architecture review. Material
implementation remains blocked until Step 4 resolves P0/P1 findings and the
orchestrator records the accepted decision in canonical state.

## Architecture acceptance criteria

This specification is acceptable for Step 3 when an independent critic finds:

- the boundary is data-versus-mechanics, not a renamed script family;
- all required source, stage, state, identity, policy, exception, asset, QA,
  acceptance, and release contracts are fail-closed;
- Viral-specific facts are grounded in current intake or explicitly unresolved;
- legacy translator evidence is not treated as authority or runtime input;
- Innsmouth remains untouched and migration is incremental;
- the first implementation slice has an exact file allowlist, tests, evidence,
  and stop conditions;
- the live LF identity regression is handled as a prerequisite without
  re-manifesting accepted artifacts;
- no implementation, generation, source processing, Git mutation, or release
  acceptance is implied by this document.
