# Scenario Package Standard

Стандарт описывает именно сценарные проекты в `CoC/Output/Scenarios`. Он не является стандартом rulebook/Keepers book.

## Разделение типов проектов

| Тип проекта | Назначение | Пример |
|---|---|---|
| Rulebook / Keepers book | Индексная база правил, терминов, механик, справочных сущностей и общих знаний. Используется как справочник при подготовке сценариев. | `CoC/Output/Keepers_book/Knowledge_Base`, `CoC/Output/Rules/Innsmouth_Guide` |
| Scenario package | Перевод и пакет конкретного приключения: полный текст, схема вождения, NPC, локации, улики, раздатки, изображения, HTML/PDF и QA. | `Beyond_the_Edge_of_Darkness`, `Crawford_Inheritance` |

Rulebook может быть внешней опорой для сценария, но структура сценарного пакета формируется по сценарным потребностям.

## Цепочка создания

| Этап | Центральный артефакт | Роль |
|---|---|---|
| PDF / source intake | исходный PDF и извлеченные материалы в `Working` | Неизменяемые или рабочие входные данные. |
| Full RU Source | `Working/Scenarios/<Scenario>/Formatted/*Source_Text_Full_RU_vN.md` | Полный русский текст, максимально близкий к источнику. Нужен для сверки полноты. |
| Keeper Full | `Output/Scenarios/<Scenario>/For_Keeper/KeeperBook_vN.md` | Полированный главный документ Хранителя: чтение, подготовка, основа HTML/PDF. |
| Knowledge Base | `Output/Scenarios/<Scenario>/Knowledge_Base/` | Структурированная Obsidian-база: акты, NPC, локации, улики, таймлайн, раздатки, приложения. |
| HTML | `Output/Scenarios/<Scenario>/<Scenario>_Full_RU_vN.html` | Основной удобный формат чтения и передачи. Обычно собирается из `KeeperBook_vN.md`. |
| PDF | `Output/Scenarios/<Scenario>/Pdf/` | Производный удобный экспорт из HTML; не обязан повторять исходную верстку страниц. |

Правило цепочки: `Working/Formatted/*Source_Text_Full_RU_vN.md` хранит максимально полный текст для сверки, а `For_Keeper/KeeperBook_vN.md` является полированным мастерским входом и источником публикации. Не развивать параллельно несколько "главных" полных текстов.

Расширенная воспроизводимая цепочка для новых сценариев:

`source PDF -> env-check -> intake -> page renders -> raw text/OCR -> source-text-qa -> normalize-source-text -> source reconstruction -> source QA -> full RU source -> KeeperBook -> normalize-headings -> term gate -> layout anchors -> review HTML -> image approval/apply -> art integration gate -> production HTML -> PDF export -> release QA -> approval`.

Общий инструмент для воспроизводимых стадий - `translator/translator.py` с config-driven профилем пакета в `translator/config/`. Сценарий хранит свои source/output/QA, а `translator` хранит только универсальные команды и shared helpers.

Для картинок ранняя цепочка расширяется так:

`source PDF -> render-pages -> extract-images -> image inventory -> classify-images -> image-contact-sheet -> prepare-image-approval -> apply-image-approval -> approved Output images -> HTML/PDF integration`.

`extract-images` сохраняет сырой dump embedded images в `Working`, а не в public Output. `classify-images` может автоматически предложить очевидный декор, но роли `source image / handout / NPC / atmosphere / reject` подтверждаются отдельным review/approval. `image-contact-sheet` нужен для быстрой визуальной проверки кандидатов и остается QA-артефактом. `prepare-image-approval` создает шаблон явных решений и не публикует assets сам. `apply-image-approval` в check-only режиме проверяет manifest; с `--apply` копирует только approved assets.

## Public Package и Workbench

| Слой | Где живет | Что хранит |
|---|---|---|
| Workbench | `CoC/Working/Scenarios/<Scenario>/` и `Output/.../project/QA` | Source PDF, page renders, OCR/raw text, extraction dumps, QA, prompts, manifests, временные сборки и отчеты. |
| Public package | `CoC/Output/Scenarios/<Scenario>/` | Только reader-facing артефакты: README/PLAN, KeeperBook, Knowledge Base, production HTML/PDF, финальные Images и manifests/status. |

В public package не держать OCR-стенды, полные dumps извлеченных картинок, временные screenshots, browser profiles, экспериментальные PDF/HTML, сырые исходники раздаток и service-отчеты, если они не нужны читателю или Хранителю как финальный материал.

Допустимое отличие от Wormsign: у CoC сценариев `Knowledge_Base` является частью public package после ручной структурной приемки, а не placeholder.

## Production Gates

Минимальные gates для production-сценария:

| Gate | Смысл |
|---|---|
| `source_pdf_intake` | PDF найден, metadata/hash/page count зафиксированы. |
| `source_text_raw_extracted` | Есть raw text/OCR или зафиксировано, почему нужен ручной extraction. |
| `source_text_normalized` | Есть рабочий normalized draft с page markers; удалены очевидные running headers/page numbers, но порядок колонок еще не считается принятым. |
| `source_reconstruction_prepared` | Есть page-by-page task packet: normalized text, QA findings и page renders сведены для ручного восстановления порядка чтения. |
| `source_reconstruction_accepted` | Ручная реконструкция порядка чтения и структуры принята как source для перевода/Full Source. |
| `source_full_ru_accepted` | Полный русский source сверяется с исходником на полноту. |
| `keeper_full_accepted` | Полированный KeeperBook принят как центральный источник HTML/PDF. |
| `heading_normalization_applied` | Markdown-заголовки KeeperBook нормализованы source-level командой `translator.py normalize-headings`; ручные TOC-ссылки не ведут на старые anchors. |
| `term_gate_passed` | Терминология проверена по CoC reference и локальным решениям. |
| `layout_anchors_accepted` | Спец-блоки, таблицы, карточки, раздатки и диаграммы имеют устойчивые anchors. |
| `review_html_built` | Собран непроизводственный HTML для просмотра/QA из принятого KeeperBook или раннего working draft. |
| `production_html_built` | HTML собран из принятого KeeperBook и самодостаточен. |
| `production_art_integrated` | Активные картинки/раздатки/NPC/atmosphere утверждены, применены в public Images и готовы к вставке в production HTML. |
| `production_pdf_built` | PDF собран из production HTML, если PDF нужен. |
| `production_approved` | README/status/final acceptance обновлены, временные файлы убраны. |

Границы approval фиксировать в `project/PROJECT_STATUS.md`, `project/Build/WORK_LOG.md` и/или `project/QA/final_acceptance_vN.md`.

## Обязательная структура Output

| Путь | Назначение |
|---|---|
| `README.md` | Внешний вход в пакет, список главных файлов и текущий статус. |
| `PLAN.md` | План обработки или миграции сценария, долговременные решения и следующие улучшения. |
| `For_Keeper/` | Главные документы Хранителя. Целевое имя: `KeeperBook_vN.md`; дополнительные индексы допустимы. |
| `For_Players/` | Индексы и материалы, которые можно показывать или передавать игрокам. |
| `Knowledge_Base/` | Obsidian-база сценария. |
| `Images/Handouts/` | Только актуальные player-facing изображения раздаток. |
| `Images/Handouts/Prompts/` | Описания, prompt-файлы, QA-заметки и решения по источникам раздаток. |
| `Images/NPC/` | Утвержденные NPC-изображения и состояния существ/фракций. |
| `Images/NPC/Prompts/` | Описания, prompts и QA-заметки для NPC-изображений. |
| `Images/Atmospheric/` | Атмосферные изображения локаций и сцен. |
| `Images/Atmospheric/Prompts/` | Описания, prompts и QA-заметки для атмосферных изображений. |
| `Images/Source_Images/` | Выбранные source-иллюстрации из PDF, используемые в HTML и справочных материалах. |
| `Pdf/` | Итоговые PDF-сборки. |
| `project/` | Служебные материалы: manifests, status, generation plan, QA. |
| `project/Build/` | Логи сборки, временные review-файлы, очереди генерации, рабочий лог. |
| `project/QA/` | Отчеты проверок: ссылки, таблицы, полнота, изображения, HTML/PDF, Obsidian. |

## Правила версий и cleanup

- Не перезаписывать `*_vN`-файлы поверх старой версии. Новая значимая сборка получает `vN+1`.
- Старые версии HTML/PDF/source можно удалять или переносить только после явного решения по cleanup; по умолчанию они остаются как история работы.
- `production_approved` переводит сценарий в состояние `accepted`: финальный HTML/PDF/KB утвержден и лежит в `Output`, но `Working` еще не считается очищенным автоматически.
- Состояние `archived` ставится только после отдельной cleanup-операции: удалены временные `_tmp`, cache, render dumps, промежуточные PDF/HTML/PNG, устаревшие QA-run папки и неутвержденные backups.
- Cleanup не должен удалять source-first текст, KeeperBook/source acceptance evidence, manifests, term/QA decisions, `PROJECT_STATUS.md`, `WORK_LOG.md`, rebuild recipe и reusable scripts/configs, если они нужны для понимания или пересборки production-артефакта.
- Результат cleanup фиксировать в `project/PROJECT_STATUS.md`, `project/Build/WORK_LOG.md`, manifest или финальном QA/acceptance-файле.
- Если в проекте уже есть Git, не создавать отдельные `project/Backups` как постоянную практику. Исключение - ручной временный backup перед рискованной миграцией, который затем разбирается.
- `project/Build/WORK_LOG.md` ведется на уровне сценария: важные решения, генерации, сборки, QA и правки из чата должны быть восстановимы из этого файла.
- `project/PROJECT_STATUS.md` фиксирует текущее состояние пакета, а не историю всех попыток.
- `PLAN.md` хранит план обработки сценария и новые правила, появившиеся в ходе работы; если пользователь меняет правило, его нужно занести в план/стандарт до или вместе с применением.

## Рекомендуемая Knowledge Base

| Файл | Назначение |
|---|---|
| `00_Passport_v1.md` | Паспорт сценария, карта файлов, статусы, исключения и назначение артефактов. |
| `01_Scenario_Overview_v1.md` | Быстрый обзор сценария, тайна, маршрут, угрозы и финальные развилки. |
| `02_Acts_v1.md` | Акты, сцены, входы/выходы, развилки, блок-схема вождения. |
| `03_Locations_v1.md` | Локации, входные/выходные точки, улики, NPC, состояние после посещения. |
| `04_NPC_v1.md` | NPC, фракции, состояния, мотивации, ссылки на статблоки и изображения. |
| `05_Clues_v1.md` | Улики, где они находятся, куда ведут, какие handouts/изображения связаны. |
| `Artifacts / Spells / Books / Mythos` | Разделяются по природе сценария. Для одного сценария это могут быть `Artifacts`, `Spells_and_Rituals`, `Books_and_Texts`; для другого - отдельный `Mythos`. |
| `Events` | События, триггеры, условные осложнения и реакции мира. Не должен дублировать полный календарь, если есть отдельный `Timeline`. |
| `Timeline` | Историческая хронология, игровой календарь, таймеры и события "через N дней". |
| `Rewards` / `Sanity` | Награды, поражения, последствия и потери/восстановления Рассудка. Можно разделять или держать вместе, если сценарий малый. |
| `Handouts` | Игровой индекс активных раздаток: связь с PNG-файлами, момент выдачи и смысл для расследования. Не хранить здесь render-методику. |
| `Appendices` | Статблоки, таблицы, семейные деревья, дополнительные приложения. |
| `KB_Audit` | Состояние базы, ссылки, остаточные риски и следующие проверки. |

## Роли KB-файлов

| Роль | Правило |
|---|---|
| `01_Scenario_Overview` | Короткий вход в сценарий: завязка, тайна, центральная цепочка, что читать дальше. Не дублировать полные списки NPC, локаций, улик и наград. |
| `02_Acts` | Главный слой вождения: акт, вход, сцены, развилки, что должны понять сыщики, выходы. Если есть блок-схема, она живет здесь или ссылается на `Diagram_Variants`. |
| `03_Locations` | Локации с входными/выходными точками, NPC, уликами, изменением состояния после посещения. |
| `04_NPC` | Все NPC и фракции, включая состояния существ/культов. Для состояний с разной механикой делать отдельные подзаголовки и ссылки на статблоки в `Appendices`. |
| `05_Clues` | Таблица улик обязана иметь ссылки в колонках "где" и "куда ведет", когда такие точки есть в KB. Если улика имеет изображение/handout, ссылка идет на активный файл или `09_Handouts`. |
| `06_Events` | Только игровые события, триггеры, осложнения и реакции мира. Историческая хронология, дневной таймер угрозы и календарь будущих событий живут в `Timeline`. |
| `07_Mythos` / lore-файл | Лор, сны, семейная/мифологическая тайна, смысловые интерпретации. Механические награды и SAN не дублировать, ссылаться на `Rewards`. |
| `08_Rewards` / `Sanity` | Единая механическая точка: потери/восстановления Рассудка, прирост Мифов, награды, поражения, юридические и кампанийные последствия. |
| `09_Handouts` | Только игровой индекс активных player-facing материалов. H-файл не обязан существовать, если сцена ведется устно. Сны, угрозы и описания не превращать в раздатки автоматически. |
| `10_Appendices` | Статблоки, таблицы, схемы, семейные деревья и большие приложения. В тексте и KB ставить ссылки на конкретные статблоки/подразделы. |
| `11_Keeper_CheatSheet` | Короткая рабочая шпаргалка, не второй обзор и не второй rewards-файл. Только ссылки и минимум критичных процедур. |
| `12_Timeline` | Историческая хронология, предыстория по датам, игровой календарь, таймер угрозы и события "через N дней". |
| `13_KB_Audit` | Аудит ролей, дублей, ссылок, остаточных рисков. Не использовать как рабочий TODO вместо `PLAN.md` и `PROJECT_STATUS.md`. |

## Правило связанных файлов

В конце каждого крупного KB-файла держать блок `## Связанные файлы`.

Назначение блока:

- показать, куда Хранитель должен переходить из этого файла во время подготовки или игры;
- не дублировать содержание соседних файлов;
- сделать Obsidian-навигацию устойчивой;
- помочь QA быстро увидеть, какие сущности должны быть связаны.

Пример: `05_Clues` связывается с `03_Locations`, `04_NPC`, `09_Handouts`, `12_Timeline`; `07_Mythos` связывается с `04_NPC`, `08_Rewards`, `12_Timeline`, `10_Appendices`.

## Что Beyond Edge дал как production-стандарт

| Область | Решение |
|---|---|
| User-facing Output | Четкое разделение `For_Keeper`, `For_Players`, `Images`, `Knowledge_Base`, `Pdf`, `project`. |
| HTML-first | HTML является основным форматом чтения и передачи; PDF - производный экспорт. |
| Изображения | Финальные изображения отдельно от prompts/QA; оригиналы раздаток из PDF живут в `Working`, не в Output. |
| Manifests | Для handouts, NPC, atmosphere нужны manifests и статусы approval. |
| QA | Все долговременные замечания уходят в `project/QA` и `project/Build/WORK_LOG.md`, а не остаются только в чате. |
| Диаграммы | Для сложных расследований полезны Excalidraw/Canvas диаграммы: основная цепочка, карта актов, сеть улик. |

## Правила изображений и генерации

| Тип | Где финал | Где prompts/QA | Правило |
|---|---|---|---|
| Source images из PDF | `Images/Source_Images/` | `project/QA/source_images_report.md` | Только выбранные иллюстрации, реально используемые в HTML/KB. Полный extraction dump держать в `Working`. |
| Embedded image extraction dump | `Working/Scenarios/<Scenario>/Images/PDF_Extracted_All/` | `project/QA/image_inventory.json` | Сырой результат `translator.py extract-images`. Не использовать напрямую в HTML/PDF без классификации и переименования. |
| Image classification | Финальные роли применяются в `Images/*` | `project/QA/image_classification.json`, `project/QA/image_classification_review.md` | Результат `translator.py classify-images`. Auto-suggested decoration можно отложить; content candidates требуют ручного review. |
| Image contact sheet | Не production | `project/QA/image_contact_sheet.png`, `project/QA/image_contact_sheet_report.json` | Визуальная QA-страница для role approval. Не переносить в public Images. |
| Image role approval | Решения применяются позднее в `Images/*` | `project/QA/image_role_approval.json`, `project/QA/image_role_approval_review.md` | Явная граница approval: `approved/rejected`, `target_role`, `target_filename`. Без этого не копировать картинки в public Output. |
| Apply image approval | `Images/Source_Images`, `Images/Handouts`, `Images/NPC`, `Images/Atmospheric` | `project/QA/apply_image_approval_report.json` | По умолчанию check-only. `--apply` допустим только после заполненного approval manifest; pending/rejected строки не копируются. |
| Original handout sources из PDF | `Working/Scenarios/<Scenario>/Images/Handouts_Original/` | `project/QA/source_images_report.md` | Не класть в Output, если это не player-facing материал. Английские ключи/таблицы вырезать или пересобирать отдельно. |
| Player-facing handouts | `Images/Handouts/` | `Images/Handouts/Prompts/` | В Output остаются только активные картинки. Описания, стиль, prompt, QA и source notes - в `Prompts`. |
| NPC | `Images/NPC/` | `Images/NPC/Prompts/` | Для важных состояний существ/культов допустимы отдельные изображения и отдельные статблоки. |
| Atmosphere | `Images/Atmospheric/` | `Images/Atmospheric/Prompts/` | Делать по списку локаций/сцен; если нужны безлюдные кадры, фиксировать это в prompt. |

Для каждой генерационной партии нужен план или очередь в `project/Build`/`project`, а результат получает статус `candidate`, `review`, `approved`, `rejected` или `superseded` в manifest.

Стиль генерации:

- ориентироваться на стиль исходного сценария: если исходник похож на ЧБ-гравюру, делать ЧБ-гравюру; если на архивные фото, делать архивные фото;
- не копировать конкретную защищенную иллюстрацию как точную репродукцию, если создается новая работа; использовать style brief и описание сцены;
- для handouts различать `image content` (что изображено), `player-facing text` (что видит игрок), `keeper context` (зачем это в сценарии), `generation brief` (как рисовать);
- если есть оригинал из PDF и он годится игрокам, использовать его; если оригинал содержит непереведенный текст/таблицу, делать player-facing версию: картинка отдельно, текст/ключ отдельно.

## Стандарт диаграмм сценария

| Артефакт | Назначение | Где лежит |
|---|---|---|
| A. Основная цепочка | Publish-диаграмма маршрута расследования сверху вниз. | `Knowledge_Base/Diagram_Variants/Investigation_Flow_A_Chain.excalidraw.md` + `.svg` + `.png` |
| B. Карта актов | Рабочая схема актов, сцен и переходов. | `Knowledge_Base/Diagram_Variants/Investigation_Flow_B_Acts.excalidraw.md` + `.svg` |
| C. Сеть улик | Рабочая карта улик, NPC, локаций и угроз. | `Knowledge_Base/Diagram_Variants/Investigation_Flow_C_Clue_Network.excalidraw.md` + `.svg` |
| Canvas-доска | Обзор всех диаграмм рядом. | `Knowledge_Base/Diagram_Variants_vN.canvas` |

Правила:

- Источник правки - `.excalidraw.md`; SVG хранить как векторный экспорт, но для Keeper/HTML/PDF предпочитать PNG-рендер, если SVG ломается в Obsidian, браузере или PDF.
- В Canvas добавлять `.excalidraw.md`, а не SVG, чтобы диаграмму можно было открыть и двигать в Obsidian.
- В `.excalidraw.md` использовать стандартный формат Obsidian Excalidraw: `## Text Elements` и `compressed-json`.
- Block refs в `## Text Elements` должны быть без `_` и спецсимволов, лучше только буквы/цифры; иначе Obsidian может показать `^id` поверх диаграммы.
- Карточки делать шире, чем кажется нужным: title и subtitle должны быть отдельными текстовыми элементами внутри одной группы.
- Стрелки делать простыми двухточечными arrows без сложных маршрутов; пересечения стрелок допустимы, их проще поправить вручную.
- Перед приемкой проверять минимум: `bad_ref_ids=0`, `text_overflow=0`, `box_overlaps=0`, `missing_file_nodes=0`.
- Для нового сценария сначала наследовать этот набор и правила из существующего production-примера, затем менять только содержание и layout.

## Что Crawford дал как стандарт вождения

| Область | Решение |
|---|---|
| Акты | `02_Acts_v1` должен описывать назначение акта, вход, ключевые сцены, развилки, что должны понять сыщики, выход. |
| Таймер угрозы | Если в сценарии есть активная угроза, ее календарь лучше держать в `Timeline`, а конкретные срабатывающие сцены и осложнения - в `Events`. |
| Мифологический слой | Если тайна сценария держится на лоре и наследии, отдельный `Mythos` допустим вместо механического набора `Artifacts/Spells/Books`. |
| Раздатки | `09_Handouts` должен быть игровым индексом. Подробный player content, render brief, keeper context и QA живут в `Images/Handouts/Prompts`. |

## Допустимые различия

| Различие | Когда допустимо |
|---|---|
| `Events` и `Timeline` одновременно | Есть активная угроза: `Timeline` хранит календарь/дни, `Events` хранит игровые срабатывания и осложнения. |
| `Mythos` вместо `Artifacts/Spells/Books` | Сценарий построен вокруг семейной/мифологической тайны, а не вокруг предметов и ритуалов. |
| Совмещенный `Rewards` и `Sanity` | Сценарий небольшой и отдельная таблица Рассудка не дает пользы. |
| `Keeper_Index` рядом с `Keeper_Full` | Допустимо только если это не дубль `11_Keeper_CheatSheet`. Центральным текстом остается `KeeperBook_vN.md`. |

## Единицы измерения в русском master

- `MASTER_EN` сохраняет величины и единицы источника. Метрическая локализация
  выполняется при подготовке `MASTER_RU`, до HTML/PDF.
- В русском reader-тексте метрическая величина является основной и по умолчанию
  единственной. Не оставлять конструкции вида `50 м (165 футов)`, если
  имперская величина не нужна для идентификации исторического предмета или
  неизменяемой надписи на карте/раздатке.
- Использовать системные коэффициенты: `1 in = 2,54 см`, `1 ft = 0,3048 м`,
  `1 yd = 0,9144 м`, `1 mi = 1,609 км`, `1 US gal = 3,785 л`,
  `1 lb = 0,4536 кг`; температуру переводить по
  `°C = (°F - 32) × 5/9`.
- Округлять для использования за столом, а не создавать ложную точность:
  размеры меньше метра — обычно до `5 см`; расстояния до `10 м` — до `0,5 м`;
  расстояния `10–100 м` — до целого метра; большие приблизительные расстояния
  — до удобных `5/10 м` или `0,5/1 км`; температуру — до целого или ближайших
  `5 °C` по контексту.
- Для игровых дистанций Call of Cthulhu, заданных в ярдах, применять табличную
  метрическую шкалу `1 yard ≈ 1 metre`: сохранять числовые пороги и формулы,
  меняя единицу (`3/6/9 yards -> 3/6/9 м`, `STR/5 yards -> СИЛ/5 м`). Это
  сохраняет игровую механику; не заменять такие пороги дробными результатами
  буквального SI-пересчёта.
- Связанные значения переводить одним согласованным набором. Например, нельзя
  независимо округлять дальность оружия, строки его таблицы результатов и
  последующие ссылки на те же диапазоны.
- Текст, напечатанный внутри неизменяемого изображения, не ретушировать на
  стадии MASTER_RU. Рядом давать метрическую подпись, ключ или таблицу, если
  величина нужна для игры.
- MASTER_RU QA должен искать остаточные `ft`, `feet`, `foot`, `yd`, `yards`,
  `mi`, `mph`, `in`, `inch`, `lb`, `oz`, `gal`, `°F` и русские формы `фут`,
  `ярд`, `миля`, `дюйм`, `фунт`, `галлон`. Проверка должна учитывать контекст
  числа/единицы и allowlist, чтобы не ловить имена вроде `Праудфут` или обычное
  значение английского `foot`.

## HTML/PDF

- HTML - главный формат передачи. Он должен быть самодостаточным настолько, насколько возможно: картинки встроены или идут рядом в понятной папке `Images`.
- Для CoC-сценариев базовым оформлением HTML/PDF служит принятый production
  profile «Инсмутского террора»: A4, тёплая книжная палитра и рамки, Georgia,
  одноколоночный печатный основной текст, структурированные statblock cards и
  ролевая раскладка артов. Сценарный builder обязан записывать точное имя и
  версию унаследованного профиля в build config/manifest, а отличия объявлять
  явно; визуальное сходство без конфигурационной связи недостаточно.
- Полноформатные карты, handouts и листы персонажей образуют атомарную печатную
  карточку: стабильный якорь, собственный заголовок, не более трёх коротких
  строк подписи и соответствующий арт. Карточка начинается на новой странице,
  занимает высоту печатной области и не делится. Следующий заголовок или
  переводимый текст не должен попадать под предыдущий арт. Если две стороны
  персонажа извлечены подряд, каждый заголовок переставляется непосредственно
  перед своей стороной до HTML-рендера.
- Обычные сюжетные иллюстрации и портреты в основном тексте получают отдельную
  семантическую роль right-float: `25%` ширины контейнера в reader HTML и PDF,
  обтекание текстом справа и очистку float перед следующим крупным заголовком
  или таблицей. Это presentation-размер; исходный bitmap не уменьшается.
- Графическая раздатка в приложении занимает `80%` ширины, центрируется и
  связывается со своим заголовком и ближайшим описанием в одной печатной
  карточке. Карты Хранителя, прегены и специально принятые opening/full-page
  арты остаются полноформатными и не наследуют правило `25%`.
- Служебные OCR-подписи `Illustration`/`Иллюстрация` подавляются по точному
  configurable allowlist; содержательные подписи сохраняются. Факсимиле с
  текстом можно убрать из reader master только после сохранения всей
  транскрипции и отдельной привязки вложенных карт/изображений.
- Для одноколоночного профиля Chromium недостаточно полагаться только на
  `page-break-after` вложенного `figure`: `column-count: 1` может интерпретировать
  его как колоночную границу. Reusable renderer должен создавать семантическую
  `.full-page-art-card` с минимальной высотой печатной области; QA проверяет
  binding заголовков, отсутствие пустых страниц и визуальный результат.
- Production HTML собирается из принятого `KeeperBook_vN.md`. Не собирать HTML напрямую из raw/source-файла, если KeeperBook уже стал центральным текстом.
- Перед production HTML запускать `translator.py normalize-headings --config ... --apply` по принятому KeeperBook, если в конфиге есть `normalize_headings`. Это правит сами Markdown-заголовки и простые TOC-ссылки; CSS/HTML-нормализация заголовков не заменяет этот шаг.
- `translator.py build-production-html --config ... --check-only` должен блокировать сборку, если нет принятого KeeperBook или обязательные gates false. Это нормальное состояние раннего сценария.
- В HTML не оставлять служебные строки вида `Файл проекта`, абсолютные локальные пути и редакторские meta-комментарии.
- В HTML по месту вставлять активные картинки раздаток/карт/NPC/атмосферы, если они нужны читателю; простая ссылка на файл допустима только в KB/Markdown.
- HTML должен иметь одно кликабельное `Оглавление`. Если в KeeperBook/source есть ручное `Содержание` или `Оглавление`, не дублировать его в HTML: использовать как source/checklist структуры, заменить generated TOC и смерджить недостающие пункты. В generated TOC не включать сам раздел `Содержание`/`Оглавление`.
- Для HTML/PDF TOC использовать `page_map.*.type = source_toc`, как в translator contract. Если исходный PDF не имеет отдельной contents page, но KeeperBook содержит локальное оглавление, заводить documented synthetic TOC page, например `000` с `synthetic: true`, и удалять/заменять его тем же source_toc-механизмом.
- Статблоки в KeeperBook/HTML/PDF оформлять таблицами: характеристики горизонтальной таблицей, производные параметры горизонтальной таблицей, атаки/действия отдельной таблицей. Не оставлять финальные статблоки обычными абзацами.
- Cover/landing page идет до сгенерированного `Оглавления`, если у сценария есть обложка или титульная картинка.
- PDF - convenience export после принятого HTML. Не пытаться повторить исходный PDF постранично; важнее полнота материала, читаемость и наличие картинок.
- PDF собирается из текущего production HTML. Не чинить PDF вручную после сборки: если есть проблема, править Markdown/HTML/CSS/картинки и пересобирать.
- `translator.py build-production-pdf --config ... --check-only` должен блокировать сборку, если production HTML отсутствует, `production_html_built` false или PDF engine не настроен.
- Не вводить жесткие page-break правила без отдельной необходимости. Если PDF ломается, возвращаться к простой continuous-flow сборке.
- Runtime-изображения в HTML/PDF можно оптимизировать в отдельную папку `Images/optimized_jpeg_q80/` на этапе postproduction, не уменьшая и не перезаписывая approved PNG masters. PNG оставлять для alpha, line art, карт/раздаток с текстом и явно отмеченных исключений.

## Layout Anchors

Перед production HTML/PDF нужно принять anchors для материала, который часто ломается при сборке:

- таблицы и статблоки;
- карты и ключи карт;
- handout-картинки и подписи;
- диаграммы и Canvas/Excalidraw exports;
- callout-врезки;
- приложения и статблоки, на которые ведут ссылки из текста.

Если блок нельзя надежно собрать автоматикой, фиксировать локальное правило в `PLAN.md` и `WORK_LOG.md`: что является source of truth, где лежит финальная картинка/таблица и как пересобрать.

## Правила ссылок

- В Markdown-таблицах не использовать wikilink-alias с `|`, чтобы не ломать таблицы.
- Для таблиц использовать обычные Markdown-ссылки или wikilinks без alias.
- В `00_Passport_v1.md` описывать назначение всех основных файлов и папок пакета.
- В `00_Passport_v1.md` не дублировать полные списки NPC/локаций/улик; вместо этого ссылаться на профильные KB-файлы.
- В таблицах `Clues`, `NPC`, `Locations`, `Artifacts` по возможности делать ссылки прямо в значимых колонках, а не только рядом с таблицей.
- Если сценарий упоминает Иннсмут, номера домов, районы, местных NPC или городские справочные сущности сверять с `CoC/Output/Rules/Innsmouth_Guide/Knowledge_Base`.
- Для иннсмутских номеров домов в основном тексте и KB ставить прямые ссылки на соответствующий chapter-раздел `Innsmouth_Guide/Knowledge_Base/Chapters/...#NNN Название`, а не только на `House_Index`. `House_Index.md` использовать как навигационный источник для поиска правильного файла, района и названия.
- Если в сценарии есть список мест Иннсмута, полезно добавить компактный блок `Справка Иннсмута` со ссылками на конкретные дома/районы, но не переносить полный текст справочника внутрь сценария.

## Проверки перед приемкой

Минимальный набор QA:

- `translator.py env-check --config translator/config/<scenario>.package.example.json`, если у сценария уже есть config-driven профиль;
- `translator.py validate-config --config ...`;
- `translator.py intake --config ...` для фиксации PDF metadata/hash/page count;
- `translator.py source-text-qa --config ...` для проверки raw text/page markers, пустых страниц, декоративных заголовков, stat-like lines и переносов перед реконструкцией source;
- `translator.py normalize-source-text --config ...` для создания рабочего Markdown draft из raw text; этот шаг не заменяет ручную реконструкцию двухколоночного порядка и полный `Full RU Source`;
- `translator.py normalize-headings --config ... --apply` для нормализации заголовков принятого KeeperBook перед HTML/PDF: spacing, closing hashes, точечные replacements, level overrides и простые Markdown TOC-links;
- `translator.py prepare-source-reconstruction --config ...` для page-by-page task packet перед ручной реконструкцией: текст, QA findings и page renders должны быть связаны;
- `translator.py prepare-translation --config ... --check-only` для проверки готовности translation task packet; без принятой source reconstruction перевод не готовить;
- `translator.py extract-images --config ...` для embedded image dump и `image_inventory.json`, если PDF содержит иллюстрации/раздатки;
- `translator.py classify-images --config ...` для первичного manifest review перед переносом картинок в public Output;
- `translator.py image-contact-sheet --config ...` для визуальной проверки candidates перед role approval;
- `translator.py prepare-image-approval --config ...` для шаблона явных решений по ролям картинок;
- `translator.py apply-image-approval --config ...` для check-only проверки approval manifest; `--apply` только после явного approval;
- `translator.py build-review-html --config ...` для непроизводственного HTML review artifact; до KeeperBook допустим normalized draft, после KeeperBook source должен быть переключен на центральный `For_Keeper/KeeperBook_vN.md`;
- `translator.py term-gate --config ... --check-only` для проверки source/output Markdown против общего CSV-реестра терминологии; без принятого source/output gate должен быть `blocked`;
- `translator.py layout-anchors --config ... --check-only` для проверки семантических anchors, обязательных паттернов, таблиц/картинок/страничных маркеров и готовности layout gate;
- `translator.py prepare-art-integration --config ... --check-only` для проверки готовности approval/apply/public image targets перед production HTML;
- `translator.py build-production-html --config ... --check-only` для проверки готовности public HTML; без `--check-only` запускать только после accepted KeeperBook, term gate, layout anchors и art integration gates;
- `translator.py build-production-pdf --config ... --check-only` для проверки готовности PDF export; без `--check-only` запускать только после production HTML gate и настройки PDF engine;
- `translator.py release-qa --config ... --check-only` для финальной проверки HTML/ссылок/картинок/локальных путей/release gates перед явным approval;
- `translator.py legacy-script-audit --config translator/config/wormsign.package.example.json` при переносе практик из Dune/Wormsign: copied legacy scripts являются справочным архивом, а не reusable upstream, пока аудит не показывает `config_driven` или пока шаг не заменен generic-командой `translator.py`;
- при сомнении сверяться с `translator/docs/wormsign/Generic_Translator_Migration_Map_20260708.md`: он задает, какие Wormsign-практики уже имеют generic-команду, а какие legacy-файлы остаются только источником идей;
- проверка терминологии через общий CoC term-gate из `CoC/PROJECT_REFERENCE.md`; если сценарий еще не добавлен в общий аудитор, завести локальную QA-таблицу терминов и добавить профиль в `CoC/Scripts/coc_term_gate_audit_20260629.py`;
- parity/source completeness gate: `Full RU Source` и `KeeperBook` не обязаны быть дословной копией исходника, но все source-блоки, статблоки, handouts, таблицы, приложения и картинки должны быть перенесены или явно занесены в список исключений;
- `git diff --check` по сценарию;
- поиск старых путей и абсолютных локальных ссылок в HTML/Markdown;
- проверка Markdown-ссылок на существование файлов;
- проверка wikilinks на существование целевых KB-файлов и ключевых якорей;
- проверка таблиц на пустые строки, сломанные pipe-символы и вертикальные статблоки;
- проверка, что `Images/Handouts`, `Images/NPC`, `Images/Atmospheric` содержат финальные картинки, а prompts/QA лежат в `Prompts`;
- проверка, что все активные картинки из manifests реально используются или осознанно отложены;
- если включена postproduction-оптимизация картинок, проверить, что runtime HTML ссылается на optimized copies, а approved masters остались нетронутыми;
- визуальная проверка HTML в браузере/Obsidian Web Viewer;
- обновление `README.md`, `00_Passport`, `PROJECT_STATUS`, `WORK_LOG`, manifests и `final_acceptance`.
