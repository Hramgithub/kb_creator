from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pdfplumber

from build_innsmouth_source_to_artifacts import (
    ROOT,
    SOURCE_PDF,
    lines_to_structured_blocks,
    ordered_structured_page_lines,
    rel,
    sha256_file,
    split_source_pages,
    words_to_structured_lines,
    write_json,
)


RUN_ID = "20260730T210831Z"
DEFAULT_KEEPER = (
    ROOT / "kb_creator/output/innsmouth_source_to_artifacts/runs" / RUN_ID / "For_Keeper/KeeperBook.md"
)
DEFAULT_REPORT_DIR = ROOT / "kb_creator/reports/innsmouth_source_to_artifacts/runs" / RUN_ID


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def count_text_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def strip_keeper_service_blocks(text: str) -> str:
    text = re.sub(r"<!--\s*source-page-\d{3}\s*-->", "", text)
    text = re.sub(r"<div class=\"keeper-art-block\".*?</div>", "", text, flags=re.DOTALL)
    text = re.sub(r"<table.*?</table>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def keeper_text_blocks(page_text: str) -> list[str]:
    clean = strip_keeper_service_blocks(page_text)
    blocks: list[str] = []
    for block in re.split(r"\n\s*\n+", clean):
        block = normalize_spaces(block)
        if not block:
            continue
        if block.startswith("|") and block.endswith("|"):
            continue
        blocks.append(block)
    return blocks


def anchor_pattern_for_pdf_line(line: str) -> str | None:
    tokens = re.findall(r"[A-Za-z][A-Za-z'’.-]{2,}|\d{2,4}", line)
    useful: list[str] = []
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "into",
        "they",
        "their",
        "there",
        "page",
        "keeper",
        "note",
    }
    for token in tokens:
        clean = token.strip(".'’-").lower()
        if len(clean) < 3 or clean in stop:
            continue
        useful.append(token)
        if len(useful) >= 3:
            break
    if not useful:
        return None
    return r".{0,80}".join(re.escape(token) for token in useful)


def find_anchor_position(keeper_page_text: str, pdf_line: str) -> int:
    pattern = anchor_pattern_for_pdf_line(pdf_line)
    if not pattern:
        return -1
    match = re.search(pattern, keeper_page_text, flags=re.IGNORECASE | re.DOTALL)
    return match.start() if match else -1


def first_meaningful_line(lines: list[dict[str, Any]], column: str) -> str:
    for line in lines:
        if line.get("column") != column:
            continue
        text = normalize_spaces(str(line.get("text") or ""))
        if len(text) < 4:
            continue
        if re.fullmatch(r"\d{1,3}", text):
            continue
        return text
    return ""


def pdf_page_records() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    with pdfplumber.open(SOURCE_PDF) as doc:
        for index, page in enumerate(doc.pages, start=1):
            page_id = f"{index:03d}"
            words = page.extract_words(
                keep_blank_chars=False,
                use_text_flow=False,
                extra_attrs=["upright"],
                x_tolerance=1.5,
                y_tolerance=2.5,
            )
            lines = words_to_structured_lines(words, float(page.width), float(page.height))
            ordered_lines = ordered_structured_page_lines(lines)
            blocks = lines_to_structured_blocks(ordered_lines)
            text = "\n\n".join(str(block.get("text") or "") for block in blocks if block.get("text"))
            columns = sorted({str(line.get("column")) for line in lines if line.get("column")})
            records[page_id] = {
                "text": text,
                "chars_no_ws": count_text_chars(text),
                "paragraph_blocks": len([block for block in blocks if str(block.get("text") or "").strip()]),
                "columns": columns,
                "left_first_line": first_meaningful_line(lines, "left"),
                "right_first_line": first_meaningful_line(lines, "right"),
                "full_first_line": first_meaningful_line(lines, "full"),
            }
    return records


def order_status(keeper_page_text: str, left_line: str, right_line: str) -> tuple[str, int, int]:
    left_pos = find_anchor_position(keeper_page_text, left_line) if left_line else -1
    right_pos = find_anchor_position(keeper_page_text, right_line) if right_line else -1
    if not left_line or not right_line:
        return ("not_applicable", left_pos, right_pos)
    if normalize_spaces(left_line).lower() == normalize_spaces(right_line).lower():
        return ("ambiguous", left_pos, right_pos)
    if left_pos < 0 or right_pos < 0:
        return ("not_testable", left_pos, right_pos)
    if left_pos == right_pos:
        return ("ambiguous", left_pos, right_pos)
    if left_pos < right_pos:
        return ("pass", left_pos, right_pos)
    return ("fail", left_pos, right_pos)


def build_report(keeper: Path) -> dict[str, Any]:
    keeper_text = keeper.read_text(encoding="utf-8", errors="replace")
    keeper_pages = split_source_pages(keeper_text)
    pdf_pages = pdf_page_records()
    rows: list[dict[str, Any]] = []

    for page_id in sorted(set(pdf_pages) | set(keeper_pages)):
        pdf_page = pdf_pages.get(page_id, {})
        keeper_page = keeper_pages.get(page_id, "")
        keeper_blocks = keeper_text_blocks(keeper_page)
        keeper_chars = count_text_chars(strip_keeper_service_blocks(keeper_page))
        pdf_chars = int(pdf_page.get("chars_no_ws") or 0)
        keeper_paragraphs = len(keeper_blocks)
        pdf_paragraphs = int(pdf_page.get("paragraph_blocks") or 0)
        ratio = round(keeper_chars / pdf_chars, 3) if pdf_chars else None
        paragraph_ratio = round(keeper_paragraphs / pdf_paragraphs, 3) if pdf_paragraphs else None
        status, left_pos, right_pos = order_status(
            keeper_page,
            str(pdf_page.get("left_first_line") or ""),
            str(pdf_page.get("right_first_line") or ""),
        )
        flags: list[str] = []
        if pdf_chars and keeper_chars and (ratio is not None) and (ratio < 0.55 or ratio > 2.2):
            flags.append("char_ratio_review")
        if pdf_paragraphs and keeper_paragraphs and paragraph_ratio is not None and (
            paragraph_ratio < 0.45 or paragraph_ratio > 2.4
        ):
            flags.append("paragraph_ratio_review")
        if status == "fail":
            flags.append("column_order_failed")
        rows.append(
            {
                "page": page_id,
                "pdf_chars_no_ws": pdf_chars,
                "keeper_chars_no_ws": keeper_chars,
                "char_ratio_keeper_over_pdf": ratio,
                "pdf_paragraph_blocks": pdf_paragraphs,
                "keeper_text_blocks": keeper_paragraphs,
                "paragraph_ratio_keeper_over_pdf": paragraph_ratio,
                "pdf_columns": ",".join(pdf_page.get("columns") or []),
                "pdf_left_first_line": pdf_page.get("left_first_line") or "",
                "pdf_right_first_line": pdf_page.get("right_first_line") or "",
                "keeper_first_blocks": " / ".join(keeper_blocks[:3]),
                "keeper_left_anchor_pos": left_pos,
                "keeper_right_anchor_pos": right_pos,
                "column_order_status": status,
                "flags": flags,
            }
        )

    return {
        "schema": "kb_creator.innsmouth_keeper_pdf_structure_audit.v1",
        "source_pdf": {"path": str(SOURCE_PDF), "sha256": sha256_file(SOURCE_PDF)},
        "keeper_markdown": {"path": rel(keeper), "sha256": sha256_file(keeper)},
        "rows": rows,
        "summary": {
            "pages": len(rows),
            "column_order_pass": sum(1 for row in rows if row["column_order_status"] == "pass"),
            "column_order_fail": sum(1 for row in rows if row["column_order_status"] == "fail"),
            "column_order_ambiguous": sum(1 for row in rows if row["column_order_status"] == "ambiguous"),
            "column_order_not_testable": sum(1 for row in rows if row["column_order_status"] == "not_testable"),
            "column_order_not_applicable": sum(1 for row in rows if row["column_order_status"] == "not_applicable"),
            "flagged_pages": [row["page"] for row in rows if row["flags"]],
        },
    }


def markdown_table(report: dict[str, Any]) -> str:
    rows = report["rows"]
    lines = [
        "# Innsmouth Keeper vs EN PDF Structure Audit",
        "",
        f"Source PDF: `{report['source_pdf']['path']}`",
        "",
        f"Keeper Markdown: `{report['keeper_markdown']['path']}`",
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
            "| Page | PDF chars | Keeper chars | Ratio | PDF paragraphs | Keeper blocks | Para ratio | PDF columns | Left first line | Right first line | Keeper first blocks | Order | Flags |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        def cell(value: Any) -> str:
            text = str(value if value is not None else "")
            text = text.replace("|", "\\|").replace("\n", " ")
            return text[:220] + ("..." if len(text) > 220 else "")

        lines.append(
            "| {page} | {pdf_chars_no_ws} | {keeper_chars_no_ws} | {ratio} | {pdf_paragraph_blocks} | {keeper_text_blocks} | {para_ratio} | {cols} | {left} | {right} | {keeper} | {order} | {flags} |".format(
                page=row["page"],
                pdf_chars_no_ws=row["pdf_chars_no_ws"],
                keeper_chars_no_ws=row["keeper_chars_no_ws"],
                ratio=row["char_ratio_keeper_over_pdf"] if row["char_ratio_keeper_over_pdf"] is not None else "",
                pdf_paragraph_blocks=row["pdf_paragraph_blocks"],
                keeper_text_blocks=row["keeper_text_blocks"],
                para_ratio=row["paragraph_ratio_keeper_over_pdf"] if row["paragraph_ratio_keeper_over_pdf"] is not None else "",
                cols=cell(row["pdf_columns"]),
                left=cell(row["pdf_left_first_line"]),
                right=cell(row["pdf_right_first_line"]),
                keeper=cell(row["keeper_first_blocks"]),
                order=row["column_order_status"],
                flags=", ".join(row["flags"]) if row["flags"] else "",
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keeper", type=Path, default=DEFAULT_KEEPER)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()

    report = build_report(args.keeper)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / "keeper_pdf_structure_audit.json"
    md_path = args.report_dir / "keeper_pdf_structure_audit.md"
    write_json(json_path, report)
    md_path.write_text(markdown_table(report), encoding="utf-8")
    print(
        "status=pass "
        f"pages={report['summary']['pages']} "
        f"order_fail={report['summary']['column_order_fail']} "
        f"not_testable={report['summary']['column_order_not_testable']} "
        f"flagged={len(report['summary']['flagged_pages'])} "
        f"report={rel(md_path)}"
    )


if __name__ == "__main__":
    main()
