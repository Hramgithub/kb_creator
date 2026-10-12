# Sourcefold — черновик модели данных пакета книги (v0)

- Дата: 2026-10-13. Статус: **черновик для обсуждения**, ничего не зафиксировано.
- Основания:
  - цель D12 (структурированный двуязычный материал, арты, мета; база для веба
    и Foundry);
  - D13 (общая модель с git_coc);
  - изучение `git_coc` (`git_coc-study.md`);
  - формат CoC7 8.13 в NRI `FoundryVTT/modules/nri-coc-library`;
  - фактическое разнообразие сущностей в DOCX Kremlin, Leningrad, Cursed Idol
    и Fear;
  - текущая семантическая разметка kb_creator
    (`pipeline/semantic_structure.py`, `contracts/page_semantic_structure.v2`).
- Примеры значений ниже синтетические.

## 1. Что показали исследования

### Книги

Статблоки встречаются минимум в четырёх форматах:

| Книга | Формат статблока |
|---|---|
| Kremlin (старая шкала) | строки `ИМЯ:` / `СИЛ: 10 … ХАР: 8` / `НАВЫКИ:` / `БОЕВЫЕ НАВЫКИ: Нож 80%, +1D6`; без ПЗ, РАС, СКО |
| Leningrad (5e) | таблица 2×N характеристик + строки `СКО`, `Бонус к урону`, `Оружие: укус 50%…`, `Броня`, `Заклинания`, `Потеря Рассудка: 0/1D4 при…; 1/1D3 при…` |
| Cursed Idol (7e) | `СИЛ 65 \| ВЫН 55 …`, атаки с половиной и пятой `40% (20/8) — Урон 1d3 + БКУ` |
| Fear (7e) | атаки и полная строка оружия: `50% (25/10), 2/раунд, 4D6/2D6/1D6, 10/20/50 ярдов, осечка 00, вместимость 5`; книги Мифов |

Встречаются также группы («4 культиста», «до 3 …»), божество со значениями
вне шкалы, прочерки `НАР -`, несколько условных потерь рассудка, прегены с
доходом, проверкой Идеи и снаряжением.

Прочие сущности:

- раздатки (газета, телеграмма, письмо, записка, приглашение, глиф),
  нумерованные `A–H`, `№ 1–14`, `Флеботомия № 1–5`;
- карты с таблицами подписей `На карте | По-русски` и ключами локаций;
- случайные таблицы, таблицы инвентаря, read-aloud текст, заметки Хранителя;
- сборник историй (Fear: 26 историй в одной книге).

### kb_creator

Статблок там — это хеш-привязанный диапазон строк Markdown, а не данные.
Раздатки находятся по подписям, отдельной сущности нет. У артов в манифесте нет
роли, страницы, области и подписи. Лучшее описание провенанса арта —
`audit/art/native-recovery-spec.json`: страница, xref, bbox, crop, хеш
исходника.

### git_coc

`id` + `aliases` + `search_text`, имя RU + `name_en`, статус изображения и
флаги качества — хорошие идеи. Но провенанс там в трёх разных форматах, а бой,
навыки и броня существ хранятся строками.

### Foundry CoC7

- Процент навыка не хранится: он равен `base` + adjustments.
- Оружие ссылается на навык по `_id` внутри актёра.
- Урон пишется без бонуса к урону, вместо этого ставится флаг `addb`.
- Потеря рассудка задаётся парой `checkPassed` / `checkFailled` (опечатка
  сохраняется системой).
- Значения навыка на атаку нет: если в книге разные проценты у «укуса» и
  «когтей», их нужно оформлять отдельно.
- Имена хранятся по-русски, связь с системой идёт через CoCID
  (`i.skill.spot-hidden`).

## 2. Принципы модели

1. **Исходное значение никогда не теряется.** Каждое типизированное поле
   хранит `raw` (как в книге), разобранное `value` и при необходимости
   нормализованный вид. Разбор может ошибаться; `raw` остаётся
   доказательством.
2. **Двуязычный текст — один тип** `Text { en, ru, ru_status }`.
3. **Один формат провенанса** для всего (§3.2).
4. **Структура и сущности разделены.** Структура описывает порядок книги
   (разделы и блоки, как в документе). Сущности — то, к чему обращаются
   (персонаж, раздатка, таблица…). Связь между ними — `occurrences`: где в
   структуре сущность описана или упомянута.
5. **Редакция — вид, а не правка.** `source_edition` + исходные значения;
   нормализация в 7e — отдельный производный слой с журналом операций
   (по образцу `U7-word-operations`: `rule_id` + disposition на каждое поле).
6. **Термины по ID.** Ссылки идут на ID общего словаря (D2), а не на строки.
7. **Стабильные ID:** `<book_id>/<kind>/<slug>`, детерминированные. Тот же ID
   используется для детерминированных `_id` при экспорте в Foundry.
8. **Флаги качества** на сущности и поле:
   `needs_review`, `ocr_suspect`, `parse_uncertain`.
9. **Без HTML в данных.** Текст хранится в ограниченном Markdown (жирный,
   курсив, ссылки на сущности); HTML делают экспортёры.

## 3. Общие типы

### 3.1 Text

```json
{ "en": "Ghoul", "ru": "Упырь", "ru_status": "proofread" }
```

`ru_status`: `missing | draft | proofread | reviewed`. Для источников, которые
изначально русские (книга правил git_coc), задаётся `en: null`, а исходным
языком объявляется `ru`.

### 3.2 Provenance

```json
{
  "source_id": "shadows-of-leningrad-1938",
  "pdf_sha256": "E8C21B6D…",
  "physical_page": 14,
  "printed_folio": "12",
  "bbox": [72.0, 410.5, 300.2, 640.0],
  "unit_ids": { "en": "p014_u0031", "ru": "p014_u0031" }
}
```

`source_id` ссылается на `reference/source-registry.json`. `bbox` задаётся в
координатах PDF (left, bottom, right, top) и необязателен. Для русского
корпуса правил вместо страницы PDF используется `chapter/section/page`, но в
тех же полях.

### 3.3 Value

```json
{ "raw": "+1D4", "value": "1D4", "unit": null, "flags": [] }
```

Для чисел `value` — число или `null`. Прочерк `"-"` даёт `value: null` и
`raw: "-"`.

## 4. Пакет книги

```
book/
  manifest.json      # id, источник (из реестра), редакция, версии схем, счётчики, статус
  structure.json     # дерево разделов и упорядоченные блоки текста
  entities/          # по файлу на тип: characters.json, handouts.json, tables.json, …
  art/               # бинарники по sha256 + art.json с метаданными
  terms.json         # использованные ID терминов и локальные (книжные) термины
  normalization/     # необязательно: журнал конвертации редакции → 7e
```

### 4.1 manifest

```json
{
  "schema": "sourcefold.book.v0",
  "book_id": "shadows-of-leningrad-1938",
  "title": { "en": "Shadows of Leningrad, 1938", "ru": "Тени Ленинграда, 1938", "ru_status": "reviewed" },
  "source": { "source_id": "shadows-of-leningrad-1938", "pdf_sha256": "E8C21B6D…", "pages": 21 },
  "game": { "system": "coc", "source_edition": "5e", "normalized_edition": null },
  "kind": "scenario",
  "counts": { "characters": 14, "handouts": 8, "tables": 3, "art": 26 },
  "status": "draft"
}
```

`kind`: `scenario | anthology | rules | supplement`. Сборник (Fear) — это
`anthology`, истории в нём — разделы с `kind: story`.

### 4.2 structure

```json
{
  "sections": [
    { "id": "…/section/area-3", "kind": "location", "level": 2,
      "title": { "en": "Area 3", "ru": "Область 3", "ru_status": "proofread" },
      "provenance": { "physical_page": 9 },
      "blocks": [
        { "id": "…/block/0412", "kind": "read_aloud", "text": { "en": "…", "ru": "…" } },
        { "id": "…/block/0413", "kind": "prose", "text": { … } },
        { "id": "…/block/0414", "kind": "entity_ref", "entity": "…/character/ghoul-pack" }
      ],
      "sections": [ ]
    }
  ]
}
```

Виды разделов: `chapter | story | scene | location | appendix | front_matter`.

Виды блоков: `prose | read_aloud | keeper_note | sidebar | list | quote |
entity_ref | art_ref`.

## 5. Сущности

### 5.1 Character (персонаж, NPC, группа, существо, божество, преген)

```json
{
  "id": "shadows-of-leningrad-1938/character/ghoul-pack",
  "kind": "character",
  "role": "creature",
  "name": { "en": "Ghouls", "ru": "Упыри", "ru_status": "proofread" },
  "aliases": [],
  "group": { "count_raw": "до 3", "count_min": 1, "count_max": 3 },
  "edition": "5e",
  "characteristics": {
    "STR": { "raw": "22", "value": 22, "scale": "3-18x" },
    "CON": { "raw": "13", "value": 13, "scale": "3-18x" },
    "APP": { "raw": "-", "value": null }
  },
  "derived": {
    "hp":   { "raw": "13", "value": 13 },
    "mp":   null, "luck": null, "san": null,
    "move": { "raw": "8", "value": 8, "modes": [] },
    "damage_bonus": { "raw": "+1D4", "value": "1D4" },
    "build": null,
    "armor": { "raw": "9 пунктов …", "value": 9, "note": { "ru": "…" } },
    "attacks_per_round": { "raw": "3", "value": 3 }
  },
  "skills": [
    { "name": { "en": "Spot Hidden", "ru": "Внимательность" }, "term_id": "coc:skill:spot-hidden",
      "specialization": null, "value": { "raw": "70%", "value": 70 } }
  ],
  "attacks": [
    { "name": { "en": "Claw", "ru": "Когти" }, "count": 2,
      "skill_term_id": "coc:skill:fighting-brawl",
      "value": { "raw": "50%", "value": 50 }, "half": 25, "fifth": 10,
      "damage": { "raw": "1D6+БкУ", "dice": "1D6", "adds_db": true },
      "range": null, "uses_per_round": null, "ammo": null, "malfunction": null,
      "special": null }
  ],
  "dodge": { "raw": "40%", "value": 40 },
  "spells": [ { "spell_id": "coc:spell:contact-ghoul", "raw": "…" } ],
  "abilities": [ { "ru": "…" } ],
  "sanity_loss": [
    { "success": "0", "fail": "1D4", "trigger": { "ru": "при нападении" } },
    { "success": "1", "fail": "1D3", "trigger": { "ru": "при наблюдении" } }
  ],
  "investigator": null,
  "portrait_art_ids": ["…/art/ghoul-portrait"],
  "description": { "en": "…", "ru": "…" },
  "keeper_notes": { "en": "…", "ru": "…" },
  "occurrences": [ { "block": "…/block/0414", "provenance": { "physical_page": 9 } } ],
  "quality": { "needs_review": false, "parse_uncertain": [] }
}
```

- `role`: `npc | npc_group | creature | deity | pregen_investigator | entity`.
- `investigator` (только для прегенов): `occupation`, `age`, `sex`,
  `residence`, `income`, `luck`, `idea_check`, `equipment[]`, `backstory`.
- Старые проверки (`Проверка Идеи` и т. п.) — в `derived.legacy_checks`.

### 5.2 Spell, Tome, Weapon

- `spell`: `name`, `alternative_names`, `cost{mp, san, pow, hp, other}` (Value
  + raw), `casting_time`, `type[]`, `description`, `keeper_notes`.
- `tome`: `title`, `language`, `san_loss`, `mythos_gain`, `mythos_rating`,
  `study_time`, `spell_ids[]`.
- `weapon` (каталожное оружие, а не атака персонажа): `name`, `skill_term_id`,
  `damage{raw, dice, adds_db}`, `range{normal, long, extreme}`,
  `uses_per_round`, `ammo`, `malfunction`, `cost`, `era[]`.

Модель совместима с `weapons_for_site` из git_coc.

### 5.3 Handout

```json
{
  "id": "…/handout/a", "kind": "handout", "label": "A",
  "handout_kind": "newspaper",
  "art_ids": ["…/art/handout-a"],
  "text": { "en": "…", "ru": "…", "ru_status": "reviewed" },
  "art_text_policy": "translation_beside_art",
  "player_facing": true,
  "occurrences": [ … ]
}
```

- `handout_kind`: `newspaper | telegram | letter | note | invitation | image |
  glyph | document`.
- `art_text_policy` описывает, как соотносятся текст на картинке и перевод:
  `text_only | art_only | translation_beside_art | original_quoted`.

### 5.4 Table

```json
{
  "id": "…/table/random-encounters", "kind": "table", "table_kind": "random",
  "dice": "1D6",
  "columns": [ { "en": "Roll", "ru": "Бросок" }, { "en": "Result", "ru": "Результат" } ],
  "rows": [ { "range": [1, 1], "cells": [ { "raw": "1" }, { "en": "…", "ru": "…" } ] } ]
}
```

`table_kind`: `random | inventory | schedule | map_key | skills | stat_grid |
generic`. Для `random` поле `range` даёт прямой экспорт в RollTable.

### 5.5 Map

`map`: `art_id`, `title`, `scale`, `labels[{en, ru}]`,
`keyed_locations[{key, section_id}]`. Таблицы подписей
`На карте | По-русски` превращаются в `labels`.

### 5.6 Art

```json
{
  "id": "…/art/handout-a", "role": "handout_image",
  "file": "art/3f1c…e9.png", "sha256": "3F1C…E9", "pixels": [1240, 1754],
  "source": { "physical_page": 18, "xref": 412, "bbox": [ … ], "crop": null,
              "extraction": "native_xobject" },
  "caption": { "en": null, "ru": "…" },
  "depicts": ["…/handout/a"],
  "quality": { "needs_review": false }
}
```

- `role`: `cover | portrait | map | handout_image | illustration | glyph |
  decor`.
- `extraction`: `native_xobject | composite | page_crop | full_page`.

### 5.7 Term

Словарь живёт в репозитории CoC (D2). Пакет книги хранит только ссылки
`term_id` и локальные книжные термины (имена NPC, топонимы) с пометкой
`scope: book`. Формат термина: `id`, `en`, `ru`, `aliases`, `definition`,
`category`, `status (accepted | review_required)`, `sources[]`. Глоссарий
git_coc (34 термина) вливается туда же.

## 6. Соответствие потребителям

| Поле модели | git_coc (monster/weapon) | Foundry CoC7 |
|---|---|---|
| `name.ru` / `name.en` | `name` / `name_en` | `name` / `flags.babele.originalName` |
| `characteristics.X.value` | `characteristics[{name, roll, average}]` | `system.characteristics.x.value` (+ `formula`) |
| `derived.hp/mp/move/db/build` | `stats{…}` (строки) | `system.attribs.{hp, mp, mov, db, build}` (`auto` при отсутствии) |
| `derived.armor` | `armor` (строка) | `attribs.armor.value` (строка) + notes |
| `attacks_per_round` | в `combat` строкой | `special.attacksPerRound` |
| `sanity_loss[0]` | `sanity_loss` строкой | `special.sanLoss.{checkPassed, checkFailled}` |
| `skills[]` | `skills` строкой | embedded skill items; `base` из таблицы CoCID, `adjustments.experience = value − base` |
| `attacks[]` | `combat` строкой | weapon item + ссылка `skill.main.id` на навык актёра; урон без БкУ + `addb`; разные % у атак → отдельные навыки или флаг |
| `spells[]` | `spells` строкой | embedded spell items |
| `description` / `keeper_notes` | `text_ru` | `biography` / `description.keeper` (HTML делает экспортёр) |
| `portrait_art_ids` | `images.art` | `img`, `prototypeToken.texture.src` |
| `provenance` | `source{book, pdf_page}` | `flags.sourcefold.{book, page}` |
| `table` (random) | — | RollTable (`formula`, results с `range`, `description`) |
| `handout` | — | JournalEntry: image page + text page, `ownership` для игроков |
| `section/block` | — | JournalEntry (страница на раздел) |

Чего книги не дают, а Foundry требует (это задача экспортёра, не модели):
CoCID и иконки навыков, `properties` навыков, детерминированные `_id`, токен,
ownership, папки, `_stats`.

## 7. Связь с конвейером

- **Шаг 1 (реконструкция)** даёт упорядоченный EN-текст с провенансом. Это
  ядро kb_creator: три вида MinerU, аудит покрытия, постраничные решения.
  Семантическая разметка kb_creator (heading/list/blockquote/statblock span)
  становится заготовкой `structure`.
- **Новый шаг (извлечение сущностей)** — задание агенту: статблок-span →
  `character` с `raw`, раздатка → `handout` и т. д. Валидатор проверяет:
  - каждое `raw` встречается в исходном спане;
  - числа сходятся;
  - нет потерянных строк спана.

  Это та же идея, что аудит покрытия, но на уровне сущности.
- **Шаги 3–4 (перевод и вычитка)** работают по единицам и переводят и блоки
  структуры, и текстовые поля сущностей. Сигнатура чисел из kb_creator
  применяется к каждому `Text`.
- **Нормализация редакции** — отдельный необязательный шаг с журналом, по
  спецификации U7.
- **DOCX и HTML** — внешние экспортёры, не Sourcefold.

## 8. Открытые вопросы

1. **Глубина типизации в v1.** Типизировать сразу всё (атаки, навыки,
   заклинания) или начать с характеристик, производных значений и потери
   рассудка, а бой и навыки сначала хранить `raw`, как в git_coc?
2. **Нормализация в 7e.** Отдельный слой в Sourcefold, решение сборки базы или
   не делать вовсе?
3. **Объединение одинаковых сущностей между книгами** (одно и то же существо,
   заклинание) — в Sourcefold (ссылки на ID правил) или в сборке базы?
4. **Единицы перевода.** Переводить блоки структуры и поля сущностей как
   единицы одного списка (проще), или сущности переводятся отдельно?
5. **Где живут схемы** — зависит от решения о репозиториях (D13).
6. **Пилотная книга** для проверки модели: Leningrad (самая разнообразная:
   5e, таблицы, раздатки A–H, прегены, карты) или Kremlin (самая маленькая)?
