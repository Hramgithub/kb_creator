"""Freeze the bounded Fear DOCX-only manifest from audited, exact inputs.

This adapter is book-specific evidence. The reusable writer lives in pipeline/.
It reads the old DOCX and frozen audit files, and writes no reader artifact.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from kb_creator.pipeline.reviewed_docx_revision import _word_bounds
from kb_creator.pipeline.reviewed_reader_revision import (
    NS, WP, _bookmark, _drawing_order, _media_for_drawing, _paragraph_text,
    _relationships, _xml,
)
from kb_creator.scripts.production_docx import bookmark_name


ROOT = Path(__file__).resolve().parents[6]
GOAL = ROOT / "kb_creator/docs/plans/20261004-user-docx-review"
AUDIT = GOAL / "audit"
DOCX = ROOT / "kb_creator/deliverables/latest/fears-sharp-little-needles/document.docx"
ART_ROOT = ROOT / "kb_creator/working/user-review-20261004/fear-source-art-v01"
OUTPUT = Path(__file__).with_name("fear-docx-only-manifest-v01.json")
PAGES = [8, 14, 19, 24, 29, 35, 41, 46, 51, 57, 63, 69, 74, 79,
         86, 92, 97, 103, 109, 113, 119, 124, 129, 135, 141, 147]
RETAINED = {46: "spilsberi-9485-2", 113: "dissotsiatsiya-2", 129: "prizraki-reivenskara-2"}
END_OFFSET = {8: 2, 14: 2, 19: 2, 24: 1, 29: 2, 35: 5, 41: 2,
              51: 2, 57: 2, 63: 5, 69: 2, 74: 2, 79: 2, 86: 2,
              92: 3, 97: 2, 103: 5, 109: 2, 119: 2, 124: 6,
              135: 2, 141: 2, 147: 2}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def exact_selector(paragraphs: list, start: int, end: int, target) -> dict:
    text = _paragraph_text(target)
    matches = [p for p in paragraphs[start:end] if _paragraph_text(p) == text]
    return {"kind": "exact_paragraph", "expected_matches": len(matches),
            "ordinal": matches.index(target)}


def main() -> None:
    decisions_path = AUDIT / "review-decisions-v01.json"
    comments_path = AUDIT / "comments/comments_inventory.json"
    spec_path = AUDIT / "art/native-recovery-spec.json"
    assets_path = ART_ROOT / "manifest.json"
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    comments = json.loads(comments_path.read_text(encoding="utf-8"))
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    assets = json.loads(assets_path.read_text(encoding="utf-8"))
    pdf_path = Path(spec["source_identity"]["path"])
    if (file_sha(DOCX) != spec["reviewed_docx_sha256"]
            or file_sha(pdf_path) != spec["source_identity"]["sha256"]
            or assets["selection_sha256"] != file_sha(spec_path)):
        raise ValueError("frozen DOCX/PDF/art-spec identity differs")
    selections = {row["source_page"]: row for row in spec["selections"]}
    art_assets = {row["source_page"]: row for row in assets["assets"]}
    if set(selections) != set(art_assets) or set(selections) != set(END_OFFSET):
        raise ValueError("the 23 source-art selections do not close")
    if set(PAGES) != set(selections) | set(RETAINED) or len(PAGES) != 26:
        raise ValueError("26 independently reviewed opening pages do not close")
    with zipfile.ZipFile(DOCX) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    document = _xml(parts["word/document.xml"], "document.xml")
    rels = _relationships(_xml(parts["word/_rels/document.xml.rels"], "rels"))
    paragraphs = document.xpath(".//w:body//w:p", namespaces=NS)
    stories = [{"story_id": "front", "word_bookmark": "nri_9f95a2d81abb4b27e3ae10ef80e9aff0"}]
    for page in PAGES:
        anchor = RETAINED.get(page) or selections[page]["html_heading_anchor"]
        bookmark = bookmark_name(anchor)
        if page in selections and bookmark != selections[page]["docx_heading_binding"]["bookmark"]:
            raise ValueError(f"page {page} frozen Word bookmark differs")
        stories.append({"story_id": f"opening-{page:03d}", "word_bookmark": bookmark})
    bounds = _word_bounds(stories, document)
    source_graphics = []
    operations = []
    for page in PAGES:
        sid = f"opening-{page:03d}"
        gid = sid
        span = bounds[sid]
        start = span["word_start"]
        if page in RETAINED:
            drawings = [(p, d) for p in paragraphs[start:span["word_end"]]
                        for d in p.xpath(".//w:drawing", namespaces=NS)]
            if not drawings or paragraphs.index(drawings[0][0]) > start + 9:
                raise ValueError(f"page {page} lacks reviewed opening artwork")
            drawing = drawings[0][1]
            docpr = drawing.find(".//" + WP + "docPr")
            if docpr is None:
                raise ValueError(f"page {page} opening drawing lacks identity")
            source_graphics.append({"graphic_id": gid, "story_id": sid,
                                    "source_page": page, "disposition": "must_include",
                                    "sha256": _media_for_drawing(drawing, rels, parts),
                                    "occurrence_ordinal": 0, "drawing_id": docpr.get("id"),
                                    "legacy_descr": docpr.get("descr")})
            continue
        selected = selections[page]
        asset = art_assets[page]
        if (asset["html_heading_anchor"] != selected["html_heading_anchor"]
                or asset["sha256"] != selected.get("candidate_selected_sha256", selected.get("candidate_png_sha256"))
                or list(asset["dimensions"]) != list(selected["source_pixel_size"])
                or file_sha(ART_ROOT / asset["path"]) != asset["sha256"]):
            raise ValueError(f"page {page} selected art bytes/provenance differ")
        heading = _bookmark(document, stories[PAGES.index(page) + 1]["word_bookmark"])
        if paragraphs.index(heading) != start:
            raise ValueError(f"page {page} heading paragraph differs")
        paragraph = paragraphs[start + END_OFFSET[page]]
        if paragraph.xpath(".//w:drawing", namespaces=NS):
            raise ValueError(f"page {page} opener end is already artwork")
        text = _paragraph_text(paragraph)
        if not text:
            raise ValueError(f"page {page} opener end is blank")
        source_graphics.append({"graphic_id": gid, "story_id": sid,
                                "source_page": page, "disposition": "must_include",
                                "sha256": asset["sha256"], "occurrence_ordinal": 0})
        operations.append({"kind": "art", "graphic_id": gid, "story_id": sid,
                           "word_bookmark": stories[PAGES.index(page) + 1]["word_bookmark"],
                           "source_page": page, "source_image": str(ART_ROOT / asset["path"]),
                           "sha256": asset["sha256"], "dimensions": asset["dimensions"],
                           "word_width_inches": 5.5,
                           "insertion": "after_exact_paragraph",
                           "position": {"expected_text": text,
                                        "expected_text_sha256": sha(text.encode("utf-8")),
                                        "selector": exact_selector(paragraphs, start, span["word_end"], paragraph)}})
    fear_decisions = [row for row in decisions["decisions"] if row["issue_id"].startswith("fear-")]
    if len(fear_decisions) != 11:
        raise ValueError("expected exactly six replace and five keep decisions")
    fear_book = next(book for book in comments["books"] if book["book"] == "fears-sharp-little-needles")
    roots = {row["root_issue_id_candidate"]: row for row in fear_book["threads"]
             if row.get("root_issue_id_candidate")}
    for decision in fear_decisions:
        issue = decision["issue_id"]
        root = roots[issue]
        comment_id = root["comment_id"]
        matched = [p for p in paragraphs if comment_id in p.xpath("./w:commentRangeStart/@w:id", namespaces=NS)]
        if len(matched) != 1:
            raise ValueError(f"{issue}: root comment paragraph missing or ambiguous")
        paragraph = matched[0]
        text = _paragraph_text(paragraph)
        if text != root["anchor"]["paragraph_text"]:
            raise ValueError(f"{issue}: reviewed native anchor text differs")
        index = paragraphs.index(paragraph)
        sid = next((name for name, span in bounds.items()
                    if span["word_start"] <= index < span["word_end"]), None)
        if sid is None:
            raise ValueError(f"{issue}: outside bound Word stories")
        span = bounds[sid]
        op = {"kind": "text" if decision["disposition"] == "replace" else "keep",
              "disposition": decision["disposition"], "issue_id": issue,
              "story_id": sid, "word_bookmark": span["word_bookmark"],
              "comment_id": comment_id, "expected_text": text,
              "expected_text_sha256": sha(text.encode("utf-8")),
              "selector": exact_selector(paragraphs, span["word_start"], span["word_end"], paragraph)}
        if op["kind"] == "text":
            if text.count(decision["old"]) != 1:
                raise ValueError(f"{issue}: old target is not unique in native comment paragraph")
            op.update(target_text=decision["old"], replacement=decision["new"])
        else:
            op["reason"] = decision.get("reason") or decision["user_text"]
        operations.insert(0, op)
    if sum(op["kind"] == "text" for op in operations) != 6 or sum(op["kind"] == "keep" for op in operations) != 5:
        raise ValueError("review decision operation counts differ")
    authorities = [{"path": str(path), "sha256": file_sha(path)}
                   for path in (decisions_path, comments_path, spec_path, assets_path)]
    manifest = {"schema": "kb_creator.reviewed_docx_revision.v1",
                "provenance": "reviewed_artifact_successor",
                "scope": "Fear DOCX-only candidate; no HTML/PDF export; no new translation/OCR",
                "inputs": {"docx_sha256": file_sha(DOCX), "source_pdf_sha256": file_sha(pdf_path),
                           "authorities": authorities,
                           "original_drawing_occurrences": [
                               {"sha256": image_sha, "drawing_id": drawing_id}
                               for image_sha, drawing_id in _drawing_order(document, rels, parts)]},
                "stories": stories,
                "source_graphic_ids": [f"opening-{page:03d}" for page in PAGES],
                "source_graphics": source_graphics,
                "operations": operations}
    if OUTPUT.exists():
        raise ValueError("immutable Fear manifest already exists")
    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(OUTPUT), "sha256": file_sha(OUTPUT),
                      "stories": len(stories), "opening_obligations": len(source_graphics),
                      "insertions": sum(op["kind"] == "art" for op in operations),
                      "text_edits": 6, "keeps": 5, "old_drawing_occurrences": len(manifest["inputs"]["original_drawing_occurrences"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
