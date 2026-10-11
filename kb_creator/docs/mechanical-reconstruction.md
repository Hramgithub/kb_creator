# Механический черновик реконструкции

Команда читает проверенный Stage 04 и создаёт новый каталог кандидата:

```powershell
python -m kb_creator.scripts.prepare_mineru_mechanical_draft --run-root <reconstruction-root> --bound-reviews <bound-corrections.json> --output <new-candidate>
```

`--bound-reviews` — результат `bind_ocr_reviews`. Загрузчик заново проверяет
исходник, метаданные MinerU, страницы пакетов, отчёты визуальной проверки,
изображения страниц и точные пары `before`/`after`. Подмена текста с пересчётом
хеша самого ledger не заменяет проверку исходного отчёта. Неуказанные или
повторяющиеся исправления запрещены. Использованные свидетельства копируются
в новый кандидат. Источники и прежние кандидаты сохраняются.

## Выбор текста

- Три одинаковые версии дают исходный текст без нормализации.
- При управляющих символах в native TXT допускается совпадающий побайтно текст
  двух OCR-версий. Повреждённая версия остаётся в альтернативных свидетельствах.
- Проверенное по исходной странице исправление имеет приоритет над совпадением
  OCR. В смещениях остаются координаты и хеш **исходного** OCR-текста; результат
  исправления получает отдельный хеш.
- Различия изображений, семантики, порядка чтения, неоднозначное сопоставление
  и небезопасная структура таблицы остаются на проверке. Исправление плоского
  текста не разрешает автоматически менять ячейки исходной HTML-таблицы.
- В версии v3 разрешено только позиционное различие ASCII и типографских
  апострофов или двойных кавычек при одинаковой длине строк и полном совпадении
  остальных символов. В reader-текст выбирается точная native TXT-строка;
  OCR-свидетели сохраняются как `equivalent` и не становятся источником байтов.
- В версии v4 добавлены только два title-like правила: позиционное изменение
  регистра ASCII-букв и удаление одиночных пробелов внутри последовательности
  минимум из четырёх ASCII-заглавных букв. Нативная TXT-строка остаётся точным
  reader-текстом; заголовочная семантика должна быть подтверждена во всех трёх
  блоках.

Контракт результата для новых кандидатов: `mechanical_draft.v4.schema.json`;
исторический `mechanical_draft.v2.schema.json` остаётся неизменным. Каждая исходная пара
`view/raw_index` сохраняется в одной компоненте. Для восстановленного текста
указаны выбранный источник и роли остальных версий. Контрольные символы
запрещены в выдаваемом читателю тексте. Проверяющий код сопоставляет смещения,
хеши, альтернативы, исправления и собранный Markdown.

## Граница этапа

### Нормализация отображения заголовков

Если `sup/sub` в MinerU обозначают переносы строк декоративного заголовка,
можно явно применить политику `flatten_word_wrapped_heading_tags`:

```powershell
python -m kb_creator.scripts.normalize_heading_display --spec <semantic-spec.json> --draft-pages <draft-pages> --packets <merge-packets-pages> --output <new-spec.json> --report <new-report.json>
```

Команда создаёт новую версию спецификации с точными заменами отображения.
Она сверяет заголовок с выбранным исходным блоком, сохраняет исходный текст,
все определения семантических блоков и порядок существующих замен.
Снимаются только парные теги без атрибутов вокруг целых слов. Числовые индексы,
формулы, теги внутри слова и неподдерживаемая разметка остаются неизменными.
Нормализация применяется как выбранная для книги политика оформления после
проверки характера разметки; она не доказывает, что любой `sup/sub` является
ошибкой OCR. Отчёт содержит исходные ключи, хеши и изменения; принятие книги
или просмотр всех страниц этим действием не отмечаются.

### Результат черновика

Это черновик с явной очередью нерешённых вопросов. Он не даёт принятия
реконструкции, не создаёт `MASTER_EN` и не отмечает страницы просмотренными.
Дальше требуются решения по структуре и оставшимся расхождениям, проверка
полноты относительно PDF и штатное создание мастера.

Исторический контракт v1 сохранён для ранее выпущенных кандидатов. Существующие
каталоги результатов не перезаписываются.

## Historical producer changes

A replay-hybrid Stage04 is consumed through `validate_replay_artifacts_for_consumption`.
It validates archived inputs, complete artifacts and seals while reporting current
producer freshness separately. This permits reading an intact old OCR result after
a diagnostic wrapper change, without granting resume or re-execution authority.
Fully replayed Stage04 still uses its strict validator. Native consumption checks
the sealed run, bound root and current source/contract bytes before stage artifacts.
A corrupt replay never falls back to native. Source-key conservation also checks
held and empty components against the exact Stage04 packet inventory.

## Привязка транскрипций к фактическим файлам

После визуального чтения региона сохраните его точную транскрипцию и исходный
ключ в наблюдениях. Смещения и хеши вычисляет общий инструмент:

```powershell
python -m kb_creator.scripts.bind_source_observations --run <reconstruction-run> --source <source.pdf> --drafts <reviewed-drafts> --observations <observations.json> --output <new-bound-observations.json>
```

Инструмент проверяет идентичность PDF, получает текст/координаты по ключу из
пакета и заново вычисляет хеши. Полное совпадение транскрипции ищется в Markdown
той же и непосредственно предыдущей страницы; совпадения только начала фразы,
повторы и различия пунктуации остаются явно неразрешёнными. Для кандидата нужен
также единственный выбранный исходный блок с точным текстом. Существующий файл
результата не перезаписывается.

Это проверка байтов и совпадений в исходном Markdown. Она не подтверждает
визуальный просмотр, точность самой транскрипции, видимость текста после
рендеринга, актуальность кода старого прогона или полноту реконструкции. Эти
проверки выполняются при проверке источников и итогового документа.

## Перенос привязок после повторной сборки Stage04

Если новый архивный прогон сохранил байты всех пакетов страниц и исходных
визуализаций, используйте общий перенос привязок:

```powershell
python -m kb_creator.scripts.rebind_staging_ledger --prior-run <старый-прогон> --target-run <новый-прогон> --ledger <старый-ledger.json> --review-root <reviewed> --output <новая-папка>
```

Команда проверяет происхождение старого прогона, актуальность нового, одинаковый
источник, роли и полный набор страниц; повторно сверяет пакеты, изображения,
черновики, записи проверки и спецификации. Она меняет только привязку очереди в
новом `ledger.json` и сохраняет `rebind-report.json`. Старые файлы остаются прежними.
Изменённый текст, изображения или состав страниц требуют новой подготовки.

Результат имеет статус `candidate_only`. Затем обязателен обычный
`stage_reviewed_drafts` с новым прогоном и новым ledger; перенос сам по себе не
закрывает нерешённые компоненты и не подтверждает вычитку или полноту книги.
# Reviewed prose with OCR line wraps

An ordinary-prose selector in `reviewed_prose_bindings_v1` may explicitly set
`"source_layout": "soft_wrapped_paragraph_v1"` when one source paragraph contains
OCR line breaks. The default still requires a single source line. Blank lines,
list/heading/quote/table/code syntax and indented code are rejected by this option.

The option validates source shape; it does not join lines or repair words. Authored
`reviewed_block_corrections` must explicitly produce the complete single-line reader
paragraph, including every required initial and interior repair. Source hashes and
correction offsets remain bound to original bytes, including newlines. The reader
must match that complete corrected paragraph exactly. When an initial is included
in the full-block correction, remove the separate initial assertion only in the new
successor spec so the same character is not attributed twice.

## Reviewed cover-label partitions

A corrected complete source block may declare multiple `label/semantic_span`
units with explicit `source_fragments`. Preparation retains the selected source
anchor only when the declared owners partition the entire source without gaps
or overlaps. Final authoring rebinds all selectors to immutable packet hashes.

`reviewed_label_partition_v1` replays each reviewed correction within its exact
fragment and verifies a sealed single-line label. Only whitespace at fragment
boundaries is removed; labels must follow source order, separated by one blank
line. Another semantic owner or other content inside that envelope is rejected.
MASTER and fresh queue reuse the same proof. Non-selected OCR alternatives retain
their own raw text. This route covers corrected complete blocks; partial source
issues, cross-column moves and other presentation kinds need separate proof.

## Regions with empty OCR

`preparation-report.json` retains the exact packet witnesses, geometry and block
types for `excluded_empty_sources`. `all_three_views_empty_count` counts regions
whose matched texts are explicitly empty in all three views; missing views do not
qualify. Their `source_content_verification` remains `unverified_from_empty_ocr`.
An empty recognition result does not establish that the PDF region contains no text.
Equal empty readings do not produce a lexical-choice row. Source visual coverage
must therefore account for these regions separately, restoring missed text or
retaining an appropriate graphic/attention record. The report is evidence for that
review, not an automatic missing-text verdict or proof of source completeness.

`python -m kb_creator.scripts.build_empty_region_visual_review` builds source crops
and numbered contact sheets from these observations. Supply `--observations`
(the preparation report, or a report with `rows`), `--source`, `--source-sha256`,
`--packets` (the Stage04 packet pages directory), `--renderer` (pdftoppm), and a
new `--output` directory. The tool checks each selected empty witness against its
packet and renders each required PDF page once. It supports unrotated pages with
equal CropBox/MediaBox and UserUnit 1; other coordinate frames are rejected.
Red rectangles identify OCR regions; surrounding pixels provide context. Original
crops, input identities and source render facts are recorded in `manifest.json`.
Every region stays `pending_visual_review`; the generator does not decide whether
text is missing, whether a graphic is retained, or whether the book is complete.

`python -m kb_creator.scripts.probe_empty_region_coverage --visual-manifest ...
--triage ... --drafts ... --packets ... --output ...` records local witnesses for
visually chosen excerpts. The triage JSON must contain one `rows` entry per
`region_id`, with an `excerpts` list. Only whitespace is collapsed. Searches are
limited to the source page and its two neighbors; matches retain exact original
character offsets and input hashes. This distinguishes candidate merged text from
potential omissions without accepting a distant repeated handout as local coverage.
An excerpt match alone does not close the whole region or its layout/graphics QA.

### Reviewed transcription of an empty text region

For a visually inspected text/title block whose raw text is exactly empty,
`empty_source_selections` adds the explicit `{view, raw_index}` as `structure`.
The page spec supplies a semantic unit with that one source key, no fabricated
source fragments, and one `visual_assertion_ids` entry. The visual assertion uses
`relation: within_selected_empty_text_region`, `empty_source: {view_id, raw_index}`,
the exact packet `bbox`, the visible `text`, and a review rationale.

Authoring binds the empty raw hash, exact source block/page/view/bbox, Stage04 page
visual identity and one exact normalized Markdown span. The visible-text verifier
also checks the transcription, including punctuation, in the unit's actual reader
span; hidden link targets do not qualify. A single semantic owner is required.
Missing, nonempty, ambiguous, stale or differently selected sources are rejected.
Stage05 includes the assertion in its coverage stream, and Stage06/MASTER retain
the semantic representation. No nonempty OCR reading or lexical choice is invented.
Source order/presentation remains an explicit reviewed book decision. A required
source graphic must still be bound separately; transcription does not supply it.

### Corrected multiline quote payloads

A complete selected OCR block may be corrected into a reviewed handout, quote or
callout with multiple paragraphs. Represent every payload line with `> ` and an
empty paragraph separator with `>`; preserve speaker labels and clipped endings.
The sole semantic owner must bind one complete source fragment and an exact
sealed reader span. `reviewed_quote_container_v1` reproduces those quote markers
for MASTER and the source-choice queue without treating them as raw OCR text.

Alternative readings retain the quote container. A freshly verified v2 ledger
may replace the complete payload; it supersedes the earlier visual correction
only for that proved whole-source quote. It does not relax partial-source or
other overlapping correction rules. Successor preparation also rebinds following
prose selectors by sealed coordinates when a replacement changes the line count.
Full source fidelity, source graphics, final DOCX and release remain separate gates.


### Source graphic review and page text review

A source-page facsimile has a separate closed visual decision bound to the exact
PDF, page, renderer, dimensions and bytes. Its graphic review does not require or
change the page's reconstruction review flag. Stage05 rerenders and compares the
asset; Stage06 requires its matching Stage05 proof. A review draft may therefore
retain a reviewed source graphic while its text remains unreviewed. Strict author
ingress, final review-draft evidence, DOCX text/visual QA and release gates retain
their separate requirements. A missing or false graphic decision still fails.

Asset placement selectors are now applied identically in semantic preflight and
authoring. The early check catches an inline graphic outside its owning semantic
span; it does not render or certify final DOCX layout.
