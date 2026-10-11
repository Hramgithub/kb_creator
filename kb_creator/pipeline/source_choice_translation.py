"""Evidence-bound translation source-choice queue and pre-R1 ledger."""
from __future__ import annotations

import json
import os
import re
import tempfile
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterator, Mapping

from .five_step_intake import verify_master_en
from .identity import canonical_bytes, file_identity, sha256_bytes
from .manifests import sealed, validate_seal
from .mechanical_reconstruction import verify_mechanical_draft
from .reader_occurrence_projection import (
    ReaderOccurrenceError, display_text, load_issue_en_bindings_v2,
    project_raw_alternative_to_reader,
)

QUEUE_SCHEMA = "kb_creator.source_choice_queue.v1"
SUBMISSION_SCHEMA = "kb_creator.source_choice_submission.v1"
LEDGER_SCHEMA = "kb_creator.source_choice_ledger.v1"
QUEUE_SCHEMA_V2 = "kb_creator.source_choice_queue.v2"
SUBMISSION_SCHEMA_V2 = "kb_creator.source_choice_submission.v2"
LEDGER_SCHEMA_V2 = "kb_creator.source_choice_ledger.v2"
PENDING_KIND = "translation_source_choice_pending"
ALLOWED_LABELS = {"Проверить смысл", "Редакторский выбор"}


class SourceChoiceError(ValueError):
    """Fail-closed source-choice contract error."""


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SourceChoiceError(f"cannot read JSON evidence: {path}") from error


def _record(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _check_record(value: Any, label: str) -> Path:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise SourceChoiceError(f"{label} identity is malformed")
    path = Path(value["path"])
    if not path.is_file() or file_identity(path) != {key: value[key] for key in ("bytes", "sha256")}:
        raise SourceChoiceError(f"{label} identity drift")
    return path


def _tree_record(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise SourceChoiceError("mechanical candidate is absent")
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SourceChoiceError("mechanical candidate contains a symlink")
        if path.is_file():
            files.append({"path": path.relative_to(root).as_posix(), **file_identity(path)})
    return {"path": str(root), "files": files}


def _check_tree(value: Any, label: str) -> Path:
    if not isinstance(value, dict) or set(value) != {"path", "files"} or not isinstance(value["files"], list):
        raise SourceChoiceError(f"{label} identity is malformed")
    root = Path(value["path"])
    if _tree_record(root) != value:
        raise SourceChoiceError(f"{label} identity drift")
    return root


def _reject_overlap(output: Path, *inputs: Path) -> None:
    output = output.resolve()
    for source in inputs:
        source = source.resolve()
        if output == source or output.is_relative_to(source) or source.is_relative_to(output):
            raise SourceChoiceError("source-choice output overlaps an input authority")


def _write_immutable(path: Path, value: dict[str, Any]) -> None:
    data = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != data:
            raise SourceChoiceError(f"immutable output already exists with different bytes: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, staging = tempfile.mkstemp(prefix=".source-choice-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(data)
        if path.exists():
            if path.read_text(encoding="utf-8") != data:
                raise SourceChoiceError(f"immutable output appeared with different bytes: {path}")
            return
        os.replace(staging, path)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)


def _source_identity(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or type(value.get("bytes")) is not int or value["bytes"] < 1:
        raise SourceChoiceError(f"{label} source identity is malformed")
    sha256 = value.get("sha256")
    if not isinstance(sha256, str) or len(sha256) != 64 or any(char not in "0123456789ABCDEF" for char in sha256):
        raise SourceChoiceError(f"{label} source identity is malformed")
    return {"bytes": value["bytes"], "sha256": sha256}


def _master(review_master: Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = review_master.resolve()
    try:
        verify_master_en(root)
    except Exception as error:
        raise SourceChoiceError(f"review master verification failed: {error}") from error
    manifest = _read(root / "MANIFEST.json")
    evidence_path = _check_record(manifest.get("final_evidence"), "review final evidence")
    master = root / "MASTER_EN.md"
    if file_identity(master) != {key: manifest["master_en"][key] for key in ("bytes", "sha256")}:
        raise SourceChoiceError("review master identity drift")
    bindings = _read(root / "ISSUE_EN_BINDINGS.v1.json")
    try:
        validate_seal(bindings, "bindings_sha256")
    except ValueError as error:
        raise SourceChoiceError("issue bindings seal is invalid") from error
    provenance_record = manifest.get("provenance")
    if (not isinstance(provenance_record, dict) or set(provenance_record) != {"path", "bytes", "sha256"}
            or provenance_record["path"] != "MASTER_EN.provenance.json"):
        raise SourceChoiceError("review master provenance identity is malformed")
    provenance_path = root / provenance_record["path"]
    if not provenance_path.is_file() or file_identity(provenance_path) != {key: provenance_record[key] for key in ("bytes", "sha256")}:
        raise SourceChoiceError("review master provenance identity drift")
    provenance = _read(provenance_path)
    return master, manifest, _read(evidence_path), bindings, _source_identity(provenance.get("source"), "review master")


def _span(master: Path, binding: dict[str, Any]) -> tuple[str, int, int]:
    text = master.read_text(encoding="utf-8")
    start, end = binding.get("character_start"), binding.get("character_end")
    if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(text):
        raise SourceChoiceError("issue binding span is malformed")
    preimage = text[start:end]
    if sha256_bytes(preimage.encode()) != binding.get("text_sha256"):
        raise SourceChoiceError("issue binding preimage drift")
    return preimage, len(text[:start].encode()), len(text[:end].encode())


def _selector(issue: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    selector = issue.get("source_selector")
    if not isinstance(selector, dict) or set(selector) != {"mechanical_diagnostic"}:
        raise SourceChoiceError("pending choice selector must name one mechanical diagnostic")
    diagnostic = selector["mechanical_diagnostic"]
    if not isinstance(diagnostic, dict) or set(diagnostic) != {"code", "source_keys"}:
        raise SourceChoiceError("mechanical diagnostic selector is malformed")
    code, keys = diagnostic.get("code"), diagnostic.get("source_keys")
    valid = isinstance(code, str) and bool(code) and isinstance(keys, list) and bool(keys)
    valid = valid and all(isinstance(key, dict) and set(key) == {"view", "raw_index"} and isinstance(key["view"], str) and type(key["raw_index"]) is int for key in keys)
    if not valid or len({(key["view"], key["raw_index"]) for key in keys}) != len(keys):
        raise SourceChoiceError("mechanical diagnostic selector is invalid")
    return code, keys


def _candidate_source(report: dict[str, Any]) -> dict[str, Any]:
    authorities = report.get("authorities")
    source = authorities.get("source") if isinstance(authorities, dict) else None
    if (not isinstance(source, dict) or set(source) != {"path_hint", "bytes", "sha256"}
            or not isinstance(source["path_hint"], str) or not source["path_hint"]
            or type(source["bytes"]) is not int or source["bytes"] < 1
            or not isinstance(source["sha256"], str) or len(source["sha256"]) != 64
            or any(char not in "0123456789ABCDEF" for char in source["sha256"])):
        raise SourceChoiceError("mechanical candidate source authority is malformed")
    return source


def _issue_source(issue: dict[str, Any], candidate_source: dict[str, Any]) -> str:
    source_sha = issue.get("source_pdf_sha256")
    if (not isinstance(source_sha, str) or len(source_sha) != 64
            or any(char not in "0123456789ABCDEF" for char in source_sha)):
        raise SourceChoiceError("pending issue source identity is malformed")
    if source_sha != candidate_source["sha256"]:
        raise SourceChoiceError("pending issue source identity does not match mechanical candidate")
    return source_sha


def _alternatives(report: dict[str, Any], issue: dict[str, Any], root: Path, candidate_source: dict[str, Any]) -> list[dict[str, Any]]:
    code, keys = _selector(issue)
    matches = [row for row in report["diagnostics"] if row["code"] == code and row["page"] == issue["source_page"] and row["source_keys"] == keys]
    if len(matches) != 1:
        raise SourceChoiceError("pending issue does not select one mechanical diagnostic")
    page_row = next((row for row in report["pages"] if row["source_page"] == issue["source_page"]), None)
    if page_row is None:
        raise SourceChoiceError("mechanical diagnostic page is absent")
    packet = Path(report["run_root"]) / "outputs/04-visual-merge-bundle/merge_packets/pages" / page_row["packet"]["path"]
    if file_identity(packet) != {key: page_row["packet"][key] for key in ("bytes", "sha256")}:
        raise SourceChoiceError("mechanical packet identity drift")
    rows = []
    for view_row in matches[0]["alternatives"]:
        view, blocks = view_row.get("view"), view_row.get("blocks")
        view_keys = [key for key in keys if key["view"] == view]
        if len(view_keys) != 1 or not isinstance(blocks, list) or len(blocks) != 1:
            raise SourceChoiceError("mechanical diagnostic lacks one exact source block per view")
        block, key = blocks[0], view_keys[0]
        if not isinstance(block, dict) or block.get("raw_index") != key["raw_index"] or not isinstance(block.get("text"), str):
            raise SourceChoiceError("mechanical alternative is not bound to its source key")
        text, text_hash = block["text"], sha256_bytes(block["text"].encode())
        if block.get("text_sha256") != text_hash:
            raise SourceChoiceError("mechanical alternative text identity drift")
        locator = {"view": view, "raw_index": key["raw_index"], "field": "text"}
        alt_hash = sha256_bytes(canonical_bytes({"source_pdf_sha256": candidate_source["sha256"], "page": issue["source_page"], "code": code, "source_keys": keys, "locator": locator, "text_sha256": text_hash}))
        rows.append({"alternative_id": f"mechanical:{alt_hash}", "text": text, "text_sha256": text_hash, "selectable": bool(text), "source_locator": locator, "evidence": {"source": candidate_source, "mechanical_draft": _record(root / "mechanical_draft.json"), "packet": _record(packet)}})
    if len({row["alternative_id"] for row in rows}) != len(rows):
        raise SourceChoiceError("mechanical diagnostic alternatives are not uniquely located")
    distinct_nonempty = {row["text_sha256"] for row in rows if row["selectable"]}
    if not distinct_nonempty:
        raise SourceChoiceError("mechanical diagnostic has no supported reading")
    if len(distinct_nonempty) == 1:
        raise SourceChoiceError("mechanical diagnostic has only one supported reading")
    return rows


def _packet_source_block(report: dict[str, Any], issue: dict[str, Any], key: dict[str, Any]) -> dict[str, Any]:
    """Reopen one selected raw container by its sealed packet locator."""
    page_row = next((row for row in report["pages"] if row.get("source_page") == issue.get("source_page")), None)
    if not isinstance(page_row, dict):
        raise SourceChoiceError("composite source packet page is absent")
    packet = Path(report["run_root"]) / "outputs/04-visual-merge-bundle/merge_packets/pages" / page_row["packet"]["path"]
    if file_identity(packet) != {name: page_row["packet"][name] for name in ("bytes", "sha256")}:
        raise SourceChoiceError("composite source packet identity drift")
    value = _read(packet); views = value.get("views", {})
    blocks = views.get(key.get("view"), {}).get("blocks", []) if isinstance(views, dict) else []
    matches = [row for row in blocks if isinstance(row, dict) and row.get("raw_index") == key.get("raw_index")]
    if len(matches) != 1 or not isinstance(matches[0].get("text"), str):
        raise SourceChoiceError("composite selected source container is absent or ambiguous")
    text = matches[0]["text"]
    # Stage04 packet blocks need not carry the diagnostic's text_sha256 field.
    # The packet seal owns these bytes; semantic/Stage05 replay checks the raw
    # digest against the selected container's independent evidence below.
    if "text_sha256" in matches[0] and matches[0]["text_sha256"] != sha256_bytes(text.encode()):
        raise SourceChoiceError("composite selected source container identity drift")
    return {"text": text, "packet": _record(packet), "source_locator": {"view": key["view"], "raw_index": key["raw_index"], "field": "text"}}


def _derive(review_master: Path, candidate: Path) -> dict[str, Any]:
    master, manifest, evidence, bindings, master_source = _master(review_master)
    candidate = candidate.resolve()
    try:
        report = verify_mechanical_draft(candidate)
    except Exception as error:
        raise SourceChoiceError(f"mechanical candidate verification failed: {error}") from error
    candidate_source = _candidate_source(report)
    if _source_identity(candidate_source, "mechanical candidate") != master_source:
        raise SourceChoiceError("review master source identity does not match mechanical candidate")
    issues = evidence.get("source_issues", {}).get("issues")
    if not isinstance(issues, list):
        raise SourceChoiceError("source issue census is malformed")
    if any(isinstance(row, dict) and row.get("kind") == "source_material_blocked" for row in issues):
        raise SourceChoiceError("source material is blocked or unplaceable")
    binding_rows = bindings.get("bindings")
    if not isinstance(binding_rows, list):
        raise SourceChoiceError("issue bindings are malformed")
    bound = {row.get("issue_id"): row for row in binding_rows if isinstance(row, dict)}
    if len(bound) != len(binding_rows):
        raise SourceChoiceError("issue bindings duplicate an issue")
    choices, spans = [], []
    for issue in [row for row in issues if isinstance(row, dict) and row.get("kind") == PENDING_KIND]:
        issue_id = issue.get("issue_id")
        if not isinstance(issue_id, str) or issue_id not in bound:
            raise SourceChoiceError("pending issue lacks an exact EN binding")
        source_sha = _issue_source(issue, candidate_source)
        preimage, start, end = _span(master, bound[issue_id])
        if any(max(start, low) < min(end, high) for low, high in spans):
            raise SourceChoiceError("source-choice spans overlap")
        spans.append((start, end))
        alternatives = _alternatives(report, issue, candidate, candidate_source)
        provisional = [row["alternative_id"] for row in alternatives if row["selectable"] and row["text"] == preimage]
        if not provisional:
            raise SourceChoiceError("R0 preimage is not a mechanical alternative")
        choices.append({"choice_id": f"choice:{issue_id}", "issue_id": issue_id, "source_pdf_sha256": source_sha, "source_page": issue["source_page"], "issue_kind": PENDING_KIND, "reason": issue.get("reason", ""), "r0_span": {"character_start": bound[issue_id]["character_start"], "character_end": bound[issue_id]["character_end"], "byte_start": start, "byte_end": end, "text": preimage, "text_sha256": sha256_bytes(preimage.encode())}, "source_selector": issue["source_selector"], "alternatives": alternatives, "provisional_alternative_ids": provisional, "provisional_alternative_id": provisional[0]})
    return sealed(QUEUE_SCHEMA, {"state": "sealed_pre_r1", "acceptance": "pending", "review_master": _record(master), "review_manifest": _record(master.parent / "MANIFEST.json"), "final_evidence": _record(_check_record(manifest["final_evidence"], "review final evidence")), "issue_bindings": _record(master.parent / "ISSUE_EN_BINDINGS.v1.json"), "candidate": _tree_record(candidate), "candidate_source": candidate_source, "choices": choices}, digest_key="queue_sha256")


def prepare(review_master: Path, candidate: Path, output: Path) -> dict[str, Any]:
    # New review masters carry dual occurrence bindings and must enter the
    # versioned raw-vs-reader route.  v1 is retained only for frozen packages.
    if (Path(review_master).resolve() / "ISSUE_EN_BINDINGS.v2.json").is_file():
        return prepare_v2(review_master, candidate, output)
    _reject_overlap(Path(output), Path(review_master), Path(candidate))
    value = _derive(Path(review_master), Path(candidate))
    target = Path(output) / "SOURCE_CHOICE_QUEUE.v1.json"; _write_immutable(target, value)
    template = {"schema": SUBMISSION_SCHEMA, "state": "submitted", "queue": _record(target), "choices": [{"issue_id": row["issue_id"], "disposition": None, "alternative_id": None, "reason": "", "label": None} for row in value["choices"]]}
    template_path = Path(output) / "SOURCE_CHOICE_SUBMISSION_TEMPLATE.v1.json"; _write_immutable(template_path, template)
    return {"state": "verified", "queue": str(target), "submission_template": str(template_path), "choices": len(value["choices"]), "queue_sha256": value["queue_sha256"]}


def verify_queue(queue: Path) -> dict[str, Any]:
    path = Path(queue) if Path(queue).is_file() else Path(queue) / "SOURCE_CHOICE_QUEUE.v1.json"
    value = _read(path)
    try: validate_seal(value, "queue_sha256")
    except ValueError as error: raise SourceChoiceError("queue seal is invalid") from error
    if value.get("schema") != QUEUE_SCHEMA: raise SourceChoiceError("queue schema is invalid")
    master = _check_record(value.get("review_master"), "queue review master")
    candidate = _check_tree(value.get("candidate"), "queue mechanical candidate")
    if value != _derive(master.parent, candidate):
        raise SourceChoiceError("queue differs from freshly derived authority")
    return {"state": "verified", "queue": str(path.resolve()), "choices": len(value["choices"]), "queue_sha256": value["queue_sha256"], "review_master": str(master), "candidate": str(candidate)}


def record_decisions(queue: Path, decisions: Path | dict[str, Any] | list[dict[str, Any]], output: Path) -> dict[str, Any]:
    queue_path = Path(queue) if Path(queue).is_file() else Path(queue) / "SOURCE_CHOICE_QUEUE.v1.json"
    verified, value = verify_queue(queue_path), _read(queue_path)
    _reject_overlap(Path(output), queue_path, Path(verified["review_master"]).parent, Path(verified["candidate"]))
    if not isinstance(decisions, (str, Path)):
        raise SourceChoiceError("submission must be a queue-bound submission file")
    submission_path = Path(decisions)
    _reject_overlap(Path(output), submission_path)
    submitted = _read(submission_path)
    if not isinstance(submitted, dict) or set(submitted) != {"schema", "state", "queue", "choices"} or submitted.get("schema") != SUBMISSION_SCHEMA or submitted.get("state") != "submitted":
        raise SourceChoiceError("submission task binding is malformed")
    submitted_queue = _check_record(submitted.get("queue"), "submission queue")
    if submitted_queue.resolve() != queue_path.resolve() or submitted["queue"] != _record(queue_path):
        raise SourceChoiceError("submission is bound to a different queue")
    submission, ledger = _decision_records(queue_path, value, submitted["choices"])
    target = Path(output); _write_immutable(target / "SOURCE_CHOICE_SUBMISSION.v1.json", submission); _write_immutable(target / "SOURCE_CHOICE_LEDGER.v1.json", ledger)
    return {"state": "verified", "submission": str(target / "SOURCE_CHOICE_SUBMISSION.v1.json"), "ledger": str(target / "SOURCE_CHOICE_LEDGER.v1.json"), "ledger_sha256": ledger["ledger_sha256"]}


def _decision_records(queue_path: Path, value: dict[str, Any], rows: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive sealed decision records identically at write and consumption time."""
    if not isinstance(rows, list) or len(rows) != len(value["choices"]) or [row.get("issue_id") if isinstance(row, dict) else None for row in rows] != [row["issue_id"] for row in value["choices"]]:
        raise SourceChoiceError("submission rows are missing, extra, duplicated, or out of order")
    ledger_rows = []
    for choice, row in zip(value["choices"], rows):
        if set(row) - {"issue_id", "disposition", "alternative_id", "reason", "label"} or not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise SourceChoiceError("submission is malformed")
        alternative = next((item for item in choice["alternatives"] if item["alternative_id"] == row.get("alternative_id")), None)
        if alternative is None or not alternative["selectable"]: raise SourceChoiceError("unknown, empty, or free-form alternative")
        if row.get("disposition") == "selected_alternative": state, label = "resolved", None
        elif row.get("disposition") == "unresolved_semantic" and row.get("alternative_id") in choice["provisional_alternative_ids"] and row.get("label") in ALLOWED_LABELS: state, label = "retained", row["label"]
        else: raise SourceChoiceError("submission disposition is invalid")
        ledger_rows.append({"issue_id": choice["issue_id"], "alternative_id": alternative["alternative_id"], "reason": row["reason"], "disposition": row["disposition"], "label": label, "predecessor_span": choice["r0_span"], "successor_page_block_preimage": {"source_page": choice["source_page"], "source_selector": choice["source_selector"], "text_sha256": choice["r0_span"]["text_sha256"]}, "intended_successor_replacement": {"text_sha256": alternative["text_sha256"], "result_sha256": sha256_bytes(alternative["text"].encode()), "resulting_issue_state": state}, "source_evidence": alternative["evidence"]})
    submission = sealed(SUBMISSION_SCHEMA, {"state": "validated", "queue": _record(queue_path), "choices": rows}, digest_key="submission_sha256")
    ledger = sealed(LEDGER_SCHEMA, {"state": "sealed_pre_r1", "acceptance": "pending", "queue": _record(queue_path), "submission": {"schema": SUBMISSION_SCHEMA, "submission_sha256": submission["submission_sha256"]}, "source_choices": ledger_rows, "intended_successor": {"authority": "linguistic_source_choice", "r1_identity": None}}, digest_key="ledger_sha256")
    return submission, ledger


def verify_ledger(ledger: Path) -> dict[str, Any]:
    """Reopen all pre-R1 authority before a successor may consume choices."""
    path = Path(ledger) if Path(ledger).is_file() else Path(ledger) / "SOURCE_CHOICE_LEDGER.v1.json"
    value = _read(path)
    submission_path = path.parent / "SOURCE_CHOICE_SUBMISSION.v1.json"
    submission = _read(submission_path)
    try:
        validate_seal(value, "ledger_sha256")
        validate_seal(submission, "submission_sha256")
    except ValueError as error:
        raise SourceChoiceError("ledger or validated submission seal is invalid") from error
    if value.get("schema") != LEDGER_SCHEMA or submission.get("schema") != SUBMISSION_SCHEMA:
        raise SourceChoiceError("ledger or validated submission schema is invalid")
    queue_path = _check_record(value.get("queue"), "ledger queue")
    verified = verify_queue(queue_path)
    expected_submission, expected_ledger = _decision_records(queue_path, _read(queue_path), submission.get("choices"))
    if submission != expected_submission or value != expected_ledger:
        raise SourceChoiceError("ledger differs from verified queue and submission decisions")
    return {"state": "verified", "ledger": str(path.resolve()),
            "submission": str(submission_path.resolve()), "queue": str(queue_path.resolve()),
            "ledger_sha256": value["ledger_sha256"], "choices": len(value["source_choices"]),
            "review_master": verified["review_master"], "candidate": verified["candidate"]}


submit_decisions = record_decisions
record_decision = record_decisions
submit = record_decisions


# V2 deliberately keeps raw source witness text and the rendered reader text
# separate.  v1 remains available for verification of frozen predecessors.
def _master_v2(review_master: Path, *, binding_root: Path) -> tuple[Path, dict[str, Any], Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = review_master.resolve()
    try:
        verify_master_en(root, binding_root=binding_root)
        bindings = load_issue_en_bindings_v2(root)
    except (Exception, ReaderOccurrenceError) as error:
        raise SourceChoiceError(f"review master v2 verification failed: {error}") from error
    manifest = _read(root / "MANIFEST.json")
    evidence_path = _check_record(manifest.get("final_evidence"), "review final evidence")
    provenance = _read(root / "MASTER_EN.provenance.json")
    return root / "MASTER_EN.md", manifest, evidence_path, _read(evidence_path), bindings, _source_identity(provenance.get("source"), "review master")


def _provisional_raw_alternatives(issue: dict[str, Any], alternatives: list[dict[str, Any]], binding: dict[str, Any]) -> list[str]:
    source = binding.get("source_occurrence", {})
    raw_hash = source.get("source_excerpt_sha256") if isinstance(source, dict) else None
    if not isinstance(raw_hash, str):
        raise SourceChoiceError("v2 binding source occurrence is malformed")
    matches = [row for row in alternatives if row["selectable"] and row["text_sha256"] == raw_hash]
    if len(matches) == 1:
        return [matches[0]["alternative_id"]]
    # Equal raw witnesses must be disambiguated by a diagnostic source key.
    _, keys = _selector(issue)
    allowed = {(row["view"], row["raw_index"]) for row in keys}
    located = [row for row in matches if (row["source_locator"]["view"], row["source_locator"]["raw_index"]) in allowed]
    if len(located) != 1:
        raise SourceChoiceError("v2 raw provisional alternative is absent or ambiguous")
    return [located[0]["alternative_id"]]


def _adapt_atx_heading_alternatives(master_root: Path, binding: dict[str, Any], alternatives: list[dict[str, Any]], *, base_policy: str) -> None:
    """Apply a sealed ATX opener only when it is part of the R0 reader span."""
    anchor, span = binding.get("reader_anchor"), binding.get("page_reader_span")
    projection, record = binding.get("reader_projection"), binding.get("decision")
    if not isinstance(anchor, dict) or anchor.get("kind") != "semantic_unit_id": return
    if not isinstance(span, dict) or not isinstance(projection, dict) or not isinstance(record, dict): raise SourceChoiceError("v2 heading authority is malformed")
    unit_id, relative = anchor.get("semantic_unit_id"), record.get("path")
    path = master_root / relative if isinstance(relative, str) else None
    if not isinstance(unit_id, str) or path is None or not path.is_file() or file_identity(path) != {key: record.get(key) for key in ("bytes", "sha256")}:
        raise SourceChoiceError("v2 heading decision identity drift")
    decision = _read(path); units = decision.get("semantic_structure", {}).get("units", [])
    found = [unit for unit in units if isinstance(unit, dict) and unit.get("id") == unit_id]
    if len(found) != 1: raise SourceChoiceError("v2 heading semantic unit is ambiguous")
    unit = found[0]
    if unit.get("kind") != "heading" or unit.get("representation") != "atx_heading" or type(unit.get("heading_level")) is not int or not 1 <= unit["heading_level"] <= 6: return
    markdown, line_span = decision.get("markdown"), unit.get("markdown_span"); start, end = span.get("character_start"), span.get("character_end")
    preimage = projection.get("reader_text")
    if not isinstance(markdown, str) or not isinstance(line_span, dict) or type(start) is not int or type(end) is not int or not isinstance(preimage, str) or markdown[start:end] != preimage: raise SourceChoiceError("v2 heading reader preimage is stale")
    lines = markdown.split("\n"); first, last = line_span.get("start_line"), line_span.get("end_line")
    if type(first) is not int or type(last) is not int or first != last or not 1 <= first <= len(lines) or line_span.get("sha256") != sha256_bytes(lines[first - 1].encode()): raise SourceChoiceError("v2 heading unit span is malformed")
    unit_start = sum(len(line) + 1 for line in lines[:first - 1]); unit_end = unit_start + len(lines[first - 1])
    if not unit_start <= start < end <= unit_end:
        raise SourceChoiceError("v2 heading reader span escapes its declared unit")
    pattern = r"(?P<opener>(?:>[ \t]*)?#{%d}[ \t]+)(?P<payload>[^\n]+)" % unit["heading_level"]
    original = re.fullmatch(pattern, preimage)
    if original is None: return
    opener = original.group("opener")
    quote = r">[ \t]*" if opener.startswith(">") else ""
    candidate_pattern = quote + r"#{%d}[ \t]+(?P<payload>[^ \t\n][^\n]*)" % unit["heading_level"]
    for alternative in alternatives:
        value = alternative["reader_text"]
        wrapped = re.fullmatch(candidate_pattern, value)
        if wrapped is not None: payload = wrapped.group("payload")
        elif "\n" not in value and value and not re.match(r"(?:>|\||[-*+] |\d+[.)] |#)", value): payload = value
        else: raise SourceChoiceError("v2 heading alternative has an unsupported container")
        final = opener + payload
        alternative["reader_text"], alternative["reader_text_sha256"] = final, sha256_bytes(final.encode())
        alternative["reader_adapter"] = {"policy": "atx_heading_container_v1", "semantic_unit_id": unit_id, "heading_level": unit["heading_level"], "unit_span_sha256": line_span["sha256"], "r0_preimage_sha256": sha256_bytes(preimage.encode()), "opener": opener, "opener_sha256": sha256_bytes(opener.encode()), "base_policy": base_policy, "payload_sha256": sha256_bytes(payload.encode()), "reader_text_sha256": alternative["reader_text_sha256"]}


def _packet_text_blocks(packet_path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    """Open a sealed Stage04 packet into exact text containers."""
    packet = _read(packet_path)
    views = packet.get("views") if isinstance(packet, dict) else None
    if not isinstance(views, dict):
        raise SourceChoiceError("v2 correction packet views are malformed")
    blocks: dict[tuple[str, int], dict[str, Any]] = {}
    for view, payload in views.items():
        rows = payload.get("blocks") if isinstance(view, str) and isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise SourceChoiceError("v2 correction packet blocks are malformed")
        for row in rows:
            raw_index = row.get("raw_index") if isinstance(row, dict) else None
            if type(raw_index) is not int or not isinstance(row.get("text"), str):
                continue
            key = (view, raw_index)
            if key in blocks:
                raise SourceChoiceError("v2 correction packet text block is duplicate")
            blocks[key] = row
    return blocks


def _reviewed_block_correction_replay(
    binding: dict[str, Any], anchor_alt: dict[str, Any], decision: dict[str, Any],
    *, key: dict[str, Any], page: int,
) -> tuple[str, dict[str, Any]]:
    """Replay only one sealed selected raw block through reviewed corrections."""
    from .semantic_structure import (
        SemanticStructureError, apply_reviewed_text_corrections,
        reviewed_block_text_corrections,
    )

    locator = (key.get("view"), key.get("raw_index"))
    if not isinstance(locator[0], str) or type(locator[1]) is not int:
        raise SourceChoiceError("v2 correction anchor key is malformed")
    evidence = anchor_alt.get("evidence")
    packet_record = evidence.get("packet") if isinstance(evidence, dict) else None
    try:
        packet_path = _check_record(packet_record, "v2 correction packet")
        packet_blocks = _packet_text_blocks(packet_path)
    except SourceChoiceError:
        raise
    if locator not in packet_blocks or packet_blocks[locator].get("text") != anchor_alt.get("raw_text"):
        raise SourceChoiceError("v2 correction anchor raw packet preimage is stale")
    selected = {
        (row.get("view"), row.get("raw_index"))
        for row in decision.get("selected_blocks", [])
        if isinstance(row, dict) and row.get("purpose") != "asset"
    }
    if locator not in selected:
        raise SourceChoiceError("v2 correction anchor is not selected text")
    markdown = decision.get("markdown")
    if not isinstance(markdown, str):
        raise SourceChoiceError("v2 correction decision Markdown is malformed")
    try:
        corrections = reviewed_block_text_corrections(
            decision, packet_blocks, selected, markdown, page,
        )
    except (SemanticStructureError, ValueError) as error:
        raise SourceChoiceError(f"v2 reviewed block correction proof failed: {error}") from error
    pairs = corrections.get(locator)
    if not pairs:
        raise SourceChoiceError("v2 raw reader anchor cannot replay the R0 reader preimage")
    rows = [
        row for row in decision.get("reviewed_block_corrections", [])
        if isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == locator
    ]
    if len(rows) != len(pairs):
        raise SourceChoiceError("v2 correction row proof is incomplete")
    # The semantic validator proves the original intervals do not overlap.  A
    # source-order replay is therefore independent of JSON row order.
    rows.sort(key=lambda row: anchor_alt["raw_text"].index(row["before"]))
    ordered_pairs = [(row["before"], row["after"]) for row in rows]
    if ordered_pairs != sorted(pairs, key=lambda pair: anchor_alt["raw_text"].index(pair[0])):
        raise SourceChoiceError("v2 correction rows differ from sealed correction proof")
    corrected = apply_reviewed_text_corrections(anchor_alt["raw_text"], locator, [], {locator: ordered_pairs})
    from .reviewed_label_partition import project_label_partition
    from .reviewed_quote_projection import project_corrected_quote
    try:
        partition = project_label_partition(decision, packet_blocks, locator, corrections, page)
        quote = project_corrected_quote(decision, packet_blocks, locator, corrections, page)
    except ValueError as error:
        raise SourceChoiceError(f"v2 label partition replay failed: {error}") from error
    if partition is not None:
        corrected = partition[0]
    if quote is not None:
        corrected = quote[0]
    if not corrected:
        raise SourceChoiceError("v2 correction replay produced an empty reader preimage")
    proof = {
        "policy": "reviewed_block_correction_v1",
        "source_locator": anchor_alt["source_locator"],
        "raw_text_sha256": anchor_alt["raw_text_sha256"],
        "correction_rows": [
            {"row_sha256": sha256_bytes(canonical_bytes(row)), "before_sha256": sha256_bytes(row["before"].encode()),
             "after_sha256": sha256_bytes(row["after"].encode())}
            for row in rows
        ],
        "corrected_text_sha256": sha256_bytes(corrected.encode()),
        "decision": binding.get("decision"),
    }
    if partition is not None:
        proof["label_partition"] = partition[1]
    if quote is not None:
        proof["quote_container"] = quote[1]
    return corrected, proof


def _strong_presentation_proof(corrected: str, reader: str) -> dict[str, Any]:
    """Prove reader-only strong markers preserve the corrected bytes exactly."""
    markers: list[dict[str, Any]] = []
    output: list[str] = []
    cursor = 0
    while cursor < len(reader):
        if reader.startswith("**", cursor) or reader.startswith("__", cursor):
            marker = reader[cursor:cursor + 2]
            close = reader.find(marker, cursor + 2)
            if close < 0 or close == cursor + 2:
                raise SourceChoiceError("v2 strong reader presentation markers are malformed")
            if "**" in reader[cursor + 2:close] or "__" in reader[cursor + 2:close]:
                raise SourceChoiceError("v2 strong reader presentation markers overlap")
            payload_start, payload_end = cursor + 2, close
            payload = reader[payload_start:payload_end]
            output.append(payload)
            markers.append({"marker_start": payload_start, "marker_end": payload_end,
                            "payload_sha256": sha256_bytes(payload.encode())})
            cursor = close + 2
            continue
        output.append(reader[cursor])
        cursor += 1
    if not markers or "".join(output) != corrected:
        raise SourceChoiceError("v2 strong reader presentation differs from corrected text")
    return {"corrected_text_sha256": sha256_bytes(corrected.encode()),
            "reader_text_sha256": sha256_bytes(reader.encode()), "markers": markers}


def _raw_reader_replay(master_root: Path, binding: dict[str, Any], alternatives: list[dict[str, Any]], *, stage05_pages: dict[int, dict[str, Any]], anchor_container: dict[str, Any] | None = None) -> dict[str, Any]:
    """Derive the packet-witness policy from the exact R0 reader anchor."""
    anchor = binding.get("reader_anchor", {}); projection = binding.get("reader_projection", {})
    key = anchor.get("selected_source_key") if isinstance(anchor, dict) else None
    if key is None and isinstance(anchor, dict) and isinstance(anchor.get("selected_source_keys"), list) and len(anchor["selected_source_keys"]) == 1:
        key = anchor["selected_source_keys"][0]
    if not isinstance(key, dict) or not isinstance(projection, dict):
        raise SourceChoiceError("v2 raw reader anchor is malformed")
    matched = [row for row in alternatives if row["selectable"] and row["source_locator"].get("view") == key.get("view") and row["source_locator"].get("raw_index") == key.get("raw_index")]
    if len(matched) != 1:
        # The selected semantic owner may be a larger raw container while the
        # diagnostic alternatives name only its reader-visible tail.  Derive
        # the tail exclusively by sealed unit and reader coordinates.
        if len(matched) or not isinstance(anchor_container, dict):
            raise SourceChoiceError("v2 raw reader anchor is absent or ambiguous")
        return _composite_source_slice_replay(master_root, binding, alternatives, stage05_pages=stage05_pages,
                                              key=key, anchor_container=anchor_container)
    anchor_alt, preimage = matched[0], projection.get("reader_text")
    if anchor_alt["raw_text"] == preimage:
        policy, reader_anchor = "identity_v1", anchor_alt["raw_text"]
        correction_replay = None
    elif display_text(anchor_alt["raw_text"]) == preimage:
        policy, reader_anchor = "display_text_v1", display_text(anchor_alt["raw_text"])
        correction_replay = None
    else:
        # The correction helper below performs its own sealed decision, packet,
        # selected-text, source-interval, and visible-reader proof checks.
        correction_replay = None
        reader_anchor = ""
        policy = "reviewed_block_correction_v1"
    span, decision_record, audit_record = binding.get("page_reader_span"), binding.get("decision"), binding.get("stage05_audit")
    if not isinstance(span, dict) or not isinstance(decision_record, dict) or not isinstance(audit_record, dict):
        raise SourceChoiceError("v2 raw reader replay evidence is malformed")
    relative = decision_record.get("path")
    decision_path = master_root / relative if isinstance(relative, str) else None
    if decision_path is None or not decision_path.is_file() or file_identity(decision_path) != {key: decision_record.get(key) for key in ("bytes", "sha256")}:
        raise SourceChoiceError("v2 raw reader decision identity drift")
    decision = _read(decision_path); markdown = decision.get("markdown")
    start, end = span.get("character_start"), span.get("character_end")
    if (not isinstance(markdown, str) or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(markdown)
            or markdown[start:end] != preimage or span.get("text_sha256") != sha256_bytes(preimage.encode())
            or span.get("decision_markdown_sha256") != sha256_bytes(markdown.encode())):
        raise SourceChoiceError("v2 raw reader span or decision preimage is stale")
    page = binding.get("source_page")
    if type(page) is not int:
        raise SourceChoiceError("v2 correction source page is malformed")
    if policy == "reviewed_block_correction_v1":
        corrected, correction_replay = _reviewed_block_correction_replay(
            binding, anchor_alt, decision, key=key, page=page,
        )
        if corrected == preimage:
            presentation_policy, reader_anchor = "identity_v1", corrected
        elif display_text(corrected) == preimage:
            presentation_policy, reader_anchor = "display_text_v1", display_text(corrected)
        else:
            presentation_proof = _strong_presentation_proof(corrected, preimage)
            full_anchor = [row for row in decision.get("reviewed_block_corrections", [])
                           if isinstance(row, dict) and row.get("view") == key.get("view")
                           and row.get("raw_index") == key.get("raw_index")
                           and row.get("before") == anchor_alt["raw_text"]
                           and row.get("after") == corrected]
            if len(full_anchor) != 1 or len(corrected) <= len(anchor_alt["raw_text"]):
                raise SourceChoiceError("v2 strong reader presentation lacks an expanded whole-block correction")
            presentation_policy, reader_anchor = "reviewed_block_correction_strong_display_v1", preimage
            correction_replay["presentation_policy"] = presentation_policy
            correction_replay["presentation_proof"] = presentation_proof
            # Other witnesses remain evidence, but their truncated raw source
            # cannot claim the reviewed continuation in this reader container.
            for row in alternatives:
                if row is not anchor_alt:
                    row["selectable"] = False
                    row["nonselectable_reason"] = "requires_separate_reviewed_source_correction"
    else:
        presentation_policy = policy
    stage05_page = stage05_pages.get(page)
    if not isinstance(stage05_page, dict):
        raise SourceChoiceError("v2 raw reader Stage05 page proof is absent or ambiguous")
    stream = stage05_page.get("ordered_proof_stream")
    if not isinstance(stream, list):
        raise SourceChoiceError("v2 raw reader Stage05 proof stream is absent")
    selected = [(index, row) for index, row in enumerate(stream) if isinstance(row, dict) and row.get("kind") == "selected"
                and row.get("unit", {}).get("view_id") == key.get("view") and row.get("unit", {}).get("raw_index") == key.get("raw_index")]
    decision_selected = [row for row in decision.get("selected_blocks", []) if isinstance(row, dict) and row.get("purpose") != "asset"
                         and row.get("view") == key.get("view") and row.get("raw_index") == key.get("raw_index")]
    if (len(selected) != 1 or len(decision_selected) != 1
            or selected[0][1].get("unit", {}).get("original_text_sha256") != anchor_alt["raw_text_sha256"]):
        raise SourceChoiceError("v2 raw reader selected Stage05 or decision proof is absent or ambiguous")
    selected_index, selected_row = selected[0]
    for row in alternatives:
        # Corrections are bound to the selected anchor locator alone.  Every
        # other diagnostic witness keeps projection from its own immutable raw.
        reader = (reader_anchor if row is anchor_alt else
                  (row["raw_text"] if presentation_policy == "identity_v1" else display_text(row["raw_text"])))
        quote_proof = correction_replay.get("quote_container") if correction_replay else None
        if quote_proof is not None:
            from .reviewed_quote_projection import quote_text
            if row is not anchor_alt and row["selectable"]:
                reader = quote_text(reader)
            row["reader_adapter"] = {"policy": "reviewed_quote_container_v1",
                                     "semantic_unit_id": quote_proof["semantic_unit_id"],
                                     "unit_span_sha256": quote_proof["markdown_span"]["sha256"],
                                     "reader_text_sha256": sha256_bytes(reader.encode())}
        if row is anchor_alt and presentation_policy == "reviewed_block_correction_strong_display_v1":
            proof = correction_replay["presentation_proof"]
            row["reader_adapter"] = {
                "policy": "reviewed_corrected_reader_retention_v1",
                "anchor_source_locator": anchor_alt["source_locator"],
                "anchor_raw_text_sha256": anchor_alt["raw_text_sha256"],
                "corrected_text_sha256": proof["corrected_text_sha256"],
                "reader_text_sha256": proof["reader_text_sha256"],
                "presentation_proof_sha256": sha256_bytes(canonical_bytes(proof)),
            }
        row["reader_text"], row["reader_text_sha256"] = reader, sha256_bytes(reader.encode())
    result = {"schema": "kb_creator.raw_reader_replay.v1", "base_policy": policy,
            "anchor_source_locator": anchor_alt["source_locator"], "anchor_alternative_id": anchor_alt["alternative_id"],
            "anchor_raw_text_sha256": anchor_alt["raw_text_sha256"], "r0_reader_text_sha256": projection.get("reader_text_sha256"),
            "r0_reader_span": span, "r0_preimage_sha256": sha256_bytes(preimage.encode()), "decision": decision_record, "stage05_audit": audit_record,
            "selected_row_proof": {"stream_index": selected_index, "source_locator": anchor_alt["source_locator"], "raw_text_sha256": anchor_alt["raw_text_sha256"], "row_sha256": sha256_bytes(canonical_bytes(selected_row)), "decision_selected_row_sha256": sha256_bytes(canonical_bytes(decision_selected[0]))}}
    if correction_replay is not None:
        result["correction_replay"] = correction_replay
        result["presentation_policy"] = presentation_policy
        if presentation_policy == "reviewed_block_correction_strong_display_v1":
            result["presentation_proof"] = correction_replay["presentation_proof"]
    return result


def _composite_source_slice_replay(master_root: Path, binding: dict[str, Any], alternatives: list[dict[str, Any]], *, stage05_pages: dict[int, dict[str, Any]], key: dict[str, Any], anchor_container: dict[str, Any]) -> dict[str, Any]:
    """Derive a v2 replay for a sealed raw subinterval, without text search."""
    from .source_choice_slice import slice_record
    from .semantic_structure import _normalized
    projection, span, decision_record = binding.get("reader_projection"), binding.get("page_reader_span"), binding.get("decision")
    if not isinstance(projection, dict) or not isinstance(span, dict) or not isinstance(decision_record, dict):
        raise SourceChoiceError("composite reader evidence is malformed")
    decision_path = master_root / decision_record.get("path", "")
    if not decision_path.is_file() or file_identity(decision_path) != {name: decision_record.get(name) for name in ("bytes", "sha256")}:
        raise SourceChoiceError("composite decision identity drift")
    decision = _read(decision_path); markdown = decision.get("markdown"); preimage = projection.get("reader_text")
    unit_id = binding.get("reader_anchor", {}).get("semantic_unit_id")
    units = decision.get("semantic_structure", {}).get("units", [])
    units = [unit for unit in units if isinstance(unit, dict) and unit.get("id") == unit_id]
    if not isinstance(markdown, str) or not isinstance(preimage, str) or len(units) != 1:
        raise SourceChoiceError("composite semantic unit is absent or ambiguous")
    unit = units[0]; unit_span = unit.get("markdown_span", {}); lines = markdown.split("\n")
    first, last = unit_span.get("start_line"), unit_span.get("end_line")
    start, end = span.get("character_start"), span.get("character_end")
    if (type(first) is not int or type(last) is not int or not 1 <= first <= last <= len(lines)
            or unit_span.get("sha256") != sha256_bytes("\n".join(lines[first - 1:last]).encode())
            or type(start) is not int or type(end) is not int):
        raise SourceChoiceError("composite semantic unit or reader span is malformed")
    unit_start = sum(len(line) + 1 for line in lines[:first - 1]); unit_end = sum(len(line) + 1 for line in lines[:last]) - 1
    fragments = [row for row in unit.get("source_fragments", []) if isinstance(row, dict) and row.get("view") == key.get("view") and row.get("raw_index") == key.get("raw_index")]
    text = anchor_container.get("text")
    if (not unit_start <= start < end <= unit_end or len(fragments) != 1 or not isinstance(text, str)
            or fragments[0].get("start") != 0 or fragments[0].get("end") != len(text)
            or fragments[0].get("source_sha256") != sha256_bytes(text.encode())
            or fragments[0].get("fragment_sha256") != sha256_bytes(text.encode())
            or fragments[0].get("normalized_sha256") != sha256_bytes(_normalized(text).encode())
            or unit.get("source_blocks") != [{"view": key.get("view"), "raw_index": key.get("raw_index")}]
            or markdown[unit_start:unit_end] != text):
        raise SourceChoiceError("composite fragment-to-unit mapping is not byte exact")
    raw_start, raw_end = start - unit_start, end - unit_start
    interval = slice_record(text, raw_start, raw_end)
    if text[raw_start:raw_end] != preimage or span.get("text_sha256") != interval["raw_text_sha256"]:
        raise SourceChoiceError("composite raw slice differs from R0 reader preimage")
    page = binding.get("source_page"); stage = stage05_pages.get(page, {})
    stream = stage.get("ordered_proof_stream", []) if isinstance(stage, dict) else []
    rows = [(index, row) for index, row in enumerate(stream) if isinstance(row, dict) and row.get("kind") == "selected" and row.get("unit", {}).get("view_id") == key.get("view") and row.get("unit", {}).get("raw_index") == key.get("raw_index")]
    if len(rows) != 1 or rows[0][1].get("unit", {}).get("original_text_sha256") != sha256_bytes(text.encode()):
        raise SourceChoiceError("composite Stage05 selected container proof is absent or stale")
    selected_span = rows[0][1].get("markdown_span")
    normalized_page = _normalized(markdown)
    normalized_container = _normalized(text)
    unit_normalized_span = [len(_normalized(markdown[:unit_start])), len(_normalized(markdown[:unit_end]))]
    if (not isinstance(selected_span, list) or len(selected_span) != 2
            or any(type(value) is not int for value in selected_span)
            or selected_span != unit_normalized_span
            or not 0 <= selected_span[0] < selected_span[1] <= len(normalized_page)
            or normalized_page[selected_span[0]:selected_span[1]] != normalized_container):
        raise SourceChoiceError("composite Stage05 normalized container range differs from semantic unit")
    normalized_slice = [selected_span[0] + len(_normalized(text[:raw_start])),
                        selected_span[0] + len(_normalized(text[:raw_end]))]
    page_normalized_slice = [len(_normalized(markdown[:start])), len(_normalized(markdown[:end]))]
    if (normalized_slice != page_normalized_slice
            or not selected_span[0] <= normalized_slice[0] < normalized_slice[1] <= selected_span[1]
            or normalized_page[normalized_slice[0]:normalized_slice[1]] != _normalized(preimage)):
        raise SourceChoiceError("composite Stage05 normalized slice differs from reader preimage")
    selected_rows = [row for row in decision.get("selected_blocks", []) if isinstance(row, dict)
                     and row.get("purpose") != "asset" and row.get("view") == key.get("view")
                     and row.get("raw_index") == key.get("raw_index")]
    if len(selected_rows) != 1:
        raise SourceChoiceError("composite decision selected container proof is absent or ambiguous")
    baseline = [row for row in alternatives if row["selectable"] and row["raw_text_sha256"] == interval["raw_text_sha256"]]
    if len(baseline) != 1:
        raise SourceChoiceError("composite diagnostic baseline is absent or ambiguous")
    for row in alternatives:
        row["reader_text"], row["reader_text_sha256"] = row["raw_text"], row["raw_text_sha256"]
    return {"schema": "kb_creator.raw_reader_replay.v2", "anchor_mode": "composite_source_slice_v1", "base_policy": "identity_v1",
            "anchor_source_locator": anchor_container["source_locator"], "anchor_container_sha256": sha256_bytes(text.encode()),
            "semantic_unit_id": unit_id, "semantic_unit_markdown_sha256": unit_span["sha256"], "source_fragment": fragments[0],
            "raw_source_slice": interval, "r0_reader_span": span, "r0_preimage_sha256": interval["raw_text_sha256"],
            "normalized_source_slice": normalized_slice,
            "diagnostic_baseline_alternative_id": baseline[0]["alternative_id"], "decision": decision_record,
            "stage05_audit": binding.get("stage05_audit"), "selected_row_proof": {"stream_index": rows[0][0], "source_locator": anchor_container["source_locator"], "raw_text_sha256": sha256_bytes(text.encode()), "row_sha256": sha256_bytes(canonical_bytes(rows[0][1]))}}


def _stage05_pages(final_evidence: Path, evidence: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Open the sealed Stage05 authority once for one queue derivation."""
    record = evidence.get("authored", {}).get("stage05_audit") if isinstance(evidence, dict) else None
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"} or not isinstance(record["path"], str):
        raise SourceChoiceError("v2 final evidence lacks Stage05 audit authority")
    path = final_evidence.parent / record["path"]
    if not path.is_file() or file_identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
        raise SourceChoiceError("v2 final evidence Stage05 audit identity drift")
    audit = _read(path); pages = audit.get("pages")
    if not isinstance(pages, list):
        raise SourceChoiceError("v2 Stage05 audit pages are malformed")
    result = {row.get("source_page"): row for row in pages if isinstance(row, dict) and type(row.get("source_page")) is int}
    if len(result) != len(pages):
        raise SourceChoiceError("v2 Stage05 audit pages are duplicate or malformed")
    return result


def _derive_v2(review_master: Path, candidate: Path, *, binding_root: Path) -> dict[str, Any]:
    master, manifest, final_evidence, evidence, bindings, master_source = _master_v2(review_master, binding_root=binding_root)
    stage05_pages = _stage05_pages(final_evidence, evidence)
    candidate = candidate.resolve()
    try:
        report = verify_mechanical_draft(candidate)
    except Exception as error:
        raise SourceChoiceError(f"mechanical candidate verification failed: {error}") from error
    candidate_source = _candidate_source(report)
    if _source_identity(candidate_source, "mechanical candidate") != master_source:
        raise SourceChoiceError("review master source identity does not match mechanical candidate")
    issues = evidence.get("source_issues", {}).get("issues")
    if not isinstance(issues, list):
        raise SourceChoiceError("source issue census is malformed")
    if any(isinstance(row, dict) and row.get("kind") == "source_material_blocked" for row in issues):
        raise SourceChoiceError("source material is blocked or unplaceable")
    bound = {row.get("issue_id"): row for row in bindings.get("bindings", []) if isinstance(row, dict)}
    if len(bound) != len(bindings.get("bindings", [])):
        raise SourceChoiceError("v2 issue bindings duplicate an issue")
    choices, spans = [], []
    for issue in [row for row in issues if isinstance(row, dict) and row.get("kind") == PENDING_KIND]:
        issue_id = issue.get("issue_id"); binding = bound.get(issue_id)
        if not isinstance(issue_id, str) or not isinstance(binding, dict):
            raise SourceChoiceError("pending choice lacks an exact v2 EN binding")
        source_sha = _issue_source(issue, candidate_source)
        page_span = binding.get("page_reader_span")
        projection = binding.get("reader_projection")
        if (not isinstance(page_span, dict) or not isinstance(projection, dict)
                or not isinstance(projection.get("reader_text"), str)):
            raise SourceChoiceError("v2 reader binding is malformed")
        start, end = page_span.get("character_start"), page_span.get("character_end")
        if type(start) is not int or type(end) is not int or start < 0 or end <= start:
            raise SourceChoiceError("v2 reader span is malformed")
        # Reader offsets are relative to their individual decision pages.
        # Distinct pages routinely begin at zero, so only same-page spans can
        # collide.
        if any(issue["source_page"] == other_page and max(start, low) < min(end, high)
               for other_page, low, high in spans):
            raise SourceChoiceError("v2 reader spans overlap")
        spans.append((issue["source_page"], start, end))
        raw_alternatives = _alternatives(report, issue, candidate, candidate_source)
        alternatives = []
        for raw in raw_alternatives:
            alternatives.append({**raw, "raw_text": raw["text"], "raw_text_sha256": raw["text_sha256"],
                                 "reader_text": "", "reader_text_sha256": ""})
        if binding.get("stage05_audit") != evidence.get("authored", {}).get("stage05_audit"):
            raise SourceChoiceError("v2 binding Stage05 authority differs from final evidence")
        anchor_key = binding.get("reader_anchor", {}).get("selected_source_key") if isinstance(binding.get("reader_anchor"), dict) else None
        if anchor_key is None and isinstance(binding.get("reader_anchor"), dict):
            keys = binding["reader_anchor"].get("selected_source_keys", [])
            anchor_key = keys[0] if isinstance(keys, list) and len(keys) == 1 else None
        anchor_container = _packet_source_block(report, issue, anchor_key) if isinstance(anchor_key, dict) and not any(
            row["source_locator"].get("view") == anchor_key.get("view") and row["source_locator"].get("raw_index") == anchor_key.get("raw_index") for row in alternatives) else None
        replay = _raw_reader_replay(master.parent, binding, alternatives, stage05_pages=stage05_pages, anchor_container=anchor_container)
        _adapt_atx_heading_alternatives(master.parent, binding, alternatives, base_policy=replay["base_policy"])
        provisional = [row["alternative_id"] for row in alternatives if row["selectable"] and row["reader_text_sha256"] == projection.get("reader_text_sha256")]
        replay_baseline = replay.get("anchor_alternative_id", replay.get("diagnostic_baseline_alternative_id"))
        if replay_baseline not in provisional:
            raise SourceChoiceError("v2 raw provisional alternative does not project to R0 reader preimage")
        choices.append({"choice_id": f"choice:{issue_id}", "issue_id": issue_id, "source_pdf_sha256": source_sha,
                        "source_page": issue["source_page"], "issue_kind": PENDING_KIND, "reason": issue.get("reason", ""),
                        "source_selector": issue["source_selector"], "r0_source_preimage": binding["source_occurrence"],
                        "r0_reader_span": page_span, "reader_anchor": binding["reader_anchor"],
                        "reader_projection": projection, "raw_reader_replay": replay, "alternatives": alternatives,
                        "provisional_alternative_ids": provisional, "provisional_alternative_id": replay_baseline})
    return sealed(QUEUE_SCHEMA_V2, {"state": "sealed_pre_r1", "acceptance": "pending", "review_master": _record(master),
                  "review_manifest": _record(master.parent / "MANIFEST.json"),
                  "review_binding_root": str(binding_root.resolve()),
                  "final_evidence": _record(_check_record(manifest["final_evidence"], "review final evidence")),
                  "issue_bindings": _record(master.parent / "ISSUE_EN_BINDINGS.v2.json"), "candidate": _tree_record(candidate),
                  "candidate_source": candidate_source, "choices": choices}, digest_key="queue_sha256")


def prepare_v2(review_master: Path, candidate: Path, output: Path, *, binding_root: Path | None = None) -> dict[str, Any]:
    """Seal a v2 queue from dual source/reader review-master bindings."""
    _reject_overlap(Path(output), Path(review_master), Path(candidate))
    root = Path(binding_root).resolve() if binding_root is not None else Path(review_master).resolve().parent
    if not root.is_dir():
        raise SourceChoiceError("v2 review binding root is absent")
    value = _derive_v2(Path(review_master), Path(candidate), binding_root=root)
    target = Path(output) / "SOURCE_CHOICE_QUEUE.v2.json"; _write_immutable(target, value)
    template = {"schema": SUBMISSION_SCHEMA_V2, "state": "submitted", "queue": _record(target),
                "choices": [{"issue_id": row["issue_id"], "disposition": None, "alternative_id": None,
                             "reason": "", "label": None} for row in value["choices"]]}
    template_path = Path(output) / "SOURCE_CHOICE_SUBMISSION_TEMPLATE.v2.json"; _write_immutable(template_path, template)
    return {"state": "verified", "queue": str(target), "submission_template": str(template_path),
            "choices": len(value["choices"]), "queue_sha256": value["queue_sha256"]}


def verify_queue_v2(queue: Path) -> dict[str, Any]:
    path = Path(queue) if Path(queue).is_file() else Path(queue) / "SOURCE_CHOICE_QUEUE.v2.json"
    value = _read(path)
    try:
        validate_seal(value, "queue_sha256")
    except ValueError as error:
        raise SourceChoiceError("v2 queue seal is invalid") from error
    if value.get("schema") != QUEUE_SCHEMA_V2:
        raise SourceChoiceError("v2 queue schema is invalid")
    master = _check_record(value.get("review_master"), "v2 queue review master")
    candidate = _check_tree(value.get("candidate"), "v2 queue mechanical candidate")
    binding_root = Path(value.get("review_binding_root", ""))
    if not binding_root.is_dir():
        raise SourceChoiceError("v2 queue review binding root is absent")
    if value != _derive_v2(master.parent, candidate, binding_root=binding_root):
        raise SourceChoiceError("v2 queue differs from freshly derived authority")
    return {"state": "verified", "queue": str(path.resolve()), "choices": len(value["choices"]),
            "queue_sha256": value["queue_sha256"], "review_master": str(master), "candidate": str(candidate)}


def _decision_records_v2(queue_path: Path, queue: dict[str, Any], rows: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if (not isinstance(rows, list) or len(rows) != len(queue["choices"])
            or [row.get("issue_id") if isinstance(row, dict) else None for row in rows] != [choice["issue_id"] for choice in queue["choices"]]):
        raise SourceChoiceError("v2 submission rows are missing, extra, duplicated, or out of order")
    ledger_rows = []
    for choice, row in zip(queue["choices"], rows):
        if set(row) - {"issue_id", "disposition", "alternative_id", "reason", "label"} or not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise SourceChoiceError("v2 submission is malformed")
        alternative = next((item for item in choice["alternatives"] if item["alternative_id"] == row.get("alternative_id")), None)
        if not isinstance(alternative, dict) or not alternative.get("selectable"):
            raise SourceChoiceError("v2 submission names unknown or empty raw alternative")
        if row.get("disposition") == "selected_alternative": state, label = "resolved", None
        elif row.get("disposition") == "unresolved_semantic" and row.get("alternative_id") == choice["provisional_alternative_id"] and row.get("label") in ALLOWED_LABELS: state, label = "retained", row["label"]
        else: raise SourceChoiceError("v2 submission disposition is invalid")
        ledger_rows.append({"issue_id": choice["issue_id"], "alternative_id": alternative["alternative_id"],
            "reason": row["reason"], "disposition": row["disposition"], "label": label,
            "r0_source_preimage": choice["r0_source_preimage"], "r0_reader_span": choice["r0_reader_span"],
            "reader_anchor": choice["reader_anchor"], "reader_projection": choice["reader_projection"],
            "raw_reader_replay": choice["raw_reader_replay"],
            "chosen_raw_alternative": {"text_sha256": alternative["raw_text_sha256"], "source_locator": alternative["source_locator"], "raw_locator": alternative["source_locator"]},
            "intended_reader_successor": {"text": alternative["reader_text"], "text_sha256": alternative["reader_text_sha256"],
                "resulting_issue_state": state}, "reader_adapter": alternative.get("reader_adapter"), "source_evidence": alternative["evidence"]})
    submission = sealed(SUBMISSION_SCHEMA_V2, {"state": "validated", "queue": _record(queue_path), "choices": rows}, digest_key="submission_sha256")
    ledger = sealed(LEDGER_SCHEMA_V2, {"state": "sealed_pre_r1", "acceptance": "pending", "queue": _record(queue_path),
        "submission": {"schema": SUBMISSION_SCHEMA_V2, "submission_sha256": submission["submission_sha256"]},
        "source_choices": ledger_rows, "intended_successor": {"authority": "linguistic_source_choice", "r1_identity": None}}, digest_key="ledger_sha256")
    return submission, ledger


def record_decisions_v2(queue: Path, decisions: Path, output: Path) -> dict[str, Any]:
    queue_path = Path(queue) if Path(queue).is_file() else Path(queue) / "SOURCE_CHOICE_QUEUE.v2.json"
    verified, value = verify_queue_v2(queue_path), _read(queue_path)
    _reject_overlap(Path(output), queue_path, Path(verified["review_master"]).parent, Path(verified["candidate"]))
    submitted = _read(Path(decisions))
    if (not isinstance(submitted, dict) or set(submitted) != {"schema", "state", "queue", "choices"}
            or submitted.get("schema") != SUBMISSION_SCHEMA_V2 or submitted.get("state") != "submitted"
            or _check_record(submitted.get("queue"), "v2 submission queue").resolve() != queue_path.resolve()
            or submitted["queue"] != _record(queue_path)):
        raise SourceChoiceError("v2 submission task binding is malformed")
    submission, ledger = _decision_records_v2(queue_path, value, submitted["choices"])
    target = Path(output); _write_immutable(target / "SOURCE_CHOICE_SUBMISSION.v2.json", submission); _write_immutable(target / "SOURCE_CHOICE_LEDGER.v2.json", ledger)
    return {"state": "verified", "submission": str(target / "SOURCE_CHOICE_SUBMISSION.v2.json"),
            "ledger": str(target / "SOURCE_CHOICE_LEDGER.v2.json"), "ledger_sha256": ledger["ledger_sha256"]}


def verify_ledger_v2(ledger: Path) -> dict[str, Any]:
    path = Path(ledger) if Path(ledger).is_file() else Path(ledger) / "SOURCE_CHOICE_LEDGER.v2.json"
    value, submission = _read(path), _read(path.parent / "SOURCE_CHOICE_SUBMISSION.v2.json")
    try:
        validate_seal(value, "ledger_sha256"); validate_seal(submission, "submission_sha256")
    except ValueError as error:
        raise SourceChoiceError("v2 ledger or submission seal is invalid") from error
    if value.get("schema") != LEDGER_SCHEMA_V2 or submission.get("schema") != SUBMISSION_SCHEMA_V2:
        raise SourceChoiceError("v2 ledger or submission schema is invalid")
    queue_path = _check_record(value.get("queue"), "v2 ledger queue")
    verified = verify_queue_v2(queue_path)
    expected_submission, expected_ledger = _decision_records_v2(queue_path, _read(queue_path), submission.get("choices"))
    if value != expected_ledger or submission != expected_submission:
        raise SourceChoiceError("v2 ledger differs from verified queue and submission")
    return {"state": "verified", "ledger": str(path.resolve()), "submission": str((path.parent / "SOURCE_CHOICE_SUBMISSION.v2.json").resolve()),
            "queue": str(queue_path.resolve()), "ledger_sha256": value["ledger_sha256"], "choices": len(value["source_choices"]),
            "review_master": verified["review_master"], "candidate": verified["candidate"]}


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _snapshot_file(path: Path) -> tuple[bytes, tuple[int, str]]:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise SourceChoiceError(f"v2 snapshot input is absent: {path}") from error
    return data, (len(data), sha256_bytes(data))


@dataclass(frozen=True)
class VerifiedLedgerV2Snapshot:
    ledger_path: Path
    submission_path: Path
    queue_path: Path
    ledger_identity: tuple[int, str]
    submission_identity: tuple[int, str]
    queue_identity: tuple[int, str]
    ledger_bytes: bytes
    submission_bytes: bytes
    queue_bytes: bytes
    ledger_value: Mapping[str, Any]
    queue_value: Mapping[str, Any]
    ledger_by_issue: Mapping[str, Mapping[str, Any]]
    queue_by_issue: Mapping[str, Mapping[str, Any]]


_AUTHOR_SNAPSHOT_LOOKUP: ContextVar[Callable[[Path], VerifiedLedgerV2Snapshot] | None] = ContextVar(
    "author_ledger_snapshot_lookup", default=None,
)


@contextmanager
def _author_ledger_snapshot_scope(lookup: Callable[[Path], VerifiedLedgerV2Snapshot] | None) -> Iterator[None]:
    """Bind a private author-owned lookup to this call chain only."""
    token = _AUTHOR_SNAPSHOT_LOOKUP.set(lookup)
    try:
        yield
    finally:
        _AUTHOR_SNAPSHOT_LOOKUP.reset(token)


def _current_author_ledger_snapshot(path: Path) -> VerifiedLedgerV2Snapshot | None:
    lookup = _AUTHOR_SNAPSHOT_LOOKUP.get()
    return lookup(Path(path)) if lookup is not None else None


def _issue_map(rows: Any, label: str) -> Mapping[str, Mapping[str, Any]]:
    if not isinstance(rows, list):
        raise SourceChoiceError(f"v2 {label} issue domain is malformed")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("issue_id"), str) or not row["issue_id"] or row["issue_id"] in result:
            raise SourceChoiceError(f"v2 {label} issue domain is malformed or duplicated")
        result[row["issue_id"]] = _freeze_json(row)
    return MappingProxyType(result)


def open_verified_ledger_v2_snapshot(ledger: Path) -> VerifiedLedgerV2Snapshot:
    path = (Path(ledger) if Path(ledger).is_file() else Path(ledger) / "SOURCE_CHOICE_LEDGER.v2.json").resolve()
    submission_path = path.parent / "SOURCE_CHOICE_SUBMISSION.v2.json"
    ledger_bytes, ledger_identity = _snapshot_file(path)
    submission_bytes, submission_identity = _snapshot_file(submission_path)
    try:
        ledger_value = json.loads(ledger_bytes)
        queue_path = Path(ledger_value["queue"]["path"]).resolve()
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise SourceChoiceError("v2 ledger queue binding is malformed") from error
    queue_bytes, queue_identity = _snapshot_file(queue_path)
    verified = verify_ledger_v2(path)
    for item_path, original in ((path, ledger_bytes), (submission_path, submission_bytes), (queue_path, queue_bytes)):
        if _snapshot_file(item_path)[0] != original:
            raise SourceChoiceError("v2 ledger snapshot changed during verification")
    queue_value = json.loads(queue_bytes)
    if (verified.get("ledger") != str(path) or verified.get("submission") != str(submission_path)
            or verified.get("queue") != str(queue_path) or verified.get("choices") != len(ledger_value["source_choices"])
            or verified.get("ledger_sha256") != ledger_value.get("ledger_sha256")
            or ledger_value["queue"] != {"path": str(queue_path), "bytes": queue_identity[0], "sha256": queue_identity[1]}):
        raise SourceChoiceError("v2 ledger verifier result differs from snapshot")
    ledger_by_issue = _issue_map(ledger_value.get("source_choices"), "ledger")
    queue_by_issue = _issue_map(queue_value.get("choices"), "queue")
    if ledger_by_issue.keys() != queue_by_issue.keys():
        raise SourceChoiceError("v2 ledger and queue issue domains differ")
    return VerifiedLedgerV2Snapshot(path, submission_path, queue_path, ledger_identity, submission_identity,
        queue_identity, ledger_bytes, submission_bytes, queue_bytes, _freeze_json(ledger_value),
        _freeze_json(queue_value), ledger_by_issue, queue_by_issue)


def reverify_ledger_v2_snapshot(snapshot: VerifiedLedgerV2Snapshot) -> None:
    verified = verify_ledger_v2(snapshot.ledger_path)
    if (verified.get("ledger") != str(snapshot.ledger_path) or verified.get("submission") != str(snapshot.submission_path)
            or verified.get("queue") != str(snapshot.queue_path)
            or verified.get("ledger_sha256") != snapshot.ledger_value["ledger_sha256"]
            or verified.get("choices") != len(snapshot.ledger_by_issue)):
        raise SourceChoiceError("v2 ledger verifier result differs from invocation snapshot")
    for path, expected in ((snapshot.ledger_path, snapshot.ledger_bytes),
                           (snapshot.submission_path, snapshot.submission_bytes),
                           (snapshot.queue_path, snapshot.queue_bytes)):
        if _snapshot_file(path)[0] != expected:
            raise SourceChoiceError("v2 ledger input changed since snapshot opening")
