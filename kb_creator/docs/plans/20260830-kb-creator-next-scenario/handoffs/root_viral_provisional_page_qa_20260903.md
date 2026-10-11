# Provisional full-page source check

- Goal: 20260830-kb-creator-next-scenario; Step 7.
- Owner: root orchestrator (Sol/medium policy; platform unverified).
- Scope: read-only source-PDF rendering and visual inspection, not publication
  acceptance or Step 8A binary-quality selection.
- Input: kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf.
- Method: existing Poppler `pdftoppm -r 200 -png -singlefile` per full page;
  no OCR overlay or detected-region crop. PDF skill used for visual verification.
- Scratch root: tmp/pdfs/viral-provisional-qa-c2953f5539a14f72aaddb393baed9c33.

All nine declared recipe pages were rendered and individually viewed:
1, 106, 107, 112, 114, 116, 118, 120, 122. Each image is 1700 x 2200.
Pages 106/107 contain the complementary map spread including Key, legend,
scale, chapel and underground regions. The six back pages retain the complete
form borders, background, gear/assets, quick-reference rules and responsibility
or fellow-investigator panels. Page 1 retains the complete cover.
No truncation attributable to an OCR crop or overlay was present.

This proves the recipe can preserve the full source pages. It does not prove
the yet-unbuilt candidate contains these assets in the correct order; candidate
manifest, placement and source/reader QA remain mandatory after the build.
Final extracted-XObject versus render quality choice stays after MASTER_RU.

Independent QA-generator test run by root: 16 passed in 6.27s.
No source, accepted reconstruction, frozen config, candidate or Git mutation.
Token breakdown: unavailable.
