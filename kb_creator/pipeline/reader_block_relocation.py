"""Exact reviewed whole-block relocation, with final HTML and Word witnesses."""
from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

from lxml import etree, html

ROLE = "reviewed_block_relocation"


def fingerprint(node) -> str:
    """Bind rich payload and presentation, allowing only generated ID changes."""
    clone = copy.deepcopy(node)
    clone.tail = None
    for item in clone.iter():
        item.attrib.pop("id", None)
    return hashlib.sha256(etree.tostring(clone, method="c14n")).hexdigest().upper()


def _blocks(tree):
    sections = tree.xpath('.//section[@data-page]')
    if any(section.getparent() is not sections[0].getparent() for section in sections):
        raise ValueError("relocation requires unnested sibling source pages")
    return [node for section in sections for node in section
            if isinstance(node.tag, str)]


def _binding(binding, bound, projection):
    if not isinstance(binding, dict) or set(binding) != {"unit_id", "ru_sha256"}:
        raise ValueError("relocation requires exact unit/hash bindings")
    unit = bound(binding)
    if (hashlib.sha256(unit["ru_text"].encode()).hexdigest().upper() != binding["ru_sha256"]
            or unit.get("parent_unit_id") is not None
            or unit.get("part_index") is not None or unit.get("part_count") is not None
            or any(row.get("parent_unit_id") == unit["unit_id"] for row in projection["units"])
            or any(unit["unit_id"] in span.get("unit_ids", []) for span in projection.get("spans", []))):
        raise ValueError("relocation unit preimage or whole ownership changed")
    return unit


def apply(tree, projection, options, pages, bound, locate, anchor, *, bind_heading_occurrence=None):
    """Apply after reflow/omissions, before final witnesses; never guess an owner."""
    from kb_creator.pipeline.reader_duplicate_text import _refs
    roles = [row for row in options["display_roles"] if row.get("role") == ROLE]
    if not roles:
        return []
    prepared = []
    order = [row["unit_id"] for row in projection["units"]]
    blocks = _blocks(tree)
    claimed = set()
    for role in roles:
        required = {"role", "units", "destination", "crossed_units", "rendered_preimage",
                    "source_evidence", "reason"}
        if (set(role) - {"keep_with_next", "heading_occurrence"} != required
                or any(not isinstance(role.get(key), str) or not role[key].strip()
                       for key in ("source_evidence", "reason"))
                or not isinstance(role["units"], list) or not role["units"]
                or not isinstance(role["crossed_units"], list)
                or ("keep_with_next" in role and role["keep_with_next"] is not True)):
            raise ValueError("relocation requires complete reviewed fields")
        dest = role["destination"]
        pre = role["rendered_preimage"]
        if (not isinstance(dest, dict) or set(dest) != {"position", "unit"}
                or dest["position"] not in {"before", "after"}
                or not isinstance(pre, dict) or set(pre) != {"units", "destination", "crossed"}
                or not isinstance(pre["units"], list) or not isinstance(pre["crossed"], list)
                or any(not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest)
                       for digest in [*pre["units"], pre["destination"], *pre["crossed"]])):
            raise ValueError("relocation destination/rendered preimage is malformed")
        moving = [_binding(row, bound, projection) for row in role["units"]]
        destination = _binding(dest["unit"], bound, projection)
        cohort_units, cohort_nodes = [], []
        if "heading_occurrence" in role:
            witness = role["heading_occurrence"]
            if (bind_heading_occurrence is None or not isinstance(witness, dict)
                    or set(witness) != {"ordinal", "cohort"}
                    or type(witness["ordinal"]) is not int or witness["ordinal"] < 0
                    or not isinstance(witness["cohort"], list) or len(witness["cohort"]) < 2):
                raise ValueError("relocation heading occurrence requires exact callback/cohort")
            cohort_units = [_binding(row, bound, projection) for row in witness["cohort"]]
            cohort_nodes = bind_heading_occurrence(dest["unit"], witness)
            section = tree.xpath('.//section[@data-page=$page]',
                                 page=f"{pages[destination['unit_id']]:03d}")
            if (len(section) != 1 or len(cohort_nodes) != len(cohort_units)
                    or any(node.getparent() is not section[0] or (node.tail or "").strip()
                           or locate(binding) is not node
                           for binding, node in zip(witness["cohort"], cohort_nodes))):
                raise ValueError("relocation heading occurrence DOM ownership changed")
        crossing = [_binding(row, bound, projection) for row in role["crossed_units"]]
        ids = [row["unit_id"] for row in moving]
        indexes = [order.index(uid) for uid in ids]
        di = order.index(destination["unit_id"])
        if (indexes != list(range(indexes[0], indexes[0] + len(indexes))) or di in indexes
                or len(set(ids)) != len(ids)):
            raise ValueError("relocation requires distinct consecutive whole source units")
        start, end = ((indexes[-1] + 1, di) if indexes[-1] < di else (di + 1, indexes[0]))
        if [row["unit_id"] for row in crossing] != order[start:end]:
            raise ValueError("relocation crossed source interval is incomplete or changed")
        for unit in [*moving, destination]:
            uid = unit["unit_id"]
            if (not (unit is destination and cohort_units)
                    and sum(row["ru_text"] == unit["ru_text"] and pages[row["unit_id"]] == pages[uid]
                   for row in projection["units"]) != 1):
                raise ValueError("relocation source occurrence is ambiguous/cohort-owned")
        for unit in [*moving, destination, *cohort_units]:
            uid = unit["unit_id"]
            for other in options["display_roles"]:
                if other is role or other.get("role") == ROLE or uid not in _refs(other):
                    continue
                # Exact retained whole handout groups may compose with relocation.
                groups = other.get("intervening_handout_groups", [])
                if (other.get("role") != "interrupted_prose_reflow"
                        or uid in {row["unit_id"] for row in other.get("units", [])}
                        or not any({"unit_id": uid, "ru_sha256": unit["ru_sha256"]}
                                   in group.get("units", []) for group in groups)):
                    raise ValueError("relocation conflicts with another structural owner")
        nodes = [locate(row) for row in role["units"]]
        target = locate(dest["unit"])
        if (any(node not in blocks or node.getparent().tag != "section"
                or node.getparent().get("data-page") is None
                or (node.tail or "").strip() for node in [*nodes, target])
                or len(set(nodes)) != len(nodes)
                or [blocks.index(node) for node in nodes] != list(range(blocks.index(nodes[0]), blocks.index(nodes[0]) + len(nodes)))
                or any(node.getparent() is not nodes[0].getparent() for node in nodes)):
            raise ValueError("relocation forbids partial/nested/nonconsecutive HTML ownership")
        a, b, d = blocks.index(nodes[0]), blocks.index(nodes[-1]), blocks.index(target)
        crossed = blocks[b + 1:d] if b < d else blocks[d + 1:a]
        if ([fingerprint(node) for node in nodes] != pre["units"]
                or fingerprint(target) != pre["destination"]
                or [fingerprint(node) for node in crossed] != pre["crossed"]):
            raise ValueError(f"relocation exact rendered preimage/crossed interval changed: {ids}; "
                             f"units={[fingerprint(node) for node in nodes]}; "
                             f"destination={fingerprint(target)}; crossed={[fingerprint(node) for node in crossed]}")
        domain = set([*nodes, target, *crossed, *cohort_nodes])
        if claimed.intersection(domain):
            raise ValueError("relocation moves overlap or have dependent destinations")
        claimed.update(domain)
        if role.get("keep_with_next") and (any(node.tag != "p" for node in nodes)
                                           or dest["position"] != "before"):
            raise ValueError("relocation keep-with-next requires plain labels before a successor")
        for binding in [*role["units"], dest["unit"]]:
            anchor(binding)
        prepared.append({"decision": role, "nodes": nodes, "destination": target,
                         "source_pages": {int(node.getparent().get("data-page"))
                                          for node in [*nodes, target, *crossed]}})
    # All preflight checks precede the first DOM mutation.
    snapshots = {node: etree.tostring(node, with_tail=True) for node in blocks}
    expected = list(blocks)
    for row in prepared:
        nodes, target, role = row["nodes"], row["destination"], row["decision"]
        for node in nodes:
            expected.remove(node)
            node.getparent().remove(node)
        at = expected.index(target) + (role["destination"]["position"] == "after")
        expected[at:at] = nodes
        parent = target.getparent()
        at = parent.index(target) + (role["destination"]["position"] == "after")
        for offset, node in enumerate(nodes):
            parent.insert(at + offset, node)
    if (_blocks(tree) != expected or any(etree.tostring(node, with_tail=True) != snapshot
                                        for node, snapshot in snapshots.items())):
        raise ValueError("relocation changed payload or unrelated whole-block order")
    for row in prepared:
        if row["decision"].get("keep_with_next"):
            for node in row["nodes"]:
                node.set("data-semantic-kind", "label")
                node.set("data-keep-with-next", "true")
    return prepared


def finalize(tree, prepared, report, master_root: Path | None):
    """Recheck final adjacency and capture Word text/image occurrence witnesses."""
    if not prepared:
        return
    from kb_creator.pipeline import reader_duplicate_text as duplicates
    from kb_creator.pipeline.reader_projection import identity, _local
    blocks = _blocks(tree)
    images = []
    image_owners = []
    for row in prepared:
        nodes, target, role = row["nodes"], row["destination"], row["decision"]
        d = blocks.index(target)
        start = d - len(nodes) if role["destination"]["position"] == "before" else d + 1
        if blocks[start:start + len(nodes)] != nodes or any(node.getparent() is not target.getparent() for node in nodes):
            raise ValueError("relocation final HTML adjacency/owner changed")
        report.setdefault("block_relocations", []).append({"decision": role,
            "anchors": [node.get("id") for node in nodes], "destination_anchor": target.get("id"),
            "source_pages": sorted(row["source_pages"]),
            "keep_with_next": bool(role.get("keep_with_next")),
            "final_payload_sha256": [fingerprint(node) for node in nodes]})
        report["display_roles"].append(role)
    touched = sorted({page for row in prepared for page in row["source_pages"]})
    for page in touched:
        section = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}")[0]
        duplicates.append_page_witness(tree, report, page, duplicates.page_paragraphs(section), key="relocation_page_witness")
        for index, figure in enumerate(section.xpath('./figure[img]')):
            if master_root is None or len(figure.xpath('./img')) != 1:
                raise ValueError("relocation needs exact local whole-figure evidence")
            ref = figure[0].get("src")
            if not figure.get("id"):
                figure.set("id", f"relocation-image-{page:03d}-{index}")
            images.append({"source_page": page, "image_unit": {}, "reference": ref,
                           "identity": identity(_local(master_root, ref)), "anchor": figure.get("id")})
            traversal = list(section.iterdescendants())
            preceding = sum(traversal.index(node) < traversal.index(figure)
                            for node, _ in duplicates._page_paragraph_nodes(section))
            image_owners.append({"page": page, "anchor": figure.get("id"), "preceding_paragraphs": preceding})
    report["relocation_image_dependencies"] = images
    report["relocation_image_owners"] = image_owners
    owners = []
    for page in touched:
        section = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}")[0]
        paragraphs = [node for node, _ in duplicates._page_paragraph_nodes(section)]
        for row in prepared:
            for node in [*row["nodes"], row["destination"]]:
                if node.getparent() is section:
                    owner = node[0] if node.tag in {"ul", "ol"} else node
                    if owner.tag != "figure":
                        if owner not in paragraphs:
                            raise ValueError("relocation has unsupported Word paragraph owner")
                        owners.append({"page": page, "anchor": node.get("id"), "ordinal": paragraphs.index(owner)})
    report["relocation_paragraph_owners"] = owners
    ids = [node.get("id") for node in tree.iter() if node.get("id")]
    if len(ids) != len(set(ids)):
        raise ValueError("relocation final HTML IDs are ambiguous")


def verify_docx(report, docx_path: Path):
    """Validate actual paired bookmarks, full page streams, and original media."""
    import zipfile
    from kb_creator.pipeline import five_step_docx as docx
    if not report.get("block_relocations"):
        return
    witnesses = report.get("relocation_page_witness")
    if not witnesses or not report.get("relocation_paragraph_owners"):
        raise docx.FiveStepDocxError("relocation final Word evidence is missing")
    with zipfile.ZipFile(docx_path) as archive:
        paragraphs, index = docx._verify_page_streams(archive.read("word/document.xml"), witnesses)
    by_page = {row["source_page"]: row for row in witnesses}
    for owner in report["relocation_paragraph_owners"]:
        docx._verify_page_owner(paragraphs, index, by_page[owner["page"]], owner["anchor"], owner["ordinal"])
    for owner in report.get("relocation_image_owners", []):
        start = index(by_page[owner["page"]]["boundary"])
        position = index(owner["anchor"])
        preceding = sum(bool(docx._word_visible_text(paragraph)) for paragraph in paragraphs[start:position])
        if preceding != owner["preceding_paragraphs"]:
            raise docx.FiveStepDocxError("relocation image moved relative to the exact text stream")
    for row in report["block_relocations"]:
        positions = [index(anchor) for anchor in row["anchors"]]
        destination = index(row["destination_anchor"])
        if (positions != sorted(set(positions))
                or (row["decision"]["destination"]["position"] == "before" and positions[-1] >= destination)
                or (row["decision"]["destination"]["position"] == "after" and positions[0] <= destination)):
            raise docx.FiveStepDocxError("relocation actual Word order changed")
        if row.get("keep_with_next"):
            ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            for position in positions:
                keep = paragraphs[position].find(f"{{{ns}}}pPr/{{{ns}}}keepNext")
                if keep is None or keep.get(f"{{{ns}}}val") in {"0", "false", "off"}:
                    raise docx.FiveStepDocxError("relocation caption lost reviewed keep-with-next")
    docx.verify_retained_artwork_docx({"retained_image_dependencies": report.get("relocation_image_dependencies", []),
                                     "reflow_page_witness": witnesses}, docx_path)
