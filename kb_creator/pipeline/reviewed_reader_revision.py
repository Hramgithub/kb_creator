"""Hash-bound, artifact-preserving successors for reviewed DOCX and HTML readers.

This route starts from reviewed artifacts. It is not a reconstruction or replay of
the source-language and translation masters. A complete, independent graphic
ledger is mandatory even when both reader formats already agree with each other.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import tempfile
import zipfile
from collections import Counter
from copy import deepcopy
from pathlib import Path, PurePosixPath

from lxml import etree, html
from PIL import Image

from kb_creator.pipeline.docx_review_comments import _StyleVisibility


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
NS = {"w": W[1:-1], "r": R[1:-1], "a": A[1:-1], "wp": WP[1:-1], "pic": PIC[1:-1]}
IMAGE_REL = R[1:-1] + "/image"
EMU_PER_INCH = 914400


class RevisionError(ValueError):
    """An identity, binding, coverage or conservation requirement failed."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _check_hash(actual: str, declared: object, label: str) -> None:
    if not isinstance(declared, str) or actual != declared.upper():
        raise RevisionError(f"{label} SHA-256 mismatch")


def _safe_relative(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if (not name or "\\" in name or path.is_absolute() or ".." in path.parts
            or "." in path.parts or ":" in name or path.parts[0] != "assets"
            or str(path) != name or len(path.parts) < 2):
        raise RevisionError(f"unsafe asset path: {name!r}")
    return path


def _xml(data: bytes, label: str) -> etree._Element:
    try:
        return etree.fromstring(data)
    except etree.XMLSyntaxError as exc:
        raise RevisionError(f"invalid {label}: {exc}") from exc


def _serial(root: etree._Element) -> bytes:
    return etree.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)


def _zip_parts(path: Path) -> dict[str, bytes]:
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise RevisionError("DOCX archive is corrupt")
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise RevisionError("DOCX has duplicate member names")
            return {name: archive.read(name) for name in names}
    except zipfile.BadZipFile as exc:
        raise RevisionError("DOCX is not a valid ZIP") from exc


def _bookmark(root: etree._Element, name: str) -> etree._Element:
    matches = root.xpath(".//w:bookmarkStart[@w:name=$name]", namespaces=NS, name=name)
    if len(matches) != 1:
        raise RevisionError(f"bookmark must occur exactly once: {name}")
    paragraphs = matches[0].xpath("ancestor::w:p[1]", namespaces=NS)
    if len(paragraphs) != 1:
        raise RevisionError(f"bookmark has no paragraph: {name}")
    return paragraphs[0]


def _html_anchor(root: etree._Element, anchor: str) -> etree._Element:
    matches = root.xpath("//*[@id=$anchor]", anchor=anchor)
    if len(matches) != 1:
        raise RevisionError(f"HTML anchor must occur exactly once: {anchor}")
    return matches[0]


def _paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def _plain_text_runs(paragraph: etree._Element, visibility: _StyleVisibility) -> list[etree._Element]:
    """Accept only text runs and inert bookmark/comment markers in edit targets."""
    markers = {W + x for x in ("bookmarkStart", "bookmarkEnd", "commentRangeStart", "commentRangeEnd")}
    runs = []
    for child in paragraph:
        if child.tag == W + "pPr" or child.tag in markers:
            continue
        children = [child] if child.tag == W + "r" else list(child) if child.tag == W + "hyperlink" else []
        if not children:
            raise RevisionError("unsupported construct in text paragraph")
        for run in children:
            if run.tag != W + "r":
                raise RevisionError("unsupported hyperlink topology")
            content = [c for c in run if c.tag != W + "rPr"]
            if not content or any(c.tag not in {W + "t", W + "commentReference"} for c in content):
                raise RevisionError("unsupported run topology")
            if any(c.tag == W + "commentReference" for c in content):
                if any(c.tag == W + "t" for c in content):
                    raise RevisionError("mixed comment reference and text run")
                continue
            if visibility.hidden(paragraph, run):
                raise RevisionError("hidden text cannot be edited")
            runs.append(run)
    return runs


def _replace_word_text(paragraph: etree._Element, expected: str, target: str,
                       replacement: str, visibility: _StyleVisibility) -> None:
    runs = _plain_text_runs(paragraph, visibility)
    if _paragraph_text(paragraph) != expected or expected.count(target) != 1:
        raise RevisionError("changed or ambiguous Word text context")
    hits = [(t, t.text or "") for run in runs for t in run.findall(W + "t") if target in (t.text or "")]
    if len(hits) != 1:
        raise RevisionError("text target crosses runs or is ambiguous")
    node, value = hits[0]
    node.text = value.replace(target, replacement, 1)
    if node.text.startswith(" ") or node.text.endswith(" "):
        node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def _replace_html_text(element: etree._Element, expected: str, target: str, replacement: str) -> tuple[str, str]:
    if "".join(element.itertext()) != expected or expected.count(target) != 1:
        raise RevisionError("changed or ambiguous HTML text context")
    slots = []
    for node in element.iter():
        if node.text is not None and target in node.text:
            slots.append((node, "text"))
        if node.tail is not None and target in node.tail:
            slots.append((node, "tail"))
    if len(slots) != 1:
        raise RevisionError("HTML target crosses text nodes or is ambiguous")
    node, field = slots[0]
    before = getattr(node, field)
    after = before.replace(target, replacement, 1)
    setattr(node, field, after)
    return before, after


def _text_targets(op, sid, bounds, document, page):
    span = bounds[sid]
    selector = op.get("selector")
    if selector is None:
        return _bookmark(document, span["word_bookmark"]), _html_anchor(page, span["html_anchor"])
    expected = op.get("expected_text", "")
    word_expected = op.get("word_expected_text", expected)
    html_expected = op.get("html_expected_text", expected)
    _check_hash(_sha(word_expected.encode("utf-8")), op.get("word_expected_sha256", op.get("expected_text_sha256")), "expected Word text")
    _check_hash(_sha(html_expected.encode("utf-8")), op.get("html_expected_sha256", op.get("expected_text_sha256")), "expected HTML text")
    word_rule, html_rule = selector.get("word", {}), selector.get("html", {})
    if word_rule.get("kind") != "exact_paragraph" or html_rule.get("kind") != "exact_element":
        raise RevisionError("unsupported exact text selector")
    word_paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    word_matches = [p for p in word_paragraphs[span["word_start"]:span["word_end"]]
                    if _paragraph_text(p) == word_expected]
    nodes = list(page.iter())
    tag = html_rule.get("tag")
    if tag not in {"p", "td", "th", "li"}:
        raise RevisionError("exact HTML selector requires p, td, th or li")
    html_matches = [node for node in nodes[span["html_start"]:span["html_end"]]
                    if node.tag == tag and "".join(node.itertext()) == html_expected]
    word_ordinal, html_ordinal = word_rule.get("ordinal"), html_rule.get("ordinal")
    if (not isinstance(word_ordinal, int) or not isinstance(html_ordinal, int)
            or word_ordinal < 0 or html_ordinal < 0
            or len(word_matches) != word_rule.get("expected_matches")
            or len(html_matches) != html_rule.get("expected_matches")
            or word_ordinal >= len(word_matches) or html_ordinal >= len(html_matches)):
        raise RevisionError("changed or ambiguous exact paragraph/cell selector")
    return word_matches[word_ordinal], html_matches[html_ordinal]


def _relationships(root: etree._Element) -> dict[str, etree._Element]:
    rows = {item.get("Id"): item for item in root}
    if len(rows) != len(root):
        raise RevisionError("duplicate relationship IDs")
    return rows


def _media_for_drawing(drawing: etree._Element, rels: dict[str, etree._Element], parts: dict[str, bytes]) -> str:
    embeds = drawing.xpath(".//a:blip/@r:embed", namespaces=NS)
    if len(embeds) != 1 or embeds[0] not in rels:
        raise RevisionError("drawing image relationship is missing or ambiguous")
    relation = rels[embeds[0]]
    if relation.get("Type") != IMAGE_REL or relation.get("TargetMode"):
        raise RevisionError("drawing does not reference an internal image")
    target = relation.get("Target", "")
    part = str(PurePosixPath("word", target))
    if part not in parts:
        raise RevisionError(f"missing image part: {part}")
    return _sha(parts[part])


def _story_bounds(manifest: dict, document: etree._Element, page: etree._Element):
    stories = manifest.get("stories")
    if not isinstance(stories, list) or not stories:
        raise RevisionError("manifest requires ordered stories")
    word_paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    html_nodes = list(page.iter())
    bounds = {}
    previous_word = previous_html = -1
    for story in stories:
        sid = story.get("story_id")
        word_name = story.get("word_bookmark")
        html_name = story.get("html_anchor")
        if not all(isinstance(x, str) and x for x in (sid, word_name, html_name)) or sid in bounds:
            raise RevisionError("invalid or duplicate story identity")
        w = word_paragraphs.index(_bookmark(document, word_name))
        h = html_nodes.index(_html_anchor(page, html_name))
        if w <= previous_word or h <= previous_html:
            raise RevisionError("story anchors must follow manifest order")
        bounds[sid] = {"word_start": w, "html_start": h, "word_bookmark": word_name, "html_anchor": html_name}
        previous_word, previous_html = w, h
    ordered = list(bounds)
    for index, sid in enumerate(ordered):
        nxt = bounds[ordered[index + 1]] if index + 1 < len(ordered) else None
        bounds[sid]["word_end"] = nxt["word_start"] if nxt else len(word_paragraphs)
        bounds[sid]["html_end"] = nxt["html_start"] if nxt else len(html_nodes)
    return bounds


def _word_occurrences(document, rels, parts, bounds):
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    result = {}
    for sid, span in bounds.items():
        rows = []
        for para in paragraphs[span["word_start"]:span["word_end"]]:
            for drawing in para.xpath(".//w:drawing", namespaces=NS):
                docpr = drawing.find(".//" + WP + "docPr")
                if docpr is None:
                    raise RevisionError("drawing lacks docPr")
                rows.append({"sha256": _media_for_drawing(drawing, rels, parts),
                             "drawing_id": int(docpr.get("id")), "graphic_id": docpr.get("descr")})
        result[sid] = rows
    return result


def _drawing_order(document, rels, parts):
    rows = []
    for drawing in document.xpath(".//w:body//w:drawing", namespaces=NS):
        docpr = drawing.find(".//" + WP + "docPr")
        if docpr is None:
            raise RevisionError("drawing lacks docPr")
        rows.append((_media_for_drawing(drawing, rels, parts), docpr.get("id")))
    return rows


def _html_occurrences(page, assets, bounds):
    nodes = list(page.iter())
    result = {}
    for sid, span in bounds.items():
        rows = []
        for node in nodes[span["html_start"]:span["html_end"]]:
            if node.tag != "img":
                continue
            src = node.get("src", "")
            safe = _safe_relative(src)
            if str(safe) not in assets:
                raise RevisionError(f"HTML image is absent from assets: {src}")
            rows.append({"sha256": assets[str(safe)]["sha256"], "src": src,
                         "graphic_id": node.get("data-graphic-id")})
        result[sid] = rows
    return result


def _coverage(ledger, word_rows, html_rows):
    if not isinstance(ledger, list) or not ledger:
        raise RevisionError("independent source graphic ledger is required")
    ids = set()
    consumed_word, consumed_html = set(), set()
    report = []
    for row in ledger:
        gid, sid, disposition = row.get("graphic_id"), row.get("story_id"), row.get("disposition")
        if not isinstance(gid, str) or not gid or gid in ids or sid not in word_rows:
            raise RevisionError("invalid or duplicate graphic ledger identity")
        ids.add(gid)
        if not isinstance(row.get("source_page"), int) or row["source_page"] < 1:
            raise RevisionError(f"{gid}: physical source_page is required")
        if disposition == "exclude":
            if row.get("reviewed") is not True or not row.get("reason"):
                raise RevisionError(f"{gid}: exclusion requires reviewed reason")
            report.append({"graphic_id": gid, "disposition": disposition, "source_page": row["source_page"]})
            continue
        if disposition != "must_include":
            raise RevisionError(f"{gid}: reference_only cannot satisfy required art")
        sha = row.get("sha256", "").upper()
        ordinal = row.get("occurrence_ordinal")
        if not isinstance(ordinal, int) or ordinal < 0:
            raise RevisionError(f"{gid}: occurrence_ordinal is required")
        for kind, collection, consumed in (("word", word_rows, consumed_word), ("html", html_rows, consumed_html)):
            matches = [(i, item) for i, item in enumerate(collection[sid]) if item["sha256"] == sha]
            if ordinal >= len(matches):
                raise RevisionError(f"{gid}: missing {kind} occurrence in story {sid}")
            index, item = matches[ordinal]
            if (sid, index) in consumed:
                raise RevisionError(f"{gid}: {kind} occurrence reused by another ledger row")
            if item["graphic_id"] and item["graphic_id"] != gid:
                raise RevisionError(f"{gid}: misplaced {kind} graphic identity")
            consumed.add((sid, index))
        report.append({"graphic_id": gid, "disposition": disposition, "story_id": sid,
                       "source_page": row["source_page"], "sha256": sha, "occurrence_ordinal": ordinal})
    return report


def _image_dimensions(payload: bytes) -> tuple[int, int]:
    from io import BytesIO
    with Image.open(BytesIO(payload)) as image:
        image.load()
        return image.size


def _add_word_image(document, rels, types, parts, paragraph, op, payload, dimensions):
    ext = op["asset_path"].rsplit(".", 1)[-1].lower()
    if ext not in {"png", "jpg", "jpeg"}:
        raise RevisionError("only PNG/JPEG source artwork is supported")
    used_parts = set(parts)
    number = 1
    while f"word/media/revision-{number}.{ext}" in used_parts:
        number += 1
    part = f"word/media/revision-{number}.{ext}"
    rid = 1
    relmap = _relationships(rels)
    while f"rIdRevision{rid}" in relmap:
        rid += 1
    relid = f"rIdRevision{rid}"
    relation = etree.SubElement(rels, PKG + "Relationship")
    relation.set("Id", relid)
    relation.set("Type", IMAGE_REL)
    relation.set("Target", f"media/revision-{number}.{ext}")
    mime = "image/png" if ext == "png" else "image/jpeg"
    defaults = types.xpath("./ct:Default[@Extension=$ext]", namespaces={"ct": CT[1:-1]}, ext=ext)
    if defaults:
        if len(defaults) != 1 or defaults[0].get("ContentType") != mime:
            raise RevisionError("conflicting image content type")
    else:
        etree.SubElement(types, CT + "Default", Extension=ext, ContentType=mime)
    existing_ids = [int(x) for x in document.xpath(".//wp:docPr/@id | .//pic:cNvPr/@id", namespaces=NS) if x.isdigit()]
    drawing_id = max(existing_ids, default=0) + 1
    width, height = dimensions
    width_inches = op.get("word_width_inches", 5.5)
    if (not isinstance(width_inches, (int, float)) or isinstance(width_inches, bool)
            or not math.isfinite(width_inches) or not 0 < width_inches <= 6.5):
        raise RevisionError("word_width_inches must be a finite positive width at most 6.5")
    max_width = int(width_inches * EMU_PER_INCH)
    cx = min(max_width, width * 9525)
    cy = round(cx * height / width)
    image_para = etree.Element(W + "p")
    run = etree.SubElement(image_para, W + "r")
    drawing = etree.SubElement(run, W + "drawing")
    inline = etree.SubElement(drawing, WP + "inline", distT="0", distB="0", distL="0", distR="0")
    etree.SubElement(inline, WP + "extent", cx=str(cx), cy=str(cy))
    etree.SubElement(inline, WP + "docPr", id=str(drawing_id), name=op["graphic_id"], descr=op["graphic_id"])
    graphic = etree.SubElement(inline, A + "graphic")
    graphic_data = etree.SubElement(graphic, A + "graphicData", uri="http://schemas.openxmlformats.org/drawingml/2006/picture")
    picture = etree.SubElement(graphic_data, PIC + "pic")
    nv = etree.SubElement(picture, PIC + "nvPicPr")
    etree.SubElement(nv, PIC + "cNvPr", id=str(drawing_id), name=op["graphic_id"])
    etree.SubElement(nv, PIC + "cNvPicPr")
    fill = etree.SubElement(picture, PIC + "blipFill")
    etree.SubElement(fill, A + "blip", {R + "embed": relid})
    stretch = etree.SubElement(fill, A + "stretch")
    etree.SubElement(stretch, A + "fillRect")
    props = etree.SubElement(picture, PIC + "spPr")
    transform = etree.SubElement(props, A + "xfrm")
    etree.SubElement(transform, A + "off", x="0", y="0")
    etree.SubElement(transform, A + "ext", cx=str(cx), cy=str(cy))
    geometry = etree.SubElement(props, A + "prstGeom", prst="rect")
    etree.SubElement(geometry, A + "avLst")
    paragraph.addnext(image_para)
    parts[part] = payload
    return {"drawing_id": drawing_id, "part": part, "width_emu": cx, "height_emu": cy}, image_para


def _input_assets(root: Path, declared: dict) -> dict:
    if not isinstance(declared, dict):
        raise RevisionError("existing_assets must be a path-to-hash object")
    observed = {}
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            observed[f"assets/{rel}"] = path
    if set(observed) != set(declared):
        raise RevisionError("existing image inventory differs from assets directory")
    result = {}
    for name, path in observed.items():
        _safe_relative(name)
        if path.is_symlink():
            raise RevisionError("symlink assets are unsupported")
        digest = _file_sha(path)
        _check_hash(digest, declared[name], name)
        result[name] = {"path": path, "sha256": digest}
    return result


def _validate_manifest(manifest: dict, paths: dict) -> None:
    if manifest.get("schema") != "kb_creator.reviewed_reader_revision.v1":
        raise RevisionError("unsupported manifest schema")
    if manifest.get("provenance") != "reviewed_artifact_successor":
        raise RevisionError("successor provenance must be explicit")
    for label in ("docx", "html", "source_pdf"):
        _check_hash(_file_sha(paths[label]), manifest.get("inputs", {}).get(label + "_sha256"), label)
    operations = manifest.get("operations")
    if not isinstance(operations, list):
        raise RevisionError("operations must be a list")
    ids = set()
    for op in operations:
        oid = op.get("issue_id") or op.get("graphic_id")
        if not isinstance(oid, str) or not oid or oid in ids:
            raise RevisionError("operations need unique issue_id or graphic_id")
        ids.add(oid)
        if op.get("kind") not in {"keep", "text", "art"}:
            raise RevisionError(f"{oid}: unsupported operation")
        if op.get("kind") == "keep" and (op.get("disposition") != "keep" or not op.get("reason")):
            raise RevisionError(f"{oid}: unchanged issue requires explicit keep disposition")


def revise_reader(manifest_path: Path, docx: Path, html_path: Path, assets_root: Path,
                  source_pdf: Path, output_root: Path) -> dict:
    """Retired dual-output writer; retained helpers support DOCX-only revisions."""
    raise RevisionError(
        "The reviewed-reader DOCX+HTML writer is retired. "
        "Use `python -m kb_creator.scripts.revise_reviewed_docx` for a DOCX-only revision; "
        "historical inputs and reports remain read-only."
    )
    paths = {"manifest": manifest_path.resolve(), "docx": docx.resolve(), "html": html_path.resolve(),
             "assets": assets_root.resolve(), "source_pdf": source_pdf.resolve(), "output": output_root.resolve()}
    if len(set(paths.values())) != len(paths) or paths["output"].exists():
        raise RevisionError("output aliases an input or already exists")
    if any(paths["output"] == p or p in paths["output"].parents or paths["output"] in p.parents
           for label, p in paths.items() if label != "output"):
        raise RevisionError("output root overlaps an input path")
    for label in ("manifest", "docx", "html", "source_pdf"):
        if not paths[label].is_file():
            raise RevisionError(f"missing input {label}")
    if not paths["assets"].is_dir():
        raise RevisionError("missing assets directory")
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8-sig"))
    _validate_manifest(manifest, paths)
    assets = _input_assets(paths["assets"], manifest.get("inputs", {}).get("existing_assets"))
    parts = _zip_parts(paths["docx"])
    for name in ("word/document.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"):
        if name not in parts:
            raise RevisionError(f"DOCX missing {name}")
    original_parts = dict(parts)
    document = _xml(parts["word/document.xml"], "document.xml")
    rels = _xml(parts["word/_rels/document.xml.rels"], "document.xml.rels")
    types = _xml(parts["[Content_Types].xml"], "[Content_Types].xml")
    original_relation_rows = [etree.tostring(item) for item in rels]
    original_type_rows = [etree.tostring(item) for item in types]
    styles = _xml(parts["word/styles.xml"], "styles.xml") if "word/styles.xml" in parts else None
    visibility = _StyleVisibility(styles)
    original_drawing_order = _drawing_order(document, _relationships(rels), parts)
    page = html.fromstring(paths["html"].read_bytes())
    original_page = deepcopy(page)
    original_html_image_order = original_page.xpath("//img/@src")
    original_html_text = Counter(original_page.itertext())
    expected_html_text = original_html_text.copy()
    bounds = _story_bounds(manifest, document, page)
    ledger = manifest.get("source_graphics")
    if not isinstance(ledger, list) or not ledger:
        raise RevisionError("source_graphics ledger must be complete and nonempty")
    ledger_by_id = {r.get("graphic_id"): r for r in ledger}
    if len(ledger_by_id) != len(ledger):
        raise RevisionError("duplicate source graphic ID")
    expected_graphics = manifest.get("source_graphic_ids")
    if (not isinstance(expected_graphics, list) or not expected_graphics
            or len(expected_graphics) != len(set(expected_graphics))
            or set(expected_graphics) != set(ledger_by_id)):
        raise RevisionError("source graphic ledger differs from independent required ID inventory")
    new_assets = {}
    operation_report = []
    original_paragraph_elements = document.xpath(".//w:body//w:p", namespaces=NS)
    expected_paragraphs = [_paragraph_text(p) for p in original_paragraph_elements]
    inserted_paragraphs = []
    original_markers = {name: Counter(document.xpath(f".//w:{name}/@w:id", namespaces=NS))
                        for name in ("commentRangeStart", "commentRangeEnd", "commentReference")}
    original_bookmarks = Counter(document.xpath(".//w:bookmarkStart/@w:name", namespaces=NS))
    original_hyperlinks = Counter(document.xpath(".//w:hyperlink/@r:id | .//w:hyperlink/@w:anchor", namespaces=NS))
    for op in manifest["operations"]:
        kind, sid = op["kind"], op.get("story_id")
        if kind == "keep":
            operation_report.append({"id": op["issue_id"], "kind": "keep"})
            continue
        if sid not in bounds:
            raise RevisionError("operation has unknown story_id")
        bounds = _story_bounds(manifest, document, page)
        span = bounds[sid]
        if op.get("word_bookmark") != span["word_bookmark"] or op.get("html_anchor") != span["html_anchor"]:
            raise RevisionError("operation story anchor mismatch")
        word_para = _bookmark(document, op["word_bookmark"])
        html_node = _html_anchor(page, op["html_anchor"])
        if kind == "text":
            expected = op.get("expected_text")
            target = op.get("target_text")
            replacement = op.get("replacement")
            if not all(isinstance(x, str) and x for x in (expected, target, replacement)) or target == replacement:
                raise RevisionError("invalid exact text operation")
            if op.get("disposition") != "replace":
                raise RevisionError("text edit requires explicit replace disposition")
            word_para, html_node = _text_targets(op, sid, bounds, document, page)
            original_index = original_paragraph_elements.index(word_para)
            _replace_word_text(word_para, expected, target, replacement, visibility)
            html_before, html_after = _replace_html_text(html_node, expected, target, replacement)
            expected_html_text[html_before] -= 1
            expected_html_text[html_after] += 1
            expected_paragraphs[original_index] = expected.replace(target, replacement, 1)
            operation_report.append({"id": op["issue_id"], "kind": "text", "before": expected,
                                     "after": expected.replace(target, replacement, 1)})
            continue
        gid = op.get("graphic_id")
        row = ledger_by_id.get(gid)
        if not row or row.get("disposition") != "must_include" or row.get("story_id") != sid:
            raise RevisionError(f"{gid}: art operation lacks matching must_include ledger row")
        source_given = Path(op.get("source_image", ""))
        source = source_given.resolve()
        if (source_given.is_symlink() or not source.is_file() or source == paths["output"]
                or paths["output"] in source.parents):
            raise RevisionError("unsafe or missing source image")
        if not isinstance(op.get("source_page"), int) or op["source_page"] != row.get("source_page"):
            raise RevisionError("art source physical page mismatch")
        payload = source.read_bytes()
        digest = _sha(payload)
        _check_hash(digest, op.get("sha256"), gid)
        _check_hash(digest, row.get("sha256"), gid + " ledger")
        dimensions = _image_dimensions(payload)
        if list(dimensions) != op.get("dimensions"):
            raise RevisionError(f"{gid}: source image dimensions changed")
        asset = str(_safe_relative(op.get("asset_path", "")))
        if asset in assets or asset in new_assets:
            raise RevisionError("new artwork asset collides with existing asset")
        new_assets[asset] = payload
        insertion = op.get("insertion")
        if insertion == "after_exact_text":
            position = op.get("position")
            if not isinstance(position, dict):
                raise RevisionError("exact artwork position is required")
            word_label = position.get("word_expected_text")
            html_label = position.get("html_expected_text")
            if (not isinstance(word_label, str) or not word_label
                    or word_label != html_label):
                raise RevisionError("artwork Word/HTML insertion text must match exactly")
            word_para, html_node = _text_targets(position, sid, bounds, document, page)
        elif insertion != "after_anchor":
            raise RevisionError("unsupported artwork insertion position")
        word_info, new_paragraph = _add_word_image(document, rels, types, parts, word_para, op, payload, dimensions)
        inserted_paragraphs.append(new_paragraph)
        figure = etree.Element("figure")
        image = etree.SubElement(figure, "img", src=asset, alt=op.get("alt", gid))
        image.set("data-graphic-id", gid)
        image.set("width", str(dimensions[0]))
        image.set("height", str(dimensions[1]))
        image.set("style", "max-width:100%;height:auto")
        html_node.addnext(figure)
        operation_report.append({"id": gid, "kind": "art", "source_page": row["source_page"],
                                 "reader_story": sid, "reader_position": insertion, "sha256": digest, **word_info})
    parts["word/document.xml"] = _serial(document)
    parts["word/_rels/document.xml.rels"] = _serial(rels)
    parts["[Content_Types].xml"] = _serial(types)
    all_assets = dict(assets)
    all_assets.update({name: {"sha256": _sha(payload)} for name, payload in new_assets.items()})
    bounds = _story_bounds(manifest, document, page)
    word_rows = _word_occurrences(document, _relationships(rels), parts, bounds)
    html_rows = _html_occurrences(page, all_assets, bounds)
    coverage = _coverage(ledger, word_rows, html_rows)
    if Counter(document.xpath(".//w:bookmarkStart/@w:name", namespaces=NS)) != original_bookmarks:
        raise RevisionError("bookmark conservation failed")
    if Counter(document.xpath(".//w:hyperlink/@r:id | .//w:hyperlink/@w:anchor", namespaces=NS)) != original_hyperlinks:
        raise RevisionError("hyperlink conservation failed")
    if ([etree.tostring(item) for item in list(rels)[:len(original_relation_rows)]] != original_relation_rows
            or [etree.tostring(item) for item in list(types)[:len(original_type_rows)]] != original_type_rows):
        raise RevisionError("existing relationship or content type changed")
    for name, expected in original_markers.items():
        if Counter(document.xpath(f".//w:{name}/@w:id", namespaces=NS)) != expected:
            raise RevisionError("native comment anchor conservation failed")
    for name, payload in original_parts.items():
        if name.startswith("word/media/") or "comment" in name.lower() or "person" in name.lower():
            if parts.get(name) != payload:
                raise RevisionError(f"review or media part changed: {name}")
    successor_paragraphs = [p for p in document.xpath(".//w:body//w:p", namespaces=NS)
                            if p not in inserted_paragraphs]
    if (successor_paragraphs != original_paragraph_elements
            or [_paragraph_text(p) for p in successor_paragraphs] != expected_paragraphs):
        raise RevisionError("ordered Word paragraph conservation failed")
    new_drawing_ids = {str(row["drawing_id"]) for row in operation_report if row["kind"] == "art"}
    current_drawings = [row for row in _drawing_order(document, _relationships(rels), parts)
                        if row[1] not in new_drawing_ids]
    if current_drawings != original_drawing_order:
        raise RevisionError("ordered existing Word artwork conservation failed")
    if [src for src in page.xpath("//img/@src") if src not in new_assets] != original_html_image_order:
        raise RevisionError("ordered existing HTML artwork conservation failed")
    for name, payload in original_parts.items():
        if name in {"word/document.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}:
            continue
        if parts.get(name) != payload:
            raise RevisionError(f"undeclared DOCX part change: {name}")
    html_bytes = html.tostring(page, encoding="utf-8", method="html", doctype="<!DOCTYPE html>")
    if Counter(original_page.xpath("//*[@id]/@id")) != Counter(page.xpath("//*[@id]/@id")):
        raise RevisionError("HTML anchor conservation failed")
    if Counter(page.itertext()) != +expected_html_text:
        raise RevisionError("undeclared HTML text change")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".reviewed-reader-", dir=output_root.parent))
    try:
        docx_out, html_out, assets_out = staged / "document.docx", staged / "document.html", staged / "assets"
        assets_out.mkdir()
        with zipfile.ZipFile(docx_out, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, payload in parts.items():
                archive.writestr(name, payload)
        html_out.write_bytes(html_bytes)
        for name, info in assets.items():
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(info["path"], target)
        for name, payload in new_assets.items():
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        written = _zip_parts(docx_out)
        for name, payload in parts.items():
            if written.get(name) != payload:
                raise RevisionError("post-write DOCX part differs")
        if html_out.read_bytes() != html_bytes or any(_file_sha(staged / name) != info["sha256"] for name, info in all_assets.items()):
            raise RevisionError("post-write HTML or asset hash mismatch")
        checked_document = _xml(written["word/document.xml"], "written document.xml")
        checked_rels = _relationships(_xml(written["word/_rels/document.xml.rels"], "written rels"))
        checked_page = html.fromstring(html_out.read_bytes())
        checked_bounds = _story_bounds(manifest, checked_document, checked_page)
        checked_word = _word_occurrences(checked_document, checked_rels, written, checked_bounds)
        checked_html = _html_occurrences(checked_page, all_assets, checked_bounds)
        if _coverage(ledger, checked_word, checked_html) != coverage:
            raise RevisionError("post-write source graphic coverage changed")
        if ([row for row in _drawing_order(checked_document, checked_rels, written)
             if row[1] not in new_drawing_ids] != original_drawing_order
                or [src for src in checked_page.xpath("//img/@src") if src not in new_assets] != original_html_image_order):
            raise RevisionError("post-write existing artwork occurrence order changed")
        for operation in operation_report:
            if operation["kind"] == "art":
                drawing = checked_document.xpath(".//wp:docPr[@id=$identifier]/ancestor::w:drawing[1]",
                                                 namespaces=NS, identifier=str(operation["drawing_id"]))
                if len(drawing) != 1:
                    raise RevisionError("post-write drawing identity changed")
                extent = drawing[0].find(".//" + WP + "extent")
                if extent is None or int(extent.get("cx", "0")) != operation["width_emu"] or int(extent.get("cy", "0")) != operation["height_emu"]:
                    raise RevisionError("post-write drawing dimensions changed")
                if drawing[0].xpath(".//a:srcRect", namespaces=NS):
                    raise RevisionError("post-write artwork has a crop")
                matching_html = checked_page.xpath("//img[@data-graphic-id=$gid]", gid=operation["id"])
                if len(matching_html) != 1:
                    raise RevisionError("post-write HTML graphic identity changed")
                matching_op = next(op for op in manifest["operations"] if op.get("graphic_id") == operation["id"])
                if [int(matching_html[0].get(axis, "0")) for axis in ("width", "height")] != matching_op["dimensions"]:
                    raise RevisionError("post-write HTML dimensions changed")
        report = {"schema": "kb_creator.reviewed_reader_revision_report.v1", "status": "validated_candidate",
                  "provenance": "reviewed_artifact_successor", "accepted": False,
                  "inputs": {label: {"path": paths[label].as_posix(), "sha256": _file_sha(paths[label])}
                             for label in ("docx", "html", "source_pdf", "manifest")},
                  "outputs": {"docx_sha256": _file_sha(docx_out), "html_sha256": _file_sha(html_out),
                              "assets": {name: info["sha256"] for name, info in all_assets.items()}},
                  "operations": operation_report, "source_graphic_coverage": coverage,
                  "preservation": {"old_media_parts": sum(name.startswith("word/media/") for name in original_parts),
                                   "old_comment_thread_parts": [name for name in original_parts if "comment" in name.lower() or "person" in name.lower()],
                                   "bookmarks": sum(original_bookmarks.values()), "hyperlinks": sum(original_hyperlinks.values())},
                  "limitations": ["Reviewed-artifact successor; upstream source/master replay is unavailable.",
                                  "Requires separate rendered-page QA and independent release review."]}
        (staged / "revision-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output_root.exists():
            raise RevisionError("output root appeared during build")
        staged.rename(output_root)
        return report
    finally:
        if staged.exists():
            shutil.rmtree(staged)
