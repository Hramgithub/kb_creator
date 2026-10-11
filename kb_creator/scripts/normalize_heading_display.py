"""Create a spec successor for explicitly chosen OCR heading display normalization."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from kb_creator.pipeline.heading_display import flatten_word_wrapped_heading
from kb_creator.scripts.author_reviewed_semantic_decisions import _render_reviewed_markdown


def _replacement(lines: list[str], index: int, replacement: str) -> dict[str, Any]:
    for radius in range(len(lines)):
        start, end = max(0, index - radius), min(len(lines), index + radius + 1)
        before = "\n".join(lines[start:end])
        if "\n".join(lines).count(before) == 1:
            after = lines[start:end].copy()
            after[index - start] = replacement
            return {"before": before, "after": "\n".join(after), "count": 1}
    raise ValueError("heading normalization needs one exact reader occurrence")


def normalize_heading_spec(spec: dict[str, Any], draft_pages: Path,
                           packets_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if spec.get("semantic_structure_profile") != "reviewed_role_outline_and_partitions_v2":
        raise ValueError("heading display normalization requires V2 source fragments")
    successor = copy.deepcopy(spec)
    report: dict[str, Any] = {"schema": "kb_creator.heading_display_normalization.v1",
                             "policy": "flatten_word_wrapped_heading_tags",
                             "accepted": False, "changes": [], "unsupported": []}
    for row in successor["pages"]:
        page = row["source_page"]
        decision = json.loads((draft_pages / f"page-{page:03d}.json").read_text(encoding="utf-8"))
        packet = json.loads((packets_root / f"page-{page:03d}.json").read_text(encoding="utf-8"))
        markdown, _ = _render_reviewed_markdown(decision, packet, row, page)
        lines = markdown.split("\n")
        selected = {(r["view"], r["raw_index"]) for r in decision["selected_blocks"]
                    if r["purpose"] in {"text", "structure"}}
        for unit in row.get("units", []):
            if unit.get("kind") != "heading" or unit.get("representation") != "atx_heading":
                continue
            start, end = unit.get("start_line"), unit.get("end_line")
            if type(start) is not int or start != end or not 1 <= start <= len(lines):
                continue
            line = lines[start - 1]
            if "<" not in line:
                continue
            view = unit.get("view", decision["overlay_preference"])
            raw_indices = unit.get("raw_indices", [])
            if len(raw_indices) != 1 or (view, raw_indices[0]) not in selected:
                raise ValueError(f"page {page}: heading display needs one selected source key")
            matches = [b for b in packet["views"][view]["blocks"] if b["raw_index"] == raw_indices[0]]
            source = matches[0].get("text") if len(matches) == 1 else None
            prefix = "#" * unit["heading_level"] + " "
            if not isinstance(source, str) or line != prefix + source:
                raise ValueError(f"page {page}: heading display source text differs from reader")
            display = flatten_word_wrapped_heading(source)
            record = {"source_page": page, "unit_id": unit["id"], "view": view,
                      "raw_index": raw_indices[0], "source_text": source,
                      "source_text_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
                      "reader_text": display}
            if display == source:
                report["unsupported"].append(record)
                continue
            replacement = prefix + display
            row.setdefault("post_patches", []).append(_replacement(lines, start - 1, replacement))
            lines[start - 1] = replacement
            report["changes"].append(record)
    return successor, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--draft-pages", required=True, type=Path)
    parser.add_argument("--packets", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve() == args.report.resolve() or args.output.exists() or args.report.exists():
        raise FileExistsError("heading normalization needs two distinct absent outputs")
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    successor, report = normalize_heading_spec(spec, args.draft_pages, args.packets)
    for path, value in ((args.output, successor), (args.report, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
