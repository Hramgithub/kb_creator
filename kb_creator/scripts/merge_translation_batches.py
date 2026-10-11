from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_markers_for_unit(source_text: str) -> list[str]:
    return re.findall(r"<!--\s*source-page-\d{3}\s*-->", source_text)


def validate_batch(en_path: Path, ru_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    en = read_json(en_path)
    if not ru_path.exists():
        return [], [{"code": "missing_ru_batch", "path": str(ru_path)}]
    ru = read_json(ru_path)
    en_units = {unit["unit_id"]: unit for unit in en.get("units", [])}
    ru_units = {unit.get("unit_id"): unit for unit in ru.get("units", [])}
    if set(en_units) != set(ru_units):
        findings.append(
            {
                "code": "unit_id_mismatch",
                "batch": en.get("batch_id"),
                "missing_in_ru": sorted(set(en_units) - set(ru_units)),
                "extra_in_ru": sorted(set(ru_units) - set(en_units)),
            }
        )
    merged_units: list[dict[str, Any]] = []
    for unit_id, en_unit in en_units.items():
        ru_unit = ru_units.get(unit_id)
        if not ru_unit:
            continue
        ru_text = str(ru_unit.get("ru_text") or ru_unit.get("ru") or "").strip()
        if not ru_text:
            findings.append({"code": "empty_ru_text", "unit_id": unit_id})
        if ru_unit.get("source_hash") != en_unit.get("source_hash"):
            findings.append({"code": "source_hash_mismatch", "unit_id": unit_id})
        for marker in source_markers_for_unit(str(en_unit.get("source_text") or "")):
            if marker not in ru_text:
                findings.append({"code": "source_marker_missing_in_ru", "unit_id": unit_id, "marker": marker})
        merged_units.append(
            {
                "unit_id": unit_id,
                "parent_unit_id": en_unit.get("parent_unit_id") or unit_id,
                "part_index": en_unit.get("part_index") or 1,
                "part_count": en_unit.get("part_count") or 1,
                "page": en_unit.get("page"),
                "source_hash": en_unit.get("source_hash"),
                "part_source_hash": en_unit.get("part_source_hash"),
                "source_chars": len(str(en_unit.get("source_text") or "")),
                "ru_text": ru_text,
                "ru_hash": sha256_text(ru_text),
            }
        )
    return merged_units, findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    all_units: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    batch_reports: list[dict[str, Any]] = []
    for batch in manifest.get("batches", []):
        en_path = Path(batch["input"])
        ru_path = Path(batch["output"])
        merged_units, batch_findings = validate_batch(en_path, ru_path)
        all_units.extend(merged_units)
        findings.extend(batch_findings)
        batch_reports.append(
            {
                "batch_id": batch.get("batch_id"),
                "input": str(en_path),
                "output": str(ru_path),
                "units": len(merged_units),
                "findings": len(batch_findings),
            }
        )

    expected_units = int(manifest.get("counts", {}).get("units") or 0)
    if len(all_units) != expected_units:
        findings.append({"code": "merged_unit_count_mismatch", "expected": expected_units, "actual": len(all_units)})

    grouped_units: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for unit in all_units:
        grouped.setdefault(str(unit["parent_unit_id"]), []).append(unit)
    for parent_id, parts in grouped.items():
        parts.sort(key=lambda item: int(item.get("part_index") or 1))
        expected_part_count = max(int(item.get("part_count") or 1) for item in parts)
        if len(parts) != expected_part_count:
            findings.append(
                {
                    "code": "split_unit_part_count_mismatch",
                    "unit_id": parent_id,
                    "expected": expected_part_count,
                    "actual": len(parts),
                }
            )
        grouped_units.append(
            {
                "unit_id": parent_id,
                "page": parts[0].get("page"),
                "source_hash": parts[0].get("source_hash"),
                "source_chars": sum(int(item.get("source_chars") or 0) for item in parts),
                "ru_text": "\n\n".join(str(item.get("ru_text") or "").strip() for item in parts).strip(),
            }
        )

    expected_original_units = int(manifest.get("counts", {}).get("original_units") or expected_units)
    if len(grouped_units) != expected_original_units:
        findings.append(
            {
                "code": "merged_original_unit_count_mismatch",
                "expected": expected_original_units,
                "actual": len(grouped_units),
            }
        )

    md_parts: list[str] = [
        "# The Innsmouth Terror - Source Text Full RU",
        "",
        "<!-- generated-by: kb_creator merge_translation_batches -->",
        f"<!-- source-batch-manifest: {args.manifest} -->",
        "",
    ]
    current_page: str | None = None
    for unit in grouped_units:
        page = unit.get("page")
        page_id = f"{int(page):03d}" if isinstance(page, int) or str(page).isdigit() else str(page or "")
        if page_id and page_id != current_page:
            md_parts.append(f"<!-- source-page-{page_id} -->")
            md_parts.append("")
            current_page = page_id
        md_parts.append(f"<!-- unit-id: {unit['unit_id']} source-hash: {unit['source_hash']} -->")
        md_parts.append("")
        md_parts.append(unit["ru_text"])
        md_parts.append("")
    text = "\n".join(md_parts).strip() + "\n"
    if not findings:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(text, encoding="utf-8", newline="\n")

    report = {
        "schema": "kb_creator.merge_translation_batches.v1",
        "status": "pass" if not findings else "blocked",
        "manifest": str(args.manifest),
        "output_markdown": str(args.out_md),
        "output_sha256": sha256_text(text) if not findings else None,
        "counts": {
            "batches": len(batch_reports),
            "units": len(all_units),
            "original_units": len(grouped_units),
            "findings": len(findings),
            "chars": len(text),
        },
        "batches": batch_reports,
        "findings": findings,
    }
    write_json(args.report, report)
    print(
        f"status={report['status']} units={len(all_units)} findings={len(findings)} "
        f"output={args.out_md} report={args.report}"
    )
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
