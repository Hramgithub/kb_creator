# Fear story artwork audit and remediation specification

Goal `20261004-user-docx-review`, step U3. Architecture analysis only. No book, source, production script, canonical plan/status, or Git state was changed. This is not a final release review.

## Result

**23 of 26 story-opening illustrations are missing from the delivered book.** All 26 original opening pages visibly contain substantial story artwork. Only the art associated with physical PDF pages 46, 113 and 129 survives in the current 63-asset output. The missing scenes are absent from the entire exported asset set, not merely from their expected page sections.

The original supplied during this audit is exactly the historical source: 200 pages, 69,575,583 bytes, SHA-256 `49CDBAD99DDF5535E5911DBB89D11E2E1D0FC7BABD69DADBCE28A80EC9586888`. Its current location is `D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/temp/fears-sharp-little-needles/Call Of Cthulhu 7ed - Fear's Sharp Little Needles.pdf`.

The human-reviewed `kb_creator/deliverables/latest/fears-sharp-little-needles/document.docx` remains SHA-256 `E8505B99F81A54E02FC1AEA9777C45AE12FDE600A8AB2B2728DDE8F9C0BF8DCD`. HTML contains 63 unique image files; DOCX contains 63 image parts and 63 drawing occurrences. **Every image hash and their order agree between HTML and DOCX.** The existing 257-page preview PDF invokes 63 images on 63 pages. These are actual content-stream image calls; the shared PDF resource dictionary alone would incorrectly imply 63 images on every page.

Visual classification of retained output: 30 maps, 16 narrative/character pictures, 3 opening pictures, 11 facsimiles/graphic handouts, 1 cover, 1 credits page and 1 decorative clip. Counts classify assets/occurrences, not unique source compositions: some maps repeat in the appendix. This confirms a concentrated loss of story-opening art rather than disappearance of all illustrations.

The user-supplied PDF's sibling DOCX, HTML and preview PDF match the delivered files byte for byte. Its sibling `assets/` contains the same 63 unique hashes and no additional art.

## Complete opening-art mapping

All page numbers below are physical, one-based pages of the hash-bound original PDF. HTML anchors, selected/native object identities, dimensions, screenshot hashes and exact image paths are in `analysis.json` and `source-inventory.json`.

| Source page | Story | Current art |
| --- | --- | --- |
| 8 | Страх разлуки | Missing |
| 14 | Подводное течение | Missing |
| 19 | Грехи моей юности | Missing |
| 24 | Последнее желание Уолтера | Missing |
| 29 | Чьё топливо — люди и камни | Missing |
| 35 | Pulvis et Umbra Sumus | Missing |
| 41 | Великий и ужасный Авто | Missing |
| 46 | Спилсбери № 9485 | Retained |
| 51 | Свет погас | Missing |
| 57 | До самых костей | Missing |
| 63 | Не вызывай того, чего не сможешь усмирить | Missing |
| 69 | Сбил и скрылся | Missing |
| 74 | Преображение рифа Хаттерас | Missing |
| 79 | Язвы | Missing |
| 86 | И тут явился Жнец | Missing |
| 92 | Воскрешение | Missing |
| 97 | В ожидании рождения | Missing |
| 103 | Анленд | Missing |
| 109 | Фокус-группа | Missing |
| 113 | Диссоциация | Retained |
| 119 | Поэтический вечер | Missing |
| 124 | Tormiss CRD, модель Z-17 | Missing |
| 129 | Призраки Рейвенскара | Retained |
| 135 | Особое меню | Missing |
| 141 | Исследовательский центр Уинока-Пойнт | Missing |
| 147 | Флеботомия | Missing |

The full 200-page source was visually triaged on five 40-page contact sheets; all 26 openings were additionally inspected on larger opening sheets. This was an artwork inventory, not a full-resolution text/layout acceptance. Additional full-page assets on source pages 2 and 193/196/199, text facsimiles on 81/82/156/165/169, and recurring faded symbols are separate repeated-cover, text-facsimile or ornament decisions. Do not silently classify them as missing story pictures or delete their translated text.

One separate provenance anomaly is confirmed: output asset index 41, the surgery scene, is labelled source page 176 in HTML, but the original picture is on physical source page 175. The picture survives. Resolve physical source identity separately from any intentional semantic owner/placement; do not move the picture blindly because of a metadata discrepancy.

## Earliest proven loss and dependency trace

`original PDF graphics -> extraction candidates -> selected source dispositions -> source/master image anchors -> reviewed RU/prepared master -> reader projection -> HTML/assets -> DOCX -> preview PDF`

The original has the 23 scenes; the HTML/assets already lack them. The same selected set survives into DOCX. Therefore the earliest observable failing boundary is **at or before reader HTML**, and the Word embedding step is exonerated for this loss. It is not yet possible to choose among extraction, source selection, master transport and reader omission: their exact frozen data is missing from this checkout and the supplied folder.

Available historical evidence supports this boundary but cannot replace the lost data. Old `queue.json` records 82 extracted assets with a graphic route at N123 and three additional image anchors on pages 23/44/66 around N133. `plan.md` records 63 images already at N151/V04, long before the latest transfer. N368/N369 explicitly preserved only the referenced 63 Fear assets. **82 minus 63 is not a valid missing-art count** because these are different inventories and stages, with possible alternate-view/duplicate assets.

Confirmed verification gap in current reusable code:

- `pipeline/five_step_docx.py:406` finds image references already in MASTER_RU.
- `_asset_plan` at line 436 derives page/anchor ownership only for those references.
- `_reader_image_occurrences` at line 459 adjusts that existing count for explicit omissions and region replacements.
- `build_docx_package` at lines 708 and 779-785 checks DOCX against that derived count. This cannot detect art absent before MASTER_RU or art never assigned a reader placement.
- `pipeline/reviewed_asset_retention.py:17` deliberately retains image-only packet assets as `reference_only`; its docstring explicitly says reader content does not change. Retention in an archive is not publication coverage.
- `pipeline/reconstruction_asset_inventory.py:27` verifies assets exposed by Stage02/03 inventories. It cannot establish that those inventories contain every meaningful source graphic.

These are contract observations. No evidence currently proves which exact row or function omitted these 23 pictures. A plausible class is opening/background artwork omitted from selection or retained only for reference; it remains a hypothesis until replay evidence is restored.

## Available inputs and missing-input allowlist

`missing-inputs.json` is the finite recovery allowlist. The original PDF is now available and is not a blocker. The current reviewed DOCX, HTML and all 63 output assets are available. Missing dependencies are the exact N327 bilingual/prepared masters, N349 reader options, N317 layout configuration, V19 build/projection/asset reports and source-choice/extraction authorities. The historical recovery index/archives may supply these inputs.

The book input/working trees and named checkpoints were checked in the current root, all ten Git-registered worktree roots including the current one, and the historical `C:/_Hobby/_work/NRI` root; none was present at those named locations. The original old Yandex path was absent; the user then supplied the matching new path. `inventory.json` records the earlier availability observation, superseded by `source-inventory.json` for source availability. No drive-wide search or remote retrieval was attempted.

## Remediation scope A: full upstream correction and rebuild

This is the route that can close the pipeline defect. It requires restoring the allowlisted frozen dependencies and their exact identity checks before any build. Never infer that old PIDs or stale running queue entries are live or successful.

1. Build an independent source graphic ledger for all 200 pages, seeded by the 26 known opening scenes. A ledger entry is one meaningful graphic occurrence, not every PDF XObject: original pages contain many glyph/shadow resources. Record `graphic_id`, source PDF hash, physical page, PDF object path/xref or rendered region, dimensions/bbox, category, semantic story/anchor, original identity, chosen binary/composition, disposition, reason and visual evidence. Distinguish physical source page from reader placement.
2. Bind each ledger row through Stage02 candidates, selected source decisions, source/master anchors, RU projection, reader choices, HTML occurrence, OOXML relationship/media hash and rendered placement. Record the first absent boundary for each of the 23 rows. Reference-only retention cannot satisfy a required reader occurrence.
3. Repair the earliest data/config/implementation boundary found. Reuse `reconstruction_asset_inventory`, reviewed source graphic decisions and normal successor lineage. If an original image is absent from all MinerU views, recover the finite required native objects with the existing `scripts/extract_pdf_image_assets.py` route and hash-bound reviewed selection; no new OCR is needed. Inspect masks, composition and completeness before choosing the largest image object. A bare area threshold is not an acceptance rule.
4. Keep translated headings/bylines/tags as text exactly once. Prefer complete native artwork where the source provides it. When only a composite/crop is safe, record the explicit bounds and remaining embedded English text; do not erase part of the picture to remove lettering or silently duplicate a full source page with English prose.
5. Generate a successor of the actual human-reviewed input, preserving all user replies/decision anchors and unrelated content. Retain prior reviewed files byte for byte. Restore the original 63 retained assets unless a separate reviewed correction changes a specific identity. Resolve the 175/176 provenance anomaly through exact semantic bindings.
6. Extend reusable QA with source-ledger coverage so required source graphics missing from MASTER_RU or reader output fail before DOCX publication. Every meaningful source graphic requires either a validated output occurrence or a specific reviewed exclusion; a blanket decorative/reference-only decision must not absorb story openings.

Acceptance criteria: all 26 opening scenes have correct, nonzero, hash-bound reader placements in their stories; all other ledger rows have a disposition and no unexplained omissions; HTML/Word/image occurrence checks are tied to this independent domain; existing maps/portraits/handouts and reviewed text/comments are conserved; the actual successor is rendered and every changed page is inspected, with exact evidence for any inherited coverage. Final source/master identity and independent release review remain separate gates.

Required focused tests: missing source-graphic row despite a self-consistent master fails; `reference_only` does not satisfy `must_include`; reviewed genuine decoration exclusion passes without suppressing an adjacent opening; changed PDF/candidate/crop hashes fail; repeated map occurrences are not collapsed by shared binary hash; a source-region replacement accounts for its exact occurrences; a dropped/misplaced/cropped Word image fails; comment and source-anchor preservation is verified on a actual successor fixture. Tests must exercise the first repaired boundary, not merely assert that 23 images were appended.

## Remediation scope B: bounded native-art recovery for a reader successor

The supplied PDF and current reviewed DOCX make a narrower art-restoration successor feasible even while replay is unavailable. It is a separate scope decision for the orchestrator/user; it is not silently substituted for scope A.

All opening pages expose substantial native image candidates (predominantly JPEG objects); exact candidate xrefs/dimensions are in `analysis.json`. After inspecting each chosen object for completeness, recover only the 23 confirmed missing scenes into a new asset set, bind them to the existing story anchors, preserve the current DOCX review threads and all original content, and generate a new reviewed successor through a reusable, manifest-bound revision route. Do not fabricate missing MASTER_EN/RU or claim the original generator was repaired. If one image per missing opening is added without replacements, the expected media/occurrence count would be 86; the real gate is the manifest mapping, not that count alone.

Acceptance criteria for this narrower result: 26/26 opening-art coverage, exact original PDF identity and per-art selection evidence, original 63 image identities conserved, all native user comments/replies and body text preserved except explicitly approved decisions, no new orphaned/duplicated headings, and rendered changed-page verification. Label its provenance as a reader-art successor with upstream cause/replay unresolved. It cannot satisfy source reconstruction lineage or full pipeline closure.

## Evidence files and limits

- `inventory.json`: exact delivered file hashes, all HTML image paths/hashes/dimensions, Word relationships/order, PDF content-stream use, source-section/TOC mapping and bounded path checks.
- `source-inventory.json`: exact supplied source identity, all 200 source page object-use inventories, 26 opening page mappings and screenshot identities through `analysis.json`.
- `analysis.json`: visual classifications, exact 23/26 result, dominant native recovery candidates, source175/176 anomaly, code identities and sibling comparison.
- `missing-inputs.json`: restoration allowlist and purpose for each missing dependency.
- `source-opening-*.png`, `source-openings-contact-*.jpg`, `source-all-pages-*.jpg`, `asset-contact-*.jpg`: audit previews. These are diagnostic evidence, not selected production images.

No book rebuild, OCR, production extraction, final release criticism or source mutation was performed. Source and reviewed DOCX identities are rechecked in the handoff evidence. The remaining blocker for full upstream closure is missing reviewed replay/master data; the artwork omissions themselves are established.
