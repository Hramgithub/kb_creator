"""Reviewed pagination groups preserve existing source containers and payload."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from lxml import etree, html

ROLE = "reviewed_statblock_group"
ATTRIBUTE = "data-reader-statblock-group"
TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}


def fingerprint(node) -> str:
    return hashlib.sha256(etree.tostring(node, with_tail=False, encoding="utf-8")).hexdigest().upper()


def member_anchor(group_id: str, index: int) -> str:
    return f"reader-statblock-group:{group_id}:{index}"


def apply(tree, projection, options, pages, bound, report):
    """Preflight all exact final sequences before marking any existing node."""
    from translator.translator import markdown_to_review_html
    from kb_creator.pipeline.reader_projection import norm

    roles = [row for row in options["display_roles"] if row.get("role") == ROLE]
    if not roles:
        return
    sections = tree.xpath('.//section[@data-page]')
    if not sections or any(s.getparent() is not sections[0].getparent() for s in sections):
        raise ValueError("statblock grouping requires sibling source pages")
    blocks = [n for s in sections for n in s if isinstance(n.tag, str)
              and not (n.tag == "div" and n.get("class") == "page-marker" and not len(n))]
    order = {u["unit_id"]: i for i, u in enumerate(projection["units"])}
    claimed, group_ids, prepared = set(), set(), []
    for role in roles:
        required = {"role", "group_id", "units", "rendered_members", "source_evidence", "reason"}
        gid = role.get("group_id")
        if (set(role) != required or not isinstance(gid, str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", gid)
                or gid in group_ids
                or any(not isinstance(role[k], str) or not role[k].strip()
                       for k in ("source_evidence", "reason"))
                or not isinstance(role["units"], list) or len(role["units"]) < 2
                or not isinstance(role["rendered_members"], list)
                or len(role["units"]) != len(role["rendered_members"])):
            raise ValueError("statblock grouping requires closed reviewed fields")
        group_ids.add(gid)
        units, wanted = [], []
        for binding, member in zip(role["units"], role["rendered_members"]):
            if not isinstance(binding, dict) or set(binding) != {"unit_id", "ru_sha256"}:
                raise ValueError("statblock grouping requires exact unit bindings")
            unit = bound(binding)
            uid = unit["unit_id"]
            if (hashlib.sha256(unit["ru_text"].encode()).hexdigest().upper() != binding["ru_sha256"]
                    or unit.get("parent_unit_id") is not None
                    or unit.get("part_index") is not None or unit.get("part_count") is not None
                    or any(u.get("parent_unit_id") == uid for u in projection["units"])
                    or any(uid in s.get("unit_ids", []) for s in projection.get("spans", []))):
                raise ValueError("statblock grouping requires whole unstructured unit ownership")
            if (not isinstance(member, dict)
                    or set(member) != {"unit_id", "source_page", "final_html_sha256"}
                    or member["unit_id"] != uid or type(member["source_page"]) is not int
                    or member["source_page"] != pages[uid]
                    or not isinstance(member["final_html_sha256"], str)
                    or not re.fullmatch(r"[A-F0-9]{64}", member["final_html_sha256"])):
                raise ValueError("statblock grouping member ownership or fingerprint is invalid")
            fragment, _, _ = markdown_to_review_html(unit["ru_text"], source_path=Path("unit.md"),
                                                      html_path=Path("unit.html"), blockquote_heading_offset=0)
            rendered = html.fragment_fromstring(fragment, create_parent="main")
            if len(rendered) != 1 or rendered[0].tag not in TAGS:
                raise ValueError("statblock grouping forbids partial or structured source units")
            units.append(unit)
            wanted.append(norm(rendered[0].text_content()))
        positions = [order[u["unit_id"]] for u in units]
        if positions != sorted(set(positions)):
            raise ValueError("statblock grouping source member order changed")
        hashes = [m["final_html_sha256"] for m in role["rendered_members"]]
        candidates = [i for i in range(len(blocks) - len(hashes) + 1)
                      if [fingerprint(n) for n in blocks[i:i + len(hashes)]] == hashes]
        if len(candidates) != 1:
            raise ValueError(f"statblock grouping final sequence is missing or ambiguous: {gid}")
        nodes = blocks[candidates[0]:candidates[0] + len(hashes)]
        if claimed.intersection(nodes):
            raise ValueError("statblock grouping members overlap")
        for node, member, text in zip(nodes, role["rendered_members"], wanted):
            if (node.tag not in TAGS or norm(node.text_content()) != text
                    or node.getparent().get("data-page") != f'{member["source_page"]:03d}'
                    or node.get(ATTRIBUTE) is not None or (node.tail or "").strip()
                    or node.xpath('ancestor::*[@data-semantic-kind] | ancestor::blockquote | .//img')
                    or any(n.tag not in {"strong", "em", "b", "i", "code", "a", "span", "br"}
                           for n in node.iterdescendants())):
                raise ValueError("statblock grouping forbids changed ownership or unsupported payload")
        claimed.update(nodes)
        prepared.append((role, nodes))
    for role, nodes in prepared:
        for node in nodes:
            node.set(ATTRIBUTE, role["group_id"])
        report.setdefault("statblock_groups", []).append({
            "decision": role,
            "source_pages": sorted({m["source_page"] for m in role["rendered_members"]}),
            "members": [{"anchor": member_anchor(role["group_id"], i),
                         "visible_text": n.text_content(),
                         **role["rendered_members"][i]} for i, n in enumerate(nodes)],
        })
        report["display_roles"].append(role)


def verify_xml(report, document_xml: bytes, *, keep_together: bool):
    """Check real member bookmarks, exact paragraph adjacency and keep flags."""
    if not report.get("statblock_groups"):
        return
    from kb_creator.scripts.production_docx import bookmark_name
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = etree.fromstring(document_xml)
    body = root.find("w:body", ns)
    stream = [n for n in body if n.tag in {f'{{{ns["w"]}}}p', f'{{{ns["w"]}}}tbl'}]
    seen = set()
    for group in report.get("statblock_groups", []):
        positions = []
        if len(group.get("members", [])) < 2:
            raise ValueError("statblock grouping Word evidence is missing")
        for i, member in enumerate(group["members"]):
            expected = member_anchor(group["decision"]["group_id"], i)
            if member["anchor"] != expected:
                raise ValueError("statblock grouping Word anchor evidence changed")
            matches = root.xpath('//w:bookmarkStart[@w:name=$name]', namespaces=ns,
                                 name=bookmark_name(expected))
            if len(matches) != 1 or matches[0].getparent() not in stream:
                raise ValueError("statblock grouping Word member is missing or ambiguous")
            paragraph = matches[0].getparent()
            position = stream.index(paragraph)
            if position in seen or " ".join("".join(paragraph.xpath('.//w:t/text()', namespaces=ns)).split()) != " ".join(member["visible_text"].split()):
                raise ValueError("statblock grouping Word payload or ownership changed")
            if paragraph.xpath('.//w:br[@w:type="page"] | ./w:pPr/w:pageBreakBefore[not(@w:val="0")]', namespaces=ns):
                raise ValueError("statblock grouping Word member has an explicit page break")
            if keep_together:
                for tag, desired in (("keepLines", True), ("keepNext", i < len(group["members"]) - 1)):
                    flags = paragraph.xpath(f'./w:pPr/w:{tag}', namespaces=ns)
                    actual = flags and flags[0].get(f'{{{ns["w"]}}}val') not in {"0", "false", "off"}
                    if len(flags) != 1 or bool(actual) != desired:
                        raise ValueError("statblock grouping Word keep flags changed")
            seen.add(position)
            positions.append(position)
        if positions != list(range(positions[0], positions[0] + len(positions))):
            raise ValueError("statblock grouping Word members are not consecutive")


def verify_docx(report, path: Path, *, keep_together: bool):
    if report.get("statblock_groups"):
        import zipfile
        with zipfile.ZipFile(path) as archive:
            verify_xml(report, archive.read("word/document.xml"), keep_together=keep_together)
