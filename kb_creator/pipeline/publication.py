from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .identity import (
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    deterministic_inventory,
    file_identity,
    implementation_inventory,
    sha256_bytes,
)
from .manifests import sealed, validate_seal
from .reconstruction_promotion import (
    ACCEPTANCE_NAME as RECONSTRUCTION_ACCEPTANCE_NAME,
    INVENTORY_NAME as RECONSTRUCTION_INVENTORY_NAME,
    ROLE_PATHS as RECONSTRUCTION_ROLE_PATHS,
    ReconstructionPromotionError,
    validate_reconstruction_package,
)
from kb_creator.scripts.normalize_publication_access import (
    normalize_publication_access_if_managed,
)


CONTRACT_SCHEMA = "kb_creator.scenario_publication_contract.v1"
HTML_PUBLICATION_POLICY_SCHEMAS = {
    "kb_creator.html_publication_policy.v1",
    "kb_creator.html_publication_policy.v2",
}
RUN_SCHEMA = "kb_creator.publication_run_spec.v1"
STAGE_SCHEMA = "kb_creator.publication_stage_manifest.v1"
ACCEPTANCE_SCHEMA = "kb_creator.artifact_acceptance.v1"
SUBMISSION_SCHEMA = "kb_creator.master_ru_submission.v1"
ARTVIEW_DECISION_AUTHORITIES = {
    ("kb_creator.scenario_artview_decisions.v3", 3),
    ("kb_creator.scenario_artview_decisions.v4", 4),
}
PACKAGE_SCHEMA = "kb_creator.production_package_manifest.v1"
PROFILE = "scenario_publication_v1"
TARGET = "production_candidate"
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

STAGES = (
    "master_en_candidate",
    "master_ru_packets",
    "master_ru_candidate",
    "artview_bundle",
    "artview_apply",
    "html_candidate",
    "docx_candidate",
    "pdf_candidate",
    "production_package",
    "offline_verify",
)
STAGE_ORDINALS = (10, 20, 21, 30, 31, 40, 50, 60, 70, 71)
PACKAGED_STAGE_COUNT = 8
ADAPTER_NAMES = {
    "master_en_candidate": "master_en_projection_v3",
    "master_ru_packets": "master_ru_packets_v1",
    "master_ru_candidate": "master_ru_assembly_v1",
    "artview_bundle": "scenario_artview_v3",
    "artview_apply": "scenario_artview_apply_v1",
    "html_candidate": "translator_build_production_html_v1",
    "docx_candidate": "production_docx_reviewed_authority_v2",
    "pdf_candidate": "docx_pdf_export_v1",
    "production_package": "production_package_v1",
    "offline_verify": "offline_package_verify_v1",
}
WAIT_STATES = {
    "master_en_candidate": "awaiting_master_en_acceptance",
    "master_ru_packets": "awaiting_master_ru_submission",
    "master_ru_candidate": "awaiting_master_ru_acceptance",
    "artview_bundle": "awaiting_artview_decisions",
    "artview_apply": "ready_for_html_candidate",
    "html_candidate": "awaiting_html_acceptance",
    "docx_candidate": "awaiting_docx_acceptance",
    "pdf_candidate": "awaiting_pdf_acceptance",
    "production_package": "ready_for_offline_verify",
    "offline_verify": "candidate_for_release_review",
}
ACCEPTANCE_STAGE = {
    "master_en": "master_en_candidate",
    "master_ru": "master_ru_candidate",
    "artview": "artview_bundle",
    "html": "html_candidate",
    "docx": "docx_candidate",
    "pdf": "pdf_candidate",
}
REQUIRED_AUTHORITIES = {
    "master_en_candidate": (),
    "master_ru_packets": ("master_en_acceptance",),
    "master_ru_candidate": ("master_ru_submission",),
    "artview_bundle": ("master_ru_acceptance",),
    "artview_apply": ("artview_acceptance", "artview_decisions"),
    "html_candidate": (
        "master_ru_acceptance",
        "artview_acceptance",
        "artview_decisions",
    ),
    "docx_candidate": ("html_acceptance",),
    "pdf_candidate": ("docx_acceptance",),
    "production_package": (
        "master_en_acceptance",
        "master_ru_acceptance",
        "artview_acceptance",
        "html_acceptance",
        "docx_acceptance",
        "pdf_acceptance",
    ),
    "offline_verify": (),
}
REVIEWED_DOCX_AUTHORITY = "reviewed_docx"


def _expected_stage_authorities(stage: str, observed: set[str]) -> set[str]:
    required = set(REQUIRED_AUTHORITIES[stage])
    if stage == "docx_candidate" and REVIEWED_DOCX_AUTHORITY in observed:
        required.add(REVIEWED_DOCX_AUTHORITY)
    return required
MANDATORY_PACKAGE_ROLES = frozenset(
    {
        "master_en",
        "master_en_acceptance",
        "master_ru",
        "master_ru_acceptance",
        "artview_bundle",
        "artview_candidate_manifest",
        "artview_decisions",
        "artview_application",
        "artview_effective_config",
        "artview_acceptance",
        "html",
        "html_acceptance",
        "docx",
        "docx_acceptance",
        "pdf",
        "pdf_acceptance",
        "source_configs",
        "effective_config",
        "stage_evidence",
        "pipeline_snapshot",
        "schema_snapshot",
        "offline_verifier",
    }
)


class PublicationControlError(ValueError):
    pass


DOCX_ONLY_ROUTE = (
    "The legacy HTML/DOCX/PDF publication writer is retired. "
    "Use `python -m kb_creator translate run` for a new DOCX-only five-step run, "
    "or `python -m kb_creator.scripts.revise_reviewed_docx` for a reviewed DOCX-only revision. "
    "Historical package verification remains read-only."
)


def reject_legacy_publication_writer() -> None:
    """Stop obsolete output routes before any stage or acceptance is written."""
    raise PublicationControlError(DOCX_ONLY_ROUTE)


@dataclass(frozen=True)
class PublicationStageAdapter:
    name: str
    invoke: Callable[..., Mapping[str, object]]
    context_aware: bool = False
    tool_records: Sequence[Mapping[str, str]] | None = None


@dataclass(frozen=True)
class PublicationStageInvocation:
    run_root: Path
    contract: Mapping[str, Any]
    effective_config: Mapping[str, Any]
    stage: str
    stage_index: int
    authorities: Mapping[str, Path]
    authority_inputs: Sequence[Mapping[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise PublicationControlError(f"cannot read JSON: {path}: {error}") from error
    if not isinstance(value, dict):
        raise PublicationControlError(f"JSON document must be an object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def _exact(value: Mapping[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise PublicationControlError(f"{label} has unknown or missing fields")


def _safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise PublicationControlError(f"invalid {label} path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.drive:
        raise PublicationControlError(f"unsafe {label} path")
    return path


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def _check_identity(root: Path, record: Mapping[str, Any], label: str) -> Path:
    _exact(record, {"path", "bytes", "sha256"}, label)
    relative = _safe_relative(record["path"], label)
    path = root / relative
    try:
        assert_existing_path_components_are_not_reparse(path)
    except ValueError as error:
        raise PublicationControlError(str(error)) from error
    if not path.is_file() or file_identity(path) != {
        "bytes": record["bytes"],
        "sha256": record["sha256"],
    }:
        raise PublicationControlError(f"{label} identity mismatch")
    return path


def _validate_sealed(value: dict[str, Any], key: str, label: str) -> None:
    try:
        validate_seal(value, key)
    except ValueError as error:
        raise PublicationControlError(f"{label}: {error}") from error


def _validate_contract(path: Path, config_root: Path) -> tuple[dict[str, Any], str]:
    try:
        assert_existing_path_components_are_not_reparse(path)
        assert_existing_path_components_are_not_reparse(config_root)
    except ValueError as error:
        raise PublicationControlError(str(error)) from error
    contract = _read(path)
    top = {
        "schema", "contract_revision", "scenario", "upstream",
        "artifact_names", "configs", "master_en", "master_ru", "artview",
        "html", "docx", "pdf", "package", "tool_policy",
    }
    _exact(contract, top, "publication contract")
    if contract["schema"] != CONTRACT_SCHEMA or contract["contract_revision"] != 1:
        raise PublicationControlError("invalid publication contract version")
    scenario = contract["scenario"]
    _exact(scenario, {"id", "title_en", "title_ru", "language_source", "language_target"}, "scenario")
    if scenario["language_source"] != "en" or scenario["language_target"] != "ru":
        raise PublicationControlError("unsupported publication language pair")
    upstream = contract["upstream"]
    _exact(upstream, {"reconstruction_contract_sha256", "required_artifact_roles"}, "publication upstream")
    if (
        not re.fullmatch(
            r"[0-9A-F]{64}", str(upstream["reconstruction_contract_sha256"])
        )
        or upstream["required_artifact_roles"] != list(RECONSTRUCTION_ROLE_PATHS)
    ):
        raise PublicationControlError("invalid publication upstream authority")
    names = contract["artifact_names"]
    _exact(names, {"master_en", "master_ru", "html", "docx", "pdf"}, "artifact names")
    expected_suffixes = {"master_en": ".md", "master_ru": ".md", "html": ".html", "docx": ".docx", "pdf": ".pdf"}
    if any(Path(names[k]).name != names[k] or not names[k].lower().endswith(s) for k, s in expected_suffixes.items()):
        raise PublicationControlError("artifact names must be stable basenames with expected suffixes")
    pdf = contract["pdf"]
    _exact(pdf, {"adapter", "export_policy", "required_qa"}, "PDF policy")
    _exact(pdf["export_policy"], {"document_input_role", "format", "all_pages", "fresh_export"}, "PDF export policy")
    if pdf["adapter"] != "docx_pdf_export_v1" or pdf["export_policy"] != {
        "document_input_role": "accepted_docx", "format": "pdf", "all_pages": True, "fresh_export": True,
    }:
        raise PublicationControlError("PDF authority must be exact accepted DOCX through the bound local export engine")
    serialized_pdf = json.dumps(pdf, ensure_ascii=False).lower()
    if any(term in serialized_pdf for term in ("source_html", "engine_command", "print-to-pdf", "chromium", "browser", "edge")):
        raise PublicationControlError("direct HTML/browser PDF configuration is forbidden")
    tool_policy = contract["tool_policy"]
    if tool_policy != {"repository_tool_root": ".tools", "allowed_system_tools": ["powershell", "microsoft_word_com"]}:
        raise PublicationControlError("invalid publication tool policy")
    required_roles = contract["package"].get("required_roles")
    if (
        not isinstance(required_roles, list)
        or len(required_roles) != len(MANDATORY_PACKAGE_ROLES)
        or any(not isinstance(role, str) for role in required_roles)
        or len(set(required_roles)) != len(required_roles)
        or set(required_roles) != MANDATORY_PACKAGE_ROLES
    ):
        raise PublicationControlError("publication package roles must be the exact mandatory role set")
    artview_roles = set(contract["artview"].get("required_bundle_roles", []))
    if not {"candidate_manifest", "accepted_decisions", "application_receipt", "effective_visual_config"}.issubset(artview_roles):
        raise PublicationControlError("ArtView bundle roles are incomplete")
    master_en = contract["master_en"]
    _exact(master_en, {"profile", "config", "required_qa"}, "MASTER_EN policy")
    master_ru = contract["master_ru"]
    _exact(master_ru, {"profile", "config", "terminology", "packet_policy", "required_qa"}, "MASTER_RU policy")
    if master_ru["packet_policy"] != "ordered_hash_bound_units_v1" or not isinstance(master_ru["terminology"], list) or not master_ru["terminology"]:
        raise PublicationControlError("invalid MASTER_RU policy")
    artview = contract["artview"]
    _exact(artview, {"profile", "required_bundle_roles", "decision_schema", "decision_version"}, "ArtView policy")
    if (artview["decision_schema"], artview["decision_version"]) not in ARTVIEW_DECISION_AUTHORITIES:
        raise PublicationControlError("invalid ArtView decision authority")
    for label in ("html", "docx"):
        policy = contract[label]
        _exact(policy, {"adapter", "config", "required_qa"}, f"{label} policy")
        expected_adapter = "translator_build_production_html_v1" if label == "html" else "production_docx_explicit_config_v1"
        if policy["adapter"] != expected_adapter:
            raise PublicationControlError(f"invalid {label} adapter")
    package_policy = contract["package"]
    _exact(package_policy, {"required_roles", "stable_names", "verifier_version"}, "package policy")
    if package_policy["stable_names"] is not True or package_policy["verifier_version"] != 1:
        raise PublicationControlError("invalid package policy")
    for label, record in (
        ("MASTER_EN config", master_en["config"]), ("MASTER_RU config", master_ru["config"]),
        ("ArtView profile", artview["profile"]), ("HTML config", contract["html"]["config"]),
        ("DOCX config", contract["docx"]["config"]),
    ):
        _check_identity(config_root, record, label)
    html_config_path = _check_identity(config_root, contract["html"]["config"], "HTML config")
    html_config = _read(html_config_path)
    html_policy = html_config.get("html_publication_policy")
    # Existing identity-bound contracts may be authored from a complete legacy
    # renderer config.  Stage 40 performs its explicit compatibility
    # normalization; a new lifecycle declaration, when present, is closed here.
    if html_policy is not None and (
        not isinstance(html_policy, dict)
        or html_policy.get("schema") not in HTML_PUBLICATION_POLICY_SCHEMAS
        or html_policy.get("state") not in {"deferred", "stage40_ready"}
    ):
        raise PublicationControlError("HTML publication-policy lifecycle is invalid")
    if isinstance(html_policy, dict) and html_policy["state"] == "deferred" and set(html_policy) != {"schema", "state"}:
        raise PublicationControlError("deferred HTML publication policy must be closed")
    for index, record in enumerate(master_ru["terminology"]):
        _check_identity(config_root, record, f"terminology config {index}")
    for label, policy in (("MASTER_EN", master_en), ("MASTER_RU", master_ru), ("HTML", contract["html"]), ("DOCX", contract["docx"]), ("PDF", pdf)):
        qa = policy["required_qa"]
        if not isinstance(qa, list) or not qa or any(not isinstance(item, str) or not item for item in qa) or len(qa) != len(set(qa)):
            raise PublicationControlError(f"invalid {label} QA policy")
    configs = contract["configs"]
    if not isinstance(configs, list) or len(configs) < 5:
        raise PublicationControlError("publication config inventory is incomplete")
    roles: set[str] = set()
    for row in configs:
        _exact(row, {"role", "file"}, "config record")
        if row["role"] in roles:
            raise PublicationControlError("duplicate publication config role")
        roles.add(row["role"])
        _check_identity(config_root, row["file"], f"config {row['role']}")
    if not {"master_en", "master_ru", "artview", "html", "docx", "pdf", "package"}.issubset(roles):
        raise PublicationControlError("required config role is missing")
    return contract, file_identity(path)["sha256"]


def _validate_acceptance(path: Path, root: Path, *, scenario_id: str, kind: str, candidate: Mapping[str, Any] | None = None, producer: Mapping[str, Any] | None = None) -> dict[str, Any]:
    value = _read(path)
    _exact(value, {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"}, "acceptance receipt")
    _validate_sealed(value, "receipt_sha256", "acceptance receipt")
    if value["schema"] != ACCEPTANCE_SCHEMA or value["scenario_id"] != scenario_id or value["artifact_kind"] != kind or value["decision"] != "accepted" or value["recorder_role"] != "main_orchestrator" or not value["user_decision_reference"]:
        raise PublicationControlError(f"invalid or unaccepted {kind} receipt")
    _check_identity(root, value["candidate"], f"{kind} candidate")
    _check_identity(root, value["producer_stage"], f"{kind} producer stage")
    if not isinstance(value["evidence"], list) or not value["evidence"]:
        raise PublicationControlError(f"{kind} acceptance lacks evidence")
    if len({canonical_bytes(row) for row in value["evidence"]}) != len(value["evidence"]):
        raise PublicationControlError(f"{kind} acceptance has duplicate evidence")
    for row in value["evidence"]:
        _check_identity(root, row, f"{kind} acceptance evidence")
    if candidate is not None and value["candidate"] != candidate:
        raise PublicationControlError(f"stale {kind} candidate acceptance")
    if producer is not None and value["producer_stage"] != producer:
        raise PublicationControlError(f"stale {kind} producer acceptance")
    return value


def _validate_reconstruction(inventory_path: Path, acceptance_path: Path, contract: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if (
        inventory_path.name != RECONSTRUCTION_INVENTORY_NAME
        or acceptance_path.name != RECONSTRUCTION_ACCEPTANCE_NAME
        or inventory_path.parent != acceptance_path.parent
        or contract["upstream"]["required_artifact_roles"]
        != list(RECONSTRUCTION_ROLE_PATHS)
    ):
        raise PublicationControlError(
            "invalid_or_unaccepted_reconstruction: fixed bridge authority is required"
        )
    try:
        inventory, acceptance = validate_reconstruction_package(
            inventory_path.parent, require_acceptance=True
        )
    except (ReconstructionPromotionError, OSError, ValueError) as error:
        raise PublicationControlError(
            f"invalid_or_unaccepted_reconstruction: {error}"
        ) from error
    assert acceptance is not None
    if (
        inventory["scenario_id"] != contract["scenario"]["id"]
        or inventory["reconstruction_contract_sha256"]
        != contract["upstream"]["reconstruction_contract_sha256"]
    ):
        raise PublicationControlError(
            "reconstruction authority does not match publication contract"
        )
    return inventory, acceptance


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _implementation() -> dict[str, Any]:
    repo = _repo_root()
    paths = [
        repo / "kb_creator" / "__main__.py",
        repo / "kb_creator" / "pipeline" / "publication.py",
        repo / "kb_creator" / "pipeline" / "publication_adapters.py",
        repo / "kb_creator" / "pipeline" / "reconstruction_promotion.py",
        # Stage 40 invokes this renderer directly; its bytes are part of every
        # publication run identity, not an ambient implementation detail.
        repo / "translator" / "translator.py",
    ]
    paths.extend(repo / "kb_creator" / "contracts" / name for name in (
        "scenario_publication_contract.v1.schema.json", "publication_run_spec.v1.schema.json",
        "publication_stage_manifest.v1.schema.json", "artifact_acceptance.v1.schema.json",
        "master_ru_submission.v1.schema.json", "production_package_manifest.v1.schema.json",
        "scenario_artview_profile.v3.schema.json", "scenario_artview_decisions.v3.schema.json",
        "scenario_artview_profile.v4.schema.json", "scenario_artview_decisions.v4.schema.json",
        "reconstruction_upstream_inventory.v1.schema.json",
        "reconstruction_upstream_manifest.v1.schema.json",
        "reconstruction_source_identity.v1.schema.json",
    ))
    paths.extend(repo / "kb_creator" / "scripts" / name for name in (
        "build_scenario_master_en.py", "verify_scenario_master_en.py",
        "scenario_master_ru.py", "verify_scenario_master_ru.py",
        "scenario_artview.py", "scenario_artview_apply.py",
        "production_docx.py", "publication_render_qa.py", "verify_production_package.py",
    ))
    paths.append(repo / "kb_creator" / "scripts" / "export_docx_to_pdf.ps1")
    paths.append(repo / "kb_creator" / "scripts" / "export_docx_to_pdf_local.py")
    return implementation_inventory(repo, paths)


def publication_preflight(contract_path: Path, upstream_inventory_path: Path, reconstruction_acceptance_path: Path, config_root: Path, run_root: Path, tools_root: Path | None = None) -> dict[str, Any]:
    reject_legacy_publication_writer()
    if run_root.exists() or not run_root.parent.is_dir():
        raise PublicationControlError("publication run root must be absent and its parent must exist")
    try:
        assert_existing_path_components_are_not_reparse(run_root.parent)
    except ValueError as error:
        raise PublicationControlError(str(error)) from error
    repo = _repo_root().resolve()
    expected_tools = (repo / ".tools").resolve()
    actual_tools = (tools_root or expected_tools).resolve()
    if actual_tools != expected_tools or not actual_tools.is_dir():
        raise PublicationControlError("publication tools root must be repository .tools")
    contract, contract_sha = _validate_contract(contract_path, config_root)
    inventory, acceptance = _validate_reconstruction(upstream_inventory_path, reconstruction_acceptance_path, contract)
    return {"schema": "kb_creator.publication_preflight.v1", "state": "ready", "target": TARGET, "contract_sha256": contract_sha, "reconstruction_inventory_sha256": inventory["inventory_sha256"], "reconstruction_acceptance_sha256": acceptance["receipt_sha256"]}


def _effective_config(contract: Mapping[str, Any]) -> dict[str, Any]:
    return sealed("kb_creator.effective_publication_config.v1", {"scenario_id": contract["scenario"]["id"], "source_configs": contract["configs"], "artview": contract["artview"], "html": contract["html"], "docx": contract["docx"], "pdf": contract["pdf"], "package": contract["package"]}, digest_key="config_inventory_sha256")


def _portable_fields(run: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in run.items() if k not in {"local", "portable_identity_sha256"}}


def _registry_tools(adapters: Mapping[str, PublicationStageAdapter]) -> list[dict[str, str]]:
    injected = [{"name": "injected_publication_adapters", "version": "test", "scope": "injected_test"}]
    word_scopes = {
        "publication_python": "repository_tools",
        "pdftoppm": "repository_tools",
        "powershell": "allowed_system",
        "microsoft_word_com": "allowed_system",
    }
    libreoffice_scopes = {
        "publication_python": "repository_tools",
        "pdftoppm": "repository_tools",
        "libreoffice": "repository_tools",
    }
    declarations = [adapters[stage].tool_records for stage in STAGES]
    if all(records is None for records in declarations):
        return injected
    if any(records is None for records in declarations):
        raise PublicationControlError("publication registry mixes production and injected tool identities")
    normalized: list[list[dict[str, str]]] = []
    modes: list[str] = []
    for records in declarations:
        assert records is not None
        if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
            raise PublicationControlError("publication tool declaration must be an array")
        current: list[dict[str, str]] = []
        for record in records:
            if not isinstance(record, Mapping) or set(record) != {"name", "version", "scope"}:
                raise PublicationControlError("publication tool identity is not closed")
            if any(not isinstance(record[key], str) for key in ("name", "version", "scope")):
                raise PublicationControlError("publication tool identity fields must be strings")
            item = {key: record[key] for key in ("name", "version", "scope")}
            current.append(item)
        if current == injected:
            modes.append("injected")
            normalized.append(injected)
            continue
        if len({item["name"] for item in current}) != len(current):
            raise PublicationControlError("production publication tools must contain unique identities")
        by_name = {item["name"]: item for item in current}
        scopes = word_scopes if set(by_name) == set(word_scopes) else libreoffice_scopes if set(by_name) == set(libreoffice_scopes) else None
        if scopes is None:
            raise PublicationControlError("production publication tool names are not exact")
        for name, scope in scopes.items():
            item = by_name[name]
            if item["scope"] != scope or re.fullmatch(r"sha256:[0-9A-F]{64}", item["version"]) is None:
                raise PublicationControlError("production publication tool scope or SHA-256 identity is invalid")
        modes.append("production")
        normalized.append([by_name[name] for name in scopes])
    if len(set(modes)) != 1:
        raise PublicationControlError("publication registry mixes production and injected tool identities")
    if any(canonical_bytes(records) != canonical_bytes(normalized[0]) for records in normalized[1:]):
        raise PublicationControlError("publication registry tool identities are inconsistent")
    return normalized[0]


def _build_run(contract_path: Path, upstream_inventory_path: Path, reconstruction_acceptance_path: Path, config_root: Path, run_root: Path, run_id: str, tools: Sequence[Mapping[str, str]], tools_root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if not SAFE_RUN_ID.fullmatch(run_id):
        raise PublicationControlError("invalid publication run id")
    publication_preflight(contract_path, upstream_inventory_path, reconstruction_acceptance_path, config_root, run_root, tools_root)
    contract, contract_sha = _validate_contract(contract_path, config_root)
    adapters = [{"stage": stage, "logical_name": ADAPTER_NAMES[stage], "version": 1} for stage in STAGES]
    configs = [{"role": row["role"], "file": row["file"]} for row in contract["configs"]]
    portable: dict[str, Any] = {
        "schema": RUN_SCHEMA, "run_id": run_id, "target": TARGET, "profile": PROFILE,
        "scenario_id": contract["scenario"]["id"],
        "contract": {"path": contract_path.name, **file_identity(contract_path)},
        "accepted_reconstruction": {"inventory": {"path": upstream_inventory_path.name, **file_identity(upstream_inventory_path)}, "acceptance": {"path": reconstruction_acceptance_path.name, **file_identity(reconstruction_acceptance_path)}},
        "stage_graph": list(STAGES), "configs": configs, "adapters": adapters,
        "tools": [dict(record) for record in tools],
        "implementation": _implementation(),
    }
    portable["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
    run = {**portable, "local": {"repo_root": str(_repo_root().resolve()), "run_root": str(run_root.resolve()), "contract_path": str(contract_path.resolve()), "upstream_inventory_path": str(upstream_inventory_path.resolve()), "reconstruction_acceptance_path": str(reconstruction_acceptance_path.resolve()), "config_root": str(config_root.resolve()), "tools_root": str((tools_root or (_repo_root() / ".tools")).resolve())}}
    return run, _effective_config(contract)


def _load_run(run_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    run = _read(run_root / "run.json")
    _exact(run, {"schema", "run_id", "target", "profile", "scenario_id", "contract", "accepted_reconstruction", "stage_graph", "configs", "adapters", "tools", "implementation", "portable_identity_sha256", "local"}, "publication run")
    if run["schema"] != RUN_SCHEMA or run["target"] != TARGET or run["profile"] != PROFILE or run["stage_graph"] != list(STAGES):
        raise PublicationControlError("invalid publication run")
    if sha256_bytes(canonical_bytes(_portable_fields(run))) != run["portable_identity_sha256"]:
        raise PublicationControlError("publication run identity mismatch")
    local = run["local"]
    _exact(local, {"repo_root", "run_root", "contract_path", "upstream_inventory_path", "reconstruction_acceptance_path", "config_root", "tools_root"}, "publication local bindings")
    if Path(local["run_root"]).resolve() != run_root.resolve() or Path(local["repo_root"]).resolve() != _repo_root().resolve() or Path(local["tools_root"]).resolve() != (_repo_root() / ".tools").resolve():
        raise PublicationControlError("stale publication local binding")
    contract, contract_sha = _validate_contract(Path(local["contract_path"]), Path(local["config_root"]))
    if contract_sha != run["contract"]["sha256"] or file_identity(Path(local["contract_path"])) != {"bytes": run["contract"]["bytes"], "sha256": run["contract"]["sha256"]}:
        raise PublicationControlError("stale publication contract")
    _validate_reconstruction(Path(local["upstream_inventory_path"]), Path(local["reconstruction_acceptance_path"]), contract)
    if _implementation() != run["implementation"]:
        raise PublicationControlError("stale publication implementation")
    effective = _read(run_root / "effective_publication_config.json")
    _validate_sealed(effective, "config_inventory_sha256", "effective publication config")
    if effective != _effective_config(contract):
        raise PublicationControlError("stale effective publication config")
    return run, contract, effective


def _stage_id(index: int) -> str:
    return f"{STAGE_ORDINALS[index]:02d}-{STAGES[index].replace('_', '-')}"


def _stage_manifest_path(run_root: Path, index: int) -> Path:
    return run_root / "evidence" / "stages" / f"{_stage_id(index)}.manifest.json"


def _inventory(root: Path, run_root: Path) -> dict[str, Any]:
    files = deterministic_inventory(root)
    return {"root": root.relative_to(run_root).as_posix(), "files": files, "inventory_sha256": sha256_bytes(canonical_bytes(files))}


def _validate_stage(run_root: Path, run: Mapping[str, Any], index: int, upstream: Sequence[dict[str, str]]) -> dict[str, Any]:
    path = _stage_manifest_path(run_root, index)
    value = _read(path)
    _exact(value, {"schema", "reproducible", "execution", "reproducible_sha256"}, "publication stage manifest")
    reproducible = value["reproducible"]
    _exact(reproducible, {"stage_id", "stage_name", "stage_version", "state", "run_identity_sha256", "upstream", "inputs", "adapter", "effective_config", "tools", "implementation_inventory_sha256", "outputs", "evidence", "cache_key"}, "publication reproducible stage")
    expected_seal = sha256_bytes(canonical_bytes({"schema": STAGE_SCHEMA, "reproducible": reproducible}))
    if value.get("reproducible_sha256") != expected_seal:
        raise PublicationControlError("publication stage reproducible seal mismatch")
    effective_path = run_root / "effective_publication_config.json"
    adapter_script = reproducible.get("adapter", {}).get("script", {})
    script_name = adapter_script.get("path") if isinstance(adapter_script, Mapping) else None
    expected_script_path = (
        _repo_root() / "kb_creator" / "pipeline" / "publication_adapters.py"
        if script_name == "publication_adapters.py"
        else Path(__file__).resolve()
    )
    expected_adapter = {"logical_name": ADAPTER_NAMES[STAGES[index]], "version": 1, "script": {"path": expected_script_path.name, **file_identity(expected_script_path)}}
    observed_kinds = {row.get("kind") for row in reproducible.get("inputs", []) if isinstance(row, dict)}
    expected_inputs = {"publication_contract", "accepted_reconstruction", *_expected_stage_authorities(STAGES[index], observed_kinds)}
    observed_inputs = reproducible.get("inputs")
    if not isinstance(observed_inputs, list) or {row.get("kind") for row in observed_inputs if isinstance(row, dict)} != expected_inputs or len(observed_inputs) != len(expected_inputs):
        raise PublicationControlError("publication stage authority inputs mismatch")
    for row in observed_inputs:
        _exact(row, {"kind", "file"}, "publication stage input")
        if row["kind"] == "publication_contract":
            if row["file"] != run["contract"]:
                raise PublicationControlError("publication stage contract input mismatch")
        elif row["kind"] == "accepted_reconstruction":
            if row["file"] != run["accepted_reconstruction"]["acceptance"]:
                raise PublicationControlError("publication stage reconstruction input mismatch")
        else:
            _check_identity(run_root, row["file"], f"publication stage input {row['kind']}")
    without_cache = {key: item for key, item in reproducible.items() if key != "cache_key"}
    if value["schema"] != STAGE_SCHEMA or reproducible.get("stage_id") != _stage_id(index) or reproducible.get("stage_name") != STAGES[index] or reproducible.get("stage_version") != 1 or reproducible.get("state") != "succeeded" or reproducible.get("run_identity_sha256") != run["portable_identity_sha256"] or reproducible.get("upstream") != list(upstream) or reproducible.get("adapter") != expected_adapter or reproducible.get("effective_config") != {"path": effective_path.name, **file_identity(effective_path)} or reproducible.get("tools") != run["tools"] or reproducible.get("implementation_inventory_sha256") != run["implementation"]["inventory_sha256"] or reproducible.get("cache_key") != sha256_bytes(canonical_bytes(without_cache)):
        raise PublicationControlError("publication stage identity mismatch")
    for key in ("outputs", "evidence"):
        inv = reproducible[key]
        root = run_root / _safe_relative(inv["root"], f"stage {key}")
        if _inventory(root, run_root) != inv:
            raise PublicationControlError(f"publication stage {key} inventory mismatch")
    stage_root = run_root / "outputs" / _stage_id(index)
    if STAGES[index] == "docx_candidate":
        _assert_no_stage50_pdf(stage_root, *_stage50_residue_roots(run_root, index))
    _assert_closed_stage_root(stage_root)
    return value


def _completed_prefix(run_root: Path, run: Mapping[str, Any]) -> tuple[int, list[dict[str, str]]]:
    manifests_root = run_root / "evidence" / "stages"
    observed = {path.name for path in manifests_root.glob("*.manifest.json")} if manifests_root.is_dir() else set()
    upstream: list[dict[str, str]] = []
    count = 0
    for index in range(len(STAGES)):
        expected = _stage_manifest_path(run_root, index).name
        if expected not in observed:
            break
        manifest = _validate_stage(run_root, run, index, upstream)
        upstream.append({"stage_id": _stage_id(index), "manifest_sha256": manifest["reproducible_sha256"]})
        count += 1
    if observed != {_stage_manifest_path(run_root, i).name for i in range(count)}:
        raise PublicationControlError("publication stage manifests are not an exact prefix")
    return count, upstream


def _primary_candidate(run_root: Path, contract: Mapping[str, Any], stage: str) -> Path:
    index = STAGES.index(stage)
    artifacts = run_root / "outputs" / _stage_id(index) / "artifacts"
    names = contract["artifact_names"]
    relative = {
        "master_en_candidate": names["master_en"], "master_ru_packets": "packet_manifest.json",
        "master_ru_candidate": names["master_ru"], "artview_bundle": "candidate_manifest.json",
        "artview_apply": "ARTVIEW_APPLIED.json", "html_candidate": names["html"],
        "docx_candidate": names["docx"], "pdf_candidate": names["pdf"],
        "production_package": "package/PRODUCTION_MANIFEST.json", "offline_verify": "offline_verify.json",
    }[stage]
    return artifacts / relative


def _acceptance_authority(run_root: Path, contract: Mapping[str, Any], kind: str, path: Path) -> dict[str, Any]:
    stage = ACCEPTANCE_STAGE[kind]
    index = STAGES.index(stage)
    candidate = _primary_candidate(run_root, contract, stage)
    manifest_path = _stage_manifest_path(run_root, index)
    if not candidate.is_file() or not manifest_path.is_file():
        raise PublicationControlError(f"{kind} candidate is not complete")
    try:
        path.resolve().relative_to(run_root.resolve())
    except ValueError as error:
        raise PublicationControlError("publication acceptance must be run-local") from error
    return _validate_acceptance(path, run_root, scenario_id=contract["scenario"]["id"], kind=kind, candidate={"path": candidate.relative_to(run_root).as_posix(), **file_identity(candidate)}, producer={"path": manifest_path.relative_to(run_root).as_posix(), **file_identity(manifest_path)})


def _validate_submission(path: Path, run_root: Path, contract: Mapping[str, Any], master_en_acceptance: Path) -> dict[str, Any]:
    value = _read(path)
    _exact(value, {"schema", "scenario_id", "accepted_master_en", "packet_manifest", "units", "batches", "review", "submission_sha256"}, "MASTER_RU submission")
    _validate_sealed(value, "submission_sha256", "MASTER_RU submission")
    if value["schema"] != SUBMISSION_SCHEMA or value["scenario_id"] != contract["scenario"]["id"] or value["review"] != {"state": "closed", "unresolved": []}:
        raise PublicationControlError("MASTER_RU submission is not closed")
    if value["accepted_master_en"] != {"path": master_en_acceptance.relative_to(run_root).as_posix(), **file_identity(master_en_acceptance)}:
        raise PublicationControlError("MASTER_RU submission has stale MASTER_EN authority")
    packet = _primary_candidate(run_root, contract, "master_ru_packets")
    if value["packet_manifest"] != {"path": packet.relative_to(run_root).as_posix(), **file_identity(packet)}:
        raise PublicationControlError("MASTER_RU submission has stale packet authority")
    units = value["units"]
    if not isinstance(units, list) or not units:
        raise PublicationControlError("MASTER_RU submission has no units")
    unit_ids: set[str] = set()
    for unit in units:
        _exact(unit, {"unit_id", "source_sha256", "russian_payload_sha256"}, "MASTER_RU unit")
        if not unit["unit_id"] or unit["unit_id"] in unit_ids:
            raise PublicationControlError("MASTER_RU submission has duplicate units")
        unit_ids.add(unit["unit_id"])
        if not re.fullmatch(r"[0-9A-F]{64}", str(unit["source_sha256"])) or not re.fullmatch(r"[0-9A-F]{64}", str(unit["russian_payload_sha256"])):
            raise PublicationControlError("MASTER_RU unit identity is invalid")
    if not isinstance(value["batches"], list) or not value["batches"]:
        raise PublicationControlError("MASTER_RU submission has no batch identity")
    for batch in value["batches"]:
        _check_identity(run_root, batch, "MASTER_RU batch")
    return value


def _validate_artview_decisions(path: Path, scenario_id: str) -> dict[str, Any]:
    value = _read(path)
    _exact(value, {"schema", "scenario_id", "state", "bindings", "decisions", "review", "decisions_sha256"}, "ArtView decisions")
    _validate_sealed(value, "decisions_sha256", "ArtView decisions")
    if value["schema"] not in {schema for schema, _version in ARTVIEW_DECISION_AUTHORITIES} or value["scenario_id"] != scenario_id or value["state"] != "accepted":
        raise PublicationControlError("ArtView decisions are not accepted and closed")
    bindings = value["bindings"]
    binding_keys = {"candidate_manifest_sha256", "candidate_files_inventory_sha256", "profile_sha256", "master_ru_sha256", "master_ru_acceptance_sha256", "master_ru_asset_manifest_sha256", "reconstruction_inventory_sha256"}
    if value["schema"] == "kb_creator.scenario_artview_decisions.v4":
        binding_keys |= {"source_pdf_sha256", "source_identity_sha256"}
    _exact(bindings, binding_keys, "ArtView decision bindings")
    if any(not re.fullmatch(r"[0-9A-F]{64}", str(bindings[name])) for name in binding_keys):
        raise PublicationControlError("ArtView decision binding identity is invalid")
    decisions = value["decisions"]
    if not isinstance(decisions, list) or not decisions:
        raise PublicationControlError("ArtView decisions have no review rows")
    asset_ids: list[str] = []
    reviewed_count = 0
    unresolved: list[str] = []
    for row in decisions:
        _exact(row, {"asset_id", "binary", "presentation", "reviewed", "notes"}, "ArtView decision row")
        _exact(row["binary"], {"choice", "candidate_id"}, "ArtView binary decision")
        _exact(row["presentation"], {"width_percent", "alignment", "wrap_text", "wrap_tables"}, "ArtView presentation")
        asset_id = row["asset_id"]
        if not isinstance(asset_id, str) or not asset_id or asset_id in asset_ids:
            raise PublicationControlError("ArtView decision rows are duplicate or invalid")
        asset_ids.append(asset_id)
        reviewed = row["reviewed"] is True
        if reviewed:
            reviewed_count += 1
        if not reviewed or row["binary"]["choice"] not in {"keep_current", "use_candidate", "exclude"}:
            unresolved.append(asset_id)
        choice = row["binary"]["choice"]
        candidate_id = row["binary"]["candidate_id"]
        if (choice == "use_candidate") != (isinstance(candidate_id, str) and bool(candidate_id)):
            raise PublicationControlError("ArtView candidate selection is inconsistent")
        presentation = row["presentation"]
        if (
            isinstance(presentation["width_percent"], bool)
            or not isinstance(presentation["width_percent"], int)
            or not 10 <= presentation["width_percent"] <= 100
            or presentation["alignment"] not in {"left", "center", "right"}
            or not isinstance(presentation["wrap_text"], bool)
            or not isinstance(presentation["wrap_tables"], bool)
            or (presentation["wrap_tables"] and not presentation["wrap_text"])
            or (presentation["alignment"] == "center" and (presentation["wrap_text"] or presentation["wrap_tables"]))
        ):
            raise PublicationControlError("ArtView presentation is invalid")
    review = value["review"]
    _exact(review, {"state", "reviewed_count", "unresolved_asset_ids"}, "ArtView review summary")
    if review != {"state": "closed", "reviewed_count": reviewed_count, "unresolved_asset_ids": unresolved} or unresolved:
        raise PublicationControlError("ArtView decisions are not accepted and closed")
    return value


def _authority_inputs(run_root: Path, contract: Mapping[str, Any], stage: str, authorities: Mapping[str, Path]) -> list[dict[str, Any]]:
    expected = _expected_stage_authorities(stage, set(authorities))
    if set(authorities) != expected:
        raise PublicationControlError(f"{stage} requires exactly: {sorted(expected)}")
    inputs: list[dict[str, Any]] = []
    for name in (*REQUIRED_AUTHORITIES[stage], *((REVIEWED_DOCX_AUTHORITY,) if REVIEWED_DOCX_AUTHORITY in expected else ())):
        path = authorities[name]
        if not path.is_file():
            raise PublicationControlError(f"missing publication authority: {name}")
        if name.endswith("_acceptance"):
            kind = name.removesuffix("_acceptance")
            _acceptance_authority(run_root, contract, kind, path)
        elif name == "master_ru_submission":
            packet_stage = _read(_stage_manifest_path(run_root, STAGES.index("master_ru_packets")))
            master_en_rows = [row for row in packet_stage["reproducible"]["inputs"] if row.get("kind") == "master_en_acceptance"]
            if len(master_en_rows) != 1:
                raise PublicationControlError("packet stage lacks exact MASTER_EN authority")
            master_en = run_root / _safe_relative(master_en_rows[0]["file"]["path"], "MASTER_EN acceptance")
            _validate_submission(path, run_root, contract, master_en)
        elif name == "artview_decisions":
            _validate_artview_decisions(path, contract["scenario"]["id"])
        elif name == REVIEWED_DOCX_AUTHORITY and path.suffix.lower() != ".docx":
            raise PublicationControlError("reviewed DOCX authority must be a .docx file")
        try:
            relative = path.relative_to(run_root).as_posix()
        except ValueError as error:
            raise PublicationControlError("publication authorities must be run-local") from error
        inputs.append({"kind": name, "file": {"path": relative, **file_identity(path)}})
    if stage in {"artview_apply", "html_candidate"}:
        acceptance = _read(authorities["artview_acceptance"])
        decision_identity = {"path": authorities["artview_decisions"].relative_to(run_root).as_posix(), **file_identity(authorities["artview_decisions"])}
        if decision_identity not in acceptance["evidence"]:
            raise PublicationControlError("ArtView acceptance does not bind native decisions")
    return inputs


def _assert_closed_stage_root(root: Path) -> None:
    expected = {"artifacts", "evidence"}
    if not root.is_dir() or {path.name for path in root.iterdir()} != expected:
        raise PublicationControlError("publication stage output root is not closed")
    if any(not (root / name).is_dir() for name in expected):
        raise PublicationControlError("publication stage output root is not closed")


def _stage50_residue_roots(run_root: Path, index: int) -> tuple[Path, Path, Path]:
    stage_id = _stage_id(index)
    return (
        run_root / "local" / "private" / stage_id,
        run_root / "local" / "cache" / stage_id,
        run_root / "cache" / stage_id,
    )


def _stage50_json_exposes_pdf(path: Path) -> bool:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        try:
            lowered = path.read_text(encoding="utf-8-sig", errors="replace").lower()
        except OSError:
            return True
        return any(term in lowered for term in (".pdf", "application/pdf", "bridge_path", "bridge_sha256", "pdf_path", "pdf_sha256"))
    return _diagnostics_expose_stage50_pdf(value)


def _assert_no_stage50_pdf(staging_or_output: Path, private: Path, local_cache: Path, cache: Path) -> None:
    for residue in (private, local_cache, cache):
        if residue.exists():
            raise PublicationControlError("Stage 50 private bridge or cache residue blocks success")
    for path in staging_or_output.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".pdf":
            raise PublicationControlError("Stage 50 cannot retain PDF anywhere in its stage scope")
        if path.suffix.lower() == ".json" and _stage50_json_exposes_pdf(path):
            raise PublicationControlError("Stage 50 cannot declare PDF media, artifacts, or bridge diagnostics")


def _sanitize_stage50_failure(staging: Path, private: Path, local_cache: Path, cache: Path) -> None:
    # Failed Stage 50 may retain safe DOCX/PNG/JSON evidence, but never PDF authority.
    if staging.exists():
        for path in tuple(staging.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() == ".pdf" or (path.suffix.lower() == ".json" and _stage50_json_exposes_pdf(path)):
                path.unlink()
    for residue in (private, local_cache, cache):
        if residue.is_dir():
            shutil.rmtree(residue)
        elif residue.exists():
            residue.unlink()


def _diagnostics_expose_stage50_pdf(value: object, key: str = "") -> bool:
    if key.lower() in {"bridge_path", "bridge_sha256", "pdf_path", "pdf_sha256"}:
        return True
    if isinstance(value, str):
        lowered = value.lower()
        return ".pdf" in lowered or "application/pdf" in lowered
    if isinstance(value, Mapping):
        return any(_diagnostics_expose_stage50_pdf(item, str(name)) for name, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_diagnostics_expose_stage50_pdf(item, key) for item in value)
    return False


def _invoke_stage(run_root: Path, run: Mapping[str, Any], contract: Mapping[str, Any], effective: Mapping[str, Any], index: int, upstream: list[dict[str, str]], authorities: Mapping[str, Path], adapter: PublicationStageAdapter) -> dict[str, Any]:
    stage = STAGES[index]
    if adapter.name != ADAPTER_NAMES[stage]:
        raise PublicationControlError(f"wrong publication adapter for {stage}")
    current_tools = _registry_tools({name: adapter for name in STAGES})
    if canonical_bytes(current_tools) != canonical_bytes(run["tools"]):
        raise PublicationControlError("publication runtime tool identity drift")
    inputs = _authority_inputs(run_root, contract, stage, authorities)
    output = run_root / "outputs" / _stage_id(index)
    staging = run_root / "local" / "staging" / _stage_id(index)
    private, local_cache, cache = _stage50_residue_roots(run_root, index)
    quarantine = run_root / "quarantine" / _stage_id(index)
    if stage == "docx_candidate" and any(path.exists() for path in (private, local_cache, cache)):
        _sanitize_stage50_failure(staging, private, local_cache, cache)
        raise PublicationControlError("private Stage 50 bridge or cache residue was removed; resume is blocked for this attempt")
    if private.exists():
        raise PublicationControlError("private stage residue blocks resume")
    if output.exists() or staging.exists() or quarantine.exists():
        raise PublicationControlError("publication stage target already exists")
    artifacts = staging / "artifacts"
    evidence = staging / "evidence"
    artifacts.mkdir(parents=True)
    evidence.mkdir(parents=True)
    started = _utc_now()
    try:
        invocation = PublicationStageInvocation(
            run_root=run_root,
            contract=contract,
            effective_config=effective,
            stage=stage,
            stage_index=index,
            authorities=dict(authorities),
            authority_inputs=tuple(inputs),
        )
        diagnostics = dict(
            adapter.invoke(staging, private, invocation)
            if adapter.context_aware
            else adapter.invoke(staging, private)
        )
        primary = _primary_candidate(run_root, contract, stage)
        staged_primary = staging / primary.relative_to(output)
        if not staged_primary.is_file():
            raise PublicationControlError(f"{stage} did not create its primary artifact")
        if stage == "docx_candidate":
            _assert_no_stage50_pdf(staging, private, local_cache, cache)
            if _diagnostics_expose_stage50_pdf(diagnostics):
                raise PublicationControlError("Stage 50 diagnostics cannot expose bridge PDF authority")
        _assert_closed_stage_root(staging)
        if stage == "pdf_candidate":
            pdfs = [path for path in staging.rglob("*.pdf") if path.is_file()]
            if len(pdfs) != 1 or staged_primary != pdfs[0]:
                raise PublicationControlError("Stage 60 must create exactly one fresh final PDF")
            required = {"document_authority_kind": "accepted_docx", "adapter": "docx_pdf_export_v1", "fresh_export": True}
            if any(diagnostics.get(k) != v for k, v in required.items()):
                raise PublicationControlError("Stage 60 lacks fresh accepted-DOCX lineage evidence")
        if stage == "production_package":
            verify_production_package(staged_primary.parent)
        if stage == "offline_verify":
            package = _primary_candidate(run_root, contract, "production_package").parent
            verify_production_package(package)
        deterministic_inventory(staging)
        output.parent.mkdir(parents=True, exist_ok=True)
        staging.replace(output)
        normalize_publication_access_if_managed(output)
    except Exception as error:
        if stage == "docx_candidate":
            _sanitize_stage50_failure(staging, private, local_cache, cache)
        failed_tree = staging if staging.exists() else output if output.exists() else None
        if failed_tree is not None:
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(failed_tree), str(quarantine))
        raise PublicationControlError(f"publication stage {stage} failed: {error}") from error
    output_artifacts = output / "artifacts"
    output_evidence = output / "evidence"
    adapter_script = (
        _repo_root() / "kb_creator" / "pipeline" / "publication_adapters.py"
        if adapter.context_aware
        else Path(__file__).resolve()
    )
    adapter_record = {"logical_name": ADAPTER_NAMES[stage], "version": 1, "script": {"path": adapter_script.name, **file_identity(adapter_script)}}
    effective_path = run_root / "effective_publication_config.json"
    reproducible = {
        "stage_id": _stage_id(index), "stage_name": stage, "stage_version": 1, "state": "succeeded",
        "run_identity_sha256": run["portable_identity_sha256"], "upstream": list(upstream),
        "inputs": [{"kind": "publication_contract", "file": run["contract"]}, {"kind": "accepted_reconstruction", "file": run["accepted_reconstruction"]["acceptance"]}, *inputs],
        "adapter": adapter_record, "effective_config": {"path": effective_path.name, **file_identity(effective_path)},
        "tools": run["tools"], "implementation_inventory_sha256": run["implementation"]["inventory_sha256"],
        "outputs": _inventory(output_artifacts, run_root), "evidence": _inventory(output_evidence, run_root),
    }
    reproducible["cache_key"] = sha256_bytes(canonical_bytes(reproducible))
    # Stage seals exclude execution timing and diagnostics.
    manifest = {
        "schema": STAGE_SCHEMA,
        "reproducible": reproducible,
        "execution": {"started_at_utc": started, "completed_at_utc": _utc_now(), "exit_code": 0, "structured_diagnostics": diagnostics},
        "reproducible_sha256": sha256_bytes(canonical_bytes({"schema": STAGE_SCHEMA, "reproducible": reproducible})),
    }
    manifest_path = _stage_manifest_path(run_root, index)
    _write(manifest_path, manifest)
    return {"schema": "kb_creator.publication_result.v1", "state": WAIT_STATES[stage], "exit_code": 10 if stage not in {"artview_apply", "production_package", "offline_verify"} else 0, "completed_stage": stage, "run_identity_sha256": run["portable_identity_sha256"], "stage_manifest": str(manifest_path)}


def publication_run(contract_path: Path, upstream_inventory_path: Path, reconstruction_acceptance_path: Path, config_root: Path, run_root: Path, run_id: str, adapters: Mapping[str, PublicationStageAdapter], tools_root: Path | None = None) -> dict[str, Any]:
    reject_legacy_publication_writer()
    if set(adapters) != set(STAGES):
        raise PublicationControlError("publication adapter registry must match the fixed graph")
    tools = _registry_tools(adapters)
    run, effective = _build_run(contract_path, upstream_inventory_path, reconstruction_acceptance_path, config_root, run_root, run_id, tools, tools_root)
    run_root.mkdir()
    _write(run_root / "run.json", run)
    _write(run_root / "effective_publication_config.json", effective)
    _, contract, effective = _load_run(run_root)
    return _invoke_stage(run_root, run, contract, effective, 0, [], {}, adapters[STAGES[0]])


def publication_resume(run_root: Path, authorities: Mapping[str, Path], adapters: Mapping[str, PublicationStageAdapter]) -> dict[str, Any]:
    reject_legacy_publication_writer()
    if set(adapters) != set(STAGES):
        raise PublicationControlError("publication adapter registry must match the fixed graph")
    # Keep every path participating in the resume boundary in one canonical
    # coordinate system.  A relative run root combined with authorities that
    # become absolute inside a context-aware adapter otherwise passes the
    # initial gate and fails only after staging has begun, quarantining a
    # semantically valid attempt.
    run_root = run_root.resolve()
    authorities = {name: path.resolve() for name, path in authorities.items()}
    run, contract, effective = _load_run(run_root)
    count, upstream = _completed_prefix(run_root, run)
    if count >= len(STAGES):
        raise PublicationControlError("publication run is already complete")
    return _invoke_stage(run_root, run, contract, effective, count, upstream, authorities, adapters[STAGES[count]])


def record_artifact_acceptance(run_root: Path, artifact_kind: str, evidence_paths: Sequence[Path], destination: Path, user_decision_reference: str, recorder_role: str = "main_orchestrator") -> dict[str, Any]:
    reject_legacy_publication_writer()
    if artifact_kind not in ACCEPTANCE_STAGE or not user_decision_reference.strip() or recorder_role != "main_orchestrator":
        raise PublicationControlError("acceptance requires a supported kind and explicit orchestrator-recorded user decision")
    if destination.exists():
        raise PublicationControlError("acceptance receipt already exists")
    try:
        destination.resolve().relative_to(run_root.resolve())
    except ValueError as error:
        raise PublicationControlError("acceptance destination must be run-local") from error
    run, contract, _ = _load_run(run_root)
    count, _ = _completed_prefix(run_root, run)
    stage = ACCEPTANCE_STAGE[artifact_kind]
    index = STAGES.index(stage)
    if count <= index:
        raise PublicationControlError("cannot accept an incomplete publication stage")
    candidate = _primary_candidate(run_root, contract, stage)
    producer = _stage_manifest_path(run_root, index)
    if not evidence_paths or any(not path.is_file() for path in evidence_paths):
        raise PublicationControlError("acceptance requires complete existing evidence")
    stage_evidence_root = run_root / "outputs" / _stage_id(index) / "evidence"
    decision_evidence = 0
    for path in evidence_paths:
        if artifact_kind == "docx" and path.suffix.lower() == ".pdf":
            raise PublicationControlError("DOCX acceptance cannot bind PDF evidence")
        try:
            path.relative_to(stage_evidence_root)
        except ValueError:
            if artifact_kind != "artview":
                raise PublicationControlError("acceptance evidence must come from its producer stage")
            try:
                _validate_artview_decisions(path, contract["scenario"]["id"])
            except PublicationControlError as error:
                raise PublicationControlError("ArtView acceptance requires closed native decisions") from error
            decision_evidence += 1
    if artifact_kind == "artview" and decision_evidence != 1:
        raise PublicationControlError("ArtView acceptance requires exactly one native decision document")
    if artifact_kind == "master_ru" and "independent_translation_qa" in contract["master_ru"]["required_qa"]:
        expected_evidence = {
            (stage_evidence_root / "MASTER_RU.qa.json").resolve(),
            (stage_evidence_root / "MASTER_RU.verification.json").resolve(),
        }
        observed_evidence = [path.resolve() for path in evidence_paths]
        if len(observed_evidence) != 2 or set(observed_evidence) != expected_evidence:
            raise PublicationControlError("MASTER_RU acceptance requires exact producer QA and independent verification")
        qa = _read(stage_evidence_root / "MASTER_RU.qa.json")
        _exact(qa, {"schema", "status", "scenario_id", "master_ru", "checks", "findings"}, "MASTER_RU producer QA")
        expected_candidate = {"path": candidate.name, **file_identity(candidate)}
        if (
            qa.get("schema") != "kb_creator.master_ru_qa.v1"
            or qa.get("status") != "pass"
            or qa.get("scenario_id") != contract["scenario"]["id"]
            or qa.get("master_ru") != expected_candidate
            or not isinstance(qa.get("checks"), Mapping)
            or not qa["checks"]
            or not all(value is True for value in qa["checks"].values())
            or qa.get("findings") != []
        ):
            raise PublicationControlError("MASTER_RU producer QA is not an exact pass for the candidate")
        verification = _read(stage_evidence_root / "MASTER_RU.verification.json")
        _exact(
            verification,
            {
                "schema", "status", "scenario_id", "master_ru", "submission",
                "packet_manifest", "contract", "candidate_inventory", "required_qa",
                "checks", "findings", "verification_sha256",
            },
            "MASTER_RU independent verification",
        )
        _validate_sealed(verification, "verification_sha256", "MASTER_RU independent verification")
        _exact(verification["master_ru"], {"bytes", "sha256"}, "verified MASTER_RU")
        _exact(verification["submission"], {"bytes", "sha256", "submission_sha256"}, "verified MASTER_RU submission")
        _exact(verification["packet_manifest"], {"bytes", "sha256", "manifest_sha256"}, "verified MASTER_RU packet")
        _exact(verification["contract"], {"bytes", "sha256"}, "verified publication contract")
        _exact(verification["candidate_inventory"], {"bytes", "sha256", "inventory_sha256"}, "verified MASTER_RU inventory")
        verification_master = verification["master_ru"]
        verification_submission = verification["submission"]
        verification_packet = verification["packet_manifest"]
        verification_contract = verification["contract"]
        verification_inventory = verification["candidate_inventory"]
        expected_checks = {
            "accepted_master_en_identity", "ordered_unit_identity",
            "markdown_structure_preservation", "mechanics_preservation",
            "terminology_authority", "asset_identity", "independent_translation_qa",
            "producer_qa", "candidate_inventory", "provenance",
        }
        stage_document = _read(producer)
        stage_inputs = stage_document["reproducible"]["inputs"]
        submission_inputs = [row for row in stage_inputs if row.get("kind") == "master_ru_submission"]
        packet_manifest = run_root / "outputs" / _stage_id(STAGES.index("master_ru_packets")) / "artifacts" / "packet_manifest.json"
        inventory_path = candidate.parent / "INVENTORY.json"
        submission_path = run_root / _safe_relative(submission_inputs[0]["file"]["path"], "MASTER_RU submission") if len(submission_inputs) == 1 else None
        submission_document = _read(submission_path) if submission_path is not None else {}
        packet_document = _read(packet_manifest)
        acceptance_checks = {
            "schema": verification.get("schema") == "kb_creator.master_ru_independent_verification.v1",
            "status": verification.get("status") == "verified_candidate_pending_user_acceptance",
            "scenario": verification.get("scenario_id") == contract["scenario"]["id"],
            "candidate": verification_master == file_identity(candidate),
            "submission_input": len(submission_inputs) == 1 and {
                key: verification_submission.get(key) for key in ("bytes", "sha256")
            } == {key: submission_inputs[0]["file"].get(key) for key in ("bytes", "sha256")},
            "submission_seal": verification_submission.get("submission_sha256") == submission_document.get("submission_sha256"),
            "packet_identity": {key: verification_packet.get(key) for key in ("bytes", "sha256")} == file_identity(packet_manifest),
            "packet_seal": verification_packet.get("manifest_sha256") == packet_document.get("manifest_sha256"),
            "contract": verification_contract == file_identity(Path(run["local"]["contract_path"])),
            "inventory_identity": {key: verification_inventory.get(key) for key in ("bytes", "sha256")} == file_identity(inventory_path),
            "inventory_seal": verification_inventory.get("inventory_sha256") == _read(inventory_path).get("inventory_sha256"),
            "required_qa": verification.get("required_qa") == contract["master_ru"]["required_qa"],
            "checks": set(verification.get("checks", {})) == expected_checks and all(value is True for value in verification["checks"].values()),
            "findings": verification.get("findings") == [],
        }
        failed_checks = sorted(name for name, passed in acceptance_checks.items() if not passed)
        if failed_checks:
            raise PublicationControlError(
                "MASTER_RU independent verification is not an exact pass for the candidate: "
                + ", ".join(failed_checks)
            )
    try:
        candidate_record = {"path": candidate.relative_to(run_root).as_posix(), **file_identity(candidate)}
        producer_record = {"path": producer.relative_to(run_root).as_posix(), **file_identity(producer)}
        evidence = [{"path": path.relative_to(run_root).as_posix(), **file_identity(path)} for path in evidence_paths]
    except ValueError as error:
        raise PublicationControlError("acceptance destination must contain candidate and evidence paths") from error
    receipt = sealed(ACCEPTANCE_SCHEMA, {"scenario_id": contract["scenario"]["id"], "artifact_kind": artifact_kind, "candidate": candidate_record, "producer_stage": producer_record, "evidence": evidence, "decision": "accepted", "decision_at_utc": _utc_now(), "user_decision_reference": user_decision_reference.strip(), "recorder_role": recorder_role}, digest_key="receipt_sha256")
    _write(destination, receipt)
    return receipt


def verify_production_package(package_root: Path) -> dict[str, Any]:
    manifest_path = package_root / "PRODUCTION_MANIFEST.json"
    manifest = _read(manifest_path)
    _exact(manifest, {"schema", "scenario_id", "package_state", "release_state", "publication_run_identity_sha256", "roles", "inventory", "stage_manifests", "acceptance_receipts", "config_inventory", "pipeline_snapshot", "upstream", "manifest_sha256"}, "production package manifest")
    _validate_sealed(manifest, "manifest_sha256", "production package manifest")
    if manifest["schema"] != PACKAGE_SCHEMA or manifest["package_state"] != "candidate_for_release_review" or manifest["release_state"] != "not_reviewed":
        raise PublicationControlError("package cannot claim acceptance or release")
    observed = deterministic_inventory(package_root)
    observed_without_manifest = [row for row in observed if row["path"] != "PRODUCTION_MANIFEST.json"]
    if manifest["inventory"] != observed_without_manifest:
        raise PublicationControlError("production package inventory mismatch")
    pdfs = [row for row in observed_without_manifest if row["path"].lower().endswith(".pdf")]
    roles = manifest["roles"]
    if not isinstance(roles, list):
        raise PublicationControlError("production package roles must be a list")
    for row in roles:
        _exact(row, {"role", "path"}, "production package role")
    role_names = [row.get("role") for row in roles]
    role_paths = [row.get("path") for row in roles]
    if len(role_names) != len(set(role_names)) or len(role_paths) != len(set(role_paths)) or not MANDATORY_PACKAGE_ROLES.issubset(role_names):
        raise PublicationControlError("production package role inventory is incomplete or duplicated")
    for row in roles:
        relative = _safe_relative(row.get("path"), f"package role {row.get('role')}")
        if not (package_root / relative).exists():
            raise PublicationControlError(f"package role path is missing: {row.get('role')}")
    role_map = {row["role"]: package_root / _safe_relative(row["path"], f"package role {row['role']}") for row in roles}
    pdf_roles = [row for row in roles if row.get("role") == "pdf"]
    if len(pdfs) != 1 or len(pdf_roles) != 1 or pdf_roles[0].get("path") != pdfs[0]["path"]:
        raise PublicationControlError("production package must contain exactly one Stage 60 PDF")
    for row in observed_without_manifest:
        if row["path"].lower().startswith((".private/", "private/", "quarantine/", "cache/")):
            raise PublicationControlError("production package contains private or cache residue")
    _validate_artview_decisions(role_map["artview_decisions"], manifest["scenario_id"])
    artview_acceptance = _read(role_map["artview_acceptance"])
    _validate_sealed(artview_acceptance, "receipt_sha256", "packaged ArtView acceptance")
    decisions_identity = _identity(role_map["artview_decisions"], package_root)
    if not isinstance(artview_acceptance.get("evidence"), list) or artview_acceptance["evidence"].count(decisions_identity) != 1:
        raise PublicationControlError("ArtView acceptance does not bind packaged decisions exactly once")
    stage_records = manifest["stage_manifests"]
    if not isinstance(stage_records, list) or len(stage_records) != PACKAGED_STAGE_COUNT:
        raise PublicationControlError("package must contain the exact eight ordered upstream stage manifests")
    if len({canonical_bytes(row) for row in stage_records}) != PACKAGED_STAGE_COUNT:
        raise PublicationControlError("package stage manifest set contains duplicates")
    packaged_stages: list[dict[str, Any]] = []
    expected_upstream: list[dict[str, str]] = []
    continuity: tuple[object, ...] | None = None
    for index, record in enumerate(stage_records):
        path = _check_identity(package_root, record, f"packaged stage manifest {index}")
        candidate = _read(path)
        _exact(candidate, {"schema", "reproducible", "execution", "reproducible_sha256"}, "packaged stage manifest")
        reproducible = candidate["reproducible"]
        _exact(reproducible, {"stage_id", "stage_name", "stage_version", "state", "run_identity_sha256", "upstream", "inputs", "adapter", "effective_config", "tools", "implementation_inventory_sha256", "outputs", "evidence", "cache_key"}, "packaged reproducible stage")
        if candidate["schema"] != STAGE_SCHEMA or candidate["reproducible_sha256"] != sha256_bytes(canonical_bytes({"schema": STAGE_SCHEMA, "reproducible": reproducible})):
            raise PublicationControlError("packaged stage manifest seal mismatch")
        without_cache = {key: item for key, item in reproducible.items() if key != "cache_key"}
        expected_stage = STAGES[index]
        inputs = reproducible["inputs"]
        observed_kinds = {row.get("kind") for row in inputs if isinstance(row, dict)} if isinstance(inputs, list) else set()
        expected_inputs = {"publication_contract", "accepted_reconstruction", *_expected_stage_authorities(expected_stage, observed_kinds)}
        if not isinstance(inputs, list) or len(inputs) != len(expected_inputs) or {row.get("kind") for row in inputs if isinstance(row, dict)} != expected_inputs:
            raise PublicationControlError("packaged stage authority inputs mismatch")
        for row in inputs:
            _exact(row, {"kind", "file"}, "packaged stage input")
            _exact(row["file"], {"path", "bytes", "sha256"}, "packaged stage input identity")
        adapter = reproducible["adapter"]
        _exact(adapter, {"logical_name", "version", "script"}, "packaged stage adapter")
        _exact(adapter["script"], {"path", "bytes", "sha256"}, "packaged stage adapter script")
        _exact(reproducible["effective_config"], {"path", "bytes", "sha256"}, "packaged stage effective config")
        if (
            reproducible["stage_id"] != _stage_id(index)
            or reproducible["stage_name"] != expected_stage
            or reproducible["stage_version"] != 1
            or reproducible["state"] != "succeeded"
            or reproducible["run_identity_sha256"] != manifest["publication_run_identity_sha256"]
            or reproducible["upstream"] != expected_upstream
            or adapter["logical_name"] != ADAPTER_NAMES[expected_stage]
            or adapter["version"] != 1
            or reproducible["cache_key"] != sha256_bytes(canonical_bytes(without_cache))
        ):
            raise PublicationControlError("packaged stage graph or identity mismatch")
        observed_continuity = (
            canonical_bytes(adapter["script"]),
            canonical_bytes(reproducible["effective_config"]),
            canonical_bytes(reproducible["tools"]),
            reproducible["implementation_inventory_sha256"],
            canonical_bytes([row["file"] for row in inputs if row["kind"] in {"publication_contract", "accepted_reconstruction"}]),
        )
        if continuity is None:
            continuity = observed_continuity
        elif observed_continuity != continuity:
            raise PublicationControlError("packaged stage config, implementation, or tools continuity mismatch")
        packaged_stages.append(candidate)
        expected_upstream.append({"stage_id": _stage_id(index), "manifest_sha256": candidate["reproducible_sha256"]})
    reviewed_inputs = [row["file"] for row in packaged_stages[STAGES.index("docx_candidate")]["reproducible"]["inputs"] if row["kind"] == REVIEWED_DOCX_AUTHORITY]
    reviewed_role = role_map.get("reviewed_docx_submission")
    if reviewed_inputs:
        if reviewed_role is None or file_identity(reviewed_role) != {key: reviewed_inputs[0][key] for key in ("bytes", "sha256")}:
            raise PublicationControlError("packaged reviewed DOCX input identity mismatch")
    elif reviewed_role is not None:
        raise PublicationControlError("package has an unbound reviewed DOCX input")
    effective_identity = file_identity(role_map["effective_config"])
    if {key: packaged_stages[0]["reproducible"]["effective_config"].get(key) for key in ("bytes", "sha256")} != effective_identity:
        raise PublicationControlError("packaged effective config does not match stage config authority")
    for group in ("acceptance_receipts", "config_inventory", "pipeline_snapshot"):
        if len({canonical_bytes(row) for row in manifest[group]}) != len(manifest[group]):
            raise PublicationControlError(f"package {group} contains duplicates")
        for record in manifest[group]:
            _check_identity(package_root, record, f"package {group}")
    for record in manifest["upstream"].values():
        _check_identity(package_root, record, "package upstream evidence")
    stage60 = packaged_stages[-1]
    reproducible = stage60["reproducible"]
    stage60_inputs = reproducible.get("inputs", [])
    document_inputs = [row for row in stage60_inputs if row.get("kind") == "docx_acceptance"]
    forbidden_document_inputs = {"html_acceptance", "pdf", "source_html", "stage50_pdf", "stage50_png"}
    if reproducible.get("adapter", {}).get("logical_name") != "docx_pdf_export_v1" or len(document_inputs) != 1 or forbidden_document_inputs.intersection(row.get("kind") for row in stage60_inputs):
        raise PublicationControlError("packaged PDF lacks exact accepted-DOCX Stage 60 lineage")
    stage60_pdfs = [row for row in reproducible.get("outputs", {}).get("files", []) if str(row.get("path", "")).lower().endswith(".pdf")]
    if len(stage60_pdfs) != 1 or {k: stage60_pdfs[0][k] for k in ("bytes", "sha256")} != file_identity(role_map["pdf"]):
        raise PublicationControlError("packaged PDF bytes do not match Stage 60 output")
    acceptance_kinds = ("master_en", "master_ru", "artview", "html", "docx", "pdf")
    acceptance_records = manifest["acceptance_receipts"]
    if not isinstance(acceptance_records, list) or len(acceptance_records) != len(acceptance_kinds):
        raise PublicationControlError("package must contain exactly six acceptance receipt identities")
    acceptance_by_kind: dict[str, dict[str, Any]] = {}
    candidate_roles = {
        "master_en": "master_en", "master_ru": "master_ru",
        "artview": "artview_candidate_manifest", "html": "html",
        "docx": "docx", "pdf": "pdf",
    }
    producer_indexes = {kind: STAGES.index(ACCEPTANCE_STAGE[kind]) for kind in acceptance_kinds}
    for kind in acceptance_kinds:
        receipt_path = role_map[f"{kind}_acceptance"]
        expected_record = _identity(receipt_path, package_root)
        if acceptance_records.count(expected_record) != 1:
            raise PublicationControlError(f"package {kind} acceptance identity does not match its role")
        receipt = _read(receipt_path)
        _validate_sealed(receipt, "receipt_sha256", f"packaged {kind} acceptance")
        if (
            receipt.get("schema") != ACCEPTANCE_SCHEMA
            or receipt.get("scenario_id") != manifest["scenario_id"]
            or receipt.get("artifact_kind") != kind
            or receipt.get("decision") != "accepted"
            or receipt.get("recorder_role") != "main_orchestrator"
            or {key: receipt.get("candidate", {}).get(key) for key in ("bytes", "sha256")} != file_identity(role_map[candidate_roles[kind]])
            or {key: receipt.get("producer_stage", {}).get(key) for key in ("bytes", "sha256")} != {key: stage_records[producer_indexes[kind]][key] for key in ("bytes", "sha256")}
        ):
            raise PublicationControlError(f"packaged {kind} acceptance does not bind its candidate and producer")
        acceptance_by_kind[kind] = receipt
    if len(acceptance_by_kind) != len(acceptance_kinds):
        raise PublicationControlError("package acceptance kinds are incomplete or duplicated")
    for index, stage in enumerate(packaged_stages):
        for row in stage["reproducible"]["inputs"]:
            kind = row.get("kind", "")
            if kind.endswith("_acceptance") and kind.removesuffix("_acceptance") in acceptance_by_kind:
                receipt_kind = kind.removesuffix("_acceptance")
                if {key: row.get("file", {}).get(key) for key in ("bytes", "sha256")} != file_identity(role_map[f"{receipt_kind}_acceptance"]):
                    raise PublicationControlError(f"packaged Stage {_stage_id(index)} has stale {kind} authority")
    pdf_acceptance = acceptance_by_kind["pdf"]
    docx_acceptance_identity = file_identity(role_map["docx_acceptance"])
    if {k: document_inputs[0]["file"][k] for k in ("bytes", "sha256")} != docx_acceptance_identity:
        raise PublicationControlError("Stage 60 does not bind the packaged DOCX acceptance")
    return {"schema": "kb_creator.production_package_verification.v1", "state": "candidate_for_release_review", "release_state": "not_reviewed", "manifest_sha256": manifest["manifest_sha256"], "pdf_count": 1}


def parse_authorities(values: Sequence[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise PublicationControlError("authority must use name=path")
        name, raw_path = value.split("=", 1)
        if not name or name in result or not raw_path:
            raise PublicationControlError("invalid or duplicate authority")
        result[name] = Path(raw_path)
    return result
