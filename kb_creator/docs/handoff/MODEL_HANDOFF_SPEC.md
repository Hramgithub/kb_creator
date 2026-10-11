# KB Creator — operational handoff specification

- Версия: `2026-10-11.1`.
- Целевая аудитория: новая модель-оркестратор, включая Claude Opus 5.5.
- Статус документа: handoff candidate; не является release acceptance кода
  или книг.

Краткое введение: [MODEL_HANDOFF_SUMMARY.md](MODEL_HANDOFF_SUMMARY.md).

## 1. Идентичность и границы снимка

| Поле | Значение |
|---|---|
| GitHub | `https://github.com/Hramgithub/kb_creator.git` |
| Branch | `main` |
| Проверенная база | `141758c2d7e67acde0f4a9f28b2822379e3f5a18` |
| Импорт | 3015 tracked paths/index entries из NRI после исключения 28 файлов `kb_creator/working/**` и двух исторических generated PDF |
| LFS | 213 отслеживаемых путей; локальный `git lfs fsck` прошёл перед публикацией |
| Безопасность | явные шаблоны токенов, cloud keys и private keys не найдены перед push |
| Текущая задача | очищенный standalone baseline и handoff; сборка книги не входит в scope |

Первоначальный import содержал два обычных PDF примерно 61–62 MiB в
`kb_creator/output/innsmouth_*`. После отдельного пользовательского решения они
удалены из очищенной reachable history как воспроизводимые исторические outputs.
Связанные reports/manifests сохранены как evidence и могут ссылаться на уже
отсутствующие binary artifacts. Default-deny allowlist вместе с общими
`*.pdf`/`*.PDF` правилами в `.gitignore` предотвращает их случайное повторное
добавление; явно разрешённые accepted/production PDF под `kb_creator/inputs/`
и `deliverables/latest/` остаются отслеживаемыми.

Новый репозиторий начинается с одного очищенного root import commit. Детальная
история решений остаётся в документах и исходном NRI Git history; `git log`
standalone не заменяет эту историю.

## 2. Модель источников истины

При конфликте использовать такой приоритет:

1. прямое актуальное решение пользователя;
2. текущий goal `plan.md` / `context.md` и его замороженный `release.md`;
3. верхние текущие разделы `PROJECT_STATUS.md`;
4. manifest/receipt точного артефакта;
5. README и тематические docs;
6. старые goal packets, historical checkpoints и комментарии в legacy-коде.

Применение к текущему снимку:

- цель `20261004-user-docx-review` завершена 5 октября;
- ранние записи внутри её `context.md`, где QA или critic ещё активны,
  исторические и superseded верхним authoritative checkpoint;
- `deliverables/latest/MANIFEST.json` пригоден для байтового inventory, но его
  текстовые state labels не являются актуальным orchestration status;
- README-фраза о том, что октябрьские кандидаты «пока проходят проверки»,
  устарела относительно completed plan/context/release;
- ссылки на corrected successors в `deliverables/latest/README_RU.md` битые в
  standalone, потому что `working/` намеренно исключён.

## 3. Определение продукта

KB Creator преобразует неизменяемый PDF и явные решения ревью в проверяемые
структурированные артефакты и русский DOCX.

```mermaid
flowchart LR
    PDF[Immutable source PDF] --> SRC[Source identity + all-page review]
    SRC --> REC[Three-view reconstruction]
    REC --> MEN[Accepted reconstruction / MASTER_EN]
    MEN --> DRAFT[Documentary RU draft]
    DRAFT --> MRU[Proofread MASTER_RU]
    MRU --> PLAN[Reader options + fidelity plan]
    PLAN --> DOCX[DOCX + assets]
    DOCX --> TEXT[Full visible-text review]
    TEXT --> VIS[All-page visual review]
    VIS --> READY[ready_for_docx_review]
    READY --> HUMAN[User proofreading / separate acceptance]
```

Конвейер не содержит встроенного LLM backend. Он создаёт задания и шаблоны,
которые выполняет человек или внешний агент; затем проверяет submission.

### Не является продуктом

- автоматическое принятие OCR или перевода;
- автоматическая публикация книги;
- общий конвертер всех игровых систем и редакций;
- хранилище секретов или cloud credentials;
- daemon/web API;
- гарантия, что любой исторический пакет можно продолжить на новом хосте;
- возможность вывести отсутствие иллюстраций из пустого списка machine hits.

## 4. Архитектурные контуры

### 4.1 Ordinary five-step PDF→DOCX v3

- Точка входа: `python -m kb_creator translate ...`.
- Оркестратор: `kb_creator/pipeline/five_step.py`.
- Схема состояния: `kb_creator.five_step_run.v3`.
- Профиль: `five_step_docx_v3`.

| Шаг | Вход | Содержательная работа | Результат/граница |
|---|---|---|---|
| 1. reconstruction | PDF, contract, source inventory/review, runtime | сравнение представлений, постраничные решения | проверенная реконструкция и source evidence |
| 2. MASTER_EN | принятая реконструкция | только разрешённая проекция/структура | `MASTER_EN.md`, spans, inventory |
| 3. documentary draft | MASTER_EN, glossary | точный документальный перевод | draft RU + proofreading task |
| 4. proofread final | EN/RU units и решения | литературная вычитка с ledger | `MASTER_RU.md` + projection |
| 5. DOCX | MASTER_RU, reader options, fidelity plan, style config | reader projection, Word build, text/page review | DOCX + assets; `ready_for_docx_review` после закрытия проверок |

`resume` может выполнить несколько чисто механических переходов, но всегда
останавливается на следующем содержательном задании. Пять шагов не означают
ровно пять команд.

Новый v3 package не содержит опубликованный HTML или PDF. Внутренний HTML/DOM
может использоваться как транспорт к Word builder. Служебный PDF bridge может
временно применяться для рендера PNG, но удаляется и не становится deliverable.

### 4.2 Reconstruction control plane

Ключевые модули: `pipeline/reconstruction.py` и
`pipeline/mineru_cpu_first.py`. Контроллер поддерживает две явно различимые
ветви:

- legacy `kb_creator.run_spec.v1` с профилем `mineru_three_view_v1`;
- CPU-first `kb_creator.run_spec.v2` / `.v3` / `.v4` с профилем
  `mineru_cpu_first_three_view_v1`.

Фактические contract revision, run schema и profile выбирают ветвь; нельзя
выводить её из имени каталога или старого примера команды. Current five-step
intake предлагает базовый совместимый шаблон и отдельный шаблон revision 3;
если выбран revision 3, reconstruction controller выбирает CPU-first run
schema v4. Обе ветви используют шесть смысловых стадий:

1. `prepare_inputs`;
2. `mineru_three_view`;
3. `compare_views`;
4. `visual_merge_bundle`;
5. `fidelity_audit`;
6. `materialize_candidate`.

Первые четыре выполняются через `run`, последние два — после закрытых решений
через `resume`. Успешная материализация возвращает
`candidate_ready_for_reconstruction_qa`, а не acceptance.

Для CPU-first обязательны три CPU pipeline views:

- MinerU text-layer extraction;
- MinerU OCR исходного PDF;
- MinerU OCR raster derivative;

CUDA hybrid/VLM views являются только capability-optional enrichment. Их
отсутствие допустимо лишь с документированной поддерживаемой причиной
недоступности и не разрешает remote fallback. Недоступный optional provider не
создаёт acceptance и не отменяет три обязательных CPU views.

Дополнительные независимые доказательства:

- PyMuPDF/Poppler/pdfplumber/pypdf как независимые геометрические и структурные
  доказательства;
- Tesseract только для спорных или отсутствующих областей.

### 4.3 Replay, recovery и promotion

Модули `reconstruction_replay*.py`, `reconstruction_promotion.py` и
`mineru_view_recovery*.py` позволяют сохранять дорогие проверенные этапы.
Повторное использование разрешено только при совпадении source, contract,
implementation inventory, tool identities и upstream bytes.

Правила:

- старый каталог не продолжать на месте после несовместимого изменения;
- создавать fresh run root;
- неизменяемые решения переносить только через проверенный rebind;
- materialization не создаёт acceptance;
- acceptance записывается отдельной операцией и требует явного решения.

### 4.4 Language и reader continuation

Модули `continue_language.py`, `continue_review_source.py`,
`continue_source_choices.py`, `continue_docx.py` сохраняют проверенный upstream
без повторного OCR. Использовать их, когда идентичности подтверждены. Если
источник, контекст или единица изменились, соответствующее решение остаётся
открытым.

### 4.5 Preserved reviewed-DOCX successor

Для правок уже проверенного DOCX есть отдельный bounded route:

- `scripts/revise_reviewed_docx.py`;
- `pipeline/reviewed_docx_revision.py`;
- `docs/reviewed-docx-revision.md`.

Он сохраняет original DOCX, комментарии, media и неуказанные OOXML части,
применяет конечный список точных операций и создаёт новый versioned successor.
Этот путь честно помечает отсутствие lost-master replay и не выдаёт себя за
полную пересборку с PDF.

### 4.6 Historical publication control plane

`pipeline/publication.py` описывает десять исторических стадий:

`MASTER_EN candidate → MASTER_RU packets → MASTER_RU candidate → ArtView bundle
→ ArtView apply → HTML → DOCX → PDF → production package → offline verify`.

Кандидаты требовали отдельного acceptance на MASTER_EN, MASTER_RU, ArtView,
HTML, DOCX и PDF. Offline verify мог вернуть только
`candidate_for_release_review` / `not_reviewed`.

Текущий код вызывает `reject_legacy_publication_writer()` для writer и
acceptance команд до записи. Допустима read-only проверка сохранённых пакетов.

## 5. State machine и язык статусов

| Состояние | Что доказано | Что не доказано |
|---|---|---|
| `needs_agent_work` | механика дошла до содержательного задания | решение задания |
| `candidate_ready_for_reconstruction_qa` | reconstruction candidate materialized | принятие реконструкции |
| `needs_output_review` / `needs_visual_review` | механическая структура построена | видимость и качество всех страниц |
| `ready_for_docx_review` | закрыты предусмотренные text/visual gates точного DOCX | пользовательская вычитка/принятие |
| `candidate_for_release_review` | package self-check прошёл | release approval |
| `approved within declared scope` | independent critic не нашёл blocker в замороженной области | качество вне scope и user acceptance |
| `accepted` receipt | явное решение на точный candidate/evidence | автоматическое принятие последующих байтов |

Любое изменение frozen implementation, authority, config, candidate bytes или
manifest инвалидирует относящийся к нему review.

## 6. Контракты и неизменяемые инварианты

### Идентичность

- canonical JSON: UTF-8, sorted keys, compact separators, `ensure_ascii=False`;
- SHA-256 в проектных manifests обычно uppercase;
- seal вычисляется без собственного digest field;
- inventory должен обнаруживать missing, changed и unexpected files;
- path traversal, symlinks/reparse points и выход из разрешённого root должны
  fail closed.

### Source fidelity

- `Source/` и оригинальные PDF/images неизменяемы;
- physical PDF page и printed folio — разные координаты;
- heading levels, bold, italic, quotes, lists, tables, statblocks/cards и page
  markers сохраняются, когда нужны для traceability;
- пустой machine image inventory не доказывает отсутствие арта;
- одинаковый image hash не объединяет разные occurrences;
- OCR corrections требуют exact source evidence.

### Language fidelity

- `MASTER_EN` и `MASTER_RU` имеют unit identity и проверяемый порядок;
- числа, dice expressions, Markdown structure и anchors нельзя менять
  незаявленно;
- CoC terminology разрешается принятой строкой канонического CSV или закрытым
  book overlay;
- editorial/primary-rule исключения без machine-resolvable authority остаются
  `needs_decision`;
- обновление общего словаря не переписывает уже sealed run.

### Reader/DOCX fidelity

- reader options меняют представление, а не master text;
- все operations привязаны к точным entity/field/page/hash boundaries;
- numeric conversion выбирает весь operand возле нужного field label, не часть
  числа;
- comments, relationships, media, styles и undeclared OOXML content сохраняются;
- полный visible-text review и all-page visual review привязаны к точным байтам
  DOCX;
- XML/mechanical checks не заменяют визуальную проверку.

### Acceptance

- acceptance не выводится автоматически;
- recorder role и user-decision reference обязательны там, где контракт
  записывает acceptance;
- acceptance старого hash не переносится на новый export;
- technical release review не означает принятие книги пользователем.

## 7. Структура репозитория

Корень намеренно содержит вложенный Python package `kb_creator/`, чтобы
сохранить исторические пути `.gitattributes`/LFS и кодовые предположения.
Счётчики ниже зафиксированы для очищенного import baseline `141758c`, до
добавления этих handoff/goal-документов отдельным коммитом.

| Путь | Примерный объём | Назначение |
|---|---:|---|
| `.gitattributes` | 1 | text/binary/LFS и exact-byte policies |
| `.gitignore` | 1 | default-deny/allowlist и исключение runtime/temp |
| `kb_creator/__main__.py` | 1 | основной CLI |
| `kb_creator/pipeline/` | 89 Python modules | state machines, validation, replay, language, reader и DOCX logic |
| `kb_creator/scripts/` | 94 Python scripts + PowerShell helpers | bounded commands, builders, audits, scenario adapters |
| `kb_creator/contracts/` | 92 JSON files | schemas и scenario/run contracts |
| `kb_creator/tests/` | 242 tracked paths; 224 `test_*.py` | pytest/unittest, regressions и adversarial gates |
| `kb_creator/docs/` | 1209 tracked paths | operating docs, goal plans, receipts и historical evidence |
| `kb_creator/inputs/` | 851 tracked paths | frozen inputs/candidates для Dissociation, Innsmouth, Number 7 Dream, Viral |
| `kb_creator/deliverables/latest/` | 210 tracked paths | шесть reviewed DOCX + assets + inventory |
| `kb_creator/reports/` | 207 tracked paths | checkpoints, transfer/recovery evidence, QA summaries |
| `kb_creator/reference/` | 5 tracked paths | reusable config/reference policies |
| `kb_creator/output/`, `pdf_raw/` | 3 и 5 paths | малые исторические Innsmouth outputs/raw evidence; два generated PDF удалены |
| `kb_creator/PROJECT_STATUS.md` | 5148 lines | rollup + длинная reverse-chronological history; читать сверху |

### Как выбирать код

- Начинать с `__main__.py` и соответствующего control-plane module.
- `pipeline/` предпочтительнее scenario-specific scripts.
- `scripts/` сначала классифицировать: current generic, historical adapter или
  one-off evidence tool.
- `contracts/` определяют допустимую форму данных; docs не могут ослабить код.
- `inputs/production` и revision packages не править на месте.
- `reports/` и старые handoffs — evidence, не автоматически current state.

## 8. Технологии и зачем они нужны

| Технология | Роль |
|---|---|
| Python | control planes, manifests, hashing, parsers, Word/PDF logic, tests |
| PowerShell | Windows process isolation, MinerU runner, Word/LibreOffice bridge, ACL handling |
| JSON + JSON Schema | versioned contracts, sealed task/submission/receipt data |
| SHA-256 + deterministic inventory | immutable lineage и проверка переноса |
| Git + Git LFS | история кода и транспорт крупных DOCX/PDF/images |
| MinerU | primary semantic extraction и OCR views |
| PyMuPDF | text spans, xref/image inventory, geometry, targeted renders |
| Poppler | independent text/layout audit, page renders, image/cairo helpers |
| pypdf | page boxes/rotation/metadata/structure и derived-PDF assembly |
| pdfplumber | coordinate-level text и raw PDF object inspection |
| Pillow | masks, crops, compositions, RGB copies, metadata stripping |
| Tesseract | escalation OCR для спорных областей |
| python-docx + lxml | editable Word generation и exact OOXML inspection |
| HTML/CSS/JS | исторический reader, ArtView и internal DOM transport |
| Microsoft Word COM / LibreOffice | service render DOCX→temporary PDF→PNG для visual QA |
| pytest + unittest | regression, property-like negative cases и contract gates |

Репозиторий не содержит root `pyproject.toml`, requirements lock или `.tools`.
Версии и runtime paths должны быть восстановлены отдельной hardening-задачей;
не устанавливать «последние версии» без фиксации и smoke tests.

## 9. Что присутствует по сценариям

В `inputs/` есть четыре верхнеуровневых сценария:

- `innsmouth`: ранний baseline и production lineage;
- `viral`: reconstruction, MASTER_EN/RU, ArtView и production evidence;
- `dissociation`: neutral pipeline/replay/publication contracts;
- `number-7-dream`: production candidate, review history и revisions.

Отдельно в `deliverables/latest/` сохранены шесть reviewed DOCX и assets,
включая Cursed Idol, Secrets of the Kremlin, Shadows of Leningrad, Fear's Sharp
Little Needles, Number 7 Dream и Dissociation.

Три corrected successors из цели 5 октября отсутствуют в standalone:

- Fear SHA-256 `D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E`;
- Leningrad SHA-256 `CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23`;
- Kremlin SHA-256 `5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8`.

Эти hash являются historical evidence, не доказательством наличия payload.
Нельзя переименовать reviewed originals в corrected successors.

## 10. Текущее доказанное состояние

### Унаследовано из NRI

- goal `20261004-user-docx-review` completed within declared scope;
- технический freeze v02/U8v04 получил independent approval;
- исторически: 239 tests + 14 subtests, один pre-existing separate-PDF COM skip,
  48 focused tests, 38 critic cases;
- исторически проверены 367 страниц corrected candidates;
- шесть reviewed originals сохранены;
- новые OCR и перевод для этой цели были вне scope;
- user book acceptance не inferred.

### Свежо проверено для standalone extraction

- очищенный root import локально зафиксирован как `141758c`; соответствие
  опубликованному `origin/main` устанавливается только финальным release
  receipt после guarded push;
- working tree был clean до начала handoff;
- 3015 tracked paths/index entries в очищенном root import соответствуют NRI
  HEAD после исключения `kb_creator/working/**` и двух generated output PDF;
- LFS fsck прошёл;
- secret-pattern scan не нашёл явных ключей;
- CLI help прошёл под внешним bundled Python;
- импорт DOCX v3 route падает на отсутствующем `translator`;
- полноценная test suite или build в standalone не запускались.

Нельзя смешивать эти два набора доказательств. Октябрьские test/page counts не
являются свежей проверкой текущего extracted tree.

## 11. Standalone gaps и blockers

| Gap | Влияние | Безопасное решение |
|---|---|---|
| отсутствует top-level `translator/` | DOCX v3 imports fail | vendor/refactor exact dependency с regression comparison |
| отсутствует `CoC/Project_Reference/...csv` | default CoC glossary authority недоступна | versioned snapshot/provenance или обязательный `--shared-registry` |
| отсутствует `.tools` | MinerU/Poppler/LibreOffice identities и runtime paths не воспроизводятся | documented bootstrap + pinned tool manifest |
| отсутствуют governance/layout rules | новая модель не получает правила ролей/layout из Git | добавить project-local policy после review |
| нет dependency manifest | clean Python environment не воспроизводим | `pyproject.toml`/lock с tested versions |
| отсутствует `working/` | старые runs и три corrected DOCX недоступны | восстановить exact payload в stable checkpoint либо исправить docs |
| stale README/manifest state labels | модель может возобновить завершённую цель или обещать отсутствующий artifact | обновить docs без переписывания historical receipts |
| root commit без старой Git history | `git log` не объясняет решения | сохранять этот handoff и ссылки на historical plans; при необходимости импортировать provenance отдельно |

Также в docs есть host-specific пути (`D:/NRI`, Yandex.Disk, `.tools`). Это
исторические доказательства, не переносимые команды.

## 12. Безопасный bootstrap новой модели

1. Убедиться, что checkout находится на ожидаемой ветке и нет чужих изменений.
2. Выполнить `git lfs pull`; проверить, что крупные artifacts не pointers.
3. Прочитать summary/spec и только current sections status/goal.
4. Создать новый goal bundle до multi-stage work.
5. Зафиксировать, какие external dependencies реально доступны на новом host.
6. Не добавлять source PDF, credentials или runtime tools без проверки
   provenance, rights, размера и commit scope.
7. Сначала закрыть standalone gaps; затем выбрать один маленький smoke scenario.
8. Запускать в новом отсутствующем run root; старые outputs не перезаписывать.
9. Сохранить exact commands, interpreter/tool identities, test counts и hashes.
10. Перед release получить bounded QA и независимого critic, не участвовавшего
    в implementation/material design.

### Минимальные проверки bootstrap

Сначала выполнить проверки, которые не должны материализовать или исправлять
Git/LFS payloads:

```powershell
git status --short --branch
python -B -m kb_creator --help
python -B -m kb_creator doctor --json
```

Затем, только после проверки исходного состояния checkout, материализовать LFS
payloads, проверить их целостность и снова проверить статус:

```powershell
git lfs pull
git lfs fsck
git status --short --branch
```

`git lfs pull` скачивает и записывает содержимое working tree; это не read-only
операция. `git lfs fsck` при обнаружении повреждения может переместить объект в
`.git/lfs/bad`; поэтому эта проверка тоже не гарантированно read-only.

`doctor` сейчас сообщает только готовность к explicit tool preflight; он не
доказывает наличие MinerU, Poppler, Word/LibreOffice, glossary или translator.

### Команды, которые не надо запускать как writers

```text
python -m kb_creator publication run
python -m kb_creator publication resume
python -m kb_creator publication record-acceptance
python -m kb_creator publication revise-docx
```

Текущий код должен отвергнуть их до записи. Не обходить этот guard прямым
вызовом старого adapter/helper.

## 13. Рекомендуемая standalone-hardening specification

### Цель

Сделать clone `Hramgithub/kb_creator` воспроизводимо запускаемым для current
DOCX v3 route без неявного доступа к NRI checkout.

### Обязательные результаты

1. Локальные `AGENTS.md`/governance/layout rules с ясной областью применения.
2. Python project/dependency declaration и tested interpreter matrix.
3. Явный tool manifest для MinerU, Poppler, renderer и optional OCR helpers.
4. Закрытая стратегия `translator`: exact vendoring либо выделение нужных
   функций в KB Creator с byte/behavior regression tests.
5. Канонический CoC registry snapshot или обязательный external authority
   binding с identity receipt.
6. Исправленный `deliverables/latest` без ссылок на отсутствующий `working`.
7. Stable immutable checkpoint для трёх corrected DOCX, если exact payload
   доступен и пользователь разрешает публикацию.
8. Clean-environment import/CLI/tests и малый fresh DOCX-only smoke run.
9. Обновлённые README/status с разделением current vs historical.
10. Independent architecture/implementation/release review.

### Acceptance gates

- import выполняется без NRI в `PYTHONPATH`;
- все external bytes/versions/authorities перечислены и проверяются;
- missing input/authority падает до создания output root;
- retired publication writers остаются заблокированы;
- relevant existing tests и new portability tests проходят;
- smoke run не создаёт published HTML/PDF;
- source/master/original DOCX hashes не меняются;
- exact new DOCX проходит text review и all-page visual review;
- working/temp/logs/screenshots не входят в commit.

## 14. Протокол работы новой модели

### Перед изменением

- сформулировать defect class, а не чинить один видимый пример;
- найти earliest failing layer: source reconstruction, translation,
  projection, rendering, asset placement или packaging;
- определить immutable inputs и expected outputs;
- проверить актуальный goal и scope authority;
- перечислить files/modules, которыми будет владеть изменение.

### Во время изменения

- предпочитать generic contract/script/test вместо scenario-specific patch;
- создавать новый output root;
- не редактировать receipts и sealed manifests;
- сохранять Russian text/filenames/terminology без явного задания на правку;
- обновлять tests при reusable code change;
- записывать evidence компактно, не сохранять raw model transcripts.

### Перед завершением

- выполнить full-scope audit аналогичных случаев;
- пересобрать затронутый artifact, если менялась producer logic;
- проверить paths/counts/hashes и expected QA files;
- проверить rendered output, если изменился DOCX/layout;
- отделить `verified`, `pending`, `failed`, `blocked`;
- получить independent critic для release candidate;
- commit/push делать только по явному запросу пользователя.

## 15. Вопросы, требующие новой пользовательской власти

- Можно ли добавить три corrected DOCX в новый GitHub repo и куда именно?
- Должен ли canonical CoC registry жить внутри standalone или подключаться
  внешним authority path?
- Нужно ли переносить NRI governance как project-local policy?
- Разрешено ли vendor legacy `translator`, или нужен чистый extraction/refactor?
- Требуется ли сохранять source PDFs в Git/LFS с учётом прав и размера?
- Какой renderer является поддерживаемым на новом хосте: Word, LibreOffice или
  оба?
- Нужно ли переносить историческую Git history или достаточно documents/receipts?

Не принимать эти решения молча.

## 16. Готовый стартовый prompt для следующей модели

```text
Ты принимаешь проект KB Creator из репозитория
https://github.com/Hramgithub/kb_creator.git. Начни с
kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md и
kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md. Затем прочитай только текущие
верхние разделы kb_creator/PROJECT_STATUS.md и goal
kb_creator/docs/plans/20261004-user-docx-review/{plan,context,release}.md.

Не запускай книгу и не меняй artifacts. Сначала проверь git/LFS и составь
fresh standalone-readiness audit: translator, Python dependencies, .tools,
canonical CoC registry, governance/layout rules, missing corrected DOCX и
stale links. Исторические NRI test/page counts не выдавай за свежий standalone
run. Current supported writer route — DOCX-only five_step_docx_v3; legacy
publication HTML/PDF writers retired. Любая реализация должна быть generic,
fail-closed, с tests и fresh output root. Не infer acceptance. Перед commit или
push запроси явное подтверждение пользователя.
```

## 17. Ключевые ссылки

- [README](../../README.md)
- [PROJECT_STATUS](../../PROJECT_STATUS.md)
- [Five-step usage](../five-step-usage.md)
- [Latest deliverables index](../../deliverables/latest/README_RU.md)
- [October correction plan](../plans/20261004-user-docx-review/plan.md)
- [October correction context](../plans/20261004-user-docx-review/context.md)
- [October technical release record](../plans/20261004-user-docx-review/release.md)
- [Current handoff goal](../plans/20261011-model-handoff/plan.md)
- [Architecture receipt](../plans/20261011-model-handoff/handoffs/H2-architect-receipt.md)
