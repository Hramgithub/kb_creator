"""Validate optional reviewer-authored source-marker disposition inputs.

The input is deliberately an authority about source occurrences, not reader
text.  It makes a reviewed classification complete for a sealed candidate
domain while leaving semantic structure and reader rendering as their own
authorities.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "kb_creator.source_marker_dispositions.v1"
_BINDING_KEYS = {"path", "bytes", "sha256"}
_CANDIDATE_KEYS = {"source_page", "view", "raw_index", "reader_preimage_sha256", "visual"}
_DISPOSITION_KEYS = _CANDIDATE_KEYS | {"disposition", "rationale"}
_VISUAL_KEYS = {"path", "bytes", "sha256"}


class SourceMarkerDispositionError(ValueError):
    """The sealed source-marker disposition contract is incomplete or stale."""


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def _identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest().upper()}


def _key(row: Mapping[str, Any]) -> tuple[int, str, int]:
    return (row["source_page"], row["view"], row["raw_index"])


def _closed_occurrence(row: Any, *, disposition: bool) -> None:
    expected = _DISPOSITION_KEYS if disposition else _CANDIDATE_KEYS
    if not isinstance(row, dict) or set(row) != expected:
        raise SourceMarkerDispositionError("source-marker occurrence has an invalid closed shape")
    if type(row["source_page"]) is not int or row["source_page"] < 1 or not isinstance(row["view"], str) or not row["view"] or type(row["raw_index"]) is not int:
        raise SourceMarkerDispositionError("source-marker occurrence has an invalid source key")
    if not isinstance(row["reader_preimage_sha256"], str) or len(row["reader_preimage_sha256"]) != 64:
        raise SourceMarkerDispositionError("source-marker occurrence has an invalid reader preimage hash")
    visual = row["visual"]
    if not isinstance(visual, dict) or set(visual) != _VISUAL_KEYS or not isinstance(visual["path"], str) or type(visual["bytes"]) is not int or visual["bytes"] <= 0 or not isinstance(visual["sha256"], str) or len(visual["sha256"]) != 64:
        raise SourceMarkerDispositionError("source-marker occurrence has an invalid visual identity")
    if disposition:
        if row["disposition"] not in {"unordered_list_item", "non_list"} or not isinstance(row["rationale"], str) or not row["rationale"].strip():
            raise SourceMarkerDispositionError("source-marker disposition needs a known disposition and reviewer rationale")


def load_bound_inputs(spec_paths: list[Path]) -> list[dict[str, Any]]:
    """Load optional sealed inputs named by reviewed spec fragments.

    A binding is local to its spec fragment.  Historical specs that omit the
    field remain supported; callers receive an empty list for that boundary.
    """
    loaded: list[dict[str, Any]] = []
    for spec_path in spec_paths:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        binding = spec.get("source_marker_dispositions")
        if binding is None:
            continue
        if not isinstance(binding, dict) or set(binding) != _BINDING_KEYS or not isinstance(binding["path"], str):
            raise SourceMarkerDispositionError("source_marker_dispositions binding has an invalid closed shape")
        path = (spec_path.parent / binding["path"]).resolve()
        try:
            path.relative_to(spec_path.parent.resolve())
        except ValueError as exc:
            raise SourceMarkerDispositionError("source_marker_dispositions binding escapes its spec directory") from exc
        if not path.is_file() or _identity(path) != {"bytes": binding["bytes"], "sha256": binding["sha256"]}:
            raise SourceMarkerDispositionError("source_marker_dispositions binding is stale")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SourceMarkerDispositionError("source_marker_dispositions input is unreadable") from exc
        loaded.append({"path": path, "value": value})
    return loaded


def copy_bound_input(spec_path: Path, target_spec_path: Path) -> None:
    """Copy the optional sealed sidecar alongside a copied authoring spec."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    binding = spec.get("source_marker_dispositions")
    if binding is None:
        return
    if not isinstance(binding, dict) or set(binding) != _BINDING_KEYS or not isinstance(binding["path"], str):
        raise SourceMarkerDispositionError("source_marker_dispositions binding has an invalid closed shape")
    source = (spec_path.parent / binding["path"]).resolve()
    target = (target_spec_path.parent / binding["path"]).resolve()
    try:
        source.relative_to(spec_path.parent.resolve())
        target.relative_to(target_spec_path.parent.resolve())
    except ValueError as exc:
        raise SourceMarkerDispositionError("source_marker_dispositions binding escapes its spec directory") from exc
    if not source.is_file() or _identity(source) != {"bytes": binding["bytes"], "sha256": binding["sha256"]}:
        raise SourceMarkerDispositionError("source_marker_dispositions binding is stale")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if _identity(target) != _identity(source):
        raise SourceMarkerDispositionError("source_marker_dispositions copied input differs from its sealed source")


def _list_syntax_is_valid(unit: Mapping[str, Any], markdown: str) -> bool:
    span = unit.get("markdown_span")
    if not isinstance(span, Mapping) or type(span.get("start_line")) is not int or type(span.get("end_line")) is not int:
        return False
    lines = markdown.split("\n")[span["start_line"] - 1:span["end_line"]]
    if not lines or type(unit.get("item_count")) is not int:
        return False
    body = [line[2:] if line.startswith("> ") else ("" if line == ">" else line) for line in lines]
    count = sum(line.startswith("- ") or line.startswith("* ") for line in body)
    return count == unit["item_count"] and count > 0 and all(not line or line.startswith(("- ", "* ", "  ")) for line in body)


def validate(inputs: list[dict[str, Any]], decisions: Mapping[int, Mapping[str, Any]], packets: Mapping[int, Mapping[str, Any]]) -> dict[str, Any]:
    """Fail closed when a declared source-marker candidate lacks one disposition."""
    candidates: dict[tuple[int, str, int], dict[str, Any]] = {}
    dispositions: dict[tuple[int, str, int], dict[str, Any]] = {}
    for bound in inputs:
        value = bound["value"]
        if not isinstance(value, dict) or set(value) != {"schema", "candidates", "dispositions"} or value.get("schema") != SCHEMA or not isinstance(value["candidates"], list) or not isinstance(value["dispositions"], list):
            raise SourceMarkerDispositionError("source-marker disposition input has an invalid closed shape")
        for row in value["candidates"]:
            _closed_occurrence(row, disposition=False); key = _key(row)
            if key in candidates:
                raise SourceMarkerDispositionError(f"duplicate source-marker candidate: {key}")
            candidates[key] = row
        for row in value["dispositions"]:
            _closed_occurrence(row, disposition=True); key = _key(row)
            if key in dispositions:
                raise SourceMarkerDispositionError(f"duplicate source-marker disposition: {key}")
            dispositions[key] = row
    if not inputs:
        return {"input_count": 0, "candidate_count": 0}
    if set(candidates) != set(dispositions):
        missing, foreign = set(candidates) - set(dispositions), set(dispositions) - set(candidates)
        raise SourceMarkerDispositionError(f"source-marker disposition domain is incomplete or foreign: missing={sorted(missing)}, foreign={sorted(foreign)}")
    for key, candidate in candidates.items():
        disposition = dispositions[key]
        if any(candidate[name] != disposition[name] for name in _CANDIDATE_KEYS):
            raise SourceMarkerDispositionError(f"source-marker disposition identity differs from candidate: {key}")
        page, view, raw_index = key
        decision, packet = decisions.get(page), packets.get(page)
        if not isinstance(decision, Mapping) or not isinstance(packet, Mapping):
            raise SourceMarkerDispositionError(f"source-marker candidate has a foreign page: {key}")
        blocks = packet.get("views", {}).get(view, {}).get("blocks", []) if isinstance(packet.get("views"), Mapping) else []
        block = next((item for item in blocks if isinstance(item, Mapping) and item.get("raw_index") == raw_index), None)
        selected = {(item.get("view"), item.get("raw_index")) for item in decision.get("selected_blocks", []) if isinstance(item, Mapping) and item.get("purpose") != "asset"}
        if not isinstance(block, Mapping) or not isinstance(block.get("text"), str) or (view, raw_index) not in selected:
            raise SourceMarkerDispositionError(f"source-marker candidate is foreign or unselected: {key}")
        if _sha256(block["text"]) != candidate["reader_preimage_sha256"]:
            raise SourceMarkerDispositionError(f"source-marker candidate reader preimage is stale: {key}")
        visual = decision.get("semantic_structure", {}).get("review", {}).get("visual") if isinstance(decision.get("semantic_structure"), Mapping) else None
        if visual != candidate["visual"]:
            raise SourceMarkerDispositionError(f"source-marker candidate visual identity is stale: {key}")
        units = decision["semantic_structure"].get("units", [])
        owners = [unit for unit in units if isinstance(unit, Mapping) and {"view": view, "raw_index": raw_index} in unit.get("source_blocks", [])]
        list_owners = [unit for unit in owners if unit.get("kind") == "list" and unit.get("representation") == "unordered_list"]
        if disposition["disposition"] == "unordered_list_item":
            if len(list_owners) != 1 or not _list_syntax_is_valid(list_owners[0], str(decision.get("markdown", ""))):
                raise SourceMarkerDispositionError(f"unordered-list source-marker lacks one valid list owner: {key}")
        elif list_owners:
            raise SourceMarkerDispositionError(f"non-list source-marker has list ownership: {key}")
    return {"input_count": len(inputs), "candidate_count": len(candidates)}
