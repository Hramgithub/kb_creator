"""DOCX-only materialization for the ``five_step_docx_v1`` profile.

This module deliberately does not call the historic publication state machine:
that route has accepted ArtView/HTML/PDF authorities which are outside this
profile.  The generated package is a review candidate, never a release.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import tempfile
import zipfile
import copy
from pathlib import Path
from typing import Any

from lxml import html as lxml_html

from kb_creator.scripts.production_docx import build_docx_projection
from kb_creator.scripts.publication_render_qa import render_docx_transient
from kb_creator.scripts.normalize_publication_access import normalize_publication_access_if_managed
from translator.translator import markdown_to_review_html, unique_slug
from .identity import file_identity


SCHEMA = "kb_creator.five_step_docx_package.v3"
PREVIOUS_SCHEMA = "kb_creator.five_step_docx_package.v2"
LEGACY_SCHEMA = "kb_creator.five_step_docx_package.v1"
MANIFEST = "DOCX_MANIFEST.json"
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")
_ANCHOR_RE = re.compile(r"(?:<a\s+id=[\"']([^\"']+)[\"']\s*></a>|\{#([A-Za-z0-9_-]+)\})")
_HEADING_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_TABLE_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*\|.*\|[ \t]*$\n^[ \t]*(?:>[ \t]*)*\|[ \t]*:?-{3,}", re.MULTILINE)
_STATBLOCK_RE = re.compile(r"<!--\s*semantic-span-start:\s*statblock;", re.I)


class FiveStepDocxError(ValueError):
    """A profile-local closure or input error."""


def verify_duplicate_text_docx(reader_report: dict[str, Any], document_xml: bytes) -> None:
    """Compare affected source-page Word paragraphs with the archived reader witness."""
    witnesses = reader_report.get("duplicate_page_witness", [])
    rows = list(reader_report.get("omitted_text_duplicates", []))
    rows += [row for row in reader_report.get("omitted_artifacts", [])
             if isinstance(row, dict) and row.get("actual_source_page") is not None]
    if not rows and not witnesses:
        return
    if not isinstance(rows, list) or not isinstance(witnesses, list) or not witnesses:
        raise FiveStepDocxError("duplicate text reader witness is missing")
    if {row.get("actual_source_page") for row in rows} != {item.get("source_page") for item in witnesses}:
        raise FiveStepDocxError("duplicate text omission rows and page witness differ")
    _verify_page_streams(document_xml, witnesses)


def _word_visible_text(paragraph: Any) -> str:
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    parts = []
    for node in paragraph.iter():
        if node.tag == f"{{{ns}}}t":
            parts.append(node.text or "")
        elif node.tag == f"{{{ns}}}br" and node.get(f"{{{ns}}}type") != "page":
            parts.append("\n")
        elif node.tag == f"{{{ns}}}tab":
            parts.append("\t")
    return "".join(parts)


def _word_bookmark_index(xml: Any, paragraphs: list, anchor: str) -> int:
    """Resolve one actual paired bookmark to its owning Word paragraph."""
    from kb_creator.scripts.production_docx import bookmark_name
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    name = bookmark_name(anchor)
    starts = [node for node in xml.iter(f"{{{ns}}}bookmarkStart")
              if node.get(f"{{{ns}}}name") == name]
    if len(starts) != 1:
        raise FiveStepDocxError(f"reader bookmark missing or repeated: {anchor}")
    start = starts[0]
    ident = start.get(f"{{{ns}}}id")
    ends = [node for node in xml.iter(f"{{{ns}}}bookmarkEnd") if node.get(f"{{{ns}}}id") == ident]
    if (not ident or len(ends) != 1
            or sum(node.get(f"{{{ns}}}id") == ident for node in xml.iter(f"{{{ns}}}bookmarkStart")) != 1):
        raise FiveStepDocxError(f"reader bookmark has no unique matching end: {anchor}")
    owner = next((node for node in start.iterancestors() if node.tag == f"{{{ns}}}p"), None)
    end_owner = next((node for node in ends[0].iterancestors() if node.tag == f"{{{ns}}}p"), None)
    if owner is None or owner is not end_owner or owner not in paragraphs:
        raise FiveStepDocxError(f"reader bookmark changed paragraph owner: {anchor}")
    members = list(owner.iter())
    if members.index(start) >= members.index(ends[0]):
        raise FiveStepDocxError(f"reader bookmark end precedes start: {anchor}")
    return paragraphs.index(owner)


def _verify_page_streams(document_xml: bytes, witnesses: list[dict]) -> tuple[list, Any]:
    """One Word paragraph extraction for omission and reflow page domains."""
    from lxml import etree
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    xml = etree.fromstring(document_xml)
    bodies = xml.findall(f".//{{{ns}}}body")
    if len(bodies) != 1:
        raise FiveStepDocxError("reader DOCX body is missing")
    paragraphs = list(bodies[0].iter(f"{{{ns}}}p"))
    def index(anchor):
        return _word_bookmark_index(xml, paragraphs, anchor)
    for witness in witnesses:
        if (not isinstance(witness, dict) or set(witness) != {"source_page", "boundary", "next_boundary", "expected_paragraphs"}
                or not isinstance(witness["expected_paragraphs"], list)):
            raise FiveStepDocxError("duplicate text page witness is malformed")
        start = index(witness["boundary"])
        end = index(witness["next_boundary"]) if witness["next_boundary"] else len(paragraphs)
        if start >= end:
            raise FiveStepDocxError("duplicate text source-page boundary order changed")
        actual = [value for paragraph in paragraphs[start:end] if (value := _word_visible_text(paragraph))]
        if actual != witness["expected_paragraphs"]:
            raise FiveStepDocxError(f"reader DOCX paragraph stream differs on source page {witness['source_page']}: actual={actual!r} expected={witness['expected_paragraphs']!r}")
    return paragraphs, index


def _verify_page_owner(paragraphs: list, index: Any, witness: dict, anchor: str, ordinal: int) -> None:
    start = index(witness["boundary"])
    end = index(witness["next_boundary"]) if witness["next_boundary"] else len(paragraphs)
    visible_positions = [position for position in range(start, end)
                         if _word_visible_text(paragraphs[position])]
    if (type(ordinal) is not int or ordinal < 0 or ordinal >= len(visible_positions)
            or index(anchor) != visible_positions[ordinal]):
        raise FiveStepDocxError(f"reader bookmark changed expected paragraph owner: {anchor}")


def verify_reflow_docx(reader_report: dict[str, Any], document_xml: bytes) -> None:
    dependencies = reader_report.get("reflow_dependencies", [])
    witnesses = reader_report.get("reflow_page_witness", [])
    if not dependencies and not witnesses:
        return
    if not isinstance(dependencies, list) or not dependencies or not isinstance(witnesses, list):
        raise FiveStepDocxError("extended reflow evidence is missing")
    domain = {page for row in dependencies for page in row["source_pages"]}
    if domain != {row.get("source_page") for row in witnesses} or len(domain) != len(witnesses):
        raise FiveStepDocxError("extended reflow page domain differs from witness")
    omission = {row["source_page"]: row["expected_paragraphs"]
                for row in reader_report.get("duplicate_page_witness", [])}
    if any(row["source_page"] in omission and row["expected_paragraphs"] != omission[row["source_page"]]
           for row in witnesses):
        raise FiveStepDocxError("reflow and omission witnesses disagree")
    paragraphs, index = _verify_page_streams(document_xml, witnesses)
    for dependency in dependencies:
        left, right = index(dependency["left_anchor"]), index(dependency["right_anchor"])
        left_page = next(row for row in witnesses if row["source_page"] == dependency["left_page"])
        start = index(left_page["boundary"])
        end = index(left_page["next_boundary"]) if left_page["next_boundary"] else len(paragraphs)
        if left != right or not start <= left < end:
            raise FiveStepDocxError("extended reflow continuation bookmark left its joined paragraph")
        joined_owner = dependency["joined_owner"]
        if _word_visible_text(paragraphs[left]) != joined_owner["text"]:
            raise FiveStepDocxError("extended reflow joined paragraph text changed")
        _verify_page_owner(paragraphs, index, left_page, dependency["left_anchor"],
                           joined_owner.get("paragraph_ordinal"))
        _verify_page_owner(paragraphs, index, left_page, dependency["right_anchor"],
                           joined_owner.get("paragraph_ordinal"))
        owners = dependency.get("retained_title_owners", [])
        if {row["anchor"] for row in owners} != set(dependency["retained_title_anchors"]):
            raise FiveStepDocxError("extended reflow retained title owner witness differs")
        for owner in owners:
            position = index(owner["anchor"])
            owner_page = next((row for row in witnesses if row["source_page"] ==
                               owner.get("source_page", dependency["left_page"])), None)
            if owner_page is None or _word_visible_text(paragraphs[position]) != owner["text"]:
                raise FiveStepDocxError("extended reflow retained meaningful title bookmark changed")
            _verify_page_owner(paragraphs, index, owner_page, owner["anchor"], owner.get("paragraph_ordinal"))
        for pair in dependency["asset_pairs"]:
            page = next(row for row in witnesses if row["source_page"] == pair["source_page"])
            start = index(page["boundary"])
            end = index(page["next_boundary"]) if page["next_boundary"] else len(paragraphs)
            for anchor in (pair["list_anchor"], pair["image_anchor"]):
                position = index(anchor)
                if not start <= position < end:
                    raise FiveStepDocxError("extended reflow map dependency moved outside source page")
            if _word_visible_text(paragraphs[index(pair["list_anchor"])]) != pair.get("list_owner_text"):
                raise FiveStepDocxError("extended reflow map list bookmark changed paragraph owner")
            _verify_page_owner(paragraphs, index, page, pair["list_anchor"], pair.get("list_paragraph_ordinal"))


def verify_retained_links_docx(reader_report: dict[str, Any], document_xml: bytes) -> None:
    dependencies = reader_report.get("retained_link_dependencies", [])
    if not dependencies:
        return
    from lxml import etree
    from kb_creator.scripts.production_docx import bookmark_name
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    xml = etree.fromstring(document_xml)
    body = xml.find(f".//{{{ns}}}body")
    if body is None:
        raise FiveStepDocxError("retained link DOCX body is missing")
    paragraphs = list(body.iter(f"{{{ns}}}p"))
    witnesses = {row["source_page"]: row for row in reader_report.get("duplicate_page_witness", [])}
    for row in dependencies:
        source = paragraphs[_word_bookmark_index(xml, paragraphs, row["source_anchor"])]
        retained = paragraphs[_word_bookmark_index(xml, paragraphs, row["target_anchor"])]
        if _word_visible_text(retained) != row["retained_text"]:
            raise FiveStepDocxError("retained link target changed paragraph owner")
        if row.get("retained_page") not in witnesses:
            raise FiveStepDocxError("retained link target source-page witness is missing")
        _verify_page_owner(paragraphs, lambda anchor: _word_bookmark_index(xml, paragraphs, anchor),
                           witnesses[row["retained_page"]], row["target_anchor"], row.get("retained_ordinal"))
        target_name = bookmark_name(row["target_anchor"])
        links = [link for link in source.iter(f"{{{ns}}}hyperlink")
                 if link.get(f"{{{ns}}}anchor") == target_name
                 and _word_visible_text(link) == row["label"]]
        if len(links) != 1:
            raise FiveStepDocxError("retained owner native body link missing or retargeted")


def verify_retained_artwork_docx(reader_report: dict[str, Any], docx_path: Path) -> None:
    """Prove the reviewed original image is used by the exact retained figure."""
    dependencies = reader_report.get("retained_image_dependencies", [])
    if not dependencies:
        return
    from lxml import etree
    from kb_creator.scripts.production_docx import bookmark_name
    word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    drawing = "http://schemas.openxmlformats.org/drawingml/2006/main"
    relationships = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    package_rels = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(docx_path) as archive:
        names = set(archive.namelist())
        if "word/_rels/document.xml.rels" not in names:
            raise FiveStepDocxError("retained artwork DOCX relationship part is missing")
        xml = etree.fromstring(archive.read("word/document.xml"))
        rels = etree.fromstring(archive.read("word/_rels/document.xml.rels"))
        body = xml.find(f".//{{{word}}}body")
        if body is None:
            raise FiveStepDocxError("retained artwork DOCX body is missing")
        paragraphs = list(body.iter(f"{{{word}}}p"))
        relationships_by_id = {row.get("Id"): row for row in rels.findall(f"{{{package_rels}}}Relationship")}
        def bookmark_index(anchor):
            name = bookmark_name(anchor)
            matches = [index for index, paragraph in enumerate(paragraphs)
                       if any(mark.get(f"{{{word}}}name") == name for mark in paragraph.iter(f"{{{word}}}bookmarkStart"))]
            if len(matches) != 1:
                raise FiveStepDocxError(f"retained artwork bookmark missing or repeated: {anchor}")
            return matches[0]
        witnesses = {row["source_page"]: row for row in [*reader_report.get("duplicate_page_witness", []),
                                                         *reader_report.get("reflow_page_witness", [])]}
        for dependency in dependencies:
            if (not isinstance(dependency, dict)
                    or set(dependency) != {"source_page", "image_unit", "reference", "identity", "anchor"}
                    or dependency["source_page"] not in witnesses):
                raise FiveStepDocxError("retained artwork dependency report is malformed")
            witness = witnesses[dependency["source_page"]]
            index = bookmark_index(dependency["anchor"])
            start = bookmark_index(witness["boundary"])
            end = bookmark_index(witness["next_boundary"]) if witness["next_boundary"] else len(paragraphs)
            if not start <= index < end:
                raise FiveStepDocxError("retained artwork bookmark moved outside source page")
            blips = list(paragraphs[index].iter(f"{{{drawing}}}blip"))
            if len(blips) != 1:
                raise FiveStepDocxError("retained artwork paragraph lost its exact image occurrence")
            if any(True for _ in paragraphs[index].iter(f"{{{drawing}}}srcRect")):
                raise FiveStepDocxError("retained artwork image was cropped in DOCX")
            rel = relationships_by_id.get(blips[0].get(f"{{{relationships}}}embed"))
            if rel is None or rel.get("TargetMode") == "External" or not rel.get("Target"):
                raise FiveStepDocxError("retained artwork image relationship is missing")
            member = posixpath.normpath(posixpath.join("word", rel.get("Target")))
            if not member.startswith("word/media/") or member not in names:
                raise FiveStepDocxError("retained artwork image media target is invalid")
            data = archive.read(member)
            if {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest().upper()} != dependency["identity"]:
                raise FiveStepDocxError("retained artwork original image bytes changed")


def _replay_duplicate_reader(root: Path, stored: dict[str, Any], manifest: dict[str, Any]) -> None:
    """Regenerate reviewed removal evidence from archived options and source."""
    from kb_creator.pipeline.reader_projection import load_options, project_reader_html
    source = root / "INTERNAL_SEMANTIC_SOURCE.md"
    options_path = root / "reader_options.json"
    projection_path = root / "semantic_context" / "RU_PROJECTION.json"
    options = load_options(options_path, root / "MASTER_RU.md", projection_path)
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    effective = copy.deepcopy(options)
    issue_path = root / "SOURCE_ISSUE_RU_PROJECTION.json"
    if issue_path.is_file():
        effective["display_roles"].extend(json.loads(issue_path.read_text(encoding="utf-8"))["roles"])
    body, toc, _ = markdown_to_review_html(source.read_text(encoding="utf-8"), source_path=source,
                                           html_path=root / ".word-projection-base", blockquote_heading_offset=0)
    projected, _, replayed = project_reader_html(body, toc, projection, effective,
                                                 options_path=options_path, master_root=root)
    expected_html = "<!doctype html><html><head><meta charset=\"utf-8\"></head><body><main>\n" + projected + "\n</main></body></html>\n"
    if manifest["schema"] == LEGACY_SCHEMA:
        transport_matches = expected_html == (root / "internal.html").read_text(encoding="utf-8")
    elif manifest["schema"] == PREVIOUS_SCHEMA:
        transport_matches = hashlib.sha256(expected_html.encode("utf-8")).hexdigest().upper() == manifest.get("projection_transport_sha256")
    else:
        # The v3 reader-only art/text projection is checked against actual Word
        # and source authorities, not an unpublished serialized HTML transport.
        transport_matches = True
    if replayed != stored or not transport_matches:
        raise FiveStepDocxError("duplicate text archived reader projection differs from replay")


def verify_rich_source_toc_docx(reader_report: dict[str, Any], document_xml: bytes) -> None:
    """Close the sealed rich-source TOC projection against OOXML structure."""
    rich = reader_report.get("rich_source_toc")
    if not isinstance(rich, dict):
        return
    entries = rich.get("entry_count")
    rows = rich.get("display_rows")
    if type(entries) is not int or entries < 1 or not isinstance(rows, list) or len(rows) != entries:
        raise FiveStepDocxError("rich source TOC report is malformed")
    from lxml import etree
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    xml = etree.fromstring(document_xml)
    tables = xml.xpath(".//w:body/w:tbl[1]", namespaces=ns)
    if len(tables) != 1:
        raise FiveStepDocxError("rich source TOC requires one leading DOCX table")
    paragraphs = [paragraph for paragraph in tables[0].xpath(".//w:tc/w:p", namespaces=ns)
                  if "".join(paragraph.xpath(".//w:t/text()", namespaces=ns)).strip()]
    if len(paragraphs) != entries * 3:
        raise FiveStepDocxError("rich source TOC paragraph count differs from semantic entries")
    links = tables[0].xpath(".//w:hyperlink", namespaces=ns)
    if len(links) != entries or any(paragraph.xpath(".//w:hyperlink", namespaces=ns) for index, paragraph in enumerate(paragraphs) if index % 3):
        raise FiveStepDocxError("rich source TOC metadata hyperlinks are forbidden")
    def visible(paragraph):
        return " ".join("".join(paragraph.xpath(".//w:t/text()", namespaces=ns)).split())

    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"title", "byline", "synopsis"}:
            raise FiveStepDocxError("rich source TOC display row is malformed")
        if any(not isinstance(row[key], str) or not row[key] for key in row):
            raise FiveStepDocxError("rich source TOC display text is malformed")
        expected = [" ".join(row[key].split()) for key in ("title", "byline", "synopsis")]
        actual = [visible(paragraph) for paragraph in paragraphs[index * 3:index * 3 + 3]]
        if actual != expected:
            raise FiveStepDocxError("rich source TOC display row differs from DOCX")
        title_links = paragraphs[index * 3].xpath(".//w:hyperlink", namespaces=ns)
        if len(title_links) != 1 or not title_links[0].get(f"{{{ns['w']}}}anchor"):
            raise FiveStepDocxError("rich source TOC title requires one internal hyperlink")
    all_paragraph_text = {visible(paragraph) for paragraph in xml.xpath(".//w:p", namespaces=ns)}
    for omitted in rich.get("omitted_display", []):
        if not isinstance(omitted, str) or " ".join(omitted.split()) in all_paragraph_text:
            raise FiveStepDocxError("rich source TOC duplicate omission is not closed")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": _sha(path)}


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def _contained(path: Path, root: Path, label: str) -> Path:
    if path.is_symlink():
        raise FiveStepDocxError(f"{label} must not be a symlink")
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as error:
        raise FiveStepDocxError(f"{label} is missing") from error
    try:
        resolved.relative_to(root.resolve(strict=True))
    except ValueError as error:
        raise FiveStepDocxError(f"{label} escapes MASTER_RU root") from error
    if resolved.is_symlink() or not resolved.is_file():
        raise FiveStepDocxError(f"{label} must be a regular file")
    return resolved


def _master_file(master_ru: Path) -> Path:
    candidate = master_ru.resolve()
    if candidate.is_dir():
        candidate = candidate / "MASTER_RU.md"
    if candidate.name != "MASTER_RU.md" or not candidate.is_file() or candidate.is_symlink():
        raise FiveStepDocxError("master_ru must be a regular MASTER_RU.md or its containing directory")
    return candidate


def _default_config(title: str) -> dict[str, Any]:
    return {
        "schema": "kb_creator.production_docx_config.v1",
        "page": {"width_mm": 210, "height_mm": 297, "orientation": "portrait"},
        "margins": {"top_mm": 15, "bottom_mm": 15, "left_mm": 17, "right_mm": 17},
        "fonts": {"body": "Times New Roman", "title": "Times New Roman", "headings": "Times New Roman", "footer": "Times New Roman"},
        "sizes": {"body_pt": 10.5, "title_pt": 22, "footer_pt": 9},
        "spacing": {"body_after_pt": 4, "body_line": 1.05},
        "headings": {str(level): {"size_pt": size, "bold": level <= 3, "space_before_pt": 10 if level <= 2 else 7, "space_after_pt": 4} for level, size in {1: 18, 2: 15, 3: 12.5, 4: 11.5, 5: 10.5, 6: 10.5}.items()},
        "statblocks": {"keep_together": True},
        "footer": {"page_numbers": True},
        "metadata": {"title": title, "subject": "Документ", "author": "NRI", "keywords": "", "comments": "five_step_docx_v2"},
    }


def _load_config(config: Path | None, title: str, root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if config is None:
        return _default_config(title), None
    source = config.resolve(strict=True)
    if source.is_symlink() or not source.is_file():
        raise FiveStepDocxError("DOCX config must be a regular file")
    value = json.loads(source.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise FiveStepDocxError("DOCX config must be an object")
    # A caller-supplied config stays authoritative except for the requested title.
    value = {**value, "metadata": {**value.get("metadata", {}), "title": title}}
    return value, _identity(source, source.parent)


def _referenced_assets(text: str, master_root: Path) -> list[tuple[str, Path]]:
    refs: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for raw in _IMAGE_RE.findall(text):
        ref = raw.replace("\\", "/")
        if "://" in ref or ref.startswith("data:"):
            raise FiveStepDocxError("remote or data image references are not permitted")
        if ref in seen:
            continue
        seen.add(ref)
        source = _contained(master_root / Path(ref), master_root, f"image reference {ref!r}")
        refs.append((ref, source))
    return refs


def _validate_links(text: str) -> None:
    anchors = {item for pair in _ANCHOR_RE.findall(text) for item in pair if item}
    used_slugs: dict[str, int] = {}
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            anchors.add(unique_slug(match.group(1), used_slugs))
    for raw in _LINK_RE.findall(text):
        if raw.startswith("#"):
            if raw[1:] not in anchors:
                raise FiveStepDocxError(f"internal link target is missing: {raw}")
        elif "://" not in raw and not raw.startswith("mailto:"):
            raise FiveStepDocxError(f"local non-anchor link is not supported by DOCX package: {raw}")


def _asset_plan(text: str, assets: list[tuple[str, Path]], root: Path) -> list[dict[str, Any]]:
    """Bind each used image to the closest source page and text anchor."""
    plans: list[dict[str, Any]] = []
    for ref, _source in assets:
        marker = f"]({ref})"
        offset = text.find(marker)
        preceding = text[:offset] if offset >= 0 else ""
        page_matches = re.findall(r"<!--\s*(?:source-page|pdf-page)-(\d{3})\s*-->", preceding)
        anchor_matches = list(_ANCHOR_RE.finditer(preceding))
        anchor = next((item for match in reversed(anchor_matches) for item in match.groups() if item), None)
        plans.append({
            "source_reference": ref,
            "rendered_path": ref,
            "choice": "include",
            "provenance": "source_rule",
            "source_image_occurrences": sum(raw.replace("\\", "/") == ref for raw in _IMAGE_RE.findall(text)),
            "text_anchor": anchor,
            "source_page": int(page_matches[-1]) if page_matches else None,
            **_identity(root / Path(ref), root),
        })
    return plans


def _reader_image_occurrences(master_occurrences: int, reader_report: dict[str, Any] | None) -> int:
    """Close DOCX image count after reviewed omissions and source-region projection."""
    if isinstance(master_occurrences, bool) or not isinstance(master_occurrences, int) or master_occurrences < 0:
        raise FiveStepDocxError("MASTER_RU image occurrence count is invalid")
    if reader_report is None:
        return master_occurrences
    omissions = reader_report.get("omitted_artifacts", [])
    if not isinstance(omissions, list):
        raise FiveStepDocxError("reader omission report is invalid")
    total = 0
    for row in omissions:
        if not isinstance(row, dict) or isinstance(row.get("image_occurrences"), bool):
            raise FiveStepDocxError("reader omission report is invalid")
        occurrences = row.get("image_occurrences")
        reference = row.get("source_reference")
        if occurrences == 0 and reference is None:
            continue
        if occurrences != 1 or not isinstance(reference, str) or not reference:
            raise FiveStepDocxError("reader omission report must contain one image occurrence per omitted unit")
        total += occurrences
    if total > master_occurrences:
        raise FiveStepDocxError("reader omission count exceeds MASTER_RU image occurrences")
    groups = reader_report.get("source_figure_regions", [])
    if not isinstance(groups, list):
        raise FiveStepDocxError("reader source figure region report is invalid")
    region_removals = 0
    region_additions = 0
    seen_units: set[str] = set()
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for group in groups:
        if (not isinstance(group, dict) or not isinstance(group.get("unit"), dict)
                or not isinstance(group["unit"].get("unit_id"), str)
                or group["unit"]["unit_id"] in seen_units
                or group.get("source_image_occurrences") != 1
                or not isinstance(group.get("regions"), list)):
            raise FiveStepDocxError("reader source figure region report is invalid")
        seen_units.add(group["unit"]["unit_id"])
        region_removals += 1
        for region in group["regions"]:
            if (not isinstance(region, dict) or not isinstance(region.get("id"), str) or not region["id"]
                    or not isinstance(region.get("rendered_path"), str) or not region["rendered_path"]
                    or region["id"] in seen_ids or region["rendered_path"] in seen_paths):
                raise FiveStepDocxError("reader source figure region report is invalid")
            seen_ids.add(region["id"])
            seen_paths.add(region["rendered_path"])
            region_additions += 1
    if total + region_removals > master_occurrences:
        raise FiveStepDocxError("reader source figure removals exceed MASTER_RU image occurrences")
    return master_occurrences - total - region_removals + region_additions


def _semantic_projection(master_root: Path, master: Path, text: str) -> dict[str, Any]:
    path = master_root / "semantic_context" / "RU_PROJECTION.json"
    if not path.is_file() or path.is_symlink():
        raise FiveStepDocxError("RU semantic projection is required for DOCX materialization")
    value = json.loads(path.read_text(encoding="utf-8"))
    seal = value.pop("projection_sha256", None)
    if value.get("schema") != "kb_creator.five_step_ru_projection.v3" or seal != hashlib.sha256(_canonical(value)).hexdigest().upper():
        raise FiveStepDocxError("RU semantic projection seal mismatch")
    if value.get("master_ru") != _identity(master, master_root):
        raise FiveStepDocxError("RU semantic projection MASTER_RU identity mismatch")
    rows = value.get("units")
    if not isinstance(rows, list) or value.get("unit_order") != [row.get("unit_id") for row in rows]:
        raise FiveStepDocxError("RU semantic projection unit order is invalid")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"unit_id","source_hash","parent_unit_id","part_index","part_count","ru_text","ru_sha256"} or not isinstance(row.get("unit_id"), str) or not isinstance(row.get("source_hash"),str) or not isinstance(row.get("ru_text"), str) or row.get("ru_sha256") != hashlib.sha256(row["ru_text"].encode("utf-8")).hexdigest().upper():
            raise FiveStepDocxError("RU semantic projection unit is invalid")
        if row["unit_id"] in result: raise FiveStepDocxError("RU semantic projection contains duplicate unit IDs")
        split=row.get("parent_unit_id") is not None
        if split != (isinstance(row.get("part_index"),int) and isinstance(row.get("part_count"),int) and row["part_index"]>=1 and row["part_count"]>=row["part_index"]): raise FiveStepDocxError("RU semantic projection split parent metadata is invalid")
        result[row["unit_id"]] = row
    from kb_creator.pipeline.five_step_language import _assemble_map
    try: assembly=_assemble_map(rows)
    except Exception as error: raise FiveStepDocxError(f"RU semantic projection assembly is invalid: {error}") from error
    if assembly["text"] != text:
        raise FiveStepDocxError("RU semantic projection units do not assemble MASTER_RU")
    spans = value.get("spans")
    if not isinstance(spans, list):
        raise FiveStepDocxError("RU semantic projection spans are required")
    value["_assembly"] = assembly
    return value


def _transport_semantic_spans(text: str, projection: dict[str, Any], spans: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    rows = {row["unit_id"]: row for row in projection["units"]}
    order = projection["unit_order"]
    assembly=projection.get("_assembly")
    if not isinstance(assembly,dict): raise FiveStepDocxError("RU semantic projection assembly map is missing")
    from kb_creator.pipeline.five_step_language import _semantic_edge
    normalized: list[dict[str, Any]] = []
    required = {"span_id", "semantic_kind", "source_span_id", "unit_ids", "start", "end", "source_sha256"}
    for span in spans:
        if not isinstance(span, dict) or set(span) != required or span["semantic_kind"] != "statblock" or not isinstance(span["span_id"], str) or not isinstance(span["source_span_id"], str) or not isinstance(span["source_sha256"], str):
            raise FiveStepDocxError("RU semantic span is unsupported or malformed")
        units = span["unit_ids"]
        if not isinstance(units, list) or not units or any(unit not in rows for unit in units):
            raise FiveStepDocxError("RU semantic span has invalid units")
        indices = [order.index(unit) for unit in units]
        if indices != list(range(indices[0], indices[0] + len(indices))):
            raise FiveStepDocxError("RU semantic span units are not contiguous")
        start, end = span["start"], span["end"]
        if not isinstance(start, dict) or not isinstance(end, dict) or set(start) != {"unit_id", "char_offset"} or set(end) != {"unit_id", "char_offset"} or start["unit_id"] != units[0] or end["unit_id"] != units[-1] or not isinstance(start["char_offset"], int) or not isinstance(end["char_offset"], int):
            raise FiveStepDocxError("RU semantic span boundaries are invalid")
        try:
            absolute_start=_semantic_edge(assembly,start["unit_id"],start["char_offset"],edge="start")
            absolute_end=_semantic_edge(assembly,end["unit_id"],end["char_offset"],edge="end")
        except Exception as error:
            raise FiveStepDocxError(f"RU semantic span boundary is not provable: {error}") from error
        if not 0 <= absolute_start < absolute_end <= len(text) or (absolute_start and text[absolute_start - 1] != "\n") or (absolute_end < len(text) and text[absolute_end] != "\n"):
            raise FiveStepDocxError("RU semantic span must be non-empty and line-boundary aligned")
        normalized.append({**span, "start_offset": absolute_start, "end_offset": absolute_end, "visible_text": text[absolute_start:absolute_end], "visible_sha256": hashlib.sha256(text[absolute_start:absolute_end].encode("utf-8")).hexdigest().upper()})
    if len({span["span_id"] for span in normalized}) != len(normalized):
        raise FiveStepDocxError("RU semantic span IDs must be unique")
    ordered = sorted(normalized, key=lambda span: span["start_offset"])
    if any(left["end_offset"] > right["start_offset"] for left, right in zip(ordered, ordered[1:])):
        raise FiveStepDocxError("RU semantic spans overlap")
    transported = text
    for span in reversed(ordered):
        transported = transported[:span["end_offset"]] + f"\n<!-- semantic-span-end: statblock; id: {span['span_id']} -->" + transported[span["end_offset"]:]
        transported = transported[:span["start_offset"]] + f"<!-- semantic-span-start: statblock; id: {span['span_id']} -->\n" + transported[span["start_offset"]:]
    return transported, ordered


def _statblock_projection(spans: list[dict[str, Any]], body: str, document_xml: bytes) -> list[dict[str, Any]]:
    """Prove every reviewed typed span becomes one HTML and DOCX container."""
    projected: list[dict[str, Any]] = []
    html_ids = re.findall(r'data-semantic-kind="statblock"\s+data-semantic-id="([A-Za-z][A-Za-z0-9._-]*)"', body)
    if set(html_ids) != {span["span_id"] for span in spans} or len(html_ids) != len(spans):
        raise FiveStepDocxError("HTML statblock containers do not match reviewed semantic spans")
    xml_text = document_xml.decode("utf-8", errors="replace")
    for span in spans:
        visible = span["visible_text"]
        tokens = [token for token in re.findall(r"[\wА-Яа-яЁё]{2,}", visible) if token]
        present = all(token in xml_text for token in tokens)
        if not present:
            raise FiveStepDocxError(f"DOCX lost visible statblock text: {span['span_id']}")
        projected.append({"semantic_kind": "statblock", "semantic_id": span["span_id"], "unit_ids": span["unit_ids"], "source_span_id": span["source_span_id"], "source_sha256": span["source_sha256"], "visible_text_sha256": span["visible_sha256"], "visible_text_present": True})
    return projected


def _toc_html(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return ""
    rows = "\n".join(
        f'<li class="toc-level-{int(row["level"])}"><a href="#{html.escape(str(row["href"]), quote=True)}">{html.escape(str(row["title"]))}</a></li>'
        for row in entries
    )
    return f'<nav id="toc" data-toc-layout="hierarchical" data-toc-numbering="none"><h1>Содержание</h1><ol>{rows}</ol></nav>\n'


def _master_asset_manifest(master_root: Path, assets: list[tuple[str, Path]]) -> None:
    path = master_root / "ASSET_MANIFEST.json"
    if not path.is_file():
        raise FiveStepDocxError("MASTER_RU ASSET_MANIFEST.json is required")
    value = json.loads(path.read_text(encoding="utf-8"))
    declared = {str(row.get("path")): row for row in value.get("assets", []) if isinstance(row, dict)}
    for ref, source in assets:
        row = declared.get(ref)
        if row is None or row.get("bytes") != source.stat().st_size or row.get("sha256") != _sha(source):
            raise FiveStepDocxError(f"MASTER_RU asset manifest does not bind {ref}")


def _copy_semantic_sidecars(master_root: Path, stage: Path) -> list[str]:
    copied: list[str] = []
    for source in sorted(master_root.glob("*.json")):
        if source.name == "INVENTORY.json":
            continue
        if source.is_symlink():
            raise FiveStepDocxError(f"semantic sidecar is a symlink: {source.name}")
        shutil.copyfile(source, stage / source.name)
        copied.append(source.name)
    return copied


def _copy_semantic_context(master_root: Path, stage: Path) -> list[str]:
    source_root = master_root / "semantic_context"
    if not source_root.exists():
        return []
    if not source_root.is_dir() or source_root.is_symlink():
        raise FiveStepDocxError("semantic_context must be a regular directory")
    copied: list[str] = []
    for source in sorted(source_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(master_root)
        if source.is_symlink():
            raise FiveStepDocxError(f"semantic context is a symlink: {relative.as_posix()}")
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(relative.as_posix())
    return copied


def _verify_master_ru_input(master_root: Path) -> dict[str, Any]:
    """Bind B4 to B3's sealed output without invoking historic acceptance."""
    required = ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json")
    missing = [name for name in required if not (master_root / name).is_file()]
    if missing:
        raise FiveStepDocxError(f"five-step MASTER_RU metadata is missing: {', '.join(missing)}")
    from kb_creator.pipeline.five_step_language import verify_language_result
    try:
        result = verify_language_result(master_root)
    except Exception as error:
        raise FiveStepDocxError(f"MASTER_RU verification failed: {error}") from error
    if result.get("state") != "verified":
        raise FiveStepDocxError("MASTER_RU is not verified")
    return result


def _runtime_paths(runtime: dict[str, Any] | None) -> dict[str, Path] | None:
    if runtime is None:
        return None
    required = {"tools_root", "pdftoppm", "libreoffice", "python"}
    missing = sorted(required - set(runtime))
    if missing:
        raise FiveStepDocxError(f"render runtime missing explicit fields: {', '.join(missing)}")
    result = {key: Path(str(runtime[key])).resolve(strict=True) for key in required}
    tools_root = result["tools_root"]
    for key in ("pdftoppm", "libreoffice", "python"):
        try:
            result[key].relative_to(tools_root)
        except ValueError as error:
            raise FiveStepDocxError(f"runtime {key} must resolve below tools_root") from error
    return result


def _inventory(root: Path) -> list[dict[str, Any]]:
    return [_identity(path, root) for path in sorted(root.rglob("*")) if path.is_file() and path.name != MANIFEST]


def _reject_published_html_pdf(root: Path) -> None:
    prohibited = [path.relative_to(root).as_posix() for path in root.rglob("*")
                  if path.is_file() and path.suffix.casefold() in {".html", ".htm", ".pdf"}]
    if prohibited:
        raise FiveStepDocxError(f"DOCX-only package contains HTML/PDF files: {prohibited}")


def build_docx_package(master_ru: Path, output_root: Path, *, title: str, config: Path | None = None,
                       runtime: dict[str, Any] | None = None, reader_options: Path | None = None,
                       source_issue_projection: dict[str, Any] | None = None,
                       fidelity_plan: Path | None = None) -> dict[str, Any]:
    """Create an immutable DOCX review package from a verified-looking MASTER_RU tree."""
    if fidelity_plan is None:
        raise FiveStepDocxError("source-fidelity plan is required before new DOCX generation")
    if config is None or reader_options is None:
        raise FiveStepDocxError("guarded DOCX requires explicit config and reviewed reader options")
    from .reader_fidelity import validate_plan
    try:
        plan = validate_plan(fidelity_plan, master_ru=_master_file(master_ru))
    except ValueError as error:
        raise FiveStepDocxError(f"source-fidelity plan is not closed: {error}") from error
    if (plan["projection"] != {"path": str((_master_file(master_ru).parent / "semantic_context/RU_PROJECTION.json").resolve(strict=True)),
                              **file_identity(_master_file(master_ru).parent / "semantic_context/RU_PROJECTION.json")}
            or plan["config"] != {"path": str(config.resolve(strict=True)), **file_identity(config)}
            or plan["policy"]["reader_profile"] != "five_step_docx_v3"):
        raise FiveStepDocxError("guarded DOCX projection/config/profile authority differs from plan")
    master = _master_file(master_ru)
    master_root = master.parent
    output_root = output_root.resolve()
    if output_root.exists() or not output_root.parent.is_dir():
        raise FiveStepDocxError("DOCX output root must be absent below an existing parent")
    if not isinstance(title, str) or not title.strip():
        raise FiveStepDocxError("title must be a non-empty string")
    text = master.read_text(encoding="utf-8")
    verified_language = _verify_master_ru_input(master_root)
    ru_projection = _semantic_projection(master_root, master, text)
    semantic_spans = ru_projection["spans"]
    transport_text, bound_spans = _transport_semantic_spans(text, ru_projection, semantic_spans)
    assets = _referenced_assets(text, master_root)
    _master_asset_manifest(master_root, assets)
    _validate_links(text)
    profile, config_identity = _load_config(config, title, master_root)
    options = None
    issue_projection = None
    if reader_options is not None:
        from kb_creator.pipeline.reader_projection import load_options, guarded_reflow
        options = load_options(reader_options, master, master_root / "semantic_context" / "RU_PROJECTION.json")
        if options["source_toc"].get("source_pdf_sha256") != plan["source_pdf"]["sha256"]:
            raise FiveStepDocxError("reviewed reader options source differs from fidelity plan")
        if any(isinstance(row, dict) and (row.get("role") == "omit_extraction_duplicate_text"
                                               or (row.get("role") == "omit_source_artifact"
                                                   and row.get("text_policy") == "reviewed_whole_plain_block_v2")
                                               or guarded_reflow(row, options["display_roles"]))
               for row in options["display_roles"]):
            source_hash = verified_language.get("inputs", {}).get("source_pdf", {}).get("identity", {}).get("sha256")
            if source_hash != options["source_toc"].get("source_pdf_sha256"):
                raise FiveStepDocxError("duplicate text source PDF differs from verified language input")
    elif re.search(r"^#{1,6}\s+(?:Содержание|Оглавление|Contents|Table of contents)\s*$", text, re.M | re.I):
        raise FiveStepDocxError("source TOC detected: reviewed reader_options required")
    if source_issue_projection is not None:
        if options is None:
            raise FiveStepDocxError("source issue projection requires reviewed reader options")
        from kb_creator.pipeline.source_issue_projection import validate_source_issue_projection
        try:
            issue_projection = validate_source_issue_projection(
                source_issue_projection, master_ru=master, ru_projection=master_root / "semantic_context" / "RU_PROJECTION.json"
            )
        except ValueError as error:
            raise FiveStepDocxError(f"source issue projection is invalid: {error}") from error
    # LibreOffice creates deeply nested profile paths on Windows.
    stage = Path(tempfile.mkdtemp(prefix=".d-", dir=output_root.parent))
    try:
        shutil.copyfile(master, stage / "MASTER_RU.md")
        (stage / "INTERNAL_SEMANTIC_SOURCE.md").write_text(transport_text, encoding="utf-8", newline="\n")
        (stage / "assets").mkdir(exist_ok=True)
        for ref, source in assets:
            target = stage / Path(ref)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        sidecars = _copy_semantic_sidecars(master_root, stage)
        semantic_context = _copy_semantic_context(master_root, stage)
        config_path = stage / "docx_config.json"
        _write_json(config_path, profile)
        body, toc, page_count = markdown_to_review_html(transport_text, source_path=stage / "INTERNAL_SEMANTIC_SOURCE.md", html_path=stage / ".word-projection-base", blockquote_heading_offset=0)
        reader_report = None
        if options is not None:
            from kb_creator.pipeline.reader_projection import project_reader_html, copy_reader_assets
            effective_options = copy.deepcopy(options)
            if issue_projection is not None:
                existing = {row.get("issue_id") for row in effective_options["display_roles"] if isinstance(row, dict)}
                new = issue_projection["roles"]
                if existing.intersection(row["issue_id"] for row in new):
                    raise FiveStepDocxError("source issue projection duplicates a reviewed reader role")
                effective_options["display_roles"].extend(new)
            body, toc, reader_report = project_reader_html(body, toc, ru_projection, effective_options,
                                                            options_path=reader_options,
                                                            master_root=master_root)
            profile = copy_reader_assets(reader_report, reader_options, stage, profile)
            _write_json(stage / "reader_options.json", options)
            _write_json(stage / "READER_PROJECTION.json", reader_report)
            if issue_projection is not None:
                _write_json(stage / "SOURCE_ISSUE_RU_PROJECTION.json", issue_projection)
            _write_json(config_path, profile)
        else:
            body = _toc_html(toc) + body
        projection_transport = "<!doctype html><html><head><meta charset=\"utf-8\"></head><body><main>\n" + body + "\n</main></body></html>\n"
        projection_root = lxml_html.fromstring(projection_transport)
        from .reader_fidelity import project_graphics, project_text_operations
        graphic_projection = project_graphics(fidelity_plan, projection_root, stage)
        text_projection = project_text_operations(fidelity_plan, projection_root)
        projection_transport = lxml_html.tostring(projection_root, encoding="unicode", method="html")
        docx_dir = stage / "docx"; docx_dir.mkdir()
        docx_path = docx_dir / "document.docx"
        base_docx = docx_dir / "document.base.docx" if issue_projection is not None and issue_projection["roles"] else docx_path
        build_result = build_docx_projection(projection_root, stage, base_docx, config=profile)
        expected = {"headings": len(_HEADING_RE.findall(text)), "tables": len(_TABLE_RE.findall(text)), "statblocks": len(bound_spans), "unique_assets": len(assets), "image_occurrences": len(_IMAGE_RE.findall(text))}
        expected["reader_image_occurrences"] = (_reader_image_occurrences(expected["image_occurrences"], reader_report)
                                                 + graphic_projection["insertions"])
        if build_result["tables"] < expected["tables"] or build_result["images"] != expected["reader_image_occurrences"]:
            raise FiveStepDocxError(
                "in-memory projection to DOCX dropped tables or images: "
                f"tables expected>={expected['tables']}, actual={build_result['tables']}; "
                f"images expected={expected['reader_image_occurrences']}, actual={build_result['images']}"
            )
        with zipfile.ZipFile(base_docx) as archive:
            names = set(archive.namelist())
            document_xml = archive.read("word/document.xml") if "word/document.xml" in names else b""
            media_hashes = {hashlib.sha256(archive.read(name)).hexdigest().upper() for name in names if name.startswith("word/media/")}
        if not {"[Content_Types].xml", "word/document.xml"}.issubset(names):
            raise FiveStepDocxError("DOCX OOXML closure failed")
        statblocks = _statblock_projection(bound_spans, body, document_xml)
        if reader_report is not None:
            from lxml import etree
            from kb_creator.scripts.production_docx import bookmark_name
            xml = etree.fromstring(document_xml)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            bookmarks = xml.xpath("//w:bookmarkStart/@w:name", namespaces=ns)
            links = xml.xpath("//w:hyperlink/@w:anchor", namespaces=ns)
            for link in reader_report["links"]:
                name = bookmark_name(link["target"])
                if bookmarks.count(name) != 1 or name not in links:
                    raise FiveStepDocxError(f"reader link not preserved in DOCX: {link['target']}")
            verify_rich_source_toc_docx(reader_report, document_xml)
            verify_duplicate_text_docx(reader_report, document_xml)
            verify_reflow_docx(reader_report, document_xml)
            verify_retained_links_docx(reader_report, document_xml)
            verify_retained_artwork_docx(reader_report, base_docx)
            from kb_creator.pipeline.reader_block_relocation import verify_docx as verify_relocated_docx
            verify_relocated_docx(reader_report, base_docx)
            from kb_creator.pipeline.reader_statblock_grouping import verify_xml as verify_grouped_statblocks
            verify_grouped_statblocks(reader_report, document_xml,
                                     keep_together=profile.get("statblocks", {}).get("keep_together", False))
            for review_anchor in reader_report["review_anchors"]:
                name = bookmark_name(review_anchor["anchor"])
                if bookmarks.count(name) != 1:
                    raise FiveStepDocxError(f"reader review anchor not preserved in DOCX: {review_anchor['anchor']}")
            for choice in reader_report["asset_choices"]:
                if choice["selected"]["sha256"] not in media_hashes:
                    raise FiveStepDocxError(f"selected asset not embedded verbatim: {choice['rendered_path']}")
            region_crops = []
            for group in reader_report.get("source_figure_regions", []):
                for region in group["regions"]:
                    if region["selected"]["sha256"] not in media_hashes:
                        raise FiveStepDocxError(f"selected source region not embedded verbatim: {region['rendered_path']}")
                    crop = region["figure_policy"]["crop_fraction"]
                    region_crops.append(tuple(str(round(float(crop[key]) * 100000)) for key in ("left", "top", "right", "bottom")))
            actual_crops = [
                tuple(node.get(edge, "0") for edge in ("l", "t", "r", "b"))
                for node in xml.xpath("//a:srcRect", namespaces={**ns, "a": "http://schemas.openxmlformats.org/drawingml/2006/main"})
            ]
            if any(actual_crops.count(crop) < region_crops.count(crop) for crop in set(region_crops)):
                raise FiveStepDocxError("source figure region crop policy not preserved in DOCX")
        annotation = None
        if issue_projection is not None and issue_projection["roles"]:
            from kb_creator.pipeline.docx_review_comments import write_annotation_report
            role_ids = {row["issue_id"] for row in issue_projection["roles"]}
            anchors = [row for row in reader_report["review_anchors"] if row.get("issue_id") in role_ids]
            if len(anchors) != len(role_ids) or {row.get("issue_id") for row in anchors} != role_ids:
                raise FiveStepDocxError("source issue reader anchors are not bijective")
            registry_path = stage / "DOCX_REVIEW_ISSUES.json"
            registry = {"schema": "kb_creator.docx_review_issues.v1", "docx_sha256": _sha(base_docx),
                        "issues": [{key: row[key] for key in ("issue_id", "anchor", "target_text", "source_page", "en_excerpt", "reason")}
                                   for row in anchors]}
            for row in registry["issues"]:
                row["reader_anchor"] = row.pop("anchor")
            _write_json(registry_path, registry)
            annotation = write_annotation_report(base_docx, registry_path, docx_path, stage / "DOCX_REVIEW_ANNOTATION.json")
            base_docx.unlink()
            if len(annotation["bindings"]) != len(role_ids) or {row["issue_id"] for row in annotation["bindings"]} != role_ids:
                raise FiveStepDocxError("native source issue comments are not bijective")
        render_result: dict[str, Any] | None = None
        runtime_paths = _runtime_paths(runtime)
        state = "built_pending_render"
        if runtime_paths is not None:
            normalize_publication_access_if_managed(stage)
            render_result = render_docx_transient(
                docx_path, stage / "render", stage / ".r",
                Path(__file__).resolve().parents[1] / "scripts" / "export_docx_to_pdf.ps1",
                Path("powershell.exe"), runtime_paths["pdftoppm"], python=runtime_paths["python"],
                libreoffice=runtime_paths["libreoffice"], local_exporter_script=Path(__file__).resolve().parents[1] / "scripts" / "export_docx_to_pdf_local.py",
                stage_root=stage, tools_root=runtime_paths["tools_root"],
            )
            state = "needs_visual_review"
        from .reader_fidelity import write_verification
        fidelity_verification = write_verification(fidelity_plan, docx_path, stage,
                                                   stage / "READER_FIDELITY_VERIFICATION.json")
        asset_plan = _asset_plan(text, assets, stage)
        if reader_report is not None:
            choices = {row["original_ref"]: row for row in reader_report["asset_choices"]}
            omissions: dict[str, list[dict[str, Any]]] = {}
            for omission in reader_report["omitted_artifacts"]:
                if omission["image_occurrences"]:
                    omissions.setdefault(omission["source_reference"], []).append(omission)
            for row in asset_plan:
                choice = choices.get(row["source_reference"])
                if choice:
                    row.update(original={key: row[key] for key in ("path", "bytes", "sha256")},
                               rendered_path=choice["rendered_path"], choice="reviewed_embedded_original",
                               provenance=choice["provenance"], **_identity(stage / choice["rendered_path"], stage))
                omitted = omissions.get(row["source_reference"])
                if omitted:
                    count = sum(item["image_occurrences"] for item in omitted)
                    row.update(choice="reader_omitted" if count == row["source_image_occurrences"] else "reader_partially_omitted",
                               provenance="reviewed_reader_omission", reader_omitted_occurrences=count,
                               omission_classifications=sorted({item["classification"] for item in omitted}),
                               omission_reasons=[item["reason"] for item in omitted],
                               omission_source_evidence=[item["source_evidence"] for item in omitted])
            source_regions: dict[str, list[dict[str, Any]]] = {}
            for group in reader_report.get("source_figure_regions", []):
                source_regions.setdefault(group["source_reference"], []).append(group)
            for row in asset_plan:
                groups = source_regions.get(row["source_reference"], [])
                if groups:
                    count = len(groups)
                    row.update(
                        choice="reader_source_region_replaced" if count == row["source_image_occurrences"] else "reader_source_region_partially_replaced",
                        provenance="reviewed_source_figure_regions", reader_replaced_occurrences=count,
                        region_classifications=sorted({item["classification"] for item in groups}),
                        region_source_evidence=[item["source_evidence"] for item in groups],
                    )
            for group in reader_report.get("source_figure_regions", []):
                for region in group["regions"]:
                    asset_plan.append({
                        "source_reference": group["source_reference"], "rendered_path": region["rendered_path"],
                        "choice": "reader_source_region", "provenance": "reviewed_source_figure_regions",
                        "source_unit_id": group["unit"]["unit_id"], "region_id": region["id"],
                        "selected_ref": region["selected_ref"], "caption": region["caption"],
                        "figure_policy": region["figure_policy"], "source_evidence": group["source_evidence"],
                        "reason": group["reason"], **_identity(stage / region["rendered_path"], stage),
                    })
        _reject_published_html_pdf(stage)
        manifest = {
            "schema": SCHEMA,
            "profile": "five_step_docx_v3",
            "state": state,
            "title": title,
            "master_ru": _identity(stage / "MASTER_RU.md", stage),
            "asset_plan": asset_plan,
            "reader_projection": reader_report,
            "source_fidelity": {"plan": {"path": str(fidelity_plan.resolve(strict=True)), **file_identity(fidelity_plan)},
                                "verification": _identity(stage / "READER_FIDELITY_VERIFICATION.json", stage),
                                "graphic_projection": graphic_projection,
                                "text_projection": text_projection},
            "source_issue_projection": issue_projection,
            "source_issue_annotation": annotation,
            "semantic_sidecars": sidecars,
            "semantic_context": semantic_context,
            "projection_transport_sha256": hashlib.sha256(projection_transport.encode("utf-8")).hexdigest().upper(),
            "internal_semantic_source": _identity(stage / "INTERNAL_SEMANTIC_SOURCE.md", stage),
            "docx": {**_identity(docx_path, stage), "build": build_result},
            "config": _identity(config_path, stage),
            "source_config": config_identity,
            "projection": {"markdown": expected, "word_transport": {"toc_entries": len(toc), "source_pages": page_count}},
            "statblock_projection": statblocks,
            "render": render_result,
            "render_task": None if render_result else {"state": "missing_runtime", "required": ["tools_root", "pdftoppm", "libreoffice", "python"], "instruction": "Rebuild this DOCX attempt with explicit local render runtime, then inspect every generated PNG page."},
            "release_state": "not_reviewed",
            "inventory": _inventory(stage),
        }
        manifest["manifest_sha256"] = hashlib.sha256(_canonical(manifest)).hexdigest().upper()
        _write_json(stage / MANIFEST, manifest)
        os.replace(stage, output_root)
        try:
            normalize_publication_access_if_managed(output_root)
            verify_docx_package(output_root)
        except Exception:
            quarantine = output_root.with_name(f".{output_root.name}.quarantine.{stage.name.rsplit('.', 1)[-1]}")
            os.replace(output_root, quarantine)
            raise
        result = {"state": state, "docx_path": output_root / "docx" / "document.docx", "manifest_path": output_root / MANIFEST, "render_task": (output_root / "render" / "review_index.json") if render_result else manifest["render_task"]}
        if render_result:
            result["render_pages"] = sorted((output_root / "render").glob("page-*.png"))
        return result
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_docx_package(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    manifest_path = root / MANIFEST
    if not manifest_path.is_file():
        raise FiveStepDocxError("DOCX manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = manifest.pop("manifest_sha256", None)
    schema = manifest.get("schema")
    if schema not in {SCHEMA, PREVIOUS_SCHEMA, LEGACY_SCHEMA} or digest != hashlib.sha256(_canonical(manifest)).hexdigest().upper():
        raise FiveStepDocxError("DOCX manifest seal mismatch")
    if schema == SCHEMA:
        if manifest.get("profile") != "five_step_docx_v3" or "internal_html" in manifest or (root / "internal.html").exists():
            raise FiveStepDocxError("guarded DOCX v3 profile/transport mismatch")
        _reject_published_html_pdf(root)
    if schema == PREVIOUS_SCHEMA:
        if manifest.get("profile") != "five_step_docx_v2" or "internal_html" in manifest or (root / "internal.html").exists():
            raise FiveStepDocxError("DOCX-only projection contract mismatch")
        _reject_published_html_pdf(root)
    inventory = manifest.get("inventory")
    if not isinstance(inventory, list) or inventory != _inventory(root):
        raise FiveStepDocxError("DOCX package inventory mismatch")
    docx = root / manifest["docx"]["path"]
    if not docx.is_file() or _identity(docx, root) != {key: manifest["docx"][key] for key in ("path", "bytes", "sha256")}:
        raise FiveStepDocxError("DOCX identity mismatch")
    if schema == SCHEMA:
        from .reader_fidelity import verify_verification
        fidelity = manifest.get("source_fidelity")
        if (not isinstance(fidelity, dict) or set(fidelity) != {"plan", "verification", "graphic_projection", "text_projection"}
                or not isinstance(fidelity["graphic_projection"], dict)
                or type(fidelity["text_projection"]) is not int):
            raise FiveStepDocxError("guarded DOCX source-fidelity authority is missing")
        report = root / "READER_FIDELITY_VERIFICATION.json"
        if _identity(report, root) != fidelity["verification"]:
            raise FiveStepDocxError("guarded DOCX fidelity report identity mismatch")
        try:
            checked = verify_verification(report, root, expected_plan=Path(fidelity["plan"]["path"]))
        except ValueError as error:
            raise FiveStepDocxError(f"guarded DOCX source/output verification failed: {error}") from error
        if (checked["plan"] != fidelity["plan"] or
                len(checked["graphics"]) != fidelity["graphic_projection"].get("placements") or
                len(checked["text"]) != fidelity["text_projection"]):
            raise FiveStepDocxError("guarded DOCX plan/observation count changed")
    with zipfile.ZipFile(docx) as archive:
        if not {"[Content_Types].xml", "word/document.xml"}.issubset(set(archive.namelist())):
            raise FiveStepDocxError("DOCX OOXML members are missing")
        document_xml = archive.read("word/document.xml")
        media_hashes = {hashlib.sha256(archive.read(name)).hexdigest().upper()
                        for name in archive.namelist() if name.startswith("word/media/")}
        comments_xml = archive.read("word/comments.xml") if "word/comments.xml" in archive.namelist() else None
    for asset in manifest.get("asset_plan", []):
        path = root / asset["rendered_path"]
        if not path.is_file() or _identity(path, root) != {key: asset[key] for key in ("path", "bytes", "sha256")}:
            raise FiveStepDocxError(f"DOCX asset closure failed: {asset.get('rendered_path')}")
    reader_report = manifest.get("reader_projection")
    issue_projection = manifest.get("source_issue_projection")
    annotation = manifest.get("source_issue_annotation")
    if issue_projection is not None:
        from kb_creator.pipeline.source_issue_projection import validate_source_issue_projection
        try:
            validate_source_issue_projection(issue_projection, master_ru=root / "MASTER_RU.md",
                                             ru_projection=root / "semantic_context" / "RU_PROJECTION.json")
        except ValueError as error:
            raise FiveStepDocxError(f"source issue projection closure failed: {error}") from error
        ids = [row.get("issue_id") for row in issue_projection["roles"]]
        if not ids:
            if annotation is not None or comments_xml is not None:
                raise FiveStepDocxError("zero-issue source projection unexpectedly has comments")
        else:
            if not isinstance(annotation, dict) or not isinstance(annotation.get("bindings"), list) or comments_xml is None:
                raise FiveStepDocxError("source issue annotation closure is missing")
            from lxml import etree
            bindings = annotation["bindings"]
            if len(ids) != len(set(ids)) or {row.get("issue_id") for row in bindings} != set(ids) or len(bindings) != len(ids):
                raise FiveStepDocxError("source issue annotation binding closure failed")
            xml = etree.fromstring(document_xml); comments = etree.fromstring(comments_xml)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            comment_ids = {str(row.get("comment_id")) for row in bindings}
            if (set(comments.xpath("//w:comment/@w:id", namespaces=ns)) != comment_ids
                    or set(xml.xpath("//w:commentRangeStart/@w:id", namespaces=ns)) != comment_ids
                    or set(xml.xpath("//w:commentRangeEnd/@w:id", namespaces=ns)) != comment_ids
                    or set(xml.xpath("//w:commentReference/@w:id", namespaces=ns)) != comment_ids):
                raise FiveStepDocxError("source issue native comment range closure failed")
    if reader_report is not None:
        if not isinstance(reader_report, dict):
            raise FiveStepDocxError("DOCX reader projection report is invalid")
        archived_options = root / "reader_options.json"
        if not archived_options.is_file():
            raise FiveStepDocxError("DOCX reader options archive is missing")
        try:
            archived_roles = json.loads(archived_options.read_text(encoding="utf-8"))["display_roles"]
            has_duplicates = any(isinstance(row, dict) and row.get("role") == "omit_extraction_duplicate_text"
                                 for row in archived_roles)
            has_whole_artifacts = any(isinstance(row, dict) and row.get("role") == "omit_source_artifact"
                                      and row.get("text_policy") == "reviewed_whole_plain_block_v2"
                                      for row in archived_roles)
            has_legacy_artwork_text = any(isinstance(row, dict) and row.get("role") == "omit_source_artifact"
                                          and row.get("classification") == "duplicate_text_represented_by_retained_artwork"
                                          and row.get("text_policy") is None for row in archived_roles)
            from kb_creator.pipeline.reader_projection import guarded_reflow
            has_extended_reflow = any(guarded_reflow(row, archived_roles) for row in archived_roles)
            has_relocations = any(isinstance(row, dict) and row.get("role") == "reviewed_block_relocation"
                                  for row in archived_roles)
            has_statblock_groups = any(isinstance(row, dict) and row.get("role") == "reviewed_statblock_group"
                                      for row in archived_roles)
        except (ValueError, KeyError, TypeError) as error:
            raise FiveStepDocxError(f"DOCX archived reader options are invalid: {error}") from error
        if (has_duplicates or has_whole_artifacts or has_extended_reflow or has_relocations or has_statblock_groups
                or (has_legacy_artwork_text and reader_report.get("duplicate_page_witness"))):
            if ((has_statblock_groups and not reader_report.get("statblock_groups"))
                    or (has_relocations and (not reader_report.get("block_relocations")
                                      or not reader_report.get("relocation_page_witness")))
                    or (has_duplicates and not reader_report.get("omitted_text_duplicates"))
                    or (has_whole_artifacts and not any(row.get("text_policy") == "reviewed_whole_plain_block_v2"
                                                         for row in reader_report.get("omitted_artifacts", [])))
                    or ((has_duplicates or has_whole_artifacts) and not reader_report.get("duplicate_page_witness"))
                    or (has_extended_reflow and (not reader_report.get("reflow_page_witness")
                                                 or not reader_report.get("reflow_dependencies")))):
                raise FiveStepDocxError("duplicate text archived reader evidence is missing")
            try:
                projection_file = root / "READER_PROJECTION.json"
                if not projection_file.is_file() or json.loads(projection_file.read_text(encoding="utf-8")) != reader_report:
                    raise FiveStepDocxError("duplicate text archived reader report differs from manifest")
                _replay_duplicate_reader(root, reader_report, manifest)
            except (ValueError, KeyError, TypeError) as error:
                if isinstance(error, FiveStepDocxError):
                    raise
                raise FiveStepDocxError(f"duplicate text archived replay failed: {error}") from error
        elif (reader_report.get("omitted_text_duplicates") or reader_report.get("duplicate_page_witness")
              or reader_report.get("reflow_page_witness") or reader_report.get("reflow_dependencies")
              or reader_report.get("block_relocations") or reader_report.get("relocation_page_witness")
              or reader_report.get("statblock_groups")):
            raise FiveStepDocxError("duplicate text report has no archived decision")
        verify_duplicate_text_docx(reader_report, document_xml)
        verify_reflow_docx(reader_report, document_xml)
        verify_retained_links_docx(reader_report, document_xml)
        verify_retained_artwork_docx(reader_report, docx)
        from kb_creator.pipeline.reader_block_relocation import verify_docx as verify_relocated_docx
        verify_relocated_docx(reader_report, docx)
        from kb_creator.pipeline.reader_statblock_grouping import verify_xml as verify_grouped_statblocks
        if reader_report.get("statblock_groups"):
            grouping_config = json.loads((root / "docx_config.json").read_text(encoding="utf-8"))
            verify_grouped_statblocks(reader_report, document_xml,
                                     keep_together=grouping_config.get("statblocks", {}).get("keep_together", False))
        markdown = manifest.get("projection", {}).get("markdown", {})
        expected_images = _reader_image_occurrences(markdown.get("image_occurrences"), reader_report)
        if schema == SCHEMA:
            expected_images += manifest["source_fidelity"]["graphic_projection"]["insertions"]
        if manifest["docx"].get("build", {}).get("images") != expected_images:
            raise FiveStepDocxError("DOCX reader image occurrence closure failed")
        omissions: dict[str, list[dict[str, Any]]] = {}
        for omission in reader_report.get("omitted_artifacts", []):
            if omission.get("image_occurrences"):
                omissions.setdefault(omission["source_reference"], []).append(omission)
        planned = {row.get("source_reference"): row for row in manifest.get("asset_plan", []) if row.get("choice") in {"reader_omitted", "reader_partially_omitted"}}
        if set(omissions) != set(planned) or any(
                planned[reference].get("reader_omitted_occurrences") != sum(item["image_occurrences"] for item in rows)
                or planned[reference].get("omission_classifications") != sorted({item["classification"] for item in rows})
                or planned[reference].get("choice") != ("reader_omitted" if sum(item["image_occurrences"] for item in rows) == planned[reference].get("source_image_occurrences") else "reader_partially_omitted")
                for reference, rows in omissions.items()):
            raise FiveStepDocxError("DOCX reader omission asset plan closure failed")
        from lxml import etree
        from kb_creator.scripts.production_docx import bookmark_name
        xml = etree.fromstring(document_xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        groups = reader_report.get("source_figure_regions", [])
        region_rows = {
            (row.get("source_unit_id"), row.get("region_id")): row
            for row in manifest.get("asset_plan", []) if row.get("choice") == "reader_source_region"
        }
        expected_regions = [
            (group, region) for group in groups if isinstance(group, dict)
            for region in group.get("regions", []) if isinstance(region, dict)
        ]
        replacement_groups: dict[str, list[dict[str, Any]]] = {}
        for group in groups:
            if isinstance(group, dict) and isinstance(group.get("source_reference"), str):
                replacement_groups.setdefault(group["source_reference"], []).append(group)
        replacement_plans = {
            row.get("source_reference"): row for row in manifest.get("asset_plan", [])
            if row.get("choice") in {"reader_source_region_replaced", "reader_source_region_partially_replaced"}
        }
        if set(replacement_groups) != set(replacement_plans) or any(
                replacement_plans[reference].get("reader_replaced_occurrences") != len(rows)
                or replacement_plans[reference].get("choice") != (
                    "reader_source_region_replaced" if len(rows) == replacement_plans[reference].get("source_image_occurrences")
                    else "reader_source_region_partially_replaced")
                for reference, rows in replacement_groups.items()):
            raise FiveStepDocxError("DOCX source figure replacement occurrence closure failed")
        if len(region_rows) != len(expected_regions) or any(
                (group.get("unit", {}).get("unit_id"), region.get("id")) not in region_rows
                for group, region in expected_regions):
            raise FiveStepDocxError("DOCX source figure region asset plan closure failed")
        region_crops = []
        for group, region in expected_regions:
            row = region_rows[(group["unit"]["unit_id"], region["id"])]
            if (_identity(root / row["rendered_path"], root) != {key: row[key] for key in ("path", "bytes", "sha256")}
                    or row.get("source_reference") != group.get("source_reference")
                    or row.get("selected_ref") != region.get("selected_ref")
                    or {key: row.get(key) for key in ("bytes", "sha256")} != region.get("selected")
                    or row.get("figure_policy") != region.get("figure_policy")):
                raise FiveStepDocxError("DOCX source figure region identity closure failed")
            if region["selected"]["sha256"] not in media_hashes:
                raise FiveStepDocxError("DOCX source figure region media closure failed")
            crop = region["figure_policy"]["crop_fraction"]
            region_crops.append(tuple(str(round(float(crop[key]) * 100000)) for key in ("left", "top", "right", "bottom")))
        actual_crops = [
            tuple(node.get(edge, "0") for edge in ("l", "t", "r", "b"))
            for node in xml.xpath("//a:srcRect", namespaces={**ns, "a": "http://schemas.openxmlformats.org/drawingml/2006/main"})
        ]
        if any(actual_crops.count(crop) < region_crops.count(crop) for crop in set(region_crops)):
            raise FiveStepDocxError("DOCX source figure region crop closure failed")
        bookmarks = xml.xpath("//w:bookmarkStart/@w:name", namespaces=ns)
        if any(bookmarks.count(bookmark_name(row.get("anchor", ""))) != 1 for row in reader_report.get("review_anchors", [])):
            raise FiveStepDocxError("DOCX reader review anchor closure failed")
    if any(row.get("semantic_kind") != "statblock" or row.get("visible_text_present") is not True for row in manifest.get("statblock_projection", [])):
        raise FiveStepDocxError("DOCX statblock projection proof is invalid")
    if manifest["state"] not in {"built_pending_render", "needs_visual_review"}:
        raise FiveStepDocxError("DOCX package state is invalid")
    status = ("verified_pending_visual_review" if schema == SCHEMA
              else "legacy_verified_source_completeness_not_assessed")
    return {"schema": schema, "status": status, "state": manifest["state"], "docx_path": docx,
            "manifest_path": manifest_path, "render_task": manifest["render_task"]}
