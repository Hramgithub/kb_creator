"""Intake and reconstruction bridge for the explicit five-step DOCX profile.

This module deliberately keeps ``agent_reviewed`` separate from the historic
user-acceptance vocabulary.  It reuses the reconstruction control plane, but
does not manufacture an acceptance receipt for it.
"""
from __future__ import annotations

import json
import tempfile
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from . import reconstruction, reconstruction_promotion, reconstruction_replay, reconstruction_replay_resume
from .identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes
from .manifests import sealed, validate_seal
from .semantic_structure import apply_block_boundaries
from .reader_occurrence_projection import (
    ReaderOccurrenceError,
    build_issue_en_bindings_v2,
    load_issue_en_bindings_v2,
)


INTAKE_SCHEMA = "kb_creator.five_step_intake.v1"
SUBMISSION_SCHEMA = "kb_creator.five_step_intake_submission.v1"
AUTHORITY_SCHEMA = "kb_creator.agent_review_authority.v1"
MASTER_SCHEMA = "kb_creator.five_step_master_en.v1"
MASTER_MANIFEST_SCHEMA = "kb_creator.five_step_master_en_manifest.v1"
REVIEW_MASTER_SCHEMA = "kb_creator.review_master_en.v1"
REVIEW_MASTER_MANIFEST_SCHEMA = "kb_creator.review_master_en_manifest.v1"
REVIEW_MATERIALIZATION_SCHEMA = "kb_creator.review_draft_materialization.v1"
ISSUE_EN_BINDINGS_SCHEMA = "kb_creator.issue_en_bindings.v1"
SAFE_SCENARIO_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class FiveStepIntakeError(ValueError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FiveStepIntakeError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise FiveStepIntakeError("JSON root must be an object")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _exact(value: Mapping[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise FiveStepIntakeError(f"{label} has unexpected or missing fields")


def _new_root(destination: Path) -> Path:
    if destination.exists():
        raise FiveStepIntakeError(f"immutable destination already exists: {destination}")
    if not destination.parent.is_dir():
        raise FiveStepIntakeError(f"destination parent is absent: {destination.parent}")
    stage = destination.parent / f".{destination.name}.staging"
    if stage.exists():
        raise FiveStepIntakeError(f"staging residue exists: {stage}")
    stage.mkdir()
    return stage


def _publish(stage: Path, destination: Path) -> None:
    try:
        os.rename(stage, destination)
    except OSError as error:
        raise FiveStepIntakeError(f"could not atomically publish {destination}") from error


def _working_root_from_run(run_root: Path) -> Path:
    """Derive the promotion working root from the profile-contained run layout."""
    resolved = run_root.resolve(strict=True)
    if resolved.parent.name != "reconstruction" or not SAFE_SCENARIO_ID.fullmatch(resolved.parent.parent.name):
        raise FiveStepIntakeError("reconstruction run must be under <working>/<scenario>/reconstruction/<run>")
    return resolved.parent.parent.parent


def _working_root_from_package(package: Path) -> Path:
    resolved = package.resolve(strict=True)
    if resolved.name != reconstruction_promotion.PACKAGE_NAME or resolved.parent.name != "promotion":
        raise FiveStepIntakeError("reconstruction package has an invalid promotion topology")
    return _working_root_from_run(resolved.parent.parent)


def _source(source: Path) -> dict[str, Any]:
    if not source.is_file():
        raise FiveStepIntakeError("source is not a file")
    try:
        geometry = reconstruction._source_pdf_geometry(source)
    except reconstruction.ControlPlaneError as error:
        raise FiveStepIntakeError(str(error)) from error
    return {**file_identity(source), **geometry}


def _source_contract(source: Mapping[str, Any]) -> dict[str, Any]:
    result = {"sha256": source["sha256"], "byte_count": source["bytes"], "page_count": source["page_count"]}
    if "page_geometry" in source:
        result["page_geometry"] = source["page_geometry"]
    else:
        result.update(media_box_points=source["media_box_points"], rotation_degrees=source["rotation_degrees"])
    return result


def _passport(source: Path, title: str | None) -> dict[str, Any]:
    observed = _source(source)
    return sealed(INTAKE_SCHEMA, {
        "state": "needs_agent_work", "source": {"basename": source.name, **observed},
        "source_path": str(source.resolve()),
        "title_hint": title, "draft_page_coverage": [
            {"source_page": page, "role": "unknown", "provisional_entity_count": 0,
             "entity_count_state": "pending_review"}
            for page in range(1, observed["page_count"] + 1)
        ],
        "constraints": {
            "scope": "all_source_pages", "unrecorded_exclusions_allowed": False,
            "semantic_fields_require_agent_review": True,
        },
    }, digest_key="intake_sha256")


def prepare_intake(source: Path, output_root: Path, *, title: str | None = None) -> dict:
    """Create an immutable, source-derived intake passport and contract task."""
    if title is not None and (not isinstance(title, str) or not title.strip()):
        raise FiveStepIntakeError("title must be a non-empty string when supplied")
    stage = _new_root(output_root)
    try:
        passport = _passport(source, title)
        _write(stage / "passport.json", passport)
        template = {
            "schema": SUBMISSION_SCHEMA, "passport_sha256": passport["intake_sha256"],
            "source": _source_contract(passport["source"]),
            "contract": {
                "scenario": {"id": "replace-with-source-specific-id", "title": title},
                "scope": {"mode": "all_source_pages", "first_page": 1,
                          "last_page": passport["source"]["page_count"],
                          "required_entities": {"numbered_player_handouts": 0}},
                "page_roles": [],
                "reconstruction": {"strategies": [], "required_review": True},
                "acceptance": {"approval_authority": "configured_reconstruction_review"},
            },
        }
        _write(stage / "intake-submission.template.json", template)
        v3_template = {
            **template,
            "contract": {
                **template["contract"],
                "contract_revision": 3,
                "scope": {
                    "mode": "all_source_pages",
                    "first_page": 1,
                    "last_page": passport["source"]["page_count"],
                    "required_entities": {"handout_label_sets": [
                        {"scope_id": "replace-with-reviewed-scope-id", "labels": [
                            {"label": "replace-with-source-visible-label", "occurrences": [
                                {"source_page": 1, "section": "body"}
                            ]}
                        ]}
                    ]},
                },
            },
        }
        _write(stage / "intake-submission.v3.template.json", v3_template)
        task = {
            "schema": "kb_creator.five_step_intake_task.v1", "state": "needs_agent_work",
            "passport": {"path": "passport.json", **file_identity(stage / "passport.json")},
            "template": {"path": "intake-submission.template.json", **file_identity(stage / "intake-submission.template.json")},
            "v3_template": {"path": "intake-submission.v3.template.json", **file_identity(stage / "intake-submission.v3.template.json")},
            "instructions": [
                "Review every source page and provide a source-specific semantic contract.",
                "Close all page roles contiguously; record all exclusions as page roles and decisions.",
                "Do not infer title, handouts, cover, credits, or topology from another scenario.",
            ],
        }
        _write(stage / "intake.task.json", task)
        _publish(stage, output_root)
    except Exception:
        if stage.exists(): shutil.rmtree(stage)
        raise
    return {"state": "needs_agent_work", "task_path": str(output_root / "intake.task.json"),
            "template_path": str(output_root / "intake-submission.template.json"),
            "passport_path": str(output_root / "passport.json")}


def _validate_submission(intake_root: Path, submission: Path) -> dict[str, Any]:
    passport = _read(intake_root / "passport.json")
    try: validate_seal(passport, "intake_sha256")
    except ValueError as error: raise FiveStepIntakeError("invalid intake passport seal") from error
    value = _read(submission)
    _exact(passport, {"schema", "state", "source", "source_path", "title_hint", "draft_page_coverage", "constraints", "intake_sha256"}, "intake passport")
    _exact(value, {"schema", "passport_sha256", "source", "contract"}, "intake submission")
    if value["schema"] != SUBMISSION_SCHEMA or value["passport_sha256"] != passport["intake_sha256"]:
        raise FiveStepIntakeError("stale intake submission")
    if value["source"] != _source_contract(passport["source"]):
        raise FiveStepIntakeError("source fields do not exactly match passport")
    source_path = Path(str(passport["source_path"]))
    expected_source = {key: passport["source"][key] for key in ("bytes", "sha256", "page_count")}
    expected_source.update({key: passport["source"][key] for key in ("page_geometry",) if key in passport["source"]})
    expected_source.update({key: passport["source"][key] for key in ("media_box_points", "rotation_degrees") if key in passport["source"]})
    if not source_path.is_file() or _source(source_path) != expected_source:
        raise FiveStepIntakeError("source changed after intake")
    contract = value["contract"]
    if not isinstance(contract, dict): raise FiveStepIntakeError("contract is invalid")
    if not isinstance(contract, dict) or set(contract) not in ({"scenario", "scope", "page_roles", "reconstruction", "acceptance"}, {"contract_revision", "scenario", "scope", "page_roles", "reconstruction", "acceptance"}):
        raise FiveStepIntakeError("submitted contract has unexpected or missing fields")
    scenario = contract["scenario"]
    if not isinstance(scenario, dict) or set(scenario) != {"id", "title"} or not SAFE_SCENARIO_ID.fullmatch(str(scenario.get("id"))) or not isinstance(scenario.get("title"), str) or not scenario["title"].strip():
        raise FiveStepIntakeError("source-specific scenario id and title are required")
    requested_revision = contract.get("contract_revision")
    if requested_revision is not None and requested_revision != 3:
        raise FiveStepIntakeError("submitted contract revision is unsupported")
    complete = {"schema": reconstruction.CONTRACT_SCHEMA_V3 if requested_revision == 3 else reconstruction.CONTRACT_SCHEMA_V2 if "page_geometry" in value["source"] else reconstruction.CONTRACT_SCHEMA, "contract_revision": 3 if requested_revision == 3 else 2 if "page_geometry" in value["source"] else 1,
                "scenario": scenario, "source": value["source"], "scope": contract["scope"],
                "page_roles": contract["page_roles"], "reconstruction": contract["reconstruction"],
                "acceptance": contract["acceptance"]}
    try: return reconstruction.validate_contract(complete)
    except reconstruction.ControlPlaneError as error: raise FiveStepIntakeError(str(error)) from error


def submit_intake(intake_root: Path, submission: Path, output_root: Path) -> dict:
    """Seal a reviewed contract after rechecking immutable source identity."""
    contract = _validate_submission(intake_root, submission)
    passport = _read(intake_root / "passport.json")
    # The source is checked again by callers through ``start_reconstruction``;
    # retaining the exact passport binding prevents a stale submission here.
    stage = _new_root(output_root)
    try:
        _write(stage / "reconstruction-contract.json", contract)
        provenance = sealed("kb_creator.five_step_intake_submission_receipt.v1", {
            "passport": {"path": "../passport.json", **file_identity(intake_root / "passport.json")},
            "submission": {"basename": submission.name, **file_identity(submission)},
            "contract": {"path": "reconstruction-contract.json", **file_identity(stage / "reconstruction-contract.json")},
        }, digest_key="receipt_sha256")
        _write(stage / "submission-receipt.json", provenance)
        _publish(stage, output_root)
    except Exception:
        if stage.exists(): shutil.rmtree(stage)
        raise
    return {"state": "contract_ready", "contract_path": str(output_root / "reconstruction-contract.json")}


def start_reconstruction(contract: Path, source: Path, run_root: Path, run_id: str, runtime, *, replay_from: Path | None = None, recovery_plan: Path | None = None, archived_replay: bool = False) -> dict:
    """Run the existing 01-04 engine and expose its honest page-decision task."""
    try:
        if replay_from is not None and recovery_plan is not None:
            raise FiveStepIntakeError("replay and verified-view recovery are mutually exclusive")
        if archived_replay and replay_from is None:
            raise FiveStepIntakeError("archived replay requires replay origin")
        if replay_from is None:
            plan = None
            if recovery_plan is not None:
                from .mineru_view_recovery_plan import load_plan
                target = reconstruction.build_run_spec(contract, source, run_root, run_id, runtime)
                plan = load_plan(recovery_plan, source, target)
            result = reconstruction.run_engine(contract, source, run_root, run_id, runtime=runtime, recovery_plan=plan)
        else:
            if archived_replay:
                result = reconstruction_replay.replay_archived_run_engine(contract, source, replay_from, run_root, run_id, runtime)
                result["replayed_prefix"] = "03-compare-views"
                result["archived_replay"] = True
            else:
             # Prefer complete reuse when its full closure is still eligible.
            # Any fallback revalidates the entire selected prefix independently.
             through = "04-visual-merge-bundle"
             fallback_reason = None
             try:
                reconstruction_replay.verify_replay_source(contract, source, replay_from, through, runtime)
             except reconstruction_replay.ReplayError as error:
                fallback_reason = str(error)
                through = "03-compare-views"
                reconstruction_replay.verify_replay_source(contract, source, replay_from, through, runtime)
             result = reconstruction_replay.replay_run_engine(contract, source, replay_from, run_root, run_id, through, runtime)
             result["replayed_prefix"] = through
             result["executed_stages"] = ["04-visual-merge-bundle"] if through == "03-compare-views" else []
             result["full_prefix_ineligible_reason"] = fallback_reason
    except (reconstruction.ControlPlaneError, reconstruction_replay.ReplayError) as error:
        raise FiveStepIntakeError(str(error)) from error
    if result["state"] != "needs_review": return result
    queue = run_root / "review/review_queue.json"
    task = {"schema": "kb_creator.five_step_reconstruction_task.v1", "state": "needs_agent_work",
            "review_queue": {"path": "review/review_queue.json", **file_identity(queue)},
            "decision_template": {"path": "review/decision_set.template.json", **file_identity(run_root / "review/decision_set.template.json")},
            "instructions": ["Review every queued source page.", "Submit a closed decision for each page.",
                "Supply an explicit source-bound reviewed allowlist for excluded headers/footers or other non-reader units; prose review notes do not authorize exclusions.",
                "Replay requires reviewed allowlist v3 (including empty lists when nothing is excluded).",
                "Do not exclude a source page without recording it in the reviewed semantic decision."],}
    _write(run_root / "five-step-reconstruction.task.json", task)
    return {**result, "task_path": str(run_root / "five-step-reconstruction.task.json"),
            "template_path": str(run_root / "review/decision_set.template.json")}


def author_reconstruction_decision_set(run_root: Path, decision_paths: list[Path], output_root: Path, *, reviewed_allowlist: Path | None = None) -> dict:
    """Package reviewed per-page decisions into the engine's hash-bound set.

    This only computes identities and copies supplied decisions.  It never
    creates page decisions or closes unresolved review work on an agent's
    behalf.
    """
    try:
        run = reconstruction.load_run(run_root)
        if (run_root / "replay/bridge.json").is_file():
            authorities = reconstruction_replay.validate_replay_authorities(run_root)
            queue = reconstruction_replay_resume.validate_replay_review_queue(authorities).queue
        else:
            queue = reconstruction.validate_queue(run_root / "review" / "review_queue.json", run)
    except (reconstruction.ControlPlaneError, reconstruction_replay.ReplayError, reconstruction_replay_resume.ReplayResumeError) as error:
        raise FiveStepIntakeError(str(error)) from error
    stage = _new_root(output_root)
    try:
        expected = {row["source_page"] for row in queue["items"]}
        copied: dict[int, dict[str, Any]] = {}
        structure_schemas: set[str | None] = set()
        for source in decision_paths:
            value = _read(source)
            structure = value.get("semantic_structure")
            if structure is not None and not isinstance(structure, dict):
                raise FiveStepIntakeError("semantic_structure must be a reviewed object")
            structure_schemas.add(structure.get("schema") if structure else None)
            page = value.get("source_page")
            if not isinstance(page, int) or page in copied or page not in expected:
                raise FiveStepIntakeError("reviewed decisions must cover each queued page once")
            target = stage / "pages" / f"page-{page:03d}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            copied[page] = {"source_page": page, "path": f"pages/page-{page:03d}.json", **file_identity(target)}
        if set(copied) != expected:
            raise FiveStepIntakeError("reviewed decisions do not cover every queued page")
        profiles = {
            "kb_creator.page_semantic_structure.v1": "visually_reviewed_semantic_containers_v1",
            "kb_creator.page_semantic_structure.v2": "reviewed_role_outline_and_partitions_v2",
        }
        if len(structure_schemas) != 1 or any(schema is not None and schema not in profiles for schema in structure_schemas):
            raise FiveStepIntakeError("page decisions must use one complete semantic structure profile")
        structure_schema = next(iter(structure_schemas))
        decision_set = {
            "schema": reconstruction.DECISION_SET_SCHEMA,
            "review_queue_sha256": queue["queue_sha256"], "contract_sha256": queue["contract_sha256"],
            "source_sha256": queue["source_sha256"], "decisions": [copied[page] for page in sorted(copied)],
            "reviewed_allowlist": None, "submission_state": "submitted_for_validation",
        }
        if structure_schema is not None:
            decision_set.update(schema=reconstruction.DECISION_SET_V2_SCHEMA,
                                semantic_structure_profile=profiles[structure_schema])
        if reviewed_allowlist is not None:
            target = stage / "reviewed_allowlist.json"
            shutil.copyfile(reviewed_allowlist, target)
            decision_set["reviewed_allowlist"] = {"path": target.name, **file_identity(target)}
        _write(stage / "decision_set.json", decision_set)
        reconstruction.validate_decision_set(stage / "decision_set.json", queue, stage)
        _publish(stage, output_root)
    except Exception:
        if stage.exists(): shutil.rmtree(stage)
        raise
    return {"state": "decision_set_ready", "decision_set": str(output_root / "decision_set.json"),
            "decisions_root": str(output_root)}


def _agent_authority(run_root: Path, package: Path) -> dict[str, Any]:
    manifest = _read(package / reconstruction_promotion.MANIFEST_NAME)
    review = manifest["review"]
    evidence = [{"path": reconstruction_promotion.MANIFEST_NAME, **file_identity(package / reconstruction_promotion.MANIFEST_NAME)},
                review["queue"], review["decision_set"], *review["decisions"], manifest["fidelity"], manifest["qa"]]
    return sealed(AUTHORITY_SCHEMA, {
        "scenario_id": manifest["scenario"]["id"], "stage": "reconstruction",
        "source": _read(package / reconstruction_promotion.SOURCE_IDENTITY_NAME)["source"],
        "task": {"path": "five-step-reconstruction.task.json", **file_identity(run_root / "five-step-reconstruction.task.json")},
        "submission": review["decision_set"], "evidence": evidence,
        "reviewer_role": "codex_content_executor", "reviewed_at_utc": _utc_now(), "unresolved": [],
    }, digest_key="authority_sha256")


def finish_reconstruction(run_root: Path, decision_set: Path, decisions_root: Path) -> dict:
    """Resume 05-06, promote, and bind closed agent review without user acceptance."""
    if not (run_root / "five-step-reconstruction.task.json").is_file():
        raise FiveStepIntakeError("first-pass reconstruction task is absent")
    try:
        if (run_root / "replay/bridge.json").is_file():
            resumed = reconstruction_replay_resume.replay_resume_engine(run_root, decision_set, decisions_root)
        else:
            resumed = reconstruction.resume_engine(run_root, decision_set, decisions_root)
        working_root = _working_root_from_run(run_root)
        promoted = reconstruction_promotion.materialize_reconstruction_promotion(run_root, working_root=working_root)
        package = Path(promoted["package_root"])
        reconstruction_promotion.validate_reconstruction_package(package, require_acceptance=False, working_root=working_root)
    except (reconstruction.ControlPlaneError, reconstruction_promotion.ReconstructionPromotionError, reconstruction_replay.ReplayError, reconstruction_replay_resume.ReplayResumeError) as error:
        raise FiveStepIntakeError(str(error)) from error
    authority_path = run_root / "agent-review-authority.json"
    if authority_path.exists(): raise FiveStepIntakeError("agent review authority already exists")
    _write(authority_path, _agent_authority(run_root, package))
    return {"state": "agent_reviewed", "reconstruction_root": str(package),
            "reconstructed_en": str(package / "content/RECONSTRUCTED_EN.md"),
            "review_path": str(authority_path), "resume": resumed}


def _inventory_value(root: Path) -> dict[str, Any]:
    rows = deterministic_inventory(root)
    return {"schema": "kb_creator.candidate_inventory.v1", "rows": rows,
            "file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows),
            "inventory_sha256": sha256_bytes(canonical_bytes(rows))}


def _copy_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        if path.is_symlink(): raise FiveStepIntakeError("reconstruction contains a symlink")
        if path.is_file():
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            if file_identity(path) != file_identity(target): raise FiveStepIntakeError("copied semantic artifact changed")


def _validate_authority(package: Path, review_path: Path) -> dict[str, Any]:
    value = _read(review_path)
    _exact(value, {"schema", "scenario_id", "stage", "source", "task", "submission", "evidence", "reviewer_role", "reviewed_at_utc", "unresolved", "authority_sha256"}, "agent review authority")
    try: validate_seal(value, "authority_sha256")
    except ValueError as error: raise FiveStepIntakeError("agent review authority seal is invalid") from error
    manifest = _read(package / reconstruction_promotion.MANIFEST_NAME)
    source = _read(package / reconstruction_promotion.SOURCE_IDENTITY_NAME)["source"]
    expected_task = review_path.parent / "five-step-reconstruction.task.json"
    review = manifest.get("review")
    if not isinstance(review, dict):
        raise FiveStepIntakeError("promoted reconstruction review is invalid")
    expected_evidence = [{"path": reconstruction_promotion.MANIFEST_NAME, **file_identity(package / reconstruction_promotion.MANIFEST_NAME)},
                         review["queue"], review["decision_set"], *review["decisions"], manifest["fidelity"], manifest["qa"]]
    if (value["schema"] != AUTHORITY_SCHEMA or value["stage"] != "reconstruction" or
        value["scenario_id"] != manifest["scenario"]["id"] or value["source"] != source or
        value["unresolved"] != [] or value["reviewer_role"] != "codex_content_executor" or
        value["submission"] != review["decision_set"] or value["evidence"] != expected_evidence or
        not expected_task.is_file() or value["task"] != {"path": "five-step-reconstruction.task.json", **file_identity(expected_task)}):
        raise FiveStepIntakeError("agent review authority is stale or unresolved")
    return value


def _source_spans(master: Path, decisions: list[Path], root: Path) -> dict[str, Any]:
    """Bind reviewed page-local statblocks to exact global MASTER_EN lines."""
    text = master.read_text(encoding="utf-8")
    markers = list(re.finditer(r"^<!--\s*source-page-(\d{3,})\s*-->\s*$", text, re.M))
    pages = {int(match.group(1)): (match.end(), markers[i + 1].start() if i + 1 < len(markers) else len(text))
             for i, match in enumerate(markers)}
    spans = []
    for path in decisions:
        decision = _read(path)
        page = decision["source_page"]
        structure = decision.get("semantic_structure") or {}
        selected = [row for row in structure.get("units", []) if row.get("kind") == "statblock" and row.get("container_parent") is None]
        if not selected:
            continue
        if page not in pages or not isinstance(decision.get("markdown"), str):
            raise FiveStepIntakeError("typed source span lacks a corresponding page")
        lines = apply_block_boundaries(decision["markdown"], decision.get("block_boundaries")).splitlines()
        lo, hi = pages[page]
        for unit in selected:
            span = unit["markdown_span"]
            start, end = span["start_line"], span["end_line"]
            if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
                raise FiveStepIntakeError("typed source span range is invalid")
            body = "\n".join(lines[start - 1:end])
            digest = sha256_bytes(body.encode("utf-8"))
            if digest != span["sha256"]:
                raise FiveStepIntakeError("typed source span hash differs from reviewed decision")
            matches = list(re.finditer(re.escape(body), text[lo:hi]))
            if len(matches) != 1:
                raise FiveStepIntakeError("typed source span has no unique exact MASTER_EN projection")
            offset = lo + matches[0].start()
            if offset and text[offset - 1] != "\n":
                raise FiveStepIntakeError("typed source span is not line aligned")
            if offset + len(body) < len(text) and text[offset + len(body)] != "\n":
                raise FiveStepIntakeError("typed source span end is not line aligned")
            global_start = text[:offset].count("\n") + 1
            spans.append({"id": unit["id"], "kind": "statblock", "source_page": page,
                          "start_line": global_start, "end_line": global_start + len(body.splitlines()) - 1,
                          "sha256": digest, "decision": {"path": path.relative_to(root).as_posix(), **file_identity(path)}})
    spans.sort(key=lambda row: row["start_line"])
    if len({row["id"] for row in spans}) != len(spans) or any(a["end_line"] >= b["start_line"] for a, b in zip(spans, spans[1:])):
        raise FiveStepIntakeError("typed source spans overlap or repeat IDs")
    return sealed("kb_creator.five_step_en_source_spans.v1", {"master_en": {"path": "MASTER_EN.md", **file_identity(master)}, "spans": spans}, digest_key="spans_sha256")


def build_master_en(reconstruction_root: Path, review_path: Path, output_root: Path) -> dict:
    """Project a promoted reconstruction into a profile-local, verifiable MASTER_EN."""
    try: reconstruction_promotion.validate_reconstruction_package(reconstruction_root, require_acceptance=False, working_root=_working_root_from_package(reconstruction_root))
    except reconstruction_promotion.ReconstructionPromotionError as error: raise FiveStepIntakeError(str(error)) from error
    authority = _validate_authority(reconstruction_root, review_path)
    content = reconstruction_root / "content"
    master = content / "RECONSTRUCTED_EN.md"
    if not master.is_file(): raise FiveStepIntakeError("promoted reconstruction lacks MASTER_EN source")
    markers = [int(value) for value in re.findall(r"<!--\s*source-page-(\d{3})\s*-->", master.read_text(encoding="utf-8"), re.I)]
    page_count = authority["source"]["page_count"]
    if markers != list(range(1, page_count + 1)):
        raise FiveStepIntakeError("reconstructed EN does not preserve every source-page marker")
    stage = _new_root(output_root)
    try:
        shutil.copyfile(master, stage / "MASTER_EN.md")
        (stage / "evidence" / "reconstruction").mkdir(parents=True)
        shutil.copyfile(master, stage / "evidence" / "reconstruction" / "RECONSTRUCTED_EN.md")
        _copy_tree(content / "assets", stage / "assets")
        _copy_tree(content / "pages", stage / "pages")
        for name in ("ASSET_MANIFEST.json", "OVERLAY_SELECTION.json", reconstruction_promotion.SEMANTIC_STRUCTURE_NAME):
            path = content / name
            if path.is_file(): shutil.copyfile(path, stage / name)
        decisions = []
        source_manifest = _read(reconstruction_root / reconstruction_promotion.MANIFEST_NAME)
        for record in source_manifest["review"].get("decisions", []):
            source_path = (reconstruction_root / record["path"]).resolve(strict=True)
            if not source_path.is_relative_to(reconstruction_root.resolve()):
                raise FiveStepIntakeError("reviewed decision escapes reconstruction package")
            target = stage / "evidence" / "review" / source_path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target)
            decisions.append(target)
        _write(stage / "EN_SOURCE_SPANS.json", _source_spans(stage / "MASTER_EN.md", decisions, stage))
        disposition = {"schema": "kb_creator.five_step_source_disposition.v1", "pages": [
            {"page": page, "disposition": "reader", "decision": "closed_reconstruction_review"}
            for page in range(1, page_count + 1)
        ]}
        _write(stage / "SOURCE_DISPOSITION.json", disposition)
        provenance = {"schema": MASTER_SCHEMA, "scenario_id": authority["scenario_id"],
            "source": authority["source"], "reconstruction": {"basename": reconstruction_root.name, **file_identity(reconstruction_root / reconstruction_promotion.MANIFEST_NAME)},
            "agent_review": {"basename": review_path.name, **file_identity(review_path)},
            "marker_pages": markers, "semantic_sidecars": [p.name for p in stage.iterdir() if p.name in {"ASSET_MANIFEST.json", "OVERLAY_SELECTION.json", reconstruction_promotion.SEMANTIC_STRUCTURE_NAME}],
            "projection": "exact_reconstructed_en_copy_v1"}
        _write(stage / "MASTER_EN.provenance.json", provenance)
        inventory = _inventory_value(stage)
        _write(stage / "INVENTORY.json", inventory)
        manifest = sealed(MASTER_MANIFEST_SCHEMA, {"state": "agent_reviewed", "scenario_id": authority["scenario_id"],
            "master_en": {"path": "MASTER_EN.md", **file_identity(stage / "MASTER_EN.md")},
            "provenance": {"path": "MASTER_EN.provenance.json", **file_identity(stage / "MASTER_EN.provenance.json")},
            "inventory": {"path": "INVENTORY.json", **file_identity(stage / "INVENTORY.json")},
            "source_pages": markers, "excluded_pages": []}, digest_key="manifest_sha256")
        _write(stage / "MANIFEST.json", manifest)
        _publish(stage, output_root)
    except Exception:
        if stage.exists(): shutil.rmtree(stage)
        raise
    verify_master_en(output_root)
    return {"state": "verified", "master_en": str(output_root / "MASTER_EN.md"), "manifest_path": str(output_root / "MANIFEST.json")}


def verify_master_en(result_root: Path, *, binding_root: Path | None = None) -> dict[str, Any]:
    """Independently recompute local identity, page and semantic-sidecar closure."""
    manifest = _read(result_root / "MANIFEST.json")
    if manifest.get("schema") == REVIEW_MASTER_MANIFEST_SCHEMA:
        from .source_page_render import _reuse_rendered_pages
        with _reuse_rendered_pages():
            return _verify_review_master_en(result_root, manifest, binding_root=binding_root)
    _exact(manifest, {"schema", "state", "scenario_id", "master_en", "provenance", "inventory", "source_pages", "excluded_pages", "manifest_sha256"}, "MASTER_EN manifest")
    try: validate_seal(manifest, "manifest_sha256")
    except ValueError as error: raise FiveStepIntakeError("MASTER_EN manifest seal is invalid") from error
    if manifest["schema"] != MASTER_MANIFEST_SCHEMA or manifest["state"] != "agent_reviewed" or manifest["excluded_pages"] != []:
        raise FiveStepIntakeError("MASTER_EN state or page exclusion is invalid")
    for record, expected in ((manifest["master_en"], "MASTER_EN.md"), (manifest["provenance"], "MASTER_EN.provenance.json"), (manifest["inventory"], "INVENTORY.json")):
        _exact(record, {"path", "bytes", "sha256"}, "MASTER_EN artifact")
        if record["path"] != expected or file_identity(result_root / expected) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise FiveStepIntakeError("MASTER_EN artifact identity mismatch")
    inventory = _read(result_root / "INVENTORY.json")
    # INVENTORY cannot inventory itself: its rows are exactly the tree before it.
    observed_rows = [row for row in deterministic_inventory(result_root) if row["path"] not in {"INVENTORY.json", "MANIFEST.json"}]
    if inventory.get("schema") != "kb_creator.candidate_inventory.v1" or inventory.get("rows") != observed_rows or inventory.get("inventory_sha256") != sha256_bytes(canonical_bytes(observed_rows)):
        raise FiveStepIntakeError("MASTER_EN inventory mismatch")
    text = (result_root / "MASTER_EN.md").read_text(encoding="utf-8")
    pages = [int(value) for value in re.findall(r"<!--\s*source-page-(\d{3})\s*-->", text, re.I)]
    if pages != manifest["source_pages"] or pages != list(range(1, len(pages) + 1)):
        raise FiveStepIntakeError("MASTER_EN source-page coverage mismatch")
    provenance = _read(result_root / "MASTER_EN.provenance.json")
    if provenance.get("schema") != MASTER_SCHEMA or provenance.get("marker_pages") != pages or provenance.get("scenario_id") != manifest["scenario_id"]:
        raise FiveStepIntakeError("MASTER_EN provenance mismatch")
    for name in provenance.get("semantic_sidecars", []):
        if not isinstance(name, str) or not (result_root / name).is_file():
            raise FiveStepIntakeError("MASTER_EN semantic sidecar is missing")
    source_copy = result_root / "evidence" / "reconstruction" / "RECONSTRUCTED_EN.md"
    if not source_copy.is_file() or file_identity(source_copy) != file_identity(result_root / "MASTER_EN.md"):
        raise FiveStepIntakeError("MASTER_EN differs from archived reconstruction evidence")
    source_spans = _read(result_root / "EN_SOURCE_SPANS.json")
    observed_spans = _source_spans(result_root / "MASTER_EN.md", sorted((result_root / "evidence" / "review").glob("*.json")), result_root)
    if source_spans != observed_spans:
        raise FiveStepIntakeError("MASTER_EN reviewed source span projection mismatch")
    for reference in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        local = reference.split("#", 1)[0]
        if local and not local.startswith(("http://", "https://")):
            candidate = (result_root / local).resolve()
            try: candidate.relative_to(result_root.resolve())
            except ValueError as error: raise FiveStepIntakeError("MASTER_EN asset reference escapes result root") from error
            if not candidate.is_file(): raise FiveStepIntakeError("MASTER_EN references a missing local asset")
    return {"state": "verified", "master_en": str(result_root / "MASTER_EN.md"), "manifest_path": str(result_root / "MANIFEST.json")}
def _review_materialization_authority(materialized_root: Path, final_evidence: Path, binding_root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Check bound review inputs and copied materialization records afresh.

    The materialization manifest is an inventory, never the authority by
    itself.  It is bound to the supplied final evidence and every referenced
    input is reopened before a review MASTER_EN can be staged.
    """
    from .review_draft import validate_review_draft_evidence, validate_review_draft_input

    material = _read(materialized_root / "REVIEW_DRAFT_MATERIALIZATION.v1.json")
    _exact(material, {"schema", "state", "acceptance", "authority", "pages", "assets"}, "review materialization manifest")
    if material["schema"] != REVIEW_MATERIALIZATION_SCHEMA or material["state"] != "verified_review_draft_candidate" or material["acceptance"] != "pending":
        raise FiveStepIntakeError("review materialization state is invalid")
    authority = material["authority"]
    if not isinstance(authority, dict) or set(authority) != {"input", "final_evidence", "audit", "source", "renderer", "comparison", "review_queue"}:
        raise FiveStepIntakeError("review materialization authority is malformed")
    for name, record in authority.items():
        _exact(record, {"path", "bytes", "sha256"}, f"review materialization {name}")
        path = Path(record["path"])
        if not path.is_file() or file_identity(path) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise FiveStepIntakeError(f"review materialization {name} identity drift")
    final_evidence = Path(final_evidence)
    if not final_evidence.is_file() or file_identity(final_evidence) != {"bytes": authority["final_evidence"]["bytes"], "sha256": authority["final_evidence"]["sha256"]}:
        raise FiveStepIntakeError("review final evidence is not the bound materialization authority")
    evidence = validate_review_draft_evidence(_read(final_evidence))
    input_path = Path(authority["input"]["path"])
    review_input = validate_review_draft_input(_read(input_path))
    if evidence["input_sha256"] != review_input.sha256 or evidence["audit"] != _read(Path(authority["audit"]["path"])):
        raise FiveStepIntakeError("review evidence does not match bound input or audit")
    recomputed = _recompute_review_descriptor(final_evidence, authority, evidence, review_input, binding_root=binding_root)
    if any(recomputed[name] != authority[name] for name in authority):
        raise FiveStepIntakeError("review materialization authority differs from fresh recomputation")
    for row in material["pages"]:
        if not isinstance(row, dict) or set(row) != {"source_page", "decision_sha256"} or type(row["source_page"]) is not int:
            raise FiveStepIntakeError("review materialization page inventory is malformed")
        path = materialized_root / "decisions" / f"page-{row['source_page']:03d}.json"
        if not path.is_file() or file_identity(path)["sha256"] != row["decision_sha256"]:
            raise FiveStepIntakeError("review materialization decision identity drift")
    pages = [row["source_page"] for row in material["pages"]]
    if pages != sorted(set(pages)) or not pages:
        raise FiveStepIntakeError("review materialization pages are incomplete")
    assets = _read(materialized_root / "ASSET_MANIFEST.json")
    if assets.get("assets") != material["assets"]:
        raise FiveStepIntakeError("review materialization asset inventory drift")
    return material, evidence, review_input.value, recomputed


def _recompute_review_descriptor(final_evidence: Path, authority: dict[str, Any], evidence: dict[str, Any], review_input: Any, *, binding_root: Path | None = None) -> dict[str, Any]:
    """Reopen the producer authority without trusting a consumer inventory."""
    # Locate the authored snapshot from identities recorded by the final
    # evidence; guessing a descriptor root would make this boundary forgeable.
    authored_rows = evidence["authored"]
    decision_row = authored_rows.get("decision_set")
    if not isinstance(decision_row, dict) or not isinstance(decision_row.get("path"), str):
        raise FiveStepIntakeError("review final evidence lacks decision-set authority")
    candidates = []
    for path in final_evidence.parent.rglob(Path(decision_row["path"]).name):
        candidate = path.parent
        if all((candidate / row["path"]).is_file() and file_identity(candidate / row["path"]) == {"bytes": row["bytes"], "sha256": row["sha256"]}
               for row in authored_rows.values() if isinstance(row, dict) and set(row) == {"path", "bytes", "sha256"}):
            candidates.append(candidate)
    if len(candidates) != 1:
        raise FiveStepIntakeError("review authored authority cannot be uniquely located")
    input_path = Path(authority["input"]["path"])
    queue_path = Path(authority["review_queue"]["path"])
    if queue_path.name != "review_queue.json" or queue_path.parent.name != "review":
        raise FiveStepIntakeError("review queue topology cannot establish fresh authority")
    from .review_draft_materialization import ReviewDraftMaterializationError, verify_final_review_draft
    try:
        recomputed = verify_final_review_draft(run_root=queue_path.parent.parent, authored_root=candidates[0],
            input_path=input_path, evidence_path=final_evidence, binding_root=binding_root)
    except (ReviewDraftMaterializationError, ValueError) as error:
        raise FiveStepIntakeError(f"review materialization fresh authority failed: {error}") from error
    return recomputed


def _fresh_review_projection(materialized_root: Path, descriptor: dict[str, Any], scratch_root: Path, binding_root: Path | None = None) -> Path:
    """Regenerate the review materialization from sealed producer authority."""
    from kb_creator.scripts.materialize_mineru_ai_merge import materialize

    fresh = scratch_root / "materialized"
    materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                Path(descriptor["decisions_root"]), fresh,
                review_draft_authority=descriptor, review_draft_binding_root=binding_root)
    if deterministic_inventory(materialized_root) != deterministic_inventory(fresh):
        raise FiveStepIntakeError("review materialization differs from fresh authority projection")
    return fresh


def _semantic_issue_occurrence(master: Path, issue: dict[str, Any], window: str) -> tuple[int, int]:
    """Locate repeated text through the verified source unit, never first match.

    Build and verify callers have already copied/checked these decisions and
    assets against fresh materialization. Reproduce that same page projection
    before using its line offsets, including asset substitutions before a unit.
    """
    from kb_creator.scripts.materialize_mineru_ai_merge import _substitute_assets

    page, excerpt = issue["source_page"], issue["source_excerpt_en"]
    path = master.parent / "evidence" / "review" / f"page-{page:03d}.json"
    if not path.is_file():
        raise FiveStepIntakeError("repeated source issue lacks a verified semantic decision")
    decision = _read(path)
    selector = issue.get("source_selector", {}).get("mechanical_diagnostic", {})
    keys = selector.get("source_keys", [])
    if decision.get("source_page") != page or not keys:
        raise FiveStepIntakeError("repeated source issue lacks source keys for its page")
    selected = {(row.get("view"), row.get("raw_index")) for row in decision.get("selected_blocks", [])}
    source_keys = {(row.get("view"), row.get("raw_index")) for row in keys} & selected
    if not source_keys:
        raise FiveStepIntakeError("repeated source issue has no selected semantic source")
    markdown = apply_block_boundaries(decision["markdown"], decision.get("block_boundaries"))
    asset_path = master.parent / "ASSET_MANIFEST.json"
    assets = _read(asset_path).get("assets", []) if asset_path.is_file() else []
    stored = {}
    for asset in decision.get("assets", []):
        matches = {row["stored_path"] for row in assets
                   if row.get("logical_name") == asset.get("logical_name")
                   and row.get("view") == asset.get("view")
                   and row.get("source_path") == asset.get("source_path")}
        if len(matches) != 1:
            raise FiveStepIntakeError("semantic issue asset projection is ambiguous")
        stored[asset["logical_name"]] = matches.pop()
    rendered = _substitute_assets(markdown, stored, "")
    expected = "\n\n" + rendered.rstrip() + "\n"
    if window.rstrip("\n") != expected.rstrip("\n"):
        raise FiveStepIntakeError("semantic issue page differs from verified decision projection")
    lines = markdown.split("\n")
    locations = set()
    for unit in (decision.get("semantic_structure") or {}).get("units", []):
        unit_keys = {(row.get("view"), row.get("raw_index")) for row in unit.get("source_blocks", [])}
        if not source_keys.intersection(unit_keys):
            continue
        span = unit.get("markdown_span", {})
        start, end = span.get("start_line"), span.get("end_line")
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise FiveStepIntakeError("semantic issue unit has an invalid line span")
        body = "\n".join(lines[start - 1:end])
        if sha256_bytes(body.encode("utf-8")) != span.get("sha256"):
            raise FiveStepIntakeError("semantic issue unit span identity differs")
        prefix = "\n".join(lines[:start - 1]) + ("\n" if start > 1 else "")
        projected_body = _substitute_assets(body, stored, "")
        offset = 2 + len(_substitute_assets(prefix, stored, ""))
        matches = list(re.finditer(re.escape(excerpt), projected_body))
        if len(matches) == 1:
            locations.add((offset + matches[0].start(), offset + matches[0].end()))
    if len(locations) != 1:
        raise FiveStepIntakeError("source issue lacks one exact semantic occurrence")
    start, end = locations.pop()
    if window[start:end] != excerpt:
        raise FiveStepIntakeError("semantic issue occurrence projection differs")
    return start, end


def _ordered_issue_occurrence(issue: dict[str, Any], window: str, final_evidence: Path) -> tuple[int, int] | None:
    """Use Stage05's ordered selected-source mapping for ordinary prose.

    The audit rebuilds every selected packet block against the current decision
    Markdown.  It is therefore the appropriate source occurrence proof when a
    source-choice diagnostic has no semantic presentation unit.  Positions are
    compared in the normalized audit stream, never chosen by a first prose hit.
    """
    try:
        evidence = _read(final_evidence)
        record = evidence["authored"]["stage05_audit"]
        path = final_evidence.parent / record["path"]
        if not path.is_file() or file_identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
            raise ValueError("audit identity drift")
        audit = _read(path)
        page = issue["source_page"]
        report = next(row for row in audit.get("pages", []) if row.get("source_page") == page)
        selector = issue.get("source_selector", {})
        if issue.get("kind") == "source_structure_role_pending":
            from .structural_role_issues import selected_source_key
            key = selected_source_key(issue)
            if key is None:
                raise ValueError("structural issue source key is invalid")
            keys = {key}
        else:
            rows = selector["mechanical_diagnostic"]["source_keys"]
            keys = {(row["view"], row["raw_index"]) for row in rows}
        mappings = [row for row in report.get("ordered_proof_stream", [])
                    if row.get("kind") == "selected"
                    and (row.get("unit", {}).get("view_id"), row.get("unit", {}).get("raw_index")) in keys]
        if len(mappings) != 1:
            return None
        span = mappings[0].get("markdown_span")
        if not isinstance(span, list) or len(span) != 2 or any(type(value) is not int for value in span) or span[0] < 0 or span[0] >= span[1]:
            raise ValueError("audit ordered source span is malformed")
    except (KeyError, StopIteration, TypeError, ValueError):
        return None
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _normalized
    excerpt = issue["source_excerpt_en"]
    candidates = []
    for match in re.finditer(re.escape(excerpt), window):
        start = len(_normalized(window[:match.start()]))
        end = len(_normalized(window[:match.end()]))
        if span[0] <= start < end <= span[1]:
            candidates.append((match.start(), match.end()))
    if len(candidates) != 1:
        return None
    return candidates[0]


def _issue_en_bindings(master: Path, source_issues: list[dict[str, Any]], pages: list[int], final_evidence: Path) -> dict[str, Any]:
    text = master.read_text(encoding="utf-8")
    markers = list(re.finditer(r"^<!--[ \t]*source-page-(\d{3,})[ \t]*-->[ \t]*$", text, re.M))
    windows = {int(match.group(1)): (match.end(), markers[index + 1].start() if index + 1 < len(markers) else len(text))
               for index, match in enumerate(markers)}
    bindings = []
    issue_ids: set[str] = set()
    for issue in source_issues:
        page, excerpt = issue["source_page"], issue["source_excerpt_en"]
        if page not in pages or page not in windows or sha256_bytes(excerpt.encode("utf-8")) != issue["source_excerpt_sha256"]:
            raise FiveStepIntakeError("source issue cannot be projected to MASTER_EN")
        lo, hi = windows[page]
        matches = list(re.finditer(re.escape(excerpt), text[lo:hi]))
        if len(matches) > 1:
            ordered = _ordered_issue_occurrence(issue, text[lo:hi], final_evidence)
            local_start, local_end = (ordered if ordered is not None
                                      else _semantic_issue_occurrence(master, issue, text[lo:hi]))
            start, end = lo + local_start, lo + local_end
        elif len(matches) == 1:
            start, end = lo + matches[0].start(), lo + matches[0].end()
        else:
            raise FiveStepIntakeError("source issue lacks a unique visible MASTER_EN span")
        # Different sealed source issues may address one exact occurrence (for
        # example lexical source choice plus structural role disagreement).
        # Keep their individual provenance rows; only duplicate issue IDs are
        # invalid and are already rejected by the sealed input validator.
        if issue["issue_id"] in issue_ids:
            raise FiveStepIntakeError("source issue ID is duplicated in MASTER_EN projection")
        issue_ids.add(issue["issue_id"])
        bindings.append({"issue_id": issue["issue_id"], "source_page": page,
                         "source_selector": issue["source_selector"],
                         "character_start": start, "character_end": end,
                         "byte_start": len(text[:start].encode("utf-8")), "byte_end": len(text[:end].encode("utf-8")),
                         "text_sha256": sha256_bytes(excerpt.encode("utf-8"))})
    return sealed(ISSUE_EN_BINDINGS_SCHEMA, {"master_en": {"path": "MASTER_EN.md", **file_identity(master)},
                                               "final_evidence": {"path": str(final_evidence.resolve()), **file_identity(final_evidence)},
                                               "bindings": bindings}, digest_key="bindings_sha256")


def build_review_master_en(materialized_root: Path, final_evidence: Path, output_root: Path, *, binding_root: Path | None = None) -> dict[str, Any]:
    """Copy a verified review-draft reconstruction without promoting it."""
    materialized_root = Path(materialized_root).resolve()
    material, evidence, review_input, descriptor = _review_materialization_authority(materialized_root, Path(final_evidence), binding_root)
    projection_parent = Path(tempfile.mkdtemp(prefix="review-master-projection-"))
    try:
        projection = _fresh_review_projection(materialized_root, descriptor, projection_parent, binding_root)
        return _build_review_master_from_projection(projection, material, evidence, final_evidence, output_root, binding_root=binding_root)
    finally:
        shutil.rmtree(projection_parent, ignore_errors=True)


def _build_review_master_from_projection(projection: Path, material: dict[str, Any], evidence: dict[str, Any], final_evidence: Path, output_root: Path, *, binding_root: Path | None = None) -> dict[str, Any]:
    reconstructed = projection / "RECONSTRUCTED_EN.md"
    if not reconstructed.is_file():
        raise FiveStepIntakeError("review materialization lacks RECONSTRUCTED_EN")
    text = reconstructed.read_text(encoding="utf-8")
    pages = [int(value) for value in re.findall(r"<!--\s*source-page-(\d{3})\s*-->", text, re.I)]
    if pages != [row["source_page"] for row in material["pages"]] or pages != list(range(1, len(pages) + 1)):
        raise FiveStepIntakeError("review reconstruction marker coverage is invalid")
    stage = _new_root(output_root)
    try:
        shutil.copyfile(reconstructed, stage / "MASTER_EN.md")
        (stage / "evidence" / "reconstruction").mkdir(parents=True)
        shutil.copyfile(reconstructed, stage / "evidence" / "reconstruction" / "RECONSTRUCTED_EN.md")
        # The review materializer permits a page set with no extracted assets.
        # Keep the MASTER_EN tree shape stable so fresh verification can inventory
        # the corresponding empty directory.
        (stage / "assets").mkdir(parents=True, exist_ok=True)
        _copy_tree(projection / "assets", stage / "assets")
        _copy_tree(projection / "pages", stage / "pages")
        for name in ("ASSET_MANIFEST.json", "OVERLAY_SELECTION.json", "SEMANTIC_STRUCTURE.json", "MERGE_PROVENANCE.json", "REVIEW_DRAFT_MATERIALIZATION.v1.json"):
            path = projection / name
            if path.is_file(): shutil.copyfile(path, stage / name)
        decisions = []
        for page in pages:
            source = projection / "decisions" / f"page-{page:03d}.json"
            target = stage / "evidence" / "review" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target); decisions.append(target)
        _write(stage / "EN_SOURCE_SPANS.json", _source_spans(stage / "MASTER_EN.md", decisions, stage))
        try:
            bindings = build_issue_en_bindings_v2(stage / "MASTER_EN.md", evidence["source_issues"]["issues"], pages, Path(final_evidence))
        except ReaderOccurrenceError as error:
            raise FiveStepIntakeError(str(error)) from error
        _write(stage / "ISSUE_EN_BINDINGS.v2.json", bindings)
        _write(stage / "SOURCE_DISPOSITION.json", {"schema": "kb_creator.five_step_source_disposition.v1", "pages": [
            {"page": page, "disposition": "reader", "decision": "verified_review_draft"} for page in pages]})
        provenance = {"schema": REVIEW_MASTER_SCHEMA, "scenario_id": "review-draft",
            "source": material["authority"]["source"], "final_evidence": material["authority"]["final_evidence"],
            "materialization": {"path": "REVIEW_DRAFT_MATERIALIZATION.v1.json", **file_identity(stage / "REVIEW_DRAFT_MATERIALIZATION.v1.json")},
            "marker_pages": pages, "semantic_sidecars": [name for name in ("ASSET_MANIFEST.json", "OVERLAY_SELECTION.json", "SEMANTIC_STRUCTURE.json") if (stage / name).is_file()],
            "projection": "exact_reconstructed_en_copy_v1", "acceptance": "pending"}
        _write(stage / "MASTER_EN.provenance.json", provenance)
        _write(stage / "INVENTORY.json", _inventory_value(stage))
        manifest = sealed(REVIEW_MASTER_MANIFEST_SCHEMA, {"state": "verified_review_draft", "acceptance": "pending", "scenario_id": "review-draft",
            "master_en": {"path": "MASTER_EN.md", **file_identity(stage / "MASTER_EN.md")}, "provenance": {"path": "MASTER_EN.provenance.json", **file_identity(stage / "MASTER_EN.provenance.json")},
            "inventory": {"path": "INVENTORY.json", **file_identity(stage / "INVENTORY.json")}, "final_evidence": material["authority"]["final_evidence"],
            "materialization": {"path": "REVIEW_DRAFT_MATERIALIZATION.v1.json", **file_identity(stage / "REVIEW_DRAFT_MATERIALIZATION.v1.json")},
            "source_pages": pages, "excluded_pages": []}, digest_key="manifest_sha256")
        _write(stage / "MANIFEST.json", manifest); _publish(stage, output_root)
    except Exception:
        if stage.exists(): shutil.rmtree(stage)
        raise
    return verify_master_en(output_root, binding_root=binding_root)


def _verify_review_master_en(result_root: Path, manifest: dict[str, Any], *, binding_root: Path | None = None) -> dict[str, Any]:
    """Verify the closed review-draft branch without accepting or promoting it."""
    from .review_draft import validate_review_draft_evidence, validate_review_draft_input

    _exact(manifest, {"schema", "state", "acceptance", "scenario_id", "master_en", "provenance", "inventory", "final_evidence", "materialization", "source_pages", "excluded_pages", "manifest_sha256"}, "review MASTER_EN manifest")
    try: validate_seal(manifest, "manifest_sha256")
    except ValueError as error: raise FiveStepIntakeError("review MASTER_EN manifest seal is invalid") from error
    if manifest["schema"] != REVIEW_MASTER_MANIFEST_SCHEMA or manifest["state"] != "verified_review_draft" or manifest["acceptance"] != "pending" or manifest["scenario_id"] != "review-draft" or manifest["excluded_pages"] != []:
        raise FiveStepIntakeError("review MASTER_EN state is invalid")
    for record, expected in ((manifest["master_en"], "MASTER_EN.md"), (manifest["provenance"], "MASTER_EN.provenance.json"), (manifest["inventory"], "INVENTORY.json"), (manifest["materialization"], "REVIEW_DRAFT_MATERIALIZATION.v1.json")):
        _exact(record, {"path", "bytes", "sha256"}, "review MASTER_EN artifact")
        if record["path"] != expected or file_identity(result_root / expected) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise FiveStepIntakeError("review MASTER_EN artifact identity mismatch")
    evidence_path = Path(manifest["final_evidence"].get("path", ""))
    if not evidence_path.is_file() or file_identity(evidence_path) != {"bytes": manifest["final_evidence"].get("bytes"), "sha256": manifest["final_evidence"].get("sha256")}:
        raise FiveStepIntakeError("review MASTER_EN final evidence identity drift")
    evidence = validate_review_draft_evidence(_read(evidence_path))
    material = _read(result_root / "REVIEW_DRAFT_MATERIALIZATION.v1.json")
    _exact(material, {"schema", "state", "acceptance", "authority", "pages", "assets"}, "copied review materialization manifest")
    if material["schema"] != REVIEW_MATERIALIZATION_SCHEMA or material["state"] != "verified_review_draft_candidate" or material["acceptance"] != "pending" or material["authority"].get("final_evidence") != manifest["final_evidence"]:
        raise FiveStepIntakeError("review MASTER_EN materialization authority mismatch")
    input_row = material["authority"].get("input")
    if not isinstance(input_row, dict) or set(input_row) != {"path", "bytes", "sha256"}:
        raise FiveStepIntakeError("review MASTER_EN input authority is malformed")
    input_path = Path(input_row["path"])
    if not input_path.is_file() or file_identity(input_path) != {"bytes": input_row["bytes"], "sha256": input_row["sha256"]}:
        raise FiveStepIntakeError("review MASTER_EN input authority drift")
    review_input = validate_review_draft_input(_read(input_path))
    if review_input.sha256 != evidence["input_sha256"]:
        raise FiveStepIntakeError("review MASTER_EN evidence binds another input")
    descriptor = _recompute_review_descriptor(evidence_path, material["authority"], evidence, review_input, binding_root=binding_root)
    inventory = _read(result_root / "INVENTORY.json")
    observed_rows = [row for row in deterministic_inventory(result_root) if row["path"] not in {"INVENTORY.json", "MANIFEST.json"}]
    if inventory.get("schema") != "kb_creator.candidate_inventory.v1" or inventory.get("rows") != observed_rows or inventory.get("inventory_sha256") != sha256_bytes(canonical_bytes(observed_rows)):
        raise FiveStepIntakeError("review MASTER_EN inventory mismatch")
    text = (result_root / "MASTER_EN.md").read_text(encoding="utf-8")
    pages = [int(value) for value in re.findall(r"<!--\s*source-page-(\d{3})\s*-->", text, re.I)]
    expected_pages = [row.get("source_page") for row in material["pages"] if isinstance(row, dict)]
    if pages != manifest["source_pages"] or pages != expected_pages or pages != list(range(1, len(pages) + 1)):
        raise FiveStepIntakeError("review MASTER_EN source-page coverage mismatch")
    for row in material["pages"]:
        path = result_root / "evidence" / "review" / f"page-{row['source_page']:03d}.json"
        if not path.is_file() or file_identity(path)["sha256"] != row["decision_sha256"]:
            raise FiveStepIntakeError("review MASTER_EN copied decision identity drift")
    source_copy = result_root / "evidence" / "reconstruction" / "RECONSTRUCTED_EN.md"
    if not source_copy.is_file() or file_identity(source_copy) != file_identity(result_root / "MASTER_EN.md"):
        raise FiveStepIntakeError("review MASTER_EN differs from reconstruction evidence")
    projection_parent = Path(tempfile.mkdtemp(prefix="review-master-verify-"))
    try:
        from kb_creator.scripts.materialize_mineru_ai_merge import materialize
        projection = projection_parent / "materialized"
        materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                    Path(descriptor["decisions_root"]), projection,
                    review_draft_authority=descriptor, review_draft_binding_root=binding_root)
        if file_identity(result_root / "MASTER_EN.md") != file_identity(projection / "RECONSTRUCTED_EN.md"):
            raise FiveStepIntakeError("review MASTER_EN differs from fresh authority projection")
        if file_identity(source_copy) != file_identity(projection / "RECONSTRUCTED_EN.md"):
            raise FiveStepIntakeError("review reconstruction evidence differs from fresh authority projection")
        for name in ("ASSET_MANIFEST.json", "OVERLAY_SELECTION.json", "SEMANTIC_STRUCTURE.json", "MERGE_PROVENANCE.json", "REVIEW_DRAFT_MATERIALIZATION.v1.json"):
            expected, observed = projection / name, result_root / name
            if expected.is_file() != observed.is_file() or (expected.is_file() and file_identity(expected) != file_identity(observed)):
                raise FiveStepIntakeError(f"review MASTER_EN {name} differs from fresh authority projection")
        for name in ("assets", "pages"):
            if deterministic_inventory(projection / name) != deterministic_inventory(result_root / name):
                raise FiveStepIntakeError(f"review MASTER_EN {name} differs from fresh authority projection")
        for row in material["pages"]:
            name = f"page-{row['source_page']:03d}.json"
            if file_identity(result_root / "evidence" / "review" / name) != file_identity(projection / "decisions" / name):
                raise FiveStepIntakeError("review MASTER_EN copied decision differs from fresh authority projection")
    finally:
        shutil.rmtree(projection_parent, ignore_errors=True)
    source_spans = _read(result_root / "EN_SOURCE_SPANS.json")
    observed_spans = _source_spans(result_root / "MASTER_EN.md", sorted((result_root / "evidence" / "review").glob("*.json")), result_root)
    if source_spans != observed_spans:
        raise FiveStepIntakeError("review MASTER_EN source span projection mismatch")
    v2, v1 = result_root / "ISSUE_EN_BINDINGS.v2.json", result_root / "ISSUE_EN_BINDINGS.v1.json"
    if v2.is_file() and not v1.exists():
        try:
            observed = load_issue_en_bindings_v2(result_root)
            expected = build_issue_en_bindings_v2(result_root / "MASTER_EN.md", evidence["source_issues"]["issues"], pages, evidence_path)
        except ReaderOccurrenceError as error:
            raise FiveStepIntakeError(str(error)) from error
        if observed != expected:
            raise FiveStepIntakeError("review MASTER_EN v2 issue binding mismatch")
    elif v1.is_file() and not v2.exists():
        if _read(v1) != _issue_en_bindings(result_root / "MASTER_EN.md", evidence["source_issues"]["issues"], pages, evidence_path):
            raise FiveStepIntakeError("review MASTER_EN issue binding mismatch")
    else:
        raise FiveStepIntakeError("review MASTER_EN issue binding version is ambiguous")
    for reference in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        local = reference.split("#", 1)[0]
        if local and not local.startswith(("http://", "https://")) and not (result_root / local).is_file():
            raise FiveStepIntakeError("review MASTER_EN references a missing local asset")
    return {"state": "verified_review_draft", "master_en": str(result_root / "MASTER_EN.md"), "manifest_path": str(result_root / "MANIFEST.json")}
