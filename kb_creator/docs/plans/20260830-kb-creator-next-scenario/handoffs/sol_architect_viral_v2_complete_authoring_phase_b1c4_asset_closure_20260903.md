# Sol architecture receipt — Viral v2 complete authoring Phase B1c4 asset closure

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1c4-asset-closure`.
- Role: `nri-architect` / requested GPT-5.6-sol / high.
- Actual platform model and effort: unavailable; requested role was used as the
  reasoning contract.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / medium. Ownership did
  not transfer.
- Assignment state: `matched`; platform runtime identity remains unverified.
- Scoped override: exact task packet
  `TASK_PACKET_architect_viral_v2_complete_authoring_phase_b1c4_asset_closure_20260903.md`,
  SHA-256
  `7D63519464780D7E8DFB456F354D5D9CCA8C6C5504F873FB083E5038C8E7D554`.
- Timestamp: `2026-09-03T13:22:30.8045621+03:00` (Europe/Moscow).
- Elapsed time: approximately 50 minutes.
- Token use: unavailable.
- Result: `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C4_ASSET_ENGINEERING`.

## Scope and bound checkpoint

This is a code-ready architecture decision, not implementation, candidate
acceptance or release review. The only changed file is this receipt. Code,
tests, config, candidates, plans, context, status, evidence, immutable inputs,
assets, downstream artifacts and Git were read-only.

The assigned packet, B1c3 implementation approval, B1c readiness addendum and
all six current code/test files matched their required hashes:

| Item | SHA-256 |
| --- | --- |
| B1c3 approval | `4F37A4E75CAE7CB6E786F6D72D80A73D9062C6582E5378EC642C417B5281F960` |
| B1c readiness addendum | `B709C7F09B3F19A65AFA2DBE3FE7AE42022357FB690E436F27C899CCDF21290F` |
| author / builder / verifier | `5F0B1E7F...D666` / `A1602EEC...F28` / `6783D5AC...FCB` |
| author / builder / verifier tests | `AC8395CA...F98` / `BE1AFABE...207` / `8D1DF368...EEB` |

The current public first errors remain builder
`v2 asset provenance mismatch` and independent verifier
`E_V2_ASSET: provenance`. Canonical `publication_config_v2.json` and v2
candidates are absent. There is no drift and no architecture blocker.

## Evidence identities and recomputation

The engineering implementation must add these two direct, closed evidence
identities to the v2 document. Aggregate package identity alone is not enough
for visual-region lookup:

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| accepted-v4 `ASSET_MANIFEST.json` | 50,739 | `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9` |
| three-view `comparison/comparison.json` | 4,045,127 | `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0` |
| accepted-v4 `MERGE_PROVENANCE.json` | 232,547 | `9B0928418E61189B8D15377240730EABBA46D4455D4EA7449338D921168DBCA2` |
| user-review registry | 160,570 | `D20414D48405A761ADD31E538B6940F8A3E0F1FB11044AF73EAD122D96C616E8` |
| source PDF | 20,718,150 | `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |

Independent recomputation, without builder helpers, proved:

- all `121` path-backed frozen rows have exact file bytes, SHA-256, MIME and
  Pillow dimensions equal to v1;
- all `121` resolve through one and only one accepted-v4 asset-manifest row and
  one and only one comparison block; every block has page, view, raw index and
  four-coordinate bbox;
- selected views are `100 original_hybrid`, `20 original_pipeline_ocr`, and
  `1 raster_hybrid`; block types are `101 image` and `20 table`;
- accepted page Markdown contains `119` unique, non-orphan image markers. The
  only path assets without a marker are the two page-1 reference-only evidence
  crops, placement indices `1` and `2`;
- the current accepted ledger supplies exactly `16` approved asset-owned
  Markdown spans. Existing unapproved marker text is a placement witness, not
  permission to relabel visual-region provenance as text provenance;
- PDF pages 106–122 are unrotated Letter pages, `612 x 792 pt`, with identical
  MediaBox and CropBox. A 200-DPI full-MediaBox render is `1700 x 2200 px`.

## Closed provenance and asset schemas

### Decision: A3's all-assets-text-span rule is too narrow

The nonempty `source_span_ids` rule remains unchanged for source-derived text,
heading, structured and anchor events. It is replaced only for asset rows and
asset events by a required closed discriminated `provenance` union. An empty
list is not provenance. Unknown kinds, cross-kind keys or unbound fields fail.

The common final asset fields are:

```text
asset_id, disposition(reader|evidence_only), source_page, owner_anchor,
binary, provenance, placement, content_role, layout_role, semantic_role,
decision_ref, migration_row_ids, replaces
```

`binary` for accepted reconstruction bytes is exactly:

```text
{path, bytes, sha256, media_type, dimensions:{width,height}}
```

The path must be a regular non-reparse descendant of the accepted-v4 package.
Magic-derived media type, decoded dimensions, byte count and digest must all
match. Evidence-only rows retain this identity even though candidate bytes are
not copied.

The required provenance variants are mutually exclusive:

1. `markdown_image_reference` — exactly the existing 16 approved rows:
   `{kind, span_id, page_markdown_identity, start_byte, end_byte, start_char,
   end_char, marker_sha256}`. The slice must be one complete Markdown image
   reference, contain the row's exact accepted-v4 asset digest once, be owned by
   the asset id and be unique across assets.
2. `visual_region` — the 100 non-ad frozen path rows not in variant 1:
   `{kind, asset_manifest_identity, asset_manifest_row_sha256,
   comparison_identity, selected_view, source_asset_reference, raw_index,
   block_type, source_page, bbox, comparison_block_sha256}`. The manifest row
   must identify the same immutable binary. The selected comparison block must
   be unique, use that source asset reference, have the declared page/view/raw
   index/type/bbox, and canonical-hash to the declaration.
3. `reviewed_provisional_full_page` — the frozen front-cover render and the
   eight new targets below: `{kind, source_pdf_identity, physical_page,
   page_index_zero_based, region:{kind:full_media_box, points:[0,0,612,792]},
   render_recipe, output_media_type, output_dimensions, quality_stage}`.
   The recipe is Poppler `pdftoppm`, one exact page (`-f N -l N`), `-r 200`,
   `-png`, MediaBox, source rotation applied, upright RGB, white background, no
   alpha and stripped metadata. Output is `image/png`, `1700 x 2200`, quality
   stage `provisional_full_page`. Candidate bytes/size/SHA are recorded after
   deterministic emission and independently reproduced by the verifier; they
   must not be invented in config before the bytes exist.
4. `excluded_advertising` occurs only in the frozen migration ledger, never in
   final `assets` or events. It records frozen source id/row hash/page and
   `decision_ref: OUT-026`; it has no target.

Primary frozen-row provenance counts are exactly:

```text
16 markdown_image_reference
100 visual_region
 1 reviewed_provisional_full_page (front cover)
 6 excluded_advertising
---
123
```

The 100 visual-region rows include real Markdown markers where present. Those
markers are legitimate placement witnesses but not promoted to the smaller set
of 16 reviewed source-provenance spans.

### Placement and events

`placement` is a second closed union and cannot be inferred from owner end:

- `source_marker`: exact page Markdown identity and unique half-open marker
  byte/character range/hash. Split the source partition at all 119 real marker
  ranges. The asset event occupies that range, so it is exactly before, between
  or after adjacent fragments and survives page/column continuation without a
  nearest-owner fallback. For in-scope rows this yields 114 marker events:
  `84` emitted reader assets and `30` suppressed evidence assets.
- `fixed_document_slot`: only frozen front cover, slot `document_start`, before
  the first page-1 prose event.
- `physical_unit_slot`: only the eight new renders, with exact physical unit id
  and zero-based page slot below.
- `none_evidence`: only the two page-1 reference-only evidence crops. They have
  visual-region source order but no reader or suppressed Markdown event.

Every marker event owns its exact marker placement span. Asset content
provenance remains the variant above. Reader marker events emit one canonical
asset reference; evidence marker events are ledgered `suppressed` and emit no
reader bytes. The builder must reject a second event per asset, a reused marker,
an event/asset disposition mismatch, or placement after an owner merely because
that is the owner's last event.

Semantic owner is the frozen v1 `owner_anchor` for every nonexcluded row except
these exact corrections, both `retained_rebound` under `OUT-005`:

- placement `32`, coastal-town asset `b90cb9...7585` ->
  `viral-isola-plots-and-schemes`;
- placement `33`, boat asset `da0cac...0083e` ->
  `viral-isola-plots-and-schemes`.

Their marker order is page 31 coastal town, page 32 boat, then the page-32
`Prologue` heading. The page-3 Spektral Krew logo keeps owner
`viral-opening-message`, but its marker event is before the first prose event.
The page-6 ruined-hall hero remains reader; the Summary marker is suppressed.

## Exact frozen 123-row disposition and migration

Let `U` be the exact ordered `assets` rows in frozen v1 config SHA-256
`C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
For any nonexcluded row, the final target is exactly
`assets:<same frozen asset_id>`. This partition is exhaustive and normative;
the 99-row complement is not an implicit fallback but the explicitly defined
set `U - rebound - reclassified - excluded`.

### `retained_rebound`, 2, decision `OUT-005`

- `assets:viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585`
- `assets:viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e`

### `reclassified` to evidence-only, 16

`OUT-006`:

- `assets:viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419`

`OUT-007`:

- `assets:viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b`
- `assets:viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab`
- `assets:viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e`
- `assets:viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e`
- `assets:viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12`

`OUT-024`:

- `assets:viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541`
- `assets:viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d`
- `assets:viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc`

`OUT-025`:

- `assets:viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b`
- `assets:viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3`
- `assets:viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50`
- `assets:viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4`
- `assets:viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f`
- `assets:viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8`
- `assets:viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166`

### `excluded_advertising`, 6, no target, decision `OUT-026`

- `assets:viral-accepted-d365a35fdb84635c1d0a0196af00f10e44dc6142ae8d5c3527086f9bba5dc54a`
- `assets:viral-accepted-0f5d05de49283e419e7fba628949676ff1eb0e2a697542fab8c82bc9d778f3f4`
- `assets:viral-accepted-55042bfe5cb8b706e22567337d6db01a2e966b1893d9b954957ef2bb32283c6c`
- `assets:viral-accepted-e14f34621fe6ef4aa1a78503d934f5c4aa0b7924a5ab9eb93fbadc35a0ef8bd6`
- `assets:viral-accepted-9ce11ee6d39615b0990d1cb4d366d8bbca797b621abe16d57bf90bf411283d7a`
- `assets:viral-render-cover-back`

### `retained_unchanged`, 99

Exactly `U` minus the preceding 24 ids. It comprises `83` reader rows and the
original `16` evidence-only rows. It has same-id targets, preserves all frozen
binary/semantic/owner fields and has `decision_ref: null`. No row has outcome
`replaced`, `split`, `merged` or `suppressed_reviewed` in this asset ledger.

The independently recomputed canonical 123-row audit object contains, per row,
placement index, full source id, source page, primary provenance object, final
disposition, migration outcome/targets/decision, final owner and exact placement
witness. Canonical UTF-8 JSON (`sort_keys=true`, compact separators) SHA-256 is
`5B90C59B5E289A9424CAA3F1A2AF1081713506885C050D162D0CBDF77CABABA5`.
Engineering tests must reproduce this digest from immutable inputs, not paste it
as the classification authority.

Conservation is exact:

```text
frozen rows: 99 retained_unchanged + 2 retained_rebound
           + 16 reclassified + 0 replaced + 0 suppressed + 6 excluded = 123
frozen dispositions: 85 reader + 16 retained evidence
                   + 16 reclassified evidence + 6 excluded = 123
```

## Eight new reviewed provisional full-page targets

Extend `migration.new_reviewed_targets` from `{target_id,decision_ref}` to the
closed form `{target_id, decision_ref, evidence_identity, replaces}`. Each old
id below occurs in exactly one `replaces`; all 16 replaced reader functions are
still conserved as frozen evidence rows above. Therefore the asset-row outcome
is `reclassified` or retained evidence, not a false disappearance.

| New target id | Owner / slot | Decision | Exact `replaces` |
| --- | --- | --- | --- |
| `assets:viral-provisional-map-ground-floor-basement-page-106` | `viral-keeper-map-ground-floor-basement`; `physical_units:viral-map-ground-floor-basement`, slot 0 | `OUT-024` | `...adb4ff51...72541`, `...f7ce778c...b321d` |
| `assets:viral-provisional-map-ground-floor-basement-page-107` | same unit, slot 1 | `OUT-024` | `...e1c168ca...f584dc` |
| `assets:viral-provisional-pregen-marco-back-page-112` | `viral-pregen-marco-background`; `physical_units:viral-pregen-marco`, back slot 1 | `OUT-025` | `...5d2410af...42230b`, `...53c27754...6a3595` |
| `assets:viral-provisional-pregen-corrina-back-page-114` | `viral-pregen-corrina-background`; `physical_units:viral-pregen-corrina`, back slot 1 | `OUT-025` | `...331f4d57...8c00d3`, `...89e3eae7...bfc297` |
| `assets:viral-provisional-pregen-enoch-back-page-116` | `viral-pregen-enoch-background`; `physical_units:viral-pregen-enoch`, back slot 1 | `OUT-025` | `...92c65562...8d01d50`, `...66088dd8...ebfcb` |
| `assets:viral-provisional-pregen-peter-back-page-118` | `viral-pregen-peter-background`; `physical_units:viral-pregen-peter`, back slot 1 | `OUT-025` | `...07982af9...864aa4`, `...fe4c839c...8fe0c3` |
| `assets:viral-provisional-pregen-ku-hyeon-back-page-120` | `viral-pregen-ku-hyeon-background`; `physical_units:viral-pregen-ku-hyeon`, back slot 1 | `OUT-025` | `...9d7ebb95...05953f`, `...df1e0189...b4730` |
| `assets:viral-provisional-pregen-blank-back-page-122` | `viral-pregen-blank-background`; `physical_units:viral-pregen-blank`, back slot 1 | `OUT-025` | `...1ae1543b...ee3b8`, `...dd0c2d51...8d8b`, `...dcf1f2f6...eb166` |

The abbreviated `replaces` cells expand to the following exact full ids, in the
same table order:

```text
viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541
viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d
viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc
viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b
viral-accepted-53c2775488f57c8e41f9d42648ecb8a1d30e9a1ce0de8d4108b7926ee26a3595
viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3
viral-accepted-89e3eae7390f0ae27a8069bcf2d2aa2956a21047eeb7168a3fd49b0b7cbfc297
viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50
viral-accepted-66088dd8192e2a93f140eb9e11fadfed92b3869c509490199a35d272197ebfcb
viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4
viral-accepted-fe4c839c1ff9b15dc4a9136f6969271a7a465fe642c77b38f456aa2af38fe0c3
viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f
viral-accepted-df1e018979c88b0737200c349889745eadfa119466dc40fb024779a0f8eb4730
viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8
viral-accepted-dd0c2d51431a4945f9f7d8293bc7b0b5e870f891dbe31d18c931926bffbb8d8b
viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166
```

All eight use the full-page provenance recipe above. New target source pages
are exactly `106,107,112,114,116,118,120,122`; page index is page minus one.
No GUI screenshot, SELECTED_OVERLAY render or detected-region crop is valid.

Final config asset records are therefore exactly:

```text
117 nonexcluded frozen targets + 8 new reviewed targets = 125
93 reader (85 frozen + 8 new) + 32 evidence-only = 125
candidate asset binaries copied/emitted = 93
evidence records preserved but not copied = 32
excluded migration-only rows = 6
```

### Physical units and accessible semantics

The map physical unit owns pages `[106,107]`, the two new reader assets in slot
order and the already reconstructed `Key` A–V, legend labels and scale as a
separate source-bound accessible payload. The three child crops are evidence
only and never reader children.

Each pregen physical unit owns one existing front full-page asset and its new
back full-page asset in front/back order. Back semantic text remains a separate
source-slice-bound payload: Background fields, Gear and Possessions, Cash and
Assets, Quick Reference Rules, character responsibilities, and for the blank
sheet its actual labels including Fellow Investigators. Raster text is not
translated and semantic text does not replace the facsimile.

B1c4 must declare asset/physical-unit identities and replacement closure. It
must not invent the later typed payload strings or recovery rows. Candidate
materialization remains closed until a later slice supplies complete source
bindings for those accessible payloads. Post-MASTER_RU Step 8A may select a
better direct dominant-XObject binary or a reviewed equivalent under the same
stable logical asset id, but cannot change source page, physical unit, order,
accessible semantics or replacement closure without returning to MASTER_EN
review.

## Builder and independent verifier requirements

Builder preflight must, before any candidate directory or asset byte is
created:

1. bind the two direct evidence files, registry, v1 config, package aggregate
   and source PDF identities;
2. recompute the 123-row partition and canonical audit digest;
3. validate all 121 path binaries, 121 unique manifest/block links, 119 unique
   marker ranges, the 16 approved provenance spans and the four provenance
   union variants;
4. split marker spans and construct exact emitted/suppressed asset events;
5. validate owner/page/order, the p3 and p31/p32 regressions, 125 final ids,
   93/32 dispositions, eight new targets and complete 16-id `replaces` graph;
6. reject any page-123/124 hierarchy/event/asset/xref/review/candidate leakage;
7. stop before candidate emission at the next declared seam.

At later authorized candidate build, accepted reader paths are copied byte for
byte and re-hashed after copy; provisional render bytes are emitted from the
source PDF recipe and then hashed/decoded. Evidence-only and excluded bytes are
not copied. Candidate manifest records all 125 final rows, exact 93 output
paths/bytes/digests/media/dimensions, 32 non-output evidence dispositions and
the replacement graph. No child in a new target's `replaces` may have a reader
event or output path.

The verifier must not import builder code or trust builder provenance, asset
manifest, QA, event ledger or inventory as source truth. It independently
reads config, v1, accepted package, comparison evidence and source PDF;
recomputes the classification/marker/bbox/replacement sets; verifies every
candidate file from bytes and magic; independently renders the eight pages and
compares bytes/digest/dimensions; scans candidate MASTER/event ledger for exact
asset event order and suppression; and rejects missing, extra, duplicate,
orphan, evidence-only or excluded output files. Builder sidecars are subjects
of verification, never authorities.

## Required engineering tests

Positive coverage:

- real-input known answer: 123 frozen rows, provenance `16/100/1/6`, outcomes
  `99/2/16/6`, final `125 = 93/32`, 121 binary/link checks, 119 markers and
  audit digest `5B90...ABA5`;
- p3 identity logo before first prose; p31 town then p32 boat immediately before
  Prologue; page-start, between-fragment and page-end markers; two p1
  no-marker evidence rows;
- Summary plus five platform/promo rows suppressed, ruined-hall hero emitted;
- map two-page unit and six front/back pairs, all eight render recipes and all
  16 replacement ids exactly once;
- builder/verifier public APIs independently reach the same later seam and
  create zero canonical config, candidates or retained temp files.

Negative mutation matrix, independently implemented in both test modules:

- every provenance kind: missing/extra/cross-kind key, empty provenance,
  foreign/duplicate span, changed page/range/hash/digest, non-image marker,
  wrong manifest row/view/source reference/raw index/block type/bbox/block hash;
- binary: one-byte mutation, wrong byte count/SHA, extension-vs-magic MIME,
  dimensions, path escape, reparse link, missing/nonregular source;
- placement: duplicate/reused marker, p3 after prose, p31/p32 Prologue owner,
  reversed town/boat, owner-end relocation, wrong page/adjacent fragment,
  evidence event emitted, reader event suppressed, duplicate/missing asset event;
- disposition/migration: each count ±1, unknown decision, changed row hash,
  missing/duplicate source id or target, same target twice, orphan target,
  excluded target/event/review/output leakage;
- replacement/physical unit: missing/duplicate/foreign `replaces`, one old id
  used twice, child reader emission/copy, wrong page/slot/order, incomplete map,
  missing back, front/back reversal, missing accessible-semantics obligation;
- provisional render: wrong PDF/page/page index/box/rotation/DPI/format/color/
  alpha/dimensions, SELECTED_OVERLAY input, screenshot/crop substitution;
- verifier independence: forged builder asset sidecar, forged output digest,
  mutated candidate after build, extra candidate image, and omitted evidence
  row must all fail without consulting builder helpers.

## Minimal engineering ownership, order and stop rules

The narrow B1c4 engineer may change only:

- `kb_creator/scripts/author_viral_master_en_v2_config.py`;
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`;
- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- one new immutable engineering receipt assigned by the orchestrator.

Ordered stages are: (1) author-side evidence binding and exact 123-row audit;
(2) closed schema and marker partition; (3) migration/new-target/replaces
closure; (4) builder validation; (5) independently written verifier parity;
(6) positive and mutation tests; (7) both real public preflights and forbidden-
output check. Do not create canonical config, candidate, render file, evidence
file or downstream artifact.

Hard stop on any bound hash drift, nonunique asset/marker/block link, unknown
bbox, unbound owner/placement, count or audit-digest mismatch, render authority
uncertainty, missing decision, candidate byte emission, or any attempt to fill
later typed/recovery/review content with placeholders.

After honest asset closure the exact next public preflight pair is intentionally:

```text
builder:  v2 visual review coverage mismatch
verifier: E_V2_REVIEW: coverage
```

That seam is expected because reader flags become truthful while complete
asset/physical-unit visual-review declarations are deliberately not fabricated
in B1c4. Later bounded slices must supply source-bound typed payload/recovery
content and complete visual-review rows before any canonical config or candidate
execution. This receipt does not authorize those slices or release review.

## Files checked or changed

- Changed: only this receipt.
- Checked read-only: assigned packet; root AGENTS; goal governance; current
  plan/context/status; B1c readiness and B1c3 approval receipts; author,
  builder, verifier and their tests; frozen v1 config; accepted-v4 package,
  pages/assets/manifest/provenance; three-view comparison; source PDF metadata;
  user-review registry.
- Blockers: none for bounded B1c4 engineering. Canonical config/candidate and
  later typed/recovery/visual-review work remain intentionally unauthorized.
- Next action: orchestrator integrates this receipt and assigns a hash-bound
  six-file B1c4 implementation packet, followed by fresh independent
  implementation review.

READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C4_ASSET_ENGINEERING
