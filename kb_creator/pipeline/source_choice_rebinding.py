"""Conservatively carry reviewed v2 source-choice answers into a successor queue."""
from __future__ import annotations

import json
import copy
from pathlib import Path
from typing import Any, Iterable

from . import source_choice_translation as choices
from .identity import canonical_bytes, file_identity, sha256_bytes


class SourceChoiceRebindingError(choices.SourceChoiceError):
    """A reviewed answer cannot safely be rebound to a new queue."""


AUDIT_SCHEMA = "kb_creator.source_choice_rebinding_audit.v1"


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceChoiceRebindingError("source-choice rebinding JSON must be an object")
    return value


def _identity(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _queue_path(value: Path) -> Path:
    return value.resolve() if value.is_file() else (value / "SOURCE_CHOICE_QUEUE.v2.json").resolve()


def _authority_roots(queue: dict[str, Any]) -> list[Path]:
    roots: list[Path] = []
    for key in ("review_master", "candidate"):
        record = queue.get(key)
        if isinstance(record, dict) and isinstance(record.get("path"), str):
            path = Path(record["path"]).resolve()
            roots.append(path.parent if key == "review_master" else path)
    return roots


def _portable_evidence(value: Any) -> Any:
    """Keep file content identities while ignoring a legitimate relocation hint."""
    if isinstance(value, list):
        return [_portable_evidence(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: _portable_evidence(item) for key, item in value.items()}
    if {"path", "bytes", "sha256"}.issubset(result):
        result.pop("path")
    if {"path_hint", "bytes", "sha256"}.issubset(result):
        result.pop("path_hint")
    return result


def _replay_identity(row: dict[str, Any]) -> dict[str, Any]:
    """Compare all replay authority except documented verified transport fields.

    Queue verification independently rederives the decision and Stage05 files.
    Their whole-file identities, page coordinates, stream position, and a
    normalized page slice can legitimately move during verified transport.
    Every other replay field, including raw-source slices and hashes, stays in
    this comparison so an unknown or changed semantic field becomes pending.
    """
    replay = row.get("raw_reader_replay")
    if not isinstance(replay, dict):
        return {"invalid": replay}
    result = copy.deepcopy(replay)
    # These are verified independently by verify_queue_v2 and may have changed
    # only because the reviewed transport was relocated or reserialized.
    result.pop("decision", None)
    result.pop("stage05_audit", None)
    result.pop("normalized_source_slice", None)
    span = result.get("r0_reader_span")
    if isinstance(span, dict):
        for key in ("character_start", "character_end", "byte_start", "byte_end",
                    "decision_markdown_sha256", "page_markdown_sha256"):
            span.pop(key, None)
    proof = result.get("selected_row_proof")
    if isinstance(proof, dict):
        proof.pop("stream_index", None)
        proof.pop("row_sha256", None)
    return result


def _stage05_authority(queue: dict[str, Any]) -> dict[str, Any]:
    """Load the queue-sealed final evidence and its one relative Stage05 authority."""
    evidence_record = queue.get("final_evidence")
    if (not isinstance(evidence_record, dict) or set(evidence_record) != {"path", "bytes", "sha256"}
            or not isinstance(evidence_record["path"], str)):
        raise SourceChoiceRebindingError("queue final evidence authority is malformed")
    evidence_path = Path(evidence_record["path"])
    if not evidence_path.is_file() or file_identity(evidence_path) != {key: evidence_record[key] for key in ("bytes", "sha256")}:
        raise SourceChoiceRebindingError("queue final evidence identity drift")
    evidence = _read(evidence_path)
    record = evidence.get("authored", {}).get("stage05_audit") if isinstance(evidence.get("authored"), dict) else None
    if (not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}
            or not isinstance(record["path"], str) or not record["path"]
            or Path(record["path"]).is_absolute()):
        raise SourceChoiceRebindingError("final evidence Stage05 authority is malformed")
    audit_path = (evidence_path.parent / record["path"]).resolve()
    if not audit_path.is_relative_to(evidence_path.parent.resolve()):
        raise SourceChoiceRebindingError("final evidence Stage05 authority escapes evidence root")
    if not audit_path.is_file() or file_identity(audit_path) != {key: record[key] for key in ("bytes", "sha256")}:
        raise SourceChoiceRebindingError("final evidence Stage05 authority identity drift")
    return {"evidence_path": evidence_path.resolve(), "evidence_identity": _identity(evidence_path),
            "record": record, "audit_path": audit_path, "audit_identity": _identity(audit_path)}


def _proof_row(replay: dict[str, Any], page: int, authority: dict[str, Any],
               cache: dict[tuple[str, int, str], dict[int, dict[str, Any]]]) -> dict[str, Any]:
    """Read one row from the queue-sealed Stage05 authority; coordinates move only later."""
    record, proof = replay.get("stage05_audit"), replay.get("selected_row_proof")
    if not isinstance(record, dict) or not isinstance(proof, dict) or record != authority["record"]:
        raise SourceChoiceRebindingError("selected Stage05 proof is malformed")
    path, identity = authority["audit_path"], authority["audit_identity"]
    key = (identity["path"], identity["bytes"], identity["sha256"])
    if key not in cache:
        audit, pages = _read(path), None
        if isinstance(audit.get("pages"), list):
            pages = {row.get("source_page"): row for row in audit["pages"]
                     if isinstance(row, dict) and type(row.get("source_page")) is int}
        if pages is None or len(pages) != len(audit.get("pages", [])):
            raise SourceChoiceRebindingError("selected Stage05 proof pages are malformed")
        cache[key] = pages
    page_row = cache[key].get(page)
    if not isinstance(page_row, dict) or not isinstance(page_row.get("ordered_proof_stream"), list):
        raise SourceChoiceRebindingError("selected Stage05 proof page is absent or ambiguous")
    index = proof.get("stream_index")
    stream = page_row["ordered_proof_stream"]
    if type(index) is not int or not 0 <= index < len(stream) or not isinstance(stream[index], dict):
        raise SourceChoiceRebindingError("selected Stage05 proof locator is invalid")
    row = stream[index]
    unit, locator = row.get("unit"), proof.get("source_locator")
    span = row.get("markdown_span")
    if (not isinstance(unit, dict) or not isinstance(locator, dict)
            or not isinstance(span, list) or len(span) != 2
            or any(type(value) is not int or value < 0 for value in span) or span[0] > span[1]
            or proof.get("row_sha256") != sha256_bytes(canonical_bytes(row))
            or row.get("kind") != "selected" or unit.get("view_id") != locator.get("view")
            or unit.get("raw_index") != locator.get("raw_index")):
        raise SourceChoiceRebindingError("selected Stage05 proof row differs")
    return row


def _same_rebound_proof(previous: dict[str, Any], current: dict[str, Any], old_authority: dict[str, Any],
                        new_authority: dict[str, Any], cache: dict[tuple[str, int, str], dict[int, dict[str, Any]]]) -> bool:
    """Allow only verified Stage05 markdown coordinates to move."""
    old_replay, new_replay = previous.get("raw_reader_replay"), current.get("raw_reader_replay")
    if not isinstance(old_replay, dict) or not isinstance(new_replay, dict): return False
    old_row = _proof_row(old_replay, previous.get("source_page"), old_authority, cache)
    new_row = _proof_row(new_replay, current.get("source_page"), new_authority, cache)
    def payload(row: dict[str, Any]) -> dict[str, Any]:
        result = copy.deepcopy(row); result.pop("markdown_span", None); return result
    return payload(old_row) == payload(new_row)


def _semantic_identity(row: dict[str, Any]) -> dict[str, Any]:
    keys = ("source_pdf_sha256", "source_page", "issue_kind", "source_selector",
            "r0_source_preimage", "reader_anchor", "reader_projection",
            "provisional_alternative_id", "provisional_alternative_ids")
    result = {key: row.get(key) for key in keys}
    result["raw_reader_replay"] = _replay_identity(row)
    result["alternatives"] = [
        {key: alternative.get(key) for key in (
            "alternative_id", "raw_text", "raw_text_sha256", "reader_text",
            "reader_text_sha256", "source_locator", "selectable",
            "nonselectable_reason", "reader_adapter")}
        | {"evidence": _portable_evidence(alternative.get("evidence"))}
        for alternative in row.get("alternatives", [])
        if isinstance(alternative, dict)
    ]
    if not isinstance(row.get("alternatives"), list) or len(result["alternatives"]) != len(row["alternatives"]):
        result["alternatives_invalid"] = True
    return result


def _validate_submissions(queue_path: Path, queue: dict[str, Any], paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    expected = {row.get("issue_id"): row for row in queue.get("choices", []) if isinstance(row, dict)}
    if len(expected) != len(queue.get("choices", [])) or None in expected:
        raise SourceChoiceRebindingError("old queue has duplicate or malformed issue IDs")
    answers: dict[str, dict[str, Any]] = {}
    exact_queue = _identity(queue_path)
    for path in paths:
        submitted = _read(path)
        if (set(submitted) != {"schema", "state", "queue", "choices"}
                or submitted.get("schema") != choices.SUBMISSION_SCHEMA_V2
                or submitted.get("state") != "submitted" or submitted.get("queue") != exact_queue
                or not isinstance(submitted.get("choices"), list)):
            raise SourceChoiceRebindingError("old submission is malformed or foreign")
        for answer in submitted["choices"]:
            if not isinstance(answer, dict) or set(answer) - {"issue_id", "disposition", "alternative_id", "reason", "label"}:
                raise SourceChoiceRebindingError("old submission answer has unsupported fields")
            issue_id = answer.get("issue_id")
            if issue_id not in expected or issue_id in answers:
                raise SourceChoiceRebindingError("old submissions contain a foreign or duplicate issue")
            if not isinstance(answer.get("reason"), str) or not answer["reason"].strip():
                raise SourceChoiceRebindingError("old submission reason is absent")
            old_row = expected[issue_id]
            alternative = next((item for item in old_row.get("alternatives", [])
                                if isinstance(item, dict) and item.get("alternative_id") == answer.get("alternative_id")), None)
            if not isinstance(alternative, dict) or not alternative.get("selectable"):
                raise SourceChoiceRebindingError("old submission selects an unknown or unavailable alternative")
            if answer.get("disposition") == "selected_alternative" and answer.get("label") is None:
                pass
            elif (answer.get("disposition") == "unresolved_semantic"
                  and answer.get("alternative_id") == old_row.get("provisional_alternative_id")
                  and answer.get("label") in choices.ALLOWED_LABELS):
                pass
            else:
                raise SourceChoiceRebindingError("old submission disposition is invalid")
            answers[issue_id] = answer
    return answers


def rebind_source_choice_submissions(old_queue: Path, new_queue: Path,
                                     old_submissions: Iterable[Path], output: Path) -> dict[str, Any]:
    """Write only exact, reviewed answers whose semantic source identity is unchanged."""
    old_path, new_path, destination = _queue_path(Path(old_queue)), _queue_path(Path(new_queue)), Path(output).resolve()
    submission_paths = [Path(path).resolve() for path in old_submissions]
    if not submission_paths:
        raise SourceChoiceRebindingError("at least one old submission is required")
    if destination.exists():
        raise SourceChoiceRebindingError("source-choice rebinding destination must be absent")
    choices._reject_overlap(destination, old_path, new_path, *submission_paths)
    before = {path: _identity(path) for path in [old_path, new_path, *submission_paths]}
    choices.verify_queue_v2(old_path)
    choices.verify_queue_v2(new_path)
    old, new = _read(old_path), _read(new_path)
    old_authority, new_authority = _stage05_authority(old), _stage05_authority(new)
    for authority in (old_authority, new_authority):
        before[authority["evidence_path"]] = authority["evidence_identity"]
        before[authority["audit_path"]] = authority["audit_identity"]
    choices._reject_overlap(destination, *_authority_roots(old), *_authority_roots(new))
    answers = _validate_submissions(old_path, old, submission_paths)
    old_rows = {row["issue_id"]: row for row in old["choices"]}
    new_rows = {row["issue_id"]: row for row in new.get("choices", []) if isinstance(row, dict) and isinstance(row.get("issue_id"), str)}
    if len(new_rows) != len(new.get("choices", [])):
        raise SourceChoiceRebindingError("new queue has duplicate or malformed issue IDs")
    audit_rows, reused, proof_cache = [], [], {}
    for issue_id, current in new_rows.items():
        previous = old_rows.get(issue_id)
        answer = answers.get(issue_id)
        if answer is None:
            state, reason = ("pending", "absent_old_answer") if previous is not None else ("absent", "absent_old_issue")
        elif previous is None:
            state, reason = "pending", "absent_old_issue"
        elif _semantic_identity(previous) != _semantic_identity(current):
            state, reason = "pending", "semantic_identity_changed"
        elif not _same_rebound_proof(previous, current, old_authority, new_authority, proof_cache):
            state, reason = "pending", "selected_row_semantic_changed"
        else:
            state, reason = "reused", "exact_semantic_identity"
            reused.append(answer)
        audit_rows.append({"issue_id": issue_id, "state": state, "reason": reason,
                           "predecessor": None if previous is None else _semantic_identity(previous),
                           "current": _semantic_identity(current)})
    # The two full derives above are intentionally the only expensive queue
    # verification here.  The recorder will freshly derive again when a human
    # later combines this partial submission with pending answers.
    if any(_identity(path) != identity for path, identity in before.items()):
        raise SourceChoiceRebindingError("source-choice rebinding input changed during verification")
    destination.mkdir(parents=True)
    new_identity = _identity(new_path)
    partial = {"schema": choices.SUBMISSION_SCHEMA_V2, "state": "submitted", "queue": new_identity, "choices": reused}
    pending_ids = {row["issue_id"] for row in audit_rows if row["state"] != "reused"}
    template = {"schema": choices.SUBMISSION_SCHEMA_V2, "state": "submitted", "queue": new_identity,
                "choices": [{"issue_id": row["issue_id"], "disposition": None, "alternative_id": None,
                             "reason": "", "label": None} for row in new["choices"] if row["issue_id"] in pending_ids]}
    audit = {"schema": AUDIT_SCHEMA, "accepted": False, "old_queue": before[old_path],
             "new_queue": new_identity, "old_submissions": [before[path] for path in submission_paths],
             "rows": audit_rows, "reused": len(reused), "pending": len(pending_ids)}
    for name, value in (("SOURCE_CHOICE_REBINDING_SUBMISSION.v2.json", partial),
                        ("SOURCE_CHOICE_REBINDING_TEMPLATE.v2.json", template),
                        ("SOURCE_CHOICE_REBINDING_AUDIT.v1.json", audit)):
        (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"state": "pending_review", "accepted": False, "reused": len(reused),
            "pending": audit["pending"], "submission": str(destination / "SOURCE_CHOICE_REBINDING_SUBMISSION.v2.json"),
            "audit": str(destination / "SOURCE_CHOICE_REBINDING_AUDIT.v1.json"),
            "audit_sha256": sha256_bytes(canonical_bytes(audit))}
