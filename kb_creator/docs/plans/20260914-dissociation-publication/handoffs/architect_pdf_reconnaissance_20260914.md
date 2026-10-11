# Architect receipt - Dissociation PDF reconnaissance

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `1-read-only-pdf-reconnaissance`
- Role: architect
- Requested model: `gpt-5.6-sol`
- Requested reasoning effort: `high`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Assignment state: `platform-unverified`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform identity unverified
- Scoped override: none
- Scope: read-only structural, text-layer, navigation, object, and visual reconnaissance of the immutable `Dissociation.PDF`; no MinerU run and no source copy or mutation
- Result: complete for contract drafting. The contract-ready source facts, gap-free candidate page-role partition, entity count, and mandatory reconstruction risks are recorded below. This is not reconstruction acceptance or a release decision.
- Timestamp: `2026-09-14T03:08:00+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:10:00`
- Token use: unavailable

## Files checked or changed

Checked:

- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md` (active Dissociation goal section)
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `C:/Users/user/.codex/plugins/cache/openai-primary-runtime/pdf/26.909.12148/skills/pdf/SKILL.md`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/scripts/scenario_contract.py` source-validation, role-partition, and runtime-resolution paths
- external source, read-only: `C:\_Hobby\Yandex.Disk\НРИ\1_Зов Ктулху\temp\маленькие иголочки страха\Dissociation.PDF`

Changed:

- added this receipt only: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_pdf_reconnaissance_20260914.md`

The canonical plan, context, project status, contract, release files, source PDF, and production artifacts were not changed.

## Contract-ready facts

These facts are directly supported by two or more of OS identity, pypdf,
pdfplumber, Poppler inspection, and page renders. They can be used without
copying topology from another scenario.

### Source and scope

| Field | Value | Evidence note |
|---|---:|---|
| Actual source basename | `Dissociation.PDF` | OS path; uppercase extension is real |
| Byte count | `2159317` | `Get-Item` and full hash read |
| SHA-256 | `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B` | live `Get-FileHash`; matches intake |
| PDF version | `1.7` | Poppler `pdfinfo` |
| Encryption | none | Poppler `pdfinfo` |
| Physical page count | `6` | Poppler, pypdf, and pdfplumber agree |
| Contract page number base | `1` | physical-page domain; do not use PDF labels or printed folios |
| Contract scope | physical pages `1-6`, all source pages | exact full-source partition |
| MediaBox | `[0, 0, 595, 841]` points on all six pages | pypdf and pdfplumber agree |
| `media_box_points` | `[595, 841]` | width and height derived from MediaBox |
| CropBox | `[0, 0, 595, 770]` points on all six pages | 71-point vertical difference from MediaBox |
| BleedBox / TrimBox / ArtBox | `[0, 0, 612, 792]` on all six pages | wider than the MediaBox; do not substitute for contract geometry |
| Rotation | `0` degrees on all six pages | Poppler, pypdf, and pdfplumber agree |
| Numbered player handouts | `0` | complete six-page visual review plus extracted-text search |

The schema's `locator_hint` pattern requires a lowercase `.pdf` suffix, while
the actual immutable file ends in `.PDF`. Use the schema-compatible logical
hint `Dissociation.pdf`; do not rename the source. The current
`resolve_source_path` implementation binds the runtime file by byte count,
SHA-256, page count, MediaBox, and rotation and does not compare the runtime
basename to `locator_hint`. Its Python validator also accepts the uppercase
suffix, but the JSON Schema pattern does not; validating through both paths
requires the normalized hint.

### Candidate contract page-role partition

This partition is gap-free, non-overlapping, covers `1-6`, and uses only facts
visible in this source. It is suitable for the first Dissociation runtime
contract draft:

| Role | Pages | Content mode | Traits | Strategies |
|---|---:|---|---|---|
| `cover` | `1-1` | `visual` | `low_text` | `embedded_text`, `visual_preserve` |
| `scenario_body` | `2-4` | `mixed` | `multi_column` | `embedded_text`, `reading_order`, `visual_preserve` |
| `scenario_body` | `5-5` | `mixed` | `multi_column` | `embedded_text`, `reading_order`, `ocr_region`, `visual_preserve` |
| `scenario_body` | `6-6` | `mixed` | `multi_column`, `statblock` | `embedded_text`, `reading_order`, `visual_preserve` |

There are no separate credits, contents, front-matter, player-handout,
keeper-map, pregenerated-investigator, or back-cover pages in this six-page
source. Page 5 contains a large Alaska map/tourism-ad graphic inside the
scenario body; it is not a standalone map page and it has no numbered handout
label. Page 6 contains a `HUMAN RESISTANCE` rules statblock.

### Numbering domains

- Physical pages for the contract and reconstruction: `1-6`.
- PDF page labels: `A`, `1`, `2`, `3`, `4`, `5`.
- Printed source folios: cover has no folio; physical pages 2-6 show `113-117`.

These domains must remain distinct. Page markers and provenance should use the
physical `1-6` domain.

## Verification and evidence

### Metadata and document structure

- Info/XMP creation: `2018-06-26T01:08:33-04:00`.
- Info/XMP modification: `2018-06-26T01:55:21-04:00`.
- No title, author, or subject metadata is populated; author/title visible on
  the cover must come from page content, not document metadata.
- PDF is untagged, non-linearized, has no JavaScript, and has no embedded files.
- Page layout is `/SinglePage`; page mode is `/UseNone`.
- `/AcroForm` exists but `/Fields` is empty: zero logical fields, zero widget
  annotations, and no form-like page. Treat this as inert inherited structure,
  not an interactive form requirement.
- All page rotations are zero and all MediaBox/CropBox values are uniform.

### Text-layer coverage and quality

| Physical page | pdfplumber character objects | Non-whitespace characters | Extracted word objects | Assessment |
|---:|---:|---:|---:|---|
| 1 | 63 | 59 | 17 | sparse cover text; illustration is dominant |
| 2 | 5379 | 4538 | 877 | substantial embedded prose text |
| 3 | 5083 | 4298 | 816 | substantial text plus names/occupations card |
| 4 | 5530 | 4625 | 942 | substantial embedded prose text |
| 5 | 1936 | 1618 | 328 | text in upper columns; map/ad text is raster-only |
| 6 | 2493 | 2110 | 406 | text plus statblock; lower half intentionally sparse |

- pypdf and pdfplumber produced identical non-whitespace counts per page.
  Poppler counts were within 0-32 characters of those values on body pages.
- No Unicode replacement characters were observed in any extractor.
- `pdffonts` reported 21 font resource rows; all were embedded, subset, and
  Unicode-mapped.
- The embedded layer is therefore usable as a textual source for pages 2-6,
  but not as layout authority. Plain extraction interleaves left and right
  columns at shared baselines, joins running headers/footers to body text, and
  preserves line-end hyphenation as split words (`cer- tain`, `mi- go`, etc.).
- Page 5's map, labels, advertisement copy, and contact details are pixels in a
  large embedded image and require region OCR plus visual preservation.

### Visual and reading-order topology

All six pages were rendered successfully from the full MediaBox and inspected.
A second contact-sheet render used the CropBox to expose box-dependent content.

- Page 1: full-page illustrated cover with `DISSOCIATION`, `by Matthew
  Sanderson`, and the thematic labels `HIDDEN ENEMY`, `SENSORY CONFUSION`,
  `MI-GO`, and `ISOLATION`.
- Page 2: two-column body beginning `Introduction`; left column continues
  through `Involving the Investigators` and `Abduction`, while the right column
  continues the abduction and then `Dreamscape` / `Environment One`.
- Page 3: two columns with a black `NAMES` / `OCCUPATIONS` callout inside the
  left column and `Examining Vessels`, `Vessel Termination`, `Dreamscape
  Interlude`, and `Environment Two` on the right.
- Page 4: two columns; `Bomb` and `Test Subjects` on the left and
  `Dreamscape Interlude`, `Environment Three`, and `Investigation` on the
  right. No conventional table or separate art asset is visible.
- Page 5: two short upper text columns followed by the `Laboratory` heading and
  a large full-width Alaska map/tourism-ad graphic occupying most of the lower
  page. Text-to-asset ownership and reading order must be explicit.
- Page 6: two upper columns; `The Scientist` and `Survivors` at left,
  `Rewards and Repercussions` and a `HUMAN RESISTANCE` statblock at right;
  intentionally large blank/decorative lower region.

The CropBox render removes the 71-point top band and therefore hides the red
running title on body pages. The MediaBox render retains it and matches the
contract geometry. Reconstruction must not silently switch to CropBox.

### Outline, links, labels, and inherited object residue

- There are no page link annotations, no named destinations, and no other page
  annotations on the six retained pages.
- The outline contains 28 entries inherited from the anthology. Only
  `DISSOCIATION` resolves to a retained page (physical page 1); the other 27
  target page objects absent from this six-page page tree.
- `/OpenAction` is a `/GoTo` action whose target dereferences to `NullObject`.
- The `/Names` dictionary is empty.
- The document has an xref length of `16862`; retained page object ids are
  `6652`, `6778`, `6786`, `6793`, `6801`, and `6807`. This, the stale outline,
  and the inert AcroForm show that the file is an extracted anthology subset
  with inherited structural residue.
- Source outline, page labels, and open action are not navigation authority.
  Navigation must be rebuilt from reconstructed headings.

### Image and object distribution

`pdfimages -list` reports low-level image/smask rows, while pdfplumber reports
rendered image placements. Neither count is a semantic asset count.

| Page | Low-level rows | Images | Soft masks | Rendered placements |
|---:|---:|---:|---:|---:|
| 1 | 144 | 88 | 56 | 29 |
| 2 | 10 | 6 | 4 | 5 |
| 3 | 9 | 6 | 3 | 5 |
| 4 | 8 | 5 | 3 | 4 |
| 5 | 9 | 6 | 3 | 5 |
| 6 | 11 | 7 | 4 | 5 |

Every page includes a near/full-page raster composite plus decorative strips;
page 1 additionally decomposes the cover into many small masked components.
Page 5 adds a `1009 x 916` map/ad image. Direct-XObject counts must not be used
as required-asset counts: masks, repeated strips, composites, and semantic art
must be reconciled through the three-view comparison.

### Parser anomaly

Poppler repeatedly reports at byte offset `1604508`:

- `Illegal character ')'`
- `Unterminated string`
- `Unknown operator ','`
- `Leftover args in content stream`

The PDF still renders and all three text readers return text. This is a source
content-stream anomaly, not evidence that the source is unreadable. Page 1 is
the highest-risk page because of its complex object/mask structure. Three-view
comparison must preserve a rendered-page fallback and record any parser/view
disagreement instead of normalizing it away.

## Contract hypotheses and facts that remain unknown

The following are deliberately not promoted to facts before MinerU and
three-view review:

- Whether the page 5 Alaska map/ad should be reader-visible art, an in-world
  unnumbered handout, keeper-only context, or a non-reader publication asset.
  It remains a page-5 scenario-body asset for contract topology.
- The final semantic asset count and whether each page composite, decorative
  strip, mask, or cover component should be retained, deduplicated, or treated
  as background.
- Exact heading hierarchy below the visible section titles, including whether
  `NAMES` / `OCCUPATIONS` is a card, table, or styled callout in the candidate.
- Exact reading order at every column break, especially page 2's split
  `Abduction`, page 3 around the black callout, and page 5 above the large map.
- Whether raster map text should be transcribed into accessible prose in
  addition to preserving the image.
- Exact reconstruction exceptions. No exception has enough closed evidence at
  reconnaissance time.
- Any publication suppression of running headers, thematic footers, printed
  folios, decorative backgrounds, or the page 6 blank lower area. Publication
  decisions are outside this step.

## Dependency and branching analysis

1. Contract materialization depends on the physical page domain and MediaBox,
   not the PDF labels, printed folios, CropBox, or anthology outline.
2. Three-view preparation depends on a fresh hash-bound read of the external
   source. The path is a readable Yandex Disk reparse point; later intake must
   fail closed if the bytes are unavailable or change.
3. Embedded-text reconstruction is viable for prose, but every body page
   requires explicit column reading order. A plain text dump is not a valid
   candidate.
4. Visual reconstruction must preserve the page-1 cover, page-3 card, page-5
   map/ad, page-6 statblock styling, and the relationship between body text and
   full-page composites.
5. Navigation generation must ignore the inherited outline/open action and use
   reconstructed semantic headings.
6. If three-view review reclassifies the page-5 asset as a handout or keeper
   map, asset disposition and review units change. The numbered-player-handout
   contract count remains `0` unless a numbered label is discovered in source
   evidence.
7. If any downstream tool uses CropBox by default, it will omit running-header
   content that exists in the MediaBox. Render recipes and evidence must state
   the selected box explicitly.

## Concrete remediation specification

For the orchestrator's contract draft and the subsequent reconstruction step:

1. Populate source facts exactly as: `page_count: 6`, `page_number_base: 1`,
   `media_box_points: [595, 841]`, `rotation_degrees: 0`, the recorded byte
   count/hash, and logical `locator_hint: Dissociation.pdf`.
2. Populate scope as all pages `1-6` with
   `required_entities.numbered_player_handouts: 0`.
3. Use the four-row page-role partition above. Do not add empty role ranges for
   roles absent from the source.
4. Keep the page-5 asset inside `scenario_body` for topology, while requiring a
   dedicated visual/OCR review unit for its semantic disposition.
5. Require a region-aware left-column-before-right-column merge for pages 2-6;
   prohibit raw extractor order as accepted reading order.
6. Require dedicated review units for page 1 cover fidelity, page 3 black
   names/occupations card, page 5 map/ad and text-to-asset ownership, page 6
   `HUMAN RESISTANCE` statblock, and the MediaBox/CropBox difference.
7. Treat the source outline, open action, and page labels as stale/noncanonical;
   construct navigation only after heading hierarchy is reviewed.
8. Record Poppler syntax warnings and parser disagreements in comparison/audit
   evidence. Keep visual-preserve fallback available for any block that cannot
   be recovered faithfully from raw/ocr views.
9. Do not encode publication suppression or scenario-specific executable
   repairs in the reconstruction contract. Any later exception must be exact,
   evidence-bound, single-match, and explicitly approved under the schema.

## Acceptance criteria for the next bounded steps

Contract draft is ready for review when:

- both the JSON Schema and `scenario_contract.py` accept it;
- source identity and geometry equal the contract-ready facts above;
- page roles are sorted, gap-free, non-overlapping, and cover pages `1-6`;
- numbered player handouts equal `0`;
- no Innsmouth/Viral page facts or scenario-specific executable logic appear;
- the CropBox, stale-navigation, page-5 asset, and parser anomalies remain
  explicit review requirements rather than silently resolved assumptions.

Three-view reconstruction evidence is minimally sufficient when:

- all six physical pages and both text and visual provenance are accounted for;
- column order is explicitly closed on pages 2-6;
- the page-1 cover, page-3 card, page-5 map/ad, and page-6 statblock have closed
  fidelity decisions;
- source outline/open action/page labels have not contaminated generated
  navigation;
- no low-level image count is presented as a semantic asset count;
- every unresolved asset, crop, reading-order, or parser discrepancy remains a
  blocker to candidate promotion.

## Blockers and next action

- Blockers to drafting the scenario contract: none.
- Expected blockers to reconstruction promotion: page-5 asset disposition,
  exact cross-column merge decisions, crop-box authority evidence, semantic
  asset deduplication, and the page-1 parser anomaly remain open by design.
- Next action: the main-chat orchestrator should draft and validate the
  Dissociation runtime contract from the contract-ready facts, then dispatch
  three-view reconstruction under the reviewed contract. No MinerU run should
  start before the contract and generic-runner boundary are closed.
