# KB Creator

## Текущие документы и исправления — 5 октября 2026

Шесть просмотренных пользователем DOCX и их ассеты находятся в
[актуальном индексе](deliverables/latest/README_RU.md). Эти просмотренные копии
сохранены; исправления создаются отдельными версиями. Девять подтверждённых
ошибочных HTML/PDF из `deliverables/latest` отправлены в корзину Windows;
исходные PDF и ассеты не удалены.

Текущий результат сборки — **DOCX**, без генерации HTML и опубликованного PDF.
Обычный Word-маршрут использует проекцию в памяти; старые команды общей
HTML/DOCX/PDF-публикации отключены до записи. Проверка исторических пакетов
остаётся доступной в режиме чтения. PDF-публикация относится к отдельному
пайплайну, а служебные PNG используются только для визуальной проверки Word.

Исправления пользовательской вычитки, восстановление иллюстраций и адаптация
старых характеристик/названий навыков: [план](docs/plans/20261004-user-docx-review/plan.md),
[текущее состояние](docs/plans/20261004-user-docx-review/context.md).
Новые кандидаты пока проходят проверки; это не принятие книг пользователем.
Удалённые исторические рабочие мастера нельзя восстановить по ссылкам ниже.

## Исторические этапы сборки и передачи

«Тени Ленинграда» готовы к пользовательской вычитке: проверены весь текст и
все 65 страниц, добавлены 5 адресных комментариев. [DOCX и полный пакет](inputs/shadows-of-leningrad-1938/candidates/review-01/PACKAGE_GUIDE.md).
Независимая проверка передачи пройдена; принятие книги пользователем и итоговый
выпуск ожидаются. Общий ночной прогон продолжается на Fear's Sharp Little Needles.

Исправленная версия Cursed Idol: 81 страница DOCX, единая типографика, исходное
оглавление со ссылками и полный [пакет для вычитки](inputs/cursed-idol/candidates/review-02/PACKAGE_GUIDE.md).
Пользовательская вычитка и выпуск книги ожидаются.

Профиль PDF → DOCX с отдельными заданиями перевода и вычитки реализован:
[команды и схема](docs/five-step-usage.md). Полный пилот на 52-страничном сценарии
Cursed Idol впервые завершён со статусом ready_for_docx_review (исторический r07: 85 страниц DOCX и 74 ассета):
[план](docs/plans/20260919-cursed-idol-pilot/plan.md),
[что автоматизировано](docs/plans/20260919-cursed-idol-pilot/automation-report.md).
Основной результат — DOCX + использованные ассеты. Полный пакет ревью также
содержит оба мастера, исходный PDF, реконструкцию, метаданные MinerU, решения,
настройки и QA с проверяемым инвентарём. Оформление меняется конфигом без
повторного перевода. Исправления после ревью проходят через отдельный `successor`;
предыдущая версия сохраняется. Содержательные задания пока выполняет Codex.

Для исправлений языкового этапа доступно [продолжение от проверенного MASTER_EN](docs/language-continuation.md)
с новым глоссарием и отдельной цепочкой результатов без повторного OCR.

Для уже подготовленной реконструкции доступно [явное продолжение проверки и структуры](docs/review-source-continuation.md):
`continue_review_source verify` проверяет сохранённые авторские файлы, а `structural`
продолжает обработку по проверенному результату. Запрос задаёт точные входы и новые
выходные папки; прежние результаты сохраняются. Управление живыми процессами остаётся
отдельным действием оператора.

Для конфликтующих трёх видов MinerU доступен [механический черновик реконструкции](docs/mechanical-reconstruction.md)
с проверенными по исходнику OCR-исправлениями, сохранением альтернатив и явной
очередью нерешённых вопросов. Он не подменяет принятие реконструкции.

После исправлений реконструкции можно [перенести проверенные ответы в новую очередь](docs/source-choice-rebinding.md).
Скрипт сохраняет только ответы с неизменными исходными и читаемыми фрагментами;
изменившиеся вопросы остаются для проверки.

Для единой пользовательской вычитки в DOCX разрабатываются
[адресные комментарии и перенос нерешённых вопросов](docs/docx-review-comments.md).
Отдельный аннотатор реализован; подключение ко всей цепочке ещё не завершено.

Отчёт о системных изменениях реконструкции, ArtView и публикации:
[`docs/pipeline-change-report-20260919.md`](docs/pipeline-change-report-20260919.md).
Number 7 Dream в нём — проверочный прогон, а не отдельная реализация правил.

## Historical neutral scenario publication control plane — 2026-09-14

The following describes the archived HTML/DOCX/PDF chain, not the current
DOCX-only production route. Its public generation/acceptance commands now fail
before writing; historical package verification remains read-only.

The historically reviewed neutral chain was:

```text
accepted RECONSTRUCTED_EN -> MASTER_EN -> accepted MASTER_EN
-> MASTER_RU packets/submission -> accepted MASTER_RU
-> ArtView bundle -> accepted ArtView decisions -> ArtView apply
-> HTML -> accepted HTML -> DOCX -> accepted DOCX
-> fresh DOCX-exported PDF -> accepted PDF -> production package -> offline verify
```

`python -m kb_creator publication run` and `publication resume` use one fixed
ten-stage registry and advance at most one stage per invocation. They never
infer user acceptance. HTML is generated only after accepted MASTER_RU and
ArtView; DOCX is generated only after accepted HTML; the sole retained PDF is
generated from the exact accepted DOCX. Stage 50 may use a private DOCX-to-PDF
bridge for PNG review, but that PDF and its private/cache state must be deleted
before the stage can succeed.

All task-installed runtimes live under repository `.tools`. Production Python,
Poppler and the optional local LibreOffice fallback must resolve there;
existing PowerShell and Microsoft Word remain the only system-tool exceptions.
Exactly one DOCX/PDF engine is bound into a run: `--word` or
`--libreoffice`. Both Stage 50 review rendering and Stage 60 final export use
the selected engine, while Stage 60 still accepts only the exact accepted
DOCX and never HTML. The production package includes a self-contained HTML
reader with every local runtime asset materialized beside it, ArtView
decisions/application, source and effective
configs, code/schema snapshots, exactly one Stage 60 PDF, and a copied
standard-library-only verifier. Verification can claim only
`candidate_for_release_review`, never release.

The copied offline verifier accepts sealed, fully reviewed ArtView decisions
in schemas v3 and v4; both retain closed-review and exact acceptance checks.
Changing that verifier changes publication identity, so an old package with a
stale copy must be preserved and rebuilt in a fresh run, not patched in place.
Fresh DOCX-to-PDF exports can be visually identical yet byte-different; an
acceptance receipt for an older PDF hash cannot be transferred automatically.

Stage 40 treats every renderer byte as governed implementation. In particular,
`translator/translator.py` is part of the publication implementation inventory,
so a renderer change makes an existing run stale before the next stage can be
accepted. Closed `frontmatter_order` is the authoritative reader order;
legacy credit-position hints are fallback-only. Semantic statblocks are mapped
from accepted reconstruction spans through accepted MASTER_EN and sealed
translation units to exact MASTER_RU ranges, then validated with a nesting-aware
HTML parser as neutral `section.statblock-card` elements. Page-local line
numbers, regex page slicing, title text, and quote presentation are not valid
substitutes for this lineage.

When Stage 40 replaces a source cover page with its required accepted ArtView
binary, semantic projection runs first against the unchanged accepted
`MASTER_RU` line topology. The adapter then refuses to replace a cover page
that owns a projected semantic span and only afterwards substitutes the cover
Markdown. Final cover validation ignores the renderer's own page marker and
`Cover` figcaption, but any other retained visible cover text fails closed.

Visible figure captions are controlled separately from image `alt` text.
`production_html.figure_caption_policy.mode = "authored_only"` removes only
known renderer-generated labels (`Cover`, `Source image from page N`, and
`Исходное изображение со страницы N`) while retaining the same `alt` text for
accessibility and preserving every other, potentially authored, caption.

The DOCX footer policy is explicit configuration. When
`footer.page_numbers` is `false`, the builder emits no footer parts, no `PAGE`
fields and no section footer references; the PDF therefore also has no page
number footer. Dissociation uses this policy from initial DOCX generation,
not as a post-build edit.

The DOCX TOC builder must preserve the accepted HTML's source-owned display
hierarchy. For explicit `data-toc-layout="flat"`, entries remain equal-weight
peers with their original capitalization, even when all links resolve to H1
headings. Numbering is independent of that display style. A DOCX with visible
flat-TOC text differing from the accepted HTML fails generation; legacy
unspecified and hierarchical layouts retain their separate behavior.

If a human reviewer edits an already rendered DOCX, do not mutate or relabel
the completed production package. Use `publication revise-docx` to create a
separate successor bundle. It verifies and embeds the immutable base package,
projects the complete production tree into the successor root, copies the
reviewed DOCX, freshly exports its PDF through the repository-local LibreOffice
engine, renders every PDF page,
checks the footer-free policy and writes a sealed revision manifest plus an
offline verifier. After all page PNGs have been inspected, close the visual
gate with `publication record-revision-review`; verify the final bundle with
`publication verify-revision`. The successor root must directly contain HTML,
its `assets/`, masters, ArtView, configs, acceptance/evidence, DOCX and PDF;
`base_package/` is immutable provenance only. Upgrade a sealed legacy wrapper
without rebuilding DOCX/PDF with `publication materialize-release`. User-facing
links must target the successor root, never an internal stage candidate or its
embedded base-package copy.

An exact human-edited DOCX and its DOCX-derived PDF may be committed under
`inputs/<scenario>/revisions/<revision-id>/` before PDF acceptance only as a
clearly labelled submission and preview. This preservation checkpoint is not
the complete successor bundle or release authority. Its README must record
the input/output hashes and the open visual-review gate. Keep the frozen
`production/` package unchanged, and promote the full verified successor as a
reviewed candidate only after explicit review.

If the DOCX was edited *before* Stage-50 acceptance and before a completed
production package exists, `revise-docx` is not applicable. Start a fresh
publication run; rebind previously accepted upstream inputs under their normal
identity checks, then supply the edited file as the run-local
`--authority reviewed_docx=<run-root>/submissions/.../*.docx` alongside
`html_acceptance` when resuming Stage 50. The generic adapter rebuilds the
accepted HTML baseline for validation, checks the reviewed OOXML package,
copies the reviewed bytes unchanged into the candidate, records their exact
hash and renders the candidate for review. Accept that exact Stage-50 candidate
before Stage 60 exports a new PDF from it. The production package preserves
the reviewed submission and its binding; an edit to the old stage output must
never be silently resealed in place.

On Windows, every real reconstruction replay Stage 06 candidate, publication
stage, reviewed-DOCX successor and release materializer normalizes its newly
materialized tree before success is reported. Stage 06 applies this gate after
the candidate is atomically renamed to its final output path and before its
stage manifest or `candidate_ready_for_reconstruction_qa` result is published;
an ACL failure quarantines a fresh candidate and fails closed. The gate restores
inherited ACLs and adds read/execute access only for the exact desktop principal
from `USERDOMAIN\USERNAME`; it does not grant a broad group, replace existing
ACEs, or change ownership. It then rechecks the deterministic file inventory so
artifact bytes cannot change. A user-owned `.obsidian` directory remains outside
both normalization passes. Isolated test/temp trees outside
`kb_creator/working` record a declared skip. For a sealed run created before
this hook was wired into the materializers, run the reusable repair helper
from repository `.tools`:

```powershell
& ".\.tools\MinerU\.venv\Scripts\python.exe" -B `
  kb_creator\scripts\normalize_publication_access.py `
  <stage-artifacts-directory>
```

The target must be an existing directory below `kb_creator/working`. A
non-Windows host records a declared skip; an ACL failure is an error rather
than a successful-but-unreadable review candidate.

For `Dissociation`, MinerU remains the reconstruction engine on the current
host. The mandatory CPU profile runs `pipeline --method txt` and
`pipeline --method ocr`; a raster-input OCR pass supplies the third independent
view. Local `hybrid-engine`/`vlm-engine` enrichment is capability-optional: when
no supported GPU is present, only that enrichment is recorded as `SKIPPED` and
the CPU reconstruction continues. Remote execution is not an automatic or
permitted fallback. The earlier sealed whole-run skip is immutable historical
evidence and cannot be resumed; implementation must start a fresh CPU-capable
run root. Word is installed on this station, but the current Codex logon returns
`0x80070520` during COM activation. The current-host fallback is the
hash-bound LibreOffice runtime under `.tools`; no remote or GPU host is used.

## Reconstruction text and art tool policy — 2026-09-14

MinerU is the primary semantic reconstruction tool; the other PDF tools provide
independent extraction, geometry, provenance and visual verification. They do
not replace MinerU, and agreement between several tools is stronger evidence
than any single extractor.

### Text extraction

| Tool or mode | Pipeline role |
|---|---|
| MinerU `pipeline --method txt` | Mandatory CPU extraction of the existing PDF text layer and reading order |
| MinerU `pipeline --method ocr` on the immutable source | Mandatory CPU OCR view |
| MinerU `pipeline --method ocr` on the raster derivative | Mandatory independent CPU OCR view that cannot reuse a damaged or interleaved PDF text layer |
| PyMuPDF | Text spans, block coordinates, page geometry and targeted region inspection |
| Poppler `pdftotext` | Independent `-layout`/`-bbox-layout` audit of columns, text and coordinates |
| `pypdf` | Page count, MediaBox/CropBox, rotation, metadata, structural integrity and derived-PDF assembly; not the primary text extractor |
| `pdfplumber` | Additional coordinate-level text and PDF-object inspection |
| Tesseract | Escalation OCR for disputed or missing regions; not a replacement for the mandatory MinerU views |

For ordinary text-bearing PDFs, Tesseract is invoked only when MinerU,
PyMuPDF and Poppler evidence disagrees or leaves a region unresolved. MinerU
`auto` is a selector between text extraction and OCR, not an independent
evidence view; production runs record explicit `txt` and `ocr` choices.

### Art extraction and review

| Tool or mode | Pipeline role |
|---|---|
| MinerU | Extracted image candidates plus layout coordinates and semantic association |
| `pdfplumber` | Raw embedded PDF XObject stream extraction |
| `pypdf` | Independent validation of object identity, subtype, dimensions, masks and decoded data |
| PyMuPDF | Image/xref inventory, direct extraction and precise region rendering |
| Poppler `pdftoppm` | Reference full-page renders and crop candidates |
| Pillow | Soft-mask composition, crops, RGB working copies, multi-object composition and metadata stripping |
| Poppler `pdfimages` | Available lossless embedded-image extractor; supplemental until bound into the generic run |
| Poppler `pdftocairo` | Available alternate renderer for difficult pages; supplemental until bound into the generic run |

Art selection follows a fixed evidence preference:

1. preserve and expose the native PDF XObject when it is complete;
2. validate the object through an independent PDF parser;
3. combine a base object with its soft mask or required native parts when the
   source art is composite;
4. use a deterministic Poppler page crop only when native extraction is not a
   faithful complete image;
5. retain a full-page render as visual context;
6. present all viable candidates through ArtView without inferring acceptance.

Production ArtView v4 is a single deterministic Stage-30 invocation. Its
checked-in profile contains only immutable input identities, an output root,
and render settings; it must not contain authored review rows, page roles, or
scenario-specific exclusion lists. The tool inventories every PDF image
occurrence, records masks as bound technical components, derives page roles
from the sealed reconstruction decision graph, reconciles reader placements
with the accepted `MASTER_RU` asset manifest, and emits one complete review
bundle. A composite cover is represented by a clean full-page render while its
raw objects remain in `source_visual_inventory.json`. Human inclusion and
presentation choices begin only in the generated ArtView page.

The ArtView decision surface uses the image cards themselves as the human
choice control. Clicking the current binary or a candidate gives that card a
green outline, changes the row status to `Выбор сделан`, and records
`reviewed: true`; there is no duplicate binary-decision field or separate
review checkbox. Presentation controls remain independent and do not clear an
existing image choice. The UI does not expose a notes field; exports retain an
empty `notes` value only for decision-schema compatibility. The decision
schema is read from the generated candidate manifest so v3 and v4 pages cannot
silently export the wrong schema version.

The v3/v4 review page also exposes `Импорт прошлого JSON` as a modal workflow.
It accepts only the closed ArtView document shape for the same scenario and
schema, verifies the canonical `decisions_sha256`, rejects duplicate rows and
invalid binary/presentation values, and never treats an unsealed file as
authority. An exact binding match restores all choices, presentation values,
and `reviewed` flags. A JSON from an older candidate may transfer only rows
whose asset and candidate identifiers still exist; all transferred rows have
`reviewed` reset to `false`, so the reviewer must confirm every retained choice
with a fresh image-card click. The dialog reports exact/compatible mode,
transferred count, and skipped rows before applying any state.

`scenario_artview.py rebind-decisions` supports both v3 and v4 successors. A
v4 rebind is allowed only when both profiles validate, the complete ordered
user-visible row graph and decision contract are identical, candidate binary
inventories match their files, and every selected target binary is exactly
equivalent. It rewrites only the target bindings and seal; it does not infer a
new choice or acceptance.

Current ArtView working renders use 200 DPI PNG/RGB for page crops and 120 DPI
page context. Context JPEGs use quality 85 and have metadata stripped. Raw PDF
streams remain provenance evidence; Pillow outputs are working derivatives,
not replacements for immutable source binaries. `pdfimages`, `pdftocairo`,
Poppler text audit and Tesseract are installed capabilities but are not yet all
bound into the neutral production reconstruction run. The generic runner must
record the exact tools, versions, settings and provider-level `SKIPPED` receipts
that were actually used.

CPU-first MinerU children run with a cleared environment. Writable home, user,
application-data, cache and temporary roots are synthesized below
`.tools/MinerU/runtime/<profile>/`; the real Windows user profile and inherited
proxy/API/Python-path settings are not passed through. A nonzero MinerU child
is never converted to a provider skip. Its bounded sanitized closed-invocation
record is written as `failure.json` inside the attempted view, and the control
plane adds a sealed `stage-failure.json`; both remain under the corresponding
run-local `failures/<stage>/` quarantine. On Windows, stdout and stderr go to
per-invocation files below that profile runtime rather than anonymous pipes.
The closed runner assigns the suspended launcher to its own Job Object before
execution, applies a 120-second CLI-surface timeout or six-hour extraction
timeout, and then uses a separate 30-second cleanup timeout to terminate and
verify only descendants owned by that job.
Temporary specs, results and logs are removed after bounded evidence is read;
successful execution requires both a zero launcher exit and an empty owned
process tree.

Wrapper dispatch is explicit: `-ToolRoot` selects the CPU-first provider path
and supports `pipeline_txt`, `pipeline_ocr`, `hybrid_high`, and `vlm_local`.
The compatibility-only `-MinerURoot` path accepts only its historical
`pipeline_ocr` and `hybrid_high` profiles; CPU-first-only profile names fail
before legacy initialization instead of being silently mapped to OCR.

RunSpec v2 candidate materialization takes its comparison authority only from
the sealed review queue. Stage 06 supplies the exact run-local
`outputs/03-compare-views/comparison.json` path and SHA-256 as an all-or-none
pair; the materializer revalidates the complete run, Stage 02-04, visual,
geometry, view-set and per-view receipt graph before creating candidate output.
Every authority path is recursively rejected if any component is a Windows
reparse point (including a symlink, junction or mount point). The historical
`<raw-root>/comparison/comparison.json` fallback remains available only to a
true v1 bundle when both new arguments are omitted.

RunSpec v2 Stage 05 is a source-visible completeness gate, not selected-block
recall alone. It enumerates every non-empty text unit from the three required
CPU views, requires a full-unit selected/equivalent mapping or an exact
identity-bound reviewed exclusion/assertion, and has no short-text exemption.
Stage 06 consumes the exact passing audit path and SHA-256 and records that
identity in merge provenance; promotion and package verification reject a v1,
replaced, incomplete, or authority-stale audit for a v2 run. The selected-only
v1 audit remains available solely through explicit legacy-v1 dispatch.

The opt-in reconstruction decision-set v2 closes semantic-container fidelity
separately from lexical completeness. Every page carries a complete visual
review bound to the exact Stage 04 page render and a typed inventory of
headings, lists, blockquotes/callouts/handouts, and stat blocks. Stage 05 emits
the composed v4 audit only when both the legacy v3 text ledger and the reviewed
Markdown spans/relations pass. Stage 06 repeats the same validation and writes
`SEMANTIC_STRUCTURE.json` beside `RECONSTRUCTED_EN.md`; syntax is validated by
the declared representation, so a missing quote marker on a real blockquote,
a quote marker inside a v2 neutral statblock span, a missing list marker,
heading level, table delimiter, parent/continuation relation, or declared
container boundary fails before materialization. Decision-set v1 and
its v3 audit remain valid historical paths but cannot claim this structural
profile.

The same profile represents visually reviewed compact ordinary-text rows as
`line_group / hard_break_lines`. Ordered source blocks are the grouping and
reading-order authority; one source block may contribute several physical
lines. Authoring canonicalizes every non-final row to an exact two-space
Markdown hard break. Stage 05 and Stage 06 reject blank internal paragraphs,
missing or final-row hard breaks, line-count drift, and reordered source lines.
No label, colon, capitalization, or scenario vocabulary is used to infer a
group. This closes the earlier boundary where scenario decisions could carry
manual hard breaks that downstream projection preserved but reconstruction did
not itself declare or validate.

Exact source-confirmed OCR repairs in this profile use reviewer notes of the
closed form `text correction: <source> -> <reader>; reason: <visual evidence>`.
The selected source form must occur exactly once and the reader form must be
present in the reviewed Markdown. Stage 05 uses that same ledger for lexical
span/OCR-equivalence mapping, while source-unit hashes and comparison evidence
remain unchanged; Stage 06 repeats the semantic check. An unreviewed, stale,
ambiguous, or unused correction fails closed.

Stage 03 now retains exact MinerU v2 table evidence when one v1 table block has
one exact same-page v2 bbox match. Only caption plus parsed `th`/`td` cell text
is retained; image paths, HTML tags, table-type metadata, and nesting metadata
cannot leak into reader text. The raster stays available as provenance. This
signal never infers that a table is a stat block: container typing remains a
closed visual-review decision. A semantic replacement may mark the crop
`reference_only`, preserving evidence without rendering duplicate image text.
Stage 01-04 replay preserves that fact as the closed positive-only
`v2_table_text=true` member of semantic evidence; false values and arbitrary
semantic-evidence keys remain invalid, and replay validates each declared
semantic-conflict variant by its exact shape.

Semantic conflict closure is selection-role aware and remains fail-closed.
`v2_table_text` is table evidence, never title evidence. A title nested in a
reviewed callout is preserved as a typed ATX heading inside its blockquote; a
title inside a v2 statblock remains ordinary ATX Markdown inside the parent
`semantic_span`. A conflicting title signal may be downgraded to ordinary
container content only with an exact source-block binding, an exact
representation-specific rendered line, completed visual review, and an
explicit reasoned review note. An `image_heading_overlap`
is closed only by either a reader-visible selected asset or a `structure`
selection bound to one reviewed blockquote/table/semantic-span unit; an untyped or
`reference_only` asset selection cannot silently resolve it.

Selected structural titles with `v2_title=true`, `markdown_heading=true`, and
`middle_title=false` require an exact reviewed title-evidence confirmation
bound to the source view/raw index and one exact reader ATX heading. If the
reader heading differs from selected source text, the same decision must also
carry the exact reviewed text-correction ledger row. This is a visual-review
gate, not an automatic word-splitting heuristic. The semantic report seals the
source/reader hashes and whether the heading changed.

Under the structural profile, reviewed Markdown may not contain repeated
interior root-level empty lines. The generic author can reduce a known run to
one separator only from an exact declaration naming the complete lines before
and after it and the observed blank count. Missing, ambiguous, duplicate,
overlapping, or undeclared runs fail closed; blockquote blank markers and
hard-break line groups remain untouched.

`MASTER_EN` is not a repair layer for a flattened reconstruction. It may add
publication anchors, navigation, deduplication, and reader policy only after
the accepted reconstruction already contains the reviewed source-visible
container Markdown and sidecar; later HTML/DOCX/PDF stages only style that
structure.

The opt-in successor profile
`reviewed_role_outline_and_partitions_v2` adds role completeness and exact
mixed-block partitions without changing historical v1 decisions. Every page
declares a closed `role_contract`. `character_statistics` pages must enumerate
every top-level statblock together with exactly one first-line contained title.
In this v2 profile a prose-shaped statblock uses `representation=semantic_span`:
its reader Markdown contains no `>` quote markers, while the sidecar seals its
exact first/last lines and hash; a real Markdown table remains valid as a
self-delimiting alternative. Historical v1 blockquote statblocks remain
readable but cannot be authored as new v2 decisions.
`pregenerated_characters` groups must be contiguous, begin with exactly one H1
root, contain exactly one H2 character record per page, and bind all declared
H3 leaf headings to that record. When an OCR block fuses a title and body row,
the reviewed decision records lossless half-open Unicode offsets and hashes for
both fragments; gaps, overlaps, stale bytes, or reader-text loss fail Stage 05
and Stage 06. The generic author can inherit unchanged v1 units but recomputes
all spans, fragments, visuals, and identities against the fresh replay.

HTML-ready publication inputs also use a closed versioned
`html_publication_policy`. The explicit `deferred` state is legal before Stage
40 but is rejected at the Stage 40 boundary. A ready policy declares page
roles, frontmatter order, cover, credits, TOC mode and exact preserved-entry
targets, optional source-owned `display_level` values, a closed TOC
`display_mode`, and the first body page. `display_mode = "flat"` keeps every
source entry at one presentation level; target H1/H2/H3 levels remain link
metadata and must never restyle the preserved source TOC. The adapter verifies both the staged Markdown
page markers and the final DOM/manifest. Semantic statblocks are transported by
adapter-derived paired `semantic-span-start/end` markers around the exact
sealed plain-Markdown range and render as neutral
`section.statblock-card[data-semantic-kind=statblock]`; accepted MASTER text
must not already contain those reserved markers, and neither reconstruction nor
publication may reinterpret a quotation/review callout as a statblock.

Reconstruction promotion dispatches legacy-v1, direct RunSpec v2 and validated
replay-v2 explicitly. Replay promotion consumes the flat Stage 06 candidate,
the v3 fidelity/provenance authorities and the sealed replay bridge; it does not
fall back to direct-v2 when any replay marker is present. Required CPU readiness
remains mandatory, while supported unavailable optional CUDA providers do not
block promotion. Materialization never creates acceptance, and a post-publish
validation failure removes only the exact package created by that invocation.

For a validated replay whose accepted decision set is v2 and fidelity audit is
v4, promotion also validates and copies the Stage 06
`SEMANTIC_STRUCTURE.json`. The sidecar is bound into acceptance evidence, while
the stable public upstream interface remains the same four roles. Required
numbered handouts may be proven by the legacy heading/asset signals or by an
exact full-line `Handout N` caption inside a validated `kind: handout` semantic
span. Promotion never searches arbitrary prose or infers a handout from a unit
identifier. Legacy runs without this structural profile retain their original
shape and behavior.

Page decisions may additionally declare a closed `block_boundaries` list for
source-backed compact structures. The supported `compact` row names one exact
ATX heading and its exact first body line; materialization removes exactly one
empty separator between them while leaving literal text and existing Markdown
hard breaks unchanged. Missing, ambiguous, already compact, multi-empty,
duplicated, unsupported or unknown declarations fail closed. Legacy decisions
remain valid with their original exact key set, and replay promotion accepts
only that legacy shape or the same shape plus `block_boundaries`.

Publication contracts are authored from a closed, scenario-neutral blueprint;
file sizes and SHA-256 identities must not be typed by hand. The author accepts
only seven named config roles plus normalized authority-root-relative
terminology files, validates the generated contract through the production
runtime, and writes only to an absent target:

```powershell
& ".\.tools\MinerU\.venv\Scripts\python.exe" -B `
  kb_creator\scripts\author_scenario_publication_contract.py `
  --blueprint <publication-blueprint.json> `
  --config-root <authority-root> `
  --output <absent-publication-contract.json>
```

This command binds configuration authority only. It does not create or infer
reconstruction, reader, visual, HTML, DOCX, PDF, or release acceptance.

## Viral ArtView v2 review — 2026-09-10

The current portable art-review checkpoint is
`inputs/viral/artview/review_checkpoint_20260909/`. Open
`candidate/artview.html` through a local HTTP server. It contains all 94
traceable reader-art rows and keeps two decisions independent:

- exact binary: current file, extracted direct XObject/page crop/full-page
  render, exclusion, or a workflow escalation;
- presentation: width percentage, left/center/right alignment, prose wrapping,
  and separate table-wrapping permission.

Each regional row now shows four distinct panes in one wide-screen row:
the current reader binary, an independent crop from the rendered PDF page, a
native PDF candidate extracted without MinerU, and the full source-page
context. The direct pane now supports a single XObject, a base image combined
with its PDF soft mask, a deliberately fuller source object, a crop from an
embedded full-page composite, or a review-only composition of several native
objects. Raw source streams and masks remain linked evidence; CMYK samples
receive a browser-safe RGB working binary without changing the source bytes.
Every non-exact route is visibly warning-marked for human review.

The current bundle contains 84 direct-PDF candidates (78 single XObjects,
including 2 soft-mask composites and 1 fuller-art match; 5 crops from embedded
page composites; and 1 multi-XObject composition), 84 page crops, 10
full-page candidates and 82 unique source-page contexts. Current production
state is projected as 78 included, 6 deliberately excluded and 10 absent rows.
The accepted 2026-09-10 review uses body art at 25% right-wrapped, most
handouts/maps at 80% centered, and full-page or pre-generated sheets at 100%
centered, with explicit row-level exceptions preserved in the accepted JSON.

Rebuild from the repository root:

```powershell
python -B kb_creator/scripts/scenario_artview.py build `
  --profile kb_creator/reference/viral/artview_review_policy_v2.json --force
```

ArtView stores browser progress only as a convenience. Export the decisions
JSON regularly. The bundle also contains the empty, hash-bound recovery file
`candidate/artview-decisions.template.json`. Validate any exported document
before it can become an accepted input:

After export, ArtView attempts to copy the exact downloaded filename to the
clipboard and reports it in the page. A portable static page cannot discover
the browser's actual download directory, so it never invents or claims to copy
an absolute filesystem path; the browser remains authoritative for that path.

```powershell
python -B kb_creator/scripts/scenario_artview.py validate-decisions `
  --profile kb_creator/reference/viral/artview_review_policy_v2.json `
  --decisions path/to/artview-decisions.json
```

Add `--require-accepted` only for a reviewed document whose state was explicitly
promoted to `accepted`. Accepted export remains disabled until every row has a
final binary choice and is explicitly marked reviewed. Neither browser state nor
exported JSON changes MASTER or production automatically; materialization is a
separate user-authorized pipeline step. Apply an accepted document without
rewriting either master with:

```powershell
python -B kb_creator/scripts/build_viral_production.py --render-only `
  --artview-decisions kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/artview-decisions.accepted.json
```

This writes a reproducible `ARTVIEW_APPLIED.json` receipt, copies the selected
binaries under `production/assets/artview/`, and generates the derived
`ARTVIEW_RENDER_RU.md`. Later plain `--render-only` runs refresh that projection
from the editable packaged `MASTER_RU.md`; the master files remain untouched.

## Viral MASTER_RU translation — 2026-09-06

The user accepted the independently verified checkpoint-D
[MASTER_EN](inputs/viral/master_en/review_checkpoint_20260905_review_fixes_d/candidate/MASTER_EN.md).
Its content-addressed acceptance receipt is under
`inputs/viral/master_en/accepted_20260906/`. Step 8 now prepares and assembles a
new Russian master from that exact English SHA; historical Viral RU/EN may be
used only for terminology comparison.

Prepare translation packets from the repository root:

```powershell
python kb_creator/scripts/scenario_master_ru.py prepare `
  --scenario-id viral `
  --repo-root . `
  --master-en kb_creator/inputs/viral/master_en/review_checkpoint_20260905_review_fixes_d/candidate/MASTER_EN.md `
  --acceptance kb_creator/inputs/viral/master_en/accepted_20260906/MASTER_EN.acceptance.json `
  --out-dir kb_creator/working/viral/master_ru/20260906_step8
```

Each completed `.ru.json` is checked with `validate-batch`. `assemble` refuses
stale acceptance/source/asset identities, missing or reordered units, changed
anchors/targets/Markdown structure, and altered numeric or dice expressions.
The generated `MASTER_RU.md` must not be edited manually. Final binary art
selection remains Step 8A after RU QA and before HTML.

When a fresh accepted `MASTER_EN` differs from a prior translated packet only
by a proved source-preserving projection, reuse the reviewed translation with
`scenario_master_ru rebind-batches`. The command validates both run-local
packet authorities and carries exact source units by identity. It supports the
two ledger-proved v3 page joins (`dehyphenated_word` and `continued_prose`) and
a closed `markdown_structure_only` projection. The latter requires identical
lexical payload and mechanics and may only change blockquote/ATX-heading
frames, heading levels, or split an inline stat-block title into a new heading
plus its mechanics-bearing row. It projects that shell onto the already
reviewed translation, then requires the complete current Markdown/mechanics
signature to match. Arbitrary wording changes, ambiguous mappings, unused old
units, extra line operations, or unverifiable title splits fail closed. The v2
report records every mapping and payload hash.

The command emits new current-packet `.ru.json` files plus the sealed report
and requires separate `--authority-root` and `--prior-authority-root` values.
Follow it with the normal `author-submission` and `validate-submission`
commands. Do not copy or edit generated batches by hand.

HTML production uses lining numerals (`font-variant-numeric: lining-nums`) for
the reader body and stat blocks. This avoids Georgia old-style figures without
forcing tabular widths in ordinary prose.

## Viral production package

The stable self-contained production output is built under
`kb_creator/inputs/viral/production/`:

```powershell
python -B kb_creator/scripts/build_viral_production.py --force
```

It contains corrected `MASTER_EN.md`, editable `MASTER_RU.md`, every referenced
asset, HTML, PDF, QA evidence, art decisions, build configuration, pipeline
snapshot and a content-addressed manifest. After manually changing bold,
italic, paragraphing or other Markdown formatting in the packaged
`MASTER_RU.md`, rebuild only the derived HTML/PDF without replacing that file:

```powershell
python -B kb_creator/scripts/build_viral_production.py --render-only
```

The render profile deliberately inherits the accepted Innsmouth Terror
production design: A4 palette/framing, Georgia typography (12pt/1.45 reader,
9.75pt/1.24 print), single-column print body, structured statblock cards and
role-aware art sizing. Viral-specific TOC, credits, handout and art decisions
remain explicit in the packaged `build_config.json`.
Narrative body art is a right float at 25% in HTML and PDF. Graphic player
handouts are centered at 80% and bound to their own heading/description on one
print page. Keeper maps, opening pages and character-sheet sides remain
full-page. Generic `Illustration`/`Иллюстрация` captions and explicitly
transcribed phone facsimiles are omitted from reader outputs. These policies
are configured and verified in production QA rather than repaired in the final
PDF.

## Number 7 Dream production candidate

The frozen run30 package is preserved under
`kb_creator/inputs/number-7-dream/production/`. It contains the reader HTML,
20 local assets, reviewed DOCX, PDF, accepted upstream artifacts, provenance,
and a self-contained offline verifier. The package manifest SHA-256 is
`930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8`.
Its state is `candidate_for_release_review`, not a release approval.

Verify the preserved package from the repository root with:

```powershell
python -B kb_creator/inputs/number-7-dream/production/pipeline/verify.py --package-root kb_creator/inputs/number-7-dream/production
```

The ignored `kb_creator/working/number-7-dream/` tree remains separate from
this tracked package. Historical publication runs 01–29 were moved to the
Windows Recycle Bin after their distinct review evidence was archived;
publication run30, reconstruction and translation remain. Do not modify files
inside the frozen package without generating a new manifest-backed candidate.

Byte-distinct earlier user-reviewed exports and their original acceptance
receipts are preserved separately under
`kb_creator/inputs/number-7-dream/review-history/`. Its manifest is historical
provenance, not an alternate current package or release approval.

## Current Innsmouth production package

The canonical unversioned reader and pipeline snapshot is now:

`kb_creator/inputs/innsmouth/production/`

It contains stable `MASTER_EN.md`, `MASTER_RU.md`, HTML and PDF filenames, one
shared asset directory, an exact pipeline/script snapshot and
`PRODUCTION_MANIFEST.json`. Version history remains in Git and manifest hashes,
not in production filenames.

Verify it from the repository root with:

```powershell
python -B kb_creator/scripts/build_innsmouth_production_package.py --verify
```

The older versioned accepted directories remain immutable provenance and
rebuild inputs; they are not the user-facing production package.

`kb_creator` is a new NRI product layer for building and validating structured
knowledge bases from accepted book/scenario artifacts.

This scaffold starts with a frozen Innsmouth Recovery v6 baseline. It does not
clone legacy Translator. It consumes a manifest-defined input contract and must
make every future KB change reproducible from declared sources, configs, and
scripts.

## Current Baseline

- Scenario: `The_Innsmouth_Terror`
- Baseline: Innsmouth Recovery v6
- Freeze manifest:
  `kb_creator/inputs/innsmouth_v6_freeze_manifest.json`
- Verification command:

```powershell
python kb_creator/scripts/check_innsmouth_v6_freeze.py --manifest kb_creator/inputs/innsmouth_v6_freeze_manifest.json --report kb_creator/reports/innsmouth_v6_reproducibility_report.json
```

## Rules

- Canonical English-to-Russian Call of Cthulhu 7e skill names are fixed in
  `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`. Use the
  Hobby World / Hobby Games Russian terminology recorded there; project helper
  databases are indexes, not terminology authorities.
- Do not edit frozen outputs directly.
- Do not cite untracked stale QA reports as freeze evidence.
- New KB logic must either regenerate outputs or produce an explicit
  reproducibility report.
- A changed input, config, generator, QA report, HTML, PDF, KeeperBook, KB file,
  or required image invalidates the current freeze manifest.
- This baseline is frozen for KB work only. It is not production approval.
- Use stable artifact filenames. Do not create new production names by adding
  version suffixes such as `_v2`, `_v3`, or `_final`. Version history belongs in
  Git commits, run ids, manifests, hashes, and reports. If an old version must
  be preserved for forensics, keep it under a run/report/freeze directory with a
  clear preservation note instead of making it the naming pattern for current
  outputs.
- Treat every user-provided pipeline defect example as a seed case for a whole
  defect class until proven otherwise. Close it only through:
  `seed case -> defect class -> full-scope audit -> pipeline fix -> rebuild -> evidence`.
  A visible fix in a final HTML/PDF/KeeperBook artifact is not enough unless the
  upstream rule, script, config, or QA gate makes the result reproducible.

## Local HTML visual verification

Do not open generated HTML through a `file://` URL. The Codex in-app browser
blocks direct local-file navigation by security policy; this is not evidence of
a broken HTML artifact and there is no project setting that should weaken that
policy.

Serve the selected HTML and its sibling assets through the loopback-only preview
script instead:

```powershell
pwsh -File kb_creator/scripts/serve_html_preview.ps1 `
  -HtmlPath kb_creator/inputs/viral/production/Viral_RU.html
```

Then open the printed `http://127.0.0.1:8765/...` URL in the browser. For Codex
automation, keep the returned terminal session id, visually inspect the actual
browser rendering, send `Ctrl+C` to that same session when finished, and verify
that the server exited. Use another `-Port` only when 8765 is already occupied.
Never bind this review server to `0.0.0.0` or leave it running after QA.
