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


def batch_units(units: list[dict[str, Any]], max_chars: int) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_chars = 0
    for unit in units:
        unit_chars = len(str(unit.get("source_text") or ""))
        if current and current_chars + unit_chars > max_chars:
            batches.append(current)
            current = [unit]
            current_chars = unit_chars
        else:
            current.append(unit)
            current_chars += unit_chars
    if current:
        batches.append(current)
    return batches


def split_text_for_limit(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    paragraphs = re.split(r"(\n\s*\n)", text)
    chunks: list[str] = []
    current = ""
    for part in paragraphs:
        candidate = current + part
        if current and len(candidate) > max_chars:
            chunks.append(current.strip())
            current = part
        else:
            current = candidate
        while len(current) > max_chars:
            split_at = current.rfind("\n", 0, max_chars)
            if split_at < max_chars // 2:
                split_at = current.rfind(". ", 0, max_chars)
            if split_at < max_chars // 2:
                split_at = max_chars
            chunks.append(current[:split_at].strip())
            current = current[split_at:].lstrip()
    if current.strip():
        chunks.append(current.strip())
    return [chunk for chunk in chunks if chunk]


def expand_units_for_translation(units: list[dict[str, Any]], max_chars: int) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for unit in units:
        source_text = str(unit.get("source_text") or "")
        parts = split_text_for_limit(source_text, max_chars)
        if len(parts) == 1:
            expanded.append(unit)
            continue
        parent_id = str(unit["unit_id"])
        parent_hash = unit.get("source_hash") or sha256_text(source_text)
        for index, part in enumerate(parts, start=1):
            split_unit = dict(unit)
            split_unit["unit_id"] = f"{parent_id}__part{index:02d}"
            split_unit["parent_unit_id"] = parent_id
            split_unit["part_index"] = index
            split_unit["part_count"] = len(parts)
            split_unit["source_hash"] = parent_hash
            split_unit["part_source_hash"] = sha256_text(part)
            split_unit["source_text"] = part
            expanded.append(split_unit)
    return expanded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-json", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-batch-chars", type=int, default=3000)
    args = parser.parse_args()

    source = json.loads(args.tasks_json.read_text(encoding="utf-8"))
    units = list(source.get("units") or [])
    if not units:
        raise SystemExit(f"No units in {args.tasks_json}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    expanded_units = expand_units_for_translation(units, args.max_batch_chars)
    batches = batch_units(expanded_units, args.max_batch_chars)
    manifest_batches: list[dict[str, Any]] = []
    for index, batch in enumerate(batches, start=1):
        batch_id = f"batch_{index:02d}"
        batch_path = args.out_dir / f"{batch_id}.en.json"
        ru_path = args.out_dir / f"{batch_id}.ru.json"
        packet = {
            "schema": "kb_creator.translation_batch.v1",
            "batch_id": batch_id,
            "source_tasks_json": str(args.tasks_json),
            "target_ru_json": str(ru_path),
            "instructions": [
                "Translate source_text from English to Russian.",
                "Preserve all unit_id values, source_hash values, source-page markers, headings, lists, tables, stat blocks, and Call of Cthulhu mechanical data.",
                "Do not use reference KeeperBook or reference PDF as a source.",
                "Fill ru_text for each unit; do not summarize or omit content.",
            ],
            "units": [
                {
                    "unit_id": unit["unit_id"],
                    "parent_unit_id": unit.get("parent_unit_id"),
                    "part_index": unit.get("part_index"),
                    "part_count": unit.get("part_count"),
                    "page": unit.get("page"),
                    "source_hash": unit.get("source_hash") or sha256_text(str(unit.get("source_text") or "")),
                    "part_source_hash": unit.get("part_source_hash"),
                    "source_text": unit.get("source_text") or "",
                    "ru_text": "",
                }
                for unit in batch
            ],
        }
        write_json(batch_path, packet)
        manifest_batches.append(
            {
                "batch_id": batch_id,
                "input": str(batch_path),
                "output": str(ru_path),
                "units": len(batch),
                "chars": sum(len(str(unit.get("source_text") or "")) for unit in batch),
                "first_unit": batch[0].get("unit_id"),
                "last_unit": batch[-1].get("unit_id"),
            }
        )

    manifest = {
        "schema": "kb_creator.translation_batch_manifest.v1",
        "tasks_json": str(args.tasks_json),
        "max_batch_chars": args.max_batch_chars,
        "batches": manifest_batches,
        "counts": {
            "batches": len(manifest_batches),
            "units": len(expanded_units),
            "original_units": len(units),
            "split_units": len(expanded_units) - len(units),
            "chars": sum(len(str(unit.get("source_text") or "")) for unit in expanded_units),
        },
    }
    manifest_path = args.out_dir / "translation_batch_manifest.json"
    write_json(manifest_path, manifest)
    print(
        f"status=pass batches={len(manifest_batches)} units={len(units)} "
        f"chars={manifest['counts']['chars']} manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
