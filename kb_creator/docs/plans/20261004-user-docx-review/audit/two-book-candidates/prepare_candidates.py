"""Freeze two source-bound Word manifests from audited, immutable inputs.

This is a narrow U5v04 adapter, not a generic conversion engine. It authors
JSON evidence only; the separately marked DOCX-only CLI authors candidates.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from kb_creator.pipeline.reviewed_docx_revision import (
    DIRECT_SKILL_MAP, _node_xml_sha, _predicted_node_xml_sha, _word_leaf,
)
from kb_creator.pipeline.reviewed_reader_revision import (
    NS, W, _drawing_order, _paragraph_text, _relationships, _xml,
)


ROOT = Path(__file__).resolve().parents[6]
GOAL = ROOT / "kb_creator/docs/plans/20261004-user-docx-review"
AUDIT = GOAL / "audit"
HERE = Path(__file__).resolve().parent
LEN = "shadows-of-leningrad-1938"
KRE = "secrets-of-the-kremlin-1931"
SOURCE_QA = AUDIT / "conversion/source-qa/U7-source-visual-qa-v03.json"
OLD_LEDGER = AUDIT / "conversion/operations/U7-word-operations-v01.json"
CLOSURE = AUDIT / "conversion/qa/closure/U7-two-book-closure.json"
CHOICE1 = AUDIT / "conversion/accepted-choices-v01.json"
CHOICE2 = AUDIT / "conversion/accepted-choices-v02.json"
SPEC = AUDIT / "conversion/architecture/conversion-spec.md"
REVIEW1 = AUDIT / "review-decisions-v01.json"
REVIEW2 = AUDIT / "review-decisions-supplement-v02.json"
COMMENTS = AUDIT / "comments/comments_inventory.json"
PACKET = GOAL / "handoffs/U5-two-book-candidate-task-v04.md"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def freeze_json(path: Path, data: dict) -> None:
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() == payload:
            return
        raise ValueError(f"immutable output differs: {path}")
    path.write_bytes(payload)


def word_parts(book: str):
    path = ROOT / "kb_creator/deliverables/latest" / book / "document.docx"
    with zipfile.ZipFile(path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = _xml(parts["word/document.xml"], "document.xml")
    return path, parts, document


def direct_body(document):
    return list(document.find(".//" + W + "body"))


def node_text(node) -> str:
    return "".join(node.xpath(".//w:t/text()", namespaces=NS))


def anchor(document, body_index: int, *, self_context: bool = False) -> dict:
    owner = direct_body(document)[body_index]
    text = node_text(owner)
    if not text:
        raise ValueError(f"empty entity/context anchor at body[{body_index}]")
    result = {"body_index": body_index, "text": text,
              "text_sha256": sha(text.encode("utf-8")),
              "bookmarks": owner.xpath(".//w:bookmarkStart/@w:name", namespaces=NS)}
    if self_context:
        if owner.tag != W + "p":
            raise ValueError("self-context must be one exact body paragraph")
        result["self_context"] = True
    return result


def leaves(document, body_index: int, *, row: int | None = None, cell: int | None = None):
    owner = direct_body(document)[body_index]
    if owner.tag == W + "p":
        if row is not None or cell is not None:
            raise ValueError("row/cell declared for non-table Word body")
        paragraphs = [(f"word/document.xml/body[{body_index}]/p", owner)]
    elif owner.tag == W + "tbl":
        if row is None or cell is None:
            raise ValueError("table cell selector is required")
        rows = owner.findall(W + "tr")
        cells = rows[row].findall(W + "tc")
        paragraphs = [(f"word/document.xml/body[{body_index}]/tbl/tr[{row}]/tc[{cell}]/p[{pi}]", p)
                      for pi, p in enumerate(cells[cell].findall(W + "p"))]
    else:
        raise ValueError("unsupported Word body topology")
    for prefix, paragraph in paragraphs:
        for ri, run in enumerate(paragraph.findall(W + "r")):
            for ti, leaf in enumerate(run.findall(W + "t")):
                yield f"{prefix}/r[{ri}]/t[{ti}]", leaf


def exact_extra(documents: dict, *, book: str, body_index: int, before: str, after: str,
                entity: str, entity_anchor: dict, page: int, field: str, kind: str,
                rule: str, evidence: dict, choice: str | None = None,
                row: int | None = None, cell: int | None = None,
                action: str | None = None, scale: str | None = None) -> dict:
    document = documents[book]
    matches = [(path, leaf) for path, leaf in leaves(document, body_index, row=row, cell=cell)
               if (leaf.text or "").count(before) == 1]
    if len(matches) != 1:
        raise ValueError(f"{book} body[{body_index}] {before!r}: {len(matches)} Word leaves")
    path, leaf = matches[0]
    start = (leaf.text or "").index(before)
    identifier = f"{book}:v04:{body_index}:{kind}:{field}:{row if row is not None else 'p'}:{cell if cell is not None else 'p'}:{start}"
    return {"id": identifier, "book_id": book,
            "story_id": "scenario" if book == LEN else "kremlin_npc_records",
            "entity_id": entity, "entity_kind": "human_npc", "entity_anchor": entity_anchor,
            "field": field, "kind": kind, "disposition": "convert_deterministic",
            "current_scale": scale, "source_verified": True, "source_evidence": evidence,
            "input_docx_sha256": file_sha(ROOT / "kb_creator/deliverables/latest" / book / "document.docx"),
            "source_pdf_sha256": source_inputs[book]["source_pdf_sha256"],
            "source_pdf_path": source_inputs[book]["source_pdf_path"],
            "source_physical_page": page,
            "source_edition_evidence": ("explicit fifth edition" if book == LEN
                                        else "old 3–18 source cards at physical page 16"),
            "selector": {"part": "word/document.xml", "path": path, "body_index": body_index,
                         "table_row": row, "table_cell": cell,
                         "text_node_before": leaf.text or "",
                         "text_node_sha256": sha((leaf.text or "").encode("utf-8")),
                         "span_start": start, "span_end": start + len(before)},
            "before_text": before, "before_sha256": sha(before.encode("utf-8")),
            "after_text": after, "reverse_before": after, "reverse_after": before,
            "rule_id": rule, "editorial_decision": choice,
            **({"action": action} if action else {}),
            **({"entity_collision_clear": True} if kind == "skill_label" else {})}


def keep_ops(document, decisions, inventory, first_bookmark: str) -> list[dict]:
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    roots = {row["root_issue_id_candidate"]: row for row in inventory["threads"]
             if row.get("root_issue_id_candidate")}
    output = []
    for decision in decisions:
        if decision.get("disposition") != "keep":
            raise ValueError("Leningrad native decision is not an explicit keep")
        issue = decision["issue_id"]
        comment = roots[issue]
        comment_id = comment["comment_id"]
        matching = [p for p in paragraphs
                    if comment_id in p.xpath("./w:commentRangeStart/@w:id", namespaces=NS)]
        if len(matching) != 1:
            raise ValueError(f"{issue}: native root comment anchor not unique")
        paragraph = matching[0]
        text = _paragraph_text(paragraph)
        if text != comment["anchor"]["paragraph_text"]:
            raise ValueError(f"{issue}: native comment context changed")
        occurrences = [p for p in paragraphs if _paragraph_text(p) == text]
        output.append({"kind": "keep", "disposition": "keep", "issue_id": issue,
                       "story_id": "whole_book", "word_bookmark": first_bookmark,
                       "comment_id": comment_id, "expected_text": text,
                       "expected_text_sha256": sha(text.encode("utf-8")),
                       "selector": {"kind": "exact_paragraph", "expected_matches": len(occurrences),
                                    "ordinal": occurrences.index(paragraph)},
                       "reason": decision.get("reason") or decision.get("user_text")})
    if len(output) != 5:
        raise ValueError("exactly five native Leningrad keeps required")
    return output


def node_groups(operations: list[dict], documents: dict) -> list[dict]:
    grouped = defaultdict(list)
    for op in operations:
        grouped[(op["book_id"], op["selector"]["path"])].append(op)
    result = []
    for (book, path), members in grouped.items():
        leaf, _, _ = _word_leaf(documents[book], path)
        before = leaf.text or ""
        ids = [op["id"] for op in members]
        spans = sorted((op["selector"]["span_start"], op["selector"]["span_end"], op)
                       for op in members)
        if any(left[1] > right[0] for left, right in zip(spans, spans[1:])) or len(spans) > 8:
            raise ValueError(f"overlapping/too many Word edits at {path}")
        after = before
        for start, end, op in reversed(spans):
            if before[start:end] != op["before_text"]:
                raise ValueError(f"stale original span: {op['id']}")
            after = after[:start] + op["after_text"] + after[end:]
        for op in members:
            op["node_group_ids"] = ids
            op["selector"]["text_node_before"] = before
            op["selector"]["text_node_sha256"] = sha(before.encode("utf-8"))
        result.append({"book_id": book, "path": path, "operation_ids": ids,
                       "before_node": before, "before_node_sha256": sha(before.encode("utf-8")),
                       "before_node_xml_sha256": _node_xml_sha(leaf),
                       "after_node": after, "after_node_sha256": sha(after.encode("utf-8")),
                       "after_node_xml_sha256": _predicted_node_xml_sha(leaf, after),
                       "reverse_before_node": after, "reverse_after_node": before})
    return result


def main() -> None:
    global source_inputs
    authorities = [OLD_LEDGER, SOURCE_QA, CLOSURE, CHOICE1, CHOICE2, SPEC,
                   REVIEW1, REVIEW2, COMMENTS, PACKET]
    old, qa, closure = (read_json(path) for path in (OLD_LEDGER, SOURCE_QA, CLOSURE))
    choice1, choice2 = read_json(CHOICE1), read_json(CHOICE2)
    if (old["schema"] != "nri.u7_word_conversion_operations.v1"
            or old["state"] != "planning_only_no_successor_authored"
            or qa["coverage"]["numeric_fields_checked"] != 146
            or qa["coverage"]["status_counts"] != {"pass": 146, "mismatch": 0, "uncertain": 0}
            or len(qa["numeric_field_checks"]) != 146):
        raise ValueError("frozen numeric source QA or planning ledger does not close")
    qa_by_id = {row["operation_id"]: row for row in qa["numeric_field_checks"]}
    if len(qa_by_id) != 146:
        raise ValueError("duplicate numeric source-QA operation identity")
    source_inputs = old["inputs"]
    parts = {}
    documents = {}
    reviewed_paths = {}
    for book in (LEN, KRE):
        path, part_map, document = word_parts(book)
        if file_sha(path) != source_inputs[book]["docx_sha256"]:
            raise ValueError(f"{book}: reviewed DOCX identity changed")
        pdf = Path(source_inputs[book]["source_pdf_path"])
        if file_sha(pdf) != source_inputs[book]["source_pdf_sha256"]:
            raise ValueError(f"{book}: original source PDF identity changed")
        reviewed_paths[book], parts[book], documents[book] = path, part_map, document
    merged_ids = [row["id"] for row in choice1["decisions"] + choice2["decisions"]]
    if len(merged_ids) != len(set(merged_ids)):
        raise ValueError("duplicate user choice ID across original authorities")
    combined = {"schema": "nri.user_conversion_choices.v1",
                "goal_id": "20261004-user-docx-review",
                "source_authorities": [{"path": str(path), "sha256": file_sha(path)}
                                       for path in (CHOICE1, CHOICE2)],
                "decisions": choice1["decisions"] + choice2["decisions"]}
    freeze_json(HERE / "accepted-choices-combined-v01.json", combined)
    operations = []
    numeric_ids = set()
    for original in old["operations"]:
        op = json.loads(json.dumps(original, ensure_ascii=False))
        book = op["book_id"]
        try:
            leaf, _, owner = _word_leaf(documents[book], op["selector"]["path"])
        except Exception as exc:
            raise ValueError(f"{op['id']}: original selector is not supported") from exc
        if (leaf.text or "") != op["selector"]["text_node_before"]:
            raise ValueError(f"{op['id']}: stale Word node")
        if op["kind"] == "characteristic":
            check = qa_by_id.get(op["id"])
            if (check is None or check["book_id"] != book or check["entity_id"] != op["entity_id"]
                    or check["word_selector_path"] != op["selector"]["path"]
                    or check["word_before_text"] != op["before_text"]
                    or check["planned_after_text"] != op["after_text"]
                    or check["source_physical_page"] != op["source_physical_page"]
                    or check["source_visual_status"] != "pass"
                    or check["word_source_value_crosswalk_status"] != "pass"):
                raise ValueError(f"{op['id']}: independent numeric source QA does not bind")
            numeric_ids.add(op["id"])
            op["current_scale"] = "old_edition"
            op["source_evidence"] = {"path": str(SOURCE_QA), "sha256": file_sha(SOURCE_QA),
                                     "operation_id": op["id"]}
        else:
            # The v04 packet explicitly approves these original bounded labels;
            # their source page, entity/action and old node are frozen in U7/closure.
            if op["after_text"] not in {"Скрытность: 90% при передвижении, 75% при укрытии"}:
                if op["after_text"] in node_text(owner):
                    raise ValueError(f"{op['id']}: direct skill target already collides in entity object")
                op["entity_collision_clear"] = True
            op["source_evidence"] = {"paths": [str(OLD_LEDGER), str(CLOSURE), str(PACKET)],
                                     "sha256": [file_sha(OLD_LEDGER), file_sha(CLOSURE), file_sha(PACKET)],
                                     "source_page": op["source_physical_page"], "operation_id": op["id"]}
        op["source_verified"] = True
        operations.append(op)
    if len(numeric_ids) != 146 or {op["id"] for op in old["operations"] if op["kind"] == "characteristic"} != numeric_ids:
        raise ValueError("all 146 independent numeric source-QA IDs must close")
    # The original planning ledger omits collision and non-card decisions.
    extra = []
    len_doc = documents[LEN]
    for index, old_label, new_label, page in (
        (77, "Подкрадывание", "Скрытность", 7),
        (250, "Сокрытие", "Ловкость рук", 17),
        (344, "Сокрытие", "Ловкость рук", 22),
        (560, "Подкрадывание", "Скрытность", 34),
        (560, "Прятаться", "Скрытность", 34),
    ):
        evidence = next((row for row in closure["legacy_skill_occurrences"]
                         if row.get("page") == page and old_label in row.get("exact", "")), None)
        if evidence is None:
            raise ValueError(f"non-card label {old_label} p{page} lacks closure evidence")
        op = exact_extra(documents, book=LEN, body_index=index, before=old_label,
                         after=new_label, entity=f"source-context-{index}",
                         entity_anchor=anchor(len_doc, index, self_context=True),
                         page=page, field="skill:" + old_label, kind="skill_label",
                         rule="official_skill_mapping_392",
                         evidence={"path": str(CLOSURE), "sha256": file_sha(CLOSURE),
                                   "docx": evidence.get("docx"), "source_page": page})
        extra.append(op)
    rybin = next(row for row in closure["legacy_skill_occurrences"] if row.get("docx") == "p290")
    extra.append(exact_extra(documents, book=LEN, body_index=256,
                             before="Сокрытие +10%", after="Скрытность +10%",
                             entity="Rybin bodily entry", entity_anchor=anchor(len_doc, 256, self_context=True),
                             page=17, field="rybin_bodily_stealth", kind="prose_label",
                             rule="user_approved_exact_prose", choice="len-rybin-bodily-conceal",
                             evidence={"path": str(CLOSURE), "sha256": file_sha(CLOSURE),
                                       "docx": rybin["docx"], "source_page": 17}))
    boris_anchor = next(op["entity_anchor"] for op in operations if op["entity_id"] == "Борис Чурин")
    boris_evidence = next(row for row in closure["legacy_skill_occurrences"] if row.get("docx") == "p669")
    extra.append(exact_extra(documents, book=LEN, body_index=536,
                             before="Искусство", after="Искусство/ремесло",
                             entity="Борис Чурин", entity_anchor=boris_anchor,
                             page=33, field="skill:Искусство", kind="skill_label",
                             rule="official_skill_mapping_392",
                             evidence={"path": str(CLOSURE), "sha256": file_sha(CLOSURE),
                                       "docx": boris_evidence["docx"], "source_page": 33}))
    for index, before, after, page in (
        (271, "СИЛ двери равна 10", "СИЛ двери равна 50", 18),
        (302, "её СИЛ составляет 16", "её СИЛ составляет 80", 20),
    ):
        if not any(row.get("source_physical_page") == page and "Strength" in row.get("finding", "")
                   for row in qa["targeted_source_mechanics"]):
            raise ValueError(f"door STR {page}: source visual QA is absent")
        extra.append(exact_extra(documents, book=LEN, body_index=index,
                                 before=before, after=after, entity=f"door-{page}",
                                 entity_anchor=anchor(len_doc, index, self_context=True),
                                 page=page, field="СИЛ", kind="characteristic_prose",
                                 rule="source_bound_door_str_times_five", scale="old_edition",
                                 evidence={"path": str(SOURCE_QA), "sha256": file_sha(SOURCE_QA),
                                           "source_physical_page": page}))
    # Exact retained two-skill pairs in the two investigator tables.
    for entity, index, survivor_row, survivor_cell, survivor_value in (
        ("Леон Стерндейл", 636, 7, 2, "40%"),
        ("Коллин Палмер", 667, 10, 0, "32%"),
    ):
        entity_anchor = next(op["entity_anchor"] for op in operations if op["entity_id"] == entity)
        table = direct_body(len_doc)[index]
        rows = table.findall(W + "tr")
        def cell_text(ri, ci):
            return node_text(rows[ri].findall(W + "tc")[ci])
        if ([cell_text(1, 2), cell_text(1, 3), cell_text(survivor_row, survivor_cell),
             cell_text(survivor_row, survivor_cell + 1)] != ["Торг", "40%", "Убеждение", survivor_value]):
            raise ValueError(f"{entity}: exact duplicate/survivor table geometry differs")
        for action, ri, ci, before, after in (
            ("clear_duplicate_label", 1, 2, "Торг", ""),
            ("clear_duplicate_value", 1, 3, "40%", ""),
            *(([("set_survivor_value", survivor_row, survivor_cell + 1, "32%", "40%")]
               if survivor_value == "32%" else [])),
        ):
            extra.append(exact_extra(documents, book=LEN, body_index=index,
                                     row=ri, cell=ci, before=before, after=after,
                                     entity=entity, entity_anchor=entity_anchor,
                                     page=38 if entity.startswith("Леон") else 40,
                                     field="Убеждение", kind="skill_consolidation",
                                     rule="user_approved_local_skill_consolidation",
                                     choice="len-pregen-persuade-consolidation", action=action,
                                     evidence={"path": str(CHOICE2), "sha256": file_sha(CHOICE2),
                                               "decision_id": "len-pregen-persuade-consolidation"}))
    kre_doc = documents[KRE]
    for entity, index, page, labels in (
        ("Евгений Потапов", 237, 16, ("Русский язык", "Английский язык", "Немецкий язык", "Архитектура")),
        ("Иван", 242, 16, ("Русский язык", "Английский язык")),
        ("Николай", 247, 16, ("Русский язык", "Английский язык")),
    ):
        entity_anchor = next(op["entity_anchor"] for op in operations if op["entity_id"] == entity)
        map_labels = next(row for row in choice2["decisions"]
                          if row["id"] == "kremlin-language-parent-adaptation")["field_map"]
        for label in labels:
            architecture = label == "Архитектура"
            after = "Искусство/ремесло (Архитектура)" if architecture else map_labels[label]
            decision_id = "kremlin-potapov-architecture" if architecture else "kremlin-language-parent-adaptation"
            extra.append(exact_extra(documents, book=KRE, body_index=index,
                                     before=label, after=after, entity=entity,
                                     entity_anchor=entity_anchor, page=page,
                                     field="architecture" if architecture else "language",
                                     kind="user_label", rule="user_approved_exact_label",
                                     choice=decision_id,
                                     evidence={"paths": [str(CHOICE2), str(CLOSURE)],
                                               "sha256": [file_sha(CHOICE2), file_sha(CLOSURE)],
                                               "decision_id": decision_id, "source_page": page}))
    operations.extend(extra)
    if len(operations) != 197 or len({op["id"] for op in operations}) != len(operations):
        raise ValueError(f"exact 197-operation approved domain differs: {len(operations)}")
    # Katerina's source-proven characteristic-effect nodes are not flattened.
    katerina_anchor = next(op["entity_anchor"] for op in operations if op["entity_id"] == "Катерина, маленький вампир")
    effect_paths = [f"word/document.xml/body[310]/p/r[{ri}]/t[0]" for ri in (2, 3, 4)]
    effect_nodes = []
    for path, fragment_before, fragment_after, at_end in zip(
        effect_paths, ("1", "D", "6 СИЛ"), ("5 × (1", "D", "6) СИЛ"), (True, False, False)
    ):
        leaf, _, _ = _word_leaf(len_doc, path)
        old_node = leaf.text or ""
        start = len(old_node) - len(fragment_before) if at_end else 0
        end = start + len(fragment_before)
        if old_node[start:end] != fragment_before:
            raise ValueError(f"Katerina split-run fragment differs: {path}")
        new_node = old_node[:start] + fragment_after + old_node[end:]
        effect_nodes.append({"path": path, "before_node": old_node,
                             "before_node_sha256": sha(old_node.encode("utf-8")),
                             "before_node_xml_sha256": _node_xml_sha(leaf),
                             "span_start": start, "span_end": end,
                             "after_fragment": fragment_after,
                             "after_node": new_node, "after_node_sha256": sha(new_node.encode("utf-8")),
                             "after_node_xml_sha256": _predicted_node_xml_sha(leaf, new_node)})
    if not any(row.get("source_physical_page") == 20 and "1D6 STR" in row.get("finding", "")
               for row in qa["targeted_source_mechanics"]):
        raise ValueError("Katerina source-verified STR drain is absent")
    expression = {"id": f"{LEN}:v04:katerina-strength-drain", "book_id": LEN,
                  "entity_id": "Катерина, маленький вампир", "entity_anchor": katerina_anchor,
                  "field": "СИЛ", "rule_id": "official_characteristic_effect_times_five",
                  "current_scale": "old_edition", "source_verified": True,
                  "source_evidence": {"path": str(SOURCE_QA), "sha256": file_sha(SOURCE_QA),
                                      "source_physical_page": 20},
                  "source_pdf_sha256": source_inputs[LEN]["source_pdf_sha256"],
                  "source_pdf_path": source_inputs[LEN]["source_pdf_path"],
                  "source_physical_page": 20, "source_edition_evidence": "explicit fifth edition",
                  "before_expression": "1D6 СИЛ", "after_expression": "5 × (1D6) СИЛ",
                  "reverse_before_expression": "5 × (1D6) СИЛ",
                  "reverse_after_expression": "1D6 СИЛ", "nodes": effect_nodes}
    groups = node_groups(operations, documents)
    approved = {"schema": old["schema"], "state": "approved_source_bound_operations",
                "source_qa_closed": True, "orchestrator_approved": True,
                "approval_authority": {"packet_path": str(PACKET), "packet_sha256": file_sha(PACKET),
                                       "numeric_source_qa_path": str(SOURCE_QA),
                                       "numeric_source_qa_sha256": file_sha(SOURCE_QA),
                                       "closure_path": str(CLOSURE), "closure_sha256": file_sha(CLOSURE)},
                "inputs": source_inputs, "operation_count": len(operations),
                "operations": operations, "node_groups": groups,
                "expression_groups": [expression],
                "excluded_mechanics": ["Resistance Table prose", "MP drain", "Kremlin accreditation POW check",
                                       "source HP/MOV/DB/Luck/SAN/attack/damage/age fields"]}
    ledger_path = HERE / "approved-word-operations-v01.json"
    freeze_json(ledger_path, approved)
    review1, review2, inventory = read_json(REVIEW1), read_json(REVIEW2), read_json(COMMENTS)
    len_decisions = ([row for row in review1["decisions"] if row["issue_id"].startswith("LEN-")
                      and row["disposition"] == "keep"]
                     + review2["decisions"])
    len_inventory = next(row for row in inventory["books"] if row["book"] == LEN)
    for book in (LEN, KRE):
        document = documents[book]
        paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
        first_bookmark = next((name for p in paragraphs for name in p.xpath("./w:bookmarkStart/@w:name", namespaces=NS)), None)
        if not first_bookmark:
            raise ValueError(f"{book}: no first Word bookmark")
        keeps = keep_ops(document, len_decisions, len_inventory, first_bookmark) if book == LEN else []
        rels = _relationships(_xml(parts[book]["word/_rels/document.xml.rels"], "Word relationships"))
        original_drawings = _drawing_order(document, rels, parts[book])
        manifest = {"schema": "kb_creator.reviewed_docx_revision.v1",
                    "provenance": "reviewed_artifact_successor",
                    "scope": "exact source-bound DOCX-only numeric/name pass; no HTML/PDF",
                    "art_scope": "preserve_original_drawings_only",
                    "inputs": {"docx_sha256": file_sha(reviewed_paths[book]),
                               "source_pdf_sha256": source_inputs[book]["source_pdf_sha256"],
                               "authorities": [{"path": str(path), "sha256": file_sha(path)}
                                               for path in authorities + [CHOICE1, CHOICE2]
                                               if path not in (CHOICE1, CHOICE2)]
                                              + [{"path": str(CHOICE1), "sha256": file_sha(CHOICE1)},
                                                 {"path": str(CHOICE2), "sha256": file_sha(CHOICE2)}],
                               "original_drawing_occurrences": [
                                   {"sha256": image_sha, "drawing_id": drawing_id}
                                   for image_sha, drawing_id in original_drawings]},
                    "stories": [{"story_id": "whole_book", "word_bookmark": first_bookmark}],
                    "source_graphic_ids": [], "source_graphics": [], "operations": keeps,
                    "source_bound_fields": {"book_id": book,
                                            "ledger": {"path": str(ledger_path), "sha256": file_sha(ledger_path)},
                                            "choices": {"path": str(HERE / "accepted-choices-combined-v01.json"),
                                                        "sha256": file_sha(HERE / "accepted-choices-combined-v01.json")},
                                            "conversion_spec": {"path": str(SPEC), "sha256": file_sha(SPEC)},
                                            "operation_ids": [op["id"] for op in operations if op["book_id"] == book],
                                            "expression_ids": [expression["id"]] if book == LEN else []}}
        freeze_json(HERE / f"{book}-manifest-v01.json", manifest)
    print(json.dumps({"approved_operations": len(operations),
                      "numeric": len(numeric_ids), "new_operations": len(extra),
                      "node_groups": len(groups), "split_expressions": 1,
                      "books": {book: {"operations": sum(op["book_id"] == book for op in operations),
                                       "old_drawings": len(_drawing_order(documents[book],
                                           _relationships(_xml(parts[book]["word/_rels/document.xml.rels"], "rels")),
                                           parts[book]))} for book in (LEN, KRE)}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
