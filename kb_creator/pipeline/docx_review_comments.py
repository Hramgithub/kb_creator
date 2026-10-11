"""Bind identity-checked review issues to native Word comments.

The module intentionally works at OOXML level.  ``python-docx`` cannot create
native comments while retaining arbitrary run formatting and hyperlink wrappers.
"""
from __future__ import annotations

import json
import os
import zipfile
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from lxml import etree

from kb_creator.pipeline.identity import sha256_file
from kb_creator.scripts.production_docx import bookmark_name


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": WORD_NS, "r": DOC_REL_NS}
W = f"{{{WORD_NS}}}"
R = f"{{{DOC_REL_NS}}}"


class DocxReviewCommentsError(ValueError):
    """Raised when an annotation cannot be bound without loss of precision."""


def _require_distinct_paths(**paths: Path) -> None:
    """Reject aliases before any output path can be created or replaced."""
    seen: dict[Path, str] = {}
    for label, path in paths.items():
        other = seen.get(path)
        if other is not None:
            raise DocxReviewCommentsError(f"{label} must not alias {other}: {path}")
        seen[path] = label


def _q(name: str) -> str:
    return W + name


def _xml_text(element: etree._Element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS))


def _parse_xml(payload: bytes, member: str) -> etree._Element:
    try:
        return etree.fromstring(payload)
    except etree.XMLSyntaxError as exc:
        raise DocxReviewCommentsError(f"invalid OOXML member {member}: {exc}") from exc


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DocxReviewCommentsError(f"issue {field} must be a non-empty string")
    return value


def _require_source_page(value: object) -> str | int:
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str) and value.strip():
        return value
    raise DocxReviewCommentsError("issue source_page must be a positive integer or non-empty string")


def _validate_registry(registry: object, source_hash: str) -> list[dict[str, Any]]:
    if not isinstance(registry, dict):
        raise DocxReviewCommentsError("issues registry must be an object")
    if registry.get("schema") != "kb_creator.docx_review_issues.v1":
        raise DocxReviewCommentsError("unsupported issues registry schema")
    declared_hash = registry.get("docx_sha256")
    if not isinstance(declared_hash, str) or declared_hash.upper() != source_hash:
        raise DocxReviewCommentsError("issues registry docx_sha256 does not match source DOCX")
    issues = registry.get("issues")
    if not isinstance(issues, list) or not issues:
        raise DocxReviewCommentsError("issues registry must contain a non-empty issues list")
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for raw in issues:
        if not isinstance(raw, dict):
            raise DocxReviewCommentsError("each issue must be an object")
        issue = dict(raw)
        issue_id = _require_string(issue.get("issue_id"), "issue_id")
        if issue_id in seen:
            raise DocxReviewCommentsError(f"duplicate issue_id: {issue_id}")
        seen.add(issue_id)
        for field in ("reader_anchor", "target_text", "reason", "en_excerpt"):
            _require_string(issue.get(field), field)
        _require_source_page(issue.get("source_page"))
        proposal = issue.get("proposal")
        if proposal is not None and (not isinstance(proposal, str) or not proposal.strip()):
            raise DocxReviewCommentsError("issue proposal must be a non-empty string when present")
        validated.append(issue)
    return validated


def _bookmark_paragraph(root: etree._Element, anchor: str) -> etree._Element:
    name = bookmark_name(anchor)
    starts = root.xpath(".//w:bookmarkStart[@w:name=$name]", namespaces=NS, name=name)
    if len(starts) != 1:
        raise DocxReviewCommentsError(f"reader anchor must occur exactly once: {anchor!r}")
    paragraph = starts[0].xpath("ancestor::w:p[1]", namespaces=NS)
    if len(paragraph) != 1:
        raise DocxReviewCommentsError(f"reader anchor has no paragraph: {anchor!r}")
    return paragraph[0]


def _vanish_enabled(properties: etree._Element | None) -> bool | None:
    if properties is None:
        return None
    vanish = properties.find(_q("vanish"))
    if vanish is None:
        return None
    value = str(vanish.get(_q("val"), "true")).strip().casefold()
    return value not in {"0", "false", "off", "no"}


class _StyleVisibility:
    """Resolve only the inherited ``w:vanish`` property needed for targeting."""

    def __init__(self, styles: etree._Element | None) -> None:
        self.styles = styles
        self.by_id = {
            str(style.get(_q("styleId"))): style
            for style in styles.xpath("./w:style", namespaces=NS)
        } if styles is not None else {}

    def _style_properties(self, style_id: str) -> list[etree._Element]:
        seen: set[str] = set()

        def visit(identifier: str) -> list[etree._Element]:
            if not identifier or identifier in seen:
                return []
            seen.add(identifier)
            style = self.by_id.get(identifier)
            if style is None:
                return []
            base = style.find(_q("basedOn"))
            parent_id = str(base.get(_q("val"))) if base is not None else ""
            result = visit(parent_id)
            properties = style.find(_q("rPr"))
            if properties is not None:
                result.append(properties)
            return result

        return visit(style_id)

    def hidden(self, paragraph: etree._Element, run: etree._Element) -> bool:
        properties: list[etree._Element] = []
        if self.styles is not None:
            default = self.styles.find("./w:docDefaults/w:rPrDefault/w:rPr", namespaces=NS)
            if default is not None:
                properties.append(default)
        paragraph_properties = paragraph.find(_q("pPr"))
        if paragraph_properties is not None:
            paragraph_style = paragraph_properties.find(_q("pStyle"))
            if paragraph_style is not None:
                properties.extend(self._style_properties(str(paragraph_style.get(_q("val"), ""))))
            paragraph_run_properties = paragraph_properties.find(_q("rPr"))
            if paragraph_run_properties is not None:
                properties.append(paragraph_run_properties)
        run_properties = run.find(_q("rPr"))
        if run_properties is not None:
            run_style = run_properties.find(_q("rStyle"))
            if run_style is not None:
                properties.extend(self._style_properties(str(run_style.get(_q("val"), ""))))
            properties.append(run_properties)
        hidden = False
        for item in properties:
            value = _vanish_enabled(item)
            if value is not None:
                hidden = value
        return hidden


def _validate_paragraph_constructs(paragraph: etree._Element, visibility: _StyleVisibility) -> None:
    """Reject all content that does not have a precise visible-text model.

    A comment range is allowed to share a paragraph with existing comment and
    bookmark markers.  Every other direct child must be a plain text run or a
    hyperlink containing only such runs.  This prevents the matcher from
    concatenating text across breaks, tabs, fields, drawings, controls, or
    tracked-change wrappers that it cannot faithfully describe.
    """
    marker_tags = {_q(name) for name in ("bookmarkStart", "bookmarkEnd", "commentRangeStart", "commentRangeEnd")}
    for child in paragraph:
        if child.tag in {_q("pPr")} | marker_tags:
            continue
        containers = [child] if child.tag == _q("r") else list(child) if child.tag == _q("hyperlink") else []
        if not containers:
            raise DocxReviewCommentsError("unsupported construct inside anchored paragraph")
        for run in containers:
            if run.tag != _q("r"):
                raise DocxReviewCommentsError("unsupported hyperlink construct inside anchored paragraph")
            tags = {item.tag for item in run}
            if tags.issubset({_q("rPr"), _q("commentReference")}) and any(
                item.tag == _q("commentReference") for item in run
            ):
                continue
            if any(item.tag not in {_q("rPr"), _q("t")} for item in run) or not run.xpath("./w:t", namespaces=NS):
                raise DocxReviewCommentsError("unsupported run construct inside anchored paragraph")
            if visibility.hidden(paragraph, run):
                raise DocxReviewCommentsError("hidden text cannot be a reader-facing comment target")


def _run_text_nodes(paragraph: etree._Element, visibility: _StyleVisibility) -> list[tuple[etree._Element, etree._Element]]:
    """Return text nodes whose run can safely be split without widening a range."""
    _validate_paragraph_constructs(paragraph, visibility)
    rows: list[tuple[etree._Element, etree._Element]] = []
    for text in paragraph.xpath(".//w:t", namespaces=NS):
        run = text.getparent()
        if run is None or run.tag != _q("r"):
            raise DocxReviewCommentsError("unsupported text construct inside anchored paragraph")
        parent = run.getparent()
        if parent is None or parent.tag not in {_q("p"), _q("hyperlink")}:
            raise DocxReviewCommentsError("unsupported run wrapper inside anchored paragraph")
        if any(child.tag not in {_q("rPr"), _q("t")} for child in run):
            raise DocxReviewCommentsError("unsupported mixed run construct inside anchored paragraph")
        if visibility.hidden(paragraph, run):
            raise DocxReviewCommentsError("hidden text cannot be a reader-facing comment target")
        rows.append((run, text))
    return rows


def _split_run(run: etree._Element, text: etree._Element, start: int, end: int) -> tuple[etree._Element | None, etree._Element, etree._Element | None]:
    value = text.text or ""
    if not (0 <= start < end <= len(value)):
        raise DocxReviewCommentsError("invalid exact-text range")
    if len(run.xpath("./w:t", namespaces=NS)) != 1:
        raise DocxReviewCommentsError("a comment target may not cross multiple text nodes in one run")

    def clone(piece: str) -> etree._Element | None:
        if not piece:
            return None
        result = deepcopy(run)
        candidate = result.find(_q("t"))
        assert candidate is not None
        candidate.text = piece
        if piece.startswith(" ") or piece.endswith(" "):
            candidate.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        return result

    return clone(value[:start]), clone(value[start:end]), clone(value[end:])


def _split_target_runs(paragraph: etree._Element, target: str, visibility: _StyleVisibility) -> list[etree._Element]:
    rows = _run_text_nodes(paragraph, visibility)
    full_text = "".join((text.text or "") for _run, text in rows)
    count = full_text.count(target)
    if count != 1:
        raise DocxReviewCommentsError(
            f"target text must occur exactly once in anchored paragraph; found {count}: {target!r}"
        )
    start = full_text.index(target)
    end = start + len(target)
    cursor = 0
    selected: list[etree._Element] = []
    for run, text in rows:
        value = text.text or ""
        next_cursor = cursor + len(value)
        overlap_start, overlap_end = max(start, cursor), min(end, next_cursor)
        if overlap_start < overlap_end:
            before, exact, after = _split_run(run, text, overlap_start - cursor, overlap_end - cursor)
            parent = run.getparent()
            assert parent is not None
            index = parent.index(run)
            parent.remove(run)
            for replacement in (before, exact, after):
                if replacement is not None:
                    parent.insert(index, replacement)
                    index += 1
            assert exact is not None
            selected.append(exact)
        cursor = next_cursor
    if not selected:
        raise DocxReviewCommentsError("exact target produced no supported OOXML runs")
    return selected


def _range_comment(paragraph: etree._Element, runs: list[etree._Element], comment_id: int) -> None:
    first_parent = runs[0].getparent()
    last_parent = runs[-1].getparent()
    if first_parent is None or last_parent is None:
        raise DocxReviewCommentsError("comment target detached from paragraph")
    start = etree.Element(_q("commentRangeStart"))
    start.set(_q("id"), str(comment_id))
    end = etree.Element(_q("commentRangeEnd"))
    end.set(_q("id"), str(comment_id))
    first_parent.insert(first_parent.index(runs[0]), start)
    last_parent.insert(last_parent.index(runs[-1]) + 1, end)
    reference_run = etree.Element(_q("r"))
    reference = etree.SubElement(reference_run, _q("commentReference"))
    reference.set(_q("id"), str(comment_id))
    # Keep the native sequence exact for both plain runs and hyperlink wrappers:
    # range start, selected text, range end, then the comment reference.
    last_parent.insert(last_parent.index(end) + 1, reference_run)


def _comment_text(issue: dict[str, Any]) -> str:
    parts = [f"[{issue['issue_id']}] {issue['reason']}"]
    if issue.get("proposal"):
        parts.append(f"Предложение: {issue['proposal']}")
    parts.append(f"Источник: стр. {issue['source_page']}; EN: {issue['en_excerpt']}")
    return "\n".join(parts)


def _comments_root(existing: bytes | None) -> etree._Element:
    if existing is not None:
        root = _parse_xml(existing, "word/comments.xml")
        if root.tag != _q("comments"):
            raise DocxReviewCommentsError("word/comments.xml has an unexpected root")
        return root
    return etree.Element(_q("comments"), nsmap={"w": WORD_NS})


def _next_comment_id(comments: etree._Element) -> int:
    ids = []
    for value in comments.xpath("./w:comment/@w:id", namespaces=NS):
        if not str(value).isdigit():
            raise DocxReviewCommentsError("existing comment has non-numeric id")
        ids.append(int(value))
    return max(ids, default=-1) + 1


def _add_comment(comments: etree._Element, comment_id: int, issue: dict[str, Any]) -> None:
    comment = etree.SubElement(comments, _q("comment"))
    comment.set(_q("id"), str(comment_id))
    comment.set(_q("author"), "NRI")
    comment.set(_q("initials"), "NRI")
    comment.set(_q("date"), datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    paragraph = etree.SubElement(comment, _q("p"))
    run = etree.SubElement(paragraph, _q("r"))
    text = etree.SubElement(run, _q("t"))
    text.text = _comment_text(issue)
    text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def _ensure_package_wiring(rels: etree._Element, types: etree._Element) -> None:
    comment_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
    comment_relationships = rels.xpath(
        "./pr:Relationship[@Type=$type]", namespaces={"pr": REL_NS}, type=comment_type
    )
    if comment_relationships:
        if len(comment_relationships) != 1:
            raise DocxReviewCommentsError("DOCX has multiple comments relationships")
        relationship = comment_relationships[0]
        if relationship.get("Target") != "comments.xml" or relationship.get("TargetMode") not in {None, "Internal"}:
            raise DocxReviewCommentsError("DOCX comments relationship must target comments.xml internally")
    else:
        used = {str(item.get("Id")) for item in rels}
        number = 1
        while f"rId{number}" in used:
            number += 1
        relation = etree.SubElement(rels, f"{{{REL_NS}}}Relationship")
        relation.set("Id", f"rId{number}")
        relation.set("Type", comment_type)
        relation.set("Target", "comments.xml")
    override_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
    matches = types.xpath("./ct:Override[@PartName='/word/comments.xml']", namespaces={"ct": CONTENT_TYPES_NS})
    if matches:
        if len(matches) != 1 or matches[0].get("ContentType") != override_type:
            raise DocxReviewCommentsError("comments content type conflicts with existing package entry")
    else:
        override = etree.SubElement(types, f"{{{CONTENT_TYPES_NS}}}Override")
        override.set("PartName", "/word/comments.xml")
        override.set("ContentType", override_type)


def annotate_docx_review(source: Path, registry_path: Path, output: Path) -> dict[str, Any]:
    """Create a new DOCX with exact-text Word comments from a sealed input identity."""
    source, registry_path, output = source.resolve(), registry_path.resolve(), output.resolve()
    _require_distinct_paths(source=source, registry=registry_path, output=output)
    if not source.is_file():
        raise FileNotFoundError(source)
    if not registry_path.is_file():
        raise FileNotFoundError(registry_path)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite output DOCX: {output}")
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise DocxReviewCommentsError(f"invalid issues registry JSON: {exc}") from exc
    source_hash = sha256_file(source)
    issues = _validate_registry(registry, source_hash)
    with zipfile.ZipFile(source) as archive:
        if archive.testzip() is not None:
            raise DocxReviewCommentsError("source DOCX archive is corrupt")
        names = set(archive.namelist())
        required = {"word/document.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}
        missing = required - names
        if missing:
            raise DocxReviewCommentsError(f"source DOCX lacks required members: {sorted(missing)}")
        document = _parse_xml(archive.read("word/document.xml"), "word/document.xml")
        rels = _parse_xml(archive.read("word/_rels/document.xml.rels"), "word/_rels/document.xml.rels")
        types = _parse_xml(archive.read("[Content_Types].xml"), "[Content_Types].xml")
        styles = _parse_xml(archive.read("word/styles.xml"), "word/styles.xml") if "word/styles.xml" in names else None
        visibility = _StyleVisibility(styles)
        comments = _comments_root(archive.read("word/comments.xml") if "word/comments.xml" in names else None)
        next_id = _next_comment_id(comments)
        bindings = []
        for issue in issues:
            paragraph = _bookmark_paragraph(document, issue["reader_anchor"])
            runs = _split_target_runs(paragraph, issue["target_text"], visibility)
            comment_id = next_id
            next_id += 1
            _range_comment(paragraph, runs, comment_id)
            _add_comment(comments, comment_id, issue)
            bindings.append({
                "issue_id": issue["issue_id"], "reader_anchor": issue["reader_anchor"],
                "bookmark_name": bookmark_name(issue["reader_anchor"]), "comment_id": comment_id,
                "selected_text": issue["target_text"],
            })
        _ensure_package_wiring(rels, types)
        replacements = {
            "word/document.xml": etree.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True),
            "word/comments.xml": etree.tostring(comments, xml_declaration=True, encoding="UTF-8", standalone=True),
            "word/_rels/document.xml.rels": etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True),
            "[Content_Types].xml": etree.tostring(types, xml_declaration=True, encoding="UTF-8", standalone=True),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.tmp")
        temporary_created = False
        try:
            # ``x`` refuses an existing sibling and avoids silently replacing a
            # prior interrupted build.  Linking publishes only if output is
            # still absent, so a concurrent creator cannot be overwritten.
            with zipfile.ZipFile(temporary, "x") as destination:
                temporary_created = True
                for info in archive.infolist():
                    destination.writestr(info, replacements.pop(info.filename, archive.read(info.filename)))
                for name, payload in replacements.items():
                    destination.writestr(name, payload)
            if zipfile.ZipFile(temporary).testzip() is not None:
                raise DocxReviewCommentsError("annotated DOCX archive is corrupt")
            os.link(temporary, output)
            temporary.unlink()
        finally:
            if temporary_created and temporary.exists():
                temporary.unlink()
    return {
        "schema": "kb_creator.docx_review_comments_report.v1",
        "source": {"path": source.as_posix(), "sha256": source_hash},
        "output": {"path": output.as_posix(), "sha256": sha256_file(output)},
        "bindings": bindings,
    }


def write_annotation_report(source: Path, registry: Path, output: Path, report: Path) -> dict[str, Any]:
    source, registry, output, report = source.resolve(), registry.resolve(), output.resolve(), report.resolve()
    _require_distinct_paths(source=source, registry=registry, output=output, report=report)
    if report.exists():
        raise FileExistsError(f"refusing to overwrite binding report: {report}")
    result = annotate_docx_review(source, registry, output)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result
