from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path
from typing import Any

from audit_innsmouth_keeper_pdf_structure import (
    count_text_chars,
    first_meaningful_line,
    normalize_spaces,
    pdf_page_records,
)
from build_innsmouth_source_to_artifacts import ROOT, SOURCE_PDF, rel, sha256_file, split_source_pages, write_json


RUN_ID = "20260730T210831Z"
DEFAULT_SOURCE = (
    ROOT
    / "kb_creator/working/innsmouth_source_to_artifacts/runs"
    / RUN_ID
    / "Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md"
)
DEFAULT_REPORT_DIR = ROOT / "kb_creator/reports/innsmouth_source_to_artifacts/runs" / RUN_ID


def source_text_blocks(page_text: str) -> list[str]:
    text = re.sub(r"<!--\s*empty-or-image-only-page\s*-->", "", page_text)
    blocks: list[str] = []
    for block in re.split(r"\n\s*\n+", text):
        block = normalize_spaces(block)
        if block:
            blocks.append(block)
    return blocks


def normalize_for_compare(text: str) -> str:
    text = re.sub(r"<!--\s*empty-or-image-only-page\s*-->", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def line_position(page_text: str, line: str) -> int:
    if not line:
        return -1
    normalized_page = normalize_for_compare(page_text)
    normalized_line = normalize_spaces(line)
    pos = normalized_page.find(normalized_line)
    if pos >= 0:
        return pos
    # Tolerate typographic fragments/hyphen fixes by matching a few stable tokens.
    tokens = re.findall(r"[A-Za-z][A-Za-z'’.-]{2,}|\d{2,4}", normalized_line)
    if len(tokens) < 2:
        return -1
    pattern = r".{0,80}".join(re.escape(token) for token in tokens[:4])
    match = re.search(pattern, normalized_page, flags=re.IGNORECASE | re.DOTALL)
    return match.start() if match else -1


def compare_blocks(pdf_text: str, source_page_text: str) -> dict[str, Any]:
    pdf_norm = normalize_for_compare(pdf_text)
    source_norm = normalize_for_compare(source_page_text)
    return {
        "exact": pdf_norm == source_norm,
        "similarity": round(difflib.SequenceMatcher(None, pdf_norm, source_norm).ratio(), 5)
        if pdf_norm or source_norm
        else 1.0,
        "pdf_chars_no_ws": count_text_chars(pdf_norm),
        "source_chars_no_ws": count_text_chars(source_norm),
        "char_delta": count_text_chars(source_norm) - count_text_chars(pdf_norm),
    }


def detect_fragile_flow(row: dict[str, Any], source_blocks: list[str], source_page_text: str) -> list[str]:
    flags: list[str] = []
    has_markdown_table = bool(re.search(r"(?m)^\|\s*[^|\n]+\s*\|.*\n\|\s*-+", source_page_text))
    left = str(row.get("pdf_left_first_line") or "")
    right = str(row.get("pdf_right_first_line") or "")
    if left and right:
        left_pos = line_position(source_page_text, left)
        right_pos = line_position(source_page_text, right)
        if left_pos >= 0 and right_pos >= 0 and left_pos > right_pos:
            flags.append("left_right_order_inverted")
        if right_pos >= 0 and len(source_blocks) >= 2:
            first_block = source_blocks[0]
            if right in first_block and len(first_block) > 220:
                flags.append("right_column_continuation_inside_first_block")
            elif right_pos > 800 and re.search(r"[a-z,;:]$", left):
                flags.append("possible_cross_column_sentence_split")
    if len(source_blocks) <= 3 and int(row.get("pdf_paragraph_blocks") or 0) >= 10 and not has_markdown_table:
        flags.append("paragraphs_collapsed_in_normalized_source")
    if int(row.get("pdf_chars_no_ws") or 0) and int(row.get("source_chars_no_ws") or 0) == 0:
        flags.append("source_page_text_missing")
    return flags


def build_report(source_markdown: Path) -> dict[str, Any]:
    source_text = source_markdown.read_text(encoding="utf-8", errors="replace")
    source_pages = split_source_pages(source_text)
    pdf_pages = pdf_page_records()
    rows: list[dict[str, Any]] = []

    for page_id in sorted(set(pdf_pages) | set(source_pages)):
        pdf_page = pdf_pages.get(page_id, {})
        source_page = source_pages.get(page_id, "")
        source_blocks = source_text_blocks(source_page)
        comparison = compare_blocks(str(pdf_page.get("text") or ""), source_page)
        pdf_blocks = int(pdf_page.get("paragraph_blocks") or 0)
        source_block_count = len(source_blocks)
        block_delta = source_block_count - pdf_blocks
        row = {
            "page": page_id,
            "pdf_chars_no_ws": comparison["pdf_chars_no_ws"],
            "source_chars_no_ws": comparison["source_chars_no_ws"],
            "char_delta": comparison["char_delta"],
            "exact_against_current_extractor": comparison["exact"],
            "similarity_against_current_extractor": comparison["similarity"],
            "pdf_paragraph_blocks": pdf_blocks,
            "source_blocks": source_block_count,
            "block_delta": block_delta,
            "pdf_columns": ",".join(pdf_page.get("columns") or []),
            "pdf_left_first_line": pdf_page.get("left_first_line") or "",
            "pdf_right_first_line": pdf_page.get("right_first_line") or "",
            "source_first_blocks": " / ".join(source_blocks[:3]),
        }
        row["flags"] = detect_fragile_flow(row, source_blocks, source_page)
        rows.append(row)

    exact_pages = [row["page"] for row in rows if row["exact_against_current_extractor"]]
    non_exact_pages = [row["page"] for row in rows if not row["exact_against_current_extractor"]]
    flagged_pages = [row["page"] for row in rows if row["flags"]]
    return {
        "schema": "kb_creator.innsmouth_source_pdf_integrity_audit.v1",
        "source_pdf": {"path": str(SOURCE_PDF), "sha256": sha256_file(SOURCE_PDF)},
        "normalized_source_markdown": {"path": rel(source_markdown), "sha256": sha256_file(source_markdown)},
        "summary": {
            "pages": len(rows),
            "exact_pages": len(exact_pages),
            "non_exact_pages": non_exact_pages,
            "flagged_pages": flagged_pages,
            "max_abs_char_delta": max((abs(int(row["char_delta"])) for row in rows), default=0),
        },
        "rows": rows,
    }


def markdown_table(report: dict[str, Any]) -> str:
    lines = [
        "# Innsmouth EN PDF vs Normalized EN Source Integrity Audit",
        "",
        f"Source PDF: `{report['source_pdf']['path']}`",
        "",
        f"Normalized source: `{report['normalized_source_markdown']['path']}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in report["summary"].items():
        if isinstance(value, list):
            value = ", ".join(value) if value else "-"
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Page Table",
            "",
            "| Page | PDF chars | Source chars | Delta | Exact | Similarity | PDF blocks | Source blocks | Block delta | Columns | Left first line | Right first line | Source first blocks | Flags |",
            "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["rows"]:
        def cell(value: Any) -> str:
            text = str(value if value is not None else "")
            text = text.replace("|", "\\|").replace("\n", " ")
            return text[:220] + ("..." if len(text) > 220 else "")

        lines.append(
            "| {page} | {pdf_chars} | {source_chars} | {delta} | {exact} | {sim} | {pdf_blocks} | {source_blocks} | {block_delta} | {cols} | {left} | {right} | {first_blocks} | {flags} |".format(
                page=row["page"],
                pdf_chars=row["pdf_chars_no_ws"],
                source_chars=row["source_chars_no_ws"],
                delta=row["char_delta"],
                exact="yes" if row["exact_against_current_extractor"] else "no",
                sim=row["similarity_against_current_extractor"],
                pdf_blocks=row["pdf_paragraph_blocks"],
                source_blocks=row["source_blocks"],
                block_delta=row["block_delta"],
                cols=cell(row["pdf_columns"]),
                left=cell(row["pdf_left_first_line"]),
                right=cell(row["pdf_right_first_line"]),
                first_blocks=cell(row["source_first_blocks"]),
                flags=", ".join(row["flags"]),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()

    report = build_report(args.source)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / "source_pdf_integrity_audit.json"
    md_path = args.report_dir / "source_pdf_integrity_audit.md"
    write_json(json_path, report)
    md_path.write_text(markdown_table(report), encoding="utf-8")
    print(
        "status=pass "
        f"pages={report['summary']['pages']} "
        f"non_exact={len(report['summary']['non_exact_pages'])} "
        f"flagged={len(report['summary']['flagged_pages'])} "
        f"report={rel(md_path)}"
    )


if __name__ == "__main__":
    main()
