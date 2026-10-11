from __future__ import annotations

import hashlib
import html
import json
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "CoC/Working/Scenarios/The_Innsmouth_Terror"
OUTPUT = ROOT / "CoC/Output/Scenarios/The_Innsmouth_Terror"
LAST_CHARACTER_NAME_REPORT: dict[str, object] = {}
LAST_PAGE_REFERENCE_REPORT: dict[str, object] = {}
VISUAL_ONLY_PUBLICATION_PLACEHOLDER = "Визуальная/служебная страница источника; текстового слоя для публикации нет."
SERVICE_BACKMATTER_TEXT_RE = re.compile(
    r"(?is)\bMiskatonic\s+Playhouse\b.*?"
    r"(?:www\.MiskatonicPlayhouse\.com|Miskatonic\s+Repository\s+Scenario\s+Map)"
)
SERVICE_BACKMATTER_PAGES = {"044"}
INNSMOUTH_READER_ART_ANCHOR_OVERRIDES: dict[str, str] = {}
INNSMOUTH_SUPPRESSED_READER_ART_IDS = {
    "xref-00070",
    "xref-00082",
    "xref-00096",
    "xref-00106",
    "xref-00110",
    "xref-00114",
    "xref-00130",
    "xref-00220",
    "xref-00724",
    # Reader artifacts should not emit page-anchor-only service/promotional
    # backmatter or a competing page-043 map under Handout 2.
    "xref-01288",
    "xref-01380",
    "xref-01391",
    # Page 044 contains source handout/backmatter service visuals. The
    # Miskatonic Playhouse ticket must not be republished as Handout 2's note.
    "xref-01397",
    "xref-01399",
    "xref-01401",
    "xref-01406",
    "xref-01447",
    "xref-01448",
    "xref-01450",
    "xref-01451",
    "xref-01452",
    "xref-01453",
    "xref-01463",
    "xref-01492",
    "xref-01509",
    "xref-01593",
    "xref-01594",
    "xref-01620",
    "xref-01626",
}


UNIT_COMMENT_RE = re.compile(r"<!--\s*/?unit-id:[\s\S]*?-->\n?", re.I)
GENERATED_COMMENT_RE = re.compile(r"<!--\s*(?:generated-by|source-en-sha256|source-batch-manifest):[\s\S]*?-->\n?", re.I)
FORBIDDEN_READER_MASTER_COMMENT_RE = re.compile(
    r"(?m)^<!--\s*(?P<kind>mineru-page|table-evidence)\s*:[^>]*-->\s*$",
    re.I,
)
SOURCE_PAGE_RE = re.compile(r"<!--\s*source-page-(\d{3})\s*-->")
PAGE_REFERENCE_RE = re.compile(r"\b(?P<label>стр\.|страниц(?:а|е|у|ы|ей|ах)?)\s+(?P<page>\d{1,3})\b", re.I)
PRINTED_PAGE_TARGET_OVERRIDES = {
    # Appendix/handout pagination follows the printed page reference rather
    # than the body offset used by scenario text.
    39: "042",
}
NOTE_RE = re.compile(r"\b(Примечание|Заметка)\s+(?:для\s+)?Хранител[юя]:\s*", re.I)
KEEPER_INFO_HEADING_RE = re.compile(r"(?m)^Информация для Хранителя\s*$")
REFERENCE_LIST_RE = re.compile(r"\bсм\.\s+.*(?:страниц|Call of Cthulhu|Книга Хранителя)", re.I)
STAT_LABELS = {
    "STR",
    "CON",
    "SIZ",
    "DEX",
    "INT",
    "APP",
    "POW",
    "EDU",
    "SAN",
    "HP",
    "MP",
    "DB",
}

PAGE_PREAMBLE_HEADINGS = {
    "003": ["## Авторы и участники"],
    "004": ["## Содержание"],
    "005": ["## Введение"],
    "008": ["## Действующие лица"],
    "011": ["## Начало: Аркхэм"],
    "015": ["## Иннсмут", "### Прибытие"],
    "017": ["## Расследование"],
    "021": ["### На съёмочной площадке"],
    "026": ["## В Иннсмут", "### Универсальный магазин"],
    "029": ["## Эпический финал"],
    "030": ["### Последний поезд из Иннсмута", "### Играя героя"],
    "032": ["## Эпилог"],
    "033": ["## Персонажи и чудовища", "### Жители Аркхэма", "### Съёмочная группа", "### Жители Иннсмута", "### Монстры"],
    "036": ["## Заранее созданные сыщики"],
    "041": ["## Раздаточные материалы"],
}

LINE_HEADINGS = {
    "ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ": "## Информация для Хранителя",
    "KEEPER INFORMATION": "## Информация для Хранителя",
    "ДЕЙСТВУЮЩИЕ ЛИЦА": "## Действующие лица",
    "ВВЕДЕНИЕ": "## Введение",
    "ПОДГОТОВКА К ИГРЕ": "### Подготовка к игре",
    "ВОВЛЕЧЕНИЕ СЫЩИКОВ": "### Вовлечение сыщиков",
    "ДЕЙСТВУЮЩИЕ ЛИЦА": "## Действующие лица",
    "ВТОРОСТЕПЕННЫЕ NPC": "### Второстепенные NPC",
    "ВТОРОСТЕПЕННЫЕ НПС": "### Второстепенные NPC",
    "БИБЛИОТЕКА ОРНА (МИСКАТОНИКСКИЙ УНИВЕРСИТЕТ)": "### Библиотека Орна",
    "«АРКХЭМСКИЙ ВЕСТНИК»": "### Аркхэмский вестник",
    "«АРКХЕМСКИЙ ВЕСТНИК»": "### Аркхэмский вестник",
    "АРКХЕМСКИЙ ВЕСТНИК": "### Аркхэмский вестник",
    "THE ARKHAM ADVERTISER": "### Аркхэмский вестник",
    "The Arkham Advertiser": "### Аркхэмский вестник",
    "MISKATONIC PLAYHOUSE": "### Мискатоникский театр",
    "Miskatonic Playhouse": "### Мискатоникский театр",
    "МИСКАТОНИКСКИЙ ТЕАТР": "### Мискатоникский театр",
    "ТЕАТР «МИСКАТОНИК»": "### Мискатоникский театр",
    "THE GILMAN HOUSE HOTEL": "### Отель «Гилман-хаус»",
    "ГОСТИНИЦА GILMAN HOUSE HOTEL": "### Отель «Гилман-хаус»",
    "БИБЛИОТЕКА ORNE (МИСКАТОНИКСКИЙ УНИВЕРСИТЕТ)": "### Библиотека Орна",
    "СТАРТ: АРКХЕМ": "## Начало: Аркхэм",
    "START: ARKHAM": "## Начало: Аркхэм",
    "СЪЁМОЧНЫЙ ЖЕЛЕЗНОДОРОЖНЫЙ ВАГОН": "### Съёмочный железнодорожный вагон",
    "ВАГОН СЪЁМОЧНОЙ ГРУППЫ": "### Съёмочный железнодорожный вагон",
    "СЪЁМОЧНЫЙ ПОЕЗД": "### Съёмочный железнодорожный вагон",
    "ЖЕЛЕЗНОДОРОЖНЫЙ ВХОД": "### Железнодорожный вход",
    "ПЕЩЕРНАЯ СИСТЕМА": "### Система пещер",
    "СИСТЕМА ПЕЩЕР": "### Система пещер",
    "НАТКНУТЬСЯ НА СЪЕМОЧНУЮ ПЛОЩАДКУ": "### Наткнуться на съёмочную площадку",
    "НАТКНУТЬСЯ НА СЪЁМОЧНУЮ ПЛОЩАДКУ": "### Наткнуться на съёмочную площадку",
    "ЖИТЕЛИ АРКХЭМА": "### Жители Аркхэма",
    "ЖИТЕЛИ АРКХЕМА": "### Жители Аркхэма",
    "СЪЕМОЧНАЯ ГРУППА": "### Съёмочная группа",
    "СЪЁМОЧНАЯ ГРУППА": "### Съёмочная группа",
    "ЖИТЕЛИ ИННСМУТА": "### Жители Иннсмута",
    "МОНСТРЫ": "### Монстры",
    "ЧУДОВИЩА": "### Монстры",
    "ГОТОВЫЕ СЫЩИКИ": "### Готовые сыщики",
    "ПОСЛЕДНИЙ ПОЕЗД ИЗ ИНСМУТА": "### Последний поезд из Иннсмута",
}

INLINE_HEADINGS = {
    "ОТЕЛЬ «ГИЛМАН-ХАУС»": "### Отель «Гилман-хаус»",
    "Отель Gilman House": "### Отель «Гилман-хаус»",
    "Жилой вагон съёмочной группы": "### Съёмочный железнодорожный вагон",
    "КАБИНЕТ ПРОДЮСЕРА": "### Кабинет продюсера",
    "ВОКРУГ ПОЕЗДА": "### Вокруг поезда",
    "Кабинет Bazzledon": "### Кабинет Баззлдона",
    "Кабинет Баззлдона": "### Bazzledon’s Office",
    "Трейлер Ginny": "### Трейлер Джинни",
    "Лаборатория McGuire": "### Лаборатория Макгуайра",
    "Лаборатория Макгуайра": "### McGuire’s Lab",
    "Bazzledon’s Office": "### Bazzledon’s Office",
    "Bazzledon's Office": "### Bazzledon’s Office",
    "Ginny’s Trailer": "### Ginny’s Trailer",
    "Ginny's Trailer": "### Ginny’s Trailer",
    "McGuire’s Lab": "### McGuire’s Lab",
    "McGuire's Lab": "### McGuire’s Lab",
    "РЕЗИДЕНЦИЯ БРЮСТЕРОВ": "### Дом Брюстеров",
    "РЕЗИДЕНЦИЯ BREWSTER": "### Дом Брюстеров",
    "Резиденция Брюстеров": "### Дом Брюстеров",
    "THE BREWSTER RESIDENCE": "### Brewster Residence",
    "The Brewster Residence": "### Brewster Residence",
    "Brewster Residence": "### Brewster Residence",
    "ЭЗОТЕРИЧЕСКИЙ ОРДЕН ДАГОНА": "### Эзотерический Орден Дагона",
    "Эзотерический орден Дагона": "### Эзотерический Орден Дагона",
    "ПОСЛЕДНИЙ ПОЕЗД ИЗ ИННСМУТА": "### Последний поезд из Иннсмута",
    "ПОСЛЕДНИЙ ПОЕЗД ИЗ ИНСМУТА": "### Последний поезд из Иннсмута",
    "Последний поезд из Инсмута": "### Последний поезд из Иннсмута",
    "ИГРАЯ ГЕРОЯ": "### Играя героя",
}
RESIDUAL_TITLE_LABELS = [
    "Innsmouth",
    "ПОДГОТОВКА К ИГРЕ",
    "ДЕЙСТВУЮЩИЕ ЛИЦА",
    "Кабинет Bazzledon",
    "РЕЗИДЕНЦИЯ БРЮСТЕРОВ",
    "НАТКНУТЬСЯ НА СЪЕМОЧНУЮ ПЛОЩАДКУ",
    "НАТКНУТЬСЯ НА СЪЁМОЧНУЮ ПЛОЩАДКУ",
    "На съёмочной площадке",
    "ЖИТЕЛИ АРКХЭМА",
    "СЪЁМОЧНАЯ ГРУППА",
    "ЖИТЕЛИ ИННСМУТА",
    "МОНСТРЫ",
    "ГОТОВЫЕ СЫЩИКИ",
]

HANDOUT_HEADINGS = {
    "041": "### Раздаточный материал 1-a: письмо (внутреннее)",
    "042": "### Раздаточный материал 1-b: письмо (внешнее)",
    "043": "### Раздаточный материал 2: записка",
}
HANDOUT_LABELS = {
    "Раздаточный материал 1-a: письмо (внутреннее)",
    "Раздаточный материал 1-b: письмо (внешнее)",
    "Раздаточный материал 2: записка",
}

START_LINE_HEADINGS = {
    "Трейлер Джинни": "### Трейлер Джинни",
    "Лаборатория Макгвайра": "### Лаборатория Макгуайра",
    "Железнодорожный вход": "### Железнодорожный вход",
    "Передвижение по пещерам": "### Передвижение по пещерам",
    "Универсальный магазин": "### Универсальный магазин",
    "Пожарная станция": "### Пожарная часть",
    "Пожарная часть": "### Пожарная часть",
    "Вход через пещеры": "### Вход через пещеры",
    "Вход через Пещеры": "### Вход через пещеры",
    "The Fire Station": "### Пожарная часть",
    "Награды": "### Награды",
    "Hugo ‘Shrimpy’ Hargreaves": "### Hugo ‘Shrimpy’ Hargreaves",
    "Hugo 'Shrimpy' Hargreaves": "### Hugo ‘Shrimpy’ Hargreaves",
    "Хьюго «Шримпи» Харгривз": "### Hugo ‘Shrimpy’ Hargreaves",
    "ХЬЮГО «ШРИМПИ» ХАРГРИВЗ": "### Hugo ‘Shrimpy’ Hargreaves",
    "Хьюго «Креветка» Харгривз": "### Hugo ‘Shrimpy’ Hargreaves",
    "ХЬЮГО «КРЕВЕТКА» ХАРГРИВЗ": "### Hugo ‘Shrimpy’ Hargreaves",
    "Patty Gillian": "### Patty Gillian",
    "Пэтти Гиллиан": "### Patty Gillian",
    "ПЭТТИ ГИЛЛИАН": "### Patty Gillian",
    "Ian Torres": "### Ian Torres",
    "Иэн Торрес": "### Ian Torres",
    "Иан Торрес": "### Ian Torres",
    "ИАН ТОРРЕС": "### Ian Torres",
    "Tiffany Quispe": "### Tiffany Quispe",
    "Тиффани Киспе": "### Tiffany Quispe",
    "ТИФФАНИ КИСПЕ": "### Tiffany Quispe",
    "Margaret ‘Maggie’ Myers": "### Margaret ‘Maggie’ Myers",
    "Margaret 'Maggie' Myers": "### Margaret ‘Maggie’ Myers",
    "Маргарет «Мэгги» Майерс": "### Margaret ‘Maggie’ Myers",
    "МАРГАРЕТ «МЭГГИ» МАЙЕРС": "### Margaret ‘Maggie’ Myers",
}

CHARACTER_LINE_RE = re.compile(
    r"^(?P<name>Genevieve [‘']Ginny[’'] Dubois|Женевьева «Джинни» Дюбуа|P\.A\. Bazzledon|П\.А\. Баззлдон|Anna Díaz|Anna Diaz|Анна Диас|Christopher McGuire|Кристофер Макгуайр|Sammy Brewster|Сэмми Брюстер),\s+(?P<rest>.+)$"
)
CHARACTER_METADATA_LINE_RE = re.compile(r"^(?:,?\s*)?(?P<meta>\d{1,3}\s+(?:год|года|лет),\s+\S[\s\S]*)$")
ROLE_TOKEN_RE = re.compile(r"^[a-zа-яё&./'’()-]+$", re.I)
MAIN_CHARACTER_CAPTION_LABELS = {
    "Genevieve ‘Ginny’ Dubois",
    "Genevieve 'Ginny' Dubois",
    "Женевьева «Джинни» Дюбуа",
    "P.A. Bazzledon",
    "P.A Bazzledon",
    "П.А. Баззлдон",
    "Anna Díaz",
    "Anna Diaz",
    "Анна Диас",
    "Christopher McGuire",
    "Кристофер Макгуайр",
    "Sammy Brewster",
    "Сэмми Брюстер",
}
PREGEN_NAMES = {
    "HUGO 'SHRIMPY' HARGREAVES",
    "HUGO ‘SHRIMPY’ HARGREAVES",
    "PATTY GILLIAN",
    "IAN TORRES",
    "TIFFANY QUISPE",
    "MARGARET 'MAGGIE' MYERS",
    "MARGARET ‘MAGGIE’ MYERS",
    "Хьюго «Шримпи» Харгривз",
    "Хьюго «Креветка» Харгривз",
    "ХЬЮГО «КРЕВЕТКА» ХАРГРИВЗ",
    "Пэтти Гиллиан",
    "ПЭТТИ ГИЛЛИАН",
    "Иэн Торрес",
    "Иан Торрес",
    "ИАН ТОРРЕС",
    "Тиффани Киспе",
    "ТИФФАНИ КИСПЕ",
    "Маргарет «Мэгги» Майерс",
    "МАРГАРЕТ «МЭГГИ» МАЙЕРС",
    "МАРГАРЕТ «МАГГИ» МАЙЕРС",
}
CHARACTER_HEADING_MAP = {
    "Genevieve ‘Ginny’ Dubois": "### Genevieve ‘Ginny’ Dubois",
    "Genevieve 'Ginny' Dubois": "### Genevieve ‘Ginny’ Dubois",
    "Женевьева «Джинни» Дюбуа": "### Genevieve ‘Ginny’ Dubois",
    "P.A. Bazzledon": "### P.A. Bazzledon",
    "П.А. Баззлдон": "### P.A. Bazzledon",
    "Christopher McGuire": "### Christopher McGuire",
    "Кристофер Макгуайр": "### Christopher McGuire",
    "Anna Díaz": "### Anna Díaz",
    "Anna Diaz": "### Anna Díaz",
    "Анна Диас": "### Anna Díaz",
    "Sammy Brewster": "### Sammy Brewster",
    "Сэмми Брюстер": "### Sammy Brewster",
    "HUGO ‘SHRIMPY’ HARGREAVES": "### Hugo ‘Shrimpy’ Hargreaves",
    "HUGO 'SHRIMPY' HARGREAVES": "### Hugo ‘Shrimpy’ Hargreaves",
    "Hugo ‘Shrimpy’ Hargreaves": "### Hugo ‘Shrimpy’ Hargreaves",
    "Hugo 'Shrimpy' Hargreaves": "### Hugo ‘Shrimpy’ Hargreaves",
    "Хьюго «Шримпи» Харгривз": "### Hugo ‘Shrimpy’ Hargreaves",
    "Хьюго «Креветка» Харгривз": "### Hugo ‘Shrimpy’ Hargreaves",
    "ХЬЮГО «КРЕВЕТКА» ХАРГРИВЗ": "### Hugo ‘Shrimpy’ Hargreaves",
    "PATTY GILLIAN": "### Patty Gillian",
    "Patty Gillian": "### Patty Gillian",
    "Пэтти Гиллиан": "### Patty Gillian",
    "ПЭТТИ ГИЛЛИАН": "### Patty Gillian",
    "IAN TORRES": "### Ian Torres",
    "Ian Torres": "### Ian Torres",
    "Иэн Торрес": "### Ian Torres",
    "Иан Торрес": "### Ian Torres",
    "ИАН ТОРРЕС": "### Ian Torres",
    "TIFFANY QUISPE": "### Tiffany Quispe",
    "Tiffany Quispe": "### Tiffany Quispe",
    "Тиффани Киспе": "### Tiffany Quispe",
    "ТИФФАНИ КИСПЕ": "### Tiffany Quispe",
    "MARGARET ‘MAGGIE’ MYERS": "### Margaret ‘Maggie’ Myers",
    "MARGARET 'MAGGIE' MYERS": "### Margaret ‘Maggie’ Myers",
    "Margaret ‘Maggie’ Myers": "### Margaret ‘Maggie’ Myers",
    "Margaret 'Maggie' Myers": "### Margaret ‘Maggie’ Myers",
    "Маргарет «Мэгги» Майерс": "### Margaret ‘Maggie’ Myers",
    "МАРГАРЕТ «МЭГГИ» МАЙЕРС": "### Margaret ‘Maggie’ Myers",
    "МАРГАРЕТ «МАГГИ» МАЙЕРС": "### Margaret ‘Maggie’ Myers",
}
DUPLICATE_ALLOWED_HEADINGS = {
    "### Съёмочная группа",
}
EXPECTED_ORDERED_HEADINGS = [
    "# Иннсмутский ужас",
    "## Авторы и участники",
    "## Содержание",
    "## Введение",
    "### Подготовка к игре",
    "### The Innsmouth Terror",
    "### Вовлечение сыщиков",
    "## Действующие лица",
    "### Genevieve ‘Ginny’ Dubois",
    "### P.A. Bazzledon",
    "### Anna Díaz",
    "### Christopher McGuire",
    "### Sammy Brewster",
    "### Съёмочная группа",
    "### Второстепенные NPC",
    "## Начало: Аркхэм",
    "### Библиотека Орна",
    "### Аркхэмский вестник",
    "### Мискатоникский театр",
    "## Иннсмут",
    "### Прибытие",
    "#### Прибытие: практическая справка",
    "### Отель «Гилман-хаус»",
    "### Съёмочный железнодорожный вагон",
    "## Расследование",
    "### Кабинет продюсера",
    "### Вокруг поезда",
    "### Bazzledon’s Office",
    "### Ginny’s Trailer",
    "### McGuire’s Lab",
    "### На съёмочной площадке",
    "### Железнодорожный вход",
    "### Система пещер",
    "### Передвижение по пещерам",
    "### Brewster Residence",
    "### Наткнуться на съёмочную площадку",
    "## В Иннсмут",
    "### Универсальный магазин",
    "### Пожарная часть",
    "### Эзотерический Орден Дагона",
    "### Вход через пещеры",
    "## Эпический финал",
    "### Последний поезд из Иннсмута",
    "### Играя героя",
    "## Эпилог",
    "### Награды",
    "## Персонажи и чудовища",
    "### Жители Аркхэма",
    "### Съёмочная группа",
    "### Жители Иннсмута",
    "### Монстры",
    "## Заранее созданные сыщики",
    "### Hugo ‘Shrimpy’ Hargreaves",
    "### Patty Gillian",
    "### Готовые сыщики",
    "### Ian Torres",
    "### Tiffany Quispe",
    "### Margaret ‘Maggie’ Myers",
    "## Раздаточные материалы",
    "### Раздаточный материал 1-a: письмо (внутреннее)",
    "### Раздаточный материал 1-b: письмо (внешнее)",
    "### Раздаточный материал 2: записка",
]
MAIN_CHARACTER_HEADINGS = {
    "### Genevieve ‘Ginny’ Dubois",
    "### P.A. Bazzledon",
    "### Anna Díaz",
    "### Christopher McGuire",
    "### Sammy Brewster",
}
KEEPER_SOURCE_TOC_ENTRIES = [
    "ВВЕДЕНИЕ",
    "Подготовка к игре",
    "«Иннсмутский ужас»",
    "Вовлечение сыщиков",
    "ДЕЙСТВУЮЩИЕ ЛИЦА",
    "Genevieve ‘Ginny’ Dubois",
    "P.A. Bazzledon",
    "Anna Díaz",
    "Christopher McGuire",
    "Sammy Brewster",
    "Съёмочная группа",
    "Второстепенные NPC",
    "НАЧАЛО: АРКХЕМ",
    "Библиотека Орн",
    "«Аркхемский вестник»",
    "Мискатоникский театр",
    "ИННСМУТ",
    "Прибытие",
    "Отель Gilman House",
    "Жилой вагон съёмочной группы",
    "РАССЛЕДОВАНИЕ",
    "Кабинет продюсера",
    "Вокруг поезда",
    "Bazzledon’s Office",
    "Ginny’s Trailer",
    "McGuire’s Lab",
    "На съёмочной площадке",
    "Железнодорожный вход",
    "Пещерная система",
    "Передвижение по пещерам",
    "Brewster Residence",
    "Наткнувшись на съёмочную площадку",
    "В ИННСМУТ",
    "Универсальный магазин",
    "Пожарная станция",
    "Эзотерический Орден Дагона",
    "Вход через пещеры",
    "ЭПИЧЕСКИЙ ФИНАЛ",
    "Последний поезд из Иннсмута Играя героя",
    "ЭПИЛОГ",
    "Награды",
    "ПЕРСОНАЖИ И ЧУДОВИЩА",
    "ЗАРАНЕЕ СОЗДАННЫЕ СЫЩИКИ",
    "РАЗДАТОЧНЫЕ МАТЕРИАЛЫ",
    "ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ",
    "Алкоголизм, потеря контроля, жертвоприношение",
    "Рекомендуется использовать инструменты безопасности, такие как предыгровое обсуждение, X-card, Lines and Veils и политика открытого стола, чтобы обеспечить игрокам приятную игру.",
]
EXPECTED_HEADING_PAGES = {
    "### Наткнуться на съёмочную площадку": "025",
}


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_blocks(text: str) -> list[tuple[str | None, str]]:
    matches = list(SOURCE_PAGE_RE.finditer(text))
    if not matches:
        return [(None, text)]
    blocks: list[tuple[str | None, str]] = []
    if matches[0].start() > 0:
        blocks.append((None, text[: matches[0].start()]))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.start() : end]))
    return blocks


def strip_printed_page_number_residue(text: str) -> tuple[str, dict[str, object]]:
    """Remove old printed source-page numbers that survived OCR/translation."""
    blocks = page_blocks(text)
    if len(blocks) == 1 and blocks[0][0] is None:
        return text, {"count": 0, "items": []}
    rebuilt: list[str] = []
    removed: list[dict[str, object]] = []
    for page, block in blocks:
        if page is None or page == "004":
            rebuilt.append(block)
            continue
        printed_page = int(page) - 4
        if printed_page <= 0:
            rebuilt.append(block)
            continue
        new_lines: list[str] = []
        for line_number, line in enumerate(block.splitlines(), start=1):
            stripped = line.strip()
            heading_residue = re.match(rf"^{printed_page}\s+(?P<label>\S[\s\S]*)$", stripped)
            label = heading_residue.group("label").strip() if heading_residue else ""
            normalized_label = _normalize_heading_prefix(label)
            label_is_known_heading = bool(
                label
                and (
                    label in LINE_HEADINGS
                    or label.upper() in LINE_HEADINGS
                    or label in INLINE_HEADINGS
                    or label.upper() in INLINE_HEADINGS
                    or label in RESIDUAL_TITLE_LABELS
                    or label in KEEPER_SOURCE_TOC_ENTRIES
                    or any(_normalize_heading_prefix(key) == normalized_label for key in LINE_HEADINGS)
                    or any(_normalize_heading_prefix(key) == normalized_label for key in INLINE_HEADINGS)
                    or any(_normalize_heading_prefix(key) == normalized_label for key in RESIDUAL_TITLE_LABELS)
                    or any(_normalize_heading_prefix(key) == normalized_label for key in KEEPER_SOURCE_TOC_ENTRIES)
                )
            )
            if stripped == str(printed_page) or label_is_known_heading:
                removed.append(
                    {
                        "source_page": page,
                        "printed_page": printed_page,
                        "line": line_number,
                        "text": stripped,
                    }
                )
                continue
            new_lines.append(line)
        rebuilt_block = "\n".join(new_lines)
        if block.endswith("\n"):
            rebuilt_block += "\n"
        rebuilt.append(rebuilt_block)
    return "".join(rebuilt), {"count": len(removed), "items": removed}


def printed_page_number_residues(text: str) -> list[dict[str, object]]:
    residues: list[dict[str, object]] = []
    for page, block in page_blocks(text):
        if page is None or page == "004":
            continue
        printed_page = int(page) - 4
        if printed_page <= 0:
            continue
        for line_number, line in enumerate(block.splitlines(), start=1):
            stripped = line.strip()
            heading_residue = re.match(rf"^{printed_page}\s+(?P<label>\S[\s\S]*)$", stripped)
            label = heading_residue.group("label").strip() if heading_residue else ""
            normalized_label = _normalize_heading_prefix(label)
            label_is_known_heading = bool(
                label
                and (
                    label in LINE_HEADINGS
                    or label.upper() in LINE_HEADINGS
                    or label in INLINE_HEADINGS
                    or label.upper() in INLINE_HEADINGS
                    or label in RESIDUAL_TITLE_LABELS
                    or label in KEEPER_SOURCE_TOC_ENTRIES
                    or any(_normalize_heading_prefix(key) == normalized_label for key in LINE_HEADINGS)
                    or any(_normalize_heading_prefix(key) == normalized_label for key in INLINE_HEADINGS)
                    or any(_normalize_heading_prefix(key) == normalized_label for key in RESIDUAL_TITLE_LABELS)
                    or any(_normalize_heading_prefix(key) == normalized_label for key in KEEPER_SOURCE_TOC_ENTRIES)
                )
            )
            if stripped == str(printed_page) or label_is_known_heading:
                residues.append(
                    {
                        "source_page": page,
                        "printed_page": printed_page,
                        "line": line_number,
                        "text": stripped,
                    }
                )
    return residues


def split_inline_headings(line: str) -> list[str]:
    parts = [line]
    labels = set(INLINE_HEADINGS)
    labels.update(LINE_HEADINGS)
    labels.update(CHARACTER_HEADING_MAP)
    labels.update(PREGEN_NAMES)
    embedded_split_labels = set(CHARACTER_HEADING_MAP)
    embedded_split_labels.update(PREGEN_NAMES)
    embedded_split_labels.update(LINE_HEADINGS)
    for label in sorted(labels, key=len, reverse=True):
        next_parts: list[str] = []
        for part in parts:
            stripped = part.strip()
            numbered = re.match(r"^(?P<page>\d{1,3})\s+(?P<body>.+)$", stripped)
            body = numbered.group("body") if numbered else stripped
            prefix = f"{numbered.group('page')} " if numbered else ""
            if body.startswith(label) and body != label:
                tail = re.sub(r"^[,;:—–-]\s*", "", body[len(label) :].lstrip())
                next_parts.append(prefix + label)
                if tail:
                    next_parts.append(tail)
            elif label in embedded_split_labels and label in body and body != label:
                next_parts.extend(re.split(rf"(?<!^)\s+(?={re.escape(label)}(?:\s|$))", part))
            else:
                next_parts.append(part)
        parts = next_parts
    return parts


def emit_heading(out: list[str], heading: str, seen: set[str]) -> None:
    if heading in seen and heading not in DUPLICATE_ALLOWED_HEADINGS:
        return
    if out and out[-1] != "":
        out.append("")
    out.append(heading)
    out.append("")
    seen.add(heading)


def slug(title: str) -> str:
    return re.sub(r"[^0-9A-Za-zА-Яа-яЁё]+", "-", title).strip("-").lower()


def html_slugify(title: str) -> str:
    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    title = "".join(mapping.get(ch, ch) for ch in title.lower())
    return re.sub(r"[^a-z0-9]+", "-", title).strip("-") or "section"


def unique_html_slug(title: str, used: dict[str, int]) -> str:
    base = html_slugify(title)
    used[base] = used.get(base, 0) + 1
    return base if used[base] == 1 else f"{base}-{used[base]}"


def page_heading_anchors(text: str) -> dict[str, str]:
    """Return source-page -> nearest useful HTML heading anchor.

    Production HTML gives page sections their own `page-NNN` ids, but the user
    asked for page references to land on sections. The first heading on a target
    source page is best; pages without headings fall back to the nearest
    previous heading.
    """
    used: dict[str, int] = {}
    page_to_first_heading: dict[str, str] = {}
    page_to_nearest_heading: dict[str, str] = {}
    current_page: str | None = None
    nearest_heading: str | None = None
    for line in text.splitlines():
        page_match = SOURCE_PAGE_RE.fullmatch(line.strip())
        if page_match:
            current_page = page_match.group(1)
            if nearest_heading:
                page_to_nearest_heading[current_page] = nearest_heading
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if not heading_match:
            continue
        anchor = unique_html_slug(heading_match.group(2).strip(), used)
        nearest_heading = anchor
        if current_page and current_page not in page_to_first_heading:
            page_to_first_heading[current_page] = anchor
        if current_page:
            page_to_nearest_heading[current_page] = anchor
    anchors = dict(page_to_nearest_heading)
    anchors.update(page_to_first_heading)
    return anchors


def link_internal_page_references(text: str) -> tuple[str, dict[str, object]]:
    """Link internal printed page references to generated section anchors.

    Innsmouth source PDF has four front-matter pages before printed scenario
    page numbering, so printed `страница 13` maps to source page `017`.
    References that do not map to a current source page are left as text; this
    preserves external rulebook page references such as pages 94/121/167.
    """
    printed_to_source_offset = 4
    anchors = page_heading_anchors(text)
    linked: list[dict[str, object]] = []
    unlinked_internal: list[dict[str, object]] = []

    def replace_segment(segment: str, line_no: int) -> str:
        def repl(match: re.Match[str]) -> str:
            printed_page = int(match.group("page"))
            source_page = PRINTED_PAGE_TARGET_OVERRIDES.get(printed_page, f"{printed_page + printed_to_source_offset:03d}")
            anchor = anchors.get(source_page)
            if not anchor:
                return match.group(0)
            linked.append(
                {
                    "line": line_no,
                    "printed_page": printed_page,
                    "source_page": source_page,
                    "anchor": anchor,
                    "text": match.group(0),
                }
            )
            return f"[{match.group(0)}](#{anchor})"

        return PAGE_REFERENCE_RE.sub(repl, segment)

    out_lines: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith("#")
            or stripped.startswith("<!--")
            or stripped.startswith("<div ")
            or stripped.startswith("<img ")
            or stripped.startswith("![")
        ):
            out_lines.append(line)
            continue
        pieces = re.split(r"(\[[^\]]+\]\([^)]+\))", line)
        rebuilt = []
        for piece in pieces:
            if re.fullmatch(r"\[[^\]]+\]\([^)]+\)", piece):
                rebuilt.append(piece)
            else:
                rebuilt.append(replace_segment(piece, line_no))
        out_lines.append("".join(rebuilt))

    linked_keys = {(int(row["line"]), int(row["printed_page"])) for row in linked}
    for line_no, line in enumerate(out_lines, start=1):
        for match in PAGE_REFERENCE_RE.finditer(line):
            printed_page = int(match.group("page"))
            source_page = PRINTED_PAGE_TARGET_OVERRIDES.get(printed_page, f"{printed_page + printed_to_source_offset:03d}")
            if source_page in anchors and (line_no, printed_page) not in linked_keys:
                unlinked_internal.append(
                    {
                        "line": line_no,
                        "printed_page": printed_page,
                        "source_page": source_page,
                        "text": match.group(0),
                    }
                )
    return "\n".join(out_lines), {
        "printed_to_source_page_offset": printed_to_source_offset,
        "linked": len(linked),
        "linked_refs": linked,
        "unlinked_internal": unlinked_internal,
        "status": "pass" if not unlinked_internal else "fail",
    }


def add_stable_heading_anchors(text: str) -> str:
    counts: dict[str, int] = {}
    out: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            title = match.group(2).strip()
            base = f"section-{slug(title)}"
            counts[base] = counts.get(base, 0) + 1
            anchor = base if counts[base] == 1 else f"{base}-{counts[base]}"
            out.append(f'<a id="{anchor}"></a>')
        out.append(line)
    return "\n".join(out)


def structure_block(page: str | None, block: str, seen: set[str]) -> str:
    lines = block.splitlines()
    out: list[str] = []
    current_page: str | None = page
    for line in lines:
        stripped = line.strip()
        marker = SOURCE_PAGE_RE.fullmatch(stripped)
        if marker:
            current_page = marker.group(1)
            out.append(line)
            for heading in PAGE_PREAMBLE_HEADINGS.get(current_page, []):
                emit_heading(out, heading, seen)
            handout_heading = HANDOUT_HEADINGS.get(current_page)
            if handout_heading:
                emit_heading(out, handout_heading, seen)
            continue
        if current_page == "004":
            if stripped == "СОДЕРЖАНИЕ":
                continue
            out.append(line)
            continue
        if current_page == "044":
            out.append(line)
            continue
        if stripped in {"Действующие лица"}:
            continue
        if stripped in {"ПОДГОТОВКА К ИГРЕ", "ДЕЙСТВУЮЩИЕ ЛИЦА", "На съёмочной площадке"}:
            heading = "### На съёмочной площадке" if stripped == "На съёмочной площадке" else LINE_HEADINGS.get(stripped)
            if heading:
                emit_heading(out, heading, seen)
            continue
        for part in split_inline_headings(line):
            part_stripped = part.strip()
            if not part_stripped:
                out.append(part)
                continue
            heading_candidate = re.sub(r"^\d{1,3}\s+(?=\S)", "", part_stripped)
            if heading_candidate in MAIN_CHARACTER_CAPTION_LABELS and stripped == heading_candidate:
                # Standalone character names in the Dramatis Personae pages are
                # usually image captions or OCR residue. The real character lead
                # carries an age/role tail and is handled below.
                continue
            mapped_character_heading = None
            for label, mapped_heading in CHARACTER_HEADING_MAP.items():
                if heading_candidate == label or heading_candidate.startswith(f"{label},"):
                    mapped_character_heading = mapped_heading
                    break
            if mapped_character_heading:
                emit_heading(out, mapped_character_heading, seen)
                if heading_candidate != label:
                    tail = (
                        re.sub(r"^[,;:—–-]\s*", "", heading_candidate[len(label) :].lstrip())
                        if heading_candidate.startswith(label)
                        else heading_candidate
                    )
                    if tail:
                        out.append(tail)
                continue
            if heading_candidate in HANDOUT_LABELS:
                if current_page in HANDOUT_HEADINGS and HANDOUT_HEADINGS[current_page] == f"### {heading_candidate}":
                    heading = f"### {heading_candidate}"
                    emit_heading(out, heading, seen)
                    continue
                out.append(part)
                continue
            if heading_candidate in RESIDUAL_TITLE_LABELS:
                if current_page and "033" <= current_page <= "040":
                    continue
                heading = LINE_HEADINGS.get(heading_candidate.upper()) or INLINE_HEADINGS.get(heading_candidate.upper())
                if heading:
                    emit_heading(out, heading, seen)
                    continue
            if part_stripped.startswith(("- ", "* ", "+ ")):
                out.append(part)
                continue
            heading = LINE_HEADINGS.get(heading_candidate.upper()) or INLINE_HEADINGS.get(heading_candidate.upper())
            heading = heading or INLINE_HEADINGS.get(heading_candidate)
            heading = heading or LINE_HEADINGS.get(heading_candidate)
            if heading:
                emit_heading(out, heading, seen)
                if heading_candidate.upper() in LINE_HEADINGS or heading_candidate in LINE_HEADINGS:
                    continue
                remainder = heading_candidate
                for label in list(INLINE_HEADINGS) + list(LINE_HEADINGS):
                    if remainder.startswith(label):
                        remainder = remainder[len(label) :].lstrip()
                        break
                if remainder:
                    out.append(remainder)
                continue
            start_heading = next(
                (value for label, value in START_LINE_HEADINGS.items() if heading_candidate.startswith(label)),
                None,
            )
            if start_heading:
                label = start_heading.removeprefix("### ")
                if heading_candidate.startswith(f"{label} ") and ":" in heading_candidate:
                    out.append(part)
                    continue
                emit_heading(out, start_heading, seen)
                if heading_candidate != label:
                    out.append(heading_candidate)
                continue
            character = CHARACTER_LINE_RE.match(part_stripped)
            if character:
                emit_heading(out, f"### {character.group('name')}", seen)
                out.append(part_stripped)
                continue
            if heading_candidate in PREGEN_NAMES:
                emit_heading(out, CHARACTER_HEADING_MAP.get(heading_candidate, f"### {heading_candidate}"), seen)
                continue
            out.append(part)
    return "\n".join(out)


def project_bullets(text: str) -> tuple[str, dict[str, object]]:
    lines = text.splitlines()
    out: list[str] = []
    source_bullets = 0
    emitted_items = 0
    empty_bullets: list[int] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip() != "•":
            out.append(line)
            index += 1
            continue
        source_bullets += 1
        bullet_line = index + 1
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines) or lines[index].strip().startswith("<!--"):
            empty_bullets.append(bullet_line)
            out.append("•")
            continue
        item = lines[index].strip()
        out.append(f"- {item}")
        emitted_items += 1
        index += 1
    return "\n".join(out), {
        "source_bullet_markers": source_bullets,
        "emitted_markdown_list_items": emitted_items,
        "standalone_bullet_lines": len(re.findall(r"(?m)^•$", "\n".join(out))),
        "empty_bullets": empty_bullets,
    }


def reference_list_item(text: str) -> bool:
    return REFERENCE_LIST_RE.search(text) is not None


def normalize_plus_lists(text: str) -> tuple[str, dict[str, object]]:
    lines = text.splitlines()
    out: list[str] = []
    plus_items = 0
    reference_items = 0
    for line in lines:
        match = re.match(r"^(\s*)\+\s+(\S.*)$", line)
        if not match:
            out.append(line)
            continue
        plus_items += 1
        indent, value = match.groups()
        value = value.strip()
        if reference_list_item(value):
            out.append(f"{indent}> - {value}")
            reference_items += 1
        else:
            out.append(f"{indent}- {value}")
    return "\n".join(out), {
        "plus_list_items_normalized": plus_items,
        "reference_list_items_blockquoted": reference_items,
    }


def apply_reader_art_publication_policy(manifest: dict[str, object], manifest_path: Path) -> tuple[dict[str, object], dict[str, object]]:
    """Persist Innsmouth reader-art publication policy for downstream HTML/PDF.

    KeeperBook, HTML, and PDF must consume the same reader-art placement set.
    The HTML builder reads art_manifest.json directly, so suppressions and
    anchor overrides must be written back to the manifest rather than applied
    only while injecting Markdown blocks.
    """
    changed = False
    suppressed: list[str] = []
    anchor_overrides: list[dict[str, str]] = []
    placements = manifest.get("placements", [])
    if not isinstance(placements, list):
        return manifest, {
            "policy_applied": False,
            "findings": [{"code": "art_manifest_placements_not_list", "path": manifest_path.as_posix()}],
        }

    for placement in placements:
        if not isinstance(placement, dict):
            continue
        placement_id = str(placement.get("placement_id") or "").strip()
        if not placement_id:
            continue
        if placement_id in INNSMOUTH_SUPPRESSED_READER_ART_IDS:
            if placement.get("emit_reader_art_block"):
                changed = True
            placement["emit_reader_art_block"] = False
            placement["reader_publication_suppressed"] = True
            placement["reader_publication_policy"] = "innsmouth_reference_parity_no_page_anchor_backmatter"
            suppressed.append(placement_id)
        override = INNSMOUTH_READER_ART_ANCHOR_OVERRIDES.get(placement_id)
        if override:
            if placement.get("heading_id") != override:
                changed = True
            placement["heading_id"] = override
            placement["reader_publication_policy"] = "innsmouth_reference_parity_anchor_override"
            anchor_overrides.append({"placement_id": placement_id, "heading_id": override})

    if changed:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return manifest, {
        "policy_applied": True,
        "manifest_rewritten": changed,
        "suppressed": suppressed,
        "suppressed_count": len(suppressed),
        "anchor_overrides": anchor_overrides,
    }


def keeper_art_block(placement: dict[str, object]) -> str | None:
    placement_id = str(placement.get("placement_id") or "").strip()
    anchor_id = (
        INNSMOUTH_READER_ART_ANCHOR_OVERRIDES.get(placement_id)
        or str(placement.get("heading_id") or "").strip()
        or f"page-{str(placement.get('source_page') or '').zfill(3)}"
    )
    page = str(placement.get("source_page") or "").zfill(3)
    runtime_src = str(placement.get("runtime_src") or "").strip()
    if not placement_id or not anchor_id or not runtime_src:
        return None
    # KeeperBook is stored in Output/.../For_Keeper, one level below HTML/assets.
    md_src = f"../{runtime_src}" if runtime_src.startswith("Images") else runtime_src
    source_anchor_id = str(placement.get("source_anchor_id") or "").strip()
    source_anchor_kind = str(placement.get("source_anchor_kind") or "").strip()
    source_anchor_method = str(placement.get("source_anchor_method") or "").strip()
    source_attrs = ""
    if source_anchor_id:
        source_attrs += f' data-source-anchor-id="{html.escape(source_anchor_id, quote=True)}"'
    if source_anchor_kind:
        source_attrs += f' data-source-anchor-kind="{html.escape(source_anchor_kind, quote=True)}"'
    if source_anchor_method:
        source_attrs += f' data-source-anchor-method="{html.escape(source_anchor_method, quote=True)}"'
    return (
        f'<div class="keeper-art-block" data-placement-id="{placement_id}" '
        f'data-anchor-id="{anchor_id}" data-source-page="{page}"{source_attrs}> '
        f'<img id="{placement_id}-image" src="{md_src}" alt="{placement_id}"> </div>'
    )


def load_reader_art_manifest(manifest_path: Path, source_anchor_manifest_path: Path | None = None) -> tuple[dict[str, object], Path, bool]:
    """Prefer source-anchor manifest when present so downstream uses accepted PDF evidence."""
    if source_anchor_manifest_path and source_anchor_manifest_path.exists():
        return json.loads(source_anchor_manifest_path.read_text(encoding="utf-8")), source_anchor_manifest_path, True
    return json.loads(manifest_path.read_text(encoding="utf-8")), manifest_path, False


def source_anchor_heading_override(placement: dict[str, object], heading_lines: dict[str, int]) -> str | None:
    anchor_text = str(placement.get("source_anchor_text") or "").strip()
    if not anchor_text:
        return None
    candidate = html_slugify(anchor_text)
    if candidate in heading_lines:
        return candidate
    return None


def reader_art_sort_key(placement: dict[str, object]) -> tuple[int, int, str]:
    try:
        line_index = int(placement.get("source_anchor_line_index"))
    except (TypeError, ValueError):
        line_index = 10_000
    try:
        xref = int(placement.get("source_xref"))
    except (TypeError, ValueError):
        xref = 10_000_000
    return (line_index, xref, str(placement.get("placement_id") or ""))


def inject_reader_art_blocks(
    text: str,
    manifest_path: Path,
    source_anchor_manifest_path: Path | None = None,
) -> tuple[str, dict[str, object]]:
    if not manifest_path.exists():
        return text, {"enabled": False, "manifest": manifest_path.as_posix(), "inserted": 0, "findings": []}
    base_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _base_manifest, base_policy_report = apply_reader_art_publication_policy(base_manifest, manifest_path)
    manifest, effective_manifest_path, source_anchor_manifest_used = load_reader_art_manifest(manifest_path, source_anchor_manifest_path)
    manifest, policy_report = apply_reader_art_publication_policy(manifest, effective_manifest_path)
    policy_report["base_manifest"] = base_policy_report
    placements = [
        placement
        for placement in manifest.get("placements", [])
        if isinstance(placement, dict) and placement.get("emit_reader_art_block")
    ]
    existing = set(re.findall(r'data-placement-id="([^"]+)"', text))
    heading_lines: dict[str, int] = {}
    used_slugs: dict[str, int] = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if not heading:
            continue
        base = html_slugify(heading.group(2))
        used_slugs[base] = used_slugs.get(base, 0) + 1
        heading_id = base if used_slugs[base] == 1 else f"{base}-{used_slugs[base]}"
        heading_lines[heading_id] = index
    inserts_by_page: dict[str, list[tuple[tuple[int, int, str], str]]] = {}
    inserts_by_line: dict[int, list[tuple[tuple[int, int, str], str]]] = {}
    findings: list[dict[str, object]] = []
    suppressed: list[str] = []
    anchor_overrides: list[dict[str, str]] = []
    source_anchor_heading_overrides: list[dict[str, str]] = []
    inserted = 0
    for placement in placements:
        placement_id = str(placement.get("placement_id") or "").strip()
        if placement_id in INNSMOUTH_SUPPRESSED_READER_ART_IDS:
            suppressed.append(placement_id)
            continue
        if not placement_id or placement_id in existing:
            continue
        sort_key = reader_art_sort_key(placement)
        page = str(placement.get("source_page") or "").zfill(3)
        source_heading_id = source_anchor_heading_override(placement, heading_lines)
        heading_id = (
            INNSMOUTH_READER_ART_ANCHOR_OVERRIDES.get(placement_id)
            or source_heading_id
            or str(placement.get("heading_id") or "").strip()
        )
        if source_heading_id:
            placement["heading_id"] = source_heading_id
            source_anchor_heading_overrides.append({"placement_id": placement_id, "heading_id": source_heading_id})
        if placement_id in INNSMOUTH_READER_ART_ANCHOR_OVERRIDES:
            anchor_overrides.append({"placement_id": placement_id, "heading_id": heading_id})
        block = keeper_art_block(placement)
        if not block or not page:
            findings.append({"code": "reader_art_block_incomplete", "placement_id": placement_id})
            continue
        heading_index = heading_lines.get(heading_id)
        if heading_index is not None:
            inserts_by_line.setdefault(heading_index, []).append((sort_key, block))
        else:
            inserts_by_page.setdefault(page, []).append((sort_key, block))
        inserted += 1

    if not inserts_by_page and not inserts_by_line:
        return text, {
            "enabled": True,
            "manifest": effective_manifest_path.as_posix(),
            "source_anchor_manifest_used": source_anchor_manifest_used,
            "placements": len(placements),
            "inserted": 0,
            "suppressed": suppressed,
            "suppressed_count": len(suppressed),
            "anchor_overrides": anchor_overrides,
            "source_anchor_heading_overrides": source_anchor_heading_overrides,
            "publication_policy": policy_report,
            "findings": findings,
        }

    out: list[str] = []
    for index, line in enumerate(lines):
        out.append(line)
        if index in inserts_by_line:
            out.append("")
            for _sort_key, block in sorted(inserts_by_line[index]):
                out.append(block)
                out.append("")
        page_match = SOURCE_PAGE_RE.fullmatch(line.strip())
        if page_match and page_match.group(1) in inserts_by_page:
            out.append("")
            for _sort_key, block in sorted(inserts_by_page[page_match.group(1)]):
                out.append(block)
                out.append("")
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), {
        "enabled": True,
        "manifest": effective_manifest_path.as_posix(),
        "source_anchor_manifest_used": source_anchor_manifest_used,
        "placements": len(placements),
        "inserted": inserted,
        "suppressed": suppressed,
        "suppressed_count": len(suppressed),
        "anchor_overrides": anchor_overrides,
        "source_anchor_heading_overrides": source_anchor_heading_overrides,
        "publication_policy": policy_report,
        "findings": findings,
    }


def cleanup_reader_art_page_marker_residuals(text: str) -> str:
    """Remove service-page markers left after publication-suppressed art."""
    return re.sub(
        r"\n{2,}<!-- source-page-044 -->\s*(?=<!-- source-page-045 -->)",
        "\n\n",
        text,
        count=1,
    )


def markdown_table(columns: list[str], rows: list[list[str]]) -> str:
    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ").strip()

    lines = [
        "| " + " | ".join(cell(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


TABLE_1_ROWS = [
    ["1922", "Мать Гидра преследует сны П.А. Баззлдона, гоня его в Аркхэм."],
    ["3 недели назад", "П.А. Баззлдон прибывает в Аркхэм."],
    ["2 недели назад", "П.А. Баззлдон убеждает Генри Армитажа отдать ему Атлантский самоцвет."],
    ["10 дней назад", "Съёмочная группа отправляется в Иннсмут поездом."],
    ["9 дней назад", "Начинаются съёмки, но их мучают поломки камеры."],
    ["3 дня назад", "Джинни Дюбуа крадёт самоцвет из лаборатории Макгуайра."],
    ["Сейчас", "Сыщиков отправляют в Иннсмут вернуть самоцвет."],
    ["Вечером второго дня", "Начинаются съёмки эпического финала."],
]

TABLE_2_ROWS = [
    ["1-5", "Какая удача: Сыщики обнаруживают быстрый и лёгкий путь туда, куда пытаются попасть. Всё это ощущается как отличная маленькая авантюра: карабкаться вверх и вниз среди всех этих скал."],
    ["6-10", "Следы: Сыщики замечают свежие следы, отчётливые как на ладони. При успешном броске Следопыт становится ясно, что их оставил кто-то в женской обуви, вероятно, примерно такого же телосложения, как Джинни или Анна."],
    ["11-20", "Треснувшая улика: Сыщики обнаруживают на земле брошенный кусок металла. Смахнув с него пыль, они понимают, что он похож блеском на изображения Драгоценности. Но форма не та. При успешном броске Оценка они определяют, что это золотой сплав, вероятно, ценный."],
    ["21-30", "Зловещий пляж: Сыщики сбиваются с пути и оказываются на зловеще выглядящем берегу. Они свернули не туда, а погода снаружи ухудшается. Они видят, как буря собирается прямо над наполовину затопленным островом недалеко от берега Иннсмута. Им придётся бросать снова."],
    ["31-40", "Дыра в стене: В стене есть отверстие, а с другой стороны пробивается тусклый свет. Оно как раз достаточно велико, чтобы кто-то мог подглядеть в него глазом. Любой сыщик, заглянувший туда, сталкивается с незабываемым образом глаз, щупалец и зубов; это сбивает с толку и ужасает, вызывая бросок Рассудок (1/1D4 потеря)."],
    ["41-50", "Заваленный проход: Путь вперёд перекрыт обломками. Хотя сыщики с РАЗМ ниже 60 могут проползти сквозь них, более крупные сыщики должны пройти бросок ЛВК или получить 1D4 урон от острого камня."],
    ["51-60", "Обвалившаяся пещера: В полу пещеры есть провал, из него поднимается рыбный запах. Хотя провал слишком узок, чтобы туда можно было спуститься, сыщик может в нём застрять. Сыщикам нужно пройти бросок Прыжок или Лазанье, иначе они рискуют упасть внутрь. Помощь друг другу даёт бонусный кубик. Сыщики, застрявшие там, получают 1D3 урон."],
    ["61-70", "Прогорклый смрад: Сыщиков выворачивает, когда туннель заполняет отвратительнейшая вонь. Запах яиц, плесени и смерти сжимает им горло. Сыщики должны пройти бросок ТЕЛ или получить 1D3 пункта урона, пока выкашливают себе внутренности."],
    ["71-80", "Ужасные звуки: Сквозь стены доносится чудовищный звук того, как какое-то неестественное существо шумно жрёт. Звучит так, будто оно отдирает плоть от костей. Это вызывает бросок Рассудок (0/1D2 потеря)."],
    ["81-90", "Внезапный удар: Словно из ниоткуда, что-то длинное и скользкое выстреливает из-за двух больших скал и хлещет по тому источнику света, который используют сыщики. Всё внезапно погружается во тьму, вызывая бросок Рассудок (0/1D3 потеря). Сыщик, держащий свет, получает штрафной кубик на этот бросок."],
    ["91-95", "Наблюдающие глаза: Сыщику, идущему в конце группы, кажется, что он увидел светящиеся глаза, следящие за ними из теней. Он делает бросок Рассудок (0/1D4 потеря), пытаясь убедить остальных, что за ними следят."],
    ["96-100", "Близкая встреча: Выйдя на уступ, сыщики видят, что внизу пещера заполнена водой. Какое-то существо лениво плавает там внизу. Сыщики должны тихо пройти по уступу, иначе рискуют потревожить Глубоководного в воде. Один сыщик должен пройти бросок Скрытность за всю группу, иначе они должны найти другой путь и бросать снова. При провале броска Скрытность из воды появляется Глубоководный и пытается сожрать сыщиков."],
]


def replace_table_1(text: str) -> tuple[str, bool]:
    title = "Таблица 1: хронология событий"
    start = text.find(title)
    end_marker = "<!-- source-page-007 -->"
    if start < 0:
        return text, False
    end = text.find(end_marker, start)
    if end < 0:
        return text, False
    replacement = title + "\n\n" + markdown_table(["Когда", "Событие"], TABLE_1_ROWS) + "\n\n"
    return text[:start] + replacement + text[end:], True


def replace_table_2(text: str) -> tuple[str, bool]:
    canonical_title = "Таблица 2: встречи в пещерах"
    title_variants = [
        "Таблица 2: столкновения в пещерах",
        "Таблица 2: встречи в пещерах",
        "Table 2: встречи в пещерах",
        "Table 2: столкновения в пещерах",
    ]
    found_title = next((title for title in title_variants if title in text), None)
    start = text.find(found_title) if found_title else -1
    end_marker = "<!-- source-page-024 -->"
    if start < 0:
        return text, False
    end = text.find(end_marker, start)
    if end < 0:
        return text, False
    replacement = canonical_title + "\n\n" + markdown_table(["1D100", "Описание"], TABLE_2_ROWS) + "\n\n"
    return text[:start] + replacement + text[end:], True


def is_structural_line(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or stripped.startswith(("#", ">", "|", "<!--", "![", "<", "- "))
    )


def join_words(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(part.strip() for part in parts if part.strip())).strip()


def join_wrapped_list_items(text: str) -> tuple[str, dict[str, int]]:
    lines = text.splitlines()
    out: list[str] = []
    joined = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped.startswith("- "):
            out.append(line)
            index += 1
            continue
        current = stripped
        index += 1
        while (
            index < len(lines)
            and lines[index].strip()
            and not is_structural_line(lines[index])
            and not re.search(r'[.;:!?…»)"\]]$', current)
        ):
            current = join_words([current, lines[index].strip()])
            joined += 1
            index += 1
        out.append(current)
    return "\n".join(out), {"wrapped_list_continuations_joined": joined}


CONTINUATION_OBJECT_RE = re.compile(
    r"\b(?:письмо|записк[ауи]|документ|улику|артефакт|предмет|книг[ауи]|бумаг[ауи])\b",
    re.I,
)
CONTINUATION_PRONOUN_RE = re.compile(r"^(?:Оно|Она|Он|Это)\b")


def join_list_item_continuation_paragraphs(text: str) -> tuple[str, dict[str, int]]:
    paragraphs = re.split(r"\n{2,}", text.strip())
    out: list[str] = []
    joined = 0
    index = 0
    while index < len(paragraphs):
        paragraph = paragraphs[index].strip()
        if (
            out
            and paragraph
            and CONTINUATION_PRONOUN_RE.match(paragraph)
        ):
            previous_lines = out[-1].splitlines()
            if (
                previous_lines
                and previous_lines[-1].lstrip().startswith("- ")
                and CONTINUATION_OBJECT_RE.search(previous_lines[-1])
            ):
                previous_lines[-1] = join_words([previous_lines[-1], paragraph])
                out[-1] = "\n".join(previous_lines)
                joined += 1
                index += 1
                continue
        out.append(paragraph)
        index += 1
    return "\n\n".join(out).strip() + "\n", {"list_item_continuation_paragraphs_joined": joined}


CHARACTER_NAME_REPLACEMENTS = [
    ("Женевьева «Джинни» Дюбуа", "Genevieve ‘Ginny’ Dubois"),
    ("Genevieve 'Ginny' Dubois", "Genevieve ‘Ginny’ Dubois"),
    ("П.А. Баззлдон", "P.A. Bazzledon"),
    ("P.A Bazzledon", "P.A. Bazzledon"),
    ("Анна Диас", "Anna Díaz"),
    ("Anna Диас", "Anna Díaz"),
    ("Anna Diaz", "Anna Díaz"),
    ("Кристофер Макгуайр", "Christopher McGuire"),
    ("Сэмми Брюстер", "Sammy Brewster"),
    ("Иеремия Брюстер", "Jeremiah Brewster"),
    ("Задок Аллен", "Zadok Allen"),
    ("Карен Уокер", "Karen Walker"),
    ("Доктор Генри Армитидж", "Dr. Henry Armitage"),
    ("Доктор Генри Армитаж", "Dr. Henry Armitage"),
    ("Генри Армитидж", "Henry Armitage"),
    ("Генри Армитаж", "Henry Armitage"),
    ("Обеда Марша", "Obed Marsh"),
    ("Обедом Маршем", "Obed Marsh"),
    ("Обед Марш", "Obed Marsh"),
    ("Хьюго «Шримпи» Харгривз", "Hugo ‘Shrimpy’ Hargreaves"),
    ("HUGO ‘SHRIMPY’ HARGREAVES", "Hugo ‘Shrimpy’ Hargreaves"),
    ("HUGO 'SHRIMPY' HARGREAVES", "Hugo ‘Shrimpy’ Hargreaves"),
    ("Пэтти Гиллиан", "Patty Gillian"),
    ("PATTY GILLIAN", "Patty Gillian"),
    ("Иэн Торрес", "Ian Torres"),
    ("IAN TORRES", "Ian Torres"),
    ("Тиффани Киспе", "Tiffany Quispe"),
    ("TIFFANY QUISPE", "Tiffany Quispe"),
    ("Маргарет «Мэгги» Майерс", "Margaret ‘Maggie’ Myers"),
    ("MARGARET ‘MAGGIE’ MYERS", "Margaret ‘Maggie’ Myers"),
    ("MARGARET 'MAGGIE' MYERS", "Margaret ‘Maggie’ Myers"),
    ("Дианой Лоринг", "Diane Loring"),
    ("Диане Лоринг", "Diane Loring"),
    ("Диану Лоринг", "Diane Loring"),
    ("Диана Лоринг", "Diane Loring"),
    ("Bazzledon’s Office", "Bazzledon’s Office"),
    ("Кабинет Баззлдона", "Bazzledon’s Office"),
    ("Кабинет Bazzledon", "Bazzledon’s Office"),
    ("Трейлер Джинни", "Ginny’s Trailer"),
    ("Трейлер Ginny", "Ginny’s Trailer"),
    ("Лаборатория Макгуайра", "McGuire’s Lab"),
    ("Лаборатория McGuire", "McGuire’s Lab"),
    ("Дом Брюстеров", "Brewster Residence"),
    ("Резиденции Брюстеров", "Brewster Residence"),
    ("Резиденция Брюстеров", "Brewster Residence"),
    ("Резиденция Brewster", "Brewster Residence"),
]

CHARACTER_TOKEN_REPLACEMENTS = [
    ("Баззлдона", "Bazzledon"),
    ("Баззлдоном", "Bazzledon"),
    ("Баззлдону", "Bazzledon"),
    ("Баззлдон", "Bazzledon"),
    ("Джинни", "Ginny"),
    ("Дюбуа", "Dubois"),
    ("Анну", "Anna"),
    ("Анной", "Anna"),
    ("Анне", "Anna"),
    ("Анна", "Anna"),
    ("Диас", "Díaz"),
    ("Макгуайра", "McGuire"),
    ("Макгуайру", "McGuire"),
    ("Макгуайром", "McGuire"),
    ("Макгуайр", "McGuire"),
    ("Кристофер", "Christopher"),
    ("Сэмми", "Sammy"),
    ("Иеремии", "Jeremiah"),
    ("Иеремию", "Jeremiah"),
    ("Иеремия", "Jeremiah"),
    ("Задока", "Zadok"),
    ("Задок", "Zadok"),
    ("Аллена", "Allen"),
    ("Аллен", "Allen"),
    ("Карен", "Karen"),
    ("Уокер", "Walker"),
    ("Хьюго", "Hugo"),
    ("Шримпи", "Shrimpy"),
    ("Харгривз", "Hargreaves"),
    ("Пэтти", "Patty"),
    ("Гиллиан", "Gillian"),
    ("Иэна", "Ian"),
    ("Иэн", "Ian"),
    ("Торрес", "Torres"),
    ("Тиффани", "Tiffany"),
    ("Киспе", "Quispe"),
    ("Маргарет", "Margaret"),
    ("Мэгги", "Maggie"),
    ("Майерс", "Myers"),
    ("Дианой", "Diane"),
    ("Диане", "Diane"),
    ("Диану", "Diane"),
    ("Диана", "Diane"),
    ("Лоринг", "Loring"),
    ("Генри", "Henry"),
    ("Армитиджа", "Armitage"),
    ("Армитиджем", "Armitage"),
    ("Армитидж", "Armitage"),
    ("Армитажа", "Armitage"),
    ("Армитажем", "Armitage"),
    ("Армитаж", "Armitage"),
    ("Обеда", "Obed"),
    ("Обедом", "Obed"),
    ("Обед", "Obed"),
    ("Марша", "Marsh"),
    ("Маршем", "Marsh"),
    ("Марш", "Marsh"),
]


def normalize_character_names(text: str) -> tuple[str, dict[str, object]]:
    """Keep named characters in source English form for Keeper/HTML consistency."""
    replacements: dict[str, int] = {}
    for source, target in CHARACTER_NAME_REPLACEMENTS:
        text, count = re.subn(re.escape(source), target, text)
        if count:
            replacements[source] = replacements.get(source, 0) + count
    for source, target in CHARACTER_TOKEN_REPLACEMENTS:
        pattern = rf"(?<![A-Za-zА-Яа-яЁё]){re.escape(source)}(?![A-Za-zА-Яа-яЁё])"
        text, count = re.subn(pattern, target, text)
        if count:
            replacements[source] = replacements.get(source, 0) + count
    return text, {
        "total_replacements": sum(replacements.values()),
        "replacements": replacements,
    }


def split_long_paragraph(paragraph: str, max_chars: int = 900) -> list[str]:
    conditional_hits = len(re.findall(r"\bЕсли\b|\bВ противном случае\b", paragraph))
    if len(paragraph) <= max_chars and conditional_hits < 3:
        return [paragraph]
    cues = [
        "Если ",
        "Когда ",
        "Однако ",
        "Ещё ",
        "Те, кто ",
        "Тогда ",
        "Эта поддержка ",
        "Так, ",
        "Ginny ",
        "Джинни ",
        "Сейчас ",
        "Сыщики ",
        "Сыщики, ",
        "Внутри ",
        "Приглашая ",
        "Дом был ",
        "Иеремия ",
        "Для него ",
        "Ему было ",
        "Он отправился ",
        "Положение ",
        "Начинается ",
        "В этот момент ",
        "В противном случае ",
        "Когда на ",
        "Испытывая ",
        "ПРИБЫТИЕ ",
        "Примечание Хранителю:",
        "Заметка Хранителю:",
        "Первая клятва:",
        "Вторая клятва:",
        "Третья клятва:",
    ]
    pattern = r"(?<=[.!?])\s+(?=(?:" + "|".join(re.escape(cue) for cue in cues) + r"))"
    parts = [part.strip() for part in re.split(pattern, paragraph) if part.strip()]
    if len(parts) <= 1:
        parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", paragraph) if part.strip()]
    if conditional_hits >= 3 and len(parts) > 1:
        return parts
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current} {part}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = part
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks or [paragraph]


def keeper_note_callout(note: str) -> str:
    note = note.strip()
    return "\n".join(["> <!-- callout-class: keeper-note -->", "> **Примечание Хранителю.** " + note])


def split_keeper_note(paragraph: str) -> list[str]:
    result: list[str] = []
    remaining = paragraph.strip()
    while remaining:
        match = NOTE_RE.search(remaining)
        if not match:
            result.append(remaining)
            break
        before = remaining[: match.start()].strip()
        if before:
            result.extend(split_long_paragraph(before))
        after = remaining[match.end() :].strip()
        next_match = NOTE_RE.search(after)
        if next_match:
            note = after[: next_match.start()].strip()
            remaining = after[next_match.start() :].strip()
        else:
            note = after
            remaining = ""
        if note:
            result.append(keeper_note_callout(note))
    return result or [paragraph]


def wrap_keeper_info_sections(text: str) -> tuple[str, dict[str, object]]:
    """Keep source Keeper Information sections as normal body sections.

    Innsmouth uses "Keeper Information" as a full source heading, while
    "Keeper note"/"Примечание Хранителю" denotes boxed Keeper-facing callouts.
    """
    return text, {"wrapped": [], "count": 0}


def normalize_flow(text: str) -> tuple[str, dict[str, int]]:
    lines = text.splitlines()
    out: list[str] = []
    stats = {
        "joined_paragraph_lines": 0,
        "split_long_paragraphs": 0,
        "keeper_note_callouts": 0,
    }
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            if out and out[-1] != "":
                out.append("")
            index += 1
            continue
        if is_structural_line(line):
            out.append(line.rstrip())
            index += 1
            continue
        parts = [stripped]
        index += 1
        while index < len(lines) and not is_structural_line(lines[index]):
            parts.append(lines[index].strip())
            stats["joined_paragraph_lines"] += 1
            index += 1
        paragraph = join_words(parts)
        chunks: list[str] = []
        for chunk in split_long_paragraph(paragraph):
            chunks.extend(split_keeper_note(chunk))
        if len(chunks) > 1:
            stats["split_long_paragraphs"] += len(chunks) - 1
        for chunk in chunks:
            out.append(chunk)
            out.append("")
    normalized = "\n".join(out)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip() + "\n"
    stats["keeper_note_callouts"] = len(re.findall(r"callout-class:\s*keeper-note", normalized))
    return normalized, stats


def apply_semantic_projection(text: str) -> tuple[str, dict[str, object]]:
    text, flow_stats = normalize_flow(text)
    text, list_wrap_stats = join_wrapped_list_items(text)
    text, list_continuation_stats = join_list_item_continuation_paragraphs(text)
    text, table1 = replace_table_1(text)
    text, table2 = replace_table_2(text)
    text = re.sub(r"(?<!\n)\s+(Таблица\s+[12]:)", r"\n\n\1", text)
    text = text.replace(" PРИБЫТИЕ ", " #### Прибытие: практическая справка ")
    text = re.sub(r"\s+ПРИБЫТИЕ\s+", "\n\n#### Прибытие: практическая справка\n\n", text)
    text = re.sub(
        r"(?m)^> \*\*Примечание Хранителю\.\*\* «Иннсмутский ужас» не будет\s*\n+«звуковое кино»\. Это немой фильм\. Стремление к цвету и звуку в\s*\n+кино возникло примерно в одно и то же время, но и то и другое сразу\?\s*\n+Безумие\.",
        "> **Примечание Хранителю.** «Иннсмутский ужас» не будет «звуковым кино». Это немой фильм. Стремление к цвету и звуку в кино возникло примерно в одно и то же время, но и то и другое сразу? Безумие.",
        text,
    )
    text = re.sub(
        r"(?m)^> \*\*Примечание Хранителю\.\*\* если Мискатоникский театр не сгорел во время вашего прохождения Stage Fright, то вскоре после этого он сгорел в результате другого несчастного случая\. Не бойтесь\s*\n+впрочем, скоро его перестроят!",
        "> **Примечание Хранителю.** если Мискатоникский театр не сгорел во время вашего прохождения Stage Fright, то вскоре после этого он сгорел в результате другого несчастного случая. Не бойтесь, впрочем, скоро его перестроят!",
        text,
    )
    text = text.replace(
        "Смогут ли сыщики раскрыть правду, прежде чем ставки повысятся и Иннсмутский ужас превратится во что-то более жуткое, чем то, что удаётся запечатлеть объективу камеры? «Мы уплывём к тому мрачному рифу в море и нырнём сквозь чёрные бездны к циклопическому, многоколонному Й’ха-нтлею, и в этом логове Глубоководных будем жить среди чудес и славы вечно». —Г.Ф. Лавкрафт, «Тень над Иннсмутом»",
        "Смогут ли сыщики раскрыть правду, прежде чем ставки повысятся и Иннсмутский ужас превратится во что-то более жуткое, чем то, что удаётся запечатлеть объективу камеры?\n\n> «Мы уплывём к тому мрачному рифу в море и нырнём сквозь чёрные бездны к циклопическому, многоколонному Й’ха-нтлею, и в этом логове Глубоководных будем жить среди чудес и славы вечно». —Г.Ф. Лавкрафт, «Тень над Иннсмутом»",
    )
    text = text.replace(
        "Эта поддержка имела свою цену, и члены ордена были вынуждены принести три клятвы: Первая клятва: «Iä! Dagon! Я, (имя говорящего), торжественно клянусь, что не буду ни вмешиваться в, ни доносить о действиях глубоководные. Iä! Dagon!» Вторая клятва: «Iä! Dagon! Я, (имя говорящего), торжественно клянусь, что, если меня об этом попросят, я окажу помощь глубоководные в меру всех своих сил и в той форме или тем способом, которые от меня потребуются. Iä! Dagon!» Третья клятва: «Iä! Dagon! Я, (имя говорящего), торжественно клянусь, что беру это существо [глубоководный] себе в жёны/мужья, что приведу его в свой дом и что вместе с ним постараюсь зачать и вырастить детей, чтобы раса и вера могли продолжать процветать. Iä! Dagon! Iä! Hydra!» Так, с третьей клятвой, появились Гибриды - потомство союза глубоководный и человека.",
        "Эта поддержка имела свою цену, и члены ордена были вынуждены принести три клятвы:\n\n> Первая клятва: «Iä! Dagon! Я, (имя говорящего), торжественно клянусь, что не буду ни вмешиваться в, ни доносить о действиях глубоководные. Iä! Dagon!»\n>\n> Вторая клятва: «Iä! Dagon! Я, (имя говорящего), торжественно клянусь, что, если меня об этом попросят, я окажу помощь глубоководные в меру всех своих сил и в той форме или тем способом, которые от меня потребуются. Iä! Dagon!»\n>\n> Третья клятва: «Iä! Dagon! Я, (имя говорящего), торжественно клянусь, что беру это существо [глубоководный] себе в жёны/мужья, что приведу его в свой дом и что вместе с ним постараюсь зачать и вырастить детей, чтобы раса и вера могли продолжать процветать. Iä! Dagon! Iä! Hydra!»\n\nТак, с третьей клятвой, появились Гибриды - потомство союза глубоководный и человека.",
    )
    text = text.replace(
        "Начинается медленное песнопение. Сначала его можно услышать от тех, кто ближе всего к Эзотерическому Ордену Дагона. А затем оно постепенно перекатывается по всему Иннсмуту. “Ph’nglui mglw’nafh Cthulhu R’lyeh wgah’nagl fhtagn Iä! Iä! Cthulhu fhtagn” Если сыщики продолжают смотреть, клубящиеся тучи над мелким рифом за пределами гавани Иннсмута становятся все гуще и гуще.",
        "Начинается медленное песнопение. Сначала его можно услышать от тех, кто ближе всего к Эзотерическому Ордену Дагона. А затем оно постепенно перекатывается по всему Иннсмуту.\n\n> “Ph’nglui mglw’nafh Cthulhu R’lyeh wgah’nagl fhtagn Iä! Iä! Cthulhu fhtagn”\n\nЕсли сыщики продолжают смотреть, клубящиеся тучи над мелким рифом за пределами гавани Иннсмута становятся все гуще и гуще.",
    )
    text = text.replace(
        "«Ты ведь всегда хотел попасть на киноэкран, правда? Я знаю, хотел, парень. Это твой великий момент, твой час сиять. Ты станешь кинозвездой. Возьми это...» Он вручает сыщику пакетик антацида Tum-Eez. «...беги по этому щупальцу и брось ему в пасть. Оно его перегрузит и отправит обратно в водяную могилу».",
        "> «Ты ведь всегда хотел попасть на киноэкран, правда? Я знаю, хотел, парень. Это твой великий момент, твой час сиять. Ты станешь кинозвездой. Возьми это...»\n\nОн вручает сыщику пакетик антацида Tum-Eez.\n\n> «...беги по этому щупальцу и брось ему в пасть. Оно его перегрузит и отправит обратно в водяную могилу».",
    )
    text = text.replace(
        "«Ты ведь всегда хотел попасть на киноэкран, правда? Я знаю, хотел, парень...»",
        "> «Ты ведь всегда хотел попасть на киноэкран, правда? Я знаю, хотел, парень...»",
    )
    text = text.replace(" DEX ", " ЛВК ").replace(" CON ", " ТЕЛ ").replace(" SIZ ", " РАЗМ ")
    text = text.replace(" POW ", " МОЩ ").replace(" SAN ", " РАСС ")
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, {
        "flow": flow_stats,
        "list_wrap": list_wrap_stats,
        "list_continuation": list_continuation_stats,
        "tables_transformed": int(table1) + int(table2),
        "table_1_transformed": table1,
        "table_2_transformed": table2,
        "keeper_note_callouts": len(re.findall(r"callout-class:\s*keeper-note", text)),
    }


def _split_once_required(text: str, marker: str) -> tuple[str, str] | None:
    if marker not in text:
        return None
    before, after = text.split(marker, 1)
    return before, marker + after


def _strip_adjacent_duplicate_heading_label(section: str, heading: str) -> str:
    label = heading.lstrip("#").strip()
    return re.sub(rf"({re.escape(heading)}\n+){re.escape(label)}\n+", r"\1", section, count=1)


def repair_confirmed_column_order(text: str) -> tuple[str, dict[str, object]]:
    """Repair source pages where OCR merged two columns right-before-left.

    These are page-specific publication projection repairs backed by PDF column
    coordinates. They do not change the accepted RU master; they restore the
    reader order for Keeper/HTML assembly.
    """
    repaired_pages: list[str] = []
    rebuilt_blocks: list[str] = []
    for page, block in page_blocks(text):
        if not page:
            rebuilt_blocks.append(block)
            continue
        original = block
        if page == "009":
            split = _split_once_required(block, "### Анна Диас") or _split_once_required(block, "### Anna Díaz")
            if split:
                christopher, anna = split
                marker = "<!-- source-page-009 -->"
                prefix = marker + "\n\n" if christopher.startswith(marker) else ""
                christopher = christopher.replace(marker, "", 1).strip()
                block = prefix + anna.strip() + "\n\n" + christopher.strip() + "\n"
        elif page == "012":
            split = _split_once_required(block, "- При успешном броске Археологии")
            if split:
                arkham_head, orne_and_tail = split
                note_marker = "> <!-- callout-class: keeper-note -->\n> **Примечание Хранителю.** если сыщики уже встречали Karen раньше"
                split_note = _split_once_required(orne_and_tail, note_marker)
                if split_note:
                    orne_continuation, karen_note = split_note
                    marker = "<!-- source-page-012 -->"
                    prefix = marker + "\n\n" if arkham_head.startswith(marker) else ""
                    arkham_head = arkham_head.replace(marker, "", 1).strip()
                    block = (
                        prefix
                        + orne_continuation.strip()
                        + "\n\n"
                        + arkham_head
                        + "\n\n"
                        + karen_note.strip()
                        + "\n"
                    )
        elif page == "015":
            split = _split_once_required(block, "#### Прибытие: практическая справка")
            if split:
                innsmouth_and_arrival, arrival_reference = split
                marker = "<!-- source-page-015 -->"
                page_prefix = marker + "\n\n" if innsmouth_and_arrival.startswith(marker) else ""
                innsmouth_and_arrival = innsmouth_and_arrival.replace(marker, "", 1).strip()
                arrival_heading = "### Прибытие"
                arrival_pos = innsmouth_and_arrival.find(arrival_heading)
                if arrival_pos >= 0:
                    innsmouth_prefix = innsmouth_and_arrival[:arrival_pos].strip()
                    arrival_section = innsmouth_and_arrival[arrival_pos:].strip()
                    arrival_body = arrival_section[len(arrival_heading) :].strip()
                    block = (
                        page_prefix
                        + innsmouth_prefix
                        + "\n\n"
                        + arrival_heading
                        + "\n\n"
                        + arrival_reference.strip()
                        + "\n\n"
                        + arrival_body
                        + "\n"
                    )
                    block = re.sub(r"\n{3,}", "\n\n", block).strip() + "\n"
        elif page == "017":
            split = _split_once_required(block, "### Кабинет продюсера")
            if split:
                investigation_head, producer_section = split
                producer_section = _strip_adjacent_duplicate_heading_label(producer_section, "### Кабинет продюсера")
                marker = "<!-- source-page-017 -->"
                head_and_misplaced = investigation_head.replace(marker, "", 1).strip()
                heading = "## Расследование"
                misplaced_prefix = head_and_misplaced.replace(heading, "", 1).strip()
                block = (
                    marker
                    + "\n\n"
                    + heading
                    + "\n\n"
                    + producer_section.strip()
                    + "\n\n"
                    + misplaced_prefix
                    + "\n"
                )
                block = re.sub(r"\n{3,}", "\n\n", block).strip() + "\n"
        elif page == "018":
            block = re.sub(
                r"\s+ВОКРУГ ПОЕЗДА\s+",
                "\n\n### Вокруг поезда\n\n",
                block,
                count=1,
            )
            block = re.sub(
                r"(переходя из трейлера в трейлер\.)\s+(?:Bazzledon[’']s Office|Кабинет Баззлдона|Кабинет Bazzledon)\s+",
                r"\1\n\n### Bazzledon’s Office\n\n",
                block,
                count=1,
            )
            split = _split_once_required(block, "### Вокруг поезда")
            if split:
                misplaced_prefix, main_section = split
                marker = "<!-- source-page-018 -->"
                misplaced_prefix = misplaced_prefix.replace(marker, "", 1).strip()
                insert_after = "Оно от человека по имени «Толстяк Тони», который вежливо объясняет Bazzledon, что Толстяк Тони знает: Bazzledon перебрался в Arkham, и если деньги Тони не вернутся в руки Тони до конца месяца, ему придётся предпринять «прискорбные меры», чтобы защитить свои вложения."
                if misplaced_prefix and insert_after in main_section:
                    main_section = main_section.replace(
                        insert_after,
                        insert_after + "\n\n" + misplaced_prefix,
                        1,
                    )
                    block = marker + "\n\n" + main_section.strip() + "\n"
        elif page == "019":
            marker = "<!-- source-page-019 -->"
            page_text = block.replace(marker, "", 1).strip()
            split = (
                _split_once_required(page_text, "В трейлере Ginny светло")
                or _split_once_required(page_text, "В трейлере Джинни светло")
            )
            if split:
                misplaced_tail, trailer_section = split
                misplaced_tail = re.sub(r"^Исследование\s+", "", misplaced_tail.strip())
                trailer_section = "### Ginny’s Trailer\n\n" + trailer_section.strip()
                note_marker = "\n> <!-- callout-class: keeper-note -->"
                if misplaced_tail and note_marker in trailer_section:
                    trailer_section = trailer_section.replace(
                        note_marker,
                        "\n\n" + misplaced_tail + note_marker,
                        1,
                    )
                trailer_section = re.sub(
                    r"\n+\s*Эй, Джи,[\s\S]*?Sammy\s+Раздаточный материал 2: записка\s*$",
                    "",
                    trailer_section,
                    count=1,
                )
                block = marker + "\n\n" + trailer_section.strip() + "\n"
        elif page == "020":
            marker = "<!-- source-page-020 -->"
            page_text = block.replace(marker, "", 1).strip()
            split = _split_once_required(page_text, "### McGuire’s Lab")
            if split:
                before_lab, lab_section = split
                if "### Ginny’s Trailer" in before_lab:
                    block = marker + "\n\n" + lab_section.strip() + "\n"
        elif page == "024":
            split = _split_once_required(block, "### Дом Брюстеров")
            if split:
                misplaced_prefix, main_section = split
                marker = "<!-- source-page-024 -->"
                misplaced_prefix = misplaced_prefix.replace(marker, "", 1).strip()
                insert_after = "Положение его отца оградило его от более уродливых сторон истории города, и он, похоже, находится в мире с тем будущим, которое ждет его под морем, и искренне его предвкушает. А почему бы и нет? Его жизнь в городе всегда была прекрасной, а недавние контакты с обычными людьми оказались довольно неприятными, еще сильнее укрепив его собственную преданность."
                if misplaced_prefix and insert_after in main_section:
                    main_section = main_section.replace(
                        insert_after,
                        insert_after + "\n\n" + misplaced_prefix,
                        1,
                    )
                    block = marker + "\n\n" + main_section.strip() + "\n"
        if block != original:
            repaired_pages.append(page)
        rebuilt_blocks.append(block.strip())
    return "\n\n".join(rebuilt_blocks).strip() + "\n", {
        "repaired_pages": repaired_pages,
        "repairs": len(repaired_pages),
    }


def _heading_section_span(lines: list[str], heading_index: int) -> tuple[int, int]:
    match = re.match(r"^(#{1,6})\s+", lines[heading_index])
    if not match:
        return heading_index, heading_index + 1
    level = len(match.group(1))
    end = len(lines)
    for index in range(heading_index + 1, len(lines)):
        next_match = re.match(r"^(#{1,6})\s+", lines[index])
        if next_match and len(next_match.group(1)) <= level:
            end = index
            break
    return heading_index, end


def _find_heading_line(lines: list[str], heading: str, start: int = 0) -> int | None:
    for index in range(start, len(lines)):
        if lines[index].strip() == heading:
            return index
    return None


def _move_heading_section_before(text: str, moving_heading: str, before_heading: str) -> tuple[str, bool]:
    lines = text.splitlines()
    moving_index = _find_heading_line(lines, moving_heading)
    before_index = _find_heading_line(lines, before_heading)
    if moving_index is None or before_index is None or moving_index < before_index:
        return text, False
    start, end = _heading_section_span(lines, moving_index)
    section = lines[start:end]
    del lines[start:end]
    before_index = _find_heading_line(lines, before_heading)
    if before_index is None:
        return text, False
    lines[before_index:before_index] = section
    return "\n".join(lines).strip() + "\n", True


def _move_heading_section_after(text: str, moving_heading: str, after_heading: str) -> tuple[str, bool]:
    lines = text.splitlines()
    moving_index = _find_heading_line(lines, moving_heading)
    after_index = _find_heading_line(lines, after_heading)
    if moving_index is None or after_index is None:
        return text, False
    start, end = _heading_section_span(lines, moving_index)
    section = lines[start:end]
    del lines[start:end]
    after_index = _find_heading_line(lines, after_heading)
    if after_index is None:
        return text, False
    _, insert_at = _heading_section_span(lines, after_index)
    lines[insert_at:insert_at] = section
    return "\n".join(lines).strip() + "\n", True


def _move_section_before_page_marker(text: str, heading: str, page: str) -> tuple[str, bool]:
    """Move a complete heading section before a source-page marker.

    Use this only for reviewed boundary drift where the reader section belongs
    to the previous page flow even if its art/source evidence is from the next
    PDF page.
    """
    lines = text.splitlines()
    heading_index = _find_heading_line(lines, heading)
    marker = f"<!-- source-page-{page} -->"
    marker_index = next((index for index, line in enumerate(lines) if line.strip() == marker), None)
    if heading_index is None or marker_index is None or heading_index < marker_index:
        return text, False
    start, end = _heading_section_span(lines, heading_index)
    section = lines[start:end]
    del lines[start:end]
    marker_index = next((index for index, line in enumerate(lines) if line.strip() == marker), None)
    if marker_index is None:
        return text, False
    lines[marker_index:marker_index] = section + [""]
    return "\n".join(lines).strip() + "\n", True


def enforce_expected_heading_spine(text: str) -> tuple[str, dict[str, object]]:
    """Move complete sibling sections into the scenario's expected reader order."""
    moves: list[dict[str, object]] = []
    before_pairs = [
        ("### Genevieve ‘Ginny’ Dubois", "### P.A. Bazzledon"),
        ("### Sammy Brewster", "### Второстепенные NPC"),
        ("### Съёмочная группа", "### Второстепенные NPC"),
        ("### Отель «Гилман-хаус»", "### Съёмочный железнодорожный вагон"),
        ("### Bazzledon’s Office", "### Ginny’s Trailer"),
        ("### Железнодорожный вход", "### Система пещер"),
        ("### Эзотерический Орден Дагона", "### Вход через пещеры"),
    ]
    for moving, before in before_pairs:
        text, moved = _move_heading_section_before(text, moving, before)
        if moved:
            moves.append({"move": moving, "before": before})
    after_pairs = [
        ("### Готовые сыщики", "### Patty Gillian"),
    ]
    for moving, after in after_pairs:
        text, moved = _move_heading_section_after(text, moving, after)
        if moved:
            moves.append({"move": moving, "after": after})
    text, moved = _move_section_before_page_marker(text, "### Второстепенные NPC", "011")
    if moved:
        moves.append({"move": "### Второстепенные NPC", "before_page_marker": "011"})
    text, moved = _move_section_before_page_marker(text, "### Съёмочный железнодорожный вагон", "017")
    if moved:
        moves.append({"move": "### Съёмочный железнодорожный вагон", "before_page_marker": "017"})
    text, moved = _move_section_before_page_marker(text, "### Вход через пещеры", "029")
    if moved:
        moves.append({"move": "### Вход через пещеры", "before_page_marker": "029"})
    return text, {"moves": moves, "move_count": len(moves)}


def project_keeper_source_toc(text: str) -> tuple[str, dict[str, object]]:
    """Replace the OCR-derived source TOC page with the accepted source TOC."""
    def replacer(block: str) -> tuple[str, bool]:
        projected = "\n\n".join(["<!-- source-page-004 -->", "## Содержание", *KEEPER_SOURCE_TOC_ENTRIES]) + "\n"
        return projected, block.strip() != projected.strip()

    projected, changed = _replace_page_block(text, "004", replacer)
    return projected, {
        "changed": changed,
        "entries": len(KEEPER_SOURCE_TOC_ENTRIES),
        "source_page": "004",
    }


def cleanup_confirmed_page_residuals(text: str) -> str:
    """Remove page-specific residuals created by mixed heading/column repairs."""
    text = re.sub(
        r"(?m)(<!-- source-page-006 -->\s*(?:### The Innsmouth Terror\s*)?)"
        r"Информация для Хранителя\s+\d+\s+ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ\s+",
        r"\1Информация для Хранителя\n\n",
        text,
        count=1,
    )
    text = re.sub(
        r"(?m)^РАССЛЕДОВАНИЕ\s*$\n?",
        "",
        text,
    )
    text = re.sub(
        r"(?m)^Расследование\s+(?=### )",
        "",
        text,
    )
    text = re.sub(
        r"\s+РАССЛЕДОВАНИЕ(?=\s*(?:<!-- source-page-|\Z))",
        "",
        text,
    )
    text = re.sub(
        r"(?m)(<!-- source-page-016 -->\s*)Innsmouth\s*\n+(?=\s*### )",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(?m)(<!-- source-page-017 -->[\s\S]*?)\bРасследование\s+(?=Díaz\s+не хочет)",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(?m)(### Пожарная часть[\s\S]*?)\bThe Fire Station\s+(?=Пожарная часть находится)",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(## Информация для Хранителя\s*\n\s*)2\s+(?=Город Инн?смут)",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(<!-- source-page-019 -->[\s\S]*?)"
        r"### Ginny’s Trailer\s+"
        r"Ginny’s Trailer \([\s\S]*?\n\s*\n"
        r"(?=### Ginny’s Trailer)",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(<!-- source-page-019 -->[\s\S]*?)\s+Эй, Джи,[\s\S]*?"
        r"Sammy Раздаточный материал 2: записка(?=\s*<!-- source-page-020 -->)",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(<!-- source-page-043 -->[\s\S]*?### Раздаточный материал 2: записка\s+)"
        r"Раздаточные материалы\s+",
        r"\1",
        text,
        count=1,
    )
    text = re.sub(
        r"(<!-- source-page-043 -->[\s\S]*?Это L L F R F L\.\s+Sammy)\s+"
        r"Раздаточный материал 2: записка \(обычный текст\)[\s\S]*?Это L L F R F L\.\s+Sammy",
        r"\1",
        text,
        count=1,
    )
    return text


def repair_confirmed_heading_boundaries(text: str) -> tuple[str, dict[str, object]]:
    """Repair reviewed heading/page boundary drift without changing body text."""
    repairs: list[dict[str, str]] = []
    new_text, changed = _replace_page_block(
        text,
        "021",
        lambda block: (
            block.replace(
                "### Железнодорожный вход\n\nЕсли сыщики направятся к станции",
                "Если сыщики направятся к станции",
                1,
            ),
            "### Железнодорожный вход\n\nЕсли сыщики направятся к станции" in block,
        ),
    )
    if changed:
        repairs.append({"page": "021", "repair": "remove_premature_railroad_heading"})
        text = new_text

    def page_022(block: str) -> tuple[str, bool]:
        original = block
        block = block.replace(
            "Расследование Вход у железной дороги Груда",
            "### Железнодорожный вход\n\nГруда",
            1,
        )
        block = block.replace(
            "Расследование\nВход у железной дороги\nГруда",
            "### Железнодорожный вход\n\nГруда",
            1,
        )
        return block, block != original

    text, changed = _replace_page_block(text, "022", page_022)
    if changed:
        repairs.append({"page": "022", "repair": "promote_railroad_heading_to_page_022"})
    return text, {"repairs": repairs, "repair_count": len(repairs)}


def cleanup_coc_terms(text: str) -> str:
    """Normalize high-confidence CoC role and mechanics terms in prose."""
    replacements = {
        "Исследователи": "Сыщики",
        "исследователи": "сыщики",
        "Исследователей": "Сыщиков",
        "исследователей": "сыщиков",
        "Исследователям": "Сыщикам",
        "исследователям": "сыщикам",
        "Исследователями": "Сыщиками",
        "исследователями": "сыщиками",
        "Исследователях": "Сыщиках",
        "исследователях": "сыщиках",
        "Исследователь": "Сыщик",
        "исследователь": "сыщик",
        "Исследователя": "Сыщика",
        "исследователя": "сыщика",
        "Исследователю": "Сыщику",
        "исследователю": "сыщику",
        "Исследователем": "Сыщиком",
        "исследователем": "сыщиком",
        "Инсмут": "Иннсмут",
        "Инсмута": "Иннсмута",
        "Инсмуте": "Иннсмуте",
        "Инсмутом": "Иннсмутом",
        "Инсмутский": "Иннсмутский",
        "инсмутский": "иннсмутский",
        "броски Listen": "броски Слуха",
        "бросок Listen": "бросок Слуха",
        "броске Listen": "броске Слуха",
        "броска Listen": "броска Слуха",
        "броски Spot Hidden": "броски Внимательности",
        "бросок Spot Hidden": "бросок Внимательности",
        "броске Spot Hidden": "броске Внимательности",
        "броска Spot Hidden": "броска Внимательности",
        "броска Sanity": "броска Рассудка",
        "бросок Sanity": "бросок Рассудка",
        "броске Sanity": "броске Рассудка",
        "самым низким Luck": "самой низкой Удачей",
        "низким Luck": "низкой Удачей",
        "бросок DEX": "бросок ЛВК",
        "броске DEX": "броске ЛВК",
        "броска DEX": "броска ЛВК",
        "броски DEX": "броски ЛВК",
        "бросок STR": "бросок СИЛ",
        "броске STR": "броске СИЛ",
        "броска STR": "броска СИЛ",
        "броски STR": "броски СИЛ",
        "проверку STR": "проверку СИЛ",
        "суммарный SIZ": "суммарный РАЗМ",
        "его SIZ": "его РАЗМ",
        "бросок Luck": "бросок Удачи",
        "броска Luck": "броска Удачи",
        "броске Luck": "броске Удачи",
        "бросок Drive Auto": "бросок Вождение автомобиля",
        "броска Drive Auto": "броска Вождение автомобиля",
        "броске Drive Auto": "броске Вождение автомобиля",
        "бросок Dodge": "бросок Уклонения",
        "броска Dodge": "броска Уклонения",
        "броске Dodge": "броске Уклонения",
        "Brawl 50%": "Драка 50%",
        "1D3 damage": "1D3 урона",
        "2D4 damage": "2D4 урона",
        "Operate Heavy Machinery": "Управления тяжёлой техникой",
        "Mechanical Repair": "Механического ремонта",
        "Drive Train": "Вождения поезда",
        "Hard Science (Physics)": "Науки (физика)",
        "Jewel": "Драгоценность",
        "The Epic Finale": "Эпический финал",
        "The Esoteric Order of Dagon": "Эзотерический орден Дагона",
        "Society for the Exploration of the Unexplained": "Общество исследования необъяснимого",
        "Star Spawn of Cthulhu": "Звёздное Отродье Ктулху",
        "Star Spawn": "Звёздное Отродье",
        "Deep Ones": "глубоководные",
        "Deep One": "глубоководный",
        "Во времяпервоначального": "Во время первоначального",
        "Рано или поздносыщики": "Рано или поздно сыщики",
        "Разговорс Sammy": "Разговор с Sammy",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = preserve_scenario_title_heading(text)
    text = re.sub(r"(?<!# )\bThe Innsmouth Terror\b", "«Иннсмутский ужас»", text)
    text = re.sub(
        r"9-часовой\s+вечерний\s+автобус\s+до\s+Иннсмута\s+с\s+Дайер-стрит",
        "автобус в Иннсмут в 21:00 с Dyer Street",
        text,
        flags=re.I,
    )
    text = re.sub(r"\bв\s+9\s+вечера\b", "в 21:00", text, flags=re.I)
    return text


def preserve_scenario_title_heading(text: str) -> str:
    """Keep the source scenario title as a heading while allowing prose localization."""
    return re.sub(r"(?m)^(#{1,6})\s+«Иннсмутский ужас»\s*$", r"\1 The Innsmouth Terror", text)


def format_ritual_oath_blocks(text: str) -> str:
    """Restore quote formatting for collapsed first/second/third oath blocks."""
    oath_re = re.compile(
        r"(?P<intro>Эта поддержка имела свою цену, и члены ордена были вынуждены принести три клятвы:)\s+"
        r"(?P<first>Первая клятва:\s*«.*?Iä!\s*Dagon!»)\s+"
        r"(?P<second>Вторая клятва:\s*«.*?Iä!\s*Dagon!»)\s+"
        r"(?P<third>Третья клятва:\s*«.*?Iä!\s*Dagon!\s*Iä!\s*Hydra!»)\s+"
        r"(?P<tail>Так,)",
        re.S,
    )

    def repl(match: re.Match[str]) -> str:
        first = re.sub(r"\s+", " ", match.group("first")).strip()
        second = re.sub(r"\s+", " ", match.group("second")).strip()
        third = re.sub(r"\s+", " ", match.group("third")).strip()
        return (
            f"{match.group('intro')}\n\n"
            f"> {first}\n"
            ">\n"
            f"> {second}\n"
            ">\n"
            f"> {third}\n\n"
            f"{match.group('tail')}"
        )

    return oath_re.sub(repl, text)


VEHICLE_MVR_BLOCK_RE = re.compile(
    r"(?P<prefix>Эпический\s+финал\s+)?"
    r"Паровоз\s+MVR\s+класса\s+B1\s+«Олмстед»\s+"
    r"MOV:\s*(?P<mov>\d+)\s+"
    r"Build:\s*(?P<build>\d+)\s+"
    r"Armour\s+for\s+people:\s*(?P<armour>\d+)\s+"
    r"Ширина\s+колеи:\s*(?P<gauge>.*?)\s+"
    r"Давление\s+в\s+котле:\s*(?P<boiler>.*?)\s+"
    r"Максимальная\s+скорость:\s*(?P<speed>.*?)\s+"
    r"(?P<rule1>Чтобы\s+вести\s+поезд,.*?техникой\.)\s+"
    r"(?P<rule2>Если\s+Build\s+снижается\s+до\s+нуля,.*?игнорируется\.)\s+"
    r"(?P<rule3>Если\s+Build\s+поезда\s+снижается\s+до\s+половины.*?штрафная\s+кость\.)\s+"
    r"(?P<rule4>Если\s+поезд\s+получает\s+за\s+один\s+инцидент.*?Науки\s+\(физика\)\.)\s+"
    r"(?P<rule5>Если\s+же\s+Build\s+поезда\s+снижается\s+до\s+нуля\s+накопленным\s+уроном.*?каждому\s+пассажиру\.)",
    re.S,
)


def project_vehicle_stat_blocks(text: str) -> tuple[str, dict[str, object]]:
    """Promote compact vehicle stat prose into a reproducible Keeper table."""

    records: list[dict[str, object]] = []

    def repl(match: re.Match[str]) -> str:
        records.append(
            {
                "vehicle": "MVR Class B1 Olmstead",
                "source_prefix_removed": bool(match.group("prefix")),
            }
        )
        rows = [
            ("Тип", "Паровоз MVR Class B1 «Olmstead»"),
            ("MOV", match.group("mov")),
            ("Build", match.group("build")),
            ("Armour for people", match.group("armour")),
            ("Ширина колеи", re.sub(r"\s+", " ", match.group("gauge")).strip()),
            ("Давление в котле", re.sub(r"\s+", " ", match.group("boiler")).strip()),
            ("Максимальная скорость", re.sub(r"\s+", " ", match.group("speed")).strip()),
        ]
        table = ["**Паровоз MVR Class B1 «Olmstead»**", "", "| Поле | Значение |", "| --- | --- |"]
        table.extend(f"| {field} | {value} |" for field, value in rows)
        rules = [
            re.sub(r"\s+", " ", match.group(f"rule{index}")).strip()
            for index in range(1, 6)
        ]
        return "\n".join(table) + "\n\n" + "\n\n".join(rules)

    projected = VEHICLE_MVR_BLOCK_RE.sub(repl, text)
    return projected, {
        "schema": "innsmouth_vehicle_statblock_projection.v1",
        "count": len(records),
        "records": records,
    }


def _replace_page_block(text: str, page: str, replacer: Callable[[str], tuple[str, bool]]) -> tuple[str, bool]:
    marker = f"<!-- source-page-{page} -->"
    start = text.find(marker)
    if start == -1:
        return text, False
    next_match = re.search(r"<!--\s*source-page-\d{3}\s*-->", text[start + len(marker) :])
    end = start + len(marker) + next_match.start() if next_match else len(text)
    block = text[start:end]
    new_block, changed = replacer(block)
    if not changed:
        return text, False
    return text[:start] + new_block.rstrip() + "\n\n" + text[end:].lstrip(), True


def _repair_page_007_order(block: str) -> tuple[str, bool]:
    marker = "<!-- source-page-007 -->"
    heading = "### Вовлечение сыщиков"
    title_label = "THE INNSMOUTH TERROR"
    if marker not in block or heading not in block or title_label not in block:
        return block, False
    original = block
    block = re.sub(r"(?m)^Информация для Хранителя\s+\d+\s*$\n*", "", block)
    before_heading, after_heading = block.split(heading, 1)
    title_match = re.search(rf"\b{re.escape(title_label)}\s+", after_heading)
    if not title_match:
        return original, False
    involvement_text = after_heading[: title_match.start()]
    title_text = after_heading[title_match.end() :]
    art_match = re.search(
        r'<div class="keeper-art-block"[^>]*data-placement-id="xref-00354"[\s\S]*?</div>\s*',
        involvement_text,
    )
    art_block = ""
    if art_match:
        art_block = art_match.group(0).strip()
        art_block = re.sub(r'data-anchor-id="[^"]+"', 'data-anchor-id="the-innsmouth-terror"', art_block)
        involvement_text = involvement_text[: art_match.start()] + involvement_text[art_match.end() :]
    parts = [marker, "### The Innsmouth Terror"]
    if art_block:
        parts.append(art_block)
    parts.append(title_text.strip())
    parts.append(heading)
    parts.append(involvement_text.strip())
    repaired = "\n\n".join(part for part in parts if part.strip()) + "\n"
    return repaired, repaired.strip() != original.strip()


def _repair_page_021_order(block: str) -> tuple[str, bool]:
    heading = "### На съёмочной площадке"
    rail_heading = "### Железнодорожный вход"
    set_marker = "На съемочной площадке Во время"
    rail_sentence = "Если сыщики направятся к станции, они заметят зловеще выглядящую щель между камнями у путей."
    if heading not in block or rail_heading not in block or set_marker not in block:
        return block, False
    before_heading, after_heading = block.split(heading, 1)
    watch_block, after_rail_heading = after_heading.split(rail_heading, 1)
    if rail_sentence not in after_rail_heading:
        return block, False
    after_rail_heading = after_rail_heading.strip()
    after_rail_sentence = after_rail_heading[len(rail_sentence) :].strip()
    if set_marker not in after_rail_sentence:
        return block, False
    set_interactions, set_body = after_rail_sentence.split(set_marker, 1)
    watch_block = watch_block.strip()
    watch_block = re.sub(r"^Исследование\s+", "", watch_block)
    set_body = "Во время " + set_body.strip()
    stage_fright_note = ""
    stage_fright_match = re.search(
        r"\s*Примечание Хранителю:\s*сыщики уже встречались с Ginny во время прохождения Stage Fright\?"
        r"\s*Не беспокойтесь об этом\.\s*Она совершенно их не помнит и обращается с ними точно так же\.",
        set_body,
    )
    if stage_fright_match:
        stage_fright_note = keeper_note_callout(
            "сыщики уже встречались с Ginny во время прохождения Stage Fright? "
            "Не беспокойтесь об этом. Она совершенно их не помнит и обращается с ними точно так же."
        )
        set_body = (set_body[: stage_fright_match.start()] + set_body[stage_fright_match.end() :]).strip()
    new_block = "\n\n".join(
        part.strip()
        for part in [
            before_heading,
            heading,
            set_body,
            watch_block,
            set_interactions,
            stage_fright_note,
            rail_heading,
            rail_sentence,
        ]
        if part.strip()
    )
    return new_block + "\n", True


def _repair_page_012_order(block: str) -> tuple[str, bool]:
    """Move Arkham Advertiser after the Orne Library research continuation."""
    heading = "### Аркхэмский вестник"
    library_marker = "- При успешном броске Археологии"
    if heading not in block or library_marker not in block:
        return block, False
    if block.find(heading) > block.find(library_marker):
        return block, False
    before_heading, after_heading = block.split(heading, 1)
    advertiser_body, library_section = after_heading.split(library_marker, 1)
    library_section = library_marker + library_section
    library_section = re.sub(
        r"(если они понадобятся\.)\s+"
        r"Пользуясь библиотекой Орна,\s+"
        r"сыщики могут выбрать множество разных направлений исследования\.",
        (
            r"\1\n\n"
            "Сыщики могут использовать разные направления исследований "
            "в библиотеке Орна."
        ),
        library_section,
        count=1,
    )
    before_heading = re.sub(r"\s*НАЧАЛО:\s*Аркхэм\s+\d+\s*$", "", before_heading.strip(), flags=re.I)

    karen_note_marker = "Примечание Хранителю: если сыщики уже встречались с Karen раньше"
    karen_note = ""
    if karen_note_marker in library_section:
        library_section, karen_tail = library_section.split(karen_note_marker, 1)
        karen_note = karen_note_marker + karen_tail.strip()
        karen_note = re.sub(r"\s+Karen\s+Джеффрис\s*$", "", karen_note)
        karen_note = "\n".join(
            [
                "> <!-- callout-class: keeper-note -->",
                "> **Примечание Хранителю.** "
                + karen_note.removeprefix("Примечание Хранителю:").strip(),
            ]
        )
        library_section = library_section.rstrip()

    new_block = "\n\n".join(
        part.strip()
        for part in [
            before_heading,
            library_section,
            heading,
            advertiser_body,
            karen_note,
        ]
        if part.strip()
    )
    return new_block + "\n", True


def _repair_page_026_order(block: str) -> tuple[str, bool]:
    """Move the section intro before the General Store body on source page 026."""
    heading = "## В Иннсмут"
    store_heading = "### Универсальный магазин"
    intro_marker = "В ИНСМУТ Рано или поздно"
    if heading not in block or store_heading not in block or intro_marker not in block:
        return block, False
    before_heading, after_heading = block.split(heading, 1)
    before_store, store_body = after_heading.split(store_heading, 1)
    if intro_marker not in store_body:
        return block, False
    store_before_intro, intro = store_body.split(intro_marker, 1)
    intro = "Рано или поздно" + intro.strip()
    intro = re.sub(r"\s+Пит\s*$", "", intro)
    store_before_intro = re.sub(r"\s+Расследование\s+", "\n\n", store_before_intro, count=1)
    store_before_intro = re.sub(r"\bThe General Store\s+The General Store\b", "Универсальный магазин", store_before_intro)
    new_block = "\n\n".join(
        part.strip()
        for part in [
            before_heading,
            heading,
            intro,
            store_heading,
            store_before_intro,
        ]
        if part.strip()
    )
    return new_block + "\n", True


def _repair_page_028_order(block: str) -> tuple[str, bool]:
    original = block
    block = re.sub(
        r"(<!-- source-page-028 -->\s*)Расследование\s+(?=### Эзотерический Орден Дагона)",
        r"\1",
        block,
        count=1,
    )
    block = block.replace(
        "### Эзотерический Орден Дагона\n\n. Стоя",
        "### Эзотерический Орден Дагона\n\nСтоя",
    )
    block = block.replace(
        "### Вход через пещеры\n\nВход через Пещеры Подземный вход",
        "### Вход через пещеры\n\nПодземный вход",
    )
    heading = "### Эзотерический Орден Дагона"
    cave_heading = "### Вход через пещеры"
    tail_marker = "Эзотерический орден Дагона Разговор"
    if heading in block and cave_heading in block and tail_marker in block:
        before_heading, after_heading = block.split(heading, 1)
        order_body, cave_section = after_heading.split(cave_heading, 1)
        cave_body, tail = cave_section.split(tail_marker, 1)
        intro = "Разговор" + tail.strip()
        intro = re.sub(r"\s*Расследование\s*$", "", intro)
        intro = re.sub(
            r"(Хранитель может ее поддержать, направив их)\s+в\s+(?=Стоя на видном месте)",
            r"\1 посетить Эзотерический орден Дагона.\n\n",
            intro,
            count=1,
        )
        block = "\n\n".join(
            part.strip()
            for part in [
                before_heading,
                heading,
                intro,
                order_body,
                cave_heading,
                cave_body,
            ]
            if part.strip()
        ) + "\n"
    return block, block != original


def _repair_page_018_order(block: str) -> tuple[str, bool]:
    """Restore the page-018 office sequence after inline-heading projection.

    The RU master can contain two right-column investigation bullets before the
    left-column "Around the Train" section. Earlier projection also promoted an
    in-sentence trailer reference as if it were the next section heading. Keep
    the repair anchored to structural phrases so minor wording changes do not
    drop the train room links again.
    """
    original = block
    marker = "<!-- source-page-018 -->"

    block = re.sub(
        r"центральная дверь ведет в\s+### Bazzledon[’']s Office",
        (
            "центральная дверь ведет в Ginny’s Trailer (страница 15), "
            "а с дальней стороны устроен небольшой пандус, ведущий в "
            "McGuire’s Lab (страница 16). Все три двери заперты; нужны "
            "ключи или успешный бросок Взлома. Как только сыщики получают "
            "доступ в одно из помещений, выясняется, что стены там тонкие, "
            "как картон, и их можно отогнуть, переходя из трейлера в трейлер.\n\n"
            "### Bazzledon’s Office"
        ),
        block,
        count=1,
    )

    around_heading = "### Вокруг поезда"
    if around_heading in block:
        before_around, around_and_tail = block.split(around_heading, 1)
        misplaced_prefix = before_around.replace(marker, "", 1).strip()
        misplaced_prefix = re.sub(r"^Исследование\s+", "", misplaced_prefix).strip()
        if misplaced_prefix:
            insertion_markers = [
                "- Сыщики, изучающие сценарии",
                "- Любой, кто читает переписку",
            ]
            inserted = False
            for insertion_marker in insertion_markers:
                if insertion_marker in around_and_tail:
                    around_and_tail = around_and_tail.replace(
                        insertion_marker,
                        misplaced_prefix + "\n\n" + insertion_marker,
                        1,
                    )
                    inserted = True
                    break
            if inserted:
                block = marker + "\n\n" + around_heading + around_and_tail

    return block, block != original


def repair_confirmed_intrapage_order(text: str) -> tuple[str, dict[str, object]]:
    """Repair reviewed same-page reading-order drift that survives heading moves."""
    repairs: list[dict[str, str]] = []
    text, changed = _replace_page_block(text, "007", _repair_page_007_order)
    if changed:
        repairs.append({"page": "007", "repair": "the_innsmouth_terror_before_involvement"})
    text, changed = _replace_page_block(text, "012", _repair_page_012_order)
    if changed:
        repairs.append({"page": "012", "repair": "orne_library_before_arkham_advertiser"})
    text, changed = _replace_page_block(text, "021", _repair_page_021_order)
    if changed:
        repairs.append({"page": "021", "repair": "set_description_before_observation_and_interviews"})
    text, changed = _replace_page_block(text, "026", _repair_page_026_order)
    if changed:
        repairs.append({"page": "026", "repair": "section_intro_before_general_store"})
    text, changed = _replace_page_block(text, "028", _repair_page_028_order)
    if changed:
        repairs.append({"page": "028", "repair": "order_intro_before_order_building_and_cave"})
    text, changed = _replace_page_block(text, "018", _repair_page_018_order)
    if changed:
        repairs.append({"page": "018", "repair": "office_investigation_after_fat_tony_and_train_links"})
    return text, {"repairs": repairs, "repair_count": len(repairs)}


def suppress_service_backmatter_text(text: str) -> str:
    """Remove reader-facing service/ad text without dropping page markers or art anchors."""
    out: list[str] = []
    for page, block in page_blocks(text):
        if page not in SERVICE_BACKMATTER_PAGES:
            out.append(block)
            continue
        marker = f"<!-- source-page-{page} -->"
        out.append(f"{marker}\n")
    return "\n".join(part.strip("\n") for part in out if part is not None)


def _normalize_heading_prefix(value: str) -> str:
    normalized = re.sub(r"[^\wА-Яа-яЁё]+", " ", value, flags=re.U).strip().casefold()
    return normalized.replace("аркхэм", "аркхем")


def _strip_repeated_heading_prefix(line: str, heading_text: str) -> tuple[str, bool]:
    stripped_heading = heading_text.strip()
    if not stripped_heading:
        return line, False
    pattern = re.compile(rf"^(?P<prefix>{re.escape(stripped_heading)})(?:\s*[:—–-]\s*|\s+)(?P<body>\S[\s\S]*)$", re.I)
    match = pattern.match(line.strip())
    if not match:
        return line, False
    body = match.group("body").strip()
    if not body:
        return line, False
    return body[:1].upper() + body[1:], True


def strip_heading_prefix_from_first_paragraph(text: str) -> tuple[str, dict[str, object]]:
    """Remove first-paragraph title echoes after headings.

    This preserves the promoted heading as the canonical section title while
    preventing source inline labels from remaining duplicated in reader prose.
    """
    lines = text.splitlines()
    transformed: list[dict[str, object]] = []
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    skip_prefixes = ("#", "<!--", "-", "* ", "+ ", ">", "|", "<")
    index = 0
    while index < len(lines) - 1:
        match = heading_re.match(lines[index].strip())
        if not match:
            index += 1
            continue
        heading_text = match.group(2).strip()
        cursor = index + 1
        while cursor < len(lines) and (not lines[cursor].strip() or lines[cursor].strip().startswith("<!--")):
            cursor += 1
        if cursor >= len(lines):
            break
        candidate = lines[cursor].strip()
        if not candidate or candidate.startswith(skip_prefixes):
            index += 1
            continue
        normalized_heading = _normalize_heading_prefix(heading_text)
        normalized_candidate = _normalize_heading_prefix(candidate[: len(heading_text) + 16])
        if normalized_heading and not normalized_candidate.startswith(normalized_heading):
            index += 1
            continue
        replacement, changed = _strip_repeated_heading_prefix(lines[cursor], heading_text)
        if changed:
            lines[cursor] = replacement
            transformed.append(
                {
                    "heading_line": index + 1,
                    "heading": heading_text,
                    "body_line": cursor + 1,
                    "replacement_prefix": replacement[:80],
                }
            )
        index += 1
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), {
        "transformed": transformed,
        "count": len(transformed),
    }


def validate_reader_master(text: str) -> None:
    findings = [
        f"{match.group('kind').lower()}@line-{text.count(chr(10), 0, match.start()) + 1}"
        for match in FORBIDDEN_READER_MASTER_COMMENT_RE.finditer(text)
    ]
    if findings:
        raise ValueError(
            "E_RU_READER_MASTER_TECHNICAL_COMMENT: " + ", ".join(findings)
        )


def build_keeperbook(text: str, version: str) -> str:
    global LAST_CHARACTER_NAME_REPORT, LAST_PAGE_REFERENCE_REPORT
    validate_reader_master(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = GENERATED_COMMENT_RE.sub("", text)
    text = UNIT_COMMENT_RE.sub("", text)
    text = re.sub(
        rf'^#\s+«Иннсмутский ужас»\s*-\s*Full RU Source {re.escape(version)}\s*$',
        "# Иннсмутский ужас",
        text,
        count=1,
        flags=re.M,
    )
    text = re.sub(
        r"^#\s+The Innsmouth Terror\s*-\s*Source Text Full RU\s*$",
        "# Иннсмутский ужас",
        text,
        count=1,
        flags=re.M,
    )
    seen: set[str] = set()
    text = "\n".join(structure_block(page, block, seen).strip() for page, block in page_blocks(text) if block.strip())
    text, _bullet_report = project_bullets(text)
    text, _plus_report = normalize_plus_lists(text)
    text = re.sub(r"(?m)^-\s*\n(?!\s*(?:#|<!--|-|\*|\+)\b)(\S[^\n]*)$", r"- \1", text)
    if "<!-- source-page-001 -->" not in text:
        text = re.sub(
            r"^# Иннсмутский ужас\s*(?=<!--\s*source-page-002\s*-->)",
            "# Иннсмутский ужас\n\n<!-- source-page-001 -->\n\n",
            text,
            count=1,
            flags=re.M,
        )
    if "<!-- source-page-045 -->" not in text:
        text += "\n<!-- source-page-045 -->\n"
    if "<!-- source-page-046 -->" not in text:
        text += "\n<!-- source-page-046 -->\n"
    text = re.sub(
        rf"(?m)^\*{re.escape(VISUAL_ONLY_PUBLICATION_PLACEHOLDER)}\*\s*$\n?",
        "",
        text,
    )
    text = suppress_service_backmatter_text(text)
    text, _semantic_report = apply_semantic_projection(text)
    text, _column_order_report = repair_confirmed_column_order(text)
    text, LAST_CHARACTER_NAME_REPORT = normalize_character_names(text)
    text, _keeper_source_toc_report = project_keeper_source_toc(text)
    text, _printed_page_report = strip_printed_page_number_residue(text)
    text = text.replace(
        "Если сыщики направятся к станции, они заметят зловеще выглядящую щель между камнями у путей.",
        "### Железнодорожный вход\n\nЕсли сыщики направятся к станции, они заметят зловеще выглядящую щель между камнями у путей.",
    )
    text, _heading_spine_report = enforce_expected_heading_spine(text)
    text = cleanup_confirmed_page_residuals(text)
    text = cleanup_coc_terms(text)
    text, _intrapage_order_report = repair_confirmed_intrapage_order(text)
    text = cleanup_coc_terms(text)
    text = format_ritual_oath_blocks(text)
    text, _keeper_info_report = wrap_keeper_info_sections(text)
    text, _vehicle_statblock_report = project_vehicle_stat_blocks(text)
    text, _heading_boundary_report = repair_confirmed_heading_boundaries(text)
    text, _heading_prefix_report = strip_heading_prefix_from_first_paragraph(text)
    text, LAST_PAGE_REFERENCE_REPORT = link_internal_page_references(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def _base_heading_for_qa(heading: str) -> str:
    if heading.startswith("### "):
        body = heading.removeprefix("### ").strip()
        for base in MAIN_CHARACTER_HEADINGS:
            base_body = base.removeprefix("### ").strip()
            if body == base_body or body.startswith(f"{base_body}, "):
                return base
    return heading


def split_character_metadata_line(line: str) -> tuple[str, str] | None:
    match = CHARACTER_METADATA_LINE_RE.match(line.strip())
    if not match:
        return None
    text = match.group("meta").strip()
    prefix = re.match(r"^(?P<age>\d{1,3}\s+(?:год|года|лет),\s+)(?P<tail>\S[\s\S]*)$", text)
    if not prefix:
        return text, ""
    age_prefix = prefix.group("age")
    words = prefix.group("tail").split()
    role_words: list[str] = []
    body_words: list[str] = []
    for word in words:
        bare = word.strip(".,;:!?»”")
        starts_body = bool(re.match(r"^[A-ZА-ЯЁ]", bare)) and role_words
        if starts_body:
            body_words.append(word)
            continue
        if body_words:
            body_words.append(word)
        else:
            role_words.append(word)
    if not role_words:
        return text, ""
    return age_prefix + " ".join(role_words), " ".join(body_words)


def merge_main_character_heading_metadata(text: str) -> tuple[str, dict[str, object]]:
    lines = text.splitlines()
    merged: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped not in MAIN_CHARACTER_HEADINGS:
            index += 1
            continue

        cursor = index + 1
        while cursor < len(lines) and (
            not lines[cursor].strip()
            or lines[cursor].strip().startswith("<!--")
            or lines[cursor].strip().startswith("<div")
            or lines[cursor].strip().startswith("<img")
            or lines[cursor].strip().startswith("</div")
        ):
            cursor += 1
        if cursor >= len(lines):
            index += 1
            continue
        split = split_character_metadata_line(lines[cursor].strip())
        if not split:
            index += 1
            continue

        meta, remainder = split
        lines[index] = f"{stripped}, {meta}"
        if remainder:
            lines[cursor] = remainder
        else:
            lines.pop(cursor)
        merged.append({"heading_line": index + 1, "heading": stripped, "metadata": meta})
        index += 1
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), {
        "merged": merged,
        "count": len(merged),
    }


def heading_qa(text: str) -> dict[str, object]:
    headings = re.findall(r"^#{1,6}\s+.+$", text, re.M)
    comparable_headings = [_base_heading_for_qa(heading) for heading in headings]
    comparable_text = "\n".join(comparable_headings)
    missing = [heading for heading in EXPECTED_ORDERED_HEADINGS if heading not in comparable_headings]
    out_of_order: list[str] = []
    cursor = 0
    for heading in EXPECTED_ORDERED_HEADINGS:
        pos = comparable_text.find(heading, cursor)
        if pos == -1:
            if heading in missing:
                continue
            out_of_order.append(heading)
            continue
        cursor = pos + len(heading)
    damaged = [
        heading
        for heading in headings
        if any(fragment in heading for fragment in (" К Игре", " Npc", "Железнодорожный Вагон", "Кабинет Продюсера"))
    ]
    residual_title_labels: list[str] = []
    adjacent_duplicate_labels: list[dict[str, object]] = []
    heading_prefix_duplicates: list[dict[str, object]] = []
    heading_tail_residues: list[dict[str, object]] = []
    character_metadata_splits: list[dict[str, object]] = []
    empty_character_bodies: list[dict[str, object]] = []
    wrong_page_headings: list[dict[str, object]] = []
    heading_level_findings: list[dict[str, object]] = []
    lines = text.splitlines()
    configured_labels = set(RESIDUAL_TITLE_LABELS)
    configured_labels.update(LINE_HEADINGS)
    configured_labels.update(LINE_HEADINGS.keys())
    configured_labels.update(INLINE_HEADINGS)
    configured_labels.update(INLINE_HEADINGS.keys())
    for page, block in page_blocks(text):
        if page == "004":
            continue
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                expected_page = EXPECTED_HEADING_PAGES.get(_base_heading_for_qa(stripped))
                if expected_page and page != expected_page:
                    wrong_page_headings.append(
                        {"heading": stripped, "actual_page": page, "expected_page": expected_page}
                    )
                continue
            if not stripped or stripped.startswith("#"):
                continue
            for label in configured_labels:
                if stripped == label:
                    residual_title_labels.append(label)
    for index, line in enumerate(lines[:-1], start=1):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        next_index = index + 1
        while next_index <= len(lines) and not lines[next_index - 1].strip():
            next_index += 1
        if next_index > len(lines):
            continue
        next_line = lines[next_index - 1].strip()
        if next_line.startswith("#") or next_line.startswith("<!--"):
            continue
        heading_text = stripped.lstrip("#").strip()
        if heading_text.casefold() == next_line.casefold() or next_line.casefold() in {
            key.casefold() for key, value in LINE_HEADINGS.items() if value.lstrip("#").strip().casefold() == heading_text.casefold()
        }:
            adjacent_duplicate_labels.append({"heading_line": index, "heading": stripped, "duplicate_line": next_index, "duplicate": next_line})
            continue
        normalized_heading = _normalize_heading_prefix(heading_text)
        normalized_next = _normalize_heading_prefix(next_line[: len(heading_text) + 16])
        if normalized_heading and normalized_next.startswith(normalized_heading):
            heading_prefix_duplicates.append(
                {
                    "heading_line": index,
                    "heading": stripped,
                    "duplicate_line": next_index,
                    "duplicate_prefix": next_line[:120],
                }
            )
        if re.match(r"^[,;:—–-]\s*(?:\d{1,3}\s+лет\b|age\s+\d{1,3}\b)", next_line, re.I):
            heading_tail_residues.append(
                {
                    "heading_line": index,
                    "heading": stripped,
                    "tail_line": next_index,
                    "tail_prefix": next_line[:120],
                }
            )
        base_heading = _base_heading_for_qa(stripped)
        if base_heading in MAIN_CHARACTER_HEADINGS:
            cursor = next_index - 1
            while cursor < len(lines):
                candidate = lines[cursor].strip()
                if not candidate or candidate.startswith(("<!--", "<div", "<img", "</div", "<figure", "</figure")):
                    cursor += 1
                    continue
                if CHARACTER_METADATA_LINE_RE.match(candidate):
                    character_metadata_splits.append(
                        {
                            "heading_line": index,
                            "heading": stripped,
                            "metadata_line": cursor + 1,
                            "metadata": candidate[:160],
                        }
                    )
                break
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        base_heading = _base_heading_for_qa(stripped)
        if base_heading not in MAIN_CHARACTER_HEADINGS:
            continue
        cursor = index
        has_body = False
        while cursor < len(lines):
            candidate = lines[cursor].strip()
            if cursor != index and candidate.startswith("#"):
                break
            cursor += 1
            if (
                not candidate
                or candidate == stripped
                or candidate == base_heading
                or candidate.startswith(("<!--", "<div", "<img", "</div", "<figure", "</figure"))
            ):
                continue
            has_body = True
            break
        if not has_body:
            empty_character_bodies.append({"heading_line": index, "heading": stripped})
    seen_levels: set[int] = set()
    previous_level = 0
    for index, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if not match:
            continue
        level = len(match.group(1))
        if level > 1 and level - previous_level > 1:
            heading_level_findings.append(
                {
                    "line": index,
                    "heading": line.strip(),
                    "code": "heading_level_jump",
                    "previous_level": previous_level,
                    "actual_level": level,
                }
            )
        if level > 1 and (level - 1) not in seen_levels:
            heading_level_findings.append(
                {
                    "line": index,
                    "heading": line.strip(),
                    "code": "missing_parent_heading_level",
                    "missing_parent_level": level - 1,
                    "actual_level": level,
                }
            )
        seen_levels.add(level)
        previous_level = level
    return {
        "status": "pass"
        if not missing
        and not out_of_order
        and not damaged
        and not residual_title_labels
        and not adjacent_duplicate_labels
        and not heading_prefix_duplicates
        and not heading_tail_residues
        and not character_metadata_splits
        and not empty_character_bodies
        and not wrong_page_headings
        and not heading_level_findings
        else "fail",
        "expected_count": len(EXPECTED_ORDERED_HEADINGS),
        "actual_heading_count": len(headings),
        "missing": missing,
        "out_of_order": out_of_order,
        "damaged_title_case": damaged,
        "residual_title_labels": residual_title_labels,
        "adjacent_duplicate_labels": adjacent_duplicate_labels,
        "heading_prefix_duplicates": heading_prefix_duplicates,
        "heading_tail_residues": heading_tail_residues,
        "character_metadata_splits": character_metadata_splits,
        "empty_character_bodies": empty_character_bodies,
        "wrong_page_headings": wrong_page_headings,
        "heading_level_findings": heading_level_findings,
    }


def structural_qa(source_text: str, keeper_text: str) -> dict[str, object]:
    source_bullets = len(re.findall(r"(?m)^•$", source_text))
    source_markdown_items = len(re.findall(r"(?m)^\s*[-*+]\s+\S", source_text))
    expected_source_items = source_bullets + source_markdown_items
    list_items = len(re.findall(r"(?m)^\s*(?:>\s*)?[-*+]\s+\S", keeper_text))
    standalone_bullets = len(re.findall(r"(?m)^•$", keeper_text))
    empty_items = [
        index
        for index, line in enumerate(keeper_text.splitlines(), start=1)
        if re.fullmatch(r"-\s*", line)
    ]
    keeper_lines = keeper_text.splitlines()
    wrapped_list_items = []
    list_continuation_paragraphs = []
    for index, line in enumerate(keeper_lines[:-1], start=1):
        stripped = line.strip()
        next_line = keeper_lines[index].strip()
        if (
            stripped.startswith("- ")
            and next_line
            and not is_structural_line(next_line)
            and not re.search(r'[.;:!?…»)"\]]$', stripped)
        ):
            wrapped_list_items.append({"line": index, "item": stripped, "continuation": next_line})
    keeper_paragraphs = re.split(r"\n{2,}", keeper_text.strip())
    for index, paragraph in enumerate(keeper_paragraphs[1:], start=1):
        previous = keeper_paragraphs[index - 1].strip()
        current = paragraph.strip()
        if (
            previous.lstrip().startswith("- ")
            and CONTINUATION_OBJECT_RE.search(previous)
            and CONTINUATION_PRONOUN_RE.match(current)
        ):
            list_continuation_paragraphs.append(
                {"paragraph": index + 1, "previous": previous[:180], "continuation": current[:180]}
            )
    handout_positions = []
    for heading in HANDOUT_HEADINGS.values():
        pos = keeper_text.find(heading)
        handout_positions.append({"heading": heading, "position": pos})
    handout_missing = [row["heading"] for row in handout_positions if row["position"] < 0]
    handout_out_of_order = []
    cursor = -1
    for row in handout_positions:
        if row["position"] < 0:
            continue
        if row["position"] < cursor:
            handout_out_of_order.append(row["heading"])
        cursor = row["position"]
    appendix_start = keeper_text.find("## Раздаточные материалы")
    appendix_text = keeper_text[appendix_start:] if appendix_start >= 0 else ""
    handout_label_lines = [
        line.strip()
        for line in appendix_text.splitlines()
        if line.strip() in HANDOUT_LABELS
    ]
    table_count = len(re.findall(r"(?m)^\|\s*(?:Когда|1D100)\s*\|", keeper_text))
    source_keeper_notes = len(NOTE_RE.findall(source_text))
    keeper_note_callouts = len(re.findall(r"callout-class:\s*keeper-note", keeper_text))
    keeper_info_callouts = [
        {"sample": match.group(0)[:180]}
        for match in re.finditer(
            r"(?s)>\s*<!--\s*callout-class:\s*keeper-note\s*-->\s*\n>\s*\*\*Информация для Хранителя\.?\*\*",
            keeper_text,
        )
    ]
    long_paragraphs = [
        {"chars": len(part), "sample": part[:180]}
        for part in re.split(r"\n\s*\n", keeper_text)
        if len(part) >= 1800 and not part.lstrip().startswith(("|", "<!--", ">"))
    ]
    visible_visual_only_placeholders = [
        {"line": index, "text": line.strip()}
        for index, line in enumerate(keeper_text.splitlines(), start=1)
        if VISUAL_ONLY_PUBLICATION_PLACEHOLDER in line
    ]
    vehicle_statblock_count = len(re.findall(r"^\*\*Паровоз\s+MVR\s+Class\s+B1\s+«Olmstead»\*\*\s*$", keeper_text, re.M))
    printed_page_residues = printed_page_number_residues(keeper_text)
    findings = []
    if expected_source_items != list_items:
        findings.append(
            {
                "code": "list_item_count_mismatch",
                "source_bullets": source_bullets,
                "source_markdown_items": source_markdown_items,
                "expected_source_items": expected_source_items,
                "keeper_list_items": list_items,
            }
        )
    if standalone_bullets:
        findings.append({"code": "standalone_bullet_lines", "count": standalone_bullets})
    if empty_items:
        findings.append({"code": "empty_list_items", "lines": empty_items})
    if wrapped_list_items:
        findings.append({"code": "wrapped_list_item_continuations", "items": wrapped_list_items[:12]})
    if list_continuation_paragraphs:
        findings.append({"code": "list_item_continuation_paragraphs", "items": list_continuation_paragraphs[:12]})
    if handout_missing:
        findings.append({"code": "missing_handout_headings", "headings": handout_missing})
    if handout_out_of_order:
        findings.append({"code": "handout_headings_out_of_order", "headings": handout_out_of_order})
    if handout_label_lines:
        findings.append({"code": "unheaded_handout_labels", "labels": handout_label_lines})
    if table_count < 2:
        findings.append({"code": "scenario_tables_missing", "expected_min": 2, "actual": table_count})
    if keeper_note_callouts < source_keeper_notes:
        findings.append(
            {
                "code": "keeper_note_callout_count_mismatch",
                "expected": source_keeper_notes,
                "actual": keeper_note_callouts,
            }
        )
    if keeper_info_callouts:
        findings.append(
            {
                "code": "keeper_info_section_rendered_as_callout",
                "items": keeper_info_callouts,
            }
        )
    if long_paragraphs:
        findings.append({"code": "long_paragraphs_after_flow_projection", "paragraphs": long_paragraphs[:8]})
    if visible_visual_only_placeholders:
        findings.append(
            {
                "code": "visible_visual_only_publication_placeholder",
                "items": visible_visual_only_placeholders[:8],
            }
        )
    if printed_page_residues:
        findings.append(
            {
                "code": "printed_page_number_residue",
                "items": printed_page_residues[:12],
                "count": len(printed_page_residues),
            }
        )
    if "Паровоз MVR" in keeper_text and vehicle_statblock_count != 1:
        findings.append(
            {
                "code": "vehicle_statblock_projection_missing",
                "expected": 1,
                "actual": vehicle_statblock_count,
            }
        )
    return {
        "status": "pass" if not findings else "fail",
        "source_bullet_markers": source_bullets,
        "source_markdown_items": source_markdown_items,
        "expected_source_items": expected_source_items,
        "markdown_list_items": list_items,
        "standalone_bullet_lines": standalone_bullets,
        "empty_list_item_lines": empty_items,
        "wrapped_list_item_continuations": wrapped_list_items,
        "list_item_continuation_paragraphs": list_continuation_paragraphs,
        "handout_headings": handout_positions,
        "unheaded_handout_labels": handout_label_lines,
        "scenario_tables": table_count,
        "source_keeper_notes": source_keeper_notes,
        "keeper_note_callouts": keeper_note_callouts,
        "keeper_info_callouts": keeper_info_callouts,
        "long_paragraphs_1800": long_paragraphs,
        "visible_visual_only_publication_placeholders": visible_visual_only_placeholders,
        "printed_page_number_residues": printed_page_residues,
        "vehicle_statblocks": vehicle_statblock_count,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v1")
    parser.add_argument("--qa-root", default="project/QA")
    parser.add_argument("--ru-master", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--art-manifest", type=Path)
    parser.add_argument("--source-art-anchor-manifest", type=Path)
    args = parser.parse_args()

    qa = Path(args.qa_root)
    if not qa.is_absolute():
        qa = PROJECT / qa
    source = args.ru_master or PROJECT / "Formatted" / f"The_Innsmouth_Terror_Source_Text_Full_RU_{args.version}.md"
    target = args.out or OUTPUT / "For_Keeper" / f"KeeperBook_{args.version}.md"
    report_path = args.report or qa / "keeperbook_assembly_report.json"
    art_manifest = args.art_manifest or qa / "art_manifest.json"
    source_art_anchor_manifest = args.source_art_anchor_manifest or qa / "art_anchor_manifest.json"

    source_text = source.read_text(encoding="utf-8")
    keeper_text = build_keeperbook(source_text, args.version)
    keeper_text, reader_art_report = inject_reader_art_blocks(keeper_text, art_manifest, source_art_anchor_manifest)
    keeper_text = cleanup_reader_art_page_marker_residuals(keeper_text)
    keeper_text, heading_metadata_report = merge_main_character_heading_metadata(keeper_text)
    keeper_text, final_printed_page_cleanup_report = strip_printed_page_number_residue(keeper_text)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(keeper_text, encoding="utf-8", newline="\n")

    heading_report = heading_qa(keeper_text)
    structure_report = structural_qa(source_text, keeper_text)
    report = {
        "schema": "innsmouth_keeperbook_assembly.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": source.as_posix(),
        "target": target.as_posix(),
        "source_sha256": sha256_bytes(source),
        "target_sha256": sha256_bytes(target),
        "counts": {
            "source_pages": len(re.findall(r"<!--\s*source-page-\d{3}\s*-->", keeper_text)),
            "headings": len(re.findall(r"^#{1,6}\s+", keeper_text, re.M)),
            "markdown_list_items": len(re.findall(r"(?m)^\s*[-*+]\s+\S", keeper_text)),
            "blockquote_markdown_list_items": len(re.findall(r"(?m)^\s*>\s*[-*+]\s+\S", keeper_text)),
            "standalone_bullet_lines": len(re.findall(r"(?m)^•$", keeper_text)),
            "unit_comments_visible": len(re.findall(r"unit-id:", keeper_text)),
            "generated_comments_visible": len(re.findall(r"generated-by:|source-en-sha256:", keeper_text)),
            "non_page_comments_visible": len(
                [
                    comment
                    for comment in re.findall(r"<!--[\s\S]*?-->", keeper_text)
                    if not SOURCE_PAGE_RE.fullmatch(comment.strip())
                ]
            ),
            "bytes": len(keeper_text.encode("utf-8")),
            "visual_only_markers_added": len(re.findall(r"source-page-(?:001|045|046)", keeper_text)),
            "scenario_tables": len(re.findall(r"(?m)^\|\s*(?:Когда|1D100)\s*\|", keeper_text)),
            "keeper_note_callouts": len(re.findall(r"callout-class:\s*keeper-note", keeper_text)),
        },
        "heading_qa": heading_report,
        "structural_qa": structure_report,
        "reader_art_blocks": reader_art_report,
        "main_character_heading_metadata": heading_metadata_report,
        "final_printed_page_cleanup": final_printed_page_cleanup_report,
        "character_name_normalization": LAST_CHARACTER_NAME_REPORT,
        "page_reference_links": LAST_PAGE_REFERENCE_REPORT,
        "status": "pass"
        if heading_report["status"] == "pass"
        and structure_report["status"] == "pass"
        and LAST_PAGE_REFERENCE_REPORT.get("status") == "pass"
        else "fail",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "status={status} pages={pages} headings={headings} bytes={bytes} target={target}".format(
            status=report["status"],
            pages=report["counts"]["source_pages"],
            headings=report["counts"]["headings"],
            bytes=report["counts"]["bytes"],
            target=target,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
