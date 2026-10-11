# Immutable handoff — U7 focused mechanics QA v02

- Goal: `20261004-user-docx-review`; bounded assignment: U7v02, two-book prose/label closure.
- Timestamp: `2026-10-05T00:14:52+03:00` (Europe/Moscow).
- Contributor: `/root/review_intake`; bounded QA policy: `gpt-6-luna / medium`.
- Orchestrator policy owner: `/root`, `gpt-6-sol / medium`; ownership remains with main.
- Actual runtime model/effort: unavailable and unverified; assignment state `platform-unverified`; scoped override: none.
- Elapsed time: unavailable (continued task; exact start not exposed). Token use: unavailable.
- Scope: read-only closure of characteristic-dependent prose/checks and skill labels in current reviewed Leningrad and Kremlin DOCX, cross-referenced to existing inventory/spec and immutable source PDFs. No book/source/code/CSV/canonical-state edits, no conversion, no OCR/translation, no HTML/PDF generation, no release decision.

## Result

Produced a finite exact-text ledger and compact findings report. Current artifact identities are freshly verified: Leningrad DOCX `3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`, Kremlin DOCX `6C110ED5E62F29E3FACF97AE3B2D8E515B0066CC1B9F48CCC4D45F09FB3B81A`. Source identities match the prior verified evidence: Leningrad PDF 2,800,661 bytes / `E8C21B6D0BFBED034E6577C7BE01EE305EBFE480C93F87225B07C12AAFD3F10A`; Kremlin PDF 978,872 bytes / `F42B054BB94378A7206CF6688CF6B6CF079606C6F24EE74D2EE5EC8A09C62CA0`.

- Leningrad: scanned 1,156 current DOCX body paragraphs and the 49-page current source/page domain; identified two non-card door-strength checks (10 and 16), three in-card characteristic mechanics already in the v01 card ledger, and all observed legacy skill labels in actual stat/skill contexts. Direct routes retain percentages and modifiers. User-authorized contextual mappings bind Katerina and python condition-values and Rybin bodily entry. No card inventory duplicated.
- Kremlin: scanned 275 current DOCX body paragraphs and 21-page source/page domain. Physical p16 crosswalk matches every source/current field for the three NPCs; all current records are demonstrably old 3–18 scale despite absent exact 5e/6e label. User-authorized ХАР→НАР×5 values are 40/25/60. One prose roll-under-POW check lacks an explicit ×3 in the checked text; it remains unconverted/unresolved rather than inferred. Two grouped label questions remain: own/other language fields and Architecture90 target.
- Photography’s Art/Craft specialization mapping is direct in the supplied primary conversion guide; CSV remains byte/status unchanged and its standalone local row may remain review_required. No extra user question is needed for that direct route.
- No edits were made to reviewed documents or source PDFs. No PDF scan rerun/OCR or visual rendering was performed. Bundled PDF text extraction returned no hits for the searched Russian terms; source correlations therefore rely on already verified exact physical-page evidence, not new OCR or visual QA.

## Files checked and produced

Inputs: `handoffs/U7-mechanics-qa-task-v02.md`; plan/context; `audit/conversion/architecture/conversion-spec.md`; `audit/conversion/accepted-choices-v01.json`; current Leningrad and Kremlin DOCX/HTML; existing `audit/conversion/qa/U7-statblock-inventory.json`; previously verified source PDF references. Used the bundled Codex Python runtime with `-X utf8` for deterministic OOXML/PDF package inspection.

New assigned artifacts:

- `audit/conversion/qa/closure/U7-two-book-closure.json`
- `audit/conversion/qa/closure/U7-two-book-closure.md`
- This immutable handoff.

QA ledger parses as JSON; assertions returned 3 prose/check rows, 18 grouped exact skill-occurrence records, 2 remaining grouped questions, and zero mutations. It provides Word paragraph anchors, source physical/printed page references where confirmed, exact text, routing/status, and explicit limits. The previous `U7-qa-v01.md` receipt is not edited.

## Scope incident disclosure

The existing helper `audit/conversion/qa/extract_inventory.py` was run to inspect coverage and wrote `audit/conversion/qa/U7-statblock-inventory.json` outside this assignment's ownership. The inventory was already an untracked artifact and no pre-run hash/byte snapshot was captured, so prior byte identity cannot be verified. The helper source itself was not changed. Per orchestrator direction, no further write or attempted restore was made; main should validate/freeze the current inventory against live document/source identities. The reviewed DOCX files were read only by this contributor; their content hashes were unchanged across my inspections.

## Blockers and next action

The two finite pending label groups are listed in the ledger/report. Main should bind them to exact output treatment or preserve-as-source decisions before candidate authoring. The Kremlin p146 POW roll-under paragraph needs its source rule context established if the intended update includes it; do not assume ×3. Leningrad door strength candidates are source-grounded under the conversion spec but not applied. Existing v01 card ledger remains the authority for card-level data.

Next action: orchestrator reviews these exact rows, records any user/architecture dispositions in canonical decision state, then engineering may bind approved operations into a versioned DOCX-only successor. No acceptance or release claim follows from this QA receipt.
