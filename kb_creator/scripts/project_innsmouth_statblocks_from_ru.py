from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_PAGE_RE = re.compile(r"<!--\s*source-page-(\d{3})\s*-->")
PREGEN_STATBLOCK_HEADING_IDS = {
    "hugo-shrimpy-hargreaves",
    "patty-gillian",
    "ian-torres",
    "tiffany-quispe",
    "margaret-maggie-myers",
}


@dataclass(frozen=True)
class CardStart:
    card_id: str
    display_name: str
    patterns: tuple[str, ...]
    group: str


CARD_STARTS: tuple[CardStart, ...] = (
    CardStart("statblock-004", "Diane Loring", ("Дайана Лоринг",), "Жители Аркхэма"),
    CardStart("statblock-005", "Dr. Henry Armitage", ("Доктор Генри Армитидж",), "Жители Аркхэма"),
    CardStart("statblock-006", "Karen Jeffries", ("Карен Джеффрис",), "Жители Аркхэма"),
    CardStart("statblock-001", "Franc Turner", ("Фрэнк Тёрнер",), "Жители Аркхэма"),
    CardStart("statblock-002", "Genevieve ‘Ginny’ Dubois", ("Женевьева «Джинни» Дюбуа",), "Съёмочная группа"),
    CardStart("statblock-003", "Anna Díaz", ("Анна Диас",), "Съёмочная группа"),
    CardStart("statblock-010", "P.A. Bazzledon", ("П.А. Баззледон", "П.А. Баззлдон"), "Съёмочная группа"),
    CardStart("statblock-011", "Christopher McGuire", ("Кристофер Макгуайр",), "Съёмочная группа"),
    CardStart("statblock-012", "Average Crew Member", ("Средний член команды",), "Съёмочная группа"),
    CardStart("statblock-007", "Sammy Brewster", ("Сэмми Брюстер",), "Жители Иннсмута"),
    CardStart("statblock-008", "Jeremiah Brewster", ("Джеремайя Брюстер", "Иеремия Брюстер"), "Жители Иннсмута"),
    CardStart("statblock-009", "Zadok Allen", ("Задок Аллен",), "Жители Иннсмута"),
    CardStart("statblock-015", "Average Human Resident", ("Средний житель-человек",), "Жители Иннсмута"),
    CardStart("statblock-016", "Average Hybrid Resident", ("Средний житель-гибрид",), "Жители Иннсмута"),
    CardStart("statblock-017", "Shoggoth", ("Шоггот",), "Монстры"),
    CardStart("statblock-013", "Star Spawn of Cthulhu", ("Звёздное Отродье Ктулху",), "Монстры"),
    CardStart("statblock-014", "Deep One", ("Глубоководный",), "Монстры"),
    CardStart("statblock-018", "Hugo ‘Shrimpy’ Hargreaves", ("ХЬЮГО «КРЕВЕТКА» ХАРГРИВЗ", "Хьюго «Креветка» Харгривз"), "Готовые сыщики"),
    CardStart("statblock-019", "Patty Gillian", ("ПЭТТИ ГИЛЛИАН", "Пэтти Гиллиан"), "Готовые сыщики"),
    CardStart("statblock-020", "Ian Torres", ("ИАН ТОРРЕС", "Иан Торрес", "Иэн Торрес"), "Готовые сыщики"),
    CardStart("statblock-021", "Tiffany Quispe", ("ТИФФАНИ КИСПЕ", "Тиффани Киспе"), "Готовые сыщики"),
    CardStart(
        "statblock-022",
        "Margaret ‘Maggie’ Myers",
        ("МАРГАРЕТ «МЭГГИ» МАЙЕРС", "МАРГАРЕТ «МАГГИ» МАЙЕРС", "Маргарет «Мэгги» Майерс", "Маргарет «Магги» Майерс"),
        "Готовые сыщики",
    ),
)

CORE_LABELS: dict[str, tuple[str, ...]] = {
    "STR": ("STR", "СИЛ"),
    "CON": ("CON", "ТЕЛ"),
    "SIZ": ("SIZ", "РАЗМ", "РАЗ"),
    "DEX": ("DEX", "ЛОВ", "ЛВК"),
    "INT": ("INT", "ИНТ"),
    "APP": ("APP", "ВНЕ", "ВНЕШ"),
    "POW": ("POW", "МОЩ"),
    "EDU": ("EDU", "ОБР"),
    "SAN": ("SAN", "РАСС"),
}
CORE_HEADERS_RU = ["СИЛ", "ТЕЛ", "РАЗМ", "ЛВК", "ИНТ", "ВНЕШ", "МОЩ", "ОБР", "РАСС"]
DERIVED_HEADERS_RU = ["ЗД", "БМ", "Телосложение", "Движение", "МЗ", "Удача"]
SECTION_LABELS = {"Бой", "Навыки", "Заклинания", "Рассудок", "Предыстория"}
STATBLOCK_NAV_LINES = {
    "персонажи и монстры",
    "персонажи и чудовища",
    "жители иннсмута",
    "жители аркхэма",
    "съемочная группа",
    "съёмочная группа",
    "монстры",
    "готовые сыщики",
    "заранее созданные сыщики",
}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def slugify(text: str) -> str:
    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    text = "".join(mapping.get(ch, ch) for ch in text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "section"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def numeric(value: str) -> str:
    value = value.strip().replace("О", "0").replace("о", "0")
    return value


def matching_start(line: str) -> CardStart | None:
    stripped = line.strip()
    for spec in CARD_STARTS:
        for pattern in spec.patterns:
            if stripped == pattern or stripped.startswith(f"{pattern},"):
                return spec
    return None


def english_patterns(spec: CardStart) -> tuple[str, ...]:
    patterns = [spec.display_name]
    if spec.display_name == "P.A. Bazzledon":
        patterns.append("P.A Bazzledon")
    return tuple(patterns)


def matching_english_start(line: str) -> CardStart | None:
    stripped = line.strip()
    for spec in CARD_STARTS:
        for pattern in english_patterns(spec):
            if stripped == pattern or stripped.startswith(f"{pattern},"):
                return spec
    return None


def extract_statblock_lines(source_text: str) -> tuple[dict[str, list[str]], dict[str, str], list[dict[str, Any]]]:
    lines = source_text.splitlines()
    in_range = False
    current: CardStart | None = None
    current_page: str | None = None
    blocks: dict[str, list[str]] = {}
    block_pages: dict[str, str] = {}
    findings: list[dict[str, Any]] = []

    for line in lines:
        page = SOURCE_PAGE_RE.fullmatch(line.strip())
        if page:
            page_id = page.group(1)
            current_page = page_id
            in_range = "033" <= page_id <= "040"
            if not in_range:
                current = None
            continue
        if not in_range:
            continue
        stripped = line.strip()
        start = matching_start(stripped)
        if start:
            current = start
            blocks[start.card_id] = [stripped]
            if current_page:
                block_pages[start.card_id] = current_page
            continue
        if current:
            blocks[current.card_id].append(line.rstrip())

    for spec in CARD_STARTS:
        if spec.card_id not in blocks:
            findings.append({"severity": "blocker", "code": "missing_statblock_source", "card_id": spec.card_id, "name": spec.display_name})
    return blocks, block_pages, findings


def extract_pdf_statblock_lines(source_pdf: Path | None) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    if source_pdf is None:
        return {}, []
    findings: list[dict[str, Any]] = []
    if not source_pdf.exists():
        return {}, [{"severity": "blocker", "code": "source_pdf_not_found", "path": str(source_pdf)}]
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return {}, [{"severity": "blocker", "code": "pymupdf_unavailable", "detail": str(exc)}]

    blocks: dict[str, list[str]] = {}
    current: CardStart | None = None
    try:
        with fitz.open(source_pdf) as doc:
            max_index = min(len(doc), 40)
            for page_index in range(32, max_index):
                for line in doc[page_index].get_text("text").splitlines():
                    stripped = line.strip()
                    start = matching_english_start(stripped)
                    if start:
                        current = start
                        blocks[start.card_id] = [stripped]
                        continue
                    if current:
                        blocks[current.card_id].append(line.rstrip())
    except Exception as exc:  # pragma: no cover - PDF/runtime dependent
        return blocks, [{"severity": "blocker", "code": "source_pdf_statblock_extract_failed", "detail": str(exc)}]

    return blocks, findings


def clean_statblock_source_line(line: str) -> str:
    value = re.sub(r"<!--\s*unit-id:[\s\S]*?-->", " ", line)
    value = re.sub(r"<!--[\s\S]*?-->", " ", value)
    value = re.sub(r"^#+\s*", "", value.strip())
    value = norm(value)
    if value.casefold().strip(" .:;") in STATBLOCK_NAV_LINES:
        return ""
    return value


def nonempty(lines: list[str]) -> list[str]:
    cleaned = [clean_statblock_source_line(line) for line in lines]
    return [line for line in cleaned if line]


def stat_line(line: str) -> bool:
    value = norm(line)
    label_pattern = "|".join(re.escape(alias) for aliases in CORE_LABELS.values() for alias in aliases)
    return re.match(rf"^(?:{label_pattern})\s+[0-9oO—–-]+$", value, re.I) is not None


def derived_line(line: str) -> bool:
    value = norm(line)
    return bool(
        re.match(r"^(?:HP|ЗД)\s*:?\s*[0-9oO—–-]+$", value, re.I)
        or re.match(r"^(?:DB|БУ|БМ|Бонус к урону)\s*:?\s*(?:[0-9oO]+D[0-9oO]+|[0-9oO—–-]+)$", value, re.I)
        or re.search(r"(?:Телосложение|Build|Передвижение|Move|MP|МЗ|Удача)\s*:", value, re.I)
    )


def first_stat_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if stat_line(line) or derived_line(line):
            return index
    return 1


def extract_core(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for canonical, aliases in CORE_LABELS.items():
        alternatives = "|".join(re.escape(alias) for alias in aliases)
        match = re.search(rf"(?<!\w)(?:{alternatives})\s*:?\s*([0-9oO]+|[—–-])", text, re.I)
        if match:
            result[canonical] = numeric(match.group(1))
    return result


def extract_derived(text: str) -> dict[str, str]:
    patterns = {
        "HP": r"(?<!\w)(?:HP|ЗД)\s*:?\s*([0-9oO]+|[—–-])",
        "DB": r"(?<!\w)(?:DB|БУ|БМ|Бонус к урону)\s*:?\s*([0-9oO]+D[0-9oO]+|[0-9oO]+|[—–-])",
        "Телосложение": r"(?:Телосложение|Build)\s*:?\s*([0-9oO]+|[—–-])",
        "Движение": r"(?:Передвижение|Движение|Move)\s*:?\s*([0-9oO]+|[—–-])",
        "MP": r"(?<!\w)(?:MP|МЗ)\s*:?\s*([0-9oO]+|[—–-])",
        "Удача": r"Удача\s*:?\s*(\([^)]+\)x5|[0-9oO]+|[—–-])",
    }
    result: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.I)
        if match:
            result[key] = numeric(match.group(1))
    return result


def append_joined(items: list[str], text: str) -> None:
    value = norm(text)
    if value:
        items.append(value)


def classify_body(lines: list[str]) -> dict[str, list[str]]:
    sections = {"combat": [], "skills_or_notes": [], "spells": [], "background": []}
    current: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if stat_line(line) or derived_line(line):
            index += 1
            continue
        if line in {"Бой", "Навыки", "Заклинания", "Предыстория"}:
            current = {"Бой": "combat", "Навыки": "skills_or_notes", "Заклинания": "spells", "Предыстория": "background"}[line]
            index += 1
            continue
        if line == "Рассудок":
            current = "skills_or_notes"
            if index + 1 < len(lines):
                append_joined(sections[current], "Рассудок: " + lines[index + 1].strip())
                index += 2
                continue
            index += 1
            continue
        if current is None:
            index += 1
            continue

        if current in {"combat", "skills_or_notes"} and index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if re.match(r"^\d{1,3}%\s*\([^)]+\)(?:[,.;]\s*.*)?$", next_line):
                append_joined(sections[current], f"{line} {next_line}")
                index += 2
                continue

        buffer = [line]
        index += 1
        while index < len(lines):
            peek = lines[index].strip()
            if not peek:
                index += 1
                continue
            if peek in SECTION_LABELS or matching_start(peek) or stat_line(peek) or derived_line(peek):
                break
            if current in {"combat", "skills_or_notes"} and re.match(r"^\d{1,3}%\s*\([^)]+\)", peek):
                break
            buffer.append(peek)
            index += 1
            if current in {"combat", "skills_or_notes"} and re.search(r"[.;:]$", buffer[-1]):
                break
        append_joined(sections[current], " ".join(buffer))
    return normalize_sections(sections)


def normalize_sections(sections: dict[str, list[str]]) -> dict[str, list[str]]:
    for section, labels in {
        "combat": {"бой"},
        "skills_or_notes": {"навыки", "навыки / заметки"},
        "spells": {"заклинания"},
        "background": {"предыстория"},
    }.items():
        sections[section] = [item for item in sections[section] if norm(item).strip(" .:;").casefold() not in labels]

    moved: list[str] = []
    skills: list[str] = []
    for item in sections["skills_or_notes"]:
        if re.match(r"^(?:атак|атаки)\s+за\s+раунд\s*:", item, re.I):
            moved.append(item)
        else:
            skills.append(item)
    sections["combat"].extend(moved)

    merged_skills: list[str] = []
    skill_buffer: list[str] = []
    for item in skills:
        if re.search(r"\d{1,3}%\s*(?:\([^)]+\))?", item):
            skill_buffer.append(item.rstrip("."))
        else:
            if skill_buffer:
                merged_skills.append(", ".join(skill_buffer))
                skill_buffer = []
            merged_skills.append(item)
    if skill_buffer:
        merged_skills.append(", ".join(skill_buffer))
    sections["skills_or_notes"] = merged_skills

    cleaned_background: list[str] = []
    for item in sections["background"]:
        cleaned_background.append(norm(item).lstrip("*- ").strip())
    sections["background"] = cleaned_background
    return sections


def table_html(headers: list[str], rows: list[list[str]], section: str) -> str:
    classes = ["statblock-structured-table"]
    if headers and headers[0] == "#":
        classes.append("has-index-column")
    head = "".join(f"<th>{html.escape(item)}</th>" for item in headers)
    body = "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        f'<table class="{" ".join(classes)}" data-section="{section}">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
    )


def rows(items: list[str], empty: str) -> list[list[str]]:
    if not items:
        return [["1", empty]]
    return [[str(index), item] for index, item in enumerate(items, start=1)]


def card_html(spec: CardStart, source_lines: list[str], supplemental_lines: list[str] | None = None) -> tuple[str, dict[str, Any]]:
    lines = nonempty(source_lines)
    stat_at = first_stat_index(lines)
    identity_text = norm(" ".join(lines[:stat_at]))
    text = norm(" ".join(lines))
    core = extract_core(text)
    derived = extract_derived(text)
    filled_from_pdf: list[str] = []
    supplemental_sha256: str | None = None
    if supplemental_lines:
        supplemental_text = norm(" ".join(supplemental_lines))
        supplemental_sha256 = sha256_text("\n".join(supplemental_lines))
        supplemental_core = extract_core(supplemental_text)
        supplemental_derived = extract_derived(supplemental_text)
        for key, value in supplemental_core.items():
            if value and not core.get(key):
                core[key] = value
                filled_from_pdf.append(key)
        for key, value in supplemental_derived.items():
            if value and not derived.get(key):
                derived[key] = value
                filled_from_pdf.append(key)
    body = classify_body(lines[stat_at:])
    identity = [["Персонаж", spec.display_name]]
    if identity_text and identity_text.casefold() != spec.display_name.casefold():
        identity.append(["Описание", identity_text])

    html_parts = [
        f'<div class="statblock-card" data-statblock-id="{spec.card_id}" data-source="kb_creator-ru-master">',
        '<div class="statblock-structured" data-schema="innsmouth-statblock-structured-v2">',
        table_html(["Поле", "Значение"], identity, "identity"),
        table_html(CORE_HEADERS_RU, [[core.get(label, "") for label in ["STR", "CON", "SIZ", "DEX", "INT", "APP", "POW", "EDU", "SAN"]]], "core_characteristics"),
        table_html(DERIVED_HEADERS_RU, [[derived.get(label, "") for label in ["HP", "DB", "Телосложение", "Движение", "MP", "Удача"]]], "derived_values"),
        table_html(["#", "Бой"], rows(body["combat"], "Явный боевой блок не выделен в источнике."), "combat"),
        table_html(["#", "Навыки / заметки"], rows(body["skills_or_notes"], "Дополнительные навыки/заметки не выделены отдельными строками в источнике."), "skills_or_notes"),
        table_html(["#", "Заклинания"], rows(body["spells"], "Заклинания не выделены в источнике."), "spells"),
        table_html(["#", "Предыстория"], rows(body["background"], "Предыстория не выделена в источнике."), "background"),
        "</div>",
        "</div>",
    ]
    missing_core = [label for label in ["STR", "CON", "SIZ", "DEX", "INT", "APP", "POW", "EDU", "SAN"] if not core.get(label)]
    record = {
        "card_id": spec.card_id,
        "display_name": spec.display_name,
        "source_lines": len(lines),
        "source_sha256": sha256_text("\n".join(source_lines)),
        "supplemental_source": "source_pdf_text_layer" if supplemental_lines else None,
        "supplemental_sha256": supplemental_sha256,
        "filled_from_pdf": filled_from_pdf,
        "missing_core": missing_core,
        "sections": {key: len(value) for key, value in body.items()},
    }
    return "\n".join(html_parts), record


def build_cards(source_text: str, source_pdf: Path | None = None) -> tuple[str, list[dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    blocks, block_pages, findings = extract_statblock_lines(source_text)
    supplemental_blocks, supplemental_findings = extract_pdf_statblock_lines(source_pdf)
    findings.extend(supplemental_findings)
    records: list[dict[str, Any]] = []
    page_heading_ids: dict[str, str] = {}
    parts = ['## Персонажи и чудовища']
    current_group: str | None = None
    current_page: str | None = "033"
    for spec in CARD_STARTS:
        if spec.group != current_group:
            current_group = spec.group
            if current_group == "Готовые сыщики":
                parts.append("\n## Заранее созданные сыщики")
            elif current_group != "Персонажи и чудовища":
                parts.append(f"\n### {current_group}")
        block = blocks.get(spec.card_id)
        if not block:
            continue
        card, record = card_html(spec, block, supplemental_blocks.get(spec.card_id))
        page = block_pages.get(spec.card_id)
        heading_id = slugify(spec.display_name)
        if page and page not in page_heading_ids:
            page_heading_ids[page] = heading_id if spec.group == "Готовые сыщики" else slugify(spec.group)
        if page and page != current_page:
            parts.append(f"\n<!-- source-page-{page} -->")
            current_page = page
        records.append(record)
        if spec.group == "Готовые сыщики":
            if spec.card_id == "statblock-020":
                parts.append("### Готовые сыщики")
            parts.append(f"### {spec.display_name}")
        else:
            parts.append(f'<a id="{heading_id}"></a>')
        parts.append(card)
    if len(records) != len(CARD_STARTS):
        findings.append({"severity": "blocker", "code": "statblock_count_mismatch", "expected": len(CARD_STARTS), "actual": len(records)})
    return "\n\n".join(parts).strip() + "\n", records, page_heading_ids, findings


def replace_keeper_section(keeper_text: str, replacement: str) -> tuple[str, bool]:
    start_match = re.search(r"(?m)^## Персонажи и чудовища\s*$", keeper_text)
    end_match = re.search(r"(?m)^## Раздаточные материалы\s*$", keeper_text)
    if not start_match or not end_match or end_match.start() <= start_match.start():
        return keeper_text, False
    removed = keeper_text[start_match.start() : end_match.start()]
    replacement_pages = set(re.findall(r"source-page-(\d{3})", replacement))
    trailing_markers = []
    for page in re.findall(r"(?m)^<!--\s*source-page-(\d{3})\s*-->$", removed):
        if page not in replacement_pages and page != "033":
            trailing_markers.append(f"<!-- source-page-{page} -->")
            replacement_pages.add(page)
    if trailing_markers:
        replacement = replacement.rstrip() + "\n\n" + "\n\n".join(trailing_markers) + "\n"
    return keeper_text[: start_match.start()] + replacement + "\n" + keeper_text[end_match.start() :], True


def retarget_statblock_art_manifest(manifest_path: Path | None, page_heading_ids: dict[str, str]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "enabled": bool(manifest_path),
        "manifest": str(manifest_path).replace("\\", "/") if manifest_path else None,
        "retargeted": [],
        "findings": [],
    }
    if not manifest_path:
        return report
    if not manifest_path.exists():
        report["findings"].append({"severity": "blocker", "code": "art_manifest_not_found"})
        return report

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recovery_report = ensure_ian_torres_portrait_placement(manifest, manifest_path)
    report["recovered"] = recovery_report.get("recovered", [])
    report["recovery_findings"] = recovery_report.get("findings", [])
    report["findings"].extend(recovery_report.get("findings", []))
    for placement in manifest.get("placements", []):
        if not isinstance(placement, dict):
            continue
        source_page = str(placement.get("source_page") or "").zfill(3)
        target = page_heading_ids.get(source_page)
        role = str(placement.get("semantic_role") or placement.get("runtime_role") or "").strip()
        if not target or role != "npc":
            continue
        old_heading = str(placement.get("heading_id") or "")
        if old_heading == target:
            continue
        placement["heading_id"] = target
        placement["anchor_kind"] = "heading"
        placement["insertion_rule"] = "after_heading"
        report["retargeted"].append(
            {
                "placement_id": placement.get("placement_id"),
                "source_page": source_page,
                "old_heading_id": old_heading,
                "new_heading_id": target,
            }
        )

    if report["retargeted"] or recovery_report.get("manifest_rewritten"):
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def ensure_ian_torres_portrait_placement(manifest: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    """Recover Ian Torres portrait when PDF image extraction misses it.

    The source page contains a clear portrait, but the current extraction stage
    does not expose it as xref-01200. Keep the recovery deterministic by
    cropping from the rendered source page and adding the expected placement.
    """
    report: dict[str, Any] = {"manifest_rewritten": False, "recovered": [], "findings": []}
    placements = manifest.get("placements", [])
    if not isinstance(placements, list):
        report["findings"].append({"severity": "blocker", "code": "art_manifest_placements_not_list"})
        return report
    if any(isinstance(item, dict) and item.get("placement_id") == "xref-01200" for item in placements):
        return report

    try:
        from PIL import Image

        working_root = manifest_path.parent.parent
        run_id = working_root.name
        kb_creator_root = working_root.parents[3]
        output_root = kb_creator_root / "output/innsmouth_source_to_artifacts/runs" / run_id
        render = working_root / "Images/Page_Renders/page-38.png"
        source_asset = working_root / "Images/Web_Safe/pdf_image_xref_01200.png"
        runtime_asset = output_root / "Images/NPC/innsmouth-page-038-xref-01200-npc.png"
        if not render.exists():
            report["findings"].append(
                {"severity": "blocker", "code": "ian_torres_render_missing", "path": str(render).replace("\\", "/")}
            )
            return report
        image = Image.open(render)
        crop_box = [790, 1080, 1425, 1850]
        crop = image.crop(tuple(crop_box))
        source_asset.parent.mkdir(parents=True, exist_ok=True)
        runtime_asset.parent.mkdir(parents=True, exist_ok=True)
        crop.save(source_asset)
        crop.save(runtime_asset)
        placements.append(
            {
                "placement_id": "xref-01200",
                "asset_id": "xref-01200",
                "source_kind": "page_render_crop_recovery",
                "runtime_filename": runtime_asset.name,
                "runtime_src": "Images/NPC/innsmouth-page-038-xref-01200-npc.png",
                "runtime_role": "npc",
                "semantic_role": "npc",
                "source_page": "038",
                "source_asset_path": str(source_asset).replace("\\", "/"),
                "source_crop_box": crop_box,
                "heading_id": "ian-torres",
                "anchor_kind": "heading",
                "insertion_rule": "after_heading",
                "emit_reader_art_block": True,
            }
        )
        report["manifest_rewritten"] = True
        report["recovered"].append(
            {
                "placement_id": "xref-01200",
                "source_page": "038",
                "runtime_src": "Images/NPC/innsmouth-page-038-xref-01200-npc.png",
                "crop_box": crop_box,
            }
        )
    except Exception as exc:
        report["findings"].append(
            {"severity": "blocker", "code": "ian_torres_portrait_recovery_failed", "message": f"{type(exc).__name__}: {exc}"}
        )
    return report


def keeper_art_block(placement: dict[str, Any]) -> str | None:
    placement_id = str(placement.get("placement_id") or "").strip()
    heading_id = str(placement.get("heading_id") or "").strip()
    runtime_src = str(placement.get("runtime_src") or "").strip()
    if not placement_id or not heading_id or not runtime_src:
        return None
    md_src = f"../{runtime_src}" if runtime_src.startswith("Images") else runtime_src
    return (
        f'<div class="keeper-art-block" data-placement-id="{placement_id}" '
        f'data-anchor-id="{heading_id}"> <img id="{placement_id}-image" '
        f'src="{md_src}" alt="{placement_id}"> </div>'
    )


def inject_statblock_art_blocks(keeper_text: str, manifest_path: Path | None) -> tuple[str, dict[str, Any]]:
    report: dict[str, Any] = {
        "enabled": bool(manifest_path),
        "manifest": str(manifest_path).replace("\\", "/") if manifest_path else None,
        "inserted": [],
        "skipped": [],
        "findings": [],
    }
    if not manifest_path:
        return keeper_text, report
    if not manifest_path.exists():
        report["findings"].append({"severity": "blocker", "code": "art_manifest_not_found"})
        return keeper_text, report

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing = set(re.findall(r'data-placement-id="([^"]+)"', keeper_text))
    lines = keeper_text.splitlines()
    inserts_by_line: dict[int, list[str]] = {}
    used_slugs: dict[str, int] = {}
    heading_lines: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if not match:
            continue
        base = slugify(match.group(2))
        used_slugs[base] = used_slugs.get(base, 0) + 1
        heading_id = base if used_slugs[base] == 1 else f"{base}-{used_slugs[base]}"
        heading_lines[heading_id] = index

    for placement in manifest.get("placements", []):
        if not isinstance(placement, dict) or not placement.get("emit_reader_art_block"):
            continue
        placement_id = str(placement.get("placement_id") or "").strip()
        heading_id = str(placement.get("heading_id") or "").strip()
        role = str(placement.get("semantic_role") or placement.get("runtime_role") or "").strip()
        if placement_id in existing:
            report["skipped"].append({"placement_id": placement_id, "reason": "already_present"})
            continue
        if role != "npc" or heading_id not in PREGEN_STATBLOCK_HEADING_IDS:
            continue
        heading_index = heading_lines.get(heading_id)
        block = keeper_art_block(placement)
        if heading_index is None or not block:
            report["findings"].append(
                {
                    "severity": "warning",
                    "code": "statblock_art_anchor_not_found",
                    "placement_id": placement_id,
                    "heading_id": heading_id,
                }
            )
            continue
        inserts_by_line.setdefault(heading_index, []).append(block)
        report["inserted"].append({"placement_id": placement_id, "heading_id": heading_id})

    if not inserts_by_line:
        return keeper_text, report
    out: list[str] = []
    for index, line in enumerate(lines):
        out.append(line)
        if index in inserts_by_line:
            out.append("")
            for block in inserts_by_line[index]:
                out.append(block)
                out.append("")
    return "\n".join(out) + ("\n" if keeper_text.endswith("\n") else ""), report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ru-master", type=Path, required=True)
    parser.add_argument("--keeper", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--art-manifest", type=Path)
    parser.add_argument("--source-pdf", type=Path)
    args = parser.parse_args()

    source_text = args.ru_master.read_text(encoding="utf-8")
    keeper_text = args.keeper.read_text(encoding="utf-8")
    replacement, records, page_heading_ids, findings = build_cards(source_text, args.source_pdf)
    projected, replaced = replace_keeper_section(keeper_text, replacement)
    if not replaced:
        findings.append({"severity": "blocker", "code": "keeper_statblock_section_not_found"})
    art_manifest_report = retarget_statblock_art_manifest(args.art_manifest, page_heading_ids)
    findings.extend(art_manifest_report["findings"])
    projected, statblock_art_report = inject_statblock_art_blocks(projected, args.art_manifest)
    findings.extend(statblock_art_report["findings"])

    status = "pass" if not findings else "blocked"
    if status == "pass":
        args.keeper.write_text(projected, encoding="utf-8", newline="\n")

    report = {
        "schema": "kb_creator.innsmouth_statblock_projection.v1",
        "generated_at_utc": now_utc(),
        "status": status,
        "ru_master": str(args.ru_master).replace("\\", "/"),
        "source_pdf": str(args.source_pdf).replace("\\", "/") if args.source_pdf else None,
        "keeper": str(args.keeper).replace("\\", "/"),
        "input_keeper_sha256": sha256_text(keeper_text),
        "output_keeper_sha256": sha256_text(projected),
        "expected_cards": len(CARD_STARTS),
        "projected_cards": len(records),
        "page_heading_ids": page_heading_ids,
        "art_manifest": art_manifest_report,
        "statblock_art_blocks": statblock_art_report,
        "records": records,
        "findings": findings,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"status={status} expected={len(CARD_STARTS)} projected={len(records)} findings={len(findings)} report={args.report}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
