# git_coc (web_helper_coc_gm) — краткое изучение

- Дата: 2026-10-12. Репозиторий: `https://github.com/Hramgithub/git_coc`,
  HEAD `e033d2a` (2 коммита, 2026-07-11). Локальный клон рядом с проектами:
  `git_coc/`.
- Цель изучения: понять, как веб-помощник соотносится с целью Sourcefold
  (D12: единая база для веба и Foundry).

## Что это

«Помощник Хранителя Call of Cthulhu 7e»: локальное SPA на React 19 +
React Router 7 + Vite 8 + TypeScript, тесты на Vitest. Бэкенда нет: данные —
статические JSON в `public/docs/**`, загружаются через `fetch` (есть проверки,
что большие JSON не попадают в JS-бандл).

Разделы: справочник Хранителя (поиск, калькуляторы 1к100 и встречной проверки,
навыки, термины, таблицы), погони, бой (трекер раундов, ассистенты стрельбы,
автоогня, урона), гримуары и магия (помощник изучения), снаряжение (424
предмета), рассудок и здоровье (калькуляторы, 100 фобий и 100 маний),
существа, состояния. Состояние пользователя хранится в `localStorage` с
импортом/экспортом JSON.

## Откуда данные

Источник — **русская книга правил** (корпус Markdown/JSONL
`../Правила/zov_cthulhu_md_v4_final/...`, вне репозитория), а не английские
PDF. PDF напрямую не используются; **глава 15 со сценариями намеренно
исключена**, сюжетные NPC, улики и сцены в приложение не добавляются.
Каждый раздел собирается своими Node-скриптами (`scripts/build-*`,
`validate-*`, `check-no-bundled-*`).

## Модели данных (по выборке)

| Сущность | Структура | Наблюдения |
|---|---|---|
| Существо (`monstersV3`) | `id`, `name`/`name_en`, `aliases`, `category`, `tags`, `threat`, `characteristics[{name, roll, average, raw}]`, `stats{hit_points, damage_bonus, build, magic_points, move}`, `combat`, `skills`, `armor`, `spells`, `sanity_loss`, `text_ru`, `images`, `source{book, pdf_page, note}`, `data_quality{translated_from_english, ocr_cleaned, needs_manual_verification}` | Характеристики структурированы, а бой, навыки, броня, заклинания — **сырые строки** |
| Оружие (`weapons_for_site`) | `items[{id, title, aliases, groupId, kind, skill[], damage, damageType[], range, attacks, ammo, malfunction, cost, era[], image{}, source{kind, external, localCorpus, ...}, dataQuality{needsManualVerification, flags, ...}}]` + `groups`, `ammunition`, `summary` | Наиболее типизированная модель |
| Справочник | карточки (129), навыки (50: `base`, `category`, `specializations`, `era`), глоссарий (34: `term`, `aliases`, `definition`, `category`, `source[{chapter, section, page}]`) | Глоссарий отдельный, маленький |

## Выводы для Sourcefold

1. **Хорошо дополняет Sourcefold.** git_coc покрывает правила из русской
   книги правил, а сценарии исключены. Sourcefold даёт именно сценарии:
   персонажей, существ, раздатки, таблицы, текст. Вместе это и есть «единая
   база» из D12.
2. **Готовые идеи, которые стоит взять в модель Sourcefold:** `id` + `aliases`
   + `search_text`; `name` RU + `name_en`; ссылка на изображение со статусом;
   флаги качества данных (`needs_manual_verification`, `ocr_suspect`);
   подход «данные отдельно от бандла, загрузка по требованию».
3. **Чего не хватает и что Sourcefold должен сделать лучше:**
   - три разных формата источника (`source{book, pdf_page}`,
     `source{kind, external, localCorpus…}`, `source[{chapter, section, page}]`)
     → в Sourcefold один формат provenance: книга, физическая страница, область;
   - статблоки существ частично строками → в Sourcefold поля боя, навыков и
     брони типизированы;
   - каждая сущность имеет свою ad hoc-схему без общего контракта →
     общие JSON-схемы сущностей;
   - глоссарий из 34 терминов живёт отдельно от общего словаря CoC (D2) →
     один словарь с ID терминов, на который ссылаются и Sourcefold, и сайт.
4. **Гигиена репозитория (к сведению):** 153 МБ изображений и данных в
   `public/docs` без LFS; закоммичены каталоги `backups/` и отчёты;
   существа хранятся в нескольких копиях (`monsters.jsonl`,
   `.complete.jsonl`, `_for_site`, `_for_site.complete`, `.min`, `_for_search`,
   `_by_page`) и дублируются между `src/data` и `public/docs`.
5. **Права.** Это русский текст официальной книги правил. Публикация
   «для других пользователей» несёт те же юридические риски, что и переводы
   сценариев (см. D12, вопрос о публичности).
