"""Synchronize and promote the explicitly accepted Innsmouth MASTER_RU."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_innsmouth_master_en as master_en
import verify_innsmouth_master_en_repo_input as verify_en


ROOT_FILES = {"MASTER_RU.md", "MASTER_RU.acceptance.json"}
HEX_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
IMAGE_REFERENCE = re.compile(r"!\[[^\]]*\]\(assets/([^)]+)\)")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
FRAGMENT = re.compile(r"\]\(#([^\)]+)\)")
REPO_ROOT = Path(__file__).resolve().parents[2]
TERMINOLOGY_REGISTRY_RELATIVE_PATH = (
    "CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv"
)
DEFAULT_TERMINOLOGY_REGISTRY = REPO_ROOT / TERMINOLOGY_REGISTRY_RELATIVE_PATH
# The accepted 2026-08-30 package remains bound to the glossary that existed
# when it was sealed.  This record verifies historical provenance only; no live
# copy of that superseded glossary is required or permitted as an authority.
LEGACY_GLOSSARY_PROVENANCE = {
    "path": "docs/terminology/CALL_OF_CTHULHU_7E_SKILLS_EN_RU.md",
    "byte_count": 11_884,
    "sha256": "BE7CCE74993263983670FF68459805CCB49DE873B1EB5B1B95E85442FF223304",
}
ACCEPTED_SOURCE_MASTER_RU_BYTES = 195_422
ACCEPTED_SOURCE_MASTER_RU_SHA256 = (
    "BAF53B8E20AA91D3124AE83C7D3A533F4D9D16B9F104AB47B93995B048C81FC9"
)
PROMOTED_MASTER_RU_BYTES = 189_302
PROMOTED_MASTER_RU_SHA256 = (
    "E9A0AF27BEFE56630E1DBF24CD63EB9C8768706FEAE4C4DB1836E3175D4DED8E"
)
ACCEPTANCE_MANIFEST_BYTES = 3_520
ACCEPTANCE_MANIFEST_SHA256 = (
    "87B3B867895209D8444F5B7E940EE6E14BECE3C79D810F35C92BD5D4FA6ED412"
)
CREDITS_ART_ASSET = "ed88e677e363073b2973212c4f3e44c3bd91c2a91aff7f7ca0e3a8da41c4e224.jpg"
SOURCE_COVER_ASSET = master_en.reconstructed.SOURCE_COVER_ASSET
RU_RETAINED_ASSETS = master_en.RETAINED_ASSETS - {CREDITS_ART_ASSET}

# These are deliberately exact reader-text substitutions. They implement the
# already approved Hobby World terminology pass without reopening translation.
TERMINOLOGY_REPLACEMENTS = (
    ("Бухгалтерского учёта", "Бухгалтерского дела", 1),
    ("проверку Библиотечного дела", "проверку Работы в библиотеке", 1),
    ("проверке Права", "проверке Юриспруденции", 1),
    ("проверке Выслеживания", "проверке Чтения следов", 3),
    ("проверку Прыжка или Лазания", "проверку Прыжков или Лазания", 1),
    ("проверку ЛВК или Броска", "проверку ЛВК или Метания", 1),
    ("проверка Внимательности", "проверка Внимания", 1),
    ("или Библиотечное дело просмотреть", "или Работы в библиотеке просмотреть", 1),
    ("успешно прошедшие Внимательность", "успешно прошедшие проверку Внимания", 1),
    ("Прошедшие Внимательность", "Прошедшие проверку Внимания", 1),
    ("Иначе нужен Внимательность.", "Иначе нужна проверка Внимания.", 1),
    ("Библиотечное дело", "Работа в библиотеке", 5),
    ("Внимательность", "Внимание", 5),
    ("Кредитный рейтинг", "Средства", 2),
    ("Репутация", "Средства", 5),
    ("Бухгалтерия", "Бухгалтерское дело", 3),
    ("Быстрая речь", "Красноречие", 3),
    ("Атлетика", "Лазание", 2),
    ("Прыжок", "Прыжки", 3),
    ("Право", "Юриспруденция", 1),
    ("Бросок", "Метание", 1),
)
OBSOLETE_SKILL_TERMS = tuple(old for old, _new, _count in TERMINOLOGY_REPLACEMENTS) + (
    "Слежение",
    "Выслеживание",
    "Ремонт механизмов",
    "Управление тяжёлой техникой",
)

# Exact translated headings for the semantic destinations corrected in the
# MASTER_EN pipeline.  This pass moves only existing anchor lines; reader text
# and link destinations remain byte-for-byte unchanged.
RU_HEADING_TARGETS = (
    ("nri-h-eb898a1c80749cbdbb6a2241", "### СЪЁМОЧНАЯ ГРУППА"),
    ("nri-h-f81478a90f8941232106712e", "### «АРКХЭМ АДВЕРТАЙЗЕР»"),
    ("nri-h-27b1ad17b7316f09136b83bc", "### МИСКАТОНИКСКИЙ ТЕАТР"),
    ("nri-h-a6cc5383a39e0ec74e8769a8", "### СЪЁМОЧНЫЙ ВАГОН"),
    ("nri-h-591edd5bcf58d378b27f28cc", "### ОТЕЛЬ «ГИЛМАН-ХАУС»"),
    ("nri-h-1e72d19ab832ccee9c380a67", "### Кабинет Bazzledon"),
    ("nri-h-9af9701e3f85a91ab3b92009", "### Трейлер Ginny"),
    ("nri-h-4a3bb4ef4c7d762c63fef3b4", "### На съёмочной площадке"),
    ("nri-h-0377b0cfaf5eda9da814e2d8", "### СИСТЕМА ПЕЩЕР"),
    ("nri-h-f6184124151c4142421b1af0", "### РЕЗИДЕНЦИЯ BREWSTER"),
    ("nri-h-d012304a399a1e520aefdba5", "### Универсальный магазин"),
    ("nri-h-1b70234c4ece0af6255492e8", "### Пожарная станция"),
    ("nri-h-04a91268c2b7afffd26817db", "### Эзотерический орден Дагона"),
    ("nri-h-7b4e91617daf61336c70a8cf", "### Последний поезд из Иннсмута"),
    ("nri-h-ee0dadea1c956d399c954d44", "### Награды"),
    ("nri-h-f1f10a91537c50581b8ff2a6", "### Шоггот"),
)

RU_HANDOUT_ANCHORS = {
    "Раздаточный материал 1-a": "nri-h-94205138fca7aa22510e0aca",
    "Раздаточный материал 1-b": "nri-h-f8e3b2764c3b8f24c4c83bfa",
    "раздаточный материал 2": "nri-h-1701b4c74a5e58fac76c83d3",
    "раздаточном материале 2": "nri-h-1701b4c74a5e58fac76c83d3",
}
RU_HANDOUT_BODY_REFERENCE_COUNTS = {
    "Раздаточный материал 1-a": 2,
    "Раздаточный материал 1-b": 1,
    "раздаточный материал 2": 4,
    "раздаточном материале 2": 1,
}
RU_DECORATIVE_HANDOUT_ASSETS = {
    "0ee550370e17bfe37128a9d44b271899b8e535c3e0847d1a41a6c32b8c5e4617.jpg",
    "334f14bd517569e118d9445575f8c2bed6a356c7504142c3ac75a6f472e954f5.jpg",
    "eca0dbf63145cd539f47da6691e5e1675c906be4372d97d73ca9d85efe7b5a6d.jpg",
    "eda68c6d95d2e6dc230faf0f05301f82f282c152251c8ae936f2879d1424d49a.jpg",
    "f442a32a6901a3299a2c4ab5d06ff239bb2ee02cc6b55581b02e8eec7c708da9.jpg",
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _expected_hash(value: str, label: str) -> str:
    if not HEX_SHA256.fullmatch(value):
        raise ValueError(f"{label} must be one explicit SHA-256")
    return value.upper()


def synchronize_terminology(markdown: str) -> tuple[str, dict[str, int]]:
    output = markdown
    counts: dict[str, int] = {}
    for old, new, expected_count in TERMINOLOGY_REPLACEMENTS:
        actual_count = output.count(old)
        if actual_count != expected_count:
            raise ValueError(
                f"terminology source count mismatch for {old!r}: "
                f"expected {expected_count}, got {actual_count}"
            )
        output = output.replace(old, new)
        counts[f"{old} -> {new}"] = actual_count
    if output == markdown:
        raise ValueError("terminology synchronization made no change")
    return output, counts


def realign_semantic_anchors(markdown: str) -> tuple[str, dict[str, str]]:
    output = markdown
    for anchor, _heading in RU_HEADING_TARGETS:
        anchor_line = f'<a id="{anchor}"></a>'
        if output.count(anchor_line) != 1:
            raise ValueError(f"semantic anchor identity mismatch: {anchor}")
        output = output.replace(anchor_line + "\n", "", 1)
    moved: dict[str, str] = {}
    for anchor, heading in RU_HEADING_TARGETS:
        heading_line = heading + "\n"
        if output.count(heading_line) != 1:
            raise ValueError(f"semantic heading binding mismatch: {heading}")
        anchor_line = f'<a id="{anchor}"></a>\n'
        output = output.replace(heading_line, anchor_line + heading_line, 1)
        moved[anchor] = heading
    master_en.validate_semantic_anchor_alignment(output)
    return output, moved


def project_handout_reader_flow(markdown: str) -> tuple[str, dict[str, int]]:
    """Mirror the canonical EN handout suppression and appendix-link policy."""
    output = markdown
    decorative_assets_suppressed = 0
    for name in sorted(RU_DECORATIVE_HANDOUT_ASSETS):
        pattern = re.compile(rf"(?m)^!\[\]\(assets/{re.escape(name)}\)[ \t]*\n?")
        output, suppressions = pattern.subn("", output, count=1)
        if suppressions != 1:
            raise ValueError(f"RU decorative handout asset binding mismatch: {name}")
        decorative_assets_suppressed += suppressions

    letter_pattern = re.compile(
        r"(?ms)^### КАБИНЕТ ВИЦЕ-КАНЦЛЕРА МИСКАТОНИКСКОГО УНИВЕРСИТЕТА, "
        r"Аркхэм, Массачусетс\n.*?"
        r"^\(См\. \[\*\*раздаточный материал 1-b\*\*\]"
        r"\(#nri-h-f8e3b2764c3b8f24c4c83bfa\)\)\n?"
    )
    output, letter_suppressions = letter_pattern.subn("", output, count=1)
    if letter_suppressions != 1:
        raise ValueError("RU body Handout 1-a duplicate binding mismatch")

    keeper_match = re.search(
        r"(?m)^\*\*Заметка Хранителя:\*\* LLFRFL — указания .+$", output
    )
    if keeper_match is None:
        raise ValueError("RU body Handout 2 Keeper note binding mismatch")
    keeper_note = keeper_match.group(0)
    note_pattern = re.compile(
        r"(?ms)^Привет, G!\n.*?^\*\*Заметка Хранителя:\*\* LLFRFL — указания [^\n]+\n?"
    )
    output, note_suppressions = note_pattern.subn("", output, count=1)
    if note_suppressions != 1:
        raise ValueError("RU body Handout 2 duplicate binding mismatch")

    appendix_boundary = output.find("## РАЗДАТОЧНЫЕ МАТЕРИАЛЫ\n")
    if appendix_boundary < 0:
        raise ValueError("RU handout appendix boundary is missing")
    body = output[:appendix_boundary]
    appendix = output[appendix_boundary:]
    appendix_note_pattern = re.compile(
        r"(?ms)^(Привет, G,\n.*?^Sammy)\n\n"
        r"\*\*Раздаточный материал 2\*\*: записка\n.*\Z"
    )
    appendix, appendix_consolidations = appendix_note_pattern.subn(
        "### Раздаточный материал 2: записка\n\n"
        + r"\1"
        + "\n\n"
        + keeper_note
        + "\n",
        appendix,
        count=1,
    )
    if appendix_consolidations != 1:
        raise ValueError("RU Handout 2 appendix consolidation binding mismatch")
    linked_references = 0
    for label, expected_count in RU_HANDOUT_BODY_REFERENCE_COUNTS.items():
        before = f"**{label}**"
        after = f"[**{label}**](#{RU_HANDOUT_ANCHORS[label]})"
        actual_count = body.count(before)
        if actual_count != expected_count:
            raise ValueError(
                f"RU body handout reference binding mismatch for {label}: "
                f"expected {expected_count}, found {actual_count}"
            )
        body = body.replace(before, after)
        linked_references += actual_count
    output = body + appendix

    for anchor, heading, expected_headings in (
        (
            RU_HANDOUT_ANCHORS["Раздаточный материал 1-a"],
            "### КАНЦЕЛЯРИЯ ВИЦЕ-КАНЦЛЕРА",
            2,
        ),
        (
            RU_HANDOUT_ANCHORS["раздаточный материал 2"],
            "### Раздаточный материал 2: записка",
            1,
        ),
    ):
        anchor_line = f'<a id="{anchor}"></a>\n'
        if anchor_line in output:
            raise ValueError(f"RU handout anchor already exists: {anchor}")
        heading_line = heading + "\n"
        matches = appendix.count(heading_line)
        if matches != expected_headings:
            raise ValueError(f"RU handout appendix heading mismatch: {heading}")
        appendix = appendix.replace(heading_line, anchor_line + heading_line, 1)
    output = body + appendix
    master_en.validate_semantic_anchor_alignment(output)
    return output, {
        "body_handout_duplicates_suppressed": letter_suppressions + note_suppressions,
        "keeper_notes_relocated_to_appendix": 1,
        "appendix_handout_duplicates_suppressed": appendix_consolidations,
        "body_handout_links": linked_references,
        "appendix_handout_anchors_added": 2,
        "decorative_handout_assets_suppressed": decorative_assets_suppressed,
    }


def project_front_matter(markdown: str) -> tuple[str, dict[str, int]]:
    output = markdown
    first_art = "c68b102eb549eaa684f8fb5a3637bc8acd12f8f123cdf8aa4b79bb5b19de103c.jpg"
    cover_binding = f"# УЖАС ИННСМУТА\n![](assets/{first_art})\n"
    if output.count(cover_binding) != 1:
        raise ValueError("RU source-cover insertion binding mismatch")
    output = output.replace(
        cover_binding,
        f"# УЖАС ИННСМУТА\n![](assets/{SOURCE_COVER_ASSET})\n"
        f"![](assets/{first_art})\n",
        1,
    )

    credits_pattern = re.compile(
        rf"(?ms)^!\[\]\(assets/{re.escape(CREDITS_ART_ASSET)}\)\n"
        r"# УЖАС ИННСМУТА\n.*?(?=^# СОДЕРЖАНИЕ\n)"
    )
    output, credits_suppressed = credits_pattern.subn("", output, count=1)
    if credits_suppressed != 1:
        raise ValueError("RU credits-section suppression binding mismatch")

    warnings_pattern = re.compile(
        r"(?ms)^## ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ\n.*?(?=^# УЖАС ИННСМУТА\n)"
    )
    output, warning_suppressions = warnings_pattern.subn("", output, count=1)
    if warning_suppressions != 1:
        raise ValueError("RU content-warning suppression binding mismatch")
    return output, {
        "source_cover_links_added": 1,
        "credits_sections_suppressed": credits_suppressed,
        "content_warning_blocks_suppressed": warning_suppressions,
    }


def validate_ru_markdown(markdown: str, canonical_en: str) -> dict[str, int]:
    if "<!-- mineru-page:" in markdown or "<!-- table-evidence:" in markdown:
        raise ValueError("technical reconstruction comments leaked into MASTER_RU")
    image_names = IMAGE_REFERENCE.findall(markdown)
    canonical_image_names = [
        name for name in IMAGE_REFERENCE.findall(canonical_en) if name != CREDITS_ART_ASSET
    ]
    if image_names != canonical_image_names:
        raise ValueError("MASTER_RU ordered image references differ from canonical MASTER_EN")
    anchors = ANCHOR.findall(markdown)
    fragments = FRAGMENT.findall(markdown)
    broken = sorted(set(fragments) - set(anchors))
    counts = {
        "image_links": len(image_names),
        "tables": markdown.count("<table>"),
        "headings": len(re.findall(r"(?m)^#{1,6} ", markdown)),
        "anchors": len(anchors),
        "fragments": len(fragments),
        "broken_fragments": len(broken),
    }
    expected = {
        "image_links": 32,
        "tables": 51,
        "headings": 152,
        "anchors": 52,
        "fragments": 86,
        "broken_fragments": 0,
    }
    if counts != expected:
        raise ValueError(f"MASTER_RU structural counts mismatch: {counts}; broken={broken}")
    if len(set(anchors)) != 52:
        raise ValueError("duplicate MASTER_RU anchors")
    master_en.validate_semantic_anchor_alignment(markdown)
    body, boundary, appendix = markdown.partition("## РАЗДАТОЧНЫЕ МАТЕРИАЛЫ\n")
    if not boundary:
        raise ValueError("MASTER_RU handout appendix boundary is missing")
    if "### КАБИНЕТ ВИЦЕ-КАНЦЛЕРА МИСКАТОНИКСКОГО УНИВЕРСИТЕТА" in body:
        raise ValueError("RU body Handout 1-a duplicate remains")
    if "Хотел заглянуть и повидаться, но твоя группа не обрадовалась" in body:
        raise ValueError("RU body Handout 2 duplicate remains")
    for label, expected_count in RU_HANDOUT_BODY_REFERENCE_COUNTS.items():
        linked = f"[**{label}**](#{RU_HANDOUT_ANCHORS[label]})"
        if body.count(linked) != expected_count:
            raise ValueError(f"RU body {label} link count mismatch")
    if appendix.count("**Заметка Хранителя:** LLFRFL — указания") != 1:
        raise ValueError("RU Handout 2 Keeper note was not conserved in appendix")
    if appendix.count("### Раздаточный материал 2: записка") != 1:
        raise ValueError("RU Handout 2 appendix heading was not consolidated")
    if appendix.count("Привет, G,") != 1 or "**Раздаточный материал 2**: записка" in appendix:
        raise ValueError("RU Handout 2 duplicate remains in appendix")
    if "ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ" in markdown:
        raise ValueError("RU content-warning block remains")
    if CREDITS_ART_ASSET in markdown or "John Hedge при участии сотрудников театра" in markdown:
        raise ValueError("RU credits section remains")
    if not markdown.startswith(
        f"# УЖАС ИННСМУТА\n![](assets/{SOURCE_COVER_ASSET})\n"
    ):
        raise ValueError("RU source cover is not the first reader asset")
    for old in OBSOLETE_SKILL_TERMS:
        if old in markdown:
            raise ValueError(f"obsolete skill terminology remains: {old}")
    return counts


def verify_terminology_registry(path: Path) -> dict[str, Any]:
    if path.resolve() != DEFAULT_TERMINOLOGY_REGISTRY.resolve():
        raise ValueError("terminology registry must be the canonical CoC system registry")
    raw = path.read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    expected_fields = {
        "source_term",
        "accepted_ru",
        "aliases",
        "bad_ru",
        "domain",
        "status",
        "source_scope",
        "decision_rule",
        "notes",
    }
    if not rows or set(rows[0]) != expected_fields:
        raise ValueError("canonical CoC terminology registry schema mismatch")
    accepted = {
        row["source_term"]: row
        for row in rows
        if row["status"].strip().casefold() == "accepted"
    }
    required = {
        "Track": "Чтение следов",
        "Spot Hidden": "Внимание",
        "Library Use": "Работа в библиотеке",
        "Credit Rating": "Средства",
        "SIZ": "ТЕЛ",
        "APP": "НАР",
        "POW": "МОЩ",
    }
    if any(
        source not in accepted
        or accepted[source]["accepted_ru"].strip() != target
        or accepted[source]["domain"].strip() not in {"skill", "characteristic"}
        for source, target in required.items()
    ):
        raise ValueError("canonical CoC terminology registry content mismatch")
    return {
        "path": TERMINOLOGY_REGISTRY_RELATIVE_PATH,
        "byte_count": len(raw),
        "sha256": sha256(raw),
    }


def _asset_inventory(
    assets: Path, expected_names: set[str], *, allow_extras: bool = False
) -> dict[str, Any]:
    if not assets.is_dir():
        raise ValueError(f"missing MASTER_RU asset directory: {assets}")
    files = {path.name for path in assets.iterdir() if path.is_file()}
    directories = {path.name for path in assets.iterdir() if path.is_dir()}
    inventory_mismatch = (
        not expected_names.issubset(files) if allow_extras else files != expected_names
    )
    if inventory_mismatch or directories:
        raise ValueError(
            f"MASTER_RU asset directory must contain exactly "
            f"{len(expected_names)} canonical files"
        )
    rows = [
        {
            "path": f"assets/{name}",
            "byte_count": (assets / name).stat().st_size,
            "sha256": master_en._sha256_file(assets / name),
        }
        for name in sorted(expected_names)
    ]
    raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "asset_count": len(rows),
        "total_bytes": sum(int(row["byte_count"]) for row in rows),
        "inventory_sha256": hashlib.sha256(raw).hexdigest(),
        "files": rows,
    }


def verify_source_asset_inventory(assets: Path) -> dict[str, Any]:
    return _asset_inventory(assets, master_en.RETAINED_ASSETS)


def verify_asset_inventory(assets: Path) -> dict[str, Any]:
    return _asset_inventory(assets, RU_RETAINED_ASSETS)


def canonical_en_report(master_en_root: Path) -> dict[str, Any]:
    report = verify_en.verify(master_en_root)
    manifest = json.loads((master_en_root / "MASTER_EN.acceptance.json").read_bytes())
    return {
        "accepted_on": manifest["accepted_on"],
        "markdown": manifest["package"]["markdown"],
        "acceptance_manifest": {
            "path": "MASTER_EN.acceptance.json",
            "byte_count": verify_en.EXPECTED_ROOTS["MASTER_EN.acceptance.json"][0],
            "sha256": verify_en.EXPECTED_ROOTS["MASTER_EN.acceptance.json"][1],
        },
        "inventory_sha256": report["inventory_sha256"],
    }


def inspect_candidate(
    candidate: Path,
    assets: Path,
    terminology_registry: Path,
    master_en_root: Path,
    expected_master_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    expected_master_sha256 = _expected_hash(expected_master_sha256, "MASTER_RU hash")
    if expected_master_sha256 != ACCEPTED_SOURCE_MASTER_RU_SHA256:
        raise ValueError("MASTER_RU expected hash is not the accepted candidate identity")
    source_raw = candidate.read_bytes()
    if (
        len(source_raw) != ACCEPTED_SOURCE_MASTER_RU_BYTES
        or sha256(source_raw) != expected_master_sha256
    ):
        raise ValueError("accepted MASTER_RU candidate identity mismatch")
    en = canonical_en_report(master_en_root)
    en_markdown = (master_en_root / "MASTER_EN.md").read_text(encoding="utf-8")
    source_markdown = source_raw.decode("utf-8")
    aligned_markdown, anchor_realignments = realign_semantic_anchors(source_markdown)
    synchronized_markdown, replacements = synchronize_terminology(aligned_markdown)
    projected_front_matter, front_matter_projection = project_front_matter(
        synchronized_markdown
    )
    promoted_markdown, handout_projection = project_handout_reader_flow(
        projected_front_matter
    )
    counts = validate_ru_markdown(promoted_markdown, en_markdown)
    registry_identity = verify_terminology_registry(terminology_registry)
    source_inventory = verify_source_asset_inventory(assets)
    canonical_source_inventory = verify_source_asset_inventory(master_en_root / "assets")
    if source_inventory != canonical_source_inventory:
        raise ValueError("retained asset inventory mismatch")
    inventory = _asset_inventory(assets, RU_RETAINED_ASSETS, allow_extras=True)
    promoted_raw = promoted_markdown.encode("utf-8")
    if (
        len(promoted_raw) != PROMOTED_MASTER_RU_BYTES
        or sha256(promoted_raw) != PROMOTED_MASTER_RU_SHA256
    ):
        raise ValueError("terminology-synchronized MASTER_RU identity mismatch")
    return (
        {
            "state": "MASTER_RU_PROMOTION_PREFLIGHT_OK",
            "source_candidate": {
                "path": "MASTER_RU.md",
                "byte_count": len(source_raw),
                "sha256": sha256(source_raw),
            },
            "markdown": {
                "path": "MASTER_RU.md",
                "byte_count": len(promoted_raw),
                "sha256": sha256(promoted_raw),
            },
            "source_master_en": en,
            "glossary": LEGACY_GLOSSARY_PROVENANCE,
            "terminology_registry": registry_identity,
            "asset_inventory": inventory,
            "counts": counts,
            "terminology_replacements": replacements,
            "semantic_anchor_realignments": anchor_realignments,
            "handout_projection": handout_projection,
            "front_matter_projection": front_matter_projection,
        },
        promoted_raw,
    )


def acceptance_manifest(report: dict[str, Any], accepted_on: str) -> bytes:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", accepted_on):
        raise ValueError("accepted-on must use YYYY-MM-DD")
    return canonical_json(
        {
            "schema": "InnsmouthAcceptedMasterRu.v1",
            "state": "ACCEPTED_MASTER_RU_REPO_INPUT",
            "accepted_on": accepted_on,
            "acceptance_authority": "explicit_user_reading_acceptance_plus_approved_glossary_sync",
            "source_candidate": report["source_candidate"],
            "source_master_en": report["source_master_en"],
            "glossary": report["glossary"],
            "package": {
                "markdown": report["markdown"],
                "asset_count": report["asset_inventory"]["asset_count"],
                "asset_inventory_sha256": report["asset_inventory"]["inventory_sha256"],
                "counts": report["counts"],
                "terminology_replacements": report["terminology_replacements"],
                "semantic_anchor_realignments": len(report["semantic_anchor_realignments"]),
                "handout_projection": report["handout_projection"],
                "front_matter_projection": report["front_matter_projection"],
            },
            "rules": {
                "manual_file_copy_forbidden": True,
                "historical_ru_or_en_bridge_forbidden": True,
                "generated_html_or_pdf_manual_edit_forbidden": True,
            },
        }
    )


def verify_promoted(
    root: Path, terminology_registry: Path, master_en_root: Path
) -> dict[str, Any]:
    root_files = {path.name for path in root.iterdir() if path.is_file()}
    root_directories = {path.name for path in root.iterdir() if path.is_dir()}
    if root_files != ROOT_FILES or root_directories != {"assets"}:
        raise ValueError("accepted MASTER_RU package layout mismatch")
    manifest_raw = (root / "MASTER_RU.acceptance.json").read_bytes()
    if (
        len(manifest_raw) != ACCEPTANCE_MANIFEST_BYTES
        or sha256(manifest_raw) != ACCEPTANCE_MANIFEST_SHA256
    ):
        raise ValueError("accepted MASTER_RU manifest identity mismatch")
    manifest = json.loads(manifest_raw)
    if manifest.get("state") != "ACCEPTED_MASTER_RU_REPO_INPUT":
        raise ValueError("MASTER_RU acceptance state mismatch")
    raw = (root / "MASTER_RU.md").read_bytes()
    package = manifest.get("package", {})
    if manifest.get("source_candidate") != {
        "path": "MASTER_RU.md",
        "byte_count": ACCEPTED_SOURCE_MASTER_RU_BYTES,
        "sha256": ACCEPTED_SOURCE_MASTER_RU_SHA256,
    }:
        raise ValueError("accepted MASTER_RU source candidate provenance mismatch")
    markdown_identity = package.get("markdown", {})
    if markdown_identity != {
        "path": "MASTER_RU.md",
        "byte_count": PROMOTED_MASTER_RU_BYTES,
        "sha256": PROMOTED_MASTER_RU_SHA256,
    }:
        raise ValueError("accepted MASTER_RU markdown identity mismatch")
    if len(raw) != PROMOTED_MASTER_RU_BYTES or sha256(raw) != PROMOTED_MASTER_RU_SHA256:
        raise ValueError("accepted MASTER_RU file identity mismatch")
    en = canonical_en_report(master_en_root)
    if manifest.get("source_master_en") != en:
        raise ValueError("accepted MASTER_RU MASTER_EN provenance mismatch")
    registry_identity = verify_terminology_registry(terminology_registry)
    if manifest.get("glossary") != LEGACY_GLOSSARY_PROVENANCE:
        raise ValueError("accepted MASTER_RU glossary provenance mismatch")
    counts = validate_ru_markdown(
        raw.decode("utf-8"),
        (master_en_root / "MASTER_EN.md").read_text(encoding="utf-8"),
    )
    if package.get("counts") != counts:
        raise ValueError("accepted MASTER_RU structural manifest mismatch")
    if package.get("semantic_anchor_realignments") != len(RU_HEADING_TARGETS):
        raise ValueError("accepted MASTER_RU semantic anchor manifest mismatch")
    if package.get("handout_projection") != {
        "body_handout_duplicates_suppressed": 2,
        "keeper_notes_relocated_to_appendix": 1,
        "appendix_handout_duplicates_suppressed": 1,
        "body_handout_links": 8,
        "appendix_handout_anchors_added": 2,
        "decorative_handout_assets_suppressed": 5,
    }:
        raise ValueError("accepted MASTER_RU handout projection manifest mismatch")
    if package.get("front_matter_projection") != {
        "source_cover_links_added": 1,
        "credits_sections_suppressed": 1,
        "content_warning_blocks_suppressed": 1,
    }:
        raise ValueError("accepted MASTER_RU front-matter projection manifest mismatch")
    expected_replacements = {
        f"{old} -> {new}": expected_count
        for old, new, expected_count in TERMINOLOGY_REPLACEMENTS
    }
    if package.get("terminology_replacements") != expected_replacements:
        raise ValueError("accepted MASTER_RU terminology manifest mismatch")
    inventory = verify_asset_inventory(root / "assets")
    if package.get("asset_count") != inventory["asset_count"]:
        raise ValueError("accepted MASTER_RU asset count mismatch")
    if package.get("asset_inventory_sha256") != inventory["inventory_sha256"]:
        raise ValueError("accepted MASTER_RU asset inventory mismatch")
    return {
        "state": "ACCEPTED_MASTER_RU_REPO_INPUT_VERIFIED",
        "markdown": markdown_identity,
        "source_master_en": en,
        "glossary": LEGACY_GLOSSARY_PROVENANCE,
        "terminology_registry": registry_identity,
        "asset_inventory": inventory,
        "counts": counts,
    }


def promote(
    candidate: Path,
    assets: Path,
    terminology_registry: Path,
    master_en_root: Path,
    target: Path,
    expected_master_sha256: str,
    accepted_on: str,
) -> dict[str, Any]:
    if target.exists():
        raise ValueError(f"refusing to overwrite accepted MASTER_RU target: {target}")
    stage = target.with_name(target.name + ".stage")
    if stage.exists():
        raise ValueError(f"MASTER_RU promotion stage already exists: {stage}")
    report, promoted_raw = inspect_candidate(
        candidate, assets, terminology_registry, master_en_root, expected_master_sha256
    )
    manifest = acceptance_manifest(report, accepted_on)
    stage.mkdir(parents=True)
    try:
        (stage / "MASTER_RU.md").write_bytes(promoted_raw)
        (stage / "assets").mkdir()
        for name in sorted(RU_RETAINED_ASSETS):
            shutil.copyfile(assets / name, stage / "assets" / name)
        (stage / "MASTER_RU.acceptance.json").write_bytes(manifest)
        stage.rename(target)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return verify_promoted(target, terminology_registry, master_en_root)


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--promote", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--assets", type=Path)
    parser.add_argument(
        "--terminology-registry",
        type=Path,
        default=DEFAULT_TERMINOLOGY_REGISTRY,
    )
    parser.add_argument("--master-en-root", type=Path, required=True)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--expected-master-sha256")
    parser.add_argument("--accepted-on")
    args = parser.parse_args()

    if args.verify:
        if args.target is None:
            raise SystemExit("--target is required with --verify")
        result = verify_promoted(
            args.target, args.terminology_registry, args.master_en_root
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        print("INNSMOUTH_ACCEPTED_MASTER_RU_REPO_INPUT_OK")
        return
    required = (args.candidate, args.assets, args.expected_master_sha256)
    if any(value is None for value in required):
        raise SystemExit(
            "--candidate, --assets and --expected-master-sha256 are required"
        )
    if args.preflight:
        result, _raw = inspect_candidate(
            args.candidate,
            args.assets,
            args.terminology_registry,
            args.master_en_root,
            args.expected_master_sha256,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        print("INNSMOUTH_MASTER_RU_PROMOTION_PREFLIGHT_OK")
        return
    if args.target is None or args.accepted_on is None:
        raise SystemExit("--target and --accepted-on are required with --promote")
    result = promote(
        args.candidate,
        args.assets,
        args.terminology_registry,
        args.master_en_root,
        args.target,
        args.expected_master_sha256,
        args.accepted_on,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("INNSMOUTH_MASTER_RU_PROMOTED")


if __name__ == "__main__":
    main()
