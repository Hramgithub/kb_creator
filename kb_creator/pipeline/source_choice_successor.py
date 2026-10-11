"""Authority adapter for linguistic source choices entering reviewed decisions.

The adapter deliberately consumes the pre-R1 ledger on every public validation
call.  It never writes an R1 identity back into that ledger.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Mapping

from .identity import canonical_bytes, file_identity, sha256_bytes
from .source_choice_translation import SourceChoiceError, _current_author_ledger_snapshot, verify_ledger, verify_ledger_v2

AUTHORITY = "linguistic_source_choice"
_LEDGER_SCOPE: ContextVar[dict[Path, tuple[dict[str, Any], dict[str, Any]]] | None] = ContextVar(
    "source_choice_ledger_scope", default=None,
)


class SourceChoiceSuccessorError(ValueError):
    """A page decision is not bound to one sealed linguistic choice."""


@contextmanager
def ledger_validation_scope():
    """Share fresh ledger verification within one public audit/materialization call."""
    token = _LEDGER_SCOPE.set({})
    try:
        yield
    finally:
        _LEDGER_SCOPE.reset(token)


def _identity(value: Any, label: str) -> Path:
    if not isinstance(value, Mapping) or set(value) != {"path", "bytes", "sha256"}:
        raise SourceChoiceSuccessorError(f"{label} identity is malformed")
    path = Path(value["path"])
    if not path.is_file() or file_identity(path) != {key: value[key] for key in ("bytes", "sha256")}:
        raise SourceChoiceSuccessorError(f"{label} identity drift")
    return path.resolve()


def linguistic_choice_corrections(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], page: int,
    *, full_source_overrides: set[tuple[str, int]] | None = None,
) -> dict[tuple[str, int], list[tuple[str, str]]]:
    """Return only exact ledger-bound replacements for one reviewed page.

    Each ledger is verified once per page call, even if the page has many
    corrections.  Legacy visual corrections are intentionally handled by the
    separate semantic-structure parser.
    """
    rows = decision.get("linguistic_source_choice_corrections", [])
    if rows is None:
        return {}
    if not isinstance(rows, list):
        raise SourceChoiceSuccessorError(f"page {page}: linguistic source choices must be a list")
    expected = {"authority", "ledger", "issue_id", "alternative_id", "view", "raw_index", "before", "after", "original_text_sha256"}
    expected_v2 = {"authority", "ledger", "issue_id", "alternative_id", "view", "raw_index", "raw_text_sha256", "selected_raw_text_sha256", "page_reader_span", "reader_anchor", "reader_preimage", "reader_replacement"}
    ledgers = _LEDGER_SCOPE.get()
    if ledgers is None:
        ledgers = {}
    result: dict[tuple[str, int], list[tuple[str, str]]] = {}
    composite: dict[tuple[str, tuple[str, int]], tuple[str, str, list[SourceSlice]]] = {}
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or (set(row) != expected and set(row) != expected_v2) or row.get("authority") != AUTHORITY:
            raise SourceChoiceSuccessorError(f"page {page}: linguistic source choice shape is invalid")
        ledger_path = _identity(row.get("ledger"), f"page {page} ledger")
        if ledger_path not in ledgers:
            snapshot = _current_author_ledger_snapshot(ledger_path) if ledger_path.name.endswith(".v2.json") else None
            if snapshot is not None:
                ledger = json.loads(snapshot.ledger_bytes)
                queue = json.loads(snapshot.queue_bytes)
            else:
                try:
                    verifier = verify_ledger_v2 if ledger_path.name.endswith(".v2.json") else verify_ledger
                    verifier(ledger_path)
                except SourceChoiceError as error:
                    raise SourceChoiceSuccessorError(f"page {page}: linguistic ledger is invalid: {error}") from error
                ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
                queue_path = Path(ledger["queue"]["path"])
                queue = json.loads(queue_path.read_text(encoding="utf-8"))
            ledgers[ledger_path] = (ledger, queue)
        ledger, queue = ledgers[ledger_path]
        issue_id = row.get("issue_id")
        if not isinstance(issue_id, str) or issue_id in seen:
            raise SourceChoiceSuccessorError(f"page {page}: linguistic issue is missing or duplicated")
        seen.add(issue_id)
        ledger_row = next((item for item in ledger["source_choices"] if item.get("issue_id") == issue_id), None)
        queue_row = next((item for item in queue["choices"] if item.get("issue_id") == issue_id), None)
        if not isinstance(ledger_row, Mapping) or not isinstance(queue_row, Mapping):
            raise SourceChoiceSuccessorError(f"page {page}: linguistic issue is absent from ledger")
        alternative = next((item for item in queue_row["alternatives"] if item.get("alternative_id") == row.get("alternative_id")), None)
        key = (row.get("view"), row.get("raw_index"))
        block = packet_blocks.get(key)
        text = block.get("text") if isinstance(block, Mapping) else None
        if key not in selected or not isinstance(text, str):
            raise SourceChoiceSuccessorError(f"page {page}: linguistic choice does not bind one selected source block")
        if set(row) == expected_v2:
            anchor_key = (ledger_row.get("reader_anchor", {}).get("selected_source_key", {})
                          if isinstance(ledger_row, Mapping) else {})
            if not anchor_key and isinstance(ledger_row, Mapping):
                anchor_keys = ledger_row.get("reader_anchor", {}).get("selected_source_keys", [])
                anchor_key = anchor_keys[0] if isinstance(anchor_keys, list) and len(anchor_keys) == 1 else {}
            if (row.get("raw_text_sha256") != sha256_bytes(text.encode())
                    or not isinstance(ledger_row.get("chosen_raw_alternative"), Mapping)
                    or anchor_key.get("view") != key[0]
                    or anchor_key.get("raw_index") != key[1]
                    or not isinstance(alternative, Mapping)
                    or sha256_bytes(str(row.get("reader_preimage", "")).encode()) != ledger_row.get("r0_reader_span", {}).get("text_sha256")
                    or sha256_bytes(str(row.get("reader_replacement", "")).encode()) != ledger_row.get("intended_reader_successor", {}).get("text_sha256")):
                raise SourceChoiceSuccessorError(f"page {page}: v2 linguistic choice differs from sealed ledger")
            chosen = ledger_row["chosen_raw_alternative"]
            if (chosen.get("text_sha256") != alternative.get("raw_text_sha256")
                    or chosen.get("text_sha256") != row.get("selected_raw_text_sha256")
                    or chosen.get("source_locator") != alternative.get("source_locator")):
                raise SourceChoiceSuccessorError(f"page {page}: v2 chosen raw alternative differs from sealed ledger")
            replay = ledger_row.get("raw_reader_replay")
            adapter = ledger_row.get("reader_adapter")
            if isinstance(adapter, Mapping) and adapter.get("policy") == "reviewed_corrected_reader_retention_v1":
                proof = replay.get("presentation_proof") if isinstance(replay, Mapping) else None
                if (row["reader_preimage"] != row["reader_replacement"]
                        or not isinstance(proof, Mapping)
                        or replay.get("presentation_policy") != "reviewed_block_correction_strong_display_v1"
                        or {key: adapter.get("anchor_source_locator", {}).get(key) for key in ("view", "raw_index")} != {key: alternative.get("source_locator", {}).get(key) for key in ("view", "raw_index")}
                        or adapter.get("anchor_raw_text_sha256") != alternative.get("raw_text_sha256")
                        or adapter.get("reader_text_sha256") != sha256_bytes(row["reader_preimage"].encode())
                        or adapter.get("presentation_proof_sha256") != sha256_bytes(canonical_bytes(proof))):
                    raise SourceChoiceSuccessorError(f"page {page}: retained corrected reader adapter differs from sealed ledger")
            if isinstance(replay, Mapping) and replay.get("anchor_mode") == "composite_source_slice_v1":
                from .source_choice_slice import SourceChoiceSliceError, SourceSlice, apply_sealed_slices
                interval = replay.get("raw_source_slice")
                locator = replay.get("anchor_source_locator")
                if (not isinstance(interval, Mapping) or set(interval) != {"raw_character_start", "raw_character_end", "raw_text_sha256"}
                        or not isinstance(locator, Mapping) or locator.get("view") != key[0] or locator.get("raw_index") != key[1]
                        or type(interval.get("raw_character_start")) is not int or type(interval.get("raw_character_end")) is not int
                        or not 0 <= interval["raw_character_start"] < interval["raw_character_end"] <= len(text)
                        or sha256_bytes(text[interval["raw_character_start"]:interval["raw_character_end"]].encode()) != interval.get("raw_text_sha256")):
                    raise SourceChoiceSuccessorError(f"page {page}: composite source slice differs from selected container")
                raw_after = alternative.get("raw_text") if isinstance(alternative, Mapping) else None
                identity = replay.get("anchor_container_sha256")
                group_key = (key, str(identity))
                prior = composite.get(group_key)
                if prior is None:
                    composite[group_key] = (text, str(identity), [SourceSlice(interval["raw_character_start"], interval["raw_character_end"], interval["raw_text_sha256"], raw_after)])
                else:
                    composite[group_key] = (prior[0], prior[1], [*prior[2], SourceSlice(interval["raw_character_start"], interval["raw_character_end"], interval["raw_text_sha256"], raw_after)])
                continue
            if row["reader_preimage"] != row["reader_replacement"]:
                quote = replay.get("correction_replay", {}).get("quote_container") if isinstance(replay, Mapping) else None
                if isinstance(quote, Mapping) and quote.get("policy") == "reviewed_quote_container_v1":
                    # The freshly verified queue proves this complete raw block's
                    # corrected R0 quote. A different selected reading supersedes
                    # that whole payload; quote markers are presentation, never
                    # an alleged substring of immutable OCR.
                    if (quote.get("source_sha256") != sha256_bytes(text.encode())
                            or quote.get("reader_sha256") != sha256_bytes(row["reader_preimage"].encode())
                            or not isinstance(alternative.get("raw_text"), str)
                            or not alternative["raw_text"]):
                        raise SourceChoiceSuccessorError(f"page {page}: quote source replacement identity mismatch")
                    result.setdefault(key, []).append((text, alternative["raw_text"]))
                    if full_source_overrides is not None:
                        full_source_overrides.add(key)
                    continue
                result.setdefault(key, []).append((row["reader_preimage"], row["reader_replacement"]))
            continue
        if text.count(row.get("before")) != 1 or row.get("original_text_sha256") != sha256_bytes(text.encode()):
            raise SourceChoiceSuccessorError(f"page {page}: linguistic choice does not bind one selected source block")
        if (not isinstance(alternative, Mapping) or alternative.get("text") != row.get("after")
                or ledger_row.get("alternative_id") != row.get("alternative_id")
                or ledger_row.get("predecessor_span", {}).get("text_sha256") != sha256_bytes(row["before"].encode())
                or ledger_row.get("intended_successor_replacement", {}).get("text_sha256") != sha256_bytes(row["after"].encode())
                or queue_row.get("source_page") != page):
            raise SourceChoiceSuccessorError(f"page {page}: linguistic choice differs from sealed ledger")
        result.setdefault(key, []).append((row["before"], row["after"]))
    # A composite correction is one replacement of the proven full container.
    # This preserves the legacy block-correction API without rediscovering any
    # repeated slice and applies all disjoint issue intervals together.
    from .source_choice_slice import SourceChoiceSliceError, apply_sealed_slices
    for (key, _), (text, container_sha, slices) in composite.items():
        try:
            result.setdefault(key, []).append((text, apply_sealed_slices(text, slices, container_sha256=container_sha)))
        except SourceChoiceSliceError as error:
            raise SourceChoiceSuccessorError(f"page {page}: composite source intervals cannot replay selected readings: {error}") from error
    return result
