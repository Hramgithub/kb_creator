# Immutable handoff — U7 QA v01

- Goal: `20261004-user-docx-review`; step: `U7`.
- Timestamp: `2026-10-04T23:58:40+03:00` (Europe/Moscow).
- Contributor: `/root/review_intake`, bounded QA policy `gpt-6-luna / medium`.
- Orchestrator policy owner: main `/root`, `gpt-6-sol / medium`; ownership not transferred.
- Actual platform model/effort: unavailable; assignment state: `platform-unverified`; scoped override: none.
- Elapsed time: unavailable (resumed after context recovery; exact start not exposed).
- Token use: unavailable.
- Scope: read-only edition/numeric-stat audit of six current reviewed DOCX outputs and their available HTML/source PDFs; all 26 Fear stories. User scope excludes other NRI outputs. No edits to books, source inputs, canonical state, source CSV, implementation, or release artifacts.

## Result

Produced a finite extraction ledger and interpretation report. All six current reader artifacts are covered. The Fear HTML exposes exactly 26 story TOC anchors; each has a page span and exact normalized stat-like excerpts in the JSON (61 excerpts total). All HTML `statblock-card` text is captured for Cursed Idol (16), Kremlin (3), Leningrad (37), and Dissociation (1); the seven Number 7 DOCX stat paragraphs are captured with paragraph numbers. Five Leningrad investigator sheets are named in the card text: Реджинальд Мастерс, Леон Стерндейл, Майкрофт Бут, Коллин Палмер, Альбион Фицджеральд. Entity classification and all exact values remain inspectable by record in the JSON; no values were converted.

Assessment:

- Fear’s Sharp Little Needles: source is explicitly the 7th-edition collection; every one of 26 stories was included. Percentile stats and attack success bands are 7e and conserved, including extreme creature characteristics. “61 excerpts” is a deterministic locator count, not a claim of 61 unique statblocks.
- Dissociation: the 6-page source is the same 2018 7e anthology story; current single block is percentile/7e form and conserved.
- Cursed Idol: 16 current cards use percentile characteristics, 7e-derived fields, and regular/hard/extreme bands; conserve the current numbers. Source PDF sampled front matter does not explicitly state its original rule edition, so report claims 7e output form only.
- Leningrad: immutable *Age of Cthulhu 3: Shadows of Leningrad* source explicitly identifies fifth edition. Fifteen scenario entries (NPCs, creatures, one object) and five investigator sheets are represented in 37 cards. Source records use pre-7e characteristics/derivations, with an unusual Ithaqua scale; do not blanket-map through the local 6e note.
- Kremlin: three NPC cards have raw 3–18-style values plus legacy `ХАР`. Original 2002 PDF is available but does not identify the rule edition in sampled text; edition binding is a genuine conversion blocker.
- Number 7 Dream: seven exact stat paragraphs are inventoried. The original source edition/text is absent; the reviewed artifact contains percentile values but inconsistent-looking attack-band text. Preserve; do not infer source edition or convert from unusual numbers alone.

## Files checked

- Current task packet, plan/context, NRI goal governance, current manifest, previous U2 inventory, and U7 architect receipt.
- Six `kb_creator/deliverables/latest/<id>/document.docx` files; all six available HTML companions and PDFs where present; exact excerpts are bound to those current reviewed paths in the inventory JSON.
- Immutable sources: Fear and Leningrad PDFs were supplied by the user. The Cursed Idol, Kremlin, and standalone Dissociation PDFs were found locally (not newly supplied for this goal) and their existence/size/SHA-256 were freshly checked: Cursed Idol `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\temp\идол манко\The_Cursed_Idol_of_Manco_Capác_A_Classic_Call_of_Cthulhu_Scenario.pdf` (50,385,015 bytes; `36C3F74EB3B488ED68ADB5DE0AF226BCD814D310BDCD388FCC03F9FDEA7CB2E8`); Kremlin `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\temp\тайны кремля 1931\2_Secrets of the Kremlin, 1931.pdf` (978,872 bytes; `F42B054BB94378A7206CF6688CF6B6CF079606C6F24EE74D2EE5EC8A09C62CA0`); Dissociation `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\temp\маленькие иголочки страха\Dissociation.PDF` (2,159,317 bytes; `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`). Number 7 original source is not present. Edition/source findings are summarized in the report.
- Manifest comparison: current DOCX hashes for Cursed Idol, Kremlin, Number 7, and Dissociation match manifest values. Fear and Leningrad DOCX hashes differ from transfer-manifest copies due user-comment/reply-bearing reviewed state; current reviewed hashes from U2 are Fear `E8505B99F81A54E02FC1AEA9777C45AE12FDE600A8AB2B2728DDE8F9C0BF8DCD` and Leningrad `3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`. Their corresponding current HTML/PDF hashes match the manifest. No mismatch is treated as a QA failure.
- No source writing, OCR, PDF conversion, desktop LibreOffice, Git fetch, or downstream artifact changes.

## Files created / verification

- `audit/conversion/qa/extract_inventory.py` — deterministic read-only HTML/DOCX extractor.
- `audit/conversion/qa/U7-statblock-inventory.json` — full exact-text ledger, 6 books, 26 Fear story spans, all extracted card/paragraph values and source excerpts.
- `audit/conversion/qa/U7-inventory.md` — finite findings, classifications/edition confidence, story count table, gaps and next action.
- This new receipt; older receipts were not edited.

Executed extractor with bundled Codex Python at `C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8`. JSON then parsed successfully; assertions confirm 6 books and all 26 Fear story anchors. Manifest/checksum comparison confirms 4/6 DOCX hashes expected-equal (two reviewed comment-bearing docs intentionally differ) and all available HTML/PDF hashes expected-equal. Extracted card counts: 16 + 3 + 37 + 1; Number 7: 7 paragraphs; Fear: 61 candidate excerpts across 26 stories. There is no claim of entity-level conversion correctness or acceptance.

## Blockers and next action

Actual source-edition/data gaps: Number 7 original source is absent; Cursed Idol’s PDF front matter sampled does not state its rule edition. Kremlin’s source edition label is absent, but the physical-page 16 crosswalk conclusively establishes all three named old-scale source/current records and their eight field correspondences; exact 5e-vs-6e label is not needed to identify the data as old 3–18. Architect owns the source-grounded rule for `CHR`/`ХАР`; QA does not choose a new target or convert. Other stat-like occurrences outside structured cards/selected `СИЛ` regex may require additional manual checks if the architect’s finite rules depend on them; the extraction script/report state that limitation. Leningrad is established as 5e and Fear as 7e; Dissociation matches the Fear 7e anthology story.

Next: main integrates this ledger with the separate architecture spec, asks only for genuinely missing source/edition decisions, and freezes entity-level operations before engineering. Preserve reviewed values and source; no QA conversion is authorized or performed here. No release recommendation issued.
