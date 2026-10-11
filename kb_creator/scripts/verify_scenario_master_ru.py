#!/usr/bin/env python3
"""Independent, standard-library-only verification for a MASTER_RU candidate."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import stat
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Sequence



HEX = re.compile(r"^[0-9A-F]{64}$")
PACKET_SCHEMA = "kb_creator.master_ru_packet_manifest.v1"
SUBMISSION_SCHEMA = "kb_creator.master_ru_submission.v1"
VERIFICATION_SCHEMA = "kb_creator.master_ru_independent_verification.v1"
PASS_STATE = "verified_candidate_pending_user_acceptance"
REQUIRED_QA_LABELS = {
    "accepted_master_en_identity", "ordered_unit_identity",
    "markdown_structure_preservation", "mechanics_preservation",
    "terminology_authority", "asset_identity", "independent_translation_qa",
}
_BATCH_KEYS = {"schema", "batch_id", "instructions", "units"}
_UNIT_KEYS = {
    "unit_id", "parent_unit_id", "part_index", "part_count", "page",
    "source_hash", "part_source_hash", "source_text", "ru_text",
}
_CSV_HEADER = (
    "source_term", "accepted_ru", "aliases", "bad_ru", "domain", "status",
    "source_scope", "decision_rule", "notes",
)
_MD_HEADER = ("English", "Принятый русский термин", "Примечание")
_COC7E_REQUIRED = frozenset({
    "STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU",
    "SAN", "HP", "MP", "MOV", "Move", "DB", "Build", "Damage bonus",
})
_COC7E_TRIGGERS = ("STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU")


class MasterRuVerificationError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": _sha_file(path)}


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MasterRuVerificationError(f"cannot read JSON: {path}") from error
    if not isinstance(value, dict):
        raise MasterRuVerificationError(f"JSON object required: {path}")
    return value


def _exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise MasterRuVerificationError(f"{label} closed schema mismatch")
    return value


def _seal_valid(value: dict[str, Any], key: str, label: str) -> None:
    digest = value.get(key)
    if not isinstance(digest, str) or not HEX.fullmatch(digest):
        raise MasterRuVerificationError(f"{label} seal missing")
    unsigned = {name: item for name, item in value.items() if name != key}
    if _sha_bytes(_canonical(unsigned)) != digest:
        raise MasterRuVerificationError(f"{label} seal mismatch")


def _is_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _contained(path: Path, root: Path, label: str, *, file: bool | None = None) -> Path:
    authority = root.resolve()
    target = path.resolve()
    try:
        target.relative_to(authority)
    except ValueError as error:
        raise MasterRuVerificationError(f"{label} escapes authority root") from error
    current = path
    while True:
        if current.exists() and _is_reparse(current):
            raise MasterRuVerificationError(f"{label} contains a reparse path")
        if current.resolve() == authority:
            break
        current = current.parent
    if file is True and not target.is_file():
        raise MasterRuVerificationError(f"{label} is not a file")
    if file is False and not target.is_dir():
        raise MasterRuVerificationError(f"{label} is not a directory")
    return target


def _safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise MasterRuVerificationError(f"unsafe {label} path")
    path = Path(value)
    if path.is_absolute() or path.drive or any(part in {"", ".", ".."} for part in path.parts):
        raise MasterRuVerificationError(f"unsafe {label} path")
    return path


def _resolve_identity(root: Path, record: object, label: str) -> Path:
    row = _exact(record, {"path", "bytes", "sha256"}, label)
    relative = _safe_relative(row["path"], label)
    path = _contained(root / relative, root, label, file=True)
    if path.stat().st_size != row["bytes"] or _sha_file(path) != row["sha256"]:
        raise MasterRuVerificationError(f"{label} identity mismatch")
    return path


def _line_class(line: str) -> str:
    stripped = line.lstrip()
    if re.fullmatch(r"<!--\s*source-page-\d{3,}\s*-->", stripped):
        return "source_page"
    if re.fullmatch(r'<a id="[^"]+"></a>', stripped):
        return "anchor"
    fence = re.match(r"^(`{3,}|~{3,})", stripped)
    if fence:
        return f"fence:{fence.group(1)[0]}:{len(fence.group(1))}"
    heading = re.match(r"^(#{1,6})\s+", stripped)
    if heading:
        return f"heading:{len(heading.group(1))}"
    if re.match(r"^>\s?", stripped):
        return "blockquote"
    if re.match(r"^(?:[-+*])\s+", stripped):
        return "unordered_list"
    if re.match(r"^\d+\.\s+", stripped):
        return "ordered_list"
    if stripped.startswith("|"):
        return "table"
    if re.match(r"^!\[[^\]]*\]\(", stripped):
        return "image"
    return "text"


def _mechanics(text: str) -> list[str]:
    """Return numeric mechanics, excluding a known OCR ``I``/``1`` artifact."""
    artifact = re.compile(r"(?<![\w])1\s+(?:am|have|asked)\b", flags=re.IGNORECASE)
    masked = artifact.sub(lambda match: match.group(0).replace("1", "I", 1), text)
    # MinerU sometimes removes only the separator around established mechanics.
    # Restore it narrowly; do not treat arbitrary number-word compounds as stats.
    labels = r"(?:STR|CON|SIZ|DEX|INT|APP|POW|EDU|SAN|HP|MP|MOV|DB|Build|Move)"
    masked = re.sub(rf"(?<!\w)({labels})(?=\d)", r"\1 ", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(?<!\w)(\d+)(?=(?:HP|MP|SAN|mph|kph|km/h|mi/h)\b)", r"\1 ", masked, flags=re.IGNORECASE)
    return sorted(re.findall(
        r"(?<![\w])(?:\d+d\d+(?:[+-]\d+)?|\d+%|\d+(?:[.,]\d+)?)(?![\w])",
        masked,
        flags=re.IGNORECASE,
    ))


def _represented_numbers(text: str) -> list[str]:
    return __import__(
        "kb_creator.pipeline.language_numeric", fromlist=["represented_numbers"]
    ).represented_numbers(text)
    masked = re.sub(r"<!--.*?-->|(?:!?)\[[^\]]*\]\([^)]*\)", " ", text, flags=re.S)
    masked = re.sub(r"(?<![\w])1\s+(?:am|have|asked)\b", lambda m: m.group(0).replace("1", "I", 1), masked, flags=re.I)
    masked = re.sub(r"(?<!\w)(\d+)(?=[A-Za-zА-Яа-я]{2,})", r"\1 ", masked)
    masked = re.sub(r"([A-Za-zА-Яа-я]{2,})(\d+)", r"\1 \2", masked)
    spans = []
    def take(pattern, convert):
        for match in pattern.finditer(masked):
            if not any(match.start() < end and match.end() > start for start, end, _ in spans): spans.append((match.start(), match.end(), convert(match)))
    clock_en = re.compile(r"(?<![\w])(?P<hour>1[0-2]|[1-9])(?::(?P<minute>[0-5]\d))?\s*(?P<meridiem>am|pm)\b", re.I)
    clock_ru = re.compile(r"(?<![\w])(?P<hour>\d{1,2})(?::(?P<minute>[0-5]\d))?\s*(?P<meridiem>утра|дня|вечера|ночи)\b", re.I)
    clock24 = re.compile(r"(?<![\w])(?P<hour>(?:[01]\d|2[0-3])):(?P<minute>[0-5]\d)(?!\d)")
    duration = re.compile(r"(?<![\w])(?P<value>\d+)\s*(?:h\b|ч(?:\b|аса\b|асов\b))", re.I)
    ordinal = re.compile(r"(?<![\w])(?P<value>\d+)(?:st|nd|rd|th|-(?:й|го|я|е|ю|ым|ом|ую|ая|ое|ые|ых|ими))\b", re.I)
    date = re.compile(r"(?<![\w])(?P<value>\d+)\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b", re.I)
    decade = re.compile(r"(?<![\w])(?P<value>\d{3,4})(?:s\b|-х(?:\s+год(?:ов|а)?)?\b)", re.I)
    def clock(match):
        hour, minute, marker = int(match.group("hour")), int(match.group("minute") or 0), match.groupdict().get("meridiem", "").casefold()
        if marker in {"pm", "вечера", "дня"} and hour != 12: hour += 12
        if marker in {"am", "утра", "ночи"} and hour == 12: hour = 0
        return f"time:{hour * 60 + minute}"
    take(clock_en, clock); take(clock_ru, clock); take(clock24, lambda m: f"time:{int(m.group('hour')) * 60 + int(m.group('minute'))}"); take(duration, lambda m: f"duration_hours:{int(m.group('value'))}"); take(ordinal, lambda m: f"number:{int(m.group('value'))}"); take(date, lambda m: f"number:{int(m.group('value'))}"); take(decade, lambda m: f"number:{int(m.group('value'))}")
    for match in re.finditer(r"(?<![\w])(?:\d+d\d+(?:[+-]\d+)?|\d+%|\d+(?:[.,]\d+)?)(?![\w])", masked, re.I):
        if any(match.start() < end and match.end() > start for start, end, _ in spans): continue
        value = match.group(0).replace(",", "."); spans.append((match.start(), match.end(), f"dice:{value.casefold()}" if "d" in value.casefold() else f"percent:{value[:-1]}" if value.endswith("%") else f"number:{value}"))
    return sorted(row[2] for row in spans)


def _signature(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    return {
        "page_markers": re.findall(r"<!--\s*source-page-\d{3,}\s*-->", text),
        "anchors": re.findall(r'<a id="[^"]+"></a>', text),
        "image_targets": re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text),
        "link_targets": [target for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)", text)],
        "headings": [len(match.group(1)) for match in re.finditer(r"(?m)^(#{1,6})\s+", text)],
        "list_markers": re.findall(r"(?m)^\s*(?:[-+*]|\d+\.)\s+", text),
        "table_cells": [line.count("|") for line in lines if line.lstrip().startswith("|")],
        "mechanics": _represented_numbers(text),
        "represented_numbers": _represented_numbers(text),
        "line_classes": [_line_class(line) for line in lines],
        "hard_breaks": [line.endswith("  ") for line in lines],
        "explicit_br": [len(re.findall(r"<br\s*/?>", line, flags=re.IGNORECASE)) for line in lines],
        "emphasis_delimiters": [re.findall(r"(?<!\\)(?:\*\*|__|~~|\*|_)", line) for line in lines],
    }


def _source_units(text: str) -> list[dict[str, Any]]:
    blocks = [part.strip() for part in re.split(r"\n[ \t]*\n", text) if part.strip()]
    return [
        {
            "unit_id": f"unit-{index:05d}",
            "page": int(match.group(1)) if (match := re.search(r"<!--\s*source-page-(\d{3,})\s*-->", block)) else None,
            "source_hash": _sha_bytes(block.encode("utf-8")),
            "source_text": block,
        }
        for index, block in enumerate(blocks, 1)
    ]


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _term_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MasterRuVerificationError(f"empty terminology {label}")
    return " ".join(value.strip().split())


def _variants(value: object, label: str) -> tuple[str, ...]:
    if value in (None, "", []):
        return ()
    raw = value if isinstance(value, list) else str(value).split(";") if isinstance(value, str) else None
    if raw is None or not raw:
        raise MasterRuVerificationError(f"malformed terminology {label}")
    result = tuple(_term_text(item, label) for item in raw)
    if len({_normalize(item) for item in result}) != len(result):
        raise MasterRuVerificationError(f"duplicate terminology {label}")
    return result


def _domain(value: object, label: str, *, fallback: str = "general") -> str:
    if value in (None, ""):
        return fallback
    result = _term_text(value, label).casefold()
    if re.fullmatch(r"[a-z0-9][a-z0-9 ./_-]*", result) is None:
        raise MasterRuVerificationError(f"malformed terminology {label}")
    return result


def _md_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return tuple(cell.strip() for cell in re.split(r"(?<!\\)\|", stripped[1:-1]))


def _usage_rule(notes: str) -> dict[str, Any] | None:
    marker = "Контекст JSON:"
    if marker not in notes:
        return None
    if notes.count(marker) != 1:
        raise MasterRuVerificationError("duplicate terminology context")
    rule, _ = json.JSONDecoder().raw_decode(notes.split(marker, 1)[1].lstrip())
    if not isinstance(rule, dict) or set(rule) != {"selector", "prose"} or rule["selector"] != "numeric_label_vs_prose":
        raise MasterRuVerificationError("unsupported terminology context")
    forms = rule["prose"]
    if not isinstance(forms, dict) or set(forms) != {"target", "aliases", "bad"}:
        raise MasterRuVerificationError("invalid prose terminology")
    accepted = [_term_text(forms["target"], "context target"), *_variants(forms["aliases"], "context aliases")]
    if {_normalize(x) for x in accepted} & {_normalize(x) for x in _variants(forms["bad"], "context bad")}:
        raise MasterRuVerificationError("context terminology conflict")
    return rule


def _effective_terms(value: dict[str, Any]) -> list[dict[str, Any]]:
    """Independently derive effective pairs and context from embedded sources."""
    required = {"schema", "system", "book_id", "sources", "terms", "context", "conflicts", "glossary_sha256"}
    if set(value) != required or value["system"] != "coc" or value["conflicts"] or set(value["sources"]) != {"registry", "overlay"}:
        raise MasterRuVerificationError("invalid effective glossary contract")
    _seal_valid(value, "glossary_sha256", "effective glossary")
    book_id = _term_text(value["book_id"], "book id")
    data = {}
    for role, snapshot in value["sources"].items():
        if set(snapshot) != {"reference", "bytes", "sha256", "content_base64"}:
            raise MasterRuVerificationError("invalid glossary snapshot")
        raw = base64.b64decode(snapshot["content_base64"], validate=True)
        if snapshot["bytes"] != len(raw) or snapshot["sha256"] != _sha_bytes(raw):
            raise MasterRuVerificationError("glossary snapshot identity mismatch")
        data[role] = raw
    with tempfile.TemporaryDirectory(prefix="coc-glossary-verify-") as folder:
        registry, overlay = Path(folder) / "registry.csv", Path(folder) / "overlay.json"
        registry.write_bytes(data["registry"]); overlay.write_bytes(data["overlay"])
        shared, book = _raw_terms(registry, "registry", allow_empty=True), _raw_terms(overlay, "overlay", allow_empty=True)
    terms = {}
    for role, rows in (("shared", shared), ("book", book)):
        seen = set()
        for row in rows:
            key = _normalize(row["source"])
            if key in seen:
                raise MasterRuVerificationError("duplicate effective glossary source")
            seen.add(key)
            candidate = {"source": row["source"], "target": row["target"], "aliases": list(row["aliases"]),
                         "bad_ru": list(row["bad"]), "domain": row["domain"]}
            if row.get("usage"):
                candidate["usage"] = row["usage"]
            if key not in terms:
                terms[key] = candidate
                continue
            current = terms[key]
            if _normalize(current["target"]) != _normalize(candidate["target"]) or (candidate["domain"] != "general" and current["domain"] != candidate["domain"]):
                raise MasterRuVerificationError("effective glossary conflict")
            for field in ("aliases", "bad_ru"):
                unique = {}
                for item in current[field] + candidate[field]:
                    unique.setdefault(_normalize(item), item)
                current[field] = list(unique.values())
    for row in terms.values():
        row["aliases"] = [a for a in row["aliases"] if _normalize(a) != _normalize(row["target"])]
    expected = [terms[key] for key in sorted(terms)]
    raw_rows = list(csv.DictReader(io.StringIO(data["registry"].decode("utf-8-sig"), newline="")))
    contexts = []
    for row in raw_rows:
        match = re.search(r"Определение:\s*(.*?)(?=\s*Источник:|\s*Область:|$)", row["notes"], re.S)
        definition = match[1].strip() if match else ""
        contexts.append({**row, "definition": definition, "definition_status": "source_recorded" if definition else "not_recorded"})
    expected_context = {"shared_rows": contexts,
        "book_rows": [{"source": r["source"], "target": r["target"], "aliases": list(r["aliases"]), "bad_ru": list(r["bad"]), "domain": r["domain"],
                       "book_id": book_id, "status": "selected_book_choice", "definition_status": "not_recorded"} for r in book],
        "policy": "Shared accepted rules plus explicit book choices. Global review_required rows are context only. No automatic replacement or edition conversion."}
    if value["terms"] != expected or value["context"] != expected_context:
        raise MasterRuVerificationError("effective glossary derivation mismatch")
    return expected


def _raw_terms(path: Path, authority: str, *, allow_empty: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    usage_by_source = {}
    if path.suffix.lower() == ".json":
        value = _read(path)
        if value.get("schema") == "kb_creator.effective_coc_glossary.v1":
            try:
                effective = _effective_terms(value)
                usage_by_source = {row["source"]: row["usage"] for row in effective if "usage" in row}
                value = {"terms": [{k: v for k, v in row.items() if k != "usage"} for row in effective]}
            except (ValueError, KeyError, TypeError) as error:
                raise MasterRuVerificationError(f"invalid effective glossary: {error}") from error
        if set(value) != {"terms"} or not isinstance(value["terms"], list):
            raise MasterRuVerificationError(f"JSON terminology is not closed: {authority}")
        allowed = {"source", "en", "target", "ru", "aliases", "bad_ru", "bad", "forbidden", "domain"}
        for index, item in enumerate(value["terms"], 1):
            if not isinstance(item, dict) or not set(item).issubset(allowed):
                raise MasterRuVerificationError(f"malformed terminology row {index}: {authority}")
            sources = [item[key] for key in ("source", "en") if key in item]
            targets = [item[key] for key in ("target", "ru") if key in item]
            bad = [item[key] for key in ("bad_ru", "bad", "forbidden") if key in item]
            if len(sources) != 1 or len(targets) != 1 or len(bad) > 1:
                raise MasterRuVerificationError(f"ambiguous terminology row {index}: {authority}")
            rows.append({"source": _term_text(sources[0], "source"), "target": _term_text(targets[0], "target"), "aliases": _variants(item.get("aliases"), "aliases"), "bad": _variants(bad[0] if bad else None, "bad"), "domain": _domain(item.get("domain"), "domain"), "domain_explicit": "domain" in item, "authority": authority})
    elif path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != _CSV_HEADER:
                raise MasterRuVerificationError(f"CSV terminology header mismatch: {authority}")
            for index, item in enumerate(reader, 2):
                if None in item or set(item) != set(_CSV_HEADER):
                    raise MasterRuVerificationError(f"malformed CSV terminology row {index}: {authority}")
                if _term_text(item["status"], "status").casefold() != "accepted":
                    continue
                rows.append({"source": _term_text(item["source_term"], "source"), "target": _term_text(item["accepted_ru"], "target"), "aliases": _variants(item["aliases"], "aliases"), "bad": _variants(item["bad_ru"], "bad"), "domain": _domain(item["domain"], "domain"), "domain_explicit": True, "authority": authority})
                rule = _usage_rule(item["notes"])
                if rule:
                    usage_by_source[rows[-1]["source"]] = rule
    elif path.suffix.lower() == ".md":
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        found = False
        index = 0
        while index < len(lines):
            if _md_cells(lines[index]) != _MD_HEADER:
                index += 1
                continue
            found = True
            if index + 1 >= len(lines):
                raise MasterRuVerificationError(f"Markdown terminology delimiter missing: {authority}")
            delimiter = _md_cells(lines[index + 1])
            if delimiter is None or len(delimiter) != 3 or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in delimiter):
                raise MasterRuVerificationError(f"Markdown terminology delimiter mismatch: {authority}")
            index += 2
            count = 0
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                cells = _md_cells(lines[index])
                if cells is None or len(cells) != 3:
                    raise MasterRuVerificationError(f"malformed Markdown terminology row: {authority}")
                rows.append({"source": _term_text(cells[0], "source"), "target": _term_text(cells[1], "target"), "aliases": (), "bad": (), "domain": "skill", "domain_explicit": False, "authority": authority})
                index += 1
                count += 1
            if not count:
                raise MasterRuVerificationError(f"empty Markdown terminology table: {authority}")
        if not found:
            raise MasterRuVerificationError(f"Markdown terminology header mismatch: {authority}")
    else:
        raise MasterRuVerificationError(f"unsupported terminology authority: {authority}")
    if not rows and not allow_empty:
        raise MasterRuVerificationError(f"terminology authority has zero accepted pairs: {authority}")
    for row in rows:
        if row["source"] in usage_by_source:
            row["usage"] = usage_by_source[row["source"]]
    return rows


def _terms(authorities: Sequence[tuple[str, Path]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    seen: set[tuple[str, str]] = set()
    for authority, path in authorities:
        for row in _raw_terms(path, authority):
            key = _normalize(row["source"])
            if (authority, key) in seen:
                raise MasterRuVerificationError(f"duplicate terminology source in {authority}")
            seen.add((authority, key))
            accepted = (row["target"], *row["aliases"])
            accepted_keys = {_normalize(item) for item in accepted}
            bad_keys = {_normalize(item) for item in row["bad"]}
            if len(accepted_keys) != len(accepted) or accepted_keys & bad_keys:
                raise MasterRuVerificationError(f"conflicting terminology variants: {row['source']}")
            current = merged.get(key)
            if current is None:
                merged[key] = {**row, "targets": list(accepted), "bad": list(row["bad"]), "authorities": [authority]}
                continue
            if _normalize(current["target"]) != _normalize(row["target"]):
                raise MasterRuVerificationError(f"conflicting terminology source: {row['source']}")
            if current["domain_explicit"] and row["domain_explicit"]:
                if current["domain"] != row["domain"]:
                    raise MasterRuVerificationError(f"conflicting terminology domain: {row['source']}")
            elif row["domain_explicit"]:
                current["domain"] = row["domain"]
                current["domain_explicit"] = True
            elif not current["domain_explicit"] and current["domain"] != row["domain"]:
                raise MasterRuVerificationError(f"conflicting implicit terminology domain: {row['source']}")
            current_accepted = {_normalize(item) for item in current["targets"]}
            current_bad = {_normalize(item) for item in current["bad"]}
            if current_accepted & bad_keys or accepted_keys & current_bad:
                raise MasterRuVerificationError(f"conflicting terminology variants: {row['source']}")
            current["targets"].extend(item for item in accepted if _normalize(item) not in current_accepted)
            current["bad"].extend(item for item in row["bad"] if _normalize(item) not in current_bad)
            current["authorities"].append(authority)
    return list(merged.values())


def _has_coc7e_statblock(source_text: str) -> bool:
    return sum(
        re.search(rf"(?<!\w){re.escape(term)}\s+(?:\d+|[-—?])", source_text, flags=re.IGNORECASE) is not None
        for term in _COC7E_TRIGGERS
    ) >= 5


def _verify_coc7e_profile(terms: Sequence[dict[str, Any]], source_text: str) -> None:
    if not _has_coc7e_statblock(source_text):
        return
    available = {_normalize(str(term["source"])) for term in terms}
    missing = sorted(term for term in _COC7E_REQUIRED if _normalize(term) not in available)
    if missing:
        raise MasterRuVerificationError(
            "CoC 7e statblock terminology profile is incomplete: " + ", ".join(missing)
        )


def _present(term: str, text: str) -> bool:
    words = re.escape(term).replace(r"\ ", r"\s+")
    return re.search(rf"(?<!\w){words}(?!\w|-+\s*[a-z])", text, flags=re.IGNORECASE) is not None


_ABILITY_FIELDS = frozenset({"skill", "skills", "ability", "abilities", "proficiency", "proficiencies"})
_IDENTITY_FIELDS = frozenset({
    "occupation", "occupations", "profession", "professions", "career", "careers",
    "name", "names", "role", "roles", "cast", "character", "characters",
})
_STATBLOCK_LABEL_ONLY_SOURCES = frozenset({"build", "move"})


def _statblock_field_applicability(source_term: str, source_text: str) -> dict[str, Any]:
    escaped = re.escape(source_term).replace(r"\ ", r"\s+")
    matcher = re.compile(
        rf"(?<!\w){escaped}\s*:?\s*(?:\d+|[-—?]|none\b|varies\b)",
        flags=re.IGNORECASE,
    )
    matches = list(matcher.finditer(source_text))
    return {
        "applicability": (
            "required_general" if matches else "excluded_non_statblock_context"
        ),
        "occurrences": len(matches),
        "required_occurrences": len(matches),
        "excluded_occurrences": 0 if matches else int(_present(source_term, source_text)),
        "ambiguous_occurrences": 0,
        "source_lines": [source_text.count("\n", 0, match.start()) for match in matches],
    }


def _field_name(line: str) -> str | None:
    found = re.match(
        r"^\s*(?:>\s*)?(?:\*\*)?([A-Za-z][A-Za-z _/-]{1,40}):(?:\*\*)?",
        line,
    )
    return (
        " ".join(found.group(1).casefold().replace("/", " ").split())
        if found is not None
        else None
    )


def _skill_applicability(source_term: str, source_text: str) -> dict[str, Any]:
    # The verifier keeps a standard-library import surface, but uses the same
    # occurrence classifier as the producer when executed from this package.
    return __import__(
        "kb_creator.pipeline.language_context", fromlist=["skill_context"]
    ).skill_context(source_term, source_text)
    words = re.escape(source_term).replace("\\ ", r"\s+")
    pattern = re.compile(rf"(?<!\w)(?:\*{{2}}|__)?{words}(?:\*{{2}}|__)?(?!\w)", re.I)
    rows = []
    for match in pattern.finditer(source_text):
        line_start = source_text.rfind("\n", 0, match.start()) + 1; line_end = source_text.find("\n", match.end()); line_end = len(source_text) if line_end < 0 else line_end
        line = source_text[line_start:line_end]; left = source_text[max(line_start, match.start() - 120):match.start()]; right = source_text[match.end():min(line_end, match.end() + 120)]
        label = re.match(r"^\s*(?:>\s*)?(?:\*\*)?([A-Za-z][A-Za-z _/-]{1,40}):", line); label_name = " ".join(label.group(1).casefold().replace("/", " ").split()) if label else ""
        explicit = re.search(r"(?:rolls?|checks?|tests?|success|failure|reveal|notice|detect|identify)\b|\d{1,3}%", right, re.I)
        alternatives = re.search(r"\b(?:using|use|with)\b", left, re.I) and re.search(r"\b(?:or|and|roles?)\b", right, re.I)
        split_lowercase = re.match(r"-\s+[a-z]", right) is not None or re.match(r"[a-z]\s*-", left[-4:]) is not None
        non_skill = label_name in {"occupation", "occupations", "profession", "professions", "career", "careers", "name", "names", "role", "roles", "cast", "character", "characters"}
        if label_name in {"skill", "skills", "ability", "abilities", "proficiency", "proficiencies"} or explicit or alternatives or re.search(r"\b(?:use|using|hard|extreme|opposed|pushed)\s+$", left, re.I) or re.search(r"\*\s*\d{1,3}%", right): kind = "required_skill"
        elif split_lowercase or non_skill or match.group().lstrip("*_ ")[:1].islower() or re.search(r"\b(?:works?|employed|hired|occupation|profession|career|job)\s*$", left, re.I): kind = "excluded_non_skill_context"
        else: kind = "ambiguous"
        rows.append({"line": source_text.count("\n", 0, match.start()), "classification": kind, "start": match.start(), "end": match.end(), "text": re.sub(r"[*_]", "", match.group(0))})
    counts = {kind: sum(row["classification"] == kind for row in rows) for kind in ("required_skill", "excluded_non_skill_context", "ambiguous")}
    return {"applicability": "ambiguous" if counts["ambiguous"] else ("required_skill" if counts["required_skill"] else "excluded_non_skill_context"), "occurrences": len(rows), "required_occurrences": counts["required_skill"], "excluded_occurrences": counts["excluded_non_skill_context"], "ambiguous_occurrences": counts["ambiguous"], "source_lines": [row["line"] for row in rows], "occurrence_rows": rows}
    escaped = re.escape(source_term).replace(r"\ ", r"\s+")
    matcher = re.compile(rf"(?<!\w){escaped}(?!\w)", flags=re.IGNORECASE)
    classifications: list[tuple[int, str]] = []
    for occurrence in matcher.finditer(source_text):
        line_number = source_text.count("\n", 0, occurrence.start())
        start = source_text.rfind("\n", 0, occurrence.start()) + 1
        end = source_text.find("\n", occurrence.end())
        end = len(source_text) if end == -1 else end
        source_line = source_text[start:end]
        field = _field_name(source_line)
        prefix = source_text[max(start, occurrence.start() - 96):occurrence.start()]
        suffix = source_text[occurrence.end():min(end, occurrence.end() + 96)]
        if field in _ABILITY_FIELDS:
            classification = "required_skill"
        elif field in _IDENTITY_FIELDS:
            classification = "excluded_non_skill_context"
        elif (
            occurrence.start() >= 2 and source_text[occurrence.start() - 1] == "-"
            and source_text[occurrence.start() - 2].isalnum()
        ) or (
            occurrence.end() + 1 < len(source_text) and source_text[occurrence.end()] == "-"
            and source_text[occurrence.end() + 1].isalnum()
        ):
            classification = "excluded_non_skill_context"
        elif occurrence.group()[0].islower():
            classification = "excluded_non_skill_context"
        else:
            suffix_is_mechanic = re.search(
                r"^\s*(?:\([^\r\n)]{1,80}\)\s*)?(?:(?:rolls?|checks?|tests?|skills?|rating|score|attempt|use|success|failure)\b|will\s+(?:reveal|uncover|expose|show|allow|find|notice|detect|identify|locate)\b|\d{1,3}%(?=\s|$|[,.;:]))",
                suffix,
                flags=re.IGNORECASE,
            ) is not None
            prefix_is_mechanic = re.search(
                r"\b(?:skill|use|using|successful|failed|regular|hard|extreme|opposed|pushed)\s+$",
                prefix,
                flags=re.IGNORECASE,
            ) is not None or re.search(
                r"\b(?:use|using)\s+(?:[A-Za-z][\w'-]*(?:\s+[A-Za-z][\w'-]*)?\s*(?:,|\bor\b|\band\b)\s*)+$",
                prefix,
                flags=re.IGNORECASE,
            ) is not None
            prefixed_job = re.search(
                r"\b(?:works? as|employed as|hired as|occupation|profession|career|job)\s+(?:[A-Za-z][\w'-]*\s+){0,4}$",
                prefix,
                flags=re.IGNORECASE,
            ) is not None
            titled_person = re.search(
                r"\b(?:a|an)\s+(?:[A-Za-z][\w'-]*\s+){0,4}$",
                prefix,
                flags=re.IGNORECASE,
            ) is not None
            job_clause = re.search(
                r"^\s*[,;\u2014-]?\s*(?:hired|employed|working|who|whose|responsible|assigned)\b",
                suffix,
                flags=re.IGNORECASE,
            ) is not None
            academic_use = re.search(
                r"^\s*(?:and\s+[A-Za-z][\w'-]*\s+)?(?:students?|lecturers?|teachers?|professors?|department|course|class|degree|major|studies)\b",
                suffix,
                flags=re.IGNORECASE,
            ) is not None
            article_skill_will = re.search(
                r"\b(?:a|an)\s+$", prefix, flags=re.IGNORECASE
            ) is not None and re.search(
                r"^\s+(?:from|by|with|for|among)\b[^.,;:]{0,80}?\bwill\s+(?:reveal|uncover|expose|show|allow|find|notice|detect|identify|locate)\b",
                suffix,
                flags=re.IGNORECASE,
            ) is not None
            if suffix_is_mechanic or prefix_is_mechanic or article_skill_will:
                classification = "required_skill"
            elif prefixed_job or (titled_person and job_clause) or academic_use:
                classification = "excluded_non_skill_context"
            else:
                classification = "ambiguous"
        classifications.append((line_number, classification))
    required_count = sum(kind == "required_skill" for _, kind in classifications)
    excluded_count = sum(kind == "excluded_non_skill_context" for _, kind in classifications)
    ambiguous_count = sum(kind == "ambiguous" for _, kind in classifications)
    applicability = (
        "ambiguous" if ambiguous_count else
        "required_skill" if required_count else
        "excluded_non_skill_context"
    )
    return {
        "applicability": applicability,
        "occurrences": len(classifications),
        "required_occurrences": required_count,
        "excluded_occurrences": excluded_count,
        "ambiguous_occurrences": ambiguous_count,
        "source_lines": [line for line, _ in classifications],
    }


def _context_forms(term: dict[str, Any], source_text: str) -> dict[str, Any]:
    result = dict(term)
    rule = term.get("usage")
    if not rule:
        return result
    token = rf"(?<!\w){re.escape(term['source'])}(?!\w)"
    occurrences = list(re.finditer(token, source_text, flags=re.I))
    labels = list(re.finditer(token + r"\s*:?\s*(?:\d+|[-—?]|none\b|varies\b)", source_text, flags=re.I))
    if labels:
        result["usage_ambiguous"] = len(labels) != len(occurrences)
    else:
        prose = rule["prose"]
        result.update(target=prose["target"], aliases=tuple(prose["aliases"]),
                      targets=[prose["target"], *prose["aliases"]], bad=list(prose["bad"]))
    return result


def _applicability(term: dict[str, Any], source_text: str) -> dict[str, Any]:
    if term.get("usage_ambiguous"):
        return {"applicability": "ambiguous", "occurrences": 1, "required_occurrences": 0,
                "excluded_occurrences": 0, "ambiguous_occurrences": 1, "source_lines": []}
    if term["domain"] == "skill":
        return _skill_applicability(term["source"], source_text)
    if _normalize(str(term["source"])) in _STATBLOCK_LABEL_ONLY_SOURCES:
        return _statblock_field_applicability(str(term["source"]), source_text)
    escaped = re.escape(term["source"]).replace(r"\ ", r"\s+")
    count = len(re.findall(rf"(?<!\w){escaped}(?!\w|-+\s*[a-z])", source_text, flags=re.IGNORECASE))
    return {
        "applicability": "required_general", "occurrences": count,
        "required_occurrences": count, "excluded_occurrences": 0,
        "ambiguous_occurrences": 0, "source_lines": [],
    }


def _accepted_target_ranges(accepted_targets: Sequence[str], text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for target in accepted_targets:
        escaped_target = re.escape(target).replace(r"\ ", r"\s+")
        ranges.extend(
            match.span()
            for match in re.finditer(
                rf"(?<!\w){escaped_target}(?!\w)", text, flags=re.IGNORECASE
            )
        )
    return ranges


def _replace_declared(
    text: str, old: str, new: str, accepted_targets: Sequence[str] = ()
) -> tuple[str, int]:
    escaped = re.escape(old).replace(r"\ ", r"\s+")
    target_ranges = _accepted_target_ranges(accepted_targets, text)
    parts: list[str] = []
    cursor = 0
    count = 0
    for match in re.finditer(rf"(?<!\w){escaped}(?!\w)", text, flags=re.IGNORECASE):
        parts.append(text[cursor:match.start()])
        if any(start <= match.start() and match.end() <= end for start, end in target_ranges):
            parts.append(match.group())
        else:
            parts.append(new)
            count += 1
        cursor = match.end()
    parts.append(text[cursor:])
    return "".join(parts), count


def _bad_variant_present(bad: str, accepted_targets: Sequence[str], text: str) -> bool:
    """Find a bad variant unless its occurrence is wholly inside a target."""
    escaped_bad = re.escape(bad).replace(r"\ ", r"\s+")
    target_ranges = _accepted_target_ranges(accepted_targets, text)
    return any(
        not any(start <= match.start() and match.end() <= end for start, end in target_ranges)
        for match in re.finditer(rf"(?<!\w){escaped_bad}(?!\w)", text, flags=re.IGNORECASE)
    )


def _normalize_declared_terms(
    source_text: str,
    ru_text: str,
    terms: Sequence[dict[str, Any]],
    unit_id: str,
) -> tuple[str, list[dict[str, Any]]]:
    output = ru_text
    events: list[dict[str, Any]] = []
    for term in terms:
        if not _present(str(term["source"]), source_text):
            continue
        term = _context_forms(term, source_text)
        context = _applicability(term, source_text)
        if context["applicability"] == "ambiguous":
            continue
        variants = sorted(
            {str(term["source"]), *(str(value) for value in term["bad"])},
            key=lambda value: (-len(value), value.casefold()),
        )
        if term["domain"] == "skill":
            source_lines = source_text.splitlines()
            output_lines = output.splitlines(keepends=True)
            if len(source_lines) != len(output_lines):
                continue
            for line_number, source_line in enumerate(source_lines):
                if not _present(str(term["source"]), source_line):
                    continue
                line_context = _skill_applicability(str(term["source"]), source_line)
                if line_context["applicability"] != "required_skill":
                    continue
                for old in variants:
                    output_lines[line_number], count = _replace_declared(
                        output_lines[line_number], old, str(term["target"]), term["targets"]
                    )
                    if count:
                        events.append({
                            "unit_id": unit_id, "source": term["source"],
                            "from": old, "to": term["target"],
                            "count": count, "line": line_number,
                        })
            output = "".join(output_lines)
            continue
        if context["applicability"] != "required_general":
            continue
        for old in variants:
            output, count = _replace_declared(
                output, old, str(term["target"]), term["targets"]
            )
            if count:
                events.append({
                    "unit_id": unit_id, "source": term["source"],
                    "from": old, "to": term["target"],
                    "count": count, "line": None,
                })
    return output, events


def _inventory(root: Path) -> tuple[list[dict[str, Any]], str]:
    rows = []
    for path in sorted((item for item in root.rglob("*") if item.is_file() and item.name != "INVENTORY.json"), key=lambda item: item.relative_to(root).as_posix()):
        rows.append({"path": path.relative_to(root).as_posix(), **_identity(path)})
    digest = _sha_bytes("".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in rows).encode("utf-8"))
    return rows, digest


def verify_candidate(packet_root: Path, submission_path: Path, candidate_root: Path, contract_path: Path, authority_root: Path) -> dict[str, Any]:
    authority = authority_root.resolve()
    packet = _contained(packet_root, authority, "packet root", file=False)
    submission_file = _contained(submission_path, authority, "submission", file=True)
    candidate = _contained(candidate_root, authority, "candidate root", file=False)
    contract_file = contract_path.resolve()
    if not contract_file.is_file() or _is_reparse(contract_path):
        raise MasterRuVerificationError("publication contract is missing or reparse")
    contract = _read(contract_file)
    required_qa = contract.get("master_ru", {}).get("required_qa")
    scenario_id = contract.get("scenario", {}).get("id")
    if (
        not isinstance(required_qa, list)
        or len(required_qa) != len(set(required_qa))
        or set(required_qa) != REQUIRED_QA_LABELS
        or not isinstance(scenario_id, str)
    ):
        raise MasterRuVerificationError("publication contract MASTER_RU QA requirements are invalid")

    manifest_path = packet / "packet_manifest.json"
    manifest = _read(manifest_path)
    _exact(manifest, {"schema", "scenario_id", "accepted_master_en", "master_en", "terminology", "tasks", "batches", "counts", "packet_policy", "manifest_sha256"}, "packet manifest")
    _seal_valid(manifest, "manifest_sha256", "packet manifest")
    if manifest["schema"] != PACKET_SCHEMA or manifest["packet_policy"] != "ordered_hash_bound_units_v1" or manifest["scenario_id"] != scenario_id:
        raise MasterRuVerificationError("packet policy or scenario mismatch")
    master_en = _resolve_identity(authority, manifest["master_en"], "MASTER_EN")
    accepted_master = _resolve_identity(authority, manifest["accepted_master_en"], "MASTER_EN acceptance")
    acceptance = _read(accepted_master)
    _exact(acceptance, {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"}, "MASTER_EN acceptance")
    _seal_valid(acceptance, "receipt_sha256", "MASTER_EN acceptance")
    expected_master_record = {"path": master_en.relative_to(authority).as_posix(), **_identity(master_en)}
    if acceptance["schema"] != "kb_creator.artifact_acceptance.v1" or acceptance["scenario_id"] != scenario_id or acceptance["artifact_kind"] != "master_en" or acceptance["decision"] != "accepted" or acceptance["recorder_role"] != "main_orchestrator" or acceptance["candidate"] != expected_master_record:
        raise MasterRuVerificationError("MASTER_EN acceptance mismatch")
    _resolve_identity(authority, acceptance["producer_stage"], "MASTER_EN producer")
    if not isinstance(acceptance["evidence"], list) or not acceptance["evidence"]:
        raise MasterRuVerificationError("MASTER_EN acceptance evidence missing")
    for index, record in enumerate(acceptance["evidence"]):
        _resolve_identity(authority, record, f"MASTER_EN evidence {index}")

    term_authorities = []
    terminology_roles: set[str] = set()
    for row in manifest["terminology"]:
        _exact(row, {"role", "file"}, "terminology record")
        if not isinstance(row["role"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", row["role"]) or row["role"] in terminology_roles:
            raise MasterRuVerificationError("duplicate or invalid terminology role")
        terminology_roles.add(row["role"])
        term_authorities.append((row["role"], _resolve_identity(authority, row["file"], f"terminology {row['role']}")))
    if not term_authorities:
        raise MasterRuVerificationError("packet has no terminology authority")
    terms = _terms(term_authorities)
    _verify_coc7e_profile(terms, master_en.read_text(encoding="utf-8"))

    tasks_path = _resolve_identity(packet, manifest["tasks"], "translation tasks")
    tasks = _read(tasks_path)
    _exact(tasks, {"schema", "scenario_id", "units"}, "translation tasks")
    if tasks["schema"] != "kb_creator.master_ru_translation_tasks.v1" or tasks["scenario_id"] != scenario_id or not isinstance(tasks["units"], list) or not tasks["units"]:
        raise MasterRuVerificationError("translation tasks mismatch")
    original_units = _source_units(master_en.read_text(encoding="utf-8"))
    originals = {row["unit_id"]: row for row in original_units}
    task_ids_seen: set[str] = set()
    grouped_parts: dict[str, list[dict[str, Any]]] = {}
    for task in tasks["units"]:
        if not isinstance(task, dict) or not isinstance(task.get("unit_id"), str) or task["unit_id"] in task_ids_seen:
            raise MasterRuVerificationError("translation task shape or duplicate id")
        task_ids_seen.add(task["unit_id"])
        parent_id = task.get("parent_unit_id") or task["unit_id"]
        original = originals.get(parent_id)
        if original is None or task.get("source_hash") != original["source_hash"] or not isinstance(task.get("source_text"), str) or not task["source_text"]:
            raise MasterRuVerificationError("translation task source authority mismatch")
        if task.get("parent_unit_id") is None:
            if task != original:
                raise MasterRuVerificationError("unsplit translation task mismatch")
        else:
            allowed = {"unit_id", "page", "source_hash", "source_text", "parent_unit_id", "part_index", "part_count", "part_source_hash"}
            part_digest = hashlib.sha256(task["source_text"].encode("utf-8")).hexdigest()
            if set(task) != allowed or task.get("page") != original["page"] or task.get("part_source_hash") != part_digest:
                raise MasterRuVerificationError("split translation task mismatch")
            grouped_parts.setdefault(parent_id, []).append(task)
    covered = {task.get("parent_unit_id") or task["unit_id"] for task in tasks["units"]}
    if covered != set(originals):
        raise MasterRuVerificationError("translation tasks do not cover MASTER_EN units")
    for parent_id, parts in grouped_parts.items():
        parts.sort(key=lambda row: row["part_index"])
        if [row["part_index"] for row in parts] != list(range(1, len(parts) + 1)) or any(row["part_count"] != len(parts) for row in parts):
            raise MasterRuVerificationError("split translation task part topology mismatch")
        cursor = 0
        source_text = originals[parent_id]["source_text"]
        for part in parts:
            position = source_text.find(part["source_text"], cursor)
            if position < cursor or source_text[cursor:position].strip():
                raise MasterRuVerificationError("split translation task source order mismatch")
            cursor = position + len(part["source_text"])
        if source_text[cursor:].strip():
            raise MasterRuVerificationError("split translation task source coverage mismatch")

    submission = _read(submission_file)
    _exact(submission, {"schema", "scenario_id", "accepted_master_en", "packet_manifest", "units", "batches", "review", "submission_sha256"}, "submission")
    _seal_valid(submission, "submission_sha256", "submission")
    expected_packet_record = {"path": manifest_path.relative_to(authority).as_posix(), **_identity(manifest_path)}
    if submission["schema"] != SUBMISSION_SCHEMA or submission["scenario_id"] != scenario_id or submission["accepted_master_en"] != manifest["accepted_master_en"] or submission["packet_manifest"] != expected_packet_record or submission["review"] != {"state": "closed", "unresolved": []}:
        raise MasterRuVerificationError("submission authority mismatch")
    if not isinstance(manifest["batches"], list) or not isinstance(submission["batches"], list) or len(manifest["batches"]) != len(submission["batches"]):
        raise MasterRuVerificationError("submission batch cardinality mismatch")

    merged: list[dict[str, Any]] = []
    replacement_events: list[dict[str, Any]] = []
    source_batch_projection: list[dict[str, Any]] = []
    observed_unit_ids: list[str] = []
    for index, (batch_record, submitted_record) in enumerate(zip(manifest["batches"], submission["batches"]), 1):
        _exact(batch_record, {"batch_id", "input", "output_path", "unit_ids"}, "packet batch")
        expected_id = f"batch-{index:04d}"
        if batch_record["batch_id"] != expected_id or batch_record["output_path"] != f"batches/{expected_id}.ru.json":
            raise MasterRuVerificationError("packet batch topology mismatch")
        en_path = _resolve_identity(packet, batch_record["input"], f"source batch {index}")
        ru_path = _resolve_identity(authority, submitted_record, f"submitted batch {index}")
        if ru_path.name != Path(batch_record["output_path"]).name:
            raise MasterRuVerificationError("submitted batch name/order mismatch")
        en = _exact(_read(en_path), _BATCH_KEYS, "source batch")
        ru = _exact(_read(ru_path), _BATCH_KEYS, "translated batch")
        if en["schema"] != "kb_creator.translation_batch.v1" or ru["schema"] != en["schema"] or en["batch_id"] != expected_id or ru["batch_id"] != expected_id or ru["instructions"] != en["instructions"] or not isinstance(en["units"], list) or not isinstance(ru["units"], list) or len(en["units"]) != len(ru["units"]):
            raise MasterRuVerificationError("translated batch outer shape mismatch")
        if [row.get("unit_id") for row in en["units"] if isinstance(row, dict)] != batch_record["unit_ids"]:
            raise MasterRuVerificationError("source batch unit order mismatch")
        for unit_index, (source_unit, translated_unit) in enumerate(zip(en["units"], ru["units"])):
            source = _exact(source_unit, _UNIT_KEYS, "source unit")
            translated = _exact(translated_unit, _UNIT_KEYS, "translated unit")
            if any(translated[key] != source[key] for key in _UNIT_KEYS - {"ru_text"}):
                raise MasterRuVerificationError(f"translated source field changed at {expected_id}/{unit_index}")
            ru_text = translated["ru_text"]
            if not isinstance(ru_text, str) or not ru_text.strip():
                raise MasterRuVerificationError(f"empty Russian payload at {expected_id}/{unit_index}")
            ru_text = ru_text.strip()
            ru_text, events = _normalize_declared_terms(
                source["source_text"], ru_text, terms, source["unit_id"]
            )
            replacement_events.extend(events)
            if _signature(source["source_text"]) != _signature(ru_text):
                raise MasterRuVerificationError(f"markdown_or_mechanics_drift: {source['unit_id']}")
            merged.append({"unit_id": source["unit_id"], "source_sha256": str(source["source_hash"]).upper(), "russian_payload_sha256": _sha_bytes(ru_text.encode("utf-8")), "source_text": source["source_text"], "ru_text": ru_text})
            source_batch_projection.append({key: source[key] for key in _UNIT_KEYS - {"ru_text"} if source[key] is not None})
            observed_unit_ids.append(source["unit_id"])
    task_ids = [row.get("unit_id") for row in tasks["units"] if isinstance(row, dict)]
    if observed_unit_ids != task_ids or len(task_ids) != len(set(task_ids)):
        raise MasterRuVerificationError("packet/submission unit order mismatch")
    normalized_tasks = [{key: value for key, value in task.items() if value is not None} for task in tasks["units"]]
    if source_batch_projection != normalized_tasks:
        raise MasterRuVerificationError("packet batches do not exactly project translation tasks")
    counts = _exact(manifest["counts"], {"original_units", "translation_units", "batches", "source_chars"}, "packet counts")
    if counts != {
        "original_units": len(original_units),
        "translation_units": len(tasks["units"]),
        "batches": len(manifest["batches"]),
        "source_chars": len(master_en.read_text(encoding="utf-8")),
    }:
        raise MasterRuVerificationError("packet counts mismatch")
    expected_declared = [{key: row[key] for key in ("unit_id", "source_sha256", "russian_payload_sha256")} for row in merged]
    if submission["units"] != expected_declared:
        raise MasterRuVerificationError("submission unit identity mismatch")

    term_checks = []
    for term in terms:
        matched = [row for row in merged if _present(term["source"], row["source_text"])]
        if not matched:
            term_checks.append({
                "source": term["source"], "target": term["target"],
                "accepted": term["targets"], "bad": term["bad"],
                "authority": term["authorities"][0], "authorities": term["authorities"],
                "domain": term["domain"], "unit_id": None, "required": False,
                "applicability": "not_present", "context": {
                    "applicability": "not_present", "occurrences": 0,
                    "required_occurrences": 0, "excluded_occurrences": 0,
                    "ambiguous_occurrences": 0, "source_lines": [],
                },
                "present": False, "bad_present": [],
            })
            continue
        context_base_term = term
        for unit in matched:
            term = _context_forms(context_base_term, unit["source_text"])
            context = _applicability(term, unit["source_text"])
            applicability = context["applicability"]
            if applicability == "ambiguous":
                raise MasterRuVerificationError(
                    f"terminology context ambiguous: {term['source']} in {unit['unit_id']}"
                )
            required = applicability in {"required_general", "required_skill"}
            present = required and any(_present(target, unit["ru_text"]) for target in term["targets"])
            bad_present = [
                bad for bad in term["bad"]
                if required and _bad_variant_present(bad, term["targets"], unit["ru_text"])
            ]
            if required and (not present or bad_present):
                raise MasterRuVerificationError(f"terminology mismatch: {term['source']} in {unit['unit_id']}")
            term_checks.append({
                "source": term["source"], "target": term["target"],
                "accepted": term["targets"], "bad": term["bad"],
                "authority": term["authorities"][0], "authorities": term["authorities"],
                "domain": term["domain"], "unit_id": unit["unit_id"],
                "required": required, "applicability": applicability,
                "context": context, "present": present, "bad_present": bad_present,
            })

    master_ru = candidate / "MASTER_RU.md"
    expected_text = "\n\n".join(row["ru_text"] for row in merged).strip() + "\n"
    if not master_ru.is_file() or master_ru.read_bytes() != expected_text.encode("utf-8"):
        raise MasterRuVerificationError("MASTER_RU candidate assembly mismatch")
    expected_assets = []
    for reference in dict.fromkeys(_signature(master_en.read_text(encoding="utf-8"))["image_targets"]):
        relative = _safe_relative(reference, "MASTER_EN asset")
        source = _contained(master_en.parent / relative, master_en.parent, "MASTER_EN asset", file=True)
        target = _contained(candidate / relative, candidate, "candidate asset", file=True)
        if target.read_bytes() != source.read_bytes():
            raise MasterRuVerificationError(f"candidate asset identity drift: {reference}")
        expected_assets.append({"path": relative.as_posix(), **_identity(target)})
    assets_path = candidate / "ASSET_MANIFEST.json"
    expected_assets_doc = {"schema": "kb_creator.master_ru_asset_manifest.v1", "scenario_id": scenario_id, "assets": expected_assets, "summary": {"total": len(expected_assets)}}
    if _read(assets_path) != expected_assets_doc:
        raise MasterRuVerificationError("MASTER_RU asset manifest mismatch")

    master_record = {"path": "MASTER_RU.md", **_identity(master_ru)}
    provenance_path = candidate / "MASTER_RU.provenance.json"
    provenance = _read(provenance_path)
    _exact(provenance, {"schema", "scenario_id", "accepted_master_en", "packet_manifest", "submission", "unit_order", "master_ru", "provenance_sha256"}, "MASTER_RU provenance")
    _seal_valid(provenance, "provenance_sha256", "MASTER_RU provenance")
    expected_submission_record = {"path": submission_file.relative_to(authority).as_posix(), **_identity(submission_file)}
    if provenance["schema"] != "kb_creator.master_ru_provenance.v1" or provenance["scenario_id"] != scenario_id or provenance["accepted_master_en"] != manifest["accepted_master_en"] or provenance["packet_manifest"] != expected_packet_record or provenance["submission"] != expected_submission_record or provenance["unit_order"] != observed_unit_ids or provenance["master_ru"] != master_record:
        raise MasterRuVerificationError("MASTER_RU provenance mismatch")

    qa_path = candidate / "MASTER_RU.qa.json"
    qa = _read(qa_path)
    expected_checks = {"ordered_hash_bound_units": True, "markdown_structure": True, "anchors_links_images": True, "numeric_dice_mechanics": True, "shared_terminology": True}
    if qa != {"schema": "kb_creator.master_ru_qa.v1", "status": "pass", "scenario_id": scenario_id, "master_ru": master_record, "checks": expected_checks, "findings": []}:
        raise MasterRuVerificationError("producer MASTER_RU QA mismatch")
    terminology_path = candidate / "TERMINOLOGY.qa.json"
    if _read(terminology_path) != {"schema": "kb_creator.master_ru_terminology_qa.v1", "authorities": manifest["terminology"], "checks": term_checks, "replacements": replacement_events, "status": "pass"}:
        raise MasterRuVerificationError("MASTER_RU terminology QA mismatch")
    rows, inventory_sha = _inventory(candidate)
    inventory_path = candidate / "INVENTORY.json"
    expected_inventory = {"schema": "kb_creator.candidate_inventory.v1", "algorithm": "sorted relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>", "rows": rows, "file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows), "inventory_sha256": inventory_sha}
    if _read(inventory_path) != expected_inventory:
        raise MasterRuVerificationError("MASTER_RU candidate inventory mismatch")
    expected_files = {
        "MASTER_RU.md", "MASTER_RU.provenance.json", "MASTER_RU.qa.json",
        "ASSET_MANIFEST.json", "TERMINOLOGY.qa.json", "INVENTORY.json",
        *(row["path"] for row in expected_assets),
    }
    observed_files = {path.relative_to(candidate).as_posix() for path in candidate.rglob("*") if path.is_file()}
    if observed_files != expected_files:
        raise MasterRuVerificationError("MASTER_RU candidate contains extra or missing files")

    checks = {
        "accepted_master_en_identity": True,
        "ordered_unit_identity": True,
        "markdown_structure_preservation": True,
        "mechanics_preservation": True,
        "terminology_authority": True,
        "asset_identity": True,
        "independent_translation_qa": True,
        "producer_qa": True,
        "candidate_inventory": True,
        "provenance": True,
    }
    receipt = {
        "schema": VERIFICATION_SCHEMA,
        "status": PASS_STATE,
        "scenario_id": scenario_id,
        "master_ru": _identity(master_ru),
        "submission": {**_identity(submission_file), "submission_sha256": submission["submission_sha256"]},
        "packet_manifest": {**_identity(manifest_path), "manifest_sha256": manifest["manifest_sha256"]},
        "contract": _identity(contract_file),
        "candidate_inventory": {**_identity(inventory_path), "inventory_sha256": inventory_sha},
        "required_qa": required_qa,
        "checks": checks,
        "findings": [],
    }
    receipt["verification_sha256"] = _sha_bytes(_canonical(receipt))
    return receipt


def _write_atomic(path: Path, value: object) -> None:
    if path.exists() or not path.parent.is_dir():
        raise MasterRuVerificationError("verification output must be absent under an existing parent")
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.staging.", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        temporary.write_bytes(_canonical(value) + b"\n")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authority-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_candidate(args.packet_root, args.submission, args.candidate_root, args.contract, args.authority_root)
        _write_atomic(args.output, result)
    except (MasterRuVerificationError, OSError, ValueError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False), file=__import__("sys").stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
