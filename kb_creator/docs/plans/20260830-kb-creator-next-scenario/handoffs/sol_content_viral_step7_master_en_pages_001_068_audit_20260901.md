# Viral Step 7 MASTER_EN content audit: source pages 001–068

## Receipt

- Assignment: `/root/viral_step7_master_en_body_audit`.
- Role: bounded content/publication audit (`gpt-5.6-sol`, high).
- Scope: accepted Viral reconstruction source pages 1–68 only; read-only inspection of accepted Markdown/page decisions, frozen three-view merge packets, asset/provenance manifests, `SELECTED_OVERLAY.pdf`, the runtime contract, and the Step 7 architecture packet.
- Sole write: this handoff. No source/package/code/test/build/MinerU/Git mutation was performed.
- Result: **BLOCKED BEFORE MASTER_EN BUILD**. A minimal accepted reconstruction successor is required. The lexical blocker pages are `20, 42, 44, 45, 49, 50, 62, 65`; semantic fact recovery is additionally required for raster-only/partial structures on `34, 55, 62, 65, 66, 67`. Once that successor is accepted, the remaining items in this report are publication-only structural transformations.
- Confidence: high for every exact blocker and mapping below; source-visible evidence and all three frozen views were inspected where selector routing matters. No unverified authorial copyedit is proposed.

## Immutable evidence identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| accepted v3 `RECONSTRUCTED_EN.md` | 346,580 | `5D28F097708CB9D58A5A0D4C72CC93E9985FC7CDB00C22EFDB0A22C9931B79ED` |
| accepted v3 `SELECTED_OVERLAY.pdf` | 27,696,569 | `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB` |
| accepted v3 portable package inventory (canonical status) | n/a | `46E61F5DB9853E795C636147C63230936221F056DE1A9C25B19A4C8DEAEA215E` |
| current resealed Step 7 architecture packet | 43,067 | `36B20416AEF0D7B7031859DAC119D65D99B61F0CA10C25CB44C34B0F23036117` |

The initial unsealed architecture draft contained two identity transcription errors. The orchestrator corrected them before normative use; the current resealed packet records the exact reconstruction, package inventory, candidate inventory, and Step 6 review identities. There is no current architecture-identity contradiction.

## 1. Reconstruction-owned blockers (not MASTER_EN transformations)

The runtime exception taxonomy places `text_repair` at `reconstructed_en`. These corrections must be made in a minimal successor to accepted v3 and independently accepted before Step 7. MASTER_EN must not silently absorb them.

### 1.1 Exact lexical correction ledger

| Severity | Page / accepted selector | Accepted before | Source-proven after / required handling | Safest source and selector disposition |
|---|---|---|---|---|
| P1 | p20, decision `markdown`; selected `original_pipeline_ocr` raw `281..301` | Entire decision body has systematic lowercase `l`→`e` corruption, including `Nuncio wiee`, `Locae Teens`, `Isoea di Maeamente`, `Ceee phone`, `## Expeoring in Perea`, `| Roee | Rumor |`, and every rumor row. | Rebuild the **entire p20 decision Markdown body**, not isolated words. Source heading is `Exploring in Perla`; restore all prose and the complete Rumors table, rows 1–6, exactly. | The already selected pipeline raw text `281..301` is substantially correct and uniquely preserves rumor rows; use it plus the overlay for row numbers/table closure. Keep selector order and `page-020-image-01.jpg`. Do **not** switch wholesale to either hybrid: both lose the rumor list in an empty list block. |
| P1 | p42 line 37; room selector rendered as heading | `## 10. Acute Ward – ...` | `1O. Acute Ward – ...` (letter `O`, not zero). | All three frozen views read `10`; no selector switch helps. Exact source-visible decision Markdown repair; retain order/assets. |
| P1 | p44, decision `markdown`; selected `original_hybrid` raw `735..752` | Systematic capital `H`→`a` corruption throughout decision Markdown. | Rebuild the **entire p44 decision Markdown body** from the selected raw blocks, then source-correct the name glyph to `Hastalÿk`. | All selected original-hybrid blocks already preserve the `H` words and order; keep selectors and `page-044-image-01.jpg`. No wholesale view replacement is needed. Raw 747 has `Hastalýk`; overlay proves `Hastalÿk`. |
| P1 | p45 line 31 | `2I. Acute Ward – See 10.` | `2I. Acute Ward – See 1O.` | All views inherit the zero/O error. Exact source-visible Markdown repair; retain selector/order/assets. |
| P1 | p49 line 33 | `Hastalijk Awakens` | `Hastalÿk Awakens` | Hybrid/raw alternatives do not preserve the exact glyph; source-visible Markdown repair only. |
| P1 | p50 line 3 | `Hastalijk Rises.` | `Hastalÿk Rises.` | No exact alternate view; source-visible Markdown repair only. |
| P1 | p62 line 9, selected pipeline raw 1069 | `This is intended to represent Hastalÿk's corruption...` | Restore the source occurrence `This is intended to represent Hastaÿk's corruption...` (missing `l` is authorial/source text). | Character-level overlay evidence gives `Hastaÿk’s` at x≈262.94/top≈211.93. All three frozen views have `Hastayk`; none is exact. Keep selector and repair only this occurrence from source. Other p62 occurrences visibly read canonical `Hastalÿk` and remain canonical. |
| P1 | p65 line 21 | `Aspect of Hastalijk` | `Aspect of Hastalÿk` | Pipeline raw 1150 says `Hastalük`; hybrids say `Hastalijk`. No exact alternate; source-visible repair only. |

Exhaustive same-class scan result: the lowercase `l`→`e` family occurs only on p20 in pages 1–68; the capital `H`→`a` family occurs only on p44. The p20 affected span is page Markdown lines 3–39 (all prose/heading/table content); the p44 affected substrings are exactly:

- `a aard Spot aidden` → `a Hard Spot Hidden`;
- all three `Administrator's aouse` → `Administrator's House`;
- `ae dealt` → `He dealt`;
- `Spot aidden` → `Spot Hidden`;
- `ais name` → `His name`;
- `ais friends` → `His friends`;
- `ae managed` → `He managed`;
- `aastalýk` → `Hastalÿk`;
- `ae reaches` → `He reaches`.

### 1.2 Reconstruction fact-ledger gaps needed before semantic publication

These source facts currently survive only in raster table crops or are incomplete in decision prose. Step 7 may format accepted facts, but it may not read missing values from the overlay/PDF. The reconstruction successor must first add exact source-backed fact rows/fields. Frozen `table` blocks on p34, p55, p62, p66 and p67 have zero text in all available views, so wholesale selector switching cannot close them.

| Severity | Page / current evidence | Required reconstruction successor closure | Safest correction source |
|---|---|---|---|
| P1 | p34 `page-034-table-01.jpg`, asset `7c83b1...a712`; all table blocks text length 0 | Add `STR Roll / Result`: `Fumble / Lose an oar in the water.`; `Failure / 1 mph`; `Success / 2 mph`; `Hard Success / 3 mph`; `Extreme Success / 4 mph`. | Exact source-visible transcription from selected original-hybrid crop/overlay into the p34 decision fact ledger; keep the current prose/order/art. |
| P1 | p55 `page-055-asset-1.jpg`, `98252d...2cf2`; all table blocks text length 0 | Add `Throw Result / Range / Result`: `Fumble / None / See Below`; `Failure / 11+ Yards / No Delay`; `Normal Success / 10 Yards / Delayed 1 Round`; `Hard Success / 6 Yards / Delayed 2 Rounds`; `Extreme Success / 3 Yards / Delayed 3 Rounds`; `Critical Success / Direct Hit / Delayed 4 Rounds`. | Exact source-visible transcription. Existing raw 933 already safely preserves the weapon statline `Skill: Throw, Damage:* 4D10/3 yards, Range: STR/5 yards, Uses per Round: ½, Malfunction: 99`; retain it. |
| P1 | p62 two table crops `5d704e...47d1`, `309b53...dd4`; decision has only tail fragments | Add one complete Taint Levels ledger with headers `Level / Modifiers / Effect`, levels 1–10 in order. Modifier sequence must be `2 Bonus Dice, 2 Bonus Dice, 1 Bonus Die, 1 Bonus Die, None, None, 1 Penalty Die, 1 Penalty Die, 2 Penalty Dice, N/A`; copy every effect cell exactly from source. | Exact source-visible transcription from both selected original-hybrid crops/overlay. Pipeline raw 1074–1081 contains only the tail and corrupt name glyph variants, so it cannot replace the full table. |
| P1 | p65 raster `5623aa...d7d4`; accepted prose omits five characteristics | Add source fields `STR 150`, `CON 150`, `SIZ 200*`, `POW 250`, `DEX 100` before existing `HP 35`, `Damage Bonus 3D6`, `Build 4*`, `Magic Points 50`, `Move 7`, `* Starting Stats`. | Prefer adding frozen pipeline raw 1151–1155 (correct values) to the existing selected sequence; keep the cleaner accepted hybrid prose/asset. Do not wholesale switch to pipeline because it introduces wrong name glyphs. |
| P1 | p66 raster `687788...81b2`; all table blocks text length 0 | Add Reliquae characteristics `STR 50`, `CON 25`, `SIZ 55`, `DEX 55`, `INT 50`, `APP 10`, `POW —`, then existing `HP 8`, `Damage Bonus 0`, `Build 0`, `Move 5`. | Exact source-visible transcription from selected table crop/overlay; keep narrative and image order. |
| P1 | p67 rasters `0c41d5...d2dbf`, `ffcd5a...d733a`; all table blocks text length 0 | Add both D8 tables. Serious: `1 Bubonic Plague; 2 Yellow Fever; 3 Syphilis; 4 Anthrax; 5 Influenza (New Variant); 6 Tuberculosis; 7 Hepatitis; 8 Measles`. Deadly: `1 Ebola; 2 Haemorrhagic Fever; 3 Smallpox; 4 Dengue; 5 Rabies; 6 Leprosy; 7 Polio; 8 Something New (This is likely to become the next pandemic if the Investigator makes it off the island alive.)`. | Exact source-visible transcription from the two selected crops/overlay; no alternate frozen text block contains the rows. |

### 1.3 Explicit non-corrections

Preserve source-visible authorial wording even when awkward or inconsistent. Confirmed examples include p21 `If the investigators asks`, p25 `Malanete`, p19 sign text `ALL'ORAAY`, p55 `takes out his pistol and end his own life`, p57 `is be pulled`, p62 `Hastaÿk's corruption`, and p65 `This avatar of Hasalÿk`. The last p65 occurrence is not the p65 heading defect: `Hasalÿk` is visibly present in the source ability paragraph and must remain. No global Hastalÿk normalization is allowed.

## 2. Publication-only hierarchy, anchors, and TOC

After accepted reconstruction correction, publication may change Markdown structure without changing visible wording. Use the exact lowercase ASCII, scenario-prefixed anchor convention in the Step 7 architecture packet; generated Markdown slugs are not authority.

### 2.1 Required hierarchy and target map for pages 1–68

- H1: `Viral` → `viral` (exactly one H1).
- H2 front matter: `Credits` → `viral-credits`; opening message → `viral-opening-message`; `Warning` → `viral-warning`; `Contents` → `viral-contents`.
- H2 `Introduction` → `viral-introduction`; H3 `Summary` / `Overview` → `viral-introduction-summary` / `viral-introduction-overview`.
- H2 `The Spektral Krew` → `viral-spektral-krew`; H3 character anchors: `viral-spektral-krew-marco-proudfoot-maglioni`, `...-corrina-trench`, `...-enoch-jeremiah-eakins`, `...-peter-wharton`, `...-ku-hyeon`, `...-maya-adeduwon`, `...-emily-em-lavigne`. Character-local `Appearance`, `Gear Carried`, and `Secrets` become H4/callout labels, never H1/H2.
- H2 siblings: `Creating New Investigators` → `viral-creating-new-investigators`; `Spektral Krew Gear` → `viral-spektral-krew-gear`; `Timeline` → `viral-timeline`; `History` → `viral-history`.
- H2 `One Night in Perla` → `viral-one-night-in-perla`; H3 targets `...-welcome`, `...-perla`, `...-exploring`, `...-burning-of-the-disease`, `...-the-next-day`, `...-npcs`; Rumors and Signs and Portents are H4 `...-rumors` / `...-signs-and-portents` under Exploring.
- H2 `Isola di Malamente` → `viral-isola-di-malamente`; H3 `Keeper's Secrets`, `Prologue`, `Isola di Malamente: Locations`, `Epilogue` use `viral-isola-keepers-secrets`, `viral-isola-prologue`, `viral-isola-locations`, `viral-epilogue`. Running the Game, Number of Sessions, Plots and Schemes are H4 under Keeper's Secrets. The body wording `Running the Investigation` may remain while the source TOC label `Running the Game` targets the declared alias `viral-isola-running-the-game`; do not rewrite either source occurrence to force equality.
- Location anchors: `viral-isola-location-01-lighthouse-radio-station`, `...-02-beggars-cove`, `...-03-weeping-bridge`, `...-04-lemon-grove`, `...-05-saint-roches-hospital`, `...-06-mass-graves`, `...-07-cremation-pit`, `...-08-dock`, `...-09-overlook-point`, `...-10-chapel-crypt`, `...-11-catacomb-entrance`, `...-12-catacombs`, `...-13-temple-of-morbus`; hospital index → `viral-isola-hospital-locations`; Hastalÿk Awakens → `viral-isola-hastalyk-awakens`.
- Add room-qualified anchors for `1A..1P` and `2A..2J`, e.g. `viral-isola-hospital-room-1i-west-corridor`, `...-1j-isolation-ward`, `...-1k-recovery-ward`, `...-1l-infectious-ward`, `...-1m-terminal-ward`, `...-1o-acute-ward`, `...-1p-recent-ward`. Use the same exact pattern for every room; do not make every room a global TOC entry.
- Epilogue children: `viral-epilogue-rewards`, `viral-epilogue-cinematic-ending`, `viral-epilogue-expanded-ending`, `viral-epilogue-expanded-ending-new-epilogue`.
- H2 `Appendix` → `viral-appendix`; H3 groups and H4 contents exactly: Encounters (`...-encounters`, Outdoor/Hospital/Catacomb); New Rules (`...-new-rules`, The Sight/The Taint/Insanity/Paranormal); New Mythos Horrors (`...-new-mythos-horrors`, Hastalÿk/Plague Monk/Reliquae); New Mythos Tome / Iuramentum; New Spells / Control Reliquae. Use the exact architecture IDs `viral-appendix-encounters-*`, `viral-appendix-new-rules-*`, `viral-appendix-new-mythos-horrors-*`, `viral-appendix-new-mythos-tome-iuramentum-corruptionis`, and `viral-appendix-new-spells-control-reliquae`.

Repeated `Keeper's Notes`, `Description`, `Background`, `ATTACKS`, and `SPECIAL ABILITIES` are local callout/statblock headings. Qualify an ID with the owner anchor only when it is an actual link target. Current top-level mistakes such as p10 `# GEAR CARRIED`, p11 `# Maya's Secrets`, p12 `# APPEARANCE`, and continuation-page `# Keeper's Notes` on p24/p38/p39/p43/p44 must be demoted into their owning unit, not treated as document sections.

Page 5 becomes a generated linked TOC from this declared tree. Preserve genuine source labels/order, remove printed page tokens, and target actual sections. In particular, source TOC `Running the Game` links to the body section alias above, and source TOC `New Epilogue` links to `viral-epilogue-expanded-ending-new-epilogue` despite the printed page inconsistency. `<!-- source-page-NNN -->` comments are reconstruction scaffolding: omit them from reader Markdown and carry their block/page traceability only in `MASTER_EN.provenance.json` and `SOURCE_DISPOSITION.json`.

## 3. Internal reference ledger

### 3.1 Printed/internal body references

Replace the printed construct with a link while retaining the meaningful visible phrase. Do not expose internal source page numbers.

| Source page / line | Source phrase | Target |
|---|---|---|
| 9:9 | `The Sight (see Appendix)` | `viral-appendix-new-rules-the-sight` |
| 11:25, 30:27, 49:29 | Taint `p.62` references | `viral-appendix-new-rules-the-taint` |
| 12:27, 36:23 | The Sight `p.60` references | `viral-appendix-new-rules-the-sight` |
| 39:40 | `History p.16` | `viral-history` |
| 39:50 | `Hospital Encounters ... p.59` | `viral-appendix-encounters-hospital` |
| 43:13 | `Iuramentum Corruptionis on p.67` | `viral-appendix-new-mythos-tome-iuramentum-corruptionis` |
| 45:53, 49:3, 48:39 | Reliquae / `Infected Flesh` / `Plague Zombie` | `viral-appendix-new-mythos-horrors-reliquae` (or a subordinate Infection anchor) |
| 52:13, 54:7 | Expanded Ending `p.56` | `viral-epilogue-expanded-ending` |
| 54:25 | Weeping Bridge description `page 35` | `viral-isola-location-03-weeping-bridge` |
| 55:29 | The Devourer `p.65` | `viral-appendix-new-mythos-horrors-hastalyk` |
| 42:35 | `See West Corridor` | `viral-isola-hospital-room-1i-west-corridor` |
| 45:19–33 | `See 1J/1K/1L/1M/1O/1P` | exact corresponding room anchors; p45 must first receive the v4 `1O` repair |
| 62:13 | `see Taint Levels below` | a local table anchor owned by `viral-appendix-new-rules-the-taint` |
| 64:39 | `see Cold Spot` | Outdoor Encounters table/row-2 anchor |
| 67:7 | `see Infection` | local Infected Flesh/infection-table anchor under Reliquae |

P57 line 7 `Knock-Out Blows on p.125 in the Keeper Rulebook` is external bibliographic wording. Preserve it unlinked unless a separately approved external URI is declared.

### 3.2 Body-to-handout links

Canonical appendix anchors must use the exact physical identities `1`, `2a`, `2b`, `3a`, `3b`, `4..39`: `viral-handout-01`, `viral-handout-02a`, `viral-handout-02b`, `viral-handout-03a`, `viral-handout-03b`, then zero-padded `viral-handout-04` … `viral-handout-39`. Link these body occurrences without changing their visible wording:

- p8:21 → Handout 12;
- p32:7 → displayed range `Handouts #1-7` (link the endpoints and ensure the canonical index exposes 2a/2b/3a/3b); p32:17 → 11;
- p33:23 → 14; p34:35 → 28; p35:29 → 32; p37:21 → 30 and 31;
- p46:9 → 33; p47:27 → 34; p48:15 → 35; p48:33 → 36; p49:5 → 37; p50:7 → 38; p52:5 → 39.

Handout target pages (outside this audit's body content but needed for link closure) are: p69=1; p70=2a; p71=2b; p72=3a; p73=3b; p74=4/5; p75=6/7; p76=8; p77=9; p78=10/11; p79=12; p80=13; p81=14; p82 contextual `Hyeon's iPads` only; p83..92=15..24; p93=25/26/27; p94..99=28..33; p100=34/35; p101=36/37; p102=38; p103=39.

## 4. Semantic tables, cards, and statblocks after v4 acceptance

Publication owns presentation only after §1.2 facts exist in the accepted reconstruction successor.

| Pages | Required publication representation |
|---|---|
| 20–21 | One GFM Rumors table, rolls 1–10; p20 repair must precede it. |
| 21–22 | One GFM Signs and Portents table, rolls 1–10. |
| 34 | GFM STR/result table from the accepted v4 ledger; make crop `7c83b1...a712` evidence-only. |
| 36 | Keep the already complete Lemon Grove Results 1–10 as one unbroken GFM table plus its general SAN note. |
| 55 | Semantic DSS Incendiary Grenades card/statline plus the 6-row Throw Result table; place table before the fumble explanation. Make crop `98252d...2cf2` evidence-only. |
| 58–59 | Join flattened rows 1–12 into one Outdoor Encounters D12 table. |
| 59 | Join flattened rows 1–12 into one Hospital Encounters D12 table. |
| 60 | Join flattened rows 1–6 into one Catacomb Encounters D6 table. |
| 62 | One complete Taint Levels table 1–10; remove duplicate tail paragraphs after their cells are represented. Make both table crops evidence-only; retain the independently meaningful portrait asset. |
| 63 | Join rows 1–10 into an Insanity and Bouts of Madness D10 table. |
| 64 | Join rows 1–10 into a Paranormal Phenomena D10 table. |
| 65 | Semantic Hastalÿk/The Devourer statblock with all characteristics, attacks, armor, SAN and abilities. Make crop `5623aa...d7d4` evidence-only. |
| 66–67 | Semantic Plague Monk card (do not invent physical stats), Reliquae statblock continuing across the page boundary, and both D8 infection tables. Make crops `687788...81b2`, `0c41d5...d2dbf`, `ffcd5a...d733a` evidence-only. |
| 67 | Semantic Iuramentum Corruptionis tome card/definition list preserving every value and spell. |
| 68 | Semantic Control Reliquae spell/rules card preserving all source wording and values. |

Tables must contain no blank lines between pipe rows. Raster crops are not reader substitutes once semantic facts are closed, but remain content-addressed evidence in provenance/asset sidecars.

## 5. Assets, placement, and reader noise

| Severity | Page / selector | Required disposition |
|---|---|---|
| P1 | p1 cover | Current two `reference_only` crops are not a cover. Generate a deterministic full-page reader asset from the immutable **clean source PDF page 1**, never from `SELECTED_OVERLAY.pdf`; place at opening, then one semantic H1 `Viral`. Camera-interface OCR fragments `UNREDACTED`, `HD`, `22:13:35`, dot, `REC` must not appear again as semantic headings/text because the visual retains them. |
| P2 | p6/p7 masthead/decorative assets | Retain source visuals with owners; do not discard source art. Own the p6 Summary graphic under Summary. Group p7 YouTube/Facebook/Instagram/Twitter/Patreon assets as the Spektral Krew masthead/social strip and own the Marco portrait under Marco. They are source visuals, not technical table crops. |
| P2 | p48 witch board `1627aa...c4f` | Suppress visible OCR debris `C120123456789 ABCDEFIG` because it duplicates/misreads lettering already retained in the image. Move the asset from the end of p48 to immediately after p47:33 `The Witch Board` paragraph. Alt: `Witch board with planchette, alphabet, numbers, and symbols.` Record relocation; do not duplicate. |
| P2 | p53 full-page art `2ebda3...8ec` | Retain full-width/full-page in source sequence between Rewards and Cinematic Ending; art-only page must not vanish. |
| P2 | p34/p55/p62/p65/p66/p67 table crops | After v4 semantic fact closure, classify the seven cited crops as `evidence_only`; omit them from reader Markdown to prevent duplicate tables. |
| P2 | p52/p56 and other generic alts | Replace `Source illustration on page N`, `Source table on page N`, hashes/coordinates, and `no visible text or symbols` boilerplate with source-grounded subject/function alt text. Table crops that become evidence-only need no reader alt. |

AI/extraction-generated standalone visual descriptions that immediately duplicate an adjacent image alt are technical reader noise, not authorial source content. Remove the standalone duplicates while retaining the image once at its source owner: p46 line 3; p49 line 31; p51 line 23; p54 line 3; p55 line 45; p57 line 13; p61 line 41; p64 line 45; p65 line 3; p66 lines 3 and 15; p67 lines 21 and 23. Preserve the corresponding reader assets and write concise descriptive alts.

No meaningful source block is authorized for suppression. Authorial `Keeper's Notes`, read-aloud descriptions, gear/secrets, rules prose, and art remain, but are structured/relocated/linked as above. Reconstruction comments and generated duplicate descriptions move to sidecar provenance or disappear from reader rendering; their removal is not a source-content suppression.

## 6. Technical-reader-noise closure

`MASTER_EN.md` must contain zero:

- `<!-- source-page-* -->` comments or OCR/merge/overlay terminology;
- device paths, hashes, coordinates, confidence/evidence IDs;
- generic `Source illustration/table on page N` alt text;
- visible page numbers copied from the printed TOC or internal source refs;
- duplicate AI visual-description paragraphs;
- raster table images standing in for a complete semantic table.

Traceability belongs in `MASTER_EN.provenance.json`, `SOURCE_DISPOSITION.json`, and the candidate asset manifest. Each pages-1–68 source unit must map to a reader unit and operation (`retained`, `structured`, `relocated`, `linked`, or `visualized`); unauthorized source-content suppression count remains zero.

## 7. Required next action and blockers

1. Produce a minimal reconstruction successor from v3 covering all lexical repairs and semantic fact-ledger additions in §1; preserve accepted selectors/assets/order except for the explicit selector additions above; run bounded same-page/same-class verification and obtain independent acceptance with new bytes/hashes.
2. Only then build MASTER_EN using §§2–6 and the current resealed normative architecture packet, with explicit anchor/xref/handout/structure/asset ledgers.
3. Run lexical-conservation, semantic navigation, table/statblock, asset ownership, no-reader-noise, deterministic-build and full visual QA. The candidate remains `candidate_for_user_reading` until exact explicit user acceptance.

No user editorial choice is needed for the source-faithful reconstruction successor. Any desire to correct authorial grammar/name typos such as p62 `Hastaÿk` or p65 `Hasalÿk` is a separate explicit editorial decision not authorized by the current contract.

## Packet identity

Capture this file's detached byte count and SHA-256 after the final write; a file cannot contain its own final whole-file hash without changing that hash.
