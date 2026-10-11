"""Exact R1 dispositions for R0 reader-coverage claims consumed by a choice.

The source transcription claim remains immutable evidence.  A disposition only
states that one sealed choice replaces its reader interval, so Stage05 must not
try to prove the new reader text with the old transcription.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json

from .identity import canonical_bytes, file_identity, sha256_bytes
from .source_choice_translation import SourceChoiceError, verify_ledger_v2
from .source_choice_slice import SourceSlice, apply_sealed_slices
from .reader_text_coverage_binding import IndexedVisiblePage, _indexed_visible_reader

SCHEMA = "kb_creator.source_choice_coverage_successor.v1"


class SourceChoiceCoverageSuccessorError(ValueError):
    """A coverage disposition is absent, stale, or substitutes authority."""


def _record(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _key(value: Any, label: str) -> dict[str, Any]:
    required = {"source_page", "view_id", "raw_index"}
    if not isinstance(value, Mapping) or not required <= set(value):
        raise SourceChoiceCoverageSuccessorError(f"{label} key is malformed")
    if type(value["source_page"]) is not int or value["source_page"] < 1 or not isinstance(value["view_id"], str) or not value["view_id"] or type(value["raw_index"]) is not int or value["raw_index"] < 0:
        raise SourceChoiceCoverageSuccessorError(f"{label} key is malformed")
    return {name: value[name] for name in required}


def _locator(value: Any, label: str) -> dict[str, Any]:
    required = {"view", "raw_index", "field"}
    if not isinstance(value, Mapping) or set(value) != required or not isinstance(value["view"], str) or not value["view"] or type(value["raw_index"]) is not int or value["raw_index"] < 0 or value["field"] != "text":
        raise SourceChoiceCoverageSuccessorError(f"{label} locator is malformed")
    return dict(value)


def _open_record(record: Mapping[str, Any], root: Path | None = None) -> dict[str, Any]:
    if not isinstance(record, Mapping) or set(record) != {"path", "bytes", "sha256"}:
        raise SourceChoiceCoverageSuccessorError("coverage authority record is malformed")
    path = Path(record["path"])
    if root is not None:
        path = root / path
    if not path.is_file() or file_identity(path) != {k: record[k] for k in ("bytes", "sha256")}:
        raise SourceChoiceCoverageSuccessorError("coverage authority identity drift")
    return json.loads(path.read_text(encoding="utf-8"))


def _visible_span(page: IndexedVisiblePage, start: int, end: int) -> tuple[int, int, str]:
    """Resolve sealed raw coordinates through a valid complete-page projection."""
    try:
        return page.raw_interval(start, end)
    except ValueError as error:
        raise SourceChoiceCoverageSuccessorError(str(error)) from error


def project_claims(claims: list[Mapping[str, Any]], choices: list[dict[str, Any]],
                   queue_by_issue: Mapping[str, Any], decisions: Mapping[int, Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Derive exact claim projections from verified R0 claims and page choices."""
    pages: dict[int, dict[str, Any]] = {}
    covered_pages = {wrapped["claim"].get("reader_page") for wrapped in claims
                     if isinstance(wrapped, Mapping) and isinstance(wrapped.get("claim"), Mapping)}
    for choice in choices:
        if choice.get("disposition") != "selected_alternative":
            continue
        issue_id = choice["issue_id"]; queue_row = queue_by_issue[issue_id]
        page = queue_row["source_page"]
        if page not in covered_pages:
            continue
        markdown = decisions[page]["markdown"]
        context = pages.setdefault(page, {"markdown": markdown, "edits": [], "choices": []})
        span = choice["r0_reader_span"]; after = choice["intended_reader_successor"]["text"]
        start, end = span["character_start"], span["character_end"]
        edit = SourceSlice(start, end, span["text_sha256"], after)
        context["edits"].append(edit); context["choices"].append(choice)
    for context in pages.values():
        markdown = context["markdown"]
        successor = apply_sealed_slices(markdown, context["edits"], container_sha256=sha256_bytes(markdown.encode()))
        before_page = _indexed_visible_reader(markdown)
        after_page = _indexed_visible_reader(successor)
        before_visible = before_page.normalized
        after_visible = after_page.normalized
        visible_edits = []
        raw_delta = 0
        previous_end = 0
        for edit, choice in sorted(zip(context["edits"], context["choices"]), key=lambda pair: pair[0].start):
            if edit.start < previous_end:
                raise SourceChoiceCoverageSuccessorError("raw choices overlap")
            previous_end = edit.end
            new_start = edit.start + raw_delta
            new_end = new_start + len(edit.after)
            raw_delta += len(edit.after) - (edit.end - edit.start)
            if markdown[edit.start:edit.end] == edit.after:
                continue
            start, end, before = _visible_span(before_page, edit.start, edit.end)
            _, _, after = _visible_span(after_page, new_start, new_end) if edit.after else (0, 0, "")
            visible_edits.append((SourceSlice(start, end, sha256_bytes(before.encode()), after), choice))
        projected = apply_sealed_slices(before_visible, [e for e, _ in visible_edits],
                                       container_sha256=sha256_bytes(before_visible.encode()))
        if projected != after_visible:
            raise SourceChoiceCoverageSuccessorError("normalized edits do not reproduce the complete successor reader")
        context.update(before_visible=before_visible, after_visible=after_visible, visible_edits=visible_edits)
    entries = []; seen = set()
    for wrapped in claims:
        if not isinstance(wrapped, Mapping) or wrapped.get("status") != "validated" or not isinstance(wrapped.get("claim"), Mapping):
            raise SourceChoiceCoverageSuccessorError("coverage disposition requires rederived validated claims")
        claim = wrapped["claim"]; claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id or claim_id in seen:
            raise SourceChoiceCoverageSuccessorError("coverage claim identity is missing or duplicated")
        seen.add(claim_id)
        context = pages.get(claim.get("reader_page"))
        if context is None:
            continue
        source = _key(claim.get("source_unit"), "coverage source")
        canonical = _key(claim.get("canonical_unit"), "coverage canonical")
        proof = claim.get("proof", {}); span = proof.get("normalized_span")
        if (not isinstance(span, list) or len(span) != 2 or any(type(v) is not int for v in span)
                or not 0 <= span[0] < span[1] <= len(context["before_visible"])
                or sha256_bytes(context["before_visible"][span[0]:span[1]].encode()) != proof.get("expected_normalized_sha256")):
            raise SourceChoiceCoverageSuccessorError("predecessor coverage reader proof is stale")
        start, end = span
        overlapping = [(edit, choice) for edit, choice in context["visible_edits"]
                       if max(edit.start, start) < min(edit.end, end)]
        changed = [(edit, choice) for edit, choice in overlapping
                   if edit.after != context["before_visible"][edit.start:edit.end]]
        replacement = context["before_visible"][start:end]; selected = None
        if changed:
            if len(changed) != 1 or (changed[0][0].start, changed[0][0].end) != (start, end):
                raise SourceChoiceCoverageSuccessorError("choice only partially overlaps predecessor coverage claim")
            edit, selected = changed[0]; replay = selected["raw_reader_replay"]
            anchor = _locator(replay.get("anchor_source_locator"), "coverage anchor")
            diagnostic = queue_by_issue[selected["issue_id"]]["source_selector"]["mechanical_diagnostic"]["source_keys"]
            keys = {(r["view"], r["raw_index"]) for r in diagnostic}
            if (replay.get("anchor_mode") != "composite_source_slice_v1"
                    or (source["view_id"], source["raw_index"]) not in keys
                    or source["source_page"] != canonical["source_page"]
                    or canonical != {"source_page": claim["reader_page"], "view_id": anchor["view"], "raw_index": anchor["raw_index"]}
                    or claim["canonical_unit"].get("raw_text_sha256") != replay.get("anchor_container_sha256")):
                raise SourceChoiceCoverageSuccessorError("changed coverage claim does not bind the exact diagnostic and anchor")
            replacement = edit.after
        delta = sum(len(edit.after) - (edit.end - edit.start) for edit, _ in context["visible_edits"] if edit.end <= start)
        successor_span = [start + delta, start + delta + len(replacement)]
        if context["after_visible"][successor_span[0]:successor_span[1]] != replacement:
            raise SourceChoiceCoverageSuccessorError("successor coverage projection differs from reader")
        if selected is None and successor_span == span:
            continue
        entry = {"claim_id": claim_id, "mode": "replaced" if selected else "shifted",
                 "source_key": source, "canonical_key": canonical, "reader_page": claim["reader_page"],
                 "predecessor_claim_sha256": sha256_bytes(canonical_bytes(claim)),
                 "r0_normalized_span": list(span), "r0_normalized_sha256": proof["expected_normalized_sha256"],
                 "r1_normalized_span": successor_span, "r1_normalized_sha256": sha256_bytes(replacement.encode()),
                 "r0_reader_sha256": sha256_bytes(context["before_visible"].encode()),
                 "r1_reader_sha256": sha256_bytes(context["after_visible"].encode()),
                 "page_choice_ids": [row["issue_id"] for row in context["choices"]]}
        if selected is not None:
            entry.update(issue_id=selected["issue_id"], raw_reader_replay=selected["raw_reader_replay"],
                         chosen_raw_alternative=selected["chosen_raw_alternative"])
        entries.append(entry)
    return entries


def make_dispositions(*, predecessor_input: Path, ledger_path: Path, claims: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Seal one disposition per exact predecessor claim touched by a v2 ledger."""
    predecessor_input, ledger_path = Path(predecessor_input).resolve(), Path(ledger_path).resolve()
    try:
        verified = verify_ledger_v2(ledger_path)
    except SourceChoiceError as error:
        raise SourceChoiceCoverageSuccessorError(f"coverage successor ledger is invalid: {error}") from error
    if not predecessor_input.is_file():
        raise SourceChoiceCoverageSuccessorError("coverage successor predecessor is absent")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    queue_path = Path(verified["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue_by_issue = {row.get("issue_id"): row for row in queue.get("choices", []) if isinstance(row, dict)}
    if len(queue_by_issue) != len(queue.get("choices", [])):
        raise SourceChoiceCoverageSuccessorError("coverage successor queue issues are malformed")
    from .review_draft import validate_review_draft_input
    predecessor = validate_review_draft_input(json.loads(predecessor_input.read_text(encoding="utf-8")))
    evidence = _open_record(queue["final_evidence"])
    if predecessor.sha256 != evidence.get("input_sha256"):
        raise SourceChoiceCoverageSuccessorError("coverage predecessor differs from queue R0 input")
    master = Path(queue["review_master"]["path"]).parent
    decisions, records = {}, {}
    covered_pages = {wrapped["claim"].get("reader_page") for wrapped in claims
                     if isinstance(wrapped, Mapping) and isinstance(wrapped.get("claim"), Mapping)}
    for row in queue_by_issue.values():
        page = row["source_page"]
        if page not in covered_pages:
            continue
        record = row["raw_reader_replay"]["decision"]
        if page in records and records[page] != record:
            raise SourceChoiceCoverageSuccessorError("page choices disagree on predecessor decision")
        if page not in decisions:
            decisions[page] = _open_record(record, master)
            records[page] = record
    entries = project_claims(claims, ledger["source_choices"], queue_by_issue, decisions)
    value = {"schema": SCHEMA, "predecessor_input": _record(predecessor_input), "queue": _record(queue_path), "ledger": _record(ledger_path), "dispositions": entries}
    value["disposition_sha256"] = sha256_bytes(canonical_bytes(value))
    return value


def validate_dispositions(value: Any, *, predecessor_input: Path, ledger_path: Path, claims: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Re-derive and compare sealed dispositions before Stage05 consumes them."""
    if not isinstance(value, Mapping) or value.get("schema") != SCHEMA or not isinstance(value.get("disposition_sha256"), str):
        raise SourceChoiceCoverageSuccessorError("coverage successor disposition is malformed")
    candidate = dict(value); digest = candidate.pop("disposition_sha256")
    if sha256_bytes(canonical_bytes(candidate)) != digest:
        raise SourceChoiceCoverageSuccessorError("coverage successor disposition seal is invalid")
    expected = make_dispositions(predecessor_input=predecessor_input, ledger_path=ledger_path, claims=claims)
    if value != expected:
        raise SourceChoiceCoverageSuccessorError("coverage successor disposition differs from re-derived authority")
    result = {row["claim_id"]: row for row in value["dispositions"]}
    if len(result) != len(value["dispositions"]):
        raise SourceChoiceCoverageSuccessorError("coverage successor disposition duplicates a claim")
    return result
