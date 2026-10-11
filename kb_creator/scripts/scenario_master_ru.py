#!/usr/bin/env python3
"""Scenario-neutral, hash-bound MASTER_RU packet and assembly lifecycle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Mapping, Sequence

from kb_creator.scripts.merge_translation_batches import validate_batch
from kb_creator.scripts.prepare_translation_batches import batch_units, expand_units_for_translation
from kb_creator.pipeline.language_numeric import represented_numbers


PACKET_SCHEMA = "kb_creator.master_ru_packet_manifest.v1"
SUBMISSION_SCHEMA = "kb_creator.master_ru_submission.v1"
ACCEPTANCE_SCHEMA = "kb_creator.artifact_acceptance.v1"
MASTER_EN_PROVENANCE_SCHEMA = "kb_creator.master_en_provenance.v3"
PUBLICATION_STAGE_SCHEMA = "kb_creator.publication_stage_manifest.v1"
HEX = re.compile(r"^[0-9A-F]{64}$")


class MasterRuError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise MasterRuError(f"cannot read JSON: {path}") from error
    if not isinstance(value, dict):
        raise MasterRuError(f"JSON object required: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def _exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise MasterRuError(f"{label} closed schema mismatch")
    return value


def _safe(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise MasterRuError(f"unsafe {label} path")
    path = Path(value)
    if path.is_absolute() or path.drive or any(part in {"", ".", ".."} for part in path.parts):
        raise MasterRuError(f"unsafe {label} path")
    return path


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.resolve().relative_to(root.resolve()).as_posix(), "bytes": path.stat().st_size, "sha256": _sha_file(path)}


def _within(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as error:
        raise MasterRuError(f"{label} escapes authority root") from error
    if path.exists() and path.is_symlink():
        raise MasterRuError(f"{label} cannot be a reparse path")
    return resolved


def _resolve_identity(root: Path, record: object, label: str) -> Path:
    row = _exact(record, {"path", "bytes", "sha256"}, label)
    relative = _safe(row["path"], label)
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise MasterRuError(f"{label} escapes authority root") from error
    if not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"] or _sha_file(path) != row["sha256"]:
        raise MasterRuError(f"{label} identity mismatch")
    return path


def _seal(schema: str, payload: dict[str, Any], key: str) -> dict[str, Any]:
    result = {"schema": schema, **payload}
    result[key] = _sha_bytes(_canonical(result))
    return result


def _validate_seal(value: dict[str, Any], key: str, label: str) -> None:
    digest = value.get(key)
    if not isinstance(digest, str) or not HEX.fullmatch(digest):
        raise MasterRuError(f"{label} seal missing")
    if _sha_bytes(_canonical({name: item for name, item in value.items() if name != key})) != digest:
        raise MasterRuError(f"{label} seal mismatch")


def _validate_acceptance(path: Path, authority_root: Path, kind: str, candidate: Path) -> dict[str, Any]:
    value = _read(path)
    _exact(value, {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"}, f"{kind} acceptance")
    _validate_seal(value, "receipt_sha256", f"{kind} acceptance")
    if value["schema"] != ACCEPTANCE_SCHEMA or value["artifact_kind"] != kind or value["decision"] != "accepted" or value["recorder_role"] != "main_orchestrator":
        raise MasterRuError(f"{kind} acceptance is not authoritative")
    if value["candidate"] != _identity(candidate, authority_root):
        raise MasterRuError(f"{kind} acceptance candidate mismatch")
    _resolve_identity(authority_root, value["producer_stage"], f"{kind} producer stage")
    if not isinstance(value["evidence"], list) or not value["evidence"]:
        raise MasterRuError(f"{kind} acceptance evidence missing")
    for index, row in enumerate(value["evidence"]):
        _resolve_identity(authority_root, row, f"{kind} evidence {index}")
    return value


def _source_units(text: str) -> list[dict[str, Any]]:
    blocks = [part.strip() for part in re.split(r"\n[ \t]*\n", text) if part.strip()]
    if not blocks:
        raise MasterRuError("MASTER_EN contains no translation units")
    return [
        {"unit_id": f"unit-{index:05d}", "page": _unit_page(block), "source_hash": _sha_bytes(block.encode("utf-8")), "source_text": block}
        for index, block in enumerate(blocks, 1)
    ]


def _unit_page(text: str) -> int | None:
    match = re.search(r"<!--\s*source-page-(\d{3,})\s*-->", text)
    return int(match.group(1)) if match else None


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


def _structure_signature(text: str) -> dict[str, Any]:
    lines = text.splitlines()

    def line_class(line: str) -> str:
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

    return {
        "page_markers": re.findall(r"<!--\s*source-page-\d{3,}\s*-->", text),
        "anchors": re.findall(r"<a id=\"[^\"]+\"></a>", text),
        "image_targets": re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text),
        "link_targets": [target for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)", text)],
        "headings": [len(match.group(1)) for match in re.finditer(r"(?m)^(#{1,6})\s+", text)],
        "list_markers": re.findall(r"(?m)^\s*(?:[-+*]|\d+\.)\s+", text),
        "table_cells": [line.count("|") for line in text.splitlines() if line.lstrip().startswith("|")],
        "mechanics": represented_numbers(text),
        "represented_numbers": represented_numbers(text),
        "line_classes": [line_class(line) for line in lines],
        "hard_breaks": [line.endswith("  ") for line in lines],
        "explicit_br": [len(re.findall(r"<br\s*/?>", line, flags=re.IGNORECASE)) for line in lines],
        "emphasis_delimiters": [
            re.findall(r"(?<!\\)(?:\*\*|__|~~|\*|_)", line)
            for line in lines
        ],
    }


_CSV_TERMINOLOGY_HEADER = (
    "source_term", "accepted_ru", "aliases", "bad_ru", "domain", "status",
    "source_scope", "decision_rule", "notes",
)
_MD_TERMINOLOGY_HEADER = ("English", "Принятый русский термин", "Примечание")

_COC7E_STATBLOCK_REQUIRED_TERMS = frozenset({
    "STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU",
    "SAN", "HP", "MP", "MOV", "Move", "DB", "Build", "Damage bonus",
})
_COC7E_STATBLOCK_TRIGGER_TERMS = ("STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU")


def _term_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MasterRuError(f"unsafe empty terminology {label}")
    return " ".join(value.strip().split())


def _term_variants(value: object, label: str) -> tuple[str, ...]:
    if value in (None, "", []):
        return ()
    raw = value if isinstance(value, list) else str(value).split(";") if isinstance(value, str) else None
    if raw is None or not raw:
        raise MasterRuError(f"malformed terminology {label}")
    variants = tuple(_term_text(item, label) for item in raw)
    normalized = [_normalize_term(item) for item in variants]
    if len(normalized) != len(set(normalized)):
        raise MasterRuError(f"duplicate terminology {label}")
    return variants


def _term_domain(value: object, label: str, *, default: str = "general") -> str:
    if value in (None, ""):
        return default
    domain = _term_text(value, label).casefold()
    if re.fullmatch(r"[a-z0-9][a-z0-9 ./_-]*", domain) is None:
        raise MasterRuError(f"malformed terminology {label}")
    return domain


def _normalize_term(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _json_terms(path: Path, authority: str) -> list[dict[str, Any]]:
    value = _read(path)
    usage_by_source = {}
    if value.get("schema") == "kb_creator.effective_coc_glossary.v1":
        from kb_creator.pipeline.coc_glossary import validate_payload
        try:
            effective = validate_payload(value)["terms"]
            usage_by_source = {row["source"]: row["usage"] for row in effective if "usage" in row}
            value = {"terms": [{k: v for k, v in row.items() if k != "usage"} for row in effective]}
        except (ValueError, KeyError, TypeError) as error:
            raise MasterRuError(f"invalid effective terminology: {error}") from error
    if set(value) != {"terms"} or not isinstance(value["terms"], list):
        raise MasterRuError(f"JSON terminology authority is not closed: {authority}")
    allowed = {"source", "en", "target", "ru", "aliases", "bad_ru", "bad", "forbidden", "domain"}
    terms = []
    for index, row in enumerate(value["terms"], 1):
        if not isinstance(row, dict) or not set(row).issubset(allowed):
            raise MasterRuError(f"malformed JSON terminology row {index}: {authority}")
        source_values = [row[key] for key in ("source", "en") if key in row]
        target_values = [row[key] for key in ("target", "ru") if key in row]
        if len(source_values) != 1 or len(target_values) != 1:
            raise MasterRuError(f"ambiguous JSON terminology row {index}: {authority}")
        bad_values = [row[key] for key in ("bad_ru", "bad", "forbidden") if key in row]
        if len(bad_values) > 1:
            raise MasterRuError(f"ambiguous JSON bad variants row {index}: {authority}")
        terms.append({
            "source": _term_text(source_values[0], f"source row {index}"),
            "target": _term_text(target_values[0], f"target row {index}"),
            "aliases": _term_variants(row.get("aliases"), f"aliases row {index}"),
            "bad": _term_variants(bad_values[0] if bad_values else None, f"bad variants row {index}"),
            "domain": _term_domain(row.get("domain"), f"domain row {index}"),
            "domain_explicit": "domain" in row,
            "authority": authority,
        })
    for term in terms:
        if term["source"] in usage_by_source:
            term["usage"] = usage_by_source[term["source"]]
    return terms


def _csv_terms(path: Path, authority: str) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != _CSV_TERMINOLOGY_HEADER:
                raise MasterRuError(f"CSV terminology header mismatch: {authority}")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as error:
        raise MasterRuError(f"cannot read CSV terminology authority: {authority}") from error
    terms = []
    for index, row in enumerate(rows, 2):
        if None in row or set(row) != set(_CSV_TERMINOLOGY_HEADER):
            raise MasterRuError(f"malformed CSV terminology row {index}: {authority}")
        status = _term_text(row["status"], f"status row {index}")
        if status.casefold() != "accepted":
            continue
        terms.append({
            "source": _term_text(row["source_term"], f"source row {index}"),
            "target": _term_text(row["accepted_ru"], f"target row {index}"),
            "aliases": _term_variants(row["aliases"], f"aliases row {index}"),
            "bad": _term_variants(row["bad_ru"], f"bad variants row {index}"),
            "domain": _term_domain(row["domain"], f"domain row {index}"),
            "domain_explicit": True,
            "authority": authority,
        })
    from kb_creator.pipeline.coc_glossary import usage_rule
    accepted_rows = [row for row in rows if row["status"].casefold() == "accepted"]
    for term, row in zip(terms, accepted_rows):
        rule = usage_rule(row["notes"])
        if rule:
            term["usage"] = rule
    return terms


def _markdown_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return tuple(cell.strip() for cell in re.split(r"(?<!\\)\|", stripped[1:-1]))


def _markdown_terms(path: Path, authority: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as error:
        raise MasterRuError(f"cannot read Markdown terminology authority: {authority}") from error
    terms = []
    found_table = False
    index = 0
    while index < len(lines):
        cells = _markdown_cells(lines[index])
        if cells != _MD_TERMINOLOGY_HEADER:
            index += 1
            continue
        found_table = True
        if index + 1 >= len(lines):
            raise MasterRuError(f"Markdown terminology delimiter missing: {authority}")
        delimiter = _markdown_cells(lines[index + 1])
        if delimiter is None or len(delimiter) != 3 or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in delimiter):
            raise MasterRuError(f"Markdown terminology delimiter mismatch: {authority}")
        index += 2
        table_count = 0
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            row = _markdown_cells(lines[index])
            if row is None or len(row) != 3:
                raise MasterRuError(f"malformed Markdown terminology row {index + 1}: {authority}")
            terms.append({
                "source": _term_text(row[0], f"source row {index + 1}"),
                "target": _term_text(row[1], f"target row {index + 1}"),
                "aliases": (), "bad": (), "domain": "skill", "domain_explicit": False,
                "authority": authority,
            })
            table_count += 1
            index += 1
        if not table_count:
            raise MasterRuError(f"empty Markdown terminology table: {authority}")
    if not found_table:
        raise MasterRuError(f"Markdown terminology header mismatch: {authority}")
    return terms


def _terminology_terms(authorities: Sequence[tuple[str, Path]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    seen_by_authority: set[tuple[str, str]] = set()
    for authority, path in authorities:
        suffix = path.suffix.lower()
        if suffix == ".json":
            rows = _json_terms(path, authority)
        elif suffix == ".csv":
            rows = _csv_terms(path, authority)
        elif suffix == ".md":
            rows = _markdown_terms(path, authority)
        else:
            raise MasterRuError(f"unsupported terminology authority suffix: {suffix or '<none>'}")
        if not rows:
            raise MasterRuError(f"terminology authority has zero usable accepted pairs: {authority}")
        for row in rows:
            source_key = _normalize_term(row["source"])
            authority_key = (authority, source_key)
            if authority_key in seen_by_authority:
                raise MasterRuError(f"duplicate normalized source term in {authority}: {row['source']}")
            seen_by_authority.add(authority_key)
            accepted = (row["target"], *row["aliases"])
            accepted_keys = {_normalize_term(item) for item in accepted}
            bad_keys = {_normalize_term(item) for item in row["bad"]}
            if len(accepted_keys) != len(accepted) or accepted_keys & bad_keys:
                raise MasterRuError(f"conflicting accepted/bad terminology variants: {row['source']}")
            current = merged.get(source_key)
            if current is None:
                merged[source_key] = {**row, "targets": list(accepted), "bad": list(row["bad"]), "authorities": [authority]}
                continue
            if _normalize_term(current["target"]) != _normalize_term(row["target"]):
                raise MasterRuError(f"conflicting normalized source term: {row['source']}")
            if current["domain_explicit"] and row["domain_explicit"]:
                if current["domain"] != row["domain"]:
                    raise MasterRuError(f"conflicting terminology domain: {row['source']}")
            elif row["domain_explicit"]:
                current["domain"] = row["domain"]
                current["domain_explicit"] = True
            elif not current["domain_explicit"] and current["domain"] != row["domain"]:
                raise MasterRuError(f"conflicting implicit terminology domain: {row['source']}")
            current_accepted = {_normalize_term(item) for item in current["targets"]}
            current_bad = {_normalize_term(item) for item in current["bad"]}
            if current_accepted & bad_keys or accepted_keys & current_bad:
                raise MasterRuError(f"conflicting accepted/bad terminology variants: {row['source']}")
            current["targets"].extend(item for item in accepted if _normalize_term(item) not in current_accepted)
            current["bad"].extend(item for item in row["bad"] if _normalize_term(item) not in current_bad)
            current["authorities"].append(authority)
    return list(merged.values())


def _requires_coc7e_statblock_profile(source_text: str) -> bool:
    matches = sum(
        re.search(rf"(?<!\w){re.escape(term)}\s+(?:\d+|[-—?])", source_text, flags=re.IGNORECASE) is not None
        for term in _COC7E_STATBLOCK_TRIGGER_TERMS
    )
    return matches >= 5


def _require_coc7e_statblock_profile(terms: Sequence[Mapping[str, Any]], source_text: str) -> None:
    if not _requires_coc7e_statblock_profile(source_text):
        return
    available = {_normalize_term(str(term["source"])) for term in terms}
    missing = sorted(
        term for term in _COC7E_STATBLOCK_REQUIRED_TERMS
        if _normalize_term(term) not in available
    )
    if missing:
        raise MasterRuError(
            "CoC 7e statblock terminology profile is incomplete: " + ", ".join(missing)
        )


def _term_present(term: str, text: str) -> bool:
    words = re.escape(term).replace(r"\ ", r"\s+")
    # OCR can split ordinary words at a line boundary (``con- veniently``).
    # An all-caps stat abbreviation at that boundary is not a stat occurrence.
    return re.search(rf"(?<!\w){words}(?!\w|-+\s*[a-z])", text, flags=re.IGNORECASE) is not None


_SKILL_LABELS = frozenset({"skill", "skills", "ability", "abilities", "proficiency", "proficiencies"})
_NON_SKILL_LABELS = frozenset({
    "occupation", "occupations", "profession", "professions", "career", "careers",
    "name", "names", "role", "roles", "cast", "character", "characters",
})
_STATBLOCK_LABEL_ONLY_SOURCES = frozenset({"build", "move"})


def _statblock_label_context(term: str, text: str) -> dict[str, Any]:
    words = re.escape(term).replace(r"\ ", r"\s+")
    pattern = re.compile(
        rf"(?<!\w){words}\s*:?\s*(?:\d+|[-—?]|none\b|varies\b)",
        flags=re.IGNORECASE,
    )
    matches = list(pattern.finditer(text))
    return {
        "applicability": (
            "required_general" if matches else "excluded_non_statblock_context"
        ),
        "occurrences": len(matches),
        "required_occurrences": len(matches),
        "excluded_occurrences": 0 if matches else int(_term_present(term, text)),
        "ambiguous_occurrences": 0,
        "source_lines": [text.count("\n", 0, match.start()) for match in matches],
    }


def _context_label(line: str) -> str | None:
    match = re.match(
        r"^\s*(?:>\s*)?(?:\*\*)?([A-Za-z][A-Za-z _/-]{1,40}):(?:\*\*)?",
        line,
    )
    if match is None:
        return None
    return " ".join(match.group(1).casefold().replace("/", " ").split())


def _skill_term_context(
    term: str, text: str, *, authorized_skills: Sequence[str] = (), predecessor_text: str = "",
) -> dict[str, Any]:
    from kb_creator.pipeline.language_context import skill_context
    return skill_context(term, text, authorized_skills=authorized_skills, predecessor_text=predecessor_text)  # shared occurrence classifier; legacy body retained for compatibility
    """Legacy classifier retained below; shared helper above is authoritative."""
    words = re.escape(term).replace(r"\ ", r"\s+")
    pattern = re.compile(rf"(?<!\w){words}(?!\w)", flags=re.IGNORECASE)
    rows = []
    for match in pattern.finditer(text):
        line_index = text.count("\n", 0, match.start())
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end < 0:
            line_end = len(text)
        line = text[line_start:line_end]
        label = _context_label(line)
        left = text[max(line_start, match.start() - 96):match.start()]
        right = text[match.end():min(line_end, match.end() + 96)]
        if label in _SKILL_LABELS:
            kind = "required_skill"
        elif label in _NON_SKILL_LABELS:
            kind = "excluded_non_skill_context"
        elif (
            match.start() >= 2 and text[match.start() - 1] == "-"
            and text[match.start() - 2].isalnum()
        ) or (
            match.end() + 1 < len(text) and text[match.end()] == "-"
            and text[match.end() + 1].isalnum()
        ):
            kind = "excluded_non_skill_context"
        elif match.group()[0].islower():
            # Lowercase title-term occurrences are ordinary prose unless a
            # labelled skill field above has already established the context.
            kind = "excluded_non_skill_context"
        elif re.search(
            r"^\s*(?:\([^\r\n)]{1,80}\)\s*)?(?:(?:rolls?|checks?|tests?|skills?|rating|score|attempt|use|success|failure)\b|will\s+(?:reveal|uncover|expose|show|allow|find|notice|detect|identify|locate)\b|\d{1,3}%(?=\s|$|[,.;:]))",
            right,
            flags=re.IGNORECASE,
        ) or re.search(
            r"\b(?:skill|use|using|successful|failed|regular|hard|extreme|opposed|pushed)\s+$",
            left,
            flags=re.IGNORECASE,
        ) or re.search(
            r"\b(?:use|using)\s+(?:[A-Za-z][\w'-]*(?:\s+[A-Za-z][\w'-]*)?\s*(?:,|\bor\b|\band\b)\s*)+$",
            left,
            flags=re.IGNORECASE,
        ) or (
            re.search(r"\b(?:a|an)\s+$", left, flags=re.IGNORECASE)
            and re.search(
                r"^\s+(?:from|by|with|for|among)\b[^.,;:]{0,80}?\bwill\s+(?:reveal|uncover|expose|show|allow|find|notice|detect|identify|locate)\b",
                right,
                flags=re.IGNORECASE,
            )
        ):
            kind = "required_skill"
        else:
            article_title = re.search(
                r"\b(?:a|an)\s+(?:[A-Za-z][\w'-]*\s+){0,4}$", left,
                flags=re.IGNORECASE,
            )
            occupation_before = re.search(
                r"\b(?:works? as|employed as|hired as|occupation|profession|career|job)\s+(?:[A-Za-z][\w'-]*\s+){0,4}$",
                left,
                flags=re.IGNORECASE,
            )
            occupation_after = re.search(
                r"^\s*[,;\u2014-]?\s*(?:hired|employed|working|who|whose|responsible|assigned)\b",
                right,
                flags=re.IGNORECASE,
            )
            academic_context = re.search(
                r"^\s*(?:and\s+[A-Za-z][\w'-]*\s+)?(?:students?|lecturers?|teachers?|professors?|department|course|class|degree|major|studies)\b",
                right,
                flags=re.IGNORECASE,
            )
            kind = (
                "excluded_non_skill_context"
                if occupation_before or (article_title and occupation_after) or academic_context
                else "ambiguous"
            )
        rows.append({"line": line_index, "classification": kind})
    counts = {
        kind: sum(row["classification"] == kind for row in rows)
        for kind in ("required_skill", "excluded_non_skill_context", "ambiguous")
    }
    if counts["ambiguous"]:
        applicability = "ambiguous"
    elif counts["required_skill"]:
        applicability = "required_skill"
    else:
        applicability = "excluded_non_skill_context"
    return {
        "applicability": applicability,
        "occurrences": len(rows),
        "required_occurrences": counts["required_skill"],
        "excluded_occurrences": counts["excluded_non_skill_context"],
        "ambiguous_occurrences": counts["ambiguous"],
        "source_lines": [row["line"] for row in rows],
    }


def _contextual_term(term: Mapping[str, Any], text: str) -> dict[str, Any]:
    """Choose only authority-declared context forms, without changing numbers."""
    if not term.get("usage"):
        return dict(term)
    result = dict(term)
    all_occurrences = list(re.finditer(rf"(?<!\w){re.escape(term['source'])}(?!\w)", text, re.I))
    # Table headers may carry their value in a later row of the same column.
    # This recognizes a label/value relationship without treating prose SAN as
    # a stat label.
    table_rows = [line.strip().strip("|").split("|") for line in text.splitlines() if line.lstrip().startswith("|")]
    for index, cells in enumerate(table_rows):
        for column, cell in enumerate(cells):
            if _normalize_term(cell) != _normalize_term(str(term["source"])):
                continue
            for later in table_rows[index + 1:]:
                if column >= len(later) or re.fullmatch(r"\s*:?-{3,}:?\s*", later[column]):
                    continue
                if re.fullmatch(r"\s*(?:\d+|[-—?])\s*", later[column]):
                    return result
                break
    labels = list(re.finditer(rf"(?<!\w){re.escape(term['source'])}\s*:?\s*(?:\d+|[-—?]|none\b|varies\b)", text, re.I))
    if labels:
        if len(labels) != len(all_occurrences):
            result["usage_ambiguous"] = True
        return result
    forms = term["usage"]["prose"]
    result.update(target=forms["target"], aliases=tuple(forms["aliases"]),
                  targets=[forms["target"], *forms["aliases"]], bad=list(forms["bad"]))
    return result


def _dying_context(text: str) -> dict[str, Any]:
    """Keep grammatical narrative dying separate from the named game condition."""
    pattern = re.compile(r"(?<!\w)dying(?!\w)", re.IGNORECASE)
    rows = []
    mechanical_cue = re.compile(
        r"\b(?:condition|status|state|health|hit\s*points?|HP|combat|unconscious|rounds?|damage|recovery|healing)\b",
        re.IGNORECASE,
    )
    progressive = re.compile(r"\b(?:am|are|is|was|were|be|been|being)\s+dying\b", re.IGNORECASE)
    for match in pattern.finditer(text):
        start = text.rfind("\n", 0, match.start()) + 1
        end = text.find("\n", match.end())
        line = text[start:len(text) if end < 0 else end]
        if progressive.search(line):
            kind = "excluded_non_mechanical_context"
        elif (re.match(r"^\s*(?:\*\*)?(?:condition|status|state|health)(?:\*\*)?\s*:\s*(?:\*\*)?dying\b", line, re.I)
              or re.match(r"^\s*(?:\*\*)?dying(?:\*\*)?\s*:", line, re.I)
              or mechanical_cue.search(line)):
            kind = "required_general"
        else:
            kind = "ambiguous"
        rows.append({"line": text.count("\n", 0, match.start()), "classification": kind})
    counts = {kind: sum(row["classification"] == kind for row in rows)
              for kind in ("required_general", "excluded_non_mechanical_context", "ambiguous")}
    return {"applicability": "ambiguous" if counts["ambiguous"] else (
        "required_general" if counts["required_general"] else "excluded_non_mechanical_context"),
        "occurrences": len(rows), "required_occurrences": counts["required_general"],
        "excluded_occurrences": counts["excluded_non_mechanical_context"],
        "ambiguous_occurrences": counts["ambiguous"],
        "source_lines": [row["line"] for row in rows]}


def _term_context(
    term: Mapping[str, Any], text: str, *, authorized_skills: Sequence[str] = (), predecessor_text: str = "",
) -> dict[str, Any]:
    if term.get("usage_ambiguous"):
        return {"applicability": "ambiguous", "occurrences": 1, "required_occurrences": 0,
                "excluded_occurrences": 0, "ambiguous_occurrences": 1, "source_lines": []}
    if term["domain"] == "skill":
        return _skill_term_context(term["source"], text, authorized_skills=authorized_skills, predecessor_text=predecessor_text)
    if _normalize_term(str(term["source"])) == "dying":
        return _dying_context(text)
    if _normalize_term(str(term["source"])) in _STATBLOCK_LABEL_ONLY_SOURCES:
        return _statblock_label_context(str(term["source"]), text)
    words = re.escape(term["source"]).replace(r"\ ", r"\s+")
    occurrences = len(list(re.finditer(rf"(?<!\w){words}(?!\w|-+\s*[a-z])", text, flags=re.IGNORECASE)))
    return {
        "applicability": "required_general",
        "occurrences": occurrences,
        "required_occurrences": occurrences,
        "excluded_occurrences": 0,
        "ambiguous_occurrences": 0,
        "source_lines": [],
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


def _replace_system_variant(
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


def _normalize_system_terminology(
    source_text: str,
    ru_text: str,
    terms: Sequence[Mapping[str, Any]],
    unit_id: str,
) -> tuple[str, list[dict[str, Any]]]:
    """Apply only authority-declared, context-safe exact replacements."""
    output = ru_text
    events: list[dict[str, Any]] = []
    authorized_skills = tuple(str(item["source"]) for item in terms if item.get("domain") == "skill")
    for term in terms:
        if not _term_present(str(term["source"]), source_text):
            continue
        term = _contextual_term(term, source_text)
        context = _term_context(term, source_text, authorized_skills=authorized_skills)
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
            for line_index, source_line in enumerate(source_lines):
                if not _term_present(str(term["source"]), source_line):
                    continue
                line_context = _skill_term_context(str(term["source"]), source_line,
                                                   authorized_skills=authorized_skills)
                if line_context["applicability"] != "required_skill":
                    continue
                for old in variants:
                    output_lines[line_index], count = _replace_system_variant(
                        output_lines[line_index], old, str(term["target"]), term["targets"]
                    )
                    if count:
                        events.append({
                            "unit_id": unit_id,
                            "source": term["source"],
                            "from": old,
                            "to": term["target"],
                            "count": count,
                            "line": line_index,
                        })
            output = "".join(output_lines)
            continue
        if context["applicability"] != "required_general":
            continue
        for old in variants:
            output, count = _replace_system_variant(
                output, old, str(term["target"]), term["targets"]
            )
            if count:
                events.append({
                    "unit_id": unit_id,
                    "source": term["source"],
                    "from": old,
                    "to": term["target"],
                    "count": count,
                    "line": None,
                })
    return output, events


def prepare(master_en: Path, master_en_acceptance: Path, terminology: Mapping[str, Path], output_root: Path, max_batch_chars: int, authority_root: Path) -> dict[str, Any]:
    master_en = master_en.resolve(); master_en_acceptance = master_en_acceptance.resolve(); authority_root = authority_root.resolve(); output_root = output_root.resolve()
    _within(master_en, authority_root, "MASTER_EN"); _within(master_en_acceptance, authority_root, "MASTER_EN acceptance"); _within(output_root, authority_root, "packet output")
    if output_root.exists() or not output_root.parent.is_dir() or max_batch_chars < 128:
        raise MasterRuError("packet output must be absent and max_batch_chars >= 128")
    acceptance = _validate_acceptance(master_en_acceptance, authority_root, "master_en", master_en)
    term_records = []
    term_authorities = []
    for role, path in sorted(terminology.items()):
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", role):
            raise MasterRuError("invalid terminology role")
        term_records.append({"role": role, "file": _identity(path.resolve(), authority_root)})
        resolved = _resolve_identity(authority_root, term_records[-1]["file"], f"terminology {role}")
        term_authorities.append((role, resolved))
    if not term_records:
        raise MasterRuError("at least one shared terminology authority is required")
    parsed_terms = _terminology_terms(term_authorities)
    _require_coc7e_statblock_profile(parsed_terms, master_en.read_text(encoding="utf-8"))
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.staging.", dir=output_root.parent))
    try:
        units = _source_units(master_en.read_text(encoding="utf-8"))
        expanded = expand_units_for_translation(units, max_batch_chars)
        batches = batch_units(expanded, max_batch_chars)
        tasks = {"schema": "kb_creator.master_ru_translation_tasks.v1", "scenario_id": acceptance["scenario_id"], "units": expanded}
        _write(stage / "translation_tasks.json", tasks)
        batch_rows = []
        for index, batch in enumerate(batches, 1):
            batch_id = f"batch-{index:04d}"
            en_path = stage / "batches" / f"{batch_id}.en.json"
            packet = {
                "schema": "kb_creator.translation_batch.v1", "batch_id": batch_id,
                "instructions": ["Translate English to Russian without omission.", "Preserve Markdown structure, anchors, links, images, source markers, numbers, dice, and Call of Cthulhu terms."],
                "units": [{"unit_id": row["unit_id"], "parent_unit_id": row.get("parent_unit_id"), "part_index": row.get("part_index"), "part_count": row.get("part_count"), "page": row.get("page"), "source_hash": row.get("source_hash") or _sha_bytes(row["source_text"].encode()), "part_source_hash": row.get("part_source_hash"), "source_text": row["source_text"], "ru_text": ""} for row in batch],
            }
            _write(en_path, packet)
            batch_rows.append({"batch_id": batch_id, "input": _identity(en_path, stage), "output_path": f"batches/{batch_id}.ru.json", "unit_ids": [row["unit_id"] for row in batch]})
        manifest = _seal(PACKET_SCHEMA, {"scenario_id": acceptance["scenario_id"], "accepted_master_en": _identity(master_en_acceptance, authority_root), "master_en": _identity(master_en, authority_root), "terminology": term_records, "tasks": _identity(stage / "translation_tasks.json", stage), "batches": batch_rows, "counts": {"original_units": len(units), "translation_units": len(expanded), "batches": len(batches), "source_chars": len(master_en.read_text(encoding="utf-8"))}, "packet_policy": "ordered_hash_bound_units_v1"}, "manifest_sha256")
        _write(stage / "packet_manifest.json", manifest)
        os.replace(stage, output_root)
        return {"status": "awaiting_master_ru_submission", "scenario_id": acceptance["scenario_id"], "packet_manifest": _identity(output_root / "packet_manifest.json", output_root), "counts": manifest["counts"]}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _validate_packet(
    packet_root: Path,
    authority_root: Path,
    *,
    require_complete_system_profile: bool = True,
) -> dict[str, Any]:
    packet_root = _within(packet_root, authority_root, "packet root")
    manifest = _read(packet_root / "packet_manifest.json")
    _exact(manifest, {"schema", "scenario_id", "accepted_master_en", "master_en", "terminology", "tasks", "batches", "counts", "packet_policy", "manifest_sha256"}, "packet manifest")
    _validate_seal(manifest, "manifest_sha256", "packet manifest")
    if manifest["schema"] != PACKET_SCHEMA or manifest["packet_policy"] != "ordered_hash_bound_units_v1":
        raise MasterRuError("invalid packet policy")
    accepted_path = _resolve_identity(authority_root, manifest["accepted_master_en"], "accepted MASTER_EN")
    master_path = _resolve_identity(authority_root, manifest["master_en"], "MASTER_EN")
    _validate_acceptance(accepted_path, authority_root, "master_en", master_path)
    terminology_roles: set[str] = set()
    terminology_authorities = []
    for row in manifest["terminology"]:
        _exact(row, {"role", "file"}, "terminology record")
        if not isinstance(row["role"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", row["role"]) or row["role"] in terminology_roles:
            raise MasterRuError("duplicate or invalid terminology role")
        terminology_roles.add(row["role"])
        terminology_authorities.append((row["role"], _resolve_identity(authority_root, row["file"], f"terminology {row['role']}")))
    if not terminology_roles:
        raise MasterRuError("packet has no terminology authority")
    parsed_terms = _terminology_terms(terminology_authorities)
    if require_complete_system_profile:
        _require_coc7e_statblock_profile(
            parsed_terms, master_path.read_text(encoding="utf-8")
        )
    tasks_path = _resolve_identity(packet_root, manifest["tasks"], "translation tasks")
    tasks = _read(tasks_path)
    _exact(tasks, {"schema", "scenario_id", "units"}, "translation tasks")
    if tasks["schema"] != "kb_creator.master_ru_translation_tasks.v1" or tasks["scenario_id"] != manifest["scenario_id"] or not isinstance(tasks["units"], list) or not tasks["units"]:
        raise MasterRuError("translation tasks mismatch")
    if not isinstance(manifest["batches"], list) or not manifest["batches"]:
        raise MasterRuError("packet has no batches")
    observed_ids: list[str] = []
    observed_units: list[str] = []
    for index, row in enumerate(manifest["batches"], 1):
        _exact(row, {"batch_id", "input", "output_path", "unit_ids"}, "packet batch")
        expected_id = f"batch-{index:04d}"
        if row["batch_id"] != expected_id or row["output_path"] != f"batches/{expected_id}.ru.json" or not isinstance(row["unit_ids"], list) or not row["unit_ids"]:
            raise MasterRuError("packet batch order or shape mismatch")
        batch_path = _resolve_identity(packet_root, row["input"], f"packet batch {index}")
        batch = _read(batch_path)
        _exact(batch, {"schema", "batch_id", "instructions", "units"}, "translation batch")
        batch_units_value = batch["units"]
        if batch["schema"] != "kb_creator.translation_batch.v1" or batch["batch_id"] != expected_id or not isinstance(batch_units_value, list) or [unit.get("unit_id") for unit in batch_units_value if isinstance(unit, dict)] != row["unit_ids"]:
            raise MasterRuError("translation batch identity or units mismatch")
        observed_ids.append(expected_id); observed_units.extend(row["unit_ids"])
    task_ids = [row.get("unit_id") for row in tasks["units"] if isinstance(row, dict)]
    if observed_units != task_ids or len(observed_units) != len(set(observed_units)):
        raise MasterRuError("translation packet unit order or cardinality mismatch")
    counts = manifest["counts"]
    _exact(counts, {"original_units", "translation_units", "batches", "source_chars"}, "packet counts")
    original_units = len({str(row.get("parent_unit_id") or row.get("unit_id")) for row in tasks["units"] if isinstance(row, dict)})
    if counts != {"original_units": original_units, "translation_units": len(task_ids), "batches": len(observed_ids), "source_chars": len(master_path.read_text(encoding="utf-8"))}:
        raise MasterRuError("translation packet counts mismatch")
    return manifest


_TRANSLATION_BATCH_KEYS = {"schema", "batch_id", "instructions", "units"}
_TRANSLATION_UNIT_KEYS = {
    "unit_id", "parent_unit_id", "part_index", "part_count", "page",
    "source_hash", "part_source_hash", "source_text", "ru_text",
}

_SOURCE_PAGE_UNIT = re.compile(r"<!--\s*source-page-(\d{3,})\s*-->")


def _closed_translated_batch(en: object, ru: object, label: str) -> list[str]:
    source = _exact(en, _TRANSLATION_BATCH_KEYS, f"{label} source")
    translated = _exact(ru, _TRANSLATION_BATCH_KEYS, f"{label} translation")
    if (
        translated["schema"] != "kb_creator.translation_batch.v1"
        or translated["schema"] != source["schema"]
        or translated["batch_id"] != source["batch_id"]
        or translated["instructions"] != source["instructions"]
        or not isinstance(source["units"], list)
        or not isinstance(translated["units"], list)
        or len(translated["units"]) != len(source["units"])
    ):
        raise MasterRuError(f"{label} outer shape mismatch")
    texts: list[str] = []
    for index, (source_unit, translated_unit) in enumerate(zip(source["units"], translated["units"])):
        source_row = _exact(source_unit, _TRANSLATION_UNIT_KEYS, f"{label} source unit {index}")
        translated_row = _exact(translated_unit, _TRANSLATION_UNIT_KEYS, f"{label} translated unit {index}")
        for key in _TRANSLATION_UNIT_KEYS - {"ru_text"}:
            if translated_row[key] != source_row[key]:
                raise MasterRuError(f"{label} changed source field {key} at unit {index}")
        text = translated_row["ru_text"]
        if not isinstance(text, str) or not text.strip():
            raise MasterRuError(f"{label} has empty ru_text at unit {index}")
        texts.append(text.strip())
    return texts


def _boundary_join(left: str, right: str) -> tuple[str, str]:
    """Return the only two page-boundary joins supported by MASTER_EN v3."""
    if left.endswith("-"):
        return left[:-1] + right, "dehyphenated_word"
    return left + " " + right, "continued_prose"


_MARKDOWN_FRAME = re.compile(
    r"^(?P<indent>[ \t]*)(?P<quote>(?:>[ \t]*)*)(?P<heading>#{1,6}[ \t]+)?"
    r"(?P<body>.*?)(?P<hard_break>[ \t]{2,})?$"
)
_MECHANICS_TOKEN = re.compile(
    r"(?<![\w])(?:\d+d\d+(?:[+-]\d+)?|\d+%|\d+(?:[.,]\d+)?)(?![\w])",
    flags=re.IGNORECASE,
)


def _markdown_frame(line: str) -> dict[str, str]:
    """Split only the Markdown shell that translation must preserve."""
    match = _MARKDOWN_FRAME.fullmatch(line)
    if match is None:
        raise MasterRuError("cannot parse Markdown line frame")
    return {key: value or "" for key, value in match.groupdict().items()}


def _markdown_payload_key(text: str) -> str:
    """Return lexical payload while ignoring quote/heading/line boundaries."""
    return " ".join(
        part
        for line in text.splitlines()
        if (part := " ".join(_markdown_frame(line)["body"].split()))
    )


def _apply_markdown_frame(frame: Mapping[str, str], body: str) -> str:
    return (
        str(frame["indent"])
        + str(frame["quote"])
        + str(frame["heading"])
        + body.strip()
        + str(frame["hard_break"])
    )


def _split_translated_heading_payload(
    translated_body: str,
    current_heading_body: str,
    current_tail_body: str,
) -> tuple[str, str] | None:
    """Split a formerly inline translated stat-block title without translating."""
    if _mechanics(current_heading_body) or not _mechanics(current_tail_body):
        return None
    first_mechanic = _MECHANICS_TOKEN.search(translated_body)
    if first_mechanic is None:
        return None
    before_number = translated_body[:first_mechanic.start()].rstrip()
    label = re.search(r"\S+$", before_number)
    if label is None or label.start() == 0:
        return None
    heading = translated_body[:label.start()].rstrip()
    tail = translated_body[label.start():].lstrip()
    if not heading or not tail:
        return None
    return heading, tail


def _reframe_markdown_translation(
    prior_source: str,
    current_source: str,
    prior_translation: str,
) -> str | None:
    """Project a proven quote/heading-only source change onto translated text."""
    if (
        _markdown_payload_key(prior_source) != _markdown_payload_key(current_source)
        or _mechanics(prior_source) != _mechanics(current_source)
        or _structure_signature(prior_source) != _structure_signature(prior_translation)
    ):
        return None

    prior_lines = prior_source.splitlines()
    current_lines = current_source.splitlines()
    translated_lines = prior_translation.splitlines()
    if len(prior_lines) != len(translated_lines):
        return None

    prior_frames = [_markdown_frame(line) for line in prior_lines]
    current_frames = [_markdown_frame(line) for line in current_lines]
    translated_frames = [_markdown_frame(line) for line in translated_lines]
    output: list[str] = []
    prior_index = 0
    current_index = 0
    while prior_index < len(prior_frames) and current_index < len(current_frames):
        prior_body = " ".join(prior_frames[prior_index]["body"].split())
        current_body = " ".join(current_frames[current_index]["body"].split())
        translated_body = translated_frames[prior_index]["body"]
        if prior_body == current_body:
            output.append(_apply_markdown_frame(current_frames[current_index], translated_body))
            prior_index += 1
            current_index += 1
            continue

        if current_index + 1 >= len(current_frames):
            return None
        next_body = " ".join(current_frames[current_index + 1]["body"].split())
        if prior_body != f"{current_body} {next_body}".strip():
            return None
        if not current_frames[current_index]["heading"] or current_frames[current_index + 1]["heading"]:
            return None
        split = _split_translated_heading_payload(translated_body, current_body, next_body)
        if split is None:
            return None
        heading, tail = split
        output.append(_apply_markdown_frame(current_frames[current_index], heading))
        output.append(_apply_markdown_frame(current_frames[current_index + 1], tail))
        prior_index += 1
        current_index += 2

    if prior_index != len(prior_frames) or current_index != len(current_frames):
        return None
    transformed = "\n".join(output)
    if (
        _markdown_payload_key(transformed) != _markdown_payload_key(prior_translation)
        or _structure_signature(current_source) != _structure_signature(transformed)
    ):
        return None
    return transformed


_PROVENANCE_INPUT_KEYS = {
    "publication_contract", "reconstruction_inventory",
    "reconstruction_acceptance", "reconstructed_en",
}
_PROVENANCE_PROJECTION_KEYS = {
    "output_name", "excluded_source_pages", "page_marker_policy",
    "anchor_policy", "asset_policy",
}
_PROVENANCE_DERIVED_KEYS = {
    "source_pages", "excluded_pages", "anchors", "headings", "assets",
    "page_boundary_joins",
}
_TRANSITION_KEYS = {
    "from_page", "to_page", "mode", "left_line_sha256", "right_line_sha256",
}


def _closed_file_record(value: object, label: str) -> dict[str, Any]:
    row = _exact(value, {"path", "bytes", "sha256"}, label)
    if (
        not isinstance(row["path"], str)
        or not row["path"]
        or not isinstance(row["bytes"], int)
        or isinstance(row["bytes"], bool)
        or row["bytes"] < 0
        or not isinstance(row["sha256"], str)
        or HEX.fullmatch(row["sha256"]) is None
    ):
        raise MasterRuError(f"{label} identity shape mismatch")
    return row


def _validated_transition_ledger(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise MasterRuError("MASTER_EN provenance transition ledger must be a list")
    result: list[dict[str, Any]] = []
    page_pairs: set[tuple[int, int]] = set()
    for index, item in enumerate(value):
        row = _exact(item, _TRANSITION_KEYS, f"MASTER_EN provenance transition {index}")
        from_page = row["from_page"]
        to_page = row["to_page"]
        if (
            not isinstance(from_page, int)
            or isinstance(from_page, bool)
            or from_page < 1
            or not isinstance(to_page, int)
            or isinstance(to_page, bool)
            or to_page != from_page + 1
            or row["mode"] not in {"dehyphenated_word", "continued_prose"}
            or not isinstance(row["left_line_sha256"], str)
            or HEX.fullmatch(row["left_line_sha256"]) is None
            or not isinstance(row["right_line_sha256"], str)
            or HEX.fullmatch(row["right_line_sha256"]) is None
        ):
            raise MasterRuError(f"MASTER_EN provenance transition {index} is invalid")
        pair = (from_page, to_page)
        if pair in page_pairs:
            raise MasterRuError("MASTER_EN provenance has duplicate page transition")
        page_pairs.add(pair)
        result.append(dict(row))
    return result


def _validate_master_en_provenance(
    provenance_path: Path,
    master_en: Path,
    scenario_id: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    value = _read(provenance_path)
    _exact(
        value,
        {"schema", "scenario_id", "inputs", "projection", "master_en", "derived", "page_boundary_transitions"},
        "MASTER_EN provenance",
    )
    if value["schema"] != MASTER_EN_PROVENANCE_SCHEMA or value["scenario_id"] != scenario_id:
        raise MasterRuError("current MASTER_EN provenance authority mismatch")
    inputs = _exact(value["inputs"], _PROVENANCE_INPUT_KEYS, "MASTER_EN provenance inputs")
    for name, record in inputs.items():
        _closed_file_record(record, f"MASTER_EN provenance input {name}")
    projection = _exact(value["projection"], _PROVENANCE_PROJECTION_KEYS, "MASTER_EN provenance projection")
    excluded = projection["excluded_source_pages"]
    if (
        projection["output_name"] != master_en.name
        or projection["page_marker_policy"] != "source_page_comment_v1"
        or projection["anchor_policy"] != "preserve_v1"
        or projection["asset_policy"] != "copy_markdown_references_v1"
        or not isinstance(excluded, list)
        or any(not isinstance(page, int) or isinstance(page, bool) or page < 1 for page in excluded)
        or len(excluded) != len(set(excluded))
    ):
        raise MasterRuError("current MASTER_EN provenance projection mismatch")
    master_record = _closed_file_record(value["master_en"], "MASTER_EN provenance master_en")
    if master_record != _identity(master_en, master_en.parent):
        raise MasterRuError("current MASTER_EN provenance master identity mismatch")
    derived = _exact(value["derived"], _PROVENANCE_DERIVED_KEYS, "MASTER_EN provenance derived")
    if any(not isinstance(derived[key], int) or isinstance(derived[key], bool) or derived[key] < 0 for key in _PROVENANCE_DERIVED_KEYS):
        raise MasterRuError("current MASTER_EN provenance derived metrics mismatch")
    transitions = _validated_transition_ledger(value["page_boundary_transitions"])
    if derived["page_boundary_joins"] != len(transitions):
        raise MasterRuError("current MASTER_EN provenance transition count mismatch")
    return value, transitions


def _resolve_current_master_en_provenance(
    manifest: Mapping[str, Any],
    authority_root: Path,
) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    """Resolve the v3 provenance through the current accepted producer stage."""
    authority = authority_root.resolve()
    master_en = _resolve_identity(authority, manifest["master_en"], "current MASTER_EN")
    acceptance_path = _resolve_identity(authority, manifest["accepted_master_en"], "accepted current MASTER_EN")
    acceptance = _validate_acceptance(acceptance_path, authority, "master_en", master_en)
    if acceptance["scenario_id"] != manifest["scenario_id"]:
        raise MasterRuError("current MASTER_EN acceptance scenario mismatch")
    producer_path = _resolve_identity(authority, acceptance["producer_stage"], "current MASTER_EN producer stage")
    stage = _read(producer_path)
    _exact(stage, {"schema", "reproducible", "execution", "reproducible_sha256"}, "current MASTER_EN producer stage")
    reproducible = _exact(
        stage["reproducible"],
        {
            "stage_id", "stage_name", "stage_version", "state", "run_identity_sha256",
            "upstream", "inputs", "adapter", "effective_config", "tools",
            "implementation_inventory_sha256", "outputs", "evidence", "cache_key",
        },
        "current MASTER_EN producer reproducible stage",
    )
    expected_seal = _sha_bytes(_canonical({"schema": stage["schema"], "reproducible": reproducible}))
    if (
        stage["schema"] != PUBLICATION_STAGE_SCHEMA
        or stage["reproducible_sha256"] != expected_seal
        or reproducible["stage_name"] != "master_en_candidate"
        or reproducible["stage_version"] != 1
        or reproducible["state"] != "succeeded"
    ):
        raise MasterRuError("current MASTER_EN producer stage authority mismatch")
    outputs = _exact(reproducible["outputs"], {"root", "files", "inventory_sha256"}, "current MASTER_EN producer outputs")
    relative_root = _safe(outputs["root"], "current MASTER_EN producer output root")
    output_root = _within(authority / relative_root, authority, "current MASTER_EN producer output root")
    if output_root != master_en.parent.resolve() or not output_root.is_dir() or _is_reparse(output_root):
        raise MasterRuError("current MASTER_EN producer output root mismatch")
    files = outputs["files"]
    if not isinstance(files, list) or outputs["inventory_sha256"] != _sha_bytes(_canonical(files)):
        raise MasterRuError("current MASTER_EN producer output inventory mismatch")
    by_path: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(files):
        row = _closed_file_record(item, f"current MASTER_EN producer output {index}")
        if row["path"] in by_path:
            raise MasterRuError("current MASTER_EN producer output inventory has duplicate path")
        _resolve_identity(output_root, row, f"current MASTER_EN producer output {index}")
        by_path[row["path"]] = row
    expected_master = _identity(master_en, output_root)
    if by_path.get(expected_master["path"]) != expected_master:
        raise MasterRuError("current MASTER_EN is not hash-bound by its producer stage")
    provenance_path = master_en.with_name("MASTER_EN.provenance.json")
    expected_provenance = _identity(provenance_path, output_root) if provenance_path.is_file() else None
    if expected_provenance is None or by_path.get("MASTER_EN.provenance.json") != expected_provenance:
        raise MasterRuError("current MASTER_EN provenance is not hash-bound by its producer stage")
    provenance, transitions = _validate_master_en_provenance(provenance_path, master_en, str(manifest["scenario_id"]))
    return provenance_path, provenance, transitions


def _prior_boundary_transition(
    prior_units: Sequence[Mapping[str, Any]],
    prior_index: int,
) -> dict[str, Any] | None:
    marker = str(prior_units[prior_index + 1].get("source_text", ""))
    marker_match = _SOURCE_PAGE_UNIT.fullmatch(marker)
    if marker_match is None:
        return None
    previous_match = next(
        (
            match
            for index in range(prior_index - 1, -1, -1)
            if (match := _SOURCE_PAGE_UNIT.fullmatch(str(prior_units[index].get("source_text", "")))) is not None
        ),
        None,
    )
    if previous_match is None:
        return None
    left = str(prior_units[prior_index].get("source_text", ""))
    right = str(prior_units[prior_index + 2].get("source_text", ""))
    left_lines = left.splitlines()
    right_lines = right.splitlines()
    if not left_lines or not right_lines:
        return None
    _joined, mode = _boundary_join(left, right)
    return {
        "from_page": int(previous_match.group(1)),
        "to_page": int(marker_match.group(1)),
        "mode": mode,
        "left_line_sha256": _sha_bytes(left_lines[-1].rstrip().encode("utf-8")),
        "right_line_sha256": _sha_bytes(right_lines[0].lstrip().encode("utf-8")),
    }


def _rebind_translation_units(
    prior_units: Sequence[Mapping[str, Any]],
    current_units: Sequence[Mapping[str, Any]],
    page_boundary_transitions: object,
) -> tuple[list[str], list[dict[str, Any]]]:
    """Rebind prior translation through exact units or ledger-proved page joins."""
    transitions = _validated_transition_ledger(page_boundary_transitions)
    available: dict[str, list[int]] = {}
    structural_available: dict[str, list[int]] = {}
    for index, row in enumerate(prior_units):
        source = str(row.get("source_text", ""))
        ru_text = row.get("ru_text")
        if not source or not isinstance(ru_text, str) or not ru_text.strip():
            raise MasterRuError("prior translation unit is incomplete")
        available.setdefault(source, []).append(index)
        structural_available.setdefault(_markdown_payload_key(source), []).append(index)

    used: set[int] = set()
    consumed_transitions: set[int] = set()
    translated: list[str] = []
    report: list[dict[str, Any]] = []
    for current_index, current in enumerate(current_units):
        source = str(current.get("source_text", ""))
        candidates = [index for index in available.get(source, []) if index not in used]
        if candidates:
            prior_index = candidates[0]
            used.add(prior_index)
            translated.append(str(prior_units[prior_index]["ru_text"]).strip())
            report.append({
                "unit_id": current.get("unit_id"),
                "mode": "exact_source",
                "prior_unit_ids": [prior_units[prior_index].get("unit_id")],
            })
            continue

        structural_matches: list[tuple[int, str]] = []
        for prior_index in structural_available.get(_markdown_payload_key(source), []):
            if prior_index in used:
                continue
            reframed = _reframe_markdown_translation(
                str(prior_units[prior_index].get("source_text", "")),
                source,
                str(prior_units[prior_index].get("ru_text", "")),
            )
            if reframed is not None:
                structural_matches.append((prior_index, reframed))
        if structural_matches:
            prior_index, reframed = structural_matches[0]
            used.add(prior_index)
            translated.append(reframed)
            report.append({
                "unit_id": current.get("unit_id"),
                "mode": "markdown_structure_only",
                "prior_unit_ids": [prior_units[prior_index].get("unit_id")],
                "payload_sha256": _sha_bytes(_markdown_payload_key(source).encode("utf-8")),
            })
            continue

        matches: list[tuple[int, int, str, dict[str, Any]]] = []
        text_shaped_match = False
        for prior_index in range(len(prior_units) - 2):
            if prior_index in used or prior_index + 1 in used or prior_index + 2 in used:
                continue
            left = str(prior_units[prior_index].get("source_text", ""))
            marker = str(prior_units[prior_index + 1].get("source_text", ""))
            right = str(prior_units[prior_index + 2].get("source_text", ""))
            if _SOURCE_PAGE_UNIT.fullmatch(marker) is None:
                continue
            joined, mode = _boundary_join(left, right)
            next_source = (
                str(current_units[current_index + 1].get("source_text", ""))
                if current_index + 1 < len(current_units)
                else ""
            )
            if joined == source and next_source == marker:
                text_shaped_match = True
                proof = _prior_boundary_transition(prior_units, prior_index)
                if proof is None or proof["mode"] != mode:
                    continue
                marker_match = _SOURCE_PAGE_UNIT.fullmatch(next_source)
                if marker_match is None or int(marker_match.group(1)) != proof["to_page"]:
                    continue
                for transition_index, transition in enumerate(transitions):
                    if transition_index not in consumed_transitions and transition == proof:
                        matches.append((prior_index, transition_index, mode, proof))
        if len(matches) != 1:
            if text_shaped_match:
                raise MasterRuError(
                    f"translation rebind source for {current.get('unit_id')} is not authorized by current MASTER_EN provenance"
                )
            raise MasterRuError(
                f"translation rebind cannot prove exactly one source for {current.get('unit_id')}"
            )
        prior_index, transition_index, mode, proof = matches[0]
        left_ru = str(prior_units[prior_index]["ru_text"]).strip()
        right_ru = str(prior_units[prior_index + 2]["ru_text"]).strip()
        joined_ru, ru_mode = _boundary_join(left_ru, right_ru)
        if ru_mode != mode:
            raise MasterRuError("translation rebind translated boundary mode mismatch")
        used.update({prior_index, prior_index + 2})
        consumed_transitions.add(transition_index)
        translated.append(joined_ru)
        report.append({
            "unit_id": current.get("unit_id"),
            "mode": mode,
            "prior_unit_ids": [
                prior_units[prior_index].get("unit_id"),
                prior_units[prior_index + 2].get("unit_id"),
            ],
            "source_page_marker": str(prior_units[prior_index + 1].get("source_text")),
            "provenance_transition": proof,
        })

    if used != set(range(len(prior_units))):
        unused = [str(prior_units[index].get("unit_id")) for index in range(len(prior_units)) if index not in used]
        raise MasterRuError(f"translation rebind left prior units unused: {unused}")
    if consumed_transitions != set(range(len(transitions))):
        unused = [transitions[index] for index in range(len(transitions)) if index not in consumed_transitions]
        raise MasterRuError(f"translation rebind left provenance transitions unused: {unused}")
    return translated, report


def _validated_translated_units(
    packet_root: Path,
    batch_root: Path,
    authority_root: Path,
    *,
    require_complete_system_profile: bool = True,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = _validate_packet(
        packet_root,
        authority_root,
        require_complete_system_profile=require_complete_system_profile,
    )
    expected_names = [Path(row["output_path"]).name for row in manifest["batches"]]
    if not batch_root.is_dir() or _is_reparse(batch_root):
        raise MasterRuError("prior translated batch root must be an existing non-reparse directory")
    observed = sorted(path.name for path in batch_root.iterdir())
    if observed != sorted(expected_names):
        raise MasterRuError("prior translated batch root must contain exactly the expected batch files")
    units: list[dict[str, Any]] = []
    for index, (batch_row, name) in enumerate(zip(manifest["batches"], expected_names)):
        en_path = _resolve_identity(packet_root, batch_row["input"], f"prior packet batch {index}")
        ru_path = batch_root / name
        en = _read(en_path)
        ru = _read(ru_path)
        texts = _closed_translated_batch(en, ru, f"prior translated batch {name}")
        _validated, findings = validate_batch(en_path, ru_path)
        if findings:
            raise MasterRuError(f"prior translated batch validation failed: {findings}")
        for source_row, ru_text in zip(en["units"], texts):
            units.append({**source_row, "ru_text": ru_text})
    return manifest, units


def rebind_batches(
    packet_root: Path,
    prior_packet_root: Path,
    prior_batch_root: Path,
    destination: Path,
    report_path: Path,
    authority_root: Path,
    prior_authority_root: Path,
) -> dict[str, Any]:
    """Materialize current translated batches from a validated prior packet."""
    authority = authority_root.resolve()
    prior_authority = prior_authority_root.resolve()
    packet = _within(packet_root, authority, "packet root")
    prior_packet = _within(prior_packet_root, prior_authority, "prior packet root")
    prior_batches = _within(prior_batch_root, prior_authority, "prior translated batch root")
    target = _within(destination, authority, "rebound batch destination")
    report_target = _within(report_path, authority, "translation rebind report")
    if target.exists() or report_target.exists() or not target.parent.is_dir() or not report_target.parent.is_dir():
        raise MasterRuError("rebind destinations must be absent under existing parents")
    current_manifest = _validate_packet(packet, authority)
    # A current complete system authority may migrate a reviewed translation
    # from a legacy packet whose authority was incomplete.  The prior packet is
    # still identity-, structure-, source-, and batch-validated; only the new
    # packet is allowed to supply the now-mandatory terminology profile.
    prior_manifest, prior_units = _validated_translated_units(
        prior_packet,
        prior_batches,
        prior_authority,
        require_complete_system_profile=False,
    )
    if current_manifest["scenario_id"] != prior_manifest["scenario_id"]:
        raise MasterRuError("translation rebind scenario mismatch")
    provenance_path, _provenance, transitions = _resolve_current_master_en_provenance(
        current_manifest, authority
    )

    current_batches = [
        _read(_resolve_identity(packet, row["input"], f"current packet batch {index}"))
        for index, row in enumerate(current_manifest["batches"])
    ]
    current_units = [unit for batch in current_batches for unit in batch["units"]]
    translations, rows = _rebind_translation_units(prior_units, current_units, transitions)
    by_id = {
        str(unit["unit_id"]): ru_text
        for unit, ru_text in zip(current_units, translations)
    }

    stage = Path(tempfile.mkdtemp(prefix=f".{target.name}.staging.", dir=target.parent))
    try:
        for batch in current_batches:
            translated = json.loads(json.dumps(batch, ensure_ascii=False))
            for unit in translated["units"]:
                unit["ru_text"] = by_id[str(unit["unit_id"])]
            _write(stage / f"{batch['batch_id']}.ru.json", translated)
        report = _seal("kb_creator.master_ru_translation_rebind.v2", {
            "scenario_id": current_manifest["scenario_id"],
            "prior_packet_manifest": _identity(prior_packet / "packet_manifest.json", prior_authority),
            "current_packet_manifest": _identity(packet / "packet_manifest.json", authority),
            "current_master_en_provenance": _identity(provenance_path, authority),
            "prior_batch_root": prior_batches.relative_to(prior_authority).as_posix(),
            "destination": target.relative_to(authority).as_posix(),
            "counts": {
                "prior_units": len(prior_units),
                "current_units": len(current_units),
                "exact_source": sum(row["mode"] == "exact_source" for row in rows),
                "markdown_structure_only": sum(row["mode"] == "markdown_structure_only" for row in rows),
                "dehyphenated_word": sum(row["mode"] == "dehyphenated_word" for row in rows),
                "continued_prose": sum(row["mode"] == "continued_prose" for row in rows),
                "provenance_transitions": len(transitions),
            },
            "rows": rows,
        }, "report_sha256")
        os.replace(stage, target)
        try:
            _write(report_target, report)
        except Exception:
            shutil.rmtree(target, ignore_errors=True)
            raise
        return {"status": "pass", **report}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def validate_submission(packet_root: Path, submission_path: Path, authority_root: Path) -> dict[str, Any]:
    packet_root = packet_root.resolve(); authority_root = authority_root.resolve(); submission_path = _within(submission_path, authority_root, "MASTER_RU submission"); manifest = _validate_packet(packet_root, authority_root)
    submission = _read(submission_path); _exact(submission, {"schema", "scenario_id", "accepted_master_en", "packet_manifest", "units", "batches", "review", "submission_sha256"}, "MASTER_RU submission"); _validate_seal(submission, "submission_sha256", "MASTER_RU submission")
    if submission["schema"] != SUBMISSION_SCHEMA or submission["scenario_id"] != manifest["scenario_id"] or submission["review"] != {"state": "closed", "unresolved": []} or submission["accepted_master_en"] != manifest["accepted_master_en"] or submission["packet_manifest"] != _identity(packet_root / "packet_manifest.json", authority_root):
        raise MasterRuError("MASTER_RU submission authority mismatch")
    expected_batch_ids = [row["batch_id"] for row in manifest["batches"]]
    if not isinstance(submission["batches"], list) or len(submission["batches"]) != len(expected_batch_ids):
        raise MasterRuError("MASTER_RU submission batch cardinality mismatch")
    terminology_authorities = [
        (row["role"], _resolve_identity(authority_root, row["file"], f"terminology {row['role']}"))
        for row in manifest["terminology"]
    ]
    terms = _terminology_terms(terminology_authorities)
    merged: list[dict[str, Any]] = []; findings: list[dict[str, Any]] = []
    replacement_events: list[dict[str, Any]] = []
    for index, batch_row in enumerate(manifest["batches"]):
        en_path = _resolve_identity(packet_root, batch_row["input"], f"packet batch {index}")
        ru_path = _resolve_identity(authority_root, submission["batches"][index], f"submitted batch {index}")
        if Path(batch_row["output_path"]).name != ru_path.name:
            raise MasterRuError("submitted batch order/name mismatch")
        units, batch_findings = validate_batch(en_path, ru_path)
        findings.extend(batch_findings)
        en = _read(en_path); ru = _read(ru_path)
        _closed_translated_batch(en, ru, f"submitted batch {expected_batch_ids[index]}")
        if ru.get("schema") != "kb_creator.translation_batch.v1" or ru.get("batch_id") != expected_batch_ids[index] or [row.get("unit_id") for row in ru.get("units", [])] != batch_row["unit_ids"]:
            findings.append({"code": "submitted_batch_shape_or_order", "batch_id": expected_batch_ids[index]})
        by_id = {row.get("unit_id"): row for row in ru.get("units", []) if isinstance(row, dict)}
        for source_row in en["units"]:
            translated = by_id.get(source_row["unit_id"], {}); ru_text = str(translated.get("ru_text") or translated.get("ru") or "").strip()
            ru_text, events = _normalize_system_terminology(
                source_row["source_text"], ru_text, terms, source_row["unit_id"]
            )
            replacement_events.extend(events)
            if _structure_signature(source_row["source_text"]) != _structure_signature(ru_text):
                findings.append({"code": "markdown_or_mechanics_drift", "unit_id": source_row["unit_id"]})
            merged.append({"unit_id": source_row["unit_id"], "source_sha256": str(source_row["source_hash"]).upper(), "russian_payload_sha256": _sha_bytes(ru_text.encode("utf-8")), "source_text": source_row["source_text"], "ru_text": ru_text})
    declared = submission["units"]
    expected_units = [{key: row[key] for key in ("unit_id", "source_sha256", "russian_payload_sha256")} for row in merged]
    if declared != expected_units:
        findings.append({"code": "submission_unit_order_or_hash_mismatch"})
    term_checks = []
    authorized_skills = tuple(str(item["source"]) for item in terms if item.get("domain") == "skill")
    for term in terms:
        matched = [row for row in merged if _term_present(term["source"], row["source_text"])]
        if not matched:
            term_checks.append({
                "source": term["source"], "target": term["target"], "accepted": term["targets"],
                "bad": term["bad"], "authority": term["authorities"][0], "authorities": term["authorities"],
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
            term = _contextual_term(context_base_term, unit["source_text"])
            context = _term_context(term, unit["source_text"], authorized_skills=authorized_skills)
            applicability = context["applicability"]
            required = applicability in {"required_general", "required_skill"}
            present = required and any(_term_present(target, unit["ru_text"]) for target in term["targets"])
            bad_present = [
                bad for bad in term["bad"]
                if required and _bad_variant_present(bad, term["targets"], unit["ru_text"])
            ]
            check = {
                "source": term["source"], "target": term["target"], "accepted": term["targets"],
                "bad": term["bad"], "authority": term["authorities"][0], "authorities": term["authorities"],
                "domain": term["domain"], "unit_id": unit["unit_id"], "required": required,
                "applicability": applicability, "context": context,
                "present": present, "bad_present": bad_present,
            }
            term_checks.append(check)
            if applicability == "ambiguous":
                findings.append({
                    "code": "terminology_context_ambiguous", "source": term["source"],
                    "domain": term["domain"], "authority": term["authorities"][0],
                    "authorities": term["authorities"], "unit_id": unit["unit_id"],
                    "context": context,
                })
            elif required and not present:
                findings.append({
                    "code": "terminology_target_missing", "source": term["source"], "target": term["target"],
                    "authority": term["authorities"][0], "authorities": term["authorities"], "unit_id": unit["unit_id"],
                })
            if bad_present:
                findings.append({
                    "code": "terminology_bad_variant", "source": term["source"], "bad": bad_present,
                    "authority": term["authorities"][0], "authorities": term["authorities"], "unit_id": unit["unit_id"],
                })
    return {"schema": "kb_creator.master_ru_submission_validation.v1", "status": "pass" if not findings else "blocked", "scenario_id": manifest["scenario_id"], "units": merged, "terminology": term_checks, "terminology_replacements": replacement_events, "findings": findings, "submission_sha256": submission["submission_sha256"], "packet_manifest_sha256": manifest["manifest_sha256"]}


def _is_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _require_non_reparse_chain(path: Path, root: Path, label: str) -> None:
    current = path
    authority = root.resolve()
    while True:
        try:
            current.resolve().relative_to(authority)
        except ValueError as error:
            raise MasterRuError(f"{label} escapes authority root") from error
        if current.exists() and _is_reparse(current):
            raise MasterRuError(f"{label} contains a reparse path")
        if current.resolve() == authority:
            return
        current = current.parent


def author_submission(packet_root: Path, batch_root: Path, destination: Path, authority_root: Path) -> dict[str, Any]:
    authority = authority_root.resolve()
    packet = _within(packet_root, authority, "packet root")
    batches = _within(batch_root, authority, "translated batch root")
    target = _within(destination, authority, "MASTER_RU submission destination")
    if not packet.is_dir() or not batches.is_dir() or _is_reparse(packet) or _is_reparse(batches):
        raise MasterRuError("packet and translated batch roots must be existing non-reparse directories")
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise MasterRuError("MASTER_RU submission destination must be absent under an existing parent")
    _require_non_reparse_chain(packet, authority, "packet root")
    _require_non_reparse_chain(batches, authority, "translated batch root")
    _require_non_reparse_chain(target.parent, authority, "submission destination parent")
    manifest = _validate_packet(packet, authority)
    terminology_authorities = [
        (row["role"], _resolve_identity(authority, row["file"], f"terminology {row['role']}"))
        for row in manifest["terminology"]
    ]
    terms = _terminology_terms(terminology_authorities)
    expected_names = [Path(row["output_path"]).name for row in manifest["batches"]]
    observed = sorted(path.name for path in batches.iterdir())
    if observed != sorted(expected_names) or len(observed) != len(expected_names):
        raise MasterRuError("translated batch root must contain exactly the expected batch files")
    batch_records: list[dict[str, Any]] = []
    declared_units: list[dict[str, Any]] = []
    for index, (batch_row, expected_name) in enumerate(zip(manifest["batches"], expected_names)):
        en_path = _resolve_identity(packet, batch_row["input"], f"packet batch {index}")
        ru_path = batches / expected_name
        if not ru_path.is_file() or _is_reparse(ru_path):
            raise MasterRuError(f"translated batch is missing or reparse: {expected_name}")
        en = _read(en_path)
        ru = _read(ru_path)
        texts = _closed_translated_batch(en, ru, f"translated batch {expected_name}")
        _units, findings = validate_batch(en_path, ru_path)
        if findings:
            raise MasterRuError(f"translated batch validation failed: {findings}")
        for source_row, ru_text in zip(en["units"], texts):
            ru_text, _events = _normalize_system_terminology(
                source_row["source_text"], ru_text, terms, source_row["unit_id"]
            )
            declared_units.append({
                "unit_id": source_row["unit_id"],
                "source_sha256": str(source_row["source_hash"]).upper(),
                "russian_payload_sha256": _sha_bytes(ru_text.encode("utf-8")),
            })
        batch_records.append(_identity(ru_path, authority))
    draft = _seal(SUBMISSION_SCHEMA, {
        "scenario_id": manifest["scenario_id"],
        "accepted_master_en": manifest["accepted_master_en"],
        "packet_manifest": _identity(packet / "packet_manifest.json", authority),
        "units": declared_units,
        "batches": batch_records,
        "review": {"state": "closed", "unresolved": []},
    }, "submission_sha256")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.staging.", dir=target.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_bytes(_canonical(draft) + b"\n")
        validation = validate_submission(packet, temporary, authority)
        if validation["status"] != "pass":
            raise MasterRuError(f"MASTER_RU submission blocked: {validation['findings']}")
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {
        "status": "pass",
        "scenario_id": manifest["scenario_id"],
        "submission": _identity(target, authority),
        "submission_sha256": draft["submission_sha256"],
        "batches": len(batch_records),
        "units": len(declared_units),
    }


def _candidate_inventory(root: Path) -> tuple[list[dict[str, Any]], str]:
    rows = []
    for path in sorted((item for item in root.rglob("*") if item.is_file() and item.name != "INVENTORY.json"), key=lambda item: item.relative_to(root).as_posix()):
        rows.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": _sha_file(path)})
    return rows, _sha_bytes("".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in rows).encode("utf-8"))


def assemble(packet_root: Path, submission_path: Path, output_root: Path, authority_root: Path) -> dict[str, Any]:
    validation = validate_submission(packet_root, submission_path, authority_root)
    if validation["status"] != "pass":
        raise MasterRuError(f"MASTER_RU submission blocked: {validation['findings']}")
    output_root = _within(output_root, authority_root.resolve(), "MASTER_RU output")
    if output_root.exists() or not output_root.parent.is_dir():
        raise MasterRuError("MASTER_RU output must be absent under an existing parent")
    manifest = _read(packet_root / "packet_manifest.json"); master_en = _resolve_identity(authority_root.resolve(), manifest["master_en"], "MASTER_EN")
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.staging.", dir=output_root.parent))
    try:
        text = "\n\n".join(row["ru_text"] for row in validation["units"]).strip() + "\n"
        (stage / "MASTER_RU.md").write_text(text, encoding="utf-8", newline="\n")
        asset_rows = []
        for reference in dict.fromkeys(_structure_signature(master_en.read_text(encoding="utf-8"))["image_targets"]):
            relative = _safe(reference, "MASTER_EN asset")
            source = (master_en.parent / relative).resolve()
            try:
                source.relative_to(master_en.parent.resolve())
            except ValueError as error:
                raise MasterRuError("MASTER_EN asset escapes candidate") from error
            if not source.is_file() or source.is_symlink():
                raise MasterRuError(f"MASTER_EN asset missing: {reference}")
            target = stage / relative; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
            asset_rows.append({"path": relative.as_posix(), "bytes": target.stat().st_size, "sha256": _sha_file(target)})
        master_identity = _identity(stage / "MASTER_RU.md", stage)
        provenance = _seal("kb_creator.master_ru_provenance.v1", {"scenario_id": validation["scenario_id"], "accepted_master_en": manifest["accepted_master_en"], "packet_manifest": _identity(packet_root / "packet_manifest.json", authority_root.resolve()), "submission": _identity(submission_path.resolve(), authority_root.resolve()), "unit_order": [row["unit_id"] for row in validation["units"]], "master_ru": master_identity}, "provenance_sha256")
        qa = {"schema": "kb_creator.master_ru_qa.v1", "status": "pass", "scenario_id": validation["scenario_id"], "master_ru": master_identity, "checks": {"ordered_hash_bound_units": True, "markdown_structure": True, "anchors_links_images": True, "numeric_dice_mechanics": True, "shared_terminology": all(not row["required"] or row["present"] for row in validation["terminology"])}, "findings": []}
        assets = {"schema": "kb_creator.master_ru_asset_manifest.v1", "scenario_id": validation["scenario_id"], "assets": asset_rows, "summary": {"total": len(asset_rows)}}
        terminology = {"schema": "kb_creator.master_ru_terminology_qa.v1", "authorities": manifest["terminology"], "checks": validation["terminology"], "replacements": validation["terminology_replacements"], "status": "pass"}
        for name, value in (("MASTER_RU.provenance.json", provenance), ("MASTER_RU.qa.json", qa), ("ASSET_MANIFEST.json", assets), ("TERMINOLOGY.qa.json", terminology)):
            _write(stage / name, value)
        rows, digest = _candidate_inventory(stage)
        _write(stage / "INVENTORY.json", {"schema": "kb_creator.candidate_inventory.v1", "algorithm": "sorted relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>", "rows": rows, "file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows), "inventory_sha256": digest})
        os.replace(stage, output_root)
        return {"status": "awaiting_master_ru_acceptance", "scenario_id": validation["scenario_id"], "master_ru": _identity(output_root / "MASTER_RU.md", output_root), "inventory_sha256": digest}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _parse_terms(values: Sequence[str]) -> dict[str, Path]:
    result = {}
    for value in values:
        if "=" not in value:
            raise MasterRuError("terminology must use role=path")
        role, raw = value.split("=", 1)
        if role in result or not role or not raw:
            raise MasterRuError("duplicate or invalid terminology")
        result[role] = Path(raw)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare"); prepare_parser.add_argument("--master-en", type=Path, required=True); prepare_parser.add_argument("--master-en-acceptance", type=Path, required=True); prepare_parser.add_argument("--terminology", action="append", default=[]); prepare_parser.add_argument("--output-root", type=Path, required=True); prepare_parser.add_argument("--authority-root", type=Path, required=True); prepare_parser.add_argument("--max-batch-chars", type=int, default=3000)
    author_parser = sub.add_parser("author-submission"); author_parser.add_argument("--packet-root", type=Path, required=True); author_parser.add_argument("--batch-root", type=Path, required=True); author_parser.add_argument("--destination", type=Path, required=True); author_parser.add_argument("--authority-root", type=Path, required=True)
    rebind_parser = sub.add_parser("rebind-batches"); rebind_parser.add_argument("--packet-root", type=Path, required=True); rebind_parser.add_argument("--prior-packet-root", type=Path, required=True); rebind_parser.add_argument("--prior-batch-root", type=Path, required=True); rebind_parser.add_argument("--destination", type=Path, required=True); rebind_parser.add_argument("--report", type=Path, required=True); rebind_parser.add_argument("--authority-root", type=Path, required=True); rebind_parser.add_argument("--prior-authority-root", type=Path, required=True)
    validate_parser = sub.add_parser("validate-submission"); validate_parser.add_argument("--packet-root", type=Path, required=True); validate_parser.add_argument("--submission", type=Path, required=True); validate_parser.add_argument("--authority-root", type=Path, required=True)
    assemble_parser = sub.add_parser("assemble"); assemble_parser.add_argument("--packet-root", type=Path, required=True); assemble_parser.add_argument("--submission", type=Path, required=True); assemble_parser.add_argument("--output-root", type=Path, required=True); assemble_parser.add_argument("--authority-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare": result = prepare(args.master_en, args.master_en_acceptance, _parse_terms(args.terminology), args.output_root, args.max_batch_chars, args.authority_root)
        elif args.command == "author-submission": result = author_submission(args.packet_root, args.batch_root, args.destination, args.authority_root)
        elif args.command == "rebind-batches": result = rebind_batches(args.packet_root, args.prior_packet_root, args.prior_batch_root, args.destination, args.report, args.authority_root, args.prior_authority_root)
        elif args.command == "validate-submission": result = validate_submission(args.packet_root, args.submission, args.authority_root)
        else: result = assemble(args.packet_root, args.submission, args.output_root, args.authority_root)
    except (MasterRuError, OSError, ValueError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False), file=__import__("sys").stderr); return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result.get("status") in {"awaiting_master_ru_submission", "awaiting_master_ru_acceptance"}:
        return 10
    return 0 if result.get("status") not in {"blocked", "fail"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
