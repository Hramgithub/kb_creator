# A2 QA receipt: source pages 10–18

- Goal: `20260917-dream-structural-fidelity-audit`
- Step: `A2`
- Role: bounded QA; requested effort `low`; assignment state `matched when dispatched`
- Model: `unavailable` (runtime identity cannot be verified from this receipt context)
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`; assignment state `platform-unverified`
- Scoped override: `none`
- Scope: read-only comparison of source render pages 010–018 against their Stage 06 page Markdown; no candidate or canonical state changed.
- Result: all 9/9 pages visually compared; structural defects confirmed on pages 10, 11, 14, 15, 17, and 18. Pages 12, 13, and 16 showed no confirmed defect in the assigned structural categories. OCR/text errors are excluded from this count.
- Files checked: source renders `outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-010.png` through `page-018.png`; candidate `outputs/06-materialize-candidate/pages/page-010.md` through `page-018.md`; assigned `plan.md`, `context.md`, `kb_creator/PROJECT_STATUS.md`, and `docs/governance/nri_goal_governance.md`.
- Verification/evidence: page-by-page visual inspection of all nine PNGs and exact candidate Markdown; page-018 contains seven separately identifiable stat blocks, itemized below. Source visuals intentionally retained as images are not counted as defects on that basis alone; findings concern lost structure/boundaries or stats whose only semantic carrier is an image.
- Blockers: none.
- Next action: orchestrator de-duplicate these findings with A1/A3 receipts and integrate exact goal-wide page and defect-unit totals.
- Elapsed time: approximately 12 minutes.
- Token use: unavailable.
- Timestamp: 2026-09-17 11:40:32 UTC.

## Findings

| Page | Structural unit | Candidate loss | Evidence / qualification |
|---:|---|---|---|
| 10 | Handout 3, promotional leaflet | Visible boxed/ad layout and handout boundary are flattened into ordinary prose; “Handout 3” occurs only as a trailing label. | Source page 10 shows the leaflet enclosed in a border with centered display copy; candidate has no callout/handout wrapper. This is structure, not a wording defect. |
| 10 | Handout 4, journal summary | Handout boundary and enclosed document treatment are not represented; the summary is ordinary heading/body text and its handout label trails the text. | Source shows a separate bordered journal extract, followed by an explanatory keeper sentence. Candidate has the heading and trailing `Handout 4` label but no semantic handout boundary. |
| 11 | Four-item event list | First (“Transhumanism”) and fourth (“Dreaming”) entries lack list markers; only entries 2 and 3 use bullets. | Candidate lines beginning `Transhumanism` and `Dreaming` are plain paragraphs, while the intervening two use `•`. This splits one source list. |
| 14 | Handout 5 letter | The letter’s boundary and letter/voice styling are lost; body and sign-off are plain flow text, with the handout label after the content. | Source presents a distinct ruled, handwritten letter panel. Candidate has no letter/callout wrapper. OCR typos within the letter are not counted here. |
| 14 | Four-item letter list | Items 1–3 are plain paragraphs without list markers; item 4 begins with escaped `\\-`, rendering a literal hyphen rather than a semantic list item. | Source letter has four hyphen bullets. Candidate only retains a non-semantic escaped dash on the fourth. |
| 15 | Keeper’s Note sidebar | Sidebar/callout role is lost; candidate heading and italic prose read as an ordinary main-flow section. | Source renders the note as a shaded, boxed, italic sidebar. The note’s text is present, but its structural role is not. |
| 17 | Conditional speech, branch “revealed Elsie’s location” | Speech is plain paragraph text rather than a quote/dialogue block. | Source uses a visibly indented italic speech block following its condition. Candidate leaves the conditional sentence and speech as unmarked paragraphs. |
| 17 | Conditional speech, branch “did not reveal Elsie’s location” | Speech is plain paragraph text rather than a quote/dialogue block. | Same source/candidate mismatch as the first conditional speech; separately scoped branch and speech unit. |
| 17 | Final speech (“In either case…”) | Distinct quoted closing speech/monologue is plain paragraph text with no quote semantics. | Source presents the passage as a separate indented italicized block; candidate merges it into regular prose flow. |
| 18 | Stanwick Webb stat block | Attack entries are concatenated into one prose run; subsequent image/table regions and skill data lack an explicit boundary from the Stanwick block or the next character. | Candidate has a character heading and some semantic values, but no structured attack list/table or complete card boundary. Image retention does not restore those semantic relationships. |
| 18 | Elsie Webb stat block | No semantic character heading; statistics are carried by source-visual images, followed by skills text without a card boundary. | Candidate’s visual/semantic sequence after Stanwick does not label this character or associate all fields in a structured block. |
| 18 | Enlightened (Regular) stat block | No semantic character heading; core stats/attack data are image-only, and following skills text is ungrouped. | Candidate inserts source visuals but does not expose the name/field association as semantic Markdown. |
| 18 | Enlightened (Heavy) stat block | No semantic character heading; core stats/attack data are image-only, and following skills text is ungrouped. | Candidate inserts source visuals but does not expose the name/field association as semantic Markdown. |
| 18 | Migo-man stat block | Core stats are image-only; skills are plain prose rather than fields in a character card. | A separate `THE MIGO MAN` heading exists, but the image and skills paragraph are not joined as a semantic stat block. |
| 18 | Migo stat block | Stat row is image-only; attacks, armor, skills, and sanity are split across plain prose/heading-like lines. A second source visual repeats the attack/armor/skills content without clear duplicate/semantic relationship. | Candidate does not provide one structured stat block. The visual duplication is reported as a structural ambiguity, not as an OCR typo. |
| 18 | Hunting Horror stat block | Core stats are image-only and the following attack/armor/skills fields are ungrouped prose, without a semantic character heading/card boundary. | Candidate includes the source visual and some fields, but does not semantically associate them as one stat block. |

## Non-findings and classification

- Pages 12, 13, and 16: headings and paragraph/section order are materially preserved; no confirmed sidebar, handout, list, table/card, heading-order, or multi-column reading-order loss was identified.
- Page 15 floor plan and page 18 stat visuals are intentional visual preservation. The defects above are the missing semantic structure/field associations, not the mere presence of images.
- Page 10’s two-column reading order is preserved in candidate flow. Page 11 and page 17 content also follows source column order; findings there concern lost list/dialogue semantics.
- OCR spellings, punctuation, capitalization, and numerical transcription discrepancies are outside this structural receipt and were not counted as structural units.
