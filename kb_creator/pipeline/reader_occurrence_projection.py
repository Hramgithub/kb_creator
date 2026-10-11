"""Exact source-bound reader occurrence projections for review-master v2.

The source issue remains immutable evidence.  This module binds its current
reader representation only inside the reviewed selected-source envelope.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from .identity import file_identity, sha256_bytes
from .manifests import sealed, validate_seal

SCHEMA = "kb_creator.issue_en_bindings.v2"
_INLINE_TAG = re.compile(r"</?(?:sup|sub)>", re.I)
_STRONG_MARKER = re.compile(r"(?:\*\*|__)")


class ReaderOccurrenceError(ValueError):
    pass


def display_text(value: str) -> str:
    """The reviewed heading display projection; Markdown wrappers stay outside."""
    return _INLINE_TAG.sub("", value)


def _strong_display_index(value: str) -> tuple[str, list[int]]:
    """Map reviewed strong-markup display text back to exact Markdown offsets.

    This deliberately admits only paired ``**`` or ``__`` delimiters.  It is
    used after the correction verifier has already proved the selected source
    key and Stage05 has bounded its reader envelope; it is not a page search
    or a general Markdown normalizer.
    """
    display, offsets = [], []
    markers: list[tuple[str, int]] = []
    index = 0
    while index < len(value):
        tag = _INLINE_TAG.match(value, index)
        if tag is not None:
            index = tag.end()
            continue
        marker = _STRONG_MARKER.match(value, index)
        if marker is not None:
            token = marker.group(0)
            if markers and markers[-1][0] == token:
                markers.pop()
            else:
                markers.append((token, index))
            index = marker.end()
            continue
        display.append(value[index]); offsets.append(index)
        index += 1
    if markers:
        raise ReaderOccurrenceError("reader strong markup is unbalanced")
    return "".join(display), offsets


def _strong_display_occurrence(expected: str, envelope: str) -> tuple[int, int] | None:
    """Find one exact correction text occurrence through sealed strong markup."""
    display, offsets = _strong_display_index(envelope)
    locations = [match for match in re.finditer(re.escape(expected), display)]
    if len(locations) > 1:
        raise ReaderOccurrenceError("source_material_blocked: reader occurrence is absent or ambiguous inside source envelope")
    if not locations:
        return None
    match = locations[0]
    return offsets[match.start()], offsets[match.end() - 1] + 1


def _stage05_excluded_spans(value: str) -> list[tuple[int, int]]:
    """Image markup and asset tokens are absent from the Stage05 text stream."""
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import ASSET, IMAGE
    spans: list[tuple[int, int]] = []
    for start, end in sorted(match.span() for pattern in (IMAGE, ASSET) for match in pattern.finditer(value)):
        if spans and start <= spans[-1][1]:
            spans[-1] = (spans[-1][0], max(spans[-1][1], end))
        else:
            spans.append((start, end))
    return spans


def _normal_index(value: str) -> tuple[str, list[int]]:
    """Map the Stage05 alphanumeric stream back to raw Markdown characters."""
    from kb_creator.pipeline.semantic_structure import _normalized
    # Keep the same character semantics as Stage05, while retaining each raw
    # character boundary needed to turn a proof span back into Markdown.
    stream, starts = [], []
    excluded = iter(_stage05_excluded_spans(value))
    current = next(excluded, None)
    for index, char in enumerate(value):
        while current is not None and index >= current[1]:
            current = next(excluded, None)
        if current is not None and current[0] <= index < current[1]:
            continue
        normalized = _normalized(char)
        if normalized:
            stream.extend(normalized)
            starts.extend([index] * len(normalized))
    return "".join(stream), starts


def _digest(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def _key(row: Mapping[str, Any]) -> tuple[str, int]:
    view, raw = row.get("view"), row.get("raw_index")
    if not isinstance(view, str) or type(raw) is not int:
        raise ReaderOccurrenceError("source key is malformed")
    return view, raw


def _page_window(master_text: str, page: int) -> tuple[int, int]:
    markers = list(re.finditer(r"^<!--\s*source-page-(\d{3,})\s*-->\s*$", master_text, re.M))
    windows = {int(match.group(1)): (match.end(), markers[index + 1].start() if index + 1 < len(markers) else len(master_text))
               for index, match in enumerate(markers)}
    if page not in windows:
        raise ReaderOccurrenceError("source page marker is absent")
    return windows[page]


def _unit_envelope(issue: Mapping[str, Any], decision: Mapping[str, Any]) -> tuple[dict[str, Any], int, int, list[tuple[str, int]]]:
    structure = decision.get("semantic_structure")
    candidate = issue.get("candidate_span")
    if not isinstance(structure, Mapping) or not isinstance(candidate, Mapping) or not isinstance(candidate.get("semantic_unit_id"), str):
        raise ReaderOccurrenceError("semantic reader anchor is absent")
    units = structure.get("units")
    if not isinstance(units, list):
        raise ReaderOccurrenceError("semantic unit list is malformed")
    matches = [row for row in units if isinstance(row, Mapping) and row.get("id") == candidate["semantic_unit_id"]]
    if len(matches) != 1:
        raise ReaderOccurrenceError("semantic reader anchor is ambiguous")
    unit = dict(matches[0]); span = unit.get("markdown_span")
    markdown = decision.get("markdown")
    if not isinstance(markdown, str) or not isinstance(span, Mapping):
        raise ReaderOccurrenceError("semantic reader anchor has no Markdown span")
    start_line, end_line = span.get("start_line"), span.get("end_line")
    lines = markdown.split("\n")
    if type(start_line) is not int or type(end_line) is not int or not 1 <= start_line <= end_line <= len(lines):
        raise ReaderOccurrenceError("semantic reader line span is malformed")
    body = "\n".join(lines[start_line - 1:end_line])
    if span.get("sha256") != _digest(body):
        raise ReaderOccurrenceError("semantic reader line span identity drift")
    start = sum(len(line) + 1 for line in lines[:start_line - 1])
    end = start + len(body)
    blocks = unit.get("source_blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ReaderOccurrenceError("semantic reader anchor lacks selected source blocks")
    return unit, start, end, [_key(row) for row in blocks if isinstance(row, Mapping)]


def _ordered_envelope(issue: Mapping[str, Any], decision: Mapping[str, Any], stage05_page: Mapping[str, Any], *,
                      ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] | None = None) -> tuple[int, int, list[tuple[str, int]], Mapping[str, Any]]:
    candidate = issue.get("candidate_span")
    if isinstance(candidate, Mapping) and candidate.get("binding") == "ordered_selected_source_v1" and isinstance(candidate.get("source_key"), Mapping):
        key = _key(candidate["source_key"])
    else:
        key = None
    selector = issue.get("source_selector")
    diagnostic = selector.get("mechanical_diagnostic") if isinstance(selector, Mapping) else None
    rows = diagnostic.get("source_keys") if isinstance(diagnostic, Mapping) else None
    if key is None and (not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], Mapping)):
        raise ReaderOccurrenceError("ordered reader anchor requires one selected source key")
    if key is None:
        key = _key(rows[0])
    stream = stage05_page.get("ordered_proof_stream")
    if not isinstance(stream, list):
        raise ReaderOccurrenceError("Stage05 ordered proof stream is absent")
    matches = [row for row in stream if isinstance(row, Mapping) and row.get("kind") in {"selected", "linguistic_source_choice_v1", "linguistic_source_choice_container_v1"}
               and isinstance(row.get("unit"), Mapping)
               and (row["unit"].get("view_id"), row["unit"].get("raw_index")) == key]
    if len(matches) != 1 or not isinstance(matches[0].get("markdown_span"), list) or len(matches[0]["markdown_span"]) != 2:
        raise ReaderOccurrenceError("Stage05 ordered source anchor is ambiguous")
    if matches[0].get("kind") in {"linguistic_source_choice_v1", "linguistic_source_choice_container_v1"}:
        validate_linguistic_source_choice_stage05_row(matches[0], key, ledger_context=ledger_context)
    if matches[0].get("kind") == "linguistic_source_choice_container_v1":
        structural = matches[0].get("structural_projection")
        container = structural["current_container"] if structural is not None else matches[0]["r1_container"]
        span = container["page_character_span"]
        start, end = span["character_start"], span["character_end"]
        markdown = decision.get("markdown")
        from .semantic_structure import _normalized
        if (not isinstance(markdown, str) or not 0 <= start < end <= len(markdown)
                or (structural is not None and _digest(markdown) != structural["current_page_sha256"])
                or markdown[start:end] != container["text"]
                or [len(_normalized(markdown[:start])), len(_normalized(markdown[:end]))] != matches[0]["markdown_span"]):
            raise ReaderOccurrenceError("container current reader envelope differs from sealed projection")
        return start, end, [key], matches[0]
    normalized_start, normalized_end = matches[0]["markdown_span"]
    markdown = decision.get("markdown")
    if type(normalized_start) is not int or type(normalized_end) is not int or not isinstance(markdown, str):
        raise ReaderOccurrenceError("Stage05 ordered source span is malformed")
    normalized, starts = _normal_index(markdown)
    if not 0 <= normalized_start < normalized_end <= len(normalized):
        raise ReaderOccurrenceError("Stage05 ordered source span is outside rendered Markdown")
    raw_start = starts[normalized_start]
    raw_end = starts[normalized_end - 1] + 1
    # Stage05 proves alphanumeric positions. Adjacent punctuation/formatting is
    # outside that normalized interval but can belong to the exact source text.
    # Bound the expanded window by the nearest other normalized characters so
    # this cannot jump into a different selected text occurrence.
    start = starts[normalized_start - 1] + 1 if normalized_start else 0
    end = starts[normalized_end] if normalized_end < len(starts) else len(markdown)
    # Punctuation expansion must not admit an adjacent image's alt text as a
    # second source occurrence, or treat its path as reader evidence.
    for excluded_start, excluded_end in _stage05_excluded_spans(markdown):
        if excluded_end <= raw_start:
            start = max(start, excluded_end)
        elif excluded_start >= raw_end:
            end = min(end, excluded_start)
    return start, end, [key], matches[0]


def _asset_paths(master_root: Path, decision: Mapping[str, Any]) -> dict[str, str]:
    """Recover only this decision's exact materialized asset substitutions."""
    assets = decision.get("assets", [])
    if not assets:
        return {}
    import json
    rows = json.loads((master_root / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))["assets"]
    result = {}
    for asset in assets:
        fields = (("origin", "source_page", "source_sha256", "logical_name")
                  if asset.get("origin") == "source_pdf_page_render_v1"
                  else ("view", "source_path", "logical_name"))
        matches = [row for row in rows if all(row.get(key) == asset.get(key) for key in fields)]
        paths = {row["stored_path"] for row in matches}
        if len(paths) != 1:
            raise ReaderOccurrenceError("decision asset has no unique materialized identity")
        stored = next(iter(paths))
        target = (master_root / stored).resolve()
        if not target.is_relative_to((master_root / "assets").resolve()):
            raise ReaderOccurrenceError("materialized asset escapes assets directory")
        if any(row.get("sha256") != file_identity(target)["sha256"] for row in matches):
            raise ReaderOccurrenceError("materialized asset identity drift")
        result[asset["logical_name"]] = stored
    return result


def _materialized_reader_span(markdown: str, start: int, end: int, asset_paths: Mapping[str, str]) -> tuple[str, int, int]:
    from kb_creator.scripts.materialize_mineru_ai_merge import ASSET_PLACEHOLDER, _substitute_assets
    adjusted_start, adjusted_end = start, end
    for match in ASSET_PLACEHOLDER.finditer(markdown):
        if match.start() < end and match.end() > start:
            raise ReaderOccurrenceError("reader text span overlaps an asset placeholder")
        replacement = asset_paths.get(match.group(1))
        if not isinstance(replacement, str):
            raise ReaderOccurrenceError("asset placeholder lacks materialized authority")
        if match.end() <= start:
            delta = len(replacement) - len(match.group(0))
            adjusted_start += delta
            adjusted_end += delta
    return _substitute_assets(markdown, dict(asset_paths), ""), adjusted_start, adjusted_end


def resolve_issue_reader_occurrence(issue: Mapping[str, Any], decision: Mapping[str, Any], stage05_page: Mapping[str, Any], rendered_page: str, *, asset_paths: Mapping[str, str] | None = None,
                                    ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] | None = None,
                                    packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Resolve one exact visible reader occurrence from reviewed source evidence."""
    page = issue.get("source_page")
    excerpt = issue.get("source_excerpt_en")
    if type(page) is not int or not isinstance(excerpt, str) or issue.get("source_excerpt_sha256") != _digest(excerpt):
        raise ReaderOccurrenceError("immutable source issue evidence is invalid")
    if decision.get("source_page") != page or not isinstance(decision.get("markdown"), str):
        raise ReaderOccurrenceError("review decision disagrees with source issue page")
    candidate = issue.get("candidate_span")
    if isinstance(candidate, Mapping) and isinstance(candidate.get("semantic_unit_id"), str):
        unit, start, end, keys = _unit_envelope(issue, decision)
        anchor = {"kind": "semantic_unit_id", "semantic_unit_id": unit["id"], "selected_source_keys": [
            {"view": view, "raw_index": raw} for view, raw in keys]}
    else:
        start, end, keys, ordered_proof = _ordered_envelope(issue, decision, stage05_page, ledger_context=ledger_context)
        anchor = {"kind": "ordered_selected_source_v1", "selected_source_key": {"view": keys[0][0], "raw_index": keys[0][1]}}
    envelope = decision["markdown"][start:end]
    if 'ordered_proof' in locals() and ordered_proof.get("kind") == "linguistic_source_choice_v1":
        policies = (("linguistic_source_choice_v1", ordered_proof["r1_text"]),)
    elif 'ordered_proof' in locals() and ordered_proof.get("kind") == "linguistic_source_choice_container_v1":
        witnesses = ordered_proof.get("diagnostic_witnesses", [])
        structural = ordered_proof.get("structural_projection")
        matching = [row for row in witnesses if isinstance(row, Mapping) and row.get("r0_preimage_sha256") == _digest(excerpt)]
        if _digest(excerpt) == ordered_proof["r0_container"]["text_sha256"]:
            target = structural["current_container"]["text"] if structural is not None else ordered_proof["r1_container"]["text"]
            policies = (("linguistic_source_choice_container_v1", target),)
        elif len(matching) > 1:
            raise ReaderOccurrenceError("source_material_blocked: retained excerpt is ambiguous across container witnesses")
        else:
            policies = (("linguistic_source_choice_container_witness_v1", matching[0]["r1_text"]),) if matching else (("identity_v1", excerpt), ("display_text_v1", display_text(excerpt)))
    else:
        policies = (("identity_v1", excerpt), ("display_text_v1", display_text(excerpt)))
        correction_rows = decision.get("reviewed_block_corrections", [])
        corrected_keys = {(row.get("view"), row.get("raw_index")) for row in correction_rows
                          if isinstance(row, Mapping)}
        if corrected_keys.intersection(keys):
            if len(keys) != 1 or packet_blocks is None:
                raise ReaderOccurrenceError("reviewed correction requires one complete packet-bound source anchor")
            key = keys[0]
            block = packet_blocks.get(key)
            if not isinstance(block, Mapping) or block.get("text") != excerpt:
                raise ReaderOccurrenceError("reviewed correction does not support a partial source issue")
            witnesses = [row for row in stage05_page.get("ordered_proof_stream", [])
                         if isinstance(row, Mapping) and row.get("kind") == "selected"
                         and (row.get("unit", {}).get("view_id"), row.get("unit", {}).get("raw_index")) == key]
            if len(witnesses) != 1 or witnesses[0]["unit"].get("original_text_sha256") != _digest(excerpt):
                raise ReaderOccurrenceError("reviewed correction Stage05 raw anchor identity mismatch")
            from .semantic_structure import reviewed_block_text_corrections, apply_reviewed_text_corrections
            selected = {_key(row) for row in decision.get("selected_blocks", []) if row.get("purpose") != "asset"}
            try:
                corrections = reviewed_block_text_corrections(
                    decision, packet_blocks, selected, decision["markdown"], page)
                pairs = corrections.get(key)
                if not pairs:
                    raise ValueError("selected anchor has no proved correction")
                ordered = sorted(pairs, key=lambda pair: excerpt.index(pair[0]))
                corrected = apply_reviewed_text_corrections(excerpt, key, [], {key: ordered})
                from .reviewed_label_partition import project_label_partition
                partition = project_label_partition(decision, packet_blocks, key, corrections, page)
                from .reviewed_quote_projection import project_corrected_quote
                quote = project_corrected_quote(decision, packet_blocks, key, corrections, page)
            except ValueError as error:
                raise ReaderOccurrenceError(f"reviewed correction occurrence proof failed: {error}") from error
            policies = (("reviewed_block_correction_v1", corrected),
                        ("reviewed_block_correction_display_v1", display_text(corrected)))
            if partition is not None:
                policies = (("reviewed_label_partition_v1", partition[0]),)
            if quote is not None:
                policies = (("reviewed_quote_container_v1", quote[0]),)
    candidates = []
    if 'ordered_proof' in locals() and ordered_proof.get("kind") == "linguistic_source_choice_container_v1" and ordered_proof.get("structural_projection") is not None:
        structural = ordered_proof["structural_projection"]
        if _digest(excerpt) == ordered_proof["r0_container"]["text_sha256"]:
            span = structural["current_container"]["page_character_span"]
            candidates = [("linguistic_source_choice_container_v1", structural["current_container"]["text"],
                           span["character_start"], span["character_end"])]
        elif len(matching) == 1:
            spans = [row["span"] for row in structural["current_witness_spans"] if row["issue_id"] == matching[0]["issue_id"]]
            if len(spans) != 1:
                raise ReaderOccurrenceError("structural witness projection is absent or duplicated")
            span = spans[0]
            candidates = [("linguistic_source_choice_container_witness_v1", matching[0]["r1_text"],
                           span["character_start"], span["character_end"])]
        if candidates and decision["markdown"][candidates[0][2]:candidates[0][3]] != candidates[0][1]:
            raise ReaderOccurrenceError("structural reader witness differs from current page")
    seen_text = set()
    for policy, expected in (() if candidates else policies):
        # Identity wins when display projection leaves bytes untouched.
        if not expected or expected in seen_text:
            continue
        seen_text.add(expected)
        locations = [match for match in re.finditer(re.escape(expected), envelope)]
        if len(locations) == 1:
            candidates.append((policy, expected, start + locations[0].start(), start + locations[0].end()))
    # A reviewed whole-block correction can add or move source wording while
    # the final reader representation carries author-proven strong emphasis.
    # Literal matching remains authoritative when it succeeds.  Only when it
    # cannot see any occurrence do we project the exact correction text
    # through paired strong Markdown delimiters within the already sealed
    # Stage05 envelope.
    if not candidates and 'corrected' in locals():
        display_span = _strong_display_occurrence(corrected, envelope)
        if display_span is not None:
            local_start, local_end = display_span
            candidates.append(("reviewed_block_correction_strong_display_v1",
                               envelope[local_start:local_end],
                               start + local_start, start + local_end))
    if len(candidates) != 1:
        raise ReaderOccurrenceError("source_material_blocked: reader occurrence is absent or ambiguous inside source envelope")
    policy, reader_text, local_start, local_end = candidates[0]
    # The marker matcher includes the marker's terminating newline.  The
    # remaining page window has one separator newline before decision Markdown.
    marker_prefix = "\n"
    materialized, materialized_start, materialized_end = _materialized_reader_span(
        decision["markdown"], local_start, local_end, asset_paths or {})
    expected_page = marker_prefix + materialized.rstrip() + "\n"
    if rendered_page.rstrip("\n") != expected_page.rstrip("\n"):
        raise ReaderOccurrenceError("review decision Markdown differs from rendered page")
    page_start, page_end = local_start, local_end
    projection = {"policy": policy, "reader_text": reader_text, "reader_text_sha256": _digest(reader_text)}
    return {"reader_anchor": anchor, "reader_projection": projection,
            "materialized_page_reader_span": {"character_start": len(marker_prefix) + materialized_start,
                                               "character_end": len(marker_prefix) + materialized_end},
            "page_reader_span": {"character_start": page_start, "character_end": page_end,
                                 "byte_start": len(decision["markdown"][:page_start].encode("utf-8")), "byte_end": len(decision["markdown"][:page_end].encode("utf-8")),
                                 "text_sha256": _digest(reader_text), "decision_markdown_sha256": _digest(decision["markdown"])}}


def _correction_packet_blocks(master_root: Path, final_evidence: Path, evidence: Mapping[str, Any],
                              audit: Mapping[str, Any], page: int, decision_path: Path) -> dict:
    """Reopen the packet through the same sealed queue used by Stage05."""
    import json

    def bound(path: Path, record: Mapping[str, Any]) -> dict:
        if file_identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
            raise ValueError("bound file identity drift")
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        validate_seal(evidence, "evidence_sha256")
        material = json.loads((master_root / "REVIEW_DRAFT_MATERIALIZATION.v1.json").read_text(encoding="utf-8"))
        authority = material["authority"]
        if authority["final_evidence"] != {"path": str(final_evidence.resolve()), **file_identity(final_evidence)}:
            raise ValueError("materialization belongs to different final evidence")
        decisions = [row for row in material["pages"] if row["source_page"] == page]
        if len(decisions) != 1 or decisions[0]["decision_sha256"] != file_identity(decision_path)["sha256"]:
            raise ValueError("materialized decision identity drift")
        decision_record = evidence["authored"]["decision_set"]
        decision_set = bound(final_evidence.parent / decision_record["path"], decision_record)
        authored_pages = [row for row in decision_set["decisions"] if row["source_page"] == page]
        if (len(authored_pages) != 1 or file_identity(decision_path)
                != {key: authored_pages[0][key] for key in ("bytes", "sha256")}):
            raise ValueError("decision differs from sealed authored evidence")
        queue_path = Path(authority["review_queue"]["path"])
        queue = bound(queue_path, authority["review_queue"])
        validate_seal(queue, "queue_sha256")
        if queue["queue_sha256"] != audit["authorities"]["review_queue_sha256"]:
            raise ValueError("packet queue differs from Stage05 authority")
        items = [row for row in queue["items"] if row["source_page"] == page]
        if len(items) != 1:
            raise ValueError("packet page is absent or duplicated")
        bundle = (queue_path.parent.parent / "outputs/04-visual-merge-bundle").resolve()
        packet_path = (bundle / items[0]["merge_packet"]["path"]).resolve()
        if not packet_path.is_relative_to(bundle):
            raise ValueError("packet path escapes source bundle")
        packet = bound(packet_path, items[0]["merge_packet"])
        rows = [((view, block["raw_index"]), block)
                for view, data in packet["views"].items() for block in data["blocks"]]
        blocks = dict(rows)
        if len(rows) != len(blocks):
            raise ValueError("packet source key duplicated")
        return blocks
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise ReaderOccurrenceError(f"reviewed correction packet authority is invalid: {error}") from error


def build_issue_en_bindings_v2(master: Path, source_issues: list[Mapping[str, Any]], pages: list[int], final_evidence: Path) -> dict[str, Any]:
    """Build the dual raw-source / rendered-reader binding ledger for new masters."""
    master_text = master.read_text(encoding="utf-8")
    if not source_issues:
        return sealed(SCHEMA, {"master_en": {"path": "MASTER_EN.md", **file_identity(master)},
                               "final_evidence": {"path": str(final_evidence.resolve()), **file_identity(final_evidence)},
                               "bindings": []}, digest_key="bindings_sha256")
    try:
        evidence = __import__("json").loads(final_evidence.read_text(encoding="utf-8"))
        audit_record = evidence["authored"]["stage05_audit"]
        audit_path = final_evidence.parent / audit_record["path"]
        if file_identity(audit_path) != {key: audit_record[key] for key in ("bytes", "sha256")}:
            raise ValueError
        audit = __import__("json").loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, KeyError, TypeError, ValueError):
        raise ReaderOccurrenceError("Stage05 audit authority is invalid") from None
    audit_pages = {row.get("source_page"): row for row in audit.get("pages", []) if isinstance(row, Mapping)}
    bindings, ids = [], set()
    correction_packets: dict[int, dict] = {}
    linguistic_ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] = {}
    for issue in source_issues:
        page, issue_id = issue.get("source_page"), issue.get("issue_id")
        if page not in pages or not isinstance(issue_id, str) or issue_id in ids or page not in audit_pages:
            raise ReaderOccurrenceError("source issue identity or Stage05 page is invalid")
        decision_path = master.parent / "evidence" / "review" / f"page-{page:03d}.json"
        if not decision_path.is_file():
            raise ReaderOccurrenceError("review decision is absent")
        decision = __import__("json").loads(decision_path.read_text(encoding="utf-8"))
        if decision.get("reviewed_block_corrections") and page not in correction_packets:
            correction_packets[page] = _correction_packet_blocks(
                master.parent, final_evidence, evidence, audit, page, decision_path)
        lo, hi = _page_window(master_text, page)
        try:
            occurrence = resolve_issue_reader_occurrence(issue, decision, audit_pages[page], master_text[lo:hi],
                                                        asset_paths=_asset_paths(master.parent, decision),
                                                        ledger_context=linguistic_ledger_context,
                                                        packet_blocks=correction_packets.get(page))
        except ReaderOccurrenceError as error:
            raise ReaderOccurrenceError(f"{issue_id}: {error}") from error
        page_span = occurrence["page_reader_span"]
        # MASTER pages retain one separator newline after the source-page marker;
        # page spans deliberately remain decision-Markdown relative for R1.
        master_start = lo + occurrence["materialized_page_reader_span"]["character_start"]
        master_end = lo + occurrence["materialized_page_reader_span"]["character_end"]
        master_span = {**page_span, "character_start": master_start, "character_end": master_end,
                       "byte_start": len(master_text[:master_start].encode("utf-8")), "byte_end": len(master_text[:master_end].encode("utf-8")),
                       "master_en_sha256": _digest(master_text)}
        binding = {"issue_id": issue_id, "source_page": page, "source_selector": issue["source_selector"],
                   "source_occurrence": {"source_excerpt_sha256": issue["source_excerpt_sha256"], "source_excerpt": issue["source_excerpt_en"],
                                         "candidate_span": issue.get("candidate_span"), "source_locator": issue.get("source_selector")},
                   "reader_anchor": occurrence["reader_anchor"], "page_reader_span": page_span,
                   "master_reader_span": master_span,
                   "reader_projection": occurrence["reader_projection"],
                   "decision": {"path": f"evidence/review/page-{page:03d}.json", **file_identity(decision_path)},
                   "stage05_audit": {"path": audit_record["path"], "bytes": audit_record["bytes"], "sha256": audit_record["sha256"]}}
        bindings.append(binding); ids.add(issue_id)
    return sealed(SCHEMA, {"master_en": {"path": "MASTER_EN.md", **file_identity(master)},
                           "final_evidence": {"path": str(final_evidence.resolve()), **file_identity(final_evidence)},
                           "bindings": bindings}, digest_key="bindings_sha256")


def validate_issue_reader_occurrence(binding: Mapping[str, Any], master_text: str) -> None:
    """Check that a sealed binding still names its exact reader slice."""
    for key in ("page_reader_span", "master_reader_span", "reader_projection", "reader_anchor", "source_occurrence"):
        if key not in binding or not isinstance(binding[key], Mapping):
            raise ReaderOccurrenceError("v2 binding is malformed")
    span = binding["master_reader_span"]; start, end = span.get("character_start"), span.get("character_end")
    text = binding["reader_projection"].get("reader_text")
    if type(start) is not int or type(end) is not int or not isinstance(text, str) or not 0 <= start < end <= len(master_text):
        raise ReaderOccurrenceError("v2 reader span is malformed")
    if master_text[start:end] != text or span.get("text_sha256") != _digest(text) or binding["reader_projection"].get("reader_text_sha256") != _digest(text):
        raise ReaderOccurrenceError("v2 reader span identity drift")


def project_raw_alternative_to_reader(raw_text: str, binding: Mapping[str, Any]) -> str:
    """Project a raw source alternative through the binding's closed policy.

    v2 currently admits identity and heading display projection here.  A future
    correction-chain row must carry and replay its explicit ordered evidence;
    accepting it without that evidence would turn a source choice into a guess.
    """
    projection = binding.get("reader_projection")
    if not isinstance(raw_text, str) or not isinstance(projection, Mapping):
        raise ReaderOccurrenceError("reader projection is malformed")
    policy = projection.get("policy")
    if policy == "identity_v1":
        return raw_text
    if policy == "display_text_v1":
        return display_text(raw_text)
    if policy == "reviewed_correction_chain_v1":
        raise ReaderOccurrenceError("reviewed correction chain requires explicit authored correction evidence")
    raise ReaderOccurrenceError("reader projection policy is unsupported")


def load_issue_en_bindings_v2(review_master: Path) -> dict[str, Any]:
    root = Path(review_master); path = root / "ISSUE_EN_BINDINGS.v2.json"; value = __import__("json").loads(path.read_text(encoding="utf-8"))
    try:
        validate_seal(value, "bindings_sha256")
    except ValueError as error:
        raise ReaderOccurrenceError("v2 binding seal is invalid") from error
    if value.get("schema") != SCHEMA or file_identity(root / "MASTER_EN.md") != {key: value.get("master_en", {}).get(key) for key in ("bytes", "sha256")}:
        raise ReaderOccurrenceError("v2 master identity drift")
    text = (root / "MASTER_EN.md").read_text(encoding="utf-8")
    for row in value.get("bindings", []): validate_issue_reader_occurrence(row, text)
    return value


def apply_bound_reader_replacements(markdown: str, replacements: list[Mapping[str, Any]]) -> tuple[str, list[dict[str, int]]]:
    """Apply nonoverlapping exact reader replacements from right to left."""
    rows = []
    for row in replacements:
        span = row.get("page_reader_span", row.get("span")) if isinstance(row, Mapping) else None
        after = row.get("after") if isinstance(row, Mapping) else None
        if not isinstance(span, Mapping) or not isinstance(after, str): raise ReaderOccurrenceError("reader replacement is malformed")
        start, end = span.get("character_start"), span.get("character_end")
        before = row.get("before", row.get("reader_projection", {}).get("reader_text"))
        if type(start) is not int or type(end) is not int or not isinstance(before, str) or not 0 <= start < end <= len(markdown) or markdown[start:end] != before:
            raise ReaderOccurrenceError("reader replacement preimage differs")
        rows.append((start, end, before, after))
    for left, right in zip(sorted(rows), sorted(rows)[1:]):
        if left[1] > right[0]: raise ReaderOccurrenceError("reader replacements overlap")
    deltas = []
    for start, end, before, after in sorted(rows, reverse=True):
        markdown = markdown[:start] + after + markdown[end:]
        deltas.append({"character_start": start, "character_delta": len(after) - len(before), "line_delta": after.count("\n") - before.count("\n")})
    return markdown, list(reversed(deltas))


def validate_linguistic_source_choice_stage05_row(
    row: Mapping[str, Any], key: tuple[str, int], *, ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> None:
    """Reopen the only R1 lexical proof form accepted by structural rebind."""
    if isinstance(row, Mapping) and row.get("kind") == "linguistic_source_choice_container_v1":
        _validate_linguistic_source_choice_container_stage05_row(row, key, ledger_context=ledger_context)
        return
    from .source_choice_translation import verify_ledger_v2
    required = {"kind", "unit", "markdown_span", "r1_span", "r1_text", "r1_text_sha256",
                "r0_anchor_source_key", "r0_preimage_sha256", "selected_raw_locator",
                "selected_raw_text_sha256", "issue_id", "alternative_id", "ledger",
                "ledger_identity", "raw_reader_replay", "row_sha256"}
    if not isinstance(row, Mapping) or set(row) != required or row.get("kind") != "linguistic_source_choice_v1":
        raise ReaderOccurrenceError("linguistic Stage05 proof shape is malformed")
    unit = row.get("unit")
    locator = row.get("selected_raw_locator")
    anchor = row.get("r0_anchor_source_key")
    span = row.get("markdown_span")
    if (not isinstance(unit, Mapping) or (unit.get("view_id"), unit.get("raw_index")) != key
            or not isinstance(locator, Mapping)
            or not isinstance(anchor, Mapping) or set(anchor) != {"view", "raw_index"}
            or (anchor.get("view"), anchor.get("raw_index")) != key
            or not isinstance(span, list) or len(span) != 2 or row.get("r1_span") != span
            or any(type(value) is not int for value in span) or span[0] >= span[1]
            or not isinstance(row.get("r1_text"), str)
            or row.get("r1_text_sha256") != _digest(row["r1_text"])):
        raise ReaderOccurrenceError("linguistic Stage05 proof span or locator is malformed")
    ledger_record = row.get("ledger")
    if not isinstance(ledger_record, Mapping) or set(ledger_record) != {"path", "bytes", "sha256"}:
        raise ReaderOccurrenceError("linguistic Stage05 ledger identity is malformed")
    ledger_path = Path(ledger_record["path"]).resolve()
    if not ledger_path.is_file() or file_identity(ledger_path) != {name: ledger_record[name] for name in ("bytes", "sha256")}:
        raise ReaderOccurrenceError("linguistic Stage05 ledger identity drift")
    context = ledger_context if ledger_context is not None else {}
    import json
    current_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    if ledger_path not in context:
        verified = verify_ledger_v2(ledger_path)
        context[ledger_path] = (verified, current_ledger)
    elif context[ledger_path][1] != current_ledger:
        raise ReaderOccurrenceError("cached ledger content changed at the same path")
    verified, ledger = context[ledger_path]
    if row.get("ledger_identity") != verified.get("ledger_sha256"):
        raise ReaderOccurrenceError("linguistic Stage05 ledger seal differs")
    choice = next((item for item in ledger.get("source_choices", []) if item.get("issue_id") == row.get("issue_id")), None)
    if not isinstance(choice, Mapping):
        raise ReaderOccurrenceError("linguistic Stage05 ledger choice is absent")
    raw = choice.get("chosen_raw_alternative", {})
    replay = choice.get("raw_reader_replay")
    successor = choice.get("intended_reader_successor", {})
    if (choice.get("disposition") != "selected_alternative" or choice.get("alternative_id") != row.get("alternative_id")
            or not isinstance(raw, Mapping) or raw.get("source_locator") != locator
            or raw.get("text_sha256") != row.get("selected_raw_text_sha256")
            or not isinstance(replay, Mapping) or replay != row.get("raw_reader_replay")
            or not isinstance(replay.get("anchor_source_locator"), Mapping)
            or (replay["anchor_source_locator"].get("view"), replay["anchor_source_locator"].get("raw_index")) != (anchor.get("view"), anchor.get("raw_index"))
            or replay.get("r0_preimage_sha256") != row.get("r0_preimage_sha256")
            or not isinstance(successor, Mapping) or successor.get("text") != row.get("r1_text")
            or successor.get("text_sha256") != row.get("r1_text_sha256")):
            raise ReaderOccurrenceError("linguistic Stage05 proof differs from sealed ledger")


def _validate_linguistic_source_choice_container_stage05_row(
    row: Mapping[str, Any], key: tuple[str, int], *, ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> None:
    """Re-derive the complete row from verified authority, including its seal."""
    import json
    from .source_choice_container_proof import derive_container_proof, open_structural_projection_context
    from .source_choice_translation import verify_ledger_v2
    try:
        record = row["ledger"]
        if not isinstance(record, Mapping) or set(record) != {"path", "bytes", "sha256"}:
            raise ValueError("container ledger record is malformed")
        path = Path(record["path"]).resolve()
        if not path.is_file() or file_identity(path) != {k: record[k] for k in ("bytes", "sha256")}:
            raise ValueError("container ledger identity drift")
        context = ledger_context if ledger_context is not None else {}
        current_ledger = json.loads(path.read_text(encoding="utf-8"))
        if path not in context:
            context[path] = (verify_ledger_v2(path), current_ledger)
        elif context[path][1] != current_ledger:
            raise ValueError("cached ledger content changed at the same path")
        verified, ledger = context[path]
        structural_context = None
        extension = row.get("structural_projection")
        if extension is not None:
            authority = extension["authority"]
            input_record = authority["input"]
            input_path = Path(input_record["path"]).resolve()
            if file_identity(input_path) != {name: input_record[name] for name in ("bytes", "sha256")}:
                raise ValueError("structural projection input identity drift")
            structural_context = open_structural_projection_context(
                input_path=input_path, binding_root=Path(authority["binding_root"]))
            if structural_context is None or structural_context["authority"] != authority:
                raise ValueError("structural projection authority differs from bound successor")
        expected = derive_container_proof(ledger_record=record, ledger=ledger, verified=verified,
                                          page=row["unit"]["source_page"], key=key,
                                          structural_context=structural_context)
        if row != expected:
            raise ValueError("container row differs from rederived source authority")
    except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
        raise ReaderOccurrenceError(f"container linguistic Stage05 proof invalid: {error}") from error
