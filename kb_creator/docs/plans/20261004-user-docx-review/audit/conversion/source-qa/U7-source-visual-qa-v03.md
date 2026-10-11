# U7 source-visual QA v03

Read-only visual crosscheck of all proposed characteristic-number fields in the current Leningrad and Kremlin Word readers against the immutable original source PDFs. Detailed identities, page-image hashes, every field status and exact Word selector are in [`U7-source-visual-qa-v03.json`](U7-source-visual-qa-v03.json). Source page PNGs in this folder are internal QA evidence only.

## Result

| Source / current reader | Verified scope | Result |
| --- | --- | --- |
| *Shadows of Leningrad* original: 49 physical pages; printed footer is physical page −1 after the front matter. Source PDF SHA-256 `E8C21B6D0BFBED034E6577C7BE01EE305EBFE480C93F87225B07C12AAFD3F10A`. Current DOCX SHA-256 `3E2172AB1CC9C045F9F5F472BF6F664337A06969FEDC786BEB2D8D40459007C8`. | 122 characteristic fields / 19 entities across physical pp7,12,19,20,24,25,28,30,31,33,35,36,37–41; additionally p6 edition evidence and pp18/20 door-strength / p20 vampire checks. | **122 pass; 0 mismatch; 0 uncertain.** Every source value was legible and visually matched the exact operation-ledger Word before-value at its selector. |
| *Secrets of the Kremlin* original: 21 physical pages, source SHA-256 `F42B054BB94378A7206CF6688CF6B6CF079606C6F24EE74D2EE5EC8A09C62CA0`. Current DOCX SHA-256 `6C110ED5E62F29E3FACF97AE3B2D8E515B0066CC1B9F48CCC4D45F09FB3B81A`. | 24 characteristic fields / 3 entities at physical p16. Accreditation locator checked at physical p8; p6 visually checked to resolve the erroneous prior citation. | **24 pass; 0 mismatch; 0 uncertain.** All three source stat/skill records match the current Word fields. |

The current Word hashes match the source-page-bound U7 operation ledger hashes, so each visual source result also binds to the exact current Word value and OOXML selector recorded there. The 146 individual rows carry `pass` status in the JSON; no conversion was performed.

## Corrected Kremlin source locator and language context

- Physical p6 is a full-page illustration, not the accreditation passage. Physical p8 contains `ACCREDITATION`: “then roll their POW”; after failure “continue to roll until he does roll his POW or better,” selecting a new publication for each subsequent roll. No die or multiplier is stated. This is a roll-under-POW instruction, not POW×3. Keep the current mechanic unresolved/preserved absent independent rule binding; do not silently invent a ×3 or hard check. This corrects U7v02's mistaken source physical-page-6 locator for Word ¶146.
- Physical p16 visually confirms three complete cards and every source stat value: Potapov STR10 INT17 EDU18 CON13 DEX10 CHR8 POW16 SIZ10; Ivan STR14 INT15 EDU17 CON17 DEX14 CHR5 POW17 SIZ12; Nikolai STR8 INT13 EDU15 CON11 DEX14 CHR12 POW10 SIZ4. Skill lines read Speak Russian100% for all three; Potapov also has English80/German70 and Architecture90; Ivan English70; Nikolai English60. User-approved ХАР→НАР×5 stays 40/25/60; this does not assert the original `CHR` abbreviation unambiguously meant APP.
- Physical p7 describes Potapov as an émigré Russian professor who left Russia in 1919, supporting Russian identity for him. The source calls the skill “Speak Russian,” not “Own Language.” For Ivan and Nikolai, names plus Speak Russian100% are evidence they speak Russian, but no biography on the checked pages establishes nativity or an own-language skill category. Do not infer that parent label for those two. Main may choose ordinary 7e parent-language localization; “own versus other” remains a separate field-classification decision.

## Leningrad dependent mechanics verified on source pages

- Physical p18 / printed p17: storage-room door is Strength10 and explicitly uses the Resistance Table. Deterministic target candidate: 10×5=50, then opposed STR per the supplied conversion guide.
- Physical p20 / printed p19: locked ward door has Strength16. Candidate: 16×5=80, then opposed STR in the door-breaking context. The sentence does not restate a Resistance Table instruction.
- Physical p20 / printed p19: Katerina’s bite drains 1D6 STR each following round. Preserve distribution exactly as `5 × (1D6)` under the supplied conversion spec; do not substitute a rerolled/approximated effect. The same card’s magic-point-vs-magic-point Resistance Table roll drains 1D3 MP; preserve current MP pools and drain amount (MP itself is not multiplied). Gaze compares POWs on the Resistance Table; modernize only to an opposed POW check if that mechanic is in the approved operation scope.

## Limits and next action

No OCR was started. Bundled PDFium rendered only the original source pages listed in the JSON; all were visually inspected for their relevant stat/mechanics text. No HTML or PDF deliverable was generated, and no source or current reader was edited. The review concerns source-value fidelity; it does not decide unresolved language-parent or Architecture skill labels, nor authorize a final output. Main should correct the accreditation source locator in integration notes, preserve the no-multiplier uncertainty, and retain all source-page/value evidence before a DOCX-only candidate is authored.
