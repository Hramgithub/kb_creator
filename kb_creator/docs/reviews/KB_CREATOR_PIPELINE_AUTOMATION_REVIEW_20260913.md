# Ревью автоматизации пайплайна `kb_creator`

Дата: `2026-09-13`

Статус: итоговое process/architecture review; план готов к реализации. Это не
release approval и не разрешение менять принятые source/master/output-пакеты.

## Итог в одном абзаце

В `kb_creator` уже достаточно сильных скриптов и fail-closed проверок, чтобы не
строить новый пайплайн с нуля. Главный недостающий компонент — единый product
control plane: одна CLI-команда, фиксированный граф стадий, общий run contract,
машинное состояние, resumability, кэш, унифицированные manifests и типизированная
очередь человеческих решений. Сейчас эту роль выполняют оркестратор и сотни
Markdown-handoff-ов. Поэтому следующий этап должен не добавлять очередной
scenario-specific script или review packet, а обернуть доказанные стадии единым
runner-ом и перенести повторяемые решения из Python/Markdown в схемы и данные.

## На какой базе сделано ревью

Опубликованная база — `origin/main` на коммите `5248894a` (`Save Viral
MASTER_EN rebuild and remediation progress`). Локальная `main` во время ревью
была `ahead 1, behind 8` и содержала большой объём пользовательской незавершённой
работы, поэтому она учитывалась только как R&D evidence, но не как authority.

Ключевые опубликованные шаги:

- `5952a224` — accepted Innsmouth MASTER_EN pipeline;
- `a7b2b215` — strict Innsmouth MASTER_EN promotion;
- `bd0da472` — accepted Innsmouth MASTER_RU;
- `c3eafb99` — HTML/PDF publication pipeline;
- `4d6033d4` — reusable three-view reconstruction tooling и scenario contract;
- `5248894a` — Viral MASTER_EN rebuild checkpoint.

Количественный срез `origin/main`:

| Поверхность | Наблюдение | Вывод |
|---|---:|---|
| Python/PowerShell entrypoints | 44 | Автоматизация есть, но раздроблена по командам |
| Python test files | 47, из них 45 основных | Сильная база, но смешаны разные классы доказательств |
| Plan-tree files | 695 | Каноническое состояние разрослось |
| Handoff files | 669 | Процесс фактически управляется документами |
| Handoffs в next-scenario goal | 563-564 | Один сценарий создаёт чрезмерную review amplification |
| Markdown review-файлы | около 225 | Review применяется шире, чем реальный риск |
| Последний Viral-коммит | 700 файлов, 562 handoff-а | Главный симптом отсутствия control plane |
| `PROJECT_STATUS.md` | около 1 867 строк в опубликованной базе | Это история, а не краткий rollup |
| Next-scenario `plan.md` / `context.md` | 3 983 / 3 375 строк | Машинное состояние хранится в prose |

Отдельно: под `kb_creator` нет собственного `pyproject.toml`, package entrypoint,
CI-контура или документированного top-level runner-а. `README.md` показывает
историческую freeze-команду, но не fresh-run flow от PDF до пакета.

## Что в проекте уже хорошо и должно быть сохранено

- Разделение reconstruction и publication: `RECONSTRUCTED_EN` не равен
  `MASTER_EN`.
- Неизменяемые входы и hash-bound provenance.
- Build создаёт candidate; acceptance/promotion — отдельное состояние.
- Atomic staging, no-overwrite, inventory sealing и independent verifier.
- Трёхпроходный MinerU flow: hybrid, pipeline/OCR и hybrid по raster-контролю.
- Fail-closed поведение при несовпадении identity, topology, asset closure,
  acceptance или resume prerequisites.
- Отдельное человеческое решение там, где машина не может доказать семантику,
  визуальную роль, качество перевода или release readiness.
- Defect-class closure: единичный пример должен вести к системному правилу,
  rebuild и full-scope evidence.

План ниже сокращает церемонию, но не ослабляет эти свойства.

## Корневая проблема

Сейчас существуют три частично пересекающихся реализации:

1. Исторический монолитный Innsmouth runner.
2. Принятая production-вертикаль Innsmouth с длинной последовательностью
   scenario-specific build/preflight/freeze/verify команд.
3. Более общий Viral/second-scenario контур с reusable extraction mechanics и
   сильной парой MASTER_EN builder/verifier, но без общего MASTER_RU -> HTML ->
   PDF -> production маршрута.

Каждая локальная проверка часто качественная, однако lifecycle между ними
неформален. Переходы фиксируются в task packets, receipts, plan, context,
PROJECT_STATUS и commit message. Один факт многократно переписывается, а
оркестратор остаётся единственным компонентом, который понимает, что разрешено
делать дальше.

Следствия:

- статус «зелёные тесты» не говорит, что именно принято;
- architecture acceptance, implementation acceptance и release acceptance
  смешиваются в длинной prose-цепочке;
- resume определяется человеком по документам, а не manifest-ами;
- scenario facts живут в Python, тестах и handoff-ах вместо contract/rule pack;
- повторяются hashing, canonical JSON, safe paths, inventory, atomic publish и
  process capture;
- новые сценарии рискуют породить копии Innsmouth/Viral скриптов;
- агентские review циклы проверяют механические факты, которые должен проверять
  детерминированный verifier.

## Избыточность тестов: что именно менять

Инженерная классификация 45 основных опубликованных test-модулей:

| Класс | Файлы | LOC | Test definitions | Решение |
|---|---:|---:|---:|---|
| Reusable behavioral | 5 | 3 423 | 161 | Сохранить, перевести на package API |
| Fixture/contract matrices | 20 | 9 523 | 235 | Сохранить coverage, свернуть в data-driven mutation catalogues |
| Generated/state assertions | 7 | 2 033 | 69 | Большую часть заменить verifier-ами run/package manifest |
| One-off scenario evidence | 13 | 1 942 | 107 | Перенести факты в scenario contract/rule packs; оставить acceptance parity |

Это не план удалить 80% тестов. Это план убрать повторение формы при сохранении
смысла.

Конкретные изменения:

1. Вынести общий `tests/support/`:
   canonical JSON, hashing, fixture builders, inventory reseal, mutation
   catalogue, v2 MASTER_EN fixture и CLI harness.
2. Убрать дублирующиеся v2 helpers из
   `test_build_scenario_master_en.py` и `test_verify_scenario_master_en.py`.
   Первый измеримый target: минус не менее шести дублей и примерно 350 LOC без
   снижения builder/verifier independence.
3. Перевести повторяющиеся field mutations в таблицы данных и один
   параметризованный test family. Явные security-boundary случаи оставить
   читаемыми отдельными тестами.
4. Прекратить динамическую загрузку `scripts/*.py` через
   `importlib.util.spec_from_file_location`: на published baseline таких
   test-модулей около 21. Логика должна импортироваться из Python package, а
   scripts стать тонкими CLI adapters.
5. Из 29 test-модулей, читающих AST/source text, оставить только checks класса
   `policy-static`, когда запрет нельзя надёжно проверить через публичный API.
   Остальные заменить behavioral negative tests. Target: сократить
   non-policy source inspection минимум на 50%.
6. Raw-PDF/page-proof/Step-5 suites сохранить как component regression. Они не
   должны автоматически становиться per-scenario review ladder.
7. Исторические Innsmouth tests пометить как `legacy_adapter` / `parity`, а не
   как основной публичный contract нового runner-а.

Целевые test layers:

```text
unit                 shared primitives and stage logic
contract-mutation    schema, policy and fail-closed matrices
integration          synthetic end-to-end stage chains
scenario-parity      Innsmouth/Viral reference compatibility
release-smoke        one frozen package, offline verification
```

## Избыточность review: минимальная безопасная модель

Нужно сократить количество review, а не строгость проверок.

| Gate | Кто исполняет | Артефакт | Когда нужен человек/critic |
|---|---|---|---|
| G0 Input contract | CLI | `run.json`, source/tool inventory | Только если спорна authority входа |
| G1 Stage execution | Stage library | `stage.json`, typed outputs | Не нужен для известной детерминированной стадии |
| G2 Mechanical QA | Verifiers | `evidence/index.json` | Critic только при изменении смысла gate-а |
| G3 Review queue | Пользователь/reviewer | `review_queue.json`, decision manifest | Семантика, визуал, перевод, source mutation |
| G4 Package freeze | CLI | package manifest и inventory | Critic, если это release candidate |
| G5 Release | Независимый critic + пользователь при необходимости | release receipt | Всегда для release |

Не нужны отдельные Sol + critic циклы для каждого:

- совпадения hash;
- известной schema validation;
- проверки отсутствия лишних файлов;
- fail-closed public route;
- повторного запуска стабильной mutation matrix;
- обычного stage transition, уже описанного и покрытого verifier-ом.

Они нужны при:

- новом contract/schema и изменении семантики gate-а;
- новой source-mutation категории;
- новой visual/semantic/translation acceptance policy;
- изменении reusable implementation с существенным blast radius;
- frozen release candidate.

Routine stages должны создавать ноль prose handoff-ов. Исторические receipts
не удаляются, но получают индекс `supersedes/superseded_by/current_for_gate`.

## Целевой one-command flow

Рекомендуемый пользовательский интерфейс:

```powershell
python -m kb_creator run `
  --contract kb_creator/contracts/viral.json `
  --source D:\path\source.pdf `
  --run-root D:\path\runs\viral-20260913 `
  --target production `
  --profile full
```

Повторный запуск после review/input:

```powershell
python -m kb_creator resume `
  --run-root D:\path\runs\viral-20260913 `
  --decisions D:\path\viral-decisions.json
```

Внутренний фиксированный граф:

```text
doctor
  -> intake/source seal
  -> MinerU three-view extraction
  -> comparison + review queue
  -> RECONSTRUCTED_EN
  -> MASTER_EN
  -> MASTER_RU acquisition/translation/proofread
  -> post-RU visual finalization
  -> HTML
  -> PDF
  -> production package
  -> external independent release gate
```

Команда обязана либо дойти до `--target`, либо безопасно остановиться с
самодостаточным packet-ом и точной resume-командой. Она не должна считать
acceptance доказанным по stdout, имени каталога, passing test count, agent
message или prose receipt.

### Человеческие паузы

Полностью автоматический happy path возможен, если все decision manifests и
принятые translation/proofread inputs уже переданы. Если их нет, результатом
первого запуска будет не «неполная работа», а законченный пакет ожидания:

- `review/review_queue.json`;
- `review/review.html` или contact sheets;
- source/page/span и candidate evidence;
- допустимые варианты решения;
- причины, почему machine gate остановился;
- шаблон decision manifest;
- стабильная resume-команда.

## Контракты и состояние

Минимальный набор версионированных схем:

- `ScenarioSpec.v2`: scenario identity, page topology, stage policy, asset and
  terminology rules, expected human decisions; без shell fragments/import paths.
- `RunSpec.v1`: contract/source identities, target, run/cache roots, resolved
  tools, options и external decision/input manifests.
- `StageManifest.v1`: одинаковый envelope для каждой стадии.
- `DecisionManifest.v1`: hash-bound semantic/visual/translation decisions.
- `AcceptanceManifest.v1`: кто, что и против какого точного кандидата принял.
- `ProductionManifest.v1`: полный package inventory, owning code и provenance.

Разрешённые stage states:

```text
pending
running
passed
awaiting_review
awaiting_input
accepted
failed
quarantined
```

`PROJECT_STATUS.md` должен быть коротким автоматически генерируемым rollup:
текущий run id, release boundary, blockers, next human action и ссылки. История
переходит в append-only `events.jsonl` и evidence index, а не в plan/context.

## Структура run package

```text
runs/<run-id>/
  run.json
  events.jsonl
  doctor.json
  stages/
    <stage-id>/
      attempts/<n>/
      stage.json
  review/
    review_queue.json
    review.html
    decisions/
  evidence/
    index.json
    summary.md
  artifacts/
    reconstructed_en/
    master_en/
    master_ru/
    html/
    pdf/
  package/
    PRODUCTION_MANIFEST.json
  failures/
```

Воспроизводимая часть manifests не включает timestamps и абсолютные локальные
пути; они хранятся в unhashed metadata/event log. Package verifier должен
работать offline на другом checkout-е.

## Cache, resume и безопасность

Cache key стадии включает:

- scenario contract hash;
- stage config/rule-pack hash;
- implementation identity;
- toolchain versions;
- hashes всех upstream inputs;
- параметры, влияющие на результат.

Resume разрешён только если совпадают весь RunSpec, predecessor manifests,
implementation/tool identities и artifact inventory. Иначе конкретная стадия и
весь downstream инвалидируются. Partial output никогда не становится
predecessor; он остаётся в quarantined attempt.

Обязательные свойства:

- output root отсутствует или является exact validated resumable run;
- component-wise path containment;
- запрет symlink/junction/reparse escape;
- atomic staging -> verify -> promote;
- no silent overwrite;
- bounded subprocess capture и redaction;
- source/config/accepted inputs read-only;
- deterministic manifest identities.

Рекомендуемые exit codes:

| Code | Смысл |
|---:|---|
| 0 | requested target reached and verified |
| 10 | human review required |
| 11 | external input required |
| 20 | invalid contract/config |
| 21 | toolchain unavailable/incompatible |
| 22 | source/upstream identity mismatch |
| 23 | quality/deterministic gate failed |
| 24 | unsafe resume/cache/provenance mismatch |
| 25 | occupied/escaping target |
| 30 | external engine/renderer failure |
| 40 | unexpected internal error |

## Предлагаемая package architecture

```text
kb_creator/pipeline/
  __main__.py
  graph.py
  runner.py
  models.py
  lifecycle.py
  identity.py
  process.py
  cache.py
  review.py
  evidence.py
  doctor.py
  stages/
    intake.py
    extraction.py
    reconstruction.py
    master_en.py
    master_ru.py
    visual_assets.py
    html.py
    pdf.py
    production.py
  adapters/
    mineru.py
    translation.py
    html_renderer.py
    pdf_renderer.py

kb_creator/tests/support/
```

`scripts/*.py` на период миграции остаются совместимыми тонкими adapters. Не
следует начинать с переписывания `build_scenario_master_en.py` или
`build_innsmouth_source_to_artifacts.py`: сначала общий runtime должен обернуть
их как proven stages.

## План реализации

### Wave 0 — baseline и executable contracts

Приоритет: P0. Оценка: 2-4 рабочих дня.

- Работать от чистого `origin/main`; локальные R&D changes не смешивать.
- Добавить минимальный Python package/`pyproject.toml` и CLI `doctor`.
- Определить ScenarioSpec/RunSpec/StageManifest/error schemas.
- Вынести canonical JSON, hashing, safe paths, inventory, atomic publish,
  process capture.
- Создать synthetic fixture и parity references Innsmouth/Viral по manifest,
  без зависимости от ignored working paths.

Done: `python -m kb_creator doctor` и `preflight` дают machine-readable результат;
один существующий CLI использует общий core без изменения поведения.

### Wave 1 — reconstruction control plane

Приоритет: P0/P1. Оценка: 4-7 дней.

- Обернуть prepare -> MinerU three views -> compare -> decisions -> audit ->
  materialize/finalize.
- Добавить content-addressed cache, safe resume и review queue.
- Генерировать единый evidence index и summary.
- Один synthetic E2E прогон дважды должен дать одинаковую reproducible identity.

Done: одна команда заменяет минимум три ручных generic invocation и корректно
возвращает 10/11 при ожидании человека/входа.

### Wave 2 — generic MASTER_EN

Приоритет: P1. Оценка: 5-10 дней.

- Разделить Viral facts и reusable builder/verifier mechanisms.
- Перенести counts, roles, page ranges, anchors и exceptions в ScenarioSpec и
  rule packs.
- Использовать package imports вместо dynamic script loading.
- Сохранить независимость verifier-а от builder-а.

Done: synthetic non-Viral contract проходит build/verify; Viral reference
parity остаётся зелёным.

### Wave 3 — MASTER_RU, assets, HTML и PDF

Приоритет: P1. Оценка: 7-12 дней.

- Унифицировать candidate/freeze/verify lifecycle.
- Ввести translation adapter и явный external-input режим.
- Генерировать typed visual review units после RU, до HTML.
- Обернуть существующие Innsmouth HTML/PDF stages adapters-ами.

Done: один `run --target pdf` либо строит verified PDF, либо выдаёт полный
review/input packet и безопасно продолжается после `resume`.

### Wave 4 — production package и offline verification

Приоритет: P1/P2. Оценка: 3-6 дней.

- Общий production packager и manifest.
- Offline verifier для clean checkout.
- Короткий generated PROJECT_STATUS rollup.
- Evidence/receipt supersession index.

Done: package переносится и проверяется без исходного working tree; mutation
любого файла, owning code или manifest-а детерминированно отклоняется.

### Wave 5 — сокращение legacy и review debt

Приоритет: P2. Оценка: итеративно после parity.

- Классифицировать все тесты marker-ами.
- Свернуть duplicate fixtures/mutation matrices.
- Архивировать, но не переписывать historical handoffs.
- Прекратить создание routine prose receipts.
- Retire scenario-specific adapters только после parity evidence.

Done targets:

- 0 новых scenario-named scripts для data-expressible rules;
- 0 dynamic imports в новых generic tests;
- минимум -50% non-policy AST/source inspection;
- routine run создаёт 0 handoff Markdown;
- PROJECT_STATUS — краткий rollup, а не event history;
- один synthetic и один reference full-run проходят из clean checkout.

## Первый bounded implementation packet

Не брать весь runner сразу. Первый пакет должен владеть только:

1. `kb_creator/pipeline/core` (`identity`, `jsonio`, `paths`, `inventory`,
   `process`, typed errors);
2. `kb_creator/tests/support`;
3. адаптацией одного низкорискового существующего CLI без изменения его
   arguments/output schema;
4. unit tests и adapter parity test;
5. `doctor`/`preflight` skeleton с JSON output.

В этот пакет не входят новый сценарий, переписывание больших builders,
MASTER_RU/HTML/PDF, cleanup исторических receipts или production rebuild.

## Решение по локальным R&D-контурам

`pdf_raw`, page-proof и Step-5 non-live suites не удалять и не включать целиком
в обязательный production DAG. Их статус:

- reusable component laboratory;
- contract/mutation regression suite;
- источник proven validators для будущего adapter-а;
- не authority нового сценария без отдельной integration/parity проверки.

Это предотвращает два плохих исхода: потерю сильных safety checks и превращение
каждого нового сценария в повтор 4b.1 -> 4b.9 с сотнями reviews.

## Риски

- Слишком тонкий shell-wrapper сохранит hard-coded paths и ручные gates. Нужен
  именно stateful control plane.
- Слишком ранняя «универсализация» Viral builder-а скроет scenario constants.
- Review queue нельзя auto-approve.
- Passing tests не равны acceptance без `acceptance_effect` и exact scope.
- Cache без tool/config/implementation identities создаст ложный resume.
- Monolithic rewrite повысит риск; migration должна быть adapter-first.
- Release review нельзя автоматизировать или заменить package verifier-ом.

## Метрики успеха

Через первые три waves должны измеряться:

- количество ручных команд на fresh run и resume;
- количество prose handoffs на routine run (цель 0);
- доля stages с общим StageManifest (цель 100% подключённых стадий);
- cache hit/miss и причины invalidation;
- количество human review units и время до решения;
- duplicated helper LOC;
- dynamic-import test count;
- non-policy AST/source-inspection count;
- clean-checkout reproducibility;
- parity с Innsmouth и Viral reference packages.

## Принятое направление

1. Не строить новый пайплайн с нуля.
2. Не продолжать размножать scenario-specific scripts.
3. Создать control plane поверх существующих доказанных стадий.
4. Перенести state и routine evidence из Markdown в versioned JSON manifests.
5. Оставить человека только там, где решение действительно семантическое,
   визуальное, переводческое, destructive/publishing или release-level.
6. Начать с Wave 0 в чистом worktree от `origin/main`.

## Evidence

- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`
- `kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260913-kb-creator-pipeline-automation-review/`
- published commits `5952a224` through `5248894a`

Contributor receipts:

- `handoffs/architect_pipeline_automation_review_20260913.md`
- `handoffs/engineer_test_script_consolidation_review_20260913.md`
- `handoffs/critic_process_review_20260913.md`

## Release note

Это process/architecture decision. Реализация ещё не создана, поэтому
independent release verdict неприменим и не заявляется.
