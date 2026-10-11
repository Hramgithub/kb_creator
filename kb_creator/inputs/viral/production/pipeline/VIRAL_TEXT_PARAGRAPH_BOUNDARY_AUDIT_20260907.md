# Viral text paragraph-boundary audit — 2026-09-07

## Scope

Проверены:

- accepted MASTER_EN checkpoint D;
- текущий QA-passing MASTER_RU review candidate;
- reconstruction v4 page decisions and page Markdown;
- raw MinerU model metadata трёх extraction views;
- accepted `publication_config_v2.json` и serializer структурных
  `inline_run_in`-блоков.

Accepted MASTER_EN и reconstruction v4 являются замороженными входами. Этот
аудит не разрешает править их вручную на месте: исправление должно создать
воспроизводимый successor через pipeline.

## Результат

Найдены два разных класса дефекта:

- три лишние границы, разрывающие один исходный абзац;
- два схлопнутых многоабзацных run-in-блока, внутри которых потеряны три
  исходные границы абзаца.

Все пять дефектных мест присутствуют и в MASTER_EN, и в MASTER_RU.

## Лишние границы абзаца

### PB-001 — `Bronze / Age`

- Source page: 6.
- MASTER_EN: строки 232 и 234.
- MASTER_RU: строки 232 и 234.
- Reconstruction: `pages/page-006.md`, два соседних текстовых блока.
- Raw MinerU: второй блок `Age, offering...` имеет `merge_prev: true` в model
  metadata; `original_hybrid` и `raster_hybrid` согласны.
- Причина: reconstruction decision/finalization сохранил оба блока, но поставил
  между ними границу Markdown-абзаца вместо применения `merge_prev`.
- Требуемый результат: `Bronze Age, offering...` / `бронзового века и...` в
  одном абзаце.

### PB-002 — `to the / US`

- Source page: 10.
- MASTER_EN: строки 336 и 338.
- MASTER_RU: строки 336 и 338.
- Reconstruction: `pages/page-010.md`, два соседних текстовых блока.
- Raw MinerU: `original_hybrid` и `raster_hybrid` сохраняют два блока, но оба
  ошибочно имеют `merge_prev: false`.
- Причина: одного доверия к `merge_prev` недостаточно; reconstruction review не
  отловил очевидное продолжение незавершённой фразы в соседнем блоке той же
  страницы.
- Требуемый результат: `...send someone over to the US to bring him back...` /
  `...прислать кого-нибудь в США, чтобы вернуть его домой...` в одном абзаце.

### PB-003 — `Bonus / Die`

- Source boundary: pages 50 -> 51.
- MASTER_EN: строки 1722 и 1724.
- MASTER_RU: строки 1722 и 1724.
- Reconstruction aggregate сохраняет между частями маркер
  `<!-- source-page-051 -->`.
- Причина: абзац продолжается через физическую границу PDF-страниц; постраничный
  `merge_prev` не способен выразить такую связь, а aggregate/master builder не
  восстановил continuation boundary.
- Требуемый результат: `...a further Bonus Die to one climber...` /
  `...ещё одну бонусную кость одному взбирающемуся...` в одном абзаце при
  сохранении page provenance вне reader-текста.

## Потерянные границы абзаца

### MB-001 — `Super Fan Option`

- Source page: 11.
- Reconstruction v4 сохраняет два самостоятельных абзаца с пустой строкой
  между ними.
- MASTER_EN: строки 378–379 идут подряд без пустой строки.
- MASTER_RU: строки 378–379 унаследовали ту же топологию и в Markdown/HTML
  отображаются одним абзацем.
- `publication_config_v2.json`: `run-in:viral-runin-super` содержит два source
  span, но `content.xref` соединяет их одиночным `\n`.
- Требуемый результат: первый абзац заканчивается `help the algorithm.` /
  `помогать алгоритму.`, а `Em learned about...` / `О расследовании...`
  начинается новым абзацем.

### MB-002 — `Another Ghost Hunter Option`

- Source page: 12.
- Reconstruction v4 сохраняет три самостоятельных абзаца с двумя пустыми
  строками-разделителями.
- MASTER_EN: строки 385–387 идут подряд без пустых строк.
- MASTER_RU: строки 385–387 унаследовали ту же топологию и в Markdown/HTML
  отображаются одним абзацем.
- `publication_config_v2.json`: `run-in:viral-runin-ghost` содержит три source
  span, но `content.xref` соединяет их одиночными `\n`.
- Требуемый результат: отдельные абзацы начинаются с `Another Ghost Hunter
  Option...`, `She has a stand-offish relationship...` и `When the group finds
  her...`; в переводе — с `Вариант с другой охотницей...`, `Её отношения с
  Корриной...` и `Когда группа находит Эм...`.

### Подтверждённая причина MB-001/MB-002

`viral_publication_projection.py` формирует каждый `inline_run_in` из всех
принадлежащих ему строк вызовом `self.joined(remainder, "\n")`. Одиночный
перенос строки внутри обычного Markdown-абзаца не создаёт новую границу, поэтому
последующий serializer закономерно выпускает один абзац.

В том же модуле уже существует `paragraph_text()`: он читает source gap и
сохраняет подтверждённую пустую строку как `\n\n` вместе с provenance binding.
Следовательно, исправление не требует новой эвристики или переделки MinerU:
run-in projection должен использовать этот уже существующий механизм и
включать separator spans в границы structured event.

## Полный автоматизированный проход

- Raw MinerU models содержат 27 `merge_prev: true` пар во всех трёх views.
- 23 пары уже представлены в MASTER_EN слитым текстом.
- Две записи, обе относящиеся к одному логическому PB-001 в разных views,
  представлены ошибочным разрывом.
- Ещё две записи относятся к одному page-33 фрагменту; в MASTER_EN он уже
  корректно слит после xref-нормализации и не является дефектом.
- Дополнительный document-wide поиск длинных plain-text блоков, разделённых
  пустой строкой после незавершённого токена, дал девять кандидатов.
- Ручная классификация этих девяти кандидатов подтвердила PB-001, PB-002 и
  PB-003; остальные шесть являются намеренными границами: credits, copyright,
  эпиграф перед summary, две строки статблока/заклинания и заголовок handout
  перед его основным текстом.
- В accepted v2 config есть 30 `inline_run_in` events. Только два из них
  содержат более одного исходного prose span: `viral-runin-super` (два) и
  `viral-runin-ghost` (три). Оба соединены одиночными `\n`; это исчерпывающий
  автоматический список дефектов данного serializer-класса.
- Таким образом, run-in scan подтвердил два схлопнутых блока и три потерянные
  границы. Остальные 28 одно-span run-in events этому дефекту не подвержены.

## Pipeline remediation contract

1. Reconstruction merge обязан применять raw `merge_prev: true`, когда оба
   соседних выбранных блока сохраняются как один reader paragraph.
2. После сборки каждой страницы запускать paragraph-boundary audit независимо
   от `merge_prev`, чтобы ошибочное `false` не проходило бесследно.
3. Отдельно проверять границы физических страниц до удаления page markers:
   незавершённая последняя фраза плюс продолжающий её первый текст следующей
   страницы создают review candidate.
4. Не выполнять массовое автоматическое склеивание по одной пунктуационной
   эвристике. Явный `merge_prev` можно применять детерминированно; остальные
   кандидаты требуют сохранённого join/keep decision или fail-closed review.
5. MASTER_EN QA должен проверять отсутствие всех подтверждённых `join`
   boundaries и отсутствие неразрешённых кандидатов.
6. `inline_run_in` projection обязан сохранять source paragraph gaps через
   `paragraph_text()` либо эквивалентное явное представление массива абзацев;
   соединение нескольких prose spans одиночным `\n` запрещено.
7. Валидатор должен независимо сравнивать source paragraph-boundary signature
   structured event с выпущенным Markdown: для MB-001 ожидаются два, для
   MB-002 — три reader paragraphs. Проверки одной текстовой prefix-метки
   недостаточно.
8. После исправления пересобрать successor MASTER_EN, затем MASTER_RU и review
   HTML. Ручные изменения замороженного MASTER_EN/MASTER_RU запрещены.

## Status

`PB-001..PB-003`, `MB-001..MB-002`: closed in production checkpoint
2026-09-08. Successor `MASTER_EN.md` and `MASTER_RU.md` contain the corrected
join/keep boundaries; the production QA checks both repaired false splits and
all three restored run-in paragraph boundaries.
