from __future__ import annotations

import json
import os
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from . import reconstruction
from .identity import canonical_bytes, deterministic_inventory, file_identity, implementation_inventory, sha256_bytes
from .manifests import sealed, validate_seal
from .reconstruction_replay import (
    FreshReplayAuthorities,
    ReplayError,
    validate_replay_authorities,
    validate_replayed_prefix,
)
from kb_creator.scripts.normalize_publication_access import (
    normalize_publication_access_if_managed,
)


SUBMISSION_SCHEMA = "kb_creator.validated_reconstruction_submission.v2"
STAGE_SCHEMA = "kb_creator.replay_downstream_stage_manifest.v1"
RESULT_SCHEMA = "kb_creator.replay_resume_result.v1"
ALLOWLIST_SCHEMA = "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3"
AUDIT_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v3"
AUDIT_V4_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v4"
PROVENANCE_SCHEMA = "kb_creator.mineru_ai_merge_provenance.v3"
STAGES = ("05-fidelity-audit", "06-materialize-candidate")
DOWNSTREAM_IMPLEMENTATION = (
    "kb_creator/__main__.py",
    "kb_creator/pipeline/reconstruction_replay_resume.py",
    "kb_creator/scripts/audit_mineru_ai_merge_fidelity.py",
    "kb_creator/scripts/materialize_mineru_ai_merge.py",
    "kb_creator/pipeline/semantic_structure.py",
    "kb_creator/pipeline/reviewed_correction_text.py",
    "kb_creator/pipeline/reviewed_prose_binding.py",
    "kb_creator/pipeline/source_page_render.py",
    "kb_creator/pipeline/reconstruction_asset_inventory.py",
    "kb_creator/pipeline/text_segmentation.py",
    "kb_creator/scripts/normalize_publication_access.py",
    "kb_creator/contracts/validated_reconstruction_submission.v2.schema.json",
    "kb_creator/contracts/replay_downstream_stage_manifest.v1.schema.json",
    "kb_creator/contracts/replay_resume_result.v1.schema.json",
    "kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json",
    "kb_creator/contracts/ai_merge_fidelity_audit.v3.schema.json",
    "kb_creator/contracts/reconstruction_decision_set.v2.schema.json",
    "kb_creator/contracts/page_semantic_structure.v1.schema.json",
    "kb_creator/contracts/page_semantic_structure.v2.schema.json",
    "kb_creator/contracts/ai_merge_fidelity_audit.v4.schema.json",
    "kb_creator/contracts/reconstruction_semantic_structure.v1.schema.json",
    "kb_creator/contracts/mineru_ai_merge_provenance.v3.schema.json",
)


class ReplayResumeError(ValueError):
    pass


@dataclass(frozen=True)
class ReplayReviewAuthorities:
    run_root: Path
    queue_path: Path
    queue: dict[str, Any]
    comparison_path: Path
    bridge_path: Path


@dataclass(frozen=True)
class SubmissionAuthorities:
    root: Path
    receipt_path: Path
    receipt: dict[str, Any]
    decisions_root: Path
    decision_set_path: Path
    allowlist_path: Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReplayResumeError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise ReplayResumeError(f"invalid JSON object: {path}")
    return value


def _closed(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ReplayResumeError(f"{label}: unknown or missing fields")
    return value


def _write_new(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    with path.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    if path.read_bytes() != raw:
        raise ReplayResumeError("write reopen mismatch")


def _copy_new(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as inp, destination.open("xb") as out:
        shutil.copyfileobj(inp, out); out.flush(); os.fsync(out.fileno())
    if file_identity(source) != file_identity(destination):
        raise ReplayResumeError("submission copy identity mismatch")


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _relative_file(run_root: Path, relative: str) -> dict[str, Any]:
    path = run_root / relative
    if not path.is_file():
        raise ReplayResumeError(f"missing authority: {relative}")
    return {"path": relative, **file_identity(path)}


def _inventory_without(root: Path, excluded: set[str]) -> list[dict[str, Any]]:
    """Filter a downstream inventory without widening the shared identity API."""
    return [row for row in deterministic_inventory(root) if row["path"] not in excluded]


def validate_replay_review_queue(authorities: FreshReplayAuthorities) -> ReplayReviewAuthorities:
    run_root = authorities.run_root
    run = _json(run_root / "run.json")
    queue_path, bridge_path = run_root / "review/review_queue.json", run_root / "replay/bridge.json"
    queue = _json(queue_path)
    _closed(queue, {"schema", "run_identity_sha256", "contract_sha256", "source_sha256", "comparison", "bridge", "required_decision_schema", "items", "queue_sha256"}, "replay review queue")
    try:
        validate_seal(queue, "queue_sha256")
    except ValueError as error:
        raise ReplayResumeError("review queue seal mismatch") from error
    if queue["schema"] != "kb_creator.review_queue.v2" or queue["run_identity_sha256"] != run["portable_identity_sha256"] or queue["contract_sha256"] != run["contract"]["sha256"] or queue["source_sha256"] != run["source"]["sha256"]:
        raise ReplayResumeError("review queue run authority mismatch")
    if authorities.comparison is None or queue["comparison"] != {"path": "outputs/03-compare-views/comparison.json", **file_identity(authorities.comparison)}:
        raise ReplayResumeError("review queue comparison authority mismatch")
    if queue["bridge"] != {"path": "replay/bridge.json", **file_identity(bridge_path), "bridge_sha256": authorities.bridge_sha256}:
        raise ReplayResumeError("review queue bridge authority mismatch")
    items = queue["items"]
    if not isinstance(items, list) or [row.get("source_page") for row in items if isinstance(row, dict)] != run["scope"]["ordered_pages"]:
        raise ReplayResumeError("review queue page domain mismatch")
    expected_item_keys = {"id", "source_page", "contract_role", "contract_traits", "contract_strategies", "merge_packet", "issue_kinds", "required_decision_file", "state"}
    bundle = run_root / "outputs/04-visual-merge-bundle"
    for row in items:
        _closed(row, expected_item_keys, "review queue item")
        page = row["source_page"]
        packet = bundle / f"merge_packets/pages/page-{page:03d}.json"
        if row["id"] != f"page-{page:03d}" or row["required_decision_file"] != f"pages/page-{page:03d}.json" or row["state"] != "open" or row["merge_packet"] != {"path": f"merge_packets/pages/page-{page:03d}.json", **file_identity(packet)}:
            raise ReplayResumeError("review queue item authority mismatch")
    return ReplayReviewAuthorities(run_root, queue_path, queue, authorities.comparison, bridge_path)


def _validate_allowlist(path: Path, review: ReplayReviewAuthorities, authorities: FreshReplayAuthorities) -> dict[str, Any]:
    value = _json(path)
    from kb_creator.pipeline.text_segmentation import TextSegmentationError, allowlist_v3_keys
    try:
        allowlist_v3_keys(value)
    except TextSegmentationError as error:
        raise ReplayResumeError(str(error)) from error
    geometry = authorities.geometry_plan
    visual = authorities.visual_manifest
    if geometry is None or visual is None:
        raise ReplayResumeError("Stage04 authority is incomplete")
    run = _json(review.run_root / "run.json")
    expected = {
        "run_identity_sha256": run["portable_identity_sha256"], "bridge_sha256": authorities.bridge_sha256,
        "review_queue_sha256": review.queue["queue_sha256"], "comparison_sha256": _json(review.comparison_path)["comparison_sha256"],
        "geometry_plan_sha256": _json(geometry)["plan_sha256"], "visual_manifest_sha256": _json(visual)["manifest_sha256"],
    }
    if value["schema"] != ALLOWLIST_SCHEMA or value["authority"] != expected:
        raise ReplayResumeError("reviewed allowlist v3 authority mismatch")
    return value


def materialize_replay_submission_snapshot(authorities: FreshReplayAuthorities, decision_set: Path, decisions_root: Path) -> SubmissionAuthorities:
    review = validate_replay_review_queue(authorities)
    try:
        decision_data = reconstruction.validate_decision_set(decision_set, review.queue, decisions_root)
    except (OSError, KeyError, reconstruction.ControlPlaneError) as error:
        raise ReplayResumeError(f"decision set invalid: {error}") from error
    allow_record = decision_data.get("reviewed_allowlist")
    if not isinstance(allow_record, dict):
        raise ReplayResumeError("replay resume requires an explicit reviewed allowlist v3")
    allow_path = decisions_root / allow_record["path"]
    if file_identity(allow_path) != {"bytes": allow_record["bytes"], "sha256": allow_record["sha256"]}:
        raise ReplayResumeError("reviewed allowlist identity mismatch")
    _validate_allowlist(allow_path, review, authorities)
    final = review.run_root / "review/validated-submission-v2"
    if final.exists():
        existing = load_replay_submission(authorities)
        if file_identity(decision_set) != {
            "bytes": existing.receipt["decision_set"]["bytes"],
            "sha256": existing.receipt["decision_set"]["sha256"],
        }:
            raise ReplayResumeError("existing submission differs from requested decision set")
        expected_pages = {
            row["path"]: {"bytes": row["bytes"], "sha256": row["sha256"]}
            for row in existing.receipt["page_decisions"]
        }
        requested_pages = {
            row["path"]: file_identity(decisions_root / row["path"])
            for row in decision_data["decisions"]
        }
        if requested_pages != expected_pages or file_identity(allow_path) != {
            "bytes": existing.receipt["reviewed_allowlist"]["bytes"],
            "sha256": existing.receipt["reviewed_allowlist"]["sha256"],
        }:
            raise ReplayResumeError("existing submission differs from requested evidence")
        return existing
    operation = uuid.uuid4().hex
    staging = final.parent / f".{final.name}.stage-{operation}"
    staging.mkdir()
    try:
        _copy_new(decision_set, staging / "decision_set.json")
        for row in decision_data["decisions"]:
            _copy_new(decisions_root / row["path"], staging / row["path"])
        _copy_new(allow_path, staging / "reviewed_allowlist.json")
        inventory = deterministic_inventory(staging)
        run = _json(review.run_root / "run.json")
        receipt = sealed(SUBMISSION_SCHEMA, {
            "run_identity_sha256": run["portable_identity_sha256"], "bridge_sha256": authorities.bridge_sha256,
            "review_queue": {"path": "review/review_queue.json", **file_identity(review.queue_path), "queue_sha256": review.queue["queue_sha256"]},
            "contract_sha256": run["contract"]["sha256"], "source_sha256": run["source"]["sha256"],
            "decision_set": {"path": "decision_set.json", **file_identity(staging / "decision_set.json")},
            "page_decisions": [{"source_page": row["source_page"], "path": row["path"], **file_identity(staging / row["path"])} for row in decision_data["decisions"]],
            "reviewed_allowlist": {"path": "reviewed_allowlist.json", **file_identity(staging / "reviewed_allowlist.json"), "schema": ALLOWLIST_SCHEMA},
            "files": inventory, "files_sha256": sha256_bytes(canonical_bytes(inventory)), "acceptance_inferred": False,
        }, digest_key="submission_sha256")
        _write_new(staging / "submission_inventory.json", receipt)
        os.replace(staging, final)
    except Exception:
        if staging.exists(): shutil.rmtree(staging)
        raise
    return load_replay_submission(authorities)


def load_replay_submission(authorities: FreshReplayAuthorities) -> SubmissionAuthorities:
    root = authorities.run_root / "review/validated-submission-v2"
    receipt_path = root / "submission_inventory.json"
    receipt = _json(receipt_path)
    try: validate_seal(receipt, "submission_sha256")
    except ValueError as error: raise ReplayResumeError("submission seal mismatch") from error
    _closed(receipt, {"schema", "run_identity_sha256", "bridge_sha256", "review_queue", "contract_sha256", "source_sha256", "decision_set", "page_decisions", "reviewed_allowlist", "files", "files_sha256", "acceptance_inferred", "submission_sha256"}, "validated submission")
    if receipt["schema"] != SUBMISSION_SCHEMA or receipt["run_identity_sha256"] != _json(authorities.run_root / "run.json")["portable_identity_sha256"] or receipt["bridge_sha256"] != authorities.bridge_sha256 or receipt["acceptance_inferred"] is not False:
        raise ReplayResumeError("submission authority mismatch")
    observed = _inventory_without(root, {"submission_inventory.json"})
    if observed != receipt["files"] or sha256_bytes(canonical_bytes(observed)) != receipt["files_sha256"]:
        raise ReplayResumeError("submission inventory mismatch")
    decision_set = root / receipt["decision_set"]["path"]
    allowlist = root / receipt["reviewed_allowlist"]["path"]
    if file_identity(decision_set) != {"bytes": receipt["decision_set"]["bytes"], "sha256": receipt["decision_set"]["sha256"]} or file_identity(allowlist) != {"bytes": receipt["reviewed_allowlist"]["bytes"], "sha256": receipt["reviewed_allowlist"]["sha256"]}:
        raise ReplayResumeError("submission file identity mismatch")
    review = validate_replay_review_queue(authorities)
    _validate_allowlist(allowlist, review, authorities)
    return SubmissionAuthorities(root, receipt_path, receipt, root, decision_set, allowlist)


def _visual_inventory(run_root: Path, visual: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    schema = visual.get("schema")
    if schema not in {"kb_creator.mineru_visual_merge_bundle.v2", "kb_creator.mineru_visual_merge_bundle.v3"}:
        raise ReplayResumeError("visual inventory schema mismatch")
    result: dict[str, dict[str, Any]] = {}
    identities: set[str] = set()
    for row in visual.get("files", []):
        if not isinstance(row, dict):
            raise ReplayResumeError("visual inventory shape mismatch")
        is_png = isinstance(row.get("path"), str) and row["path"].casefold().endswith(".png")
        expected = {"path", "bytes", "sha256"}
        if schema == "kb_creator.mineru_visual_merge_bundle.v2" and is_png:
            expected.add("dimensions")
        if set(row) != expected:
            raise ReplayResumeError("visual inventory shape mismatch")
        if schema == "kb_creator.mineru_visual_merge_bundle.v2" and is_png:
            dimensions = row["dimensions"]
            if (
                not isinstance(dimensions, list)
                or len(dimensions) != 2
                or any(type(value) is not int or value <= 0 for value in dimensions)
            ):
                raise ReplayResumeError("visual inventory dimensions mismatch")
        full = f"outputs/04-visual-merge-bundle/{row['path']}"
        identity_key = full.casefold()
        if identity_key in identities:
            raise ReplayResumeError("visual inventory contains duplicate paths")
        identities.add(identity_key)
        result[full] = {"bytes": row["bytes"], "sha256": row["sha256"]}
        path = run_root / full
        if not path.is_file() or file_identity(path) != result[full]:
            raise ReplayResumeError("visual inventory identity mismatch")
    from kb_creator.pipeline.reconstruction_asset_inventory import selected_asset_inventory
    return selected_asset_inventory(run_root, result)


def build_replay_audit(authorities: FreshReplayAuthorities, submission: SubmissionAuthorities) -> dict[str, Any]:
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v3_content, audit_v4_content
    review = validate_replay_review_queue(authorities)
    comparison = _json(review.comparison_path)
    geometry = _json(authorities.geometry_plan) if authorities.geometry_plan else {}
    visual = _json(authorities.visual_manifest) if authorities.visual_manifest else {}
    allowlist = _validate_allowlist(submission.allowlist_path, review, authorities)
    packets, decisions, packet_authorities = {}, {}, []
    bundle = authorities.run_root / "outputs/04-visual-merge-bundle"
    for item in review.queue["items"]:
        page = item["source_page"]
        packet_path = bundle / item["merge_packet"]["path"]
        packet = _json(packet_path)
        for view_id in comparison["required_views"]:
            expected = [block for block in comparison["views"][view_id]["blocks"] if block.get("source_page") == page]
            if packet.get("views", {}).get(view_id, {}).get("blocks") != expected:
                raise ReplayResumeError("packet differs from comparison projection")
        packets[page] = packet
        decision_path = submission.root / f"pages/page-{page:03d}.json"
        decisions[page] = _json(decision_path)
        packet_authorities.append({"source_page": page, "path": f"outputs/04-visual-merge-bundle/{item['merge_packet']['path']}", **file_identity(packet_path)})
    run = _json(authorities.run_root / "run.json")
    report_authorities = {
        "run_identity_sha256": run["portable_identity_sha256"], "bridge_sha256": authorities.bridge_sha256,
        "submission_sha256": submission.receipt["submission_sha256"],
        "review_queue": {"path": "review/review_queue.json", **file_identity(review.queue_path), "queue_sha256": review.queue["queue_sha256"]},
        "comparison": {"path": "outputs/03-compare-views/comparison.json", **file_identity(review.comparison_path), "comparison_sha256": comparison["comparison_sha256"]},
        "geometry": {"path": "outputs/04-visual-merge-bundle/visual/geometry_plan.json", **file_identity(authorities.geometry_plan), "plan_sha256": geometry["plan_sha256"]},
        "visual_manifest": {"path": "outputs/04-visual-merge-bundle/visual/visual_manifest.json", **file_identity(authorities.visual_manifest), "manifest_sha256": visual["manifest_sha256"]},
        "decision_set": {"path": "review/validated-submission-v2/decision_set.json", **file_identity(submission.decision_set_path)},
        "reviewed_allowlist": {"path": "review/validated-submission-v2/reviewed_allowlist.json", **file_identity(submission.allowlist_path)},
        "packets": packet_authorities,
    }
    decision_set = _json(submission.decision_set_path)
    audit = audit_v4_content if decision_set.get("schema") == reconstruction.DECISION_SET_V2_SCHEMA else audit_v3_content
    has_source_render = any(
        any(isinstance(asset, dict) and asset.get("origin") == "source_pdf_page_render_v1" for asset in decision.get("assets", []))
        for decision in decisions.values()
    )
    if has_source_render:
        from kb_creator.pipeline.source_page_render import replay_source_render_context
        source_render_context = replay_source_render_context(authorities.run_root, geometry)
    else:
        source_render_context = None
    return audit(packets, decisions, allowlist=allowlist, geometry=geometry, visual_inventory=_visual_inventory(authorities.run_root, visual), authorities=report_authorities, source_render_context=source_render_context)


def _closure() -> dict[str, Any]:
    paths = [_repo_root() / path for path in DOWNSTREAM_IMPLEMENTATION]
    return implementation_inventory(_repo_root(), paths)


def _validate_post_publish_access(
    output: Path,
    expected_inventory: list[dict[str, Any]],
    callback: Callable[[Path], dict[str, object]],
) -> None:
    result = callback(output)
    if not isinstance(result, dict):
        raise ReplayResumeError("post-publish access normalization returned an invalid result")
    state = result.get("state")
    if state == "normalized":
        pass
    elif state == "skipped" and result.get("reason") in {
        "non_windows_host",
        "outside_managed_working_tree",
    }:
        pass
    else:
        raise ReplayResumeError("post-publish access normalization did not complete")
    if deterministic_inventory(output) != expected_inventory:
        raise ReplayResumeError("post-publish access normalization changed artifact bytes")


def _quarantine_fresh_stage(
    run_root: Path,
    stage_id: str,
    operation: str,
    output: Path,
    manifest_root: Path,
    original_error: Exception,
) -> None:
    quarantine = run_root / "failures" / f".{stage_id}-{operation}"
    try:
        quarantine.mkdir(parents=True, exist_ok=False)
        if output.exists():
            os.replace(output, quarantine / "output")
        if manifest_root.exists():
            os.replace(manifest_root, quarantine / "stage")
    except Exception as cleanup_error:
        residual = [str(path) for path in (output, manifest_root) if path.exists()]
        raise ReplayResumeError(
            f"{stage_id}: post-publish failure ({original_error}); quarantine failed "
            f"({cleanup_error}); residual paths: {residual}"
        ) from cleanup_error


def _publish_stage(
    run_root: Path,
    stage_id: str,
    build: Callable[[Path], dict[str, Any]],
    inputs: list[dict[str, Any]],
    upstream: list[dict[str, Any]],
    bridge_sha256: str,
    *,
    post_publish: Callable[[Path], dict[str, object]] | None = None,
) -> dict[str, Any]:
    output, manifest_root = run_root / "outputs" / stage_id, run_root / "stages" / stage_id
    if output.exists() or manifest_root.exists():
        if output.exists() != manifest_root.exists(): raise ReplayResumeError(f"{stage_id}: partial output/manifest pair")
        result = _validate_downstream_stage(run_root, stage_id, bridge_sha256, upstream)
        if post_publish is not None:
            expected = deterministic_inventory(output)
            _validate_post_publish_access(output, expected, post_publish)
            result = _validate_downstream_stage(run_root, stage_id, bridge_sha256, upstream)
        return result
    operation = uuid.uuid4().hex
    temp_output = run_root / "outputs" / f".{stage_id}.stage-{operation}"
    temp_stage = run_root / "stages" / f".{stage_id}.stage-{operation}"
    temp_output.parent.mkdir(parents=True, exist_ok=True)
    temp_stage.parent.mkdir(parents=True, exist_ok=True)
    temp_output.mkdir(); temp_stage.mkdir()
    try:
        result = build(temp_output)
        inventory = deterministic_inventory(temp_output)
        closure = _closure()
        command = sealed("kb_creator.replay_downstream_command.v1", {"stage_id": stage_id, "run_identity_sha256": _json(run_root / "run.json")["portable_identity_sha256"], "bridge_sha256": bridge_sha256, "producer_invoked": True, "acceptance_inferred": False}, digest_key="command_sha256")
        _write_new(temp_stage / "command.json", command)
        os.replace(temp_output, output)
        try:
            if post_publish is not None:
                _validate_post_publish_access(output, inventory, post_publish)
            manifest = sealed(STAGE_SCHEMA, {
                "stage_id": stage_id, "run_identity_sha256": _json(run_root / "run.json")["portable_identity_sha256"], "bridge_sha256": bridge_sha256,
                "execution": {"mode": "executed", "producer_invoked": True, "reusable": False, "completed_at_utc": _utc(), "exit_code": 0},
                "upstream": upstream, "inputs": inputs, "producer_closure": closure,
                "outputs": {"root": f"outputs/{stage_id}", "files": inventory, "inventory_sha256": sha256_bytes(canonical_bytes(inventory))},
                "command": {"path": f"stages/{stage_id}/command.json", **file_identity(temp_stage / "command.json"), "command_sha256": command["command_sha256"]},
                "result": result, "acceptance_inferred": False,
            }, digest_key="manifest_sha256")
            _write_new(temp_stage / "stage.json", manifest)
            os.replace(temp_stage, manifest_root)
            return _validate_downstream_stage(run_root, stage_id, bridge_sha256, upstream)
        except Exception as error:
            _quarantine_fresh_stage(run_root, stage_id, operation, output, manifest_root, error)
            raise
    except Exception:
        if temp_output.exists(): shutil.rmtree(temp_output)
        if temp_stage.exists(): shutil.rmtree(temp_stage)
        raise


def _validate_downstream_stage(run_root: Path, stage_id: str, bridge_sha256: str, upstream: list[dict[str, Any]]) -> dict[str, Any]:
    manifest_path = run_root / "stages" / stage_id / "stage.json"
    manifest = _json(manifest_path)
    try: validate_seal(manifest, "manifest_sha256")
    except ValueError as error: raise ReplayResumeError(f"{stage_id}: manifest seal mismatch") from error
    _closed(manifest, {"schema", "stage_id", "run_identity_sha256", "bridge_sha256", "execution", "upstream", "inputs", "producer_closure", "outputs", "command", "result", "acceptance_inferred", "manifest_sha256"}, "downstream stage")
    run = _json(run_root / "run.json")
    if manifest["schema"] != STAGE_SCHEMA or manifest["stage_id"] != stage_id or manifest["run_identity_sha256"] != run["portable_identity_sha256"] or manifest["bridge_sha256"] != bridge_sha256 or manifest["upstream"] != upstream or manifest["execution"].get("mode") != "executed" or manifest["execution"].get("producer_invoked") is not True or manifest["execution"].get("reusable") is not False or manifest["acceptance_inferred"] is not False:
        raise ReplayResumeError(f"{stage_id}: stage authority mismatch")
    observed = deterministic_inventory(run_root / "outputs" / stage_id)
    if observed != manifest["outputs"]["files"] or sha256_bytes(canonical_bytes(observed)) != manifest["outputs"]["inventory_sha256"]:
        raise ReplayResumeError(f"{stage_id}: output inventory mismatch")
    if _closure() != manifest["producer_closure"]:
        raise ReplayResumeError(f"{stage_id}: producer closure drift")
    return {"stage_id": stage_id, "manifest_sha256": manifest["manifest_sha256"], "output_inventory_sha256": manifest["outputs"]["inventory_sha256"]}


def replay_downstream_adapters(authorities: FreshReplayAuthorities, submission: SubmissionAuthorities) -> dict[str, Callable[[Path], dict[str, Any]]]:
    def audit_adapter(output: Path) -> dict[str, Any]:
        report = build_replay_audit(authorities, submission)
        _write_new(output / "audit.json", report)
        if report["passed"] is not True:
            raise ReplayResumeError("Stage05 fidelity audit did not pass")
        return {"state": "fidelity_passed", "audit": {"path": "audit.json", **file_identity(output / "audit.json")}}

    def materialize_adapter(output: Path) -> dict[str, Any]:
        from kb_creator.scripts.materialize_mineru_ai_merge import materialize
        audit_path = authorities.run_root / "outputs/05-fidelity-audit/audit.json"
        result = materialize(
            authorities.run_root / "outputs/04-visual-merge-bundle", authorities.stage_02_root, submission.decisions_root / "pages", output,
            fidelity_audit=audit_path, fidelity_audit_sha256=file_identity(audit_path)["sha256"],
            replay_run_root=authorities.run_root, replay_bridge_sha256=authorities.bridge_sha256,
            replay_submission=submission.receipt_path, replay_submission_sha256=file_identity(submission.receipt_path)["sha256"],
        )
        provenance = _json(output / "MERGE_PROVENANCE.json")
        if provenance.get("schema") != PROVENANCE_SCHEMA or provenance.get("acceptance_inferred") is not False:
            raise ReplayResumeError("Stage06 replay provenance mismatch")
        return result

    return {"fidelity_audit": audit_adapter, "materialize_candidate": materialize_adapter}


def replay_resume_engine(run_root: Path, decision_set: Path, decisions_root: Path, *, adapters: Mapping[str, Callable[[Path], dict[str, Any]]] | None = None) -> dict[str, Any]:
    # A native v2 Stage04 is valid only when its hybrid completion validates
    # the executed Stage04 edge. Full v3 replay retains its established prefix
    # validator and keeps testable direct-v3 compatibility.
    authorities = (
        validate_replay_authorities(run_root)
        if (run_root / "replay/completion.json").is_file()
        else validate_replayed_prefix(run_root)
    )
    review = validate_replay_review_queue(authorities)
    submission = materialize_replay_submission_snapshot(authorities, decision_set, decisions_root)
    active = dict(adapters or replay_downstream_adapters(authorities, submission))
    if set(active) != {"fidelity_audit", "materialize_candidate"}:
        raise ReplayResumeError("replay downstream adapter set mismatch")
    submission_input = {"path": "review/validated-submission-v2/submission_inventory.json", **file_identity(submission.receipt_path), "submission_sha256": submission.receipt["submission_sha256"]}
    bridge_input = {"path": "replay/bridge.json", **file_identity(review.bridge_path), "bridge_sha256": authorities.bridge_sha256}
    stage5 = _publish_stage(run_root, STAGES[0], active["fidelity_audit"], [bridge_input, submission_input], [], authorities.bridge_sha256)
    audit_path = run_root / "outputs/05-fidelity-audit/audit.json"
    audit = _json(audit_path)
    expected_audit = AUDIT_V4_SCHEMA if _json(submission.decision_set_path).get("schema") == reconstruction.DECISION_SET_V2_SCHEMA else AUDIT_SCHEMA
    if audit.get("schema") != expected_audit or audit.get("passed") is not True or audit.get("errors") != []:
        raise ReplayResumeError("Stage05 passing audit authority is missing")
    audit_input = {"path": "outputs/05-fidelity-audit/audit.json", **file_identity(audit_path)}
    stage6 = _publish_stage(
        run_root, STAGES[1], active["materialize_candidate"],
        [bridge_input, submission_input, audit_input], [stage5], authorities.bridge_sha256,
        post_publish=normalize_publication_access_if_managed,
    )
    result = {
        "state": "candidate_ready_for_reconstruction_qa", "run_identity_sha256": _json(run_root / "run.json")["portable_identity_sha256"],
        "bridge_sha256": authorities.bridge_sha256, "submission_sha256": submission.receipt["submission_sha256"],
        "stages": [stage5, stage6], "candidate_root": "outputs/06-materialize-candidate", "acceptance_inferred": False, "exit_code": 0,
    }
    return {"schema": RESULT_SCHEMA, **result}
