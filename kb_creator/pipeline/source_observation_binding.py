"""Recompute observation identities and full-text reader matches from local bytes.

This does not attest that a reviewer viewed an image, approve transcription, or
accept source coverage. Downstream fidelity checks still own those decisions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .identity import file_identity, sha256_bytes


class ObservationBindingError(ValueError):
    pass


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ObservationBindingError(f"object required: {path}")
    return value


def _record(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _occurrences(text: str, needle: str) -> list[int]:
    offsets: list[int] = []
    cursor = 0
    while True:
        offset = text.find(needle, cursor)
        if offset < 0:
            return offsets
        offsets.append(offset)
        cursor = offset + 1


def bind_observations(*, run_root: Path, source_pdf: Path, drafts_root: Path,
                      observations_path: Path) -> dict[str, Any]:
    run = _json(run_root / "run.json")
    identity = file_identity(source_pdf)
    if (identity["bytes"] != run["source"]["bytes"]
            or identity["sha256"] != str(run["source"]["sha256"]).upper()):
        raise ObservationBindingError("source PDF does not match recorded run")
    inputs = _json(observations_path).get("observations")
    if not isinstance(inputs, list) or not inputs:
        raise ObservationBindingError("nonempty observations required")
    packets_root = run_root / "outputs/04-visual-merge-bundle/merge_packets/pages"
    visual_root = run_root / "outputs/04-visual-merge-bundle/visual"
    packets: dict[int, tuple[Path, dict]] = {}

    def packet(page: int) -> tuple[Path, dict]:
        if page not in packets:
            path = packets_root / f"page-{page:03d}.json"
            value = _json(path)
            if value.get("source_page") != page:
                raise ObservationBindingError("packet page mismatch")
            packets[page] = path, value
        return packets[page]

    outputs, seen = [], set()
    for observation in inputs:
        page = observation.get("source_page")
        unit = observation.get("source_unit", {})
        view, raw = unit.get("view"), unit.get("raw_index")
        transcript = observation.get("source_transcription")
        if (type(page) is not int or page < 1 or type(raw) is not int or raw < 0
                or view not in {"original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"}
                or not isinstance(transcript, str) or not transcript.strip()):
            raise ObservationBindingError("invalid observation selector or transcription")
        key = page, view, raw
        if key in seen:
            raise ObservationBindingError("duplicate source observation")
        seen.add(key)
        packet_path, data = packet(page)
        blocks = [b for b in data["views"][view]["blocks"] if b.get("raw_index") == raw]
        if len(blocks) != 1 or not isinstance(blocks[0].get("text"), str):
            raise ObservationBindingError("source key must identify one text block")
        block = blocks[0]
        matches, checked = [], []
        for reader_page in range(max(1, page - 1), page + 1):
            path = drafts_root / "pages" / f"page-{reader_page:03d}.json"
            draft = _json(path)
            if draft.get("source_page") != reader_page or not isinstance(draft.get("markdown"), str):
                raise ObservationBindingError("reader page or Markdown mismatch")
            checked.append(_record(path))
            for start in _occurrences(draft["markdown"], transcript):
                matches.append((reader_page, path, draft, start))
        canonical = []
        bound_reader, reader_page, span = None, None, None
        if len(matches) == 1:
            reader_page, reader_path, draft, start = matches[0]
            bound_reader = _record(reader_path)
            span = [start, start + len(transcript)]
            _, reader_packet = packet(reader_page)
            selected_keys = [(r.get("view"), r.get("raw_index")) for r in draft["selected_blocks"]
                             if r.get("purpose") != "asset"]
            if len(set(selected_keys)) != len(selected_keys):
                raise ObservationBindingError("duplicate selected reader source key")
            for selected_view, selected_raw in selected_keys:
                for selected in reader_packet["views"][selected_view]["blocks"]:
                    if selected.get("raw_index") == selected_raw and isinstance(selected.get("text"), str):
                        if len(_occurrences(selected["text"], transcript)) == 1:
                            canonical.append({"view": selected_view, "raw_index": selected_raw})
        reason = ("no_complete_reader_match" if not matches else
                  "ambiguous_reader_match" if len(matches) != 1 else
                  "canonical_mapping_pending" if len(canonical) != 1 else None)
        outputs.append({
            "source_page": page,
            "source_unit": {"view": view, "raw_index": raw, "bbox": block.get("bbox"),
                            "text_sha256": sha256_bytes(block["text"].encode("utf-8"))},
            "packet": _record(packet_path),
            "source_visual": _record(visual_root / view / "pages" / f"page-{page:03d}.png"),
            "reviewer": observation.get("reviewer"),
            "source_transcription": transcript,
            "source_transcription_sha256": sha256_bytes(transcript.encode("utf-8")),
            "reader_page": reader_page, "reader_draft": bound_reader,
            "reader_drafts_checked": checked, "selected_raw_exact_matches": canonical,
            "reader_exact_occurrences": len(matches), "reader_character_span": span,
            "state": "held" if reason else "exact_reader_candidate",
            "reason": reason,
        })
    return {"schema": "kb_creator.bound_source_observations.v1",
            "source": _record(source_pdf), "recorded_run": _record(run_root / "run.json"),
            "input_observations": _record(observations_path),
            "scope": "Computed identities and exact matches only; no visual, transcription, coverage or page acceptance.",
            "observations": outputs}
