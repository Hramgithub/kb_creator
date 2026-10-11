# Viral Step 7 MASTER_EN executable publication packet

## Immutable contributor receipt

- Goal / plan: `20260830-kb-creator-next-scenario`, Step 7 (`fresh Viral MASTER_EN`).
- Assignment: `/root/viral_step7_master_en_architecture`.
- Assignment state: `complete_as_architecture`; publication implementation remains unstarted and blocked on an accepted corrected reconstruction successor.
- Role: NRI architect (`gpt-5.6-sol`, `high`).
- Orchestrator and policy owner: `/root`, NRI orchestrator (`gpt-5.6-sol`, `medium`). Orchestration ownership did not transfer.
- Scoped override: this contributor may write only this handoff receipt; all source, canonical plan/context/status, release, code, test, build, MinerU, and Git surfaces are read-only.
- Scope performed: architecture and content specification for deterministic construction, QA, review, and user acceptance of a fresh English reader master covering all 124 source pages.
- Result: executable publication contract defined. The accepted v3 reconstruction is not a valid direct Step 7 input after source-visible defect classes were found. A minimal, immutable, independently accepted v4 reconstruction correction successor is a hard precondition. MASTER_EN must not absorb those corrections as editorial transformations.
- Changed file: only `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_publication_packet_20260901.md`.
- Blockers: accepted v4 identities do not yet exist; the two bounded content-audit inventories and their resulting v4 correction ledger must be completed and pinned. No MinerU rerun and no 371-case matrix rerun are required by this architecture.
- Next action: orchestrator commissions the bounded v4 reconstruction correction/verification; after its acceptance, engineering implements this Step 7 builder/config contract and produces a hash-pinned review candidate. Explicit user reading acceptance remains mandatory before promotion or translation.
- Timestamp: `2026-09-01T17:47:20+03:00` (`Europe/Moscow`).
- Elapsed time: approximately 70 minutes including evidence inspection and visual-source review.
- Token use: unavailable (exact role-level accounting was not exposed).
- Packet identity: the detached SHA-256 and byte count of this final file must be captured after the last write and reported to the orchestrator. A file cannot contain its own final whole-file hash without changing that hash.

## 1. Decision and release posture

This packet is the normative Step 7 publication specification, not an acceptance of a MASTER_EN artifact. It reconciles the Viral runtime contract, the accepted reconstruction package, source/overlay evidence, and the generic stage-separation lessons from the reusable pipeline documentation.

The immediate release posture is **BLOCKED BEFORE BUILD**:

1. `20260901_step6a_reconstructed_en_package_v3` remains immutable and remains valid evidence of the completed Step 6 review at the identity recorded below.
2. Direct source inspection has proved lexical reconstruction defects, not reader-style issues:
   - source page 20 has systematic lowercase `l` → `e` corruption, including source `Exploring in Perla` versus reconstructed `Expeoring in Perea`, and affected prose/table cells;
   - source page 44 has systematic capital `H` → `a` corruption, including source `Administrator’s House` versus reconstructed `Administrator's aouse`;
   - pages 42 and 45 contain `10` where the source has location label `1O`;
   - pages 49 and 50 contain `Hastalijk` where the source has `Hastalÿk`;
   - page 62 was silently normalized in v3 even though the specific source occurrence actually reads `Hastaÿk's corruption` (missing `l`); v4 must restore that exact occurrence while retaining canonical `Hastalÿk` at source occurrences that use it;
   - page 65 reconstructed `Aspect of Hastalijk` must become source-exact `Aspect of Hastalÿk`; a separate source-visible `Hasalÿk` occurrence on the same page is authorial and remains immutable. These are occurrence-specific decisions, not permission to globally normalize the name.
3. These are `text_repair` operations owned by `reconstructed_en`. They must be applied in a minimal v4 successor, with bounded same-page/same-defect-class closure and the separate page-range audit receipts as inputs. They must **not** be represented as provenance-recorded MASTER_EN editorial transformations.
4. The minimal v4 pass reuses the accepted v3 package and source/overlay evidence. It does not rerun MinerU, the three-view generation, or the historical 371-case matrix. It must nevertheless rebuild its own immutable package identities, QA, provenance, and acceptance evidence.
5. Step 7 may begin only when the v4 root, `RECONSTRUCTED_EN.md`, reconstruction QA, provenance, asset manifest, and accepted-review receipt identities are pinned in the publication config.

This decision follows the defect-class boundary: publication owns reader structure and presentation; reconstruction owns recovery or correction of source lexical facts. A clean-looking MASTER_EN cannot cure an unaccepted reconstruction input.

## 2. Governing authorities and inspected evidence

### Canonical authorities

- Runtime scenario contract: `kb_creator/contracts/viral.json`. This supersedes the nonexistent initial locator `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract.yaml`.
  - Contract SHA-256 recorded by the accepted reconstruction provenance: `67688867918624D331C7EC7CE4AD10ED84D26A8489670E4C016A5C7BF067536D`.
  - Source identity: SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`, `20,718,150` bytes, `124` pages.
  - MASTER_EN gates: `accepted_reconstructed`, `source_disposition`, `semantic_navigation`, `handout_mapping`, `table_statblock_closure`, `asset_closure`, `no_technical_reader_noise`.
  - MASTER_EN approval authority: `explicit_user_reading_acceptance`.
- Canonical plan: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`, especially the Step 6 acceptance / Step 7 activation record around lines 1975-2020 at inspection time.
- Canonical context: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`, especially the accepted v3 package identities and Step 7 boundary around lines 1718-1770 at inspection time.
- Architecture contract: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`.
- Goal governance: `docs/governance/nri_goal_governance.md`.

### Accepted Step 6 evidence

- Package root: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3/`.
- Reader-source Markdown: `.../RECONSTRUCTED_EN.md` — SHA-256 `5D28F097708CB9D58A5A0D4C72CC93E9985FC7CDB00C22EFDB0A22C9931B79ED`.
- Selected visual overlay: `.../SELECTED_OVERLAY.pdf` — SHA-256 `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`.
- Package ordinal inventory SHA-256: `46E61F5DB9853E795C636147C63230936221F056DE1A9C25B19A4C8DEAEA215E`.
- Candidate ordinal inventory SHA-256: `B0D74C6560648454DD3B12E02446969A11851BD722B41F0222FFA9DE32121EA1`.
- Package sidecars inspected: `ASSET_MANIFEST.json`, `MERGE_PROVENANCE.json`, `OVERLAY_SELECTION.json`, `RECONSTRUCTION_PROVENANCE.json`, `RECONSTRUCTION_QA.json`, and `RECONSTRUCTION_QA.md` in that root.
- Step 6 independent review: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstructed_en_package_v3_review_20260901.md` — SHA-256 recorded in canonical context: `D7814D686B40C462046A4EF8D4434792106E44CAE8B88D4F67D827226B02CB2E`.
- Step 6 visual QA: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_reconstructed_en_package_v3_visual_20260901.md`.
- Immutable source PDF for spot checks and declared visual derivation only: `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`.

`SELECTED_OVERLAY.pdf` is evidence only. Its layout boxes, labels, and annotations are technical overlays and must never be copied, rendered, or linked as reader assets.

### Generic lessons used, never scenario rules

- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`.
- `kb_creator/inputs/innsmouth/master_en/README.md`.
- `kb_creator/inputs/innsmouth/master_en/PIPELINE.md`.

Only these generic patterns transfer: separate reconstruction/publication/freeze stages; immutable, hash-pinned predecessor; explicit semantic anchors; generated navigation; sidecar provenance; asset ownership; table/statblock presentation closure; build-to-new-empty-target; and explicit user acceptance. No Innsmouth scope, handout numbering, suppression rule, asset allowlist, anchor name, scenario wording, or accepted hash transfers to Viral.

## 3. Publication scope and 124-page disposition contract

`viral.json` says `all_source_pages`, pages 1-124, and has no exceptions. Therefore every source page must have exactly one page-disposition row and all source-bearing units on it must close. No authorial source content may be suppressed in Step 7. Technical reconstruction markers are not source content and are removed under reader-noise policy.

| Source pages | Role | MASTER_EN disposition | Required closure |
|---|---|---|---|
| 1 | cover | `retained_visual` | Exact clean source-page visual at the opening plus one semantic document H1, `Viral`; suppress OCR fragments such as camera-interface words because the clean visual already retains them and they are not standalone reader headings. |
| 2 | credits | `transformed_semantic_visual` | Preserve all credit/legal text in readable semantic structure and preserve material logos/art with explicit ownership; do not use the annotated overlay. |
| 3-4 | front matter | `retained_semantic` | Preserve Marco's opening message and the complete warning/safety text. No reader-policy removal is authorized. |
| 5 | contents | `transformed_navigation` | Replace printed page-number TOC with a generated semantic TOC targeting explicit anchors. Preserve every genuine contents entry as navigation; do not reproduce printed page tokens. |
| 6-68 | scenario body | `transformed_semantic` | Preserve authorial text and meaningful art, repair hierarchy, lists, tables/statblocks, callouts, and internal links. Every block maps to a stable semantic anchor and source provenance. |
| 69-103 | player handouts | `relocated_canonical_appendix` | Publish one canonical unit per physical handout identity, in source order, with hybrid semantic/visual representation as appropriate. Preserve the page-82 “Hyeon's iPads” introduction as contextual appendix text, not as a numbered handout. |
| 104-110 | keeper maps | `retained_visual_semantic_key` | Preserve all seven map pages and their keys/legends. Page 107 is an owned continuation of page 106, never an orphan. |
| 111-120 | five pregens | `retained_hybrid` | Preserve each front investigator sheet as a complete legible visual form and each corresponding back page as semantic background/equipment/responsibility text with owned silhouette/quick-reference art. |
| 121-122 | blank pregen template | `retained_hybrid` | Preserve the complete blank front form and the semantic blank background/template, quick reference, and relationship diagram. |
| 123 | merchandise/QR | `retained_visual_semantic` | Preserve merchandise images, wording, and source QR code as historical source content. Do not rewrite, silently update, or endorse the external destination. |
| 124 | back cover | `retained_visual` | Exact clean source-page visual at the close. Do not duplicate its quote/blurb as a second visible transcript; provenance may retain the extracted semantic text. |

The source disposition sidecar must enumerate pages `1..124` without gaps or duplicates and include sub-unit rows where one source page owns multiple handouts/assets. Allowed publication operations are `retain`, `structure`, `relocate`, `link`, `visualize`, and removal of technical evidence markers. `suppress_source_content` is invalid while `viral.json.exceptions` is empty.

## 4. Reader hierarchy, explicit anchors, and TOC

### Heading rules

- Exactly one H1: `Viral`, explicit anchor `viral`.
- Source page boundaries never create headings and are absent from reader Markdown.
- Major reader groups are H2; source TOC children are H3/H4 in the hierarchy below.
- Repeated labels such as `Keeper's Notes`, `Description`, `Background`, and `Quick Reference Rules` are subordinate local headings/callouts. They are not global TOC entries and receive parent-qualified IDs only if link targets are required.
- Explicit HTML-compatible IDs placed immediately before their headings are authoritative. Generated Markdown slugs are not identifiers.
- IDs are lowercase ASCII kebab-case, scenario-prefixed, unique, stable across wording/typography changes, and declared in config rather than inferred at build time. `Hastalÿk` normalizes to `hastalyk` only in IDs, never in visible text.

### Normative navigation tree

The config must explicitly declare at least the following tree and IDs. The builder emits the TOC from this declaration and fails if a declared heading is absent or appears more than once.

```text
Viral [viral]
  Credits [viral-credits]
  Opening Message [viral-opening-message]
  Warning [viral-warning]
  Contents [viral-contents]
  Introduction [viral-introduction]
    Summary [viral-introduction-summary]
    Overview [viral-introduction-overview]
  The Spektral Krew [viral-spektral-krew]
    Marco 'Proudfoot' Maglioni [viral-spektral-krew-marco-proudfoot-maglioni]
    Corrina Trench [viral-spektral-krew-corrina-trench]
    Enoch Jeremiah Eakins [viral-spektral-krew-enoch-jeremiah-eakins]
    Peter Wharton [viral-spektral-krew-peter-wharton]
    Ku Hyeon [viral-spektral-krew-ku-hyeon]
    Maya Adeduwon [viral-spektral-krew-maya-adeduwon]
    Emily 'Em' Lavigne [viral-spektral-krew-emily-em-lavigne]
  Creating New Investigators [viral-creating-new-investigators]
  Spektral Krew Gear [viral-spektral-krew-gear]
  Timeline [viral-timeline]
  History [viral-history]
  One Night in Perla [viral-one-night-in-perla]
    Welcome to Perla [viral-one-night-in-perla-welcome]
    Perla [viral-one-night-in-perla-perla]
    Exploring Perla [viral-one-night-in-perla-exploring]
      Rumors [viral-one-night-in-perla-rumors]
      Signs and Portents [viral-one-night-in-perla-signs-and-portents]
    Burning of the Disease [viral-one-night-in-perla-burning-of-the-disease]
    The Next Day [viral-one-night-in-perla-the-next-day]
    Perla NPCs [viral-one-night-in-perla-npcs]
  Isola di Malamente [viral-isola-di-malamente]
    Keeper's Secrets [viral-isola-keepers-secrets]
      Running the Game [viral-isola-running-the-game]
      Number of Sessions [viral-isola-number-of-sessions]
      Plots and Schemes [viral-isola-plots-and-schemes]
    Prologue [viral-isola-prologue]
    Isola di Malamente: Locations [viral-isola-locations]
      1. Lighthouse/Radio Station [viral-isola-location-01-lighthouse-radio-station]
      2. Beggar's Cove [viral-isola-location-02-beggars-cove]
      3. The Weeping Bridge [viral-isola-location-03-weeping-bridge]
      4. Lemon Grove [viral-isola-location-04-lemon-grove]
      5. Saint Roche's Hospital [viral-isola-location-05-saint-roches-hospital]
        Hospital Locations [viral-isola-hospital-locations]
      6. Mass Graves [viral-isola-location-06-mass-graves]
      7. Cremation Pit [viral-isola-location-07-cremation-pit]
      8. Isola di Malamente Dock [viral-isola-location-08-dock]
      9. Overlook Point [viral-isola-location-09-overlook-point]
      10. Chapel & Crypt [viral-isola-location-10-chapel-crypt]
      11. Catacomb Entrance [viral-isola-location-11-catacomb-entrance]
      12. Catacombs [viral-isola-location-12-catacombs]
      13. Temple of Morbus [viral-isola-location-13-temple-of-morbus]
      Hastalÿk Awakens [viral-isola-hastalyk-awakens]
    Epilogue [viral-epilogue]
      Rewards [viral-epilogue-rewards]
      Cinematic Ending [viral-epilogue-cinematic-ending]
      Expanded Ending [viral-epilogue-expanded-ending]
        New Epilogue [viral-epilogue-expanded-ending-new-epilogue]
  Appendix [viral-appendix]
    Encounters [viral-appendix-encounters]
      Outdoor Encounters [viral-appendix-encounters-outdoor]
      Hospital Encounters [viral-appendix-encounters-hospital]
      Catacomb Encounters [viral-appendix-encounters-catacomb]
    New Rules [viral-appendix-new-rules]
      The Sight [viral-appendix-new-rules-the-sight]
      The Taint [viral-appendix-new-rules-the-taint]
      Insanity and Bouts of Madness [viral-appendix-new-rules-insanity-bouts]
      Paranormal Phenomena [viral-appendix-new-rules-paranormal-phenomena]
    New Mythos Horrors [viral-appendix-new-mythos-horrors]
      Hastalÿk [viral-appendix-new-mythos-horrors-hastalyk]
      The Plague Monk [viral-appendix-new-mythos-horrors-plague-monk]
      The Reliquae [viral-appendix-new-mythos-horrors-reliquae]
    New Mythos Tome [viral-appendix-new-mythos-tome]
      Iuramentum Corruptionis [viral-appendix-new-mythos-tome-iuramentum-corruptionis]
    New Spells [viral-appendix-new-spells]
      Control Reliquae [viral-appendix-new-spells-control-reliquae]
  Player Handouts [viral-player-handouts]
  Keeper Maps [viral-keeper-maps]
  Pregenerated Investigators [viral-pregenerated-investigators]
  Merchandise [viral-merchandise]
  Back Cover [viral-back-cover]
```

Handout, map, and pregen unit anchors extend this tree as defined below. TOC depth is H2-H4 and includes the major appendices; it must not flood the TOC with each repeated callout, individual background field, or every handout unless the config's `toc.include_handout_index` explicitly generates a compact nested handout index. The canonical Handouts section itself must always include the complete linked index.

## 5. Printed-reference replacement and internal-link policy

The builder uses an explicit xref ledger, never blind page-number substitution:

```json
{
  "source_page": 36,
  "source_visible_phrase": "The Sight",
  "printed_token": "see p.60",
  "reader_label": "The Sight",
  "target_anchor": "viral-appendix-new-rules-the-sight",
  "kind": "internal"
}
```

For an internal reference, retain the visible semantic phrase and replace only the printed page token/construct with a Markdown link. Do not expose source page numbers in link text, footnotes, alt text, or comments. Known link families that the ledger must cover include:

- body references to `The Sight`, `The Taint`, `History`, Hospital Locations/encounters, the Temple/Hastalÿk-awakening material, the Epilogue/Cinematic/Expanded endings, Hastalÿk/The Devourer, The Reliquae, and `Iuramentum Corruptionis`;
- narrative handout references, including the known occurrences for Handouts 11, 12, 14, 28, 30-39;
- every TOC entry and map/pregen/handout index entry.

`Knock-Out Blows on p.125 in the Keeper Rulebook` is an external bibliographic reference. Preserve it as readable unlinked source wording (or link only if a separately approved external URI exists); it is not a dangling MASTER_EN internal reference.

QA scans visible Markdown outside code spans for `p.`, `pp.`, `page`, and bare printed page-number patterns. Every hit must be classified in the xref ledger as `internal_replaced`, `external_preserved`, or `literal_source_quote`. Zero unclassified hits and zero unresolved/dangling anchors are allowed.

## 6. Exact handout identity, reference, and map policy

### Identity invariants

- The contract's `numbered_player_handouts: 39` means numeric ordinals 1 through 39 are all present, not that there are only 39 physical identities.
- Physical identities are **41**: `1`, `2a`, `2b`, `3a`, `3b`, and `4..39`.
- `2a`/`2b` and `3a`/`3b` are distinct and may not be merged, renamed, flattened to 2/3, or renumbered.
- Multi-handout source pages own multiple canonical units. One page image or heading cannot stand in for multiple identities without separate anchors, titles, provenance rows, and index entries.
- Page 82 is contextual text (`Hyeon's iPads`) between Handouts 14 and 15; it is retained once and has no invented handout number.

### Normative label-to-page ledger

| Source page | Canonical handout identities / anchors |
|---:|---|
| 69 | `1` → `viral-handout-01` |
| 70 | `2a` → `viral-handout-02a` |
| 71 | `2b` → `viral-handout-02b` |
| 72 | `3a` → `viral-handout-03a` |
| 73 | `3b` → `viral-handout-03b` |
| 74 | `4` → `viral-handout-04`; `5` → `viral-handout-05` |
| 75 | `6` → `viral-handout-06`; `7` → `viral-handout-07` |
| 76 | `8` → `viral-handout-08` |
| 77 | `9` → `viral-handout-09` |
| 78 | `10` → `viral-handout-10`; `11` → `viral-handout-11` |
| 79 | `12` → `viral-handout-12` |
| 80 | `13` → `viral-handout-13` |
| 81 | `14` → `viral-handout-14` |
| 82 | contextual `Hyeon's iPads` → `viral-handouts-hyeons-ipads` (not numbered) |
| 83-92 | `15..24` → `viral-handout-15` .. `viral-handout-24`, one per page in order |
| 93 | `25` → `viral-handout-25`; `26` → `viral-handout-26`; `27` → `viral-handout-27` |
| 94-99 | `28..33` → `viral-handout-28` .. `viral-handout-33`, one per page in order |
| 100 | `34` → `viral-handout-34`; `35` → `viral-handout-35` |
| 101 | `36` → `viral-handout-36`; `37` → `viral-handout-37` |
| 102 | `38` → `viral-handout-38` |
| 103 | `39` → `viral-handout-39` |

Each handout config row must contain: `label`, `ordinal`, optional `variant`, `source_page`, `source_region_or_blocks`, `title`, `anchor`, `representation` (`semantic`, `visual`, or `hybrid`), `owned_asset_ids`, `narrative_reference_sources`, and `provenance_unit_ids`. The builder fails duplicate labels, missing ordinals, invented labels, mismatched pages, or any narrative link whose target is not the canonical appendix unit.

Reader policy is canonical appendix only: body occurrences contain a short semantic link such as `[Handout 28](#viral-handout-28)`, never a second full handout body. The appendix index lists all 41 identities in source order. Contextual keeper notes stay adjacent to the one canonical unit they govern and are not silently discarded.

## 7. Table, card, and statblock closure

### Stage boundary

The v3 Markdown contains table-looking pipe rows but effectively zero reliably parseable semantic CommonMark tables because blank lines separate headers, delimiters, and rows. Other source tables/statblocks are flattened prose or raster crops. That is not itself a reason to put presentation work back into reconstruction.

The exact boundary is:

- **Reconstruction/v4 owns facts**: every source label, row, cell, characteristic, attack, damage value, die expression, note, and ordering relation must exist accurately in the accepted reconstruction/provenance. If a row/value is absent or corrupt, it is a v4 `text_repair` blocker. A raster table crop alone may be retained as evidence, but it does not prove a source-complete semantic fact ledger.
- **Publication/Step 7 owns presentation**: once facts are source-complete, Step 7 may join pipe rows, promote flattened rows into semantic Markdown tables, group statblock fields, create accessible labels/captions, and lay out weapon/rule cards. These operations must be lexical-value preserving.
- MASTER_EN must never read missing values from the PDF/image as an editorial convenience. Any such recovery changes the accepted reconstruction and requires a new reconstruction successor.

### Required closure inventory

The publication config must enumerate, at minimum, these source-backed structures and classify each as `semantic_table`, `semantic_statblock`, `semantic_card`, or `visual_form`:

- pages 20-21: Rumors, rolls 1-10;
- pages 21-22: Signs and Portents, rolls 1-10;
- page 34: STR rowing-speed results;
- page 36: Lemon Grove Results, rolls 1-10 plus its general SAN note;
- page 55: DSS Incendiary Grenades weapon card/statline and distance-damage note;
- pages 58-59: Outdoor Encounters, D12;
- page 59: Hospital Encounters, D12;
- page 60: Catacomb Encounters, D6;
- page 62: Taint Levels, levels 1-10, with all modifiers/effects;
- page 63: Insanity and Bouts of Madness, D10;
- page 64: Paranormal Phenomena, D10;
- page 65: Hastalÿk / Devourer characteristics, attacks, armor, SAN, and abilities;
- page 66: Plague Monk characteristics/attacks/abilities;
- pages 66-67: Reliquae characteristics, attacks/abilities, and both infection progressions;
- page 67: Iuramentum Corruptionis tome/rules card;
- page 68: Control Reliquae spell/rules card;
- pages 111, 113, 115, 117, 119, and 121: five populated investigator-sheet fronts plus the blank front as `visual_form` units whose closure is complete legibility and source visual parity, not an invented partial Markdown transcription;
- pages 112, 114, 116, 118, 120, and 122: semantic background/equipment/quick-reference structures, paired with their front-form owners.

This inventory is a minimum, not permission to ignore another source table/card found by the v4 content audits. The final v4-derived inventory is closed when every structure has an expected key/row/field ledger and a representation decision.

For semantic tables, QA parses the Markdown with the target renderer's CommonMark/GFM table parser and compares ordered headers, row keys, cell values, notes, and dice expressions against the accepted reconstruction fact ledger. Blank lines that split a table are forbidden. For statblocks/cards, QA compares named fields and ordered attacks/abilities. A source raster table crop becomes `evidence_only` when an exact semantic table replaces it; showing both is reader duplication and fails unless the config explicitly classifies the image as independently meaningful visual art. Seven known table raster crops around pages 55, 62, 65, 66, and 67 therefore default to evidence-only after semantic closure.

## 8. Asset ownership and visual-only-page policy

The v3 asset manifest has 121 rows: `full_page` 7, `full_width` 35, `handout` 19, `inline` 47, `map` 11, and `reference_only` 2. The accepted reconstruction references 119 unique assets. The two small unreferenced page-1 `reference_only` crops (`e1e2...6ce85.jpg`, 270×276; `a1d8...acd6c1.jpg`, 153×79) are not a complete cover and must not be promoted as one.

Every candidate asset row must have:

```text
asset_id / sha256 / bytes / media_type / dimensions
source_page + source_region or deterministic source_page_render declaration
semantic_role
representation: reader | evidence_only
owner_anchor (exactly one primary owner)
placement_index
alt_text
visual_review_status and evidence
```

Rules:

1. No orphan reader asset, missing referenced asset, basename collision, duplicate binary under different IDs, or unowned page continuation.
2. Reader alt text describes the depicted subject/function. Phrases such as `Source illustration on page 56`, `Source table on page 55`, hashes, crop coordinates, OCR decisions, and overlay labels are technical noise and fail QA.
3. Page 1 and page 124 require deterministic full-page renders from the immutable clean source PDF because the current extracted crops do not preserve the complete covers. Render declarations pin source hash, page index, media box, rotation, resolution, color profile, alpha/background policy, encoder version/settings, and metadata stripping. Output names are content-addressed. The builder may not render from `SELECTED_OVERLAY.pdf`.
4. Page 2 uses semantic credits plus owned material logo/art assets; avoid duplicating a full screenshot behind identical visible text.
5. Pages 69-103 use semantic/hybrid handout units. A visual/form handout must retain all meaningful marks, handwriting, signatures, symbols, or layout relationships; a text-only handout may use semantic text without a page screenshot. This is decided per config row and visually reviewed.
6. Keeper maps:
   - `viral-keeper-map-isola-location` (p104 approximate-location map and note),
   - `viral-keeper-map-isola-overview` (p105),
   - `viral-keeper-map-ground-floor-basement` (p106 plus p107 continuation),
   - `viral-keeper-map-second-third-floors` (p108),
   - `viral-keeper-map-administrators-house-east-wing-attic` (p109),
   - `viral-keeper-map-secret-underground` (p110).
   Keys, legends, and scale text remain semantic and adjacent. Page 107 must be owned by the p106 map unit with ordered placement 2.
7. Pregen fronts on p111/113/115/117/119 and the blank front p121 remain complete visual forms. Corresponding backs are semantic/hybrid. Use paired anchors:
   - `viral-pregen-marco-front` / `viral-pregen-marco-background`;
   - `viral-pregen-corrina-front` / `viral-pregen-corrina-background`;
   - `viral-pregen-enoch-front` / `viral-pregen-enoch-background`;
   - `viral-pregen-peter-front` / `viral-pregen-peter-background`;
   - `viral-pregen-ku-hyeon-front` / `viral-pregen-ku-hyeon-background`;
   - `viral-pregen-blank-front` / `viral-pregen-blank-background`.
8. Page 123 merchandise and QR assets remain owned by `viral-merchandise`; the QR is source content, not a live-link acceptance claim.

Visual QA must inspect 100% of cover/back-cover, 41 handout units, 6 map units covering all seven pages, 12 pregen/template pages, and page 123. Sampling is not sufficient for these classes.

## 9. Typography, obvious reconstruction correction, and authorial text

### Allowed Step 7 transformations

- heading-level and callout restructuring;
- generated TOC and semantic link insertion;
- list/table/statblock/card formatting from already complete accepted facts;
- removal of source-page comments, overlay/OCR notes, evidence-only images, hash/crop labels, and reader-facing technical alt text;
- whitespace, paragraph-flow, and Markdown escaping normalization where rendered lexical content is unchanged;
- relocation without duplication, recorded in provenance;
- semantic alt text and accessibility labeling that describe rather than rewrite source prose.

### Reconstruction-only corrections

Any change to a visible source word, letter, number, punctuation mark that changes meaning, proper-name spelling/diacritic, table value, location label, or rules value is a reconstruction correction even when visually “obvious.” The proven p20/p42/p44/p45/p49/p50/p62/p65 classes therefore require v4. Source-proven apostrophe/quote glyph restoration also belongs in v4 when it changes the accepted text bytes; Step 7 does not use typography normalization as a covert lexical repair channel.

### Authorial text protection

Apparent grammar, idiom, continuity, punctuation, or factual oddities that are visibly present in the source remain authorial text. Step 7 must not silently copyedit them. The p62 specific source occurrence `Hastaÿk's corruption`, the separate p65 source occurrence `Hasalÿk`, and the p104 wording `It's specific location` / `It's actual location` are preserved exactly where the source shows them. By contrast, the p65 heading is source-exact `Aspect of Hastalÿk` and v4 must correct reconstructed `Aspect of Hastalijk` to that form. Canonical source-visible `Hastalÿk` occurrences remain canonical. Global name-normalization is forbidden. A desired authorial correction requires an explicit user editorial decision, a declared publication exception/operation, and provenance distinct from source reconstruction. No such exceptions are authorized in the current runtime contract.

## 10. Source traceability without reader noise

Traceability lives in sidecars, not visible reader scaffolding.

Required candidate sidecars:

- `MASTER_EN.provenance.json`: one row per reader unit, with `anchor`, ordered source pages/blocks, accepted reconstruction unit IDs/hashes, operation (`retained`, `structured`, `relocated`, `linked`, `visualized`), output span hash, and asset IDs;
- `SOURCE_DISPOSITION.json`: exact pages 1-124 plus sub-units, disposition, target anchors, and closure status;
- `ASSET_MANIFEST.json`: reader/evidence classification and ownership contract from section 8;
- `MASTER_EN.qa.json` and `MASTER_EN.qa.md`: machine and human gate evidence;
- `MASTER_EN.acceptance.json`: absent for an unaccepted candidate and created only by the separate freeze/promote operation after exact explicit user acceptance.

`MASTER_EN.md` must contain no `source-page-*` comments, OCR/merge/overlay terminology, file-system paths, hashes, coordinates, confidence scores, evidence IDs, or alt text that says only “source image/table on page N.” It may contain normal author-facing notes that are part of the published scenario.

Provenance must remain path-independent: repository-relative logical locators and content hashes, never device-specific absolute paths. Every reader unit must trace to at least one accepted reconstruction unit; every accepted source unit must close through a reader unit or an explicitly contract-authorized suppression. With current exceptions empty, source-content suppression count is zero.

## 11. Deterministic builder/config interface

No Viral MASTER_EN builder exists at inspection time. Engineering should implement a reusable scenario publication entry point rather than fork Innsmouth logic:

```powershell
python -B kb_creator/scripts/build_scenario_master_en.py `
  --contract kb_creator/contracts/viral.json `
  --reconstruction-package <accepted-v4-package-root> `
  --publication-config kb_creator/working/viral/master_en/publication_config_v1.json `
  --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf `
  --target kb_creator/working/viral/master_en/candidates/<candidate-id>
```

The `<accepted-v4-package-root>` and config must pin exact SHA-256/byte identities for the v4 reconstruction Markdown, all required sidecars/assets, source PDF, runtime contract, and accepted reconstruction-review receipt. The source PDF is available only to declared deterministic `source_page_render` asset operations; it is not a fallback text source.

### Config minimum schema

```json
{
  "schema": "kb_creator.master_en_publication.v1",
  "scenario_id": "viral",
  "contract": {"path": "kb_creator/contracts/viral.json", "sha256": "..."},
  "accepted_reconstruction": {
    "root": "...",
    "inventory_sha256": "...",
    "reconstructed_md_sha256": "...",
    "qa_sha256": "...",
    "provenance_sha256": "...",
    "asset_manifest_sha256": "...",
    "acceptance_receipt_sha256": "..."
  },
  "document": {"title": "Viral", "root_anchor": "viral", "source_pages": [1, 124]},
  "hierarchy": [],
  "source_disposition": [],
  "xrefs": [],
  "handouts": [],
  "structured_content": [],
  "assets": [],
  "visual_review_units": [],
  "reader_noise_patterns": []
}
```

The arrays are fully explicit data corresponding to sections 3-10; no scenario-specific behavior is hard-coded in the reusable builder.

### Candidate output contract

The target must be new and empty. Builder output is closed to:

```text
<candidate-id>/
  MASTER_EN.md
  MASTER_EN.provenance.json
  SOURCE_DISPOSITION.json
  ASSET_MANIFEST.json
  MASTER_EN.qa.json
  MASTER_EN.qa.md
  INVENTORY.json
  assets/<sha256>.<ext>
```

No `MASTER_EN.acceptance.json` appears in a review candidate. The builder refuses an occupied target, hidden fallback input, unpinned predecessor, path escape, extra output, or current-time-dependent content.

Canonical serialization is UTF-8 without BOM, LF newlines, stable JSON key ordering/indentation, stable array order from config, stripped generated-image metadata, and content-addressed asset names. Two fresh builds from the same pinned inputs/config must have byte-identical files and identical closed inventory digest. The independent verifier reads outputs without importing builder implementation and validates the same contracts.

Promotion is a separate, later operation to a new root shaped like:

`kb_creator/inputs/viral/master_en/accepted_<YYYYMMDD>[_rN]/`

It requires expected candidate root digest, expected `MASTER_EN.md` and QA hashes, explicit user acceptance of those exact identities, and an independent release review. It refuses overwrite. Translation, HTML, PDF, production snapshot, and Git publication are outside Step 7.

## 12. Acceptance gates

All gates are fail-closed:

1. **Accepted reconstruction** — exact accepted v4 identities match config; v4 has no open reconstruction blockers; both bounded content-audit ranges are dispositioned in its correction/QA evidence.
2. **Source disposition** — pages 1-124 exactly once, all sub-units closed, zero unauthorized source-content suppressions, and every accepted reconstruction unit accounted for.
3. **Semantic navigation** — one H1, declared hierarchy present, anchors unique and heading-bound, generated TOC complete, all internal links resolved, zero unclassified printed references.
4. **Handout mapping** — ordinals 1..39 complete; physical labels exactly `{1,2a,2b,3a,3b,4..39}` (41 units); page map exact; p82 contextual; no duplicate handout bodies; every narrative reference targets the canonical unit.
5. **Table/statblock closure** — final v4-derived inventory complete; every semantic table parses; headers/rows/cells/notes and every stat/card field match the accepted fact ledger; visual forms legible and paired; no raster table used as a substitute for missing source facts.
6. **Asset closure** — all reader references resolve, all reader assets content-addressed and singly owned, no orphan/duplicate/missing asset, evidence-only crops absent from reader, covers/maps/forms close visually, source/overlay identities correct.
7. **No technical reader noise** — zero source-page/overlay/OCR/provenance comments, coordinates, device paths, hashes, evidence-only labels, or technical page-number alt text in reader content.
8. **Lexical conservation** — every visible lexical delta from accepted v4 is classified as structural Markdown representation, link wrapper, relocation, or an explicitly authorized editorial operation. Current authorized editorial lexical delta count is zero.
9. **Determinism and closed inventory** — two clean builds byte-identical; verifier passes; only declared output files exist; all file hashes/bytes recorded.
10. **Full visual QA** — 100% review of cover/back cover, all handout units, all map pages/units, all pregen/template pages, page 123, and every structured table/statblock/card at rendered-reader scale. No clipping, illegible text, wrong order, duplicate rendering, or overlay artifacts.
11. **Independent release review** — an independent `gpt-5.5` release critic confirms the candidate/evidence meets this contract. This cannot substitute for user acceptance.
12. **Explicit user reading acceptance** — mandatory final MASTER_EN authority, as below.

## 13. Explicit user reading acceptance boundary

Automated QA, visual QA, architecture approval, reconstruction acceptance, and independent critic review do not accept MASTER_EN on the user's behalf.

The user-review packet must provide the complete candidate `MASTER_EN.md` with all reader assets, a concise issue/decision ledger, QA summaries, and exact candidate root / MASTER_EN / QA hashes and byte counts. The user must read the complete reader artifact and explicitly accept the exact immutable identities, for example:

> I accept the Viral MASTER_EN candidate with MASTER_EN SHA-256 `<hash>` and candidate inventory SHA-256 `<hash>` as the English publication source for promotion.

Before that statement, status is `candidate_for_user_reading`, never `accepted`. Ambiguous approval of a screenshot, sample pages, QA report, or reconstruction package is insufficient. Any byte change after acceptance invalidates it and requires a new candidate identity, rerun gates, renewed release review as applicable, and new explicit user acceptance. Only the separate freeze/promote operation records the acceptance text, timestamp, exact identities, contract hash, reconstruction lineage, and accepting authority in `MASTER_EN.acceptance.json`.

No MASTER_RU work may consume the candidate before this boundary closes.

## 14. Risks and open execution facts

| Risk / unresolved fact | Consequence | Required mitigation / owner |
|---|---|---|
| v4 and its two content-audit receipt identities do not yet exist | Builder pins cannot be finalized; Step 7 cannot start | Reconstruction owner produces minimal v4 and independent acceptance; orchestrator records hashes. |
| p20/p44 corruptions are systematic rather than isolated | Correcting only headings leaves corrupt prose/table facts | Bounded full-page and same-class audit in v4; no MASTER_EN patching. |
| Table crops may hide facts absent from v3 prose, especially Taint Levels | Semantic tables could be incomplete while looking valid | v4 fact-ledger closure against source/overlay before publication restructuring. |
| Cover/back-cover full visuals are absent as complete current reader assets | Visual page roles would fail | Deterministic clean-source page renders under the declared asset contract; 100% visual QA. |
| Hybrid handouts can duplicate text or lose material layout marks | Reader noise or content loss | Per-handout representation/ownership decision and full 41-unit review. |
| Printed references can be mistaken for external references | Broken or misleading navigation | Explicit xref ledger plus zero-unclassified-hit scan; preserve Keeper Rulebook p125 as external. |
| Source grammar/typos may tempt silent cleanup | Loss of source fidelity and unreviewed authorship | Preserve authorial text; require explicit user editorial exception for any non-reconstruction change. |
| Generic Innsmouth implementation may encode scenario assumptions | Wrong Viral scope/handouts/assets | Reusable data-driven builder; Viral config is sole scenario policy; no Innsmouth hashes/rules. |

There is no material user choice required to proceed with the minimal v4 correction and then build a review candidate. Any proposed authorial copyedit, suppression, handout renumbering, or replacement of source QR/merchandise content is a new user decision outside this packet.

## 15. Verification performed for this architecture receipt

- Read canonical plan/context/governance and the actual runtime contract.
- Verified the initial `scenario_contract.yaml` locator is absent and used `kb_creator/contracts/viral.json`.
- Inspected actual v3 `RECONSTRUCTED_EN.md`, package manifests/provenance/QA, selected page ranges, asset classes, handout labels, map/pregen pages, and accepted review evidence.
- Inspected source/overlay visual evidence for cover, back cover, handouts, maps, pregens, and the demonstrated reconstruction defect classes.
- Reconciled page roles and all 124 pages against the contract.
- Used Innsmouth README/PIPELINE only for generic stage/interface lessons and did not import scenario-specific rules.
- Per scoped override, ran no code, tests, build, MinerU, or Git operation and changed no file except this receipt.

Architecture result: **complete; Step 7 implementation is specified but blocked until accepted minimal v4 reconstruction correction evidence is pinned.**
