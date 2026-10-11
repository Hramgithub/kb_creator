"""Closed source-to-reader plan checks for prospective DOCX-only packages.

This module deliberately does not turn a validated plan into production
readiness.  Generation also needs an actual DOCX occurrence verifier and an
independent reopened-package check; callers must not use this as a bypass.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from .edition_projection import EditionProjectionError, validate_edition_rows, validate_terminology_rows
from .identity import assert_existing_path_components_are_not_reparse, file_identity
from .manifests import sealed, validate_seal
from .source_graphics import SourceGraphicsError, validate_inventory, validate_produced_inventory, validate_review


PLAN_SCHEMA = "kb_creator.reader_fidelity_plan.v2"
VERIFICATION_SCHEMA = "kb_creator.reader_fidelity_verification.v1"


class ReaderFidelityError(ValueError):
    pass


def _closed(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ReaderFidelityError(f"{label} has unknown or missing fields")
    return value


def _exact_file(row: Any, *, label: str) -> Path:
    record = _closed(row, {"path", "bytes", "sha256"}, label)
    path = Path(str(record["path"]))
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ReaderFidelityError(f"{label} must be an existing absolute regular file")
    assert_existing_path_components_are_not_reparse(path)
    if file_identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
        raise ReaderFidelityError(f"{label} identity mismatch")
    return path


def _validate_text_batches(plan: dict[str, Any]) -> None:
    """Reconstruct each final node once from the original, nonoverlapping spans."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in [*plan["edition_rows"], *plan["terminology_rows"]]:
        groups.setdefault(row["selector"]["html_anchor"], []).append(row["selector"])
    for selectors in groups.values():
        original = selectors[0]["before_text"]
        approved = selectors[0]["after_text"]
        if any(s["before_text"] != original or s["after_text"] != approved for s in selectors):
            raise ReaderFidelityError("same-node operations disagree on original/final snapshot")
        spans = sorted((s["before_start"], s["before_end"],
                        s["after_text"][s["after_start"]:s["after_end"]]) for s in selectors)
        if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
            raise ReaderFidelityError("same-node operations overlap")
        after_spans = sorted((s["after_start"], s["after_end"]) for s in selectors)
        if any(left[1] > right[0] for left, right in zip(after_spans, after_spans[1:])):
            raise ReaderFidelityError("same-node final operations overlap")
        rendered = original
        for start, end, replacement in reversed(spans):
            rendered = rendered[:start] + replacement + rendered[end:]
        if rendered != approved:
            raise ReaderFidelityError("approved final text changes unreviewed exterior content")


def validate_plan(plan_path: Path, *, source_pdf: Path | None = None,
                  master_ru: Path | None = None) -> dict[str, Any]:
    """Reopen source/review/masters and require one decision per graphic."""
    assert_existing_path_components_are_not_reparse(plan_path)
    if not plan_path.is_file() or plan_path.is_symlink():
        raise ReaderFidelityError("reader plan is not a regular file")
    try:
        value = json.loads(plan_path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise ReaderFidelityError("reader plan must be an object")
        validate_seal(value, "plan_sha256")
    except (OSError, ValueError, TypeError) as error:
        raise ReaderFidelityError(f"invalid reader plan: {error}") from error
    _closed(value, {"schema", "inventory", "review", "source_pdf", "master_ru", "projection",
                    "config", "glossary_registry", "glossary_overlay", "policy",
                    "placements", "edition_domain", "edition_rows", "terminology_rows", "section_domain",
                    "section_reviews", "state", "plan_sha256"}, "reader plan")
    if value["schema"] != PLAN_SCHEMA or value["state"] != "closed":
        raise ReaderFidelityError("reader plan version or review state is not closed")
    inventory_path = _exact_file(value["inventory"], label="source inventory")
    review_path = _exact_file(value["review"], label="source review")
    review = validate_review(review_path, inventory_path, source_pdf=source_pdf)
    inventory = validate_inventory(inventory_path, source_pdf=source_pdf)
    if value["source_pdf"] != review["source_pdf"]:
        raise ReaderFidelityError("reader plan source PDF differs from reviewed domain")
    master_path = _exact_file(value["master_ru"], label="MASTER_RU")
    if master_ru is not None and master_path.resolve() != master_ru.resolve(strict=True):
        raise ReaderFidelityError("reader plan MASTER_RU authority mismatch")
    authority_paths = {field: _exact_file(value[field], label=field)
                       for field in ("projection", "config", "glossary_registry", "glossary_overlay")}
    policy = _closed(value["policy"], {"target_edition", "edition_applicability", "rules_version",
                                        "reader_profile", "review_reference", "book_id"}, "reader policy")
    if (policy["target_edition"] != "7e" or policy["edition_applicability"] not in
            {"applicable", "nonapplicable_reviewed"} or any(not isinstance(policy[key], str)
            or not policy[key].strip() for key in ("rules_version", "reader_profile", "review_reference", "book_id"))):
        raise ReaderFidelityError("target edition/profile has no reviewed authority")
    sections = value["section_domain"]
    if not isinstance(sections, list) or not sections or any(not isinstance(s, str) or not s for s in sections) or len(set(sections)) != len(sections):
        raise ReaderFidelityError("source-bound section domain is missing or duplicate")
    reviews = value["section_reviews"]
    if not isinstance(reviews, list) or len(reviews) != len(sections):
        raise ReaderFidelityError("every source section needs mechanics/label domain review")
    reviewed: set[str] = set()
    for row in reviews:
        _closed(row, {"section_id", "cards", "prose", "pregens", "checks", "labels",
                      "reviewed", "decision_reference", "residual_issues"}, "section review")
        sid = row["section_id"]
        if (sid in reviewed or sid not in sections or row["reviewed"] is not True
                or row["residual_issues"] or not isinstance(row["decision_reference"], str)
                or not row["decision_reference"].strip()
                or any(type(row[key]) is not int or row[key] < 0
                       for key in ("cards", "prose", "pregens", "checks", "labels"))):
            raise ReaderFidelityError("section mechanics/label review is incomplete")
        reviewed.add(sid)
    if reviewed != set(sections):
        raise ReaderFidelityError("section mechanics/label domain is incomplete")
    if policy["edition_applicability"] == "nonapplicable_reviewed" and (value["edition_rows"] or value["edition_domain"]):
        raise ReaderFidelityError("nonapplicable edition profile has conversion rows")
    try:
        validate_edition_rows(value["edition_rows"], source_pdf_sha256=value["source_pdf"]["sha256"],
                              source_pages=inventory["pages"], section_domain=sections,
                              book_id=policy["book_id"], reviewed_domain=value["edition_domain"])
        validate_terminology_rows(value["terminology_rows"],
                                  registry_path=authority_paths["glossary_registry"],
                                  overlay_path=authority_paths["glossary_overlay"],
                                  book_id=policy["book_id"],
                                  registry_sha256=value["glossary_registry"]["sha256"],
                                  overlay_sha256=value["glossary_overlay"]["sha256"])
    except EditionProjectionError as error:
        raise ReaderFidelityError(f"edition/terminology decision is open: {error}") from error
    _validate_text_batches(value)
    graphics = {row["graphic_id"]: row for row in review["graphics"]}
    included = {gid for gid, row in graphics.items() if row["disposition"] != "exclude"}
    placements = value["placements"]
    if not isinstance(placements, list):
        raise ReaderFidelityError("graphic placements must be a list")
    seen_ids: set[str] = set()
    seen_graphics: set[str] = set()
    anchors: set[tuple[str, str, int]] = set()
    for row in placements:
        _closed(row, {"placement_id", "graphic_id", "story_id", "anchor", "position",
                      "repeat_ordinal", "selected_sha256", "representation", "master_relation",
                      "route", "crop", "fit", "decision_reference"}, "graphic placement")
        pid, gid = row["placement_id"], row["graphic_id"]
        if (not isinstance(pid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", pid)
                or pid in seen_ids or gid not in included
                or gid in seen_graphics or row["story_id"] != graphics[gid]["owner"]
                or row["selected_sha256"] != graphics[gid]["selected"]["sha256"]
                or not isinstance(row["anchor"], str) or not row["anchor"]
                or row["position"] not in {"before", "after"}
                or type(row["repeat_ordinal"]) is not int or row["repeat_ordinal"] < 0
                or row["representation"] != "word_drawing"
                or row["master_relation"] not in {"in_master", "reference_only", "absent_from_master"}
                or row["route"] not in {"retain_exact", "reviewed_reader_insertion", "reviewed_equivalent"}
                or not isinstance(row["decision_reference"], str) or not row["decision_reference"].strip()):
            raise ReaderFidelityError("graphic placement is duplicate, stale or unresolved")
        if row["master_relation"] != "in_master" and row["route"] == "retain_exact":
            raise ReaderFidelityError("reference-only/absent graphic needs explicit reader insertion")
        _closed(row["crop"], {"left", "top", "right", "bottom", "approved"}, "crop")
        if any(type(row["crop"][key]) not in {int, float} or not 0 <= row["crop"][key] < 1
               for key in ("left", "top", "right", "bottom")) or row["crop"]["approved"] is not True:
            raise ReaderFidelityError("crop lacks bounded reviewed approval")
        _closed(row["fit"], {"width_emu", "height_emu"}, "fit")
        if any(type(row["fit"][key]) is not int or row["fit"][key] <= 0
               for key in ("width_emu", "height_emu")):
            raise ReaderFidelityError("placement has zero or unsupported extent")
        anchor = (row["story_id"], row["anchor"], row["repeat_ordinal"])
        if anchor in anchors:
            raise ReaderFidelityError("two placements claim the same reader anchor")
        anchors.add(anchor)
        seen_ids.add(pid)
        seen_graphics.add(gid)
    if seen_graphics != included:
        raise ReaderFidelityError("reader placements do not cover every reviewed inclusion")
    return value


def project_graphics(plan_path: Path, projection_root: Any, stage: Path) -> dict[str, Any]:
    """Apply only reviewed graphic placements to an in-memory reader tree.

    Masters remain unchanged. Newly selected binaries are copied into the
    isolated DOCX package stage and every supported image gets a stable Word ID.
    """
    from lxml import html as lxml_html
    from .source_graphics import _bound_file

    plan = validate_plan(plan_path)
    review_path = Path(plan["review"]["path"])
    review = validate_review(review_path, Path(plan["inventory"]["path"]))
    graphics = {row["graphic_id"]: row for row in review["graphics"]}
    nodes = list(projection_root.iter())
    bounds: dict[str, tuple[int, int]] = {}
    previous = -1
    for sid in plan["section_domain"]:
        matches = projection_root.xpath("//*[@id=$anchor]", anchor=sid)
        if len(matches) != 1:
            raise ReaderFidelityError(f"reader story anchor is missing or ambiguous: {sid}")
        index = nodes.index(matches[0])
        if index <= previous:
            raise ReaderFidelityError("reader story anchors changed order")
        bounds[sid] = (index, len(nodes))
        if previous >= 0:
            prior = plan["section_domain"][len(bounds) - 2]
            bounds[prior] = (bounds[prior][0], index)
        previous = index
    used_images: set[int] = set()
    added = 0
    for row in plan["placements"]:
        sid = row["story_id"]
        if sid not in bounds:
            raise ReaderFidelityError("placement story is outside reviewed section domain")
        anchors = projection_root.xpath("//*[@id=$anchor]", anchor=row["anchor"])
        if len(anchors) != 1 or not bounds[sid][0] <= nodes.index(anchors[0]) < bounds[sid][1]:
            raise ReaderFidelityError("placement anchor is missing or belongs to wrong story")
        selected = _bound_file(review_path.parent, graphics[row["graphic_id"]]["selected"], "selected graphic")
        if row["master_relation"] == "in_master":
            candidates = []
            for image in projection_root.xpath("//img[@src]"):
                if image not in nodes:
                    continue
                if not bounds[sid][0] <= nodes.index(image) < bounds[sid][1]:
                    continue
                src = image.get("src", "")
                path = (stage / src).resolve()
                if (not path.is_relative_to(stage.resolve()) or not path.is_file()
                        or file_identity(path)["sha256"] != row["selected_sha256"]):
                    continue
                candidates.append(image)
            if row["repeat_ordinal"] >= len(candidates):
                raise ReaderFidelityError("reviewed in-master image occurrence is absent")
            image = candidates[row["repeat_ordinal"]]
            if nodes.index(image) in used_images or image.get("data-fidelity-placement-id"):
                raise ReaderFidelityError("reader image occurrence reused by placements")
            used_images.add(nodes.index(image))
        else:
            suffix = selected.suffix.lower()
            if suffix not in {".png", ".jpg", ".jpeg"}:
                raise ReaderFidelityError("selected graphic needs reviewed PNG/JPEG Word representation")
            relative = f"assets/fidelity-{row['placement_id']}{suffix}"
            target = stage / relative
            if target.exists():
                raise ReaderFidelityError("graphic insertion path collision")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(selected, target)
            if file_identity(target)["sha256"] != row["selected_sha256"]:
                raise ReaderFidelityError("selected graphic changed during projection")
            block = anchors[0]
            while block.tag not in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "figure", "div", "section"}:
                if block.getparent() is None:
                    raise ReaderFidelityError("reader anchor has no block placement")
                block = block.getparent()
            figure = lxml_html.Element("figure")
            image = lxml_html.Element("img")
            image.set("src", relative)
            image.set("alt", row["graphic_id"])
            figure.append(image)
            if row["position"] == "before":
                block.addprevious(figure)
            else:
                block.addnext(figure)
            added += 1
        image.set("data-fidelity-placement-id", row["placement_id"])
        image.set("data-fidelity-width-emu", str(row["fit"]["width_emu"]))
        image.set("data-fidelity-height-emu", str(row["fit"]["height_emu"]))
        for edge in ("left", "top", "right", "bottom"):
            image.set(f"data-fidelity-crop-{edge}", str(row["crop"][edge]))
    return {"placements": len(plan["placements"]), "insertions": added}


def project_text_operations(plan_path: Path, projection_root: Any) -> int:
    """Batch nonoverlapping, exact-span reader-only changes from one snapshot.

    An operation spanning multiple styled text nodes is held for an explicit
    selector instead of flattening Word/HTML formatting.
    """
    plan = validate_plan(plan_path)
    nodes = list(projection_root.iter())
    section_starts: dict[str, int] = {}
    if plan["edition_rows"]:
        for section in plan["section_domain"]:
            matches = projection_root.xpath("//*[@id=$anchor]", anchor=section)
            if len(matches) != 1:
                raise ReaderFidelityError("reader edition section anchor is missing or ambiguous")
            section_starts[section] = nodes.index(matches[0])
        if list(section_starts.values()) != sorted(set(section_starts.values())):
            raise ReaderFidelityError("reader edition section anchors changed order")
        for row in plan["edition_rows"]:
            section = row["story_id"]
            element = projection_root.xpath("//*[@id=$anchor]", anchor=row["selector"]["html_anchor"])
            lower = section_starts[section]
            later = [position for position in section_starts.values() if position > lower]
            upper = min(later) if later else len(nodes)
            if len(element) != 1 or not lower <= nodes.index(element[0]) < upper:
                raise ReaderFidelityError("reader edition selector is outside reviewed story")
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in [*plan["edition_rows"], *plan["terminology_rows"]]:
        groups.setdefault(row["selector"]["html_anchor"], []).append(row["selector"])
    for anchor, selectors in groups.items():
        matches = projection_root.xpath("//*[@id=$anchor]", anchor=anchor)
        if len(matches) != 1:
            raise ReaderFidelityError("reader text operation anchor is missing or ambiguous")
        element = matches[0]
        if any(node.tag in {"script", "style", "del", "ins"}
               or node.get("hidden") is not None or node.get("aria-hidden") == "true"
               or re.search(r"(?:display\s*:\s*none|visibility\s*:\s*hidden)", node.get("style", ""), re.I)
               for node in element.iter()):
            raise ReaderFidelityError("reader text operation contains hidden or unsupported inline content")
        before = selectors[0]["before_text"]
        after = selectors[0]["after_text"]
        if (element.text_content() != before or any(row["before_text"] != before or row["after_text"] != after
                                                    for row in selectors)):
            raise ReaderFidelityError("reader text operation snapshot differs from approved source")
        spans = sorted((row["before_start"], row["before_end"],
                        row["after_text"][row["after_start"]:row["after_end"]])
                       for row in selectors)
        if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
            raise ReaderFidelityError("reader text operations overlap on one source node")
        text_nodes = list(element.xpath(".//text()"))
        mapping = []
        cursor = 0
        for node in text_nodes:
            mapping.append((cursor, cursor + len(node), node))
            cursor += len(node)
        if cursor != len(before):
            raise ReaderFidelityError("reader text operation topology is ambiguous")
        changes: dict[int, list[tuple[int, int, str]]] = {}
        for start, end, replacement in spans:
            targets = [(index, left, node) for index, (left, right, node) in enumerate(mapping)
                       if left <= start and end <= right]
            if len(targets) != 1:
                raise ReaderFidelityError("reader text operation crosses styled runs")
            index, left, node = targets[0]
            changes.setdefault(index, []).append((start - left, end - left, replacement))
        for index, edits in changes.items():
            node = mapping[index][2]
            original = str(node)
            changed = original
            for start, end, replacement in sorted(edits, reverse=True):
                changed = changed[:start] + replacement + changed[end:]
            parent = node.getparent()
            if node.is_text:
                parent.text = changed
            elif node.is_tail:
                parent.tail = changed
            else:
                raise ReaderFidelityError("unsupported reader text node")
        if element.text_content() != after:
            raise ReaderFidelityError("reader text operation did not produce approved text")
    return sum(map(len, groups.values()))


def verify_word_text(plan_path: Path, docx_path: Path) -> list[dict[str, Any]]:
    """Reopen exact output paragraphs and compare every approved final value."""
    from kb_creator.pipeline.reviewed_reader_revision import NS, _xml, _zip_parts

    plan = validate_plan(plan_path)
    try:
        document = _xml(_zip_parts(docx_path)["word/document.xml"], "Word document")
    except (KeyError, ValueError) as error:
        raise ReaderFidelityError(f"actual Word text package is invalid: {error}") from error
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    tables = document.xpath(".//w:body//w:tbl", namespaces=NS)
    section_starts: dict[str, int] = {}
    if plan["edition_rows"]:
        from kb_creator.scripts.production_docx import bookmark_name
        for section in plan["section_domain"]:
            name = bookmark_name(section)
            matches = [index for index, paragraph in enumerate(paragraphs)
                       if paragraph.xpath(".//w:bookmarkStart[@w:name=$name]", namespaces=NS, name=name)]
            if len(matches) != 1:
                raise ReaderFidelityError("actual Word edition section anchor is missing or ambiguous")
            section_starts[section] = matches[0]
        if list(section_starts.values()) != sorted(set(section_starts.values())):
            raise ReaderFidelityError("actual Word edition section anchors changed order")
    observations = []
    for kind, rows in (("edition", plan["edition_rows"]), ("terminology", plan["terminology_rows"])):
        for row in rows:
            selector = row["selector"]
            index = selector["paragraph"]
            if index >= len(paragraphs):
                raise ReaderFidelityError("approved Word text paragraph is missing")
            paragraph = paragraphs[index]
            if kind == "edition":
                lower = section_starts[row["story_id"]]
                later = [position for position in section_starts.values() if position > lower]
                upper = min(later) if later else len(paragraphs)
                if not lower <= index < upper:
                    raise ReaderFidelityError("actual Word edition operand left reviewed story")
            parents = paragraph.xpath("ancestor::w:tbl", namespaces=NS)
            if parents:
                if len(parents) != 1 or selector["table"] >= len(tables) or tables[selector["table"]] is not parents[0]:
                    raise ReaderFidelityError("Word text table topology changed")
                cells = parents[0].xpath(".//w:tr/w:tc", namespaces=NS)
                cell = paragraph.xpath("ancestor::w:tc[1]", namespaces=NS)
                if len(cell) != 1 or selector["cell"] >= len(cells) or cells[selector["cell"]] is not cell[0]:
                    raise ReaderFidelityError("Word text cell topology changed")
            elif selector["table"] != 0 or selector["cell"] != 0:
                raise ReaderFidelityError("Word text unexpectedly left its table/cell")
            if paragraph.xpath(".//w:vanish|.//w:webHidden", namespaces=NS):
                raise ReaderFidelityError("approved Word text became hidden")
            if paragraph.xpath(".//w:fldChar|.//w:instrText|.//w:delText|.//w:sdt|.//w:object|.//w:pict",
                               namespaces=NS):
                raise ReaderFidelityError("approved Word text has unsupported inline field or object")
            actual = "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))
            if actual != selector["after_text"]:
                raise ReaderFidelityError("actual Word value/label differs from approved final text")
            start, end = selector["after_start"], selector["after_end"]
            cursor = 0
            contained = False
            for text_node in paragraph.xpath(".//w:t", namespaces=NS):
                next_cursor = cursor + len(text_node.text or "")
                if cursor <= start and end <= next_cursor:
                    contained = True
                cursor = next_cursor
            if not contained:
                raise ReaderFidelityError("approved Word text operand crosses run boundaries")
            observations.append({"kind": kind, "occurrence_id": row["occurrence_id"],
                                 "paragraph": index, "after_sha256": selector["after_sha256"]})
    return observations


def verify_word_graphics(plan_path: Path, docx_path: Path) -> list[dict[str, Any]]:
    """Observe referenced Word drawings, not media parts or builder counters.

    This is a graphic-only structural check. It does not attest edited prose,
    rendered visibility, or the full verification contract.
    """
    plan = validate_plan(plan_path)
    if not docx_path.is_file() or docx_path.is_symlink():
        raise ReaderFidelityError("actual Word document is missing")
    from kb_creator.pipeline.reviewed_reader_revision import (
        A, NS, WP, W, _media_for_drawing, _relationships, _xml, _zip_parts,
    )
    from kb_creator.scripts.production_docx import bookmark_name

    try:
        parts = _zip_parts(docx_path)
        document = _xml(parts["word/document.xml"], "Word document")
        rels = _relationships(_xml(parts["word/_rels/document.xml.rels"], "Word relationships"))
    except (KeyError, ValueError) as error:
        raise ReaderFidelityError(f"actual Word package is invalid: {error}") from error
    if document.xpath(".//w:pict | .//w:object", namespaces=NS):
        raise ReaderFidelityError("actual Word has unsupported VML/OLE graphic outside reviewed drawings")
    for name, payload in parts.items():
        if not re.fullmatch(r"word/(?:header|footer|footnotes|endnotes|comments)[^/]*\.xml", name):
            continue
        story = _xml(payload, name)
        if story.xpath(".//w:drawing | .//w:pict | .//w:object", namespaces=NS):
            raise ReaderFidelityError("actual Word has unreviewed non-body graphic story")
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    def bookmark_location(anchor: str) -> tuple[int, Any, Any]:
        name = bookmark_name(anchor)
        matches = [(index, paragraph, node) for index, paragraph in enumerate(paragraphs)
                   for node in paragraph.xpath(".//w:bookmarkStart[@w:name=$name]", namespaces=NS, name=name)]
        if len(matches) != 1:
            raise ReaderFidelityError(f"Word anchor is missing or ambiguous: {anchor}")
        index, paragraph, start_node = matches[0]
        marker_id = start_node.get(W + "id")
        endings = document.xpath(".//w:bookmarkEnd[@w:id=$marker]", namespaces=NS, marker=marker_id)
        local_endings = paragraph.xpath(".//w:bookmarkEnd[@w:id=$marker]", namespaces=NS,
                                        marker=marker_id)
        if (not marker_id or len(endings) != 1 or len(local_endings) != 1
                or list(paragraph.iter()).index(start_node) >= list(paragraph.iter()).index(local_endings[0])):
            raise ReaderFidelityError(f"Word anchor lacks paired same-paragraph bookmark: {anchor}")
        return index, start_node, local_endings[0]

    sections = plan["section_domain"]
    starts = [bookmark_location(section)[0] for section in sections]
    if starts != sorted(set(starts)):
        raise ReaderFidelityError("Word section anchors changed order")
    bounds = {section: (starts[index], starts[index + 1] if index + 1 < len(starts) else len(paragraphs))
              for index, section in enumerate(sections)}
    planned = {row["placement_id"]: row for row in plan["placements"]}
    observed: dict[str, dict[str, Any]] = {}
    for paragraph_index, paragraph in enumerate(paragraphs):
        for drawing in paragraph.xpath(".//w:drawing", namespaces=NS):
            docpr = drawing.find(".//" + WP + "docPr")
            extents = drawing.findall(".//" + WP + "extent")
            if docpr is None or len(extents) != 1:
                raise ReaderFidelityError("Word drawing has missing metadata or ambiguous extent")
            pid = docpr.get("descr")
            if pid not in planned or pid in observed:
                raise ReaderFidelityError("Word drawing is orphaned or duplicates a placement ID")
            row = planned[pid]
            if row["story_id"] not in bounds:
                raise ReaderFidelityError("Word placement has no reviewed story section")
            start, end = bounds[row["story_id"]]
            anchor, anchor_start, anchor_end = bookmark_location(row["anchor"])
            if (not start <= paragraph_index < end or not start <= anchor < end
                    or (row["position"] == "after" and paragraph_index < anchor)
                    or (row["position"] == "before" and paragraph_index > anchor)):
                raise ReaderFidelityError("Word drawing has wrong story/anchor position")
            if paragraph_index == anchor:
                order = list(paragraph.iter())
                drawing_at = order.index(drawing)
                visible = [order.index(node) for node in paragraph.xpath(".//w:t", namespaces=NS)
                           if node.text]
                boundary = max([order.index(anchor_end), *visible]) if row["position"] == "after" else min([order.index(anchor_start), *visible])
                if ((row["position"] == "after" and drawing_at <= boundary)
                        or (row["position"] == "before" and drawing_at >= boundary)):
                    raise ReaderFidelityError("Word drawing is on wrong side of inline anchor text")
            extent = extents[0]
            try:
                dimensions = {"width_emu": int(extent.get("cx")), "height_emu": int(extent.get("cy"))}
            except (TypeError, ValueError) as error:
                raise ReaderFidelityError("Word drawing extent is malformed") from error
            if dimensions != row["fit"]:
                raise ReaderFidelityError("Word drawing extent differs from approved fit")
            crops = drawing.findall(".//" + A + "srcRect")
            if len(crops) > 1:
                raise ReaderFidelityError("Word drawing crop is ambiguous")
            crop = {key: 0.0 for key in ("left", "top", "right", "bottom")}
            if crops:
                for edge, attribute in (("left", "l"), ("top", "t"), ("right", "r"), ("bottom", "b")):
                    try:
                        crop[edge] = int(crops[0].get(attribute, "0")) / 100000
                    except ValueError as error:
                        raise ReaderFidelityError("Word drawing crop is malformed") from error
            if any(abs(crop[key] - row["crop"][key]) > 0.00001 for key in crop):
                raise ReaderFidelityError("Word drawing crop differs from reviewed crop")
            try:
                media_sha = _media_for_drawing(drawing, rels, parts)
            except ValueError as error:
                raise ReaderFidelityError(f"Word drawing relationship/media is invalid: {error}") from error
            if media_sha != row["selected_sha256"]:
                raise ReaderFidelityError("Word drawing binary differs from reviewed selection")
            observed[pid] = {"placement_id": pid, "graphic_id": row["graphic_id"],
                             "story_id": row["story_id"], "paragraph_index": paragraph_index,
                             "media_sha256": media_sha, "extent": dimensions, "crop": crop}
    if set(observed) != set(planned):
        raise ReaderFidelityError("actual Word drawings do not cover every planned placement")
    return [observed[row["placement_id"]] for row in plan["placements"]]


def write_verification(plan_path: Path, docx_path: Path, package_root: Path,
                       report_path: Path) -> dict[str, Any]:
    """Seal independent actual-DOCX observations; output visual review stays pending."""
    plan = validate_plan(plan_path)
    root = package_root.resolve(strict=True)
    docx = docx_path.resolve(strict=True)
    if not docx.is_relative_to(root) or report_path.exists():
        raise ReaderFidelityError("DOCX verification target is unsafe or already exists")
    pages = []
    render_root = root / "render"
    if render_root.is_dir():
        pages = [{"path": path.relative_to(root).as_posix(), **file_identity(path)}
                 for path in sorted(render_root.glob("page-*.png"))]
    value = sealed(VERIFICATION_SCHEMA, {
        "source_pdf": plan["source_pdf"], "inventory": plan["inventory"],
        "review": plan["review"],
        "plan": {"path": str(plan_path.resolve(strict=True)), **file_identity(plan_path)},
        "docx": {"path": docx.relative_to(root).as_posix(), **file_identity(docx)},
        "verifier": {"implementation_sha256": file_identity(Path(__file__))["sha256"]},
        "graphics": verify_word_graphics(plan_path, docx),
        "text": verify_word_text(plan_path, docx),
        "render_pages": pages, "discrepancies": [],
        "mechanical_state": "closed", "semantic_state": "needs_output_review",
    }, digest_key="verification_sha256")
    report_path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return value


def verify_verification(report_path: Path, package_root: Path,
                        *, expected_plan: Path | None = None) -> dict[str, Any]:
    """Reopen a package and recompute Word observations from sealed authorities."""
    root = package_root.resolve(strict=True)
    if not report_path.is_file() or report_path.is_symlink() or not report_path.resolve().is_relative_to(root):
        raise ReaderFidelityError("DOCX fidelity report is missing from package")
    value = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ReaderFidelityError("DOCX fidelity report must be an object")
    validate_seal(value, "verification_sha256")
    _closed(value, {"schema", "source_pdf", "inventory", "review", "plan", "docx",
                    "verifier", "graphics", "text", "render_pages", "discrepancies",
                    "mechanical_state", "semantic_state", "verification_sha256"}, "DOCX fidelity report")
    if (value["schema"] != VERIFICATION_SCHEMA or value["mechanical_state"] != "closed"
            or value["semantic_state"] != "needs_output_review" or value["discrepancies"]):
        raise ReaderFidelityError("DOCX fidelity report is not a supported closed mechanical state")
    if value["verifier"] != {"implementation_sha256": file_identity(Path(__file__))["sha256"]}:
        raise ReaderFidelityError("DOCX fidelity verifier implementation changed")
    plan_path = _exact_file(value["plan"], label="reader plan")
    if expected_plan is not None and plan_path.resolve() != expected_plan.resolve(strict=True):
        raise ReaderFidelityError("DOCX package plan differs from expected authority")
    plan = validate_plan(plan_path)
    if any(value[key] != plan[key] for key in ("source_pdf", "inventory", "review")):
        raise ReaderFidelityError("DOCX fidelity report source authority mismatch")
    docx_row = _closed(value["docx"], {"path", "bytes", "sha256"}, "actual Word")
    docx_path = (root / str(docx_row["path"])).resolve()
    if (not docx_path.is_relative_to(root) or not docx_path.is_file() or docx_path.is_symlink()
            or {"path": docx_path.relative_to(root).as_posix(), **file_identity(docx_path)} != docx_row):
        raise ReaderFidelityError("actual Word identity differs from fidelity report")
    if value["graphics"] != verify_word_graphics(plan_path, docx_path):
        raise ReaderFidelityError("DOCX graphic observation changed")
    if value["text"] != verify_word_text(plan_path, docx_path):
        raise ReaderFidelityError("DOCX text observation changed")
    actual_pages = []
    render_root = root / "render"
    if render_root.is_dir():
        actual_pages = [{"path": path.relative_to(root).as_posix(), **file_identity(path)}
                        for path in sorted(render_root.glob("page-*.png"))]
    if actual_pages != value["render_pages"]:
        raise ReaderFidelityError("DOCX render review images changed")
    return value
