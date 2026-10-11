# Viral: реестр типовых проблем пользовательского ревью

Дата начала: 2026-09-02

Статус: живой реестр; `MASTER_EN` ещё не принят пользователем
Область: результат `MASTER_EN`, реконструкция источника и процесс, который их
создал

## Назначение

Этот файл отделяет три разных вещи:

1. подтверждённые дефекты результата;
2. допустимые преобразования, которые выглядят подозрительно без объяснения;
3. процессные дефекты, способные повториться на следующем сценарии.

Новый пункт сначала фиксируется как наблюдение. Причина и системное исправление
не считаются доказанными, пока не проведён отдельный анализ. Пользовательское
чтение Candidate C продолжается; этот реестр не является его принятием.

## Шкала статусов

- `OPEN` — наблюдение подтверждено, квалификация или решение ещё не приняты.
- `DEFECT` — подтверждённый дефект результата или процесса.
- `ACCEPTED_DESIGN` — осознанное и принятое преобразование, не дефект.
- `REVIEW_AID` — проблема удобства проверки, не обязательно production-дефект.
- `RESOLVED` — системное исправление реализовано и проверено на повторяемом
  тесте.

## A. Проблемы и особенности результата

### OUT-001 — В `MASTER_EN.md` не видны номера исходных страниц

- Статус: `REVIEW_AID`.
- Наблюдение: в reader Markdown отсутствуют видимые `Page N` и скрытые
  HTML-маркеры страниц.
- Что сохранено: привязки блоков находятся в `MASTER_EN.provenance.json` через
  `source_fragments[].page`, `source_page` и диапазоны итогового текста.
- Риск: ручная сверка `MASTER_EN` с исходным PDF требует обращения к JSON и
  неудобна пользователю.
- Это не означает потерю трассируемости и пока не считается дефектом
  production-reader.
- Системный вопрос: нужен ли для каждого сценария отдельный производный
  `MASTER_EN_REVIEW.md` или HTML-review view с source-page markers, не меняющий
  замороженный reader candidate?
- Доказательства:
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.provenance.json`.

### OUT-002 — Оригинальный TOC заменён нашим кликабельным оглавлением

- Статус: `ACCEPTED_DESIGN` — пользователь подтвердил 2026-09-02.
- Наблюдение: исходное оглавление с авторскими номерами страниц находится на
  `source-page-005` в `RECONSTRUCTED_EN.md`; в `MASTER_EN.md` вместо него
  собран расширенный список внутренних anchor-ссылок без исходных номеров.
- Почему допустимо: исходный TOC не потерян, остаётся в reconstruction layer и
  может быть проверен; `MASTER_EN` использует навигацию своей новой структуры.
- Типовой риск: без явного transformation record это выглядит как незаметная
  потеря авторского материала.
- Системный вопрос: должен ли provenance явно маркировать такие блоки как
  `generated_navigation_replaces_source_toc`, а не оставлять у unit общее
  `operations: [retained]` при пустом `source_fragments`?
- Доказательства:
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/RECONSTRUCTED_EN.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.provenance.json`.

### OUT-003 — Замороженный Candidate C потерял `MASTER_EN.md`

- Статус: `DEFECT`; блокирует формальное пользовательское принятие именно
  каталога Candidate C.
- Наблюдение: каталог
  `viral-master-en-candidate-20260902-c` сохранил шесть root-sidecars и все
  123 asset-файла, но больше не содержит `MASTER_EN.md`; сейчас в нём 129
  файлов вместо исходных 130.
- Сохранность данных: две retained scratch-сборки содержат побайтово одинаковый
  `MASTER_EN.md`, 357130 bytes, SHA-256
  `F486849BB6A2E8EE860F092C0AE691CD4780A08A8065BFF19C47B3BB0DC461D1`.
- Риск: сущность, объявленная frozen/immutable, фактически могла быть изменена
  последующей работой; пользовательская ссылка стала невалидной.
- Системный вопрос: какой процесс удалил payload и почему pre/post identity
  check не остановил операцию до повреждения? Нужны immutable candidate
  lifecycle, content-addressed retention и обязательная existence/hash-проверка
  перед любым handoff.
- Доказательства:
  - `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`, раздел
    `Parallel preservation pass — 2026-09-02`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c/`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-1/`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/`.

### OUT-004 — Пользователю была дана ссылка на уже отсутствующий payload

- Статус: `DEFECT` процесса handoff.
- Наблюдение: путь Candidate C был назван актуальным для чтения до повторной
  проверки существования `MASTER_EN.md`.
- Риск: статус-документ и фактическое состояние файлов разошлись; пользователь
  тратит время на поиск или проверяет не тот артефакт.
- Системный вопрос: user-facing deliverable pointer должен формироваться только
  после автоматической проверки `exists + expected bytes + expected SHA-256 +
  asset closure` непосредственно перед ответом или handoff.

### OUT-005 — Арты не сохраняют порядок относительно текста из overlay

- Статус: `DEFECT`; обнаружен пользователем на source page 3.
- Наблюдение: на overlay страницы 3 логотип Spektral Krew расположен до первого
  абзаца. В `MASTER_EN.md` тот же asset помещён после последней фразы `OK - so
  any questions?`, непосредственно перед разделом `Warning`.
- Второй подтверждённый случай находится на границе `Plots and Schemes` /
  `Prologue`. В принятой реконструкции и source order ночной прибрежный город
  `b90cb9...7585` завершает page 31, а лодка `da0cac...0083e` стоит в начале
  page 32 до `# Prologue`. Оба изображения тем самым завершают визуальную
  последовательность `Plots and Schemes` и должны находиться непосредственно
  перед новым heading `Prologue`, в порядке город -> лодка.
- `publication_config_v1.json` ошибочно присвоил обоим assets
  `owner_anchor: viral-isola-prologue`; source-disposition повторяет тот же
  `target_anchor`. Builder затем штатно добавил их после последнего span
  `Prologue`, поэтому в `MASTER_EN.md` они оказались на строках 1900/1902, далеко
  после heading и prose раздела. Здесь одновременно ошибочен declared owner и
  проявляется owner-end placement алгоритма.
- Это не единичная ошибка `placement_index`. Текущий builder удаляет все
  исходные Markdown image references из текстового span, затем добавляет все
  reader assets только после последнего span их `owner_anchor`. Внутри этой
  группы `placement_index` управляет лишь порядком артов между собой, но не их
  положением относительно абзацев.
- Риск: иллюстрация, карта, портрет или карточка отрывается от исходного
  контекста; порядок может совпасть с overlay только случайно.
- Системный вопрос: в reusable contract нужен relative placement selector или
  единый ordered stream `text fragment | asset`, полученный из принятого
  reconstruction/overlay order. Для допустимого осознанного переноса требуется
  отдельная reviewed override, а не неявное owner-end placement.
- Предыдущий Innsmouth pipeline уже разделял часть этих обязанностей: NPC art
  получал semantic identity/heading anchors; прочий art получал ближайший
  source-text anchor по bbox/order; downstream HTML оставлял full-width art
  full-width, а non-full-width оформлял как right-float. Viral не перенёс этот
  placement contract и свёл все классы к одному `owner_anchor`.
- Доказательства:
  - screenshot пользователя от 2026-09-02;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/SELECTED_OVERLAY.pdf`, page 3;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-003.md`;
  - source PDF pages 30–32 и reconstruction pages 31–32;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`, assets
    `b90cb9...7585` и `da0cac...0083e`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`;
  - `kb_creator/scripts/build_scenario_master_en.py`, `clean_span()` и
    `assemble_reader()`.

### OUT-006 — Типографический заголовок `Summary` продублирован как reader-art

- Статус: `DEFECT`; обнаружен пользователем на source page 6.
- Наблюдение: `MASTER_EN.md` уже содержит семантический заголовок `### Summary`,
  но после текста Summary дополнительно выводит JPEG `Summary heading` размером
  209x56. В source overlay это одна типографическая плашка раздела, а не
  самостоятельная иллюстрация.
- Root-cause evidence: original-hybrid block 86 распознал bbox
  `[84,498,202,522]` как текст `Summary`; original-pipeline-OCR block 42
  распознал практически тот же bbox `[83,497,205,522]` как image. Merge decision
  page 6 выбрал оба блока: hybrid как `structure` и pipeline/OCR как `asset`.
- Дополнительный art страницы — большой ruined-hall hero с встроенным словом
  `Introduction` — имеет самостоятельное визуальное содержание. Маленький
  `Summary` crop состоит только из типографического заголовка и должен быть
  evidence-only/suppressed после сохранения семантического heading text.
- Риск: визуально дублируются заголовки, в reader попадает layout residue, а
  downstream HTML/PDF получает ложный full-width art.
- Системный вопрос: типографический crop, совпадающий с heading text другого
  view по bbox/содержанию и не имеющий независимого visual content, запрещён как
  reader asset. Он остаётся только reconstruction evidence.
- Доказательства:
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate/merge_packets/pages/page-006.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/decisions/page-006.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-006.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`.

### OUT-007 — Platform logos и promotional badge опубликованы как content art

- Статус: `DEFECT`; пользовательская disposition подтверждена 2026-09-02.
- Наблюдение: source page 7 содержит пять отдельных crops: YouTube, Facebook,
  Instagram, Twitter и `Become a Patron`. Все пять попали в `MASTER_EN.md` как
  reader images между tagline Spektral Krew и разделом Marco.
- Пользовательское решение: первые четыре assets являются изолированными
  `platform_logo`, пятый — `promotional_badge`; в таком виде они не несут
  самостоятельной ценности для документа (`reader_value: false`) и не должны
  публиковаться в reader. Сам класс `logo` не является разрешением на публикацию.
- Что сохранить: исходные crops и их provenance остаются в reconstruction
  evidence; текстовая информация сценария о YouTube-канале сохраняется в
  prose. Если в будущем badge сопровождает функциональный URL, reader должен
  сохранить сам текст/link, а не обязательную raster-кнопку.
- Узкое исключение: platform icon внутри цельного in-world handout/screenshot,
  где UI является частью физического свидетельства, сохраняется вместе со всей
  physical unit; это не разрешает публиковать изолированный badge.
- Отличие от Spektral Krew logo: уникальный in-world logo самого объекта
  сценария может иметь `reader_value: true` как identity/atmospheric art; общие
  логотипы внешних платформ этого значения здесь не имеют.
- Доказательства:
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-007.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`;
  - пять config assets `page-007-image-01.jpg` ...
    `page-007-image-05.jpg`, сейчас ошибочно `representation: reader` и
    `semantic_role: inline`.

### OUT-008 — Цельная web-композиция page 7 не стала asset-кандидатом

- Статус: `OPEN`, non-blocking future research; пользователь 2026-09-02
  подтвердил, что это не критично для текущего Viral и не требует перестройки
  Candidate C.
- Наблюдение: верх source page 7 визуально образует одну in-world web/identity
  композицию Spektral Krew: logo, tagline, navigation, platform/patron strip и
  персонаж внутри общей рамки. Ни один из трёх extraction views не выдал эту
  область как один цельный image/crop candidate.
- `original_hybrid` и `raster_hybrid` разложили её на текст/logo, tagline,
  menu/list, пять маленьких badge-assets и отдельный portrait asset.
  `original_pipeline_ocr` выдал `doc_title`/text-блоки и `0 image` detections;
  персонаж как asset в этом view вообще отсутствует.
- Важно: видимая общая рамка на layout PDF не является извлечённым цельным
  asset. Финальный merge мог выбрать только уже раздробленные блоки и потому
  не предоставил reviewer выбор `keep whole composite`.
- Риск: multi-element handout, faux website, dossier, card или рекламная
  композиция теряет собственную визуальную единицу, даже когда отдельные text
  и image blocks формально извлечены без пропусков.
- Ожидаемый системный вариант: materialize reviewed source-region candidate
  `in_world_composite_panel`; при его выборе child badges/typographic crops не
  публикуются повторно, а доступный semantic text может сохраняться отдельно.
  Если пользователь решает не публиковать композицию, это должно быть явным
  `reviewed_suppression`, а не следствием отсутствия кандидата.
- Доказательства:
  - три `Call_of_Cthulhu_Viral_layout.pdf`, page 7, в full three-view run;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/runs/original_pipeline_ocr/Call_of_Cthulhu_Viral/ocr/Call_of_Cthulhu_Viral_model.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate/merge_packets/pages/page-007.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/decisions/page-007.json`.

### OUT-009 — Между многими Markdown-блоками осталось по 3–4 пустые строки

- Статус: `DEFECT` форматирования; авторский текст не потерян.
- Наблюдение пользователя: в Obsidian/Markdown view между абзацами и
  headings по всему `MASTER_EN.md` видны чрезмерные вертикальные интервалы.
- Измеренный охват Candidate C scratch-copy: 1936 runs пустых строк, из них
  469 имеют длину 3 и ещё 35 — длину 4; максимальная длина — 4. Поэтому это не
  единичная особенность темы или конкретного heading.
- Семантика: CommonMark/HTML renderer обычно схлопывает несколько пустых строк
  между blocks, поэтому content structure в большинстве exports не меняется.
  Однако source view и Obsidian Live Preview становятся раздутыми, а поведение
  presentation-specific renderers нельзя считать гарантированным.
- Уточнение после проверки таблиц: внутри pipe-table эта же последовательность
  пустых строк уже не косметическая. Она разрывает Markdown table между header,
  separator и rows. Такие случаи вынесены в OUT-013 и являются structural
  defects, а не только форматированием editor view.
- Ожидаемое состояние: один blank line между обычными Markdown blocks, кроме
  точных конструкций, где дополнительные строки являются явно доказанной
  частью literal/code content.
- Доказательства:
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, например строки 656–668;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/RECONSTRUCTED_EN.md`.

### OUT-010 — Config short titles заменяют полные авторские source headings

- Статус: `DEFECT` содержания/структуры; пользователь 2026-09-02 подтвердил
  общее правило: такие части заголовка обязательны и не могут удаляться.
- Наблюдение: source headings содержат `Ku Hyeon (Investigator)`,
  `Maya Adeduwon (NPC)` и `Emily ‘Em’ Lavigne (NPC)`, а `MASTER_EN.md`
  публикует только `### Ku Hyeon`, `### Maya Adeduwon` и
  `### Emily “Em” Lavigne`.
- Охват: тем же способом сокращены все семь верхнеуровневых character headings
  Spektral Krew: Marco `(Lead Investigator)`, Corrina `(Investigator)`, Enoch
  `(Investigator)`, Peter `(Investigator)`, Ku Hyeon `(Investigator)`, Maya
  `(NPC)` и Emily `(NPC)`.
- Дополнительный подтверждённый охват: `2. Beggar's Cove` потерял
  `(Baia dei Mendicanti)`, `5. Saint Roche's Hospital` потерял
  `(Ospedale di San Rocco)`, а `Hastalÿk` потерял pronunciation hint
  `(HAS-tah-lik)`. Это такие же дефекты, а не допустимые сокращения.
- Ещё один подтверждённый случай вне скобок: source page 18 и reconstruction
  содержат полный heading `Welcome to Perla`, но `MASTER_EN.md` публикует только
  `### Welcome`; TOC также показывает `Welcome`.
- Второй подтверждённый случай вне скобок: source page 68 и reconstruction
  содержат singular heading `New Spell`, но config и `MASTER_EN.md` заменяют его
  на plural `New Spells`. Это не нормализация регистра или пунктуации, а
  неподтверждённое изменение авторского title.
- Это тот же механизм, а не отдельная OCR-ошибка и не универсальный regex,
  удаляющий скобки. В `publication_config_v1.json` source locator сохраняет
  точный selector `# Welcome to Perla`, но hierarchy row вручную задаёт
  `title: "Welcome"`. Для персонажей и локаций тот же config layer задаёт
  shortened titles без qualifiers. Builder затем без source-title fidelity
  check материализует `row['title']` как reader heading.
- Почему это значимо: qualifier передаёт игровую роль и различает playable
  Investigator от NPC; это не декоративная пунктуация и не должна исчезать из
  reader heading.
- Контрпример пользователя: `APPEARANCE (SUPER FAN OPTION)` и
  `APPEARANCE (ANOTHER GHOST HUNTER OPTION)` сохранили скобочную часть, потому
  что их text не был заменён сокращённым hierarchy title.
- Ожидаемое состояние: reader headings сохраняют нормализованный исходный title
  целиком, включая role qualifier, nickname, альтернативное/оригинальное
  название, pronunciation hint и остальные авторские слова (`to Perla`).
  Короткое display-name разрешено только как отдельное поле для
  anchor/navigation и не заменяет полный reader heading.
- Системная защита: любое lexical отличие hierarchy `title` от найденного
  source heading требует отдельного reviewed transformation record с причиной;
  иначе builder/verifier обязан отклонить config. Cosmetic case/style
  normalization, расширенные названия handouts и настоящие editorial renames
  должны классифицироваться отдельно, а не попадать в один неявный механизм.
- Доказательства:
  - screenshot source overlay пользователя от 2026-09-02;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/RECONSTRUCTED_EN.md`, source pages 7–11 и 18;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`, hierarchy
    entries персонажей, локаций и `viral-one-night-in-perla-welcome`;
  - `kb_creator/scripts/build_scenario_master_en.py`, `assemble_reader()`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 639, 674, 714, 1155 и TOC.

### OUT-011 — Врезки ошибочно включены в heading hierarchy и ломают folding

- Статус: `DEFECT` структуры/presentation; подтверждён пользователем на Maya и
  Emily, затем проверен по полным source pages 10–12.
- Наблюдение: `MASTER_EN.md` представляет визуальные inset panels как headings.
  У Maya получена ложная цепочка `### Maya Adeduwon` → `#### Maya's Secrets` →
  `##### APPEARANCE`, хотя `Maya's Secrets` и `APPEARANCE` являются двумя
  отдельными серыми врезками и не состоят друг в друге.
- У Emily `#### APPEARANCE (SUPER FAN OPTION)` становится родителем для
  `##### APPEARANCE (ANOTHER GHOST HUNTER OPTION)` и `##### Keeper's Notes`.
  В Obsidian folding первого heading поэтому скрывает почти весь остаток Emily
  до настоящего нового раздела `## Creating New Investigators`.
- Обобщённый тип ошибки: `heading scope leakage`. Source label владеет одним
  визуально ограниченным фрагментом, после которого документ возвращается в
  основной поток родительского раздела. Markdown heading не имеет собственного
  closing boundary и продолжает владеть всеми последующими blocks до следующего
  heading того же или более высокого уровня. В результате fold забирает и
  правильное тело label, и посторонний основной текст.
- На page 12 scope `APPEARANCE (SUPER FAN OPTION)` заканчивается сразу после
  абзаца `Em is 5'2"...`. Следующий `Another Ghost Hunter Option.` уже является
  основной прозой Emily, но текущая Markdown hierarchy ошибочно оставляет его
  внутри `APPEARANCE`.
- Это не исправляется простым выравниванием `####`/`#####`: врезки вообще не
  должны входить в document outline. Character heading остаётся владельцем
  всего блока до следующего character/major heading; inset panels живут внутри
  него как atomic non-heading units.
- Проверенная source-классификация:
  - page 10: серый panel Hyeon объединяет `APPEARANCE` и `GEAR CARRIED`; это одна
    врезка с двумя внутренними labels;
  - page 11: `Maya's Secrets` и `APPEARANCE` — две отдельные серые врезки;
  - page 12: `APPEARANCE (SUPER FAN OPTION)`,
    `APPEARANCE (ANOTHER GHOST HUNTER OPTION)` и `Keeper's Notes` — три
    отдельные врезки;
  - `Another Ghost Hunter Option.` и `Other Investigator Options.` — run-in
    labels внутри обычной прозы, не section headings;
  - `Creating New Investigators` — настоящий новый section heading.
- Дополнительный повторяющийся класс подтверждён на девяти бледно-зелёных
  panels `Possible Vision from The Sight` / `Possible Visions from The Sight`,
  начинающихся на pages 35, 37, 39, 45, 46 (два), 48 и 49 (два). У всех один
  визуальный шаблон: зелёный background, одинаковые margins/padding, bold label
  и замкнутое тело. Один panel начинается внизу page 45 и визуально продолжается
  на page 46; один из page-49 panels содержит несколько paragraphs/quote, поэтому
  scope нельзя определять как `label + один следующий block`.
- В `MASTER_EN.md` первые три экземпляра ошибочно стали `######` headings
  (строки 2052, 2153, 2390), а остальные шесть остались plain labels без
  enclosing container. Оба представления непоследовательны и неверны: все девять
  являются peer callouts одного template class и не входят в outline/folding.
- Raw `original_hybrid` присваивает всем девяти labels `text_level: 2`, что
  подтверждает ограничение page-local OCR: типографический heading signal внутри
  панели не равен document heading role. Document-level repetition и enclosing
  geometry должны переопределять локальную классификацию как inset label.
- Ожидаемое Markdown-представление: portable blockquote/callout container с
  bold title/labels, например `> **Maya's Secrets**`, и `>` перед каждой строкой
  тела. В sidecar сохраняются `layout_unit: inset`, source bbox, owner и child
  blocks; HTML/PDF layer может оформить его как `<aside>`. Символы `#` внутри
  inset title не используются.
- Доказательства:
  - полные source pages 10–12 `Call_of_Cthulhu_Viral.pdf`;
  - screenshots/overlay пользователя от 2026-09-02;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 674–768;
  - `NRI_OCR_LAYOUT_RULES.md`, правила preserve heading hierarchy и
    image/sidebar/callout anchors.

### OUT-012 — Inline bold/italic/underline page 12 не перенесены в MASTER_EN

- Статус: `MASTER_EN_ENHANCEMENT`; обнаружено пользователем на page 12;
  `NON_BLOCKING` для source reconstruction по решению пользователя 2026-09-02.
- Source visual содержит как минимум:
  - bold-italic run-in `Another Ghost Hunter Option.`;
  - italic `The Phantom Posse` внутри того же paragraph;
  - bold-italic run-in `Other Investigator Options.`;
  - underline у `Mythos Investigators`.
- Merge packet, reconstruction decision, `pages/page-012.md` и `MASTER_EN.md`
  представляют эти фрагменты как plain text без Markdown/HTML emphasis.
- Проверка metadata: raw MinerU `middle.json`, `model.json` и
  `content_list.json` не содержат span-level keys для `font`, `bold`, `italic`,
  `underline`, `text_decoration` или `style`; merge packet хранит только flat
  `text + bbox + type`; `MASTER_EN.provenance.json` также не содержит inline
  style spans.
- Дополнительный source-page-16 case показывает, что теряется не только
  Markdown emphasis, но и типографический класс блока. Заголовок правой врезки
  `Keeper's Notes` нативно имеет `ScalaSansPro-Bold`, её тело —
  `ScalaSansPro-Regular`, а окружающая основная проза — `Bookmania-Regular`.
  Настоящий курсив на той же странице отдельно закодирован как
  `Bookmania-RegularItalic`. Следовательно, тело `Keeper's Notes` не должно
  целиком становиться курсивом: смена font family является evidence врезки, а
  не автоматически semantic emphasis.
- Граница gate: случай не ставит под сомнение достоверность снятого текста и
  смысла и поэтому не блокирует закрытие reconstruction step. Он остаётся
  улучшением структурно-типографической fidelity будущего `MASTER_EN`.
- Риск для улучшенного reader: run-in labels перестают визуально отделять
  варианты/подпункты, названия внутри prose теряют авторское emphasis, а
  underline исчезает без возможности восстановить его из текущего provenance.
- Ожидаемое состояние: exact text-range metadata сохраняет style set и evidence;
  reader Markdown materializes bold/italic нативными markers, а underline —
  совместимым HTML/semantic representation, выбранным production policy.
- Доказательства:
  - screenshot/overlay пользователя page 12 от 2026-09-02;
  - screenshot/overlay пользователя и native PDF text spans page 16 от
    2026-09-02;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate/merge_packets/pages/page-012.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/decisions/page-012.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-012.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`.

### OUT-013 — Три logical tables опубликованы как невалидные pipe-table fragments

- Статус: `DEFECT` структуры/reader presentation; обнаружен пользователем на
  `Rumors` и `Signs and Portents`, системный аудит добавил `Lemon Grove Results`.
- Source содержит три цельные logical tables:
  - `Rumors`, rows 1–10, продолжается с page 20 на page 21;
  - `Signs and Portents`, rows 1–10, начинается на page 21, продолжается во
    второй колонке и затем на page 22;
  - `Lemon Grove Results`, rows 1–10, продолжается между колонками page 36.
- В `MASTER_EN.md` первая часть `Rumors` rows 1–6 является валидной таблицей,
  потому что header, separator и rows смежны. Повторный header и rows 7–10
  разделены тремя пустыми строками и отображаются как plain pipe text.
- `Signs and Portents` сломана с первого row: оба fragments pages 21/22 имеют
  пустые строки между header, separator и каждой row. `Lemon Grove Results`
  имеет тот же дефект для всех rows.
- Полный аудит pipe headers нашёл четыре invalid fragments, представляющих эти
  три таблицы; остальные обнаруженные pipe tables имеют смежные header/separator
  и не показывают данный syntax defect.
- Слова, row numbers и их порядок в проверенных случаях присутствуют, поэтому
  данные восстанавливаемы. Но logical relation `roll -> result/rumor` больше не
  выражена валидной Markdown table и reader rendering сломан.
- Ожидаемое состояние `MASTER_EN`: одна canonical table на один logical table,
  один header/separator и непрерывные rows 1–10. Source page/column boundaries
  остаются в provenance; repeated page headers не дублируются в reader table.
- Доказательства:
  - source PDF pages 20–22 и 36;
  - screenshots/overlay пользователя от 2026-09-02;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-020.md` ... `page-022.md` и `page-036.md`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 1302–1399 и 2082+.

### OUT-014 — Имена Perla NPCs потеряли статус дочерних заголовков

- Статус: `DEFECT` структуры; пользователь обнаружил на
  `Santina Maria Salvatore`, проверка добавила peer-heading `Padre Angelo`.
- Source page 25 имеет ясный повторяющийся двухколоночный шаблон:
  `portrait -> выделенное имя -> собственный prose block`. Оба имени являются
  равноправными subsection labels внутри `Perla NPCs`, а не первыми строками
  обычных абзацев.
- Accepted reconstruction `page-025.md` сохраняет оба имени только как plain
  lines без Markdown heading marker. `MASTER_EN.md` поэтому также показывает
  `Santina Maria Salvatore` и `Padre Angelo` обычным текстом и не включает их в
  outline/folding/navigation.
- Это не случай OUT-010: полного source heading нет в config selector и он не
  был заменён коротким `title`. Исходный MinerU heading был распознан корректно,
  но semantic heading metadata потерялась в comparison adapter до merge review;
  Master hierarchy затем просто не получила двух дочерних NPC units.
- Ожидаемая структура: `### Perla NPCs` владеет двумя peer subsections
  `#### Santina Maria Salvatore` и `#### Padre Angelo`; каждый NPC subsection
  владеет своим portrait и prose до следующего peer heading. Конкретный HTML/PDF
  float не должен менять эту document hierarchy.
- Доказательства:
  - source PDF page 25 и screenshot/overlay пользователя от 2026-09-02;
  - raw MinerU `content_list.json`: у обоих имён `text_level: 2`; raw Markdown
    всех трёх views содержит `## Santina Maria Salvatore` и `## Padre Angelo`;
    selected `original_hybrid` `content_list_v2.json` хранит оба блока как
    `type: title`, `level: 2`, а model JSON — как `paragraph_title`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/decisions/page-025.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-025.md`;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 1519 и 1535.

### OUT-015 — Stream Schedule потерял единый серый inset-контейнер

- Статус: `DEFECT` структуры/presentation; обнаружен пользователем при чтении
  `MASTER_EN.md` и подтверждён по полным source pages 27–28.
- Это не pipe-table: в источнике после обычного run-in абзаца `Stream Schedule`
  идёт одна серая врезка с ordered list из восьми пунктов. Врезка начинается на
  page 28 с `1. Opening Monologue at the Bridge` и заканчивается
  `8. Wrap-Up`; следующий run-in абзац `Maya` снова принадлежит основному потоку.
- Accepted reconstruction и `MASTER_EN.md` сохранили все восемь номеров и весь
  текст, поэтому content loss нет. Потеряна enclosing-panel semantics: пункты
  материализованы как плоский список с чрезмерными пустыми строками, без общего
  callout/blockquote boundary. Подчёркнутые названия локаций внутри пунктов также
  не сохранены как inline emphasis.
- Случай входит в восстановление врезок вместе с OUT-011, но требует отдельной
  cross-page regression: вводный `Stream Schedule` остаётся обычным run-in
  paragraph на page 27, а только contiguous items 1–8 на page 28 образуют один
  atomic inset. Нельзя превращать их в pipe-table или захватывать следующий
  `Maya` paragraph.
- Ожидаемое Markdown-представление: один portable blockquote/callout с ordered
  list 1–8; location labels сохраняются inline emphasis, а список не входит в
  document outline.
- Доказательства:
  - полные source PDF pages 27–28 и screenshot пользователя от 2026-09-02;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-027.md`, строка 63;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-028.md`, строки 3–31;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 1615–1650.

### OUT-016 — Hospital group headings потеряны как plain labels

- Статус: `DEFECT` структуры; пользователь обнаружил на `Hospital, Cellar`, а
  проверка повторений расширила охват до всего семейства `Hospital, ...`.
- В source page 39 `Hospital, Cellar` является отдельным жирным group heading
  внутри `Hospital Locations`. Следующий `Morgue` — уже другой semantic type:
  подчёркнутый run-in label текущего room paragraph, а не peer heading.
- Во всех трёх raw MinerU views `Hospital, Cellar` имеет `text_level: 2`, а raw
  Markdown содержит точную строку `## Hospital, Cellar`. Такие же heading
  semantics подтверждены для peer labels `Hospital, Ground Floor`,
  `Hospital, Second Floor` и `Hospital, Third Floor`.
- Comparison adapter удалил `text_level`: normalized block 638 на source page 39
  содержит только `type: text` и сам текст. Accepted decision выбрал этот block
  как `purpose: text`; его Markdown содержит plain label и не содержит heading.
  Поэтому reconstruction и `MASTER_EN.md` воспроизвели label лексически, но
  потеряли folding, outline и semantic ownership.
- В текущем `MASTER_EN.md` plain lines остаются не только у четырёх этажей, но и
  у peer/group labels `Hospital, Ground Floor, West Wing`, `East Wing`,
  `Secret Rooms`, `Hospital, Second Floor, West Wing` и `East Wing`.
  `publication_config_v1.json` не содержит для них дочерних hierarchy rows.
- Ожидаемое правило: повторяющиеся `Hospital, <level/wing>` образуют иерархию
  location groups под `Hospital Locations`; numbered rooms и run-in room labels
  принадлежат правильному group owner до следующего peer group. Исправление
  нельзя сводить к добавлению `#####` только перед `Hospital, Cellar`: текущие
  numbered rooms уже используют H5, поэтому уровни всей hospital subtree нужно
  переназначить согласованно, без collisions и случайного захвата соседних rooms.
- Это новый output defect, но не новая первичная причина: он подтверждает более
  широкий охват PROC-019/PROC-020 за пределами имён NPC.
- Доказательства:
  - полная source PDF page 39 и screenshot/overlay пользователя от 2026-09-02;
  - raw MinerU `content_list.json` и raw Markdown трёх views для source pages
    39–45;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json`, source page 39 block 638;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/decisions/page-039.json`;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-039.md`, строка 52;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 2422–2902.

### OUT-017 — Однострочные hospital cross-references разделены на heading и body

- Статус: `DEFECT` структуры/presentation; пользователь обнаружил на компактных
  room references source page 45.
- В источнике шесть записей `2E`–`2J` являются шестью отдельными, но цельными
  строками: подчёркнутый room label, тире и `See ...` находятся на одной строке.
  У этих записей нет собственного prose body, которое следовало бы помещать под
  отдельный Markdown heading.
- Все три raw MinerU views классифицируют, например,
  `2E. Isolation Ward – See 1J.` как единый `type: text` block без heading
  metadata. Raw Markdown и accepted reconstruction также сохраняют каждую
  запись одной строкой. Значит, это не OCR split и не merge defect.
- Разделение вводит только Master publication layer. Для каждой комнаты config
  создаёт H5 hierarchy row с `semantic_role: room` и применяет
  `replace_label_retain_remainder`: builder печатает `##### 2E. Isolation Ward`,
  удаляет label из исходной строки и добавляет остаток `[See 1J](...)` отдельным
  body block через пустую строку. Xref-механизм лишь делает `See ...` ссылкой и
  сам по себе строку не делит.
- Непосредственный охват: `2E. Isolation Ward`, `2F. Recovery Ward`,
  `2G. Infectious Ward`, `2H. Terminal Ward`, `2I. Acute Ward` и
  `2J. Recent Ward`. Большие вертикальные интервалы в reader view являются
  следствием шести искусственных H5 headings и отдельных paragraph margins.
- Ожидаемое представление: сохранить каждую запись одним компактным run-in row,
  например `**2E. Isolation Ward** — [See 1J.](#...)`; технический anchor можно
  оставить перед строкой, но сама запись не должна становиться folding/outline
  heading. Для `2I` сохраняется уже проверенная коррекция `1O`, а не OCR `10`.
- Source page показывает тот же run-in template и на комнатах `2A`–`2D` с
  полноценным prose remainder. Их массовое превращение в H5 также требует
  проверки при общей переразметке hospital subtree; на reference-only rows
  дефект уже однозначен.
- Вместе OUT-016 и OUT-017 показывают инверсию иерархии: настоящие group headings
  `Hospital, ...` были понижены до plain text, а вложенные run-in room labels,
  наоборот, повышены до document headings.
- Доказательства:
  - полная source PDF page 45 и screenshots пользователя от 2026-09-02;
  - raw MinerU `content_list.json` и raw Markdown всех трёх views, source page 45;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-045.md`, строки 19–31;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`, hierarchy rows `viral-isola-hospital-room-2e-isolation-ward` … `room-2j-recent-ward`;
  - `kb_creator/scripts/build_scenario_master_en.py`, `assemble_reader()` и `clean_span()`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 2862–2900.

### OUT-018 — DSS Incendiary Grenades потерял semantic card title и контейнер

- Статус: `DEFECT` структуры/presentation; пользователь обнаружил потерянный
  уровень у `DSS Incendiary Grenades (12)` на source page 55.
- В источнике это заголовок отдельной серой equipment stat-card. Физический scope
  карточки ограничен тремя частями: title, строкой `Skill: ... Malfunction: 99`
  и italic footnote `*Delivers 4D10 ... for 3 rounds.` Следующий paragraph
  `The Devourer is repelled by fire ...` уже находится за пределами карточки.
- `original_hybrid` и `raster_hybrid` распознали title как `type: text` с
  `text_level: 2`; их raw Markdown содержит
  `## DSS Incendiary Grenades (12)`. `original_pipeline_ocr` оставил ту же строку
  plain text, поэтому visual/card geometry и majority raw evidence здесь важны.
- Accepted decision выбрал именно `original_hybrid` raw block 932, но уже как
  `purpose: text`: comparison adapter удалил `text_level`, reconstruction и
  `MASTER_EN.md` материализовали title простой строкой. Это ещё один реальный
  пример PROC-019/PROC-020.
- Publication config отдельно распознаёт region как `semantic_card` /
  `literal_card`, однако этот contract только доказывает наличие и порядок
  literals в reader span. Он не materialize серый container и не возвращает
  title presentation; в `MASTER_EN.md` title, stats и footnote остаются тремя
  плоскими paragraphs.
- Текущая termination карточки также слишком широкая: она поставлена перед
  `While the grenades do damage Hastalÿk ...`, поэтому contract span захватывает
  находящиеся после карточки основной paragraph, `Keeper's Notes` и последующий
  prose. Физическая граница должна завершаться перед
  `The Devourer is repelled by fire ...`.
- Ожидаемое представление: одна bounded equipment stat-card/callout с сохранённым
  card title и двумя body lines. Title является настоящим semantic heading
  карточки, но не должен становиться свободным Markdown H4, который при folding
  заберёт весь остаток `Cinematic Ending`; при необходимости card получает
  отдельный технический anchor.
- Доказательства:
  - полная source PDF page 55;
  - raw MinerU `content_list.json` и raw Markdown всех трёх views, source page 55;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json`, original-hybrid block 932;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/decisions/page-055.json` и `pages/page-055.md`, строка 17;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`, structure `semantic_card` с start selector `DSS Incendiary Grenades (12)`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 3240–3248.

### OUT-019 — Appendix sections и page-68 inset опубликованы вне source order

- Статус: `DEFECT` порядка/иерархии; пользователь обнаружил после последнего
  вводного paragraph раздела `Encounters` преждевременные `New Rules`,
  `New Mythos Horrors` и `New Spells` вместо `Outdoor Encounters`.
- Source и accepted reconstruction имеют однозначный порядок:
  `Encounters` intro (page 58) → `Outdoor Encounters` rows 1–9 (page 58) → rows
  10–12 и `Hospital Encounters` (page 59) → `Catacomb Encounters` (page 60) →
  `New Rules` / `The Sight` (page 60). `New Mythos Horrors` начинается только на
  page 65, а `New Spell` и inset `A Few Pointers on Running Viral from Bud` — на
  page 68.
- Publication config также содержит правильные numeric assembly orders:
  `Encounters` 84, `Outdoor` 85, `Hospital` 87, `Catacomb` 88, `New Rules` 89,
  `New Mythos Horrors` 95, `New Spells` 102. Ошибка появляется не в source и не
  в declaration order, а в `fragment_emission_plan()`.
- Текущий `MASTER_EN.md` после `Encounters` intro печатает три пустых parent
  headings `New Rules`, `New Mythos Horrors`, `New Spells`, затем переносит сюда
  page-68 advice inset уже как плоский текст и только после него начинает
  `Outdoor Encounters`.
- Отдельно подтверждён пользовательский симптом на source page 65: heading
  `### New Mythos Horrors` не потерян лексически, но напечатан на строке 3345,
  тогда как первый настоящий child `#### Hastalÿk / The Devourer` начинается
  только на строке 3655. Разрыв в 310 строк делает heading визуально отсутствующим
  у собственного раздела и оставляет `Hastalÿk` без видимого parent heading.
- Аналогичный симптом подтверждён для source page 68: parent heading напечатан
  как `### New Spells` на строке 3349, а его единственный child
  `#### Control Reliquae` начинается только на строке 3846. Разрыв в 497 строк
  делает раздел визуально безымянным на правильном месте. После исправления
  порядка parent должен стоять непосредственно перед `Control Reliquae` и
  сохранять source form `New Spell` в единственном числе.
- Следующий пользовательский симптом той же page 68: весь inset
  `A Few Pointers on Running Viral from Bud` не потерян, но перенесён на строки
  3351–3395 сразу после преждевременного `New Spells`. В source он следует после
  последнего paragraph `Control Reliquae` и непосредственно перед следующим
  major section `Player Handouts`; в Master `Control Reliquae` заканчивается на
  строке 3855, а `## Player Handouts` начинается на 3859 без inset между ними.
  Правильная сборка возвращает весь блок с внутренними labels `The Live Stream
  Chat`, `Maya`, `Enoch and The Sight`, `Peter's Sabotage`, `Hyeon's Skepticism`,
  `Marco`, `Time`, `Urban Decay`, `Hastalÿk` и заключительными lines на это место
  как один bounded callout/inset.
- Это не только визуальная перестановка. После раннего `### New Spells` все H4
  `Outdoor Encounters`, `Hospital Encounters`, `Catacomb Encounters`, `The Sight`
  и другие units структурно становятся его детьми до следующего H3. Folding,
  outline и semantic ownership Appendix поэтому неверны.
- Provenance подтверждает механизм: parent units `New Rules`,
  `New Mythos Horrors` и `New Spells` не имеют output fragments, но headings
  materialize при первом plan event. Единственный retained fragment самого
  `Appendix` — page-68 `A Few Pointers ...` — emitted перед fragment'ами
  `Outdoor Encounters`, несмотря на более позднюю source page.
- Ожидаемое состояние: reader order монотонен по source page+bbox с учётом
  column reading order; parent heading появляется непосредственно перед первым
  descendant/content event своего subtree. Page-68 advice panel остаётся после
  `Control Reliquae` и восстанавливается как один bounded inset, а не body
  раннего Appendix.
- Доказательства:
  - полные source PDF pages 58–60, 65 и 68;
  - `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/pages/page-058.md` … `page-060.md`, `page-065.md`, `page-068.md`;
  - `kb_creator/working/viral/master_en/publication_config_v1.json`, assembly orders 83–102;
  - `kb_creator/scripts/build_scenario_master_en.py`, `fragment_emission_plan()`;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.provenance.json`, Appendix units 83–102;
  - `kb_creator/working/viral/master_en/candidates/viral-master-en-scratch-20260902-2/MASTER_EN.md`, строки 3324–3399 и Appendix outline далее.

### OUT-020 — Outdoor/Hospital/Catacomb Encounters потеряли table representation

- Статус: `DEFECT` структуры/reader presentation; обнаружен пользователем вместе
  с OUT-019 на source pages 58–60.
- Source содержит три roll tables с общей двухколоночной схемой
  `Roll | Phenomenon Encountered`:
  - `Outdoor Encounters`, rows 1–12, продолжение page 58 → page 59;
  - `Hospital Encounters`, rows 1–12 на page 59;
  - `Catacomb Encounters`, rows 1–6 на page 60.
- Accepted reconstruction сохраняет весь текст и порядок rows, но представляет
  таблицы как `Roll Phenomenon Encountered` и отдельные numbered paragraphs без
  cell/table sidecar semantics. Значит, lexical content доступен для повторной
  материализации, но logical relation `roll → phenomenon` потеряна.
- Config уже объявляет все три units как `classification: semantic_table` с
  `source_format: numbered_record_series`, record counts и continuation modes.
  Builder, однако, не сериализует из этих facts canonical Markdown tables, а
  переносит исходные paragraphs через `clean_span()`.
- Дополнительное повреждение `Outdoor Encounters`: row 2 `Cold Spot` ошибочно
  превращён в отдельный H5 hierarchy node, поэтому одна таблица разрезана между
  разными owners. Остальные rows остаются plain paragraphs.
- Ожидаемый reader: три canonical двухколоночные Markdown tables с одним header
  на logical table, соответственно 12/12/6 rows; page/column continuation остаётся
  только в provenance. Название phenomenon сохраняется inline emphasis внутри
  второй cell; ни одна строка таблицы не становится heading/outline entry.
- Основные процессные причины уже представлены PROC-017/PROC-018; promotion
  `Cold Spot` дополнительно подтверждает PROC-021.
- Доказательства:
  - полные source PDF pages 58–60 и screenshot пользователя от 2026-09-02;
  - reconstruction `pages/page-058.md` … `page-060.md`;
  - `publication_config_v1.json`, structures
    `viral-structure-outdoor-encounters`, `hospital-encounters`,
    `catacomb-encounters`;
  - `MASTER_EN.md`, строки 3397–3481.

### OUT-021 — Две Appendix-таблицы `D10 Roll Result` опубликованы как абзацы

- Статус: `DEFECT` структуры/reader presentation; пользователь указал на первую
  таблицу `Insanity and Bouts of Madness` по screenshot от 2026-09-02.
- Полная визуальная проверка source pages 63–64 подтверждает две отдельные
  физические двухколоночные таблицы с общей схемой `D10 | Roll Result`:
  - `Insanity and Bouts of Madness`, rows 1–10 на page 63; таблица продолжается
    из левой колонки в правую без повторного header;
  - `Paranormal Phenomena`, rows 1–10 на page 64 с тем же layout pattern.
- Reconstruction сохраняет header и весь текст двадцати rows, но обе таблицы
  представлены как `D10 Roll Result` и отдельные numbered paragraphs. Cell
  relation `D10 value → result` и logical table boundary отсутствуют.
- В `MASTER_EN.md` это переносится без восстановления: первая таблица занимает
  строки 3581–3601, вторая — 3629–3649. Поэтому Markdown renderer показывает
  обычные абзацы, а не таблицы.
- Config уже правильно объявляет обе units как `classification: semantic_table`,
  `representation: semantic_from_accepted_facts`, `source_format:
  numbered_record_series`, с ordered keys 1–10 и `record_count: 10`.
  Следовательно, это не ошибка распознавания текста и не отсутствие semantic
  contract, а нематериализованный contract в reconstruction/Master layer.
- Ожидаемый reader: две canonical двухколоночные Markdown tables, каждая с одним
  header и десятью rows. Source-underlined result labels (`Body Horror`, `Bugs`,
  `Echoes of the Past` и т. п.) сохраняются как inline emphasis внутри второй
  cell; rows не становятся headings/outline entries.
- Процессные причины: PROC-017 и PROC-018.
- Доказательства:
  - полные source PDF pages 63–64 и screenshot пользователя от 2026-09-02;
  - reconstruction `pages/page-063.md` и `pages/page-064.md`;
  - `publication_config_v1.json`, structures
    `viral-structure-insanity-bouts-of-madness` и
    `viral-structure-paranormal-phenomena`;
  - `MASTER_EN.md`, строки 3576–3649.

### OUT-022 — Creature statblocks потеряли карточку и внутреннюю структуру

- Статус: `DEFECT` структуры/presentation с одной lexical loss; пользователь
  указал на плоское представление карточки `The Devourer` по screenshot от
  2026-09-02.
- Полная визуальная проверка source pages 65–67 подтверждает два однотипных
  серых creature statblocks:
  - `The Devourer / Aspect of Hastalÿk` целиком находится на page 65;
  - `The Reliquae / Cursed Plague Zombies` начинается на page 66 и продолжается
    на page 67 через `ATTACKS`, `SPECIAL ABILITIES` и две infection roll tables.
- Это hybrid card, а не одна сплошная таблица: верхняя часть является компактной
  key/value-таблицей характеристик и derived stats; атаки и abilities остаются
  структурированным prose с run-in labels; вложенные roll tables сохраняются
  настоящими таблицами внутри того же card scope.
- Reconstruction оставляет все поля отдельными paragraphs и сохраняет отдельные
  evidence crops `Source table on page 65/66/67`, но не создаёт logical statblock
  container. В `MASTER_EN.md` Devourer занимает строки 3668–3716, а Reliquae —
  3742–3809 как плоский поток без общей карточки и компактной stat grid.
- Config уже объявляет обе структуры как `classification: semantic_statblock`,
  `contract_kind: statblock`, `representation: semantic_from_accepted_facts`:
  `viral-structure-hastalyk-devourer` и `viral-structure-reliquae`. Для Reliquae
  отдельно заданы regions pages 66–67 и обе infection tables. Builder проверяет
  ordered literals, но не materialize statblock representation.
- Дополнительная lexical loss: source subtitle `Cursed Plague Zombies` внутри
  карточки Reliquae отсутствует в reconstruction, structured contract и Master.
  Внутренний card title `The Reliquae` также не представлен отдельно от reader
  section heading `Reliquae`.
- Screenshot крупного фрагмента page 66 уточняет физическую границу: верхний
  heading `The Reliquae` и следующий description paragraph находятся вне серой
  панели; нижняя панель намеренно повторяет внутренний title `The Reliquae`,
  затем subtitle `Cursed Plague Zombies` и stat grid. Это не OCR-дубликат:
  section heading и card title выполняют разные функции, поэтому deduplication
  не имеет права удалять второе вхождение.
- `The Plague Monk` является контрольным исключением: source page 66 не содержит
  для него серой таблицы характеристик и прямо сообщает, что у него нет physical
  abilities. Его нельзя автоматически превращать в creature statblock только
  из-за соседства с двумя существами.
- Ожидаемый reader: два единообразных bounded statblock cards. Каждый сохраняет
  title/subtitle, компактную двухколоночную characteristics table, derived stats,
  внутренние labels `ATTACKS` / `SPECIAL ABILITIES`, run-in attack/ability labels
  и весь prose. Reliquae остаётся одним card через page boundary; две infection
  tables находятся внутри него. Внутренние labels не попадают в document outline.
- Процессная причина: PROC-022.
- Доказательства:
  - полные source PDF pages 65–67 и screenshot пользователя от 2026-09-02;
  - reconstruction `pages/page-065.md` … `page-067.md`;
  - `publication_config_v1.json`, structures
    `viral-structure-hastalyk-devourer`, `viral-structure-plague-monk` и
    `viral-structure-reliquae`;
  - `MASTER_EN.md`, строки 3653–3809.

### OUT-023 — Перед infection tables добавлен отсутствующий в source heading

- Статус: `DEFECT` source fidelity/иерархии; пользователь заметил видимый
  heading `Infection` над двумя таблицами Reliquae.
- На source page 67 отдельного heading `Infection` нет. Source содержит только:
  - cross-reference `(see Infection)` в описании атаки;
  - run-in ability label `Infected Flesh:`;
  - два table headers `Roll | Infection, Serious` и
    `Roll | Infection, Deadly`.
- Config искусственно создаёт hierarchy unit
  `viral-appendix-new-mythos-horrors-reliquae-infection` с `level: 5`, title
  `Infection`, `semantic_role: semantic_tables` и locator `insert_before` первой
  таблицы. Builder закономерно materialize его как `##### Infection` на строке
  3787 `MASTER_EN.md`, хотя такого текста/heading в source нет.
- Причина создания unit понятна: на него направлены xrefs `see Infection`,
  `Infected Flesh in the The Reliquae` и `Plague Zombie`. Но addressability не
  требует видимого Markdown heading.
- Ожидаемое представление: сохранить тот же stable anchor невидимым перед
  `Infected Flesh:` внутри statblock Reliquae; ссылки ведут на него, а ability
  label и две таблицы остаются внутри одной карточки. Видимый heading `Infection`
  удаляется, не меняя source text таблиц или ссылок.
- Это отдельный output-симптом PROC-021 и дополнительное подтверждение OUT-022:
  техническая адресация не должна разрывать statblock reader hierarchy.
- Доказательства:
  - source page 67 и screenshot пользователя от 2026-09-02;
  - reconstruction `pages/page-067.md`, строки 17–41;
  - `publication_config_v1.json`, hierarchy anchor
    `viral-appendix-new-mythos-horrors-reliquae-infection` и xref
    `p067-infection`;
  - `MASTER_EN.md`, строки 3765–3809.

### OUT-024 — Ground Floor & Basement опубликован неполными crops вместо полного handout

- Статус: `DEFECT` полноты reader-art/handout; пользователь заметил 2026-09-02.
- Source PDF pages 106–107 образуют одну двухстраничную physical unit: карта
  `Ground Floor & Basement` начинается на page 106 и продолжается на page 107.
  Отдельный crop page 106 обрезает часть карты и потому не может считаться
  каноническим handout, даже если соседний crop page 107 присутствует.
- Reconstruction и текущий `MASTER_EN.md` материализуют три самостоятельных
  reader-assets: маленький crop key/legend, широкий неполный crop карты page 106
  и portrait crop продолжения page 107. Формально все declared assets
  присутствуют, но исходный двухстраничный визуальный объект не сохранён целиком.
- Текстовый `Key` A–V в текущем MASTER извлечён полностью и должен остаться
  отдельным доступным/переводимым слоем. Так же сохраняются текстом legend
  (`Important Areas`, `Dangerous Areas`, `Secret Rooms`, `Chapel Ruins`, `Crypt`)
  и scale `0–100 feet`; они не заменяют саму карту.
- Ожидаемый reader: две полные source-page images 106 и 107 в исходном порядке
  как канонический handout плюс отдельные `Key`, legend и scale text. Проверенная
  склейка в один разворот допустима как дополнительное presentation derivative,
  но не как единственное audit/source representation. Partial child crops после
  этого не публикуются повторно и остаются evidence-only.
- Процессная причина: PROC-024.
- Доказательства:
  - полные renders source PDF pages 106–107 и screenshot пользователя от
    2026-09-02;
  - reconstruction `pages/page-106.md` и `pages/page-107.md`;
  - `publication_config_v1.json`, hierarchy unit
    `viral-keeper-map-ground-floor-basement`, `source_pages: [106, 107]` и три
    reader assets `page-106-ground-floor-key.jpg`,
    `page-106-ground-floor-plan.jpg`, `page-107-ground-floor-east-wing-map.jpg`;
  - `MASTER_EN.md`, строки 4734–4772.

### OUT-025 — Обороты pregenerated investigator sheets потеряли full-page facsimile

- Статус: `DEFECT` полноты player handout; пользователь заметил 2026-09-02 на
  примере Marco Proudfoot pages 111–112.
- Source pages 111–122 составляют шесть пар нестандартных Spektral Krew
  investigator sheets: Marco 111/112, Corrina 113/114, Enoch 115/116, Peter
  117/118, Ku Hyeon 119/120 и blank template 121/122. Лицевая и оборотная
  страницы каждой пары являются одним physical player handout и должны
  сохраняться как неизменённые full-page facsimiles.
- Текущий reader уже правильно публикует лицевые pages 111, 113, 115, 117, 119
  и 121 как `full_page`. Но для оборотов публикуется только semantic Markdown и
  маленький silhouette crop (`203–234 x 253–259`); full-page back image
  отсутствует. На blank back page 122 дополнительно materialize отдельный
  `Fellow Investigators` crop. Это разбирает авторский лист на части и не
  сохраняет предназначенный игроку printable handout.
- Ожидаемый reader: для каждой пары сначала полная лицевая страница, затем
  полная оборотная страница в исходном виде. Текст внутри facsimile не
  переводится и не заменяется реконструированной таблицей/формой.
- Для оборота дополнительно сохраняется отдельный доступный и переводимый
  semantic text: `Background` с десятью field labels, `Gear and Possessions`,
  `Cash and Assets`, `Quick Reference Rules` и character-specific
  `... Responsibilities`; для blank template — его фактические section labels,
  включая `Fellow Investigators`. Этот слой дополняет изображение, а не
  заменяет его.
- После добавления full-page back facsimile silhouette, quick-reference и
  diagram child crops не публикуются повторно; они становятся evidence-only,
  если не существует отдельного явного reader use case.
- Процессная причина: PROC-025.
- Доказательства:
  - полные source PDF renders pages 111–112 и screenshot пользователя от
    2026-09-02;
  - reconstruction `pages/page-111.md` … `pages/page-122.md`;
  - `publication_config_v1.json`: front assets имеют `semantic_role: full_page`,
    а back reader assets являются только silhouette crops; back structures
    классифицированы как `semantic_card`;
  - `MASTER_EN.md`, Marco pair около строк 4844–4908 и повторяющиеся пары ниже.

### OUT-026 — Source pages 123–124 исключены из reader как реклама

- Статус: `ACCEPTED USER SCOPE DECISION`, 2026-09-02; это намеренное исключение,
  а не потеря extraction.
- Page 123 — рекламная страница `SPEKTRAL KREW` / `Merchandise`: футболка,
  кепка, patch, badge/T-shirt, Zazzle call-to-action и QR-код. Page 124 —
  promotional back cover с tagline, synopsis и publisher marks. Пользователь
  определил обе страницы как ненужную рекламу.
- Текущий `MASTER_EN.md` ошибочно публикует их после blank investigator sheet:
  `## Merchandise` с пятью assets на строках 5247–5270 и `## Back Cover` с
  текстом/asset на строках 5272–5289.
- Ожидаемый reader: ни headings, ни текст, ни изображения pages 123–124 не
  входят в MASTER_EN, MASTER_RU, artview, HTML, PDF или production.
- Reconstruction остаётся полным для всех 124 source pages. Config/page ledger
  содержит две точные записи `excluded_advertising` с source page, reason и
  source hash; соответствующие hierarchy/assets/xrefs/visual-review units не
  materialize в reader. Conservation QA считает страницы намеренно
  исключёнными, а не missing.
- Exact regression: publication page scope заканчивается page 122; reader не
  содержит `viral-merchandise`, `viral-back-cover`, Zazzle QR или back-cover
  asset/text; audit inventory по-прежнему доказывает наличие pages 123–124.

## B. Проблемы процесса и пайплайна

### PROC-001 — QA-размер вырос до 371/119/490 проверок без соразмерной пользы

- Статус: `DEFECT` проектирования QA; пользователь оспорил 2026-09-01.
- Наблюдение: verifier получил 368 mutation cases плюс build/protected suites,
  а полные прогоны многократно повторялись и занимали значительное время.
- Риск: тестируется матрица селекторов, а не основной риск MinerU и
  AI-объединения; высокая стоимость доказательств маскирует отсутствие простой
  проверки полезного результата.
- Системный вопрос: заменить exhaustive selector matrix риск-ориентированной
  пирамидой — несколько schema/unit tests, один representative mutation на
  класс инварианта, integration smoke и визуальная/семантическая QA реального
  сценария.

### PROC-002 — Смешались понятия intake-копии источника и результата MinerU

- Статус: `DEFECT` контракта/коммуникации.
- Наблюдение: часть QA искала или доказывала побайтовую source copy, хотя
  ожидаемые продукты MinerU — overlay PDF, метаданные и извлечённый текст.
- Принятое правило пользователя: внешний PDF сначала копируется в рабочую
  область как immutable local input; последующий pipeline не должен зависеть
  от исходной внешней папки.
- Системный вопрос: формально разделить `ingested_source` и
  `mineru_extraction_outputs`; у каждого собственные manifest, identity checks
  и cleanup lifecycle.

### PROC-003 — QA первоначально зависела от внешнего пути источника

- Статус: `DEFECT` воспроизводимости.
- Наблюдение: исходный PDF был дан из `D:\яндекс\...`, а нормальный поток должен
  сразу создать локальную immutable copy внутри scenario root и работать
  только с ней.
- Риск: недоступность внешнего диска, переименование или синхронизация ломают
  повторный прогон и независимую QA.
- Системный вопрос: обязательная операция ingest до MinerU, после которой
  downstream получает только scenario-local path и recorded source hash.

### PROC-004 — Запрашивалось отдельное разрешение на штатную очистку temp copy

- Статус: `DEFECT` governance granularity.
- Наблюдение: обычный `TemporaryDirectory.cleanup()` после остановки локального
  API был вынесен в отдельный approval, хотя это нормальная часть ограниченного
  lifecycle.
- Риск: процесс останавливается на безопасных штатных действиях и создаёт
  ложное ощущение, что pipeline не знает собственных границ.
- Системный вопрос: заранее описать разрешённый lifecycle run-local temp roots;
  спрашивать пользователя только при ручной, широкой или неоднозначной очистке.

### PROC-005 — Evidence capture стал тяжелее самой проверки

- Статус: `DEFECT` процесса QA.
- Наблюдение: тесты пришлось повторять после потери PTY output; затем создавались
  большие receipts и отдельные audit objects для каждого mutation case.
- Риск: повторные 17-минутные прогоны возникают из-за транспорта доказательств,
  а не из-за изменения кода или нового риска.
- Системный вопрос: команда QA должна писать атомарный machine-readable summary
  и bounded raw log сама; receipt ссылается на них и не пересказывает весь
  execution stream.

### PROC-006 — Роли моделей назначались непоследовательно

- Статус: `DEFECT` orchestration.
- Принятое правило пользователя:
  - Luna выполняет только подготовленные bounded QA scripts/commands;
  - Terra строит reusable code, fixtures и tests;
  - GPT-5.5/high выполняет независимый финальный critique/release review;
  - для рабочей скорости разрешён accelerated service tier;
  - UI-chat или agent выбирается по удобству, а завершённая задача затем
    архивируется/закрывается.
- Риск: executor начинает проектировать тесты, critic участвует в реализации,
  либо orchestration тратит время на искусственные запреты выбора транспорта.
- Системный вопрос: один короткий role-routing contract, проверяемый перед
  dispatch, без отдельных разовых запретов для каждого чата.

### PROC-007 — Durable goal state и фактическая работа расходились

- Статус: `OPEN`.
- Наблюдение: цель несколько раз выглядела paused/deleted/blocked, хотя рабочие
  артефакты и действия продолжались.
- Риск: UI-goal становится ложным источником состояния; восстановление зависит
  от длинного chat history.
- Системный вопрос: canonical state должен жить в компактных context/plan/status
  artifacts, а UI-goal быть только указателем на них, не единственным носителем.

### PROC-008 — Frozen candidate не был физически защищён от последующей работы

- Статус: `DEFECT`; процессная причина OUT-003 ещё не установлена.
- Наблюдение: preservation work декларировала Candidate C read-only, но payload
  исчез.
- Системный вопрос: после freeze создавать manifest-sealed content-addressed
  snapshot; subsequent tools получают deny-write boundary или работают только
  с копией; после каждой операции выполняется cheap seal verification.

### PROC-009 — QA проверяет наличие и owner арта, но не его относительный порядок

- Статус: `DEFECT`; процессная причина OUT-005.
- Наблюдение: tests/verifier закрывают identity, количество, единственность,
  `owner_anchor` и сортировку по `placement_index`, но не проверяют, находится ли
  арт до/после правильного source fragment.
- Дополнение по pages 31–32: verifier проверяет совпадение output owner с
  declared config owner, но не доказывает сам declared owner из source section
  boundaries. Поэтому два ошибочных `owner_anchor: viral-isola-prologue`
  проходят как внутренне согласованные, хотя reconstruction однозначно ставит
  оба assets до heading `Prologue`.
- Почему это прошло визуальную QA: существование правильной картинки внутри
  правильного крупного раздела удовлетворяло текущему контракту, хотя source
  reading order уже был потерян алгоритмом.
- Системный вопрос: добавить order-conservation contract и representative tests
  как минимум для `image before text`, `image between fragments`, `multiple
  images on one page`, `images immediately before next section heading`,
  cross-page section tail и осознанного relocation override. Config validation
  должна выводить/проверять owner из соседних source boundaries, а не только
  сравнивать output с собственным declaration. Визуальный bundle
  должен показывать source/overlay и reader в сопоставимом порядке, а reviewer
  должен явно подтвердить placement, не только identity.

### PROC-010 — Cross-view merge не запрещает text/image semantic duplication

- Статус: `DEFECT`; процессная причина OUT-006.
- Наблюдение: page 6 decision одновременно выбрал pipeline/OCR image block 42
  как `asset` и overlapping hybrid text block 86 как `structure`, хотя оба
  представляют один `Summary` heading. Decision был помечен
  `visual_reviewed: true`, а unresolved list остался пустым.
- Почему это прошло: merge contract проверяет валидность выбранных raw refs и
  отсутствие формально открытых blockers, но не доказывает, что выбранные
  блоки семантически непересекаются между views.
- Системный вопрос: перед materialization строить cross-view conflict pairs.
  High-IoU `image vs heading-text` требует одного из исходов:
  `text_wins_crop_evidence_only`, `visual_hero_with_accessible_heading`, либо
  явного reviewed exception. Одновременное reader-emission без классификации
  должно fail closed.

### PROC-011 — Extracted asset по умолчанию считается ценным для reader

- Статус: `DEFECT`; процессная причина OUT-007 и один из факторов OUT-006.
- Наблюдение: пять platform/promotional crops получили `representation: reader`
  без отдельного доказательства reader value; `inline` описывает только размер,
  но не смысл и не необходимость публикации.
- Системный вопрос: между extraction и publication нужен обязательный
  `reader_value` gate. Допустимые исходы: `content_art`, `semantic_visual`,
  `physical_unit`, `platform_logo`, `promotional_badge`,
  `decorative_residue`, `evidence_only`. Только первые три могут автоматически
  претендовать на reader; `platform_logo` и `promotional_badge` по умолчанию
  получают `reader_value: false`, а исключение требует точного reviewed override.

### PROC-012 — Merge умеет выбирать blocks, но не восстанавливает composite unit

- Статус: `OPEN`, long-term research backlog; не блокирует текущий pipeline.
- Наблюдение: три-view merge объединяет и классифицирует готовые raw blocks. Он
  не строит новый composite candidate из общей source-region/layout semantics,
  если ни один engine не экспортировал всю визуальную единицу одним image.
- Почему три прогона не помогли: два hybrid view согласованно раздробили page 7,
  а OCR view распознал ещё меньше asset-семантики. Majority/union такого набора
  повышает уверенность в блоках, но не обнаруживает общее ошибочное допущение.
- Системный вопрос: перед reader-asset selection нужен отдельный
  `composite-unit proposal` по enclosing frame/background, совместной геометрии,
  page-region semantics и/или AI visual review. Candidate должен хранить точный
  source bbox и отношения `contains child blocks`; выбор parent автоматически
  запрещает двойную публикацию его children, кроме явного reuse override.
- Representative regression: page 7 должна предоставлять reviewer взаимоисключающий
  выбор `whole panel` либо `semantic text + selected children/suppression`, а не
  только набор фрагментов.

### PROC-013 — Reconstruction приняла malformed `CRCRLF` как допустимый EOL

- Статус: `DEFECT`; процессная причина OUT-009.
- Наблюдение: 40 из 124 finalized page Markdown files, все в диапазоне
  `page-001` ... `page-043`, содержат последовательности `CR CR LF`. В
  `RECONSTRUCTED_EN.md` измерено 3788 нормальных `CRLF` boundaries и 1229
  дополнительных lone `CR`; это даёт 579 runs ровно по три blank lines.
- Lineage: повреждение уже присутствует в первом
  `20260901_step6a_ai_merge_candidate` и побайтово наследуется v2, v3, v4 и
  finalized reconstruction package; master builder не создаёт исходный
  `CRCRLF`, но расширяет его через Python universal-newline reading и
  собственный `"\n\n"` block join.
- Почему QA пропустила: identity/hash/conservation gates закрепили фактические
  bytes, но не проверяли canonical EOL и bounded inter-block whitespace.
- Системный вопрос: Markdown production boundary должен принимать только один
  canonical EOL (`LF` предпочтительно), отклонять `CRCRLF`/lone `CR` и
  проверять максимальный blank-run вне literal blocks. Нужны regression cases
  для `LF`, `CRLF`, malformed `CRCRLF` и сохранения code/literal content.

### PROC-014 — `replace_heading` допускает необоснованное сокращение source title

- Статус: `DEFECT`; процессная причина OUT-010.
- Наблюдение: для семи Spektral Krew entries locator selector содержит полный
  source heading с `(Investigator)`, `(Lead Investigator)` или `(NPC)`, но
  соседнее hierarchy field `title` уже записано без qualifier. Builder удаляет
  selector через action `replace_heading`, затем без дополнительной проверки
  вставляет `hierarchy.title` как новый Markdown heading.
- Почему `APPEARANCE (...)` не пострадал: это nested heading внутри retained
  span. `clean_span()` меняет ему только heading level и сохраняет title text;
  сокращение происходит только на configured owner-heading replacement.
- Дополнительный охват: автоматическая выборка нашла 10 hierarchy entries, где
  source selector содержит скобочную часть, а output title её не содержит:
  семь персонажей, две локации с итальянскими названиями и Hastalÿk с
  pronunciation hint. Пользователь подтвердил, что все 10 должны сохранять
  скобочную часть.
- Тот же invariant применяется к любому lexical drift: page 68 selector
  `New Spell` не может быть заменён hierarchy title `New Spells` без отдельного
  reviewed transformation record.
- Системное правило: contract для `replace_heading` обязан сохранять normalized
  source title целиком. Role qualifier, nickname, alternate/original name и
  pronunciation hint запрещено удалять. Отдельный compact navigation label или
  anchor slug не изменяет reader heading. Verifier должен сопоставлять selector
  и emitted heading, а не только emitted heading с уже сокращённым config.

### PROC-015 — OCR heading depth подменяет semantic `heading vs inset`

- Статус: `DEFECT`; процессная причина OUT-011.
- Наблюдение: все meaningful blocks page 12 во всех трёх MinerU views имеют
  общий тип `text`; отдельного `sidebar`, `card`, `callout` или enclosing-panel
  объекта нет. Reconstruction назначила части визуальных labels Markdown `#` и
  `##`, не сохранив физическую светло-серую панель как layout unit.
- Builder затем механически вычисляет nested level как
  `owner_level + source_hash_count`. Поэтому source `# Maya's Secrets` становится
  `####`, source `## APPEARANCE` становится `#####`, и визуальная типографика
  ошибочно превращается в semantic parent/child relation.
- Page 12 является обязательным complex regression fixture со следующим
  reading-order graph по номерам пользовательского overlay:
  - `1` — продолжение основной прозы Emily;
  - `2+3` — atomic inset `APPEARANCE (SUPER FAN OPTION)`;
  - `4–7` — основная проза `Another Ghost Hunter Option`, продолжающаяся между
    колонками;
  - `8+9` — atomic inset `APPEARANCE (ANOTHER GHOST HUNTER OPTION)`;
  - `10+11` — atomic inset `Keeper's Notes`;
  - `12` — настоящий section heading `Creating New Investigators`;
  - `13–17` — его prose, включая run-in label, но без новых outline headings.
- Системное правило: до MASTER assembly нужен explicit layout-unit pass с
  классами как минимум `section_heading`, `run_in_label`, `prose`, `inset` и
  `asset`. Inset proposal строится по полной странице и сочетает enclosing
  background/frame, shared geometry/padding, typography и reading order; один
  только keyword или OCR heading level недостаточен.
- Document-level repetition является дополнительным сильным сигналом. В
  текущем `MASTER_EN` найдено 8 headings семейства `APPEARANCE`, 5
  `GEAR CARRIED` и 37 `Keeper's Notes`; последний label механически оказался на
  уровнях от `####` до `######`. Такие clusters должны предлагать semantic
  template и проверку всех occurrences до page-by-page materialization.
- Безопасность: high-confidence panel получает `contains child blocks` и
  materializes как один quote/callout. Ambiguous candidate остаётся unresolved
  для bounded visual review; он не может автоматически попасть в outline.
- Verifier должен проверять, что inset title отсутствует в TOC/heading tree,
  blockquote замкнут ровно на child blocks, source order сохранён, а следующий
  настоящий section heading находится вне quote container.
- Общий heading-scope invariant: для каждого emitted heading все blocks до
  следующего heading уровня `<= current` обязаны принадлежать его semantic
  source unit. Если source unit заканчивается раньше и reading order возвращается
  к parent stream, label запрещено materialize как heading; нужен явно
  замыкаемый container (`blockquote/callout/aside`) либо non-heading run-in label.
- Representative regression обязан включать `bounded label + one paragraph +
  parent prose`: folding label не может скрывать parent prose. Дополнительные
  cases — два соседних inset, inset перед настоящим section heading и inset
  между частями cross-column prose.

### PROC-016 — MASTER_EN pipeline не переносит inline style spans

- Статус: `ENHANCEMENT_GAP`; процессная причина OUT-012; не является blocker
  source reconstruction.
- Наблюдение: текущий three-view contract сравнивает block text/type/bbox/assets,
  но не имеет model для character/text spans и их styles. Поэтому три одинаково
  плоских MinerU views не могут majority-merge информацию, отсутствующую во всех
  трёх representations; `visual_reviewed: true` не создаёт style metadata.
- Требуемый reusable слой: `inline_style_spans[]` с `source_page`, block ref,
  exact text offsets, `styles: [bold|italic|underline]`, source bbox, extraction
  method, confidence и visual/native-PDF evidence.
- Пользователь 2026-09-02 подтвердил направление отдельного четвёртого прохода
  с извлечением текста и фиксацией форматирования по blocks. Это не четвёртый
  MinerU/OCR view: рабочее имя канала — `native_pdf_typography`, и он читает
  нативные PDF text objects независимо от трёх content-reconstruction views.
- Контракт прохода разделяет два слоя, которые нельзя смешивать:
  - `typography_runs[]`: font family/name, size, weight/slant, bbox и offsets;
    смена serif/sans, размера или leading помогает классифицировать layout unit;
  - `inline_style_spans[]`: подтверждённые semantic `bold`, `italic` и
    `underline`, которые materialize в reader Markdown/HTML.
- Для born-digital PDF дешёвый first pass должен читать native PDF text spans,
  font names/flags/size и графические линии под text; MinerU text используется
  для lexical alignment. Scan/image fallback строит только flagged visual
  candidates, а не требует full-resolution AI review каждой страницы.
- Минимальные artifacts прохода: `typography_spans.json` со всеми нативными
  runs, `style_candidates.json` с aligned ranges/conflicts и компактный
  `style_candidate_review.html` только для ambiguous/visual-only случаев.
- Привязка к существующим blocks выполняется по page + bbox overlap + lexical
  alignment; одно лишь имя шрифта не имеет права менять текст. Underline может
  быть отдельной PDF drawing line, поэтому сохраняется связь line geometry с
  ближайшим baseline и требует review при неоднозначности.
- Merge обязан сохранять конфликт `plain text vs styled span` как style candidate,
  а не считать views согласованными только по словам. Ambiguous ranges идут в
  bounded crop review.
- Verifier проверяет offset validity, non-overlap/nesting, exact visible text и
  materialization markers. Page 12 является regression fixture для комбинации
  bold-italic run-in, internal italic и underline.

### PROC-017 — Reconstruction не сохраняет physical table как logical table unit

- Статус: `DEFECT`; первая процессная причина OUT-013, OUT-020 и OUT-021.
- Overlay-наблюдение пользователя корректно: продолжение `Signs and Portents`
  во второй колонке page 21 выбрано как набор отдельных text blocks, хотя source
  визуально продолжает одну таблицу.
- На pages 20–22 и 36 accepted decisions выбирают `original_pipeline_ocr`:
  текст ячеек имеет type `text`, а номера строк — отдельные `aside_text` blocks.
  Original/raster hybrid на page 21 видят большие `list` regions, но без
  пригодного cell text. Three-view merge поэтому не получает готового table
  object и обязан реконструировать row/cell relations из geometry и content.
- Page 20 показывает, что такая реконструкция возможна: rows 1–6 `Rumors`
  собраны в смежные pipe rows. Но decisions pages 21, 22 и 36 вставляют пустой
  paragraph между header, separator и каждой row. Значит, ошибка находится не
  только в исходном OCR type: reconstruction непоследовательно группирует одни
  и те же `text + aside_text` patterns.
- Page/column continuation должен сохраняться как единый `layout_unit: table`
  с stable table id, ordered rows, cells, source page+bbox и continuation edges.
  Markdown страницы reconstruction могут иметь локальное представление, но
  sidecar обязан доказывать, что fragments принадлежат одной logical table.
- Та же потеря проявилась на pages 58–60: три визуальные encounter tables
  сохранены как `numbered_record_series` без cell relations; cross-page Outdoor
  table существует только как три declared regions, а не один logical table unit.
- Pages 63–64 повторяют тот же дефект на двух page-local D10 tables: визуально
  непрерывные rows 1–10 с отдельной первой колонкой сохранены как двадцать
  numbered paragraphs без stable table/cell relations.
- Candidate detector для table unit использует совместно enclosing background,
  повторяемые row-number bbox, согласованные column bounds, header tokens,
  vertical adjacency и continuation at page/column edge; один OCR block type не
  является достаточным решением.

### PROC-018 — Semantic-table QA проверяет values, но не Markdown renderability

- Статус: `DEFECT`; вторая независимая процессная причина OUT-013, OUT-020 и
  OUT-021.
- Config уже объявляет `Rumors`, `Signs and Portents` и `Lemon Grove Results`
  как `classification: semantic_table` и
  `representation: semantic_from_accepted_facts`, включая ожидаемые ordered
  row keys. Однако builder не сериализует canonical table из этих facts, а
  переносит исходные fragments через `clean_span()`.
- `structured_resolver()` ищет любые строки, начинающиеся с `|`, отдельно
  проверяет наличие header и последовательность first-column keys, но удаляет
  blank lines только из логики поиска. Поэтому header, separator и rows могут
  быть разделены пустыми paragraphs, все checks проходят, а CommonMark table не
  существует.
- Заявленные visual review requirements `no clipping or broken rows` остаются
  `pending_external_visual_qa`; machine verifier не парсит итоговый Markdown и
  не проверяет rendered DOM/table count. Candidate поэтому смог пройти текущие
  проверки с визуально сломанными таблицами.
- Требуемое исправление Master layer:
  1. materialize `semantic_from_accepted_facts` canonical serializer'ом, а не
     source-fragment passthrough;
  2. merge continuation regions в одну logical table и не повторять page header;
  3. запрещать blank lines между table header, delimiter и rows;
  4. парсить итоговый Markdown/HTML и проверять table count, ordered row keys,
     cell count и absence of orphan pipe rows;
  5. добавить exact regressions для pages 20–22 и 36, включая cross-page и
     cross-column continuation;
  6. добавить pages 58–60: ровно три rendered tables с 12/12/6 rows, без
     heading-row `Cold Spot` и без повторного Outdoor header на page boundary.
  7. добавить pages 63–64: ровно две rendered `D10 | Roll Result` tables по
     десять rows, без orphan numbered paragraphs и без повторного header при
     column continuation page 63.

### PROC-019 — Comparison adapter отбрасывает MinerU heading metadata

- Статус: `DEFECT`; первичная процессная причина OUT-014, OUT-016 и OUT-018. Предыдущее утверждение,
  что MinerU классифицировал имена как обычный текст, было неверным: оно
  описывало уже нормализованный merge packet, а не raw MinerU artifacts.
- Во всех трёх raw `content_list.json` у `Santina Maria Salvatore` и
  `Padre Angelo` стоит `text_level: 2`; raw Markdown всех трёх views содержит
  точные строки `## Santina Maria Salvatore` и `## Padre Angelo`. В selected
  `original_hybrid` `content_list_v2.json` оба блока имеют `type: title` и
  `level: 2`, а model JSON — `paragraph_title`. Синий layout overlay согласуется
  с этими raw semantics.
- `compare_mineru_three_views.py::normalize_content()` (строки 79–96) переносит
  из v1 только `type`, bbox, text и assets, но отбрасывает `text_level`.
  `inspect_view()` (строки 133–148) требует наличие `content_list_v2.json`, но
  не читает его при построении blocks; model JSON и heading markers raw Markdown
  также не участвуют. Поэтому исходный `text + text_level: 2` превращается в
  неразличимый `type: text` в comparison/merge packet.
- Unit test `test_normalization_maps_mineru_page_indices_and_assets` проверяет
  page mapping и assets, но не сохранение `text_level`/semantic title; fixture
  `content_list_v2.json` записывается пустым массивом. Это позволило data-loss
  оставаться зелёным.
- Тот же downgrade подтверждён на повторяющейся hierarchy family
  `Hospital, Cellar` / `Hospital, <Floor>`: это не NPC-specific эвристика, а
  общая потеря MinerU heading semantics.
- На `DSS Incendiary Grenades (12)` два raw views и выбранный
  `original_hybrid` также несут heading metadata, но normalized block 932 её уже
  не содержит. Несогласие третьего view должно оставаться review evidence, а не
  давать adapter право молча стереть положительные признаки двух других views.
- Исправление reusable adapter: сохранять raw `text_level`, сводить v1/v2/model
  и Markdown evidence в отдельные `semantic_type`/`semantic_evidence`, а
  конфликтующие признаки не понижать молча до `text`. Exact regression page 25
  должен доказать, что оба NPC имени входят в merge packet как title candidates;
  regression page 39 должен делать то же для `Hospital, Cellar`.

### PROC-020 — Merge review не сверяет flattened decision с raw semantics

- Статус: `DEFECT`; вторичная процессная причина OUT-014, OUT-016 и OUT-018.
- После потери metadata accepted decision выбирает `original_hybrid` blocks 397
  и 402 с purpose `text` и материализует оба имени plain lines. Ни merge review,
  ни reconstruction verifier не сверяют такой downgrade с selected raw
  `content_list_v2`, model JSON, Markdown headings или layout overlay.
- Publication config создаёт единственный hierarchy row
  `viral-one-night-in-perla-npcs`; дочерних NPC anchors нет. Builder не выводит
  новые headings по смыслу и поэтому не может исправить раннюю потерю.
- Текущая lexical conservation доказывает наличие имён и paragraphs, но не
  доказывает полноту document outline. Visual QA assets знает два portraits,
  однако не проверяет, что каждый portrait связан с отдельным semantic owner и
  его visible name heading.
- Primary verifier должен запрещать silent downgrade: raw semantic title из
  selected view обязан остаться heading candidate либо иметь явный reviewed
  override с причиной. Дополнительный visual detector остаётся страховкой для
  реально пропущенных OCR headings: repeated same-style short name line,
  portrait adjacency, own prose region, peer geometry и общий section owner.
- Outline verifier должен сравнивать semantic candidates с reconstruction и
  Master hierarchy: каждый confirmed candidate имеет ровно один heading/anchor,
  правильного parent и непересекающийся owned span. Exact regression page 25
  требует двух peer NPC headings, а не nested headings и не plain labels.

### PROC-021 — Addressable unit ошибочно приравнен к Markdown heading

- Статус: `DEFECT` publication model; первичная причина OUT-017, дополнительная
  причина OUT-020 и OUT-023.
- Current config выражает каждую адресуемую hospital room только через hierarchy
  row с обязательными `level` и `title`. Builder поэтому всегда печатает heading,
  даже когда source representation является inline/run-in label или компактной
  cross-reference строкой.
- Action `replace_label_retain_remainder` по контракту удаляет label из source
  span, а `assemble_reader()` независимо печатает его как generated heading и
  присоединяет очищенный remainder отдельным block. Таким образом, split является
  детерминированным результатом модели, а не случайной ошибкой Markdown renderer.
- Reusable исправление должно развести три понятия: semantic owner, addressable
  anchor и outline heading. Нужен representation mode вроде `inline_run_in` или
  `compact_xref_row`, который сохраняет label и remainder в одном paragraph,
  допускает anchor/xref, но не создаёт outline node.
- Verifier должен проверять не только наличие anchor/link/text, но и structural
  conservation: одна source cross-reference line даёт одну reader line/block;
  недопустимы orphan `See ...` paragraphs и лишние headings.
- Exact regression source page 45: шесть строк `2E`–`2J` остаются шестью
  компактными rows; label и ссылка находятся вместе; `2I` ведёт на `1O`; ни одна
  из шести записей не появляется в document outline.
- Тот же запрет нужен для table records: `Cold Spot` на page 58 может иметь
  inline emphasis или технический anchor, но не H5 heading, разрезающий table.
- Exact regression source page 67: xrefs `see Infection`, `Infected Flesh in the
  The Reliquae` и `Plague Zombie` разрешаются на stable anchor перед run-in label
  `Infected Flesh:`, но reader не содержит `##### Infection`; обе infection
  tables остаются внутри statblock Reliquae.

### PROC-022 — Card/statblock contracts проверяют literals, но не восстанавливают container

- Статус: `DEFECT` structured publication/QA; дополнительная причина OUT-018 и
  первичная процессная причина OUT-022.
- `structured_declarations()` валидирует schema, source identity, required tokens
  и declared termination. `structured_resolver()` затем ищет тот же очищенный
  source span в reader и доказывает его единственное присутствие, но не создаёт
  container, card title или presentation semantics.
- Поэтому `classification: semantic_card` / `semantic_statblock` и зелёная
  lexical/region evidence не означают, что reader действительно содержит
  карточку. Текущий contract может принять плоские paragraphs и даже чрезмерно
  широкий span, если literals присутствуют в нужном порядке.
- Reusable contract должен разделять source scope и target representation:
  materialize bounded card/callout либо требовать доказательство существующего
  target container; title, точная граница и набор contained blocks должны быть
  обязательными evidence fields.
- Exact regression page 55: `DSS Incendiary Grenades (12)` + stats + footnote
  составляют ровно одну card; следующий `The Devourer is repelled by fire ...`
  находится вне неё; title не plain и карточка не захватывает `Keeper's Notes`.
- Exact regressions pages 65–67: ровно два rendered creature statblocks —
  Devourer и Reliquae; оба имеют title/subtitle и characteristics table. Reliquae
  остаётся одним container через page boundary и содержит две infection tables;
  внешние section heading/description находятся до container, внутренние
  `The Reliquae` и `Cursed Plague Zombies` присутствуют внутри него. Plague Monk
  не получает stat grid.

### PROC-023 — Fragment emission не сохраняет global source/subtree order

- Статус: `DEFECT` reader assembly; первичная причина OUT-019.
- `fragment_emission_plan()` обходит bindings и direct children, но вставляет
  descendants только тогда, когда все их spans лежат между двумя соседними
  собственными spans parent. Descendant, расположенный после последнего parent
  span, не закрывается внутри subtree и позднее emitted отдельным проходом.
- Appendix является точным контрпримером: parent labels на pages 60/65/68
  попадают между собственными Appendix spans page 58 и page 68, поэтому headings
  трёх будущих разделов materialize сразу; их реальные descendants остаются на
  поздний проход. Собственный page-68 fragment Appendix затем выходит раньше
  encounter children pages 58–60.
- Numeric `assembly_binding.order` и source span hashes существуют, но final QA
  не проверяет монотонность emitted source coordinates, contiguous subtree spans
  или соответствие document outline source hierarchy. Anchor/link/count
  invariants поэтому остаются зелёными при семантически перемешанной книге.
- Reusable исправление: строить единый source-ordered event stream по
  page+bbox/line offsets, открывать ancestor headings перед первым descendant и
  завершать subtree до следующего peer; затем проверять monotonicity, parent
  containment и отсутствие header-only nodes, отделённых от первого content
  fragment другим peer subtree.
- Exact regression Appendix: после `Encounters` intro немедленно идёт Outdoor
  table; `New Rules` появляется только после Catacomb row 6; `New Mythos Horrors`
  начинается на page 65; `New Spell` и `A Few Pointers ...` остаются на page 68
  в исходном порядке.

### PROC-024 — Keeper-map QA проверяет наличие crops, но не полноту physical unit

- Статус: `DEFECT` art/handout contract; первичная причина OUT-024.
- Текущий config правильно объявляет pages 106–107 одной `owned_page_unit` и
  требует `all map pages and continuations present`, однако проверяет только
  наличие трёх заранее перечисленных crops. Их bbox coverage, page aspect,
  полнота исходной страницы и отсутствие срезанного map content не проверяются.
- Для `map`, `handout`, `form` и `pregen sheet` source scope должен определяться
  physical page unit, а не набором detected image boxes. Если визуальный объект
  занимает всю страницу или разворот, канонический reader asset создаётся из
  полного page render каждого source page; object crops могут быть только
  evidence или явно reviewed derivatives.
- Reusable QA contract должен проверять: точное множество source pages; порядок
  continuation pages; full-page coverage или явно утверждённый stitched-spread
  derivative; ожидаемый aspect/dimensions; отсутствие clipped content; полноту
  доступного `Key` A–V, legend и scale; отсутствие дублирующих partial crops в
  reader output.
- Exact regression pages 106–107: две полные page images идут подряд; map не
  обрезана; `Key` содержит A–V; legend и scale присутствуют отдельным текстом;
  старые три child crops не materialize повторно.

### PROC-025 — Pregen back page ошибочно признана semantic card вместо visual form

- Статус: `DEFECT` classification/visual closure; первичная причина OUT-025.
- Config асимметрично обрабатывает одну physical pair: fronts pages 111, 113,
  115, 117, 119 и 121 имеют `classification: visual_form` и полный page asset,
  тогда как backs pages 112, 114, 116, 118, 120 и 122 имеют только
  `classification: semantic_card` и child crops. Тем не менее visual-review
  contract оборота требует `complete page closure` и принимает tiny silhouette
  asset как доказательство полной страницы.
- Reusable classification должна сначала распознавать повторяющиеся
  front/back page pairs по full-page geometry, shared visual template,
  alternating source order и owner/name relation. Semantic extraction оборота
  становится дополнительным accessible/localization layer внутри того же
  handout owner, а не альтернативой visual form.
- QA должна требовать для обеих сторон: full-page bounds/aspect/dimensions,
  точную пару и source order, отсутствие clipping, legibility и отсутствие
  дублирующих child crops. Для back дополнительно проверяется полнота section
  labels и extracted text; наличие semantic text не закрывает отсутствие page
  facsimile.
- Exact regressions: pairs 111/112, 113/114, 115/116, 117/118, 119/120 и
  121/122. В каждой reader содержит ровно два full-page facsimiles; back имеет
  отдельный semantic text layer; оригинальный raster остаётся непереведённым.

### PROC-026 — Full-page handouts нужно извлекать из PDF XObject, а не переснимать

- Статус: `PROCESS IMPROVEMENT` source-fidelity; подтверждено live-анализом PDF
  2026-09-02 для pages 106–122.
- Все map/handout/pregen pages 106–122 содержат доминирующий full-page image
  XObject: исходный `DCTDecode` CMYK JPEG `1228 x 1588`, размещённый примерно в
  `[-1.1, -1.1, 613.1, 793.1]` при page box `612 x 792 pt`. Pages 106–112,
  114, 116, 118, 120 и 122 состоят ровно из одного такого изображения, без PDF
  words и vector drawings.
- На fronts 113, 115, 117, 119 и 121 дополнительно присутствует технический
  indexed/Flate image `5 x 1655`, занимающий около двух points у левого края.
  Доминирующий JPEG всё равно покрывает всю страницу, но visual regression с
  полным page render должен подтвердить, что edge strip не несёт значимого
  содержания, прежде чем её отбрасывать.
- Acquisition precedence для full-page facsimile:
  1. распознать dominant image XObject по coverage page box;
  2. извлечь исходный compressed stream напрямую, сохранив source hash,
     dimensions, colorspace и page/xref lineage;
  3. построить детерминированный page render только для visual comparison и,
     при необходимости, отдельную sRGB/web derivative;
  4. если страница действительно composite (несколько значимых images, vector
     graphics, text, masks), использовать полный PDF page render, но никогда не
     GUI screenshot или crop detected region;
  5. проверить full-page closure, clipping, orientation и читаемость до
     публикации.
- Для Viral direct XObject extraction предпочтительнее текущих увеличенных
  reconstruction crops/renders: он сохраняет оригинальные JPEG bytes и не
  добавляет resampling или повторное lossy-кодирование. Accessible/translatable
  text layer извлекается отдельно и не встраивается обратно в facsimile.
- Pipeline placement: extraction bakeoff не входит в пользовательскую проверку
  `MASTER_EN` и не прерывает автоматизируемый переход `MASTER_EN -> MASTER_RU`.
  После построения frozen QA-complete MASTER_RU отдельный Step 8A автоматически
  строит `artview.html` и candidate manifest, показывая рядом current crop,
  direct PDF XObject и при необходимости full-page render. Пользователь получает
  готовые RU и artview одним checkpoint и выбирает `keep`, `replace`, `full page`,
  `keep both`, `suppress`, `manual work` или `reopen masters`; решение
  сохраняется в hash-bound JSON, а не только в browser state.
- `Suppress` допустим для уже классифицированного optional/decorative slot.
  Попытка убрать обязательный map/handout/form, изменить owner/role либо оставить
  два semantic duplicates не является binary-quality решением и должна
  fail-closed вернуть работу в MASTER_EN review с последующей пересборкой RU.
- Step 8A является обязательной зависимостью HTML/PDF. Поэтому обычное
  исправление качества или замена binary asset не вызывает churn принятого
  MASTER_EN/MASTER_RU: publishers разрешают stable logical asset id через
  accepted visual-asset manifest.

## C. Как продолжать сбор

Во время пользовательского чтения новый случай добавляется без немедленного
перестроения Candidate C. Для каждого случая фиксируются:

1. точный фрагмент/путь/страница;
2. наблюдаемое и ожидаемое поведение;
3. повторяемость на других разделах или сценариях;
4. класс: content, structure, asset, provenance, QA, lifecycle или governance;
5. временная квалификация;
6. решение пользователя, если оно уже принято.

После завершения чтения выполняется отдельный системный разбор:

1. сгруппировать случаи по общей причине;
2. восстановить causal chain по scripts/config/receipts;
3. выбрать уровень исправления: skill, reusable script, contract/schema, test,
   governance или только scenario-specific config;
4. сначала исправить минимальный reusable слой;
5. проверить его на synthetic fixture и на Viral;
6. только затем решать, нужен ли новый candidate.

## D. Рабочая гипотеза системной art policy

Статус: гипотеза по замечанию пользователя от 2026-09-02; ещё не frozen design
и не разрешение на изменение Candidate C.

Текущий `semantic_role` Viral смешивает разные понятия. Например,
`full_width` — это способ показа, а не смысл изображения. Для переносимой
политики нужны три независимые оси:

1. `content_role`: `portrait`, `atmospheric`, `logo`, `object`, `map`,
   `handout`, `form`, `cover`, `decorative`;
2. `layout_role`: `inline`, `float_right`, `full_width`, `full_page`;
3. `placement_policy`: `source_order`, `semantic_anchor`, `physical_unit`,
   `fixed_document_slot`, `reviewed_suppression`.

Предварительная матрица:

| Content class | Порядок в MASTER | Допустимый перенос | HTML/PDF presentation |
| --- | --- | --- | --- |
| NPC/character portrait | У semantic heading/lead/caption персонажа | Да, если identity доказана caption/heading/manual override | Обычно right-float с wrap |
| Full-width atmospheric art или logo | Сохранять относительное место из принятого overlay/reconstruction | Только явный reviewed override | Full-width; не менять DOM/Markdown order |
| Section hero с встроенным title | Сохранять hero в source order и отдельный accessible semantic heading | Только явный reviewed override | Full-width hero; встроенный title не заменяет heading |
| Изолированный типографический heading/label crop | Не публиковать как art; сохранить heading text | Нет; crop остаётся evidence-only | Оформлять текст/CSS, не JPEG |
| Изолированный platform logo или promotional badge | `reader_value: false`; не публиковать, сохранить функциональный текст/link, если он есть | Только как часть цельного reviewed in-world handout или отдельный доказанный scenario-identity logo | Evidence-only; не отдельный reader image |
| In-world composite panel / faux website / dossier card | Предлагать как одну physical visual unit в source order; child blocks не публиковать повторно | Только явный выбор разобранного semantic представления или reviewed relocation | Единый region render/full-width; accessible text хранить отдельно от raster |
| Inline contextual art/object | Сохранять source order рядом с исходным абзацем или caption | Только к доказанному reference/caption anchor | Inline или float может быть presentation-only |
| Map/handout/form/pregen sheet | Отдельная physical unit в source/declared order | Только в предназначенный индекс/appendix | Own block/full-page по типу |
| Front/back cover | Fixed document slot | Нет, кроме новой reviewed document architecture | Full-page |
| Decorative/residue | Source order по умолчанию | Suppress только через точную reviewed allowlist | Presentation-specific |

Ключевое правило: CSS float и размер изображения не должны менять его
семантическую позицию в Markdown/DOM. Автоматически отходить от overlay order
можно прежде всего для доказанных semantic classes вроде портретов. Для
atmospheric/full-width art default — order preservation.

### Одностороннее правило разрешения `text vs image`

Пользовательское решение от 2026-09-02: автоматическое разрешение конфликта
должно быть асимметричным.

1. Если хотя бы один принятый extraction view распознал совпадающую область как
   семантический текст, другой view не может автоматически повысить crop той же
   области до reader-art только потому, что назвал её `image`.
2. Для isolated typography (`heading`, `label`, `page number`, decorative word
   mark без самостоятельного изображения) действует `text_wins`: в reader
   публикуется текст, crop остаётся только evidence и не материализуется как
   art.
3. Автоматическое направление `text -> art` запрещено. Для него требуется
   положительное доказательство independent visual content и явная
   классификация.
4. Исключение: map, handout/facsimile, form/character sheet, diagram, logo,
   portrait или atmospheric/section hero не заменяются одним OCR-текстом,
   потому что изображение несёт самостоятельную визуальную информацию. Для
   таких conflict pair результат — `keep_visual_plus_accessible_text` либо
   обязательный review, но не слепое `text_wins`.
5. Если система не может доказать `isolated typography` или `independent visual
   content`, конфликт остаётся unresolved и merge не закрывается.

Для многостраничной карты/handout `full-page` относится ко всем страницам
physical unit. Detected object boxes не заменяют полные page renders: они могут
быть evidence или presentation derivatives, но не единственным reader source.
`Key`, legend, scale и другой переводимый текст сохраняются рядом отдельным
accessible layer, не дублируя child image crops.

То же правило действует для нестандартных scenario-specific character sheets.
Front/back сохраняются целыми непереведёнными facsimiles как одна physical pair.
Для back разрешён и желателен дополнительный переводимый semantic layer с
полями background, gear, assets, quick-reference rules и responsibilities; он
не даёт права удалить или разобрать full-page image.

### Приоритет получения full-page facsimile

`Full-page` не означает screenshot. Если PDF page содержит один доминирующий
image XObject, закрывающий page box, канонический asset извлекается напрямую из
PDF без resampling и повторного JPEG-кодирования. Page render используется для
визуального сравнения и как fallback для настоящих composite pages. GUI
screenshot и detected-region crop не являются допустимым source asset.

Применение к Viral page 6:

- `Summary`: isolated typographic heading; hybrid уже восстановил `Summary` как
  semantic heading, поэтому pipeline/OCR crop block 42 обязан стать
  evidence-only;
- `Overview`: уже представлен текстом, дополнительного решения не требует;
- ruined-hall `Introduction` hero: содержит самостоятельный атмосферный art,
  поэтому сохраняется как visual hero, даже если другой view распознал
  встроенное слово `Introduction` как текст.

Историческое основание:

- `kb_creator/PROJECT_STATUS.md`: source art anchor manifest использовал
  `nearest_source_text_bbox`, `npc_order_on_source_page`, heading order и
  page fallback; позже NPC identity стал fail-closed по caption/heading/manual
  override;
- `kb_creator/scripts/build_innsmouth_html_from_master_ru.py`: 21 exact
  non-full-width placements оформлялись как right-float, а full-width allowlist
  оставалась full-width;
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`: reader-art
  ownership/placement принадлежит MASTER, а right-float/full-width presentation
  принадлежит HTML layer.

## E. Рабочая гипотеза document-level semantic templates

Статус: предложено и подтверждено пользователем 2026-09-02 после выявления
повторяющихся `APPEARANCE`, `GEAR CARRIED` и `Keeper's Notes`; принят
candidate-first workflow без детального сканирования всех страниц, но он ещё не
реализован.

### Зачем нужен слой шаблонов

Page-local OCR видит отдельные text blocks, но не знает, что один и тот же label
повторяется по всей книге и выполняет стабильную semantic функцию. Перед
финальной разметкой нужен document-level pass:

1. нормализовать потенциальные labels без удаления их авторского текста;
2. сгруппировать повторения по lexical form, typography и layout geometry;
3. сравнить окружающие blocks и enclosing visual panels;
4. предложить book-specific template и список исключений;
5. materialize только подтверждённые instances, а неоднозначные оставить на
   bounded review.

Повторение само по себе не даёт права автоматически обрамлять блок. Оно создаёт
template candidate; точный scope подтверждается физической панелью, reading
order и semantic ownership.

### Предварительные шаблоны Viral

| Template | Labels/signals | Scope | MASTER representation |
| --- | --- | --- | --- |
| `character_quick_reference` | `APPEARANCE`, `GEAR CARRIED`, общий серый panel внутри character owner | Все blocks, заключённые в одной физической панели; один или несколько labels | Один blockquote/callout; labels bold; отсутствует в outline |
| `appearance_variant` | `APPEARANCE (...)`, отдельный серый panel | Все contained body blocks до границы панели, не фиксированное число OCR blocks | Отдельный blockquote/callout с полным title |
| `keeper_note` | `Keeper's Notes` и согласованный visual style | Весь panel, включая несколько paragraphs/list/table при наличии | Отдельный blockquote/callout; не heading |
| `sight_vision` | `Possible Vision from The Sight` / `Possible Visions from The Sight`, повторяющийся бледно-зелёный panel | Полный enclosing panel со всеми paragraphs/quote; допускается page-boundary continuation | Один blockquote/callout; source label bold и сохраняется дословно; отсутствует в outline |
| `hospital_region` | `Hospital, Cellar`, `Hospital, Ground Floor`, повторяющиеся `Hospital, ... Wing` и согласованная жирная group-heading typography | Владеет room blocks до следующего peer `Hospital, ...` group либо следующего major location; вложенность floor/wing должна следовать source order | Настоящий heading/anchor под `Hospital Locations`; numbered rooms получают дочерний уровень, run-in labels сохраняются inline; не callout |
| `hospital_room_run_in` | Подчёркнутые numbered labels `1A. ...`, `2E. ...` в начале строки/абзаца; после label идёт тире | Ровно текущая room entry: prose remainder либо компактный `See ...` xref; может иметь технический anchor | Inline emphasis + remainder/xref в одном paragraph; не heading и не outline entry |
| `equipment_stat_card` | Выделенный серый panel с equipment title и полями `Skill`, `Damage`, `Range`, `Uses per Round`, `Malfunction` | Только blocks внутри физической панели: title, stat line(s), footnote; scope завершается по panel boundary | Один bounded blockquote/callout; title сохраняется как card heading, но отсутствует в document outline; optional technical anchor |
| `creature_statblock` | Серая panel, creature title/subtitle, characteristic labels (`STR`, `CON`, `SIZ`...), `ATTACKS`, `SPECIAL ABILITIES` | Вся physical card; допускается page-boundary continuation; вложенные roll tables остаются внутри card scope | Один bounded statblock callout/card; title/subtitle; compact key/value table; section labels bold; attacks/abilities как run-in prose; nested tables canonical; внутренние labels отсутствуют в outline |
| `encounter_roll_table` | Titles `Outdoor Encounters`, `Hospital Encounters`, `Catacomb Encounters`; header `Roll / Phenomenon Encountered`; numbered rows с underlined phenomenon label | Одна logical table до заданного record count; поддерживает page/column continuation без повторного reader header | Canonical two-column Markdown table; title — section heading, row labels — inline emphasis; records отсутствуют в outline |
| `d10_result_table` | Header `D10 Roll Result`; левая колонка содержит ordered keys 1–10; result начинается с underlined label | Одна logical table до десяти records; column continuation не создаёт новый reader header или новый table | Canonical two-column Markdown table; result label — inline emphasis во второй cell; records отсутствуют в outline |
| `full_page_map_handout` | `map`/`handout` classification; визуал занимает page или продолжается на следующей page; рядом есть `Key`, legend или scale | Все source pages одной physical unit в declared/source order; detected child crops не определяют scope | Direct dominant-XObject extraction по возможности, иначе детерминированные полные page renders; optional reviewed stitched spread; `Key`/legend/scale отдельным accessible text; child crops evidence-only |
| `pregen_character_sheet_pair` | Повторяющийся scenario-specific full-page form; чередующиеся front/back pages; общий character/template owner и визуальная рамка | Ровно две полные source pages одной пары; semantic fields оборота принадлежат той же pair; child crops не определяют visual scope | Direct dominant-XObject front/back facsimiles в source order без перевода raster; fallback только full-page render; для back отдельный переводимый accessible text; silhouette/quick-reference/diagram crops evidence-only без отдельного use case |
| `generic_inset` | Уникальный title, но доказанная рамка/background/padding | Enclosing-panel children | Reviewable blockquote/callout candidate |
| `run_in_label` | Bold/italic phrase в начале prose без отдельной панели | Только текущий paragraph | Сохранить emphasis inline; не heading и не callout |

### Почему нельзя использовать `label + ровно один следующий block`

- один исходный paragraph может быть разрезан OCR на несколько blocks;
- panel может содержать несколько paragraphs, list или table;
- `APPEARANCE` и `GEAR CARRIED` могут быть двумя fields одной общей панели;
- page/column boundary может разорвать один semantic body;
- следующий по координатам block иногда относится к соседней колонке или уже к
  parent prose.

Contract поэтому хранит не `next_block_count`, а явное отношение
`layout_unit.contains[]`, source bbox/polygon, owner, reading-order position и
confidence/evidence. Quote закрывается по границе layout unit, а не по появлению
следующего Markdown heading.

### Геометрические сигналы границы врезки

Пользователь дополнительно указал два типовых page-12 случая:

- между `APPEARANCE (ANOTHER GHOST HUNTER OPTION)` и `Keeper's Notes` видны две
  отдельные серые поверхности и whitespace band; это граница двух соседних
  inset units, а не один container с двумя headings;
- после `APPEARANCE (SUPER FAN OPTION)` заканчивается серый background,
  присутствует увеличенный вертикальный интервал и начинается обычная проза
  `Another Ghost Hunter Option.` на основном фоне страницы; это явный возврат
  из inset к parent stream.

Boundary detector должен учитывать совместно:

1. continuity/discontinuity background или frame;
2. vertical whitespace band относительно median local line height, а не
   фиксированное число pixels;
3. совпадение/изменение left-right panel margins и padding;
4. новый title style и начало нового enclosing rectangle;
5. semantic owner и reading-order continuity.

Whitespace сам по себе не доказывает inset boundary: разрыв может возникнуть у
page/column transition, перед art или из-за source design. Но в сочетании с
разрывом серого background и сменой margins он даёт high-confidence boundary.
Обратный пример — общий серый panel Hyeon: `APPEARANCE` и `GEAR CARRIED`
разделены внутренним spacing, но background/frame непрерывен, поэтому это одна
врезка с двумя fields.

### Локальная baseline-сетка и быстрый coordinate proposer

Межстрочный шаг является почти константой только внутри одного style cluster
(font/size/leading) и локального потока, а не для документа целиком. Body prose,
headings, captions, lists, inset text и run-in labels имеют разные line heights
и paragraph gaps. Поэтому detector сначала оценивает median line height и
baseline gap отдельно по page/column/style cluster.

На page 12 `original_hybrid` уже даёт показательные block coordinates:

- `APPEARANCE (SUPER FAN OPTION)` title заканчивается на `y=268`, body
  начинается на `y=270`: internal gap `2`;
- body заканчивается на `y=377`, parent prose начинается на `y=388`: outer gap
  `11`;
- второй appearance body заканчивается на `y=215`, `Keeper's Notes` начинается
  на `y=239`: inter-panel gap `24`;
- Keeper note body заканчивается на `y=344`, настоящий section heading
  начинается на `y=376`: section-boundary gap `32`;
- обычная колонка использует примерно `x=81..491` / `504..913`, а inset body —
  `x=96..478` / `519..898`, то есть имеет согласованный внутренний margin около
  `15` с обеих сторон.

Для Viral координатный pre-pass поэтому может дёшево предлагать inset groups:

1. segment page into columns;
2. estimate local line/baseline metrics;
3. соединить label и body при малом normalized internal gap и согласованных
   horizontal bounds;
4. завершить candidate при скачке normalized gap, изменении margins или
   background discontinuity;
5. подтвердить candidate повторяющимся semantic template и/или visual panel.

Это proposer, а не единственное доказательство: обычный paragraph gap, art
wrap, caption или column break тоже может дать большой coordinate gap. Но
комбинация `known label + local gap jump + inset margins + panel background`
для данного документа должна давать high-confidence candidate proposal без
отдельного AI-решения на каждом occurrence; обрамление выполняется только после
bounded confirmation.

### Candidate-first review вместо полного постраничного сканирования

Принятое пользовательское требование: pipeline не должен подробно анализировать
каждую страницу full-resolution AI review. Нужен быстрый high-recall pass,
который с наибольшей вероятностью находит места вида «здесь возможна
врезка/вставка», после чего проверяются только эти места.

Предлагаемый поток:

1. использовать уже извлечённые line/block coordinates, document-level label
   frequencies и дешёвые native-PDF typography clusters без повторного OCR;
2. дополнить их дешёвым low-resolution анализом background/frame/whitespace;
3. построить ranked `inset_candidates` с page, bbox/polygon, label,
   предполагаемыми child block ids, owner, signals и confidence;
4. для каждого кандидата создать компактный crop preview с соседним контекстом,
   чтобы reviewer видел границу до/после panel;
5. reviewer выбирает `confirm inset`, `reject` или `adjust boundary`;
6. только подтверждённый candidate materializes в `MASTER_EN` как точно
   замкнутый blockquote/callout;
7. verifier проверяет quote closure, source order, child coverage и отсутствие
   inset title в heading tree/TOC.

Оптимизация приоритетов:

- high confidence: повторяющийся known label + inset margins + gap jump +
  background/frame — обязательный короткий review, затем batch application;
- medium confidence: часть сигналов отсутствует — показать расширенный crop;
- low confidence: только одиночный spacing/style signal — не менять автоматически,
  хранить в candidate list для выборочного просмотра.

Для этого достаточно двух review artifacts:

- `inset_candidates.json` — machine-readable предложения и evidence;
- `inset_candidate_review.html` или contact sheet — только flagged crops, а не
  подробный render всех 124 страниц.

Цель proposer — высокий recall при приемлемом числе false positives. Ошибочный
candidate безопасен, потому что до подтверждения он ничего не меняет; пропущенная
врезка опаснее, поскольку снова превращается в ложный heading и создаёт
`heading scope leakage`.

## F. Возможные улучшения MASTER_EN, не блокирующие reconstruction

Эта секция отделяет улучшения reader/production fidelity от gate достоверного
снятия текста и смысла. Наличие записи здесь не удерживает reconstruction step
от приёмки, если text completeness и semantic meaning подтверждены его
собственными проверками.

### ENH-001 — Отдельный native-PDF typography pass

- Связанные записи: OUT-012 и PROC-016.
- Назначение: после подтверждённой реконструкции добавить в `MASTER_EN` сведения
  о том, в каких aligned text blocks/ranges источник использует bold, italic,
  underline и устойчиво отличающийся типографический класс.
- Это возможный четвёртый evidence pass, но не четвёртый MinerU/OCR-прогон и не
  источник текста: `native_pdf_typography` читает born-digital PDF text objects,
  сопоставляет их с уже принятым текстом и не имеет права заменять его.
- Дешёвый полный проход создаёт `typography_spans.json`; только конфликты,
  visual-only underline и неоднозначное alignment попадают в
  `style_candidates.json` и compact flagged-crop review.
- Materialization выполняется на стадии улучшения `MASTER_EN`: настоящие
  bold/italic/underline становятся Markdown/HTML emphasis, а простая смена
  font family остаётся layout evidence и может помогать распознаванию врезок.
- Не является blocker reconstruction step, потому что не меняет подтверждённые
  слова, reading order или смысл; решение о реализации принимается после
  завершения текущего пользовательского ревью.
