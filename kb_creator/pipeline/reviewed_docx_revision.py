"""Build a sealed, DOCX-only successor of a human-reviewed Word reader.

The source graphic ledger is independent of what the reviewed DOCX already
contains. This route does not reconstruct lost masters or publish HTML/PDF.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from io import BytesIO
from pathlib import Path

from lxml import etree
from PIL import Image

from kb_creator.pipeline.docx_review_comments import _StyleVisibility
from kb_creator.pipeline.reviewed_reader_revision import (
    R, W, WP, NS, RevisionError, _add_word_image, _bookmark, _drawing_order,
    _media_for_drawing, _paragraph_text, _relationships, _replace_word_text,
    _serial, _xml,
)


SCHEMA = "kb_creator.reviewed_docx_revision.v1"
FIELD_LEDGER_SCHEMA = "nri.u7_word_conversion_operations.v1"
FIELD_APPROVED_STATE = "approved_source_bound_operations"
CHARACTERISTICS = {"STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU",
                   "СИЛ", "ВЫН", "ТЕЛ", "ИНТ", "МОЩ", "ЛВК", "НАР", "ОБР"}
DIRECT_SKILL_MAP = {
    "Подкрадывание": "Скрытность", "Прятаться": "Скрытность",
    "Торг": "Убеждение", "Сокрытие": "Ловкость рук",
    "Удар кулаком": "Ближний бой (Драка)",
    "Пистолет": "Стрельба (пистолет)",
    "Винтовка (слоновье ружьё)": "Стрельба (винтовка/дробовик) (слоновье ружьё)",
    "Искусство (Танец)": "Искусство/ремесло (Танец)",
    "Искусство (Живопись)": "Искусство/ремесло (Живопись)",
    "Искусство (Чревовещание)": "Искусство/ремесло (Чревовещание)",
    "Фотография": "Искусство/ремесло (Фотография)",
    "Астрономия": "Наука (Астрономия)",
    "Естественная история": "Естествознание",
    "Искусство": "Искусство/ремесло",
}
PROSE_FIELDS = {"rybin_bodily_stealth"}
FIELD_PATH = re.compile(
    r"word/document\.xml/body\[(\d+)\]/"
    r"(?:(p)|tbl/tr\[(\d+)\]/tc\[(\d+)\]/p\[(\d+)\])/r\[(\d+)\]/t\[(\d+)\]$"
)


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _identity(payload: bytes, declared: object, label: str) -> None:
    if not isinstance(declared, str) or _sha(payload) != declared.upper():
        raise RevisionError(f"{label} SHA-256 mismatch")


def _source_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise RevisionError(f"missing or linked authority input: {path}")
    return path.read_bytes()


def _path_guard(inputs: list[Path], output_root: Path, report_path: Path) -> None:
    resolved = [path.resolve() for path in inputs]
    output_root, report_path = output_root.resolve(), report_path.resolve()
    if output_root.exists() or report_path.exists():
        raise RevisionError("candidate output or report already exists")
    if output_root == report_path or output_root in report_path.parents or report_path in output_root.parents:
        raise RevisionError("candidate output and report overlap")
    for item in resolved:
        if (output_root == item or output_root in item.parents or item in output_root.parents
                or report_path == item or report_path in item.parents):
            raise RevisionError("output aliases or overlaps an authority input")


def _zip_snapshot(payload: bytes) -> dict[str, bytes]:
    try:
        with zipfile.ZipFile(BytesIO(payload)) as archive:
            if archive.testzip() is not None:
                raise RevisionError("reviewed DOCX archive is corrupt")
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise RevisionError("duplicate DOCX package member")
            return {name: archive.read(name) for name in names}
    except zipfile.BadZipFile as exc:
        raise RevisionError("reviewed DOCX is not a ZIP") from exc


def _word_bounds(stories: object, document: etree._Element) -> dict:
    if not isinstance(stories, list) or not stories:
        raise RevisionError("ordered stories are required")
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    bounds = {}
    previous = -1
    for story in stories:
        sid, name = story.get("story_id"), story.get("word_bookmark")
        if not isinstance(sid, str) or not sid or not isinstance(name, str) or not name or sid in bounds:
            raise RevisionError("invalid or duplicate story identity")
        start = paragraphs.index(_bookmark(document, name))
        if start <= previous:
            raise RevisionError("story bookmarks are not in declared order")
        bounds[sid] = {"word_start": start, "word_bookmark": name}
        previous = start
    names = list(bounds)
    for index, sid in enumerate(names):
        bounds[sid]["word_end"] = bounds[names[index + 1]]["word_start"] if index + 1 < len(names) else len(paragraphs)
    return bounds


def _target_paragraph(document, bounds, story_id, selector, expected_text, expected_sha):
    if story_id not in bounds:
        raise RevisionError(f"unknown story: {story_id}")
    if not isinstance(expected_text, str) or not expected_text:
        raise RevisionError("exact paragraph text is required")
    _identity(expected_text.encode("utf-8"), expected_sha, "paragraph context")
    if not isinstance(selector, dict) or selector.get("kind") != "exact_paragraph":
        raise RevisionError("mandatory exact paragraph selector is absent")
    count, ordinal = selector.get("expected_matches"), selector.get("ordinal")
    if (not isinstance(count, int) or isinstance(count, bool) or count < 1
            or not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 0):
        raise RevisionError("invalid paragraph selector count or ordinal")
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    span = bounds[story_id]
    matches = [p for p in paragraphs[span["word_start"]:span["word_end"]]
               if _paragraph_text(p) == expected_text]
    if len(matches) != count or ordinal >= len(matches):
        raise RevisionError("changed or ambiguous exact paragraph context")
    return matches[ordinal]


def _comment_binding(paragraph: etree._Element, comment_id: object) -> None:
    if not isinstance(comment_id, str) or not comment_id.isdigit():
        raise RevisionError("operation requires native root comment ID")
    ids = paragraph.xpath("./w:commentRangeStart/@w:id", namespaces=NS)
    if comment_id not in ids:
        raise RevisionError(f"comment {comment_id} does not anchor selected paragraph")


def _image_identity(payload: bytes, expected_dimensions: object) -> str:
    try:
        with Image.open(BytesIO(payload)) as image:
            image.load()
            fmt, dimensions = image.format, image.size
    except Exception as exc:
        raise RevisionError("selected artwork is not a readable image") from exc
    if list(dimensions) != expected_dimensions:
        raise RevisionError("selected artwork dimensions changed")
    if fmt == "JPEG":
        return "jpg"
    if fmt == "PNG":
        return "png"
    raise RevisionError("only detected JPEG and PNG artwork is supported")


def _graphic_coverage(ledger: object, expected_ids: object, bounds: dict,
                      document: etree._Element, rels, parts) -> list[dict]:
    if (not isinstance(ledger, list) or not isinstance(expected_ids, list)
            or len(expected_ids) != len(set(expected_ids))):
        raise RevisionError("independent source graphic ID domain is required")
    by_id = {row.get("graphic_id"): row for row in ledger}
    if len(by_id) != len(ledger) or set(by_id) != set(expected_ids):
        raise RevisionError("source graphic ledger does not close its frozen ID domain")
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    consumed = set()
    report = []
    for gid in expected_ids:
        row = by_id[gid]
        sid = row.get("story_id")
        if not isinstance(gid, str) or not gid or sid not in bounds:
            raise RevisionError("invalid source graphic identity or story")
        page = row.get("source_page")
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            raise RevisionError(f"{gid}: physical source page required")
        if row.get("disposition") == "exclude":
            if row.get("reviewed") is not True or not row.get("reason"):
                raise RevisionError(f"{gid}: unreviewed source art exclusion")
            report.append({"graphic_id": gid, "source_page": page, "disposition": "exclude"})
            continue
        if row.get("disposition") != "must_include":
            raise RevisionError(f"{gid}: reference_only does not satisfy required art")
        span = bounds[sid]
        drawings = [d for para in paragraphs[span["word_start"]:span["word_end"]]
                    for d in para.xpath(".//w:drawing", namespaces=NS)]
        matches = []
        for index, drawing in enumerate(drawings):
            sha = _media_for_drawing(drawing, rels, parts)
            if sha == str(row.get("sha256", "")).upper():
                matches.append((index, drawing))
        ordinal = row.get("occurrence_ordinal")
        if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 0 or ordinal >= len(matches):
            raise RevisionError(f"{gid}: missing required Word artwork in story {sid}")
        index, drawing = matches[ordinal]
        if (sid, index) in consumed:
            raise RevisionError(f"{gid}: Word artwork occurrence consumed twice")
        consumed.add((sid, index))
        docpr = drawing.find(".//" + WP + "docPr")
        if docpr is None:
            raise RevisionError("Word drawing lacks docPr")
        declared_id = row.get("drawing_id")
        if declared_id is not None and str(declared_id) != docpr.get("id"):
            raise RevisionError(f"{gid}: retained drawing identity changed")
        if docpr.get("descr") and docpr.get("descr") not in (gid, row.get("legacy_descr")):
            raise RevisionError(f"{gid}: drawing identity belongs to another graphic")
        report.append({"graphic_id": gid, "source_page": page, "reader_story": sid,
                       "disposition": "must_include", "sha256": row["sha256"],
                       "drawing_id": docpr.get("id"), "occurrence_ordinal": ordinal})
    return report


def _validate_operations(operations: object) -> None:
    if not isinstance(operations, list):
        raise RevisionError("operations must be a list")
    ids = set()
    for op in operations:
        kind = op.get("kind")
        identity = op.get("issue_id") if kind in {"text", "keep"} else op.get("graphic_id")
        if not isinstance(identity, str) or not identity or identity in ids or kind not in {"text", "keep", "art"}:
            raise RevisionError("invalid or duplicate operation identity")
        ids.add(identity)
        if kind == "keep" and (op.get("disposition") != "keep" or not op.get("reason")):
            raise RevisionError("unchanged issue requires explicit keep reason")
        if kind == "text" and op.get("disposition") != "replace":
            raise RevisionError("text edit requires explicit replace disposition")


def _field_authority_paths(config: object) -> list[Path]:
    if config is None:
        return []
    if not isinstance(config, dict):
        raise RevisionError("source_bound_fields must be an object")
    paths = []
    for name in ("ledger", "choices", "conversion_spec"):
        row = config.get(name)
        if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not row["path"]:
            raise RevisionError(f"source-bound {name} authority path is required")
        paths.append(Path(row["path"]).resolve())
    if len(set(paths)) != len(paths):
        raise RevisionError("source-bound authorities alias one another")
    return paths


def _word_leaf(document: etree._Element, path: object,
               visibility: _StyleVisibility | None = None):
    if not isinstance(path, str) or not (match := FIELD_PATH.fullmatch(path)):
        raise RevisionError("unsupported or ambiguous Word text-node path")
    body_index, plain, row_index, cell_index, paragraph_index, run_index, text_index = match.groups()
    body = document.find(".//" + W + "body")
    if body is None:
        raise RevisionError("Word document has no body")
    children = list(body)
    index = int(body_index)
    if index >= len(children):
        raise RevisionError("Word body index outside original snapshot")
    owner = children[index]
    if plain:
        if owner.tag != W + "p":
            raise RevisionError("Word paragraph selector aliases another body object")
        paragraph = owner
    else:
        if owner.tag != W + "tbl":
            raise RevisionError("Word table selector aliases another body object")
        rows = owner.findall(W + "tr")
        if int(row_index) >= len(rows):
            raise RevisionError("Word table row selector is stale")
        cells = rows[int(row_index)].findall(W + "tc")
        if int(cell_index) >= len(cells):
            raise RevisionError("Word table cell selector is stale")
        paragraphs = cells[int(cell_index)].findall(W + "p")
        if int(paragraph_index) >= len(paragraphs):
            raise RevisionError("Word cell paragraph selector is stale")
        paragraph = paragraphs[int(paragraph_index)]
    runs = paragraph.findall(W + "r")
    if int(run_index) >= len(runs):
        raise RevisionError("Word run selector is stale")
    run = runs[int(run_index)]
    leaves = run.findall(W + "t")
    if int(text_index) >= len(leaves):
        raise RevisionError("Word text selector is stale")
    leaf = leaves[int(text_index)]
    # A plain line break before the selected text is structural, not a field or
    # another text value. Leave it in place while replacing only the w:t leaf.
    if any(child.tag not in {W + "rPr", W + "t", W + "br"}
           or (child.tag == W + "br" and child.attrib) for child in run):
        raise RevisionError("unsupported rich or field topology in target Word run")
    if any(node.tag in {W + "vanish", W + "webHidden"} for node in run.iter()):
        raise RevisionError("hidden target Word run is unsupported")
    if paragraph.xpath(".//w:fldChar | .//w:instrText | .//w:del | .//w:ins | .//w:sdt", namespaces=NS):
        raise RevisionError("Word field, revision or content-control topology is unsupported")
    if (visibility or _StyleVisibility(None)).hidden(paragraph, run):
        raise RevisionError("effective hidden Word target is unsupported")
    return leaf, paragraph, owner


def _node_xml_sha(node: etree._Element) -> str:
    return _sha(etree.tostring(node, encoding="UTF-8", with_tail=False))


def _predicted_node_xml_sha(node: etree._Element, after: str) -> str:
    """Hash edited leaf in its original namespace context, then restore it."""
    before = node.text
    try:
        node.text = after
        return _node_xml_sha(node)
    finally:
        node.text = before


def _field_entity_anchor(document: etree._Element, op: dict, selected_body_index: int) -> None:
    anchor = op.get("entity_anchor")
    if not isinstance(anchor, dict):
        raise RevisionError("source-bound operation requires entity anchor")
    index = anchor.get("body_index")
    self_context = anchor.get("self_context") is True
    if (not isinstance(index, int) or isinstance(index, bool) or index < 0
            or (self_context and (index != selected_body_index
                                  or op.get("kind") not in {"skill_label", "prose_label", "characteristic_prose", "user_label"}))
            or (not self_context and not index < selected_body_index <= index + 10)):
        raise RevisionError("entity anchor does not own selected Word field")
    body = document.find(".//" + W + "body")
    owner = list(body)[index]
    text_value = "".join(owner.xpath(".//w:t/text()", namespaces=NS))
    if (text_value != anchor.get("text") or _sha(text_value.encode("utf-8")) != anchor.get("text_sha256")
            or (not self_context and op.get("entity_id") not in text_value)):
        raise RevisionError("source-bound entity anchor text/hash differs")
    bookmarks = owner.xpath(".//w:bookmarkStart/@w:name", namespaces=NS)
    if bookmarks != anchor.get("bookmarks"):
        raise RevisionError("source-bound entity bookmark differs")


def _approved_field_rule(op: dict, choices: dict) -> None:
    kind, rule, field = op.get("kind"), op.get("rule_id"), op.get("field")
    before, after = op.get("before_text"), op.get("after_text")
    if (op.get("disposition") != "convert_deterministic" or not isinstance(before, str)
            or not before or not isinstance(after, str)
            or (not after and kind != "skill_consolidation") or before == after
            or op.get("reverse_before") != after or op.get("reverse_after") != before
            or _sha(before.encode("utf-8")) != op.get("before_sha256")):
        raise RevisionError("field operation is not exact and reversible")
    choice_id = op.get("editorial_decision")
    choice = next((row for row in choices.get("decisions", []) if row.get("id") == choice_id), None)
    if choice_id is not None and choice is None:
        raise RevisionError("field operation lacks its accepted user decision")
    if choice is not None and not str(choice.get("disposition", "")).startswith("approved_"):
        raise RevisionError("field operation references an unapproved user choice")
    if kind == "characteristic":
        if field not in CHARACTERISTICS and field != "ХАР":
            raise RevisionError("numeric field is outside characteristic allowlist")
        if op.get("current_scale") != "old_edition":
            raise RevisionError("numeric field scale is not proven old edition")
        old_values, new_values = re.findall(r"\d+", before), re.findall(r"\d+", after)
        if len(old_values) != 1 or len(new_values) != 1:
            raise RevisionError("numeric characteristic span must contain exactly one value")
        old, new = int(old_values[0]), int(new_values[0])
        before_skeleton = re.sub(r"\d+", "<value>", before, count=1)
        after_skeleton = re.sub(r"\d+", "<value>", after, count=1)
        if rule == "official_old_characteristic_times_five":
            if (field == "ХАР" or choice_id is not None or new != old * 5
                    or (field in {"EDU", "ОБР"} and old > 18)
                    or before_skeleton != after_skeleton):
                raise RevisionError("ordinary characteristic ×5 rule mismatch")
        elif rule == "official_EDU_19_to_27_plus":
            if (field not in {"EDU", "ОБР"} or old < 19
                    or op.get("entity_kind") == "creature" or new != min(old + 72, 99)
                    or before_skeleton != after_skeleton):
                raise RevisionError("high-EDU conversion table mismatch")
        elif rule == "user_approved_CHR_to_APP_times_five":
            if (field != "ХАР" or choice_id != "kremlin-chr-app-crosswalk"
                    or new != old * 5 or not before.startswith("ХАР:") or not after.startswith("НАР:")
                    or before_skeleton.replace("ХАР:", "НАР:", 1) != after_skeleton):
                raise RevisionError("user-approved CHR/APP crosswalk mismatch")
        else:
            raise RevisionError("unapproved numeric conversion rule")
    elif kind == "skill_label":
        if field == "contextual_stealth" and rule == "user_approved_contextual_stealth":
            if (choice_id != "len-stealth-context-values" or before != choice.get("old")
                    or after != choice.get("new")):
                raise RevisionError("contextual stealth decision mismatch")
        elif (not isinstance(field, str) or field != "skill:" + before
              or rule != "official_skill_mapping_392" or choice_id is not None
              or DIRECT_SKILL_MAP.get(before) != after
              or op.get("entity_collision_clear") is not True):
            raise RevisionError("skill label is outside approved direct mapping")
    elif kind == "prose_label":
        if (field not in PROSE_FIELDS or rule != "user_approved_exact_prose"
                or choice_id != "len-rybin-bodily-conceal" or choice is None
                or "Сокрытие" not in before or "Скрытность" not in after
                or re.findall(r"\d+", before) != re.findall(r"\d+", after)):
            raise RevisionError("unannotated prose lacks explicit authority")
    elif kind == "characteristic_prose":
        old_values, new_values = re.findall(r"\d+", before), re.findall(r"\d+", after)
        if (field != "СИЛ" or rule != "source_bound_door_str_times_five"
                or choice_id is not None or op.get("current_scale") != "old_edition"
                or len(old_values) != 1 or len(new_values) != 1
                or int(new_values[0]) != int(old_values[0]) * 5
                or int(old_values[0]) not in {10, 16}
                or before.replace(old_values[0], new_values[0], 1) != after
                or "СИЛ" not in before):
            raise RevisionError("door STR prose conversion is not source-bound")
    elif kind == "user_label":
        if rule != "user_approved_exact_label" or choice is None:
            raise RevisionError("user label requires exact accepted decision")
        if choice_id == "kremlin-potapov-architecture":
            if (op.get("entity_id") != choice.get("entity") or field != "architecture"
                    or before != "Архитектура" or after != "Искусство/ремесло (Архитектура)"):
                raise RevisionError("Architecture label decision differs")
        elif choice_id == "kremlin-language-parent-adaptation":
            if (op.get("entity_id") not in choice.get("entities", []) or field != "language"
                    or choice.get("field_map", {}).get(before) != after):
                raise RevisionError("language parent decision differs")
        else:
            raise RevisionError("unknown accepted user label decision")
    elif kind == "skill_consolidation":
        values = choice.get("source_values", {}).get(op.get("entity_id"), {}) if choice else {}
        action = op.get("action")
        if (rule != "user_approved_local_skill_consolidation"
                or choice_id != "len-pregen-persuade-consolidation"
                or choice is None or field != "Убеждение"
                or op.get("entity_id") not in choice.get("entities", [])
                or values.get("Торг") != 40 or values.get("Убеждение") not in {32, 40}):
            raise RevisionError("skill consolidation lacks accepted entity decision")
        if action == "clear_duplicate_label":
            valid = before == "Торг" and after == ""
        elif action == "clear_duplicate_value":
            valid = before == "40%" and after == ""
        elif action == "set_survivor_value":
            valid = (values["Убеждение"] == 32 and before == "32%" and after == "40%")
        else:
            valid = False
        if not valid:
            raise RevisionError("unsupported exact skill consolidation action")
    else:
        raise RevisionError("unsupported source-bound field kind")


def _field_label_binding(owner: etree._Element, op: dict, path: str) -> None:
    if op.get("kind") != "characteristic":
        return
    field = op["field"]
    before = op["before_text"].strip()
    if not before.isdigit():
        if not before.startswith(field + ":") and not before.startswith(field + " "):
            raise RevisionError("numeric span does not bind its declared characteristic label")
        return
    match = FIELD_PATH.fullmatch(path)
    row_number, cell_number = match.group(3), match.group(4)
    if owner.tag != W + "tbl" or row_number is None:
        raise RevisionError("bare characteristic number lacks a table-header binding")
    rows = owner.findall(W + "tr")
    label_found = False
    for row in rows[:int(row_number)]:
        cells = row.findall(W + "tc")
        if int(cell_number) < len(cells):
            value = "".join(cells[int(cell_number)].xpath(".//w:t/text()", namespaces=NS)).strip()
            label_found = label_found or value == field
    if not label_found:
        raise RevisionError("bare characteristic number does not match its table header")


def _numeric_operand_boundary(paragraph: etree._Element, leaf: etree._Element,
                              start: int, end: int,
                              visibility: _StyleVisibility | None) -> None:
    """Require a complete visible digit operand across supported Word inline runs."""
    zero_width = {W + name for name in (
        "pPr", "rPr", "bookmarkStart", "bookmarkEnd", "commentRangeStart",
        "commentRangeEnd", "commentReference", "proofErr")}
    units: list[str | None] = []
    selected: dict[int, int] = {}
    effective_visibility = visibility or _StyleVisibility(None)

    def consume_run(run: etree._Element) -> None:
        if effective_visibility.hidden(paragraph, run):
            return
        for child in run:
            if child.tag in zero_width:
                continue
            if child.tag == W + "t":
                for offset, character in enumerate(child.text or ""):
                    if child == leaf:
                        selected[offset] = len(units)
                    units.append(character)
            elif child.tag in {W + "tab", W + "br", W + "cr"}:
                units.append(" ")
            else:
                units.append(None)

    for child in paragraph:
        if child.tag in zero_width:
            continue
        if child.tag == W + "r":
            consume_run(child)
        elif child.tag == W + "hyperlink":
            for nested in child:
                if nested.tag == W + "r":
                    consume_run(nested)
                elif nested.tag not in zero_width:
                    units.append(None)
        else:
            units.append(None)
    if start not in selected or end - 1 not in selected:
        raise RevisionError("numeric characteristic is not bound to visible inline text")
    left, right = selected[start] - 1, selected[end - 1] + 1
    if ((left >= 0 and (units[left] is None or units[left].isdigit()))
            or (right < len(units) and (units[right] is None or units[right].isdigit()))):
        raise RevisionError("numeric characteristic span selects only part of a visible operand")


def _skill_consolidation_binding(owner: etree._Element, op: dict, path: str) -> None:
    if op.get("kind") != "skill_consolidation":
        return
    match = FIELD_PATH.fullmatch(path)
    row_number, cell_number = match.group(3), match.group(4)
    if owner.tag != W + "tbl" or row_number is None:
        raise RevisionError("skill consolidation must bind an exact table cell")
    row = owner.findall(W + "tr")[int(row_number)]
    cells = row.findall(W + "tc")
    index = int(cell_number)
    content = lambda cell: "".join(cell.xpath(".//w:t/text()", namespaces=NS))
    if op["action"] == "clear_duplicate_label":
        valid = index + 1 < len(cells) and content(cells[index]) == "Торг" and content(cells[index + 1]) == "40%"
    elif op["action"] == "clear_duplicate_value":
        valid = index > 0 and content(cells[index - 1]) == "Торг" and content(cells[index]) == "40%"
    else:
        valid = index > 0 and content(cells[index - 1]) == "Убеждение" and content(cells[index]) == "32%"
    if not valid:
        raise RevisionError("skill consolidation table pair or survivor differs")


def _consolidation_outcome(document: etree._Element, body_index: int) -> None:
    body = document.find(".//" + W + "body")
    rows = list(body)[body_index].findall(W + "tr")
    pairs = []
    for row in rows:
        cells = row.findall(W + "tc")
        values = ["".join(cell.xpath(".//w:t/text()", namespaces=NS)) for cell in cells]
        pairs.extend((value, values[index + 1]) for index, value in enumerate(values[:-1])
                     if value in {"Торг", "Убеждение"})
    if pairs != [("Убеждение", "40%")]:
        raise RevisionError("consolidation does not leave exactly one Persuasion 40 pair")


def _source_bound_plan(config: dict, snapshots: dict[Path, bytes], document: etree._Element,
                       inputs: dict, source_pdf: Path,
                       visibility: _StyleVisibility | None = None):
    paths = _field_authority_paths(config)
    for name, path in zip(("ledger", "choices", "conversion_spec"), paths):
        _identity(snapshots[path], config[name].get("sha256"), f"source-bound {name}")
    try:
        ledger = json.loads(snapshots[paths[0]].decode("utf-8-sig"))
        choices = json.loads(snapshots[paths[1]].decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RevisionError("invalid source-bound ledger or choices") from exc
    if (ledger.get("schema") != FIELD_LEDGER_SCHEMA or ledger.get("state") != FIELD_APPROVED_STATE
            or ledger.get("source_qa_closed") is not True or ledger.get("orchestrator_approved") is not True):
        raise RevisionError("source-bound operation ledger is not approved after source QA")
    if choices.get("schema") != "nri.user_conversion_choices.v1":
        raise RevisionError("unsupported source-bound choice authority")
    book = config.get("book_id")
    if not isinstance(book, str) or not book:
        raise RevisionError("source-bound book identity is required")
    book_input = ledger.get("inputs", {}).get(book)
    if (not isinstance(book_input, dict) or book_input.get("docx_sha256") != inputs.get("docx_sha256")
            or book_input.get("source_pdf_sha256") != inputs.get("source_pdf_sha256")
            or Path(book_input.get("source_pdf_path", "")).resolve() != source_pdf):
        raise RevisionError("source-bound ledger belongs to another book or input")
    all_ops = ledger.get("operations", [])
    all_groups = ledger.get("node_groups", [])
    if not isinstance(all_ops, list) or not isinstance(all_groups, list) or ledger.get("operation_count") != len(all_ops):
        raise RevisionError("source-bound ledger structure or count differs")
    ops = [op for op in all_ops if op.get("book_id") == book]
    declared_ids = config.get("operation_ids")
    if (not isinstance(declared_ids, list) or not declared_ids
            or len(declared_ids) != len(set(declared_ids))
            or declared_ids != [op.get("id") for op in ops]):
        raise RevisionError("source-bound operation ID domain does not close")
    groups = [row for row in all_groups if row.get("book_id") == book]
    if not groups or len({row.get("path") for row in groups}) != len(groups):
        raise RevisionError("source-bound node groups are missing or aliased")
    by_id = {op["id"]: op for op in ops}
    consolidations = [op for op in ops if op.get("kind") == "skill_consolidation"]
    if consolidations:
        decision = next((row for row in choices.get("decisions", [])
                         if row.get("id") == "len-pregen-persuade-consolidation"), None)
        if decision is None or {op.get("entity_id") for op in consolidations} != set(decision.get("entities", [])):
            raise RevisionError("approved Persuasion consolidation entities do not close")
        for entity in decision["entities"]:
            actions = [op.get("action") for op in consolidations if op.get("entity_id") == entity]
            expected = ["clear_duplicate_label", "clear_duplicate_value"]
            if decision["source_values"][entity]["Убеждение"] != 40:
                expected.append("set_survivor_value")
            if sorted(actions) != sorted(expected):
                raise RevisionError("approved Persuasion consolidation action set does not close")
    seen = set()
    plan = []
    for group in groups:
        ids = group.get("operation_ids")
        if (not isinstance(ids, list) or not ids or len(ids) > 8
                or len(ids) != len(set(ids)) or not set(ids) <= set(by_id)):
            raise RevisionError("source-bound node group has invalid operation IDs")
        if seen.intersection(ids):
            raise RevisionError("source-bound operation is consumed twice")
        seen.update(ids)
        path = group.get("path")
        leaf, paragraph, owner = _word_leaf(document, path, visibility)
        old = leaf.text or ""
        if (old != group.get("before_node") or _sha(old.encode("utf-8")) != group.get("before_node_sha256")
                or _node_xml_sha(leaf) != group.get("before_node_xml_sha256")
                or group.get("reverse_after_node") != old or group.get("reverse_before_node") != group.get("after_node")):
            raise RevisionError("source-bound Word node text/XML snapshot differs")
        spans = []
        for op_id in ids:
            op = by_id[op_id]
            selector = op.get("selector", {})
            selected_index = int(FIELD_PATH.fullmatch(path).group(1))
            if (selector.get("path") != path or selector.get("part") != "word/document.xml"
                    or selector.get("body_index") != selected_index
                    or selector.get("table_row") != (int(FIELD_PATH.fullmatch(path).group(3)) if FIELD_PATH.fullmatch(path).group(3) else None)
                    or selector.get("table_cell") != (int(FIELD_PATH.fullmatch(path).group(4)) if FIELD_PATH.fullmatch(path).group(4) else None)
                    or selector.get("text_node_before") != old
                    or selector.get("text_node_sha256") != group.get("before_node_sha256")
                    or op.get("node_group_ids") != ids
                    or op.get("input_docx_sha256") != inputs.get("docx_sha256")
                    or op.get("source_pdf_sha256") != inputs.get("source_pdf_sha256")
                    or op.get("source_verified") is not True
                    or Path(op.get("source_pdf_path", "")).resolve() != source_pdf
                    or not isinstance(op.get("source_physical_page"), int)
                    or op["source_physical_page"] < 1 or not op.get("source_edition_evidence")):
                raise RevisionError("source-bound operation selector/provenance differs")
            _field_entity_anchor(document, op, selected_index)
            _approved_field_rule(op, choices)
            _field_label_binding(owner, op, path)
            _skill_consolidation_binding(owner, op, path)
            start, end = selector.get("span_start"), selector.get("span_end")
            if (not isinstance(start, int) or not isinstance(end, int) or isinstance(start, bool)
                    or isinstance(end, bool) or not 0 <= start < end <= len(old)
                    or old[start:end] != op["before_text"]):
                raise RevisionError("source-bound exact span is stale")
            if op.get("kind") == "characteristic":
                operand = re.search(r"\d+", op["before_text"])
                if operand is None:
                    raise RevisionError("characteristic operand is missing")
                operand_start, operand_end = start + operand.start(), start + operand.end()
                _numeric_operand_boundary(paragraph, leaf, operand_start, operand_end, visibility)
            spans.append((start, end, op))
        spans.sort(key=lambda item: item[0])
        if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
            raise RevisionError("source-bound field spans overlap")
        after = old
        for start, end, op in reversed(spans):
            after = after[:start] + op["after_text"] + after[end:]
        if (after != group.get("after_node") or _sha(after.encode("utf-8")) != group.get("after_node_sha256")):
            raise RevisionError("source-bound grouped after-node hash differs")
        if _predicted_node_xml_sha(leaf, after) != group.get("after_node_xml_sha256"):
            raise RevisionError("source-bound grouped after-node XML hash differs")
        plan.append({"path": path, "leaf": leaf, "paragraph": paragraph,
                     "before": old, "after": after, "after_sha256": group["after_node_sha256"],
                     "after_xml_sha256": group["after_node_xml_sha256"], "operation_ids": ids,
                     "consolidation_body_index": (int(FIELD_PATH.fullmatch(path).group(1))
                                                  if any(by_id[op_id].get("kind") == "skill_consolidation" for op_id in ids)
                                                  else None)})
    if seen != set(declared_ids):
        raise RevisionError("source-bound node grouping does not close operation domain")
    expressions = [row for row in ledger.get("expression_groups", []) if row.get("book_id") == book]
    expression_ids = config.get("expression_ids", [])
    if (not isinstance(expression_ids, list) or len(expression_ids) != len(set(expression_ids))
            or expression_ids != [row.get("id") for row in expressions]):
        raise RevisionError("source-bound split-run expression domain does not close")
    used_paths = {item["path"] for item in plan}
    for expression in expressions:
        if (expression.get("rule_id") != "official_characteristic_effect_times_five"
                or expression.get("field") not in CHARACTERISTICS
                or expression.get("current_scale") != "old_edition"
                or expression.get("source_pdf_sha256") != inputs.get("source_pdf_sha256")
                or expression.get("source_verified") is not True
                or Path(expression.get("source_pdf_path", "")).resolve() != source_pdf
                or not isinstance(expression.get("source_physical_page"), int)
                or expression["source_physical_page"] < 1
                or not expression.get("source_edition_evidence")):
            raise RevisionError("unsupported or unbound split-run characteristic effect")
        nodes = expression.get("nodes")
        if not isinstance(nodes, list) or len(nodes) < 2 or len(nodes) > 4:
            raise RevisionError("split-run expression requires two to four exact text nodes")
        selected = []
        for row in nodes:
            path = row.get("path")
            if path in used_paths:
                raise RevisionError("split-run expression aliases another field node")
            used_paths.add(path)
            leaf, paragraph, _ = _word_leaf(document, path, visibility)
            before, after = leaf.text or "", row.get("after_node")
            start, end = row.get("span_start", 0), row.get("span_end", len(before))
            if (not isinstance(start, int) or not isinstance(end, int) or isinstance(start, bool)
                    or isinstance(end, bool) or not 0 <= start < end <= len(before)):
                raise RevisionError("split-run expression fragment span is invalid")
            before_fragment = before[start:end]
            after_fragment = row.get("after_fragment", after)
            if (not isinstance(after_fragment, str)
                    or before[:start] + after_fragment + before[end:] != after):
                raise RevisionError("split-run expression node changes outside its exact fragment")
            if (before != row.get("before_node") or _sha(before.encode("utf-8")) != row.get("before_node_sha256")
                    or _node_xml_sha(leaf) != row.get("before_node_xml_sha256")
                    or not isinstance(after, str) or _sha(after.encode("utf-8")) != row.get("after_node_sha256")):
                raise RevisionError("split-run expression Word node differs")
            if _predicted_node_xml_sha(leaf, after) != row.get("after_node_xml_sha256"):
                raise RevisionError("split-run expression after-node XML differs")
            selected.append((path, leaf, paragraph, before, after, row,
                             before_fragment, after_fragment))
        if len({id(item[2]) for item in selected}) != 1:
            raise RevisionError("split-run expression crosses paragraphs")
        paragraph = selected[0][2]
        selected_runs = [item[1].getparent() for item in selected]
        paragraph_children = list(paragraph)
        positions = [paragraph_children.index(run) for run in selected_runs]
        if (positions != list(range(positions[0], positions[0] + len(positions)))
                or any(run.tag != W + "r" or run.findall(W + "t") != [item[1]]
                       or any(child.tag not in {W + "rPr", W + "t"} for child in run)
                       for run, item in zip(selected_runs, selected))):
            raise RevisionError("split-run expression nodes are not contiguous in Word")
        for index, (_, _, _, before, _, row, _, _) in enumerate(selected):
            start, end = row.get("span_start", 0), row.get("span_end", len(before))
            if ((index > 0 and start != 0)
                    or (index < len(selected) - 1 and end != len(before))):
                raise RevisionError("split-run expression leaves visible text inside its bounds")
        before_projection = "".join(item[6] for item in selected)
        after_projection = "".join(item[7] for item in selected)
        if (before_projection != expression.get("before_expression")
                or after_projection != expression.get("after_expression")
                or expression.get("reverse_before_expression") != after_projection
                or expression.get("reverse_after_expression") != before_projection
                or not re.fullmatch(r"\d+D\d+\s+(?:СИЛ|ВЫН|ТЕЛ|ИНТ|МОЩ|ЛВК|НАР|ОБР)", before_projection)
                or after_projection != f"5 × ({before_projection.split(' ')[0]}) {before_projection.split(' ', 1)[1]}"):
            raise RevisionError("split-run characteristic projection is not exact and reversible")
        _field_entity_anchor(document, expression, int(FIELD_PATH.fullmatch(selected[0][0]).group(1)))
        for path, leaf, paragraph, before, after, row, _, _ in selected:
            plan.append({"path": path, "leaf": leaf, "paragraph": paragraph,
                         "before": before, "after": after,
                         "after_sha256": row["after_node_sha256"],
                         "after_xml_sha256": row["after_node_xml_sha256"],
                         "operation_ids": [expression["id"]]})
    return plan


def revise_docx(manifest_path: Path, reviewed_docx: Path, source_pdf: Path,
                output_root: Path, report_path: Path) -> dict:
    """Create one new DOCX and write a separate machine-readable QA report."""
    manifest_path, reviewed_docx, source_pdf = (p.resolve() for p in (manifest_path, reviewed_docx, source_pdf))
    output_root, report_path = output_root.resolve(), report_path.resolve()
    manifest_bytes = _source_bytes(manifest_path)
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RevisionError("invalid revision manifest") from exc
    if manifest.get("schema") != SCHEMA or manifest.get("provenance") != "reviewed_artifact_successor":
        raise RevisionError("unsupported DOCX-only manifest or provenance")
    inputs = manifest.get("inputs", {})
    if not isinstance(inputs, dict) or not isinstance(inputs.get("authorities", []), list):
        raise RevisionError("manifest inputs must be an object")
    operations = manifest.get("operations")
    _validate_operations(operations)
    field_config = manifest.get("source_bound_fields")
    field_paths = _field_authority_paths(field_config)
    if field_config is not None and any(op["kind"] == "art" for op in operations):
        raise RevisionError("source-bound Word field edits cannot share a build with art insertions")
    image_paths = [Path(op.get("source_image", "")) for op in operations
                   if op.get("kind") == "art"]
    authority_paths = [Path(row.get("path", "")) for row in inputs.get("authorities", [])]
    all_inputs = list(dict.fromkeys([manifest_path, reviewed_docx, source_pdf, *authority_paths, *field_paths, *image_paths]))
    _path_guard(all_inputs, output_root, report_path)
    snapshots = {manifest_path: manifest_bytes}
    for path in all_inputs:
        resolved = path.resolve()
        if resolved not in snapshots:
            snapshots[resolved] = _source_bytes(resolved)
    if _file_sha(manifest_path) != _sha(manifest_bytes):
        raise RevisionError("manifest changed after its captured parse snapshot")
    _identity(snapshots[reviewed_docx], inputs.get("docx_sha256"), "reviewed DOCX")
    _identity(snapshots[source_pdf], inputs.get("source_pdf_sha256"), "source PDF")
    for row in inputs.get("authorities", []):
        path = Path(row["path"]).resolve()
        _identity(snapshots[path], row.get("sha256"), str(path))
    parts = _zip_snapshot(snapshots[reviewed_docx])
    required = {"word/document.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}
    if required - parts.keys():
        raise RevisionError("reviewed DOCX lacks required OOXML members")
    original_parts = dict(parts)
    document = _xml(parts["word/document.xml"], "document.xml")
    rels = _xml(parts["word/_rels/document.xml.rels"], "document.xml.rels")
    types = _xml(parts["[Content_Types].xml"], "content types")
    styles = _xml(parts["word/styles.xml"], "styles.xml") if "word/styles.xml" in parts else None
    visibility = _StyleVisibility(styles)
    original_rels = [etree.tostring(row) for row in rels]
    original_types = [etree.tostring(row) for row in types]
    old_drawings = _drawing_order(document, _relationships(rels), parts)
    declared_drawings = inputs.get("original_drawing_occurrences")
    if not isinstance(declared_drawings, list) or declared_drawings != [
        {"sha256": sha, "drawing_id": identifier} for sha, identifier in old_drawings
    ]:
        raise RevisionError("ordered original drawing inventory differs")
    bounds = _word_bounds(manifest.get("stories"), document)
    original_paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    first_story = next(iter(bounds.values()))
    if any(p.xpath(".//w:drawing", namespaces=NS)
           for p in original_paragraphs[:first_story["word_start"]]):
        raise RevisionError("unowned artwork precedes the first declared story")
    expected_text = [_paragraph_text(p) for p in original_paragraphs]
    field_plan = (_source_bound_plan(field_config, snapshots, document, inputs, source_pdf, visibility)
                  if field_config is not None else [])
    original_bookmarks = Counter(document.xpath(".//w:bookmarkStart/@w:name", namespaces=NS))
    original_hyperlinks = Counter(document.xpath(".//w:hyperlink/@r:id | .//w:hyperlink/@w:anchor", namespaces=NS))
    marker_names = ("commentRangeStart", "commentRangeEnd", "commentReference")
    original_markers = {name: Counter(document.xpath(f".//w:{name}/@w:id", namespaces=NS)) for name in marker_names}
    graphic_rows = manifest.get("source_graphics")
    graphic_ids = manifest.get("source_graphic_ids")
    field_only_art = (field_config is not None
                      and manifest.get("art_scope") == "preserve_original_drawings_only"
                      and graphic_rows == [] and graphic_ids == [])
    if manifest.get("art_scope") == "preserve_original_drawings_only" and not field_only_art:
        raise RevisionError("field-only art scope requires source-bound fields and an empty art ledger")
    if (not isinstance(graphic_rows, list) or not isinstance(graphic_ids, list)
            or (not graphic_ids and not field_only_art)):
        raise RevisionError("source graphic ledger or explicit field-only art scope is required")
    new_graphic_ids = {op.get("graphic_id") for op in operations if op["kind"] == "art"}
    initial_coverage = _graphic_coverage(
        [row for row in graphic_rows if row.get("graphic_id") not in new_graphic_ids],
        [gid for gid in graphic_ids if gid not in new_graphic_ids],
        bounds, document, _relationships(rels), parts,
    )
    issue_bindings = {}
    for op in operations:
        if op["kind"] not in {"keep", "text"}:
            continue
        paragraph = _target_paragraph(document, bounds, op.get("story_id"), op.get("selector"),
                                      op.get("expected_text"), op.get("expected_text_sha256"))
        _comment_binding(paragraph, op.get("comment_id"))
        if op.get("word_bookmark") != bounds[op["story_id"]]["word_bookmark"]:
            raise RevisionError("issue story bookmark mismatch")
        issue_bindings[op["issue_id"]] = paragraph
    field_report = []
    for item in field_plan:
        item["leaf"].text = item["after"]
        if (_sha((item["leaf"].text or "").encode("utf-8")) != item["after_sha256"]
                or _node_xml_sha(item["leaf"]) != item["after_xml_sha256"]):
            raise RevisionError("source-bound field changed after preflight")
        paragraph = item["paragraph"]
        expected_text[original_paragraphs.index(paragraph)] = _paragraph_text(paragraph)
        field_report.append({"path": item["path"], "operation_ids": item["operation_ids"],
                             "before_node_sha256": _sha(item["before"].encode("utf-8")),
                             "after_node_sha256": item["after_sha256"],
                             "after_node_xml_sha256": item["after_xml_sha256"]})
    consolidation_indexes = {item["consolidation_body_index"] for item in field_plan
                             if item.get("consolidation_body_index") is not None}
    for body_index in consolidation_indexes:
        _consolidation_outcome(document, body_index)
    inserted_paragraphs = []
    operation_report = []
    for op in operations:
        bounds = _word_bounds(manifest["stories"], document)
        kind = op["kind"]
        if kind in {"keep", "text"}:
            paragraph = issue_bindings[op["issue_id"]]
            if kind == "keep":
                operation_report.append({"issue_id": op["issue_id"], "kind": "keep"})
                continue
            if _paragraph_text(paragraph) != op["expected_text"]:
                raise RevisionError("comment-bound replacement overlaps source-bound field edits")
            target, replacement = op.get("target_text"), op.get("replacement")
            if not all(isinstance(x, str) and x for x in (target, replacement)) or target == replacement:
                raise RevisionError("invalid exact text replacement")
            original_index = original_paragraphs.index(paragraph)
            _replace_word_text(paragraph, op["expected_text"], target, replacement, visibility)
            expected_text[original_index] = op["expected_text"].replace(target, replacement, 1)
            operation_report.append({"issue_id": op["issue_id"], "kind": "text",
                                     "before": op["expected_text"], "after": expected_text[original_index]})
            continue
        gid, sid = op.get("graphic_id"), op.get("story_id")
        row = next((r for r in graphic_rows if r.get("graphic_id") == gid), None)
        if (not row or row.get("disposition") != "must_include" or row.get("story_id") != sid
                or row.get("source_page") != op.get("source_page") or sid not in bounds
                or op.get("word_bookmark") != bounds[sid]["word_bookmark"]):
            raise RevisionError(f"{gid}: art operation does not bind required source graphic")
        position = op.get("position")
        if not isinstance(position, dict):
            raise RevisionError("artwork requires exact in-story position")
        paragraph = _target_paragraph(document, bounds, sid, position.get("selector"),
                                      position.get("expected_text"), position.get("expected_text_sha256"))
        source = Path(op.get("source_image", "")).resolve()
        payload = snapshots[source]
        _identity(payload, op.get("sha256"), gid)
        _identity(payload, row.get("sha256"), gid + " ledger")
        ext = _image_identity(payload, op.get("dimensions"))
        if op.get("insertion") != "after_exact_paragraph":
            raise RevisionError("artwork insertion must follow exact selected paragraph")
        internal = dict(op)
        internal["asset_path"] = f"assets/revision-{gid}.{ext}"
        image_info, image_paragraph = _add_word_image(document, rels, types, parts, paragraph,
                                                      internal, payload, tuple(op["dimensions"]))
        inserted_paragraphs.append(image_paragraph)
        operation_report.append({"graphic_id": gid, "kind": "art", "source_page": row["source_page"],
                                 "reader_story": sid, "position_text_sha256": position["expected_text_sha256"],
                                 "selected_sha256": _sha(payload), "detected_content_type": "image/png" if ext == "png" else "image/jpeg",
                                 **image_info})
    parts["word/document.xml"] = _serial(document)
    parts["word/_rels/document.xml.rels"] = _serial(rels)
    parts["[Content_Types].xml"] = _serial(types)
    bounds = _word_bounds(manifest["stories"], document)
    coverage = _graphic_coverage(graphic_rows, graphic_ids, bounds, document, _relationships(rels), parts)
    if len(coverage) != len(graphic_ids) or len(initial_coverage) + len([x for x in operation_report if x["kind"] == "art"]) != len(coverage):
        raise RevisionError("source graphic obligation count did not close")
    survivors = [p for p in document.xpath(".//w:body//w:p", namespaces=NS) if p not in inserted_paragraphs]
    if survivors != original_paragraphs or [_paragraph_text(p) for p in survivors] != expected_text:
        raise RevisionError("ordered paragraph conservation failed")
    new_drawing_ids = {str(op["drawing_id"]) for op in operation_report if op["kind"] == "art"}
    if [row for row in _drawing_order(document, _relationships(rels), parts) if row[1] not in new_drawing_ids] != old_drawings:
        raise RevisionError("ordered original drawing conservation failed")
    if Counter(document.xpath(".//w:bookmarkStart/@w:name", namespaces=NS)) != original_bookmarks:
        raise RevisionError("bookmark conservation failed")
    if Counter(document.xpath(".//w:hyperlink/@r:id | .//w:hyperlink/@w:anchor", namespaces=NS)) != original_hyperlinks:
        raise RevisionError("hyperlink conservation failed")
    for name in marker_names:
        if Counter(document.xpath(f".//w:{name}/@w:id", namespaces=NS)) != original_markers[name]:
            raise RevisionError("native review marker conservation failed")
    if ([etree.tostring(row) for row in list(rels)[:len(original_rels)]] != original_rels
            or [etree.tostring(row) for row in list(types)[:len(original_types)]] != original_types):
        raise RevisionError("existing OOXML relationship or content type changed")
    for name, payload in original_parts.items():
        if name not in {"word/document.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"} and parts.get(name) != payload:
            raise RevisionError(f"undeclared original package part change: {name}")
    for path, snapshot in snapshots.items():
        if _file_sha(path) != _sha(snapshot):
            raise RevisionError(f"authority input changed during build: {path}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".reviewed-docx-", dir=output_root.parent))
    try:
        out = staged / "document.docx"
        with zipfile.ZipFile(out, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, payload in parts.items():
                archive.writestr(name, payload)
        checked = _zip_snapshot(out.read_bytes())
        if checked != parts:
            raise RevisionError("written DOCX package differs from validated parts")
        checked_document = _xml(checked["word/document.xml"], "written document")
        for item in field_plan:
            leaf, _, _ = _word_leaf(checked_document, item["path"], visibility)
            # An empty w:t round-trips from text="" to text=None in lxml. Compare
            # its written XML with the same round-trip of the validated leaf.
            expected_written_leaf = etree.fromstring(
                etree.tostring(item["leaf"], encoding="UTF-8", with_tail=False))
            if ((leaf.text or "") != item["after"]
                    or _node_xml_sha(leaf) != _node_xml_sha(expected_written_leaf)):
                raise RevisionError(f"post-write source-bound field node changed: {item['path']}")
        for body_index in consolidation_indexes:
            _consolidation_outcome(checked_document, body_index)
        checked_rels = _relationships(_xml(checked["word/_rels/document.xml.rels"], "written relationships"))
        checked_bounds = _word_bounds(manifest["stories"], checked_document)
        if _graphic_coverage(graphic_rows, graphic_ids, checked_bounds, checked_document, checked_rels, checked) != coverage:
            raise RevisionError("post-write source graphic coverage changed")
        if [row for row in _drawing_order(checked_document, checked_rels, checked) if row[1] not in new_drawing_ids] != old_drawings:
            raise RevisionError("post-write original drawing order changed")
        for path, snapshot in snapshots.items():
            if _file_sha(path) != _sha(snapshot):
                raise RevisionError(f"authority input changed before publish: {path}")
        report = {"schema": "kb_creator.reviewed_docx_revision_report.v1",
                  "status": "validated_candidate", "accepted": False,
                  "provenance": "reviewed_artifact_successor",
                  "inputs": {"manifest_sha256": _sha(manifest_bytes), "docx_sha256": _sha(snapshots[reviewed_docx]),
                             "source_pdf_sha256": _sha(snapshots[source_pdf]),
                             "authorities": {str(path): _sha(snapshots[path]) for path in authority_paths}},
                  "output": {"docx_sha256": _file_sha(out), "path": (output_root / "document.docx").as_posix()},
                  "preservation": {"old_drawing_occurrences": len(old_drawings),
                                   "old_media_parts": sum(name.startswith("word/media/") for name in original_parts),
                                   "old_comment_thread_parts": [name for name in original_parts if "comment" in name.lower() or "person" in name.lower()],
                                   "bookmarks": sum(original_bookmarks.values()),
                                   "hyperlinks": sum(original_hyperlinks.values())},
                  "operations": operation_report, "source_bound_field_nodes": field_report,
                  "source_graphic_coverage": coverage,
                  "limitations": ["Reviewed-artifact successor; lost upstream master lineage cannot be reconstructed.",
                                  "Rendered page QA and independent release review remain pending."]}
        if field_only_art:
            report["limitations"].append(
                "Field-only pass conserves all original artwork; source-art completeness was not assessed.")
        if output_root.exists() or report_path.exists():
            raise RevisionError("output or report appeared during build")
        staged.rename(output_root)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        return report
    finally:
        if staged.exists():
            shutil.rmtree(staged)
