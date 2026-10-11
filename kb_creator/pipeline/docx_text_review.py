"""Identity-bound coverage evidence for a complete human DOCX text read.

This module extracts visible OOXML text for a review checklist.  It does not
judge prose or claim that an extractor has proofread a document.
"""
from __future__ import annotations

import copy
import json
import zipfile
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

from .identity import canonical_bytes, file_identity, sha256_bytes
from .manifests import sealed, validate_seal


class DocxTextReviewError(ValueError):
    """Raised when DOCX text coverage cannot be proven safely."""


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
TAG_P = f"{{{W}}}p"
TAG_T = f"{{{W}}}t"
TAG_TAB = f"{{{W}}}tab"
TAG_BR = f"{{{W}}}br"
TAG_CR = f"{{{W}}}cr"
TAG_TBL = f"{{{W}}}tbl"
TAG_TXBX = f"{{{W}}}txbxContent"
TAG_COMMENT = f"{{{W}}}comment"

TASK_SCHEMA = "kb_creator.docx_text_review_task.v1"
SUBMISSION_SCHEMA = "kb_creator.docx_text_review_submission.v1"
RECORD_SCHEMA = "kb_creator.docx_text_review_record.v1"


def _xml_text(paragraph: ET.Element) -> str:
    """Read displayed paragraph text, including runs inside hyperlinks."""
    chunks: list[str] = []
    def visit(node: ET.Element) -> None:
        # Text-box paragraphs are separate review blocks.  Do not let an
        # enclosing body paragraph consume their text a second time.
        if node is not paragraph and node.tag == TAG_P:
            return
        if node.tag == TAG_T:
            chunks.append(node.text or "")
        elif node.tag == TAG_TAB:
            chunks.append("\t")
        elif node.tag in (TAG_BR, TAG_CR):
            chunks.append("\n")
        for child in node:
            visit(child)
    visit(paragraph)
    return "".join(chunks)


def _parents(root: ET.Element) -> dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in parent}


def _has_ancestor(node: ET.Element, parents: dict[ET.Element, ET.Element], tag: str) -> bool:
    parent = parents.get(node)
    while parent is not None:
        if parent.tag == tag:
            return True
        parent = parents.get(parent)
    return False


def _ancestor(node: ET.Element, parents: dict[ET.Element, ET.Element], tag: str) -> ET.Element | None:
    parent = parents.get(node)
    while parent is not None:
        if parent.tag == tag:
            return parent
        parent = parents.get(parent)
    return None


def _container(node: ET.Element, parents: dict[ET.Element, ET.Element]) -> str:
    if _has_ancestor(node, parents, TAG_TXBX):
        return "textbox"
    if _has_ancestor(node, parents, TAG_TBL):
        return "table_cell"
    return "paragraph"


def _iter_part_blocks(part: str, data: bytes) -> Iterable[dict[str, Any]]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise DocxTextReviewError(f"invalid OOXML text part: {part}") from exc
    parents = _parents(root)
    ordinal = 0
    for paragraph in root.iter(TAG_P):
        # A text-box paragraph belongs to the text-box stream.  Its enclosing
        # body paragraph is never duplicated because it has no direct text.
        text = _xml_text(paragraph)
        if not text:
            continue
        ordinal += 1
        comment = _ancestor(paragraph, parents, TAG_COMMENT) if part == "word/comments.xml" else None
        if part == "word/comments.xml" and (comment is None or not comment.get(f"{{{W}}}id")):
            raise DocxTextReviewError("comment text paragraph lacks a source comment id")
        container = "comment" if comment is not None else _container(paragraph, parents)
        locator = {"part": part, "container": container, "ordinal": ordinal}
        if comment is not None:
            locator["comment_id"] = comment.get(f"{{{W}}}id")
        yield {
            **locator,
            "block_id": "docx-text-" + sha256_bytes(canonical_bytes(locator))[:24],
            "text": text,
            "text_sha256": sha256_bytes(text.encode("utf-8")),
        }


def _known_text_parts(names: Iterable[str]) -> list[str]:
    result = []
    for name in names:
        if name == "word/document.xml" or name in {"word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"}:
            result.append(name)
        elif name.startswith("word/header") and name.endswith(".xml"):
            result.append(name)
        elif name.startswith("word/footer") and name.endswith(".xml"):
            result.append(name)
    return sorted(result, key=lambda item: (item != "word/document.xml", item))


def _visible_text_in_unknown_part(name: str, data: bytes) -> bool:
    if not name.startswith("word/") or not name.endswith(".xml"):
        return False
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise DocxTextReviewError(f"invalid OOXML part: {name}") from exc
    return any((node.text or "") for node in root.iter(TAG_T))


def extract_visible_text_blocks(docx_path: Path) -> list[dict[str, Any]]:
    """Extract every supported visible-text block in deterministic OOXML order.

    Any Word XML part with text outside body/header/footer/footnote/endnote/comment
    containers is rejected so a caller cannot mistake partial coverage for a
    full read.
    """
    if not docx_path.is_file() or docx_path.suffix.lower() != ".docx":
        raise DocxTextReviewError(f"DOCX file required: {docx_path}")
    try:
        with zipfile.ZipFile(docx_path) as archive:
            names = archive.namelist()
            if "word/document.xml" not in names:
                raise DocxTextReviewError("DOCX lacks word/document.xml")
            known = set(_known_text_parts(names))
            unsupported = [
                name for name in names
                if name not in known and _visible_text_in_unknown_part(name, archive.read(name))
            ]
            if unsupported:
                raise DocxTextReviewError(
                    "unsupported OOXML visible-text container(s): " + ", ".join(sorted(unsupported))
                )
            blocks = [block for part in _known_text_parts(names) for block in _iter_part_blocks(part, archive.read(part))]
    except zipfile.BadZipFile as exc:
        raise DocxTextReviewError(f"invalid DOCX archive: {docx_path}") from exc
    if not blocks:
        raise DocxTextReviewError("DOCX has no visible text blocks to review")
    return blocks


def _task_blocks_digest(blocks: list[dict[str, Any]]) -> str:
    projection = [
        {key: block[key] for key in ("block_id", "part", "container", "ordinal", "text_sha256")}
        for block in blocks
    ]
    return sha256_bytes(canonical_bytes(projection))


def prepare_docx_text_review(docx_path: Path) -> dict[str, Any]:
    """Create a sealed task that binds review coverage to one exact DOCX."""
    docx_path = docx_path.resolve()
    blocks = extract_visible_text_blocks(docx_path)
    return sealed(
        TASK_SCHEMA,
        {
            "docx": {"path": docx_path.name, **file_identity(docx_path)},
            "blocks": blocks,
            "blocks_sha256": _task_blocks_digest(blocks),
        },
        digest_key="task_sha256",
    )


def validate_docx_text_review(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    """Validate exhaustive ordered human-read assertions and resolved findings."""
    if task.get("schema") != TASK_SCHEMA:
        raise DocxTextReviewError("unsupported DOCX text review task")
    validate_seal(task, "task_sha256")
    if task.get("blocks_sha256") != _task_blocks_digest(task.get("blocks", [])):
        raise DocxTextReviewError("task block inventory mismatch")
    if submission.get("schema") != SUBMISSION_SCHEMA:
        raise DocxTextReviewError("unsupported DOCX text review submission")
    required = {"schema", "task_sha256", "docx", "reviewer_role", "blocks", "findings"}
    if set(submission) != required:
        raise DocxTextReviewError("submission has unsupported fields")
    if submission["task_sha256"] != task["task_sha256"] or submission["docx"] != task["docx"]:
        raise DocxTextReviewError("stale or foreign DOCX text review submission")
    if submission["reviewer_role"] != "agent":
        raise DocxTextReviewError("DOCX text review requires reviewer_role=agent")
    expected = task["blocks"]
    rows = submission["blocks"]
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise DocxTextReviewError("full DOCX block coverage required")
    for expected_block, row in zip(expected, rows):
        if set(row) != {"block_id", "text_sha256", "read"}:
            raise DocxTextReviewError("review block has unsupported fields")
        if row["block_id"] != expected_block["block_id"] or row["text_sha256"] != expected_block["text_sha256"]:
            raise DocxTextReviewError("review block identity or order mismatch")
        if row["read"] is not True:
            raise DocxTextReviewError("every DOCX text block must be marked read")
    identifiers: set[str] = set()
    for finding in submission["findings"]:
        if set(finding) != {"finding_id", "block_id", "status", "resolution"}:
            raise DocxTextReviewError("finding has unsupported fields")
        if not isinstance(finding["finding_id"], str) or not finding["finding_id"] or finding["finding_id"] in identifiers:
            raise DocxTextReviewError("finding id must be unique and nonempty")
        identifiers.add(finding["finding_id"])
        if finding["block_id"] not in {block["block_id"] for block in expected}:
            raise DocxTextReviewError("finding references unknown block")
        if finding["status"] != "resolved" or not isinstance(finding["resolution"], str) or not finding["resolution"].strip():
            raise DocxTextReviewError("unresolved DOCX text review finding")
    payload = copy.deepcopy(submission)
    payload.pop("schema")
    return sealed(RECORD_SCHEMA, payload, digest_key="record_sha256")


def write_docx_text_review_task(docx_path: Path, output_path: Path) -> dict[str, Any]:
    task = prepare_docx_text_review(docx_path)
    output_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return task


def record_docx_text_review(task_path: Path, submission_path: Path, output_path: Path) -> dict[str, Any]:
    task = json.loads(task_path.read_text(encoding="utf-8"))
    submission = json.loads(submission_path.read_text(encoding="utf-8"))
    record = validate_docx_text_review(task, submission)
    output_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record
