# KB Creator pipeline — итог Innsmouth и базовая архитектура

Дата среза: `2026-08-30`

Статус: Innsmouth production vertical slice завершён и пользовательски принят;
универсализация на второй сценарий ещё не выполнена.

## Главный итог

`kb_creator` прошёл путь от экспериментальных reconstruction/fixture-гейтов и
разрозненных кандидатов до полного production-пайплайна для одного реального
сценария — `The Innsmouth Terror`:

```text
source PDF
  -> MinerU reading extraction + controlled OCR recovery
  -> RECONSTRUCTED_EN
  -> MASTER_EN
  -> MASTER_RU
  -> HTML
  -> PDF
  -> unversioned production package
```

Каждый переход имеет отдельную ответственность, immutable accepted package,
явную пользовательскую приёмку там, где она нужна, и fail-closed verifier.
Финальный пакет находится в `inputs/innsmouth/production/` и использует
стабильные пользовательские имена без release-суффиксов.

## Ответственность стадий

| Стадия | Что она доказывает | Результат |
|---|---|---|
| Source reconstruction | Текст, страницы, блоки, изображения и видимые semantic containers восстановлены из неизменяемого источника с provenance | `RECONSTRUCTED_EN` + `SEMANTIC_STRUCTURE.json` для structural-profile runs |
| English publication | Реконструкция преобразована в читательский английский master по явно принятой policy | `MASTER_EN` |
| Russian publication | Русский master происходит от текущего `MASTER_EN`, нормативного словаря и пользовательски принятого перевода | `MASTER_RU` |
| Reader rendering | HTML детерминированно собирается из принятого RU без ручной правки результата | HTML |
| Print rendering | PDF добавляет только печатную presentation layer и проверяет физические страницы/ссылки | PDF |
| Packaging | Артефакты, ассеты, owning code, terminology и provenance запечатаны одним manifest | production package |

## 1. Source reconstruction

Реконструкция отделена от издательской редактуры. Исходный PDF неизменяем;
MinerU reading extraction задаёт основной поток, OCR используется только для
контролируемого восстановления, а контрольный PDF остаётся источником полноты
и геометрии. `RECONSTRUCTED_EN` сохраняет все `46` страниц и reconstruction
evidence. Для нового opt-in structural profile визуально подтверждённые
границы quote/callout/handout, list, heading и statblock уже представлены
нативным Markdown на этом уровне. Stage 05 проверяет их вместе с текстовой
полнотой, а Stage 06 повторно проверяет и материализует hash-bound
`SEMANTIC_STRUCTURE.json`. Растровая таблица может остаться
`reference_only`-доказательством, но не заменяет reader-facing semantic text.
Конфликты классификаторов закрываются ролью выбранного блока: вложенный
заголовок сохраняется как ATX heading внутри blockquote, ошибочное title-
понижение требует точной визуально проверенной записи причины, а
image/heading overlap допускается только для читательского asset или для
`structure`-блока, привязанного к типизированному semantic unit. Сам признак
`v2_table_text` заголовком не является.

Визуально компактные последовательности обычных строк оформляются на этом же
этапе как `line_group / hard_break_lines`: reviewed-порядок исходных блоков
задаёт порядок строк, все строки кроме последней получают Markdown hard break,
а перед следующим смысловым блоком остаётся обычная граница абзаца. Stage 05 и
Stage 06 отклоняют пустой абзац внутри группы, пропущенный hard break, перенос
на последней строке или перестановку строк. Эвристика по двоеточиям и названиям
полей не используется.

Подтверждённые по source visual OCR-исправления оформляются точной reviewed
записью `text correction: source -> reader; reason: ...`. Исходный extracted
unit и его hash остаются неизменными; source-форма должна встретиться ровно
один раз в выбранных доказательствах страницы, reader-форма — уже находиться
в reviewed Markdown. Один correction ledger используется и semantic-span
проверкой, и OCR-equivalence audit; неоднозначная, устаревшая или неиспользуемая
поправка блокирует сборку.

Ключевая граница:

```text
RECONSTRUCTED_EN = что было в источнике
MASTER_EN        = что публикуется читателю
```

## 2. MASTER_EN

`MASTER_EN` — publication master, а не очищенный OCR. Он сохраняет уже
принятую reconstruction-структуру и не восстанавливает заново потерянные в
`RECONSTRUCTED_EN` границы. На этом уровне живут:

- scenario/front-matter scope;
- publication heading policy и semantic anchors при сохранении исходной
  иерархии;
- TOC и внутренние ссылки вместо печатных `page N`;
- handout references и deduplication;
- reader-art ownership/placement policy;
- publication-проекция уже восстановленных таблиц и stat-block structure;
- исключение технических `mineru-page`/`table-evidence` комментариев.

Исторический RU, старый очищенный EN и прежний `unit_id/source_hash` bridge не
являются входами финального маршрута. Правильная цепочка:

```text
new source -> new MASTER_EN -> new MASTER_RU
```

Финальный `MASTER_EN r6`: `127823` байта, SHA-256
`5F8284E4FE047F644774A21962E52ECB06B0DF5BD3375F1EE52939F8ED3D234B`,
`33` ассета.

## 3. MASTER_RU

RU-слой строится относительно принятого текущего `MASTER_EN`. Его gate
проверяет английское происхождение, пользовательски принятый RU-кандидат,
официальную терминологию Hobby World/Hobby Games, semantic-anchor projection,
изображения, `51` таблицу, stat blocks, handout policy и внутренние ссылки.

Нормативные примеры: `Track -> Чтение следов`, `Move -> СКО`, `Build -> КМПЛ`.
Прежние RU-переводы могут быть только справочным материалом и не являются
автоматическим источником нового master.

Финальный `MASTER_RU r6`: `189146` байт, SHA-256
`B67CCE65F18984117204A12AD3ACB79E51D2E50622993268121458070B25E2BB`,
`32` используемых ассета.

## 4. HTML

HTML генерируется только из принятого `MASTER_RU`; ручное редактирование
generated HTML запрещено. Pipeline владеет title/TOC layout, внутренними
переходами, right-float/full-width art policy, columns, investigator cards,
handout presentation и удалением технических следов.

Финальный `HTML r6`: `226114` байт, SHA-256
`B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.
Он содержит `32` изображения, `51` таблицу, `45` TOC links, `45` уникальных
direct heading targets, `0` broken fragments и `0` standalone TOC targets.

## 5. PDF

PDF строится только из принятого HTML. Print-stage владеет page boundaries,
front-matter isolation, началом handouts с новой страницы, print-only image
layout и физической проверкой named destinations. Он не меняет upstream text.

Финальный `PDF r7`: `11557577` байт, SHA-256
`6883AE5D15FB498477239B98B3D278E458223EACA1691B3C73EB17F987D5E0E5`.
Свойства: `36` A4 pages, `32` image XObjects, `89` internal links, `0` empty
pages; все `45/45` TOC destinations ведут к ожидаемому heading text, maximum
vertical delta `0.866 pt` при gate `8 pt`.

## 6. Production package

`inputs/innsmouth/production/` содержит стабильные `MASTER_EN.md`,
`MASTER_RU.md`, HTML, PDF, один общий `33`-файловый `assets/`, точный snapshot
`10` owning scripts, используемые translator modules, terminology и
`PRODUCTION_MANIFEST.json`.

Пакет: `70` файлов / `22619186` байт. Manifest: `14435` байт, SHA-256
`40DEB53603F1D4E14769C236663015B125C88EFA62F6F57CC61FBFC6FDBDF103`;
inventory SHA-256
`9A44C69454F243C8717C0A7B41FC34F99A8ABFE440653311090FDB1A084C5E71`.

Verifier отклоняет missing/changed/extra files, неверный accepted provenance,
asset closure drift, PDF identity drift, TOC regression и owning-code drift.

## Нормативная модель состояния

```text
working/
  rebuildable candidate; не является authority

inputs/<scenario>/<stage>/accepted_*/
  immutable accepted input следующей стадии

inputs/<scenario>/production/
  текущий пользовательский snapshot со стабильными именами
```

Build создаёт candidate. Freeze/promote — отдельное действие после явной
приёмки: проверяет explicit identities, публикует через staging, запрещает
overwrite и создаёт acceptance manifest. История живёт в Git, manifest/hash и
QA receipts, а не в именах `_final_rN`.

## Закрытые классы дефектов

- смешивание reconstruction и publication editing;
- перенос старого RU через исторический EN bridge;
- одиночные исправления без full-scope audit;
- печатные `page N` вместо semantic links;
- TOC anchors вне destination headings;
- handout body/application duplication;
- потерянные/лишние изображения и неправильный art owner;
- technical comments в reader artifacts;
- terminology/stat abbreviations drift;
- detached table titles;
- ручные HTML/PDF исправления вне owning layer;
- тесты, зависевшие от заранее существующего ignored working candidate.

Seed case закрывается только по маршруту:

```text
seed -> defect class -> full-scope audit -> owning-layer fix
     -> rebuild -> evidence
```

## QA и cleanup

До production package: `159 passed, 7 skipped, 22 subtests passed`. После
cleanup-focused исправления test isolation: `98 passed, 3 skipped, 22 subtests
passed`. Все пять EN/RU/HTML/PDF/production verifiers проходят.

Cleanup удалил `41` obsolete/generated каталог, `2804` present files и
`1,043,301,296` байт (`994.97 MiB`), сохранив production, финальные r6/r7,
уникальный accepted pre-promotion RU source, source/MinerU evidence и Git
history tracked-пакетов.

## Что уже универсально, а что ещё нет

Универсальна архитектура: staged reconstruction/publication, immutable
accepted inputs, manifests, build/freeze/verify, semantic anchors, asset
closure, user acceptance gates, production seal и defect-class closure.

Реализация пока остаётся Innsmouth reference implementation. В
`kb_creator/scripts` есть `23` Innsmouth-specific scripts с pinned paths,
hashes, page/table/asset counts и scenario structure. Второй сценарий не должен
получить ещё один скопированный комплект таких скриптов.

Следующий продуктовый шаг — выделить declarative scenario contract и доказать
его вторым реальным сценарием. Общая логика должна оставаться в reusable
modules; scenario-specific identity, counts, policy и exceptions — в data/config.

## Текущая Git/release граница

- production save-point: `54607bd3 Finalize Innsmouth production package`;
- local branch на момент среза: `codex/innsmouth-master-en-main`, `ahead 3`;
- cleanup и эта документация ещё не закоммичены/не отправлены;
- fresh independent `gpt-5.5` release verdict для frozen Innsmouth candidate
  остаётся pending.

Новый сценарий нельзя смешивать с незакрытым cleanup diff. Сначала нужен
чистый Git boundary или отдельный clean worktree.

## Связанные документы

- `../README.md`;
- `../PROJECT_STATUS.md`;
- `../inputs/innsmouth/production/README.md`;
- `../inputs/innsmouth/production/pipeline/PIPELINE.md`;
- `plans/20260830-innsmouth-production-package/context.md`;
- `plans/20260830-innsmouth-production-package/release.md`;
- `plans/20260830-innsmouth-production-package/CLEANUP_PREPARATION_20260830.md`;
- `plans/20260830-kb-creator-next-scenario/plan.md`;
- `plans/20260830-kb-creator-next-scenario/context.md`.
