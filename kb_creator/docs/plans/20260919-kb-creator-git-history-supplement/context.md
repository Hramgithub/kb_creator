# Текущий контекст

Goal id: `20260919-kb-creator-git-history-supplement`. State: `completed`.

Пользователь уточнил, что прошлый обзор слишком опирался на локальные папки. Цель — проверить Git, прежде всего «Террор в Инсмуте», и другие исторические работы до дальнейшего обсуждения универсального DOCX-first потока.

Первый обзор охватывал восемь разных названий в `kb_creator` и legacy `translator`; это была граница выборки, не общее число проектов NRI. Проверены история NRI (`git log --all`, `git show`, `git ls-tree`) и отдельный CoC publishing repo `C:\_Hobby\_work\NRI\Git`, remote-tracking `origin/main` (`a782bb1`). У CoC checkout есть прежние удаления backup-файлов и локальный commit поверх remote; их не трогать.

`The Innsmouth Terror` имеет коммиты accepted MASTER_EN/RU и завершённой публикации в августе 2026. Отдельный `Innsmouth_Guide` в CoC publishing repo строит KB из русского текстового слоя русского PDF. Beyond the Edge of Darkness и Crawford Inheritance имеют ранние RU Keeper/HTML/PDF пакеты, но не подтверждают современный EN→RU→DOCX маршрут. Dune Corebook — большая отдельная PDF_EN→RU Markdown/HTML/PDF локализация без подтверждённого DOCX. Lightless Beacon, Memphis House, Edge of Darkness 1923 — intake/планы, не завершённые прогоны.

Создан `git-evidence.md`; предложение и `PROJECT_STATUS.md` дополнены. Пользователь назвал `The Innsmouth Terror` хорошим примером; он принят как главный исторический тест будущего DOCX-first эксперимента. Исходники, скрипты, принятые output и Git state не менялись. Следующее решение — критерии сравнительной DOCX-сборки, включая проверку таблиц, статблоков, арта и полноты текста.
