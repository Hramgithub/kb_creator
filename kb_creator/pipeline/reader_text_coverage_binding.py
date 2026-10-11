"""Bind reader-coverage selectors to the local reconstruction and draft bytes.

This is an evidence adapter.  It deliberately returns holds instead of changing
any ledger, review, or acceptance state.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .identity import file_identity
from .reader_text_coverage import (
    OCR_FACT_SCHEMA, TRANSCRIPTION_FACT_SCHEMA, ReaderTextCoverageError,
    assess_claim, normalized_text, validate_claims,
)
from .reviewed_correction_text import (
    UnsupportedMarkdownError, _inline_visible_text_indexed, _project_block_line_indexed,
)
from .semantic_structure import (
    SemanticStructureError, apply_reviewed_text_corrections,
    reviewed_block_text_corrections, reviewed_text_corrections,
)


SCHEMA = "kb_creator.reader_text_coverage_binding.v1"
SELECTORS_SCHEMA = "kb_creator.reader_text_coverage_selectors.v1"
EVIDENCE_SCHEMA = "kb_creator.reader_text_coverage_evidence.v1"
SOURCE_TRANSCRIPTION_APPROVAL = "source_image_bound_exact_transcription"
OCR_CLASS_APPROVAL = "existing_audit_v3_ocr_class"


class ReaderTextCoverageBindingError(ValueError):
    """Raised when a local coverage binding is malformed or stale."""


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReaderTextCoverageBindingError(f"cannot read JSON: {path}") from error
    if not isinstance(value, dict):
        raise ReaderTextCoverageBindingError(f"JSON object required: {path}")
    return value


def _record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ReaderTextCoverageBindingError(f"required local file is absent: {path}")
    return {"path": str(path.resolve()), **file_identity(path)}


def _key(value: Any, label: str) -> tuple[int, str, int]:
    if not isinstance(value, Mapping) or set(value) != {"source_page", "view_id", "raw_index"}:
        raise ReaderTextCoverageBindingError(f"{label} key has an invalid closed shape")
    page, view, raw = value["source_page"], value["view_id"], value["raw_index"]
    if type(page) is not int or page < 1 or not isinstance(view, str) or not view or type(raw) is not int or raw < 0:
        raise ReaderTextCoverageBindingError(f"{label} key is malformed")
    return page, view, raw


def _block(packet: Mapping[str, Any], key: tuple[int, str, int]) -> dict[str, Any]:
    page, view, raw = key
    if packet.get("source_page") != page:
        raise ReaderTextCoverageBindingError("packet page does not match coverage key")
    views = packet.get("views")
    if not isinstance(views, Mapping) or not isinstance(views.get(view), Mapping):
        raise ReaderTextCoverageBindingError("coverage key view is absent from packet")
    matches = [row for row in views[view].get("blocks", []) if isinstance(row, Mapping) and row.get("raw_index") == raw]
    if len(matches) != 1 or not isinstance(matches[0].get("text"), str):
        raise ReaderTextCoverageBindingError("coverage key must name one text packet block")
    row = matches[0]
    block_type = row.get("type")
    if block_type is None:
        raise ReaderTextCoverageBindingError("packet block type is required")
    if not isinstance(block_type, str):
        raise ReaderTextCoverageBindingError("packet block type is malformed")
    return {
        "source_page": page, "view_id": view, "raw_index": raw,
        "block_type": block_type, "text": row["text"],
        "raw_text_sha256": __import__("hashlib").sha256(row["text"].encode("utf-8")).hexdigest().upper(),
        "bbox": row.get("bbox"),
    }


def _packet(run_root: Path, page: int) -> tuple[Path, dict[str, Any]]:
    path = run_root / "outputs/04-visual-merge-bundle/merge_packets/pages" / f"page-{page:03d}.json"
    return path, _json(path)


def _draft(drafts_root: Path, page: int, *, draft_pages_dir: Path | None = None) -> tuple[Path, dict[str, Any]]:
    pages = Path(draft_pages_dir) if draft_pages_dir is not None else drafts_root / "pages"
    path = pages / f"page-{page:03d}.json"
    value = _json(path)
    if value.get("source_page") != page or not isinstance(value.get("markdown"), str):
        raise ReaderTextCoverageBindingError("reader draft page or Markdown is invalid")
    return path, value


def _selected_keys(draft: Mapping[str, Any], page: int) -> list[tuple[int, str, int]]:
    rows = draft.get("selected_blocks")
    if not isinstance(rows, list):
        raise ReaderTextCoverageBindingError("reader draft selected_blocks is required")
    keys: list[tuple[int, str, int]] = []
    for row in rows:
        if not isinstance(row, Mapping) or row.get("purpose") == "asset":
            continue
        key = (page, row.get("view"), row.get("raw_index"))
        if not isinstance(key[1], str) or type(key[2]) is not int:
            raise ReaderTextCoverageBindingError("selected reader block is malformed")
        keys.append(key)
    if len(keys) != len(set(keys)):
        raise ReaderTextCoverageBindingError("reader draft repeats a selected source key")
    return keys


@dataclass(frozen=True)
class IndexedVisiblePage:
    visible: str
    normalized: str
    origins: tuple[tuple[int, int], ...]
    raw_length: int

    def raw_interval(self, start: int, end: int) -> tuple[int, int, str]:
        """Resolve one raw character slice without searching equal visible text."""
        if not 0 <= start < end <= self.raw_length:
            raise ReaderTextCoverageBindingError("raw choice interval is invalid")
        selected = []
        for index, (left, right) in enumerate(self.origins):
            if left < end and start < right:
                if left < start or right > end:
                    raise ReaderTextCoverageBindingError("raw choice partially owns normalized whitespace")
                selected.append(index)
        if not selected or selected[-1] - selected[0] + 1 != len(selected):
            raise ReaderTextCoverageBindingError("raw choice has no contiguous visible interval")
        first, last = selected[0], selected[-1] + 1
        return first, last, self.normalized[first:last]


def _indexed_visible_reader(markdown: str) -> IndexedVisiblePage:
    """Parse the complete page once, retaining visible and normalized provenance."""
    pieces: list[str] = []
    origins: list[tuple[int, int]] = []
    pending_gap = False
    previous_end = 0
    raw_offset = 0
    for raw_line in markdown.splitlines(keepends=True):
        line = raw_line.splitlines()[0]
        line_start = raw_offset
        raw_offset += len(raw_line)
        stripped = line.strip()
        # An empty blockquote line separates visible paragraphs, just like a
        # blank line; do not collapse the paragraphs on either side into one.
        empty_quote = re.fullmatch(r" {0,3}(?:>[ \t]*)+", line) is not None
        if not stripped or empty_quote or stripped.startswith("![") or stripped.startswith("[^" ) or (stripped.startswith("<!--") and stripped.endswith("-->")):
            if pieces:
                pending_gap = True
            continue
        if stripped.startswith(("```", "~~~")) or "<!--" in line or "<" in line or line.startswith(("    ", "\t")):
            raise ReaderTextCoverageBindingError("unsupported Markdown is outside visible coverage mapping")
        try:
            block, block_positions = _project_block_line_indexed(line)
            visible, positions = _inline_visible_text_indexed(
                block, [line_start + index for index in block_positions]
            )
        except UnsupportedMarkdownError as error:
            raise ReaderTextCoverageBindingError(str(error)) from error
        if not visible.strip():
            raise ReaderTextCoverageBindingError("empty visible Markdown line is unsupported")
        if pieces:
            separator = "\n\n" if pending_gap else "\n"
            pieces.append(separator)
            origins.extend([(previous_end, line_start)] * len(separator))
        pieces.append(visible)
        origins.extend((index, index + 1) for index in positions)
        previous_end = line_start + len(line)
        pending_gap = False
    full = "".join(pieces)
    normalized_chars: list[str] = []
    normalized_origins: list[tuple[int, int]] = []
    for match in re.finditer(r"\s+|\S", full, re.UNICODE):
        char = match.group()
        if char.isspace():
            if not normalized_chars or match.end() == len(full):
                continue
            normalized_chars.append(" ")
            covered = origins[match.start():match.end()]
            normalized_origins.append((min(a for a, _ in covered), max(b for _, b in covered)))
        else:
            normalized_chars.append(char)
            normalized_origins.append(origins[match.start()])
    result = IndexedVisiblePage(full, "".join(normalized_chars), tuple(normalized_origins), len(markdown))
    if result.normalized != normalized_text(result.visible):
        raise ReaderTextCoverageBindingError("indexed coverage normalization differs")
    return result


def _visible_paragraphs(markdown: str) -> list[str]:
    """Return conservative visible paragraphs, omitting hidden Markdown payloads."""
    visible = _indexed_visible_reader(markdown).visible
    return visible.split("\n\n") if visible else []


def _visible_reader(markdown: str) -> str:
    return "\n\n".join(_visible_paragraphs(markdown))


def _derived_subspan(reader: str, facts: Mapping[str, Any], selector: Mapping[str, Any]) -> list[int]:
    fact_id = selector.get("validated_fact_id")
    fact = facts.get(fact_id)
    if not isinstance(fact, Mapping) or not isinstance(fact.get("exact_text"), str):
        # Preserve the helper's typed missing-evidence outcome.
        return selector.get("reader_span", [])
    proof = normalized_text(fact["exact_text"])
    visible = normalized_text(reader)
    first = visible.find(proof)
    if first < 0 or visible.find(proof, first + 1) >= 0:
        raise ReaderTextCoverageBindingError("approved source text has no unique visible reader subspan")
    return [first, first + len(proof)]


def _mapping_for(text: str, reader: str, page: int) -> dict[str, Any]:
    text = normalized_text(text)
    paragraphs = _visible_paragraphs(reader)
    if sum(normalized_text(paragraph) == text for paragraph in paragraphs) != 1:
        raise ReaderTextCoverageBindingError("selected canonical unit has no unique complete visible paragraph")
    normalized = normalized_text("\n\n".join(paragraphs))
    hits: list[int] = []; cursor = 0
    while True:
        hit = normalized.find(text, cursor)
        if hit < 0:
            break
        hits.append(hit); cursor = hit + 1
    if len(hits) != 1:
        raise ReaderTextCoverageBindingError("selected canonical unit has no unique complete reader mapping")
    return {"reader_page": page, "normalized_span": [hits[0], hits[0] + len(text)], "semantic_container": "complete_selected_block"}


def _effective_canonical_text(
    decision: Mapping[str, Any], canonical: Mapping[str, Any], reader: str,
    selected: list[tuple[int, str, int]], packet: Mapping[str, Any], page: int,
) -> str:
    """Recompute a corrected reader-only canonical form from sealed decision evidence.

    The packet block remains the portable raw canonical unit.  This helper is
    only a mapping projection and deliberately delegates all correction and
    ordinary-prose authority to the existing semantic validators.
    """
    packet_blocks = {
        (view, block["raw_index"]): block
        for view, data in packet.get("views", {}).items()
        if isinstance(data, Mapping)
        for block in data.get("blocks", [])
        if isinstance(block, Mapping) and type(block.get("raw_index")) is int
    }
    selected_keys = {(view, raw) for selected_page, view, raw in selected if selected_page == page}
    corrections = reviewed_text_corrections(
        decision, packet_blocks, selected_keys, reader, page,
    )
    block_corrections = reviewed_block_text_corrections(
        decision, packet_blocks, selected_keys, reader, page,
    )
    return apply_reviewed_text_corrections(
        canonical["text"], (canonical["view_id"], canonical["raw_index"]),
        corrections, block_corrections,
    )


def _ocr_class_fact(
    fact: Mapping[str, Any], *, source: Mapping[str, Any], run_root: Path,
    source_key: tuple[int, str, int], canonical_key: tuple[int, str, int],
    source_visual: Mapping[str, Any], canonical: Mapping[str, Any],
    decision: Mapping[str, Any], validator,
) -> dict[str, Any]:
    """Validate one OCR-class fact through the already-established audit policy.

    A fact file is only a locator for a reviewed class binding.  The supplied
    validator is the existing fidelity-audit route, and must recompute its
    result from the live packet, selected reader decision, visual, class spec,
    and any sealed correction evidence.  This adapter checks the returned
    closed receipt before it can become a reader-coverage fact.
    """
    evidence = fact["evidence"]
    local = (Path(evidence["path"]) if Path(evidence["path"]).is_absolute()
             else Path(evidence["path"]))
    if not local.is_file() or _record(local) != {"path": str(local.resolve()), "bytes": evidence["bytes"], "sha256": evidence["sha256"]}:
        raise ReaderTextCoverageBindingError("OCR-class evidence file identity is stale")
    reviewed = _json(local)
    required = {
        "schema", "approval", "class_id", "source_key", "canonical_key",
        "source_pdf", "source_visual", "source_packet", "canonical_packet",
        "class_spec", "exact_text",
    }
    if set(reviewed) != required or reviewed.get("schema") != "kb_creator.reviewed_ocr_class_binding.v1":
        raise ReaderTextCoverageBindingError("OCR-class review has an invalid closed shape")
    if reviewed["approval"] != OCR_CLASS_APPROVAL:
        raise ReaderTextCoverageBindingError("OCR-class review approval is unsupported")
    if (_key(reviewed["source_key"], "OCR-class source") != source_key
            or _key(reviewed["canonical_key"], "OCR-class canonical") != canonical_key
            or reviewed["source_pdf"] != source
            or reviewed["source_visual"] != dict(source_visual)
            or reviewed["exact_text"] != fact["exact_text"]):
        raise ReaderTextCoverageBindingError("OCR-class review does not bind asserted fact")
    source_packet_path, _ = _packet(run_root, source_key[0])
    canonical_packet_path, _ = _packet(run_root, canonical_key[0])
    if (reviewed["source_packet"] != _record(source_packet_path)
            or reviewed["canonical_packet"] != _record(canonical_packet_path)):
        raise ReaderTextCoverageBindingError("OCR-class review packet identity is stale")
    class_spec = reviewed["class_spec"]
    if not isinstance(class_spec, Mapping) or set(class_spec) != {"path", "bytes", "sha256"}:
        raise ReaderTextCoverageBindingError("OCR-class spec identity is malformed")
    spec_path = Path(class_spec["path"])
    if not spec_path.is_file() or _record(spec_path) != {"path": str(spec_path.resolve()), "bytes": class_spec["bytes"], "sha256": class_spec["sha256"]}:
        raise ReaderTextCoverageBindingError("OCR-class spec identity is stale")
    spec = _json(spec_path)
    classes = spec.get("ocr_equivalence_classes")
    matches = [row for row in classes if isinstance(row, Mapping) and row.get("class_id") == reviewed["class_id"]] if isinstance(classes, list) else []
    if len(matches) != 1:
        raise ReaderTextCoverageBindingError("OCR-class spec has no unique selected class")
    class_row = matches[0]
    canonical_selector = class_row.get("canonical")
    alternates = class_row.get("alternates")
    if (class_row.get("source_page") != canonical_key[0]
            or not isinstance(canonical_selector, Mapping)
            or set(canonical_selector) != {"view_id", "raw_index"}
            or (canonical_selector["view_id"], canonical_selector["raw_index"]) != canonical_key[1:]
            or not isinstance(alternates, list)
            or sum(isinstance(item, Mapping) and set(item) == {"view_id", "raw_index"}
                   and (item["view_id"], item["raw_index"]) == source_key[1:] for item in alternates) != 1):
        raise ReaderTextCoverageBindingError("OCR-class spec does not bind the asserted source and canonical keys")
    validator = validator or _default_ocr_class_validator
    try:
        result = validator(
            class_id=reviewed["class_id"], source_key=source_key, canonical_key=canonical_key,
            exact_text=fact["exact_text"], source=source, source_visual=dict(source_visual),
            source_packet=_record(source_packet_path), canonical_packet=_record(canonical_packet_path),
            class_spec=_record(spec_path), class_selector=dict(class_row),
            canonical_raw=dict(canonical), decision=dict(decision),
        )
    except Exception as error:
        raise ReaderTextCoverageBindingError(f"OCR-class validator rejected evidence: {error}") from error
    expected = {
        "status": "validated", "class_id": reviewed["class_id"],
        "source_key": dict(reviewed["source_key"]), "canonical_key": dict(reviewed["canonical_key"]),
        "exact_text": fact["exact_text"], "source_visual": dict(source_visual),
        "canonical_raw_text_sha256": canonical["raw_text_sha256"],
    }
    if result != expected:
        raise ReaderTextCoverageBindingError("OCR-class validator returned an invalid or stale receipt")
    return {name: fact[name] for name in set(fact) - {"approval"}}


def _default_ocr_class_validator(**context: Any) -> dict[str, Any]:
    """Run the existing v3 fidelity policy for one sealed OCR-class selector.

    This is intentionally a thin adapter around the established cold-author
    class expansion and ``audit_v3_content``.  It does not copy geometry,
    correction, OCR, or class policy into reader coverage.
    """
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _v3_ocr_class_proofs, _v3_page_context
    from kb_creator.scripts.author_reviewed_semantic_decisions import _cold_ocr_classes, _visual_inventory

    source_key = context["source_key"]
    canonical_key = context["canonical_key"]
    if source_key[0] != canonical_key[0]:
        raise ReaderTextCoverageBindingError("OCR-class source and canonical pages must match")
    page = canonical_key[0]
    run_root = Path(context["canonical_packet"]["path"]).parents[4]
    packet_path = run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json"
    if _record(packet_path) != context["canonical_packet"] or _record(packet_path) != context["source_packet"]:
        raise ReaderTextCoverageBindingError("OCR-class validator packet root is unsupported")
    geometry_path = run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"
    if not geometry_path.is_file():
        raise ReaderTextCoverageBindingError("OCR-class validator geometry authority is absent")
    packet = _json(packet_path)
    decision = context["decision"]
    if not isinstance(decision, Mapping) or decision.get("source_page") != page:
        raise ReaderTextCoverageBindingError("OCR-class validator decision is stale")
    # _cold_ocr_classes validates the source selector against live packet
    # units, produces the v3 public-unit shape, and recomputes correction
    # proof text before the fidelity auditor evaluates it.
    rows = _cold_ocr_classes(
        run_root, [context["class_selector"]], _visual_inventory(run_root),
        {page: dict(decision)}, {},
    )
    geometry, visuals = _json(geometry_path), _visual_inventory(run_root)
    # Preserve page-wide conservation in audit_v3_content.  This bounded route
    # asks only whether the named class itself satisfies that same policy.
    scoped_references = {
        (unit["view_id"], unit["raw_index"])
        for row in rows for unit in [row["canonical_unit"], *row["alternate_units"]]
    }
    scoped_references.update(
        (row.get("view"), row.get("raw_index"))
        for row in decision.get("selected_blocks", [])
        if isinstance(row, Mapping) and row.get("purpose") != "asset"
        and isinstance(row.get("view"), str) and type(row.get("raw_index")) is int
    )
    context_errors: list[str] = []
    page_context = _v3_page_context(
        page, packet, dict(decision), geometry, context_errors,
        scoped_references=scoped_references,
    )
    class_errors: list[str] = []
    _, classes, _ = _v3_ocr_class_proofs(
        page, page_context, rows, [], geometry, visuals, class_errors, dict(decision),
    )
    if class_errors or len(classes) != 1 or classes[0].get("class_id") != context["class_id"]:
        raise ReaderTextCoverageBindingError(f"OCR-class audit v3 did not validate class: {'; '.join(class_errors) or 'missing class proof'}")
    return {
        "status": "validated", "class_id": context["class_id"],
        "source_key": {"source_page": source_key[0], "view_id": source_key[1], "raw_index": source_key[2]},
        "canonical_key": {"source_page": canonical_key[0], "view_id": canonical_key[1], "raw_index": canonical_key[2]},
        "exact_text": context["exact_text"], "source_visual": context["source_visual"],
        "canonical_raw_text_sha256": context["canonical_raw"]["raw_text_sha256"],
    }


def _facts(evidence_path: Path, source: Mapping[str, Any], run_root: Path, *, reuse_run_root: Path | None = None) -> dict[str, Any]:
    data = _json(evidence_path)
    if set(data) != {"schema", "facts"} or data["schema"] != EVIDENCE_SCHEMA or not isinstance(data["facts"], list):
        raise ReaderTextCoverageBindingError("coverage evidence has an invalid closed shape")
    result: dict[str, Any] = {}
    for fact in data["facts"]:
        if not isinstance(fact, Mapping) or fact.get("fact_id") in result:
            raise ReaderTextCoverageBindingError("coverage evidence fact is malformed or duplicated")
        required = {"schema", "fact_id", "source_key", "canonical_key", "source_visual", "evidence_kind", "evidence", "exact_text", "approval"}
        if set(fact) != required or fact["schema"] not in {OCR_FACT_SCHEMA, TRANSCRIPTION_FACT_SCHEMA}:
            raise ReaderTextCoverageBindingError("coverage evidence fact has an invalid closed shape")
        source_key = _key(fact["source_key"], "evidence source")
        if not isinstance(fact["source_visual"], Mapping):
            raise ReaderTextCoverageBindingError("coverage evidence visual identity is malformed")
        evidence = fact["evidence"]
        if not isinstance(evidence, Mapping) or set(evidence) != {"path", "bytes", "sha256"} or not isinstance(evidence["path"], str):
            raise ReaderTextCoverageBindingError("coverage evidence file identity is malformed")
        local = (evidence_path.parent / evidence["path"]).resolve()
        if _record(local) != {"path": str(local), "bytes": evidence["bytes"], "sha256": evidence["sha256"]}:
            raise ReaderTextCoverageBindingError("coverage evidence file identity is stale")
        if fact["schema"] == OCR_FACT_SCHEMA:
            # OCR classes need the live selected reader decision, so their
            # audit binding occurs at the claim call-site below.
            result[fact["fact_id"]] = dict(fact)
            continue
        if fact["approval"] != SOURCE_TRANSCRIPTION_APPROVAL:
            # A bound observation or a visual_reviewed boolean is not an approval.
            continue
        reviewed = _json(local)
        expected = {"schema", "approval", "reviewer", "source_key", "canonical_key", "source_pdf", "source_visual", "packet", "exact_text", "scope"}
        if set(reviewed) != expected or reviewed.get("schema") != "kb_creator.reviewed_source_transcription.v1":
            raise ReaderTextCoverageBindingError("source transcription review has an invalid closed shape")
        packet_path, _ = _packet(run_root, source_key[0])
        actual_visual = _record(run_root / "outputs/04-visual-merge-bundle/visual" / source_key[1] / "pages" / f"page-{source_key[0]:03d}.png")
        if (reviewed["approval"] != SOURCE_TRANSCRIPTION_APPROVAL or reviewed["source_key"] != fact["source_key"]
                or reviewed["canonical_key"] != fact["canonical_key"] or reviewed["source_pdf"] != source
                or reviewed["source_visual"] != fact["source_visual"]
                or reviewed["exact_text"] != fact["exact_text"]):
            raise ReaderTextCoverageBindingError("source transcription review does not bind asserted fact")
        if reviewed["source_visual"] != actual_visual or reviewed["packet"] != _record(packet_path):
            if reuse_run_root is None:
                raise ReaderTextCoverageBindingError("source transcription review packet identity is stale")
            reuse_run_root = Path(reuse_run_root).resolve()
            archived_source = _json(reuse_run_root / "run.json").get("source")
            if (not isinstance(archived_source, Mapping)
                    or any(archived_source.get(key) != source[key] for key in ("bytes", "sha256"))):
                raise ReaderTextCoverageBindingError("source transcription archived run PDF differs")
            old_packet, _ = _packet(reuse_run_root, source_key[0])
            old_visual = reuse_run_root / "outputs/04-visual-merge-bundle/visual" / source_key[1] / "pages" / f"page-{source_key[0]:03d}.png"
            archived_packet, archived_visual = _record(old_packet), _record(old_visual)
            current_packet = _record(packet_path)
            if (reviewed["packet"] != archived_packet or reviewed["source_visual"] != archived_visual
                    or any(archived_packet[key] != current_packet[key] for key in ("bytes", "sha256"))
                    or any(archived_visual[key] != actual_visual[key] for key in ("bytes", "sha256"))):
                raise ReaderTextCoverageBindingError("source transcription replay identity differs")
        copied = {name: fact[name] for name in required - {"approval"}}
        # Rebind the in-memory fact only after both copies reproduce the reviewed
        # bytes. The original reviewed record remains the evidence authority.
        copied["source_visual"] = actual_visual
        copied["evidence"] = _record(local)
        result[fact["fact_id"]] = copied
    return result


def bind_reader_coverage_claims(*, run_root: Path, source_pdf: Path, drafts_root: Path,
                                selectors_path: Path, evidence_path: Path,
                                ocr_class_validator=None, reuse_run_root: Path | None = None,
                                draft_pages_dir: Path | None = None) -> dict[str, Any]:
    """Recompute supported claims from local bytes and return typed holds.

    Selectors carry only the narrow claim decision.  Packet blocks, selected
    canonical mappings, identities, and reader intervals are reconstructed here.
    """
    run = _json(run_root / "run.json")
    source = _record(source_pdf)
    recorded_source = run.get("source")
    if not isinstance(recorded_source, Mapping) or recorded_source.get("bytes") != source["bytes"] or recorded_source.get("sha256") != source["sha256"]:
        raise ReaderTextCoverageBindingError("source PDF does not match recorded run")
    selectors = _json(selectors_path)
    if set(selectors) != {"schema", "claims"} or selectors["schema"] != SELECTORS_SCHEMA or not isinstance(selectors["claims"], list):
        raise ReaderTextCoverageBindingError("coverage selectors have an invalid closed shape")
    try:
        facts = _facts(evidence_path, source, run_root, reuse_run_root=reuse_run_root)
    except ReaderTextCoverageBindingError as error:
        return {"schema": SCHEMA, "run": _record(run_root / "run.json"), "source": source,
                "selectors": _record(selectors_path), "evidence": _record(evidence_path),
                "claims": [{"status": "held", "claim_id": row.get("claim_id") if isinstance(row, Mapping) else None,
                            "reason_code": "unsupported_or_stale_evidence", "detail": str(error)} for row in selectors["claims"]],
                "scope": "Candidate proof and typed holds only; no coverage, reviewer, or page acceptance state is changed."}
    output: list[dict[str, Any]] = []
    primary_claims: dict[str, Mapping[str, Any]] = {}
    ordered_selectors = [row for row in selectors["claims"] if not isinstance(row, Mapping) or row.get("proof_mode") != "coincident_exact_alias"]
    ordered_selectors.extend(row for row in selectors["claims"] if isinstance(row, Mapping) and row.get("proof_mode") == "coincident_exact_alias")
    for selector in ordered_selectors:
        try:
            if not isinstance(selector, Mapping):
                raise ReaderTextCoverageBindingError("coverage selector must be an object")
            source_key, canonical_key = _key(selector.get("source_key"), "selector source"), _key(selector.get("canonical_key"), "selector canonical")
            source_packet_path, source_packet = _packet(run_root, source_key[0])
            reader_page = selector.get("reader_page")
            if type(reader_page) is not int:
                raise ReaderTextCoverageBindingError("selector reader_page is malformed")
            reader_packet_path, reader_packet = _packet(run_root, reader_page)
            reader_path, draft = _draft(drafts_root, reader_page, draft_pages_dir=draft_pages_dir)
            canonical = _block(reader_packet, canonical_key)
            selected = _selected_keys(draft, reader_page)
            source_visual = _record(run_root / "outputs/04-visual-merge-bundle/visual" / source_key[1] / "pages" / f"page-{source_key[0]:03d}.png")
            visible_reader = _visible_reader(draft["markdown"])
            effective_canonical = _effective_canonical_text(
                draft, canonical, draft["markdown"], selected, reader_packet,
                reader_page,
            )
            if selector.get("proof_mode") == "reviewed_ocr_class":
                fact_id = selector.get("validated_fact_id")
                fact = facts.get(fact_id)
                if not isinstance(fact, Mapping):
                    output.append({"status": "deferred", "claim_id": selector.get("claim_id"), "reason_code": "missing_bound_evidence", "needed": "validated OCR-class fact", "source_key": dict(selector["source_key"])})
                    continue
                facts = dict(facts)
                facts[fact_id] = _ocr_class_fact(
                    fact, source=source, run_root=run_root, source_key=source_key,
                    canonical_key=canonical_key, source_visual=source_visual,
                    canonical=canonical, decision=draft, validator=ocr_class_validator,
                )
            mapping = _mapping_for(effective_canonical, draft["markdown"], reader_page)
            derived_selector = dict(selector)
            if selector.get("proof_mode") == "exact_full_unit":
                derived_selector["reader_span"] = mapping["normalized_span"]
            elif selector.get("proof_mode") == "coincident_exact_alias":
                primary = primary_claims.get(selector.get("alias_of_claim_id"))
                if not isinstance(primary, Mapping):
                    raise ReaderTextCoverageBindingError("coincident alias primary is missing or did not validate")
                derived_selector["reader_span"] = list(primary["proof"]["normalized_span"])
            else:
                derived_selector["reader_span"] = _derived_subspan(visible_reader, facts, selector)
            context = {
                "units": {source_key: _block(source_packet, source_key), canonical_key: canonical},
                "selected_keys": selected, "reader_pages": {reader_page: {"markdown": visible_reader, "semantic_container": "complete_selected_block"}},
                "source_pdf": source, "packet": _record(source_packet_path), "source_visuals": {source_key[0]: source_visual},
                "reader_markdown": {reader_page: _record(reader_path)},
                "selected_mappings": {canonical_key: mapping},
                "validated_facts": facts, "primary_claims": primary_claims,
            }
            row = assess_claim(derived_selector, **context)
            output.append(row)
            if row.get("status") == "validated":
                primary_claims[row["claim"]["claim_id"]] = row["claim"]
        except (ReaderTextCoverageBindingError, ReaderTextCoverageError, SemanticStructureError) as error:
            claim_id = selector.get("claim_id") if isinstance(selector, Mapping) else None
            output.append({"status": "held", "claim_id": claim_id, "reason_code": "unsupported_or_stale_binding", "detail": str(error)})
    validated = [row for row in output if row.get("status") == "validated"]
    try:
        validate_claims(validated)
    except ReaderTextCoverageError as error:
        raise ReaderTextCoverageBindingError(f"coverage claim batch is invalid: {error}") from error
    return {"schema": SCHEMA, "run": _record(run_root / "run.json"), "source": source,
            "selectors": _record(selectors_path), "evidence": _record(evidence_path), "claims": output,
            "scope": "Candidate proof and typed holds only; no coverage, reviewer, or page acceptance state is changed."}
