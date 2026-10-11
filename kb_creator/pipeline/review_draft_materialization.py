"""Fresh verification authority for the review-draft materialization route."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, NamedTuple

from .identity import file_identity
from .manifests import validate_seal
from .review_draft import (ArchiveConsumptionAuthorities,
                           build_archive_consumption_context,
                           validate_review_draft_evidence,
                           validate_review_draft_input)

SCHEMA = "kb_creator.verified_review_draft_materialization.v1"
IDENTITY = {"path", "bytes", "sha256"}


class Stage06Proofs(NamedTuple):
    """Validated derived assertions and the proof keys computed from them."""

    reference_proof_keys: set[tuple[int, str, int, str, str]]
    split_structure_proof_keys: set[tuple[int, str, int]]
    visual_assertions: dict[str, dict[str, Any]]


class ReviewDraftMaterializationError(ValueError):
    pass


def _record(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _path(row: Any, label: str) -> Path:
    if not isinstance(row, dict) or set(row) != IDENTITY:
        raise ReviewDraftMaterializationError(f"{label} identity is malformed")
    path = Path(row["path"])
    if not path.is_file() or file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
        raise ReviewDraftMaterializationError(f"{label} identity drift")
    return path


def _portable_relative(value: Any, label: str) -> Path:
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or value.startswith("/") or value.endswith("/")):
        raise ReviewDraftMaterializationError(f"{label} path is not portable")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ReviewDraftMaterializationError(f"{label} path is not a normalized relative path")
    return Path(*parts)


def _resolved_under(root: Path, relative: Any, label: str) -> Path:
    root = Path(root).resolve(strict=True)
    candidate = (root / _portable_relative(relative, label)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ReviewDraftMaterializationError(f"{label} path escapes its binding root") from error
    return candidate


def _input_binding_root(*, input_path: Path, review_input: Any, evidence: dict[str, Any],
                        authored) -> Path:
    """Derive the sealed input root from the bridge's original candidate binding."""
    rows = evidence["authored"]
    final_candidate, prepared_staging = rows.get("final_candidate"), rows.get("prepared_staging")
    if final_candidate is None and prepared_staging is None:
        return input_path.parent.resolve()
    if final_candidate is None or prepared_staging is None:
        raise ReviewDraftMaterializationError("final-candidate coverage bridge is incomplete")
    candidate_manifest = authored("final_candidate")
    staging_manifest = authored("prepared_staging")
    try:
        staging = json.loads(staging_manifest.read_text(encoding="utf-8"))
        bound = staging["bindings"]["finalized_candidate_manifest"]
        reviewed = review_input.value["bindings"]["reviewed_candidate_manifest"]
        source_record_path = Path(bound["path"])
        if not source_record_path.is_absolute():
            raise ValueError("finalized candidate binding is not absolute")
        source_path = source_record_path.resolve(strict=True)
    except (KeyError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise ReviewDraftMaterializationError("final bridge cannot derive its input binding root") from error
    if file_identity(source_path) != {key: final_candidate[key] for key in ("bytes", "sha256")}:
        raise ReviewDraftMaterializationError("final bridge candidate preimage identity differs")
    suffix = _portable_relative(reviewed.get("path") if isinstance(reviewed, dict) else None,
                                "reviewed candidate binding").parts
    if len(source_path.parts) < len(suffix) or tuple(source_path.parts[-len(suffix):]) != suffix:
        raise ReviewDraftMaterializationError("final bridge candidate preimage does not match review input binding root")
    root = source_path
    for _ in suffix:
        root = root.parent
    return root.resolve()


def _input_files(input_path: Path, review_input: Any, binding_root: Path, *,
                 final_candidate_bridge: bool) -> None:
    bindings = review_input.value["bindings"]
    if final_candidate_bridge:
        # The real producer seals the review input before prepared staging
        # exists.  The final evidence bridge binds staging separately, so
        # requiring it inside the input would create an input->staging->input
        # cycle.  Its durable producer shape records the predecessor candidate,
        # staging ledger, source dispositions, reviewed candidate, and inputs.
        for name, label in (("candidate_manifest", "candidate"), ("ledger", "ledger"),
                            ("source_dispositions", "source dispositions"),
                            ("reviewed_candidate_manifest", "reviewed candidate")):
            if name not in bindings:
                raise ReviewDraftMaterializationError(f"review input lacks {label} binding")
            if not any(name.startswith("input_") for name in bindings):
                raise ReviewDraftMaterializationError("review input lacks spec binding")
    elif "composer_config" in bindings:
        # The production composer seals its mechanical candidate, exact config,
        # report, source specs, and projected draft pages before authoring. It
        # has no prepared-staging ledger, so require its own complete closed
        # producer shape instead of accepting a fabricated staging placeholder.
        for name in ("candidate_manifest", "composer_config", "composer_report"):
            if name not in bindings:
                raise ReviewDraftMaterializationError(f"composer review input lacks {name} binding")
        if not any(name.startswith("semantic_source_") for name in bindings):
            raise ReviewDraftMaterializationError("composer review input lacks source spec binding")
        if not any(name.startswith("draft_") for name in bindings):
            raise ReviewDraftMaterializationError("composer review input lacks draft-page binding")
    else:
        # Keep the supported pre-bridge contracts unchanged.
        for needle, label in (("candidate", "candidate"), ("staging", "prepared staging"),
                              ("input_", "spec"), ("disposition", "disposition")):
            if not any(needle in name for name in bindings):
                raise ReviewDraftMaterializationError(f"review input lacks {label} binding")
    for name, row in bindings.items():
        if not isinstance(row, dict) or set(row) != IDENTITY:
            raise ReviewDraftMaterializationError(f"review input {name} identity is malformed")
        path = _resolved_under(binding_root, row["path"], f"review input {name}")
        if not path.is_file() or file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
            raise ReviewDraftMaterializationError(f"review input {name} identity drift")
    for disposition in review_input.value["unresolved_dispositions"]:
        for name in ("predecessor", "current"):
            row = disposition[name]; path = _resolved_under(binding_root, row["path"], f"disposition {name}")
            if not path.is_file() or file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
                raise ReviewDraftMaterializationError(f"disposition {name} identity drift")


def verify_descriptor(value: Any) -> dict[str, Any]:
    required = {"schema", "state", "bundle_root", "raw_root", "decisions_root",
                "input", "final_evidence", "audit", "source", "renderer",
                "comparison", "review_queue", "pages", "assets",
                "reference_proof_keys", "split_structure_proof_keys"}
    if (not isinstance(value, dict) or not required <= set(value)
            or set(value) - required - {"structural_role_proofs"} or value.get("schema") != SCHEMA):
        raise ReviewDraftMaterializationError("review-draft descriptor is not closed")
    if value.get("state") != "verified_review_draft_candidate":
        raise ReviewDraftMaterializationError("review-draft descriptor is not verified")
    for name in ("bundle_root", "raw_root", "decisions_root"):
        if not isinstance(value[name], str) or not Path(value[name]).is_dir():
            raise ReviewDraftMaterializationError(f"descriptor {name} is unavailable")
    for name in ("input", "final_evidence", "audit", "source", "renderer", "comparison", "review_queue"):
        _path(value[name], f"descriptor {name}")
    if not isinstance(value["pages"], list) or not value["pages"] or not isinstance(value["assets"], list):
        raise ReviewDraftMaterializationError("descriptor inventory is malformed")
    pages = [row.get("source_page") for row in value["pages"] if isinstance(row, dict)]
    if len(pages) != len(value["pages"]) or sorted(pages) != sorted(set(pages)) or any(type(page) is not int or page < 1 for page in pages):
        raise ReviewDraftMaterializationError("descriptor page inventory is malformed")
    structural = value.get("structural_role_proofs", [])
    if not isinstance(structural, list):
        raise ReviewDraftMaterializationError("descriptor structural proofs are malformed")
    seen = set()
    for row in structural:
        if not isinstance(row, dict) or set(row) != {"locator", "proof"}:
            raise ReviewDraftMaterializationError("descriptor structural proof row is malformed")
        locator, proof = row["locator"], row["proof"]
        if (not isinstance(locator, list) or len(locator) != 4
                or type(locator[0]) is not int or locator[0] not in pages
                or not isinstance(locator[1], str) or type(locator[2]) is not int or locator[2] < 0
                or not isinstance(locator[3], str) or len(locator[3]) != 64
                or not isinstance(proof, dict) or set(proof) != {"issue_id", "selected_source_key"}
                or not isinstance(proof["issue_id"], str) or not proof["issue_id"]
                or not isinstance(proof["selected_source_key"], dict)
                or set(proof["selected_source_key"]) != {"view", "raw_index"}
                or not isinstance(proof["selected_source_key"]["view"], str)
                or type(proof["selected_source_key"]["raw_index"]) is not int
                or tuple(locator) in seen):
            raise ReviewDraftMaterializationError("descriptor structural proof identity is malformed")
        seen.add(tuple(locator))
    return value


def _stage06_proof_keys(decisions: dict[int, dict[str, Any]], packets: dict[int, dict[str, Any]],
                        allowlist: dict[str, Any], visual_inventory: dict[str, Any], geometry: dict[str, Any]) -> Stage06Proofs:
    """Derive Stage06 conflict proofs from the same audited decisions, never defaults."""
    assertions = {row["assertion_id"]: row for row in allowlist.get("visual_text_assertions", [])
                  if isinstance(row, dict) and isinstance(row.get("assertion_id"), str)}
    if not any("semantic_structure" in decision for decision in decisions.values()):
        return Stage06Proofs(set(), set(), assertions)
    from kb_creator.pipeline.semantic_structure import (
        collect_reference_image_proof_keys, collect_split_structure_proof_keys,
        validate_semantic_structure,
    )
    from kb_creator.scripts.author_reviewed_semantic_decisions import semantic_assertion_map
    try:
        assertions = semantic_assertion_map(assertions, decisions, packets, geometry)
    except ValueError as error:
        raise ReviewDraftMaterializationError(f"positional assertion context is invalid: {error}") from error
    validate_semantic_structure(decisions, packets, visual_inventory, required_pages=sorted(decisions),
                                visual_assertions=assertions or None)
    return Stage06Proofs(
        collect_reference_image_proof_keys(decisions, packets, assertions),
        collect_split_structure_proof_keys(decisions, packets), assertions,
    )


def _recompute_final_candidate_coverage(*, run_root: Path, evidence: dict[str, Any],
                                        authored: Any, input_path: Path, binding_root: Path,
                                        drafts_root: Path) -> list[dict[str, Any]] | None:
    """Reopen the final-candidate bridge when this review route used one.

    Legacy reviewed-draft evidence has no final-candidate bridge and therefore
    deliberately returns ``None``.  A route that records either half of the
    bridge must record both halves and rerun the author-side validations before
    its Stage05 audit can be trusted by a downstream materializer.
    """
    final_candidate = evidence["authored"].get("final_candidate")
    prepared_staging = evidence["authored"].get("prepared_staging")
    if final_candidate is None and prepared_staging is None:
        try:
            from kb_creator.scripts.author_reviewed_semantic_decisions import _recompute_composer_coverage
            review_input = json.loads(Path(input_path).read_text(encoding="utf-8"))
            return _recompute_composer_coverage(review_input, Path(binding_root), Path(run_root), Path(drafts_root))
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise ReviewDraftMaterializationError(f"composer coverage cannot be rederived: {error}") from error
    if final_candidate is None or prepared_staging is None:
        raise ReviewDraftMaterializationError("final-candidate coverage bridge is incomplete")
    candidate_manifest = authored("final_candidate")
    staging_manifest = authored("prepared_staging")
    try:
        candidate = json.loads(candidate_manifest.read_text(encoding="utf-8"))
        specs = candidate["inputs"]["specs"]
        if not isinstance(specs, list) or not all(isinstance(row, dict) and isinstance(row.get("path"), str)
                                                  for row in specs):
            raise ValueError("final candidate semantic spec bindings are malformed")
        spec_paths = [Path(row["path"]).resolve() for row in specs]
        from kb_creator.scripts.author_reviewed_semantic_decisions import (
            _recompute_prepared_coverage,
            _validate_prepared_staging,
            validate_final_candidate,
        )
        verified = validate_final_candidate(run_root, candidate_manifest.parent, spec_paths, input_path)
        _validate_prepared_staging(staging_manifest, candidate_manifest, verified["review_draft_input_sha256"])
        return _recompute_prepared_coverage(staging_manifest, run_root, candidate_manifest.parent)
    except (KeyError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise ReviewDraftMaterializationError(
            f"final-candidate coverage bridge cannot be rederived: {error}"
        ) from error


def _archive_context_for_final_candidate(*, run_root: Path, review_input: Any, authored) -> dict[str, Any]:
    """Rebuild the sealed archive lineage, retaining only live freshness as diagnostic.

    Prepared staging was sealed before authoring and is itself hash-bound by the
    final evidence.  It is therefore the authority for the archived source run;
    selecting the supplied target as both source and target would omit that
    lineage from a fresh downstream verifier.
    """
    from kb_creator.scripts.author_reviewed_semantic_decisions import _validate_prepared_staging

    candidate_manifest = authored("final_candidate")
    staging_manifest = authored("prepared_staging")
    try:
        staging = json.loads(staging_manifest.read_text(encoding="utf-8"))
        if staging.get("schema") != "kb_creator.reviewed_draft_staging.v3" or staging.get("state") != "prepared_for_audit":
            raise ValueError("prepared staging schema or state is invalid")
        validate_seal(staging, "manifest_sha256")
        staged = _validate_prepared_staging(staging_manifest, candidate_manifest, review_input.sha256)
        recorded = staged["archive_authority"]
        if not isinstance(recorded, dict) or set(recorded) != {"schema", "state", "source_run_root", "target_run_root", "source_sha256", "source", "target", "checked_paths"}:
            raise ValueError("prepared staging archive authority has an invalid closed shape")
        if recorded["schema"] != "kb_creator.review_draft_archive_consumption.v1" or recorded["state"] != "read_only_consumption":
            raise ValueError("prepared staging archive authority schema or state is invalid")
        source_root = Path(recorded["source_run_root"])
        target_root = Path(recorded["target_run_root"])
        if not source_root.is_absolute() or not target_root.is_absolute():
            raise ValueError("prepared staging archive roots must be absolute")
        source_root = source_root.resolve(strict=True); target_root = target_root.resolve(strict=True)
        if source_root == target_root or target_root != run_root:
            raise ValueError("prepared staging archive roots do not select the supplied target")
        expected_paths = {"stage_02_root", "comparison", "merge_packets", "visual_manifest", "geometry_plan", "review_queue"}
        if not isinstance(recorded["checked_paths"], dict) or set(recorded["checked_paths"]) != expected_paths:
            raise ValueError("prepared staging archive checked paths are incomplete")
        for side in ("source", "target"):
            value = recorded[side]
            if not isinstance(value, dict) or set(value) != {"run_identity_sha256", "bridge_sha256", "producer_freshness"}:
                raise ValueError(f"prepared staging archive {side} authority is malformed")
            if not isinstance(value["producer_freshness"], dict):
                raise ValueError(f"prepared staging archive {side} freshness is malformed")
        rebuilt = build_archive_consumption_context(source_run_root=source_root, target_run_root=target_root)
        stable = {
            "schema": rebuilt.get("schema"), "state": rebuilt.get("state"),
            "source_run_root": str(source_root), "target_run_root": str(target_root),
            "source_sha256": rebuilt.get("source_sha256"),
            "source": {key: rebuilt.get("source", {}).get(key) for key in ("run_identity_sha256", "bridge_sha256")},
            "target": {key: rebuilt.get("target", {}).get(key) for key in ("run_identity_sha256", "bridge_sha256")},
            "checked_paths": {key: str(Path(rebuilt.get("checked_paths", {})[key]).resolve()) for key in expected_paths},
        }
        recorded_stable = {
            "schema": recorded["schema"], "state": recorded["state"],
            "source_run_root": str(source_root), "target_run_root": str(target_root),
            "source_sha256": recorded["source_sha256"],
            "source": {key: recorded["source"].get(key) for key in ("run_identity_sha256", "bridge_sha256")},
            "target": {key: recorded["target"].get(key) for key in ("run_identity_sha256", "bridge_sha256")},
            "checked_paths": {key: str(Path(recorded["checked_paths"][key]).resolve()) for key in expected_paths},
        }
    except (KeyError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise ReviewDraftMaterializationError(
            f"final-candidate archive authority cannot be rederived: {error}"
        ) from error
    if rebuilt.get("state") != "read_only_consumption" or stable != recorded_stable:
        raise ReviewDraftMaterializationError("final-candidate archive authority differs from prepared staging")
    return rebuilt


def verify_final_review_draft(*, run_root: Path, authored_root: Path, input_path: Path,
                              evidence_path: Path, binding_root: Path | None = None) -> dict[str, Any]:
    """Recompute archive authority, Stage05, and Stage06 before materialization."""
    from kb_creator.pipeline.reconstruction_replay_resume import validate_replay_review_queue
    from kb_creator.pipeline.source_page_render import replay_source_render_context
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v3_content
    from kb_creator.scripts.materialize_mineru_ai_merge import _validate_decision

    run_root, authored_root = Path(run_root).resolve(), Path(authored_root).resolve()
    input_path, evidence_path = Path(input_path).resolve(), Path(evidence_path).resolve()
    evidence = validate_review_draft_evidence(json.loads(evidence_path.read_text(encoding="utf-8")))
    review_input = validate_review_draft_input(json.loads(input_path.read_text(encoding="utf-8")))
    if evidence["input_sha256"] != review_input.sha256:
        raise ReviewDraftMaterializationError("final evidence binds a different review input")

    def authored(name: str) -> Path:
        row = evidence["authored"].get(name)
        if not isinstance(row, dict) or set(row) != IDENTITY:
            raise ReviewDraftMaterializationError(f"final evidence lacks {name} identity")
        path = _resolved_under(authored_root, row["path"], f"final evidence {name}")
        if not path.is_file() or file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
            raise ReviewDraftMaterializationError(f"final evidence {name} identity drift")
        return path

    binding_root = (Path(binding_root).resolve() if binding_root is not None else
                    _input_binding_root(input_path=input_path, review_input=review_input,
                                        evidence=evidence, authored=authored))
    _input_files(input_path, review_input, binding_root,
                 final_candidate_bridge=("final_candidate" in evidence["authored"]))
    from .source_choice_container_proof import open_structural_projection_context
    structural_context = open_structural_projection_context(
        input_path=input_path, binding_root=binding_root)

    decision_set_path, allowlist_path, audit_path = (authored(name) for name in
        ("decision_set", "reviewed_allowlist", "stage05_audit"))
    if "final_candidate" in evidence["authored"]:
        archive = _archive_context_for_final_candidate(
            run_root=run_root, review_input=review_input, authored=authored)
    else:
        archive = build_archive_consumption_context(source_run_root=run_root, target_run_root=run_root)
    paths = {name: Path(path) for name, path in archive["checked_paths"].items()}
    authority = ArchiveConsumptionAuthorities(run_root=run_root, bridge_sha256=archive["target"]["bridge_sha256"],
        **{name: paths[name] for name in ("stage_02_root", "comparison", "merge_packets", "visual_manifest", "geometry_plan")})
    queue = validate_replay_review_queue(authority)
    decisions = {int(path.stem.split("-")[1]): json.loads(path.read_text(encoding="utf-8"))
                 for path in (authored_root / "pages").glob("page-*.json")}
    queue_pages = {row.get("source_page") for row in queue.queue.get("items", []) if isinstance(row, dict)}
    if not decisions or set(decisions) != queue_pages:
        raise ReviewDraftMaterializationError("authored decision page domain differs from checked queue")
    expected_unresolved = {(row["source_page"], row["predecessor_unresolved"])
                           for row in evidence["unresolved_dispositions"]}
    actual_unresolved = {(page, item) for page, decision in decisions.items()
                         for item in decision.get("unresolved", [])}
    if expected_unresolved != actual_unresolved:
        raise ReviewDraftMaterializationError("final dispositions do not exactly cover authored unresolved strings")
    false_pages = sorted(page for page, decision in decisions.items()
                         if decision.get("review", {}).get("visual_reviewed") is False)
    if false_pages != evidence["visual_reviewed_false_pages"]:
        raise ReviewDraftMaterializationError("final false visual-review flags differ from evidence")

    decision_set = json.loads(decision_set_path.read_text(encoding="utf-8"))
    rows = decision_set.get("decisions") if isinstance(decision_set, dict) else None
    if not isinstance(rows, list) or {row.get("source_page") for row in rows if isinstance(row, dict)} != set(decisions):
        raise ReviewDraftMaterializationError("decision set does not bind every authored page")
    for row in rows:
        path = _resolved_under(authored_root, row["path"], "decision set page")
        if not path.is_file() or file_identity(path) != {key: row.get(key) for key in ("bytes", "sha256")}:
            raise ReviewDraftMaterializationError("decision set page identity drift")

    packets = {page: json.loads((paths["merge_packets"] / "pages" / f"page-{page:03d}.json").read_text(encoding="utf-8"))
               for page in decisions}
    geometry = json.loads(paths["geometry_plan"].read_text(encoding="utf-8"))
    from kb_creator.scripts.author_reviewed_semantic_decisions import (
        _composer_coverage_successor_dispositions, _visual_inventory,
    )
    source_context = replay_source_render_context(run_root, geometry)
    allowlist = json.loads(allowlist_path.read_text(encoding="utf-8"))
    visual_inventory = _visual_inventory(run_root)
    reader_coverage_claims = _recompute_final_candidate_coverage(
        run_root=run_root, evidence=evidence, authored=authored, input_path=input_path, binding_root=binding_root,
        drafts_root=authored_root / "pages",
    )
    coverage_successor_dispositions = _composer_coverage_successor_dispositions(
        review_input.value, binding_root, reader_coverage_claims)
    pending_source_context = None
    if any(isinstance(row, dict) and row.get("kind") == "translation_source_choice_pending"
           for row in review_input.value.get("source_issues", {}).get("issues", [])):
        pending_source_context = {"review_input": review_input.value, "input_path": str(input_path),
                                  "binding_root": str(binding_root), "run_root": str(run_root)}
    recomputed = audit_v3_content(packets, decisions, allowlist=allowlist, geometry=geometry,
        visual_inventory=visual_inventory, authorities=allowlist.get("authority"),
        source_render_context=source_context, reader_coverage_claims=reader_coverage_claims,
        coverage_successor_dispositions=coverage_successor_dispositions,
        pending_source_context=pending_source_context,
        structural_input_path=input_path, structural_binding_root=binding_root)
    persisted = json.loads(audit_path.read_text(encoding="utf-8"))
    if not recomputed.get("passed") or recomputed.get("errors") != [] or recomputed != persisted or evidence["audit"] != recomputed:
        raise ReviewDraftMaterializationError("recomputed Stage05 audit differs from final evidence")
    source_context["proofs"] = {row["source_page"]: row.get("source_page_renders", [])
                                for row in recomputed.get("pages", [])}
    stage06 = _stage06_proof_keys(
        decisions, packets, allowlist, visual_inventory, geometry)
    reference_proof_keys = stage06.reference_proof_keys
    split_structure_proof_keys = stage06.split_structure_proof_keys
    comparison = json.loads(paths["comparison"].read_text(encoding="utf-8"))
    structural_role_proofs = {}
    if any(isinstance(row, dict) and row.get("kind") == "source_structure_role_pending"
           for row in review_input.value.get("source_issues", {}).get("issues", [])):
        from .structural_role_issues import derive_structural_role_conflict_proofs
        structural_role_proofs = derive_structural_role_conflict_proofs(
            review_input=review_input.value, input_path=input_path, binding_root=binding_root,
            run_root=run_root, decisions=decisions, packets=packets, comparison=comparison,
            stage05_pages=recomputed.get("pages", []))
    scratch = Path(tempfile.mkdtemp(prefix="review-draft-stage06-"))
    try:
        names: set[str] = set(); assets: list[dict[str, Any]] = []
        for page in sorted(decisions):
            _, page_assets, _ = _validate_decision(decisions[page], packets[page], comparison,
                paths["stage_02_root"], names, source_context, scratch,
                reference_proof_keys, split_structure_proof_keys, structural_role_proofs,
                stage06.visual_assertions or None)
            assets.extend({key: value for key, value in row.items()
                           if key not in {"resolved_source", "stored_path"}} for row in page_assets)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    descriptor = verify_descriptor({
        "schema": SCHEMA, "state": "verified_review_draft_candidate",
        "bundle_root": str((run_root / "outputs/04-visual-merge-bundle").resolve()),
        "raw_root": str(paths["stage_02_root"].resolve()),
        "decisions_root": str((authored_root / "pages").resolve()),
        "input": _record(input_path), "final_evidence": _record(evidence_path),
        "audit": _record(audit_path), "source": _record(source_context["source"]),
        "renderer": _record(source_context["renderer"]), "comparison": _record(paths["comparison"]),
        "review_queue": _record(queue.queue_path),
        "pages": [{"source_page": page, **file_identity(authored_root / "pages" / f"page-{page:03d}.json")}
                  for page in sorted(decisions)],
        "assets": assets,
        "reference_proof_keys": [list(key) for key in sorted(reference_proof_keys)],
        "split_structure_proof_keys": [list(key) for key in sorted(split_structure_proof_keys)],
        **({"structural_role_proofs": [{"locator": list(key), "proof": structural_role_proofs[key]}
                                      for key in sorted(structural_role_proofs)]} if structural_role_proofs else {}),
    })
    if structural_context is not None and open_structural_projection_context(
            input_path=input_path, binding_root=binding_root) != structural_context:
        raise ReviewDraftMaterializationError("structural projection authority changed before verification returned")
    return descriptor
