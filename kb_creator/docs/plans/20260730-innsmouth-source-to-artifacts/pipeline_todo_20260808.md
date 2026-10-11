# Innsmouth Pipeline TODO - 2026-08-08

Status: active investigation package.

Owner: orchestrator.

Scope:

- source PDF -> EN source reconstruction;
- EN source -> RU master;
- RU master -> KeeperBook;
- KeeperBook -> HTML/PDF;
- art anchor semantics and downstream placement.

Important boundary:

- These are not isolated hand edits. Each row must either become a pipeline
  repair, a QA gate, or a documented source exception.
- The review target is the current `20260730T210831Z` Innsmouth run.

## User-Reported TODO

| ID | Finding | Suspected layer | Expected outcome |
| --- | --- | --- | --- |
| 0 | Art anchors: some art placement remains page fallback or semantically unproven. Current blocker: `xref-01172` / Hugo `Shrimpy` Hargreaves has `npc_art_identity_not_semantically_proven`. | source art anchor manifest, semantic identity, art placement | Art anchors must be semantic section anchors, with source page/xref preserved as evidence. Final layout must not depend on original PDF coordinates, but source coordinates may be used as evidence. |
| 1 | Links like `(стр. "номер")`. | RU cleanup, Keeper/HTML linking | Page references should be normalized and linked to matching section anchors where possible. Old printed page references must not remain as inert garbage. |
| 2 | Lines like `Таблица "номер, название"`. | source cleanup, table heading normalization | Table labels should become canonical headings/captions, e.g. `Таблица 2: встречи в пещерах`, not split or malformed text. |
| 3 | Lines like `Раздаточный материал "номер, название"`. | source cleanup, handout heading normalization | Handout labels should become canonical headings/captions and preserve number/title. |
| 4 | Broken name lines, e.g. `Финеас Артур Bazzledo,  Дайан\nLoring`. | source/RU line-break repair, proper-name preservation | Known names must not split across physical OCR line breaks or mix unrelated names in one line. |
| 5 | Split handout label: `Раздаточный материал\n1-a: письмо (См. раздаточный материал 1-b на\nстранице 39)`. | source cleanup, handout label/link normalization | Multi-line handout labels and their references should normalize into one readable title/reference block. |
| 6 | `Прибытие` and `Прибытие: практическая справка`. | heading normalization, duplicate heading control | If source has heading plus boxed/practical subheading, preserve intentional hierarchy; avoid duplicate heading/body residue. |
| 7 | In `Прибытие`, `Innsmouth` appears twice although source text does not contain those instances. | translation/proper-name residue, source comparison | Remove or normalize unsupported English residue; add source-backed proper-name audit for section text. |
| 8 | People-by-train art is placed under `Отель Gilman House`, but should belong to another section. | semantic art anchor, section placement | Art must anchor by subject/near source context, not by nearest downstream heading after layout drift. |
| 9 | `Кабинет продюсера`: list and body glued after `Именно там хранится вся хрупкая техника».` / `Единственная другая зацепка...`. | source block order, list/body boundary | Restore list/body boundary and paragraph separation according to source page evidence. |
| 10 | `Bazzledon's Office`: content mismatch or text-block order mismatch. | source reading order, RU preservation | Compare source page blocks against EN/RU/Keeper and repair the accepted block order. |
| 11 | `Ginny's Trailer` appears at the end of `Исследование`: unclear whether this is stray or lost heading/content. | source reading order, heading placement | Determine source location and re-anchor as intended heading/content or remove as stray residue with evidence. |
| 12 | `На съёмочной площадке`: possible mixed blocks/columns; list and body glued. | source reading order, list/body boundary | Reconstruct source block order and list boundaries before RU/Keeper projection. |
| 13 | `Передвижение по пещерам`: `Table 2` must become `Таблица 2: встречи в пещерах`; isolated `Расследование` is garbage. | table detection, orphan heading/source running header cleanup | Table label normalized; orphan section token removed or reclassified with evidence. |
| 14 | Pages 20/21, `Brewster Residence`: likely mixed columns. | EN source reconstruction, column order | Verify visible PDF column order against EN source page and repair accepted source. |
| 15 | Pages 21/22, `Наткнуться на съёмочную площадку`: likely mixed columns. | EN source reconstruction, column order | Verify and repair accepted source order. |
| 16 | Pages 22/23: likely mixed columns. | EN source reconstruction, column order | Verify and repair accepted source order. |
| 17 | `Эпический финал`: block/column order may be mixed or content glued under `Последний поезд из Иннсмута`; heading below exists but placement is wrong. | source reading order, heading anchoring | Restore intended section ordering and ensure `Эпический финал` content does not fall under wrong subsection. |
| 18 | `Играя героя` should be a separate subsection after train card/body. | heading/card boundary, vehicle card projection | Preserve vehicle card as card/stat block and keep `Играя героя` as separate subsection. |
| 19 | More general column/block order mix suspected. | global source reconstruction gate | Add broader audit that checks first line/order of source columns and block monotonicity, especially pages without repeated headings. |

## Required Classification Before Fixes

Each finding must be tagged as one of:

- `source_en_reconstruction`;
- `ru_master_preservation`;
- `keeper_projection`;
- `art_anchor_semantics`;
- `html_pdf_rendering`;
- `source_exception`.

No finding should be closed only by changing final HTML/PDF. The fix must be
upstream enough that a rebuild reproduces it.

## Acceptance Shape

The next remediation stage is accepted only when:

- every TODO row has a status, owner, and evidence path;
- source-order findings have page-level before/after evidence;
- art findings have semantic anchor evidence, not only page coordinates;
- KeeperBook, HTML, and PDF are rebuilt from the same accepted inputs;
- QA reports include checks for the repaired classes of failures;
- `full_run_report.json` no longer hides a blocker behind downstream passes.
