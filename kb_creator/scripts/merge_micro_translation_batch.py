from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--micro-manifest", type=Path, required=True)
    parser.add_argument("--out-batch", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.micro_manifest.read_text(encoding="utf-8"))
    units: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for item in manifest.get("units", []):
        output = Path(item["output"])
        if not output.exists():
            findings.append({"code": "missing_micro_ru", "unit_id": item.get("unit_id"), "path": str(output)})
            continue
        data = json.loads(output.read_text(encoding="utf-8"))
        micro_units = data.get("units", [])
        if len(micro_units) != 1:
            findings.append({"code": "micro_unit_count_invalid", "path": str(output), "count": len(micro_units)})
            continue
        unit = micro_units[0]
        if unit.get("unit_id") != item.get("unit_id"):
            findings.append({"code": "micro_unit_id_mismatch", "expected": item.get("unit_id"), "actual": unit.get("unit_id")})
            continue
        if not str(unit.get("ru_text") or "").strip():
            findings.append({"code": "empty_micro_ru_text", "unit_id": item.get("unit_id")})
            continue
        units.append(unit)

    batch = {
        "schema": "kb_creator.translation_batch_ru.v1",
        "batch_id": manifest.get("parent_batch"),
        "units": units,
    }
    if not findings:
        write_json(args.out_batch, batch)
    report = {
        "schema": "kb_creator.merge_micro_translation_batch.v1",
        "status": "pass" if not findings else "blocked",
        "micro_manifest": str(args.micro_manifest),
        "out_batch": str(args.out_batch),
        "counts": {"units": len(units), "findings": len(findings)},
        "findings": findings,
    }
    write_json(args.report, report)
    print(f"status={report['status']} units={len(units)} findings={len(findings)} out={args.out_batch}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
