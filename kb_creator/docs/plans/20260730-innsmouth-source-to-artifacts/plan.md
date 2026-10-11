# Innsmouth Source PDF to Artifacts Plan

Goal id: `20260730-innsmouth-source-to-artifacts`

Objective: process the original `The Innsmouth terror.pdf` through
`kb_creator` and produce fresh KeeperBook, HTML, and PDF artifacts without
depending on the deleted `CoC/Working/Scenarios/The_Innsmouth_Terror` or
`CoC/Output/Scenarios/The_Innsmouth_Terror` scenario trees.

## Source and References

Source PDF:

`D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/english/7th Edition Call of Cthulhu/Adventures/1923_The Innsmouth Terror/The Innsmouth terror.pdf`

SHA-256:

`CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F`

Reference KeeperBook for comparison only:

`D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/1_Сценарии/Компания/1928 Побег из Инсмута/Террор в инсмуте/For_Keeper/KeeperBook_v6.md`

SHA-256:

`E1C889ADB5676798D7E296E4231040FA730029A7BA40AD515BF97059F5F78BA7`

Reference PDF for comparison only:

`D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/1_Сценарии/Компания/1928 Побег из Инсмута/Террор в инсмуте/Pdf/The_Innsmouth_Terror_RU.pdf`

SHA-256:

`D89BA390B296211692419D08F8E8F84CB0D393B54E94489531542BB5A0E08FC5`

## Target Outputs

Fresh outputs must be generated under `kb_creator`, not copied from the
reference folder:

- `kb_creator/output/innsmouth_source_to_artifacts/runs/<run_id>/For_Keeper/KeeperBook.md`
- `kb_creator/output/innsmouth_source_to_artifacts/runs/<run_id>/The_Innsmouth_Terror_Full_RU.html`
- `kb_creator/output/innsmouth_source_to_artifacts/runs/<run_id>/Pdf/The_Innsmouth_Terror_RU.pdf`
- `kb_creator/reports/innsmouth_source_to_artifacts/runs/<run_id>/full_run_report.json`
- comparison reports against the Keeper/PDF references.

## Non-negotiable Boundary

The previous `kb_creator` result proved a v6-derived publishing rebuild. This
goal must not repeat that shortcut.

The pipeline may reuse code and rules from `translator`, but it must generate
the current artifacts from the original PDF and explicit `kb_creator` working
state.

If a required stage still depends on historical accepted v6 outputs, the run is
blocked and the missing reusable stage must be implemented or ported.

## Steps

| Step | Owner | Effort | Status | Definition of Done | Evidence | Blocker | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Verify source/reference availability | gpt-5.5 orchestrator | medium | completed | Source PDF and both references exist and hashes are recorded | this plan; shell hash check | none | done |
| 2. Audit existing kb_creator capability | gpt-5.5 orchestrator | medium | completed | Known scripts are classified as reusable, v6-dependent, or missing | context.md; runner report | none | done |
| 3. Define real full pipeline contract | gpt-5.5 orchestrator | medium | completed | Stage contract covers PDF intake, text-layer source, OCR audit, image inventory, translation tasks, Keeper, HTML, PDF, and comparisons | `kb_creator/scripts/build_innsmouth_source_to_artifacts.py` | none | done |
| 4. Implement missing kb_creator source stages | gpt-5.5 orchestrator | medium | completed | Clean-room config, PyMuPDF text-layer extraction, OCR separation, source cleanup, reading-order evidence, and tests exist | `kb_creator/tests/test_innsmouth_source_to_artifacts.py`; run `20260730T210831Z` | none | done |
| 5. Execute accepted RU translation/proofread stage | gpt-5.5 orchestrator + bounded agents | medium | completed-for-current-candidate | Translation batches are filled without using reference KeeperBook as source; RU master is assembled with source hashes | `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Formatted/The_Innsmouth_Terror_Source_Text_Full_RU.md`; `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`; `pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py` | none for current candidate | keep improving preservation/proofread quality |
| 6. Run source PDF to Keeper/HTML/PDF | gpt-5.5 orchestrator | medium | completed | Fresh KeeperBook/HTML/PDF are generated under `kb_creator/output/...` | `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/full_run_report.json` | none | done |
| 7. Compare against references | gpt-5.5 orchestrator + Terra review if needed | medium/high | completed-for-current-candidate | Keeper/PDF exact differences are recorded, and non-exact agent translation drift is accepted only when structural/body/PDF gates pass | `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/artifact_comparison_report.json`; `statblock_readiness_report.json`; `production_pdf_report_two_column.json` | none | user visual review or next productization step |
| 8. Source art anchor contract | gpt-5.5 orchestrator | medium | completed-for-source-layer | Approved reader art has deterministic EN-source anchors before RU publishing; EN Keeper carries explicit art blocks for downstream restoration | `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/art_anchor_manifest.json`; `source_art_anchor_report.json`; `For_Keeper/KeeperBook_EN.md`; tests `36 passed` | `1` page fallback remains for cover/title art and is expected because cover has no body anchor | connect this manifest to RU Keeper/HTML/PDF as the authoritative art placement source |

## Acceptance Criteria

- The source PDF hash matches the recorded SHA-256.
- The generated KeeperBook is not copied from the reference path.
- The generated HTML is built from the generated KeeperBook.
- The generated PDF is built from the generated HTML.
- Each stage records command, input hash, output hash, and findings.
- Keeper comparison against the reference reports structure/text/art deltas.
- PDF comparison against the reference reports page count, render evidence, and
  visual/text differences.
- Any fallback to historical v6 accepted artifacts is explicit and blocks final
  acceptance unless the user approves that narrower scope.

## Current Status

`completed-for-current-candidate`.

Latest clean-room source-to-artifacts run:

`kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/full_run_report.json`

The run starts from the original PDF, renders pages, extracts primary source
text from the embedded PDF text layer via PyMuPDF, normalizes it, keeps column
OCR as an audit/fallback layer, extracts images, prepares translation units,
builds the current RU-master-derived KeeperBook, rebuilds production HTML, and
rebuilds the two-column PDF.

Current result:

- current stage status: `pass`;
- final comparison status: `accepted_drift`;
- exact byte/text identity is not required for body text produced by an
  agentic translation step; exact differences remain recorded in the report;
- remaining blocker code: none;
- KeeperBook/HTML/PDF are fresh kb_creator outputs, not copied reference files;
- generated KeeperBook: `46` source-page markers in the current candidate vs
  reference `45`;
- generated HTML: `46` source pages, `77` headings, `61` image refs,
  `0` missing image refs;
- statblock projection is now active: `22/22` cards projected from the RU
  master, `22` HTML cards, `176` structured statblock tables/sections,
  `0` flattened statblock findings;
- generated PDF builds successfully from the generated HTML; latest PDF report
  status is `pass`, `action=built`, `findings=0`;
- service/backmatter text from source page `044` is now suppressed from
  reader-facing text while preserving page/art anchors; comparison classifies
  page `044` as `extra_art_or_trace_only`, not reader-text drift;
- reference comparison is accepted with deterministic drift gates: source pages
  `45/45`, headings `62/62`, Keeper art blocks `34/34`, body gate `pass`,
  body pages requiring review `0`, PDF pages `32/32`, PDF text delta ratio
  `0.0297`.

Structure-aware comparison update:

- strict normalized delta after the latest boundary repairs, page `043`
  duplicate Handout #2 cleanup, and full statblock projection: `+7857` chars;
- reader-text delta: `+7805` chars;
- reader-text delta ignoring statblock scaffold: `+2364` chars;
- statblock-aware split: `non_statblock_delta_chars=2324`,
  `statblock_delta_chars=40`;
- missing reader-text pages: none;
- extra reader-text pages: none;
- extra art/trace-only pages: `044`;
- repaired large boundary drifts: `010/011`, `016/017`, `018`, `019/020`,
  and `028/029`;
- repaired duplicate reader text: page `043` duplicate Handout #2 body;
- top remaining non-statblock text deltas: page `016 +350`, `028 +252`,
  `021 +236`, `026 +229`, `017 +200`, `012 +174`, `006 -164`,
  `027 +139`;
- PDF page count matches the reference: `32` vs `32`; PDF text chars remain
  different: `118315` vs `113519`.

The current blocker is no longer source reconstruction, image integration,
statblock structure, HTML generation, PDF generation, or exact wording drift.
Statblock-page drift is proven to be mostly projection form rather than missing
card structure, and body text passes the deterministic preservation gate. The
remaining known issue is a non-blocking PDF QA warning: page `32` is
`half_empty_pdf_page`, because final handout flow differs visually from the
reference while preserving content.

Operational note: the full run was executed with explicit permission because
the PDF renderer needs filesystem access for temporary PDF replacement. The
latest full-run report itself is now `status=pass`, not a manual partial
override.

## 2026-08-01 Checkpoint: Accepted Drift Full Run

Status: completed-for-current-candidate.

Evidence:

- full source-PDF-to-artifacts runner:
  `status=pass`, `findings=0`;
- full run report:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/full_run_report.json`;
- generated KeeperBook:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook.md`;
- generated HTML:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/The_Innsmouth_Terror_Full_RU.html`;
- generated PDF:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf`;
- comparison report:
  `status=accepted_drift`, `keeper=accepted_drift`, `pdf=accepted_drift`;
- source pages: `45/45`;
- headings: `62/62`;
- Keeper art blocks: `34/34`;
- body similarity: `pass`, pages requiring review `0`;
- PDF pages: `32/32`;
- PDF text delta ratio: `0.0297`;
- PDF print QA: `status=pass`, `findings=0`, `warnings=1`;
- technical garbage scan in Keeper/HTML found no escaped anchors, source hash
  comments, unit ids, or numeric entity residue.

The remaining PDF warning is `half_empty_pdf_page` on page `32`; this is a
layout-density issue and does not block the current reproducibility objective.

Translation batch limit update:

The practical translation delegation limit is fixed at about `3000` source
characters. `build_innsmouth_source_to_artifacts.py` writes
`translation.max_unit_chars = 3000`; `prepare_translation_batches.py` defaults
to `3000`, splits source units that exceed the limit, and
`merge_translation_batches.py` reassembles split parts back into their original
unit. The source-to-artifacts runner now generates the primary handoff batch
manifest at
`Translation_Work/RU_Batches_3000/translation_batch_manifest.json`. Verified
current manifest: `54` batches, `60` original units, `60` translation parts,
maximum batch size `2998`, `0` batches over `3000`. Test evidence: `4 passed`
in `kb_creator/tests/test_innsmouth_source_to_artifacts.py`.

Legacy note: `Translation_Work/RU_Batches/` is an older large-batch handoff
directory from the first delegation wave and is not valid for new translation
work.

## Follow-up Checkpoint: Translation Batch Limit

The practical translation handoff limit is verified as `3000` source
characters.

Evidence:

- current manifest:
  `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest counts: `54` batches, `60` units, `60` original units,
  `0` split units, max batch size `2998`, `0` batches over `3000`;
- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`;
- page-delta diagnostics are script-backed by
  `kb_creator/scripts/dump_innsmouth_page_deltas.py`;
- deterministic CoC term cleanup and confirmed intra-page order repairs for
  pages `021` and `028` have been applied in
  `build_keeperbook_from_ru_master.py`;
- fresh comparison still reports `different`, with
  `reader_text.delta_chars=7667`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2226`,
  `non_statblock_delta_chars=2186`, and `statblock_delta_chars=40`;
- PDF page count remains matched at `32` vs `32`, with no PDF structural
  findings.

Immediate next step:

Continue page-scoped RU preservation/proofread parity on ordinary reader text,
starting from pages `016`, `026`, `028`, `021`, `012`, `006`, `017`, and
`027`. Do not change the `3000` batch limit unless a future source unit proves
that the limit itself is failing.

## Follow-up Checkpoint: Page-Order Repairs

Applied reproducible Keeper assembly repairs for pages `012`, `026`, and
`028`, then rebuilt KeeperBook, HTML, statblock projections, PDF, comparison,
and tests.

Evidence:

- KeeperBook assembly: `status=pass`, `pages=46`, `headings=63`;
- structural QA, heading QA, and page-reference QA: `pass`;
- statblock projection/readiness: `22/22`, `176` structured sections,
  `0` flattened findings;
- production HTML: `status=pass`, `pages=46`, `images=61`, `findings=0`;
- production PDF: `status=pass`, `variant=two_column`, `findings=0`,
  `sha256=6faca553bbd61cb0bcaa3591ff5968bfc24b08de09ef355b02536d1e5a638fdb`;
- tests: `4 passed`;
- comparison still `different`, but drift improved:
  `reader_text.delta_chars=7573`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2132`,
  `non_statblock_delta_chars=2092`, `statblock_delta_chars=40`.

Next pages by current priority: `016`, `028`, `021`, `026`, `006`, `012`,
`017`, `027`.

## Follow-up Checkpoint: User Translation Limit Hint

The user-provided practical translation limit was rechecked against the current
run. It remains the active invariant:

- `max_batch_chars=3000`;
- manifest: `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- current manifest: `54` batches, maximum observed batch size `2998`,
  `0` batches over `3000`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`.

This closes the limit-check subtask. Continue artifact-drift remediation without
changing the translation batch size unless new evidence proves the limit itself
is failing.

## Follow-up Checkpoint: Residual Header and Glued-Word Cleanup

Applied reproducible assembly fixes in
`kb_creator/scripts/build_keeperbook_from_ru_master.py`:

- standalone page `016` running/header residue `Innsmouth` is removed only when
  it appears after the source-page marker and before a heading;
- CoC term/spacing cleanup runs again after page-order repairs, because those
  repairs can surface glued line-break strings.

Verified removals:

- no `времяпервоначального`;
- no `поздносыщики`;
- no `Разговорс`;
- no standalone `Innsmouth` in the generated KeeperBook.

Rebuilt KeeperBook, statblock projection, HTML, PDF, comparison, page-delta
dump, and tests. Current result remains `different`:

- `reader_text.delta_chars=7566`;
- `reader_text_ignoring_statblock_scaffold.delta_chars=2125`;
- `non_statblock_delta_chars=2092`;
- `statblock_delta_chars=40`;
- PDF: `32` pages vs `32`, no structural findings;
- tests: `4 passed`.

Next remediation should distinguish true pipeline defects from ordinary
reference-style drift. Current priority pages: `016`, `021`, `028`, `026`,
`012`, `006`, `017`, `027`.

## Follow-up Checkpoint: Verified Translation Ceiling

The user hint about the translation limit was rechecked against the live run and
is now treated as a fixed ceiling for this goal:

- `max_batch_chars=3000`;
- manifest:
  `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- `54` batches, `60` units, `60` original units, `0` split units;
- maximum observed batch size: `2998`;
- `0` batches over `3000`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`.

Do not tune translation batch size while addressing the current comparison
blocker. Continue with page-scoped RU preservation/proofread parity.

## Follow-up Checkpoint: Reader-Art Publication Parity

Applied reproducible reader-art policy and statblock-art preservation fixes:

- `build_keeperbook_from_ru_master.py` now persists reader-art suppressions and
  anchor overrides into `art_manifest.json`, so downstream HTML/PDF use the
  same placement policy as KeeperBook;
- decorative/source-page-only front/backmatter placements are suppressed from
  reader artifacts;
- Handout 2 art `xref-01397` is anchored to
  `razdatochnyi-material-2-zapiska`;
- `project_innsmouth_statblocks_from_ru.py` now reinjects NPC art blocks after
  replacing the statblock section;
- Ian Torres portrait `xref-01200` is recovered from source page render 38 as
  a deterministic crop and added to manifest/output assets.

Evidence after full rebuild:

- KeeperBook art IDs: candidate `34`, reference `34`, `extra=0`, `missing=0`;
- production HTML: `status=pass`, `images=34`, `findings=0`;
- statblock HTML readiness: `22` cards, `176` structured sections,
  `0` flattened findings;
- production PDF: `status=pass`, `variant=two_column`, `findings=0`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`.

Current comparison remains `different`:

- `reader_text.delta_chars=7480`;
- `reader_text_ignoring_statblock_scaffold.delta_chars=2039`;
- `non_statblock_delta_chars=2006`;
- `statblock_delta_chars=40`;
- PDF pages: `27` candidate vs `32` reference.

Next remediation target:

Continue with ordinary RU preservation/proofread parity and PDF layout density.
The art-set blocker is closed.

## Follow-up Checkpoint: Page 018 Reader-Order Repair

Status: completed for the confirmed page `018` defect.

Implemented:

- `build_keeperbook_from_ru_master.py` now has `_repair_page_018_order()`;
- the repair restores the train-room sequence:
  `Bazzledon’s Office -> Ginny’s Trailer -> McGuire’s Lab`;
- leading Bazzledon office investigation bullets are moved from before
  `### Вокруг поезда` back into `### Bazzledon’s Office`;
- `test_page_018_intrapage_repair_preserves_train_links_and_bullets` locks the
  behavior.

Evidence:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `5 passed`;
- KeeperBook and production HTML were rebuilt in the full run;
- two-column PDF was rebuilt through `build-production-pdf`;
- PDF SHA:
  `15b538122e03805fac2464a0a1874c0c730108b712d135dfc55eb5cd0ec0fb67`.

Current comparison:

- still `different`;
- `reader_text.delta_chars=7838`;
- `reader_text_ignoring_statblock_scaffold.delta_chars=2397`;
- `non_statblock_delta_chars=2364`;
- `statblock_delta_chars=40`;
- PDF pages remain `27` candidate vs `32` reference.

Next remediation target:

Classify the remaining top deltas by defect type before making another script
change: `016`, `026`, `028`, `021`, `012`, `006`, `017`.
## Follow-up Checkpoint: Translation Packet Limit Recheck

Status: completed after context compaction.

The practical translation handoff ceiling remains fixed at `3000` source
characters.

Evidence:

- active manifest:
  `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest values: `max_batch_chars=3000`, `54` batches, `60` units,
  max observed batch size `2998`, `0` batches over `3000`;
- config/script contract:
  `translation.max_unit_chars = 3000`,
  `prepare_translation_batches.py --max-batch-chars` default `3000`;
- test evidence:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `5 passed`.

Next action remains unchanged: classify remaining top deltas before making a
new repair.

## Follow-up Checkpoint: Projection Residual Cleanup

Status: completed for the confirmed residue class.

Implemented:

- removed artificial page-title/readout residue from page `006`;
- split page `012` Orne Library research continuation out of the Loring bullet;
- removed residual inline `Расследование` before `Díaz`;
- removed residual English `The Fire Station` before the translated fire station
  body;
- updated expected heading spine so page `006` no longer expects reader heading
  `### The Innsmouth Terror`, while the real
  `#### Прибытие: практическая справка` heading is tracked.

Evidence:

- tests: `7 passed`;
- Keeper assembly: `status=pass`, `headings=62`;
- production PDF: `status=pass`, `variant=two_column`,
  `sha256=3e40c0f16759fad087f7ef1c4a739b413ebad5b01e74a983e028201b07e9e52e`;
- comparison remains `different`, now with
  `reader_text.delta_chars=7761`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2324`,
  `non_statblock_delta_chars=2287`,
  `statblock_delta_chars=40`.

Next action:

Use
`kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/page_delta_classification_20260731.md`
to continue page-scoped classification and repair.

### Contract update - translation unit size

Status: completed.

Owner: orchestrator.

User clarified the translation limit as approximately `3000` source chars.
For this goal, kb_creator now treats `translation.max_unit_chars = 3000` as the
hard batch contract.

Evidence:

- active config has `translation.max_unit_chars = 3000`;
- active batch directory is `Translation_Work/RU_Batches_3000`;
- EN batch verification found `54` batch files and `60` units;
- largest unit is `2998` chars (`batch_16.en.json`, `p013_u0017`);
- units over `3000`: `0`;
- `kb_creator/tests/test_innsmouth_source_to_artifacts.py` asserts the
  generated config and batch naming.

### Follow-up Checkpoint: Oath Formatting And PDF Density

Status: completed.

Owner: orchestrator.

Implemented:

- restored the collapsed first/second/third Innsmouth oath sequence as a quote
  block in the reproducible KeeperBook builder;
- kept translation batches under the `3000` source-character contract;
- normalized generated two-column PDF body font size to `10pt`; statblock
  cards remain compact at `8pt`.

Evidence:

- tests: `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `9 passed`;
- full runner still reaches Keeper/HTML and blocks only at the known PDF
  subprocess sandbox boundary;
- manual/escalated production PDF step:
  `status=pass`, `variant=two_column`, `findings=0`;
- PDF print QA:
  `status=pass`, `pages=32`, `findings=0`, `warnings=1`;
- comparison after rebuild:
  `reader_text.delta_chars=7771`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2334`,
  `non_statblock_delta_chars=2297`,
  `statblock_delta_chars=40`,
  PDF pages `32/32`;
- candidate PDF SHA-256:
  `6d642656338392966081b5a149058965f2b234e58bf3c2115b122152628839cd`.

Next action:

Classify the remaining ordinary-text deltas page by page. Do not copy reference
wording to reduce delta; only implement reproducible source/RU-master-backed
pipeline fixes.

### Follow-up Checkpoint: Translation Payload Ceiling Recheck

Status: completed.

Owner: orchestrator.

User reiterated the practical translation limit as approximately `3000` source
characters. The current live batch manifest was rechecked and still satisfies
the contract.

Evidence:

- manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- `max_batch_chars=3000`;
- manifest counts: `54` batches, `60` units, `60` original units,
  `0` split units, `113960` source chars total;
- maximum observed batch size: `2998` (`batch_16`);
- batches over `3000`: `0`;
- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `10 passed`.

Next action:

Continue artifact parity work without changing the verified translation batch
limit.

### Follow-up Checkpoint: Source-Backed Statblock Core Fallback

Status: completed-for-current-candidate.

Owner: orchestrator.

Implemented a PDF text-layer fallback for statblock core values. This addresses
the source reconstruction loss where pages `033`-`035` preserved `STR/CON/DEX`
but lost combined-line values such as `SIZ`, `POW`, and `EDU`.

Evidence:

- script changes:
  `kb_creator/scripts/project_innsmouth_statblocks_from_ru.py`,
  `kb_creator/scripts/build_innsmouth_source_to_artifacts.py`;
- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `11 passed`;
- projection report:
  `status=pass`, `records=22`, `filled_from_pdf=51`, no findings;
- generated KeeperBook sample: Diane Loring now has complete core row
  `50/70/50/55/80/65/50/70/50`;
- PDF build and print QA pass, but current PDF remains `33` pages versus
  `32` reference pages.

Next action:

Continue with PDF density/layout parity and comparison-normalizer review. Do
not treat the remaining statblock comparison delta as proof of missing values
until the comparer can normalize HTML tables and plain-text reference
statblocks consistently.

### Follow-up Checkpoint: PDF Table Density And Art Parity

Owner: orchestrator.

Implemented:

- PDF statblock font override now preserves relative compact table sizing
  instead of forcing every nested table to the card base font size.
- reader-art marker cleanup now removes the false `source-page-044` publication
  boundary when retargeted handout art `xref-01397` is present under Handout 2.

Evidence:

- tests: `12 passed`;
- generated KeeperBook: `source-page-044=0`, `source-page-045=1`,
  `source-page-046=1`, `xref-01397=true`;
- generated HTML includes `xref-01397`;
- production PDF: normal full runner reached PDF but hit Windows
  `Permission denied` in `Temp/Production_PDF`; escalated PDF build then passed
  with `status=pass`, `variant=two_column`, `findings=0`;
- PDF print QA: `status=pass`, `pages=33`, `findings=0`, `warnings=0`;
- comparison still `different`, candidate/reference PDF pages `33/32`.

Current remaining blocker:

- art parity for Handout 2 is fixed;
- remaining differences are PDF density/layout parity and page-scoped
  RU/proofread drift;
- keep the verified `3000` translation batch-size contract unchanged.

### Follow-up Checkpoint: Full Runner Comparison Gate

Status: blocked-by-strict-comparison.

Owner: orchestrator.

The full kb_creator dry-run now reaches the final comparison gate through the
complete generation path from source PDF. The runner is blocked only because
the candidate is not yet equivalent to the frozen reference.

Evidence:

- generation path completed through PDF:
  `source PDF -> source reconstruction -> translation batches -> RU master -> KeeperBook -> HTML -> PDF`;
- full runner PDF command:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- PDF print QA:
  `status=pass`, `pages=33`, `text_chars=135387`, `findings=0`,
  `warnings=0`;
- comparison:
  `status=different`, `keeper=different`, `pdf=different`;
- candidate/reference source pages: `45/45`;
- candidate/reference art blocks: `34/34`;
- candidate/reference headings: `61/62`;
- candidate/reference PDF pages: `33/32`;
- `reader_text.delta_chars=7592`;
- `reader_text_ignoring_statblock_scaffold.delta_chars=2073`;
- verified translation ceiling: `max_batch_chars=3000`, maximum observed
  `2998`, batches over `3000=0`.

Next action:

Use the comparison report to continue parity remediation. Do not change the
translation batch limit, and do not re-open the fixed Handout 2 art issue unless
new evidence appears.

### Follow-up Checkpoint: Translation Ceiling Revalidated

Status: completed.

Owner: orchestrator.

The user hint about the practical translation limit is now treated as a hard
kb_creator contract for this goal: source translation packets must stay at
`3000` source characters or below.

Fresh verification:

- config: `translation.max_unit_chars=3000`;
- manifest: `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest field: `max_batch_chars=3000`;
- batches: `54`;
- units: `60`;
- original units: `60`;
- split units: `0`;
- maximum observed batch size: `2998` (`batch_16`);
- batches over `3000`: `0`;
- tests: `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `15 passed`.

Next action: continue strict artifact-parity remediation without changing this
translation ceiling.

### Follow-up Checkpoint: Body Similarity Gate

Status: completed-for-current-candidate.

Owner: orchestrator.

The comparison method now distinguishes exact wording drift from evidence of
body-text loss. Exact body text identity is still recorded, but body acceptance
uses hard deterministic signals: length delta and numeric preservation.

Evidence:

- `compare_innsmouth_artifacts.py` includes `body_similarity_report`;
- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `17 passed`;
- latest body report:
  `status=pass`, `pages_checked=34`, `pages_passing=34`,
  `pages_requiring_review=0`, `pages_requiring_semantic_review_only=24`;
- latest PDF build after unlock:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- latest PDF QA:
  `status=pass`, `pages=33`, `findings=0`, `warnings=0`;
- latest candidate PDF SHA-256:
  `1e337ddbaf829f8437b98a0e2a20b4e2c6887f6a8ca7d10b46b2eb332edec3ff`.

Next action:

Continue with objective non-body blockers: PDF page-count/density `33/32`,
statblock/reference divergence, heading count `61/62`, and any structural
source-backed issues. Do not chase 100% body wording identity.

### Follow-up Checkpoint: Preserve Tmp PDF Art-Order Candidate

Status: open-follow-up.

Owner: orchestrator.

Do not delete:

`D:\NRI\kb_creator\output\innsmouth_source_to_artifacts\runs\20260730T210831Z\Pdf\.The_Innsmouth_Terror_RU.tmp-37396-1785454676611631.pdf`

Reason: user observed that this temporary PDF appears to preserve art order and
near-text placement relative to the English source PDF better than the later
published candidate. Treat it as forensic evidence for a future pipeline
improvement.

Next action: compare tmp PDF, final generated PDF, and source English PDF;
recover the mechanism that produced the successful art order; encode it as a
deterministic `kb_creator` placement/layout rule and regression check.

### Follow-up Checkpoint: Source PDF Structured Text Extraction Gate

Status: completed for the source-only structure stage.

Owner: orchestrator.

Implemented:

- primary source extraction now uses `pdfplumber` coordinate lines instead of a
  page-wide PyMuPDF text blob;
- line grouping is column-aware, so same-height left/right column text cannot
  merge into one line;
- reading order is deterministic: full-width lines first when present, then
  left column, then right column;
- paragraph breaks use observed PDF geometry: normal line continuation is about
  `2pt`, paragraph breaks are about `6.5pt`;
- bullet and `Keeper note:` continuation lines stay inside their owning block;
- source running headers and scrambled visual-letter strings are filtered;
- `--stop-after-source` now blocks only on source-structure findings, not on
  missing downstream Keeper/HTML/PDF.

Evidence:

- latest source-only run:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260802TSTRUCTURE06/full_run_report.json`;
- source-structure audit:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260802TSTRUCTURE06/QA/source_structure_hazard_audit.json`;
- audit status: `pass`, findings `0`;
- source pages: `46`, missing/unexpected page markers `0/0`;
- reading-order anchors passed for pages `009`, `012`, and `024`;
- long paragraph blocks over `2800` chars: `0`;
- scrambled visual text blocks: `0`;
- unquoted Keeper notes: `0`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `20 passed`.

Decision:

Stop here for this micro-goal. Do not proceed to translation, KeeperBook, HTML,
or PDF until the next explicit instruction.

### Follow-up Checkpoint: KeeperBook vs EN PDF Structure Audit

Status: completed.

Owner: orchestrator.

Implemented a reproducible page-level audit:

- `kb_creator/scripts/audit_innsmouth_keeper_pdf_structure.py`;
- full Markdown table:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/keeper_pdf_structure_audit.md`;
- machine-readable JSON:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/keeper_pdf_structure_audit.json`.

The audit compares the current generated KeeperBook against the English source
PDF by source page:

- no-whitespace character counts;
- paragraph/block counts;
- first meaningful left/right PDF column lines;
- mechanical left/right order in Keeper when line anchors can be found without
  semantic translation.

Evidence:

- pages checked: `46`;
- column-order failures: `0`;
- column-order pass: `1`;
- ambiguous: `2`;
- not-testable: `38`;
- not-applicable: `5`;
- flagged pages for ratio/projection review:
  `002`, `003`, `006`, `014`, `023`, `033`, `034`, `035`, `036`, `037`,
  `038`, `039`, `040`, `041`, `042`, `043`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `20 passed`.

Next action:

Use the table to separate real structural defects from projection-specific
expected drift. There is currently no mechanically proven column-order failure
in the generated KeeperBook.

### Follow-up Checkpoint: EN PDF vs Normalized EN Source Integrity

Status: completed.

Owner: orchestrator.

Implemented a source-layer integrity audit:

- `kb_creator/scripts/audit_innsmouth_source_pdf_integrity.py`;
- full Markdown table:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/source_pdf_integrity_audit.md`;
- machine-readable JSON:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/source_pdf_integrity_audit.json`.

The audit compares the English source PDF against
`The_Innsmouth_Terror_Source_Text_Normalized_EN.md` page by page:

- no-whitespace character counts;
- paragraph/block counts;
- first meaningful left/right PDF column lines;
- exact/similarity score against the current coordinate extractor output;
- warning flags for pages that may have cross-column sentence-flow hazards.

Evidence:

- pages checked: `46`;
- exact pages: `23`;
- non-exact pages: `23`;
- maximum no-whitespace character delta: `15`;
- minimum similarity: `0.99377`;
- paragraph/block deltas only on pages `012` (`+1`) and `042` (`-1`);
- possible cross-column sentence split warnings:
  `005`, `006`, `007`, `009`, `010`, `012`, `013`, `016`, `019`, `020`,
  `021`, `023`, `028`, `030`, `031`, `032`, `033`, `035`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `20 passed`.

Next action:

Review the warning pages visually and decide whether they need page-type or
layout-specific reading-order policy. Do not treat the current source layer as
character-lossy; the live evidence points to reading-flow policy risk instead.

### Follow-up Checkpoint: Delegated Warning-Page Review

Status: completed.

Owner: orchestrator with bounded `gpt-5.4` executor/QA handoffs.

Handoff artifacts:

- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_A1.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_A2.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_A3.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_B.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_summary.md`.

Coverage:

- warning pages assigned: `18`;
- warning pages reviewed: `18`;
- missing pages: none.

Result:

- `ok`: `14` pages;
- `real_issue`: `005`, `006`, `023`;
- `needs_human_visual_review`: `031`.

### Follow-up Checkpoint: Source Extraction Fixes for 005/006/023

Status: completed.

Owner: orchestrator.

Changes:

- page `005`: repaired split quote / introduction interleaving;
- page `006`: repaired oath/body reading order and `Table 1` timeline;
- page `023`: repaired `Table 2` as an explicit Markdown table;
- source hazard and source integrity audits now accept Markdown tables as
  structured table blocks rather than prose collapse.

Evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `23 passed`;
- source rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z --stop-after-source`
  -> `status=pass`, `findings=0`;
- EN PDF/source audit:
  `python kb_creator/scripts/audit_innsmouth_source_pdf_integrity.py`
  -> `status=pass`, `pages=46`, `flagged=15`;
- pages `005`, `006`, and `023` now have no integrity flags.

### Follow-up Checkpoint: Page 031 Occluded Text-Layer Policy

Status: completed.

Owner: orchestrator.

Decision:

- page `031` contains a `What if they’re captured?` block in the technical PDF
  text layer, but not in the visible rendered source page;
- this is classified as `occluded_text_layer_recovered_content`;
- the block is excluded from the accepted EN source;
- the block is retained in a QA artifact and may only be published by explicit
  editorial recovered-content decision.

Evidence:

- QA artifact:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/occluded_text_layer_recovered_content.json`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `24 passed`;
- source rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z --stop-after-source`
  -> `status=pass`, `findings=0`.

Next action:

If a future publishing profile wants Keeper utility over strict visible-source
faithfulness, add this item as an explicitly marked recovered-content note; do
not silently merge it into body text.

### Follow-up Checkpoint: HTML/Keeper/PDF Rebuild

Status: completed.

Owner: orchestrator.

Changes:

- rebuilt the current Innsmouth source-to-artifacts run after the page `031`
  occluded text-layer policy;
- fixed production PDF temp directory creation to avoid inaccessible
  `tempfile.mkdtemp` directories on this Windows station;
- fixed Innsmouth generated package config to pass `{source_html_uri}` to Edge
  print-to-PDF.

Evidence:

- full rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z`
  -> `status=pass`, `findings=0`;
- PDF report:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/production_pdf_report_two_column.json`
  -> `status=pass`, `action=built`, `canonical_replaced=true`,
  `findings=0`;
- PDF reader check: `32` pages.

Artifacts:

- `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook.md`;
- `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/The_Innsmouth_Terror_Full_RU.html`;
- `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf`.

### Follow-up Checkpoint: Heading-Prefix Duplicate Repair

Status: completed.

Owner: orchestrator.

Changes:

- added universal KeeperBook cleanup for first-paragraph heading-prefix echoes;
- added `heading_prefix_duplicates` to Keeper heading QA;
- rebuilt KeeperBook and HTML through the source-to-artifacts run.

Evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `26 passed`;
- current KeeperBook scan -> `heading_prefix_issues=0`;
- `Эпический финал Наконец` and `Универсальный магазин - известная` are absent
  from current KeeperBook;
- current HTML and Keeper timestamps were updated after the repair.

PDF completion:

- after the file lock was released, `build-production-pdf --variant two_column`
  was rerun successfully;
- `production_pdf_report_two_column.json` -> `status=pass`,
  `action=built`, `canonical_replaced=true`, `findings=0`;
- canonical PDF was replaced successfully.

### Follow-up Checkpoint: MVR Class B1 Vehicle Block Projection

Status: completed.

Owner: orchestrator.

Changes:

- promoted the `MVR Class B1 'Olmstead'` train prose block from ordinary body
  text into a structured vehicle/stat-object table;
- kept the vehicle title as bold text rather than a Markdown heading, so source
  TOC and heading-spine counts are not changed;
- added structural QA coverage for the vehicle block.

Evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `27 passed`;
- translator regression:
  `python -m pytest translator/tests/test_p0_contracts.py`
  -> `21 passed`, `1 skipped` when run outside sandbox temp-write limits;
- full rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z`
  -> `status=pass`, `findings=0`;
- PDF report:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/production_pdf_report_two_column.json`
  -> `status=pass`, `action=built`, `canonical_replaced=true`,
  `findings=0`.

### Follow-up Checkpoint: Keeper Note Callout Completeness

Status: completed.

Owner: orchestrator.

Changes:

- expanded Keeper note detection to include `Примечание/Заметка для Хранителя`;
- made `split_keeper_note` split multiple note markers from one paragraph into
  separate callouts;
- upgraded structural QA from a low minimum to exact source-note vs callout
  count matching.

Evidence:

- accepted EN source has `14` `Keeper note:` blocks;
- RU master has `14` Russian Keeper-note labels;
- KeeperBook has `14` `callout-class: keeper-note` blocks;
- HTML has `14` `review-callout keeper-note` blocks;
- PDF text extraction finds `14` `Примечание Хранителю` occurrences;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `29 passed`;
- production HTML/PDF were rebuilt and PDF report is `status=pass`,
  `action=built`, `canonical_replaced=true`, `findings=0`.

### Follow-up Checkpoint: Printed Page-Number Residue Cleanup

Status: completed for the residue defect; separate PDF layout QA finding
remains open.

Owner: orchestrator.

Changes:

- added source-layer cleanup for standalone old printed page numbers outside
  the source `Содержание` page;
- added KeeperBook downstream cleanup using the same `source-page - 4` rule;
- added Keeper structural QA blocker `printed_page_number_residue`;
- added regression tests for source cleanup and Keeper cleanup/QA.

Evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `31 passed`;
- KeeperBook rebuild:
  `status=pass`, `printed_page_number_residues=[]`;
- statblock projection:
  `status=pass`, `expected=22`, `projected=22`, `findings=0`;
- HTML rebuild:
  `status=pass`, `pages=45`, `headings=61`, `images=34`, `findings=0`;
- PDF rebuild:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- standalone old page-number residue scan:
  Keeper `0`, HTML `0`, PDF text extraction `0`.

Open follow-up:

- `pdf-print-qa` currently blocks on
  `page_flow_columns_missing_statblock_section_break`; handle this as a
  separate layout-policy task.

### Follow-up Checkpoint: Character Heading Tail Residue Cleanup

Status: completed.

Owner: orchestrator.

Changes:

- fixed inline character-heading splitting so metadata tails no longer keep a
  leading separator after the name is promoted to a heading;
- applied the same cleanup in the mapped character-heading fallback path;
- added `heading_tail_residues` to Keeper heading QA;
- added tests for both the cleanup and the QA blocker.

Count:

- found before repair: `3` cases;
- fixed after rebuild: `3`;
- affected headings: `Genevieve ‘Ginny’ Dubois`, `Anna Díaz`,
  `Christopher McGuire`.

Evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `33 passed`;
- KeeperBook rebuild:
  `status=pass`, `pages=45`, `headings=62`;
- statblock projection:
  `status=pass`, `expected=22`, `projected=22`, `findings=0`;
- HTML rebuild:
  `status=pass`, `pages=45`, `headings=61`, `images=34`, `findings=0`;
- PDF rebuild:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- heading-tail residue scan:
  Keeper `0`, HTML `0`, PDF text extraction `0`;
- Keeper `heading_qa`:
  `status=pass`, `heading_tail_residues=0`,
  `heading_prefix_duplicates=0`, `wrong_page_headings=0`.

### Follow-up Checkpoint: Source-Anchor Art Downstream Integration

Status: completed.

Owner: orchestrator.

Changes:

- RU Keeper assembly now consumes `art_anchor_manifest.json` via
  `--source-art-anchor-manifest`;
- reader art blocks now preserve source-anchor metadata in generated Markdown;
- character/source-anchor text can retarget art to the matching RU heading slug;
- same-heading/page art insertion is sorted by source anchor line order;
- production HTML rendering now accepts extended generated `keeper-art-block`
  divs and no longer escapes them as text;
- production art layout can use `source_anchor_manifest` as the canonical
  reader-art manifest.

Evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `37 passed`;
- KeeperBook rebuild:
  `status=pass`, `reader_art_blocks.source_anchor_manifest_used=true`,
  `placements=34`, `inserted=34`;
- HTML rebuild:
  `status=pass`, `images=34`, `findings=0`,
  escaped keeper-art-block count `0`;
- statblock cleanup/readiness:
  `cards=22`, `structured=22`, `flattened=0`;
- PDF rebuild:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- visual smoke render:
  pages `008`, `009`, `010` show source-anchor art near the intended
  character/section positions.
## 2026-08-04 - TOC Expansion Checkpoint

Status: completed.

- Owner: orchestrator.
- Scope: preserved source-style `Содержание` for Innsmouth run
  `20260730T210831Z`.
- Change: expanded `toc_policy.source_entries` from 45 plain rows to 59
  structured `{title, level, href}` rows based on current accepted HTML heading
  spine, excluding service `Авторы и участники`.
- Pipeline repair: `translator.py` now honors explicit `href` in accepted
  source TOC entries, preventing duplicate-title headings from linking to the
  wrong section.
- Generator repair: `build_innsmouth_source_to_artifacts.py` now emits the same
  structured TOC entries for future package regeneration.
- Verification:
  - syntax check via `ast.parse` for `translator.py` and
    `build_innsmouth_source_to_artifacts.py`;
  - production HTML rebuilt with `status=pass`, `findings=0`;
  - statblock HTML postprocess/readiness pass, `cards=22`;
  - TOC audit: `toc_items=59`, `toc_links=59`, `unresolved=0`,
    `missing_href_count=0`;
  - PDF rebuilt with `status=pass`, `action=built`, `findings=0`.

## 2026-08-04 - Handout 2 Wrong Art Suppression

Status: completed.

Owner: orchestrator.

Scope:

- `Раздаточный материал 2: записка`;
- reader-art publication policy for page `044` service/backmatter assets;
- run `20260730T210831Z` KeeperBook/HTML/PDF artifacts.

Change:

- removed the old `xref-01397 -> razdatochnyi-material-2-zapiska` anchor
  override;
- added `xref-01397` to Innsmouth reader-art suppression;
- made reader-art publication policy persist to both base `art_manifest.json`
  and source-anchor `art_anchor_manifest.json`.

DoD / Evidence:

- reader-art regression tests pass: `3 passed`;
- KeeperBook rebuilt: `status=pass`, `pages=45`, `headings=63`;
- statblock projection/readiness remains pass: `22/22`;
- production HTML rebuilt: `status=pass`, `images=33`, `findings=0`;
- production PDF rebuilt: `status=pass`, `action=built`, `findings=0`;
- KeeperBook and HTML no longer contain `xref-01397`,
  `innsmouth-page-044-xref-01397-handout.png`, or `GOLD WINNER`;
- both art manifests mark `xref-01397` as
  `emit_reader_art_block=false` and `reader_publication_suppressed=true`.

## 2026-08-08 - User TODO / Systemic Pipeline Remediation Package

Status: active.

Owner: orchestrator.

Scope:

- the user supplied a 0-19 TODO list covering cross-reference links, table and
  handout labels, broken name lines, duplicate heading/body residues, repeated
  or unsupported `Innsmouth` text, misplaced art, list/body gluing, suspected
  column-order failures, and unresolved source-art anchors;
- UI-visible subagents are unavailable in the current tool surface, so this
  checkpoint uses internal role reviews instead of claiming created agents.

Artifacts:

- `pipeline_todo_20260808.md`;
- `handoffs/sol_pipeline_systemic_todo_review_20260808.md`;
- `handoffs/terra_pipeline_control_review_20260808.md`.

Merged decision:

- treat the list as systemic pipeline debt, not as individual PDF-page fixes;
- create audit-only controls first, then repair the earliest failing layer;
- keep semantic art anchoring as an upstream blocker until each publishable art
  item has source evidence and target section evidence;
- do not accept downstream HTML/PDF `pass` as release readiness while
  `full_run_report.json` still reports upstream blockers.
