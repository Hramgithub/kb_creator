"""Materialize a fresh, reviewed semantic decision set from an immutable baseline.

The scenario spec contains editorial replacements and unit-to-source mappings;
this helper computes every visual, span, allowlist, and decision identity from
the selected fresh replay rather than storing derived hashes in the spec.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.source_choice_translation import (
    _author_ledger_snapshot_scope, open_verified_ledger_v2_snapshot, reverify_ledger_v2_snapshot,
)
from kb_creator.pipeline.semantic_structure import (
    PROFILE,
    PROFILE_V2,
    SCHEMA,
    SCHEMA_V2,
    _normalized,
    apply_reviewed_text_corrections,
    apply_block_boundaries,
    reviewed_block_text_corrections,
    reviewed_text_corrections,
)
from kb_creator.pipeline.source_marker_dispositions import (
    SourceMarkerDispositionError,
    load_bound_inputs,
    validate as validate_source_marker_dispositions,
)
from kb_creator.pipeline.source_page_render import (
    replay_source_render_context,
    render_source_pdf_page,
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


class _AuthorLedgerContexts:
    """Keep verified V2 ledgers local to one top-level author invocation."""

    def __init__(self, owner: object) -> None:
        self._owner = owner
        self._snapshots = {}

    def _require_owner(self, owner: object) -> None:
        if owner is not self._owner:
            raise ValueError("ledger context belongs to another author invocation")

    def lookup_v2(self, owner: object, ledger: Path, issue_id: str) -> tuple[Mapping[str, Any] | None, Mapping[str, Any] | None]:
        self._require_owner(owner)
        path = ledger.resolve()
        if path not in self._snapshots:
            self._snapshots[path] = open_verified_ledger_v2_snapshot(path)
        snapshot = self._snapshots[path]
        return snapshot.ledger_by_issue.get(issue_id), snapshot.queue_by_issue.get(issue_id)

    def snapshot_v2(self, owner: object, ledger: Path):
        self._require_owner(owner)
        path = ledger.resolve()
        if path not in self._snapshots:
            self._snapshots[path] = open_verified_ledger_v2_snapshot(path)
        return self._snapshots[path]

    def audit_values_v2(self, owner: object, ledger: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        snapshot = self.snapshot_v2(owner, ledger)
        verified = {"ledger": str(snapshot.ledger_path), "submission": str(snapshot.submission_path),
                    "queue": str(snapshot.queue_path), "ledger_sha256": snapshot.ledger_value["ledger_sha256"],
                    "choices": len(snapshot.ledger_by_issue)}
        return verified, json.loads(snapshot.ledger_bytes), json.loads(snapshot.queue_bytes)

    def reverify_before_publish(self, owner: object) -> None:
        self._require_owner(owner)
        for snapshot in self._snapshots.values():
            reverify_ledger_v2_snapshot(snapshot)


def _mutable_ledger_json(value: Any) -> Any:
    """Copy frozen snapshot values into ordinary JSON values for emitted rows."""
    if isinstance(value, Mapping):
        return {key: _mutable_ledger_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_mutable_ledger_json(item) for item in value]
    return value


def _normalized_reader_markdown(markdown: str) -> str:
    """Use the fidelity proof stream, which excludes binary asset markup."""
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import ASSET, IMAGE
    return _normalized(ASSET.sub("", IMAGE.sub("", markdown)))


def semantic_assertion_map(
    assertions: Mapping[str, Mapping[str, Any]], decisions: Mapping[int, Mapping[str, Any]],
    packets: Mapping[int, Mapping[str, Any]], geometry: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Add ephemeral reader intervals for positional semantic proof.

    The reviewed allowlist intentionally retains its sealed positional row
    shape.  This map is the shared preflight/final-authoring adapter consumed
    by semantic validation; it never writes a new field to the allowlist.
    """
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _v3_page_context
    result: dict[str, dict[str, Any]] = {}
    positional = {"before_anchor", "after_anchor", "column_before_anchor", "column_after_anchor"}
    for identity, row in assertions.items():
        copied = copy.deepcopy(dict(row))
        placement = copied.get("placement")
        if not isinstance(placement, dict) or placement.get("relation") not in positional:
            result[identity] = copied
            continue
        page = copied.get("source_page")
        anchor = placement.get("anchor_unit")
        if type(page) is not int or not isinstance(anchor, dict):
            raise ValueError(f"positional semantic assertion is malformed: {identity}")
        errors: list[str] = []
        context = _v3_page_context(page, packets[page], decisions[page], geometry, errors)
        mappings = [item for item in context["mappings"] if item["unit"].get("view_id") == anchor.get("view_id") and item["unit"].get("raw_index") == anchor.get("raw_index")]
        if errors or len(mappings) != 1:
            raise ValueError(f"page {page}: source assertion anchor lacks one corrected reader mapping")
        normalized = _normalized(str(copied.get("text", "")))
        anchor_start, anchor_end = mappings[0]["markdown_span"]
        if placement["relation"] in {"after_anchor", "column_after_anchor"}:
            start, end = anchor_end, anchor_end + len(normalized)
        else:
            start, end = anchor_start - len(normalized), anchor_start
        if start < 0 or context["rendered"][start:end] != normalized:
            raise ValueError(f"page {page}: positional assertion reader adjacency failed: {identity}")
        copied["placement"] = {**placement, "markdown_span": {"start": start, "end": end}}
        result[identity] = copied
    return result


def _canonical_assertion_proof(text: str, assertions: list[dict[str, Any]]) -> str:
    after_relations = {"after_anchor", "column_after_anchor"}
    before = [row for row in assertions if row.get("placement", {}).get("relation") not in after_relations]
    after = [row for row in assertions if row.get("placement", {}).get("relation") in after_relations]
    return "".join(_normalized(row["text"]) for row in before) + _normalized(text) + "".join(_normalized(row["text"]) for row in after)


def identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": digest(data)}


def display_text(text: str) -> str:
    """Remove only MinerU's inline sup/sub tags for reader display selectors."""
    return re.sub(r"</?(?:sup|sub)>", "", text, flags=re.IGNORECASE)


def _replace_source_text(markdown: str, source_text: str, replacement: str, page: int) -> str:
    candidates = list(dict.fromkeys([source_text, display_text(source_text)]))
    matches = [text for text in candidates if text and markdown.count(text) == 1]
    if len(matches) != 1:
        raise ValueError(f"page {page}: exact source/display text is not unique: {source_text[:80]!r}")
    return markdown.replace(matches[0], replacement, 1)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _recompute_prepared_coverage(staging_manifest: Path, run_root: Path, drafts_root: Path) -> list[dict[str, Any]]:
    """Reopen sealed factories; never trust a staged claim status or payload."""
    staging = json.loads(staging_manifest.read_text(encoding="utf-8"))
    coverage = staging.get("evidence", {}).get("coverage_factories") if isinstance(staging, dict) else None
    if not isinstance(coverage, dict) or coverage.get("schema") != "kb_creator.review_draft_coverage_factories.v1":
        raise ValueError("prepared staging lacks coverage factory descriptors")
    source = coverage.get("source_pdf")
    rows = coverage.get("factories")
    if not isinstance(rows, list):
        raise ValueError("prepared coverage descriptors are malformed")

    def descriptor_path(record: Any, label: str) -> Path:
        required = {"path", "bytes", "sha256"}
        if not isinstance(record, dict) or set(record) != required or not isinstance(record["path"], str):
            raise ValueError(f"prepared coverage {label} descriptor is malformed")
        path = Path(record["path"])
        if not path.is_file() or identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise ValueError(f"prepared coverage {label} identity is stale")
        return path

    source_path = descriptor_path(source, "source PDF")
    factories = []
    for row in rows:
        required = {"factory_id", "selectors", "evidence", "claim_count"}
        permitted = required | {"reuse_run"}
        if not isinstance(row, dict) or (set(row) != required and set(row) != permitted) or not isinstance(row["factory_id"], str) or not isinstance(row["claim_count"], int):
            raise ValueError("prepared coverage factory descriptor is malformed")
        selectors_path = descriptor_path(row["selectors"], "selector")
        evidence_path = descriptor_path(row["evidence"], "evidence")
        factory = {"factory_id": row["factory_id"], "selectors_path": str(selectors_path), "evidence_path": str(evidence_path)}
        if "reuse_run" in row:
            reuse = descriptor_path(row["reuse_run"], "reuse run")
            if reuse.name != "run.json":
                raise ValueError("prepared coverage reuse run descriptor is malformed")
            factory["reuse_run_root"] = str(reuse.parent)
        factories.append(factory)
    from kb_creator.pipeline.reviewed_draft_staging import recompute_coverage_factories
    actual = recompute_coverage_factories(run_root=run_root, source_pdf=source_path, drafts_root=drafts_root, factories=factories)
    claims = [item["claim"] for item in actual["claims"]]
    if len(claims) != actual["source_key_owner_count"]:
        raise ValueError("recomputed coverage ownership count is inconsistent")
    return claims


def _recompute_composer_coverage(review_input: dict[str, Any], binding_root: Path, run_root: Path,
                                 drafts_root: Path) -> list[dict[str, Any]] | None:
    record = review_input.get("bindings", {}).get("coverage_factories")
    if record is None:
        return None
    required = {"path", "bytes", "sha256"}
    if not isinstance(record, dict) or set(record) != required or not isinstance(record["path"], str):
        raise ValueError("composer coverage factory binding is malformed")
    path = (binding_root / record["path"]).resolve()
    try:
        path.relative_to(binding_root.resolve())
    except ValueError as exc:
        raise ValueError("composer coverage factory binding escapes root") from exc
    if not path.is_file() or identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
        raise ValueError("composer coverage factory binding is stale")
    factories = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(factories, list):
        raise ValueError("composer coverage factories are malformed")
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    source = Path(str(run.get("local", {}).get("source_path", "")))
    from kb_creator.pipeline.reviewed_draft_staging import recompute_coverage_factories
    actual = recompute_coverage_factories(run_root=run_root, source_pdf=source, drafts_root=drafts_root, factories=factories)
    return [item["claim"] for item in actual["claims"]]


def _composer_coverage_successor_dispositions(review_input: dict[str, Any], binding_root: Path,
                                               claims: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]] | None:
    """Reopen a sealed R1 coverage disposition; factories stay source evidence."""
    record = review_input.get("bindings", {}).get("source_choice_coverage_dispositions")
    if record is None:
        return None
    required = {"path", "bytes", "sha256"}
    if not isinstance(record, dict) or set(record) != required or not isinstance(record["path"], str):
        raise ValueError("composer coverage successor disposition binding is malformed")
    path = (binding_root / record["path"]).resolve()
    if not path.is_file() or identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
        raise ValueError("composer coverage successor disposition binding is stale")
    value = json.loads(path.read_text(encoding="utf-8"))
    for binding_name, field in (("source_choice_predecessor", "predecessor_input"),
                                ("source_choice_ledger", "ledger"), ("source_choice_queue", "queue")):
        bound = review_input.get("bindings", {}).get(binding_name)
        declared = value.get(field) if isinstance(value, dict) else None
        if (not isinstance(bound, dict) or set(bound) != required
                or not isinstance(declared, dict) or set(declared) != required
                or (binding_root / bound["path"]).resolve() != Path(declared["path"]).resolve()
                or any(bound[name] != declared[name] for name in ("bytes", "sha256"))):
            raise ValueError(f"coverage disposition differs from successor {binding_name} binding")
    predecessor = value.get("predecessor_input", {}) if isinstance(value, dict) else {}
    ledger = value.get("ledger", {}) if isinstance(value, dict) else {}
    from kb_creator.pipeline.source_choice_coverage_successor import (
        SourceChoiceCoverageSuccessorError, validate_dispositions,
    )
    try:
        return validate_dispositions(value, predecessor_input=Path(predecessor["path"]),
                                     ledger_path=Path(ledger["path"]), claims=claims or [])
    except (KeyError, TypeError, SourceChoiceCoverageSuccessorError) as error:
        raise ValueError(f"composer coverage successor disposition is invalid: {error}") from error


def _write_failed_fidelity_audit(destination: Path, run_root: Path, staging_manifest: Path | None, spec_paths: list[Path], output: Path, audit: dict[str, Any]) -> None:
    path = destination.parent / f"{destination.name}.failed-fidelity-audit.json"
    if path.exists():
        raise ValueError(f"failed fidelity audit diagnostic already exists: {path}")
    payload = {"schema": "kb_creator.failed_fidelity_audit.v1", "state": "failed_unpublished",
               "run": {"path": str((run_root / "run.json").resolve()), **identity(run_root / "run.json")},
               "specs": [{"path": str(item.resolve()), **identity(item)} for item in spec_paths],
               "prepared_staging": ({"path": str(staging_manifest.resolve()), **identity(staging_manifest)} if staging_manifest else None),
               "candidate": {"decision_set": {"path": "decision_set.json", **identity(output / "decision_set.json")}},
               "allowlist": {"path": "reviewed_allowlist.v3.json", **identity(output / "reviewed_allowlist.v3.json")}, "audit": audit}
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists():
        raise ValueError(f"failed fidelity audit temporary path already exists: {temporary}")
    write_json(temporary, payload); temporary.replace(path)


def _validate_authored_pages(decisions: dict[int, dict[str, Any]], packets: dict[int, dict[str, Any]],
                             comparison: dict[str, Any], raw_root: Path, source_render_context: Any,
                             source_render_staging: Path, reference_proof_keys: Any,
                             split_structure_proof_keys: Any,
                             structural_role_proofs: Any = None,
                             visual_assertions: Any = None) -> dict[str, Any]:
    """Run the real Stage06 validator on every page without publishing output."""
    from kb_creator.scripts.materialize_mineru_ai_merge import _validate_decision
    names: set[str] = set()
    failures, passed_pages = [], []
    for page in sorted(decisions):
        candidate_names = set(names)
        try:
            _validate_decision(decisions[page], packets[page], comparison, raw_root,
                               candidate_names, source_render_context, source_render_staging,
                               reference_proof_keys, split_structure_proof_keys, structural_role_proofs,
                               visual_assertions)
        except ValueError as exc:
            failures.append({"source_page": page, "error_type": type(exc).__name__, "error": str(exc)})
        else:
            names = candidate_names
            passed_pages.append(page)
    return {"scope": "first_validation_error_per_page", "checked_pages": sorted(decisions),
            "passed_pages": passed_pages, "failures": failures, "passed": not failures}


def _write_failed_decision_validation(destination: Path, run_root: Path, staging_manifest: Path | None,
                                      spec_paths: list[Path], output: Path, audit: dict[str, Any],
                                      validation: dict[str, Any]) -> None:
    """Preserve successful Stage05 and exact failed candidates before temp cleanup."""
    path = destination.parent / f"{destination.name}.failed-decision-validation.json"
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.exists() or temporary.exists():
        raise ValueError(f"failed decision validation diagnostic already exists: {path}")
    payload = {"schema": "kb_creator.failed_decision_validation.v1", "state": "failed_unpublished",
               "accepted": False,
               "run": {"path": str((run_root / "run.json").resolve()), **identity(run_root / "run.json")},
               "specs": [{"path": str(item.resolve()), **identity(item)} for item in spec_paths],
               "prepared_staging": ({"path": str(staging_manifest.resolve()), **identity(staging_manifest)} if staging_manifest else None),
               "decision_set": {"path": "decision_set.json", **identity(output / "decision_set.json")},
               "allowlist": {"path": "reviewed_allowlist.v3.json", **identity(output / "reviewed_allowlist.v3.json")},
               "stage05_audit": audit, "stage06_validation": validation,
               "candidate_pages": [{"path": file.relative_to(output).as_posix(), **identity(file),
                                    "decision": json.loads(file.read_text(encoding="utf-8"))}
                                   for file in sorted((output / "pages").glob("page-*.json"))]}
    write_json(temporary, payload); temporary.replace(path)


def _derive_source_page_render(run_root: Path, geometry: dict[str, Any], page: int, selector: Any, preview_root: Path) -> dict[str, Any]:
    """Derive the only permitted source-page render row from an explicit review selector."""
    required = {"logical_name", "dpi", "visual_reviewed", "rationale"}
    if not isinstance(selector, dict) or set(selector) != required or selector["visual_reviewed"] is not True or not isinstance(selector["logical_name"], str) or not isinstance(selector["rationale"], str) or not selector["rationale"].strip():
        raise ValueError(f"page {page}: source_page_render selector needs a closed reviewed shape")
    context = replay_source_render_context(run_root, geometry)
    preview = preview_root / f"page-{page:03d}-{selector['logical_name']}"
    facts = render_source_pdf_page(context["source"], page, context["renderer"], selector["dpi"], preview, expected_source_sha256=context["source_sha256"], expected_renderer_sha256=context["renderer_sha256"])
    return {"origin": "source_pdf_page_render_v1", "source_page": page, "source_sha256": facts["source_sha256"], "logical_name": selector["logical_name"], "placement": "full_page", "render": {key: facts[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")}, "source_visual_review": {"visual_reviewed": True, "rationale": selector["rationale"]}}


def _load_spec_fragments(paths: list[Path]) -> dict[str, Any]:
    """Compose disjoint reviewed page fragments without scenario-specific glue."""
    pages: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    segmentation: list[dict[str, Any]] = []
    seen_pages: set[int] = set()
    seen_assertions: set[str] = set()
    profiles: set[str] = set()
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        profile = value.get("semantic_structure_profile", PROFILE)
        if profile not in {PROFILE, PROFILE_V2}:
            raise ValueError(f"invalid semantic_structure_profile: {profile!r}")
        profiles.add(profile)
        for page in value.get("pages", []):
            number = page.get("source_page")
            if type(number) is not int or number in seen_pages:
                raise ValueError(f"duplicate or invalid source_page across spec fragments: {number!r}")
            seen_pages.add(number)
            pages.append(page)
        for assertion in value.get("visual_text_assertions", []):
            identity = assertion.get("assertion_id")
            if not isinstance(identity, str) or not identity or identity in seen_assertions:
                raise ValueError(f"duplicate or invalid assertion_id across spec fragments: {identity!r}")
            seen_assertions.add(identity)
            assertions.append(assertion)
        exclusions.extend(value.get("source_text_exclusions", []))
        segmentation.extend(value.get("text_segmentation_claims", []))
    if len(profiles) != 1:
        raise ValueError("spec fragments must declare one semantic_structure_profile")
    return {
        "pages": sorted(pages, key=lambda row: row["source_page"]),
        "visual_text_assertions": assertions,
        "source_text_exclusions": exclusions,
        "text_segmentation_claims": segmentation,
        "semantic_structure_profile": profiles.pop(),
    }


def _visual_inventory(run_root: Path) -> dict[str, dict[str, Any]]:
    data = json.loads((run_root / "outputs/04-visual-merge-bundle/visual/visual_manifest.json").read_text(encoding="utf-8"))
    inventory: dict[str, dict[str, Any]] = {}
    def visit(node: Any) -> None:
        if isinstance(node, dict):
            path = node.get("path")
            if isinstance(path, str) and path.startswith("visual/"):
                relative = f"outputs/04-visual-merge-bundle/{path}"
                local = run_root / relative
                if local.is_file():
                    inventory[relative] = identity(local)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(data)
    from kb_creator.pipeline.reconstruction_asset_inventory import selected_asset_inventory
    return selected_asset_inventory(run_root, inventory)


def _packet_unit(run_root: Path, page: int, view: str, raw_index: int) -> dict[str, Any]:
    packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
    block = next(row for row in packet["views"][view]["blocks"] if row["raw_index"] == raw_index)
    text = block.get("text", "")
    normalized = _normalized(text)
    return {"source_page": page, "view_id": view, "raw_index": raw_index, "block_type": block.get("type"), "bbox": block["bbox"], "original_text_sha256": digest(text.encode()), "normalized_text_sha256": digest(normalized.encode()), "normalized_character_count": len(normalized)}


def _packet_text(run_root: Path, page: int, view: str, raw_index: int) -> str:
    packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
    return next(row["text"] for row in packet["views"][view]["blocks"] if row["raw_index"] == raw_index)


def _validate_ocr_selector_domain(run_root: Path, classes: Any) -> None:
    """Fail before rendering when a textual OCR class names a non-text unit."""
    if not isinstance(classes, list):
        raise ValueError("OCR equivalence classes must be a list")
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _make_unit

    packets: dict[int, dict[str, Any]] = {}
    for row in classes:
        if not isinstance(row, dict):
            raise ValueError("OCR equivalence class must be an object")
        class_id, page = row.get("class_id"), row.get("source_page")
        if not isinstance(class_id, str) or not class_id or type(page) is not int:
            raise ValueError("OCR equivalence class has invalid class_id or source_page")
        canonical = row.get("canonical", row.get("canonical_unit"))
        alternates = row.get("alternates", row.get("alternate_units"))
        if not isinstance(canonical, dict) or not isinstance(alternates, list):
            raise ValueError(f"OCR class {class_id!r} page {page}: canonical or alternates are invalid")
        packet = packets.setdefault(
            page,
            json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8")),
        )
        for role, member in [("canonical", canonical), *(("alternate", value) for value in alternates)]:
            if not isinstance(member, dict):
                raise ValueError(f"OCR class {class_id!r} page {page}: {role} member has invalid view/index")
            view, raw_index = member.get("view_id"), member.get("raw_index")
            if not isinstance(view, str) or type(raw_index) is not int:
                raise ValueError(f"OCR class {class_id!r} page {page}: {role} member has invalid view/index")
            blocks = packet.get("views", {}).get(view, {}).get("blocks")
            matches = [block for block in blocks if isinstance(block, dict) and block.get("raw_index") == raw_index] if isinstance(blocks, list) else []
            if len(matches) != 1:
                raise ValueError(f"OCR class {class_id!r} page {page}: {role} member missing view={view!r} raw_index={raw_index}")
            try:
                unit = _make_unit(page, view, matches[0])
            except ValueError as exc:
                raise ValueError(f"OCR class {class_id!r} page {page}: {role} member is not a textual Stage05 unit view={view!r} raw_index={raw_index}") from exc
            if unit.get("_normalization_empty_artifact"):
                raise ValueError(f"OCR class {class_id!r} page {page}: {role} member has empty lexical normalization view={view!r} raw_index={raw_index}")


def _validate_ocr_support_membership(raw_specs: list[dict[str, Any]]) -> None:
    """Reject a named OCR support unless the raw assertion anchors it exactly."""
    anchored: dict[tuple[int, str, int], set[str]] = {}
    for spec in raw_specs:
        for assertion in spec.get("visual_text_assertions", []):
            if not isinstance(assertion, dict):
                continue
            anchor, identity, page = assertion.get("anchor"), assertion.get("assertion_id"), assertion.get("source_page")
            if isinstance(anchor, dict) and isinstance(identity, str) and type(page) is int and isinstance(anchor.get("view_id"), str) and type(anchor.get("raw_index")) is int:
                anchored.setdefault((page, anchor["view_id"], anchor["raw_index"]), set()).add(identity)
        for row in spec.get("ocr_equivalence_classes", []):
            if not isinstance(row, dict) or "supporting_assertion_ids" not in row:
                continue
            canonical, class_id, page, named = row.get("canonical"), row.get("class_id"), row.get("source_page"), row.get("supporting_assertion_ids")
            if not isinstance(canonical, dict) or not isinstance(class_id, str) or type(page) is not int or not isinstance(named, list) or len(named) != len(set(named)) or any(not isinstance(item, str) or not item for item in named):
                raise ValueError("reviewed OCR selector support IDs are invalid")
            actual = anchored.get((page, canonical.get("view_id"), canonical.get("raw_index")), set())
            missing = sorted(set(named) - actual)
            if missing:
                raise ValueError(f"OCR class {class_id!r} page {page}: named support is absent or anchored elsewhere: {missing}")


def _packet_asset_block(run_root: Path, page: int, view: str, raw_index: int, source_path: str) -> dict[str, Any]:
    """Resolve an actual selected image/table block; never synthesize OCR evidence."""
    packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
    blocks = packet.get("views", {}).get(view, {}).get("blocks", [])
    matches = [row for row in blocks if isinstance(row, dict) and row.get("raw_index") == raw_index]
    if len(matches) != 1:
        raise ValueError(f"page {page}: selected asset block is stale or ambiguous")
    block = matches[0]
    if block.get("type") not in {"image", "table"} or block.get("assets") != [source_path] or not isinstance(block.get("bbox"), list):
        raise ValueError(f"page {page}: selected asset block has no exact single asset")
    return {"source_page": page, "view_id": view, "raw_index": raw_index, "block_type": block["type"], "bbox": block["bbox"], "source_path": source_path}


def _source_fragments(packet: dict[str, Any], definition: dict[str, Any], default_view: str, page: int, shared: set[tuple[str, int]]) -> list[dict[str, Any]]:
    """Resolve reviewed v2 offsets into exact hash-bound fragment identities."""
    selectors = definition.get("source_fragments")
    if selectors is None:
        selectors = []
        for raw_index in definition.get("raw_indices", []):
            key = (definition.get("view") or default_view, raw_index)
            if key in shared:
                raise ValueError(f"page {page}: shared v2 source block requires explicit source_fragments")
            text = next((block.get("text") for block in packet.get("views", {}).get(key[0], {}).get("blocks", []) if block.get("raw_index") == raw_index), None)
            if not isinstance(text, str) or not text:
                raise ValueError(f"page {page}: v2 source fragment selector is stale or out of range")
            selectors.append({"view": key[0], "raw_index": raw_index, "start": 0, "end": len(text)})
    if not isinstance(selectors, list):
        raise ValueError(f"page {page}: v2 unit source_fragments must be a list")
    rows = []
    for selector in selectors:
        if not isinstance(selector, dict) or set(selector) - {"view", "raw_index", "start", "end"}:
            raise ValueError(f"page {page}: v2 source fragment selector is invalid")
        view = selector.get("view", default_view)
        raw_index, start, end = selector.get("raw_index"), selector.get("start"), selector.get("end")
        if not isinstance(view, str) or type(raw_index) is not int or type(start) is not int or type(end) is not int:
            raise ValueError(f"page {page}: v2 source fragment selector is invalid")
        text = next((block.get("text") for block in packet.get("views", {}).get(view, {}).get("blocks", []) if block.get("raw_index") == raw_index), None)
        if not isinstance(text, str) or not 0 <= start < end <= len(text):
            raise ValueError(f"page {page}: v2 source fragment selector is stale or out of range")
        fragment = text[start:end]
        rows.append({"view": view, "raw_index": raw_index, "source_sha256": digest(text.encode("utf-8")), "normalized_sha256": digest(_normalized(fragment).encode("utf-8")), "start": start, "end": end, "fragment_sha256": digest(fragment.encode("utf-8"))})
    return rows


def _shared_unit_sources(row: dict[str, Any], default_view: str) -> set[tuple[str, int]]:
    """Find sources assigned to more than one semantic unit on a page."""
    counts: dict[tuple[str, int], int] = {}
    for definition in row.get("units", []):
        for raw_index in definition.get("raw_indices", []):
            key = (definition.get("view", default_view), raw_index)
            counts[key] = counts.get(key, 0) + 1
    return {key for key, count in counts.items() if count > 1}


def _build_semantic_unit(packet: dict[str, Any], definition: dict[str, Any],
                         default_view: str, page: int, lines: list[str],
                         shared_sources: set[tuple[str, int]], profile: str) -> dict[str, Any]:
    """Build the exact unit shape used by authoring and prepared owner checks."""
    start, end = _definition_span(lines, definition, page)
    unit = {
        "id": definition["id"], "kind": definition["kind"],
        "representation": definition["representation"],
        "source_blocks": [{"view": definition.get("view") or default_view, "raw_index": index}
                          for index in definition["raw_indices"]],
        "markdown_span": {"start_line": start, "end_line": end,
                          "sha256": digest("\n".join(lines[start - 1:end]).encode("utf-8"))},
        "container_parent": definition.get("container_parent"),
        "semantic_parent": definition.get("semantic_parent"),
        "continuation_of": definition.get("continuation_of"),
        "heading_level": definition.get("heading_level"),
        "item_count": definition.get("item_count"),
    }
    if profile == PROFILE_V2:
        unit["source_fragments"] = ([] if definition.get("visual_assertion_ids") is not None
                                    else _source_fragments(packet, definition, default_view, page, shared_sources))
        if "visual_assertion_ids" in definition:
            ids = definition["visual_assertion_ids"]
            if not isinstance(ids, list) or len(ids) != len(set(ids)) or any(
                    not isinstance(value, str) or not value for value in ids):
                raise ValueError(f"page {page}: visual_assertion_ids must be a unique nonempty-id list")
            unit["visual_assertion_ids"] = ids
    return unit


def _unit_definitions(row: dict[str, Any], baseline: dict[str, Any], page: int) -> list[dict[str, Any]]:
    """Use only baseline logical selectors; all fresh span/hash evidence is rebuilt."""
    inherit = row.get("inherit_units_from_baseline", False)
    supplied = row.get("units")
    if inherit is not True and inherit is not False:
        raise ValueError(f"page {page}: inherit_units_from_baseline must be boolean")
    if inherit:
        if supplied is not None:
            raise ValueError(f"page {page}: inherited units are mutually exclusive with units")
        structure = baseline.get("semantic_structure")
        if not isinstance(structure, dict) or not isinstance(structure.get("units"), list):
            raise ValueError(f"page {page}: baseline has no semantic units to inherit")
        result = []
        for unit in structure["units"]:
            if not isinstance(unit, dict) or not isinstance(unit.get("markdown_span"), dict):
                raise ValueError(f"page {page}: baseline semantic unit is invalid")
            sources = unit.get("source_blocks")
            views = {source.get("view") for source in sources if isinstance(source, dict)} if isinstance(sources, list) else set()
            if len(views) != 1:
                raise ValueError(f"page {page}: inherited unit must have one explicit source view")
            inherited_fragments = unit.get("source_fragments", [])
            if not isinstance(inherited_fragments, list) or any(
                not isinstance(fragment, dict)
                or type(fragment.get("raw_index")) is not int
                or type(fragment.get("start")) is not int
                or type(fragment.get("end")) is not int
                or not isinstance(fragment.get("view"), str)
                for fragment in inherited_fragments
            ):
                raise ValueError(f"page {page}: inherited source fragments are invalid")
            result.append({
                "id": unit.get("id"), "kind": unit.get("kind"), "representation": unit.get("representation"),
                "view": views.pop(), "raw_indices": [source.get("raw_index") for source in sources],
                # A v1 baseline has no reviewed partition ledger.  Keep the
                # mandatory v2 field empty so the existing whole-source-block
                # validation remains authoritative.  A v2 baseline contributes
                # only its reviewed selectors; fresh source and fragment hashes
                # are recomputed below against the selected replay packet.
                "source_fragments": [
                    {key: fragment[key] for key in ("view", "raw_index", "start", "end")}
                    for fragment in inherited_fragments
                ],
                "start_line": unit["markdown_span"].get("start_line"), "end_line": unit["markdown_span"].get("end_line"),
                "container_parent": unit.get("container_parent"), "semantic_parent": unit.get("semantic_parent"),
                "continuation_of": unit.get("continuation_of"), "heading_level": unit.get("heading_level"), "item_count": unit.get("item_count"),
            })
        return result
    if not isinstance(supplied, list):
        raise ValueError(f"page {page}: units must be a list")
    return supplied


def _definition_span(lines: list[str], definition: dict[str, Any], page: int) -> tuple[int, int]:
    if "start_line" in definition or "end_line" in definition:
        start, end = definition.get("start_line"), definition.get("end_line")
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError(f"page {page}: inherited semantic span is stale")
        return start, end
    return _find_span(lines, definition["start"], definition.get("end"))


def _find_span(lines: list[str], start: str, end: str | None = None) -> tuple[int, int]:
    starts = [i for i, line in enumerate(lines) if start in line]
    if len(starts) != 1:
        raise ValueError(f"span start selector must be unique: {start!r} ({len(starts)} hits)")
    first = starts[0]
    if end is None:
        return first + 1, first + 1
    ends = [i for i in range(first, len(lines)) if end in lines[i]]
    if len(ends) != 1:
        raise ValueError(f"span end selector must be unique after start: {end!r} ({len(ends)} hits)")
    return first + 1, ends[0] + 1


def _patch_markdown(markdown: str, patches: list[dict[str, str]], page: int) -> str:
    for patch in patches:
        before, after = patch["before"], patch["after"]
        count = markdown.count(before)
        if count != patch.get("count", 1):
            raise ValueError(f"page {page}: expected {patch.get('count', 1)} patch matches, found {count}: {before[:80]!r}")
        markdown = markdown.replace(before, after)
    return markdown


def _append_review_notes(decision: dict[str, Any], notes: Any, page: int) -> None:
    """Append explicit, reviewer-authored evidence notes without replacing history."""
    if notes is None:
        return
    if not isinstance(notes, list) or not notes or any(not isinstance(note, str) or not note.strip() for note in notes):
        raise ValueError(f"page {page}: review_notes_append must be a non-empty list of non-empty strings")
    review = decision.get("review")
    if not isinstance(review, dict) or review.get("visual_reviewed") is not True or not isinstance(review.get("notes"), str):
        raise ValueError(f"page {page}: review notes require an existing visually reviewed decision")
    existing = review["notes"].rstrip()
    review["notes"] = existing + "\n" + "\n".join(note.strip() for note in notes)


def _remove_review_notes(decision: dict[str, Any], notes: Any, page: int) -> None:
    """Remove superseded exact review-note lines while retaining all other history."""
    if notes is None:
        return
    if not isinstance(notes, list) or not notes or any(not isinstance(note, str) or not note.strip() for note in notes):
        raise ValueError(f"page {page}: review_notes_remove must be a non-empty list of non-empty strings")
    review = decision.get("review")
    if not isinstance(review, dict) or not isinstance(review.get("notes"), str):
        raise ValueError(f"page {page}: review notes require an existing decision review")
    lines = review["notes"].splitlines()
    for note in notes:
        exact = note.strip()
        if lines.count(exact) != 1:
            raise ValueError(f"page {page}: superseded review note must match exactly once")
        lines.remove(exact)
    review["notes"] = "\n".join(lines)


def _apply_selected_before(decision: dict[str, Any], moves: Any, page: int) -> None:
    """Apply the same exact selected-block reorder in validation and authoring."""
    if moves is None:
        return
    if not isinstance(moves, list):
        raise ValueError(f"page {page}: selected_before must be a list")
    for move in moves:
        legacy = {"raw_index", "before_raw_index"}
        qualified = legacy | {"view", "before_view"}
        if not isinstance(move, dict) or (set(move) != legacy and set(move) != qualified):
            raise ValueError(f"page {page}: selected-block reorder must have exact keys")
        if (any(type(move[key]) is not int for key in ("raw_index", "before_raw_index"))
                or (set(move) == qualified and any(not isinstance(move[key], str) or not move[key]
                                                   for key in ("view", "before_view")))):
            raise ValueError(f"page {page}: selected-block reorder source key is invalid")
        selected = decision["selected_blocks"]
        moving = [block for block in selected if block["raw_index"] == move["raw_index"]
                  and ("view" not in move or block.get("view") == move["view"])]
        targets = [block for block in selected if block["raw_index"] == move["before_raw_index"]
                   and ("before_view" not in move or block.get("view") == move["before_view"])]
        if len(moving) != 1 or len(targets) != 1 or moving[0] is targets[0]:
            raise ValueError(f"page {page}: selected-block reorder selector is not unique")
        selected.remove(moving[0])
        target_index = next(
            index for index, block in enumerate(selected)
            if block is targets[0]
        )
        selected.insert(target_index, moving[0])


def _materialize_reviewed_block_corrections(
    decision: dict[str, Any], packet: dict[str, Any], selectors: Any, page: int,
) -> None:
    """Bind page-spec corrections to one selected immutable packet block."""
    if selectors is None:
        return
    if not isinstance(selectors, list):
        raise ValueError(f"page {page}: reviewed_block_corrections must be a list")
    expected = {"view", "raw_index", "before", "after", "reason"}
    selected = {
        (row.get("view"), row.get("raw_index"))
        for row in decision.get("selected_blocks", [])
        if isinstance(row, dict) and row.get("purpose") != "asset"
    }
    blocks = {
        (view, block["raw_index"]): block
        for view, data in packet.get("views", {}).items()
        for block in data.get("blocks", [])
        if isinstance(block, dict) and type(block.get("raw_index")) is int
    }
    rows = []
    for selector in selectors:
        if not isinstance(selector, dict) or set(selector) != expected:
            raise ValueError(f"page {page}: reviewed block correction selector has invalid shape")
        key = (selector["view"], selector["raw_index"])
        block = blocks.get(key); text = block.get("text") if isinstance(block, dict) else None
        if key not in selected or not isinstance(text, str) or not text:
            raise ValueError(f"page {page}: reviewed block correction selector is not a selected text block")
        row = {**selector, "original_text_sha256": digest(text.encode("utf-8"))}
        rows.append(row)
    decision["reviewed_block_corrections"] = rows


def _materialize_linguistic_source_choice_corrections(
    decision: dict[str, Any], packet: dict[str, Any], selectors: Any, page: int,
    ledger_contexts: _AuthorLedgerContexts, owner: object,
) -> None:
    """Carry sealed translation-stage choices without claiming visual review."""
    if selectors is None:
        return
    if not isinstance(selectors, list):
        raise ValueError(f"page {page}: linguistic source choices must be a list")
    expected = {"ledger", "issue_id", "alternative_id", "view", "raw_index", "before", "after"}
    expected_v2 = {"ledger", "issue_id", "alternative_id", "view", "raw_index"}
    selected = {(row.get("view"), row.get("raw_index")) for row in decision.get("selected_blocks", [])
                if isinstance(row, dict) and row.get("purpose") != "asset"}
    blocks = {(view, block["raw_index"]): block for view, data in packet.get("views", {}).items()
              for block in data.get("blocks", []) if isinstance(block, dict) and type(block.get("raw_index")) is int}
    rows = []
    for selector in selectors:
        if not isinstance(selector, dict) or (set(selector) != expected and set(selector) != expected_v2):
            raise ValueError(f"page {page}: linguistic source choice selector has invalid shape")
        key = (selector["view"], selector["raw_index"]); block = blocks.get(key)
        text = block.get("text") if isinstance(block, dict) else None
        if key not in selected or not isinstance(text, str) or not text:
            raise ValueError(f"page {page}: linguistic source choice selector is not an exact selected text block")
        ledger = Path(selector["ledger"])
        if set(selector) == expected_v2:
            choice, queue_choice = ledger_contexts.lookup_v2(owner, ledger, selector["issue_id"])
            anchor_key = (choice.get("reader_anchor", {}).get("selected_source_key", {})
                          if isinstance(choice, Mapping) else {})
            if not anchor_key and isinstance(choice, Mapping):
                anchor_keys = choice.get("reader_anchor", {}).get("selected_source_keys", [])
                anchor_key = anchor_keys[0] if isinstance(anchor_keys, (list, tuple)) and len(anchor_keys) == 1 else {}
            if (choice is None or queue_choice is None or choice.get("alternative_id") != selector["alternative_id"]
                    or anchor_key.get("view") != key[0]
                    or anchor_key.get("raw_index") != key[1]):
                raise ValueError(f"page {page}: v2 linguistic source choice differs from ledger")
            rows.append({"authority": "linguistic_source_choice", "ledger": {"path": str(ledger.resolve()), **file_identity(ledger)},
                "issue_id": selector["issue_id"], "alternative_id": selector["alternative_id"], "view": key[0], "raw_index": key[1],
                "raw_text_sha256": digest(text.encode("utf-8")), "page_reader_span": _mutable_ledger_json(choice["r0_reader_span"]),
                "reader_anchor": _mutable_ledger_json(choice["reader_anchor"]), "reader_preimage": queue_choice["reader_projection"]["reader_text"],
                "reader_replacement": choice["intended_reader_successor"]["text"],
                "selected_raw_text_sha256": choice["chosen_raw_alternative"]["text_sha256"]})
            continue
        if text.count(selector["before"]) != 1:
            raise ValueError(f"page {page}: linguistic source choice selector is not an exact selected text block")
        rows.append({"authority": "linguistic_source_choice", "ledger": {"path": str(ledger.resolve()), **file_identity(ledger)},
                     "issue_id": selector["issue_id"], "alternative_id": selector["alternative_id"],
                     "view": selector["view"], "raw_index": selector["raw_index"], "before": selector["before"],
                     "after": selector["after"], "original_text_sha256": digest(text.encode("utf-8"))})
    decision["linguistic_source_choice_corrections"] = rows


def _materialize_reviewed_prose_bindings(
    decision: dict[str, Any], packet: dict[str, Any], selectors: Any,
    effective_markdown: str, page: int,
) -> None:
    """Derive sealed paragraph bindings from selectors after final rendering."""
    if selectors is None:
        return
    if not isinstance(selectors, list):
        raise ValueError(f"page {page}: reviewed prose bindings must be a list")
    expected = {"view", "raw_index", "markdown_span"}
    selected = {
        (row.get("view"), row.get("raw_index"))
        for row in decision.get("selected_blocks", [])
        if isinstance(row, dict) and row.get("purpose") != "asset"
    }
    blocks = {
        (view, block["raw_index"]): block
        for view, data in packet.get("views", {}).items()
        for block in data.get("blocks", [])
        if isinstance(block, dict) and type(block.get("raw_index")) is int
    }
    lines, rows, seen = effective_markdown.split("\n"), [], set()
    for selector in selectors:
        if not isinstance(selector, dict) or set(selector) not in (expected, expected | {"source_layout"}):
            raise ValueError(f"page {page}: reviewed prose binding selector has invalid shape")
        if "source_layout" in selector and selector["source_layout"] != "soft_wrapped_paragraph_v1":
            raise ValueError(f"page {page}: reviewed prose binding source layout is invalid")
        span = selector["markdown_span"]
        key = (selector["view"], selector["raw_index"])
        if (not isinstance(span, dict) or set(span) != {"start_line", "end_line"}
                or type(span.get("start_line")) is not int or type(span.get("end_line")) is not int
                or not 1 <= span["start_line"] <= span["end_line"] <= len(lines)
                or key in seen or key not in selected):
            raise ValueError(f"page {page}: reviewed prose binding selector is invalid or unselected")
        text = blocks.get(key, {}).get("text")
        if not isinstance(text, str) or not text:
            raise ValueError(f"page {page}: reviewed prose binding source block is absent")
        seen.add(key)
        rows.append({
            "view": key[0], "raw_index": key[1],
            "original_text_sha256": digest(text.encode("utf-8")),
            "markdown_span": {**span, "sha256": digest("\n".join(lines[span["start_line"] - 1:span["end_line"]]).encode("utf-8"))},
            **({"source_layout": selector["source_layout"]} if "source_layout" in selector else {}),
        })
    decision["reviewed_prose_bindings_v1"] = rows


def _derive_lexical_prose_bindings(
    decision: dict[str, Any], packet: dict[str, Any], effective: str,
    units: list[dict[str, Any]], page: int, *, collect_errors: bool = False,
) -> list[str]:
    """Bind only ledger-authorized whole ordinary paragraphs left without an owner."""
    from kb_creator.pipeline.reviewed_prose_binding import (
        ReviewedProseBindingError, _corrected_source, _single_plain_paragraph,
        _source_paragraph, _visible_page_paragraphs, _visible_prose_line,
        verify_reviewed_prose_bindings,
    )
    from kb_creator.pipeline.semantic_structure import reviewed_block_text_correction_candidates
    from kb_creator.pipeline.source_choice_successor import linguistic_choice_corrections

    blocks = {(view, block["raw_index"]): block for view, data in packet.get("views", {}).items()
              for block in data.get("blocks", []) if isinstance(block, dict) and type(block.get("raw_index")) is int}
    selected = {(row.get("view"), row.get("raw_index")) for row in decision.get("selected_blocks", [])
                if isinstance(row, dict) and row.get("purpose") != "asset"}
    candidates = reviewed_block_text_correction_candidates(decision, blocks, selected, page)
    linguistic = linguistic_choice_corrections(decision, blocks, selected, page)
    owned = {(source.get("view"), source.get("raw_index")) for unit in units
             for source in unit.get("source_blocks", []) if isinstance(source, dict)}
    explicit = decision.get("reviewed_prose_bindings_v1", [])
    if not isinstance(explicit, list):
        raise ValueError(f"page {page}: reviewed prose bindings must be a list")
    explicit_keys = {(row.get("view"), row.get("raw_index")) for row in explicit if isinstance(row, dict)}
    issues = {key: sorted(row.get("issue_id", "") for row in decision.get("linguistic_source_choice_corrections", [])
                          if isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key)
              for key in candidates}
    diagnostics: list[str] = []
    paragraphs: list[tuple[str, int, int]] | None = None
    for key in sorted(set(candidates) - owned - explicit_keys):
        label = f"page {page} key {key[0]}:{key[1]} issues {issues[key]}"
        if Counter(candidates[key]) != Counter(linguistic.get(key, [])):
            diagnostics.append(f"{label}: mixed visual/lexical or nonlexical correction requires reviewed owner")
            continue
        try:
            source = _source_paragraph(blocks[key].get("text"), None, page=page)
            corrected, _ = _corrected_source(source, candidates[key], page=page)
            corrected = _single_plain_paragraph(corrected, page=page, label="corrected source paragraph")
            if paragraphs is None:
                paragraphs = _visible_page_paragraphs(effective, page=page)
            matches = [(start, end) for text, start, end in paragraphs if text == corrected]
            if len(matches) != 1:
                raise ReviewedProseBindingError(
                    f"page {page}: corrected source requires exactly one complete visible paragraph; found {len(matches)}")
            start, end = matches[0]
            lines = effective.splitlines()
            if start != end or _visible_prose_line(lines[start - 1], page=page, label="reader paragraph") != corrected:
                raise ReviewedProseBindingError(f"page {page}: corrected source is not one plain reader line")
            row = {"view": key[0], "raw_index": key[1], "original_text_sha256": digest(source.encode("utf-8")),
                   "markdown_span": {"start_line": start, "end_line": end,
                                     "sha256": digest(lines[start - 1].encode("utf-8"))}}
            decision.setdefault("reviewed_prose_bindings_v1", []).append(row)
        except (ReviewedProseBindingError, KeyError, TypeError) as exc:
            diagnostics.append(f"{label}: {exc}")
    # Validate explicit rows even when no automatic row was needed.
    try:
        verify_reviewed_prose_bindings(decision, blocks, selected, effective, page,
                                       semantic_units=units, correction_candidates=candidates)
    except ReviewedProseBindingError as exc:
        if not collect_errors:
            raise
        diagnostics.append(str(exc))
    return diagnostics


def _materialize_reviewed_prose_roles(decision: dict[str, Any], packet: dict[str, Any], selectors: Any,
                                      effective_markdown: str, page: int, visual_inventory: dict[str, dict[str, Any]]) -> None:
    if selectors is None:
        return
    expected = {"role", "view", "raw_index", "markdown_span", "visual_reviewed", "rationale"}
    if not isinstance(selectors, list):
        raise ValueError(f"page {page}: reviewed prose roles must be a list")
    visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
    if visual_path not in visual_inventory:
        raise ValueError(f"page {page}: reviewed prose role visual is missing")
    lines, rows, seen = effective_markdown.split("\n"), [], set()
    selected = {(item.get("view"), item.get("raw_index")): item.get("purpose") for item in decision.get("selected_blocks", []) if isinstance(item, dict)}
    blocks = {(view, block.get("raw_index")): block for view, data in packet.get("views", {}).items() for block in data.get("blocks", []) if isinstance(block, dict)}
    for selector in selectors:
        if not isinstance(selector, dict) or set(selector) != expected or selector.get("role") != "ordinary_prose" or selector.get("visual_reviewed") is not True or not isinstance(selector.get("rationale"), str) or not selector["rationale"].strip():
            raise ValueError(f"page {page}: reviewed prose role selector is invalid")
        key = (selector.get("view"), selector.get("raw_index")); span = selector.get("markdown_span")
        block = blocks.get(key)
        if key in seen or selected.get(key) != "text" or not isinstance(block, dict) or block.get("type") != "text" or not isinstance(block.get("text"), str) or not block["text"] or not isinstance(span, dict) or set(span) != {"start_line", "end_line"} or not 1 <= span.get("start_line", 0) <= span.get("end_line", 0) <= len(lines):
            raise ValueError(f"page {page}: reviewed prose role selector is invalid or unselected")
        evidence = block.get("semantic_evidence", {})
        title_evidence = {name: evidence.get(name) if isinstance(evidence, dict) else None for name in ("text_level", "v2_title", "middle_title", "markdown_heading", "model_title")}
        if not any(title_evidence.values()):
            raise ValueError(f"page {page}: reviewed prose role source is not title-marked")
        seen.add(key)
        rows.append({"role": "ordinary_prose", "view": key[0], "raw_index": key[1], "selection_purpose": "text", "block_type": "text", "source_bbox": block.get("bbox"), "original_text_sha256": digest(block["text"].encode()), "title_evidence": title_evidence, "markdown_span": {**span, "sha256": digest("\n".join(lines[span["start_line"] - 1:span["end_line"]]).encode())}, "visual": {"path": visual_path, **visual_inventory[visual_path]}, "rationale": selector["rationale"]})
    decision["reviewed_prose_roles_v1"] = rows


def _canonicalize_line_groups(
    markdown: str, decision: dict[str, Any], packet: dict[str, Any],
    definitions: list[dict[str, Any]], page: int,
) -> str:
    """Render reviewed source-block sequences as canonical Markdown hard breaks."""
    groups = [
        definition for definition in definitions
        if definition.get("kind") == "line_group"
        or definition.get("representation") == "hard_break_lines"
    ]
    for definition in groups:
        if (
            definition.get("kind") != "line_group"
            or definition.get("representation") != "hard_break_lines"
        ):
            raise ValueError(f"page {page}: incomplete line-group kind/representation pair")
        view = definition.get("view", decision["overlay_preference"])
        blocks = {
            row["raw_index"]: row for row in packet["views"][view]["blocks"]
            if isinstance(row, dict) and type(row.get("raw_index")) is int
        }
        selected = {
            (row.get("view"), row.get("raw_index"))
            for row in decision.get("selected_blocks", []) if isinstance(row, dict)
        }
        raw_indices = definition.get("raw_indices")
        if (
            not isinstance(raw_indices, list) or not raw_indices
            or any(type(index) is not int for index in raw_indices)
            or len(set(raw_indices)) != len(raw_indices)
        ):
            raise ValueError(f"page {page}: line-group raw_indices must be a nonempty unique integer list")
        packet_blocks = {
            (view_id, block["raw_index"]): block
            for view_id, view_data in packet["views"].items()
            for block in view_data["blocks"]
            if isinstance(block, dict) and type(block.get("raw_index")) is int
        }
        corrections = reviewed_text_corrections(
            decision, packet_blocks, selected, markdown, page,
        )
        from kb_creator.pipeline.semantic_structure import reviewed_block_text_correction_candidates
        block_corrections = reviewed_block_text_correction_candidates(
            decision, packet_blocks, selected, page,
        )
        expected_lines: list[str] = []
        for raw_index in raw_indices:
            if raw_index not in blocks or (view, raw_index) not in selected:
                raise ValueError(f"page {page}: line-group source block is absent or unselected: {raw_index}")
            text = blocks[raw_index].get("text")
            if not isinstance(text, str) or not text:
                raise ValueError(f"page {page}: line-group source block has no text: {raw_index}")
            text = apply_reviewed_text_corrections(
                text, (view, raw_index), corrections, block_corrections,
            )
            source_lines = [display_text(line).rstrip(" \t") for line in text.splitlines()]
            if not source_lines or any(not line.strip() for line in source_lines):
                raise ValueError(f"page {page}: line-group source contains an empty line")
            expected_lines.extend(source_lines)
        if len(expected_lines) < 2:
            raise ValueError(f"page {page}: line-group requires at least two physical source lines")

        from kb_creator.pipeline.reviewed_line_group import canonicalize_reviewed_line_group
        markdown = canonicalize_reviewed_line_group(markdown, expected_lines)
    return markdown


def _canonicalize_blank_separators(
    markdown: str, declarations: list[dict[str, Any]], page: int,
) -> str:
    """Replace only explicitly reviewed multi-blank separators with one blank."""
    if not isinstance(declarations, list):
        raise ValueError(f"blank_separator_declaration_invalid: page {page}: declarations must be a list")
    lines = markdown.split("\n")
    replacements: list[tuple[int, int]] = []
    selectors: set[tuple[str, str]] = set()
    for declaration in declarations:
        if not isinstance(declaration, dict) or set(declaration) != {"before_line", "after_line", "expected_blank_lines"}:
            raise ValueError(f"blank_separator_declaration_invalid: page {page}: declaration must have exact keys")
        before, after, expected = (
            declaration["before_line"], declaration["after_line"], declaration["expected_blank_lines"],
        )
        if (
            not isinstance(before, str) or not before or "\n" in before
            or not isinstance(after, str) or not after or "\n" in after
            or type(expected) is not int or expected < 2
            or (before, after) in selectors
        ):
            raise ValueError(f"blank_separator_declaration_invalid: page {page}: invalid or duplicate declaration")
        selectors.add((before, after))
        matches = [
            index for index in range(len(lines))
            if lines[index] == before
            and index + expected + 1 < len(lines)
            and all(lines[cursor] == "" for cursor in range(index + 1, index + expected + 1))
            and lines[index + expected + 1] == after
        ]
        if len(matches) != 1:
            raise ValueError(f"blank_separator_selector_mismatch: page {page}: selector must match exactly once")
        replacements.append((matches[0] + 1, expected))
    occupied: set[int] = set()
    for start, length in replacements:
        interval = set(range(start, start + length))
        if occupied & interval:
            raise ValueError(f"blank_separator_declaration_overlap: page {page}: declarations overlap")
        occupied.update(interval)
    for start, length in sorted(replacements, reverse=True):
        lines[start:start + length] = [""]
    return "\n".join(lines)


def _render_reviewed_markdown(
    decision: dict[str, Any], packet: dict[str, Any], row: dict[str, Any], page: int,
) -> tuple[str, str]:
    """Return stored and effective Markdown through one author/validate path."""
    stored = _patch_markdown(decision["markdown"], row.get("patches", []), page)
    stored = _apply_review_rules(stored, decision, packet, row.get("rules", {}), page)
    stored = _patch_markdown(stored, row.get("post_patches", []), page)
    v2 = [item for item in decision.get("linguistic_source_choice_corrections", [])
          if isinstance(item, dict) and "page_reader_span" in item]
    if v2:
        from kb_creator.pipeline.reader_occurrence_projection import apply_bound_reader_replacements
        stored, _ = apply_bound_reader_replacements(stored, [
            {"page_reader_span": item["page_reader_span"], "before": item["reader_preimage"], "after": item["reader_replacement"]}
            for item in v2])
    # Structural edits deliberately see the final v2 reader wording.  They are
    # exact reviewed patches, not a parser or a list-recognition fallback.
    stored = _patch_markdown(stored, row.get("structural_post_patches", []), page)
    stored = _canonicalize_line_groups(stored, decision, packet, row.get("units", []), page)
    stored = _canonicalize_blank_separators(stored, row.get("rules", {}).get("blank_separators", []), page)
    return stored, apply_block_boundaries(stored, decision.get("block_boundaries"))


def _apply_asset_placements(decision: dict[str, Any], placements: Any, page: int) -> None:
    """Apply exact reviewed asset placement selectors to one decision."""
    if placements is None:
        return
    if not isinstance(placements, dict):
        raise ValueError(f"page {page}: asset placements must be an object")
    assets = decision.get("assets", [])
    if not isinstance(assets, list):
        raise ValueError(f"page {page}: decision assets must be a list")
    for logical_name, placement in placements.items():
        if not isinstance(logical_name, str) or not logical_name:
            raise ValueError(f"page {page}: asset placement logical name is invalid")
        if not isinstance(placement, str) or not placement:
            raise ValueError(f"page {page}: asset placement value is invalid")
        matches = [asset for asset in assets if isinstance(asset, dict) and asset.get("logical_name") == logical_name]
        if len(matches) != 1:
            raise ValueError(f"page {page}: asset placement selector is invalid or ambiguous: {logical_name!r}")
        matches[0]["placement"] = placement


def _apply_review_rules(markdown: str, decision: dict[str, Any], packet: dict[str, Any], rules: dict[str, Any], page: int) -> str:
    blocks = {row["raw_index"]: row for row in packet["views"][decision["overlay_preference"]]["blocks"]}
    for heading in rules.get("headings", []):
        text = blocks[heading["raw_index"]]["text"]
        candidates = [line for line in markdown.split("\n") if line.strip("# ") in {text, display_text(text)}]
        if len(candidates) != 1:
            raise ValueError(f"page {page}: heading source block is not unique: {text!r}")
        markdown = markdown.replace(candidates[0], "#" * heading["level"] + " " + text, 1)
    for raw_index in rules.get("unordered_list", []):
        text = blocks[raw_index]["text"]
        item = __import__("re").sub(r"^(?:[•*+-]|\\-)[ \t]*", "", text)
        markdown = _replace_source_text(markdown, text, "- " + display_text(item), page)
    for group in rules.get("blockquote_groups", []):
        start_text = group.get("start_selector", display_text(blocks[group["start"]]["text"].split("\n", 1)[0]))
        end_text = group.get("end_selector", display_text(blocks[group["end"]]["text"].split("\n")[-1]))
        lines = markdown.split("\n")
        starts = [i for i, line in enumerate(lines) if (line == start_text if group.get("start_match") == "exact" else start_text in line)]
        if len(starts) != 1:
            raise ValueError(f"page {page}: quote start is not unique: {start_text!r}")
        start = starts[0]
        ends = [i for i in range(start, len(lines)) if end_text in lines[i]]
        if len(ends) != 1:
            raise ValueError(f"page {page}: quote end is not unique: {end_text!r}")
        end = ends[0]
        for index in range(start, end + 1):
            if lines[index] and not lines[index].startswith(">"):
                lines[index] = "> " + lines[index]
            elif not lines[index]:
                lines[index] = ">"
        markdown = "\n".join(lines)
    for group in rules.get("statblocks", []):
        for raw_index in group["raw_indices"]:
            block = blocks[raw_index]
            if block.get("type") == "table":
                asset_paths = block.get("assets", [])
                asset = next((row for row in decision.get("assets", []) if row.get("source_path") in asset_paths), None)
                if asset is None:
                    raise ValueError(f"page {page}: table block has no selected asset: {raw_index}")
                placeholder = f"{{{{asset:{asset['logical_name']}}}}}"
                markdown = markdown.replace(f"![Source visual from page {page}]({placeholder})", "", 1)
                asset["placement"] = "reference_only"
        lines = markdown.split("\n")
        start_selector = group["start_selector"]
        end_selector = group["end_selector"]
        starts = [i for i, line in enumerate(lines) if start_selector in line]
        if len(starts) != 1:
            raise ValueError(f"page {page}: statblock start is not unique: {start_selector!r}")
        start = starts[0]
        ends = [
            i for i in range(start, len(lines))
            if (lines[i] == end_selector if group.get("end_match") == "exact" else end_selector in lines[i])
        ]
        if len(ends) != 1:
            raise ValueError(f"page {page}: statblock end is not unique: {end_selector!r}")
        block_lines: list[str] = []
        for raw_index in group["raw_indices"]:
            text = display_text(blocks[raw_index].get("text", ""))
            if text:
                block_lines.extend("> " + line if line else ">" for line in text.split("\n"))
        lines[start:ends[0] + 1] = block_lines
        markdown = "\n".join(lines)
    return markdown


def _author_with_ledger_contexts(run_root: Path, baseline_root: Path, destination: Path, spec_paths: list[Path], *,
                                 preview_root: Path | None, ledger_contexts: _AuthorLedgerContexts, owner: object) -> dict[str, Any]:
    raw_specs = [json.loads(path.read_text(encoding="utf-8")) for path in spec_paths]
    try:
        source_marker_inputs = load_bound_inputs(spec_paths)
    except SourceMarkerDispositionError as exc:
        raise ValueError(f"invalid source_marker_dispositions input: {exc}") from exc
    _validate_ocr_selector_domain(run_root, [item for value in raw_specs for item in value.get("ocr_equivalence_classes", [])])
    _validate_ocr_support_membership(raw_specs)
    spec = _load_spec_fragments(spec_paths)
    queue_path = run_root / "review/review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    baseline_set = json.loads((baseline_root / "decision_set.json").read_text(encoding="utf-8"))
    allowlist_source = baseline_root / baseline_set["reviewed_allowlist"]["path"]
    allowlist = json.loads(allowlist_source.read_text(encoding="utf-8"))
    _validate_ocr_selector_domain(run_root, allowlist.get("ocr_equivalence_classes"))
    if spec["text_segmentation_claims"]:
        allowlist["text_segmentation_claims"] = []
    visual_inventory = _visual_inventory(run_root)
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    comparison = json.loads((run_root / "outputs/03-compare-views/comparison.json").read_text(encoding="utf-8"))
    geometry = json.loads((run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_root / "outputs/04-visual-merge-bundle/visual/visual_manifest.json").read_text(encoding="utf-8"))
    bridge_path = run_root / "replay/bridge.json"
    if not bridge_path.is_file():
        raise ValueError("fresh run has no replay/bridge.json; reviewed-allowlist v3 requires a replay bridge SHA256. Create/use a fresh replay root before decision-set materialization.")
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    allowlist["authority"] = {
        "run_identity_sha256": run["portable_identity_sha256"], "bridge_sha256": bridge["bridge_sha256"],
        "review_queue_sha256": queue["queue_sha256"], "comparison_sha256": comparison["comparison_sha256"],
        "geometry_plan_sha256": geometry["plan_sha256"], "visual_manifest_sha256": manifest["manifest_sha256"],
    }
    # Refresh all visual records from the new replay. Their paths stay relative
    # to Stage04 and each hash is bound to the fresh visual bytes.
    def refresh_visuals(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("visual", "source_visual"):
                value = node.get(key)
                if isinstance(value, dict) and isinstance(value.get("path"), str):
                    full = value["path"]
                    if full in visual_inventory:
                        value.update(visual_inventory[full])
            if {"source_page", "view_id", "raw_index"}.issubset(node):
                try:
                    fresh = _packet_unit(run_root, node["source_page"], node["view_id"], node["raw_index"])
                    if set(node) == set(fresh):
                        node.update(fresh)
                except (StopIteration, KeyError):
                    pass
            for child in node.values(): refresh_visuals(child)
        elif isinstance(node, list):
            for child in node: refresh_visuals(child)
    refresh_visuals(allowlist)
    expected_pages = {row["source_page"] for row in queue["items"]}
    entries = {int(row["source_page"]): row for row in spec["pages"]}
    if set(entries) != expected_pages:
        raise ValueError("spec must contain exactly one reviewed record for every fresh replay page")
    destination.mkdir(parents=True, exist_ok=False)
    records = []
    profile = spec["semantic_structure_profile"]
    for page in sorted(expected_pages):
        source = json.loads((baseline_root / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        row = entries[page]
        from kb_creator.pipeline.empty_text_assertions import select_empty_sources
        select_empty_sources(source, packet, row.get("empty_source_selections"), page)
        for override in row.get("selected_purposes", []):
            matches = [
                block for block in source["selected_blocks"]
                if block["view"] == override.get("view", source["overlay_preference"])
                and block["raw_index"] == override["raw_index"]
            ]
            if len(matches) != 1 or override["purpose"] not in {"text", "asset", "structure", "visual"}:
                raise ValueError(f"page {page}: selected-purpose selector is invalid or ambiguous")
            matches[0]["purpose"] = override["purpose"]
        _remove_review_notes(source, row.get("review_notes_remove"), page)
        _append_review_notes(source, row.get("review_notes_append"), page)
        _apply_selected_before(source, row.get("selected_before"), page)
        _materialize_reviewed_block_corrections(source, packet, row.get("reviewed_block_corrections"), page)
        _materialize_linguistic_source_choice_corrections(source, packet, row.get("linguistic_source_choice_corrections"), page, ledger_contexts, owner)
        source["markdown"], effective = _render_reviewed_markdown(source, packet, row, page)
        _materialize_reviewed_prose_bindings(source, packet, row.get("reviewed_prose_bindings_v1"), effective, page)
        _materialize_reviewed_prose_roles(source, packet, row.get("reviewed_prose_roles_v1"), effective, page, visual_inventory)
        selector = row.get("source_page_render")
        if selector is not None:
            page_preview_root = preview_root if preview_root is not None else run_root / "review" / "source-page-render-previews"
            source.setdefault("assets", []).append(
                _derive_source_page_render(run_root, geometry, page, selector, page_preview_root)
            )
        _apply_asset_placements(source, row.get("asset_placements"), page)
        lines = effective.split("\n")
        units = []
        definitions = _unit_definitions(row, source, page)
        definition_row = {**row, "units": definitions}
        shared_sources = _shared_unit_sources(definition_row, source["overlay_preference"])
        for definition in definitions:
            start, end = _definition_span(lines, definition, page)
            span_text = "\n".join(lines[start - 1:end])
            unit = {
                "id": definition["id"], "kind": definition["kind"],
                "representation": definition["representation"],
                "source_blocks": [{"view": definition.get("view") or source["overlay_preference"], "raw_index": index} for index in definition["raw_indices"]],
                "markdown_span": {"start_line": start, "end_line": end, "sha256": digest(span_text.encode("utf-8"))},
                "container_parent": definition.get("container_parent"),
                "semantic_parent": definition.get("semantic_parent"),
                "continuation_of": definition.get("continuation_of"),
                "heading_level": definition.get("heading_level"),
                "item_count": definition.get("item_count"),
            }
            if profile == PROFILE_V2:
                unit["source_fragments"] = [] if definition.get("visual_assertion_ids") is not None else _source_fragments(packet, definition, source["overlay_preference"], page, shared_sources)
                if "visual_assertion_ids" in definition:
                    ids = definition["visual_assertion_ids"]
                    if not isinstance(ids, list) or len(ids) != len(set(ids)) or any(not isinstance(value, str) or not value for value in ids):
                        raise ValueError(f"page {page}: visual_assertion_ids must be a unique nonempty-id list")
                    unit["visual_assertion_ids"] = ids
            units.append(unit)
        lexical_diagnostics = _derive_lexical_prose_bindings(source, packet, effective, units, page)
        if lexical_diagnostics:
            raise ValueError("lexical prose binding preflight failed:\n" + "\n".join(lexical_diagnostics))
        visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
        if visual_path not in visual_inventory:
            raise ValueError(f"page {page}: exact Stage04 page visual is absent from visual manifest")
        source["semantic_structure"] = (
            {"schema": SCHEMA, "review": {"state": "complete", "visual": {"path": visual_path, **visual_inventory[visual_path]}}, "units": units}
            if profile == PROFILE else
            {"schema": SCHEMA_V2, "profile": PROFILE_V2, "role_contract": row.get("role_contract"), "review": {"state": "complete", "visual": {"path": visual_path, **visual_inventory[visual_path]}}, "units": units}
        )
        decision_path = destination / f"pages/page-{page:03d}.json"
        write_json(decision_path, source)
        records.append({"source_page": page, "path": f"pages/page-{page:03d}.json", **identity(decision_path)})
    # Assertion records are supplied as source facts in the scenario spec;
    # this helper resolves visual identity and calculates all content hashes.
    for assertion in spec.get("visual_text_assertions", []):
        assertion = dict(assertion)
        page = assertion["source_page"]
        from kb_creator.pipeline.empty_text_assertions import RELATION as EMPTY_TEXT_RELATION, author_assertion
        if assertion.get("relation") == EMPTY_TEXT_RELATION:
            decision = json.loads((destination / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            allowlist["visual_text_assertions"].append(author_assertion(assertion, packet, decision, visual_inventory))
            continue
        visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
        text = assertion["text"]
        normalized = _normalized(text)
        assertion["original_text_sha256"] = digest(text.encode("utf-8"))
        assertion["normalized_text_sha256"] = digest(normalized.encode("utf-8"))
        assertion["visual"] = {"path": visual_path, **visual_inventory[visual_path]}
        relation = assertion["relation"]
        if relation == "within_selected_asset_region":
            selector = assertion.pop("asset", None)
            if not isinstance(selector, dict) or set(selector) != {"view_id", "raw_index", "logical_name", "source_path"}:
                raise ValueError(f"page {page}: asset assertion selector is invalid")
            asset_block = _packet_asset_block(run_root, page, selector["view_id"], selector["raw_index"], selector["source_path"])
            decision = json.loads((destination / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            selected = [row for row in decision["selected_blocks"] if row.get("view") == selector["view_id"] and row.get("raw_index") == selector["raw_index"] and row.get("purpose") == "asset"]
            assets = [row for row in decision.get("assets", []) if row.get("view") == selector["view_id"] and row.get("source_path") == selector["source_path"] and row.get("logical_name") == selector["logical_name"]]
            if len(selected) != 1 or len(assets) != 1:
                raise ValueError(f"page {page}: asset assertion must bind one selected asset-purpose decision asset")
            from kb_creator.pipeline.reconstruction_asset_inventory import exact_selected_asset_path
            asset_path = exact_selected_asset_path(visual_inventory, selector["view_id"], selector["source_path"])
            rendered = _normalized_reader_markdown(decision["markdown"])
            start = rendered.find(normalized)
            if start < 0 or rendered.find(normalized, start + 1) >= 0:
                raise ValueError(f"page {page}: asset assertion text must occur exactly once in normalized Markdown")
            assertion["source_region"] = {"view_id": selector["view_id"], "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": assertion.pop("bbox")}
            assertion["placement"] = {"relation": relation, "asset_block": asset_block, "logical_name": selector["logical_name"], "asset": {"path": asset_path, **visual_inventory[asset_path]}, "markdown_span": {"start": start, "end": start + len(normalized), "sha256": digest(normalized.encode("utf-8"))}}
            assertion.pop("relation", None)
        else:
            anchor = _packet_unit(run_root, page, assertion["anchor"]["view_id"], assertion["anchor"]["raw_index"])
            assertion["source_region"] = {"view_id": anchor["view_id"], "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": assertion.pop("bbox")}
            anchor_text = _packet_text(run_root, page, anchor["view_id"], anchor["raw_index"])
            pair = (_normalized(anchor_text) + _normalized(text)) if relation in {"after_anchor", "column_after_anchor"} else (_normalized(text) + _normalized(anchor_text))
            assertion["placement"] = {"relation": relation, "anchor_unit": anchor, "expected_pair_sha256": digest(pair.encode())}
            for key in ("anchor", "relation"):
                assertion.pop(key, None)
        assertion["visual_verdict"] = "source_text_visible_at_region"
        allowlist["visual_text_assertions"].append(assertion)
    for exclusion in spec.get("source_text_exclusions", []):
        exclusion = dict(exclusion)
        page = exclusion.pop("source_page")
        view = exclusion.pop("view_id")
        raw_index = exclusion.pop("raw_index")
        visual_path = exclusion.pop(
            "visual_path",
            f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png",
        )
        if visual_path not in visual_inventory:
            raise ValueError(f"page {page}: exclusion visual is absent from fresh replay")
        allowlist["source_text_exclusions"].append({
            "unit": _packet_unit(run_root, page, view, raw_index),
            "visual": {"path": visual_path, **visual_inventory[visual_path]},
            **exclusion,
        })
    # OCR-equivalence source identities stay immutable, while a reviewed
    # source-to-reader correction changes the canonical proof text. Rebind
    # only affected reviewed proofs to the final Markdown form.
    assertions_by_id = {
        row["assertion_id"]: row for row in allowlist["visual_text_assertions"]
        if isinstance(row, dict) and isinstance(row.get("assertion_id"), str)
    }
    for ocr_class in allowlist["ocr_equivalence_classes"]:
        proof = ocr_class.get("canonical_proof") if isinstance(ocr_class, dict) else None
        canonical = ocr_class.get("canonical_unit") if isinstance(ocr_class, dict) else None
        if not isinstance(proof, dict) or not isinstance(canonical, dict):
            continue
        page = canonical["source_page"]
        decision = json.loads((destination / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        packet_blocks = {
            (view_id, block["raw_index"]): block
            for view_id, view in packet["views"].items()
            for block in view["blocks"]
            if isinstance(block, dict) and type(block.get("raw_index")) is int
        }
        selected = {
            (row["view"], row["raw_index"]) for row in decision["selected_blocks"]
            if isinstance(row, dict) and isinstance(row.get("view"), str) and type(row.get("raw_index")) is int
        }
        corrections = reviewed_text_corrections(
            decision, packet_blocks, selected, decision["markdown"], page,
        )
        block_corrections = reviewed_block_text_corrections(
            decision, packet_blocks, selected, decision["markdown"], page,
        )
        key = (canonical["view_id"], canonical["raw_index"])
        source_text = str(packet_blocks[key].get("text", ""))
        corrected_text = apply_reviewed_text_corrections(
            source_text, key, corrections, block_corrections,
        )
        if corrected_text == source_text:
            continue
        supporting = []
        for assertion_id in proof["supporting_assertion_ids"]:
            assertion = assertions_by_id.get(assertion_id)
            if assertion is None:
                raise ValueError(f"page {page}: corrected OCR proof names an absent visual assertion")
            supporting.append(assertion)
        proof["expected_normalized_sha256"] = digest(_canonical_assertion_proof(corrected_text, supporting).encode("utf-8"))
    if spec["text_segmentation_claims"]:
        from kb_creator.pipeline.text_segmentation import derive_claim
        from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _public_unit, _v3_page_context
        for selector in spec["text_segmentation_claims"]:
            page = selector.get("source_page") if isinstance(selector, dict) else None
            if type(page) is not int:
                raise ValueError("text segmentation selector has no source page")
            packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            decision = json.loads((destination / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            errors: list[str] = []
            context = _v3_page_context(page, packet, decision, geometry, errors)
            if errors:
                raise ValueError("text segmentation selected proof is not monotonic: " + "; ".join(errors))
            references = {(page, view, index): unit for (view, index), unit in context["references"].items()}
            mappings = {(page, row["unit"]["view_id"], row["unit"]["raw_index"]): row for row in context["mappings"]}
            visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
            allowlist["text_segmentation_claims"].append(derive_claim(selector, references=references, selected_mappings=mappings, reader_text=context["rendered"], source_visual={"path": visual_path, **visual_inventory[visual_path]}, normalize=_normalized))
    if source_marker_inputs:
        authored_decisions = {
            page: json.loads((destination / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            for page in expected_pages
        }
        authored_packets = {
            page: json.loads((run_root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-{:03d}.json".format(page)).read_text(encoding="utf-8"))
            for page in expected_pages
        }
        try:
            validate_source_marker_dispositions(
                source_marker_inputs, authored_decisions, authored_packets,
            )
        except SourceMarkerDispositionError as exc:
            raise ValueError(f"source_marker_dispositions validation failed: {exc}") from exc
    write_json(destination / "reviewed_allowlist.v3.json", allowlist)
    set_data = {
        "schema": "kb_creator.reconstruction_decision_set.v2",
        "review_queue_sha256": queue["queue_sha256"],
        "contract_sha256": queue["contract_sha256"],
        "source_sha256": queue["source_sha256"],
        "decisions": records,
        "reviewed_allowlist": {"path": "reviewed_allowlist.v3.json", **identity(destination / "reviewed_allowlist.v3.json")},
        "semantic_structure_profile": profile,
        "submission_state": "submitted_for_validation",
    }
    write_json(destination / "decision_set.json", set_data)
    return set_data


def author(run_root: Path, baseline_root: Path, destination: Path, spec_paths: list[Path], *, preview_root: Path | None = None) -> dict[str, Any]:
    destination = Path(destination)
    if destination.exists():
        raise ValueError("author destination already exists")
    stage = destination.parent / f".{destination.name}.author-staging"
    if stage.exists():
        raise ValueError("author staging destination already exists")
    owner = object()
    ledger_contexts = _AuthorLedgerContexts(owner)
    try:
        staged_preview = (stage / Path(preview_root).relative_to(destination)
                          if preview_root is not None and Path(preview_root).is_relative_to(destination)
                          else preview_root)
        with _author_ledger_snapshot_scope(lambda path: ledger_contexts.snapshot_v2(owner, path)):
            result = _author_with_ledger_contexts(run_root, baseline_root, stage, spec_paths,
                preview_root=staged_preview, ledger_contexts=ledger_contexts, owner=owner)
            ledger_contexts.reverify_before_publish(owner)
        stage.replace(destination)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _author_final_candidate(
    run_root: Path, candidate_root: Path, output: Path, spec_paths: list[Path], draft_input: Path,
    ledger_contexts: _AuthorLedgerContexts, owner: object,
) -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    """Copy verified final pages and add only freshly derived source renders.

    Regeneration exists solely to derive post-decision authority and prove the
    permitted render delta.  Candidate prose and review state are copied from
    the sealed page bytes; they are never regenerated into the published set.
    """
    verified = validate_final_candidate(run_root, candidate_root, spec_paths, draft_input)
    manifest = json.loads((candidate_root / "candidate_manifest.json").read_text(encoding="utf-8"))
    baseline_root = _manifest_path(manifest["inputs"]["baseline"]["path"], label="raw baseline")
    regenerated = output.parent / ".final-candidate-regenerated"
    author_baseline = output.parent / ".final-candidate-raw-baseline"
    if regenerated.exists() or author_baseline.exists():
        raise ValueError("final candidate regenerated staging destination already exists")
    try:
        for page in verified["pages"]:
            source = baseline_root / "pages" / f"page-{page:03d}.json"
            target = author_baseline / "pages" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        write_json(author_baseline / "reviewed_allowlist.v3.json", {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []})
        write_json(author_baseline / "decision_set.json", {"reviewed_allowlist": {"path": "reviewed_allowlist.v3.json"}})
        regenerated_set = _author_with_ledger_contexts(run_root, author_baseline, regenerated, spec_paths,
            preview_root=regenerated / "source-page-render-previews", ledger_contexts=ledger_contexts, owner=owner)
        decisions: dict[int, dict[str, Any]] = {}
        for page, sealed in verified["pages"].items():
            generated = json.loads((regenerated / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
            additions = [asset for asset in generated.get("assets", []) if isinstance(asset, dict) and asset.get("origin") == "source_pdf_page_render_v1"]
            without_additions = copy.deepcopy(generated)
            without_additions["assets"] = [asset for asset in without_additions.get("assets", []) if not (isinstance(asset, dict) and asset.get("origin") == "source_pdf_page_render_v1")]
            if without_additions != sealed:
                raise ValueError(f"final candidate page {page} has a non-render regeneration difference")
            decision = copy.deepcopy(sealed)
            if additions:
                decision.setdefault("assets", []).extend(additions)
            decisions[page] = decision
            write_json(output / f"pages/page-{page:03d}.json", decision)
        shutil.copy2(regenerated / "reviewed_allowlist.v3.json", output / "reviewed_allowlist.v3.json")
        set_data = copy.deepcopy(regenerated_set)
        set_data["decisions"] = [
            {"source_page": page, "path": f"pages/page-{page:03d}.json", **identity(output / f"pages/page-{page:03d}.json")}
            for page in sorted(decisions)
        ]
        set_data["reviewed_allowlist"] = {"path": "reviewed_allowlist.v3.json", **identity(output / "reviewed_allowlist.v3.json")}
        write_json(output / "decision_set.json", set_data)
        return set_data, decisions
    finally:
        if regenerated.exists():
            shutil.rmtree(regenerated)
        if author_baseline.exists():
            shutil.rmtree(author_baseline)


def _write_validated_candidate(
    destination: Path, run_root: Path, baseline_root: Path, spec_paths: list[Path],
    decisions: Mapping[int, Mapping[str, Any]], report: Mapping[str, Any],
) -> dict[str, Any]:
    """Save already-validated decisions as a pending candidate, never an acceptance set."""
    if destination.exists():
        raise ValueError("candidate output destination already exists")
    stage = destination.parent / f".{destination.name}.candidate-staging"
    if stage.exists():
        raise ValueError("candidate output staging destination already exists")
    queue_path = run_root / "review/review_queue.json"
    run_path = run_root / "run.json"
    if not queue_path.is_file() or not run_path.is_file():
        raise ValueError("candidate output requires run and review queue identities")
    baseline_pages = [baseline_root / f"pages/page-{page:03d}.json" for page in sorted(decisions)]
    if any(not path.is_file() for path in baseline_pages):
        raise ValueError("candidate output baseline page is missing")
    run = json.loads(run_path.read_text(encoding="utf-8"))
    source = _candidate_source_identity(run)
    incomplete = {
        "schema": "kb_creator.validated_draft_candidate.v1",
        "state": "incomplete_candidate_output",
        "scope": "candidate_only",
        "acceptance": "pending",
    }
    stage.mkdir(parents=True)
    write_json(stage / "candidate_manifest.json", incomplete)
    records = []
    for page, decision in sorted(decisions.items()):
        path = stage / f"pages/page-{page:03d}.json"
        write_json(path, decision)
        records.append({"source_page": page, "path": f"pages/page-{page:03d}.json", **identity(path)})
    manifest = {
            "schema": "kb_creator.validated_draft_candidate.v1",
            "state": "validated_candidate_only",
            "scope": "candidate_only",
            "acceptance": "pending",
            "validation": dict(report),
            "inputs": {
                "source": source,
                "run": {"path": str(run_path), **identity(run_path), "portable_identity_sha256": run.get("portable_identity_sha256")},
                "review_queue": {"path": "review/review_queue.json", **identity(queue_path)},
                "baseline": {"path": str(baseline_root), "pages": [{"path": str(path.relative_to(baseline_root)), **identity(path)} for path in baseline_pages]},
                "specs": [{"path": str(path), **identity(path)} for path in spec_paths],
                "code": {"path": "kb_creator/scripts/author_reviewed_semantic_decisions.py", **identity(Path(__file__))},
            },
            "pages": records,
        }
    # Keep the staging marker incomplete until the directory is published.
    # A rename failure therefore leaves explicit failure evidence instead of a
    # success-state manifest in a path that was never published.
    stage.replace(destination)
    write_json(destination / "candidate_manifest.json", manifest)
    return {"path": str(destination), **identity(destination / "candidate_manifest.json")}


def _candidate_source_identity(run: Mapping[str, Any]) -> dict[str, Any]:
    """Read the source identity from the supported nested run envelopes."""
    supported = {"kb_creator.run_spec.v2", "kb_creator.run_spec.v3", "kb_creator.run_spec.v4"}
    if not isinstance(run, Mapping) or run.get("schema") not in supported:
        raise ValueError("candidate output has unsupported run envelope")
    source = run.get("source")
    if not isinstance(source, Mapping) or not {"sha256", "bytes"}.issubset(source):
        raise ValueError("candidate output run source identity is missing")
    sha256, size = source.get("sha256"), source.get("bytes")
    if not isinstance(sha256, str) or not re.fullmatch(r"[0-9A-F]{64}", sha256) or type(size) is not int or size < 1:
        raise ValueError("candidate output run source identity is invalid")
    if "source_sha256" in run:
        raise ValueError("candidate output run has contradictory unsupported source identity")
    return {"sha256": sha256, "bytes": size, "path_hint": source.get("path_hint")}


def _reject_overlapping_selected_asset_assertions(assertions: list[Any]) -> None:
    """Fail early when two text regions claim the same selected asset pixels."""
    by_asset: dict[tuple[Any, ...], list[tuple[str, list[Any]]]] = {}
    for assertion in assertions:
        if not isinstance(assertion, dict) or assertion.get("relation") != "within_selected_asset_region":
            continue
        asset, bbox = assertion.get("asset"), assertion.get("bbox")
        if (not isinstance(asset, dict) or not isinstance(bbox, list) or len(bbox) != 4
                or not isinstance(assertion.get("source_page"), int)
                or not isinstance(assertion.get("assertion_id"), str)):
            # Closed-shape validation below owns malformed-selector diagnostics.
            continue
        # This is the preflight representation of the auditor's asset_block:
        # a logical name describes placement, while the selected source asset
        # is fixed by its page, view, raw block and source path.
        identity = (assertion["source_page"], asset.get("view_id"), asset.get("raw_index"),
                    asset.get("source_path"))
        for other_id, other_bbox in by_asset.setdefault(identity, []):
            if not (bbox[2] <= other_bbox[0] or other_bbox[2] <= bbox[0]
                    or bbox[3] <= other_bbox[1] or other_bbox[3] <= bbox[1]):
                raise ValueError(
                    f"page {assertion['source_page']}: overlapping selected asset regions "
                    f"{assertion['assertion_id']} and {other_id}"
                )
        by_asset[identity].append((assertion["assertion_id"], bbox))


def _require_bound_cold_inputs(review_input: dict[str, Any], binding_root: Path,
                               draft_pages: Path, spec_paths: list[Path], pages: list[int]) -> None:
    bindings = review_input["bindings"]
    for page in pages:
        name = (f"source_choice_successor_page-{page:03d}"
                if f"source_choice_successor_page-{page:03d}" in bindings else f"draft_page-{page:03d}")
        record = bindings.get(name)
        if record is None or (binding_root / record["path"]).resolve() != (draft_pages / f"page-{page:03d}.json").resolve():
            raise ValueError(f"sealed draft page {page} differs from bound input path")
    prefix = ("source_choice_successor_spec-" if any(
        name.startswith("source_choice_successor_spec-") for name in bindings) else "input_")
    bound_specs = {(binding_root / record["path"]).resolve() for name, record in bindings.items()
                   if name.startswith(prefix)}
    if len(spec_paths) != len(bound_specs) or {path.resolve() for path in spec_paths} != bound_specs:
        raise ValueError("sealed semantic spec paths differ from bound input")


def validate_spec(
    run_root: Path, baseline_root: Path | None, spec_paths: list[Path], *,
    candidate_output: Path | None = None, draft_pages: Path | None = None,
    draft_input: Path | None = None, binding_root: Path | None = None,
) -> dict[str, Any]:
    """Check every bounded page selector against fresh packets and baseline text."""
    if (baseline_root is None) == (draft_pages is None):
        raise ValueError("validate_spec requires exactly one baseline or sealed draft-pages input")
    if draft_pages is not None and (draft_input is None or binding_root is None or candidate_output is not None):
        raise ValueError("sealed draft preflight requires draft input and binding root, without candidate output")
    owner = object()
    ledger_contexts = _AuthorLedgerContexts(owner)
    with _author_ledger_snapshot_scope(lambda path: ledger_contexts.snapshot_v2(owner, path)):
        result = _validate_spec_with_ledger_contexts(run_root, baseline_root, spec_paths,
            candidate_output=candidate_output, draft_pages=draft_pages, draft_input=draft_input,
            binding_root=binding_root, ledger_contexts=ledger_contexts, owner=owner)
    return result


def _validate_spec_with_ledger_contexts(
    run_root: Path, baseline_root: Path | None, spec_paths: list[Path], *, candidate_output: Path | None,
    draft_pages: Path | None = None, draft_input: Path | None = None, binding_root: Path | None = None,
    ledger_contexts: _AuthorLedgerContexts, owner: object,
) -> dict[str, Any]:
    """Internal preflight sharing only its enclosing invocation's ledger context."""
    if candidate_output is not None:
        if candidate_output.exists():
            raise ValueError("candidate output destination already exists")
        if (candidate_output.parent / f".{candidate_output.name}.candidate-staging").exists():
            raise ValueError("candidate output staging destination already exists")
    drafts = None
    sealed_input = None
    if draft_pages is not None:
        from kb_creator.pipeline.review_draft import prepare_review_draft_input
        from kb_creator.pipeline.review_draft_preparation import validate_review_draft_author_input
        sealed_input = validate_review_draft_author_input(input_path=draft_input, binding_root=binding_root)
        review_input = json.loads(draft_input.read_text(encoding="utf-8"))
        prepare_review_draft_input(review_input)
        queue = json.loads((run_root / "review/review_queue.json").read_text(encoding="utf-8"))
        drafts = _load_cold_drafts(draft_pages, queue, review_draft_authority=review_input)
        _require_bound_cold_inputs(review_input, Path(binding_root), Path(draft_pages),
                                   spec_paths, list(drafts))
    raw_specs = [json.loads(path.read_text(encoding="utf-8")) for path in spec_paths]
    _validate_ocr_selector_domain(run_root, [item for value in raw_specs for item in value.get("ocr_equivalence_classes", [])])
    _validate_ocr_support_membership(raw_specs)
    spec = _load_spec_fragments(spec_paths)
    if drafts is not None and {row["source_page"] for row in spec["pages"]} != set(drafts):
        raise ValueError("sealed draft page domain differs from semantic spec")
    _reject_overlapping_selected_asset_assertions(spec.get("visual_text_assertions", []))
    profile = spec["semantic_structure_profile"]
    visual_inventory = _visual_inventory(run_root)
    reports = []
    decisions: dict[int, dict[str, Any]] = {}
    packets: dict[int, dict[str, Any]] = {}
    rendered_by_page: dict[int, str] = {}
    lexical_diagnostics: list[str] = []
    for row in spec["pages"]:
        page = row["source_page"]
        decision = copy.deepcopy(drafts[page]) if drafts is not None else json.loads(
            (baseline_root / f"pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        from kb_creator.pipeline.empty_text_assertions import select_empty_sources
        select_empty_sources(decision, packet, row.get("empty_source_selections"), page)
        for override in row.get("selected_purposes", []):
            matches = [
                block for block in decision["selected_blocks"]
                if block["view"] == override.get("view", decision["overlay_preference"])
                and block["raw_index"] == override["raw_index"]
            ]
            if len(matches) != 1 or override["purpose"] not in {"text", "asset", "structure", "visual"}:
                raise ValueError(f"page {page}: selected-purpose selector is invalid or ambiguous")
            matches[0]["purpose"] = override["purpose"]
        _remove_review_notes(decision, row.get("review_notes_remove"), page)
        _append_review_notes(decision, row.get("review_notes_append"), page)
        _apply_selected_before(decision, row.get("selected_before"), page)
        _materialize_reviewed_block_corrections(decision, packet, row.get("reviewed_block_corrections"), page)
        _materialize_linguistic_source_choice_corrections(decision, packet, row.get("linguistic_source_choice_corrections"), page, ledger_contexts, owner)
        markdown, effective = _render_reviewed_markdown(decision, packet, row, page)
        _materialize_reviewed_prose_bindings(decision, packet, row.get("reviewed_prose_bindings_v1"), effective, page)
        _materialize_reviewed_prose_roles(decision, packet, row.get("reviewed_prose_roles_v1"), effective, page, visual_inventory)
        _apply_asset_placements(decision, row.get("asset_placements"), page)
        lines = effective.split("\n")
        definitions = _unit_definitions(row, decision, page)
        for unit in definitions:
            _definition_span(lines, unit, page)
            view = unit.get("view") or decision["overlay_preference"]
            if not isinstance(view, str) or view not in packet.get("views", {}):
                raise ValueError(f"page {page}: source view missing from fresh packet: {view!r}")
            for raw_index in unit["raw_indices"]:
                if not any(block.get("raw_index") == raw_index for block in packet["views"][view]["blocks"]):
                    raise ValueError(f"page {page}: source raw index missing from fresh packet: {raw_index}")
        visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
        if visual_path not in visual_inventory:
            raise ValueError(f"page {page}: fresh Stage04 visual is missing")
        units = []
        definition_row = {**row, "units": definitions}
        shared_sources = _shared_unit_sources(definition_row, decision["overlay_preference"])
        for definition in definitions:
            units.append(_build_semantic_unit(packet, definition, decision["overlay_preference"],
                                              page, lines, shared_sources, profile))
        lexical_diagnostics.extend(_derive_lexical_prose_bindings(decision, packet, effective, units, page,
                                                                  collect_errors=True))
        decision["markdown"] = markdown
        decision["semantic_structure"] = (
            {"schema": SCHEMA, "review": {"state": "complete", "visual": {"path": visual_path, **visual_inventory[visual_path]}}, "units": units}
            if profile == PROFILE else
            {"schema": SCHEMA_V2, "profile": PROFILE_V2, "role_contract": row.get("role_contract"), "review": {"state": "complete", "visual": {"path": visual_path, **visual_inventory[visual_path]}}, "units": units}
        )
        decisions[page] = decision
        packets[page] = packet
        rendered_by_page[page] = _normalized_reader_markdown(markdown)
        reports.append({"source_page": page, "unit_count": len(definitions), "markdown_lines": len(lines), "visual": visual_inventory[visual_path]})
    assertion_reports = []
    semantic_assertions: dict[str, dict[str, Any]] = {}
    for assertion in spec.get("visual_text_assertions", []):
        page = assertion["source_page"]
        from kb_creator.pipeline.empty_text_assertions import RELATION as EMPTY_TEXT_RELATION, author_assertion
        if assertion.get("relation") == EMPTY_TEXT_RELATION:
            semantic_assertions[assertion["assertion_id"]] = author_assertion(assertion, packets[page], decisions[page], visual_inventory)
            assertion_reports.append({"id": assertion["assertion_id"], "page": page, "region_predicate": EMPTY_TEXT_RELATION, "rendered_adjacency": False, "exact_region_binding": True})
            continue
        if assertion["relation"] == "within_selected_asset_region":
            selector = assertion.get("asset")
            if not isinstance(selector, dict) or set(selector) != {"view_id", "raw_index", "logical_name", "source_path"}:
                raise ValueError(f"page {page}: asset assertion selector is invalid")
            block = _packet_asset_block(run_root, page, selector["view_id"], selector["raw_index"], selector["source_path"])
            x1, y1, x2, y2 = assertion["bbox"]
            ax1, ay1, ax2, ay2 = block["bbox"]
            if not (ax1 < x1 < x2 < ax2 and ay1 < y1 < y2 < ay2):
                raise ValueError(f"page {page}: asset assertion region must be strictly inside selected asset")
            rendered = rendered_by_page[page]; normalized_text = _normalized(assertion["text"])
            if rendered.count(normalized_text) != 1:
                raise ValueError(f"page {page}: asset assertion text must occur exactly once in Markdown")
            start = rendered.find(normalized_text)
            semantic_assertions[assertion["assertion_id"]] = {
                "source_page": page,
                "text": assertion["text"],
                "placement": {
                    "relation": "within_selected_asset_region",
                    "asset_block": block,
                    "logical_name": selector["logical_name"],
                    "markdown_span": {"start": start, "end": start + len(normalized_text)},
                },
            }
            assertion_reports.append({"id": assertion["assertion_id"], "page": page, "region_predicate": "within_selected_asset_region", "rendered_adjacency": True})
            continue
        anchor_ref = assertion["anchor"]
        anchor = _packet_unit(run_root, page, anchor_ref["view_id"], anchor_ref["raw_index"])
        x1, y1, x2, y2 = assertion["bbox"]
        ax1, ay1, ax2, ay2 = anchor["bbox"]
        relation = assertion["relation"]
        if relation not in {"before_anchor", "after_anchor", "column_before_anchor", "column_after_anchor", "anchor_prefix"}:
            raise ValueError(f"page {page}: source assertion relation is invalid")
        valid = (
            x2 <= ax1 if relation == "column_before_anchor" else
            x1 >= ax2 if relation == "column_after_anchor" else
            y2 <= ay1 and min(x2, ax2) > max(x1, ax1) if relation == "before_anchor" else
            y1 >= ay2 and min(x2, ax2) > max(x1, ax1) if relation == "after_anchor" else
            min(y2, ay2) > max(y1, ay1) and (x1 + x2) / 2 <= ax1 + (ax2 - ax1) * .25
        )
        normalized_text = _normalized(assertion["text"])
        from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _v3_page_context
        geometry = json.loads((run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json").read_text(encoding="utf-8"))
        mapping_errors: list[str] = []
        context = _v3_page_context(page, packets[page], decisions[page], geometry, mapping_errors)
        mappings = [item for item in context["mappings"] if item["unit"]["view_id"] == anchor_ref["view_id"] and item["unit"]["raw_index"] == anchor_ref["raw_index"]]
        if mapping_errors or len(mappings) != 1:
            raise ValueError(f"page {page}: source assertion anchor lacks one corrected reader mapping")
        anchor_start, anchor_end = mappings[0]["markdown_span"]
        rendered = context["rendered"]
        adjacent = rendered[anchor_end:anchor_end + len(normalized_text)] == normalized_text if relation in {"after_anchor", "column_after_anchor"} else anchor_start >= len(normalized_text) and rendered[anchor_start - len(normalized_text):anchor_start] == normalized_text
        if not valid or not adjacent:
            raise ValueError(f"page {page}: source assertion region predicate or rendered adjacency failed: {assertion['assertion_id']}")
        pair = (_normalized(_packet_text(run_root, page, anchor_ref["view_id"], anchor_ref["raw_index"])) + normalized_text) if relation in {"after_anchor", "column_after_anchor"} else (normalized_text + _normalized(_packet_text(run_root, page, anchor_ref["view_id"], anchor_ref["raw_index"])))
        semantic_assertions[assertion["assertion_id"]] = {
            "source_page": page, "text": assertion["text"],
            "placement": {"relation": relation, "anchor_unit": anchor, "expected_pair_sha256": digest(pair.encode())},
        }
        assertion_reports.append({"id": assertion["assertion_id"], "page": page, "region_predicate": relation, "rendered_adjacency": True})
    if lexical_diagnostics:
        raise ValueError("lexical prose binding preflight failed:\n" + "\n".join(lexical_diagnostics))
    from kb_creator.pipeline.semantic_structure import validate_semantic_structure
    geometry = (json.loads((run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json").read_text(encoding="utf-8"))
                if semantic_assertions else {})
    semantic_assertions = semantic_assertion_map(semantic_assertions, decisions, packets, geometry)
    structural_result = validate_semantic_structure(decisions, packets, visual_inventory, required_pages=sorted(decisions), visual_assertions=semantic_assertions)
    result = {"page_count": len(reports), "unit_count": sum(row["unit_count"] for row in reports), "visual_assertion_count": len(assertion_reports), "visual_assertions": assertion_reports, "semantic_structure_sha256": structural_result["structure_sha256"], "pages": reports}
    if sealed_input is not None:
        result["sealed_draft_input"] = sealed_input
        result["lexical_prose_binding_count"] = sum(len(decision.get("reviewed_prose_bindings_v1", [])) for decision in decisions.values())
        result["correction_coverage"] = {"page_count": len(decisions), "unbound_keys": 0}
    ledger_contexts.reverify_before_publish(owner)
    if candidate_output is not None:
        result["candidate_output"] = _write_validated_candidate(
            candidate_output, run_root, baseline_root, spec_paths, decisions, result,
        )
    return result


def _bound_file(path: Path, record: Any, label: str) -> None:
    """Reject a missing or changed file described by a candidate manifest."""
    if not isinstance(record, dict) or not {"bytes", "sha256"}.issubset(record):
        raise ValueError(f"final candidate {label} identity is malformed")
    if not path.is_file() or identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
        raise ValueError(f"final candidate {label} identity differs")


def _manifest_path(value: Any, *, relative_to: Path | None = None, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"final candidate {label} path is missing")
    candidate = Path(value)
    if relative_to is not None and not candidate.is_absolute():
        candidate = relative_to / candidate
    return candidate.resolve()


def validate_final_candidate(
    run_root: Path, candidate_root: Path, spec_paths: list[Path], draft_input: Path | None,
) -> dict[str, Any]:
    """Validate a semantic candidate by replaying its raw baseline exactly once.

    This is deliberately an ingress verifier, not an authoring shortcut.  The
    supplied candidate bytes are never used as a baseline for ``validate_spec``:
    the latter runs only against the manifest-bound raw baseline in disposable
    storage and every regenerated decision must equal the supplied page.
    """
    from kb_creator.pipeline.review_draft import ReviewDraftError, validate_review_draft_input

    if draft_input is None:
        raise ValueError("final candidate verification requires sealed review-draft input")
    try:
        draft_value = json.loads(Path(draft_input).read_text(encoding="utf-8"))
        review_record = validate_review_draft_input(draft_value)
    except (OSError, UnicodeError, json.JSONDecodeError, ReviewDraftError) as exc:
        raise ValueError(f"final candidate review-draft input is invalid: {exc}") from exc

    run_root = Path(run_root).resolve(); candidate_root = Path(candidate_root).resolve()
    manifest_path = candidate_root / "candidate_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("final candidate manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = {"schema", "state", "scope", "acceptance", "validation", "inputs", "pages"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError("final candidate manifest has invalid closed shape")
    if (manifest["schema"], manifest["state"], manifest["scope"], manifest["acceptance"]) != (
        "kb_creator.validated_draft_candidate.v1", "validated_candidate_only", "candidate_only", "pending",
    ):
        raise ValueError("final candidate manifest has unsupported state or scope")
    inputs = manifest["inputs"]
    if not isinstance(inputs, dict) or set(inputs) != {"source", "run", "review_queue", "baseline", "specs", "code"}:
        raise ValueError("final candidate manifest inputs have invalid closed shape")
    bindings = review_record.value["bindings"]
    reviewed_binding = bindings.get("reviewed_candidate_manifest")
    if not isinstance(reviewed_binding, dict) or {key: reviewed_binding.get(key) for key in ("bytes", "sha256")} != identity(manifest_path):
        raise ValueError("review-draft input is not bound to this final candidate manifest")
    run_record = inputs["run"]
    if not isinstance(run_record, dict):
        raise ValueError("final candidate run record is malformed")
    _bound_file(run_root / "run.json", run_record, "run")
    queue_record = inputs["review_queue"]
    if not isinstance(queue_record, dict) or queue_record.get("path") != "review/review_queue.json":
        raise ValueError("final candidate review queue record is malformed")
    _bound_file(run_root / "review/review_queue.json", queue_record, "review queue")
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    if _candidate_source_identity(run) != inputs["source"]:
        raise ValueError("final candidate source identity differs from run")
    queue = json.loads((run_root / "review/review_queue.json").read_text(encoding="utf-8"))
    expected_pages = {item.get("source_page") for item in queue.get("items", []) if isinstance(item, dict)}
    if not expected_pages or not all(type(page) is int for page in expected_pages):
        raise ValueError("final candidate replay queue has invalid page domain")

    baseline = inputs["baseline"]
    if not isinstance(baseline, dict) or set(baseline) != {"path", "pages"} or not isinstance(baseline["pages"], list):
        raise ValueError("final candidate raw baseline record is malformed")
    baseline_root = _manifest_path(baseline["path"], label="raw baseline")
    baseline_records = baseline["pages"]
    baseline_pages: set[int] = set()
    for record in baseline_records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ValueError("final candidate raw baseline page record is malformed")
        relative = record["path"].replace("\\", "/")
        match = re.fullmatch(r"pages/page-(\d{3})\.json", relative)
        if not match:
            raise ValueError("final candidate raw baseline page path is invalid")
        page = int(match.group(1)); baseline_pages.add(page)
        _bound_file(baseline_root / Path(relative), record, f"raw baseline page {page}")
    if baseline_pages != expected_pages:
        raise ValueError("final candidate raw baseline page domain differs from replay queue")
    declared_specs = inputs["specs"]
    supplied_specs = [Path(path).resolve() for path in spec_paths]
    if not isinstance(declared_specs, list) or len(declared_specs) != len(supplied_specs):
        raise ValueError("final candidate must bind exactly the supplied spec paths")
    for declared, supplied in zip(declared_specs, supplied_specs):
        if not isinstance(declared, dict):
            raise ValueError("final candidate spec record is malformed")
        _bound_file(supplied, declared, "semantic spec")
        if _manifest_path(declared.get("path"), label="semantic spec") != supplied:
            raise ValueError("final candidate semantic spec path differs")
    bound_specs = [bindings.get(f"input_{index:02d}") for index in range(len(supplied_specs))]
    if any(not isinstance(row, dict) for row in bound_specs) or [
        {key: row.get(key) for key in ("bytes", "sha256")} for row in bound_specs
    ] != [{key: declared.get(key) for key in ("bytes", "sha256")} for declared in declared_specs]:
        raise ValueError("review-draft input semantic spec bindings differ from final candidate")

    candidate_pages: dict[int, dict[str, Any]] = {}
    records = manifest["pages"]
    if not isinstance(records, list) or len(records) != len(expected_pages):
        raise ValueError("final candidate page inventory is incomplete")
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("source_page"), int) or not isinstance(record.get("path"), str):
            raise ValueError("final candidate page record is malformed")
        page = record["source_page"]
        if page in candidate_pages or record["path"] != f"pages/page-{page:03d}.json":
            raise ValueError("final candidate page record is duplicated or noncanonical")
        path = candidate_root / record["path"]
        _bound_file(path, {key: record[key] for key in ("path", "bytes", "sha256") if key in record}, f"page {page}")
        candidate_pages[page] = json.loads(path.read_text(encoding="utf-8"))
    disk_pages = {path.name for path in (candidate_root / "pages").glob("page-*.json")} if (candidate_root / "pages").is_dir() else set()
    if set(candidate_pages) != expected_pages or disk_pages != {f"page-{page:03d}.json" for page in expected_pages}:
        raise ValueError("final candidate page domain has missing or extra files")

    # validate_spec writes its own sealed candidate.  Comparing that output is
    # the proof that one-shot selectors were applied to raw pages exactly once.
    with tempfile.TemporaryDirectory(prefix="n25-final-candidate-") as temporary:
        regenerated_root = Path(temporary) / "regenerated"
        result = validate_spec(run_root, baseline_root, supplied_specs, candidate_output=regenerated_root)
        regenerated_manifest = json.loads((regenerated_root / "candidate_manifest.json").read_text(encoding="utf-8"))
        regenerated_records = {row["source_page"]: row for row in regenerated_manifest["pages"]}
        if set(regenerated_records) != expected_pages or result.get("validation"):
            raise ValueError("final candidate regeneration returned invalid page domain")
        for page, candidate in candidate_pages.items():
            generated_path = regenerated_root / regenerated_records[page]["path"]
            if generated_path.read_bytes() != (candidate_root / f"pages/page-{page:03d}.json").read_bytes():
                raise ValueError(f"final candidate page {page} differs from raw-baseline regeneration")
        regenerated_validation = regenerated_manifest.get("validation")
    if manifest["validation"] != regenerated_validation:
        raise ValueError("final candidate validation report differs from raw-baseline regeneration")
    return {
        "schema": "kb_creator.final_candidate_verification.v1",
        "candidate_manifest": {"path": str(manifest_path), **identity(manifest_path)},
        "review_draft_input_sha256": review_record.sha256,
        "page_count": len(candidate_pages),
        "pages": candidate_pages,
        "validation": regenerated_validation,
    }


def _validate_prepared_staging(staging_manifest: Path, candidate_manifest: Path, review_input_sha256: str) -> dict[str, Any]:
    """Require the staging owner's sealed prepared-for-audit binding."""
    try:
        staging = json.loads(staging_manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"prepared staging manifest is unreadable: {exc}") from exc
    if not isinstance(staging, dict):
        raise ValueError("final candidate requires prepared-for-audit staging")
    from kb_creator.pipeline.manifests import validate_seal
    try:
        validate_seal(staging, "manifest_sha256")
    except ValueError as exc:
        raise ValueError(f"prepared staging manifest seal is invalid: {exc}") from exc
    if staging.get("schema") != "kb_creator.reviewed_draft_staging.v3" or staging.get("state") != "prepared_for_audit":
        raise ValueError("final candidate requires prepared-for-audit staging")
    binding = staging.get("bindings", {}).get("finalized_candidate_manifest")
    if not isinstance(binding, dict) or {key: binding.get(key) for key in ("bytes", "sha256")} != identity(candidate_manifest):
        raise ValueError("prepared staging is not bound to this final candidate")
    preflight = staging.get("evidence", {}).get("review_draft_preflight")
    if not isinstance(preflight, dict) or preflight.get("input_sha256") != review_input_sha256:
        raise ValueError("prepared staging is not bound to this review-draft input")
    archive = staging.get("evidence", {}).get("authority", {}).get("archive_authority")
    if not isinstance(archive, dict) or archive.get("schema") != "kb_creator.review_draft_archive_consumption.v1":
        raise ValueError("prepared staging lacks explicit archive consumption authority")
    return {"path": str(staging_manifest), **identity(staging_manifest), "archive_authority": archive}


def _is_reparse_point(path: Path) -> bool:
    """Keep authored evidence copies free of symlink and Windows reparse indirection."""
    stat = path.lstat()
    return path.is_symlink() or bool(getattr(stat, "st_file_attributes", 0) & 0x400)


def _copy_final_evidence_projection(*, candidate_root: Path, verified: dict[str, Any],
                                    staging_manifest: Path, output: Path) -> dict[str, dict[str, Any]]:
    """Copy the minimum portable bridge only after the ingress checks passed.

    The manifest and page bytes remain the sealed candidate preimage.  The
    authored directory receives a byte-identical projection so its final
    evidence can use portable paths without changing external bindings.
    """
    source_candidate_root = Path(candidate_root)
    source_staging_manifest = Path(staging_manifest)
    if _is_reparse_point(source_candidate_root) or _is_reparse_point(source_staging_manifest):
        raise ValueError("final evidence projection rejects source reparse points")
    candidate_root = source_candidate_root.resolve(strict=True)
    staging_manifest = source_staging_manifest.resolve(strict=True)
    if not candidate_root.is_dir():
        raise ValueError("final candidate root is unsafe for evidence projection")
    if not staging_manifest.is_file():
        raise ValueError("prepared staging manifest is unsafe for evidence projection")
    expected_pages = sorted(verified["pages"])
    expected_files = {Path("candidate_manifest.json"), *{Path("pages") / f"page-{page:03d}.json" for page in expected_pages}}
    expected_dirs = {Path("pages")}
    actual_files: set[Path] = set()
    actual_dirs: set[Path] = set()
    for path in candidate_root.rglob("*"):
        relative = path.relative_to(candidate_root)
        if _is_reparse_point(path):
            raise ValueError(f"final candidate projection rejects reparse point: {relative.as_posix()}")
        if path.is_file():
            actual_files.add(relative)
        elif path.is_dir():
            actual_dirs.add(relative)
        else:
            raise ValueError(f"final candidate projection rejects non-regular entry: {relative.as_posix()}")
    if actual_files != expected_files or actual_dirs != expected_dirs:
        raise ValueError("final candidate projection source inventory is not exact")
    manifest = candidate_root / "candidate_manifest.json"
    if identity(manifest) != {key: verified["candidate_manifest"][key] for key in ("bytes", "sha256")}:
        raise ValueError("final candidate manifest changed before evidence projection")
    for page in expected_pages:
        path = candidate_root / "pages" / f"page-{page:03d}.json"
        if not path.is_file():
            raise ValueError(f"final candidate projection page is missing: {page}")
    candidate_destination = output / "final-candidate"
    staging_destination = output / "prepared-staging" / "staging-manifest.json"
    if candidate_destination.exists() or staging_destination.parent.exists():
        raise ValueError("final evidence projection destination already exists")
    candidate_destination.mkdir(parents=True)
    (candidate_destination / "pages").mkdir()
    for source in sorted(expected_files, key=lambda item: item.as_posix()):
        source_path = candidate_root / source
        target_path = candidate_destination / source
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)
        if identity(target_path) != identity(source_path):
            raise ValueError(f"final candidate projection copy differs: {source.as_posix()}")
    staging_destination.parent.mkdir(parents=True)
    shutil.copyfile(staging_manifest, staging_destination)
    if identity(staging_destination) != identity(staging_manifest):
        raise ValueError("prepared staging projection copy differs")
    return {
        "final_candidate": {"path": "final-candidate/candidate_manifest.json", **identity(candidate_destination / "candidate_manifest.json")},
        "prepared_staging": {"path": "prepared-staging/staging-manifest.json", **identity(staging_destination)},
    }


def _load_cold_drafts(draft_pages: Path, queue: dict[str, Any], *, review_draft_authority: dict[str, Any] | None = None) -> dict[int, dict[str, Any]]:
    required = {"schema", "source_page", "semantic_role", "overlay_preference", "selected_blocks", "markdown", "assets", "unresolved", "review"}
    allowed = required | {"block_boundaries"}
    expected = {int(item["source_page"]): item for item in queue["items"]}
    if not draft_pages.is_dir():
        raise ValueError("draft-pages directory is missing")
    result: dict[int, dict[str, Any]] = {}
    for path in sorted(draft_pages.glob("page-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        page = value.get("source_page") if isinstance(value, dict) else None
        if type(page) is not int or set(value) - allowed or required - set(value) or page in result:
            raise ValueError("draft page has invalid closed shape or duplicate source_page")
        if path.name != f"page-{page:03d}.json" or page not in expected or value["semantic_role"] != expected[page]["contract_role"]:
            raise ValueError(f"draft page {path.name}: page or semantic role mismatches replay queue")
        review = value["review"]
        visual_ok = (
            isinstance(review, dict)
            and (review.get("visual_reviewed") in {True, False} if review_draft_authority is not None else review.get("visual_reviewed") is True)
        )
        if value["schema"] != "kb_creator.mineru_ai_page_decision.v1" or value["unresolved"] != [] or not isinstance(review, dict) or set(review) != {"visual_reviewed", "notes"} or not visual_ok or not isinstance(review.get("notes"), str):
            requirement = "literal visual review and empty unresolved" if review_draft_authority is not None else "closed visual review and empty unresolved"
            raise ValueError(f"draft page {page}: exact schema, {requirement} are required")
        result[page] = value
    if set(result) != set(expected):
        raise ValueError("draft-pages must contain exactly one reviewed page for every replay queue item")
    return result


def _cold_ocr_classes(run_root: Path, selectors: list[dict[str, Any]], visuals: dict[str, dict[str, Any]], decisions: dict[int, dict[str, Any]], assertions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows, seen = [], set(); base = {"class_id", "source_page", "canonical", "alternates", "rationale"}; reviewed = base | {"visual_verdict", "equivalence_policy", "supporting_assertion_ids"}
    reviewed_policies = {"reviewed_visual_full_unit_v1", "reviewed_visual_full_unit_any_cpu_view_v1", "reviewed_exact_raw_text_geometry_drift_v1"}
    for value in selectors:
        if not isinstance(value, dict) or set(value) != base and set(value) != reviewed: raise ValueError("OCR equivalence selector has invalid closed shape")
        page, class_id, full = value["source_page"], value["class_id"], set(value) == reviewed
        if type(page) is not int or not isinstance(class_id, str) or not class_id or class_id in seen or not isinstance(value["rationale"], str) or not value["rationale"].strip(): raise ValueError("OCR equivalence selector has invalid identity")
        def unit(ref: Any) -> dict[str, Any]:
            if not isinstance(ref, dict) or set(ref) != {"view_id", "raw_index"} or not isinstance(ref["view_id"], str) or type(ref["raw_index"]) is not int: raise ValueError("OCR equivalence selector unit is invalid")
            return _packet_unit(run_root, page, ref["view_id"], ref["raw_index"])
        canonical = unit(value["canonical"]); alternates = [unit(item) for item in value["alternates"]] if isinstance(value["alternates"], list) else []
        identities = [(item["view_id"], item["raw_index"]) for item in [canonical, *alternates]]; visual_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
        if (not full and canonical["view_id"] != "original_pipeline_txt") or not 1 <= len(alternates) <= 2 or len(identities) != len(set(identities)) or visual_path not in visuals: raise ValueError("OCR equivalence selector members or visual are invalid")
        row = {"class_id": class_id, "source_page": page, "canonical_unit": canonical, "alternate_units": alternates, "visual": {"path": visual_path, **visuals[visual_path]}, "visual_verdict": "canonical_text_visible_alternate_text_absent", "rationale": value["rationale"]}
        if full:
            ids = value["supporting_assertion_ids"]
            policy = value["equivalence_policy"]
            if value["visual_verdict"] != "canonical_proof_complete_for_region_alternates_are_ocr_corruption" or policy not in reviewed_policies or (policy == "reviewed_visual_full_unit_v1" and canonical["view_id"] != "original_pipeline_txt") or not isinstance(ids, list) or len(ids) != len(set(ids)) or any(not isinstance(item, str) for item in ids): raise ValueError("reviewed OCR selector policy, verdict, or assertion IDs are invalid")
            named = [assertions.get(item) for item in ids]
            if any(item is None for item in named): raise ValueError("reviewed OCR selector names a stale assertion")
            packet = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8")); blocks = {(view, block["raw_index"]): block for view, data in packet["views"].items() for block in data["blocks"] if isinstance(block, dict) and type(block.get("raw_index")) is int}; decision = decisions[page]; selected = {(item["view"], item["raw_index"]) for item in decision["selected_blocks"] if item.get("purpose") != "asset"}; corrected = str(blocks[(canonical["view_id"], canonical["raw_index"])].get("text", ""))
            corrections = reviewed_text_corrections(decision, blocks, selected, decision["markdown"], page)
            block_corrections = reviewed_block_text_corrections(decision, blocks, selected, decision["markdown"], page)
            corrected = apply_reviewed_text_corrections(corrected, (canonical["view_id"], canonical["raw_index"]), corrections, block_corrections)
            row.update({"visual_verdict": value["visual_verdict"], "equivalence_policy": value["equivalence_policy"], "source_visual": {"path": visual_path, **visuals[visual_path]}, "canonical_proof": {"supporting_assertion_ids": ids, "expected_normalized_sha256": digest(_canonical_assertion_proof(corrected, named).encode())}})
        rows.append(row); seen.add(class_id)
    return rows

def _author_drafts_with_ledger_contexts(run_root: Path, draft_pages: Path | None, destination: Path, spec_paths: list[Path], *, mode: str = "strict", draft_input: Path | None = None, binding_root: Path | None = None, validated_candidate: Path | None = None, prepared_staging: Path | None = None, ledger_contexts: _AuthorLedgerContexts, owner: object) -> dict[str, Any]:
    """Cold-start route: stage explicit reviewed drafts, derive every authority, then validate before publish."""
    from kb_creator.pipeline import reconstruction, reconstruction_replay, reconstruction_replay_resume
    from kb_creator.pipeline.review_draft import (
        ReviewDraftError, finalize_review_draft_evidence, prepare_review_draft_input,
        validate_review_draft_input,
    )
    from kb_creator.pipeline.semantic_structure import validate_semantic_structure
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _audit_v3_content_for_author
    if mode not in {"strict", "review_draft"} or (mode == "review_draft") != (draft_input is not None):
        raise ValueError("review-draft authoring requires explicit mode and sealed draft input")
    if validated_candidate is not None and mode != "review_draft":
        raise ValueError("final candidate authoring requires review-draft mode")
    if validated_candidate is None and draft_pages is None:
        raise ValueError("cold-start authoring requires draft pages")
    if validated_candidate is not None and prepared_staging is None:
        raise ValueError("final candidate authoring requires prepared staging manifest")
    review_authority = None
    review_input = None
    structural_context = None
    if draft_input is not None:
        try:
            review_input = json.loads(Path(draft_input).read_text(encoding="utf-8"))
            validate_review_draft_input(review_input)
            review_authority = prepare_review_draft_input(review_input)
        except (OSError, UnicodeError, json.JSONDecodeError, ReviewDraftError) as exc:
            raise ValueError(f"invalid review-draft input: {exc}") from exc
        if (binding_root is None and any(item.get("kind") == "translation_source_choice_pending"
                                        for item in review_input["source_issues"]["issues"])):
            raise ValueError("review-draft authoring requires an explicit input binding root")
    verified = None
    staging_authority = None
    if validated_candidate is not None:
        # Validate both sealed ingress records before reading archive paths.
        # This prevents an unrelated staging manifest from selecting any
        # historical replay artifact.
        verified = validate_final_candidate(run_root, validated_candidate, spec_paths, draft_input)
        staging_authority = _validate_prepared_staging(
            Path(prepared_staging), Path(validated_candidate) / "candidate_manifest.json",
            verified["review_draft_input_sha256"],
        )
    if validated_candidate is None:
        if mode == "review_draft":
            from kb_creator.pipeline.review_draft import build_archive_consumption_context
            from kb_creator.pipeline.review_draft_preparation import validate_review_draft_author_input
            validate_review_draft_author_input(input_path=Path(draft_input), binding_root=Path(binding_root))
            page_prefix = ("source_choice_successor_page-" if any(name.startswith("source_choice_successor_page-")
                           for name in review_input["bindings"]) else "draft_page-")
            bound_pages = [int(name.removeprefix(page_prefix)) for name in review_input["bindings"]
                           if name.startswith(page_prefix)]
            _require_bound_cold_inputs(review_input, Path(binding_root), Path(draft_pages),
                                       spec_paths, bound_pages)
            required = {"candidate_manifest", "composer_config", "composer_report"}
            if not required <= set(review_input["bindings"]):
                raise ValueError("review-draft archive consumption requires a sealed composer input")
            # A sealed composer consumes an archived replay payload.  Its input
            # already binds the mechanical candidate and current draft bytes;
            # the archive context reopens packet, visual, geometry and queue
            # identities without granting replay/resume capability.
            archive = build_archive_consumption_context(source_run_root=Path(run_root), target_run_root=Path(run_root))
            checked = archive["checked_paths"]
            authorities = SimpleNamespace(
                stage_02_root=Path(checked["stage_02_root"]), comparison=Path(checked["comparison"]),
                merge_packets=Path(checked["merge_packets"]), visual_manifest=Path(checked["visual_manifest"]),
                geometry_plan=Path(checked["geometry_plan"]), bridge_sha256=archive["target"]["bridge_sha256"],
            )
            queue = json.loads(Path(checked["review_queue"]).read_text(encoding="utf-8"))
        else:
            authorities = reconstruction_replay.validate_replayed_prefix(run_root)
            replay_review_authority = reconstruction_replay_resume.validate_replay_review_queue(authorities)
            queue = replay_review_authority.queue
    else:
        archive = staging_authority["archive_authority"]
        checked = archive.get("checked_paths") if isinstance(archive, dict) else None
        required_paths = {"stage_02_root", "comparison", "merge_packets", "visual_manifest", "geometry_plan", "review_queue"}
        if not isinstance(checked, dict) or set(checked) != required_paths or any(not isinstance(checked[key], str) for key in required_paths):
            raise ValueError("prepared staging archive authority lacks checked replay paths")
        expected_queue = (Path(run_root) / "review/review_queue.json").resolve()
        if Path(checked["review_queue"]).resolve() != expected_queue:
            raise ValueError("prepared staging archive authority queue differs from selected run")
        if archive.get("source_sha256") != json.loads((Path(validated_candidate) / "candidate_manifest.json").read_text(encoding="utf-8"))["inputs"]["source"]["sha256"]:
            raise ValueError("prepared staging archive authority source differs from final candidate")
        authorities = SimpleNamespace(
            stage_02_root=Path(checked["stage_02_root"]), comparison=Path(checked["comparison"]),
            merge_packets=Path(checked["merge_packets"]), visual_manifest=Path(checked["visual_manifest"]),
            geometry_plan=Path(checked["geometry_plan"]), bridge_sha256=archive.get("target_bridge_sha256"),
        )
        queue = json.loads((run_root / "review/review_queue.json").read_text(encoding="utf-8"))
    if review_input is not None and binding_root is not None:
        from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context
        structural_context = open_structural_projection_context(
            input_path=Path(draft_input), binding_root=Path(binding_root))
    raw_spec = [json.loads(path.read_text(encoding="utf-8")) for path in spec_paths]
    if any("semantic_structure_profile" not in value for value in raw_spec):
        raise ValueError("cold-start spec must explicitly declare semantic_structure_profile")
    spec = _load_spec_fragments(spec_paths)
    ocr_selectors = [item for value in raw_spec for item in value.get("ocr_equivalence_classes", [])]
    if any(any(key in row for key in ("inherit_units_from_baseline", "review_notes_remove")) for row in spec["pages"]):
        raise ValueError("cold-start spec cannot use inherited baseline selectors")
    if validated_candidate is None:
        drafts = _load_cold_drafts(draft_pages, queue, review_draft_authority=review_authority)
        prepared_coverage = (_recompute_composer_coverage(review_input, Path(binding_root), Path(run_root), Path(draft_pages))
                            if review_input is not None and binding_root is not None else None)
        coverage_successor_dispositions = (_composer_coverage_successor_dispositions(
            review_input, Path(binding_root), prepared_coverage)
            if review_input is not None and binding_root is not None else None)
    else:
        drafts = verified["pages"]
        if set(drafts) != {item["source_page"] for item in queue["items"]}:
            raise ValueError("final candidate page domain differs from replay queue")
        prepared_coverage = _recompute_prepared_coverage(Path(prepared_staging), Path(run_root), Path(validated_candidate))
        coverage_successor_dispositions = None
    if destination.exists(): raise ValueError("destination already exists")
    stage = destination.parent / f".{destination.name}.cold-start-staging"
    if stage.exists(): raise ValueError("cold-start staging destination already exists")
    try:
        baseline, output = stage / "baseline", stage / "output"
        allowlist = {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []}
        if validated_candidate is None:
            write_json(baseline / "reviewed_allowlist.v3.json", allowlist)
            write_json(baseline / "decision_set.json", {"reviewed_allowlist": {"path": "reviewed_allowlist.v3.json"}})
            for page, value in drafts.items(): write_json(baseline / f"pages/page-{page:03d}.json", value)
            result = _author_with_ledger_contexts(run_root, baseline, output, spec_paths,
                preview_root=None, ledger_contexts=ledger_contexts, owner=owner)
        else:
            result, _ = _author_final_candidate(run_root, Path(validated_candidate), output, spec_paths, Path(draft_input), ledger_contexts, owner)
        if mode == "strict":
            reconstruction.validate_decision_set(output / "decision_set.json", queue, output)
        decisions = {page: json.loads((output / f"pages/page-{page:03d}.json").read_text(encoding="utf-8")) for page in drafts}
        packets = {page: json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8")) for page in drafts}
        visuals = _visual_inventory(run_root)
        geometry = json.loads((run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json").read_text(encoding="utf-8"))
        reviewed = json.loads((output / "reviewed_allowlist.v3.json").read_text(encoding="utf-8"))
        assertions = semantic_assertion_map(
            {item["assertion_id"]: item for item in reviewed["visual_text_assertions"]}, decisions, packets, geometry,
        )
        validate_semantic_structure(decisions, packets, visuals, required_pages=sorted(decisions), visual_assertions=assertions)
        from kb_creator.pipeline.semantic_structure import (
            collect_reference_image_proof_keys, collect_split_structure_proof_keys,
        )
        reference_proof_keys = collect_reference_image_proof_keys(decisions, packets, assertions)
        split_structure_proof_keys = collect_split_structure_proof_keys(decisions, packets)
        reviewed["ocr_equivalence_classes"] = _cold_ocr_classes(run_root, ocr_selectors, visuals, decisions, assertions)
        write_json(output / "reviewed_allowlist.v3.json", reviewed)
        result["reviewed_allowlist"] = {"path": "reviewed_allowlist.v3.json", **identity(output / "reviewed_allowlist.v3.json")}
        write_json(output / "decision_set.json", result)
        if mode == "strict":
            reconstruction.validate_decision_set(output / "decision_set.json", queue, output)
        has_source_render = any(
            any(isinstance(asset, dict) and asset.get("origin") == "source_pdf_page_render_v1" for asset in decision.get("assets", []))
            for decision in decisions.values()
        )
        if has_source_render:
            from kb_creator.pipeline.source_page_render import replay_source_render_context
            source_render_context = replay_source_render_context(run_root, geometry)
        else:
            source_render_context = None
        pending_source_context = None
        if review_input is not None and any(item.get("kind") == "translation_source_choice_pending"
                                            for item in review_input["source_issues"]["issues"]):
            pending_source_context = {"review_input": review_input, "input_path": str(Path(draft_input)),
                                      "binding_root": str(Path(binding_root)), "run_root": str(Path(run_root))}
        audit = _audit_v3_content_for_author(packets, decisions, allowlist=reviewed, geometry=geometry, visual_inventory=visuals, authorities=reviewed["authority"], source_render_context=source_render_context, reader_coverage_claims=prepared_coverage, coverage_successor_dispositions=coverage_successor_dispositions, pending_source_context=pending_source_context, ledger_contexts=ledger_contexts, ledger_owner=owner, structural_context=structural_context)
        if not audit["passed"]:
            _write_failed_fidelity_audit(destination, Path(run_root), Path(prepared_staging) if prepared_staging else None, spec_paths, output, audit)
            raise ValueError("cold-start fidelity audit failed; persistent diagnostic written")
        # Reuse the exact Stage 06 decision validator before publishing the
        # cold-start output. This keeps title guards, asset resolution, and
        # source-render proof checks identical to later materialization.
        comparison = json.loads(authorities.comparison.read_text(encoding="utf-8"))
        if source_render_context is not None:
            source_render_context = {**source_render_context, "proofs": {
                page["source_page"]: page.get("source_page_renders", [])
                for page in audit.get("pages", [])
            }}
        source_render_staging = stage / "source-renders"
        source_render_staging.mkdir(parents=True, exist_ok=True)
        structural_role_proofs = {}
        if review_input is not None and any(item.get("kind") == "source_structure_role_pending"
                                            for item in review_input["source_issues"]["issues"]):
            from kb_creator.pipeline.structural_role_issues import derive_structural_role_conflict_proofs
            structural_role_proofs = derive_structural_role_conflict_proofs(
                review_input=review_input, input_path=Path(draft_input), binding_root=Path(binding_root),
                run_root=Path(run_root), decisions=decisions, packets=packets, comparison=comparison,
                stage05_pages=audit.get("pages", []))
        validation = _validate_authored_pages(
            decisions, packets, comparison, authorities.stage_02_root, source_render_context,
            source_render_staging, reference_proof_keys, split_structure_proof_keys,
            structural_role_proofs, assertions)
        if not validation["passed"]:
            _write_failed_decision_validation(destination, Path(run_root),
                Path(prepared_staging) if prepared_staging else None, spec_paths, output, audit, validation)
            first = validation["failures"][0]
            raise ValueError(f"page-{first['source_page']:03d}.json: {first['error']}; "
                             f"{len(validation['failures'])} pages failed; persistent diagnostic written")
        if mode == "review_draft":
            audit_path = output / "review-draft-stage05-audit.json"
            write_json(audit_path, audit)
            authored = {
                "decision_set": {"path": "decision_set.json", **identity(output / "decision_set.json")},
                "reviewed_allowlist": {"path": "reviewed_allowlist.v3.json", **identity(output / "reviewed_allowlist.v3.json")},
                "stage05_audit": {"path": audit_path.name, **identity(audit_path)},
            }
            if validated_candidate is not None:
                authored.update(_copy_final_evidence_projection(
                    candidate_root=Path(validated_candidate), verified=verified,
                    staging_manifest=Path(prepared_staging), output=output,
                ))
            final = finalize_review_draft_evidence(
                review_input, authored=authored, audit=audit,
                visual_reviewed_false_pages=sorted(page for page, draft in drafts.items() if draft["review"]["visual_reviewed"] is False),
            )
            write_json(output / "review-draft-evidence.json", final)
            result["review_draft"] = {"preflight": review_authority, "evidence": {"path": "review-draft-evidence.json", **identity(output / "review-draft-evidence.json")}}
        if structural_context is not None:
            reopened = open_structural_projection_context(
                input_path=Path(draft_input), binding_root=Path(binding_root))
            if reopened != structural_context:
                raise ValueError("structural projection authority changed before publication")
        ledger_contexts.reverify_before_publish(owner)
        output.replace(destination)
        return result
    finally:
        if stage.exists(): shutil.rmtree(stage)


def author_drafts(run_root: Path, draft_pages: Path | None, destination: Path, spec_paths: list[Path], *, mode: str = "strict", draft_input: Path | None = None, binding_root: Path | None = None, validated_candidate: Path | None = None, prepared_staging: Path | None = None) -> dict[str, Any]:
    owner = object()
    ledger_contexts = _AuthorLedgerContexts(owner)
    with _author_ledger_snapshot_scope(lambda path: ledger_contexts.snapshot_v2(owner, path)):
        return _author_drafts_with_ledger_contexts(run_root, draft_pages, destination, spec_paths,
            mode=mode, draft_input=draft_input, binding_root=binding_root,
            validated_candidate=validated_candidate, prepared_staging=prepared_staging,
            ledger_contexts=ledger_contexts, owner=owner)
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--draft-pages", type=Path)
    parser.add_argument("--spec", type=Path, required=True, nargs="+", help="One or more disjoint reviewed page fragments")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-output", type=Path)
    parser.add_argument("--draft-input", type=Path)
    parser.add_argument("--binding-root", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if (args.baseline is None) == (args.draft_pages is None):
        parser.error("provide exactly one of --baseline or --draft-pages")
    if args.validate_only:
        if args.draft_pages is not None:
            if args.draft_input is None or args.binding_root is None or args.candidate_output is not None:
                parser.error("sealed draft preflight requires --draft-input and --binding-root, without --candidate-output")
        if args.draft_pages is None:
            result = validate_spec(args.run, args.baseline, args.spec, candidate_output=args.candidate_output)
        else:
            result = validate_spec(args.run, None, args.spec, draft_pages=args.draft_pages,
                draft_input=args.draft_input, binding_root=args.binding_root)
        print(json.dumps(result, indent=2))
        return 0
    if args.candidate_output is not None:
        parser.error("--candidate-output requires --validate-only")
    if args.output is None:
        parser.error("--output is required unless --validate-only is set")
    result = author_drafts(args.run, args.draft_pages, args.output, args.spec) if args.draft_pages is not None else author(args.run, args.baseline, args.output, args.spec)
    print(json.dumps({"pages": len(result["decisions"]), "decision_set": str(args.output / "decision_set.json"), "sha256": identity(args.output / "decision_set.json")["sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
