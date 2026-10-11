role/model/effort: executor/QA, gpt-5.4, low

scope and files inspected:
- Source PDF: `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\1923_The Innsmouth Terror\The Innsmouth terror.pdf`
- Normalized source: `D:\NRI\kb_creator\working\innsmouth_source_to_artifacts\runs\20260730T210831Z\Formatted\The_Innsmouth_Terror_Source_Text_Normalized_EN.md`
- Existing audit table: `D:\NRI\kb_creator\reports\innsmouth_source_to_artifacts\runs\20260730T210831Z\source_pdf_integrity_audit.md`
- Existing audit json: `D:\NRI\kb_creator\reports\innsmouth_source_to_artifacts\runs\20260730T210831Z\source_pdf_integrity_audit.json`
- Plan/context reviewed: `D:\NRI\kb_creator\docs\plans\20260730-innsmouth-source-to-artifacts\plan.md`, `D:\NRI\kb_creator\docs\plans\20260730-innsmouth-source-to-artifacts\context.md`
- Visual spot renders used for confirmation: source PDF pages `031`, `033`, `035`

| page | status | evidence | recommended action |
| --- | --- | --- | --- |
| 019 | ok | PDF coordinate order is standard left column then right column. The top-right line (`If the investigators don’t find the note...`) looks like a continuation, but in visual page flow it belongs after the left-column `Handout 2: note` block. `Normalized_EN.md` keeps left column first, then right-column continuation. | No source fix needed. Keep as acceptable two-column flow. |
| 020 | ok | PDF has main body in the left column and a `Keeper note:` box in the right column starting higher on the page. `Normalized_EN.md` places the main body first and the keeper note last, which matches intended reading order better than raw coordinate order. | No source fix needed. Treat warning as false positive caused by side-note placement. |
| 021 | ok | PDF is a normal two-column investigation page: left-column scene setup, then right-column interaction bullets and follow-up paragraphs. The audit warning is triggered because the right column begins high on the page (`Other than that...`), but the normalized page preserves coherent left-then-right reading. | No source fix needed. |
| 023 | real_issue | This page is a table (`Table 2: encounters in the caves`). In `Normalized_EN.md`, row ranges and descriptions are interleaved into broken prose (`What Luck... 1-5 feels like...`, `31-40 unforgettable image...`). PDF coordinates show the table is readable visually, but the normalized linearization is not. | Add table-aware extraction or a page-type override for this page class; re-audit page 023 after table normalization. |
| 028 | ok | PDF text layer merges the left section (`The Esoteric Order of Dagon`) and the right section (`Entering through the Caves`) onto the same output lines, but `Normalized_EN.md` separates them into coherent sequential sections. This is better than the raw mixed text layer and matches the visual page. | No source fix needed. Keep current normalized order. |
| 030 | ok | Warning is a false positive from the running header (`the epIc` / `fInale`) and dense statblock formatting. The actual page body is a full-width locomotive statblock and reads correctly in `Normalized_EN.md`. | No source fix needed. |
| 031 | needs_human_visual_review | PDF text coordinates show an upper-right block starting with `What if they’re captured?`, but the rendered page view is dominated by artwork and visible body text for `Playing the Hero`; the text-layer evidence and the visible page do not line up cleanly. `Normalized_EN.md` includes the captured-investigators block on page 031, but this should be confirmed against the true visible source layout. | Human visual review of the source PDF page is recommended before changing extraction policy. If confirmed absent/relocated in the visible layout, treat as a real text-layer ordering/placement defect. |
| 032 | ok | PDF is a normal two-column epilogue/rewards page. The warning is triggered because the right-column paragraph `If it is released...` starts near the top, but the normalized page preserves coherent left-column epilogue text before the right-column rewards/release material. | No source fix needed. |
| 033 | ok | This is a statblock spread page. Warning is caused by decorative header text (`characters / anD / monsters`) and simultaneous left/right statblock starts. The normalized page linearizes left column content and remains readable; no cross-column sentence break is evident. | No source fix needed. |
| 035 | ok | Another statblock spread. PDF has left-column NPC/monster entries and right-column Star Spawn/Deep One entries beginning near the top. `Normalized_EN.md` reads as a left-then-right statblock sequence; the warning is a page-type false positive, not a broken sentence flow. | No source fix needed. |

list pages covered:
- 019
- 020
- 021
- 023
- 028
- 030
- 031
- 032
- 033
- 035

blockers:
- None for page classification.
- Page `031` remains visually ambiguous because the text layer and rendered page appearance do not align cleanly; classification is therefore conservative.

tokens/time if available:
- goal tokens used: `139226`
- active work time: `88s`
- timestamp: `2026-08-02`
