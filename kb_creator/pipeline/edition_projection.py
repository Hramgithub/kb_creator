"""Source-bound 7e reader-operation validation; source masters are never edited."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


class EditionProjectionError(ValueError):
    pass


CHARACTERISTICS = {"STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU",
                   "СИЛ", "ВЫН", "ТЕЛ", "ИНТ", "МОЩ", "ЛВК", "НАР", "ОБР"}
EDU_LABELS = {"EDU", "ОБР"}
HUMAN_KINDS = {"investigator", "pregen_investigator", "human_npc"}
PROTECTED_FIELDS = {"Luck", "Удача", "HP", "ХП", "MP", "МП", "SAN", "РАС", "MOV", "ПЕР",
                    "armor", "броня", "skill", "навык", "poison_pot", "damage"}


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _selector(value: Any, *, before_value: str, after_value: str) -> None:
    required = {"html_anchor", "part", "paragraph", "table", "cell", "before_text", "after_text",
                "before_sha256", "after_sha256", "before_start", "before_end",
                "after_start", "after_end"}
    if not isinstance(value, dict) or set(value) != required:
        raise EditionProjectionError("operation needs exact HTML/Word text selector")
    if (not isinstance(value["html_anchor"], str) or not value["html_anchor"]
            or value["part"] != "word/document.xml"
            or any(type(value[key]) is not int or value[key] < 0 for key in ("paragraph", "table", "cell"))
            or any(not isinstance(value[key], str) for key in ("before_text", "after_text"))
            or value["before_sha256"] != _sha_text(value["before_text"])
            or value["after_sha256"] != _sha_text(value["after_text"])):
        raise EditionProjectionError("operation text selector identity is stale")
    for prefix, expected in (("before", before_value), ("after", after_value)):
        start, end = value[f"{prefix}_start"], value[f"{prefix}_end"]
        text = value[f"{prefix}_text"]
        if (type(start) is not int or type(end) is not int or start < 0 or end <= start
                or end > len(text) or text[start:end] != expected):
            raise EditionProjectionError(f"operation {prefix} span does not match approved value")


def _characteristic_operand(selector: dict[str, Any], field: str) -> None:
    """Bind the whole visible integer and its actual adjacent field label."""
    for prefix in ("before", "after"):
        text = selector[f"{prefix}_text"]
        start, end = selector[f"{prefix}_start"], selector[f"{prefix}_end"]
        if ((start and text[start - 1] in "0123456789.,")
                or (end < len(text) and text[end] in "0123456789.,%")
                or not re.search(r"(?<!\w)" + re.escape(field) + r"\s*[:=]?\s*$",
                                 text[:start], flags=re.IGNORECASE)):
            raise EditionProjectionError("edition operand is partial or not bound to declared visible field")


def expected_characteristic(field: str, before: int, *, source_edition: str,
                            present_scale: str, entity_kind: str) -> int | None:
    """Return only an evidence-eligible deterministic target; None means review."""
    if type(before) is not int or before < 0:
        raise EditionProjectionError("characteristic must be a nonnegative integer")
    if field not in CHARACTERISTICS:
        return None
    if source_edition == "7e" or present_scale == "7e":
        return before if source_edition == "7e" and present_scale == "7e" else None
    if source_edition != "legacy_proven" or present_scale != "legacy":
        return None
    if field in EDU_LABELS:
        if entity_kind not in HUMAN_KINDS:
            return None
        return before * 5 if before <= 18 else min(99, before + 72)
    return before * 5


def validate_edition_rows(rows: Any, *, source_pdf_sha256: str,
                          source_pages: list[dict[str, Any]], section_domain: list[str],
                          book_id: str, reviewed_domain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Require exact evidence and approved per-occurrence disposition, not ranges."""
    if not isinstance(rows, list):
        raise EditionProjectionError("edition rows must be a list")
    if (not isinstance(book_id, str) or not book_id.strip() or not isinstance(reviewed_domain, list)
            or not isinstance(source_pages, list) or not source_pages):
        raise EditionProjectionError("edition source/occurrence domain is missing")
    page_hashes = {page["page"]: page["render"]["sha256"] for page in source_pages}
    domain: dict[str, dict[str, Any]] = {}
    domain_keys = {"occurrence_id", "book_id", "story_id", "entity_id", "source_page",
                   "field", "source_render_sha256", "decision_reference"}
    for reviewed in reviewed_domain:
        if (not isinstance(reviewed, dict) or set(reviewed) != domain_keys
                or not isinstance(reviewed["occurrence_id"], str) or not reviewed["occurrence_id"]
                or reviewed["occurrence_id"] in domain or reviewed["book_id"] != book_id
                or reviewed["story_id"] not in section_domain
                or not isinstance(reviewed["entity_id"], str) or not reviewed["entity_id"]
                or not isinstance(reviewed["field"], str) or not reviewed["field"]
                or type(reviewed["source_page"]) is not int
                or reviewed["source_render_sha256"] != page_hashes.get(reviewed["source_page"])
                or not isinstance(reviewed["decision_reference"], str)
                or not reviewed["decision_reference"].strip()):
            raise EditionProjectionError("reviewed edition occurrence has foreign book/story/page/owner")
        domain[reviewed["occurrence_id"]] = reviewed
    seen: set[str] = set()
    required = {"occurrence_id", "book_id", "story_id", "entity_id", "source_page",
                "source_pdf_sha256", "source_edition", "present_scale", "entity_kind", "field",
                "before", "after", "action", "rule_id", "decision_reference", "selector"}
    for row in rows:
        if not isinstance(row, dict) or set(row) != required:
            raise EditionProjectionError("edition row has unknown or missing fields")
        oid = row["occurrence_id"]
        if not isinstance(oid, str) or not oid or oid in seen:
            raise EditionProjectionError("edition occurrence identity is missing or duplicate")
        seen.add(oid)
        if (row["source_pdf_sha256"] != source_pdf_sha256 or row["book_id"] != book_id
                or row["story_id"] not in section_domain or type(row["source_page"]) is not int
                or row["source_page"] not in page_hashes
                or oid not in domain
                or any(row[key] != domain[oid][key]
                       for key in ("occurrence_id", "book_id", "story_id", "entity_id", "source_page", "field", "decision_reference"))
                or any(not isinstance(row[key], str) or not row[key].strip()
                                                  for key in ("book_id", "story_id", "entity_id", "decision_reference", "rule_id"))):
            raise EditionProjectionError("edition row lacks exact source/decision authority")
        _selector(row["selector"], before_value=str(row["before"]), after_value=str(row["after"]))
        _characteristic_operand(row["selector"], row["field"])
        action = row["action"]
        if action not in {"convert_deterministic", "keep_7e", "keep_editorial_exception", "keep_source_value"}:
            raise EditionProjectionError("edition row is unresolved")
        if row["field"] in PROTECTED_FIELDS and action == "convert_deterministic":
            raise EditionProjectionError("protected noncharacteristic field cannot be multiplied")
        if action == "convert_deterministic":
            expected = expected_characteristic(row["field"], row["before"],
                                               source_edition=row["source_edition"],
                                               present_scale=row["present_scale"], entity_kind=row["entity_kind"])
            if expected is None or expected == row["before"] or row["after"] != expected:
                raise EditionProjectionError("conversion is not source/scale-bound or has wrong target")
        elif action == "keep_7e":
            if row["source_edition"] != "7e" or row["present_scale"] != "7e" or row["after"] != row["before"]:
                raise EditionProjectionError("keep_7e requires actual current-scale evidence")
        elif row["after"] != row["before"]:
            raise EditionProjectionError("keep disposition cannot change a source value")
    if seen != set(domain):
        raise EditionProjectionError("edition rows do not cover reviewed occurrence domain")
    return rows


def validate_terminology_rows(rows: Any, *, registry_path: Path, overlay_path: Path,
                              registry_sha256: str, overlay_sha256: str,
                              book_id: str) -> list[dict[str, Any]]:
    """Reject unapproved mappings and many-to-one percentage collisions."""
    if not isinstance(rows, list) or not registry_sha256 or not overlay_sha256:
        raise EditionProjectionError("accepted terminology snapshots are required")
    from . import coc_glossary

    try:
        shared = coc_glossary.registry_rows(registry_path.read_bytes())
        book = coc_glossary.overlay_rows(overlay_path.read_bytes())
        if rows:
            derived = coc_glossary._derive(registry_path.read_bytes(), overlay_path.read_bytes(), book_id)
            if derived["conflicts"]:
                raise EditionProjectionError("accepted terminology authorities contain unresolved conflicts")
    except (OSError, UnicodeError, ValueError) as error:
        raise EditionProjectionError(f"accepted terminology authority is invalid: {error}") from error
    normalize = coc_glossary.normalize
    accepted_shared = {normalize(row["source_term"]): row for row in shared if row["status"] == "accepted"}
    accepted_book = {normalize(row["source"]): row for row in book}
    required = {"occurrence_id", "entity_id", "source_label", "source_context", "target_label",
                "percentage", "registry_sha256", "overlay_sha256", "disposition",
                "authority_reference", "collision_decision", "selector"}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != required:
            raise EditionProjectionError("terminology row has unknown or missing fields")
        if (row["occurrence_id"] in seen or row["registry_sha256"] != registry_sha256
                or row["overlay_sha256"] != overlay_sha256 or row["disposition"] not in
                {"accepted_direct_mapping", "accepted_primary_rule_mapping", "keep_editorial_exception"}
                or not row["authority_reference"] or not row["source_context"]):
            raise EditionProjectionError("terminology row is stale or unapproved")
        if row["disposition"] != "accepted_direct_mapping":
            raise EditionProjectionError("unsupported_authority: needs_decision for primary-rule/editorial mapping")
        reference = row["authority_reference"]
        source_key = normalize(row["source_label"])
        if reference == f"registry:{row['source_label']}":
            authority = accepted_shared.get(source_key)
            if authority is None:
                raise EditionProjectionError("accepted_direct_mapping has no accepted registry row")
            target = authority["accepted_ru"]
            aliases = coc_glossary._variants(authority["aliases"])
            domain_name = authority["domain"]
            usage = coc_glossary.usage_rule(authority["notes"])
            if usage is not None:
                if row["source_context"] == "prose":
                    target, aliases = usage["prose"]["target"], usage["prose"]["aliases"]
                elif row["source_context"] != "numeric_label":
                    raise EditionProjectionError("contextual terminology mapping has unknown context")
        elif reference == f"overlay:{row['source_label']}":
            authority = accepted_book.get(source_key)
            if authority is None:
                raise EditionProjectionError("accepted_direct_mapping has no selected book overlay row")
            target, aliases, domain_name = authority["target"], authority["aliases"], authority["domain"]
        else:
            raise EditionProjectionError("accepted_direct_mapping authority reference is not an exact row")
        if (normalize(row["target_label"]) not in {normalize(value) for value in (target, *aliases)}
                or (normalize(domain_name) != "general"
                    and normalize(row["source_context"]) != normalize(domain_name)
                    and not (reference.startswith("registry:") and usage is not None
                             and row["source_context"] in {"prose", "numeric_label"}))):
            raise EditionProjectionError("accepted_direct_mapping target/context is not in accepted authority")
        seen.add(row["occurrence_id"])
        _selector(row["selector"], before_value=row["source_label"], after_value=row["target_label"])
        groups.setdefault((row["entity_id"], row["target_label"]), []).append(row)
    for group in groups.values():
        if len(group) > 1 and len({row["percentage"] for row in group}) > 1:
            if any(not row["collision_decision"] for row in group):
                raise EditionProjectionError("many-to-one skill collision needs an exact decision")
    return rows
