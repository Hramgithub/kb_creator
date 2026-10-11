from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_markdown_text(text: str) -> str:
    text = re.sub(r"<!--\s*source-page-\d{3}\s*-->", " ", text)
    text = re.sub(r"<!--[\s\S]*?-->", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


SOURCE_PAGE_RE = re.compile(r"<!--\s*source-page-(\d{3})\s*-->")
KEEPER_ART_BLOCK_RE = re.compile(
    r'<div\s+class="keeper-art-block"[\s\S]*?</div>',
    re.I,
)
STATBLOCK_SCAFFOLD_RE = re.compile(
    r"\b(?:Поле|Значение|Навыки\s*/\s*заметки|Предыстория|Заклинания|"
    r"Бой|Персонаж|Возраст|Род занятий)\b|#",
    re.I,
)
TABLE_HEAD_RE = re.compile(r"<thead[\s\S]*?</thead>", re.I)
INDEX_CELL_RE = re.compile(r"<td>\s*\d+\s*</td>", re.I)
LABEL_CELL_RE = re.compile(
    r"<td>\s*(?:Поле|Значение|Персонаж|Возраст|Род занятий)\s*</td>",
    re.I,
)
EMPTY_SOURCE_PLACEHOLDER_RE = re.compile(
    r"\b(?:Заклинания|Предыстория)\s+не\s+выделен[аы]?\s+в\s+источнике\.?",
    re.I,
)


def strip_reader_inert_blocks(text: str) -> str:
    text = KEEPER_ART_BLOCK_RE.sub(" ", text)
    text = re.sub(r"<!--[\s\S]*?-->", " ", text)
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    return text


def canonicalize_statblock_markup(text: str) -> str:
    """Keep statblock content but remove table/card scaffolding noise."""
    text = TABLE_HEAD_RE.sub(" ", text)
    text = INDEX_CELL_RE.sub(" ", text)
    text = LABEL_CELL_RE.sub(" ", text)
    text = EMPTY_SOURCE_PLACEHOLDER_RE.sub(" ", text)
    return text


def normalize_reader_text(text: str, *, ignore_statblock_scaffold: bool = False) -> str:
    text = strip_reader_inert_blocks(text)
    if ignore_statblock_scaffold:
        text = canonicalize_statblock_markup(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    if ignore_statblock_scaffold:
        text = STATBLOCK_SCAFFOLD_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_statblock_like_page(text: str) -> bool:
    return bool(
        re.search(
            r"statblock-card|statblock-structured-table|СИЛ\s+ТЕЛ|Навыки\s*/\s*заметки",
            text,
            re.I,
        )
    )


def normalize_page_reader_text(text: str) -> str:
    return normalize_reader_text(
        text,
        ignore_statblock_scaffold=is_statblock_like_page(text),
    )


def page_blocks(text: str) -> dict[str, str]:
    matches = list(SOURCE_PAGE_RE.finditer(text))
    if not matches:
        return {}
    pages: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        pages[match.group(1)] = text[match.end() : end]
    return pages


def page_delta_report(candidate_text: str, reference_text: str) -> dict[str, Any]:
    candidate_pages = page_blocks(candidate_text)
    reference_pages = page_blocks(reference_text)
    pages = sorted(set(candidate_pages) | set(reference_pages))
    rows: list[dict[str, Any]] = []
    for page in pages:
        candidate_norm = normalize_page_reader_text(candidate_pages.get(page, ""))
        reference_norm = normalize_page_reader_text(reference_pages.get(page, ""))
        rows.append(
            {
                "page": page,
                "candidate_chars": len(candidate_norm),
                "reference_chars": len(reference_norm),
                "delta_chars": len(candidate_norm) - len(reference_norm),
                "candidate_sha256": sha256_text(candidate_norm) if candidate_norm else None,
                "reference_sha256": sha256_text(reference_norm) if reference_norm else None,
                "identical": candidate_norm == reference_norm,
            }
        )
    top_abs = sorted(rows, key=lambda row: abs(row["delta_chars"]), reverse=True)[:12]
    missing_in_candidate = [page for page in sorted(reference_pages) if page not in candidate_pages]
    extra_in_candidate = [page for page in sorted(candidate_pages) if page not in reference_pages]
    row_by_page = {row["page"]: row for row in rows}
    missing_reader_text_pages = [
        page
        for page in missing_in_candidate
        if row_by_page[page]["reference_chars"] > 0
    ]
    extra_reader_text_pages = [
        page
        for page in extra_in_candidate
        if row_by_page[page]["candidate_chars"] > 0
    ]
    extra_art_or_trace_only_pages = [
        page
        for page in extra_in_candidate
        if row_by_page[page]["candidate_chars"] == 0
    ]
    return {
        "candidate_pages": sorted(candidate_pages),
        "reference_pages": sorted(reference_pages),
        "missing_in_candidate": missing_in_candidate,
        "extra_in_candidate": extra_in_candidate,
        "missing_reader_text_pages": missing_reader_text_pages,
        "extra_reader_text_pages": extra_reader_text_pages,
        "extra_art_or_trace_only_pages": extra_art_or_trace_only_pages,
        "page_rows": rows,
        "top_abs_page_deltas": top_abs,
    }


def statblock_aware_page_delta_report(candidate_text: str, reference_text: str) -> dict[str, Any]:
    candidate_pages = page_blocks(candidate_text)
    reference_pages = page_blocks(reference_text)
    pages = sorted(set(candidate_pages) | set(reference_pages))
    rows: list[dict[str, Any]] = []
    for page in pages:
        candidate_page = candidate_pages.get(page, "")
        reference_page = reference_pages.get(page, "")
        statblock_like = bool(
            is_statblock_like_page(candidate_page)
            or is_statblock_like_page(reference_page)
        )
        candidate_norm = normalize_reader_text(candidate_page, ignore_statblock_scaffold=statblock_like)
        reference_norm = normalize_reader_text(reference_page, ignore_statblock_scaffold=statblock_like)
        rows.append(
            {
                "page": page,
                "candidate_chars": len(candidate_norm),
                "reference_chars": len(reference_norm),
                "delta_chars": len(candidate_norm) - len(reference_norm),
                "candidate_sha256": sha256_text(candidate_norm) if candidate_norm else None,
                "reference_sha256": sha256_text(reference_norm) if reference_norm else None,
                "identical": candidate_norm == reference_norm,
                "statblock_like": statblock_like,
            }
        )
    statblock_rows = [row for row in rows if row["statblock_like"]]
    non_statblock_rows = [row for row in rows if not row["statblock_like"]]
    return {
        "page_rows": rows,
        "statblock_pages": [row["page"] for row in statblock_rows],
        "non_statblock_top_abs_page_deltas": sorted(
            non_statblock_rows,
            key=lambda row: abs(row["delta_chars"]),
            reverse=True,
        )[:12],
        "statblock_top_abs_page_deltas": sorted(
            statblock_rows,
            key=lambda row: abs(row["delta_chars"]),
            reverse=True,
        )[:12],
        "non_statblock_delta_chars": sum(row["delta_chars"] for row in non_statblock_rows),
        "statblock_delta_chars": sum(row["delta_chars"] for row in statblock_rows),
    }


def body_similarity_report(
    candidate_text: str,
    reference_text: str,
    *,
    similarity_threshold: float = 0.82,
    char_delta_threshold: float = 0.12,
) -> dict[str, Any]:
    """Compare translated prose with tolerance for legitimate wording drift.

    This is not a replacement for structural gates. It is a deterministic
    triage layer: body pages may differ from an agent-created reference wording.
    Length and numeric preservation are hard signals; low literal similarity
    is recorded for semantic review but does not fail the page by itself.
    """
    candidate_pages = page_blocks(candidate_text)
    reference_pages = page_blocks(reference_text)
    rows: list[dict[str, Any]] = []
    for page in sorted(set(candidate_pages) | set(reference_pages)):
        candidate_page = candidate_pages.get(page, "")
        reference_page = reference_pages.get(page, "")
        statblock_like = bool(is_statblock_like_page(candidate_page) or is_statblock_like_page(reference_page))
        if statblock_like:
            continue
        candidate_norm = normalize_reader_text(candidate_page)
        reference_norm = normalize_reader_text(reference_page)
        if not candidate_norm and not reference_norm:
            continue
        larger = max(len(candidate_norm), len(reference_norm), 1)
        delta_ratio = abs(len(candidate_norm) - len(reference_norm)) / larger
        similarity = SequenceMatcher(None, candidate_norm, reference_norm, autojunk=False).ratio()
        candidate_numbers = set(re.findall(r"\d+(?:[.,/]\d+)?", candidate_norm))
        reference_numbers = set(re.findall(r"\d+(?:[.,/]\d+)?", reference_norm))
        missing_numbers = sorted(reference_numbers - candidate_numbers)
        extra_numbers = sorted(candidate_numbers - reference_numbers)
        accepted = delta_ratio <= char_delta_threshold and not missing_numbers
        rows.append(
            {
                "page": page,
                "candidate_chars": len(candidate_norm),
                "reference_chars": len(reference_norm),
                "delta_chars": len(candidate_norm) - len(reference_norm),
                "char_delta_ratio": round(delta_ratio, 4),
                "similarity_ratio": round(similarity, 4),
                "literal_similarity_below_threshold": similarity < similarity_threshold,
                "missing_numbers": missing_numbers[:20],
                "extra_numbers": extra_numbers[:20],
                "accepted_by_body_threshold": accepted,
                "statblock_like": False,
            }
        )
    failing = [row for row in rows if not row["accepted_by_body_threshold"]]
    semantic_review = [
        row
        for row in rows
        if row["accepted_by_body_threshold"] and row["literal_similarity_below_threshold"]
    ]
    return {
        "method": "length_numeric_gate_plus_literal_similarity_advisory",
        "scope": "non_statblock_reader_text_pages",
        "char_delta_threshold": char_delta_threshold,
        "literal_similarity_advisory_threshold": similarity_threshold,
        "pages_checked": len(rows),
        "pages_passing": len(rows) - len(failing),
        "pages_requiring_review": len(failing),
        "pages_requiring_semantic_review_only": len(semantic_review),
        "status": "pass" if not failing else "needs_review",
        "rows": rows,
        "requiring_review_top": sorted(
            failing,
            key=lambda row: (-row["char_delta_ratio"], len(row["missing_numbers"])),
            reverse=True,
        )[:12],
        "semantic_review_top": sorted(
            semantic_review,
            key=lambda row: row["similarity_ratio"],
        )[:12],
    }


def structure_counts(text: str) -> dict[str, int]:
    return {
        "source_pages": len(SOURCE_PAGE_RE.findall(text)),
        "headings": len(re.findall(r"^#{1,6}\s+", text, re.M)),
        "keeper_art_blocks": len(re.findall(r"keeper-art-block", text)),
        "html_tables": len(re.findall(r"<table\b", text, re.I)),
        "html_divs": len(re.findall(r"<div\b", text, re.I)),
        "statblock_cards": len(re.findall(r"statblock-card", text)),
    }


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
    }


def compare_keeper(candidate: Path, reference: Path) -> dict[str, Any]:
    if not candidate.exists() or not reference.exists():
        return {"status": "missing_input", "candidate": file_record(candidate), "reference": file_record(reference)}
    candidate_text = candidate.read_text(encoding="utf-8", errors="replace")
    reference_text = reference.read_text(encoding="utf-8", errors="replace")
    candidate_norm = normalize_markdown_text(candidate_text)
    reference_norm = normalize_markdown_text(reference_text)
    candidate_reader = normalize_reader_text(candidate_text)
    reference_reader = normalize_reader_text(reference_text)
    candidate_reader_no_scaffold = normalize_reader_text(candidate_text, ignore_statblock_scaffold=True)
    reference_reader_no_scaffold = normalize_reader_text(reference_text, ignore_statblock_scaffold=True)
    statblock_page_report = statblock_aware_page_delta_report(candidate_text, reference_text)
    body_similarity = body_similarity_report(candidate_text, reference_text)
    page_report = page_delta_report(candidate_text, reference_text)
    structure = {
        "candidate": structure_counts(candidate_text),
        "reference": structure_counts(reference_text),
    }
    scaffold_delta = abs(len(candidate_reader_no_scaffold) - len(reference_reader_no_scaffold))
    scaffold_larger = max(len(candidate_reader_no_scaffold), len(reference_reader_no_scaffold), 1)
    acceptance_findings: list[dict[str, Any]] = []
    if len(SOURCE_PAGE_RE.findall(candidate_text)) != len(SOURCE_PAGE_RE.findall(reference_text)):
        acceptance_findings.append({"code": "source_page_count_mismatch"})
    if len(re.findall(r"^#{1,6}\s+", candidate_text, re.M)) != len(re.findall(r"^#{1,6}\s+", reference_text, re.M)):
        acceptance_findings.append({"code": "heading_count_mismatch"})
    if structure["candidate"]["keeper_art_blocks"] != structure["reference"]["keeper_art_blocks"]:
        acceptance_findings.append({"code": "keeper_art_block_count_mismatch"})
    if page_report["missing_reader_text_pages"]:
        acceptance_findings.append(
            {"code": "missing_reader_text_pages", "pages": page_report["missing_reader_text_pages"]}
        )
    if page_report["extra_reader_text_pages"]:
        acceptance_findings.append(
            {"code": "extra_reader_text_pages", "pages": page_report["extra_reader_text_pages"]}
        )
    if body_similarity["status"] != "pass":
        acceptance_findings.append({"code": "body_similarity_needs_review"})
    if scaffold_delta / scaffold_larger > 0.05:
        acceptance_findings.append(
            {
                "code": "reader_text_delta_over_threshold",
                "delta_chars": scaffold_delta,
                "threshold_ratio": 0.05,
            }
        )
    exact_pass = candidate_norm == reference_norm
    accepted_drift = not exact_pass and not acceptance_findings
    return {
        "status": "pass" if exact_pass else "accepted_drift" if accepted_drift else "different",
        "acceptance": {
            "method": "exact_or_structural_body_preservation_gate",
            "exact_required": False,
            "accepted_non_exact": accepted_drift,
            "findings": acceptance_findings,
            "reader_text_ignoring_statblock_scaffold_delta_ratio": round(scaffold_delta / scaffold_larger, 4),
            "reader_text_delta_threshold": 0.05,
        },
        "candidate": file_record(candidate),
        "reference": file_record(reference),
        "byte_identical": sha256_file(candidate) == sha256_file(reference),
        "normalized_text_identical": candidate_norm == reference_norm,
        "candidate_normalized_sha256": sha256_text(candidate_norm),
        "reference_normalized_sha256": sha256_text(reference_norm),
        "candidate_chars": len(candidate_text),
        "reference_chars": len(reference_text),
        "candidate_normalized_chars": len(candidate_norm),
        "reference_normalized_chars": len(reference_norm),
        "candidate_source_pages": len(re.findall(r"<!--\s*source-page-\d{3}\s*-->", candidate_text)),
        "reference_source_pages": len(re.findall(r"<!--\s*source-page-\d{3}\s*-->", reference_text)),
        "candidate_headings": len(re.findall(r"^#{1,6}\s+", candidate_text, re.M)),
        "reference_headings": len(re.findall(r"^#{1,6}\s+", reference_text, re.M)),
        "reader_text": {
            "identical": candidate_reader == reference_reader,
            "candidate_sha256": sha256_text(candidate_reader),
            "reference_sha256": sha256_text(reference_reader),
            "candidate_chars": len(candidate_reader),
            "reference_chars": len(reference_reader),
            "delta_chars": len(candidate_reader) - len(reference_reader),
        },
        "reader_text_ignoring_statblock_scaffold": {
            "identical": candidate_reader_no_scaffold == reference_reader_no_scaffold,
            "candidate_sha256": sha256_text(candidate_reader_no_scaffold),
            "reference_sha256": sha256_text(reference_reader_no_scaffold),
            "candidate_chars": len(candidate_reader_no_scaffold),
            "reference_chars": len(reference_reader_no_scaffold),
            "delta_chars": len(candidate_reader_no_scaffold) - len(reference_reader_no_scaffold),
        },
        "structure_counts": structure,
        "page_delta_report": page_report,
        "statblock_aware_page_delta_report": statblock_page_report,
        "body_similarity_report": body_similarity,
    }


def extract_pdf_text(path: Path) -> tuple[int | None, str, list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    try:
        from pypdf import PdfReader
    except Exception as exc:
        return None, "", [{"code": "pypdf_unavailable", "message": f"{type(exc).__name__}: {exc}"}]

    try:
        reader = PdfReader(str(path))
        pages = len(reader.pages)
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return pages, "\n".join(parts), findings
    except Exception as exc:
        return None, "", [{"code": "pdf_text_extract_failed", "message": f"{type(exc).__name__}: {exc}"}]


def compare_pdf(candidate: Path, reference: Path) -> dict[str, Any]:
    if not candidate.exists() or not reference.exists():
        return {"status": "missing_input", "candidate": file_record(candidate), "reference": file_record(reference)}
    candidate_pages, candidate_text, candidate_findings = extract_pdf_text(candidate)
    reference_pages, reference_text, reference_findings = extract_pdf_text(reference)
    candidate_norm = re.sub(r"\s+", " ", candidate_text).strip()
    reference_norm = re.sub(r"\s+", " ", reference_text).strip()
    findings = candidate_findings + reference_findings
    text_delta = abs(len(candidate_norm) - len(reference_norm))
    text_larger = max(len(candidate_norm), len(reference_norm), 1)
    acceptance_findings: list[dict[str, Any]] = []
    if findings:
        acceptance_findings.append({"code": "pdf_text_extraction_findings"})
    if candidate_pages != reference_pages:
        acceptance_findings.append({"code": "pdf_page_count_mismatch"})
    if not candidate_norm:
        acceptance_findings.append({"code": "candidate_pdf_text_empty"})
    if text_delta / text_larger > 0.05:
        acceptance_findings.append(
            {
                "code": "pdf_text_delta_over_threshold",
                "delta_chars": text_delta,
                "threshold_ratio": 0.05,
            }
        )
    exact_pass = not findings and candidate_norm == reference_norm
    accepted_drift = not exact_pass and not acceptance_findings
    return {
        "status": "pass" if exact_pass else "accepted_drift" if accepted_drift else "different",
        "acceptance": {
            "method": "exact_or_page_count_and_text_volume_gate",
            "exact_required": False,
            "accepted_non_exact": accepted_drift,
            "findings": acceptance_findings,
            "text_delta_ratio": round(text_delta / text_larger, 4),
            "text_delta_threshold": 0.05,
        },
        "candidate": file_record(candidate),
        "reference": file_record(reference),
        "byte_identical": sha256_file(candidate) == sha256_file(reference),
        "page_count_identical": candidate_pages == reference_pages,
        "candidate_pages": candidate_pages,
        "reference_pages": reference_pages,
        "text_identical": candidate_norm == reference_norm,
        "candidate_text_sha256": sha256_text(candidate_norm),
        "reference_text_sha256": sha256_text(reference_norm),
        "candidate_text_chars": len(candidate_norm),
        "reference_text_chars": len(reference_norm),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-keeper", type=Path, required=True)
    parser.add_argument("--reference-keeper", type=Path, required=True)
    parser.add_argument("--candidate-pdf", type=Path, required=True)
    parser.add_argument("--reference-pdf", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    keeper = compare_keeper(args.candidate_keeper, args.reference_keeper)
    pdf = compare_pdf(args.candidate_pdf, args.reference_pdf)
    accepted_statuses = {"pass", "accepted_drift"}
    if keeper["status"] == "pass" and pdf["status"] == "pass":
        status = "pass"
    elif keeper["status"] in accepted_statuses and pdf["status"] in accepted_statuses:
        status = "accepted_drift"
    else:
        status = "different"
    report = {
        "schema": "kb_creator.innsmouth_artifact_comparison.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "keeper": keeper,
        "pdf": pdf,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "status={status} keeper={keeper_status} pdf={pdf_status} report={report}".format(
            status=status,
            keeper_status=keeper["status"],
            pdf_status=pdf["status"],
            report=args.report,
        )
    )
    return 0 if status in {"pass", "accepted_drift"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
