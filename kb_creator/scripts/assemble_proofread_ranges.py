"""Combine explicitly reviewed, disjoint ranges into one complete submission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline import five_step_language as language
from kb_creator.pipeline.identity import file_identity


def assemble(task_path: Path, template_path: Path, parts: list[Path], output: Path) -> dict:
    task = language._read(task_path)
    language._seal_ok(task, "task_sha256", "kb_creator.five_step_language_proofread_task.v2")
    template = language._read(template_path)
    authority = {"task": {"path": task_path.name, **file_identity(task_path)},
                 "draft": task["draft"], "master_en": task["master_en"], "glossary": task["glossary"]}
    if any(template.get(key) != value for key, value in authority.items()):
        raise ValueError("template authority mismatch")
    expected = {row["unit_id"]: row for row in task["units"]}
    if len(expected) != len(task["units"]):
        raise ValueError("duplicate source unit")
    collected, inputs = {}, []
    required = {"unit_id", "source_hash", "draft_ru_sha256", "final_ru_text", "disposition", "reason", "unresolved"}
    for path in parts:
        value = language._read(path)
        if value.get("schema") != "kb_creator.five_step_language_proofread_submission.v2" or any(
            value.get(key) != identity for key, identity in authority.items()
        ):
            raise ValueError("range authority mismatch")
        if not isinstance(value.get("units"), list) or not value["units"]:
            raise ValueError("empty or malformed range")
        for row in value["units"]:
            if not isinstance(row, dict) or set(row) != required:
                raise ValueError("invalid reviewed row fields")
            uid = row["unit_id"]
            if uid not in expected or uid in collected:
                raise ValueError("unknown or overlapping reviewed unit")
            source = expected[uid]
            if any(row[key] != source[key] for key in ("source_hash", "draft_ru_sha256")):
                raise ValueError("reviewed row preimage mismatch")
            text, disposition = row["final_ru_text"], row["disposition"]
            if not isinstance(text, str) or not text.strip() or row["unresolved"] != []:
                raise ValueError("empty text or unresolved review")
            changed = language._sha(text.strip().encode()) != row["draft_ru_sha256"]
            if disposition not in {"changed", "checked_unchanged"} or (disposition == "changed") != changed:
                raise ValueError("pending or untruthful review disposition")
            if not isinstance(row["reason"], str) or (changed and not row["reason"].strip()) or (not changed and row["reason"]):
                raise ValueError("review reason mismatch")
            collected[uid] = row
        inputs.append({"path": str(path.resolve()), **file_identity(path), "unit_ids": [row["unit_id"] for row in value["units"]]})
    if set(collected) != set(expected):
        raise ValueError("reviewed ranges do not cover every unit")
    submission = {"schema": "kb_creator.five_step_language_proofread_submission.v2", **authority,
                  "units": [collected[row["unit_id"]] for row in task["units"]]}
    report = {"schema": "kb_creator.proofread_range_assembly.v1", "task": authority["task"],
              "inputs": inputs, "units": len(collected),
              "changed": sum(row["disposition"] == "changed" for row in collected.values()),
              "review_inferred": False, "release_accepted": False}
    def build(stage):
        language._write(stage / "proofread.submission.json", language._seal(submission["schema"], submission, "submission_sha256"))
        language._write(stage / "assembly-report.json", report)
    language._atomic(output.resolve(), build)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--part", required=True, action="append", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = assemble(args.task, args.template, args.part, args.output)
    except (ValueError, KeyError, OSError) as error:
        print(json.dumps({"state": "failed", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"state": "assembled", "units": result["units"], "changed": result["changed"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
