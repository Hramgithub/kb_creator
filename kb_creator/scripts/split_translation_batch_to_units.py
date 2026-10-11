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
    parser.add_argument("--batch-json", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    batch = json.loads(args.batch_json.read_text(encoding="utf-8"))
    parent = str(batch.get("batch_id") or args.batch_json.stem)
    manifest_units: list[dict[str, Any]] = []
    for unit in batch.get("units", []):
        unit_id = unit["unit_id"]
        en_path = args.out_dir / f"{unit_id}.en.json"
        ru_path = args.out_dir / f"{unit_id}.ru.json"
        write_json(
            en_path,
            {
                "schema": "kb_creator.translation_micro_batch.v1",
                "parent_batch": parent,
                "batch_id": unit_id,
                "target_ru_json": str(ru_path),
                "instructions": batch.get("instructions", []),
                "units": [unit],
            },
        )
        manifest_units.append(
            {
                "unit_id": unit_id,
                "input": str(en_path),
                "output": str(ru_path),
                "chars": len(str(unit.get("source_text") or "")),
            }
        )
    manifest_path = args.out_dir / f"{parent}_micro_manifest.json"
    write_json(
        manifest_path,
        {
            "schema": "kb_creator.translation_micro_manifest.v1",
            "parent_batch": parent,
            "units": manifest_units,
        },
    )
    print(f"status=pass parent={parent} units={len(manifest_units)} manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
