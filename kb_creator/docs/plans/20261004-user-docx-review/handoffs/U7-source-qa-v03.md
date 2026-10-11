# Immutable handoff — U7 source visual QA v03

- Goal: `20261004-user-docx-review`; bounded assignment U7-source-qa-v03.
- Timestamp: `2026-10-05T00:23:21+03:00` (Europe/Moscow).
- Contributor: `/root/review_intake`; bounded QA policy `gpt-6-luna / medium`.
- Orchestrator policy owner: `/root`, `gpt-6-sol / medium`; orchestration remains with main.
- Actual runtime model/effort: unavailable, platform unverified; scoped override: none.
- Elapsed time: unavailable (resumed follow-up; exact start not exposed). Token use: unavailable.
- Scope: render/read-only source verification for all 146 numeric characteristic operations in 22 Leningrad/Kremlin entities; targeted check of Leningrad two doors and vampire STR/POW/MP mechanics and Kremlin accreditation/three NPC source records. No source/DOCX/HTML/PDF-generation/code/glossary/canonical-plan edits; no OCR, conversion or release decision.

## Result

Produced the field-level source check table and a concise finding report. The current Word hashes match those in the operation ledger: Leningrad `3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`; Kremlin `6C110ED5E62F29E3FACF97AE3B2D8E515B0066CC1B9F48CCC4D45F09FB3B81A0`. Immutable source PDFs also match the established identities: Leningrad 2,800,661 bytes / `E8C21B6D0BFBED034E6577C7BE01EE305EBFE480C93F87225B07C12AAFD3F10A`; Kremlin 978,872 bytes / `F42B054BB94378A7206CF6688CF6B6CF079606C6F24EE74D2EE5EC8A09C62CA0`.

- All 122 Leningrad and 24 Kremlin numeric values visually match the source pages and operation-ledger Word before-values: 146 `pass`, zero mismatch, zero uncertain, across 22 entities.
- Visually rendered 19 Leningrad physical pages (field pages plus edition/door/effect checks) and seven Kremlin pages for the locator and NPC source context. Page PNG hashes and per-field OOXML selector/path, old value, proposed after-value and status are recorded in JSON.
- Corrected source locator: Kremlin p6 is a full-page illustration. Accreditation instruction is p8, which explicitly says roll POW and repeat until rolling POW or better; no multiplier/die appears. Therefore U7v02’s p6 source citation is wrong and no POW×3/hard conversion is supported by that passage.
- Kremlin physical p16 confirms all three NPC source stat lines and the 24 numeric crosswalk values. Potapov is explicitly described on physical p7 as a Russian émigré professor. Ivan/Nikolai have `Speak Russian 100%`, but checked source text does not explicitly classify it as Own Language or establish their nativity; do not infer that 7e parent field for them.
- Leningrad physical p18/printed17 confirms door Strength10 + Resistance Table; physical p20/printed19 confirms door Strength16 and Katerina’s 1D6 STR loss per following round, MP-v-MP check draining 1D3 MP, and POW-v-POW Resistance Table check. Conversion candidates and limits are reported; none applied.

## Files checked / produced

Checked U7 task packet, U7 operation ledger and relevant architecture conversion spec; immutable original Leningrad/Kremlin PDFs; current reviewed Word DOCX inputs and their ledger-bound hashes. The six removed/old HTML/PDF outputs were not used. Used bundled Codex Python and PDFium, with `-X utf8`, to render only original-PDF physical pages required for source visual checks.

New assigned artifacts only:

- `audit/conversion/source-qa/U7-source-visual-qa-v03.json`
- `audit/conversion/source-qa/U7-source-visual-qa-v03.md`
- Rendered source pages under `audit/conversion/source-qa/` (internal QA evidence, not published output).
- This immutable handoff.

JSON validation confirmed schema `nri.u7_source_visual_qa.v1`, 146 unique numeric operations, 22 entities, 26 relevant rendered/checked source pages, all rendered PNGs present, 2/2 Word hashes matching the operation ledger, 146 pass, zero mismatch/uncertain. No book/source file was edited; no HTML or PDF output was generated.

## Blockers and next action

Correct the inaccurate Kremlin accreditation source locator in integration notes/decision context without rewriting this historical v02 receipt. Preserve the source’s plain POW roll-under instruction; any mechanic conversion needs independently supplied rule authority rather than an inferred ×3. Main retains the language-parent choice for Ivan/Nikolai and previously identified skill-label decisions. The field-value source gate itself is complete; engineering can proceed only with exact accepted operations and its existing DOCX-only safety constraints. No release recommendation is made.
