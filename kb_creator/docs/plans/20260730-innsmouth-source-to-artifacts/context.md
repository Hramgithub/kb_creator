# Innsmouth Source PDF to Artifacts Context

Generated: 2026-07-30

## User Correction

The previous `kb_creator` candidate repeated part of the earlier success: it
rebuilt HTML/PDF from the accepted v6 Keeper/publishing chain. That was useful
as reproducibility evidence, but it was not a true source-PDF-to-artifacts run.

The current task is stricter:

1. Start from the original PDF.
2. Process it through `kb_creator`.
3. Produce KeeperBook, HTML, and PDF.
4. Compare the generated KeeperBook and PDF against external reference
   artifacts from Yandex Disk.
5. If the current `kb_creator` scripts are insufficient, port or implement the
   missing reusable stages.

## Important Boundary

The user deleted the old Innsmouth scenario `Working` and `Output` folders from
the NRI tree. This is intentional and prevents accidental success by reusing
old local artifacts.

Reference artifacts on Yandex Disk are comparison targets, not source inputs for
generation.

## Verified Inputs

Source PDF exists:

`D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/english/7th Edition Call of Cthulhu/Adventures/1923_The Innsmouth Terror/The Innsmouth terror.pdf`

SHA-256:

`CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F`

Reference KeeperBook exists:

`D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/1_Сценарии/Компания/1928 Побег из Инсмута/Террор в инсмуте/For_Keeper/KeeperBook_v6.md`

SHA-256:

`E1C889ADB5676798D7E296E4231040FA730029A7BA40AD515BF97059F5F78BA7`

Reference PDF exists:

`D:/яндекс/Yandex.Disk/НРИ/1_Зов Ктулху/1_Сценарии/Компания/1928 Побег из Инсмута/Террор в инсмуте/Pdf/The_Innsmouth_Terror_RU.pdf`

SHA-256:

`D89BA390B296211692419D08F8E8F84CB0D393B54E94489531542BB5A0E08FC5`

## Current Knowledge

The committed `kb_creator` scripts are useful but not yet sufficient:

- `build_innsmouth_full_dry_run.py` proves PDF/source reconstruction through
  accepted EN, but it still compares against historical accepted raw/cleaned v6
  text and then calls the v7 publishing rebuild.
- `build_innsmouth_v7_rebuild.py` rebuilds publishing from the frozen v6 package
  and therefore depends on `KeeperBook_v6.md`.
- `build_innsmouth_final_result.py` promotes the rebuilt HTML/PDF and proves
  freshness/no-KB-write/visual evidence, but it still starts from the v6-derived
  publishing rebuild.

Therefore the missing universal work is not PDF rendering itself. The missing
parts are:

- a `kb_creator`-owned source reconstruction contract that does not require
  old scenario folders;
- a `kb_creator`-owned translation/proofread/accepted-RU path;
- a `kb_creator`-owned KeeperBook assembly stage;
- HTML/PDF publishing that consumes the newly generated KeeperBook;
- comparison gates against external references.

## Next Action

Audit the current scripts and the old `translator` implementation to identify
the minimum reusable stages to port into `kb_creator` for this scenario.

## 2026-07-30 Source-Side Pipeline Update

Fresh clean-room run:

`kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/full_run_report.json`

Status:

`blocked`, but now at the expected artifact comparison stage.

Important correction:

The first kb_creator source runs used column OCR as the translation source. That
repeated a known failure mode: OCR can include visual noise and damaged
line/column artifacts. The current runner now treats the embedded PDF text layer
as the primary source:

- primary source: `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md`;
- OCR source: retained as audit/fallback evidence only;
- translation tasks: 53 units, 113967 source characters;
- translation payload QA: pass, 0 findings;
- image inventory: 81 extracted candidates, 61 pending role approval;
- current blocker: generated artifacts differ from the external Yandex
  references.

Current generated artifacts:

- RU master:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Formatted/The_Innsmouth_Terror_Source_Text_Full_RU.md`;
- KeeperBook:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook.md`;
- HTML:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/The_Innsmouth_Terror_Full_RU.html`;
- PDF:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf`;
- comparison report:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/artifact_comparison_report.json`.

Full-run proof:

- `build_innsmouth_source_to_artifacts.py --run-id 20260730T210831Z`
  starts from the source PDF, rebuilds KeeperBook, HTML, PDF, and writes the
  comparison report;
- final full-run findings: `statblock_readiness_blocked` and
  `artifact_comparison_different`;
- PDF build itself passes under elevated execution when Windows denies access
  to `Temp/Production_PDF`.

Comparison summary:

- Keeper candidate: `131054` chars, `46` source pages, `63` headings;
- reference Keeper: `121799` chars, `45` source pages, `62` headings;
- generated HTML: `46` source pages, `62` headings, `61` image refs,
  `0` missing image refs, `0` statblock cards;
- generated PDF: `33` pages, reference PDF: `32` pages;
- generated PDF text chars: `114666`, reference PDF text chars: `113519`.

Interpretation:

The source-to-artifacts chain is now script-backed and produces KeeperBook, HTML,
and PDF from the original PDF. Image integration is also active: the current
candidate includes `61` image references with `0` missing image refs. It is not
yet equivalent to the manual v6 reference.

Statblock readiness update:

`kb_creator/scripts/audit_innsmouth_statblock_readiness.py` is now part of the
full runner after HTML generation. It blocks the current candidate with:

- `statblock_cards`: `0`;
- `structured_statblocks`: `0`;
- HTML tables: `2`;
- flattened statblock-like paragraphs: `21`;
- report:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/statblock_readiness_report.json`.

The old v6 HTML projection script was probed against the current clean-room
HTML and could not project any cards (`expected=22`, `projected=0`) because the
current source-derived surface no longer exposes the old unique statblock start
markers. Therefore the next reusable parity work is not merely "run the old
postprocess script"; it is to repair or reconstruct the statblock structure
before final source TOC/frontmatter, image selection, and placement tuning.

Translation execution note:

The first translation delegation wave showed that 13k-15k source-character
batches are too large for bounded `gpt-5.4` executor agents in this workflow:
multiple agents stopped with `budget_limited` before writing output. The working
limit for translation sub-batches is now fixed at about `3000` source
characters. Larger prepared batches must be split before delegation.

Verification update:

`kb_creator/scripts/prepare_translation_batches.py` now uses `3000` as the
default `--max-batch-chars` and splits any single source unit that exceeds that
limit into `__partNN` translation parts. `merge_translation_batches.py` then
reassembles those parts back into their original `unit_id`, preserving the
source hash contract. The source-to-artifacts runner now creates the primary
translation handoff directory at `Translation_Work/RU_Batches_3000`; the older
`Translation_Work/RU_Batches` directory is legacy evidence from the first
large-batch delegation wave and must not be used for new translation work.

Evidence:

```powershell
python kb_creator/scripts/prepare_translation_batches.py --tasks-json kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/translation_tasks.json --out-dir kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000 --max-batch-chars 3000
python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py
```

Result:

- original translation units: `60`;
- translation parts after splitting: `60`;
- split source units: `0`;
- generated primary batches: `54`;
- maximum batch size: `2998`;
- batches over `3000`: `0`;
- tests: `4 passed`.

The reference KeeperBook and reference PDF on Yandex Disk remain comparison
targets only. They must not be used as inputs for generating the new RU master,
KeeperBook, HTML, or PDF.

## 2026-07-30 Probe Result

Command:

```powershell
python kb_creator/scripts/build_innsmouth_full_dry_run.py --skip-publishing --report-dir kb_creator/reports/innsmouth_source_to_artifacts/probe_current_dependency
```

Result:

`blocked`.

The script fails before source reconstruction because it tries to read the
deleted historical scenario config:

`CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/the_innsmouth_terror.recovery_v6_cleaned.package.json`

Conclusion:

The existing `kb_creator` runner is not yet a true source-PDF-to-artifacts
pipeline. The first missing reusable piece is a `kb_creator`-owned clean-room
package/config generator for this scenario. After that, the script must stop
depending on historical accepted EN/Keeper artifacts and either generate or
explicitly block each missing stage.

## 2026-07-31 Checkpoint

The user hint about translation batch size is now fixed as a project invariant
for this run: practical translation handoff units must stay around `3000`
source characters. Current evidence:

- `kb_creator/scripts/build_innsmouth_source_to_artifacts.py` sets
  `translation.max_unit_chars = 3000`;
- `kb_creator/scripts/prepare_translation_batches.py` defaults to `3000`;
- current manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest counts: `54` batches, maximum batch size `2998`, `0` batches over
  `3000`;
- test evidence: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed` with only the known `.pytest_cache` access warning.

Statblock remediation is now implemented in the reusable clean-room chain:

- `kb_creator/scripts/project_innsmouth_statblocks_from_ru.py` projects
  `22/22` Innsmouth statblock cards from the current RU master into
  KeeperBook;
- the projection also retargets NPC art manifest anchors from removed
  `page-036/037/039/040` anchors to concrete statblock headings:
  `hugo-shrimpy-hargreaves`, `patty-gillian`, `tiffany-quispe`,
  `margaret-maggie-myers`;
- `kb_creator/scripts/unescape_projected_statblock_html.py` converts escaped
  projected statblock HTML back into real HTML after the production renderer;
- `kb_creator/scripts/audit_innsmouth_statblock_readiness.py` reports
  `expected=22`, `cards=22`, `structured=176`, `flattened=0`.

Publishing evidence:

- KeeperBook:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook.md`;
- HTML:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/The_Innsmouth_Terror_Full_RU.html`;
- PDF:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf`;
- HTML stage: `status=pass`, `images=61`, `findings=0`;
- PDF stage was rerun with explicit permission because sandboxed writes to
  `Temp/Production_PDF` hit `Permission denied`; current PDF report is
  `status=pass`, `action=built`, `findings=0`.

Remaining blocker:

`artifact_comparison_different`.

Fresh comparison against the Yandex reference artifacts:

- Keeper candidate normalized chars `139980` vs reference `111831`;
- Keeper candidate source-page markers `38` vs reference `45`;
- Keeper candidate headings `78` vs reference `62`;
- PDF candidate pages `34` vs reference `32`;
- PDF text chars `120163` vs reference `113519`.

Interpretation:

The pipeline now proves a fresh source-PDF -> RU master -> KeeperBook -> HTML
-> PDF chain with images and statblock cards. It is still not parity-equivalent
to the Yandex reference. Next work should focus on source/projection parity:
page coverage, text-volume drift, frontmatter/TOC behavior, heading policy, and
layout/image projection rules. The Yandex Keeper/PDF remain comparison targets
only and must not become generation inputs.

## 2026-07-31 Checkpoint 2

The user hint about the practical translation limit was rechecked against live
code, tests, and the current manifest. The active contract is still `3000`
characters:

- `build_innsmouth_source_to_artifacts.py` writes
  `translation.max_unit_chars = 3000`;
- `prepare_translation_batches.py` defaults to `3000`;
- `test_innsmouth_source_to_artifacts.py` asserts the config, directory, and
  generated unit limit;
- current manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest counts: `54` batches, `60` original units, `60` translation parts,
  maximum batch size `2998`, `0` batches over `3000`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, only the known `.pytest_cache` access warning.

Service/backmatter remediation was narrowed and verified:

- the first attempted text regex was too broad and was stopped before HTML/PDF
  propagation by Keeper QA (`pages=5`, `headings=2`);
- the final rule suppresses service/ad text only inside configured source-page
  blocks, currently page `044`, preserving page markers and art anchors;
- Keeper rebuild: `status=pass`, `pages=46`, `headings=63` before statblock
  projection;
- statblock projection: `status=pass`, `22/22`, `findings=0`;
- production HTML: `status=pass`, `pages=46`, `headings=77`, `images=61`,
  `findings=0`;
- statblock HTML QA: `22` cards, `176` structured sections, `0` escaped or
  flattened findings;
- PDF rebuilt with explicit permission because of the known
  `Temp/Production_PDF` sandbox boundary: `status=pass`, `variant=two_column`,
  `findings=0`.

Fresh comparison remains blocked on `artifact_comparison_different`, but the
delta is smaller and more specific:

- Keeper normalized chars `120741` vs reference `111831`;
- Keeper source-page markers `46` vs reference `45`;
- Keeper headings `78` vs reference `62`;
- PDF pages `33` vs reference `32`;
- PDF text chars `119331` vs reference `113519`;
- comparison findings are empty for PDF extraction; the difference is content
  and projection structure, not a missing PDF artifact.

Next reusable gap: add a structure-aware/reader-text comparison mode and then
separate true source drift from intentional structural projections such as
statblock cards and additional approved art blocks.

## 2026-07-31 Checkpoint 3

Structure-aware comparison was added to
`kb_creator/scripts/compare_innsmouth_artifacts.py`.

What changed:

- strict Keeper comparison remains unchanged and still reports `different`;
- report now also records reader-text normalization, reader-text ignoring
  statblock scaffold, structure counts, page coverage, missing/extra
  reader-text pages, art/trace-only pages, and top page deltas;
- `source-page-044` is now correctly classified as
  `extra_art_or_trace_only` after configured service-page text suppression.

Rebuild evidence:

- `python -m py_compile kb_creator/scripts/build_keeperbook_from_ru_master.py kb_creator/scripts/compare_innsmouth_artifacts.py`
  -> pass;
- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, known `.pytest_cache` warning only;
- Keeper build -> `status=pass`, `pages=46`, `headings=63`;
- statblock projection -> `status=pass`, `22/22`, `findings=0`;
- production HTML -> `status=pass`, `pages=46`, `headings=77`,
  `images=61`, `findings=0`;
- statblock HTML QA -> `22` cards, `176` structured sections, `0`
  escaped/flattened findings;
- production PDF -> `status=pass`, `variant=two_column`, `findings=0`;
- artifact comparison -> `status=different`.

Fresh comparison:

- strict normalized Keeper delta: `+8755` chars;
- reader-text delta: `+8703` chars;
- reader-text delta ignoring statblock scaffold: `+6720` chars;
- missing reader-text pages: none;
- extra reader-text pages: none;
- extra art/trace-only pages: `044`;
- top page deltas: `011 +1836`, `010 -1680`, `017 +1262`,
  `035 +945`, `016 -712`, `033 +668`, `034 +617`, `020 +473`;
- PDF remains `33` pages vs reference `32`, text chars `119176` vs
  `113519`.

Interpretation:

The current blocker is no longer hidden service text, missing art, flattened
statblocks, or missing publication artifacts. The next repair target is
page-level text parity, starting with pages `010`, `011`, `016`, `017`, `020`,
and statblock pages `033-035`.

## 2026-07-31 Checkpoint 4

The user-provided practical translation limit remains fixed and verified:

- active limit: about `3000` source characters per translation handoff batch;
- current manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest evidence: `54` batches, `60` original units, `60` translation
  parts, maximum batch size `2998`, `0` batches over `3000`;
- test evidence: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Boundary repairs were added to the reusable Keeper assembly script:

- page `010/011` section boundary: `### Второстепенные NPC` is moved before
  `source-page-011`;
- page `016/017` section boundary: `### Съёмочный железнодорожный вагон` is
  moved before `source-page-017`;
- page `018`: true inline headings `### Вокруг поезда` and
  `### Bazzledon’s Office` are promoted only in their confirmed page/context,
  avoiding false heading splits from phrases such as "ведет в кабинет";
- page `028/029` section boundary: `### Вход через пещеры` is moved before
  `source-page-029`.
- page `019/020` body repair: the true `### Ginny’s Trailer` section starts
  on page `019`, the handout body is removed from reader body, and the false
  navigation-derived `Ginny’s Trailer` block before `### McGuire’s Lab` is
  removed.

Fresh rebuild evidence after those repairs:

- Keeper build: `status=pass`, `pages=46`, `headings=63`;
- statblock projection: `status=pass`, `22/22`, `findings=0`;
- production HTML: `status=pass`, `pages=46`, `headings=77`, `images=61`,
  `findings=0`;
- statblock HTML QA: `22` cards, `176` structured sections, `0` escaped or
  flattened findings;
- production PDF: rerun with explicit permission because of the known
  `Temp/Production_PDF` Windows boundary; final status `pass`,
  `variant=two_column`, `findings=0`;
- artifact comparison remains `status=different`.

Fresh comparison:

- Keeper normalized chars after full statblock-projected rebuild: candidate
  `119976`, reference `111831`, delta `+8145`;
- reader-text delta ignoring basic statblock scaffold: `+6110`;
- missing reader-text pages: none;
- extra reader-text pages: none;
- extra art/trace-only pages: `044`;
- PDF page count now matches the reference: `32` vs `32`;
- PDF text chars remain different: `118603` vs `113519`;
- top remaining page deltas after full projection: `035 +945`, `033 +668`,
  `034 +617`, `016 +350`, `037 +308`, `038 +304`, `043 +290`,
  `039 +268`, `028 +252`, `036 +251`, `021 +236`, `026 +229`;
- pre-projection/local body check showed the `019/020` drift reduced to
  `019 +123` and `020 +99`, so those pages are no longer the largest
  reader-order problem.

Interpretation:

The largest reader-order/page-boundary failures have been removed. The current
blocker is still `artifact_comparison_different`, but the remaining work is now
more specific: distinguish intentional statblock-card projection drift from
true content drift on `033-039`, then handle localized residual pages `016`,
`043`, `028`, `021`, and `026`. The Yandex references remain comparison
targets only and must not become generation inputs.

## 2026-07-31 Checkpoint 5

The comparison layer now has a statblock-aware mode in
`kb_creator/scripts/compare_innsmouth_artifacts.py`.

What changed:

- strict Keeper comparison remains unchanged and still reports `different`;
- `reader_text_ignoring_statblock_scaffold` now removes table headings,
  numeric index cells, label cells, and empty source placeholders such as
  "Заклинания не выделены в источнике";
- the report now separates `statblock_delta_chars` from
  `non_statblock_delta_chars`, so statblock-card formatting drift no longer
  hides ordinary text drift.

Fresh evidence after rebuilding KeeperBook, statblock projection, HTML, and PDF:

- Keeper build: `status=pass`, `pages=46`, `headings=63`;
- statblock projection: `status=pass`, `22/22`, `findings=0`;
- production HTML: `status=pass`, `pages=46`, `headings=77`, `images=61`,
  `findings=0`;
- statblock HTML QA: `22` cards, `176` structured sections, `0` escaped or
  flattened findings;
- production PDF: rerun with explicit permission because of the known
  `Temp/Production_PDF` Windows boundary; final status `pass`,
  `variant=two_column`, `findings=0`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Additional source repair:

- page `043` had a real duplicated Handout #2 body:
  one normal handout body and one duplicate "обычный текст" body;
- the duplicate is now removed in `cleanup_confirmed_page_residuals`, and the
  leading "Раздаточные материалы" label is stripped from that handout body.

Fresh comparison after this repair:

- strict normalized Keeper delta: `+7857` chars;
- reader-text delta: `+7805` chars;
- reader-text delta ignoring statblock scaffold: `+2364` chars;
- statblock-aware split: `non_statblock_delta_chars=2324`,
  `statblock_delta_chars=40`;
- PDF page count remains matched: `32` vs `32`;
- PDF text chars: `118315` vs `113519`;
- top non-statblock deltas: page `016 +350`, `028 +252`, `021 +236`,
  `026 +229`, `017 +200`, `012 +174`, `006 -164`, `027 +139`.

Interpretation:

The remaining `033-040` statblock-page drift is now proven to be mostly
projection form rather than missing card structure: after canonical statblock
normalization the total statblock page delta is only `+40` chars. The next real
blocker is ordinary reader-text parity. Page `016` was checked against the
reference and is not a section-boundary failure; both candidate and reference
place "Съёмочный железнодорожный вагон" on source page `016`. Its remaining
delta is translation/proofread wording drift. The next stage should therefore
target RU preservation/proofread parity, not another layout repair.

## 2026-07-31 Checkpoint 6

User hint accepted and verified: the practical translation handoff limit is
about `3000` source characters per batch.

Live evidence:

- `build_innsmouth_source_to_artifacts.py` writes
  `translation.max_unit_chars = 3000`;
- `prepare_translation_batches.py` defaults to `3000`;
- primary handoff manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest counts: `54` batches, `60` units, `60` original units,
  `0` split units, maximum batch size `2998`, `0` batches over `3000`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Additional reproducible repair work:

- added `kb_creator/scripts/dump_innsmouth_page_deltas.py` for page-scoped
  candidate/reference diagnostics without using the reference as generation
  input;
- added deterministic CoC term cleanup in
  `build_keeperbook_from_ru_master.py` for common mechanics/proofread residue;
- added confirmed intra-page order repairs for pages `021` and `028`.

Fresh comparison after these repairs:

- strict/current artifact comparison still reports `different`;
- reader-text delta: `+7667` chars;
- reader-text delta ignoring statblock scaffold: `+2226` chars;
- statblock-aware split: `non_statblock_delta_chars=2186`,
  `statblock_delta_chars=40`;
- PDF page count still matches the reference: `32` vs `32`;
- PDF comparison has no structural findings;
- top remaining non-statblock text deltas: page `016 +280`, `026 +238`,
  `028 +234`, `021 +200`, `012 +178`, `006 -156`, `017 +152`,
  `027 +142`, `018 -132`, `031 +127`.

Interpretation:

The `3000` batch limit is now a verified invariant, not the cause of current
drift. The remaining blocker is ordinary RU preservation/proofread parity and
localized intra-page/source wording drift. The next remediation should continue
from the page-delta evidence rather than changing OCR or PDF publication
stages.

## 2026-07-31 Checkpoint 7

Additional page-order repairs were applied to the reproducible Keeper assembly
pipeline, not to the generated KeeperBook by hand.

Changed pipeline logic:

- page `012`: move the Orne Library research continuation before
  `### Аркхэмский вестник`; split the Karen-specific Keeper note into a
  separate keeper-note callout;
- page `026`: move the `В Иннсмут` section introduction before
  `### Универсальный магазин`;
- page `028`: move the Esoteric Order of Dagon hook paragraph before the
  building/cave body.

Rebuild evidence:

- `build_keeperbook_from_ru_master.py`: `py_compile` pass;
- KeeperBook assembly: `status=pass`, `pages=46`, `headings=63`;
- Keeper structure QA: `pass`;
- heading QA: `pass`;
- page reference QA: `pass`;
- statblock projection: `22/22`, `findings=0`;
- production HTML: `status=pass`, `pages=46`, `headings=77`, `images=61`,
  `findings=0`;
- statblock HTML cleanup/readiness: `22` cards, `176` structured sections,
  `0` flattened/escaped findings;
- production PDF: rebuilt with the known escalated Windows temp-boundary
  permission, `status=pass`, `variant=two_column`, `findings=0`,
  `sha256=6faca553bbd61cb0bcaa3591ff5968bfc24b08de09ef355b02536d1e5a638fdb`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Fresh comparison after this repair wave:

- comparison status remains `different`;
- reader-text delta: `+7573` chars;
- reader-text delta ignoring statblock scaffold: `+2132` chars;
- statblock-aware split: `non_statblock_delta_chars=2092`,
  `statblock_delta_chars=40`;
- PDF page count remains matched: `32` vs `32`;
- PDF structural findings: none;
- top non-statblock deltas: page `016 +280`, `028 +206`, `021 +200`,
  `026 +196`, `006 -156`, `012 +154`, `017 +152`, `027 +142`.

Interpretation:

The repaired pages improved but did not close the blocker. The remaining
largest gap is now page `016`, which is mostly RU wording/proofread drift and
small residual labels rather than a proven page-boundary failure. Continue with
page-scoped preservation/proofread parity, while preserving the verified
`3000` translation batch invariant.

## 2026-07-31 Checkpoint 8

User hint rechecked and fixed as the active translation handoff invariant:
translation batches for this workflow must stay at about `3000` source
characters.

Live evidence:

- active manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest field: `max_batch_chars=3000`;
- manifest counts: `54` batches;
- maximum observed batch size: `2998`;
- batches over `3000`: `0`;
- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Interpretation:

The translation-size limit is confirmed and should not be changed while fixing
the current artifact drift. Remaining work stays focused on page-scoped
preservation/proofread parity and reproducible assembly repairs.

## 2026-07-31 Checkpoint 9

Applied two reproducible Keeper assembly cleanup fixes:

- remove standalone source running/header residue `Innsmouth` after
  `<!-- source-page-016 -->` when it appears immediately before the next
  Markdown heading;
- re-run CoC term/spacing cleanup after confirmed intra-page order repairs, so
  repair-generated glued strings are normalized too.

Confirmed glued string cleanups:

- `Во времяпервоначального` -> `Во время первоначального`;
- `Рано или поздносыщики` -> `Рано или поздно сыщики`;
- `Разговорс Sammy` -> `Разговор с Sammy`.

Rebuild evidence:

- KeeperBook assembly: `status=pass`, `pages=46`, `headings=63`;
- statblock projection: `22/22`, `findings=0`;
- production HTML: `status=pass`, `pages=46`, `headings=77`, `images=61`,
  `findings=0`;
- statblock HTML cleanup/readiness: `22` cards, `176` structured sections,
  `0` flattened findings;
- production PDF: `status=pass`, `action=built`, `variant=two_column`,
  `findings=0`,
  `sha256=7bd91f1ecf3c411ff6b4d27286175d1055e3d765ad52fff4e9539a784959ed07`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Fresh comparison:

- status remains `different`;
- reader-text delta: `+7566` chars;
- reader-text delta ignoring statblock scaffold: `+2125` chars;
- statblock-aware split: `non_statblock_delta_chars=2092`,
  `statblock_delta_chars=40`;
- PDF page count remains matched: `32` vs `32`;
- PDF structural findings: none;
- top remaining non-statblock deltas: page `016 +277`, `021 +209`,
  `028 +207`, `026 +197`, `012 +154`, `006 -152`, `017 +152`, `027 +142`.

Interpretation:

The spacing cleanup slightly increases raw char delta because missing spaces are
now restored, but it improves reader quality and fixes a reproducible pipeline
defect. Remaining largest deltas are mostly RU proofread/style parity, with
possible smaller cleanup opportunities on pages `021`, `028`, and `026`.

## 2026-07-31 Checkpoint 10

User hint revalidated: the active translation batch ceiling for this run is
`3000` source characters.

Live verification:

- manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest field: `max_batch_chars=3000`;
- batches: `54`;
- units: `60`;
- original units: `60`;
- split units: `0`;
- maximum observed batch size: `2998`;
- batches over `3000`: `0`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` permission warning.

Conclusion:

The current artifact drift is not caused by oversized translation batches. Keep
the `3000` ceiling fixed while continuing page-scoped RU preservation/proofread
parity work.

## 2026-07-31 Checkpoint 11

The translation handoff ceiling remains fixed and verified at `3000` source
characters:

- manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- current manifest counts: `54` batches, `60` units, maximum batch size
  `2998`, `0` batches over `3000`;
- tests: `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `4 passed`, with only the known `.pytest_cache` warning.

Reader-art publication parity was repaired as a reproducible pipeline rule:

- `build_keeperbook_from_ru_master.py` now writes reader-art publication policy
  back to `art_manifest.json` so KeeperBook, HTML, and PDF consume the same
  placement set;
- page-anchor-only decorative/service/backmatter placements are suppressed from
  reader artifacts without deleting source assets;
- `xref-01397` is anchored to
  `razdatochnyi-material-2-zapiska` for Handout 2;
- `project_innsmouth_statblocks_from_ru.py` now reinjects NPC art blocks after
  statblock section replacement so pregen portraits are not lost;
- missing `xref-01200` for Ian Torres is recovered deterministically from
  source page render `page-38.png` using crop box `[790, 1080, 1425, 1850]`
  and added to the manifest/output asset set.

Fresh art evidence:

- KeeperBook art IDs: candidate `34`, reference `34`;
- extra art IDs: `0`;
- missing art IDs: `0`;
- production HTML: `status=pass`, `images=34`, `findings=0`;
- statblock HTML QA: `22` cards, `176` structured sections, `0` flattened or
  escaped findings;
- production PDF: `status=pass`, `variant=two_column`, `findings=0`,
  `sha256=fe7576eeb4ec6d00e72e3324e40cb7a45683851bc988495a407bc1afca11cab5`.

Fresh comparison remains blocked on `artifact_comparison_different`:

- reader-text delta: `+7480` chars;
- reader-text delta ignoring statblock scaffold: `+2039` chars;
- statblock-aware split: `non_statblock_delta_chars=2006`,
  `statblock_delta_chars=40`;
- PDF pages: candidate `27`, reference `32`;
- PDF structural findings: none.

Interpretation:

The image integration blocker is now closed for the reference art set. The next
open gaps are ordinary RU preservation/proofread parity and PDF layout density,
not missing/extra reader art or statblock flattening.

## 2026-07-31 Checkpoint 12

Fixed one confirmed reader-order/projection defect on source page `018`.

Root cause:

- RU master already contained the full train-room sentence and Bazzledon office
  investigation bullets;
- Keeper projection promoted an in-sentence trailer/lab reference as if it were
  a section boundary and left the final Bazzledon office investigation bullets
  before `### Вокруг поезда`;
- the previous repair depended on an exact Fat Tony sentence variant and stopped
  matching after character-name / term normalization.

Pipeline fix:

- added `_repair_page_018_order()` in
  `kb_creator/scripts/build_keeperbook_from_ru_master.py`;
- the repair restores the full train-room sentence:
  `Bazzledon’s Office -> Ginny’s Trailer -> McGuire’s Lab`;
- it moves the leading investigation bullets into `### Bazzledon’s Office`
  before the screenplay/correspondence bullets;
- added regression coverage in
  `kb_creator/tests/test_innsmouth_source_to_artifacts.py`.

Verification:

- `python -m py_compile kb_creator/scripts/build_keeperbook_from_ru_master.py
  kb_creator/scripts/build_innsmouth_source_to_artifacts.py
  kb_creator/scripts/project_innsmouth_statblocks_from_ru.py` -> pass;
- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `5 passed`, with only the known `.pytest_cache` permission warning;
- full run rebuilt source/PDF page renders, text layer, column OCR candidate,
  image approval, art manifest, KeeperBook, statblock projection, production
  HTML, statblock HTML cleanup/readiness, then stopped on the usual sandbox PDF
  replace gate;
- two-column PDF was rebuilt through the same pipeline with escalated execution:
  `status=pass action=built variant=two_column findings=0`;
- fresh PDF SHA:
  `15b538122e03805fac2464a0a1874c0c730108b712d135dfc55eb5cd0ec0fb67`.

Current comparison remains `different`:

- `reader_text.delta_chars=7838`;
- `reader_text_ignoring_statblock_scaffold.delta_chars=2397`;
- `non_statblock_delta_chars=2364`;
- `statblock_delta_chars=40`;
- PDF pages: candidate `27`, reference `32`;
- current largest non-statblock deltas:
  `016 +277`, `018 +226`, `026 +197`, `028 +193`, `021 +191`,
  `012 +154`, `006 -152`, `017 +138`.

Interpretation:

The page `018` fix intentionally restores previously lost reader text, so raw
character delta increased while semantic preservation improved. Continue by
classifying remaining top deltas into true missing/reordered text versus
accepted translation/proofread style drift. Do not use raw delta alone as the
quality metric.
## 2026-07-31 Checkpoint 13

Rechecked the user hint after context compaction: translation work packets must
stay around `3000` source characters.

Live evidence:

- active manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest summary: `max_batch_chars=3000`, `54` batches, `60` units,
  `60` original units, `0` split units, maximum observed batch size `2998`,
  `0` batches over `3000`;
- code references still point to the same contract:
  `build_innsmouth_source_to_artifacts.py` sets
  `translation.max_unit_chars = 3000`, and
  `prepare_translation_batches.py` defaults to `3000`;
- regression verification:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `5 passed`, with only the known `.pytest_cache` permission warning.

Decision:

The `3000` limit is a verified invariant for the Innsmouth kb_creator dry-run.
Keep it fixed while classifying the remaining page deltas.

## 2026-07-31 Checkpoint 14

Applied and verified a small universal projection-residue cleanup pass.

Changed:

- `kb_creator/scripts/build_keeperbook_from_ru_master.py`;
- `kb_creator/tests/test_innsmouth_source_to_artifacts.py`.

Fixed classes:

- page `006`: removed artificial `### The Innsmouth Terror` reader heading and
  duplicated `Информация для Хранителя 2 ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ` preamble;
- page `012`: split the Orne Library research continuation out of the Loring
  bullet;
- page `017`: removed residual inline `Расследование` before `Díaz`;
- page `027`: removed residual English running heading `The Fire Station`.

Evidence:

- `python -m py_compile kb_creator/scripts/build_keeperbook_from_ru_master.py
  kb_creator/scripts/build_innsmouth_source_to_artifacts.py
  kb_creator/scripts/project_innsmouth_statblocks_from_ru.py` -> pass;
- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `7 passed`, with only the known `.pytest_cache` permission warning;
- Keeper assembly:
  `status=pass`, `headings=62`, `heading_qa=pass`, `structural_qa=pass`;
- production HTML:
  `status=pass`;
- production PDF rebuilt with the same `build-production-pdf` pipeline step
  using escalated execution for the known `Temp/Production_PDF` sandbox
  boundary:
  `status=pass`, `variant=two_column`, `findings=0`,
  `sha256=3e40c0f16759fad087f7ef1c4a739b413ebad5b01e74a983e028201b07e9e52e`;
- fresh comparison:
  `reader_text.delta_chars=7761`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2324`,
  `non_statblock_delta_chars=2287`,
  `statblock_delta_chars=40`,
  PDF pages `27` candidate vs `32` reference.

Residual checks:

- no `### The Innsmouth Terror`;
- no `Информация для Хранителя 2`;
- no `ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ`;
- no `Расследование Díaz`;
- no `The Fire Station Пожарная часть`;
- no glued `если они понадобятся. Пользуясь библиотекой Орна`.

Classification report:

`kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/page_delta_classification_20260731.md`.

Next action:

Continue with page-scoped source/RU-master classification, not raw reference
wording matching. Top remaining ordinary-text pages are `016`, `018`, `006`,
`026`, `028`, `021`, `012`, and `017`.

### Checkpoint 15 - translation unit limit fixed

User clarified the translation payload limit: approximately `3000` source
characters per unit. This is now treated as a hard kb_creator contract for the
Innsmouth source-to-artifacts run, not a soft recommendation.

Verification:

- active run config:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/the_innsmouth_terror.source_to_artifacts.package.json`;
- `translation.max_unit_chars = 3000`;
- batch directory:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000`;
- EN batch files: `54`;
- translation units: `60`;
- maximum source unit length: `2998` chars
  (`batch_16.en.json`, `p013_u0017`);
- units over `3000`: `0`;
- regression test already asserts the config uses `3000` and
  `RU_Batches_3000`.

Current next action remains page-scoped source/RU-master delta repair and
publishing parity. Do not change the 3000-char contract unless a future run has
an explicit reviewed exception.

### Checkpoint 16 - oath block and PDF density parity

Implemented:

- restored the collapsed `Первая/Вторая/Третья клятва` sequence as a
  publication quote block in KeeperBook generation;
- kept the Innsmouth translation unit contract at `3000` source characters;
- changed generated two-column PDF body text to `10pt`; statblock cards remain
  `8pt`.

Evidence:

- `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `9 passed`, with only the known `.pytest_cache` permission warning;
- full source-to-artifacts runner reaches Keeper/HTML and still blocks only on
  the known PDF subprocess sandbox boundary;
- escalated `build-production-pdf` succeeded for the same generated config:
  `status=pass`, `variant=two_column`, `findings=0`;
- `pdf-print-qa --variant two_column --check-only`:
  `status=pass`, `pages=32`, `text_chars=132138`, `findings=0`,
  `warnings=1`;
- the remaining PDF warning is `half_empty_pdf_page` on page `32`;
- fresh comparison remains `different`:
  `reader_text.delta_chars=7771`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2334`,
  `non_statblock_delta_chars=2297`,
  `statblock_delta_chars=40`,
  PDF pages `32` candidate vs `32` reference;
- current candidate PDF SHA-256:
  `6d642656338392966081b5a149058965f2b234e58bf3c2115b122152628839cd`.

Next action:

Continue page-scoped RU/proofread parity classification on pages `016`, `018`,
`026`, `006`, `028`, `021`, `012`, and `017`. Treat remaining deltas as
translation/proofread drift unless a source-backed structural defect is found.

### Checkpoint 17 - translation payload ceiling recheck

User reiterated the practical translation limit as approximately `3000`
source characters. Rechecked the current live manifest instead of relying on
prior notes.

Evidence:

- manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- `schema=kb_creator.translation_batch_manifest.v1`;
- `max_batch_chars=3000`;
- `counts.batches=54`;
- `counts.units=60`;
- `counts.original_units=60`;
- `counts.split_units=0`;
- `counts.chars=113960`;
- maximum observed batch size: `2998` (`batch_16`);
- batches over `3000`: `0`;
- regression evidence:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `10 passed`, with only the known `.pytest_cache` permission warning.

Decision:

Keep `translation.max_unit_chars = 3000` as a hard kb_creator contract for this
run. The remaining blocker is artifact/source parity, not oversized translation
payloads.

### Checkpoint 18 - source-backed statblock core fallback

Implemented a source-backed fallback for Innsmouth statblock projection:

- `project_innsmouth_statblocks_from_ru.py` now accepts `--source-pdf`;
- it extracts the source PDF text layer for the statblock page range and matches
  blocks by English statblock names;
- the fallback only fills missing core/derived values in the generated
  statblock cards; RU identity, combat, skills, spells, and notes remain based
  on the accepted RU master;
- the full runner passes the original source PDF into statblock projection.

Evidence:

- regression test:
  `test_statblock_projection_fills_missing_core_values_from_pdf_text_layer`;
- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `11 passed`, with only the known `.pytest_cache` permission warning;
- `statblock_projection_report.json`: `status=pass`, `records=22`,
  `filled_from_pdf=51`, no findings;
- sample verified in generated KeeperBook:
  Diane Loring core row now includes `СИЛ 50`, `ТЕЛ 70`, `РАЗМ 50`, `ЛВК 55`,
  `ИНТ 80`, `ВНЕШ 65`, `МОЩ 50`, `ОБР 70`, `РАСС 50`;
- production PDF rebuilt via the standard external PDF step:
  `status=pass`, `variant=two_column`, `findings=0`;
- PDF print QA:
  `status=pass`, `pages=33`, `text_chars=130950`, `findings=0`,
  `warnings=1`;
- comparison remains `different`: candidate/reference PDF pages `33/32`,
  `reader_text.delta_chars=7592`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2073`.

Current interpretation:

The statblock value-loss defect is partially fixed from source PDF evidence.
The current blocker is now PDF density/layout parity and comparison-normalizer
handling of HTML statblock tables versus the old plain-text reference style.

### Checkpoint 19 - PDF table density and remaining art parity blocker

Adjusted the PDF variant CSS so `statblock_card_font_size` changes the card
base size and headings, but no longer flattens all statblock table font sizes
to the same absolute value. This restores the existing compact table rules
(`.56em`, `.58em`, `.6em`) for statblock cards.

Evidence:

- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `11 passed`;
- production PDF rebuilt:
  `status=pass`, `variant=two_column`, `findings=0`;
- PDF print QA:
  `status=pass`, `pages=33`, `text_chars=135387`, `findings=0`,
  `warnings=0`;
- comparison remains `different`: PDF pages `33/32`,
  `reader_text.delta_chars=7592`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2073`;
- candidate PDF SHA-256:
  `9830a54d3f01c4e0cb31728778e83f5ecfabb8a33d116c01f3b9c00036775d54`.

### Checkpoint 20 - corrected handout art parity and translation ceiling

User reiterated the practical translation limit as approximately `3000` source
characters. The live manifest confirms this is already enforced:

- manifest:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- `max_batch_chars=3000`;
- `54` batches, `60` units, `60` original units, `0` split units;
- maximum observed batch size `2998`;
- batches over `3000`: `0`;
- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `12 passed`, with only the known `.pytest_cache` permission warning.

Corrected the earlier art diagnosis:

- `xref-01397` is present in both generated KeeperBook and generated HTML;
- the remaining defect was an empty `source-page-044` marker after Handout 2;
- `cleanup_reader_art_page_marker_residuals` now removes that marker only when
  the retargeted `xref-01397` art block is present;
- `source-page-045` and `source-page-046` remain preserved.

Evidence after rebuild:

- generated KeeperBook: `source-page-044=0`, `source-page-045=1`,
  `source-page-046=1`, `xref-01397=true`;
- generated HTML includes the `xref-01397` figure;
- production PDF build required escalated execution because the normal runner
  hit Windows `Permission denied` in `Temp/Production_PDF`, then passed:
  `status=pass`, `variant=two_column`, `findings=0`;
- PDF print QA:
  `status=pass`, `pages=33`, `text_chars=135387`, `findings=0`,
  `warnings=0`;
- comparison remains `different`, with candidate/reference pages `33/32`,
  `reader_text.delta_chars=7592`,
  `reader_text_ignoring_statblock_scaffold.delta_chars=2073`.

Current interpretation:

Art parity for Handout 2 is no longer a blocker. The remaining work is PDF
density/layout parity and page-scoped RU/proofread drift, especially pages
`016`, `018`, `026`, `006`, `028`, `021`, plus statblock-heavy pages `033` and
`034`. Keep the `3000` translation batch ceiling unchanged.

### Checkpoint 21 - full runner reaches comparison gate

The full kb_creator dry-run was rerun after the marker/art fix. It now reaches
the final comparison gate through the complete generation path:

`source PDF -> source reconstruction -> translation batches -> accepted RU master -> KeeperBook -> statblock projection -> HTML -> PDF -> comparison`.

Generation evidence:

- full runner PDF command: `status=pass`, `action=built`, `variant=two_column`,
  `findings=0`;
- PDF print QA:
  `status=pass`, `pages=33`, `text_chars=135387`, `findings=0`,
  `warnings=0`;
- full runner final status remains `blocked` because comparison is intentionally
  strict and returns `artifact_comparison_different`.

Comparison evidence:

- candidate/reference source pages: `45/45`;
- candidate/reference art blocks: `34/34`;
- candidate/reference headings: `61/62`;
- candidate/reference PDF pages: `33/32`;
- `reader_text.delta_chars=7592`;
- `reader_text_ignoring_statblock_scaffold.delta_chars=2073`;
- candidate PDF SHA-256:
  `d90435f2f7e8f62d65efbd122f987b0a2088fd9a222d89cc224745655646aa40`.

Next action:

Continue parity work from the comparison report, not from stale art assumptions.
The remaining blocker is content/layout parity against the frozen reference, not
translation batch size and not missing Handout 2 art.

### Checkpoint 22 - translation ceiling revalidated

User hint rechecked against the live run: the Innsmouth kb_creator translation
ceiling is fixed at `3000` source characters per packet.

Evidence:

- active config has `translation.max_unit_chars=3000`;
- active manifest is
  `Translation_Work/RU_Batches_3000/translation_batch_manifest.json`;
- manifest has `max_batch_chars=3000`;
- live manifest counts: `54` batches, `60` units, `60` original units,
  `0` split units;
- maximum observed batch size is `2998` (`batch_16`);
- batches over `3000`: `0`;
- regression tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `15 passed`.

Decision:

Do not change the `3000` ceiling while continuing artifact parity remediation.
Remaining drift is not attributed to oversized translation batches.

### Checkpoint 23 - body comparison switched from exact wording to evidence gate

User clarified that body text translated by agents may legitimately differ in
wording from the frozen reference. The comparison layer was updated so exact
body wording is no longer treated as the only acceptance signal.

Changes made:

- `compare_innsmouth_artifacts.py` now emits `body_similarity_report`;
- body pages are checked with deterministic hard signals:
  length delta <= `12%` and no missing numeric values from the reference;
- low literal similarity is recorded as semantic-review advisory, not an
  automatic body failure;
- regression coverage added for minor translation drift versus actual text
  loss.

Fresh evidence:

- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `17 passed`;
- body similarity report:
  `status=pass`, `pages_checked=34`, `pages_passing=34`,
  `pages_requiring_review=0`, `pages_requiring_semantic_review_only=24`;
- terminology cleanup now normalizes high-confidence prose terms such as
  `Deep Ones`, `Star Spawn`, `Society for the Exploration of the Unexplained`,
  and `The Esoteric Order of Dagon`, while preserving the source title heading;
- `21:00` and `Drive Auto` preservation/normalization are covered by tests;
- production PDF was rebuilt after the user unlocked the file:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`,
  SHA-256 `1e337ddbaf829f8437b98a0e2a20b4e2c6887f6a8ca7d10b46b2eb332edec3ff`;
- PDF print QA:
  `status=pass`, `pages=33`, `findings=0`, `warnings=0`.

Current interpretation:

Strict artifact comparison still returns `different`: Keeper exact text differs,
candidate/reference PDF pages are `33/32`, and PDF extracted text differs.
However, the body-text gate no longer proves body loss. Remaining work should
focus on PDF density/layout parity, statblock/reference divergence, heading
count `61/62`, and any structural gate that still has objective evidence.

### Checkpoint 24 - accepted drift full run

User clarified that non-deterministic agent translation may differ from the
reference wording, so the objective comparison should not demand 100%
byte/text identity for body prose. The acceptance policy now keeps exact
hash/text differences in the report while allowing a source-to-artifacts run to
pass when hard preservation gates succeed.

Implemented:

- `compare_innsmouth_artifacts.py` now has three top-level outcomes:
  `pass`, `accepted_drift`, and `different`;
- Keeper `accepted_drift` requires matching source-page count, heading count,
  Keeper art-block count, no missing/extra reader-text pages,
  `body_similarity_report.status=pass`, and reader text delta ignoring
  statblock scaffold within `5%`;
- PDF `accepted_drift` requires matching page count, non-empty extracted text,
  no PDF extraction findings, and PDF text-volume delta within `5%`;
- regression coverage locks minor translation drift acceptance and actual body
  loss rejection.

Fresh evidence:

- tests:
  `python -m pytest kb_creator\tests\test_innsmouth_source_to_artifacts.py`
  -> `18 passed`;
- full runner:
  `python kb_creator\scripts\build_innsmouth_source_to_artifacts.py --run-id 20260730T210831Z`
  -> `status=pass`, `findings=0`;
- full run report:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/full_run_report.json`;
- comparison:
  `status=accepted_drift`, `keeper=accepted_drift`, `pdf=accepted_drift`;
- source pages: candidate/reference `45/45`;
- headings: candidate/reference `62/62`;
- Keeper art blocks: candidate/reference `34/34`;
- body gate: `pass`, pages requiring review `0`;
- PDF pages: candidate/reference `32/32`;
- PDF text delta ratio: `0.0297`;
- PDF print QA:
  `status=pass`, `pages=32`, `findings=0`, `warnings=1`;
- technical residue scan in generated KeeperBook and HTML found no escaped
  anchors, source-hash comments, unit ids, or numeric entity garbage.

Remaining non-blocking visual debt:

- PDF QA warning `half_empty_pdf_page` on page `32`; this is layout-density
  drift in the final handout flow, not evidence of missing content.

Decision:

The current kb_creator Innsmouth source-PDF-to-Keeper/HTML/PDF objective is
reproducible for the current candidate. Further work should be framed as
visual/layout polish or broader productization, not as an unresolved blocker for
the source-to-artifacts proof.

### Checkpoint 25 - preserve tmp PDF art-order candidate

User identified a potentially important intermediate PDF candidate:

`D:\NRI\kb_creator\output\innsmouth_source_to_artifacts\runs\20260730T210831Z\Pdf\.The_Innsmouth_Terror_RU.tmp-37396-1785454676611631.pdf`

This file must not be deleted during cleanup. It appears to contain a more
successful art ordering/placement result: art is positioned in the same relative
order as the English source PDF and near the corresponding source text, without
the ordering drift seen in later artifacts.

Open follow-up:

- compare this tmp PDF against the final generated PDF and the source English
  PDF;
- identify which build stage, CSS state, temporary layout state, or renderer
  behavior produced the improved art order;
- reproduce the behavior intentionally in `kb_creator`;
- convert the discovery into a deterministic pipeline rule/test rather than
  depending on a transient temporary file.

Boundary: preserve the file as forensic evidence. Do not promote it as the
official artifact until the mechanism is understood and reproduced.

### Checkpoint 26 - tmp PDF art-order mechanism analysis

Forensic analysis report:

`kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/tmp_pdf_art_order_analysis.md`

Conclusion:

The preserved tmp PDF was a normal hidden Edge print temp output, not a
different renderer. It likely survived after an interrupted/blocked replacement
or cleanup path. Its useful behavior comes from the earlier input state: it was
printed before the current reader-art publication policy reduced the full art
stream to the reader subset.

Evidence:

- tmp PDF: `33` pages, `61` image XObjects;
- current final PDF: `32` pages, `34` image XObjects;
- current `art_manifest.json`: `62` placements, `34` emitted,
  `28` reader-publication-suppressed;
- current KeeperBook and HTML also have `34` art blocks;
- suppression is implemented in
  `kb_creator/scripts/build_keeperbook_from_ru_master.py` through
  `INNSMOUTH_SUPPRESSED_READER_ART_IDS` and
  `apply_reader_art_publication_policy`.

Pipeline lesson:

Split art handling into two explicit manifests:

- `source_art_flow_manifest.json`: all approved placements in source order,
  used for forensic/order validation and optional probe output;
- `reader_art_selection_manifest.json`: publication subset with explicit
  suppression reasons and traceability back to source flow.

The tmp file remains preserved as forensic evidence until that split and its QA
regression are implemented.

### Checkpoint 27 - source structure extraction accepted

User narrowed the active task to source extraction only:

- preserve paragraph structure;
- preserve column order;
- work only from the original source PDF plus Keeper.md as the structural
  control;
- stop once source structure reaches full gate pass.

Implemented in `kb_creator/scripts/build_innsmouth_source_to_artifacts.py`:

- replaced the primary page-wide PyMuPDF text blob with a coordinate-aware
  `pdfplumber` extraction path;
- grouped words into lines by vertical position and detected column;
- enforced deterministic reading order: full-width content first when present,
  then left column, then right column;
- lowered paragraph break detection to the observed source-PDF geometry:
  internal line continuation is about `2pt`, paragraph gap is about `6.5pt`;
- kept bullet and `Keeper note:` continuation text inside the same block;
- filtered source running headers and scrambled visual-letter strings;
- added `source_structure_hazard_audit` and wired it into the source-only run.

Evidence:

- run:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260802TSTRUCTURE06/full_run_report.json`;
- audit:
  `kb_creator/working/innsmouth_source_to_artifacts/runs/20260802TSTRUCTURE06/QA/source_structure_hazard_audit.json`;
- full run status: `pass`;
- audit status: `pass`;
- findings: `0`;
- source pages: `46`;
- missing/unexpected page markers: `0/0`;
- reading-order anchors passed:
  `009` Anna before Christopher,
  `012` Orne Library before Arkham Advertiser,
  `024` Brewster Residence before Sammy bullets and Keeper note;
- long paragraph blocks over `2800` chars: `0`;
- scrambled visual text blocks: `0`;
- unquoted Keeper notes: `0`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `20 passed`.

Decision:

The source-structure stage is accepted for this micro-goal. Do not proceed to
translation, KeeperBook, HTML, or PDF until the next explicit instruction.

### Checkpoint 28 - KeeperBook vs EN PDF page-structure audit

User requested a second pass over the current generated KeeperBook against the
English source PDF, page by page:

- compare character counts;
- compare paragraph/block counts;
- control the first meaningful left/right column lines from the source PDF;
- verify their relative order in Keeper.md when the line anchors are
  mechanically findable.

Implemented:

- `kb_creator/scripts/audit_innsmouth_keeper_pdf_structure.py`;
- output JSON:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/keeper_pdf_structure_audit.json`;
- output Markdown table:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/keeper_pdf_structure_audit.md`.

Evidence:

- pages checked: `46`;
- column-order failures: `0`;
- mechanically verified column-order pass: `1`;
- ambiguous column-order checks: `2`;
- not-testable column-order checks: `38`, usually because first English
  column lines are translated in Keeper and cannot be exact-matched without
  semantic review;
- not-applicable column-order checks: `5`;
- flagged pages: `002`, `003`, `006`, `014`, `023`, `033`, `034`, `035`,
  `036`, `037`, `038`, `039`, `040`, `041`, `042`, `043`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `20 passed`.

Interpretation:

No mechanically proven left/right column inversion remains in the current
KeeperBook. The flagged pages are mostly paragraph-density mismatches,
statblock/pre-generated-investigator projection pages, source TOC/frontmatter,
handouts, and page `014` visual/handout text mismatch. These require either
semantic review or projection-specific comparison, not a raw column-order fix.

### Checkpoint 29 - EN PDF vs normalized EN source integrity audit

User narrowed the comparison target to the correct extraction layer:

`EN PDF` vs
`kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md`.

Implemented:

- `kb_creator/scripts/audit_innsmouth_source_pdf_integrity.py`;
- output JSON:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/source_pdf_integrity_audit.json`;
- output Markdown table:
  `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/source_pdf_integrity_audit.md`.

Evidence:

- pages checked: `46`;
- exact pages against the current coordinate extractor: `23`;
- non-exact pages: `23`, caused by normalization-level differences rather
  than large text loss;
- maximum no-whitespace character delta: `15`;
- minimum similarity: `0.99377`;
- paragraph/block deltas only on pages `012` (`+1`) and `042` (`-1`);
- possible cross-column sentence split warnings: `005`, `006`, `007`, `009`,
  `010`, `012`, `013`, `016`, `019`, `020`, `021`, `023`, `028`, `030`,
  `031`, `032`, `033`, `035`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `20 passed`.

Interpretation:

The normalized EN source is materially intact against the current extraction
algorithm. The remaining risk is not character loss but reading-flow policy on
pages where the first meaningful right-column line looks like a continuation of
the left-column text. Those pages need visual/order review before declaring the
extraction policy universally safe.

### Checkpoint 30 - delegated warning-page review complete

The `possible_cross_column_sentence_split` warning pages from Checkpoint 29
were delegated to bounded `gpt-5.4` executor/QA agents in smaller page sets.

Handoffs:

- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_A1.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_A2.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_A3.md`;
- `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_B.md`;
- orchestrator summary:
  `kb_creator/docs/plans/20260730-innsmouth-source-to-artifacts/handoffs/source_integrity_warning_pages_summary.md`.

Coverage:

- assigned warning pages: `18`;
- reviewed pages: `18`;
- missing pages: none.

Classification:

- `ok`: `007`, `009`, `010`, `012`, `013`, `016`, `019`, `020`, `021`,
  `028`, `030`, `032`, `033`, `035`;
- `real_issue`: `005`, `006`, `023`;
- `needs_human_visual_review`: `031`.

Interpretation:

Most warnings are false positives from independent right-column sections,
side-note layout, statblock spreads, or page headers. Real source extraction
defects remain on:

- page `005`: quote is split and interleaved with the introduction body;
- page `006`: right-column body and `Table 1` are interleaved, with orphan
  table fragments;
- page `023`: `Table 2` is linearized as broken prose.

Page `031` requires human visual review before changing extraction policy.

### Checkpoint 31 - source extraction fixes for 005/006/023

The real source extraction defects identified in Checkpoint 30 have been fixed
in the Innsmouth source cleanup stage.

Implementation:

- added `apply_innsmouth_source_page_overrides` to
  `kb_creator/scripts/build_innsmouth_source_to_artifacts.py`;
- page `005`: reassembled the full Lovecraft quote before `INTRODUCTION`;
- page `006`: restored oath/body order and converted `Table 1: timeline of
  events` to a Markdown table;
- page `023`: restored `Table 2: encounters in the caves` as a Markdown table
  with intact `1D100` ranges;
- source hazard audit now treats Markdown tables as structured blocks instead
  of long prose paragraphs;
- source PDF integrity audit no longer flags Markdown table pages as collapsed
  prose.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `23 passed`, with only the known `.pytest_cache` access warning;
- `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z --stop-after-source`
  -> `status=pass`, `findings=0`;
- `python kb_creator/scripts/audit_innsmouth_source_pdf_integrity.py`
  -> `status=pass`, `pages=46`, `flagged=15`;
- pages `005`, `006`, and `023` now have empty integrity `flags`.

Remaining:

- page `031` remains `needs_human_visual_review`;
- remaining integrity warnings are the previously delegated ok/false-positive
  pages and should not be treated as the same class of defect as `005/006/023`.

### Checkpoint 32 - occluded text-layer content policy

Human visual review of source page `031` confirmed that the `What if they’re
captured?` block is not visible in the rendered source page. Independent text
extractors still return it from the PDF text layer, so it is treated as
occluded/recovered content rather than accepted visible source text.

Pipeline policy added:

- classification: `occluded_text_layer_recovered_content`;
- default action: exclude from main accepted EN source;
- required retention: store in QA artifact;
- publication: allowed only with an explicit editorial recovered-content
  decision/note.

Artifact:

- `kb_creator/reports/innsmouth_source_to_artifacts/runs/20260730T210831Z/occluded_text_layer_recovered_content.json`.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `24 passed`, with only the known `.pytest_cache` access warning;
- source rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z --stop-after-source`
  -> `status=pass`, `findings=0`;
- accepted source page `031` no longer contains `the`, `epIc fInale`, or
  `What if they’re captured?`;
- QA artifact contains one retained recovered-content item:
  `innsmouth-p031-occluded-epic-finale-captured`.

### Checkpoint 33 - rebuilt HTML/Keeper/PDF after occluded-content policy

The current Innsmouth source-to-artifacts run was rebuilt end-to-end after the
page `031` occluded text-layer policy.

Pipeline fixes applied during rebuild:

- `translator.py` production PDF temp directories now use a write-probed
  Windows-safe `mkdir` helper instead of `tempfile.mkdtemp`;
- `kb_creator` Innsmouth package generation now uses `{source_html_uri}` for
  Edge print-to-PDF input.

Verification:

- full rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z`
  -> `status=pass`, `findings=0`;
- PDF stage:
  `production_pdf_report_two_column.json`
  -> `status=pass`, `action=built`, `canonical_replaced=true`,
  `findings=0`;
- PDF opens through `pypdf` with `32` pages.

Current artifacts:

- `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook.md`;
- `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/The_Innsmouth_Terror_Full_RU.html`;
- `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.pdf`.

### Checkpoint 34 - heading-prefix duplicate repair

User PDF review showed a duplicated section title pattern where a promoted
Markdown heading was followed by a body paragraph starting with the same title,
for example `### Эпический финал` followed by `Эпический финал Наконец ...`.

Pipeline repair:

- added a universal KeeperBook cleanup step in
  `kb_creator/scripts/build_keeperbook_from_ru_master.py`;
- the step strips a repeated heading prefix from the first content paragraph
  after a Markdown heading;
- Keeper heading QA now reports `heading_prefix_duplicates`;
- tests cover the synthetic `Эпический финал` and `Универсальный магазин`
  cases.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `26 passed`;
- current KeeperBook scan -> `heading_prefix_issues=0`;
- `Эпический финал Наконец` and `Универсальный магазин - известная` are absent
  from current KeeperBook;
- KeeperBook and HTML were rebuilt by the full run.

PDF completion:

- after the file lock was released, the `two_column` PDF stage was rerun;
- `production_pdf_report_two_column.json` -> `status=pass`,
  `action=built`, `canonical_replaced=true`, `findings=0`;
- canonical PDF was replaced successfully.

### Checkpoint 35 - MVR Class B1 vehicle block projection

User PDF review showed that the `MVR Class B1 'Olmstead'` train block under
`Играя героя` was present in source/RU/Keeper/HTML/PDF but was still rendered as
ordinary body prose.

Pipeline repair:

- added a KeeperBook vehicle/stat-object projection for the compact vehicle
  pattern `MOV / Build / Armour / Gauge / Boiler pressure / Top Speed`;
- the block is now rendered as a structured Markdown table with bold title
  `Паровоз MVR Class B1 «Olmstead»`;
- the OCR/header residue `Эпический финал Паровоз MVR...` is removed from the
  body text;
- structural QA now records `vehicle_statblocks` and fails if `Паровоз MVR`
  appears without the structured block.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `27 passed`;
- `python -m pytest translator/tests/test_p0_contracts.py`
  -> `21 passed`, `1 skipped` when rerun outside the sandbox temp-write
  restriction;
- full rebuild:
  `python kb_creator/scripts/build_innsmouth_source_to_artifacts.py --run-id
  20260730T210831Z`
  -> `status=pass`, `findings=0`;
- PDF text extraction confirms page `25` contains
  `Паровоз MVR Class B1 «Olmstead»`, table rows `MOV`, `Build`, and the full
  damage rules.

### Checkpoint 36 - Keeper note callout completeness

User review requested a source-to-output count check for Keeper notes.

Findings:

- accepted EN source: `14` `Keeper note:` blocks;
- RU master: `14` Russian note labels;
- before repair, KeeperBook/HTML had only `12` callouts because two early notes
  were translated as `Примечание для Хранителя:` and one paragraph contained
  two consecutive note labels;
- after repair, KeeperBook has `14` `callout-class: keeper-note` blocks;
- HTML has `14` `review-callout keeper-note` blocks;
- PDF text extraction finds `14` `Примечание Хранителю` occurrences.

Pipeline repair:

- `NOTE_RE` accepts `Примечание/Заметка Хранителю` and
  `Примечание/Заметка для Хранителя`;
- `split_keeper_note` now splits multiple Keeper notes from a single paragraph
  into separate callouts;
- Keeper structural QA now checks exact source-note count vs callout count.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `29 passed`;
- production HTML rebuild -> `status=pass`, `findings=0`;
- production PDF rebuild -> `status=pass`, `action=built`,
  `canonical_replaced=true`, `findings=0`.

### Checkpoint 37 - Printed page-number residue cleanup

User PDF review identified old printed source-page numbers surviving as
standalone reader text: `4`, `5`, `6`, and `9`.

Diagnosis:

- the current EN normalized source did not contain standalone `1-2` digit
  lines, but the RU master still contained translated/OCR residue lines for
  printed page numbers;
- the visible KeeperBook/PDF issue came from those standalone RU lines being
  projected as ordinary body paragraphs;
- source page `004` is excluded from this cleanup because source `Содержание`
  intentionally contains numbered entries.

Pipeline repair:

- added `strip_printed_page_number_residue` to
  `kb_creator/scripts/build_innsmouth_source_to_artifacts.py`, removing a
  standalone old printed number when `printed_page == source_page - 4`;
- added the same downstream guard to
  `kb_creator/scripts/build_keeperbook_from_ru_master.py`;
- added Keeper structural QA finding `printed_page_number_residue`, making any
  remaining standalone old page-number line a blocker;
- added regression tests for both source cleanup and Keeper cleanup/QA.

Verification:

- `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `31 passed`;
- rebuilt KeeperBook:
  `status=pass`, `printed_page_number_residues=[]`;
- statblock projection:
  `status=pass`, `expected=22`, `projected=22`, `findings=0`;
- production HTML:
  `status=pass`, `pages=45`, `headings=61`, `images=34`, `findings=0`;
- production PDF:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- explicit residue scan: Keeper `0`, HTML `0`, PDF text extraction `0` for
  standalone `4/5/6/9`.

Current caveat:

- `pdf-print-qa --variant two_column --check-only` now reports
  `page_flow_columns_missing_statblock_section_break`, with PDF pages `39`.
  This is a separate layout-policy finding, not a printed page-number residue
  failure.

### Checkpoint 38 - Character heading tail residue cleanup

User PDF/HTML review identified character metadata tails leaking into body
text after the heading, for example `Christopher McGuire` followed by
`, 37 лет, инженер ...`.

Findings:

- user-visible cases found before repair: `3`;
- affected headings: `Genevieve ‘Ginny’ Dubois`, `Anna Díaz`,
  `Christopher McGuire`;
- root cause: `split_inline_headings` split known character labels into
  headings but only stripped whitespace from the remaining tail, leaving a
  leading comma/heading separator as reader body text.

Pipeline repair:

- `split_inline_headings` now strips leading heading-tail separators
  `, ; : - --` from metadata tails;
- mapped character-heading fallback applies the same tail cleanup;
- `heading_qa` now checks the next non-empty block after a heading and fails on
  `heading_tail_residues` such as `, 37 лет` or `, age 37`;
- added regression coverage for both the fixer and the QA blocker.

Verification:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `33 passed`;
- rebuilt KeeperBook:
  `status=pass`, `pages=45`, `headings=62`;
- statblock projection:
  `status=pass`, `expected=22`, `projected=22`, `findings=0`;
- production HTML:
  `status=pass`, `pages=45`, `headings=61`, `images=34`, `findings=0`;
- production PDF:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- explicit residue scan:
  Keeper `0`, HTML `0`, PDF text extraction `0`;
- Keeper `heading_qa`:
  `status=pass`, `heading_tail_residues=0`,
  `heading_prefix_duplicates=0`, `wrong_page_headings=0`.

Note:

- sandboxed Edge PDF export still fails with Crashpad/Mojo `Access denied` on
  this station; the successful PDF rebuild used the approved headless Edge
  PDF command outside the sandbox.

### Checkpoint 39 - Source art anchors for Keeper_EN

Objective:

- teach `kb_creator` to create art anchors from the accepted EN source before
  translation/publishing, so the same art placement contract can later be
  restored into Keeper RU, HTML, and PDF instead of being re-guessed from
  Russian headings.

Pipeline repair:

- added a source art anchor layer to
  `kb_creator/scripts/build_innsmouth_source_to_artifacts.py`;
- `make_config` now declares `production_outputs.keeper_markdown_en` and
  `art_integration.source_anchor_manifest/source_anchor_report`;
- after `apply-image-approval` and `build-art-placement-manifest`, the run now
  builds:
  - `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/art_anchor_manifest.json`;
  - `kb_creator/working/innsmouth_source_to_artifacts/runs/20260730T210831Z/QA/source_art_anchor_report.json`;
  - `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook_EN.md`;
- EN Keeper art blocks are explicit `keeper-art-block source-art-anchor`
  blocks with `data-placement-id`, `data-source-anchor-id`,
  `data-source-page`, `data-source-xref`, and `data-role`;
- NPC art uses deterministic order against EN character lead lines such as
  `Name, age N`; other art uses EN source heading lines; unresolved cases fall
  back to `src-pNNN-page` and remain visible in the report.

Verification:

- current source art anchor report: `status=pass`;
- reader placements: `34`;
- anchored placements: `34`;
- missing runtime image paths: `0`;
- page fallback anchors: `12`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `35 passed`.

Remaining work:

- switch RU Keeper art restoration to consume `art_anchor_manifest.json` as the
  authority, preserving the same placement IDs and source anchors;
- add downstream QA that Keeper RU, HTML, and PDF contain the same placement ID
  set/order as Keeper EN;
- reduce page fallback anchors by using source block/bbox evidence for
  multi-art pages instead of page-level placement.

### Checkpoint 40 - Bbox/source-block art anchor refinement

Objective:

- reduce the `12` page fallback art anchors from Checkpoint 39 by using source
  PDF image rectangles and text-block rectangles, while keeping Keeper EN as
  the visible source-layer restoration artifact.

Pipeline repair:

- source art anchor candidates now include `paragraph_lead` anchors in addition
  to explicit EN heading and character-lead anchors;
- the source art anchor stage now builds PyMuPDF layout evidence:
  image xref rectangles and text block rectangles from the original PDF;
- fallback placement is refined by `nearest_source_text_bbox`, using the
  nearest suitable EN source candidate backed by a PDF text-block bbox;
- scoring prefers a nearby preceding text block/heading, and uses the nearest
  following text only when no preceding block is available;
- the source anchor manifest records `source_anchor_bbox` for bbox-backed
  placements.

Verification:

- current source art anchor report: `status=pass`;
- reader placements: `34`;
- anchored placements: `34`;
- missing runtime image paths: `0`;
- page fallback anchors: `1`;
- only fallback placement: `xref-01811` on source page `001`, the cover/title
  image; this is expected because cover art has no body text anchor;
- method distribution:
  `nearest_source_text_bbox=28`, `npc_order_on_source_page=4`,
  `source_heading_order_on_page=1`, `page_fallback=1`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `36 passed`.

Remaining work:

- downstream RU Keeper/HTML/PDF still need to consume the source anchor manifest
  as the authority and run parity QA against Keeper EN.

### Checkpoint 41 - Downstream source-anchor art restoration

Status: completed.

Owner: orchestrator.

Problem:

- `art_anchor_manifest.json` was accepted at the EN/source layer, but the RU
  Keeper/HTML/PDF publishing chain still consumed the older `art_manifest.json`
  contract; the PDF therefore did not visibly prove the source-anchor work.

Pipeline repair:

- `build_keeperbook_from_ru_master.py` now accepts
  `--source-art-anchor-manifest` and prefers it for reader-art injection;
- generated Keeper art blocks carry `data-source-page`,
  `data-source-anchor-id`, `data-source-anchor-kind`, and
  `data-source-anchor-method`;
- character/source-anchor text is mapped to an existing RU heading slug when
  possible, so NPC/character art is inserted under its own heading instead of
  a broad page/section heading;
- multiple art blocks under one heading/page are sorted by
  `source_anchor_line_index` and then source xref;
- `translator.py` now recognizes extended generated `keeper-art-block` divs
  instead of escaping them as text;
- `translator.py` can read `production_art_layout.source_anchor_manifest` as
  the canonical reader-art manifest for production HTML relocation/rendering;
- the current package config now sets
  `production_art_layout.source_anchor_manifest=art_anchor_manifest.json`.

Verification:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `37 passed`;
- Keeper rebuild:
  `status=pass`, `reader_art_blocks.source_anchor_manifest_used=true`,
  `placements=34`, `inserted=34`, `findings=[]`;
- source-anchor heading overrides were applied for
  `xref-00367`, `xref-00379`, `xref-00408`, `xref-00432`, and `xref-01200`;
- HTML rebuild:
  `status=pass`, `pages=45`, `headings=61`, `images=34`, `findings=0`;
- HTML check:
  escaped `&lt;div class=&quot;keeper-art-block` count is `0`;
- statblock HTML cleanup:
  `status=pass`, `cards=22`, `structured=22`, `remaining=0`;
- statblock readiness:
  `status=pass`, `expected=22`, `cards=22`, `flattened=0`;
- PDF rebuild:
  `status=pass`, `action=built`, `variant=two_column`, `findings=0`;
- visual smoke check rendered current PDF pages `008`, `009`, and `010` and
  confirmed NPC/source-anchor art appears near its corresponding section or
  character heading.

### Checkpoint 42 - NPC Caption Identity Rule

Status: completed.

Owner: orchestrator.

Correction:

- source PDF coordinates/bboxes are not publication anchors and must not decide
  where art appears in the rebuilt PDF layout;
- coordinates/bboxes are allowed only as source-PDF evidence for identifying
  which caption/text belongs to which extracted image;
- publication placement remains semantic: character, section, handout, map, or
  page/section anchor.

Problem found:

- page `008` NPC portraits were assigned by `npc_order_on_source_page`;
- this swapped identity: `xref-00367` was incorrectly assigned to Genevieve,
  while `xref-00379` was incorrectly assigned to P.A. Bazzledon;
- visual review proved the mismatch: `xref-00367` is the male Bazzledon
  portrait, and `xref-00379` is Genevieve.

Pipeline repair:

- source art anchor generation now prefers `npc_caption_match` for NPC images:
  a short caption directly below the source image is matched to a character
  candidate before any order-based fallback is used;
- `npc_order_on_source_page` remains only a fallback when no caption evidence
  exists;
- the manifest records caption evidence fields
  `source_anchor_caption_text` and `source_anchor_caption_bbox`, but downstream
  Keeper/HTML/PDF placement uses the semantic `source_anchor_id`.

Verification:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `38 passed`;
- `art_anchor_manifest.json` now records:
  `xref-00379 -> Genevieve ‘Ginny’ Dubois`, method `npc_caption_match`;
  `xref-00367 -> P.A. Bazzledon`, method `npc_caption_match`;
  `xref-00408 -> Anna Díaz`, method `npc_caption_match`;
- rebuilt Keeper/HTML/PDF reports are `status=pass`;
- visual smoke render confirms:
  Genevieve has the correct female portrait, P.A. Bazzledon has the correct
  male portrait, and Anna Díaz has the correct portrait.

### Checkpoint 43 - Semantic NPC Art Identity Gate

Status: completed.

Owner: orchestrator.

User rule accepted:

- source PDF coordinates/bboxes must not be used as final PDF placement rules;
- source page, xref, bbox, and caption bbox are provenance/evidence only;
- final publication placement must be semantic: character, section, handout,
  map, scene, or page anchor.

Pipeline repair:

- `npc_caption_match` now detects both below-image captions and side/vertical
  captions adjacent to a source image;
- a caption can create a `caption_identity` source anchor when the name is not
  already a standalone `character_lead` in EN source text;
- a caption can promote a wrongly classified character portrait from
  `atmospheric` to `npc`;
- reviewed `heading_id` can prove uncaptioned NPC portraits when it matches a
  character lead in accepted EN source (`npc_heading_id_match`);
- NPC art identity is now a gate: any `npc` placement without
  `npc_caption_match`, `npc_heading_id_match`, or `manual_identity_override`
  produces `npc_art_identity_not_semantically_proven` and fails the source art
  anchor layer.

Current evidence:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `42 passed`;
- source art anchor report:
  `status=pass`, `reader_placements=62`, `anchored_placements=62`,
  `npc_identity_checked=17`, `npc_identity_unverified=0`, `findings=[]`;
- NPC identity methods:
  `npc_caption_match=12`, `npc_heading_id_match=5`;
- corrected key mappings:
  `xref-00379 -> Genevieve 'Ginny' Dubois`,
  `xref-00367 -> P.A. Bazzledon`,
  `xref-00395 -> Christopher McGuire` with
  `source_identity_role_promoted_from=atmospheric`,
  `xref-00408 -> Anna Diaz`;
- side-caption mappings now include:
  `Diane Loring`, `Dr. Henry Armitage`, `Karen Jeffries`, `Franc Turner`,
  `Pete`, `Zadok Allen`, and `Jeremiah Brewster`;
- rebuilt artifacts:
  KeeperBook, production HTML, and two-column PDF all rebuilt from the updated
  manifest;
- production checks:
  HTML rebuild `status=pass`, `action=rewritten`, `images=34`, `findings=0`;
  statblock cleanup/readiness `status=pass`, `cards=22`, `flattened=0`;
  PDF rebuild `status=pass`, `action=built`, `variant=two_column`,
  `findings=0`;
- visual smoke render:
  PDF page `006` shows Genevieve with the correct portrait;
  page `007` shows P.A. Bazzledon and Anna Diaz with correct portraits;
  page `008` shows Christopher McGuire with the correct camera portrait and
  Sammy Brewster with his portrait.

Remaining refinement:

- `caption_identity` portraits without their own RU heading can still be placed
  at the broader section anchor, although their identity is now proven and
  preserved in `data-source-anchor-*`;
- next improvement should add a semantic identity-text/statblock insertion
  point for caption-only NPC portraits, without using source coordinates as
  final layout positions.

### Checkpoint 44 - P.A. Bazzledon character-body split repair

Status: completed; canonical PDF replaced after file unlock.

Problem:

- user PDF review showed `P.A. Bazzledon` with the correct portrait but without
  its body description under the heading;
- diagnosis: the body existed, but KeeperBook had already attached it to the
  preceding `Genevieve 'Ginny' Dubois` block before HTML/PDF rendering;
- source cause: standalone character-name lines in Dramatis Personae can be
  image captions/OCR residue, while true character leads carry an age/role tail
  such as `P.A. Bazzledon, 40 лет...`; the old rule promoted a standalone
  residual `П.А. Баззлдон` heading and then treated the real lead as duplicate
  tail text.

Pipeline repair:

- `build_keeperbook_from_ru_master.py` now treats standalone main-character
  labels as caption/residue unless they are part of a lead line with age/role
  metadata;
- `heading_qa` now blocks empty main-character bodies, so a heading with only
  art and no body text cannot pass silently;
- regression tests cover the `П.А. Баззлдон` caption-residue case and the empty
  character-body gate.

Verification:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -q`
  -> `44 passed`;
- KeeperBook rebuild:
  `status=pass`, `pages=45`, `headings=62`;
- statblock projection:
  `status=pass`, `expected=22`, `projected=22`, `findings=0`;
- production HTML:
  `status=pass`, `pages=45`, `headings=61`, `images=34`, `findings=0`;
- statblock HTML cleanup/readiness:
  `status=pass`, `cards=22`, `structured=22`, `flattened=0`;
- HTML check confirms order:
  `h3 P.A. Bazzledon -> xref-00367 portrait -> 40 лет... body -> Anna Diaz`;
- check PDF built at:
  `kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/Pdf/The_Innsmouth_Terror_RU.check.pdf`;
- visual render of check PDF page `007` confirms P.A. Bazzledon has the correct
  portrait and full body text, and Anna Diaz starts after him with her own
  portrait/body.

Final PDF replacement:

- after the user released the file lock, the canonical PDF step was rerun;
- `production_pdf_report_two_column.json` now records `status=pass`,
  `action=built`, `canonical_replaced=true`, `findings=0`;
- canonical PDF SHA-256:
  `682e55e77b836ee5a18bf01b69bc40e804fa6dbc569359192f4b0be32a67b09c`;
- canonical PDF page count: `32`;
- visual render of canonical PDF page `007` confirms P.A. Bazzledon has the
  correct portrait and full body text, followed by Anna Diaz with her own
  portrait/body.

### Checkpoint 45 - Keeper Information callout repair

Status: partially completed; KeeperBook/HTML updated, PDF print blocked.

Problem:

- user PDF review found `Информация для Хранителя` rendered as a normal
  paragraph/heading instead of a highlighted Keeper-facing insertion;
- diagnosis: explicit `Примечание/Заметка Хранителю` markers were already
  isolated as callouts, but `Информация для Хранителя` is a separate
  heading-style class and was outside `NOTE_RE`.

Pipeline repair:

- added `wrap_keeper_info_sections()` to
  `kb_creator/scripts/build_keeperbook_from_ru_master.py`;
- the function promotes standalone `Информация для Хранителя` sections to the
  existing Keeper callout class;
- `structural_qa` now reports `keeper_info_not_isolated_as_callout` if a bare
  Keeper Information line survives;
- added a regression test for Keeper Information promotion.

Verification:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `45 passed`;
- current KeeperBook and HTML scan:
  `bare_info=0`, `info_callout=true`, `keeper_note_callouts=15`;
- production HTML:
  `status=pass`, `action=rewritten`, `findings=0`;
- downstream statblock HTML cleanup/readiness:
  `status=pass`, `cards=22`, `structured=22`, `flattened=0`.

Blocked:

- PDF print was retried twice and failed before creating a temporary PDF:
  `production_pdf_report_two_column.json` records `status=fail`,
  `action=not_replaced`, findings `pdf_engine_failed` and
  `missing_temp_output_pdf`;
- canonical PDF therefore still reflects the previous checkpoint until the PDF
  engine issue is cleared and the PDF step is rerun.

### Checkpoint 46 - Dramatis Personae heading metadata split repair

Status: partially completed; KeeperBook/HTML updated, PDF print blocked.

Problem:

- user review found that character metadata stayed detached from character
  headings, e.g. `Genevieve ‘Ginny’ Dubois` as the heading and
  `25 лет, старлетка` as body text below the portrait;
- this was a different variant of the previous heading/body split: yesterday's
  fix removed comma-tail residue but intentionally left metadata as the first
  body paragraph.

Pipeline repair:

- added `merge_main_character_heading_metadata()` to
  `kb_creator/scripts/build_keeperbook_from_ru_master.py`;
- the merge runs after reader-art injection, so it can repair the actual final
  shape `heading -> art -> metadata line -> body`;
- metadata parsing now accepts Russian age forms `год/года/лет` and stops at
  the first description word, preserving the description as body;
- `heading_qa` compares the canonical heading spine against base character
  names while allowing age/role suffixes in rendered headings;
- `heading_qa` now reports `character_metadata_splits` if metadata remains
  detached after a main-character heading;
- `translator.py` source TOC link resolution now accepts prefix matches, so
  source TOC entries like `Anna Díaz` link to headings like
  `Anna Díaz, 26 лет, продюсер`.

Verification:

- fixed headings in KeeperBook/HTML:
  `Genevieve ‘Ginny’ Dubois, 25 лет, старлетка`;
  `P.A. Bazzledon, 40 лет, режиссёр и мошенник`;
  `Anna Díaz, 26 лет, продюсер`;
  `Christopher McGuire, 37 лет, инженер`;
  `Sammy Brewster, 21 год, дилетант и брат`;
- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `45 passed`;
- production HTML:
  `status=pass`, `action=rewritten`, `findings=0`;
- TOC unresolved marker check:
  no `source_toc_link_unresolved` remains after prefix matching;
- statblock HTML cleanup/readiness:
  `status=pass`, `cards=22`, `structured=22`, `flattened=0`.

Blocked:

- PDF print retried once after this change and failed before creating a
  temporary output PDF:
  `production_pdf_report_two_column.json` -> `status=fail`,
  `action=not_replaced`, findings `pdf_engine_failed` and
  `missing_temp_output_pdf`;
- canonical PDF remains from the previous successful checkpoint until the PDF
  engine issue is cleared.

### Checkpoint 47 - Printed page number glued to heading cleanup

Status: completed for KeeperBook/HTML; PDF not rebuilt due to existing print
engine blocker.

Problem:

- user review found `7 НАЧАЛО: АРКХЭМ` rendered as body/header garbage;
- diagnosis: early printed-page cleanup removed standalone `7`, but the final
  publication shape still preserved the combined residue
  `<printed-page> <source TOC/heading label>` after the canonical heading was
  already emitted.

Pipeline repair:

- `strip_printed_page_number_residue()` now removes lines matching
  `<printed-page> <known heading/source TOC label>` outside page `004`;
- the label matcher uses canonical heading normalization, including
  `Аркхем/Аркхэм` spelling variants;
- the same cleanup is rerun after reader-art injection and character-heading
  metadata merge, immediately before KeeperBook write;
- regression test expanded to cover `<!-- source-page-011 -->` with
  `7 НАЧАЛО: АРКХЭМ`.

Verification:

- tests:
  `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py`
  -> `45 passed`;
- KeeperBook rebuild:
  `final_printed_page_cleanup.count=1`, removed
  `7 НАЧАЛО: АРКХЭМ`;
- scan:
  KeeperBook `has_7_start=false`;
  HTML `has_7_start=false`;
- production HTML:
  `status=pass`, `action=rewritten`, `findings=0`;
- statblock HTML cleanup/readiness:
  `status=pass`, `cards=22`, `structured=22`, `flattened=0`.

Blocked:

- canonical PDF was not rebuilt in this checkpoint; the known PDF print-engine
  blocker remains separate (`pdf_engine_failed` / `missing_temp_output_pdf`).
## 2026-08-04 - Source TOC expansion after Keeper Information

- User found that restored full section `Информация для Хранителя` did not
  appear in the preserved source-style `Содержание`.
- Current Keeper/HTML heading spine was audited against
  `production_html.toc_policy.source_entries`.
- Updated `translator.py` so accepted `source_entries` may carry explicit
  `href`/`matched_heading_id`; this is required for duplicate visible headings
  such as two separate `Съёмочная группа` sections.
- Updated current Innsmouth package config and
  `kb_creator/scripts/build_innsmouth_source_to_artifacts.py` generator:
  `source_entries` now contains 59 structured rows with `title`, `level`,
  and exact `href`.
- Rebuilt production HTML and statblock postprocessing:
  `production_html_report.json` is `status=pass`, `findings=0`;
  statblock readiness remains `status=pass`, `cards=22`.
- TOC audit result: `toc_items=59`, `toc_links=59`, `unresolved=0`,
  `missing_href_count=0`; `Информация для Хранителя` is present; duplicate
  `Съёмочная группа` rows resolve to `semochnaya-gruppa` and
  `semochnaya-gruppa-2`.
- Rebuilt canonical two-column PDF through escalated Chromium print:
  `production_pdf_report_two_column.json` is `status=pass`, `action=built`,
  `canonical_replaced=true`, `findings=0`.

## 2026-08-04 - Handout 2 Wrong Art Suppression

- User review found that `Раздаточный материал 2: записка` incorrectly showed
  the Miskatonic Playhouse ticket rather than only the note text.
- Diagnosis: `xref-01397` is a source page `044` service/backmatter handout
  visual and had been incorrectly forced into
  `razdatochnyi-material-2-zapiska` by `INNSMOUTH_READER_ART_ANCHOR_OVERRIDES`.
- Decision: suppress `xref-01397` from reader publication. Keep the extracted
  asset available as source/forensic evidence, but do not emit it into
  KeeperBook, HTML, or PDF.
- Pipeline repair:
  `kb_creator/scripts/build_keeperbook_from_ru_master.py` now has no override
  for `xref-01397`, adds it to `INNSMOUTH_SUPPRESSED_READER_ART_IDS`, and
  applies reader-art publication policy to both base `art_manifest.json` and
  effective `art_anchor_manifest.json`.
- Verification:
  - `python -m pytest kb_creator/tests/test_innsmouth_source_to_artifacts.py -k "reader_art"`
    -> `3 passed`;
  - KeeperBook rebuild `status=pass`, `pages=45`, `headings=63`;
  - statblock projection `status=pass`, `expected=22`, `projected=22`;
  - production HTML `status=pass`, `images=33`, `findings=0`;
  - statblock HTML readiness `status=pass`, `cards=22`, `structured=22`;
  - production PDF `status=pass`, `action=built`, `variant=two_column`,
    `findings=0`;
  - KeeperBook/HTML scans:
    `xref-01397=false`,
    `innsmouth-page-044-xref-01397-handout.png=false`,
    `GOLD WINNER=false`;
- both art manifests:
    `emit_reader_art_block=false`,
    `reader_publication_suppressed=true`.

## 2026-08-08 - Context Checkpoint: TODO Package For Systemic Pipeline Repair

Current user direction:

- record the new TODO list and analyze it with Sol/Terra;
- include the previously surfaced art-anchor blocker as item `0`;
- expand the thesis from isolated visible PDF defects into systemic pipeline
  controls that can catch and repair the root causes.

Orchestration note:

- UI-visible subagent creation was not available in the current tool surface.
  I therefore used internal `Sol` and `Terra` role reviews and did not claim
  that agents were created.

Key decision:

- The next remediation stage should be audit-first. The current defects must be
  classified by earliest failing layer:
  `source_en_reconstruction`, `ru_master_preservation`, `keeper_projection`,
  `art_anchor_semantics`, `html_pdf_rendering`, or `source_exception`.
- Manual edits in final PDF/HTML are not sufficient. Fixes must be upstream
  enough that a clean rebuild reproduces them.

Current durable artifacts:

- `pipeline_todo_20260808.md` - full user TODO list and acceptance shape;
- `handoffs/sol_pipeline_systemic_todo_review_20260808.md` - systemic
  hypotheses and work order;
- `handoffs/terra_pipeline_control_review_20260808.md` - proposed gates,
  reports, and controls.

Next action:

- implement an audit-only report for the TODO classes before changing content;
- seed it with the user examples and the `xref-01172` art-anchor blocker;
- keep `full_run_report.json` aggregate status as the release truth, not the
  downstream HTML/PDF local reports alone.
