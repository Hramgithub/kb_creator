"""Exact, reviewed omission of whole extraction duplicate paragraphs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from lxml import etree, html
from translator.translator import markdown_to_review_html


ROLE = "omit_extraction_duplicate_text"
_HEX = re.compile(r"[0-9A-F]{64}\Z")
_PLAIN = re.compile(r"(?![#>\s]*$)[^*_[\]`<>!\\\r]+\Z", re.S)
_ARTIFACT_PLAIN = re.compile(r"(?![#>\s]*$)[^*_`<>!\\\r]+\Z", re.S)
_LEAF = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "figcaption"}


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _signature(node):
    if node.tag != "p" or node.attrib and set(node.attrib) - {"id"}:
        raise ValueError("duplicate text requires a plain paragraph")
    parts = [node.text or ""]
    for child in node:
        if child.tag != "br" or child.attrib or len(child) or child.text:
            raise ValueError("duplicate text rejects inline markup")
        parts.extend(("\n", child.tail or ""))
    return tuple(parts)


def _rendered(text: str, *, artifact: bool = False):
    permitted = _ARTIFACT_PLAIN if artifact else _PLAIN
    if (not isinstance(text, str) or not text.strip() or not permitted.fullmatch(text)
            or any(re.match(r"\s*(?:#{1,6}\s|>|[-+*]\s|\d+[.)]\s|\|)", line) for line in text.splitlines())):
        raise ValueError("duplicate text unit is not plain paragraph Markdown")
    if artifact:
        lines = text.split("\n")
        if ("\t" in text or re.search(r"\[[^\]]+\]\s*\(", text)
                or any(not line or (line.endswith("  ") and (not line[:-2] or line[:-2] != line[:-2].strip()))
                       or (not line.endswith("  ") and line != line.strip())
                       for line in lines)):
            raise ValueError("artifact whole plain block has unaccounted Markdown whitespace or markup")
    fragment, _, _ = markdown_to_review_html(text, source_path=Path("unit.md"), html_path=Path("unit.html"), blockquote_heading_offset=0)
    blocks = html.fragment_fromstring(fragment, create_parent="main")
    if len(blocks) != 1 or blocks[0].tag != "p":
        raise ValueError("duplicate text unit must render as one paragraph")
    signature = _signature(blocks[0])
    if artifact:
        expected = ""
        for index, line in enumerate(lines):
            hard = line.endswith("  ")
            expected += line[:-2] if hard else line
            if index + 1 < len(lines):
                expected += "\n" if hard else " "
        if blocks[0].text_content() != expected:
            raise ValueError("artifact raw text is not conserved by Markdown transport")
    return signature


def _page(node):
    sections = [parent for parent in node.iterancestors() if parent.tag == "section" and parent.get("data-page")]
    if len(sections) != 1:
        raise ValueError("duplicate text paragraph has ambiguous source page")
    return int(sections[0].get("data-page")), sections[0]


def _supported(node):
    if node.tag != "p" or any(parent.tag in {"table", "ul", "ol", "li", "blockquote", "figure", "nav"}
                              or (parent.get("data-semantic-kind") and parent.get("data-semantic-kind") != "statblock")
                              for parent in node.iterancestors()):
        raise ValueError("duplicate text target is in an unsupported structured container")
    return _signature(node)


def _refs(value):
    if isinstance(value, dict):
        if value.get("role") == "reviewed_block_relocation":
            # Crossed units are exact evidence, not owners of their presentation.
            yield from _refs(value.get("units"))
            yield from _refs(value.get("destination"))
            return
        if isinstance(value.get("unit_id"), str) and "ru_sha256" in value:
            yield value["unit_id"]
        for child in value.values():
            yield from _refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _refs(child)


def resolve_plain_occurrence(tree, projection: dict, pages: dict, unit: dict, binding: dict,
                             *, artifact: bool = False, reviewed_cohort: dict | None = None):
    """Resolve an exact whole projection unit to one original page paragraph."""
    uid = unit["unit_id"]
    page = pages[uid]
    signature = _rendered(unit["ru_text"], artifact=artifact)
    sections = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}")
    if len(sections) != 1:
        raise ValueError("reviewed text source page missing or ambiguous")
    nodes = []
    for node in sections[0].iterdescendants():
        if node.tag == "p":
            try:
                if _supported(node) == signature:
                    nodes.append(node)
            except ValueError:
                continue
    cohort = [candidate for candidate in projection["units"] if pages[candidate["unit_id"]] == page
              and candidate.get("parent_unit_id") is None
              and _candidate_signature(candidate, artifact=artifact) == signature]
    if len(nodes) != len(cohort) or not cohort:
        raise ValueError("reviewed text occurrence cohort differs from exact projection units")
    if reviewed_cohort is None:
        if any(candidate["ru_text"] != unit["ru_text"] for candidate in cohort):
            raise ValueError("reviewed text occurrence cohort differs from exact projection units")
    else:
        members = reviewed_cohort.get("members") if isinstance(reviewed_cohort, dict) else None
        if (not artifact or not isinstance(reviewed_cohort, dict)
                or set(reviewed_cohort) != {"source_page", "members"}
                or type(reviewed_cohort["source_page"]) is not int or reviewed_cohort["source_page"] != page
                or not isinstance(members, list) or len(members) < 2 or len(members) != len(cohort)
                or len({candidate["ru_text"] for candidate in cohort}) < 2):
            raise ValueError("reviewed rendered-equivalent cohort requires an exact page and full distinct membership")
        for ordinal, (member, candidate) in enumerate(zip(members, cohort)):
            if (not isinstance(member, dict)
                    or set(member) != {"unit_id", "ru_sha256", "expected_raw_text", "match_ordinal"}
                    or member["unit_id"] != candidate["unit_id"]
                    or member["ru_sha256"] != candidate["ru_sha256"]
                    or member["ru_sha256"] != _hash(candidate["ru_text"])
                    or member["expected_raw_text"] != candidate["ru_text"]
                    or type(member["match_ordinal"]) is not int or member["match_ordinal"] != ordinal
                    or pages[candidate["unit_id"]] != page
                    or _candidate_signature(candidate, artifact=True) != signature):
                raise ValueError("reviewed rendered-equivalent cohort member differs from exact projection")
    ordinal = binding["match_ordinal"]
    if ordinal >= len(nodes) or cohort[ordinal]["unit_id"] != uid:
        raise ValueError("reviewed text occurrence ordinal differs from projection order")
    node = nodes[ordinal]
    if _page(node)[0] != page:
        raise ValueError("reviewed text actual source page mismatch")
    return node, signature


def _evidence(decision: dict, options: dict, options_path: Path | None, local, identity):
    evidence = decision.get("source_evidence")
    if (not isinstance(evidence, dict) or set(evidence) != {"finding_id", "approval", "reviewer", "source_pdf_sha256", "source_visual", "observed_source_occurrences"}
            or evidence.get("approval") != "reviewed" or type(evidence.get("observed_source_occurrences")) is not int
            or evidence["observed_source_occurrences"] != 1
            or any(not isinstance(evidence.get(k), str) or not evidence[k].strip() for k in ("finding_id", "reviewer"))
            or not isinstance(evidence.get("source_pdf_sha256"), str) or not _HEX.fullmatch(evidence["source_pdf_sha256"])
            or evidence["source_pdf_sha256"] != options["source_toc"].get("source_pdf_sha256")):
        raise ValueError("duplicate text requires reviewed one-occurrence source evidence")
    visual = evidence["source_visual"]
    if (not isinstance(visual, dict) or set(visual) != {"path", "bytes", "sha256"}
            or not isinstance(visual["path"], str) or not visual["path"].startswith("evidence/")
            or any(part in {"", ".", ".."} for part in visual["path"].split("/"))
            or Path(visual["path"]).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}
            or "\\" in visual["path"] or type(visual["bytes"]) is not int or visual["bytes"] <= 0
            or not isinstance(visual["sha256"], str) or not _HEX.fullmatch(visual["sha256"]) or options_path is None):
        raise ValueError("duplicate text requires a portable source visual identity")
    path = local(options_path.parent, visual["path"])
    if not path.is_file() or {"path": visual["path"], **identity(path)} != visual:
        raise ValueError("duplicate text source visual identity mismatch")


def prepare(tree, projection: dict, options: dict, pages: dict, bound, *, options_path: Path | None, local, identity):
    decisions = [row for row in options["display_roles"] if isinstance(row, dict) and row.get("role") == ROLE]
    if not decisions:
        return []
    references = {}
    for key in ("source_toc", "asset_choices", "hit_points"):
        for uid in _refs(options[key]):
            references.setdefault(uid, set()).add(key)
    for link in options["body_links"]:
        for key in ("unit", "target"):
            for uid in _refs(link.get(key)):
                references.setdefault(uid, set()).add("body_link_target" if key == "target" else "body_link_source")
    for row in options["display_roles"]:
        if row not in decisions:
            for uid in _refs(row):
                references.setdefault(uid, set()).add(row.get("role", "display_role"))
    omitted_ids = []
    retained_ids = []
    prepared = []
    for decision in decisions:
        required = {"role", "unit", "retained", "retained_raw_span", "source_page", "source_evidence", "reason"}
        if (set(decision) != required or type(decision.get("source_page")) is not int or decision["source_page"] < 1
                or not isinstance(decision.get("reason"), str) or not decision["reason"].strip()):
            raise ValueError("duplicate text decision has invalid fields")
        _evidence(decision, options, options_path, local, identity)
        pair = []
        for key in ("unit", "retained"):
            binding = decision[key]
            if (not isinstance(binding, dict) or set(binding) != {"unit_id", "ru_sha256", "match_ordinal"}
                    or not isinstance(binding["unit_id"], str) or not binding["unit_id"]
                    or type(binding["match_ordinal"]) is not int or binding["match_ordinal"] < 0):
                raise ValueError("duplicate text occurrence binding is malformed")
            unit = bound(binding)
            if pages[unit["unit_id"]] != decision["source_page"] or unit.get("parent_unit_id") is not None:
                raise ValueError("duplicate text unit page or split-parent topology is unsupported")
            pair.append(unit)
        omitted, retained = pair
        if omitted["unit_id"] == retained["unit_id"]:
            raise ValueError("duplicate text cannot omit its retained owner")
        span = decision["retained_raw_span"]
        text = retained["ru_text"]
        if (not isinstance(span, dict) or set(span) != {"start", "end"}
                or type(span["start"]) is not int or type(span["end"]) is not int
                or not 0 <= span["start"] < span["end"] <= len(text)
                or (span["start"] and text[span["start"] - 1] != "\n")
                or (span["end"] != len(text) and text[span["end"]] != "\n"
                    and (text[span["end"]:span["end"] + 3] != "  \n" or text[span["end"] - 1] == " "))
                or omitted["ru_text"] != text[span["start"]:span["end"]]):
            raise ValueError("duplicate text retained raw interval does not exactly cover whole lines")
        for unit in pair:
            _rendered(unit["ru_text"])
        omitted_ids.append(omitted["unit_id"]); retained_ids.append(retained["unit_id"])
        prepared.append({"decision": decision, "omitted": omitted, "retained": retained})
    if len(omitted_ids) != len(set(omitted_ids)) or set(omitted_ids) & set(retained_ids):
        raise ValueError("duplicate text removal ownership conflicts or cycles")
    for row in prepared:
        for kind in ("omitted", "retained"):
            unit = row[kind]; uid = unit["unit_id"]
            routes = references.get(uid, set())
            allowed = {"review_anchor", "source_issue_review_anchor", "body_link_target"} if kind == "retained" else set()
            if routes - allowed:
                raise ValueError(f"duplicate text {kind} unit {uid} conflicts with {sorted(routes - allowed)}")
            node, signature = resolve_plain_occurrence(
                tree, projection, pages, unit,
                row["decision"]["unit" if kind == "omitted" else "retained"])
            row[kind + "_node"] = node
            row[kind + "_signature"] = signature
    if len({id(row["omitted_node"]) for row in prepared}) != len(prepared):
        raise ValueError("duplicate text decisions select the same rendered paragraph")
    return prepared


def _candidate_signature(unit, *, artifact: bool = False):
    try:
        return _rendered(unit["ru_text"], artifact=artifact)
    except ValueError:
        return None


def _artifact_evidence(decision: dict, options: dict, options_path: Path | None, local, identity):
    evidence = decision.get("source_evidence")
    if (not isinstance(evidence, dict)
            or set(evidence) != {"approval", "reviewer", "source_pdf_sha256", "source_visual", "source_region", "visual_verdict", "rationale"}
            or evidence.get("approval") != "reviewed"
            or any(not isinstance(evidence.get(key), str) or not evidence[key].strip()
                   for key in ("reviewer", "rationale"))
            or evidence.get("source_pdf_sha256") != options["source_toc"].get("source_pdf_sha256")
            or not isinstance(evidence.get("source_pdf_sha256"), str)
            or not _HEX.fullmatch(evidence["source_pdf_sha256"])):
        raise ValueError("whole artifact requires exact reviewed source evidence")
    expected_verdict = ("whole_unit_is_running_furniture" if decision["classification"] == "source_furniture_text"
                        else "whole_unit_is_facsimile_interface_text")
    if evidence.get("visual_verdict") != expected_verdict:
        raise ValueError("whole artifact visual verdict differs from classification")
    visual = evidence["source_visual"]
    if (not isinstance(visual, dict) or set(visual) != {"path", "bytes", "sha256"}
            or not isinstance(visual["path"], str) or not visual["path"].startswith("evidence/")
            or any(part in {"", ".", ".."} for part in visual["path"].split("/"))
            or "\\" in visual["path"] or Path(visual["path"]).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}
            or type(visual["bytes"]) is not int or visual["bytes"] <= 0
            or not isinstance(visual["sha256"], str) or not _HEX.fullmatch(visual["sha256"])
            or options_path is None):
        raise ValueError("whole artifact visual identity is invalid")
    source = local(options_path.parent, visual["path"])
    if not source.is_file() or identity(source) != {key: visual[key] for key in ("bytes", "sha256")}:
        raise ValueError("whole artifact source visual identity mismatch")
    region = evidence["source_region"]
    if (not isinstance(region, dict) or set(region) != {"coordinate_space", "bbox"}
            or region["coordinate_space"] != "source_visual_pixels_top_left_v1"
            or not isinstance(region["bbox"], list) or len(region["bbox"]) != 4
            or any(type(value) is not int for value in region["bbox"])):
        raise ValueError("whole artifact source region is invalid")
    from PIL import Image
    with Image.open(source) as image:
        width, height = image.size
    x0, y0, x1, y1 = region["bbox"]
    if not 0 <= x0 < x1 <= width or not 0 <= y0 < y1 <= height:
        raise ValueError("whole artifact source region leaves reviewed visual")
    return visual


def _image_signature(unit_text: str):
    match = re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+)\)(?:\{([^}]*)\})?", unit_text)
    if not match:
        raise ValueError("retained artwork unit must contain one exact image")
    fragment, _, _ = markdown_to_review_html(unit_text, source_path=Path("unit.md"),
                                              html_path=Path("unit.html"), blockquote_heading_offset=0)
    blocks = html.fragment_fromstring(fragment, create_parent="main")
    if len(blocks) != 1 or blocks[0].tag != "figure":
        raise ValueError("retained artwork unit must render one figure")
    figure = blocks[0]
    images = figure.xpath("./img")
    if len(images) != 1 or len(figure.xpath("./figcaption")) > 1:
        raise ValueError("retained artwork figure is ambiguous")
    caption = figure.xpath("./figcaption")
    return (images[0].get("src"), images[0].get("alt"), caption[0].text_content() if caption else None,
            figure.get("class"))


def _actual_image_signature(figure):
    images = figure.xpath("./img")
    caption = figure.xpath("./figcaption")
    if (figure.tag != "figure" or len(images) != 1 or len(caption) > 1
            or len(figure) != len(images) + len(caption)
            or (figure.text or "").strip()
            or any((child.tail or "").strip() for child in figure)):
        raise ValueError("retained artwork requires an exact figure occurrence")
    return (images[0].get("src"), images[0].get("alt"), caption[0].text_content() if caption else None,
            figure.get("class"))


def _resolve_image(tree, projection: dict, pages: dict, unit: dict, binding: dict):
    page = pages[unit["unit_id"]]
    signature = _image_signature(unit["ru_text"])
    sections = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}")
    if len(sections) != 1:
        raise ValueError("retained artwork source page is missing")
    nodes = [node for node in sections[0].iterdescendants() if node.tag == "figure"
             and _actual_image_signature(node) == signature]
    cohort = []
    for candidate in projection["units"]:
        if pages[candidate["unit_id"]] != page or candidate.get("parent_unit_id") is not None:
            continue
        try:
            if _image_signature(candidate["ru_text"]) == signature:
                cohort.append(candidate)
        except ValueError:
            continue
    ordinal = binding["match_ordinal"]
    if (len(nodes) != len(cohort) or ordinal >= len(nodes) or cohort[ordinal]["unit_id"] != unit["unit_id"]
            or any(candidate["ru_text"] != unit["ru_text"] for candidate in cohort)):
        raise ValueError("retained artwork occurrence ordinal or cohort changed")
    return nodes[ordinal], signature[0]


def prepare_artifacts(tree, projection: dict, options: dict, pages: dict, bound, duplicate_rows: list,
                      *, options_path: Path | None, master_root: Path | None, local, identity,
                      guarded_transit: dict[str, int] | None = None):
    decisions = [row for row in options["display_roles"] if isinstance(row, dict)
                 and row.get("role") == "omit_source_artifact" and row.get("text_policy") == "reviewed_whole_plain_block_v2"]
    if not decisions:
        return []
    if master_root is None:
        raise ValueError("whole artifact requires an exact language master root")
    references = {}
    for key in ("source_toc", "body_links", "asset_choices", "hit_points"):
        for uid in _refs(options[key]):
            references.setdefault(uid, set()).add(key)
    for row in options["display_roles"]:
        if row not in decisions:
            for uid in _refs(row):
                references.setdefault(uid, set()).add(row.get("role", "display_role"))
    removed = {row["omitted"]["unit_id"] for row in duplicate_rows}
    retained_text = {row["retained"]["unit_id"] for row in duplicate_rows}
    prepared = []
    for decision in decisions:
        furniture = decision.get("classification") == "source_furniture_text"
        artwork = decision.get("classification") == "duplicate_text_represented_by_retained_artwork"
        common = {"role", "classification", "text_policy", "unit", "source_page", "expected_raw_text", "source_evidence", "reason"}
        expected = (common | {"furniture_kind", "extracted_as_ocr_fragment"} if furniture else
                    common | {"retained_image_unit", "retained_image_reference", "retained_image_identity"})
        if (not (furniture or artwork) or set(decision) not in (expected, expected | {"rendered_equivalent_cohort"})
                or type(decision.get("source_page")) is not int or decision["source_page"] < 1
                or not isinstance(decision.get("reason"), str) or not decision["reason"].strip()
                or not isinstance(decision.get("expected_raw_text"), str) or not decision["expected_raw_text"]):
            raise ValueError("whole artifact decision has invalid exact fields")
        if furniture and (decision["furniture_kind"] not in {"page_number", "running_header", "running_footer"}
                          or type(decision["extracted_as_ocr_fragment"]) is not bool):
            raise ValueError("source furniture requires reviewed positional kind and OCR flag")
        visual = _artifact_evidence(decision, options, options_path, local, identity)
        binding = decision["unit"]
        if (not isinstance(binding, dict) or set(binding) != {"unit_id", "ru_sha256", "match_ordinal"}
                or not isinstance(binding["unit_id"], str) or not binding["unit_id"]
                or type(binding["match_ordinal"]) is not int or binding["match_ordinal"] < 0):
            raise ValueError("whole artifact text occurrence binding is malformed")
        unit = bound(binding)
        uid = unit["unit_id"]
        routes = references.get(uid, set())
        transit = (uid in (guarded_transit or {})
                   and routes == {"interrupted_prose_reflow"})
        if (pages[uid] != decision["source_page"] or unit.get("parent_unit_id") is not None
                or unit["ru_text"] != decision["expected_raw_text"] or uid in removed | retained_text
                or (routes and not transit)
                or any(uid in span.get("unit_ids", []) for span in projection.get("spans", []))):
            raise ValueError("whole artifact text preimage, page, or protected ownership mismatch")
        node, signature = resolve_plain_occurrence(
            tree, projection, pages, unit, binding, artifact=True,
            reviewed_cohort=decision.get("rendered_equivalent_cohort"))
        row = {"decision": decision, "omitted": unit, "omitted_node": node, "omitted_signature": signature,
               "source_visual": visual, "kind": "artwork" if artwork else "furniture"}
        if artwork:
            image_binding = decision["retained_image_unit"]
            image_identity = decision["retained_image_identity"]
            reference = decision["retained_image_reference"]
            if (not isinstance(image_binding, dict) or set(image_binding) != {"unit_id", "ru_sha256", "match_ordinal"}
                    or not isinstance(image_binding["unit_id"], str) or not image_binding["unit_id"]
                    or type(image_binding["match_ordinal"]) is not int or image_binding["match_ordinal"] < 0
                    or not isinstance(reference, str) or not reference
                    or not isinstance(image_identity, dict) or set(image_identity) != {"bytes", "sha256"}
                    or type(image_identity["bytes"]) is not int or image_identity["bytes"] <= 0
                    or not isinstance(image_identity["sha256"], str) or not _HEX.fullmatch(image_identity["sha256"])
                    or visual["bytes"] != image_identity["bytes"] or visual["sha256"] != image_identity["sha256"]):
                raise ValueError("retained artwork binding or byte identity is invalid")
            image_unit = bound(image_binding)
            image_uid = image_unit["unit_id"]
            image_routes = references.get(image_uid, set())
            image_transit = (transit and guarded_transit is not None
                             and guarded_transit.get(image_uid) == guarded_transit[uid]
                             and image_routes == {"interrupted_prose_reflow"})
            if (pages[image_uid] != decision["source_page"] or image_unit.get("parent_unit_id") is not None
                    or image_uid == uid or image_uid in removed
                    or any(image_uid in span.get("unit_ids", []) for span in projection.get("spans", []))
                    or (transit and not image_transit)
                    or (image_routes and not image_transit)):
                raise ValueError("retained artwork unit is missing, changed, or owned by another role")
            image_node, rendered_ref = _resolve_image(tree, projection, pages, image_unit, image_binding)
            original = local(master_root, reference)
            if (rendered_ref != reference or not original.is_file() or identity(original) != image_identity
                    or any(choice.get("original_ref") == reference for choice in options["asset_choices"])
                    or any(other is not decision and other.get("role") in {"source_figure_regions", "asset_alt_metadata", "omit_source_artifact"}
                           and (other.get("source_reference") == reference
                                or (isinstance(other.get("unit"), dict) and other["unit"].get("unit_id") == image_uid))
                           for other in options["display_roles"] if isinstance(other, dict))):
                raise ValueError("retained artwork original image conflicts with another image route")
            row.update(image_unit=image_unit, image_node=image_node, image_signature=_actual_image_signature(image_node),
                       image_identity=image_identity, image_reference=reference)
            retained_text.add(image_uid)
        removed.add(uid)
        prepared.append(row)
    if len({id(row["omitted_node"]) for row in prepared}) != len(prepared):
        raise ValueError("whole artifact decisions select one rendered paragraph more than once")
    return prepared


def _inline(node):
    from kb_creator.scripts.production_docx import BLOCK_TAGS, normalized_fragment
    result = ""
    def add(value):
        nonlocal result
        text = normalized_fragment(value)
        if text:
            result += text.lstrip() if not result else text
    def visit(element):
        nonlocal result
        add(element.text)
        for child in element:
            if child.tag == "br":
                result += "\n"
            elif child.tag not in BLOCK_TAGS and child.tag != "img":
                visit(child)
            add(child.tail)
    visit(node)
    return result


def page_paragraphs(section):
    """Expected nonempty Word paragraph stream for supported source-page HTML."""
    return [value for _, value in _page_paragraph_nodes(section)]


def _page_paragraph_nodes(section):
    rows = []
    for node in section.iterdescendants():
        if not isinstance(node.tag, str):
            continue
        if node.tag in _LEAF:
            if any(parent.tag in _LEAF and not (node.tag == "li" and parent.tag == "li")
                   for parent in node.iterancestors() if parent is not section):
                raise ValueError("duplicate text DOCX witness unsupported nested paragraph topology")
            value = _inline(node)
            if value:
                rows.append((node, value))
        elif node.tag not in _LEAF | {"section", "div", "figure", "img", "table", "thead", "tbody", "tr", "ul", "ol", "blockquote", "br", "span", "a", "strong", "em", "b", "i", "code"}:
            raise ValueError(f"duplicate text DOCX witness unsupported HTML tag: {node.tag}")
    return rows


def apply(tree, prepared, report):
    if not prepared:
        return
    pages = {}
    for row in prepared:
        decision = row["decision"]
        page = decision["source_page"]
        _, section = _page(row["omitted_node"])
        pages[page] = section
        for kind in ("omitted", "retained"):
            node = row[kind + "_node"]
            if tree not in node.iterancestors() or _page(node)[0] != page or _supported(node) != row[kind + "_signature"]:
                raise ValueError("duplicate text operand changed before omission")
        node = row["omitted_node"]
        ids = [part.get("id") for part in node.iter() if part.get("id")]
        incoming = [link for link in tree.xpath('.//a[@href]') if link.get("href", "").startswith("#") and link.get("href")[1:] in ids]
        if ids or incoming or node.xpath('.//a'):
            raise ValueError("duplicate text omission conflicts with an HTML anchor or link")
        parent = node.getparent()
        if parent is None or len([child for child in parent if isinstance(child.tag, str) and child is not node and child.text_content().strip()]) == 0:
            raise ValueError("duplicate text omission would empty its semantic container")
    before_nodes = {page: _page_paragraph_nodes(section) for page, section in pages.items()}
    before = {page: [value for _, value in nodes] for page, nodes in before_nodes.items()}
    for row in prepared:
        row["omitted_node"].getparent().remove(row["omitted_node"])
    after_nodes = {page: _page_paragraph_nodes(section) for page, section in pages.items()}
    after = {page: [value for _, value in nodes] for page, nodes in after_nodes.items()}
    for page, prior in before.items():
        removed = [row for row in prepared if row["decision"]["source_page"] == page]
        removed_nodes = {id(row["omitted_node"]) for row in removed}
        expected_nodes = [(node, value) for node, value in before_nodes[page] if id(node) not in removed_nodes]
        if (len(prior) - len(after[page]) != len(removed)
                or [id(node) for node, _ in after_nodes[page]] != [id(node) for node, _ in expected_nodes]
                or after[page] != [value for _, value in expected_nodes]):
            raise ValueError("duplicate text changed unexpected source-page paragraphs")
    for row in prepared:
        decision = row["decision"]
        page = decision["source_page"]
        if tree not in row["retained_node"].iterancestors() or _supported(row["retained_node"]) != row["retained_signature"]:
            raise ValueError("duplicate text retained owner changed after omission")
        report["omitted_text_duplicates"].append({
            **decision, "actual_source_page": page,
            "omitted_occurrence": dict(decision["unit"]), "retained_occurrence": dict(decision["retained"]),
            "omitted_raw_sha256": _hash(row["omitted"]["ru_text"]),
            "retained_raw_sha256": _hash(row["retained"]["ru_text"]),
            "omitted_rendered_text": _inline(row["omitted_node"]),
            "affected_page_before": before[page], "affected_page_after": after[page],
            "affected_page_before_sha256": _hash(json.dumps(before[page], ensure_ascii=False, separators=(",", ":"))),
            "affected_page_after_sha256": _hash(json.dumps(after[page], ensure_ascii=False, separators=(",", ":"))),
        })
        report["display_roles"].append(decision)
    for page in sorted(pages):
        append_page_witness(tree, report, page, after[page])


def append_page_witness(tree, report, page: int, expected: list[str],
                        *, key: str = "duplicate_page_witness"):
    sections = [node for node in tree.iterdescendants() if node.tag == "section" and node.get("data-page")]
    matching = [node for node in sections if node.get("data-page") == f"{page:03d}"]
    if len(matching) != 1:
        raise ValueError("reviewed omission source page is missing or ambiguous")
    section = matching[0]
    index = sections.index(section)
    next_section = sections[index + 1] if index + 1 < len(sections) else None
    used_ids = {node.get("id") for node in tree.iter() if node.get("id")}
    for target in (section, next_section):
        if target is None or target.get("id"):
            continue
        internal = f"reader-page-boundary-{target.get('data-page')}"
        if internal in used_ids:
            raise ValueError("reviewed omission source-page boundary ID collision")
        target.set("id", internal); used_ids.add(internal)
    witness = {"source_page": page, "boundary": section.get("id"),
               "next_boundary": next_section.get("id") if next_section is not None else None,
               "expected_paragraphs": expected}
    rows = report.setdefault(key, [])
    old = next((row for row in rows if row["source_page"] == page), None)
    if old is None:
        rows.append(witness); rows.sort(key=lambda row: row["source_page"])
    elif (old["boundary"], old["next_boundary"]) != (witness["boundary"], witness["next_boundary"]):
        raise ValueError("reviewed omission source-page boundary changed between decisions")
    else:
        old["expected_paragraphs"] = expected


def apply_artifacts(tree, prepared: list, report: dict):
    if not prepared:
        return
    pages = {}
    for row in prepared:
        node = row["omitted_node"]
        page = row["decision"]["source_page"]
        actual_page, section = _page(node)
        if (tree not in node.iterancestors() or actual_page != page
                or _supported(node) != row["omitted_signature"]):
            raise ValueError("whole artifact paragraph changed before omission")
        ids = [part.get("id") for part in node.iter() if part.get("id")]
        if ids or node.xpath('.//a') or any(link.get("href") in {"#" + value for value in ids}
                                           for link in tree.xpath('.//a[@href]')):
            raise ValueError("whole artifact omission conflicts with an HTML bookmark or link")
        parent = node.getparent()
        if parent is None or not any(child is not node and isinstance(child.tag, str)
                                     and child.text_content().strip() for child in parent):
            raise ValueError("whole artifact would empty its semantic container")
        if row["kind"] == "artwork":
            image_node = row["image_node"]
            if (tree not in image_node.iterancestors() or _page(image_node)[0] != page
                    or _actual_image_signature(image_node) != row["image_signature"]):
                raise ValueError("retained artwork changed before text omission")
        pages[page] = section
    before_nodes = {page: _page_paragraph_nodes(section) for page, section in pages.items()}
    for row in prepared:
        row["omitted_node"].getparent().remove(row["omitted_node"])
    for page, section in sorted(pages.items()):
        after_nodes = _page_paragraph_nodes(section)
        removed = {id(row["omitted_node"]) for row in prepared if row["decision"]["source_page"] == page}
        expected = [(node, value) for node, value in before_nodes[page] if id(node) not in removed]
        if (not expected or [id(node) for node, _ in after_nodes] != [id(node) for node, _ in expected]
                or [value for _, value in after_nodes] != [value for _, value in expected]):
            raise ValueError("whole artifact omission changed unrelated page text or emptied page")
        append_page_witness(tree, report, page, [value for _, value in after_nodes])
    used_ids = {node.get("id") for node in tree.iter() if node.get("id")}
    for row in prepared:
        decision = row["decision"]
        page = decision["source_page"]
        prior = [value for _, value in before_nodes[page]]
        after = page_paragraphs(pages[page])
        report["omitted_artifacts"].append({
            **decision, "source_reference": None, "image_occurrences": 0,
            "actual_source_page": page, "omitted_raw_sha256": _hash(row["omitted"]["ru_text"]),
            "omitted_rendered_text": _inline(row["omitted_node"]),
            "affected_page_before": prior, "affected_page_after": after,
        })
        report["display_roles"].append(decision)
        if row["kind"] == "artwork":
            image_node = row["image_node"]
            anchor = image_node.get("id")
            if not anchor:
                anchor = "reader-retained-art-" + _hash(row["image_unit"]["unit_id"])[:24].lower()
                if anchor in used_ids:
                    raise ValueError("retained artwork anchor collision")
                image_node.set("id", anchor); used_ids.add(anchor)
            report["retained_image_dependencies"].append({
                "source_page": page, "image_unit": dict(decision["retained_image_unit"]),
                "reference": row["image_reference"], "identity": dict(row["image_identity"]),
                "anchor": anchor,
            })


def finalize(tree, prepared, report, artifact_rows=()):
    for row in prepared:
        node = row["retained_node"]
        if (tree not in node.iterancestors() or _page(node)[0] != row["decision"]["source_page"]
                or _supported(node) != row["retained_signature"]):
            raise ValueError("duplicate text retained owner changed after reader finishing")
    for row in artifact_rows:
        if row["kind"] == "artwork":
            node = row["image_node"]
            if (tree not in node.iterancestors() or _page(node)[0] != row["decision"]["source_page"]
                    or _actual_image_signature(node) != row["image_signature"]):
                raise ValueError("retained artwork changed after reader finishing")
    for witness in report.get("duplicate_page_witness", []):
        sections = tree.xpath('.//section[@data-page=$page]', page=f'{witness["source_page"]:03d}')
        if len(sections) != 1 or sections[0].get("id") != witness["boundary"]:
            raise ValueError("duplicate text source-page boundary changed")
        final = page_paragraphs(sections[0])
        original_after = witness["expected_paragraphs"]
        for row in [*prepared, *artifact_rows]:
            if row["decision"]["source_page"] == witness["source_page"]:
                omitted_text = _inline(row["omitted_node"])
                if final.count(omitted_text) > original_after.count(omitted_text):
                    raise ValueError("duplicate text reappeared after reader finishing")
        for row in report.get("omitted_artifacts", []):
            if (row.get("classification") == "duplicate_text_represented_by_retained_artwork"
                    and row.get("text_policy") is None
                    and row.get("actual_source_page") == witness["source_page"]):
                omitted_text = row["omitted_rendered_text"]
                if final.count(omitted_text) > original_after.count(omitted_text):
                    raise ValueError("legacy artwork duplicate text reappeared after reader finishing")
        witness["expected_paragraphs"] = final
