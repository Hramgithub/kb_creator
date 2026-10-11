# Viral Step 7 MASTER_EN content/publication audit — source pages 069–124

Date: 2026-09-01  
Role: content/publication audit, read-only except for this receipt  
Scope: accepted English reconstruction source pages 069–124 only  
Disposition: BLOCKED_BEFORE_BUILD

## Result

The accepted v3 reconstruction is structurally sufficient to specify the complete player-handout, Keeper-map, pre-generated-investigator, merchandise, and back-cover publication contract, but it is not yet a safe direct MASTER_EN build input.

Two definite P1 blockers must be closed before publication:

1. Page 080 contains a source-proven reconstruction corruption in the handwritten direction after Marco's intro.
2. Page 124 has no accepted clean full-page reader asset, although the back cover is a retained-visual source page.

Three source titles are also absent from the accepted selected-block fact set and from RECONSTRUCTED_EN.md: page 069 “Isola di Malamente – Original Google Map”, page 074 “Marco's Emails”, and page 075 “Maya's Emails (1 of 2)”. They are visible in the source/overlay and in unselected merge-packet blocks. They must be promoted into the corrected accepted reconstruction/fact ledger before MASTER_EN may expose them as lexical reader text. Stage 7 must not silently recover them from the PDF.

No pre-generated-investigator Quick Reference Rules facts were lost on pages 112/114/116/118/120/122. The apparent drift is normalization or correct OCR repair. Publication still needs one semantic Levels of Success table, explicit subheadings, and a consistent visual/semantic treatment.

## Authority and packet identity

Normative Step 7 architecture packet:

- Path: kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_publication_packet_20260901.md
- Bytes: 43,067
- SHA-256: 36B20416AEF0D7B7031859DAC119D65D99B61F0CA10C25CB44C34B0F23036117

Audited accepted evidence:

| File | Bytes | SHA-256 |
|---|---:|---|
| RECONSTRUCTED_EN.md | 346,580 | 5D28F097708CB9D58A5A0D4C72CC93E9985FC7CDB00C22EFDB0A22C9931B79ED |
| SELECTED_OVERLAY.pdf | 27,696,569 | 62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB |
| ASSET_MANIFEST.json | 50,739 | 914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9 |
| RECONSTRUCTION_PROVENANCE.json | 228,782 | 7872946148455CA277E2639C0E9D19894BD7BF9ACEC28E4AD971A11111B10DA7 |

The overlay is evidence only. It must never be copied, linked, or rendered into reader-facing output because it contains selection boxes and technical annotations.

## P1 reconstruction and asset blockers

| Page / selector | Current accepted text or state | Required accepted state before MASTER_EN | Evidence | Severity / uncertainty |
|---|---|---|---|---|
| p080, final handwritten paragraph in page-080.md | “They Marco Batez, make sure you emphasize the / do if parts when you're doing your thing. You've got this! / It's going to be the best stream EVER!” | “Hey Marco Babez, make sure you emphasize the bold parts when you're doing your thing. You've got this! It's going to be the best stream EVER!” Preserve the handwritten-note paragraph as a distinct source block. | Direct source-page visual; selected original_hybrid raw 1253 is visibly corrupt and raster_hybrid raw 1289 is also unreliable. | P1. “Babez” is the direct visual reading; because the handwriting is stylized, pin the exact glyph sequence in the corrected fact ledger and have the reconstruction reviewer confirm it. |
| p069, after Player Handouts | Accepted selected blocks contain only “Player Handouts” and the generic image description; title absent. | Corrected reconstruction must add source title “Isola di Malamente – Original Google Map” before the map. MASTER_EN then uses it as the Handout 1 title. | Merge packet original_pipeline_ocr raw 1236 and direct source visual; raw 1236 was not selected in v3. | P1 lexical fact gap. Do not add only at publication time. Dash glyph may be normalized typographically after the exact source wording is pinned. |
| p074, before Handout #4 | Source title absent; selected blocks begin with email fields. | Corrected reconstruction must add “Marco's Emails” as the shared page/source title above Handouts 4 and 5. | Direct source visual; merge packet original_hybrid raw 1218 / raster_hybrid raw 1254, neither selected. | P1 lexical fact gap. |
| p075, before Handout #6 | Source title absent; selected blocks begin with email fields. | Corrected reconstruction must add “Maya's Emails (1 of 2)” as the shared page/source title above Handouts 6 and 7. | Direct source visual; original_hybrid raw 1222–1223 / raster_hybrid raw 1258–1259, none selected. | P1 lexical fact gap. |
| p124, reader asset ownership | No page-124 asset row and no reader image; Markdown contains a transcript only. | Deterministically render the immutable clean source PDF page 124 as one full-page retained_visual asset. Put it at the close under viral-back-cover. Suppress the duplicated visible transcript; keep extracted text in provenance/QA sidecars. | Direct clean source-page visual; ASSET_MANIFEST has no p124 row; contract role back_cover. | P1 asset closure. Do not use SELECTED_OVERLAY.pdf. |

These blockers are upstream or publication-input closure. They are not authorization to rewrite the source prose during Step 7.

## Canonical document hierarchy and anchors

MASTER_EN must contain one H1 only: Viral.

For this range, use these H2 section anchors:

| Section | Anchor | Pages |
|---|---|---:|
| Player Handouts | viral-player-handouts | 069–103 |
| Keeper Maps | viral-keeper-maps | 104–110 |
| Pregenerated Investigators | viral-pregenerated-investigators | 111–122 |
| Merchandise | viral-merchandise | 123 |
| Back Cover | viral-back-cover | 124 |

Every physical handout is an H3 unit with an explicit ASCII scenario-prefixed anchor. Its printed/source title is subordinate H4 context when the physical label itself is the canonical H3 identity. Page-local source headings currently expressed as H1 on pages 087–124 must therefore be demoted. Do not rely on renderer-generated slugs.

The contextual Hyeon's iPads material on page 082 is not a numbered physical handout. Give it the stable anchor viral-handouts-hyeons-ipads under Player Handouts; do not invent Handout 14a or 14b.

Source-page comments such as <!-- source-page-069 --> are traceability metadata, not reader prose. Remove them from MASTER_EN and preserve page traceability in provenance/sidecars.

## Canonical physical handout map and exact required handling

| Source page | Physical label | Canonical anchor | Source title / context | Representation and exact publication handling |
|---:|---|---|---|---|
| 069 | 1 | viral-handout-01 | Isola di Malamente – Original Google Map | Visual handout. After corrected reconstruction admits the missing title, place the map immediately under the unit. Remove the standalone generic image-description paragraph; retain a concise source-grounded alt. |
| 070 | 2a | viral-handout-02a | The Sight: Player Reference Sheet | Semantic text. Preserve all prose and inline labels; normalize only hierarchy. |
| 071 | 2b | viral-handout-02b | The Sight: Player Reference Sheet | Semantic continuation. Keep the physical 2b identity; do not merge away the body-link target. |
| 072 | 3a | viral-handout-03a | How to Be a Ghost Hunter: Getting into the Mindset | Semantic text. Preserve authorial wording and named works. |
| 073 | 3b | viral-handout-03b | How to Be a Ghost Hunter: Recommended Viewing | Semantic continuation. Preserve the physical 3b identity. |
| 074 | 4 | viral-handout-04 | Marco's Emails, first panel | Hybrid. Put source title above the pair, then Handout 4 before the first email text and page-074-asset-1 directly in this unit. |
| 074 | 5 | viral-handout-05 | Marco's Emails, second panel | Hybrid. Put Handout 5 before its continuation text and page-074-asset-2 directly in this unit. Do not leave both images after both text blocks. |
| 075 | 6 | viral-handout-06 | Maya's Emails (1 of 2), first panel | Hybrid. Put source title above the pair, then Handout 6 before the first email text and page-075-asset-1 in this unit. |
| 075 | 7 | viral-handout-07 | Maya's Emails (1 of 2), second panel | Hybrid. Put Handout 7 before its continuation text and page-075-asset-2 in this unit. Preserve source-authorial “upshot of us” and “a millions subs babez”. |
| 076 | 8 | viral-handout-08 | Maya's Emails (2 of 2) | Visual handout. Retain the full email-continuation asset. The image owns the p.s./p.p.s./attachment layout; do not invent a partial Markdown transcription. |
| 077 | 9 | viral-handout-09 | Printout of Island Map with Notes | Visual handout. Keep annotated island map full-width. |
| 078 | 10 | viral-handout-10 | Saint Roche's Hospital – Photocopy from Maya (Player's Map) | Visual handout. Move the player-map asset directly under Handout 10, before Handout 11. |
| 078 | 11 | viral-handout-11 | Enoch's Vision | Semantic text. Keep the vision paragraph after its own anchor; no map asset belongs here. |
| 079 | 12 | viral-handout-12 | Corrina's Research | Semantic text. Convert bullet glyphs to Markdown list markers without changing wording. |
| 080 | 13 | viral-handout-13 | Marco's Intro Script | Semantic text. Publish only after the handwritten note is corrected upstream; retain [Intro Script] as a subordinate source label. |
| 081 | 14 | viral-handout-14 | Isola di Malamente Lighthouse | Visual handout. Remove the duplicate generic description paragraph; keep a concise alt and the image. |
| 082 | — | viral-handouts-hyeons-ipads | Hyeon's iPads / The Stream Begins / Keeper's Notes | Contextual semantic-plus-visual unit. Keep all prose and Keeper's Notes. Remove the generic duplicate image-description paragraph; keep a concise alt. |
| 083 | 15 | viral-handout-15 | The Stream Begins/The Weeping Bridge | Semantic handout. Put anchor/identity before all iPad blocks; normalize bullet glyphs only. |
| 084 | 16 | viral-handout-16 | Lemon Grove | Semantic handout. Preserve “Most want Marcus to bite a lemon.” exactly; it is source-authorial. Normalize list markers only. |
| 085 | 17 | viral-handout-17 | The Cremation Pit | Semantic handout. Preserve “SATANSIST” exactly; it is source-authorial chat. Convert malformed bullet glyphs to Markdown list markers. |
| 086 | 18 | viral-handout-18 | Mass Graves | Semantic handout. Convert “·“OMG!!!”” to a Markdown bullet containing “OMG!!!”; lexical content unchanged. |
| 087 | 19 | viral-handout-19 | Outside the Hospital | Semantic handout. Demote current page H1 and move the physical anchor/heading before the body. |
| 088 | 20 | viral-handout-20 | Administrator's House | Same treatment as p087. |
| 089 | 21 | viral-handout-21 | Inside the Hospital #1 | Same treatment as p087. |
| 090 | 22 | viral-handout-22 | Inside the Hospital #2 | Same treatment as p087. |
| 091 | 23 | viral-handout-23 | Inside the Hospital #3: The Secret Rooms | Same treatment as p087. |
| 092 | 24 | viral-handout-24 | The Chapel | Same treatment as p087. |
| 093 | 25 | viral-handout-25 | The Crypt: The Witch Board Ritual | Move identity/anchor before its three iPad blocks. |
| 093 | 26 | viral-handout-26 | The Crypt: Following the Collapse | Move identity/anchor before its body. |
| 093 | 27 | viral-handout-27 | The Catacombs and Beyond | Move identity/anchor before its body. |
| 094 | 28 | viral-handout-28 | The Weeping Bridge | Visual handout. Move label/anchor before title/image. |
| 095 | 29 | viral-handout-29 | The Elder Sign | Visual handout. Move label/anchor before title/image. |
| 096 | 30 | viral-handout-30 | Something in the Window (The Plague Monk) | Visual handout. Use the parenthetical canonical disambiguator; keep source title wording. |
| 097 | 31 | viral-handout-31 | Something in the Window (Just Curtains) | Visual handout. Use the parenthetical canonical disambiguator; keep source title wording. |
| 098 | 32 | viral-handout-32 | Lemon Grove | Visual handout. Move label/anchor before title/image. |
| 099 | 33 | viral-handout-33 | Cremation Pit | Visual handout. Move label/anchor before title/image. |
| 100 | 34 | viral-handout-34 | The Witch Board | Visual handout. Put the anchor before its title/image. |
| 100 | 35 | viral-handout-35 | Book Fragment | Hybrid. Put the anchor before image and the Latin/English semantic text; retain both. |
| 101 | 36 | viral-handout-36 | The Catacombs | Visual handout. Put anchor before title/image. |
| 101 | 37 | viral-handout-37 | The Forgotten Knight | Visual handout. Put anchor before title/image. |
| 102 | 38 | viral-handout-38 | Hastalÿk Rises | Visual handout. Preserve the source diacritic. |
| 103 | 39 | viral-handout-39 | Hastalÿk Destroyed | Visual handout. Preserve the source diacritic. |

This is exactly 41 physical identities: 1, 2a, 2b, 3a, 3b, and 4 through 39. Page 082 is contextual and excluded from that count.

## Body-link targets

All body references must link to canonical physical anchors rather than page comments or generated slugs. The pages 001–068 audit supplies the source selectors; this range owns the targets:

| Body source selector | Visible reference | Target |
|---|---|---|
| p008 line/paragraph containing Handout #12 | Handout #12 | #viral-handout-12 |
| p032 first reference range | Handouts #1–7 | Link the phrase/range per architecture, with endpoint access to #viral-handout-01 through #viral-handout-07 and canonical index exposure of 2a/2b/3a/3b. Do not invent labels 2 or 3. |
| p032 later reference | Handout #11 | #viral-handout-11 |
| p033 | Handout #14 | #viral-handout-14 |
| p034 | Handout #28 | #viral-handout-28 |
| p035 | Handout #32 | #viral-handout-32 |
| p037 | Handouts #30 and #31 | #viral-handout-30 and #viral-handout-31 |
| p046 | Handout #33 | #viral-handout-33 |
| p047 | Handout #34 | #viral-handout-34 |
| p048 first reference | Handout #35 | #viral-handout-35 |
| p048 later reference | Handout #36 | #viral-handout-36 |
| p049 | Handout #37 | #viral-handout-37 |
| p050 | Handout #38 | #viral-handout-38 |
| p052 | Handout #39 | #viral-handout-39 |

The Player Handouts section must also expose a compact physical-handout index so variants 2a/2b and 3a/3b are directly navigable even where the body uses a range phrase.

## Keeper-map closure, pages 104–110

Use H2 Keeper Maps with these exact unit anchors and ownership:

| Pages | Canonical anchor | Required handling |
|---:|---|---|
| 104 | viral-keeper-map-isola-location | Retain the Gulf of Gela/location visual and its semantic note together. Preserve source-authorial “It's specific location” and “It's actual location”; do not grammar-correct them. |
| 105 | viral-keeper-map-isola-overview | Retain overview map full-width and keep the semantic location list adjacent. |
| 106–107 | viral-keeper-map-ground-floor-basement | One continuous unit. Order: p106 key, p106 ground-floor plan, p107 east-wing continuation. Never orphan p107 as a separate map section. Keep legend/key/scale text adjacent. |
| 108 | viral-keeper-map-second-third-floors | Retain second/third-floor map full-width with its key/legend. |
| 109 | viral-keeper-map-administrators-house-east-wing-attic | Retain the accepted composite Keeper map from original_pipeline_ocr. No decorative replacement. |
| 110 | viral-keeper-map-secret-underground | Retain secret-underground map full-width with semantic context. |

Current page-local H1 headings must be demoted beneath the single document H1 and H2 Keeper Maps.

## Pregenerated-investigator closure, pages 111–122

Use H2 Pregenerated Investigators and these exact unit anchors:

| Page | Anchor | Representation |
|---:|---|---|
| 111 | viral-pregen-marco-front | Visual-only form; retain clean full-page sheet. |
| 112 | viral-pregen-marco-background | Semantic/hybrid background; retain silhouette, semantic sections, Quick Reference Rules, and responsibilities. |
| 113 | viral-pregen-corrina-front | Visual-only form; retain clean full-page sheet. |
| 114 | viral-pregen-corrina-background | Semantic/hybrid background; same closure. |
| 115 | viral-pregen-enoch-front | Visual-only form; retain clean full-page sheet. |
| 116 | viral-pregen-enoch-background | Semantic/hybrid background; same closure. |
| 117 | viral-pregen-peter-front | Visual-only form; retain clean full-page sheet. |
| 118 | viral-pregen-peter-background | Semantic/hybrid background; same closure. |
| 119 | viral-pregen-ku-hyeon-front | Visual-only form; retain clean full-page sheet. |
| 120 | viral-pregen-ku-hyeon-background | Semantic/hybrid background; same closure. |
| 121 | viral-pregen-blank-front | Visual-only blank form; retain clean full-page template. |
| 122 | viral-pregen-blank-background | Semantic/hybrid blank background; retain silhouette and Fellow Investigators diagram. |

The front sheets are forms whose values and layout are owned by the full-page visual assets. Do not manufacture partial Markdown transcriptions. Closure is source visual parity and legibility at publication scale.

### Quick Reference Rules: exact semantic closure

Pages 112/114/116/118/120/122 repeat the same Quick Reference Rules. Publish a consistent semantic rendering in every background unit, or define one canonical reusable block that is visibly and accessibly present for each unit. Required substructure:

1. Subheading Skill & Characteristic Rolls.
2. Semantic Levels of Success table:

| Level of Success | Fumble | Fail | Regular | Hard | Extreme | Critical |
|---|---:|---:|---:|---:|---:|---:|
| Roll | 100/96+ | > skill | ≤ skill | ½ skill | ⅕ skill | 01 |

3. Pushing Rolls: Must justify reroll; Cannot Push Combat or Sanity Rolls.
4. Subheading Wounds & Healing.
5. Preserve all source rule statements:

- First Aid heals 1 HP;
- Medicine heals +1d3 HP
- Major Wound = loss of ≥ ½ max HP in one attack
- Reach 0 HP without Major Wound = Unconscious
- Reach 0 HP with Major Wound = Dying
- Dying: First Aid = temp. stabilised; then require Medicine
- Natural Heal rate (non Major Wound): recover 1 HP per day
- Natural Heal rate (Major Wound): weekly healing roll

The accepted reconstruction's 1HP → 1 HP difference is whitespace normalization, not fact loss. The levels table is visible in the accepted skill-reference crops and its source labels occur in the merge packets; the Markdown omission is a semantic-publication structure gap.

When the semantic table is present, classify the six repeated skill-reference crop assets on pages 112/114/116/118/120/122 as evidence_only and omit them from the reader. Showing the same rules as both a crop and a semantic table is reader duplication. Retain the six silhouettes; they are visual identity/layout elements rather than duplicate rule text.

### Pregen drift adjudication

| Page | Flagged token | Decision | Evidence / handling |
|---:|---|---|---|
| 112 | narcissit → narcissist | Correct reconstruction repair. | Source visual/original_hybrid reads narcissist; pipeline OCR raw 1663 is wrong. Keep narcissist. |
| 112/114/116/118/120/122 | 1HP → 1 HP | Safe whitespace normalization. | No numeric or rules fact changes. |
| 116 | repeasters → Repeaters | Correct reconstruction repair. | Source visual and accepted contextual wording support Repeaters; raw OCR token is noise. |
| 120 | thewool → the-wool | Correct reconstruction repair. | Source phrase is dyed-in-the-wool, split by layout/OCR. Keep accepted reconstruction. |
| 120 | “a significant portion is ties up in video and audio gear.” | Source-authorial wording. | Direct source visual confirms ties up. Do not change to tied up. |
| all backs | healing / wounds token-count delta | No source-fact loss. | All eight healing/wound statements are present. Add semantic headings/table; do not add new rules. |

## Merchandise and back cover

Page 123 is contractually inside the broad pre-generated-investigator run but its fine-grained reader role is Merchandise. Publish it under viral-merchandise. Retain source wording, five accepted product/QR assets, and the historical Zazzle presentation. Do not claim that prices, stock status, QR destination, or store availability are current.

Page 124 is retained_visual under viral-back-cover. The clean source page visibly contains the Marco Proudfoot quote, scenario blurb, and publisher logos. The one full-page visual is the reader representation; the transcript remains provenance/QA evidence and is not repeated visibly.

## Asset ownership and placement

The accepted range has 54 manifest asset rows, 54 reader references, no missing accepted file, and no unreferenced accepted file. Placement counts are full_page 6, full_width 2, handout 19, inline 16, and map 11. Pages 070–073, 079–080, and 083–093 are intentionally text-only. Page 124 is the only required new visual asset.

Exact accepted asset ownership for the visually sensitive range:

| Page(s) | Accepted logical assets | Publication ownership |
|---:|---|---|
| 069 | page-069-asset-1.jpg → assets/9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8.jpg | Handout 1 |
| 074 | page-074-asset-1.jpg → assets/9ee3d23cac4831e4230386f671d228d7a53b336310983f967eada4f3d2677ad8.jpg; page-074-asset-2.jpg → assets/b1b7888cf28240790d1fd7fdc5621da9fe159c9442ec0f3bfa7f45243319cfea.jpg | Handouts 4 and 5 respectively |
| 075 | page-075-asset-1.jpg → assets/f796716cd86ee8580b1d2cd8552d89cbf29f989bc8eae6be386ffa2528dc078b.jpg; page-075-asset-2.jpg → assets/2a60f183499c0a1a5f3bd353949a7efc2a389d5fbd98782e79e53d346d9c390f.jpg | Handouts 6 and 7 respectively |
| 076–078 | page-076-asset-1.jpg → assets/8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e.jpg; page-077-asset-1.jpg → assets/826e5103327297822e6270444f8d57d02a135ffbc2d246ffbdb5788d297fd55a.jpg; page-078-asset-1.jpg → assets/8dfcf412070881aa81b8933eeb329d7409edbe1316329701bb605c9dab835d65.jpg | Handouts 8, 9, and 10 respectively |
| 081–082 | page-081-asset-1.jpg → assets/5246e2c434242d2ddea6226d861d9608f5b6afa86230da5ad3b6d01553bb4ca5.jpg; page-082-asset-1.jpg → assets/2e49f854b389f6c5cf89bced8318e197b6e79fd53d47dfa5dd64b0dcd697bbcc.jpg | Handout 14; contextual Hyeon's iPads unit |
| 094–099 | page-094-weeping-bridge.jpg; page-095-elder-sign.jpg; page-096-plague-monk-window.jpg; page-097-curtains-window.jpg; page-098-lemon-grove.jpg; page-099-cremation-pit.jpg | Handouts 28–33 in order |
| 100–103 | page-100-witch-board.jpg; page-100-book-fragment.jpg; page-101-catacombs.jpg; page-101-forgotten-knight.jpg; page-102-hastalyk-rises.jpg; page-103-hastalyk-destroyed.jpg | Handouts 34–39 in order |
| 104–110 | page-104-gulf-of-gela-map.jpg; page-105-isola-di-malamente-map.jpg; page-106-ground-floor-key.jpg; page-106-ground-floor-plan.jpg; page-107-ground-floor-east-wing-map.jpg; page-108-second-third-floors-map.jpg; page-109-composite-keeper-map.jpg; page-110-secret-underground-map.jpg | Six canonical Keeper-map units; p106/p107 form one ordered continuation unit |
| 111/113/115/117/119/121 | six page-*-sheet-front/template-front.jpg full_page assets | Six pregen front units |
| 112/114/116/118/120/122 | six background silhouettes | Corresponding background units; retain |
| 112/114/116/118/120/122 | six skill-roll-reference.jpg crops | evidence_only after semantic table closure; omit from reader |
| 122 | page-122-fellow-investigators-diagram.jpg | Blank background unit; retain full-width |
| 123 | page-123-krew-tshirt.jpg; krew-hat.jpg; krew-patch.jpg; krew-badge-and-shirt.jpg; zazzle-qr.jpg | Merchandise unit; historical source content |
| 124 | no accepted asset | Must create one deterministic clean-source full-page retained_visual asset |

Do not copy source extraction paths into reader Markdown. MASTER_EN asset paths must point to publication-owned assets, with asset/provenance sidecars recording source page, source view, source path, and SHA-256.

## Tables, statblocks, and form closure

- Pages 069–110 contain no conventional statblock requiring reconstruction.
- The Hyeon's iPads and handout iPad blocks are structured prose/lists, not tables; do not force them into tables unless the publisher style requires it without changing content.
- The only required semantic table in this range is the repeated Levels of Success table on the pregen backs.
- Pages 111/113/115/117/119/121 are visual forms. The form labels, values, checkboxes, tracks, and handwritten/printed layout remain in the clean full-page visuals.
- Page 122's blank form fields remain blank. Do not infer sample values.
- Source bullet glyphs on pages 079 and 083–086 may be normalized to Markdown lists; this is structure-only.

## Source-block disposition and reader-noise rules

| Source block class | Disposition |
|---|---|
| Authorial prose, chat, email, captions, rule statements, map keys, responsibilities | Retain verbatim except source-proven extraction repairs admitted by the corrected reconstruction. |
| Physical Handout labels | Transform into canonical H3 units and explicit anchors; visible labels remain recognizable. |
| Page/source titles | Demote to subordinate headings; retain wording. Missing p069/p074/p075 titles require upstream acceptance first. |
| source-page comments | Relocate to provenance/sidecars; suppress from reader. |
| Generic AI image-description paragraphs on p069, p081, p082 | Suppress as duplicated technical reader noise; replace with concise source-grounded alt text. |
| Image alt strings containing boilerplate such as “no visible text or symbols” | Rewrite only as functional, source-grounded alt text. Do not add unverified interpretation. |
| Repeated skill-roll crop images | Retain as evidence_only, omit from reader after semantic table closure. |
| p124 transcript | Retain in provenance/QA; suppress visibly when the full-page back-cover asset is shown. |
| SELECTED_OVERLAY.pdf, merge paths, raw indices, hashes, decision labels | Evidence/technical metadata only; never reader content. |
| Merchandise prices, availability, QR | Retain as historical source depiction; no current-commerce assertion. |

No source content is approved for deletion. Suppression above applies only to duplicated technical descriptions, trace comments, or a transcript whose complete visual source is intentionally the reader representation.

## Source-authorial wording that must not be “fixed”

These suspicious strings were directly source-confirmed and are immutable:

- p075: “The upshot of us that ‘ain't fraid of no ghost’...” and “Here's to a millions subs babez!”
- p084: “Most want Marcus to bite a lemon.”
- p085: “IS IT FUCKIN' SATANSIST?!!!”
- p104: “It's specific location” and “It's actual location”.
- p120: “a significant portion is ties up in video and audio gear.”

Safe already-applied extraction repairs include p112 narcissit → narcissist, p116 repeasters → Repeaters, and p120 thewool → the-wool. These are source recovery, not editorial rewriting.

## Severity summary and uncertainty

| Severity | Finding | Closure |
|---|---|---|
| P1 | p080 handwritten note corrupt | Correct and accept in reconstruction v4/fact ledger; visual reviewer confirms “Babez”. |
| P1 | p069/p074/p075 source titles dropped from selected facts | Promote exact unselected source-title blocks into corrected reconstruction before publication. |
| P1 | p124 clean full-page asset absent | Deterministically render immutable clean source page 124; add publication asset/provenance row. |
| P2 | Canonical handout hierarchy/anchors and body links absent | Apply exact 41-unit map and link table above. |
| P2 | p074/p075/p078 multi-unit asset placement currently ambiguous/wrong | Relocate each asset into its owning physical unit without duplication. |
| P2 | Keeper-map continuation and pregen front/back ownership need semantic closure | Apply exact map and pregen anchors/representations above. |
| P2 | Quick Reference levels table/headings absent from semantic Markdown | Publish exact table and headings; mark repeated crops evidence_only. |
| P2 | Page-local H1s conflict with one-H1 document model | Demote under canonical H2/H3 hierarchy. |
| P3 | source-page comments, generic descriptions, duplicated visible back-cover transcript | Relocate/suppress as specified; preserve provenance. |

No uncertainty remains about the physical handout count/map, body-link targets, map continuity, pregen front/back pairing, Quick Reference Rules facts, or historical merchandise disposition. The only lexical uncertainty requiring an explicit visual confirmation is the stylized final character in p080 “Babez”; publication must use the corrected accepted reconstruction, not this receipt, as its lexical authority.

## Blockers and next action

Result: BLOCKED_BEFORE_BUILD.

Required next action:

1. Reconstruction owner emits and independently accepts corrected v4 with the p080 note and the three dropped source titles pinned in the fact ledger.
2. Publication owner creates the clean source-page-124 full-page asset and its provenance record.
3. Step 7 builder applies the exact hierarchy, canonical anchors, body links, asset ownership, table/form closure, and reader-noise dispositions in this receipt and the normative architecture packet.
4. QA verifies 41 physical handout anchors, all body targets, six Keeper-map units, twelve pregen front/back units, one semantic Quick Reference table model, 54 accepted v3 asset dispositions plus the new p124 asset, and zero overlay/technical-reader leakage.

Files changed by this audit: this receipt only. No source, contract, reconstruction, asset, code, test, build, MinerU, or Git operation was performed.
