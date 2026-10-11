"""Bind reviewed cold drafts to conserved source components and a fresh replay.

Reviewed text is copied exactly; this stage never infers approval or promotes a
master. Full semantic authoring and fidelity audit remain separate stages.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any

from . import mechanical_reconstruction
from .identity import assert_existing_path_components_are_not_reparse, canonical_bytes, file_identity, sha256_bytes
from .manifests import validate_seal
from .review_draft import (ReviewDraftError, build_archive_consumption_context,
                           prepare_review_draft_input, validate_review_draft_input)

LEDGER_SCHEMA = "kb_creator.reviewed_staging_ledger.v2"
REVIEW_SCHEMA = "kb_creator.reviewed_staging_page_review.v1"


class ReviewedDraftStagingError(ValueError):
    """An input cannot establish a complete reviewed cold draft."""


@dataclass(frozen=True)
class StagingPreflight:
    state: str
    gaps: dict[int, list[str]]
    bindings: dict[str, Any]
    conservation: list[dict[str, Any]]
    pages: dict[int, dict[str, Any]]
    spec: dict[str, Any]
    evidence: dict[str, Any]


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewedDraftStagingError(f"cannot read JSON: {path}") from exc


def _shape(value: Any, fields: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != fields:
        raise ReviewedDraftStagingError(f"{label} has an invalid closed shape")


def _safe_file(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ReviewedDraftStagingError("binding requires a relative POSIX path")
    if PurePosixPath(relative).is_absolute() or any(p in {"..", ".", ""} for p in relative.split("/")):
        raise ReviewedDraftStagingError("binding path escapes its approved root")
    candidate = root / relative
    assert_existing_path_components_are_not_reparse(candidate)
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ReviewedDraftStagingError("binding path escapes its approved root") from exc
    if not candidate.is_file():
        raise ReviewedDraftStagingError(f"binding is not a regular file: {relative}")
    return candidate


def _verify(root: Path, record: Any, label: str) -> Path:
    _shape(record, {"path", "bytes", "sha256"}, label)
    if type(record["bytes"]) is not int or record["bytes"] < 0:
        raise ReviewedDraftStagingError(f"{label} has an invalid byte count")
    path = _safe_file(root, record["path"])
    if file_identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
        raise ReviewedDraftStagingError(f"{label} identity mismatch")
    return path


def _key(value: Any) -> tuple[str, int]:
    _shape(value, {"view", "raw_index"}, "source key")
    if value["view"] not in mechanical_reconstruction.VIEWS or type(value["raw_index"]) is not int or value["raw_index"] < 0:
        raise ReviewedDraftStagingError("source key is invalid")
    return value["view"], value["raw_index"]


def _keys(values: Any) -> set[tuple[str, int]]:
    if not isinstance(values, list):
        raise ReviewedDraftStagingError("source keys must be a list")
    result = [_key(value) for value in values]
    if len(result) != len(set(result)):
        raise ReviewedDraftStagingError("duplicate source key")
    return set(result)


def _page_rows(rows: Any, label: str) -> dict[int, dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        raise ReviewedDraftStagingError(f"{label} pages must be nonempty")
    result = {}
    for row in rows:
        page = row.get("source_page") if isinstance(row, dict) else None
        if type(page) is not int or page < 1 or page in result:
            raise ReviewedDraftStagingError(f"{label} has an invalid or duplicate page")
        result[page] = row
    return result


def _authority(source_root: Path, target_root: Path, manifest: dict, candidate_dir: Path, *, mode: str = "strict") -> dict:
    """Mandatory production authority; synthetic tests patch this boundary."""
    from . import reconstruction_replay, reconstruction_replay_resume
    if not (source_root / "run.json").is_file() or not (target_root / "run.json").is_file():
        raise ReviewedDraftStagingError("source and target run authority are required")
    if mode == "review_draft":
        context = build_archive_consumption_context(source_run_root=source_root, target_run_root=target_root)
        source = reconstruction_replay.validate_replay_artifacts_for_consumption(source_root)
        target = reconstruction_replay.validate_replay_artifacts_for_consumption(target_root)
    else:
        source = reconstruction_replay.validate_replay_artifacts_for_consumption(source_root)
        target = reconstruction_replay.validate_replayed_prefix(target_root)
        reconstruction_replay_resume.validate_replay_review_queue(target)
        context = None
    mechanical_reconstruction._validate_generated_draft(manifest, candidate_dir)
    if Path(manifest["run_root"]).resolve() != source_root:
        raise ReviewedDraftStagingError("candidate belongs to a different source run")
    if manifest["authorities"]["run"] != {"path": "run.json", **file_identity(source_root / "run.json")}:
        raise ReviewedDraftStagingError("candidate source run identity changed")
    return {"source_consumption": source.producer_freshness,
            "target_replay": "archive_consumption" if context else "validated",
            "candidate": "validated", "archive_authority": context}


def _compose_specs(paths: list[Path]) -> dict[str, Any]:
    from kb_creator.scripts.author_reviewed_semantic_decisions import _load_spec_fragments
    spec = _load_spec_fragments(paths)
    spec["schema"] = "kb_creator.reviewed_semantic_draft_spec.v1"
    # Cold authoring reads these before _load_spec_fragments: preserve them.
    spec["ocr_equivalence_classes"] = [
        row for path in paths for row in _read(path).get("ocr_equivalence_classes", [])
    ]
    identifiers = [row.get("class_id") for row in spec["ocr_equivalence_classes"]]
    if any(not isinstance(key, str) or not key for key in identifiers) or len(identifiers) != len(set(identifiers)):
        raise ReviewedDraftStagingError("OCR equivalence class IDs must be unique")
    for row in spec["pages"]:
        if row.get("inherit_units_from_baseline") or row.get("selected_before") or row.get("review_notes_remove"):
            raise ReviewedDraftStagingError("cold spec depends on inherited baseline state")
    return spec


def recompute_coverage_factories(*, run_root: Path, source_pdf: Path, drafts_root: Path,
        factories: list[dict[str, Any]], ocr_class_validator: Any = None) -> dict[str, Any]:
    """Recompute coverage from selector/evidence pairs, never a merged report.

    Each factory is deliberately small and portable at the call boundary:
    ``factory_id``, ``selectors_path``, and ``evidence_path``.  The existing
    adapter reopens packet, candidate, reader-span, and source evidence.  This
    function only aggregates those independently recomputed claims and rejects
    duplicate source-key ownership.
    """
    from .reader_text_coverage_binding import bind_reader_coverage_claims
    from .reader_text_coverage import ReaderTextCoverageError, validate_claims
    if not isinstance(factories, list) or not factories:
        raise ReviewedDraftStagingError("review-draft coverage factories are required")
    claims: list[dict[str, Any]] = []; validated_rows: list[dict[str, Any]] = []
    seen_factory: set[str] = set(); seen_claim: set[str] = set(); owners: set[tuple[Any, ...]] = set()
    records: list[dict[str, Any]] = []
    for factory in factories:
        required = {"factory_id", "selectors_path", "evidence_path"}
        optional = required | {"reuse_run_root"}
        optional_pages = optional | {"draft_pages_dir"}
        if not isinstance(factory, dict) or set(factory) not in (required, optional, optional_pages, required | {"draft_pages_dir"}):
            raise ReviewedDraftStagingError("coverage factory has an invalid closed shape")
        factory_id = factory["factory_id"]
        if not isinstance(factory_id, str) or not factory_id or factory_id in seen_factory:
            raise ReviewedDraftStagingError("coverage factory ID is missing or duplicated")
        selectors, evidence = Path(factory["selectors_path"]), Path(factory["evidence_path"])
        reuse = Path(factory["reuse_run_root"]).resolve() if "reuse_run_root" in factory else None
        draft_pages = Path(factory["draft_pages_dir"]).resolve() if "draft_pages_dir" in factory else None
        if reuse is not None and not (reuse / "run.json").is_file():
            raise ReviewedDraftStagingError("coverage factory reuse run is unavailable")
        if draft_pages is not None and not draft_pages.is_dir():
            raise ReviewedDraftStagingError("coverage factory draft pages are unavailable")
        result = bind_reader_coverage_claims(
            run_root=Path(run_root), source_pdf=Path(source_pdf), drafts_root=Path(drafts_root),
            selectors_path=selectors, evidence_path=evidence, ocr_class_validator=ocr_class_validator,
            reuse_run_root=reuse,
            draft_pages_dir=draft_pages,
        )
        rows = result.get("claims") if isinstance(result, dict) else None
        if not isinstance(rows, list) or any(row.get("status") != "validated" for row in rows if isinstance(row, dict)):
            raise ReviewedDraftStagingError(f"coverage factory {factory_id} contains a held or malformed claim")
        for row in rows:
            claim = row.get("claim", row)
            claim_id = claim.get("claim_id") if isinstance(claim, dict) else None
            source_key = claim.get("source_key", claim.get("source_unit")) if isinstance(claim, dict) else None
            if not isinstance(row, dict) or not isinstance(claim_id, str) or not isinstance(source_key, dict):
                raise ReviewedDraftStagingError("recomputed coverage claim lacks a source key")
            owner = (source_key.get("source_page"), source_key.get("view_id"), source_key.get("raw_index"))
            if owner in owners or claim_id in seen_claim:
                raise ReviewedDraftStagingError("coverage claim duplicates source-key ownership")
            owners.add(owner); seen_claim.add(claim_id)
            claims.append({"factory_id": factory_id, "claim": row})
            validated_rows.append(row)
        seen_factory.add(factory_id)
        records.append({"factory_id": factory_id, "selectors": {"path": str(selectors), **file_identity(selectors)},
                        "evidence": {"path": str(evidence), **file_identity(evidence)},
                        **({"reuse_run": {"path": str(reuse / "run.json"), **file_identity(reuse / "run.json")}} if reuse is not None else {}),
                        "claim_count": len(rows)})
    try:
        validate_claims(validated_rows)
    except ReaderTextCoverageError as error:
        raise ReviewedDraftStagingError(f"inter-factory coverage claims conflict: {error}") from error
    return {"schema": "kb_creator.review_draft_coverage_factories.v1", "factories": records,
            "source_pdf": {"path": str(Path(source_pdf).resolve()), **file_identity(Path(source_pdf))},
            "claims": claims, "source_key_owner_count": len(owners)}


def _packet_blocks(packet: dict) -> dict[tuple[str, int], dict]:
    result = {}
    for view in mechanical_reconstruction.VIEWS:
        for block in packet["views"][view]["blocks"]:
            key = _key({"view": view, "raw_index": block["raw_index"]})
            if key in result:
                raise ReviewedDraftStagingError("packet repeats a source key")
            result[key] = block
    return result


def _review(page: int, draft: dict, receipt: dict, row: dict, spec: dict, *, mode: str,
        review_draft_authority: dict[str, Any] | None = None) -> bool:
    _shape(receipt, {"schema", "source_page", "source_visual", "draft_sha256", "spec_sha256",
                     "visual_reviewed", "reviewer", "notes"}, "page review")
    if receipt["schema"] != REVIEW_SCHEMA or receipt["source_page"] != page:
        raise ReviewedDraftStagingError("page review identity mismatch")
    if receipt["source_visual"] != row["target_visual"] or receipt["draft_sha256"] != row["reviewed_draft"]["sha256"] or receipt["spec_sha256"] != sha256_bytes(canonical_bytes(spec)):
        raise ReviewedDraftStagingError(f"page {page} review does not bind final draft/spec/visual")
    if not isinstance(receipt["reviewer"], str) or not receipt["reviewer"].strip() or not isinstance(receipt["notes"], str):
        raise ReviewedDraftStagingError("page review requires reviewer and notes")
    if mode == "review_draft":
        unresolved = draft.get("unresolved")
        dispositions = (review_draft_authority or {}).get("_sealed_unresolved_dispositions")
        if not isinstance(unresolved, list) or not isinstance(dispositions, list):
            return False
        declared = {(item.get("source_page"), item.get("predecessor_unresolved")): item
                    for item in dispositions if isinstance(item, dict)}
        if len(declared) != len(dispositions):
            return False
        for text in unresolved:
            item = declared.get((page, text))
            if not isinstance(text, str) or item is None or item.get("current", {}).get("sha256") != row["reviewed_draft"]["sha256"]:
                return False
        # The literal flags remain evidence.  Complete source/reader accounting
        # is a different gate from page-level visual review.
        return receipt["visual_reviewed"] is draft.get("review", {}).get("visual_reviewed")
    if draft.get("unresolved") != []:
        return False
    return receipt["visual_reviewed"] is True and draft.get("review", {}).get("visual_reviewed") is True


def _conserve(page: int, candidate: dict, packet: dict, draft: dict, resolutions: Any, spec: dict, *, coverage_claims: dict[tuple[str, int], str] | None = None, pending_source_keys: set[tuple[int, str, int]] | None = None) -> tuple[list[dict], bool]:
    blocks = _packet_blocks(packet)
    selected_list = draft.get("selected_blocks", [])
    selected = _keys([{key: value[key] for key in ("view", "raw_index")} for value in selected_list])
    if not selected <= set(blocks):
        raise ReviewedDraftStagingError(f"page {page} selects a missing packet block")
    if not isinstance(resolutions, list):
        raise ReviewedDraftStagingError("component resolutions must be a list")
    entries = {entry["ordinal"]: entry for entry in candidate["entries"]}
    rows = {}
    for resolution in resolutions:
        allowed = {"ordinal", "source_keys", "action", "selected", "rationale"}
        covered_fields = allowed | {"coverage_claim_id", "coverage_source_key", "empty_companion_keys"}
        pending_fields = covered_fields | {"pending_companion_keys"}
        if not isinstance(resolution, dict) or (set(resolution) != allowed and set(resolution) != allowed | {"coverage_claim_id"} and set(resolution) != covered_fields and set(resolution) != pending_fields):
            raise ReviewedDraftStagingError("component resolution has an invalid closed shape")
        if set(resolution) in (covered_fields, pending_fields) and resolution.get("action") != "covered_by_reader":
            raise ReviewedDraftStagingError("companion partition requires covered_by_reader action")
        ordinal = resolution["ordinal"]
        if type(ordinal) is not int or ordinal not in entries or ordinal in rows:
            raise ReviewedDraftStagingError("duplicate or missing component ordinal")
        if not isinstance(resolution["rationale"], str) or not resolution["rationale"].strip():
            raise ReviewedDraftStagingError("resolution rationale is required")
        rows[ordinal] = resolution
    if set(rows) != set(entries):
        raise ReviewedDraftStagingError("every component requires an explicit disposition")
    exclusions = {(v["view_id"], v["raw_index"]) for v in spec.get("source_text_exclusions", []) if v["source_page"] == page}
    seen, accounted, conservation, unresolved = set(), set(), [], False
    for ordinal, entry in entries.items():
        keys = _keys(entry["source_keys"]); resolution = rows[ordinal]
        if _keys(resolution["source_keys"]) != keys or seen & keys or not keys <= set(blocks):
            raise ReviewedDraftStagingError("component source-key conservation mismatch")
        seen |= keys
        chosen = _keys(resolution["selected"])
        if chosen != selected & keys:
            raise ReviewedDraftStagingError("component selected keys differ from exact reviewed draft")
        action = resolution["action"]
        if action == "selected":
            if not chosen:
                raise ReviewedDraftStagingError("selected component has no reviewed selection")
            accounted |= chosen
        elif action == "excluded_empty":
            if chosen or any(blocks[key].get("text") or blocks[key].get("assets") or blocks[key].get("table_body") for key in keys):
                raise ReviewedDraftStagingError("nonempty source cannot be excluded as empty")
        elif action == "excluded_reviewed":
            nonempty = {key for key in keys if blocks[key].get("text")}
            if chosen or not nonempty <= exclusions:
                raise ReviewedDraftStagingError("reviewed exclusion lacks source-text exclusion evidence")
            if any(blocks[key].get("assets") for key in keys):
                raise ReviewedDraftStagingError("source assets require a selected reference or facsimile")
        elif action == "covered_by_reader":
            claim_id = resolution.get("coverage_claim_id")
            if chosen or not isinstance(claim_id, str) or not claim_id or coverage_claims is None:
                raise ReviewedDraftStagingError("covered_by_reader requires an exact recomputed claim")
            if set(resolution) == allowed | {"coverage_claim_id"}:
                if any(coverage_claims.get(key) != claim_id for key in keys):
                    raise ReviewedDraftStagingError("covered_by_reader claim does not uniquely own every source key")
            else:
                def companion_key(value: Any) -> tuple[str, int]:
                    if not isinstance(value, dict) or set(value) != {"view_id", "raw_index"}:
                        raise ReviewedDraftStagingError("covered_by_reader companion key has invalid producer shape")
                    view, raw = value["view_id"], value["raw_index"]
                    if not isinstance(view, str) or type(raw) is not int:
                        raise ReviewedDraftStagingError("covered_by_reader companion key is invalid")
                    return view, raw
                coverage_key = {companion_key(resolution["coverage_source_key"])}
                if not isinstance(resolution["empty_companion_keys"], list):
                    raise ReviewedDraftStagingError("empty companion keys must be a list")
                raw_empty = [companion_key(value) for value in resolution["empty_companion_keys"]]
                empty_keys = set(raw_empty)
                raw_pending = ([] if set(resolution) == covered_fields else
                               [companion_key(value) for value in resolution["pending_companion_keys"]]
                               if isinstance(resolution.get("pending_companion_keys"), list) else None)
                if raw_pending is None:
                    raise ReviewedDraftStagingError("pending companion keys must be a list")
                pending_keys = set(raw_pending)
                if len(raw_empty) != len(empty_keys):
                    raise ReviewedDraftStagingError("covered_by_reader companion partition duplicates a source key")
                if len(raw_pending) != len(pending_keys) or empty_keys & pending_keys:
                    raise ReviewedDraftStagingError("covered_by_reader companion partition duplicates a source key")
                if len(coverage_key) != 1 or coverage_key & (empty_keys | pending_keys) or coverage_key | empty_keys | pending_keys != keys:
                    raise ReviewedDraftStagingError("covered_by_reader companion partition is invalid")
                key = next(iter(coverage_key))
                if coverage_claims.get(key) != claim_id:
                    raise ReviewedDraftStagingError("covered_by_reader claim does not own named source key")
                if any(blocks[key].get("text") or blocks[key].get("assets") or blocks[key].get("table_body") for key in empty_keys):
                    raise ReviewedDraftStagingError("covered_by_reader empty companion is not empty")
                expected_pending = set() if pending_source_keys is None else pending_source_keys
                declared_pending = {(page, view, raw) for view, raw in pending_keys}
                if declared_pending != expected_pending.intersection(declared_pending) or not declared_pending <= expected_pending:
                    raise ReviewedDraftStagingError("covered_by_reader pending companion lacks sealed diagnostic authority")
                if declared_pending and pending_source_keys is None:
                    raise ReviewedDraftStagingError("covered_by_reader pending companion requires sealed review input")
        elif action == "retain_unresolved":
            unresolved = True
        else:
            raise ReviewedDraftStagingError("unknown component action")
        conservation.append({"source_page": page, "ordinal": ordinal, "machine_disposition": entry["disposition"],
                             "source_keys": sorted(keys), "selected": sorted(chosen), "action": action,
                             **({"coverage_claim_id": resolution["coverage_claim_id"], "coverage_source_key": resolution["coverage_source_key"], "empty_companion_keys": resolution["empty_companion_keys"],
                                  **({"pending_companion_keys": resolution["pending_companion_keys"]} if set(resolution) == pending_fields else {})} if set(resolution) in (covered_fields, pending_fields) else {}),
                             "rationale": resolution["rationale"]})
    if seen != set(blocks) or not unresolved and accounted != selected:
        raise ReviewedDraftStagingError("full packet/selected-key conservation failed")
    return conservation, unresolved


def _semantic_preflight(target: Path, drafts: dict[int, dict], queue: dict, spec: dict, *, mode: str,
        review_draft_authority: dict[str, Any] | None, finalized_candidate_dir: Path | None = None,
        semantic_spec_paths: list[Path] | None = None, draft_input: Path | None = None) -> dict:
    if mode == "review_draft" and finalized_candidate_dir is not None:
        if semantic_spec_paths is None or draft_input is None:
            raise ReviewedDraftStagingError("review_draft staging requires a finalized semantic candidate")
        from kb_creator.scripts.author_reviewed_semantic_decisions import validate_final_candidate
        try:
            return validate_final_candidate(target, Path(finalized_candidate_dir), semantic_spec_paths, Path(draft_input))
        except ValueError as error:
            raise ReviewedDraftStagingError(f"finalized semantic candidate validation failed: {error}") from error
    from kb_creator.scripts.author_reviewed_semantic_decisions import _load_cold_drafts, validate_spec
    with tempfile.TemporaryDirectory(prefix="kb-reviewed-staging-") as temporary:
        root = Path(temporary); pages = root / "pages"; pages.mkdir()
        for page, draft in drafts.items():
            (pages / f"page-{page:03d}.json").write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
        _load_cold_drafts(pages, queue, review_draft_authority=review_draft_authority if mode == "review_draft" else None)
        spec_path = root / "spec.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        return validate_spec(target, root, [spec_path])


def validate_reviewed_staging_inputs(*, candidate_dir: Path, source_run_root: Path,
        target_run_root: Path, ledger_path: Path, semantic_spec_paths: list[Path],
        review_root: Path | None = None, mode: str = "strict", draft_input: Path | None = None,
        recomputed_coverage: dict[str, Any] | None = None,
        coverage_factories: list[dict[str, Any]] | None = None, coverage_source_pdf: Path | None = None,
        semantic_spec_root: Path | None = None, review_receipt_root: Path | None = None,
        finalized_candidate_dir: Path | None = None) -> StagingPreflight:
    if mode not in {"strict", "review_draft"}:
        raise ReviewedDraftStagingError("mode must be strict or review_draft")
    if (mode == "review_draft") != (draft_input is not None):
        raise ReviewedDraftStagingError("review_draft mode requires exactly one sealed draft input")
    if coverage_factories is not None:
        if recomputed_coverage is not None or coverage_source_pdf is None:
            raise ReviewedDraftStagingError("coverage factories require exactly one current source PDF")
        recomputed_coverage = recompute_coverage_factories(
            run_root=Path(target_run_root), source_pdf=Path(coverage_source_pdf),
            drafts_root=Path(finalized_candidate_dir) if finalized_candidate_dir is not None else Path(review_root or target_run_root),
            factories=coverage_factories,
        )
    review_authority: dict[str, Any] | None = None
    if draft_input is not None:
        try:
            input_record = validate_review_draft_input(_read(Path(draft_input)))
            review_authority = prepare_review_draft_input(input_record.value)
            review_authority["_sealed_unresolved_dispositions"] = input_record.value["unresolved_dispositions"]
            review_authority["_sealed_review_input"] = input_record.value
        except ReviewDraftError as exc:
            raise ReviewedDraftStagingError(str(exc)) from exc
    coverage_claims: dict[tuple[str, int], str] | None = None
    coverage_owner_keys: set[tuple[int, str, int]] = set()
    if recomputed_coverage is not None:
        rows = recomputed_coverage.get("claims") if isinstance(recomputed_coverage, dict) else None
        if not isinstance(rows, list):
            raise ReviewedDraftStagingError("recomputed coverage has no claim rows")
        coverage_claims = {}
        for wrapped in rows:
            row = wrapped.get("claim") if isinstance(wrapped, dict) else None
            claim = row.get("claim", row) if isinstance(row, dict) else None
            source_key = claim.get("source_key", claim.get("source_unit")) if isinstance(claim, dict) else None
            claim_id = claim.get("claim_id") if isinstance(claim, dict) else None
            if not isinstance(source_key, dict) or not isinstance(claim_id, str):
                raise ReviewedDraftStagingError("recomputed coverage claim is malformed")
            key = (source_key.get("view_id"), source_key.get("raw_index"))
            if key in coverage_claims:
                raise ReviewedDraftStagingError("recomputed coverage duplicates a source key")
            coverage_claims[key] = claim_id
            page = source_key.get("source_page")
            if type(page) is not int or not isinstance(key[0], str) or type(key[1]) is not int:
                raise ReviewedDraftStagingError("recomputed coverage source key is malformed")
            coverage_owner_keys.add((page, key[0], key[1]))
    candidate_dir, source, target = (Path(v).resolve() for v in (candidate_dir, source_run_root, target_run_root))
    review_root = Path(review_root).resolve() if review_root is not None else target
    semantic_spec_root = Path(semantic_spec_root).resolve() if semantic_spec_root is not None else review_root
    review_receipt_root = Path(review_receipt_root).resolve() if review_receipt_root is not None else review_root
    ledger_path = Path(ledger_path); ledger = _read(ledger_path)
    _shape(ledger, {"schema", "bindings", "pages"}, "staging ledger")
    if ledger["schema"] != LEDGER_SCHEMA:
        raise ReviewedDraftStagingError("reviewed staging requires ledger v2")
    pending_source_keys: set[tuple[int, str, int]] | None = None
    if mode == "review_draft":
        from .pending_source_choices import PendingSourceChoiceError, derive_pending_source_keys
        selected_keys: set[tuple[int, str, int]] = set()
        for row in ledger["pages"]:
            page = row.get("source_page") if isinstance(row, dict) else None
            if type(page) is not int:
                raise ReviewedDraftStagingError("staging ledger page is malformed")
            draft = _read(_verify(review_root, row.get("reviewed_draft"), "reviewed draft"))
            for selected in draft.get("selected_blocks", []):
                if not isinstance(selected, dict) or selected.get("purpose") == "asset":
                    continue
                view, raw = selected.get("view"), selected.get("raw_index")
                if not isinstance(view, str) or type(raw) is not int:
                    raise ReviewedDraftStagingError("reviewed draft selected block is malformed")
                selected_keys.add((page, view, raw))
        try:
            pending_source_keys = derive_pending_source_keys(
                review_input=review_authority["_sealed_review_input"], input_path=Path(draft_input),
                binding_root=review_root, run_root=target_run_root, selected_keys=selected_keys,
                coverage_owner_keys=coverage_owner_keys,
            )
        except PendingSourceChoiceError as error:
            raise ReviewedDraftStagingError(f"pending source authority is invalid: {error}") from error
    bound = ledger["bindings"]
    _shape(bound, {"candidate_manifest", "source_sha256", "target_queue", "semantic_specs"}, "ledger bindings")
    manifest_path = _verify(candidate_dir, bound["candidate_manifest"], "candidate manifest")
    manifest = _read(manifest_path)
    authority = (_authority(source, target, manifest, candidate_dir, mode=mode)
                 if mode == "review_draft" else _authority(source, target, manifest, candidate_dir))
    queue_path = _verify(target, bound["target_queue"], "target queue")
    if queue_path.resolve() != (target / "review/review_queue.json").resolve():
        raise ReviewedDraftStagingError("ledger must bind the authoritative target queue")
    queue = _read(queue_path)
    if manifest["authorities"]["source"]["sha256"] != bound["source_sha256"] or queue["source_sha256"] != bound["source_sha256"]:
        raise ReviewedDraftStagingError("source identity differs between candidate and target")
    if not isinstance(bound["semantic_specs"], list) or not bound["semantic_specs"]:
        raise ReviewedDraftStagingError("semantic spec bindings are required")
    paths = [_verify(semantic_spec_root, value, "semantic spec") for value in bound["semantic_specs"]]
    if len(paths) != len(set(paths)) or len(semantic_spec_paths) != len(paths) or {p.resolve() for p in paths} != {Path(p).resolve() for p in semantic_spec_paths}:
        raise ReviewedDraftStagingError("bind exactly the supplied unique semantic specs")
    spec = _compose_specs(paths)
    candidate_rows, queue_rows, ledger_rows, spec_rows = (
        _page_rows(value, label) for value, label in ((manifest["pages"], "candidate"), (queue["items"], "queue"), (ledger["pages"], "ledger"), (spec["pages"], "spec")))
    if not set(candidate_rows) == set(queue_rows) == set(ledger_rows) == set(spec_rows):
        raise ReviewedDraftStagingError("candidate, queue, ledger and spec page domains differ")
    from kb_creator.scripts.author_reviewed_semantic_decisions import _visual_inventory
    visuals = _visual_inventory(target)
    drafts, gaps, conservation, table_evidence = {}, {}, [], []
    retained_literals: set[tuple[int, str]] = set()
    for page in queue_rows:
        row = ledger_rows[page]
        _shape(row, {"source_page", "candidate_page", "target_packet", "target_visual", "reviewed_draft", "review_receipt", "resolutions", "tables"}, "ledger page")
        candidate_path = _verify(candidate_dir, row["candidate_page"], "candidate page")
        if row["candidate_page"] != candidate_rows[page]["candidate"]:
            raise ReviewedDraftStagingError("candidate page differs from manifest")
        expected_packet = {**queue_rows[page]["merge_packet"], "path": "outputs/04-visual-merge-bundle/" + queue_rows[page]["merge_packet"]["path"]}
        if row["target_packet"] != expected_packet:
            raise ReviewedDraftStagingError("target packet differs from review queue")
        packet_path = _verify(target, row["target_packet"], "target packet")
        old_packet = candidate_rows[page]["packet"]
        if any(old_packet[key] != row["target_packet"][key] for key in ("bytes", "sha256")):
            raise ReviewedDraftStagingError("packet changed; explicit remapping is not implemented")
        visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
        if visual_path not in visuals or row["target_visual"] != {"path": visual_path, **visuals[visual_path]}:
            raise ReviewedDraftStagingError("target visual is not the authoritative page visual")
        _verify(target, row["target_visual"], "target visual")
        candidate, packet = _read(candidate_path), _read(packet_path)
        mechanical_reconstruction._validate_candidate_page(candidate, schema=manifest.get("schema", mechanical_reconstruction.V2_SCHEMA))
        if packet["source_page"] != page or candidate["source_page"] != page:
            raise ReviewedDraftStagingError("candidate/packet page identity mismatch")
        draft_path = _verify(review_root, row["reviewed_draft"], "reviewed draft")
        review_path = _verify(review_receipt_root, row["review_receipt"], "page review")
        draft = _read(draft_path)
        if draft.get("source_page") != page or draft.get("semantic_role") != queue_rows[page]["contract_role"]:
            raise ReviewedDraftStagingError("reviewed draft page/role differs from queue")
        if not _review(page, draft, _read(review_path), row, spec, mode=mode,
                       review_draft_authority=review_authority):
            gaps.setdefault(page, []).append("unreviewed_final_page")
        if mode == "review_draft":
            retained_literals.update((page, value) for value in draft.get("unresolved", []) if isinstance(value, str))
        rows, unresolved = _conserve(page, candidate, packet, draft, row["resolutions"], spec,
                                     coverage_claims=coverage_claims, pending_source_keys=pending_source_keys)
        conservation.extend(rows)
        if unresolved:
            gaps.setdefault(page, []).append("unresolved_component")
        from .reviewed_table_evidence import verify_table_evidence
        table_evidence.extend(verify_table_evidence(target, packet, draft, spec_rows[page], row["tables"]))
        drafts[page] = draft
    if mode == "review_draft":
        sealed = review_authority.get("_sealed_unresolved_dispositions", []) if review_authority else []
        bound_literals = {
            (item["source_page"], item["predecessor_unresolved"])
            for item in sealed
            if isinstance(item, dict) and item.get("source_page") in ledger_rows
            and item.get("current", {}).get("sha256") == ledger_rows[item["source_page"]]["reviewed_draft"]["sha256"]
        }
        if retained_literals != bound_literals:
            raise ReviewedDraftStagingError("sealed unresolved dispositions do not exactly match reviewed drafts")
    semantics = None
    if not gaps:
        semantics = _semantic_preflight(target, drafts, queue, spec, mode=mode,
                                        review_draft_authority=review_authority,
                                        finalized_candidate_dir=finalized_candidate_dir,
                                        semantic_spec_paths=paths, draft_input=Path(draft_input) if draft_input else None)
    bindings = {"ledger": {"path": str(ledger_path.resolve()), **file_identity(ledger_path)},
                "candidate_manifest": {"path": str(manifest_path), **file_identity(manifest_path)},
                "target_queue": {"path": str(queue_path), **file_identity(queue_path)},
                "semantic_specs": [{"path": str(p), **file_identity(p)} for p in paths],
                "source_run_root": str(source), "target_run_root": str(target)}
    if finalized_candidate_dir is not None:
        final_manifest = Path(finalized_candidate_dir) / "candidate_manifest.json"
        bindings["finalized_candidate_manifest"] = {"path": str(final_manifest.resolve()), **file_identity(final_manifest)}
    literal_false = sorted(page for page, draft in drafts.items() if draft.get("review", {}).get("visual_reviewed") is False)
    state = "gaps" if gaps else "prepared_for_audit" if mode == "review_draft" else "ready"
    return StagingPreflight(state, gaps, bindings, conservation, drafts, spec,
                            {"authority": authority, "tables": table_evidence, "semantic_validation": semantics,
                             "mode": mode, "review_draft_preflight": review_authority,
                             "visual_reviewed_false_pages": literal_false,
                             "coverage_factories": recomputed_coverage})


def stage_reviewed_drafts(**kwargs: Any) -> dict[str, Any]:
    destination = Path(kwargs.pop("destination")).resolve()
    if destination.exists():
        raise FileExistsError("staging destination already exists")
    preflight = validate_reviewed_staging_inputs(**kwargs)
    report = {"schema": "kb_creator.reviewed_draft_staging.v3", "state": preflight.state,
              "gaps": preflight.gaps, "bindings": preflight.bindings,
              "source_key_conservation": preflight.conservation, "evidence": preflight.evidence}
    destination.mkdir(parents=True, exist_ok=False)
    if preflight.state == "gaps":
        (destination / "staging-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report
    pages = destination / "pages"; pages.mkdir()
    artifacts = []
    for page, draft in preflight.pages.items():
        path = pages / f"page-{page:03d}.json"
        path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        artifacts.append({"path": path.relative_to(destination).as_posix(), **file_identity(path)})
    spec_path = destination / "spec.json"
    spec_path.write_text(json.dumps(preflight.spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts.append({"path": "spec.json", **file_identity(spec_path)})
    report.update(page_count=len(preflight.pages), artifacts=artifacts)
    try:
        report = json.loads(json.dumps(report, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError, RecursionError) as exc:
        raise ReviewedDraftStagingError("staging manifest is not JSON round-trippable") from exc
    report["manifest_sha256"] = sha256_bytes(canonical_bytes(report))
    manifest_path = destination / "staging-manifest.json"
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        written = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_seal(written, "manifest_sha256")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ReviewedDraftStagingError("written staging manifest seal is invalid") from exc
    if written != report:
        raise ReviewedDraftStagingError("written staging manifest did not round-trip")
    return report
