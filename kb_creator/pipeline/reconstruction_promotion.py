from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence

from .identity import (
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    deterministic_inventory,
    file_identity,
    implementation_inventory,
    is_reparse_point,
    sha256_bytes,
)
from .manifests import sealed, validate_seal
from . import reconstruction, reconstruction_replay, reconstruction_replay_resume
from .handout_ledger import declared_occurrences, observed_occurrences


INVENTORY_SCHEMA = "kb_creator.reconstruction_upstream_inventory.v1"
MANIFEST_SCHEMA = "kb_creator.reconstruction_upstream_manifest.v1"
SOURCE_IDENTITY_SCHEMA = "kb_creator.reconstruction_source_identity.v1"
SOURCE_IDENTITY_SCHEMA_V2 = "kb_creator.reconstruction_source_identity.v2"
SOURCE_IDENTITY_SCHEMA_V3 = "kb_creator.reconstruction_source_identity.v3"
QA_SCHEMA = "kb_creator.reconstruction_qa.v1"
ACCEPTANCE_SCHEMA = "kb_creator.artifact_acceptance.v1"
PACKAGE_NAME = "reconstruction-upstream-v1"
INVENTORY_NAME = "RECONSTRUCTION_INVENTORY.json"
MANIFEST_NAME = "RECONSTRUCTION_MANIFEST.json"
QA_NAME = "RECONSTRUCTION_QA.json"
SOURCE_IDENTITY_NAME = "SOURCE_IDENTITY.json"
ACCEPTANCE_NAME = "RECONSTRUCTION_ACCEPTANCE.json"
ROLE_PATHS = {
    "reconstructed_en": "content/RECONSTRUCTED_EN.md",
    "reconstruction_manifest": MANIFEST_NAME,
    "reconstruction_qa": QA_NAME,
    "source_identity": SOURCE_IDENTITY_NAME,
}
QA_GATES = (
    "source_identity",
    "complete_stage_chain",
    "closed_decision_authority",
    "fidelity_audit",
    "page_and_role_coverage",
    "text_ocr_provenance",
    "required_entity_closure",
    "asset_closure",
    "no_open_blockers",
)
STAGE_IDS = tuple(
    reconstruction._stage_id(index, name)
    for index, name in enumerate(reconstruction.ALL_STAGES, 1)
)
RUN_KIND_LEGACY = "legacy_v1"
RUN_KIND_DIRECT_V2 = "direct_v2"
RUN_KIND_REPLAY_V2 = "replay_v2"
REPLAY_PREFIX_STAGE_SCHEMA = reconstruction_replay.STAGE_SCHEMA
REPLAY_DOWNSTREAM_STAGE_SCHEMA = reconstruction_replay_resume.STAGE_SCHEMA
REPLAY_SUBMISSION_DIRECTORY = "validated-submission-v2"
REPLAY_IMPLEMENTATION_REASONS = frozenset(
    {
        "registry_drift",
        "registry_version_mismatch",
        "registry_seal_mismatch",
        "registry_graph_mismatch",
        "producer_closure_changed",
        "legacy_closure_member_missing",
        "closure_member_missing_or_unsafe",
        "source_implementation_inventory_missing",
        "source_implementation_inventory_ambiguous",
    }
)
RESERVED = {
    "con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}
MARKER = re.compile(r"<!--\s*source-page-(\d{3})\s*-->", re.IGNORECASE)
MARKDOWN_IMAGE = re.compile(r"!\[[^\]\r\n]*\]\(([^)]+)\)")
PLAYER_HANDOUT_HEADING = re.compile(
    r"(?im)^#{1,6}\s+[^\r\n]*player[\s_-]+handout[\s_-]+(\d+)\b"
)
HANDOUT_CAPTION = re.compile(
    r"^(?:(?:figure|fig\.)\s+\d+\s+)?(?:player\s+)?handout\s+(?:#\s*)?([1-9]\d*)(?:\s*$|\s*(?:-|–|—|:)\s+\S.*)$",
    re.IGNORECASE,
)
SEMANTIC_STRUCTURE_NAME = "SEMANTIC_STRUCTURE.json"
SEMANTIC_STRUCTURE_SCHEMA = "kb_creator.reconstruction_semantic_structure.v1"
SEMANTIC_STRUCTURE_PROFILE = "visually_reviewed_semantic_containers_v1"
SEMANTIC_STRUCTURE_PROFILES = {SEMANTIC_STRUCTURE_PROFILE, "reviewed_role_outline_and_partitions_v2"}


class ReconstructionPromotionError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise ReconstructionPromotionError(code, detail)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path, code: str = "candidate_not_promotable") -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReconstructionPromotionError(code, f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        _fail(code, f"JSON root is not an object: {path}")
    return value


def _write_json(path: Path, value: object, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if exclusive else "wb"
    payload = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    with path.open(mode) as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _exact(value: Mapping[str, Any], keys: set[str], label: str, code: str) -> None:
    if set(value) != keys:
        _fail(code, f"{label} has unexpected or missing fields")


def _validate_seal(value: Mapping[str, Any], key: str, label: str, code: str) -> None:
    try:
        validate_seal(dict(value), key)
    except ValueError as error:
        raise ReconstructionPromotionError(code, f"invalid {label} seal") from error


def _safe_relative(value: Any, *, code: str = "unsafe_promotion_path") -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(code, "portable path must be a non-empty trimmed string")
    if "\\" in value or ":" in value or "\x00" in value:
        _fail(code, f"unsafe portable path: {value!r}")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if value.startswith("/") or posix.is_absolute() or windows.is_absolute() or windows.drive:
        _fail(code, f"absolute portable path: {value!r}")
    components = value.split("/")
    if (
        any(part in {"", ".", ".."} for part in components)
        or posix.as_posix() != value
    ):
        _fail(code, f"unsafe portable path component: {value!r}")
    for part in posix.parts:
        stem = part.rstrip(" .").split(".", 1)[0].casefold()
        if stem in RESERVED or part != part.rstrip(" ."):
            _fail(code, f"Windows-unsafe portable path: {value!r}")
    return value


def _safe_inventory(records: Any, *, code: str) -> list[dict[str, Any]]:
    if not isinstance(records, list):
        _fail(code, "file inventory must be an array")
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in records:
        if not isinstance(row, dict):
            _fail(code, "file inventory row must be an object")
        _exact(row, {"path", "bytes", "sha256"}, "file inventory row", code)
        path = _safe_relative(row["path"], code=code)
        folded = path.casefold()
        if folded in seen or not isinstance(row["bytes"], int) or row["bytes"] < 1 or not re.fullmatch(r"[0-9A-F]{64}", str(row["sha256"])):
            _fail(code, "duplicate or invalid file inventory row")
        seen.add(folded)
        result.append(dict(row))
    return result


def _record(path: Path, root: Path) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    _safe_relative(relative)
    return {"path": relative, **file_identity(path)}


def _copy(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        _fail("unsafe_promotion_path", f"copy source is not a regular non-symlink file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        _fail("promotion_path_exists", f"copy destination exists: {destination}")
    shutil.copyfile(source, destination)
    if file_identity(source) != file_identity(destination):
        _fail("candidate_not_promotable", f"copied file identity mismatch: {source}")


def _assert_tree_non_reparse(root: Path) -> None:
    try:
        assert_existing_path_components_are_not_reparse(root)
        for path in root.rglob("*"):
            if path.is_symlink() or is_reparse_point(path):
                _fail("unsafe_promotion_path", f"tree contains a reparse point: {path}")
    except ValueError as error:
        raise ReconstructionPromotionError("unsafe_promotion_path", str(error)) from error


def _implementation() -> dict[str, Any]:
    repo = _repo_root()
    paths = [
        repo / "kb_creator" / "__main__.py",
        repo / "kb_creator" / "pipeline" / "identity.py",
        repo / "kb_creator" / "pipeline" / "manifests.py",
        repo / "kb_creator" / "pipeline" / "reconstruction.py",
        repo / "kb_creator" / "pipeline" / "reconstruction_promotion.py",
        repo / "kb_creator" / "pipeline" / "handout_ledger.py",
        repo / "kb_creator" / "pipeline" / "semantic_structure.py",
        repo / "kb_creator" / "pipeline" / "reviewed_correction_text.py",
        repo / "kb_creator" / "pipeline" / "reviewed_prose_binding.py",
        repo / "kb_creator" / "pipeline" / "source_page_render.py",
        repo / "kb_creator" / "pipeline" / "reconstruction_asset_inventory.py",
        repo / "kb_creator" / "pipeline" / "text_segmentation.py",
        repo / "kb_creator" / "pipeline" / "publication.py",
        repo / "kb_creator" / "contracts" / "artifact_acceptance.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_upstream_inventory.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_upstream_manifest.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_source_identity.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_source_identity.v2.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_source_identity.v3.schema.json",
        repo / "kb_creator" / "contracts" / "scenario_reconstruction_contract.v2.schema.json",
        repo / "kb_creator" / "contracts" / "scenario_reconstruction_contract.v3.schema.json",
        repo / "kb_creator" / "contracts" / "run_spec.v3.schema.json",
        repo / "kb_creator" / "contracts" / "run_spec.v4.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_three_view_inputs.v3.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_semantic_structure.v1.schema.json",
        repo / "kb_creator" / "contracts" / "page_semantic_structure.v1.schema.json",
        repo / "kb_creator" / "contracts" / "page_semantic_structure.v2.schema.json",
        repo / "kb_creator" / "contracts" / "ai_merge_fidelity_audit.v4.schema.json",
    ]
    return implementation_inventory(repo, paths)


def _canonical_run_root(run_root: Path, scenario_id: str, working_root: Path | None = None) -> Path:
    try:
        resolved = run_root.resolve(strict=True)
        assert_existing_path_components_are_not_reparse(resolved)
    except (OSError, ValueError) as error:
        raise ReconstructionPromotionError("unsafe_promotion_path", "run root is missing, unresolved, or reparsed") from error
    working = (working_root or (_repo_root() / "kb_creator" / "working")).resolve()
    expected_parent = working / scenario_id / "reconstruction"
    if resolved.parent != expected_parent or not reconstruction.SAFE_RUN_ID.fullmatch(resolved.name):
        _fail("unsafe_promotion_path", "run root is outside canonical reconstruction topology")
    return resolved


def _has_replay_marker(root: Path) -> bool:
    if (root / "replay").exists() or (root / "review" / REPLAY_SUBMISSION_DIRECTORY).exists():
        return True
    for stage_id in STAGE_IDS[:4]:
        stage = root / "stages" / stage_id / "stage.json"
        if stage.is_file() and _read(stage, "reconstruction_stage_chain_invalid").get("schema") == REPLAY_PREFIX_STAGE_SCHEMA:
            return True
    for stage_id in STAGE_IDS[4:]:
        stage = root / "stages" / stage_id / "stage.json"
        if stage.is_file() and _read(stage, "reconstruction_stage_chain_invalid").get("schema") == REPLAY_DOWNSTREAM_STAGE_SCHEMA:
            return True
    return False


def _run_kind(root: Path, run: Mapping[str, Any]) -> str:
    if run.get("schema") == reconstruction.RUN_SCHEMA:
        return RUN_KIND_LEGACY
    if run.get("schema") not in reconstruction.mineru_cpu_first.RUN_SCHEMAS:
        _fail("reconstruction_stage_chain_invalid", "unsupported reconstruction run schema")
    return RUN_KIND_REPLAY_V2 if _has_replay_marker(root) else RUN_KIND_DIRECT_V2


def _validate_cpu_first_capability(run: Mapping[str, Any]) -> None:
    capability = run.get("capability_snapshot")
    if not isinstance(capability, dict):
        _fail("capability_drift", "CPU-first capability snapshot is absent")
    expected_snapshot_keys = {
        "path_hint", "bytes", "sha256", "receipt_sha256", "providers", "provider_receipt"
    }
    if set(capability) != expected_snapshot_keys:
        _fail("capability_drift", "CPU-first capability snapshot shape mismatch")
    receipt = capability.get("provider_receipt")
    providers = capability.get("providers")
    if not isinstance(receipt, dict) or not isinstance(providers, list):
        _fail("capability_drift", "CPU-first provider authority is malformed")
    try:
        reconstruction.mineru_cpu_first._lower_seal(receipt, "receipt_sha256", sorted_keys=False)
        reconstruction.mineru_cpu_first.validate_view_plan(run.get("view_plan"))
    except Exception as error:
        raise ReconstructionPromotionError("capability_drift", "CPU-first provider snapshot seal or view plan is invalid") from error
    if receipt.get("providers") != providers or receipt.get("receipt_sha256") != capability.get("receipt_sha256"):
        _fail("capability_drift", "frozen provider receipt does not equal the run snapshot")
    expected_ids = ["pipeline_cpu", "hybrid_cuda", "vlm_cuda"]
    if [row.get("provider_id") if isinstance(row, dict) else None for row in providers] != expected_ids:
        _fail("capability_drift", "provider order or domain mismatch")
    for index, row in enumerate(providers):
        if not isinstance(row, dict) or set(row) != {
            "provider_id", "required", "state", "reason_code", "profile", "verification_receipt"
        }:
            _fail("capability_drift", "provider capability row is malformed")
        expected_profile = "mineru-pipeline-cpu-windows-v1" if index == 0 else "mineru-local-windows-cu128-v1"
        expected_required = index == 0
        if row["required"] is not expected_required or row["profile"] != expected_profile:
            _fail("capability_drift", "provider requirement or profile mismatch")
        if index == 0:
            if row["state"] != "ready" or row["reason_code"] != "verified_cpu_profile":
                _fail("capability_drift", "required pipeline_cpu provider is not ready")
        elif row["state"] == "unavailable":
            if row["reason_code"] not in reconstruction.mineru_cpu_first.OPTIONAL_UNAVAILABLE_REASONS or row["verification_receipt"] is not None:
                _fail("capability_drift", "optional provider unavailable evidence is unsupported")
            continue
        elif row["state"] != "ready" or row["reason_code"] != "verified_cuda_profile":
            _fail("capability_drift", "optional provider state is invalid")
        receipt_identity = row.get("verification_receipt")
        if not isinstance(receipt_identity, dict) or set(receipt_identity) != {"path_hint", "bytes", "sha256"}:
            _fail("capability_drift", "ready provider verification identity is malformed")


def _validate_cpu_first_live_without_implementation(root: Path, run: Mapping[str, Any]) -> None:
    local = run.get("local")
    expected_local = {
        "contract_path", "source_path", "run_root", "mineru_root", "provider_capabilities_path",
        "mineru_source_root", "profile_paths", "common_paths",
    }
    if not isinstance(local, dict) or set(local) != expected_local:
        _fail("contract_drift", "CPU-first local bindings are malformed")
    contract_path = Path(str(local["contract_path"]))
    source_path = Path(str(local["source_path"]))
    try:
        _, contract_sha = reconstruction.load_contract(contract_path)
    except Exception as error:
        raise ReconstructionPromotionError("contract_drift", "reconstruction contract is invalid or stale") from error
    if contract_sha != run["contract"]["sha256"]:
        _fail("contract_drift", "stale reconstruction contract")
    if file_identity(source_path) != {"bytes": run["source"]["bytes"], "sha256": run["source"]["sha256"]}:
        _fail("source_drift", "stale reconstruction source")
    try:
        source_root = Path(str(local["mineru_source_root"])).resolve()
        mineru_root = Path(str(local["mineru_root"])).resolve()
        current_profiles: dict[str, Any] = {}
        expected_paths: dict[str, Any] = {}
        for provider in run["capability_snapshot"]["providers"]:
            if provider["state"] != "ready":
                continue
            snapshot, paths = reconstruction.mineru_cpu_first._validate_profile(provider, mineru_root, source_root)
            current_profiles[provider["provider_id"]] = snapshot
            expected_paths[provider["provider_id"]] = paths
        common_paths = {name: Path(path).resolve() for name, path in local["common_paths"].items()}
        current_common = {
            name: reconstruction.mineru_cpu_first._identity_lower(path)
            for name, path in common_paths.items()
        }
    except Exception as error:
        raise ReconstructionPromotionError("tool_drift", "CPU-first provider profile or common tool is stale") from error
    if current_profiles != run.get("provider_profiles") or expected_paths != local.get("profile_paths"):
        _fail("tool_drift", "stale CPU-first provider profile binding")
    if current_common != run.get("common_tools"):
        _fail("tool_drift", "stale CPU-first common tool binding")


def _map_direct_live_error(error: reconstruction.ControlPlaneError) -> ReconstructionPromotionError:
    mapping = {
        "stale implementation": "implementation_drift",
        "stale source": "source_drift",
        "stale contract": "contract_drift",
        "stale CPU-first provider profile binding": "tool_drift",
        "stale CPU-first common tool binding": "tool_drift",
        "invalid frozen provider capability snapshot": "capability_drift",
    }
    message = str(error)
    code = mapping.get(message)
    if code is None and message.startswith(("stale tool binding: ", "missing executable binding: ")):
        code = "tool_drift"
    if code is None and message in {
        "unexpected executable binding", "MinerU root binding mismatch", "invalid toolchain inventory",
        "invalid toolchain record", "duplicate or invalid toolchain name", "invalid executable path bindings",
    }:
        code = "tool_drift"
    if code is None and message == "stale MinerU CUDA capability binding":
        code = "capability_drift"
    return ReconstructionPromotionError(code or "reconstruction_stage_chain_invalid", message)


def _load_run_authority(run_root: Path, working_root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], Path, str]:
    try:
        run = reconstruction.load_run(run_root)
    except Exception as error:
        raise ReconstructionPromotionError("reconstruction_stage_chain_invalid", "invalid run authority") from error
    contract_path = Path(str(run.get("local", {}).get("contract_path", "")))
    try:
        contract, _ = reconstruction.load_contract(contract_path)
    except Exception as error:
        raise ReconstructionPromotionError("contract_drift", "reconstruction contract is invalid or stale") from error
    root = _canonical_run_root(run_root, contract["scenario"]["id"], working_root)
    if str(root) != str(Path(str(run["local"]["run_root"])).resolve()):
        _fail("unsafe_promotion_path", "run.json local root does not bind the canonical run root")
    kind = _run_kind(root, run)
    if (root / "skip.json").exists():
        _fail("run_not_promotable_skipped", "skipped reconstruction run cannot be promoted")
    if kind == RUN_KIND_LEGACY:
        if _has_replay_marker(root):
            _fail("reconstruction_stage_chain_invalid", "legacy run contains replay authority markers")
        capability_state = run.get("capability", {}).get("state")
        if capability_state == "unavailable":
            _fail("run_not_promotable_skipped", "unavailable reconstruction run cannot be promoted")
        if capability_state == "injected":
            _fail("run_not_production_authority", "injected-adapter run is not production authority")
        if capability_state != "available":
            _fail("capability_drift", "reconstruction capability is not available")
        try:
            reconstruction._validate_live_run_bindings(root, run)
        except reconstruction.ControlPlaneError as error:
            raise _map_direct_live_error(error) from error
    else:
        _validate_cpu_first_capability(run)
        if kind == RUN_KIND_DIRECT_V2:
            try:
                reconstruction._validate_live_run_bindings(root, run)
            except reconstruction.ControlPlaneError as error:
                raise _map_direct_live_error(error) from error
        else:
            _validate_cpu_first_live_without_implementation(root, run)
    return run, contract, root, kind


def _load_chain(root: Path, run: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], Path]:
    queue_path = root / "review" / "review_queue.json"
    snapshot_root = root / "review" / "validated-submission-v1"
    try:
        queue = reconstruction.validate_queue(queue_path, run)
        snapshot_inventory, decisions = reconstruction._validate_submission_snapshot(snapshot_root, run, queue)
        inputs = reconstruction._decision_inputs(snapshot_root / "decision_set.json", decisions, run=run, queue=queue)
        inputs_by_stage = {"fidelity_audit": inputs, "materialize_candidate": inputs}
        if run.get("schema") in reconstruction.mineru_cpu_first.RUN_SCHEMAS:
            audit_path = root / "outputs" / STAGE_IDS[4] / "audit.json"
            inputs_by_stage["materialize_candidate"] = inputs + [{"kind": "fidelity_audit", "path_hint": "outputs/05-fidelity-audit/audit.json", **file_identity(audit_path)}]
        reconstruction._validate_stage_prefix(root, run, reconstruction.ALL_STAGES, inputs_by_stage)
    except Exception as error:
        code = "decision_authority_invalid" if "submission" in str(error).lower() or "decision" in str(error).lower() or "queue" in str(error).lower() else "reconstruction_stage_chain_invalid"
        raise ReconstructionPromotionError(code, str(error)) from error
    expected_dirs = set(STAGE_IDS)
    for container in (root / "stages", root / "outputs"):
        if not container.is_dir() or {item.name for item in container.iterdir() if item.is_dir()} != expected_dirs:
            _fail("reconstruction_stage_chain_invalid", f"{container.name} stage set is incomplete or contains extras")
    manifests = [_read(root / "stages" / stage_id / "stage.json", "reconstruction_stage_chain_invalid") for stage_id in STAGE_IDS]
    return manifests, queue, snapshot_inventory, snapshot_root


def _map_replay_error(error: reconstruction_replay.ReplayError) -> ReconstructionPromotionError:
    code = "implementation_drift" if error.reason_code in REPLAY_IMPLEMENTATION_REASONS else "reconstruction_stage_chain_invalid"
    return ReconstructionPromotionError(code, str(error))


def _load_replay_chain(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    try:
        authorities = reconstruction_replay.validate_replay_authorities(root)
    except reconstruction_replay.ReplayError as error:
        raise _map_replay_error(error) from error
    try:
        review = reconstruction_replay_resume.validate_replay_review_queue(authorities)
        submission = reconstruction_replay_resume.load_replay_submission(authorities)
    except reconstruction_replay_resume.ReplayResumeError as error:
        raise ReconstructionPromotionError("decision_authority_invalid", str(error)) from error
    try:
        stage5_record = reconstruction_replay_resume._validate_downstream_stage(
            root, STAGE_IDS[4], authorities.bridge_sha256, []
        )
        stage6_record = reconstruction_replay_resume._validate_downstream_stage(
            root, STAGE_IDS[5], authorities.bridge_sha256, [stage5_record]
        )
    except reconstruction_replay_resume.ReplayResumeError as error:
        raise ReconstructionPromotionError("reconstruction_stage_chain_invalid", str(error)) from error
    manifests = [
        _read(root / "stages" / stage_id / "stage.json", "reconstruction_stage_chain_invalid")
        for stage_id in STAGE_IDS
    ]
    expected_dirs = set(STAGE_IDS)
    for container in (root / "stages", root / "outputs"):
        if not container.is_dir() or {item.name for item in container.iterdir() if item.is_dir()} != expected_dirs:
            _fail("reconstruction_stage_chain_invalid", f"{container.name} stage set is incomplete or contains extras")
    bridge_path = root / "replay/bridge.json"
    submission_path = submission.receipt_path
    stage5_expected_inputs = [
        {"path": "replay/bridge.json", **file_identity(bridge_path), "bridge_sha256": authorities.bridge_sha256},
        {"path": "review/validated-submission-v2/submission_inventory.json", **file_identity(submission_path), "submission_sha256": submission.receipt["submission_sha256"]},
    ]
    audit_path = root / "outputs/05-fidelity-audit/audit.json"
    stage6_expected_inputs = [*stage5_expected_inputs, {"path": "outputs/05-fidelity-audit/audit.json", **file_identity(audit_path)}]
    if manifests[4].get("inputs") != stage5_expected_inputs or manifests[5].get("inputs") != stage6_expected_inputs:
        _fail("reconstruction_stage_chain_invalid", "replay downstream inputs do not bind bridge, submission, and audit exactly")
    try:
        expected_audit = reconstruction_replay_resume.build_replay_audit(authorities, submission)
    except reconstruction_replay_resume.ReplayResumeError as error:
        raise ReconstructionPromotionError("fidelity_not_closed", str(error)) from error
    sealed_audit = _read(audit_path, "fidelity_not_closed")
    if sealed_audit != expected_audit or sealed_audit.get("passed") is not True or sealed_audit.get("errors") != []:
        _fail("fidelity_not_closed", "replay fidelity audit is stale, incomplete, or non-passing")
    decisions = {"decisions": submission.receipt["page_decisions"]}
    candidate_root = root / "outputs" / STAGE_IDS[5]
    candidate = _validate_candidate(
        root,
        reconstruction.load_contract(Path(str(run["local"]["contract_path"])))[0],
        submission.root,
        decisions,
        run=run,
        fidelity_path=audit_path,
        fidelity=sealed_audit,
        candidate_root=candidate_root,
        replay_bridge_sha256=authorities.bridge_sha256,
        replay_submission=submission.receipt,
        stage6_files=manifests[5]["outputs"]["files"],
    )
    return {
        "manifests": manifests,
        "queue": review.queue,
        "snapshot_inventory": {**submission.receipt, "inventory_sha256": submission.receipt["submission_sha256"]},
        "snapshot_root": submission.root,
        "decisions": decisions,
        "fidelity_source": audit_path,
        "fidelity": sealed_audit,
        "candidate": candidate,
        "authorities": authorities,
        "submission": submission,
    }


def _promotion_preflight(run_root: Path, working_root: Path | None = None) -> dict[str, Any]:
    run, contract, root, kind = _load_run_authority(run_root, working_root)
    if kind == RUN_KIND_REPLAY_V2:
        chain = _load_replay_chain(root, run)
    else:
        manifests, queue, snapshot_inventory, snapshot_root = _load_chain(root, run)
        _, decisions = reconstruction._validate_submission_snapshot(snapshot_root, run, queue)
        fidelity_source = root / "outputs" / STAGE_IDS[4] / "audit.json"
        fidelity = _validate_fidelity(
            fidelity_source,
            run["scope"]["ordered_pages"],
            run=run,
            queue=queue,
            snapshot_root=snapshot_root,
        )
        candidate = _validate_candidate(
            root,
            contract,
            snapshot_root,
            decisions,
            run=run,
            fidelity_path=fidelity_source,
            fidelity=fidelity,
        )
        chain = {
            "manifests": manifests,
            "queue": queue,
            "snapshot_inventory": snapshot_inventory,
            "snapshot_root": snapshot_root,
            "decisions": decisions,
            "fidelity_source": fidelity_source,
            "fidelity": fidelity,
            "candidate": candidate,
            "authorities": None,
            "submission": None,
        }
    return {"run": run, "contract": contract, "root": root, "kind": kind, **chain}


def preflight_reconstruction_promotion(run_root: Path, *, working_root: Path | None = None) -> dict[str, Any]:
    """Validate a promotion authority without creating or changing any artifact."""
    context = _promotion_preflight(run_root, working_root)
    return {
        "schema": "kb_creator.reconstruction_promotion_preflight.v1",
        "state": "promotion_preflight_passed",
        "run_kind": context["kind"],
        "run_identity_sha256": context["run"]["portable_identity_sha256"],
        "candidate_inventory_sha256": context["candidate"]["inventory_sha256"],
    }


def _contract_role(contract: Mapping[str, Any], page: int) -> str:
    matches = [row["role"] for row in contract["page_roles"] if row["first_page"] <= page <= row["last_page"]]
    if len(matches) != 1:
        _fail("candidate_not_promotable", f"page {page} has no unique contract role")
    return matches[0]


def _validate_fidelity(path: Path, pages: Sequence[int], *, run: Mapping[str, Any] | None = None, queue: Mapping[str, Any] | None = None, snapshot_root: Path | None = None) -> dict[str, Any]:
    value = _read(path, "fidelity_not_closed")
    if run is not None and run.get("schema") in reconstruction.mineru_cpu_first.RUN_SCHEMAS:
        _exact(value, {"schema", "authorities", "policy", "pages", "boundaries", "errors", "passed"}, "v2 fidelity audit", "fidelity_not_closed")
        policy = value.get("policy")
        authorities = value.get("authorities")
        rows = value.get("pages")
        expected_policy = {"source_completeness_threshold": 1.0, "selected_recall_threshold": 0.95, "required_views": list(reconstruction.mineru_cpu_first.REQUIRED_VIEWS), "normalization": "unicode_nfkc_casefold_alphanumeric_stream_v1", "low_text_exemption": False}
        queue_path = Path(str(run["local"]["run_root"])) / "review" / "review_queue.json"
        comparison_path = Path(str(run["local"]["run_root"])) / queue["comparison"]["path"] if queue is not None else None
        decision_set_path = snapshot_root / "decision_set.json" if snapshot_root is not None else None
        if (
            value.get("schema") != "kb_creator.ai-merge-fidelity-audit/v2"
            or value.get("passed") is not True or value.get("errors") != []
            or policy != expected_policy or not isinstance(authorities, dict)
            or queue is None or snapshot_root is None or comparison_path is None
            or authorities.get("review_queue") != {"path_hint": "review/review_queue.json", **file_identity(queue_path), "queue_sha256": queue["queue_sha256"]}
            or authorities.get("comparison") != {"path_hint": queue["comparison"]["path"], **file_identity(comparison_path)}
            or authorities.get("decision_set") != {"path_hint": "validated-submission/decision_set.json", **file_identity(decision_set_path)}
            or not isinstance(rows, list) or [row.get("source_page") for row in rows] != list(pages)
            or any(row.get("passed") is not True or row.get("completeness") != 1.0 or row.get("unaccounted_unit_count") != 0 for row in rows)
        ):
            _fail("fidelity_not_closed", "v2 fidelity audit authority or completeness is not closed")
        return value
    _exact(value, {"schema", "recall_threshold", "pages", "errors", "passed"}, "fidelity audit", "fidelity_not_closed")
    rows = value.get("pages")
    row_keys = {
        "source_page", "selected_token_count", "decision_token_count",
        "recall", "precision", "recall_threshold_applied", "word_pairs",
        "substitutions", "passed",
    }
    if (
        value.get("schema") != "kb_creator.ai-merge-fidelity-audit/v1"
        or value.get("passed") is not True
        or value.get("errors") != []
        or not isinstance(rows, list)
        or any(not isinstance(row, dict) or set(row) != row_keys for row in rows)
        or [row["source_page"] for row in rows] != list(pages)
        or any(row["passed"] is not True for row in rows)
    ):
        _fail("fidelity_not_closed", "fidelity audit is absent, incomplete, or non-passing")
    return value


def _structural_mode(
    decision_set: Mapping[str, Any], fidelity: Mapping[str, Any] | None,
    submission: Mapping[str, Any] | None,
    *, code: str,
) -> bool:
    """Select the semantic bridge only from the sealed v2/v4 authorities."""
    declared = (
        decision_set.get("schema") == reconstruction.DECISION_SET_V2_SCHEMA
        and decision_set.get("semantic_structure_profile") in SEMANTIC_STRUCTURE_PROFILES
    )
    audited = (
        isinstance(fidelity, Mapping)
        and fidelity.get("schema") == reconstruction_replay_resume.AUDIT_V4_SCHEMA
        and fidelity.get("semantic_structure_profile") == decision_set.get("semantic_structure_profile")
    )
    if declared != audited:
        _fail(code, "semantic profile declaration and fidelity authority disagree")
    if not declared:
        return False
    if submission is None or fidelity is None:
        _fail(code, "semantic profile lacks replay submission or fidelity authority")
    if fidelity.get("authorities", {}).get("submission_sha256") != submission.get("submission_sha256"):
        _fail(code, "semantic fidelity authority does not bind replay submission")
    return True


def _validate_semantic_sidecar(
    path: Path,
    *,
    pages: Sequence[int],
    fidelity: Mapping[str, Any],
    audit_path: Path,
    submission: Mapping[str, Any],
    decision_paths: Mapping[int, Path],
    code: str,
) -> dict[str, Any]:
    """Validate the Stage 06 semantic projection against sealed authorities."""
    value = _read(path, code)
    _exact(
        value,
        {"schema", "profile", "pages", "structure_sha256", "submission_sha256", "fidelity_audit", "page_decisions"},
        "semantic structure sidecar", code,
    )
    base = {key: value[key] for key in ("schema", "profile", "pages", "structure_sha256")}
    if (
        base != fidelity.get("semantic_structure")
        or value.get("schema") != SEMANTIC_STRUCTURE_SCHEMA
        or value.get("profile") not in SEMANTIC_STRUCTURE_PROFILES
        or value.get("profile") != fidelity.get("semantic_structure_profile")
        or value.get("submission_sha256") != submission.get("submission_sha256")
        or value.get("fidelity_audit") != {
            "path": "outputs/05-fidelity-audit/audit.json", **file_identity(audit_path)
        }
    ):
        _fail(code, "semantic sidecar does not bind the sealed audit and submission")
    rows = value.get("page_decisions")
    if (
        not isinstance(rows, list)
        or [row.get("source_page") if isinstance(row, dict) else None for row in rows] != list(pages)
        or any(not isinstance(row, dict) or set(row) != {"source_page", "sha256"} for row in rows)
    ):
        _fail(code, "semantic sidecar page-decision domain is not exact and ordered")
    submission_rows = submission.get("page_decisions")
    if not isinstance(submission_rows, list):
        _fail(code, "semantic sidecar submission page-decision authority is invalid")
    submission_by_page = {row.get("source_page"): row for row in submission_rows if isinstance(row, dict)}
    if set(submission_by_page) != set(pages):
        _fail(code, "semantic sidecar submission page-decision domain is incomplete")
    for row in rows:
        page = row["source_page"]
        digest = row["sha256"]
        expected = submission_by_page[page]
        decision = decision_paths.get(page)
        if (
            not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest)
            or decision is None
            or digest != expected.get("sha256")
            or file_identity(decision).get("sha256") != digest
        ):
            _fail(code, f"semantic sidecar page {page} decision identity mismatch")
    return value


def _caption_line(line: str, representation: Any) -> str:
    """Remove only syntax proven by a reviewed semantic representation."""
    value = line
    if representation == "blockquote":
        while True:
            stripped = re.sub(r"^\s*>\s?", "", value)
            if stripped == value:
                break
            value = stripped
    value = re.sub(r"^\s{0,3}#{1,6}\s+", "", value).strip()
    emphasis = re.fullmatch(r"(\*\*|__|\*|_)(.+)\1", value)
    if emphasis is not None:
        value = emphasis.group(2).strip()
    return value


def _semantic_handout_numbers(
    decisions: Mapping[int, Mapping[str, Any]], *, code: str,
) -> set[int]:
    """Extract visible handout captions from already validated handout spans."""
    from .semantic_structure import SemanticStructureError, apply_block_boundaries

    numbered: set[int] = set()
    for page, decision in decisions.items():
        markdown = decision.get("markdown")
        structure = decision.get("semantic_structure")
        if not isinstance(markdown, str) or not isinstance(structure, dict):
            _fail(code, f"page {page} structural decision is incomplete")
        units = structure.get("units")
        if not isinstance(units, list):
            _fail(code, f"page {page} structural units are invalid")
        try:
            lines = apply_block_boundaries(markdown, decision.get("block_boundaries")).splitlines()
        except SemanticStructureError as error:
            raise ReconstructionPromotionError(code, f"page {page} structural boundaries are invalid") from error
        for unit in units:
            if not isinstance(unit, dict) or unit.get("kind") != "handout":
                continue
            span = unit.get("markdown_span")
            if (
                not isinstance(span, dict)
                or type(span.get("start_line")) is not int
                or type(span.get("end_line")) is not int
                or not 1 <= span["start_line"] <= span["end_line"] <= len(lines)
            ):
                _fail(code, f"page {page} handout span is invalid")
            matches = {
                int(match.group(1))
                for line in lines[span["start_line"] - 1:span["end_line"]]
                if (match := HANDOUT_CAPTION.fullmatch(_caption_line(line, unit.get("representation"))))
            }
            if len(matches) > 1:
                _fail(code, f"page {page} handout span has ambiguous visible captions")
            numbered.update(matches)
    return numbered


def _visible_handout_heading_numbers(markdown: str) -> set[int]:
    """Recognize standalone source captions without counting prose references."""
    numbered = {int(value) for value in PLAYER_HANDOUT_HEADING.findall(markdown)}
    for line in markdown.splitlines():
        if re.match(r"^#{1,6}\s+", line) is None:
            continue
        match = HANDOUT_CAPTION.fullmatch(_caption_line(line, "atx_heading"))
        if match:
            numbered.add(int(match.group(1)))
    return numbered


def _v3_handout_ledger(contract: Mapping[str, Any], decisions: Mapping[int, Mapping[str, Any]], *, code: str) -> set[tuple[str, str, int, str]]:
    try:
        return observed_occurrences(contract, decisions)
    except ValueError as error:
        _fail(code, str(error))


def _validate_candidate(root: Path, contract: Mapping[str, Any], snapshot_root: Path, decisions: Mapping[str, Any], *, run: Mapping[str, Any] | None = None, fidelity_path: Path | None = None, fidelity: Mapping[str, Any] | None = None, candidate_root: Path | None = None, replay_bridge_sha256: str | None = None, replay_submission: Mapping[str, Any] | None = None, stage6_files: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    candidate = candidate_root or (root / "outputs" / STAGE_IDS[5] / "candidate")
    decision_set = _read(snapshot_root / "decision_set.json", "candidate_not_promotable")
    structural = _structural_mode(
        decision_set, fidelity, replay_submission, code="candidate_not_promotable"
    )
    required_top = {"RECONSTRUCTED_EN.md", "MERGE_PROVENANCE.json", "ASSET_MANIFEST.json", "OVERLAY_SELECTION.json", "pages", "decisions", "assets"}
    if structural:
        required_top.add(SEMANTIC_STRUCTURE_NAME)
    if not candidate.is_dir() or {item.name for item in candidate.iterdir()} != required_top:
        _fail("candidate_not_promotable", "candidate root shape is incomplete or contains extras")
    try:
        _assert_tree_non_reparse(candidate)
        inventory = deterministic_inventory(candidate)
    except ValueError as error:
        raise ReconstructionPromotionError("unsafe_promotion_path", str(error)) from error
    if stage6_files is not None and inventory != list(stage6_files):
        _fail("candidate_not_promotable", "flat candidate is not the exact Stage 06 output inventory")
    pages = list(range(1, contract["source"]["page_count"] + 1))
    expected_page_names = {f"page-{page:03d}.md" for page in pages}
    expected_decision_names = {f"page-{page:03d}.json" for page in pages}
    if {p.name for p in (candidate / "pages").iterdir()} != expected_page_names or {p.name for p in (candidate / "decisions").iterdir()} != expected_decision_names:
        _fail("candidate_not_promotable", "candidate page or decision domain mismatch")
    combined = (candidate / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")
    if [int(item) for item in MARKER.findall(combined)] != pages:
        _fail("candidate_not_promotable", "combined source-page markers are missing, duplicated, or out of order")
    decision_by_page = {row["source_page"]: row for row in decisions["decisions"]}
    loaded_decisions: dict[int, dict[str, Any]] = {}
    all_markdown = [combined]
    handout_names: set[str] = set()
    for page in pages:
        page_path = candidate / "pages" / f"page-{page:03d}.md"
        text = page_path.read_text(encoding="utf-8")
        all_markdown.append(text)
        if [int(item) for item in MARKER.findall(text)] != [page]:
            _fail("candidate_not_promotable", f"page {page} marker mismatch")
        decision_path = candidate / "decisions" / f"page-{page:03d}.json"
        snapshot_path = snapshot_root / f"pages/page-{page:03d}.json"
        if file_identity(decision_path) != file_identity(snapshot_path) or file_identity(decision_path) != {"bytes": decision_by_page[page]["bytes"], "sha256": decision_by_page[page]["sha256"]}:
            _fail("candidate_not_promotable", f"page {page} decision copy mismatch")
        decision = _read(decision_path)
        loaded_decisions[page] = decision
        decision_keys = frozenset({
            "schema", "source_page", "semantic_role", "overlay_preference",
            "selected_blocks", "markdown", "assets", "unresolved", "review",
        })
        allowed_decision_keys = {
            decision_keys | ({"semantic_structure"} if structural else set()),
            decision_keys | {"block_boundaries"} | ({"semantic_structure"} if structural else set()),
        }
        if structural:
            allowed_decision_keys |= {keys | {"reviewed_block_corrections"} for keys in allowed_decision_keys}
        if not isinstance(decision, dict) or frozenset(decision) not in allowed_decision_keys:
            _fail("candidate_not_promotable", f"page {page} decision keys mismatch")
        if decision.get("semantic_role") != _contract_role(contract, page) or decision.get("unresolved") != [] or decision.get("review", {}).get("visual_reviewed") is not True:
            _fail("candidate_not_promotable", f"page {page} role or closed-review mismatch")
        for asset in decision.get("assets", []):
            if isinstance(asset, dict) and asset.get("placement") == "handout" and isinstance(asset.get("logical_name"), str):
                handout_names.add(asset["logical_name"].casefold())
    asset_manifest = _read(candidate / "ASSET_MANIFEST.json")
    _exact(asset_manifest, {"assets"}, "asset manifest", "candidate_not_promotable")
    records = asset_manifest["assets"]
    if not isinstance(records, list):
        _fail("candidate_not_promotable", "asset manifest rows are invalid")
    declared_files: set[str] = set()
    logical_names: set[str] = set()
    for row in records:
        if not isinstance(row, dict):
            _fail("candidate_not_promotable", "asset row is invalid")
        source_render = row.get("origin") == "source_pdf_page_render_v1"
        _exact(row, {"origin", "source_page", "source_sha256", "logical_name", "placement", "render", "source_visual_review", "sha256", "stored_path"} if source_render else {"view", "source_path", "logical_name", "placement", "sha256", "stored_path"}, "asset row", "candidate_not_promotable")
        if source_render:
            decision = loaded_decisions.get(row["source_page"], {})
            matches = [asset for asset in decision.get("assets", []) if isinstance(asset, dict) and asset.get("origin") == "source_pdf_page_render_v1" and asset.get("logical_name") == row["logical_name"]]
            proofs = [page for page in (fidelity or {}).get("pages", []) if page.get("source_page") == row["source_page"]]
            proof_rows = proofs[0].get("source_page_renders", []) if len(proofs) == 1 else []
            if len(matches) != 1 or len([proof for proof in proof_rows if proof.get("logical_name") == row["logical_name"] and proof.get("render") == row["render"]]) != 1:
                _fail("candidate_not_promotable", "source-page render lacks matching closed decision or Stage05 proof")
        stored = _safe_relative(row["stored_path"])
        if not stored.startswith("assets/") or str(row["logical_name"]).casefold() in logical_names:
            _fail("candidate_not_promotable", "asset row path or logical name is invalid")
        logical_names.add(str(row["logical_name"]).casefold())
        asset = candidate / stored
        if not asset.is_file() or file_identity(asset)["sha256"] != row["sha256"]:
            _fail("candidate_not_promotable", "asset file identity mismatch")
        declared_files.add(stored)
    actual_assets = {path.relative_to(candidate).as_posix() for path in (candidate / "assets").rglob("*") if path.is_file()}
    if actual_assets != declared_files:
        _fail("candidate_not_promotable", "asset manifest and asset tree are not closed")
    references: set[str] = set()
    for markdown in all_markdown:
        for target in MARKDOWN_IMAGE.findall(markdown):
            if "://" in target or target.startswith(("/", "\\")):
                _fail("candidate_not_promotable", "Markdown asset reference escapes the candidate")
            normalized = target[3:] if target.startswith("../assets/") else target
            if not normalized.startswith("assets/"):
                _fail("candidate_not_promotable", "Markdown image is not a closed package asset")
            references.add(normalized)
    required_references = {row["stored_path"] for row in records if row["placement"] != "reference_only"}
    if not required_references.issubset(references) or not references.issubset(actual_assets):
        _fail("candidate_not_promotable", "Markdown and asset manifest references are not closed")
    overlay = _read(candidate / "OVERLAY_SELECTION.json")
    overlay_rows = overlay.get("pages")
    if set(overlay) != {"pages"} or not isinstance(overlay_rows, list) or any(not isinstance(row, dict) or set(row) != {"source_page", "overlay_preference"} for row in overlay_rows) or [row["source_page"] for row in overlay_rows] != pages:
        _fail("candidate_not_promotable", "overlay selection page domain mismatch")
    provenance = _read(candidate / "MERGE_PROVENANCE.json")
    provenance_rows = provenance.get("pages")
    provenance_keys = {"source_page", "semantic_role", "packet", "packet_sha256", "decision_sha256", "selected_blocks", "unresolved"}
    replay_v2 = replay_bridge_sha256 is not None
    v2 = run is not None and run.get("schema") in reconstruction.mineru_cpu_first.RUN_SCHEMAS
    expected_top = (
        {"schema", "status", "run_identity_sha256", "bridge_sha256", "submission", "comparison", "fidelity_audit", "pages", "acceptance_inferred"}
        if replay_v2
        else {"schema", "status", "raw_comparison", "fidelity_audit", "authorities", "pages"}
        if v2
        else {"schema", "status", "raw_comparison", "pages"}
    )
    expected_schema = (
        reconstruction_replay_resume.PROVENANCE_SCHEMA
        if replay_v2
        else "kb_creator.mineru_ai_merge_provenance.v2"
        if v2
        else "kb_creator.mineru_ai_merge_provenance.v1"
    )
    if set(provenance) != expected_top or provenance.get("schema") != expected_schema or provenance.get("status") != "candidate_ready_for_reconstruction_qa" or not isinstance(provenance_rows, list) or any(not isinstance(row, dict) or set(row) != provenance_keys for row in provenance_rows) or [row["source_page"] for row in provenance_rows] != pages or any(row["unresolved"] != [] for row in provenance_rows):
        _fail("candidate_not_promotable", "materializer provenance is incomplete or non-ready")
    if replay_v2:
        comparison_path = root / "outputs/03-compare-views/comparison.json"
        if (
            run is None or replay_submission is None or fidelity_path is None or fidelity is None
            or provenance.get("run_identity_sha256") != run.get("portable_identity_sha256")
            or provenance.get("bridge_sha256") != replay_bridge_sha256
            or provenance.get("acceptance_inferred") is not False
            or provenance.get("submission") != {
                "path": "review/validated-submission-v2/submission_inventory.json",
                **file_identity(snapshot_root / "submission_inventory.json"),
                "submission_sha256": replay_submission.get("submission_sha256"),
            }
            or provenance.get("comparison") != {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}
            or provenance.get("fidelity_audit") != {"path": "outputs/05-fidelity-audit/audit.json", **file_identity(fidelity_path)}
        ):
            _fail("candidate_not_promotable", "replay provenance authority is stale or inferred")
    elif v2 and (fidelity_path is None or fidelity is None or provenance.get("fidelity_audit") != {"path": str(fidelity_path.resolve()), **file_identity(fidelity_path)} or provenance.get("authorities") != fidelity.get("authorities")):
        _fail("candidate_not_promotable", "materializer provenance does not bind the passed v2 audit")
    run_root = root
    for row in provenance_rows:
        page = row["source_page"]
        packet = run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json"
        expected_selected = [
            {"view": item["view"], "raw_index": item["raw_index"]}
            for item in loaded_decisions[page]["selected_blocks"]
        ]
        if (
            ((root / str(row["packet"])).resolve() if replay_v2 else Path(str(row["packet"])).resolve()) != packet.resolve()
            or row["packet_sha256"] != file_identity(packet)["sha256"]
            or row["decision_sha256"] != decision_by_page[page]["sha256"]
            or row["semantic_role"] != _contract_role(contract, page)
            or row["selected_blocks"] != expected_selected
        ):
            _fail("candidate_not_promotable", f"page {page} selected-block provenance mismatch")
    sidecar = None
    if structural:
        if fidelity_path is None or fidelity is None or replay_submission is None:
            _fail("candidate_not_promotable", "semantic candidate lacks sealed fidelity authority")
        sidecar = _validate_semantic_sidecar(
            candidate / SEMANTIC_STRUCTURE_NAME,
            pages=pages,
            fidelity=fidelity,
            audit_path=fidelity_path,
            submission=replay_submission,
            decision_paths={page: candidate / "decisions" / f"page-{page:03d}.json" for page in pages},
            code="candidate_not_promotable",
        )
    if contract.get("contract_revision") == 3:
        observed = _v3_handout_ledger(contract, loaded_decisions, code="candidate_not_promotable")
        expected = declared_occurrences(contract)
        if observed != expected:
            _fail("candidate_not_promotable", f"handout occurrence ledger mismatch: missing {sorted(expected - observed)}, extra {sorted(observed - expected)}")
        return {"root": candidate, "files": inventory, "inventory_sha256": sha256_bytes(canonical_bytes(inventory)), "pages": pages, "asset_manifest": asset_manifest, "provenance": provenance, "semantic_sidecar": sidecar}
    numbered = _visible_handout_heading_numbers(combined)
    numbered.update(
        int(match)
        for name in handout_names
        for match in re.findall(r"player[\s_-]+handout[\s_-]+(\d+)\b", name)
    )
    if structural:
        numbered.update(_semantic_handout_numbers(loaded_decisions, code="candidate_not_promotable"))
    expected_handouts = contract["scope"]["required_entities"]["numbered_player_handouts"]
    if numbered != set(range(1, expected_handouts + 1)):
        _fail("candidate_not_promotable", f"contract-derived required-entity count mismatch: expected handouts 1..{expected_handouts}, observed {sorted(numbered)}")
    return {"root": candidate, "files": inventory, "inventory_sha256": sha256_bytes(canonical_bytes(inventory)), "pages": pages, "asset_manifest": asset_manifest, "provenance": provenance, "semantic_sidecar": sidecar}


def _portable_provenance(candidate: Mapping[str, Any], snapshot_root: Path, *, run_root: Path | None = None, fidelity: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = []
    for row in candidate["provenance"]["pages"]:
        page = row["source_page"]
        decision = snapshot_root / f"pages/page-{page:03d}.json"
        page_file = candidate["root"] / f"pages/page-{page:03d}.md"
        authority_root = run_root or candidate["root"].parents[2]
        packet = authority_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json"
        packet_identity = file_identity(packet)
        if packet_identity["sha256"] != row["packet_sha256"]:
            _fail("candidate_not_promotable", f"page {page} merge packet identity mismatch")
        rows.append({
            "source_page": page,
            "semantic_role": row["semantic_role"],
            "merge_packet": packet_identity,
            "decision": {"path": f"evidence/review/pages/page-{page:03d}.json", **file_identity(decision)},
            "page": {"path": f"content/pages/page-{page:03d}.md", **file_identity(page_file)},
            "selected_blocks": row["selected_blocks"],
        })
    if candidate["provenance"].get("schema") == reconstruction_replay_resume.PROVENANCE_SCHEMA:
        if fidelity is None:
            _fail("candidate_not_promotable", "replay portable provenance lacks validated fidelity authority")
        audit = candidate["provenance"]["fidelity_audit"]
        return {
            "schema": "kb_creator.reconstruction_merge_provenance.v2",
            "status": "candidate_ready_for_user_reconstruction_review",
            "fidelity_audit": {"path": "evidence/fidelity/audit.json", "bytes": audit["bytes"], "sha256": audit["sha256"]},
            "authorities": fidelity["authorities"],
            "pages": rows,
        }
    if candidate["provenance"].get("schema") == "kb_creator.mineru_ai_merge_provenance.v2":
        audit = candidate["provenance"]["fidelity_audit"]
        return {
            "schema": "kb_creator.reconstruction_merge_provenance.v2",
            "status": "candidate_ready_for_user_reconstruction_review",
            "fidelity_audit": {"path": "evidence/fidelity/audit.json", "bytes": audit["bytes"], "sha256": audit["sha256"]},
            "authorities": candidate["provenance"]["authorities"],
            "pages": rows,
        }
    return {"schema": "kb_creator.reconstruction_merge_provenance.v1", "status": "candidate_ready_for_user_reconstruction_review", "pages": rows}


def _source_identity(run: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    mixed = "page_geometry" in run["source"]
    revision = run["contract"]["contract_revision"]
    schema = SOURCE_IDENTITY_SCHEMA_V3 if revision == 3 else SOURCE_IDENTITY_SCHEMA_V2 if mixed else SOURCE_IDENTITY_SCHEMA
    return sealed(schema, {
        "scenario_id": contract["scenario"]["id"],
        "run_identity_sha256": run["portable_identity_sha256"],
        "contract": {"basename": run["contract"]["path_hint"], "bytes": run["contract"]["bytes"], "sha256": run["contract"]["sha256"], "contract_revision": run["contract"]["contract_revision"]},
        "source": {"basename": run["source"]["path_hint"], "bytes": run["source"]["bytes"], "sha256": run["source"]["sha256"], "page_count": run["source"]["page_count"], **({"page_geometry": run["source"]["page_geometry"]} if mixed else {"media_box_points": run["source"]["media_box_points"], "rotation_degrees": run["source"]["rotation_degrees"]})},
    }, digest_key="source_identity_sha256")


def _qa(run: Mapping[str, Any], contract: Mapping[str, Any], package: Path, stage6: Path, fidelity: Path, snapshot_inventory: Mapping[str, Any]) -> dict[str, Any]:
    return sealed(QA_SCHEMA, {
        "state": "candidate_ready_for_user_reconstruction_review",
        "scenario_id": contract["scenario"]["id"],
        "run_identity_sha256": run["portable_identity_sha256"],
        "reconstruction_contract_sha256": run["contract"]["sha256"],
        "source_sha256": run["source"]["sha256"],
        "candidate": _record(package / "content/RECONSTRUCTED_EN.md", package),
        "producer_stage": _record(stage6, package),
        "fidelity": _record(fidelity, package),
        "decision_authority_sha256": snapshot_inventory["inventory_sha256"],
        "findings": [],
        "gates": [{"name": name, "status": "pass", "errors": []} for name in QA_GATES],
    }, digest_key="qa_sha256")


def _validate_qa(value: dict[str, Any], *, code: str = "reconstruction_qa_not_closed") -> None:
    _exact(value, {"schema", "state", "scenario_id", "run_identity_sha256", "reconstruction_contract_sha256", "source_sha256", "candidate", "producer_stage", "fidelity", "decision_authority_sha256", "findings", "gates", "qa_sha256"}, "reconstruction QA", code)
    _validate_seal(value, "qa_sha256", "reconstruction QA", code)
    gates = value.get("gates")
    if value.get("schema") != QA_SCHEMA or value.get("state") != "candidate_ready_for_user_reconstruction_review" or value.get("findings") != [] or not isinstance(gates, list) or any(not isinstance(row, dict) for row in gates) or [row["name"] for row in gates] != list(QA_GATES) or any(set(row) != {"name", "status", "errors"} or row.get("status") != "pass" or row.get("errors") != [] for row in gates):
        _fail(code, "reconstruction QA gates are not exactly closed and passing")


def _cleanup_owned_published_package(
    package: Path,
    expected_inventory: Sequence[Mapping[str, Any]],
    *,
    promotion_root_created: bool,
) -> None:
    """Remove only the unchanged package published by the current invocation."""
    promotion_root = package.parent
    if package.name != PACKAGE_NAME or promotion_root.name != "promotion":
        _fail("unsafe_promotion_path", "refusing cleanup outside the fixed promotion topology")
    try:
        assert_existing_path_components_are_not_reparse(promotion_root)
        if package.is_symlink() or is_reparse_point(package):
            _fail("unsafe_promotion_path", "refusing cleanup of a reparsed promotion package")
        _assert_tree_non_reparse(package)
        observed = deterministic_inventory(package)
    except (OSError, ValueError) as error:
        raise ReconstructionPromotionError("unsafe_promotion_path", "published package cannot be verified for rollback") from error
    if observed != list(expected_inventory):
        _fail("unsafe_promotion_path", "published package changed before rollback; cleanup refused")
    shutil.rmtree(package)
    if promotion_root_created and promotion_root.is_dir() and not any(promotion_root.iterdir()):
        promotion_root.rmdir()


def materialize_reconstruction_promotion(run_root: Path, *, working_root: Path | None = None) -> dict[str, Any]:
    context = _promotion_preflight(run_root, working_root)
    run, contract, root, kind = context["run"], context["contract"], context["root"], context["kind"]
    manifests, queue = context["manifests"], context["queue"]
    snapshot_inventory, snapshot_root = context["snapshot_inventory"], context["snapshot_root"]
    fidelity_source, fidelity_report, candidate = context["fidelity_source"], context["fidelity"], context["candidate"]
    package = root / "promotion" / PACKAGE_NAME
    staging = root / "promotion" / f".{PACKAGE_NAME}.staging"
    if package.exists() or staging.exists():
        _fail("promotion_path_exists", "promotion destination or staging residue exists")
    promotion_root_created = not package.parent.exists()
    package.parent.mkdir(exist_ok=True)
    published = False
    published_inventory: list[dict[str, Any]] = []
    try:
        staging.mkdir()
        content = staging / "content"
        (content / "pages").mkdir(parents=True)
        (content / "assets").mkdir()
        for name in ("RECONSTRUCTED_EN.md", "ASSET_MANIFEST.json", "OVERLAY_SELECTION.json"):
            _copy(candidate["root"] / name, content / name)
        if candidate["semantic_sidecar"] is not None:
            _copy(candidate["root"] / SEMANTIC_STRUCTURE_NAME, content / SEMANTIC_STRUCTURE_NAME)
        for directory in ("pages", "assets"):
            for source in sorted((candidate["root"] / directory).rglob("*")):
                if source.is_file():
                    _copy(source, content / source.relative_to(candidate["root"]))
        run_portable = {key: value for key, value in run.items() if key != "local"}
        _write_json(staging / "evidence/run/run.portable.json", run_portable)
        stage_records = []
        for stage_id, name, manifest in zip(STAGE_IDS, reconstruction.ALL_STAGES, manifests):
            destination = staging / f"evidence/stages/{stage_id}.stage.json"
            _copy(root / "stages" / stage_id / "stage.json", destination)
            digest = manifest["manifest_sha256"] if kind == RUN_KIND_REPLAY_V2 and stage_id in STAGE_IDS[4:] else manifest["reproducible_sha256"]
            stage_records.append({"stage_id": stage_id, "stage_name": name, "manifest": _record(destination, staging), "reproducible_sha256": digest})
        _copy(root / "review/review_queue.json", staging / "evidence/review/review_queue.json")
        _copy(snapshot_root / "decision_set.json", staging / "evidence/review/decision_set.json")
        for source in sorted((snapshot_root / "pages").glob("*.json")):
            _copy(source, staging / "evidence/review/pages" / source.name)
        if (snapshot_root / "reviewed_allowlist.json").exists():
            _copy(snapshot_root / "reviewed_allowlist.json", staging / "evidence/review/reviewed_allowlist.json")
        _copy(snapshot_root / "submission_inventory.json", staging / "evidence/review/submission_inventory.json")
        _write_json(staging / "evidence/review/MERGE_PROVENANCE.portable.json", _portable_provenance(candidate, snapshot_root, run_root=root, fidelity=fidelity_report))
        if kind == RUN_KIND_REPLAY_V2:
            _copy(root / "replay/intake.json", staging / "evidence/replay/intake.json")
            _copy(root / "replay/bridge.json", staging / "evidence/replay/bridge.json")
            if (root / "replay/completion.json").is_file():
                _copy(root / "replay/completion.json", staging / "evidence/replay/completion.json")
            for stage_id in STAGE_IDS[:3 if (root / "replay/completion.json").is_file() else 4]:
                _copy(root / "stages" / stage_id / "rebase.json", staging / f"evidence/replay/{stage_id}.rebase.json")
        _copy(fidelity_source, staging / "evidence/fidelity/audit.json")
        _write_json(staging / SOURCE_IDENTITY_NAME, _source_identity(run, contract))
        stage6 = staging / f"evidence/stages/{STAGE_IDS[5]}.stage.json"
        fidelity = staging / "evidence/fidelity/audit.json"
        qa = _qa(run, contract, staging, stage6, fidelity, snapshot_inventory)
        _write_json(staging / QA_NAME, qa)
        content_files = deterministic_inventory(content)
        package_files = deterministic_inventory(staging)
        review = {
            "queue": _record(staging / "evidence/review/review_queue.json", staging),
            "validated_submission": _record(staging / "evidence/review/submission_inventory.json", staging),
            "decision_set": _record(staging / "evidence/review/decision_set.json", staging),
            "decisions": [_record(path, staging) for path in sorted((staging / "evidence/review/pages").glob("*.json"))],
            "reviewed_allowlist": _record(staging / "evidence/review/reviewed_allowlist.json", staging) if (staging / "evidence/review/reviewed_allowlist.json").exists() else None,
        }
        manifest = sealed(MANIFEST_SCHEMA, {
            "package_state": "candidate_awaiting_reconstruction_acceptance",
            "scenario": contract["scenario"],
            "run": {"run_id": run["run_id"], "portable_identity_sha256": run["portable_identity_sha256"]},
            "reconstruction_contract": {"basename": run["contract"]["path_hint"], "bytes": run["contract"]["bytes"], "sha256": run["contract"]["sha256"], "contract_revision": run["contract"]["contract_revision"]},
            "source_identity": _record(staging / SOURCE_IDENTITY_NAME, staging),
            "review": review,
            "stages": stage_records,
            "candidate": {"files": candidate["files"], "inventory_sha256": candidate["inventory_sha256"]},
            "content": {"files": content_files, "inventory_sha256": sha256_bytes(canonical_bytes(content_files))},
            "fidelity": _record(fidelity, staging),
            "qa": _record(staging / QA_NAME, staging),
            "implementation": _implementation(),
            "package_files": package_files,
        }, digest_key="manifest_sha256")
        _write_json(staging / MANIFEST_NAME, manifest)
        artifacts = [{"role": role, **_record(staging / relative, staging)} for role, relative in ROLE_PATHS.items()]
        inventory = sealed(INVENTORY_SCHEMA, {"scenario_id": contract["scenario"]["id"], "reconstruction_contract_sha256": run["contract"]["sha256"], "artifacts": artifacts}, digest_key="inventory_sha256")
        _write_json(staging / INVENTORY_NAME, inventory)
        published_inventory = deterministic_inventory(staging)
        _promotion_preflight(root, working_root)
        if package.exists():
            _fail("promotion_path_exists", "promotion destination appeared before publish")
        try:
            os.rename(staging, package)
            published = True
        except FileExistsError as error:
            raise ReconstructionPromotionError(
                "promotion_path_exists", "promotion destination won the publish race"
            ) from error
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if published:
            _cleanup_owned_published_package(
                package,
                published_inventory,
                promotion_root_created=promotion_root_created,
            )
        raise
    try:
        validate_reconstruction_package(package, require_acceptance=False, working_root=working_root)
    except Exception:
        _cleanup_owned_published_package(
            package,
            published_inventory,
            promotion_root_created=promotion_root_created,
        )
        raise
    return {"schema": "kb_creator.reconstruction_promotion_result.v1", "state": "candidate_awaiting_reconstruction_acceptance", "exit_code": 0, "run_identity_sha256": run["portable_identity_sha256"], "package_root": str(package), "inventory": str(package / INVENTORY_NAME), "acceptance": None}


def _validate_source_identity(value: dict[str, Any], scenario_id: str) -> None:
    _exact(value, {"schema", "scenario_id", "run_identity_sha256", "contract", "source", "source_identity_sha256"}, "source identity", "candidate_not_promotable")
    _validate_seal(value, "source_identity_sha256", "source identity", "candidate_not_promotable")
    if value.get("schema") not in {SOURCE_IDENTITY_SCHEMA, SOURCE_IDENTITY_SCHEMA_V2, SOURCE_IDENTITY_SCHEMA_V3} or value.get("scenario_id") != scenario_id:
        _fail("candidate_not_promotable", "source identity schema or scenario mismatch")
    revision = 3 if value["schema"] == SOURCE_IDENTITY_SCHEMA_V3 else 2 if value["schema"] == SOURCE_IDENTITY_SCHEMA_V2 else 1
    if value.get("contract", {}).get("contract_revision") != revision:
        _fail("candidate_not_promotable", "source identity contract revision mismatch")
    mixed = "page_geometry" in value.get("source", {})
    if mixed:
        try:
            reconstruction._validate_page_geometry(value["source"].get("page_geometry"), value["source"].get("page_count"))
        except (ValueError, KeyError, TypeError) as error:
            raise ReconstructionPromotionError("candidate_not_promotable", "source identity page geometry invalid") from error
    expected = {
        "contract": {"basename", "bytes", "sha256", "contract_revision"},
        "source": {"basename", "bytes", "sha256", "page_count", "page_geometry"} if mixed else {"basename", "bytes", "sha256", "page_count", "media_box_points", "rotation_degrees"},
    }
    for label, keys in expected.items():
        record = value[label]
        if not isinstance(record, dict):
            _fail("candidate_not_promotable", f"{label} identity is not an object")
        _exact(record, keys, f"{label} identity", "candidate_not_promotable")
        if "/" in str(record.get("basename", "")) or "\\" in str(record.get("basename", "")) or ":" in str(record.get("basename", "")):
            _fail("unsafe_promotion_path", f"{label} identity exposes an unsafe basename")


def _identity_at(package: Path, record: Mapping[str, Any], label: str, code: str) -> Path:
    if not isinstance(record, dict):
        _fail(code, f"{label} identity is invalid")
    _exact(record, {"path", "bytes", "sha256"}, label, code)
    relative = _safe_relative(record["path"], code=code)
    path = package / relative
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(package.resolve())
        assert_existing_path_components_are_not_reparse(resolved)
        if not resolved.is_file() or resolved.is_symlink() or file_identity(resolved) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            _fail(code, f"{label} identity mismatch")
    except (OSError, ValueError) as error:
        raise ReconstructionPromotionError(code, f"{label} identity mismatch") from error
    return resolved


def _validate_acceptance(package: Path, inventory: dict[str, Any], manifest: dict[str, Any], qa: dict[str, Any]) -> dict[str, Any]:
    path = package / ACCEPTANCE_NAME
    value = _read(path, "invalid_or_unaccepted_reconstruction")
    _exact(value, {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"}, "reconstruction acceptance", "invalid_or_unaccepted_reconstruction")
    _validate_seal(value, "receipt_sha256", "reconstruction acceptance", "invalid_or_unaccepted_reconstruction")
    roles = {row["role"]: {key: row[key] for key in ("path", "bytes", "sha256")} for row in inventory["artifacts"]}
    producer = manifest["stages"][5]["manifest"]
    fidelity = _read(package / "evidence/fidelity/audit.json", "invalid_or_unaccepted_reconstruction")
    evidence_paths = [INVENTORY_NAME, MANIFEST_NAME, QA_NAME, SOURCE_IDENTITY_NAME, "evidence/fidelity/audit.json"]
    if fidelity.get("schema") == reconstruction_replay_resume.AUDIT_V4_SCHEMA:
        evidence_paths.append(f"content/{SEMANTIC_STRUCTURE_NAME}")
    expected_evidence = [_record(package / item, package) for item in evidence_paths]
    if value.get("schema") != ACCEPTANCE_SCHEMA or value.get("scenario_id") != inventory["scenario_id"] or value.get("artifact_kind") != "reconstructed_en" or value.get("candidate") != roles["reconstructed_en"] or value.get("producer_stage") != producer or value.get("evidence") != expected_evidence or value.get("decision") != "accepted" or value.get("recorder_role") != "main_orchestrator" or not isinstance(value.get("decision_at_utc"), str) or not value["decision_at_utc"].strip() or not isinstance(value.get("user_decision_reference"), str) or not value["user_decision_reference"].strip():
        _fail("invalid_or_unaccepted_reconstruction", "reconstruction acceptance is stale, incomplete, or not orchestrator-recorded")
    for record in [value["candidate"], value["producer_stage"], *value["evidence"]]:
        _identity_at(package, record, "acceptance evidence", "invalid_or_unaccepted_reconstruction")
    return value


def _validate_packaged_stages(
    package: Path,
    stages: Any,
    portable_run: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(stages, list) or len(stages) != 6:
        _fail("invalid_or_unaccepted_reconstruction", "manifest does not bind six stages")
    expected_upstream: list[dict[str, Any]] = []
    values: list[dict[str, Any]] = []
    for index, (row, stage_id, stage_name) in enumerate(
        zip(stages, STAGE_IDS, reconstruction.ALL_STAGES), 1
    ):
        if not isinstance(row, dict):
            _fail("invalid_or_unaccepted_reconstruction", "stage record is invalid")
        _exact(
            row,
            {"stage_id", "stage_name", "manifest", "reproducible_sha256"},
            "stage record",
            "invalid_or_unaccepted_reconstruction",
        )
        if row["stage_id"] != stage_id or row["stage_name"] != stage_name:
            _fail("invalid_or_unaccepted_reconstruction", "stage order or identity mismatch")
        path = _identity_at(
            package, row["manifest"], "stage manifest", "invalid_or_unaccepted_reconstruction"
        )
        stage = _read(path, "invalid_or_unaccepted_reconstruction")
        schema = stage.get("schema")
        if schema in {reconstruction.STAGE_SCHEMA, REPLAY_PREFIX_STAGE_SCHEMA}:
            _exact(stage, {"schema", "reproducible", "execution", "reproducible_sha256"}, "stage manifest", "invalid_or_unaccepted_reconstruction")
            reproducible = stage.get("reproducible")
            if not isinstance(reproducible, dict):
                _fail("invalid_or_unaccepted_reconstruction", "stage reproducible record is invalid")
            execution = stage.get("execution")
            outputs = reproducible.get("outputs")
            if not isinstance(execution, dict) or not isinstance(outputs, dict):
                _fail("invalid_or_unaccepted_reconstruction", "stage execution or output record is invalid")
            output_files = _safe_inventory(outputs.get("files"), code="invalid_or_unaccepted_reconstruction")
            expected_version = 2 if schema == REPLAY_PREFIX_STAGE_SCHEMA else 1
            stage_expected_upstream = expected_upstream
            if schema == REPLAY_PREFIX_STAGE_SCHEMA:
                _validate_seal(stage, "reproducible_sha256", "replay prefix stage", "invalid_or_unaccepted_reconstruction")
                digest_matches = stage.get("reproducible_sha256") == row["reproducible_sha256"]
            else:
                digest_matches = (
                    stage.get("reproducible_sha256") == row["reproducible_sha256"]
                    and sha256_bytes(canonical_bytes(reproducible)) == row["reproducible_sha256"]
                )
            if (
                not digest_matches
                or reproducible.get("stage_id") != stage_id
                or reproducible.get("stage_name") != stage_name
                or reproducible.get("stage_version") != expected_version
                or reproducible.get("state") != "succeeded"
                or reproducible.get("run_identity_sha256") != portable_run.get("portable_identity_sha256")
                or reproducible.get("upstream") != stage_expected_upstream
                or outputs.get("root_hint") != f"outputs/{stage_id}"
                or outputs.get("inventory_sha256") != sha256_bytes(canonical_bytes(output_files))
            ):
                _fail("invalid_or_unaccepted_reconstruction", "stage chain, seal, state, or output inventory mismatch")
            if schema == reconstruction.STAGE_SCHEMA:
                if execution.get("exit_code") != 0 or not isinstance(execution.get("structured_diagnostics"), dict):
                    _fail("invalid_or_unaccepted_reconstruction", "legacy/direct stage execution is not successful")
            elif execution.get("mode") != "replayed" or execution.get("producer_invoked") is not False:
                _fail("invalid_or_unaccepted_reconstruction", "replay prefix stage execution authority mismatch")
            if schema == REPLAY_PREFIX_STAGE_SCHEMA:
                rebase = reproducible.get("rebase")
                if not isinstance(rebase, dict) or rebase.get("rebase_sha256") is None:
                    _fail("invalid_or_unaccepted_reconstruction", "replay prefix rebase authority is absent")
                expected_upstream.append({
                    "stage_id": stage_id,
                    "manifest_sha256": row["reproducible_sha256"],
                    "rebase_sha256": rebase["rebase_sha256"],
                    "output_inventory_sha256": outputs["inventory_sha256"],
                })
            else:
                expected_upstream.append({"stage_id": stage_id, "manifest_sha256": row["reproducible_sha256"]})
        elif schema == REPLAY_DOWNSTREAM_STAGE_SCHEMA:
            _validate_seal(stage, "manifest_sha256", "replay downstream stage", "invalid_or_unaccepted_reconstruction")
            outputs = stage.get("outputs")
            execution = stage.get("execution")
            if not isinstance(outputs, dict) or not isinstance(execution, dict):
                _fail("invalid_or_unaccepted_reconstruction", "replay downstream stage records are malformed")
            output_files = _safe_inventory(outputs.get("files"), code="invalid_or_unaccepted_reconstruction")
            expected_downstream_upstream = [] if index == 5 else [
                {
                    "stage_id": STAGE_IDS[4],
                    "manifest_sha256": stages[4]["reproducible_sha256"],
                    "output_inventory_sha256": values[4]["outputs"]["inventory_sha256"],
                }
            ]
            if (
                index not in {5, 6}
                or stage.get("stage_id") != stage_id
                or stage.get("run_identity_sha256") != portable_run.get("portable_identity_sha256")
                or stage.get("manifest_sha256") != row["reproducible_sha256"]
                or stage.get("upstream") != expected_downstream_upstream
                or stage.get("acceptance_inferred") is not False
                or execution.get("mode") != "executed"
                or execution.get("producer_invoked") is not True
                or execution.get("reusable") is not False
                or execution.get("exit_code") != 0
                or outputs.get("root") != f"outputs/{stage_id}"
                or outputs.get("inventory_sha256") != sha256_bytes(canonical_bytes(output_files))
            ):
                _fail("invalid_or_unaccepted_reconstruction", "replay downstream stage authority mismatch")
        else:
            _fail("invalid_or_unaccepted_reconstruction", "unsupported packaged stage schema")
        values.append(stage)
    schemas = [stage.get("schema") for stage in values]
    legacy_or_direct = all(schema == reconstruction.STAGE_SCHEMA for schema in schemas)
    replay = schemas[:4] == [REPLAY_PREFIX_STAGE_SCHEMA] * 4 and schemas[4:] == [REPLAY_DOWNSTREAM_STAGE_SCHEMA] * 2
    hybrid = schemas[:3] == [REPLAY_PREFIX_STAGE_SCHEMA] * 3 and schemas[3] == reconstruction.STAGE_SCHEMA and schemas[4:] == [REPLAY_DOWNSTREAM_STAGE_SCHEMA] * 2
    if not legacy_or_direct and not replay and not hybrid:
        _fail("invalid_or_unaccepted_reconstruction", "mixed packaged stage chain is invalid")
    return values


def _validate_packaged_replay_evidence(
    package: Path,
    stage_values: Sequence[Mapping[str, Any]],
    portable_run: Mapping[str, Any],
) -> None:
    replay_root = package / "evidence/replay"
    hybrid = stage_values[3].get("schema") == reconstruction.STAGE_SCHEMA
    expected_names = {"intake.json", "bridge.json", *(f"{stage_id}.rebase.json" for stage_id in STAGE_IDS[:3 if hybrid else 4])}
    if hybrid:
        expected_names.add("completion.json")
    if not replay_root.is_dir() or {path.name for path in replay_root.iterdir()} != expected_names:
        _fail("invalid_or_unaccepted_reconstruction", "packaged replay evidence topology mismatch")
    intake = _read(replay_root / "intake.json", "invalid_or_unaccepted_reconstruction")
    bridge = _read(replay_root / "bridge.json", "invalid_or_unaccepted_reconstruction")
    _validate_seal(intake, "intake_sha256", "replay intake", "invalid_or_unaccepted_reconstruction")
    _validate_seal(bridge, "bridge_sha256", "replay bridge", "invalid_or_unaccepted_reconstruction")
    expected_intake_identity = {"path": "replay/intake.json", **file_identity(replay_root / "intake.json"), "intake_sha256": intake.get("intake_sha256")}
    if (
        intake.get("run_identity_sha256") != portable_run.get("portable_identity_sha256")
        or intake.get("acceptance_inferred") is not False
        or intake.get("decisions_replayed") is not False
        or intake.get("stages_05_06_replayed") is not False
        or bridge.get("run_identity_sha256") != portable_run.get("portable_identity_sha256")
        or bridge.get("acceptance_inferred") is not False
        or bridge.get("decisions_replayed") is not False
        or bridge.get("stages_05_06_replayed") is not False
        or bridge.get("operational_stale_authority_count") != 0
        or bridge.get("intake") != expected_intake_identity
    ):
        _fail("invalid_or_unaccepted_reconstruction", "packaged replay evidence infers authority")
    bridge_rows = bridge.get("stages")
    if not isinstance(bridge_rows, list) or len(bridge_rows) != (3 if hybrid else 4):
        _fail("invalid_or_unaccepted_reconstruction", "packaged replay bridge stage domain mismatch")
    for index, stage_id in enumerate(STAGE_IDS[:3 if hybrid else 4]):
        rebase = _read(replay_root / f"{stage_id}.rebase.json", "invalid_or_unaccepted_reconstruction")
        _validate_seal(rebase, "rebase_sha256", "replay rebase", "invalid_or_unaccepted_reconstruction")
        stage = stage_values[index]
        reproducible = stage.get("reproducible", {})
        row = bridge_rows[index]
        if (
            rebase.get("stage_id") != stage_id
            or rebase.get("run_identity_sha256") != portable_run.get("portable_identity_sha256")
            or rebase.get("intake_sha256") != intake.get("intake_sha256")
            or rebase.get("producer_invoked") is not False
            or rebase.get("semantic_content_changed") is not False
            or rebase.get("acceptance_inferred") is not False
            or row != {
                "stage_id": stage_id,
                "manifest_sha256": stage.get("reproducible_sha256"),
                "rebase_sha256": rebase.get("rebase_sha256"),
                "output_inventory_sha256": reproducible.get("outputs", {}).get("inventory_sha256"),
            }
        ):
            _fail("invalid_or_unaccepted_reconstruction", "packaged replay rebase or bridge binding mismatch")
    if hybrid:
        completion = _read(replay_root / "completion.json", "invalid_or_unaccepted_reconstruction")
        stage04 = stage_values[3]
        try:
            reconstruction_replay.validate_hybrid_completion(
                completion, portable_run["portable_identity_sha256"],
                {**file_identity(replay_root / "bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
                bridge_rows,
                file_identity(package / "evidence/stages/04-visual-merge-bundle.stage.json"),
                {"stage_id": STAGE_IDS[3], "manifest_sha256": stage04["reproducible_sha256"]},
            )
        except (OSError, KeyError, reconstruction_replay.ReplayError) as error:
            _fail("invalid_or_unaccepted_reconstruction", f"packaged hybrid completion mismatch: {error}")


def validate_reconstruction_package(package_root: Path, *, require_acceptance: bool, working_root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        package = package_root.resolve(strict=True)
    except OSError as error:
        raise ReconstructionPromotionError(
            "invalid_or_unaccepted_reconstruction", "fixed reconstruction package is absent"
        ) from error
    if package.name != PACKAGE_NAME or package.parent.name != "promotion":
        _fail("unsafe_promotion_path", "package root does not have the fixed bridge topology")
    run_root = package.parent.parent
    inventory = _read(package / INVENTORY_NAME, "invalid_or_unaccepted_reconstruction")
    scenario_id = inventory.get("scenario_id")
    if not isinstance(scenario_id, str):
        _fail("invalid_or_unaccepted_reconstruction", "inventory scenario id is invalid")
    _canonical_run_root(run_root, scenario_id, working_root)
    try:
        _assert_tree_non_reparse(package)
        observed = deterministic_inventory(package)
    except ValueError as error:
        raise ReconstructionPromotionError("unsafe_promotion_path", str(error)) from error
    _safe_inventory(observed, code="unsafe_promotion_path")
    _exact(inventory, {"schema", "scenario_id", "reconstruction_contract_sha256", "artifacts", "inventory_sha256"}, "reconstruction inventory", "invalid_or_unaccepted_reconstruction")
    _validate_seal(inventory, "inventory_sha256", "reconstruction inventory", "invalid_or_unaccepted_reconstruction")
    records = inventory.get("artifacts")
    if inventory.get("schema") != INVENTORY_SCHEMA or not isinstance(records, list) or len(records) != 4:
        _fail("invalid_or_unaccepted_reconstruction", "reconstruction inventory schema or cardinality mismatch")
    role_map: dict[str, dict[str, Any]] = {}
    for row in records:
        if not isinstance(row, dict):
            _fail("invalid_or_unaccepted_reconstruction", "invalid inventory artifact row")
        _exact(row, {"role", "path", "bytes", "sha256"}, "inventory artifact", "invalid_or_unaccepted_reconstruction")
        if row.get("role") in role_map or ROLE_PATHS.get(row.get("role")) != row.get("path"):
            _fail("invalid_or_unaccepted_reconstruction", "inventory roles are duplicate, missing, or mapped incorrectly")
        role_map[row["role"]] = dict(row)
        _identity_at(package, {key: row[key] for key in ("path", "bytes", "sha256")}, "inventory artifact", "invalid_or_unaccepted_reconstruction")
    if set(role_map) != set(ROLE_PATHS):
        _fail("invalid_or_unaccepted_reconstruction", "inventory does not expose the exact four roles")
    manifest = _read(package / MANIFEST_NAME, "invalid_or_unaccepted_reconstruction")
    _exact(manifest, {"schema", "package_state", "scenario", "run", "reconstruction_contract", "source_identity", "review", "stages", "candidate", "content", "fidelity", "qa", "implementation", "package_files", "manifest_sha256"}, "reconstruction manifest", "invalid_or_unaccepted_reconstruction")
    _validate_seal(manifest, "manifest_sha256", "reconstruction manifest", "invalid_or_unaccepted_reconstruction")
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("package_state") != "candidate_awaiting_reconstruction_acceptance" or manifest.get("scenario", {}).get("id") != scenario_id or manifest.get("reconstruction_contract", {}).get("sha256") != inventory["reconstruction_contract_sha256"]:
        _fail("invalid_or_unaccepted_reconstruction", "manifest authority mismatch")
    for label, keys in (
        ("scenario", {"id", "title"}),
        ("run", {"run_id", "portable_identity_sha256"}),
        ("reconstruction_contract", {"basename", "bytes", "sha256", "contract_revision"}),
        ("candidate", {"files", "inventory_sha256"}),
        ("content", {"files", "inventory_sha256"}),
        ("implementation", {"files", "inventory_sha256"}),
    ):
        nested = manifest.get(label)
        if not isinstance(nested, dict):
            _fail("invalid_or_unaccepted_reconstruction", f"manifest {label} is invalid")
        _exact(nested, keys, f"manifest {label}", "invalid_or_unaccepted_reconstruction")
    implementation = manifest.get("implementation", {})
    implementation_files = _safe_inventory(
        implementation.get("files"), code="invalid_or_unaccepted_reconstruction"
    )
    if implementation.get("inventory_sha256") != sha256_bytes(canonical_bytes(implementation_files)):
        _fail("invalid_or_unaccepted_reconstruction", "bridge implementation inventory seal is invalid")
    portable_run = _read(package / "evidence/run/run.portable.json", "invalid_or_unaccepted_reconstruction")
    portable_v2 = portable_run.get("schema") in reconstruction.mineru_cpu_first.RUN_SCHEMAS
    portable_keys = {"schema", "run_id", "target", "profile", "contract", "source", "scope", "options", "execution_boundary", "view_plan", "capability_snapshot", "provider_profiles", "common_tools", "toolchain", "implementation", "portable_identity_sha256"} if portable_v2 else {"schema", "run_id", "target", "profile", "contract", "source", "scope", "options", "capability", "toolchain", "implementation", "portable_identity_sha256"}
    _exact(portable_run, portable_keys, "portable run", "invalid_or_unaccepted_reconstruction")
    valid_run_kind = (portable_v2 and portable_run.get("profile") == reconstruction.mineru_cpu_first.PROFILE) or (portable_run.get("schema") == reconstruction.RUN_SCHEMA and portable_run.get("target") == reconstruction.TARGET and portable_run.get("profile") == reconstruction.PROFILE)
    if not valid_run_kind or portable_run.get("portable_identity_sha256") != manifest.get("run", {}).get("portable_identity_sha256") or sha256_bytes(canonical_bytes({key: value for key, value in portable_run.items() if key != "portable_identity_sha256"})) != portable_run.get("portable_identity_sha256"):
        _fail("invalid_or_unaccepted_reconstruction", "portable run identity mismatch")
    stages = manifest.get("stages")
    stage_values = _validate_packaged_stages(package, stages, portable_run)
    stage_schemas = [stage.get("schema") for stage in stage_values]
    replay_chain = stage_schemas == [REPLAY_PREFIX_STAGE_SCHEMA] * 4 + [REPLAY_DOWNSTREAM_STAGE_SCHEMA] * 2 or stage_schemas == [REPLAY_PREFIX_STAGE_SCHEMA] * 3 + [reconstruction.STAGE_SCHEMA] + [REPLAY_DOWNSTREAM_STAGE_SCHEMA] * 2
    if replay_chain:
        _validate_packaged_replay_evidence(package, stage_values, portable_run)
    assert isinstance(stages, list)
    source_record = manifest.get("source_identity")
    source_path = _identity_at(package, source_record, "source identity", "invalid_or_unaccepted_reconstruction")
    if source_path != package / SOURCE_IDENTITY_NAME:
        _fail("invalid_or_unaccepted_reconstruction", "manifest source identity path is not fixed")
    review = manifest.get("review")
    if not isinstance(review, dict):
        _fail("invalid_or_unaccepted_reconstruction", "manifest review authority is invalid")
    _exact(review, {"queue", "validated_submission", "decision_set", "decisions", "reviewed_allowlist"}, "manifest review authority", "invalid_or_unaccepted_reconstruction")
    for label in ("queue", "validated_submission", "decision_set"):
        _identity_at(package, review[label], f"review {label}", "invalid_or_unaccepted_reconstruction")
    decisions = review.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        _fail("invalid_or_unaccepted_reconstruction", "review decision domain is empty")
    decision_paths = []
    for record in decisions:
        decision_paths.append(_identity_at(package, record, "review decision", "invalid_or_unaccepted_reconstruction"))
    if len({path.name.casefold() for path in decision_paths}) != len(decision_paths):
        _fail("invalid_or_unaccepted_reconstruction", "review decision domain is duplicate")
    if review["reviewed_allowlist"] is not None:
        _identity_at(package, review["reviewed_allowlist"], "review allowlist", "invalid_or_unaccepted_reconstruction")
    portable_provenance = _read(
        package / "evidence/review/MERGE_PROVENANCE.portable.json",
        "invalid_or_unaccepted_reconstruction",
    )
    provenance_v2 = portable_v2
    _exact(
        portable_provenance,
        {"schema", "status", "fidelity_audit", "authorities", "pages"} if provenance_v2 else {"schema", "status", "pages"},
        "portable merge provenance",
        "invalid_or_unaccepted_reconstruction",
    )
    provenance_rows = portable_provenance.get("pages")
    if (
        portable_provenance.get("schema")
        != ("kb_creator.reconstruction_merge_provenance.v2" if provenance_v2 else "kb_creator.reconstruction_merge_provenance.v1")
        or portable_provenance.get("status")
        != "candidate_ready_for_user_reconstruction_review"
        or not isinstance(provenance_rows, list)
        or len(provenance_rows) != len(decision_paths)
    ):
        _fail("invalid_or_unaccepted_reconstruction", "portable merge provenance is incomplete")
    for index, row in enumerate(provenance_rows, 1):
        if not isinstance(row, dict):
            _fail("invalid_or_unaccepted_reconstruction", "portable provenance row is invalid")
        _exact(row, {"source_page", "semantic_role", "merge_packet", "decision", "page", "selected_blocks"}, "portable provenance row", "invalid_or_unaccepted_reconstruction")
        packet = row.get("merge_packet")
        if not isinstance(packet, dict):
            _fail("invalid_or_unaccepted_reconstruction", "portable packet identity is invalid")
        _exact(packet, {"bytes", "sha256"}, "portable packet identity", "invalid_or_unaccepted_reconstruction")
        expected_decision = review["decisions"][index - 1]
        expected_page = {
            "path": f"content/pages/page-{index:03d}.md",
            **file_identity(package / f"content/pages/page-{index:03d}.md"),
        }
        if row["source_page"] != index or row["decision"] != expected_decision or row["page"] != expected_page or not isinstance(row["selected_blocks"], list):
            _fail("invalid_or_unaccepted_reconstruction", "portable provenance page binding mismatch")
    source_identity = _read(package / SOURCE_IDENTITY_NAME, "invalid_or_unaccepted_reconstruction")
    _validate_source_identity(source_identity, scenario_id)
    qa = _read(package / QA_NAME, "invalid_or_unaccepted_reconstruction")
    _validate_qa(qa, code="invalid_or_unaccepted_reconstruction")
    _identity_at(package, qa["candidate"], "QA candidate", "invalid_or_unaccepted_reconstruction")
    submission = _read(_identity_at(package, review["validated_submission"], "validated submission", "invalid_or_unaccepted_reconstruction"), "invalid_or_unaccepted_reconstruction")
    if replay_chain:
        _validate_seal(submission, "submission_sha256", "validated replay submission", "invalid_or_unaccepted_reconstruction")
        if (
            submission.get("schema") != reconstruction_replay_resume.SUBMISSION_SCHEMA
            or submission.get("run_identity_sha256") != manifest["run"]["portable_identity_sha256"]
            or submission.get("bridge_sha256") != stage_values[4].get("bridge_sha256")
            or submission.get("acceptance_inferred") is not False
            or submission.get("page_decisions") != [
                {"source_page": index, "path": f"pages/page-{index:03d}.json", **file_identity(package / f"evidence/review/pages/page-{index:03d}.json")}
                for index in range(1, len(decision_paths) + 1)
            ]
        ):
            _fail("invalid_or_unaccepted_reconstruction", "packaged replay submission authority mismatch")
    if (
        qa["candidate"] != {key: role_map["reconstructed_en"][key] for key in ("path", "bytes", "sha256")}
        or qa["producer_stage"] != stages[5]["manifest"]
        or qa["fidelity"] != manifest["fidelity"]
        or qa["scenario_id"] != scenario_id
        or qa["run_identity_sha256"] != manifest["run"]["portable_identity_sha256"]
        or qa["reconstruction_contract_sha256"] != inventory["reconstruction_contract_sha256"]
        or qa["source_sha256"] != source_identity["source"]["sha256"]
        or qa["decision_authority_sha256"] != submission.get("submission_sha256" if replay_chain else "inventory_sha256")
    ):
        _fail("invalid_or_unaccepted_reconstruction", "QA does not bind candidate, Stage 06, and fidelity exactly")
    fidelity_path = _identity_at(package, manifest["fidelity"], "fidelity", "invalid_or_unaccepted_reconstruction")
    if replay_chain:
        fidelity_value = _read(fidelity_path, "invalid_or_unaccepted_reconstruction")
        if (
            fidelity_value.get("schema") not in {
                reconstruction_replay_resume.AUDIT_SCHEMA,
                reconstruction_replay_resume.AUDIT_V4_SCHEMA,
            }
            or fidelity_value.get("passed") is not True
            or fidelity_value.get("errors") != []
            or fidelity_value.get("authorities", {}).get("run_identity_sha256") != portable_run.get("portable_identity_sha256")
            or portable_provenance.get("fidelity_audit") != manifest["fidelity"]
            or portable_provenance.get("authorities") != fidelity_value.get("authorities")
        ):
            _fail("fidelity_not_closed", "packaged replay fidelity authority is stale or incomplete")
    elif portable_v2:
        fidelity_value = _read(fidelity_path, "invalid_or_unaccepted_reconstruction")
        pages = list(range(1, source_identity["source"]["page_count"] + 1))
        queue_path = package / "evidence/review/review_queue.json"
        decision_set_path = package / "evidence/review/decision_set.json"
        authorities = fidelity_value.get("authorities") if isinstance(fidelity_value, dict) else None
        stage3_files = stage_values[2]["reproducible"]["outputs"]["files"]
        comparison_rows = [row for row in stage3_files if row.get("path") == "comparison.json"]
        queue_value = _read(queue_path, "invalid_or_unaccepted_reconstruction")
        expected_policy = {"source_completeness_threshold": 1.0, "selected_recall_threshold": 0.95, "required_views": list(reconstruction.mineru_cpu_first.REQUIRED_VIEWS), "normalization": "unicode_nfkc_casefold_alphanumeric_stream_v1", "low_text_exemption": False}
        if (
            fidelity_value.get("schema") != "kb_creator.ai-merge-fidelity-audit/v2" or fidelity_value.get("passed") is not True or fidelity_value.get("errors") != []
            or fidelity_value.get("policy") != expected_policy or not isinstance(authorities, dict)
            or authorities.get("review_queue") != {"path_hint": "review/review_queue.json", **file_identity(queue_path), "queue_sha256": queue_value.get("queue_sha256")}
            or authorities.get("decision_set") != {"path_hint": "validated-submission/decision_set.json", **file_identity(decision_set_path)}
            or len(comparison_rows) != 1 or authorities.get("comparison") != {"path_hint": "outputs/03-compare-views/comparison.json", "bytes": comparison_rows[0]["bytes"], "sha256": comparison_rows[0]["sha256"]}
            or [row.get("source_page") for row in fidelity_value.get("pages", [])] != pages
            or any(row.get("passed") is not True or row.get("completeness") != 1.0 or row.get("unaccounted_unit_count") != 0 for row in fidelity_value.get("pages", []))
            or portable_provenance.get("fidelity_audit") != manifest["fidelity"]
            or portable_provenance.get("authorities") != authorities
        ):
            _fail("fidelity_not_closed", "packaged v2 fidelity authority is stale or incomplete")
    else:
        _validate_fidelity(fidelity_path, list(range(1, source_identity["source"]["page_count"] + 1)))
        fidelity_value = _read(fidelity_path, "invalid_or_unaccepted_reconstruction")
    decision_set_value = _read(
        package / "evidence/review/decision_set.json", "invalid_or_unaccepted_reconstruction"
    )
    structural = _structural_mode(
        decision_set_value,
        fidelity_value,
        submission if replay_chain else None,
        code="invalid_or_unaccepted_reconstruction",
    )
    sidecar_path = package / "content" / SEMANTIC_STRUCTURE_NAME
    if sidecar_path.is_file() != structural:
        _fail("invalid_or_unaccepted_reconstruction", "semantic sidecar presence does not match packaged authority")
    if structural:
        _validate_semantic_sidecar(
            sidecar_path,
            pages=list(range(1, len(decision_paths) + 1)),
            fidelity=fidelity_value,
            audit_path=fidelity_path,
            submission=submission,
            decision_paths={index: path for index, path in enumerate(decision_paths, 1)},
            code="invalid_or_unaccepted_reconstruction",
        )
        candidate_sidecar = next(
            (row for row in manifest["candidate"]["files"] if row["path"] == SEMANTIC_STRUCTURE_NAME),
            None,
        )
        if candidate_sidecar is None or file_identity(sidecar_path) != {
            "bytes": candidate_sidecar["bytes"], "sha256": candidate_sidecar["sha256"]
        }:
            _fail("invalid_or_unaccepted_reconstruction", "semantic sidecar candidate/content identity mismatch")
    content_files = _safe_inventory(manifest.get("content", {}).get("files"), code="invalid_or_unaccepted_reconstruction")
    if content_files != deterministic_inventory(package / "content") or manifest["content"].get("inventory_sha256") != sha256_bytes(canonical_bytes(content_files)):
        _fail("invalid_or_unaccepted_reconstruction", "portable content inventory mismatch")
    candidate_files = _safe_inventory(manifest.get("candidate", {}).get("files"), code="invalid_or_unaccepted_reconstruction")
    if manifest["candidate"].get("inventory_sha256") != sha256_bytes(canonical_bytes(candidate_files)):
        _fail("invalid_or_unaccepted_reconstruction", "original candidate inventory digest mismatch")
    stage6_files = stage_values[5]["outputs"]["files"] if replay_chain else stage_values[5]["reproducible"]["outputs"]["files"]
    expected_candidate = list(stage6_files) if replay_chain else [
        {"path": row["path"][len("candidate/"):], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in stage6_files if row["path"].startswith("candidate/")
    ]
    if candidate_files != expected_candidate:
        _fail("invalid_or_unaccepted_reconstruction", "manifest candidate is not the exact Stage 06 product")
    package_files = _safe_inventory(manifest.get("package_files"), code="invalid_or_unaccepted_reconstruction")
    actual_package_files = [row for row in observed if row["path"] not in {MANIFEST_NAME, INVENTORY_NAME, ACCEPTANCE_NAME}]
    if package_files != actual_package_files:
        _fail("invalid_or_unaccepted_reconstruction", "package file closure mismatch")
    allowed = set(row["path"] for row in package_files) | {MANIFEST_NAME, INVENTORY_NAME}
    acceptance_exists = (package / ACCEPTANCE_NAME).exists()
    if acceptance_exists:
        allowed.add(ACCEPTANCE_NAME)
    if {row["path"] for row in observed} != allowed:
        _fail("invalid_or_unaccepted_reconstruction", "package contains a missing or unlisted file")
    expected_dirs = {"content/assets"}
    for relative in allowed:
        parent = PurePosixPath(relative).parent
        while str(parent) != ".":
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    observed_dirs = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_dir()
    }
    if observed_dirs != expected_dirs:
        _fail("invalid_or_unaccepted_reconstruction", "package directory topology is not exact")
    acceptance = _validate_acceptance(package, inventory, manifest, qa) if acceptance_exists else None
    if require_acceptance and acceptance is None:
        _fail("invalid_or_unaccepted_reconstruction", "reconstruction acceptance is absent")
    return inventory, acceptance


def record_reconstruction_acceptance(run_root: Path, user_decision_reference: str, *, working_root: Path | None = None) -> dict[str, Any]:
    if not isinstance(user_decision_reference, str) or not user_decision_reference.strip():
        _fail("invalid_or_unaccepted_reconstruction", "explicit non-blank user decision reference is required")
    context = _promotion_preflight(run_root, working_root)
    run, contract, root = context["run"], context["contract"], context["root"]
    package = root / "promotion" / PACKAGE_NAME
    if (package / ACCEPTANCE_NAME).exists():
        _fail("acceptance_receipt_exists", "reconstruction acceptance receipt already exists")
    inventory, acceptance = validate_reconstruction_package(package, require_acceptance=False, working_root=working_root)
    if acceptance is not None or (package / ACCEPTANCE_NAME).exists():
        _fail("acceptance_receipt_exists", "reconstruction acceptance receipt already exists")
    manifest = _read(package / MANIFEST_NAME)
    role_map = {row["role"]: {key: row[key] for key in ("path", "bytes", "sha256")} for row in inventory["artifacts"]}
    evidence_paths = [INVENTORY_NAME, MANIFEST_NAME, QA_NAME, SOURCE_IDENTITY_NAME, "evidence/fidelity/audit.json"]
    if context["candidate"]["semantic_sidecar"] is not None:
        evidence_paths.append(f"content/{SEMANTIC_STRUCTURE_NAME}")
    receipt = sealed(ACCEPTANCE_SCHEMA, {
        "scenario_id": contract["scenario"]["id"],
        "artifact_kind": "reconstructed_en",
        "candidate": role_map["reconstructed_en"],
        "producer_stage": manifest["stages"][5]["manifest"],
        "evidence": [_record(package / relative, package) for relative in evidence_paths],
        "decision": "accepted",
        "decision_at_utc": _utc_now(),
        "user_decision_reference": user_decision_reference.strip(),
        "recorder_role": "main_orchestrator",
    }, digest_key="receipt_sha256")
    destination = package / ACCEPTANCE_NAME
    try:
        _write_json(destination, receipt, exclusive=True)
    except FileExistsError as error:
        raise ReconstructionPromotionError("acceptance_receipt_exists", "reconstruction acceptance receipt already exists") from error
    written_identity = file_identity(destination)
    try:
        _, accepted = validate_reconstruction_package(package, require_acceptance=True, working_root=working_root)
    except Exception:
        # The receipt did not cross the validated public boundary. Remove only the
        # exact file created by this invocation; never touch a pre-existing path.
        if destination.is_file() and file_identity(destination) == written_identity:
            destination.unlink()
        raise
    assert accepted is not None
    return {"schema": "kb_creator.reconstruction_promotion_result.v1", "state": "accepted_reconstruction_upstream_ready", "exit_code": 0, "run_identity_sha256": run["portable_identity_sha256"], "package_root": str(package), "inventory": str(package / INVENTORY_NAME), "acceptance": str(destination), "acceptance_sha256": accepted["receipt_sha256"]}
