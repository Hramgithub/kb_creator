# Viral Step 7 MASTER_EN reader-surface remediation architecture receipt

## Receipt

- Goal / step: `20260830-kb-creator-next-scenario` / Viral Step 7 reader-surface remediation architecture.
- Assignment: `sol_orchestrator_viral_step7_master_en_reader_surface_remediation_architecture_assignment_20260902.md`; verified SHA-256 `ECF1BA589AA5F7413C8C2E890502494BDEA76FB2952D6B6DB439FCFD60EE06F4`.
- Role / model / effort: Sol root-cause and remediation architecture / `gpt-5.6-sol` / high.
- Orchestrator policy owner: root main-chat `gpt-5.6-sol` / medium. This receipt does not transfer orchestration ownership.
- Assignment state: bounded contributor step complete; implementation and release acceptance are not performed.
- Scoped override: architecture/high role and the one receipt write were explicitly assigned; all source, reconstruction, config, code, tests, candidates, plan/context/status/release files, Git, MASTER_RU and downstream outputs remained read-only.
- Result / verdict: **READY_FOR_BOUNDED_REMEDIATION**.
- Timestamp: `2026-09-02T01:22:10.5884756+03:00` (evidence-freeze timestamp; Europe/Moscow).
- Elapsed time: approximately 95 minutes; exact telemetry unavailable.
- Token use: unavailable for this contributor run; no estimate is presented as exact.
- Files changed: this receipt only.
- Blockers: none. No source-semantic ambiguity requires user input.
- Next action: orchestrator assigns the exact config/builder/test surfaces below to Terra/medium, then follows the invalidation and rerun sequence. Explicit user reading acceptance remains pending; MASTER_RU remains closed.

## Evidence and scope closure

The audit used the immutable rejected Candidate A and its pinned inputs:

- candidate root `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`;
- candidate inventory identity `37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421`;
- `INVENTORY.json` `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`;
- `MASTER_EN.md` `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`;
- `publication_config_v1.json` 660,329 bytes / `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`;
- accepted reconstruction inventory `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83` and all 124 accepted page Markdown files;
- independent reject receipt `FBE15693C3CAD6FE5B5E7F01DF79E031C5B48180E563F24B63B585D1D5D42678`;
- full visual-QA resume receipt `1B076F39877310F425829F3E8B4CB0E554415B1D46112F5F4D18E0DCF9D8FD23`;
- builder 70,773 bytes / `82C720B5...`, verifier 20,182 bytes / `C151967D...`, focused builder tests 26,786 bytes / `01BDFFFC...`, focused verifier tests 10,665 bytes / `B7D6822A...`, candidate provenance `5BF8385F...`, asset manifest `734099D6...`, and source disposition `01673B51...`.

Coverage is complete: **168/168 publication units**, **171 locators**, every accepted page-start/page-end transition, **107/107 reader assets/alts**, and every heading in every owner region. The new candidate name `viral-master-en-candidate-20260902-c` was confirmed absent at the evidence freeze.

Confirmed defects are counted as independent contract rows, not examples: **278 total** = 25 semantic-fragment ownership seams + 22 technical reader-noise blocks + 72 defective alt labels (61 provenance-style, 11 repeated generic) + 125 owner-local heading violations + 34 asset-owner bindings (33 reader, 1 evidence-only). The 107-alt audit and 145-source-heading census include conforming rows too; they are not inflated into the defect count. Cover-camera headings are counted as five noise blocks, not again as hierarchy violations.

## Root cause and dependency trace

`resolve_bindings` assigns each configured locator start through the next locator on that page (or EOF) to the locator's owner; a `continuation_pages` declaration adds a page-start claim. The current data therefore assigns a cross-page prefix to the *next* semantic anchor whenever that anchor carries the page-start locator. `clean_span` then strips source images/comments and globally increments every retained source heading by one without regard to the generated owner's depth. `assemble_reader` emits each generated heading, its claimed spans, and all configured reader assets at the owner's end. Current noise validation only recognizes three tooling strings. Thus one start-only claim controls prose, xref owner, structured/note owner, asset placement, and navigation presentation without a closed semantic-fragment or reader-surface contract.

The existing generic locator machinery can express every one of the 25 ownership repairs. Builder support is required only for strict contract validation, authorized exact suppression, local heading normalization, and alt validation; no per-selector mutation matrix or historical 371/119/490 mechanism is justified.

## A. Exact semantic-fragment repairs

Selectors are against immutable accepted-v4 page Markdown after LF normalization. `PS`/`PE` mean page-content start/end excluding the `<!-- source-page-NNN -->` marker and surrounding blank lines. End selectors are exclusive. Hashes cover the raw selected range (before source-image stripping or authorized suppression), joined with LF and no appended newline. Existing hierarchy locators/source-pages express the repaired owner; the new contract ledger validates that result.

| ID | Page; start → end | Current owner → correct owner | Candidate locus | Raw-fragment SHA-256 | Binding consequences |
|---|---|---|---|---|---|
| S01 | 8; PS → `Corrina Trench (Investigator)` | `viral-spektral-krew-corrina-trench` → `viral-spektral-krew-marco-proudfoot-maglioni` | 547-564 | `1C39F0DBE867C06AC8A8A957D62AD183B533BFB22D24C1BBDD838A3A71DC87F3` | text before Corrina; p8 assets stay/rebind to Corrina per asset ledger |
| S02 | 10; `# GEAR CARRIED` → `Ku Hyeon (Investigator)` | `viral-spektral-krew-ku-hyeon` → `viral-spektral-krew-peter-wharton` | 665-670 | `5F8974D2C409AC8A5D5F915DED0AE9E74ECA7D3425C2046D2F5B563C1C8BCA71` | p10 assets independently Ku/Maya |
| S03 | 11; `# Maya's Secrets` → `Emily ‘Em’ Lavigne (NPC)` | `viral-spektral-krew-emily-em-lavigne` → `viral-spektral-krew-maya-adeduwon` | 718-739 | `4A23E1B90A21D2790A08953D5E22ECF8B993DEDD63EE139AFE2FFC8DFDC6D8DB` | workstation→Maya; portrait→Emily |
| S04 | 12; `# APPEARANCE (SUPER FAN OPTION)` → `## Creating New Investigators` | `viral-creating-new-investigators` → `viral-spektral-krew-emily-em-lavigne` | 760-793 | `930C2764B12AB62BB679BCAA69D40B0A7F13F9FE31A8040F4C2F62C24CED4EC8` | p13 continuation remains Creating New Investigators |
| S05 | 19; PS → `## Perla` | `viral-one-night-in-perla-perla` → `viral-one-night-in-perla-welcome` | 1253-1262 | `CB3AA66376817225B5BCC47304F2E039D1473A208E5A5E7D08EA1F4FCA2C9320` | Paolo asset→Welcome |
| S06 | 20; PS → `## Exploring in Perla` | `viral-one-night-in-perla-exploring` → `viral-one-night-in-perla-perla` | 1303-1314 | `37BEBF1E77B2256E61A9647B98C2BBA0E46AC6ACAB592D5B18D8FCE5A177C7F6` | harbor asset→Perla |
| S07 | 24; `# Keeper's Notes` → `## The Next Day` | `viral-one-night-in-perla-the-next-day` → `viral-one-night-in-perla-burning-of-the-disease` | 1463-1488 | `55FB26CB1620F0B3FF4BE3B37D80CD97E64E2AF48FEF3F873196393C5DA1D187` | sunset asset→Next Day, not moved prefix |
| S08 | 30; PS → `Number of Sessions` | `viral-isola-number-of-sessions` → `viral-isola-running-the-game` | 1758-1767 | `3A8B19E444A2CA463F54CF8BE6D866E0CE07BC463240604F21A26F1C726D5115` | none |
| S09 | 34; PS → `## 2. Beggar's Cove (Baia dei Mendicanti)` | `viral-isola-location-02-beggars-cove` → `viral-isola-location-01-lighthouse-and-radio-station` | 1995-2004 | `249CBE4DBFE20BAD671BCF97140CBAFF1BB101DA53FEACB6AAC17F723C1BB976` | bridge asset→Weeping Bridge |
| S10 | 35; PS → `## 4. Lemon Grove` | `viral-isola-location-04-the-lemon-grove` → `viral-isola-location-03-the-weeping-bridge` | 2046-2087 | `3B1CCDED20C88DC0E81310639FAE3064A6F1B25A1E18506FD9870ED44F8F8A76` | cave/grove asset→Lemon Grove |
| S11 | 37; PS → `## 5. Saint Roche's Hospital (Ospedale di San Rocco)` | `viral-isola-location-05-saint-roches-hospital` → `viral-isola-location-04-the-lemon-grove` | 2173-2186 | `E7A72805A8F5A255E077461FF61E2D6D05522A11A93C902C376179C80709573D` | none |
| S12 | 38; PS → PE | `viral-isola-hospital-locations` → `viral-isola-location-05-saint-roches-hospital` | 2242-2359 | `61E18DCB45A560D0D9C9F9A2BE9A5C5028793B6F830FCB977690ED28A6239125` | whole accepted page; none |
| S13 | 39; `# Audio Recording (English Translation)` → `## Hospital Locations` | `viral-isola-hospital-locations` → `viral-isola-location-05-saint-roches-hospital` | 2362-2445 | `FF633AECB9FAE8E7198F68A586C95543391FA0A23FF6FE2F6D8AE975DEF70E30` | rebind xref `p039-history`; `p039-hospital-encounters` stays Hospital Locations |
| S14 | 40; PS → line-prefix `1A. Administrator's Office –` | `viral-isola-hospital-room-1a-administrators-office` → `viral-isola-hospital-locations` | 2476-2493 | `7235218D915A93E90FC5D0B217E56F79FB55F66938F6C454C03461A27AB8D736` | morgue asset→Hospital Locations |
| S15 | 41; PS → line-prefix `1D. Boiler Room –` | `viral-isola-hospital-room-1d-boiler-room` → `viral-isola-hospital-room-1c-laundry-ward` | 2539-2560 | `B33DB1625AF8A7A556B5A8CFED775EB4418D2F11DC3BD9F958D1B52F5CE4F4D3` | none |
| S16 | 42; line-prefix `1Q. Office Suite –` → PE | `viral-isola-hospital-room-1p-recent-ward` → `viral-isola-hospital-locations` | 2734-2754 | `B205ED41A98750BD830CB7FA7002E80D16C0EB1910F461FE551C5E97E69DBD43` | includes 1Q-1R/prayer chapel; no dedicated child anchors exist |
| S17 | 45; PS → line-prefix `2A. Head Nurse's Office –` | `viral-isola-hospital-room-2a-head-nurses-office` → `viral-isola-hospital-locations` | 2865-2867 | `BA1DF3BA2421E14D0C66DAB0A87FEDB6BCEF4ADB083A1863AF3873A0F2D5B65B` | none |
| S18 | 45; `Hospital, Third Floor` → line-prefix `6. Mass Graves` | `viral-isola-hospital-room-2j-recent-ward` → `viral-isola-hospital-locations` | 2933-2939 | `496C01867BF38A700FEB3F0B6A0FCF3A895C43A8BBB25BE498C61D6DED60077B` | none |
| S19 | 47; PS → `10. Chapel & Crypt` | `viral-isola-location-10-chapel-and-crypt` → `viral-isola-location-09-overlook-point` | 3020-3023 | `6F49C0EC422C66957885659E0156ED9E54FAF5AF82CDD7CE1D6A656B054E1EA1` | none |
| S20 | 48; `It shouldn't take them long to discover that the shaking opened a passage...` (full exact line) → `11. Catacomb Entrance` | `viral-isola-location-11-catacomb-entrance` → `viral-isola-location-10-chapel-and-crypt` | 3059-3063 | `5813B79BF201D44AA68F836D2C85732428885E05A658C74CEABB9A96D3446451` | preceding OCR line is N07 suppression; witch-board asset→Chapel/Crypt |
| S21 | 49; PS → `13. Temple of Morbus` | `viral-isola-location-13-temple-of-morbus` → `viral-isola-location-12-catacombs` | 3104-3110 | `3E867E7575ED27B08C3DD92BB2CD2246E170D5054DB6F8F66194BAE7ADCC9305` | rebind `p049-infected-flesh`, `p049-handout-5`; `p049-taint` stays Temple |
| S22 | 52; PS → `Epilogue` | `viral-epilogue` → `viral-isola-hastalyk-awakens` | 3207-3213 | `81F227ED66A69A489EF06376CCAD0F56D40B7572017E7B5628220F493C80710E` | rebind `p052-handout-5`; `p052-expanded-ending` stays Epilogue; p52 fire asset→Rewards |
| S23 | 55; PS → PE | `viral-epilogue-expanded-ending` → `viral-epilogue-cinematic-ending` | 3270-3321 | `6EE04898BE971F45C095771D39D47673ABF1A902C4D16657230F45256C31BF89` | rebind `p055-devourer`, both p55 structures and their three note selectors; evidence asset `98252...` and reader asset `ba787...`→Cinematic; N11 suppressed separately |
| S24 | 64; PS → `Paranormal Phenomena` | `viral-appendix-new-rules-paranormal-phenomena` → `viral-appendix-new-rules-insanity-and-bouts-of-madness` | 3598-3612 | `1E91C62DE4864109ABE19E0C1788E595A78382484F5809BA05BA1A045F749768` | none |
| S25 | 68; `A Few Pointers on Running Viral from Bud` → PE | `viral-appendix-new-spells-control-reliquae` → `viral-appendix` | 3867-3911 | `18E9661DD34600CA05C337D5256DAF6F4104B1E4D126899039C502673942A75D` | none |

For S23, the structures are `viral-structure-dss-incendiary-grenades` and `viral-structure-dss-throw-results`. The latter's attached exact-note selectors begin `While the grenades do damage Hastalÿk...`, `If the throw is fumbled...`, and `Note that these attacks are cumulative...`; change both `owner_anchor` and each region `binding_anchor` to Cinematic Ending. Preserve the evidence-only representation of `viral-accepted-98252...`.

## Asset semantic-owner corrections

These are independent config binding defects exposed by the all-107 audit; do not automatically move every page asset with a prose fragment. The table lists all **34** required owner changes. IDs are unique prefixes of the pinned full `asset_id`.

| Assets | Current → correct owner |
|---|---|
| `647b583c`, `eda9c6f6`, `21704f0d`, `b2ba43b7`, `af48429e` (p7 social/button) | Marco → `viral-spektral-krew` |
| `d65de690`, `2a4ae067` (p8 Corrina portrait/crystal) | Marco → `viral-spektral-krew-corrina-trench` |
| `1ae78ddf` / `a5a54caa` | Corrina → Enoch / Peter respectively |
| `739a8456` / `f76ae66f` | Enoch → Ku Hyeon / Maya respectively |
| `cfb05876` / `44587a04` | Peter → Maya / Emily respectively |
| `9bd48830` | Emily → `viral-creating-new-investigators` |
| `7ad2d1b6` | Creating New Investigators → `viral-spektral-krew-gear` |
| `46fe7137` | Spektral Krew Gear → `viral-history` |
| `290e0d24` | History → `viral-one-night-in-perla` |
| `0964f307` | Perla → `viral-one-night-in-perla-welcome` |
| `327bcc22` | Rumors → `viral-one-night-in-perla-perla` |
| `29f27288` | Burning of the Disease → `viral-one-night-in-perla-the-next-day` |
| `10c6ced9` | Beggar's Cove → `viral-isola-location-03-the-weeping-bridge` |
| `222ccd9a` | Weeping Bridge → `viral-isola-location-04-the-lemon-grove` |
| `694c04bf` | Administrator's Office → `viral-isola-hospital-locations` |
| `f0ecf365` | Mass Graves → `viral-isola-location-07-cremation-pit` |
| `1627aa2f` | Dock → `viral-isola-location-10-chapel-and-crypt` |
| `87d8a9e4` | Overlook Point → `viral-isola-hastalyk-awakens` |
| `15de2b65` | Catacombs → `viral-isola-hastalyk-awakens` |
| `1a47e9a1` | Temple of Morbus → `viral-epilogue-rewards` |
| `98252d0b` (evidence-only), `ba787578` | Expanded Ending → `viral-epilogue-cinematic-ending` |
| `c708f914` | New Epilogue → `viral-epilogue-expanded-ending` |
| `70a9e13d` | Appendix → `viral-epilogue-expanded-ending-new-epilogue` |
| `81953e33` / `6e1d78ee` | Infection → Plague Monk / Reliquae respectively |
| `dbe93023` | Infection → `viral-appendix-new-mythos-tome-iuramentum-corruptionis` |

## B. Authorized technical reader-noise ledger

All **22** blocks are exact; no broad prose regex may silently delete content. Each suppression row must pin the accepted page SHA, exact selector/range SHA, expected occurrence `1`, owner, `authorial_text_affected:false`, and a disposition. The 17 descriptions are `omit_reader_duplicate` with the named replacement reader asset; the five cover-camera headings are `sidecar_only` because the front-cover render preserves the visible design. Candidate lines are evidence loci.

| ID | Page / candidate line | Exact technical block | Correct owner / replacement |
|---|---|---|---|
| N01-N05 | p1 / 6,10,14,18,26 | headings `VIRAL`; `UNREDACTED`; `HD`; `22:13:35`; `REC` | `viral`; front-cover render |
| N06 | p46 / 2967 | `Nighttime outdoor scene with a circular structure and a lit fire at the bottom, surrounded by trees and a starry sky (no text or symbols visible)` | Cremation Pit / `f0ecf365...` |
| N07 | p48 / 3057 | `C120123456789 ABCDEFIG` | Chapel/Crypt / `1627aa2f...` |
| N08 | p49 / 3131 | `Interior of a dimly lit stone cave with arched ceilings and a large creature-like creature, no visible text or symbols` | Hastalÿk Awakens / `87d8a9e4...` |
| N09 | p51 / 3200 | `Silhouette of a figure on a rock under a starry sky with two helicopters flying overhead, no text or symbols present` | Hastalÿk Awakens / `15de2b65...` |
| N10 | p54 / 3238 | `Military helicopter in flight with a green circular overlay, captured at night (no visible text or symbols on the aircraft or background)` | Cinematic Ending / `29e9a40a...` |
| N11 | p55 / 3321 | `Ancient stone carving depicting a figure in traditional attire amidst clouds (no text or symbols)` | Cinematic Ending / `ba787578...` (visual is aerial island destruction, not a carving) |
| N12 | p57 / 3358 | `Silhouette of a submarine at sea with a small speedboat nearby, no visible text or symbols` | New Epilogue / `70a9e13d...` |
| N13 | p61 / 3523 | `Interior view of a building with wooden beams and a person standing in the entrance (no visible text or symbols)` | The Sight / `d03da367...` |
| N14 | p64 / 3639 | `Black electronic device with a blue ball and chain, no visible text or symbols` | Paranormal Phenomena / `2ff7daab...` |
| N15 | p65 / 3648 | `Historical street scene with a large firecracker and two figures in a medieval-style shop (no visible text or symbols)` | Hastalÿk / `8e99d692...` |
| N16 | p66 / 3722 | `Futuristic figure in a hooded coat and gas mask holding a gas stove, standing against a dark background (no text or symbols visible)` | Plague Monk / `81953e33...` |
| N17 | p66 / 3733 | `Human skull profile with green fill and scattered dots, no visible text or symbols` | Reliquae / `6e1d78ee...` |
| N18 | p67 / 3809 | `Close-up photo of a fly with large eyes and antennae, resting on a textured surface (no text or symbols visible)` | Infection / `2fbd3199...` |
| N19 | p67 / 3811 | `Illustration of an old, weathered book with a saucer and a small insect on top (no visible text or symbols)` | Iuramentum / `dbe93023...` |
| N20 | p69 / 4004 | `Satellite or aerial grayscale image showing a textured mountainous terrain with no visible text or symbols` | Handout 1 / `9cddc3fc...` |
| N21 | p81 / 4254 | `Black-and-white image of a tall lighthouse at night, with a bright light at the top and a cross on the structure, no visible text or symbols` | Handout 14 / `5246e2c4...`; preserve source-authored `Isola di Malamente Lighthouse` title |
| N22 | p82 / 4277 | `Person wearing a tactical vest with 'SPEKTRAL' and 'KREW' badges, standing indoors in a dimly lit room (no visible text or symbols on the subject)` | Hyeon's iPads / `2e49f854...` |

Conservation closes as: normalized source tokens = emitted semantic tokens + exact generated-heading replacements + source-image-tag relocations + the 22 authorized suppression ranges. Suppressed raw text and hashes remain in provenance/sidecar evidence. A zero-, duplicate-, or multi-match suppression is fatal.

## Complete 107-alt contract

Ordinal is the one-based reader-asset order under pinned config `CEAA...`; implementation binds each row to the existing full `asset_id` at that ordinal before any reordering. Rows not among the 72 defects may retain their current wording only when it exactly equals this ledger. Punctuation is part of the contract.

```text
001 Spektral Krew logo with skull-and-crossbones symbols.
002 Ruined hall with tall arched windows.
003 Summary heading.
004 YouTube icon.
005 Facebook icon.
006 Instagram icon.
007 Twitter icon.
008 Become a Patron button.
009 Portrait of Marco Proudfoot in a black leather jacket.
010 Portrait of Corrina Trench with purple hair.
011 Translucent crystal specimen.
012 Portrait of Enoch Jeremiah Eakins wearing a Spektral Krew cap.
013 Portrait of Peter Wharton outdoors.
014 Portrait of Ku Hyeon wearing glasses.
015 Portrait of Maya Adeduwon smiling.
016 Computer workstation with video monitors.
017 Portrait of Emily Lavigne smiling outdoors.
018 Silhouette raising a cup in a dimly lit room.
019 Close-up of a laboratory instrument.
020 Ancient layered stone structure beneath a cloudy sky.
021 Aerial view of the Perla coastal harbor and village.
022 Portrait of Paolo.
023 Coastal harbor with small boats.
024 Stone stairway between village buildings.
025 Festival bonfire engulfing a wooden effigy.
026 Sunset over the ocean.
027 Portrait of Santina Maria Salvatore in a patterned headscarf.
028 Portrait of Padre Angelo in clerical attire.
029 Interior of a historic stone church.
030 Coastal town at night reflected on the water.
031 Black fishing boat on calm water.
032 Lighthouse with an adjacent building.
033 Weathered wooden suspension bridge at dusk.
034 Two figures entering the subterranean Lemon Grove.
035 Green-tinted view of an abandoned morgue.
036 Carved stone shrine basin in a crypt.
037 Angelo Russo slumped in a cluttered, decaying room.
038 Candle-ringed cremation pit burning at night.
039 Witch board with planchette, alphabet, numbers, and symbols.
040 Hastalÿk rising in the underground temple.
041 Hastalÿk silhouetted beneath military helicopters at night.
042 Silhouetted survivor watching Isola di Malamente burn after an aerial attack.
043 Two fighter jets flying in formation against a sunset sky.
044 Military helicopter in flight at night.
045 Aerial view of Isola di Malamente engulfed by explosions and fire.
046 Sunset beneath dark storm clouds above the Expanded Ending.
047 Submarine surfacing beside the investigators' small boat at night.
048 Ancient catacomb excavation with scattered human skulls and debris.
049 Vision seen through The Sight inside a ruined timbered building.
050 Taint victim pressing both hands against their face.
051 Distorted face during a bout of madness.
052 Paranormal investigation device with a blue sensor and chain.
053 Hastalÿk, the towering Devourer formed from infected flesh.
054 The Plague Monk in a hooded coat and gas mask.
055 Reliquae infection represented by a green, spotted skull profile.
056 Close-up of a fly associated with Reliquae infection.
057 Weathered Iuramentum Corruptionis tome with fly emblem.
058 Map of Isola di Malamente with marked locations.
059 Marco's email, first screen.
060 Marco's email, second screen.
061 Maya's email, first screen.
062 Maya's email, second screen.
063 Maya's email continuation with island map attachment.
064 Annotated island map prepared for the investigators.
065 Player map of Saint Roche's Hospital.
066 Isola di Malamente lighthouse at night.
067 Hyeon's iPad stream layout showing a Spektral Krew tactical vest.
068 The Weeping Bridge at sunset.
069 Elder Sign marked into the ground.
070 Plague Monk visible through a broken window.
071 Curtains visible through a broken window.
072 Two figures entering the subterranean Lemon Grove.
073 Fire burning in the center of a candle-ringed cremation pit at night.
074 Witch board used in the crypt.
075 Fragment of an illuminated manuscript.
076 Figure moving through the catacombs.
077 Reclining stone knight amid bones.
078 Hastalÿk rising in the underground temple.
079 Hastalÿk destroyed in a vast fire.
080 Map locating Isola di Malamente in the Gulf of Gela.
081 Keeper map of Isola di Malamente with numbered locations and communications ranges.
082 Ground-floor map key and legend.
083 Ground-floor and basement plan of Saint Roche's Hospital.
084 Continuation of the ground-floor and basement plan, including the East Wing, chapel ruins, staff dormitory, infirmary, morgue, catacombs, and ancient altar.
085 Second- and third-floor plan of Saint Roche's Hospital.
086 Keeper maps of the Administrator's House, East Wing, and hospital attic.
087 Keeper map of the crypt, catacombs, Temple of Morbus, and Hastalÿk's rising.
088 Complete front page of Marco Proudfoot's pregenerated investigator sheet.
089 Marco Proudfoot's background silhouette.
090 Complete front page of Corrina Trench's pregenerated investigator sheet.
091 Corrina Trench's background silhouette.
092 Complete front page of Enoch Jeremiah Eakins's pregenerated investigator sheet.
093 Enoch Jeremiah Eakins's background silhouette.
094 Complete front page of Peter Wharton's pregenerated investigator sheet.
095 Peter Wharton's background silhouette.
096 Complete front page of Ku Hyeon's pregenerated investigator sheet.
097 Ku Hyeon's background silhouette.
098 Complete blank investigator template.
099 Blank background-page silhouette.
100 Blank fellow-investigators relationship diagram.
101 Spektral Krew T-shirt.
102 Spektral Krew hat.
103 Spektral Krew patch.
104 Spektral Krew badge and T-shirt.
105 QR code for the historical Spektral Krew merchandise store.
106 Viral front cover showing the Spektral Krew recording frame and scenario title.
107 Viral back cover with Marco Proudfoot quotation, scenario synopsis, and publisher marks.
```

The current 72 defective rows are 61 labels beginning `Scenario illustration owned by ...` plus five repeated `Complete pregenerated investigator sheet form.` and six repeated `Character silhouette accompanying the background sheet.`. Validation must reject, case-insensitively: empty/whitespace; `owned by`; `scenario illustration`; `source illustration`; `source table`; 32/64-hex hashes; filesystem separators or tooling names; and standalone provenance page forms such as `page 52`/`p.52`. It must not reject a semantically necessary proper name or visible-text description merely because the source page also contains it.

## C. Complete heading hierarchy audit

The 168 generated headings are exactly the 168 config levels: L1=1, L2=19, L3=87, L4=32, L5=29. Candidate A additionally contains **145 source headings** in 59 regions: H2=23 and H3=122. Of these, **125** are at or above their generated owner level in **54 regions** and violate the local contract. The remaining **20** are already subordinate across seven regions (two regions contain both classes). This accounts for every heading: 168 generated + 145 source = 313.

Every violating source heading is enumerated below as `anchor [generated level]: candidate-line/source-level/title`:

```text
viral-spektral-krew-corrina-trench [3]: 552/H3 APPEARANCE; 560/H3 GEAR CARRIED; 581/H3 APPEARANCE; 589/H3 GEAR CARRIED
viral-spektral-krew-enoch-jeremiah-eakins [3]: 618/H3 APPEARANCE; 626/H3 GEAR CARRIED
viral-spektral-krew-peter-wharton [3]: 651/H3 APPEARANCE
viral-spektral-krew-ku-hyeon [3]: 666/H2 GEAR CARRIED; 687/H3 APPEARANCE; 695/H3 GEAR CARRIED
viral-spektral-krew-emily-em-lavigne [3]: 719/H2 Maya's Secrets; 735/H3 APPEARANCE
viral-creating-new-investigators [2]: 761/H2 APPEARANCE (SUPER FAN OPTION)
viral-one-night-in-perla-welcome [3]: 1203/H3 Keeper's Notes; 1223/H3 Keeper's Notes
viral-one-night-in-perla-exploring [3]: 1308/H3 Keeper's Notes
viral-one-night-in-perla-burning-of-the-disease [3]: 1441/H3 Keeper's Notes
viral-one-night-in-perla-the-next-day [3]: 1464/H2 Keeper's Notes; 1480/H3 Keeper's Notes; 1501/H3 Keeper's Notes
viral-isola-prologue [3]: 1877/H3 Keeper's Notes; 1917/H3 Keeper's Notes
viral-isola-locations [3]: 1934/H3 General Description: The Main island; 1950/H3 Keeper's Notes
viral-isola-location-01-lighthouse-and-radio-station [4]: 1979/H3 Keeper's Notes
viral-isola-location-02-beggars-cove [4]: 2002/H3 Keeper's Notes; 2011/H3 Keeper's Notes
viral-isola-location-04-the-lemon-grove [4]: 2051/H3 Keeper's Notes; 2083/H3 Possible Vision from The Sight; 2100/H3 Keeper's Notes; 2107/H3 Lemon Grove Results
viral-isola-location-05-saint-roches-hospital [4]: 2182/H3 Possible Vision from The Sight; 2203/H3 Keeper's Notes; 2219/H3 Keeper's Notes
viral-isola-hospital-locations [4]: 2242/H2 Keeper's Notes; 2254/H3 Keeper's Notes; 2266/H3 Keeper's Notes; 2278/H3 Keeper's Notes; 2362/H2 Audio Recording (English Translation); 2417/H3 Possible Vision from The Sight; 2425/H3 Keeper's Notes; 2466/H3 Keeper's Notes
viral-isola-hospital-room-1a-administrators-office [5]: 2499/H3 Keeper's Notes
viral-isola-hospital-room-1b-admission-ward [5]: 2515/H3 Keeper's Notes
viral-isola-hospital-room-1d-boiler-room [5]: 2552/H3 Keeper's Notes; 2578/H3 Keeper's Notes
viral-isola-hospital-room-1e-operating-room [5]: 2596/H3 Keeper's Notes
viral-isola-hospital-room-1f-exam-room [5]: 2610/H3 Keeper's Notes
viral-isola-hospital-room-1g-kitchen [5]: 2628/H3 Keeper's Notes
viral-isola-hospital-room-1h-main-dining-and-recreation-hall [5]: 2646/H3 Keeper's Notes
viral-isola-hospital-room-1i-west-corridor [5]: 2664/H3 Keeper's Notes
viral-isola-hospital-room-1j-isolation-ward [5]: 2686/H3 Keeper's Notes
viral-isola-hospital-room-1p-recent-ward [5]: 2742/H3 Keeper's Notes; 2757/H2 Keeper's Notes; 2785/H3 Keeper's Notes; 2809/H3 Keeper's Notes; 2824/H2 Keeper's Notes; 2828/H3 Administrator's House; 2832/H3 Keeper's Notes
viral-handout-19..25 [3]: each has three H3 source headings `iPad One`, `iPad Two`, `iPad Three` at 4463/4469/4473, 4493/4499/4503, 4523/4528/4532, 4552/4556/4560, 4581/4585/4589, 4610/4615/4619, 4642/4647/4651 (21 violations)
viral-keeper-map-isola-location [3]: 4773/H2 Keeper Maps
viral-keeper-map-isola-overview [3]: 4784/H2 Isola di Malamente
viral-keeper-map-ground-floor-basement [3]: 4803/H2 Ground Floor & Basement; 4805/H3 Key
viral-keeper-map-second-third-floors [3]: 4843/H2 Second & Third Floors
viral-keeper-map-administrators-house-east-wing-attic [3]: 4865/H2 Administrator's House, East Wing, and Hospital Attic
viral-keeper-map-secret-underground [3]: 4874/H2 Secret Underground
viral-pregen-marco-front [3]: 4911/H2 Marco Proudfoot — Investigator Sheet
viral-pregen-marco-background [3]: 4920/H3 Background; 4942/H3 Gear and Possessions; 4951/H3 Cash and Assets; 4957/H3 Quick Reference Rules; 4968/H3 Marco's Responsibilities
viral-pregen-corrina-front [3]: 4979/H2 Corrina Trench — Investigator Sheet
viral-pregen-corrina-background [3]: 4988/H3 Background; 5010/H3 Gear and Possessions; 5018/H3 Cash and Assets; 5024/H3 Quick Reference Rules; 5035/H3 Corrina's Responsibilities
viral-pregen-enoch-front [3]: 5046/H2 Enoch Jeremiah Eakins — Investigator Sheet
viral-pregen-enoch-background [3]: 5055/H3 Background; 5077/H3 Gear and Possessions; 5085/H3 Cash and Assets; 5091/H3 Quick Reference Rules; 5102/H3 Enoch's Responsibilities
viral-pregen-peter-front [3]: 5113/H2 Peter Wharton — Investigator Sheet
viral-pregen-peter-background [3]: 5122/H3 Background; 5144/H3 Gear and Possessions; 5156/H3 Cash and Assets; 5162/H3 Quick Reference Rules; 5173/H3 Peter's Responsibilities
viral-pregen-ku-hyeon-front [3]: 5184/H2 Ku Hyeon — Investigator Sheet
viral-pregen-ku-hyeon-background [3]: 5193/H3 Background; 5215/H3 Gear and Possessions; 5223/H3 Cash and Assets; 5229/H3 Quick Reference Rules; 5240/H3 Hyeon's Responsibilities
viral-pregen-blank-front [3]: 5255/H2 Blank Spektral Krew Investigator Template
viral-pregen-blank-background [3]: 5264/H3 Background; 5286/H3 Gear and Possessions; 5288/H3 Cash and Assets; 5294/H3 Quick Reference Rules; 5305/H3 Fellow Investigators
viral-merchandise [2]: 5316/H2 SPEKTRAL KREW
viral-back-cover [2]: 5341/H2 Viral — Back Cover
```

The 20 already-subordinate source headings are also closed: cover N01-N05 (five H2/H3, but suppressed as noise); Credits has five H3 (`Writing`, `Editing`, `Additional Editing`, `Language Consultant`, `Play Testers`); Creating New Investigators has two H3 (`APPEARANCE (ANOTHER GHOST HUNTER OPTION)`, `Keeper's Notes`); Spektral Krew Gear has four H3 `Keeper's Notes`; History has two H3 `Keeper's Notes`; One Night in Perla has one H3 `Keeper's Notes`; Merchandise has H3 `Now YOU too can be one of the Krew!`.

Closed heading rule:

1. A generated owner heading stays at its configured level.
2. For each contiguous source-heading subtree, preserve text and relative depth but map its shallowest retained heading to `owner_level + 1`.
3. A mapped level at most 6 emits Markdown. Any deeper level emits a deterministic strong label (`**text.**`, avoiding a doubled terminal period) and remains in the same content position.
4. An exact semantic duplicate of the generated owner/group label becomes a strong label unless an explicit exact suppression row proves it is technical duplicate text. Never silently delete authorial labels.
5. After assembly, every source Markdown heading must have level greater than its current generated owner, no H1/H2 may leak from a deeper region, and no heading may exceed H6. The builder records original and emitted forms in provenance.

## D. Minimal reusable remediation surfaces

### Config

Amend only `kb_creator/working/viral/master_en/publication_config_v1.json`:

- repair hierarchy `source_pages`, locators and `continuation_pages` using existing `page_start`, `markdown_heading_exact`, `line_exact`, and `line_prefix` primitives for S01-S25;
- rebind the exact xref/structured/note/asset rows above;
- set all 107 `alt_text` values to the ledger;
- add one strict top-level `reader_surface` object with exactly `schema_version`, `semantic_fragments`, `authorized_suppressions`, `heading_policy`, `alt_policy`.

Strict nested shapes:

- semantic fragment: exactly `fragment_id`, `source_page`, `start`, `end`, `expected_owner`, `raw_sha256`, `order`; selector exactly `kind`, optional `text`, `occurrence`, where kind is `page_start|page_end|line_exact|line_prefix|markdown_heading_exact`, occurrence is positive and page sentinels forbid text;
- suppression: exactly `suppression_id`, `source_page`, `owner_anchor`, `start`, `end`, `raw_sha256`, `expected_occurrence`, `disposition`, `replacement_asset_id`, `authorial_text_affected`; disposition is `sidecar_only|omit_reader_duplicate`, occurrence is 1, authorial flag must be false;
- heading policy: exactly `generated_mode:"declared"`, `source_mode:"owner_local"`, `max_level:6`, `overflow:"strong_label"`, `duplicate_label:"strong_label"`;
- alt policy: exactly `require_nonempty`, `banned_substrings`, `banned_regexes`; use the bans above.

Pin all 25 raw hashes from table A and 22 suppression hashes computed from immutable v4. The semantic ledger is validation, not a second mutation engine: after normal locator resolution, the builder must prove each raw fragment resolves once, wholly, in order, to `expected_owner`. Unknown keys at every new nesting level are fatal. Counts are closed for this config: 168 hierarchy units, 25 semantic fragments, 22 suppressions, 107 reader alts.

### Builder and verifier behavior

Amend only `kb_creator/scripts/build_scenario_master_en.py` and, where independent verification needs the same public contract rather than builder internals, `kb_creator/scripts/verify_scenario_master_en.py`:

- validate the new closed schema before reading output state;
- resolve existing locator claims, then validate non-overlap, exact once-only coverage, expected owner, configured order and raw range hashes for all semantic fragments;
- perform only exact authorized suppressions; retain hashes/text in provenance and conservation accounting;
- replace global `heading + 1` with the owner-local algorithm above;
- validate every emitted reader alt before copying assets;
- emit sidecars with fragment/suppression/heading/alt outcomes so the independent verifier can recompute from accepted pages, config and candidate rather than trust builder success;
- reject missing/duplicate/out-of-order semantic content, unclaimed/overlapping bytes, unmatched suppressions, plain description leakage, provenance/empty alts, generated duplicate headings, owner-local violations, and any unknown nested key.

Do not change accepted reconstruction, source PDF, source disposition semantics, asset bytes, public link targets, or unrelated publication machinery.

### Focused tests

Amend only `kb_creator/tests/test_build_scenario_master_en.py` and `kb_creator/tests/test_verify_scenario_master_en.py` (plus a narrowly named fixture file only if existing inline fixtures become unreadable):

1. compact generic two-page fixture with preceding-anchor continuation, next-anchor start, page-prefix and page-suffix splits; prove exact order/conservation and reject missing, duplicate, overlapping, out-of-order, wrong-owner and wrong-hash fragments;
2. unknown-key tests for every `reader_surface` nesting level and invalid selector field combinations;
3. exact suppression fixture: one match passes; zero, two, broad/partial, wrong owner/hash, `authorial_text_affected:true`, or missing replacement fails;
4. alt fixture rejects empty, provenance phrases, generic source phrases, hash/path/tooling/page provenance and accepts descriptive visible-text alts;
5. heading fixtures for owners L2-L5, preserved relative depth, exact generated-label duplicate, H6 boundary and strong-label overflow; verifier independently rejects H1/H2 leakage and source level `<= owner`;
6. content-aware Candidate-A regressions: p8 Marco/Corrina prefix, p55 Cinematic structured/note ownership, p68 Appendix suffix, p46 plain description, provenance alt, map/pregen/merchandise/back-cover duplicate headings;
7. full-config assertions: 168 units, 25 semantic fragments, 22 suppressions, 107 reader alts, 168 generated headings, zero semantic-owner mismatches, zero unapproved description blocks and zero owner-local heading violations;
8. dependency assertions that S13/S21/S22/S23 xrefs, both p55 structures, three attached notes, and all 34 asset bindings follow their declared semantic owners.

## E. Invalidation and rerun boundary

Any config or builder change makes stale: the former C2b implementation/reviews tied to `CEAA...`/`82C...`; Candidate A/B inventories, verifier runs and frozen-candidate execution evidence; Candidate A reader/provenance/asset-manifest identities; the prior independent release reject as a decision on the successor; and all reader-surface/text/accessibility conclusions. A/B remain immutable rejected evidence and are never overwritten.

Smallest safe sequence:

1. Terra/medium implements only the config, builder/verifier and focused tests named above.
2. Run focused builder/verifier unit tests and a read-only full-config contract audit.
3. Obtain independent GPT-5.5/high implementation review; remediate only findings within this specification.
4. Confirm `viral-master-en-candidate-20260902-c` is still absent; build twice into two absent scratch roots and compare deterministic projections, then build/freeze `...-c` once and run the independent verifier.
5. Run bounded content-aware QA over all 168 regions, 25 fragments, 22 suppressions, 107 alts, 313-heading expectation and all sidecar dependency outcomes.
6. Obtain a new independent GPT-5.5/high **release** review of the frozen successor. Only the orchestrator may integrate that decision; user reading acceptance remains a separate pending gate.

The existing p27/p39/p80 visual inspection may be **carried forward conditionally**, not by the now-stale whole `ASSET_MANIFEST.json` hash. Recompute a canonical binary projection for all 123 configured assets containing only full asset identity, SHA-256, byte count, media type, dimensions and source-page/source-region identity. If that projection, the 107-reader/16-evidence representation set, and front/back rendered asset bytes are byte-identical, the prior visual content evidence remains valid: owner and alt metadata changes do not change pixels. Placement/order, semantic owner labels and accessibility still require the new all-reader QA. If any binary projection row, representation, reader inclusion, cover render or asset count differs, repeat the affected visual inspection; if the difference cannot be bounded exactly, repeat the full visual QA.

## Acceptance criteria

Bounded remediation is ready for freeze only when all of the following are evidenced:

- all 168 units and every accepted source-visible word are conserved exactly once except the 22 authorized technical ranges;
- all 25 raw fragments hash-match and resolve once, in order, to the specified owner;
- all affected xref/structure/note and 34 asset-owner bindings match this receipt;
- no plain technical description or cover-camera heading remains in reader prose;
- all 107 reader images have the exact deterministic descriptive alt ledger and none violates the closed policy;
- generated headings remain at declared levels, all retained source headings are locally subordinate or strong labels, and no duplicate/global H2 navigation remains;
- focused tests, two-build determinism, independent verifier, bounded full-reader QA and a new independent GPT-5.5/high release review pass on the frozen successor;
- Candidate A/B remain unchanged, explicit user reading acceptance remains pending, and MASTER_RU remains closed.

