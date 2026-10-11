"""Bounded review views and lossless collection of explicit source choices."""
from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any

from . import source_choice_translation as choices
from .identity import file_identity


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise choices.SourceChoiceError("review batch must be a JSON object")
    return value


def _identity(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _write_new(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _protect_source_roots(output: Path, queue: Path, value: dict[str, Any]) -> None:
    choices._reject_overlap(output, queue, Path(value["review_master"]["path"]).parent,
                            Path(value["candidate"]["path"]))


def _changes(before: str, after: str) -> list[dict[str, Any]]:
    """Exact changed slices, with offsets into the fully retained baseline."""
    return [{"start": i, "end": j, "before": before[i:j], "after": after[a:b]}
            for tag, i, j, a, b in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes()
            if tag != "equal"]


def _review_text(row: dict[str, Any]) -> str:
    baseline = next(alt for alt in row["alternatives"]
                    if alt["alternative_id"] == row["provisional_alternative_id"])
    view = {"issue_id": row["issue_id"], "source_page": row["source_page"],
            "reason": row.get("reason", ""), "provisional_alternative_id": baseline["alternative_id"],
            "baseline_raw_text": baseline["raw_text"], "baseline_reader_text": baseline["reader_text"],
            "alternatives": []}
    for alt in row["alternatives"]:
        view["alternatives"].append({"alternative_id": alt["alternative_id"],
            "source_locator": alt["source_locator"], "selectable": alt["selectable"],
            "raw_changes": _changes(baseline["raw_text"], alt["raw_text"]),
            "reader_changes": _changes(baseline["reader_text"], alt["reader_text"])})
    # JSON quoting preserves whitespace and keeps book text distinct from instructions.
    return json.dumps(view, ensure_ascii=False, indent=2)


def prepare_batches(queue: Path, output: Path, *, max_choices: int = 25,
                    max_review_chars: int = 50000) -> dict[str, Any]:
    if type(max_choices) is not int or max_choices < 1 or type(max_review_chars) is not int or max_review_chars < 1:
        raise choices.SourceChoiceError("review batch limits must be positive integers")
    queue, output = Path(queue).resolve(), Path(output).resolve()
    if output.exists() or queue == output or queue.is_relative_to(output):
        raise choices.SourceChoiceError("review output must be a new directory outside queue ancestry")
    initial_identity = _identity(queue)
    choices.verify_queue_v2(queue)
    value = _read(queue)
    if _identity(queue) != initial_identity:
        raise choices.SourceChoiceError("queue changed during batch preparation")
    _protect_source_roots(output, queue, value)
    rows = value["choices"]
    ids = [row["issue_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise choices.SourceChoiceError("queue repeats an issue")
    grouped: list[list[tuple[dict[str, Any], str]]] = []
    current: list[tuple[dict[str, Any], str]] = []
    size = 0
    for row in rows:
        text = _review_text(row)
        if current and (len(current) >= max_choices or size + len(text) > max_review_chars):
            grouped.append(current)
            current, size = [], 0
        current.append((row, text))
        size += len(text)
    if current:
        grouped.append(current)
    output.mkdir(parents=True, exist_ok=False)
    packets = []
    for index, group in enumerate(grouped, 1):
        name = f"batch-{index:03d}"
        task = output / f"{name}.task.json"
        review = output / f"{name}.review.json"
        template = output / f"{name}.submission-template.json"
        _write_new(task, {"schema": "kb_creator.source_choice_review_batch.v1",
                         "queue": initial_identity, "choices": [row for row, _ in group]})
        _write_new(review, {"purpose": "Reading aid only; exact raw evidence is retained in the task and queue.",
                           "queue": initial_identity, "choices": [json.loads(text) for _, text in group]})
        _write_new(template, {"schema": choices.SUBMISSION_SCHEMA_V2, "state": "submitted",
                             "queue": initial_identity, "choices": [
                                 {"issue_id": row["issue_id"], "disposition": None,
                                  "alternative_id": None, "reason": "", "label": None}
                                 for row, _ in group]})
        packets.append({"batch_id": name, "issue_ids": [row["issue_id"] for row, _ in group],
                        "task": _identity(task), "review": _identity(review), "template": _identity(template)})
    manifest = output / "MANIFEST.json"
    _write_new(manifest, {"schema": "kb_creator.source_choice_review_batches.v1",
                         "queue": initial_identity, "acceptance": "pending",
                         "max_choices": max_choices, "max_review_chars": max_review_chars,
                         "batches": packets})
    return {"state": "prepared", "choices": len(rows), "batches": len(packets), "manifest": str(manifest)}


def collect_submissions(queue: Path, submissions: list[Path], output: Path) -> dict[str, Any]:
    """Reorder explicit answers by queue order; the existing public recorder verifies them."""
    queue, output = Path(queue).resolve(), Path(output).resolve()
    if output.exists() or queue == output or queue.is_relative_to(output):
        raise choices.SourceChoiceError("review result must use a new directory outside queue ancestry")
    queue_identity = _identity(queue)
    value = _read(queue)
    if value.get("schema") != choices.QUEUE_SCHEMA_V2:
        raise choices.SourceChoiceError("review batches require a v2 queue")
    _protect_source_roots(output, queue, value)
    expected_ids = [row["issue_id"] for row in value["choices"]]
    if len(expected_ids) != len(set(expected_ids)):
        raise choices.SourceChoiceError("queue repeats an issue")
    by_id = {}
    for path in submissions:
        submitted = _read(Path(path))
        if (set(submitted) != {"schema", "state", "queue", "choices"}
                or submitted["schema"] != choices.SUBMISSION_SCHEMA_V2
                or submitted["state"] != "submitted" or submitted["queue"] != queue_identity
                or not isinstance(submitted["choices"], list)):
            raise choices.SourceChoiceError("batch submission does not bind the exact queue")
        for row in submitted["choices"]:
            issue_id = row.get("issue_id") if isinstance(row, dict) else None
            if issue_id not in expected_ids or issue_id in by_id:
                raise choices.SourceChoiceError("batch submissions contain an unknown or duplicate issue")
            by_id[issue_id] = row
    if set(by_id) != set(expected_ids):
        raise choices.SourceChoiceError("batch submissions do not cover the whole queue")
    if _identity(queue) != queue_identity:
        raise choices.SourceChoiceError("queue changed during answer collection")
    output.mkdir(parents=True, exist_ok=False)
    merged = output / "submission.json"
    _write_new(merged, {"schema": choices.SUBMISSION_SCHEMA_V2, "state": "submitted",
                        "queue": queue_identity, "choices": [by_id[key] for key in expected_ids]})
    # This call freshly verifies the original queue and validates every decision.
    return choices.record_decisions_v2(queue, merged, output / "ledger")
