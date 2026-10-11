"""Explicit, immutable verification and structural continuation of authored source.

The operator owns process quiescence and reviewed runtime selection. This module
never resumes historical jobs and never converts a caller's status into proof.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import inspect
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

from .identity import (assert_existing_path_components_are_not_reparse,
                       deterministic_inventory, file_identity, sha256_bytes)
from .manifests import sealed, validate_seal
from .review_draft import validate_review_draft_evidence, validate_review_draft_input
from .review_draft_materialization import _resolved_under, verify_descriptor
from kb_creator.scripts.scenario_contract import (_reject_duplicate_keys,
                                                 _reject_nonfinite_constant)

REQUEST_SCHEMA = "kb_creator.review_source_continuation_request.v1"
RECEIPT_SCHEMA = "kb_creator.review_source_continuation_receipt.v1"
COMMON = {"schema", "operation", "binding_root", "run_root", "authored_root",
          "input", "evidence", "expected_pages", "runtime", "authority_files",
          "authority_inventories", "output_root", "request_sha256"}
STRUCTURAL = {"verification_receipt", "verification_request", "proposal",
              "projection", "review_root", "excluded_owner_pages"}
AUTHORITY = {"old_runtime_manifest", "runtime_integration", "patch_evidence",
             "implementation_review", "compatibility_decision", "ownership_decision",
             "old_job_observation", "exit_observation", "source", "renderer"}


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=_reject_duplicate_keys,
                      parse_constant=_reject_nonfinite_constant)


def record(path: Path) -> dict[str, Any]:
    path = Path(path).resolve(strict=True)
    return {"path": str(path), **file_identity(path)}


def _absolute(value: Any) -> Path:
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError("continuation paths must be absolute")
    return Path(value).resolve()


def _checked(row: Any, root: Path | None = None) -> Path:
    if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
        raise ValueError("identity must have closed path/bytes/sha256 shape")
    path = _absolute(row["path"]) if root is None else _resolved_under(root, row["path"], "continuation")
    if not path.is_file() or file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
        raise ValueError(f"identity drift: {path}")
    return path


def _write_new(path: Path, value: Any) -> None:
    """Publish complete bytes atomically without replacing an existing target."""
    descriptor, temporary = tempfile.mkstemp(prefix=".continuation-", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _request(path: Path, operation: str) -> dict[str, Any]:
    value = read_json(path)
    fields = COMMON | (STRUCTURAL if operation == "structural" else set())
    if not isinstance(value, dict) or set(value) != fields or value.get("schema") != REQUEST_SCHEMA:
        raise ValueError("continuation request has invalid closed shape")
    validate_seal(value, "request_sha256")
    if value["operation"] != operation:
        raise ValueError("request operation mismatch")
    pages = value["expected_pages"]
    if (not isinstance(pages, list) or not pages or any(type(p) is not int or p < 1 for p in pages)
            or pages != sorted(set(pages))):
        raise ValueError("expected page domain must be sorted unique positive integers")
    if not isinstance(value["authority_files"], dict) or not AUTHORITY <= set(value["authority_files"]):
        raise ValueError("required recovery authority identities are missing")
    if not isinstance(value["authority_inventories"], list):
        raise ValueError("authority inventories must be explicit")
    inventory_roots = {str(_absolute(row["root"])) for row in value["authority_inventories"]}
    if not {str(_absolute(value[name])) for name in ("run_root", "authored_root")} <= inventory_roots:
        raise ValueError("request must pin complete replay and authored inventories")
    for name in ("binding_root", "run_root", "authored_root"):
        if not _absolute(value[name]).is_dir():
            raise ValueError(f"{name} unavailable")
    return value


def _runtime(value: dict[str, Any]) -> None:
    if set(value) != {"root", "manifest", "executable", "dependencies"}:
        raise ValueError("runtime has invalid closed shape")
    root = _absolute(value["root"])
    manifest_path = _checked(value["manifest"])
    if manifest_path != root / "manifest.json" or _checked(value["executable"]) != Path(sys.executable).resolve():
        raise ValueError("runtime manifest/executable mismatch")
    manifest = read_json(manifest_path)
    if not isinstance(value["dependencies"], list):
        raise ValueError("runtime dependencies must be explicit identity records")
    declared = set()
    for row in manifest["files"]:
        path = _checked(row, root / "code")
        if path in declared:
            raise ValueError("duplicate runtime file")
        declared.add(path)
    # Every imported production module must come from the pinned frozen tree.
    for name, module in list(sys.modules.items()):
        if name == "kb_creator" or name.startswith("kb_creator."):
            origin = getattr(module, "__file__", None)
            if origin and Path(origin).resolve() not in declared:
                raise ValueError(f"unbound runtime import: {name}")
    for row in value["dependencies"]:
        _checked(row)


def _operations(runtime: dict[str, Any]) -> dict[str, Any]:
    from .review_draft_materialization import verify_final_review_draft
    from .review_draft_preparation import prepare_review_draft_structural_successor
    from .five_step_intake import build_review_master_en
    from kb_creator.scripts.author_reviewed_semantic_decisions import author_drafts, validate_spec
    from kb_creator.scripts.materialize_mineru_ai_merge import materialize
    operations = {operation.__name__: operation for operation in (
        verify_final_review_draft, prepare_review_draft_structural_successor,
        validate_spec, author_drafts, materialize, build_review_master_en)}
    root = _absolute(runtime["root"]) / "code"
    for operation in operations.values():
        if not Path(inspect.getfile(operation)).resolve().is_relative_to(root):
            raise ValueError("public operation is outside the configured frozen runtime")
    _runtime(runtime)
    return operations


def _snapshot(request: dict[str, Any]) -> dict[str, Any]:
    """Pin all direct bindings, complete archive/authored trees and external closure."""
    _runtime(request["runtime"])
    binding = _absolute(request["binding_root"])
    authored = _absolute(request["authored_root"])
    input_path, evidence_path = _checked(request["input"]), _checked(request["evidence"])
    if evidence_path != authored / "review-draft-evidence.json":
        raise ValueError("evidence is outside the authored predecessor")
    review_input = validate_review_draft_input(read_json(input_path))
    evidence = validate_review_draft_evidence(read_json(evidence_path))
    if evidence["input_sha256"] != review_input.sha256:
        raise ValueError("input/evidence binding mismatch")
    files = {str(path): record(path) for path in (input_path, evidence_path)}
    for row in request["authority_files"].values():
        path = _checked(row); files[str(path)] = record(path)
    for row in review_input.value["bindings"].values():
        path = _checked(row, binding); files[str(path)] = record(path)
    for row in review_input.value["unresolved_dispositions"]:
        for name in ("predecessor", "current"):
            path = _checked(row[name], binding); files[str(path)] = record(path)
    for row in evidence["authored"].values():
        path = _checked(row, authored); files[str(path)] = record(path)
    decisions = read_json(_checked(evidence["authored"]["decision_set"], authored))["decisions"]
    pages = []
    for row in decisions:
        page = row["source_page"]
        if type(page) is not int or row["path"] != f"pages/page-{page:03d}.json":
            raise ValueError("decision page/path mismatch")
        path = _checked({key: row[key] for key in ("path", "bytes", "sha256")}, authored)
        if read_json(path)["source_page"] != page:
            raise ValueError("decision source page mismatch")
        pages.append(page); files[str(path)] = record(path)
    if sorted(pages) != request["expected_pages"]:
        raise ValueError("authored page domain differs from request")
    trees = {str(root): deterministic_inventory(root) for root in (
        _absolute(request["run_root"]), authored)}
    for inventory in request["authority_inventories"]:
        if set(inventory) != {"root", "files"}:
            raise ValueError("authority inventory is malformed")
        root = _absolute(inventory["root"])
        actual = deterministic_inventory(root)
        if actual != inventory["files"]:
            raise ValueError(f"authority inventory drift: {root}")
        trees[str(root)] = actual
    return {"files": [files[key] for key in sorted(files)], "trees": trees,
            "runtime": request["runtime"]}


def _descriptor(value: Any, request: dict[str, Any]) -> dict[str, Any]:
    value = verify_descriptor(value)
    if value["input"] != request["input"] or value["final_evidence"] != request["evidence"]:
        raise ValueError("descriptor input/evidence mismatch")
    if Path(value["decisions_root"]).resolve() != _absolute(request["authored_root"]) / "pages":
        raise ValueError("descriptor authored root mismatch")
    if Path(value["bundle_root"]).resolve() != _absolute(request["run_root"]) / "outputs/04-visual-merge-bundle":
        raise ValueError("descriptor replay root mismatch")
    if Path(value["raw_root"]).resolve() != _absolute(request["run_root"]) / "outputs/02-mineru-three-view":
        raise ValueError("descriptor raw root mismatch")
    evidence = validate_review_draft_evidence(read_json(_checked(request["evidence"])))
    if value["audit"] != record(_checked(evidence["authored"]["stage05_audit"], _absolute(request["authored_root"]))):
        raise ValueError("descriptor audit/evidence mismatch")
    if [row["source_page"] for row in value["pages"]] != request["expected_pages"]:
        raise ValueError("descriptor page domain mismatch")
    for row in value["pages"]:
        path = _absolute(request["authored_root"]) / f"pages/page-{row['source_page']:03d}.json"
        if file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
            raise ValueError("descriptor decision identity drift")
    for name in ("source", "renderer"):
        if value[name] != request["authority_files"][name]:
            raise ValueError(f"descriptor {name} mismatch")
    return value


def _output(request: dict[str, Any]) -> Path:
    root = _absolute(request["output_root"])
    assert_existing_path_components_are_not_reparse(root)
    if root.exists() or (root.parent / ("." + root.name + ".staging")).exists() or not root.parent.is_dir():
        raise ValueError("successor output exists or parent unavailable")
    if not root.is_relative_to(_absolute(request["binding_root"])):
        raise ValueError("output must remain under the explicit binding root")
    protected = [_absolute(request[name]) for name in ("binding_root", "run_root", "authored_root")]
    protected += [_absolute(request["runtime"]["root"])]
    protected += [_absolute(row["root"]) for row in request["authority_inventories"]]
    # Outputs may live under the broad binding root, but never inside pinned trees.
    if any(root == path or path.is_relative_to(root) for path in protected):
        raise ValueError("output overlaps authority root")
    if any(root.is_relative_to(path) for path in protected[1:]):
        raise ValueError("output lies inside immutable inventory")
    return root


def _finish(root: Path, request_path: Path, request: dict[str, Any], before: dict[str, Any],
            operation: str, results: dict[str, Any]) -> dict[str, Any]:
    after = _snapshot(request)
    if before != after:
        raise ValueError("immutable authority changed during operation")
    if record(request_path) != results.pop("request_identity"):
        raise ValueError("request changed during operation")
    receipt = sealed(RECEIPT_SCHEMA, {"state": "completed", "operation": operation,
        "request": record(request_path), "runtime": request["runtime"],
        "inventory_before": before, "inventory_after": after,
        "accepted": False, "authoring_repeated": False, "ocr_repeated": False,
        "process": {"pid": os.getpid(), "executable": record(Path(sys.executable)),
                    "observed_utc": datetime.now(timezone.utc).isoformat()},
        "recovery_authorities": request["authority_files"], **results}, digest_key="receipt_sha256")
    _write_new(root / "receipt.json", receipt)
    return receipt


def _failed(root: Path, error: Exception, phase: str) -> None:
    _write_new(root / "failure.json", {"state": "failed", "phase": phase,
        "error_type": type(error).__name__, "error": str(error), "accepted": False,
        "timestamp": datetime.now(timezone.utc).isoformat()})


def verify_authored_source(request_path: Path) -> dict[str, Any]:
    request_path = Path(request_path).resolve(strict=True)
    request_identity = record(request_path)
    request = _request(request_path, "verify")
    root = _output(request)
    before = _snapshot(request)
    operations = _operations(request["runtime"])
    root.mkdir()
    try:
        descriptor = operations["verify_final_review_draft"](
            run_root=_absolute(request["run_root"]), authored_root=_absolute(request["authored_root"]),
            input_path=_checked(request["input"]), evidence_path=_checked(request["evidence"]),
            binding_root=_absolute(request["binding_root"]))
        _descriptor(descriptor, request)
        if _snapshot(request) != before or record(request_path) != request_identity:
            raise ValueError("immutable authority changed during verification")
        _write_new(root / "descriptor.json", descriptor)
        return _finish(root, request_path, request, before, "verify_final_review_draft", {
            "descriptor": record(root / "descriptor.json"), "request_identity": request_identity})
    except Exception as error:
        _failed(root, error, "verify_final_review_draft")
        raise


def _verified_predecessor(request: dict[str, Any]) -> dict[str, Any]:
    receipt = read_json(_checked(request["verification_receipt"]))
    validate_seal(receipt, "receipt_sha256")
    old_path = _checked(request["verification_request"])
    old = _request(old_path, "verify")
    if (receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("state") != "completed"
            or receipt.get("operation") != "verify_final_review_draft"
            or receipt.get("accepted") is not False or receipt.get("authoring_repeated") is not False
            or receipt.get("ocr_repeated") is not False or receipt.get("request") != record(old_path)):
        raise ValueError("not an actual successful verification receipt")
    for name in COMMON - {"operation", "output_root", "request_sha256"}:
        if request[name] != old[name]:
            raise ValueError(f"verification predecessor {name} mismatch")
    if (receipt["runtime"] != request["runtime"]
            or receipt["recovery_authorities"] != request["authority_files"]
            or receipt["inventory_before"] != receipt["inventory_after"]
            or _snapshot(request) != receipt["inventory_after"]):
        raise ValueError("verification receipt is stale")
    descriptor_path = _checked(receipt["descriptor"])
    if descriptor_path != _absolute(old["output_root"]) / "descriptor.json":
        raise ValueError("verification descriptor has wrong lineage")
    return _descriptor(read_json(descriptor_path), request)


def _bind_structural(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    review_root = _absolute(request["review_root"])
    proposal = read_json(_checked(request["proposal"]))["normal_api_edit_sections"]
    projection = read_json(_checked(request["projection"]))
    for row in projection["parents"]:
        _checked(row, review_root)
    projections = projection["post_ledger_page_projections"]
    if (len(projections) != len(request["expected_pages"])
            or sorted(row["source_page"] for row in projections) != request["expected_pages"]):
        raise ValueError("reviewed projection page domain mismatch")
    authored = _absolute(request["authored_root"])
    decisions = {}
    for row in projections:
        page = row["source_page"]
        decision = read_json(authored / f"pages/page-{page:03d}.json")
        if sha256_bytes(decision["markdown"].encode("utf-8")) != row["projected_post_ledger_markdown_sha256"]:
            raise ValueError(f"reviewed projection mismatch on page {page}")
        decisions[page] = decision
    excluded = request["excluded_owner_pages"]
    if (not isinstance(excluded, list) or any(type(page) is not int or page not in decisions for page in excluded)
            or len(excluded) != len(set(excluded))):
        raise ValueError("excluded owner page domain is malformed")
    if {row["source_page"] for row in proposal["page_units"]} & set(excluded):
        raise ValueError("structural edits replace an excluded owner page")
    sidecar = deepcopy(proposal["source_marker_dispositions_sidecar_proposal"])
    for collection in ("candidates", "dispositions"):
        for row in sidecar[collection]:
            decision = decisions[row["source_page"]]
            selected = {(item["view"], item["raw_index"]) for item in decision["selected_blocks"]
                        if item.get("purpose") != "asset"}
            if (row["view"], row["raw_index"]) not in selected:
                raise ValueError("structural selected raw key mismatch")
            _checked(row["visual"], review_root)
            actual_visual = decision["semantic_structure"]["review"]["visual"]
            _checked(actual_visual, _absolute(request["run_root"]))
            row["visual"] = deepcopy(actual_visual)
    patches = deepcopy(proposal["structural_post_patches"])
    allowed = {"source_occurrences", "before", "before_sha256", "after", "after_sha256", "count", "interval_map"}
    for page in patches:
        for patch in page["patches"]:
            if set(patch) - allowed - {"ornament_removed"}:
                raise ValueError("unsupported structural proposal annotation")
            patch.pop("ornament_removed", None)
    edits = {"schema": proposal["schema"],
        "predecessor_input": {"path": Path(request["input"]["path"]).name,
                              **file_identity(_checked(request["input"]))},
        "predecessor_evidence": {"path": "review-draft-evidence.json",
                                 **file_identity(_checked(request["evidence"]))},
        "structural_post_patches": patches, "retained_owner_assertions": proposal["retained_owner_assertions"],
        "page_units": proposal["page_units"]}
    return sidecar, edits


def continue_structural_source(request_path: Path) -> dict[str, Any]:
    request_path = Path(request_path).resolve(strict=True)
    request_identity = record(request_path)
    request = _request(request_path, "structural")
    root = _output(request)
    _verified_predecessor(request)
    before = _snapshot(request)
    sidecar, edits = _bind_structural(request)
    # Freeze proposal parents and both original/bound visuals through the operation.
    structural_files = [request["proposal"], request["projection"]]
    projection = read_json(_checked(request["projection"]))
    structural_files += [record(_checked(row, _absolute(request["review_root"]))) for row in projection["parents"]]
    original = read_json(_checked(request["proposal"]))["normal_api_edit_sections"]["source_marker_dispositions_sidecar_proposal"]
    for rows, base in ((original, _absolute(request["review_root"])), (sidecar, _absolute(request["run_root"]))):
        structural_files += [record(_checked(row["visual"], base)) for collection in ("candidates", "dispositions")
                             for row in rows[collection]]
    operations = _operations(request["runtime"])
    root.mkdir()
    phase = "prepare"
    stages = {}
    def freshness() -> None:
        for row in structural_files:
            _checked(row)
        _verified_predecessor(request)
        if _snapshot(request) != before or record(request_path) != request_identity:
            raise ValueError("authority changed between structural stages")

    try:
        _write_new(root / "marker-dispositions.json", sidecar)
        edits["source_marker_dispositions"] = {"path": "marker-dispositions.json", **file_identity(root / "marker-dispositions.json")}
        _write_new(root / "edits.json", edits)
        stages[phase] = operations["prepare_review_draft_structural_successor"](
            predecessor_input=_checked(request["input"]), predecessor_authored=_absolute(request["authored_root"]),
            binding_root=_absolute(request["binding_root"]), edits_path=root / "edits.json", output_dir=root / "prepared")
        if stages[phase].get("state") != "sealed_structural_successor":
            raise ValueError("structural preparation did not return sealed successor")
        input_path = Path(stages[phase]["input"]["path"])
        _checked(stages[phase]["input"])
        bindings = validate_review_draft_input(read_json(input_path)).value["bindings"]
        spec_prefix = ("source_choice_successor_spec-" if any(key.startswith("source_choice_successor_spec-")
                       for key in bindings) else "input_")
        draft_prefix = ("source_choice_successor_page-" if any(key.startswith("source_choice_successor_page-")
                        for key in bindings) else "draft_")
        specs = [_checked(row, _absolute(request["binding_root"])) for key, row in sorted(bindings.items())
                 if key.startswith(spec_prefix)]
        drafts = [_checked(row, _absolute(request["binding_root"])) for key, row in sorted(bindings.items())
                  if key.startswith(draft_prefix)]
        if not specs or len(drafts) != len(request["expected_pages"]) or len({path.parent for path in drafts}) != 1:
            raise ValueError("prepared spec/draft page domain mismatch")
        _write_new(root / "stage-prepare.json", stages[phase])
        freshness()
        run, binding = _absolute(request["run_root"]), _absolute(request["binding_root"])
        phase = "preflight"
        stages[phase] = operations["validate_spec"](run, None, specs, draft_pages=drafts[0].parent,
                                                   draft_input=input_path, binding_root=binding)
        if (stages[phase]["page_count"] != len(request["expected_pages"])
                or stages[phase]["correction_coverage"] != {"page_count": len(request["expected_pages"]), "unbound_keys": 0}):
            raise ValueError("structural preflight page/coverage mismatch")
        _write_new(root / "stage-preflight.json", stages[phase])
        freshness()
        phase = "author"
        authored = root / "authored"
        value = operations["author_drafts"](run, drafts[0].parent, authored, specs,
            mode="review_draft", draft_input=input_path, binding_root=binding)
        if len(value["decisions"]) != len(request["expected_pages"]):
            raise ValueError("structural authored page count mismatch")
        stages[phase] = {"page_count": len(value["decisions"])}
        _write_new(root / "stage-author.json", stages[phase])
        freshness()
        phase = "verify"
        successor = {**request, "authored_root": str(authored), "input": record(input_path),
                     "evidence": record(authored / "review-draft-evidence.json")}
        descriptor = operations["verify_final_review_draft"](run_root=run, authored_root=authored,
            input_path=input_path, evidence_path=authored / "review-draft-evidence.json", binding_root=binding)
        _descriptor(descriptor, successor)
        _write_new(root / "descriptor.json", descriptor)
        stages[phase] = record(root / "descriptor.json")
        freshness()
        phase = "materialize"
        result = operations["materialize"](Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
            Path(descriptor["decisions_root"]), root / "materialized", review_draft_authority=descriptor,
            review_draft_binding_root=binding)
        if result.get("status") != "verified_review_draft_candidate":
            raise ValueError("materializer did not return verified review draft")
        stages[phase] = {"root": str(root / "materialized")}
        _write_new(root / "stage-materialize.json", result)
        freshness()
        phase = "build_master"
        stages[phase] = operations["build_review_master_en"](root / "materialized",
            authored / "review-draft-evidence.json", root / "master", binding_root=binding)
        if stages[phase].get("state") != "verified_review_draft":
            raise ValueError("master builder did not return verified review draft")
        _write_new(root / "stage-build-master.json", stages[phase])
        for row in structural_files:
            _checked(row)
        _verified_predecessor(request)
        return _finish(root, request_path, request, before, "structural_continuation", {
            "request_identity": request_identity, "predecessor_receipt": request["verification_receipt"],
            "structural_authorities": structural_files, "stages": stages,
            "output_inventory": deterministic_inventory(root),
            "master": record(root / "master/MASTER_EN.md"),
            "assets": record(root / "master/ASSET_MANIFEST.json")})
    except Exception as error:
        _failed(root, error, phase)
        raise
