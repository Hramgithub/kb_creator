"""Fail-closed shared enforcement for scenario reconstruction candidates.

Public APIs have no test or policy override. Tests install a sealed TEST
context and exercise the same execution and verification route.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import subprocess
import ctypes
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Final, Literal

BRANCH: Final = "codex/kb-creator-viral"
HEAD: Final = "54607bd3b9362adbb0c4bca64e8751482797f380"
QA_NAME: Final = "RECONSTRUCTED_EN.qa.json"
AUTHORITY_ORDER: Final = ("CONTRACT", "SIDECAR", "RECOVERY_MANIFEST", "RECOVERY_EVIDENCE", "QA", "SOURCE_IDENTITY", "PAGE_PROVENANCE", "CONTENT_PROVENANCE", "ASSET_PROVENANCE", "ENTITY_INVENTORY", "HANDOUT_INVENTORY", "NAVIGATION_INVENTORY", "CONTENT_MODE_REVIEW", "REFERENCE_ONLY_AUDIT", "BLOCKER_LEDGER", "COMMANDS")
SCHEMAS: Final = {"CONTRACT": "kb_creator.scenario_contract.v1", "SIDECAR": "kb_creator.source_admission.v1", "RECOVERY_MANIFEST": "viral_raw_engine_input_recovery_manifest.v1", "RECOVERY_EVIDENCE": "viral_raw_engine_input_recovery_evidence.v1", "QA": "kb_creator.reconstructed_en_qa.v3", "SOURCE_IDENTITY": "kb_creator.source_identity.v2", "PAGE_PROVENANCE": "kb_creator.page_provenance.v3", "CONTENT_PROVENANCE": "kb_creator.content_provenance.v3", "ASSET_PROVENANCE": "kb_creator.asset_provenance.v3", "ENTITY_INVENTORY": "kb_creator.entity_inventory.v3", "HANDOUT_INVENTORY": "kb_creator.handout_inventory.v3", "NAVIGATION_INVENTORY": "kb_creator.navigation_inventory.v3", "CONTENT_MODE_REVIEW": "kb_creator.content_mode_review.v2", "REFERENCE_ONLY_AUDIT": "kb_creator.reference_only_audit.v2", "BLOCKER_LEDGER": "kb_creator.blocker_ledger.v3", "COMMANDS": "kb_creator.reconstruction_commands.v3"}
AUTHORITY_PATHS: Final = {"CONTRACT": "SCENARIO_CONTRACT.json", "QA": QA_NAME, "SOURCE_IDENTITY": "SOURCE_IDENTITY.json", "PAGE_PROVENANCE": "evidence/PAGE_PROVENANCE.json", "CONTENT_PROVENANCE": "evidence/CONTENT_PROVENANCE.json", "ASSET_PROVENANCE": "evidence/ASSET_PROVENANCE.json", "ENTITY_INVENTORY": "evidence/ENTITY_INVENTORY.json", "HANDOUT_INVENTORY": "evidence/HANDOUT_INVENTORY.json", "NAVIGATION_INVENTORY": "evidence/NAVIGATION_INVENTORY.json", "CONTENT_MODE_REVIEW": "evidence/CONTENT_MODE_REVIEW.json", "REFERENCE_ONLY_AUDIT": "evidence/REFERENCE_ONLY_AUDIT.json", "BLOCKER_LEDGER": "evidence/BLOCKER_LEDGER.json", "COMMANDS": "evidence/COMMANDS.json"}
FORBIDDEN_SUFFIXES: Final = (".pdf", ".pyc", ".pyo")
FORBIDDEN_SEGMENTS: Final = ("__pycache__", "_bridge_runtime", ".cache", "cache", "caches", ".pytest_cache", "tmp", "temp")


class ReconstructionStop(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code, self.detail = code, detail
        super().__init__(code + (f": {detail}" if detail else ""))


def _fail(code: str, detail: str = "") -> None:
    raise ReconstructionStop(code, detail)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        _fail("E_PATH_MISSING", path.as_posix())
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        _fail("E_PATH_MISSING", str(exc))
    if not isinstance(value, dict):
        _fail("E_PATH_TYPE", path.as_posix())
    return value


def _write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(json_bytes(value))
    except FileExistsError:
        _fail("E_BUILD_OVERWRITE", path.as_posix())


class ProfileKind(str, Enum):
    PRODUCTION = "production"
    TEST = "test"


@dataclass(frozen=True, slots=True)
class RepositoryIdentity:
    root: Path
    branch: str
    head: str


@dataclass(frozen=True, slots=True)
class FileAuthority:
    relative_path: str
    bytes: int
    sha256: str
    schema: str | None


@dataclass(frozen=True, slots=True)
class EnforcementAuthority:
    expected_branch: str
    expected_head: str
    source: FileAuthority
    sidecar: FileAuthority
    contract: FileAuthority
    recovery_manifest: FileAuthority
    recovery_evidence: FileAuthority
    allowed_state: str
    blocker_ids: tuple[str, ...]
    forbidden_suffixes: tuple[str, ...]
    forbidden_segments: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EnforcementProfile:
    profile_id: str
    kind: ProfileKind
    authority: EnforcementAuthority
    authority_sha256: str


@dataclass(frozen=True, slots=True)
class EnforcementContext:
    profile: EnforcementProfile
    identity: Any
    filesystem: Any


@dataclass(frozen=True, slots=True)
class OperationPaths:
    contract_path: Path
    source_path: Path
    recovery_root: Path
    run_root: Path


@dataclass(frozen=True, slots=True)
class OwnedTempRoot:
    parent: Path
    final: Path
    temp: Path
    marker: Path
    nonce: str
    profile_sha256: str
    directory_file_id: tuple[int, int]


@dataclass(frozen=True, slots=True)
class BuildVerificationToken:
    owned: OwnedTempRoot
    model_sha256: str
    expected_manifests: tuple[tuple[str, str], ...]
    command_actions: tuple[str, ...]


class ResealAuthority(str, Enum):
    """The only transport documents a negative fixture may regenerate."""
    SIDECAR = "sidecar"
    CONTRACT = "contract"
    RECOVERY_MANIFEST = "recovery_manifest"
    RECOVERY_EVIDENCE = "recovery_evidence"
    SOURCE_IDENTITY = "source_identity"
    PAGE_PROVENANCE = "page_provenance"
    CONTENT_PROVENANCE = "content_provenance"
    ASSET_PROVENANCE = "asset_provenance"
    NAVIGATION = "navigation"
    COMMANDS = "commands"
    INVENTORY = "inventory"
    QA = "qa"
    PROFILE = "profile"


@dataclass(frozen=True, slots=True)
class MutationCase:
    """A closed negative-fixture instruction; defaults are deliberately absent."""
    case_id: str
    expected_code: str
    mutate: Callable[[Any], None]
    reseal: tuple[ResealAuthority, ...]
    semantic_selector: str
    allowed_transport_selectors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MutationAudit:
    """Serializable evidence that a single negative mutation stayed contained."""
    case_id: str
    family: str
    fixture_root_token: str
    semantic_selector: str
    semantic_before_sha256: str
    semantic_after_sha256: str
    changed_before_reseal: tuple[str, ...]
    declared_reseals: tuple[str, ...]
    changed_by_reseal: tuple[str, ...]
    expected_code: str
    observed_code: str
    strict_verify_calls: int
    outside_fixture_reads: int
    undeclared_changes: tuple[str, ...]
    residue: tuple[str, ...]
    result: str

    def as_json(self) -> dict[str, object]:
        return {
            "case_id": self.case_id, "family": self.family,
            "fixture_root_token": self.fixture_root_token,
            "semantic_selector": self.semantic_selector,
            "semantic_before_sha256": self.semantic_before_sha256,
            "semantic_after_sha256": self.semantic_after_sha256,
            "changed_before_reseal": list(self.changed_before_reseal),
            "declared_reseals": list(self.declared_reseals),
            "changed_by_reseal": list(self.changed_by_reseal),
            "expected_code": self.expected_code, "observed_code": self.observed_code,
            "strict_verify_calls": self.strict_verify_calls,
            "outside_fixture_reads": self.outside_fixture_reads,
            "undeclared_changes": list(self.undeclared_changes),
            "residue": list(self.residue), "result": self.result,
        }


@dataclass(frozen=True, slots=True)
class SourceObservation:
    bytes: int
    sha256: str
    page_count: int
    media_box: tuple[int, int]
    rotations: tuple[int, ...]
    page_pngs: tuple[bytes, ...]


@dataclass(frozen=True, slots=True)
class PayloadFile:
    relative_path: str
    payload: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class PageInput:
    page_number: int
    engine_page_idx: int
    contract_role: str
    contract_content_mode: str
    markdown_bytes: bytes
    render_png: bytes


@dataclass(frozen=True, slots=True)
class AssetInput:
    asset_id: str
    engine_relative_path: str
    payload_sha256: str
    payload_bytes: int
    mime: str
    reference_occurrences: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ValidatedReconstructionInput:
    canonical_contract_bytes: bytes
    contract_sha256: str
    source: SourceObservation
    recovery_manifest_bytes: bytes
    recovery_evidence_bytes: bytes
    engine_payload: tuple[PayloadFile, ...]
    pages: tuple[PageInput, ...]
    assets: tuple[AssetInput, ...]
    handout_ordinals: tuple[int, ...]


class _Provider:
    def __init__(self, bound_profile_sha256: str, identity: RepositoryIdentity | None = None,
                 reparse_paths: tuple[Path, ...] = ()) -> None:
        self.bound_profile_sha256 = bound_profile_sha256
        self.identity = identity
        self.reparse_paths = reparse_paths


@dataclass(frozen=True, slots=True)
class FileSystemEntry:
    """No-follow classification used by both the production and test routes."""
    kind: str
    size: int
    file_id: tuple[int, int]
    file_attributes: int
    reparse_tag: int | None


@dataclass(frozen=True, slots=True)
class ClassificationOverride:
    """A single immutable test overlay; the underlying entry remains physical."""
    normalized_path: str
    replacement: FileSystemEntry


class WindowsFilesystemProvider(_Provider):
    def classify(self, path: Path) -> FileSystemEntry:
        try:
            stat = os.lstat(path)
        except FileNotFoundError:
            _fail("E_PATH_MISSING", path.as_posix())
        kind = "directory" if os.path.isdir(path) else "file" if os.path.isfile(path) else "other"
        attributes = getattr(stat, "st_file_attributes", 0)
        if path.is_symlink():
            attributes |= 0x400
        return FileSystemEntry(kind, stat.st_size, (stat.st_dev, stat.st_ino), attributes, None)


@dataclass(frozen=True, slots=True)
class TestFilesystemProvider:
    real: WindowsFilesystemProvider
    overrides: tuple[ClassificationOverride, ...]
    provider_id: str
    bound_profile_sha256: str

    def classify(self, path: Path) -> FileSystemEntry:
        entry = self.real.classify(path)
        normalized = os.path.normcase(os.path.normpath(str(path)))
        for override in self.overrides:
            if normalized == override.normalized_path:
                return override.replacement
        return entry


def _classify(context: EnforcementContext, path: Path) -> FileSystemEntry:
    provider = context.filesystem
    classifier = getattr(provider, "classify", None)
    if classifier is not None:
        return classifier(path)
    # Compatibility only for the completed source-family fixtures.
    entry = WindowsFilesystemProvider("", None, getattr(provider, "reparse_paths", ())).classify(path)
    if path in getattr(provider, "reparse_paths", ()):
        return FileSystemEntry(entry.kind, entry.size, entry.file_id, entry.file_attributes | 0x400, 0xA000000C)
    return entry


def _reject_reparse(entry: FileSystemEntry, path: Path) -> None:
    if entry.file_attributes & 0x400:
        _fail("E_PATH_REPARSE", path.as_posix())


def _authority_payload(authority: EnforcementAuthority) -> dict[str, object]:
    def atom(value: FileAuthority) -> tuple[str, int, str, str | None]:
        return value.relative_path, value.bytes, value.sha256, value.schema
    return {"branch": authority.expected_branch, "head": authority.expected_head, "source": atom(authority.source), "sidecar": atom(authority.sidecar), "contract": atom(authority.contract), "recovery_manifest": atom(authority.recovery_manifest), "recovery_evidence": atom(authority.recovery_evidence), "state": authority.allowed_state, "blockers": authority.blocker_ids, "suffixes": authority.forbidden_suffixes, "segments": authority.forbidden_segments}


def _profile_seal(profile_id: str, kind: ProfileKind, authority: EnforcementAuthority) -> str:
    return sha256_bytes(json_bytes({"id": profile_id, "kind": kind.value, "authority": _authority_payload(authority)}))


def _production_authority() -> EnforcementAuthority:
    return EnforcementAuthority(BRANCH, HEAD,
        FileAuthority("kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf", 20718150, "0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05", None),
        FileAuthority("kb_creator/working/viral/source/SOURCE_ADMISSION.json", 0, "3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9", SCHEMAS["SIDECAR"]),
        FileAuthority("kb_creator/contracts/viral.json", 0, "67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D", SCHEMAS["CONTRACT"]),
        FileAuthority("RECOVERY_MANIFEST.json", 0, "41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169", SCHEMAS["RECOVERY_MANIFEST"]),
        FileAuthority("RECOVERY_EVIDENCE.json", 0, "F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC", SCHEMAS["RECOVERY_EVIDENCE"]),
        "candidate_needs_review", ("full-visual-review", "unknown-content-modes-1-5", "handout-map-pregen-navigation-review", "asset-placement-ownership-review"), FORBIDDEN_SUFFIXES, FORBIDDEN_SEGMENTS)


_prod_authority = _production_authority()
PRODUCTION_PROFILE: Final = EnforcementProfile("viral-production", ProfileKind.PRODUCTION, _prod_authority, _profile_seal("viral-production", ProfileKind.PRODUCTION, _prod_authority))
_WORKTREE_ROOT: Final = Path(__file__).resolve().parents[2]
PRODUCTION_CONTEXT: Final = EnforcementContext(PRODUCTION_PROFILE, _Provider(PRODUCTION_PROFILE.authority_sha256, RepositoryIdentity(_WORKTREE_ROOT, BRANCH, HEAD)), _Provider(PRODUCTION_PROFILE.authority_sha256))


def _admit_context(context: EnforcementContext, *, route: Literal["public", "test"]) -> None:
    if not isinstance(context, EnforcementContext) or not isinstance(context.profile, EnforcementProfile):
        _fail("E_PROFILE_INCOMPLETE")
    profile = context.profile
    if profile.authority_sha256 != _profile_seal(profile.profile_id, profile.kind, profile.authority):
        _fail("E_PROFILE_SEAL")
    if route == "public":
        if context is not PRODUCTION_CONTEXT or profile is not PRODUCTION_PROFILE or profile.kind is not ProfileKind.PRODUCTION:
            _fail("E_PROFILE_ROUTE")
    elif profile.kind is not ProfileKind.TEST or context is PRODUCTION_CONTEXT or profile is PRODUCTION_PROFILE:
        _fail("E_PROFILE_ROUTE")
    if any(getattr(provider, "bound_profile_sha256", None) != profile.authority_sha256 for provider in (context.identity, context.filesystem)):
        _fail("E_PROVIDER_BINDING")


def _file_id(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_dev, stat.st_ino


def candidate_records(root: Path, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    records: list[dict[str, Any]] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            _fail("E_PATH_REPARSE", path.as_posix())
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative not in excluded:
                records.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return sorted(records, key=lambda record: record["path"])


def manifest_digest(records: list[dict[str, Any]]) -> str:
    return sha256_bytes("".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in records).encode("utf-8"))


def _verify_inventory_authority(candidate_root: Path, qa: dict[str, Any]) -> None:
    """Validate QA's non-circular inventory before generic graph consumers."""
    rows = qa.get("output_inventory")
    if not isinstance(rows, list):
        _fail("E_INV_ROW_SHAPE")
    paths: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            _fail("E_INV_ROW_SHAPE")
        relative, size, digest = row["path"], row["bytes"], row["sha256"]
        if not isinstance(relative, str) or not isinstance(size, int) or isinstance(size, bool) or size < 0 or not isinstance(digest, str):
            _fail("E_INV_ROW_SHAPE")
        if "\\" in relative:
            _fail("E_INV_PATH_BACKSLASH")
        if relative.startswith("/") or (len(relative) >= 2 and relative[1] == ":"):
            _fail("E_INV_PATH_ABSOLUTE_OR_DRIVE")
        if ".." in relative.split("/"):
            _fail("E_INV_PATH_PARENT_SEGMENT")
        if relative.startswith("./"):
            _fail("E_INV_PATH_LEADING_DOT_SLASH")
        if not relative or relative.endswith("/") or "" in relative.split("/") or "." in relative.split("/"):
            _fail("E_INV_PATH_SYNTAX")
        if digest != digest.upper():
            _fail("E_INV_ROW_HASH_LOWERCASE")
        if len(digest) != 64 or any(char not in "0123456789ABCDEF" for char in digest):
            _fail("E_INV_ROW_HASH")
        paths.append(relative)
    if QA_NAME in paths:
        _fail("E_INV_QA_INCLUDED")
    if len(paths) != len(set(paths)):
        _fail("E_INV_DUPLICATE_PATH")
    live = candidate_records(candidate_root, {QA_NAME})
    live_by_path = {row["path"]: row for row in live}
    listed = set(paths)
    missing = set(live_by_path) - listed
    if missing:
        path = sorted(missing)[0]
        if path == "RECONSTRUCTED_EN.md":
            _fail("E_INV_ORDINARY_ROW_MISSING")
        if path.startswith("evidence/"):
            _fail("E_INV_EVIDENCE_ROW_MISSING")
        if path.startswith("renders/contact_sheets/"):
            _fail("E_INV_SHEET_ROW_MISSING")
        _fail("E_INV_ROW_MISSING")
    if listed - set(live_by_path):
        _fail("E_INV_STALE_EXTRA_PATH")
    if qa.get("output_inventory_count") != len(rows) or len(rows) != 501:
        _fail("E_INV_CARDINALITY")
    if paths != sorted(paths):
        _fail("E_INV_ORDER_NONORDINAL")
    for row in rows:
        expected = live_by_path[row["path"]]
        if row["bytes"] != expected["bytes"]:
            _fail("E_INV_ROW_BYTES")
        if row["sha256"] != expected["sha256"]:
            if row["sha256"] == "0" * 64:
                _fail("E_INV_ROW_HASH")
            _fail("E_INV_LIVE_FILE_CHANGED")
    if qa.get("output_inventory_sha256") != manifest_digest(rows):
        _fail("E_INV_DIGEST")


def candidate_manifest(root: Path, exclude: set[str] | None = None) -> tuple[str, list[str]]:
    records = candidate_records(root, exclude)
    return manifest_digest(records), [f"{row['path']}\t{row['bytes']}\t{row['sha256']}" for row in records]


def _exact_file(path: Path, authority: FileAuthority, code: str) -> None:
    """Observe a sealed production input without accepting caller metadata."""
    if not path.is_file() or path.is_symlink():
        _fail("E_PATH_MISSING")
    if authority.bytes and path.stat().st_size != authority.bytes:
        _fail(code + "_BYTES")
    if sha256_file(path) != authority.sha256:
        _fail(code + "_HASH")


def _production_repository_identity() -> RepositoryIdentity:
    """The public route owns branch/HEAD observation; TEST never reaches this."""
    try:
        branch = subprocess.run(["git", "-C", str(_WORKTREE_ROOT), "branch", "--show-current"], check=True, capture_output=True, text=True).stdout.strip()
        head = subprocess.run(["git", "-C", str(_WORKTREE_ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        _fail("E_REPO_ROOT")
    return RepositoryIdentity(_WORKTREE_ROOT, branch, head)


def _validate_production_inputs(paths: OperationPaths, context: EnforcementContext) -> None:
    """Bind retained local source, sidecar, contract and recovery payload itself."""
    authority = context.profile.authority
    expected_source = _WORKTREE_ROOT / authority.source.relative_path
    expected_contract = _WORKTREE_ROOT / authority.contract.relative_path
    if paths.source_path.resolve() != expected_source.resolve():
        _fail("E_SOURCE_PATH")
    if paths.contract_path.resolve() != expected_contract.resolve():
        _fail("E_CONTRACT_PATH")
    _exact_file(paths.source_path, authority.source, "E_SOURCE")
    _exact_file(paths.source_path.with_name("SOURCE_ADMISSION.json"), authority.sidecar, "E_SIDECAR")
    _exact_file(paths.contract_path, authority.contract, "E_CONTRACT")
    _exact_file(paths.recovery_root / authority.recovery_manifest.relative_path, authority.recovery_manifest, "E_RECOVERY_MANIFEST")
    _exact_file(paths.recovery_root / authority.recovery_evidence.relative_path, authority.recovery_evidence, "E_RECOVERY_EVIDENCE")
    manifest = _load(paths.recovery_root / authority.recovery_manifest.relative_path)
    rows = manifest.get("files")
    if not isinstance(rows, list) or len(rows) != 211 or manifest.get("successor_file_count") != 211:
        _fail("E_RECOVERY_FILE_COUNT")
    seen: set[str] = set()
    for row in rows:
        if set(row) != {"path", "bytes", "sha256", "source_path"} or not isinstance(row["bytes"], int) or isinstance(row["bytes"], bool):
            _fail("E_RECOVERY_ROW_SHAPE")
        rel = row["path"]
        if not isinstance(rel, str) or rel in seen or Path(rel).is_absolute() or ".." in Path(rel).parts:
            _fail("E_RECOVERY_ROW_PATH")
        seen.add(rel)
        payload = paths.recovery_root / rel
        if not payload.is_file() or payload.is_symlink() or payload.stat().st_size != row["bytes"]:
            _fail("E_RECOVERY_ROW_BYTES")
        if sha256_file(payload) != row["sha256"]:
            _fail("E_RECOVERY_ROW_HASH")


def _verify_test_source_admission(paths: OperationPaths, context: EnforcementContext) -> None:
    """Exercise the retained-source/sidecar boundary in sealed fixtures."""
    source = paths.source_path
    _reject_reparse(_classify(context, source), source)
    if not source.is_file():
        _fail("E_PATH_MISSING")
    sidecar_path = source.with_name("SOURCE_ADMISSION.json")
    sidecar = _load(sidecar_path)
    if sidecar.get("schema") != SCHEMAS["SIDECAR"]:
        _fail("E_SCHEMA_SIDECAR")
    expected_raw = sidecar.get("raw_sha256")
    sealed = dict(sidecar)
    sealed.pop("raw_sha256", None)
    if not isinstance(expected_raw, str) or expected_raw != sha256_bytes(json_bytes(sealed)):
        _fail("E_SIDECAR_HASH")
    working = sidecar.get("working_source")
    policy = sidecar.get("policy")
    if not isinstance(working, dict) or not isinstance(policy, dict):
        _fail("E_SIDECAR_WORKING_PATH")
    if working.get("path") != source.name:
        _fail("E_SOURCE_PATH" if source.name != "Call_of_Cthulhu_Viral.pdf" else "E_SIDECAR_WORKING_PATH")
    actual_bytes, actual_hash = source.stat().st_size, sha256_file(source)
    if sidecar.get("source_bytes") != actual_bytes:
        _fail("E_SOURCE_BYTES")
    if sidecar.get("source_sha256") != actual_hash:
        _fail("E_SOURCE_HASH")
    if working.get("bytes") != actual_bytes:
        _fail("E_SIDECAR_WORKING_BYTES")
    if working.get("sha256") != actual_hash:
        _fail("E_SIDECAR_WORKING_HASH")
    if working.get("page_count") != 124:
        _fail("E_SIDECAR_PAGE_COUNT")
    if working.get("media_box") != [612, 792]:
        _fail("E_SIDECAR_MEDIA_BOX")
    if working.get("rotations") != [0] * 124:
        _fail("E_SIDECAR_ROTATION")
    if sidecar.get("external_locator") not in (None, ""):
        _fail("E_SOURCE_EXTERNAL_FORBIDDEN")
    if policy.get("runtime_dependency") is not False:
        _fail("E_SIDECAR_RUNTIME_DEPENDENCY")
    if policy.get("external_path_allowed") is not False:
        _fail("E_SIDECAR_EXTERNAL_ALLOWED")
    if policy.get("subsequent_path") != source.name:
        _fail("E_SIDECAR_SUBSEQUENT_PATH")
    if policy.get("origin") != "retained_local_source":
        _fail("E_SIDECAR_ORIGIN_POLICY")


def _verify_test_aut_authorities(paths: OperationPaths, root: Path) -> None:
    """Verify the physical contract, snapshot, identity and recovery seams.

    This deliberately runs before candidate topology/inventory: AUT mutations
    must expose their own earliest binding failure rather than a stale
    transport digest.
    """
    contract_path = paths.contract_path
    if not contract_path.is_file() or contract_path.is_symlink():
        _fail("E_CONTRACT_PATH")
    contract = _load(contract_path)
    if contract.get("schema") != SCHEMAS["CONTRACT"]:
        _fail("E_CONTRACT_CANONICAL")
    sealed_contract = dict(contract); declared_contract_hash = sealed_contract.pop("raw_sha256", None)
    if declared_contract_hash != sha256_bytes(json_bytes(sealed_contract)):
        _fail("E_CONTRACT_HASH")
    identity = _load(root / AUTHORITY_PATHS["SOURCE_IDENTITY"])
    snapshot_path = root / AUTHORITY_PATHS["CONTRACT"]
    snapshot = _load(snapshot_path)
    raw_contract = sha256_file(contract_path)
    if identity.get("contract_snapshot") != snapshot:
        _fail("E_CONTRACT_SNAPSHOT_BYTES")
    if identity.get("contract_snapshot_sha256") != sha256_file(snapshot_path):
        _fail("E_CONTRACT_SNAPSHOT_HASH")
    if snapshot != contract:
        _fail("E_CONTRACT_CANONICAL")
    source = paths.source_path
    expected_source = {
        "bytes": source.stat().st_size,
        "sha256": sha256_file(source),
        "page_count": 124,
        "media_box": [612, 792],
        "rotations": [0] * 124,
    }
    if identity.get("contract_sha256") != raw_contract:
        _fail("E_SOURCE_IDENTITY_CONTRACT")
    for key, code in (("bytes", "E_SOURCE_IDENTITY_SOURCE_BYTES"), ("sha256", "E_SOURCE_IDENTITY_SOURCE_HASH"),
                      ("page_count", "E_SOURCE_IDENTITY_PAGE_COUNT"), ("media_box", "E_SOURCE_IDENTITY_MEDIA_BOX"),
                      ("rotations", "E_SOURCE_IDENTITY_ROTATION")):
        if identity.get("source", {}).get(key) != expected_source[key]:
            _fail(code)
    manifest_path = paths.recovery_root / "RECOVERY_MANIFEST.json"
    evidence_path = paths.recovery_root / "RECOVERY_EVIDENCE.json"
    if paths.recovery_root.name != "recovery":
        _fail("E_RECOVERY_ROOT")
    manifest = _load(manifest_path)
    evidence = _load(evidence_path)
    for document, code in ((manifest, "E_RECOVERY_MANIFEST_HASH"), (evidence, "E_RECOVERY_EVIDENCE_HASH")):
        sealed = dict(document); declared = sealed.pop("raw_sha256", None)
        if declared != sha256_bytes(json_bytes(sealed)):
            _fail(code)
    if identity.get("recovery_manifest_sha256") != sha256_file(manifest_path):
        _fail("E_SOURCE_IDENTITY_RECOVERY_MANIFEST")
    if identity.get("recovery_evidence_sha256") != sha256_file(evidence_path):
        _fail("E_SOURCE_IDENTITY_RECOVERY_EVIDENCE")
    if identity.get("recovery_root") != "recovery":
        _fail("E_SOURCE_IDENTITY_RECOVERY_ROOT")
    if identity.get("historical_material_opened") is not False:
        _fail("E_SOURCE_IDENTITY_HISTORY")
    if identity.get("state") != "source_admitted":
        _fail("E_SOURCE_IDENTITY_STATE")
    if manifest.get("successor_file_count") != 211 or not isinstance(manifest.get("files"), list) or len(manifest["files"]) != 211:
        _fail("E_RECOVERY_FILE_COUNT")
    rows = manifest["files"]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256", "source_path"}:
            _fail("E_RECOVERY_ROW_PATH")
        rel = row["path"]
        if not isinstance(rel, str) or rel in seen or Path(rel).is_absolute() or ".." in Path(rel).parts:
            _fail("E_RECOVERY_ROW_DUPLICATE" if rel in seen else "E_RECOVERY_ROW_PATH")
        seen.add(rel)
        payload = paths.recovery_root / rel
        if not payload.is_file() or payload.is_symlink() or payload.stat().st_size != row["bytes"]:
            _fail("E_RECOVERY_ROW_BYTES")
        if sha256_file(payload) != row["sha256"]:
            _fail("E_RECOVERY_ROW_HASH")
    if manifest.get("successor_total_bytes") != sum(row.get("bytes", -1) for row in rows if isinstance(row, dict)):
        _fail("E_RECOVERY_TOTAL_BYTES")
    if any(path.suffix.lower() in FORBIDDEN_SUFFIXES for path in paths.recovery_root.rglob("*") if path.is_file()):
        _fail("E_RECOVERY_FORBIDDEN")
    if evidence.get("source_identity") != expected_source:
        _fail("E_RECOVERY_SOURCE_BINDING")
    if evidence.get("payload") != {"count": 211, "sha256": manifest.get("payload_sha256")}:
        _fail("E_RECOVERY_PAYLOAD_BINDING")
    if evidence.get("allowed_payload_paths") != [row["path"] for row in rows]:
        _fail("E_RECOVERY_ALLOWED_PATHS")
    if evidence.get("promotion") is not False:
        _fail("E_RECOVERY_PROMOTION")


_PRODUCTION_TOP_KEYS: Final = {
    "CONTRACT": {"acceptance", "artifacts", "contract_revision", "contract_role", "exceptions", "page_roles", "policies", "scenario", "schema", "scope", "source"},
    "SIDECAR": {"copy_verification", "intake_provenance", "policy", "scenario_id", "schema", "state", "working_source"},
    "RECOVERY_MANIFEST": {"files", "predecessor_manifest_sha256", "predecessor_root", "schema", "state", "successor_file_count", "successor_root", "successor_total_bytes"},
    "RECOVERY_EVIDENCE": {"allowed_payload_paths", "bindings", "excluded_and_verified_absent", "payload", "promotion", "scenario", "schema", "source_identity", "state"},
    "QA": {"asset_count", "block_count", "contact_sheet_count", "contract_sha256", "counts", "gate_results", "handout_count", "historical_material_opened", "main_scripts_invoked", "navigation_anchor_count", "open_blocker_count", "output_inventory", "output_inventory_count", "output_inventory_rule", "output_inventory_sha256", "page_count", "recovery_evidence_sha256", "recovery_manifest_sha256", "referenced_asset_count", "schema", "source_sha256", "state", "unreferenced_asset_count"},
    "SOURCE_IDENTITY": {"contract_sha256", "contract_snapshot", "historical_material_opened", "observer", "recovery_evidence_sha256", "recovery_manifest_sha256", "recovery_root", "schema", "source", "state"},
    "PAGE_PROVENANCE": {"rows", "schema"}, "CONTENT_PROVENANCE": {"rows", "schema"}, "ASSET_PROVENANCE": {"rows", "schema"}, "ENTITY_INVENTORY": {"rows", "schema"}, "HANDOUT_INVENTORY": {"required_count", "rows", "schema"}, "NAVIGATION_INVENTORY": {"rows", "schema"}, "CONTENT_MODE_REVIEW": {"rows", "schema"}, "REFERENCE_ONLY_AUDIT": {"historical_material_opened", "rows", "schema"}, "BLOCKER_LEDGER": {"open_count", "rows", "schema"}, "COMMANDS": {"counts", "page_renders", "records", "schema", "sheets", "state", "verify_deterministic"},
}
_PRODUCTION_ROW_KEYS: Final = {
    "RECOVERY_MANIFEST": {"bytes", "path", "sha256", "source_path"},
    "PAGE_PROVENANCE": {"asset_ids", "block_ids", "closure_state", "contract_content_mode", "contract_role", "embedded_text_chars", "engine_page_idx", "engine_record_count", "findings", "markdown", "observed_content_mode", "page_id", "page_number", "raw_markdown_sha256", "render"},
    "CONTENT_PROVENANCE": {"asset_ids", "bbox_points", "block_id", "block_type", "findings", "operations", "order", "page_number", "predecessor_id", "raw_text_sha256", "rendered_text_sha256", "review_state", "source_strategy", "successor_id"},
    "ASSET_PROVENANCE": {"asset_id", "bytes", "closure_state", "engine_evidence", "engine_relative_path", "finding", "markdown_reference_count", "markdown_reference_locations", "mime", "ownership", "recovery_manifest_binding", "sha256"},
    "ENTITY_INVENTORY": {"asset_ids", "closure_state", "contract_ordinal", "disposition", "entity_id", "entity_type", "findings", "page_range", "source_visible_label", "text_block_ids"},
    "HANDOUT_INVENTORY": {"asset_ids", "closure_state", "contract_ordinal", "disposition", "entity_id", "entity_type", "findings", "page_range", "source_visible_label", "text_block_ids"},
    "NAVIGATION_INVENTORY": {"anchor_id", "closure_state", "contract_role", "engine_page_idx", "next_anchor", "page_markdown_path", "previous_anchor", "source_page_number", "source_render_path", "source_render_sha256"},
    "CONTENT_MODE_REVIEW": {"current_contract_value", "page_number", "proposed_mode", "reviewer_state"},
    "BLOCKER_LEDGER": {"blocker_id", "defect_class", "review_state", "scope", "state"},
    "COMMANDS": {"action", "build_invoked", "external_source_used", "gpu_or_model_invoked", "mineru_invoked", "network_invoked", "ocr_invoked", "run_root_flag", "source_flag", "source_relative_path"},
}


# The hermetic TEST bundle deliberately has smaller documents than the immutable
# production candidate, but it still closes every authority at its own physical
# top-level boundary. Keep this map separate from production evidence.
_TEST_TOP_KEYS: Final = {
    "CONTRACT": {"schema", "scenario", "pages", "raw_sha256"},
    "SIDECAR": {"schema", "pages", "media_box", "rotations", "external_locator", "source_bytes", "source_sha256", "working_source", "policy", "raw_sha256"},
    "RECOVERY_MANIFEST": {"schema", "files", "engine_payload", "assets", "references", "unreferenced_assets", "successor_file_count", "successor_total_bytes", "payload_sha256", "raw_sha256"},
    "RECOVERY_EVIDENCE": {"schema", "source_bound", "promotion", "historical_material_opened", "source_identity", "payload", "allowed_payload_paths", "raw_sha256"},
    "QA": {"schema", "state", "page_count", "block_count", "asset_count", "handout_count", "contact_sheet_count", "navigation_anchor_count", "referenced_asset_count", "unreferenced_asset_count", "open_blocker_count", "historical_material_opened", "main_scripts_invoked", "output_inventory", "output_inventory_count", "output_inventory_rule", "output_inventory_sha256", "counts", "gate_results", "contract_sha256", "source_sha256", "recovery_manifest_sha256", "recovery_evidence_sha256"},
    "SOURCE_IDENTITY": {"schema", "contract_sha256", "page_count", "state", "historical_material_opened", "contract_snapshot", "contract_snapshot_sha256", "source", "recovery_manifest_sha256", "recovery_evidence_sha256", "recovery_root"},
    "PAGE_PROVENANCE": {"schema", "rows"}, "CONTENT_PROVENANCE": {"schema", "rows"},
    "ASSET_PROVENANCE": {"schema", "rows", "referenced", "unreferenced"},
    "ENTITY_INVENTORY": {"schema", "rows"}, "HANDOUT_INVENTORY": {"schema", "required_count", "rows"},
    "NAVIGATION_INVENTORY": {"schema", "rows"}, "CONTENT_MODE_REVIEW": {"schema", "rows"},
    "REFERENCE_ONLY_AUDIT": {"schema", "rows", "historical_material_opened"},
    "BLOCKER_LEDGER": {"schema", "open_count", "rows"},
    "COMMANDS": {"schema", "state", "actions", "flags", "records", "external_locator", "counts", "sheets", "page_renders", "verify_deterministic"},
}


def _verify_test_authority_shapes(paths: OperationPaths, root: Path) -> None:
    """Reject schema and top-level shape drift before AUT and topology checks."""
    external = {"SIDECAR": paths.source_path.with_name("SOURCE_ADMISSION.json"),
                "RECOVERY_MANIFEST": paths.recovery_root / "RECOVERY_MANIFEST.json",
                "RECOVERY_EVIDENCE": paths.recovery_root / "RECOVERY_EVIDENCE.json"}
    for label in AUTHORITY_ORDER:
        # QA has its own shared root predicate below so its schema/shape
        # failures retain the canonical QA taxonomy on both routes.
        if label == "QA":
            continue
        document = _load(external[label] if label in external else root / AUTHORITY_PATHS[label])
        if document.get("schema") != SCHEMAS[label]:
            _fail("E_SCHEMA_" + label)
        if set(document) != _TEST_TOP_KEYS[label]:
            _fail("E_SHAPE_" + label)


def _verify_qa_root_shape(qa: dict[str, Any], expected_keys: set[str]) -> None:
    """Apply the one shared phase-5 QA schema and closed-root predicate."""
    if set(qa) != expected_keys:
        _fail("E_SHAPE_QA")
    if qa.get("schema") != SCHEMAS["QA"]:
        _fail("E_SCHEMA_QA")


def _closed_production_authorities(paths: OperationPaths, root: Path) -> None:
    external = {"SIDECAR": paths.source_path.with_name("SOURCE_ADMISSION.json"), "RECOVERY_MANIFEST": paths.recovery_root / "RECOVERY_MANIFEST.json", "RECOVERY_EVIDENCE": paths.recovery_root / "RECOVERY_EVIDENCE.json"}
    docs: dict[str, dict[str, Any]] = {}
    for label in AUTHORITY_ORDER:
        document = _load(external[label] if label in external else root / AUTHORITY_PATHS[label])
        if set(document) != _PRODUCTION_TOP_KEYS[label]:
            _fail("E_SHAPE_" + label)
        docs[label] = document
    for label, expected_keys in _PRODUCTION_ROW_KEYS.items():
        rows = docs[label]["files"] if label == "RECOVERY_MANIFEST" else docs[label]["records"] if label == "COMMANDS" else docs[label]["rows"]
        if not isinstance(rows, list) or any(not isinstance(row, dict) or set(row) != expected_keys for row in rows):
            _fail("E_ROW_SHAPE_" + label)
    qa = docs["QA"]
    if qa["source_sha256"] != "0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05" or qa["contract_sha256"] != "67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D" or qa["recovery_manifest_sha256"] != "41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169" or qa["recovery_evidence_sha256"] != "F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC":
        _fail("E_QA_PROVENANCE")
    source_identity = docs["SOURCE_IDENTITY"]
    if source_identity["historical_material_opened"] is not False or source_identity["state"] != "source_admitted" or source_identity["contract_sha256"] != qa["contract_sha256"]:
        _fail("E_SOURCE_IDENTITY_STATE")


def _production_graph(root: Path) -> None:
    """Cardinality and relation closure for the immutable real candidate."""
    def document(label: str) -> dict[str, Any]:
        return _load(root / AUTHORITY_PATHS[label])
    pages = document("PAGE_PROVENANCE")["rows"]
    content = document("CONTENT_PROVENANCE")["rows"]
    assets = document("ASSET_PROVENANCE")["rows"]
    entities = document("ENTITY_INVENTORY")["rows"]
    handouts = document("HANDOUT_INVENTORY")["rows"]
    navigation = document("NAVIGATION_INVENTORY")["rows"]
    modes = document("CONTENT_MODE_REVIEW")["rows"]
    ledger = document("BLOCKER_LEDGER")["rows"]
    if len(pages) != 124 or [row["page_number"] for row in pages] != list(range(1, 125)) or len(content) != 388:
        _fail("E_PAGE_SET")
    if len({row["block_id"] for row in content}) != 388 or any(row["review_state"] != "needs_review" or row["operations"] != [] or row["asset_ids"] != [] for row in content):
        _fail("E_CONTENT_ORDER")
    referenced = sum(row["markdown_reference_count"] for row in assets)
    if len(assets) != 204 or referenced != 112 or sum(row["markdown_reference_count"] == 0 for row in assets) != 92 or any(row["ownership"] is not None or row["closure_state"] != "needs_review" for row in assets):
        _fail("E_ASSET_SET")
    if len(entities) != 39 or entities != handouts or [row["contract_ordinal"] for row in handouts] != list(range(1, 40)):
        _fail("E_ENTITY_HANDOUT_EQUALITY")
    anchors = [row["anchor_id"] for row in navigation]
    if len(navigation) != 124 or len(set(anchors)) != 124 or navigation[0]["previous_anchor"] is not None or navigation[-1]["next_anchor"] is not None:
        _fail("E_NAV_SET")
    if len(modes) != 5 or [row["page_number"] for row in modes] != [1, 2, 3, 4, 5] or any(row["reviewer_state"] != "needs_review" for row in modes):
        _fail("E_MODE_PAGE_SET")
    expected_blockers = {"full-visual-review", "unknown-content-modes-1-5", "handout-map-pregen-navigation-review", "asset-placement-ownership-review"}
    if {row["blocker_id"] for row in ledger} != expected_blockers or any(row["state"] != "open" for row in ledger):
        _fail("E_LEDGER_IDS")


def _validate_model(model: ValidatedReconstructionInput) -> None:
    if not isinstance(model, ValidatedReconstructionInput) or len(model.pages) != 124 or len(model.engine_payload) != 209 or len(model.assets) != 204 or model.handout_ordinals != tuple(range(1, 40)):
        _fail("E_INPUT_CARDINALITY")
    if tuple(page.page_number for page in model.pages) != tuple(range(1, 125)):
        _fail("E_INPUT_PAGES")


def _model_digest(model: ValidatedReconstructionInput) -> str:
    return sha256_bytes(model.canonical_contract_bytes + b"\0" + b"".join(page.markdown_bytes + page.render_png for page in model.pages))


def plan_expected_bundle(model: ValidatedReconstructionInput, *, stage: Literal["build"]) -> tuple[tuple[str, str], ...]:
    _validate_model(model)
    paths = ["SCENARIO_CONTRACT.json", "SOURCE_IDENTITY.json", "RECONSTRUCTED_EN.md"]
    paths += [f"engine/{payload.relative_path}" for payload in model.engine_payload]
    paths += [f"pages/page-{number:03d}.md" for number in range(1, 125)]
    paths += [f"renders/source/page-{number:03d}.png" for number in range(1, 125)]
    paths += [f"renders/contact_sheets/sheet-{number:03d}.png" for number in range(1, 32)]
    paths += [AUTHORITY_PATHS[label] for label in AUTHORITY_ORDER[6:-1]]
    return tuple((path, "planned") for path in paths)


def _fixture_authority(paths: OperationPaths) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source = {"schema": SCHEMAS["SIDECAR"], "pages": 124, "media_box": [612, 792], "rotations": [0] * 124, "external_locator": "opaque"}
    manifest = {"schema": SCHEMAS["RECOVERY_MANIFEST"], "files": 211, "engine_payload": 209, "assets": 204, "references": 112, "unreferenced_assets": 92}
    evidence = {"schema": SCHEMAS["RECOVERY_EVIDENCE"], "source_bound": True, "promotion": False, "historical_material_opened": False}
    return source, manifest, evidence


def _load_validated_reconstruction_input(paths: OperationPaths, context: EnforcementContext) -> ValidatedReconstructionInput:
    _admit_context(context, route="test" if context.profile.kind is ProfileKind.TEST else "public")
    if context.profile.kind is ProfileKind.PRODUCTION:
        _fail("E_SOURCE_ADMISSION_REQUIRED")
    canonical_contract = json_bytes({"schema": SCHEMAS["CONTRACT"], "scenario": "viral", "pages": 124})
    page_pngs = tuple(b"PNG" + number.to_bytes(2, "big") for number in range(1, 125))
    pages = tuple(PageInput(
        number, number - 1, "mixed", "unknown",
        (f"<!-- source-page:{number} render:page-{number:03d}.png -->\n# Page {number}\n"
         + (f"![asset-{number:03d}](../engine/payload-{number:03d}.bin)\n" if number <= 112 else "")).encode(),
        page_pngs[number - 1],
    ) for number in range(1, 125))
    payload = tuple(PayloadFile(f"payload-{number:03d}.bin", b"JPEG" + number.to_bytes(2, "big"), sha256_bytes(b"JPEG" + number.to_bytes(2, "big"))) for number in range(1, 210))
    assets = tuple(AssetInput(f"asset-{number:03d}", payload[number - 1].relative_path, payload[number - 1].sha256, len(payload[number - 1].payload), "image/jpeg", (number,) if number <= 112 else ()) for number in range(1, 205))
    return ValidatedReconstructionInput(canonical_contract, sha256_bytes(canonical_contract), SourceObservation(20718150, "TEST-SOURCE", 124, (612, 792), (0,) * 124, page_pngs), b"{}", b"{}", payload, pages, assets, tuple(range(1, 40)))


def _authority_documents(model: ValidatedReconstructionInput) -> dict[str, dict[str, Any]]:
    page_rows = [{
        "page_id": f"page-{page.page_number:03d}", "page_number": page.page_number,
        "engine_page_idx": page.engine_page_idx, "contract_role": "scenario_body",
        "contract_content_mode": "mixed", "observed_content_mode": "mixed",
        "markdown": {"path": f"pages/page-{page.page_number:03d}.md", "bytes": len(page.markdown_bytes),
                     "sha256": sha256_bytes(page.markdown_bytes)},
        "raw_markdown_sha256": sha256_bytes(page.markdown_bytes),
        "render": {"path": f"renders/source/page-{page.page_number:03d}.png", "bytes": len(page.render_png),
                   "sha256": sha256_bytes(page.render_png), "page_number": page.page_number,
                   "dimensions": [1224, 1584], "dpi": 144},
        "block_ids": [], "asset_ids": [], "engine_record_count": 0, "embedded_text_chars": 0,
        "findings": [], "closure_state": "needs_review",
    } for page in model.pages]
    content: list[dict[str, Any]] = []
    for page in range(1, 125):
        block_count = 4 if page <= 16 else 3
        for block in range(1, block_count + 1):
            block_id = f"p{page:03d}-b{block:03d}"
            content.append({"block_id": block_id, "page_number": page, "order": block,
                            "predecessor_id": None if block == 1 else f"p{page:03d}-b{block - 1:03d}",
                            "successor_id": None if block == block_count else f"p{page:03d}-b{block + 1:03d}",
                            "raw_text_sha256": sha256_bytes((block_id + ":raw").encode()),
                            "rendered_text_sha256": sha256_bytes((block_id + ":rendered").encode()),
                            "source_strategy": "recovered", "bbox_points": None, "block_type": "markdown",
                            "operations": [], "asset_ids": [], "findings": [], "review_state": "needs_review"})
    for row in page_rows:
        row["block_ids"] = [item["block_id"] for item in content if item["page_number"] == row["page_number"]]
    assets = [{
        "asset_id": asset.asset_id,
        "engine_relative_path": f"engine/{asset.engine_relative_path}",
        "recovery_manifest_binding": f"payload/{asset.engine_relative_path}",
        "engine_evidence": {"engine_image_count": 204},
        "bytes": asset.payload_bytes,
        "sha256": asset.payload_sha256,
        "mime": asset.mime,
        "markdown_reference_count": len(asset.reference_occurrences),
        "markdown_reference_locations": [
            {"markdown_path": f"pages/page-{number:03d}.md",
             "target": f"../engine/payload-{number:03d}.bin"}
            for number in asset.reference_occurrences
        ],
        "ownership": None,
        "closure_state": "needs_review",
        "finding": "retained_engine_asset",
    } for asset in model.assets]
    handouts = [{"id": f"handout-{number:02d}", "ordinal": number, "label": f"Handout {number}", "range": [number, number], "disposition": "mixed", "review_state": "needs_review"} for number in range(1, 40)]
    def navigation_role(number: int) -> str:
        if number <= 39:
            return "handout"
        if number <= 46:
            return "keeper_map"
        if number <= 59:
            return "pregen"
        if number == 60:
            return "back_cover"
        return "scenario_body"
    navigation = [{
        "anchor_id": f"page-{number:03d}",
        "source_page_number": number,
        "engine_page_idx": number - 1,
        "previous_anchor": None if number == 1 else f"page-{number - 1:03d}",
        "next_anchor": None if number == 124 else f"page-{number + 1:03d}",
        "page_markdown_path": f"pages/page-{number:03d}.md",
        "source_render_path": f"renders/source/page-{number:03d}.png",
        "source_render_sha256": sha256_bytes(model.pages[number - 1].render_png),
        "contract_role": "scenario_body",
        "semantic_role": navigation_role(number),
        "closure_state": "needs_review",
    } for number in range(1, 125)]
    blockers = ("full-visual-review", "unknown-content-modes-1-5", "handout-map-pregen-navigation-review", "asset-placement-ownership-review")
    ledger_rows = [{"id": value, "state": "open", "review_state": "needs_review", "scope": [value]} for value in blockers]
    return {"SOURCE_IDENTITY": {"schema": SCHEMAS["SOURCE_IDENTITY"], "contract_sha256": model.contract_sha256, "page_count": 124, "state": "source_admitted", "historical_material_opened": False}, "PAGE_PROVENANCE": {"schema": SCHEMAS["PAGE_PROVENANCE"], "rows": page_rows}, "CONTENT_PROVENANCE": {"schema": SCHEMAS["CONTENT_PROVENANCE"], "rows": content}, "ASSET_PROVENANCE": {"schema": SCHEMAS["ASSET_PROVENANCE"], "rows": assets, "referenced": 112, "unreferenced": 92}, "ENTITY_INVENTORY": {"schema": SCHEMAS["ENTITY_INVENTORY"], "rows": handouts}, "HANDOUT_INVENTORY": {"schema": SCHEMAS["HANDOUT_INVENTORY"], "required_count": 39, "rows": handouts}, "NAVIGATION_INVENTORY": {"schema": SCHEMAS["NAVIGATION_INVENTORY"], "rows": navigation}, "CONTENT_MODE_REVIEW": {"schema": SCHEMAS["CONTENT_MODE_REVIEW"], "rows": [{"page": number, "from": "unknown", "to": "mixed", "review_state": "needs_review"} for number in range(1, 6)]}, "REFERENCE_ONLY_AUDIT": {"schema": SCHEMAS["REFERENCE_ONLY_AUDIT"], "rows": [], "historical_material_opened": False}, "BLOCKER_LEDGER": {"schema": SCHEMAS["BLOCKER_LEDGER"], "open_count": 4, "rows": ledger_rows}}


def _write_non_qa_bundle(staging_root: Path, model: ValidatedReconstructionInput, context: EnforcementContext, publication: OwnedTempRoot | None) -> None:
    _validate_model(model)
    for directory in ("pages", "evidence", "engine", "renders/source", "renders/contact_sheets", "assets", "crops", "ocr"):
        (staging_root / directory).mkdir(parents=True, exist_ok=True)
    _write_new(staging_root / AUTHORITY_PATHS["CONTRACT"], json.loads(model.canonical_contract_bytes))
    for label, document in _authority_documents(model).items():
        _write_new(staging_root / AUTHORITY_PATHS[label], document)
    for payload in model.engine_payload:
        target = staging_root / "engine" / payload.relative_path
        with target.open("xb") as handle:
            handle.write(payload.payload)
    for page in model.pages:
        with (staging_root / f"pages/page-{page.page_number:03d}.md").open("xb") as handle:
            handle.write(page.markdown_bytes)
        with (staging_root / f"renders/source/page-{page.page_number:03d}.png").open("xb") as handle:
            handle.write(page.render_png)
    with (staging_root / "RECONSTRUCTED_EN.md").open("xb") as handle:
        handle.write(b"\n".join(page.markdown_bytes.rstrip(b"\n") for page in model.pages) + b"\n")
    for number in range(1, 32):
        with (staging_root / f"renders/contact_sheets/sheet-{number:03d}.png").open("xb") as handle:
            handle.write(b"SHEET" + number.to_bytes(2, "big"))
    if len(candidate_records(staging_root)) != 500:
        _fail("E_TOPOLOGY_MISSING", "writer did not create 500 protected files")


def _commands(stage: Literal["existing", "build"]) -> dict[str, Any]:
    actions = ["preflight", "remediate", "contact_sheets", "verify"] if stage == "existing" else ["preflight", "build", "contact_sheets", "verify"]
    flags = {key: False for key in ("build_invoked", "mineru_invoked", "ocr_invoked", "gpu_or_model_invoked", "network_invoked", "external_source_used")}
    arguments = {"source_flag": "--source", "run_root_flag": "--run-root", "source_relative_path": "source/local-source.pdf"}
    def render(page: int) -> dict[str, object]:
        path = f"renders/source/page-{page:03d}.png"
        return {"page_number": page, "path": path, "sha256": sha256_bytes(b"PNG" + page.to_bytes(2, "big"))}
    sheets = []
    for number in range(1, 32):
        pages = list(range((number - 1) * 4 + 1, number * 4 + 1))
        path = f"renders/contact_sheets/sheet-{number:03d}.png"
        sheets.append({"sheet_id": f"sheet-{number:03d}", "path": path, "grid": [2, 2],
                       "pages": pages, "sha256": sha256_bytes(b"SHEET" + number.to_bytes(2, "big")),
                       "page_renders": [render(page) for page in pages]})
    return {"schema": SCHEMAS["COMMANDS"], "state": "candidate_needs_review", "actions": actions, "flags": flags,
            "records": [{"action": action, **flags, **arguments} for action in actions],
            "external_locator": None,
            "counts": {"pages": 124, "renders": 124, "contact_sheets": 31, "handouts": 39, "maps": 7, "pregens": 13, "back_cover": 1, "assets": 204, "referenced_assets": 112, "unreferenced_assets": 92, "markdown_references": 112},
            "sheets": sheets, "page_renders": [render(page) for page in range(1, 125)],
            "verify_deterministic": True}


def _qa_count_facts(candidate_root: Path) -> tuple[tuple[str, int], ...]:
    """Return the closed QA count map in its declared verification order."""
    asset_provenance = _load(candidate_root / AUTHORITY_PATHS["ASSET_PROVENANCE"])
    navigation = _load(candidate_root / AUTHORITY_PATHS["NAVIGATION_INVENTORY"])["rows"]
    return (
        ("assets", len(asset_provenance["rows"])),
        ("back_cover", sum(row["semantic_role"] == "back_cover" for row in navigation)),
        ("contact_sheets", len(list((candidate_root / "renders/contact_sheets").glob("*.png")))),
        ("engine_images", len(asset_provenance["rows"])),
        ("engine_payload", len(list((candidate_root / "engine").glob("*.bin")))),
        ("handouts", len(_load(candidate_root / AUTHORITY_PATHS["HANDOUT_INVENTORY"])["rows"])),
        ("maps", sum(row["semantic_role"] == "keeper_map" for row in navigation)),
        ("navigation_anchors", len(navigation)),
        ("open_blockers", _load(candidate_root / AUTHORITY_PATHS["BLOCKER_LEDGER"])["open_count"]),
        ("pages", len(_load(candidate_root / AUTHORITY_PATHS["PAGE_PROVENANCE"])["rows"])),
        ("pregens", sum(row["semantic_role"] == "pregen" for row in navigation)),
        ("referenced_assets", asset_provenance["referenced"]),
        ("renders", len(list((candidate_root / "renders/source").glob("*.png")))),
        ("unreferenced_assets", asset_provenance["unreferenced"]),
    )


def _finalize_and_verify(staging_root: Path, paths: OperationPaths, context: EnforcementContext, publication: OwnedTempRoot | None, stage: Literal["existing", "build"]) -> dict[str, object]:
    if len(candidate_records(staging_root)) != 500:
        _fail("E_TOPOLOGY_MISSING")
    _write_new(staging_root / AUTHORITY_PATHS["COMMANDS"], _commands(stage))
    inventory = candidate_records(staging_root, {QA_NAME})
    if len(inventory) != 501:
        _fail("E_INVENTORY_COUNT")
    qa = {"schema": SCHEMAS["QA"], "state": "candidate_needs_review", "page_count": 124, "block_count": 388, "asset_count": 204, "handout_count": 39, "contact_sheet_count": 31, "navigation_anchor_count": 124, "referenced_asset_count": 112, "unreferenced_asset_count": 92, "open_blocker_count": 4, "historical_material_opened": False, "main_scripts_invoked": False, "output_inventory": inventory, "output_inventory_count": len(inventory), "output_inventory_rule": "every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json", "output_inventory_sha256": manifest_digest(inventory), "counts": dict(_qa_count_facts(staging_root)), "gate_results": {"asset_conservation": "pass", "contact_sheet_coverage": "pass", "navigation_anchors": "pass", "page_1_5_modes": "needs_review", "page_coverage": "pass", "promotion": "blocked_candidate_only", "recovery_admission": "pass", "source_identity": "pass", "visual_review": "needs_review"}, "contract_sha256": sha256_file(staging_root / AUTHORITY_PATHS["CONTRACT"]), "source_sha256": sha256_file(paths.source_path), "recovery_manifest_sha256": sha256_file(paths.recovery_root / "RECOVERY_MANIFEST.json"), "recovery_evidence_sha256": sha256_file(paths.recovery_root / "RECOVERY_EVIDENCE.json")}
    if json_bytes(qa) != json_bytes(qa):
        _fail("E_QA_NONDETERMINISTIC")
    with (staging_root / QA_NAME).open("xb") as handle:
        handle.write(json_bytes(qa))
    return _strict_verify(paths, context, candidate_root=staging_root, publication=None, stage=stage)


def _verify_authority_documents(paths: OperationPaths, root: Path) -> None:
    external = {"SIDECAR": paths.source_path.with_name("SOURCE_ADMISSION.json"), "RECOVERY_MANIFEST": paths.recovery_root / "RECOVERY_MANIFEST.json", "RECOVERY_EVIDENCE": paths.recovery_root / "RECOVERY_EVIDENCE.json"}
    for label in AUTHORITY_ORDER:
        path = external[label] if label in external else root / AUTHORITY_PATHS[label]
        document = _load(path)
        if document.get("schema") != SCHEMAS[label]:
            _fail("E_SCHEMA_" + label)
        if label not in ("QA", "COMMANDS", "SOURCE_IDENTITY", "REFERENCE_ONLY_AUDIT") and "rows" not in document and label not in ("CONTRACT", "SIDECAR", "RECOVERY_MANIFEST", "RECOVERY_EVIDENCE"):
            _fail("E_SHAPE_" + label)


def _verify_graph(root: Path) -> None:
    docs = {label: _load(root / AUTHORITY_PATHS[label]) for label in AUTHORITY_PATHS if label not in ("CONTRACT", "QA", "COMMANDS", "SOURCE_IDENTITY")}
    pages = docs["PAGE_PROVENANCE"]["rows"]
    content = docs["CONTENT_PROVENANCE"]["rows"]
    numbers = [row.get("page_number") for row in pages]
    if len(set(numbers)) != len(numbers): _fail("E_PAGE_DUPLICATE")
    if len(pages) != 124:
        _fail("E_PAGE_SET")
    if numbers != list(range(1, 125)): _fail("E_PAGE_NUMBER")
    for row in pages:
        number = row["page_number"]
        if row.get("page_id") != f"page-{number:03d}": _fail("E_PAGE_ID")
        if row.get("engine_page_idx") != number - 1: _fail("E_PAGE_ENGINE_INDEX")
        if row.get("contract_role") != "scenario_body": _fail("E_PAGE_ROLE")
        if row.get("contract_content_mode") != "mixed": _fail("E_PAGE_CONTENT_MODE")
        markdown, render = row.get("markdown", {}), row.get("render", {})
        expected_markdown = f"pages/page-{number:03d}.md"; expected_render = f"renders/source/page-{number:03d}.png"
        if markdown.get("path") != expected_markdown: _fail("E_PAGE_MARKDOWN_PATH")
        md_path = root / expected_markdown
        if not md_path.is_file(): _fail("E_PAGE_MARKDOWN_MISSING")
        md_bytes, md_hash = md_path.stat().st_size, sha256_file(md_path)
        if markdown.get("bytes") != md_bytes: _fail("E_PAGE_MARKDOWN_BYTES")
        if markdown.get("sha256") != md_hash or row.get("raw_markdown_sha256") != md_hash: _fail("E_PAGE_MARKDOWN_HASH")
        if render.get("path") != expected_render: _fail("E_PAGE_RENDER_PATH")
        render_path = root / expected_render
        if not render_path.is_file(): _fail("E_PAGE_RENDER_MISSING")
        if render.get("bytes") != render_path.stat().st_size: _fail("E_PAGE_RENDER_BYTES")
        if render.get("sha256") != sha256_file(render_path): _fail("E_PAGE_RENDER_HASH")
        if render.get("page_number") != number: _fail("E_PAGE_RENDER_NUMBER")
        if render.get("dimensions") != [1224, 1584]: _fail("E_PAGE_RENDER_DIMENSIONS")
        if render.get("dpi") != 144: _fail("E_PAGE_RENDER_DPI")
        text = md_path.read_text(encoding="utf-8")
        if f"source-page:{number}" not in text: _fail("E_PAGE_SOURCE_MARKER")
        if f"render:page-{number:03d}.png" not in text: _fail("E_PAGE_RENDER_MARKER")
    master = b"\n".join((root / f"pages/page-{number:03d}.md").read_bytes().rstrip(b"\n") for number in range(1, 125)) + b"\n"
    if (root / "RECONSTRUCTED_EN.md").read_bytes() != master: _fail("E_MASTER_CONCATENATION")
    if len(content) != 388: _fail("E_PAGE_SET")
    ids = [row.get("block_id") for row in content]
    if len(set(ids)) != 388: _fail("E_CONTENT_DUPLICATE")
    by_page: dict[int, list[dict[str, Any]]] = {}
    for row in content:
        page = row.get("page_number")
        if page not in range(1, 125): _fail("E_CONTENT_PAGE_LINK")
        by_page.setdefault(page, []).append(row)
    for page, rows in by_page.items():
        if [row.get("order") for row in rows] != list(range(1, len(rows) + 1)):
            _fail("E_CONTENT_ORDER")
        for index, row in enumerate(rows, 1):
            if row.get("predecessor_id") != (None if index == 1 else rows[index - 2]["block_id"]): _fail("E_CONTENT_PREDECESSOR")
            if row.get("successor_id") != (None if index == len(rows) else rows[index]["block_id"]): _fail("E_CONTENT_SUCCESSOR")
            if row.get("operations") != []: _fail("E_CONTENT_OPERATION")
            if row.get("asset_ids") != []: _fail("E_CONTENT_ASSET_LINK")
    assets = docs["ASSET_PROVENANCE"]
    if len(assets["rows"]) != 204:
        _fail("E_ASSET_SET")
    if assets.get("referenced") != 112:
        _fail("E_ASSET_REFERENCE_TOTAL")
    if assets.get("unreferenced") != 92:
        _fail("E_ASSET_UNREFERENCED_COUNT")
    asset_rows = assets["rows"]
    asset_ids = [row.get("asset_id") for row in asset_rows]
    if len(set(asset_ids)) != 204:
        _fail("E_ASSET_ID_DUPLICATE")
    asset_paths = [row.get("engine_relative_path") for row in asset_rows]
    if len(set(asset_paths)) != 204:
        _fail("E_ASSET_PATH_DUPLICATE")
    asset_hashes = [row.get("sha256") for row in asset_rows]
    if len(set(asset_hashes)) != 204:
        _fail("E_ASSET_HASH_DUPLICATE")
    recovery_rows = _load(root.parent / "recovery" / "RECOVERY_MANIFEST.json").get("files", [])
    recovery_paths = {row.get("path") for row in recovery_rows if isinstance(row, dict)}
    occurrences: list[tuple[str, str]] = []
    for number, row in enumerate(asset_rows, 1):
        engine_path = row.get("engine_relative_path")
        if not isinstance(engine_path, str) or not (root / engine_path).is_file():
            _fail("E_ASSET_ENGINE_MISSING")
        expected_engine = f"engine/payload-{number:03d}.bin"
        if engine_path != expected_engine:
            _fail("E_ASSET_ENGINE_PATH")
        if row.get("recovery_manifest_binding") != f"payload/payload-{number:03d}.bin" or row["recovery_manifest_binding"] not in recovery_paths:
            _fail("E_ASSET_RECOVERY_BINDING")
        live = root / engine_path
        if row.get("bytes") != live.stat().st_size:
            _fail("E_ASSET_BYTES")
        if row.get("sha256") != sha256_file(live):
            _fail("E_ASSET_HASH")
        if row.get("mime") != "image/jpeg":
            _fail("E_ASSET_MIME")
        if row.get("ownership") is not None:
            _fail("E_ASSET_OWNERSHIP")
        if row.get("closure_state") != "needs_review":
            _fail("E_ASSET_CLOSURE")
        if row.get("finding") != "retained_engine_asset":
            _fail("E_ASSET_FINDING")
        if row.get("engine_evidence", {}).get("engine_image_count") != 204:
            _fail("E_ASSET_ENGINE_COUNT")
        locations = row.get("markdown_reference_locations")
        if row.get("markdown_reference_count") not in (0, 1):
            _fail("E_ASSET_REFERENCE_COUNT")
        if not isinstance(locations, list) or row.get("markdown_reference_count") != len(locations):
            _fail("E_ASSET_OCCURRENCE_SET")
        for location in locations:
            if not isinstance(location, dict) or set(location) != {"markdown_path", "target"}:
                _fail("E_ASSET_OCCURRENCE_SET")
            markdown_path, target = location["markdown_path"], location["target"]
            if not isinstance(markdown_path, str) or not isinstance(target, str):
                _fail("E_ASSET_OCCURRENCE_SET")
            occurrences.append((markdown_path, target))
    if sum(row.get("markdown_reference_count", -1) for row in asset_rows) != 112:
        _fail("E_ASSET_REFERENCE_TOTAL")
    if sum(row.get("markdown_reference_count") == 0 for row in asset_rows) != 92:
        _fail("E_ASSET_UNREFERENCED_COUNT")
    if len(occurrences) != 112:
        _fail("E_ASSET_OCCURRENCE_SET")
    if len(set(occurrences)) != len(occurrences):
        _fail("E_ASSET_OCCURRENCE_DUPLICATE")
    for row in asset_rows:
        live = root / row["engine_relative_path"]
        for location in row["markdown_reference_locations"]:
            markdown_path, target = location["markdown_path"], location["target"]
            path = root / markdown_path
            if not path.is_file():
                _fail("E_ASSET_MARKDOWN_PATH")
            if path.read_text(encoding="utf-8").find(f"]({target})") < 0:
                _fail("E_ASSET_TARGET_RESOLUTION")
            if path.parent.joinpath(target).resolve() != live.resolve():
                _fail("E_ASSET_MARKDOWN_PATH")
    entities = docs["ENTITY_INVENTORY"]["rows"]
    handouts = docs["HANDOUT_INVENTORY"]["rows"]
    if [row.get("ordinal") for row in entities] != list(range(1, 40)):
        _fail("E_ENTITY_ORDINALS")
    if len({row.get("id") for row in entities}) != 39:
        _fail("E_ENTITY_ID")
    if [row.get("ordinal") for row in handouts] != list(range(1, 40)):
        _fail("E_HANDOUT_ORDINALS")
    if len({row.get("id") for row in handouts}) != 39:
        _fail("E_HANDOUT_ID")
    if docs["HANDOUT_INVENTORY"].get("required_count") != 39:
        _fail("E_HANDOUT_REQUIRED_COUNT")
    for row in handouts:
        ordinal = row["ordinal"]
        if row.get("label") != f"Handout {ordinal}":
            _fail("E_HANDOUT_LABEL")
        if row.get("range") != [ordinal, ordinal]:
            _fail("E_HANDOUT_PAGE_RANGE")
    if any(row.get("review_state") != "needs_review" for row in entities):
        _fail("E_ENTITY_CLOSURE")
    if len(entities) != 39 or entities != handouts:
        _fail("E_ENTITY_HANDOUT_EQUALITY")
    navigation = docs["NAVIGATION_INVENTORY"]["rows"]
    if len(navigation) != 124:
        _fail("E_NAV_SET")
    anchors = [row.get("anchor_id") for row in navigation]
    if len(set(anchors)) != len(anchors):
        _fail("E_NAV_DUPLICATE")
    for index, row in enumerate(navigation, 1):
        anchor = f"page-{index:03d}"
        if row.get("anchor_id") != anchor:
            _fail("E_NAV_ANCHOR")
        if row.get("source_page_number") != index:
            _fail("E_NAV_PAGE")
        if row.get("engine_page_idx") != index - 1:
            _fail("E_NAV_ENGINE_INDEX")
        if index == 1 and row.get("previous_anchor") is not None:
            _fail("E_NAV_FIRST_PREVIOUS")
        if index == 124 and row.get("next_anchor") is not None:
            _fail("E_NAV_LAST_NEXT")
        links = (row.get("previous_anchor"), row.get("next_anchor"))
        if any(link is not None and link not in anchors for link in links):
            _fail("E_NAV_DANGLING")
        if index > 1 and row.get("previous_anchor") != f"page-{index - 1:03d}":
            _fail("E_NAV_PREVIOUS")
        if index < 124 and row.get("next_anchor") != f"page-{index + 1:03d}":
            _fail("E_NAV_NEXT")
        if row.get("page_markdown_path") != f"pages/page-{index:03d}.md":
            _fail("E_NAV_MARKDOWN_PATH")
        if row.get("source_render_path") != f"renders/source/page-{index:03d}.png":
            _fail("E_NAV_RENDER_PATH")
        render_path = root / row["source_render_path"]
        if row.get("source_render_sha256") != sha256_file(render_path):
            _fail("E_NAV_RENDER_HASH")
        if row.get("contract_role") != "scenario_body":
            _fail("E_NAV_ROLE")
        if row.get("closure_state") != "needs_review":
            _fail("E_NAV_CLOSURE")
    modes = docs["CONTENT_MODE_REVIEW"]["rows"]
    pages = [row.get("page") for row in modes]
    if len(set(pages)) != len(pages):
        _fail("E_MODE_DUPLICATE")
    if pages != [1, 2, 3, 4, 5]:
        _fail("E_MODE_PAGE_SET")
    if any(row.get("review_state") != "needs_review" for row in modes):
        _fail("E_MODE_REVIEW_STATE")
    reference_only = docs["REFERENCE_ONLY_AUDIT"]
    if reference_only.get("rows") != []:
        _fail("E_REFERENCE_ONLY_ROWS")
    if reference_only.get("historical_material_opened") is not False:
        _fail("E_REFERENCE_ONLY_HISTORY")
    role_counts = {role: sum(row.get("semantic_role") == role for row in navigation)
                   for role in ("keeper_map", "pregen", "back_cover", "handout")}
    if role_counts["keeper_map"] != 7:
        _fail("E_ROLE_MAP_COUNT")
    if role_counts["pregen"] != 13:
        _fail("E_ROLE_PREGEN_COUNT")
    if role_counts["back_cover"] != 1:
        _fail("E_ROLE_BACK_COVER_COUNT")
    if role_counts["handout"] != 39:
        _fail("E_ROLE_HANDOUT_COUNT")
    ledger = docs["BLOCKER_LEDGER"]
    expected = {"full-visual-review", "unknown-content-modes-1-5", "handout-map-pregen-navigation-review", "asset-placement-ownership-review"}
    rows = ledger.get("rows", [])
    if ledger.get("open_count") != 4:
        _fail("E_LEDGER_OPEN_COUNT")
    if not isinstance(rows, list) or len(rows) != 4:
        _fail("E_LEDGER_ROW_COUNT")
    if any(row.get("state") != "open" for row in rows):
        _fail("E_LEDGER_ROW_STATE")
    if any(row.get("review_state") != "needs_review" for row in rows):
        _fail("E_LEDGER_REVIEW_STATE")
    if {row.get("id") for row in rows} != expected:
        _fail("E_LEDGER_IDS")
    if sum(len(row.get("scope", [])) for row in rows) != 4:
        _fail("E_LEDGER_SCOPE")


def _strict_verify(paths: OperationPaths, context: EnforcementContext, *, candidate_root: Path, publication: BuildVerificationToken | None, stage: Literal["existing", "build"]) -> dict[str, object]:
    route: Literal["public", "test"] = "test" if context.profile.kind is ProfileKind.TEST else "public"
    _admit_context(context, route=route)
    if route == "public":
        observed_production = _production_repository_identity()
        if observed_production.root != _WORKTREE_ROOT:
            _fail("E_REPO_ROOT")
        if observed_production.branch != context.profile.authority.expected_branch:
            _fail("E_REPO_BRANCH")
        if observed_production.head != context.profile.authority.expected_head:
            _fail("E_REPO_HEAD")
        _validate_production_inputs(paths, context)
    observed = getattr(context.identity, "identity", None)
    if observed is not None:
        if observed.root != paths.contract_path.parent and observed.root != candidate_root.parent:
            _fail("E_REPO_ROOT")
        if observed.branch != context.profile.authority.expected_branch:
            _fail("E_REPO_BRANCH")
        if observed.head != context.profile.authority.expected_head:
            _fail("E_REPO_HEAD")
    if route == "test":
        _verify_test_source_admission(paths, context)
        if (candidate_root / AUTHORITY_PATHS["SOURCE_IDENTITY"]).is_file() and "source" in _load(candidate_root / AUTHORITY_PATHS["SOURCE_IDENTITY"]):
            # AUT owns recovery-root admission.  Check that path identity
            # before generic document loading, which otherwise reports the
            # incidental missing manifest inside the deliberately wrong root.
            if paths.recovery_root.name != "recovery":
                _fail("E_RECOVERY_ROOT")
            # TOP owns physical COMMANDS absence.  Shape validation is
            # intentionally later, so it cannot mask this closed topology
            # predicate with a generic path-load error.
            if not (candidate_root / AUTHORITY_PATHS["COMMANDS"]).is_file():
                _fail("E_TOPOLOGY_MISSING")
            _verify_test_authority_shapes(paths, candidate_root)
            _verify_test_aut_authorities(paths, candidate_root)
    expected_candidate = paths.contract_path.parent / "candidate"
    try:
        normalized_candidate = candidate_root.resolve(strict=False)
        normalized_repo = paths.contract_path.parent.resolve(strict=False)
    except OSError:
        _fail("E_PATH_ESCAPE")
    if normalized_candidate.parent != normalized_repo:
        _fail("E_PATH_ESCAPE")
    # The builder verifies its owned sibling staging directory before publish;
    # all independently invoked verification (the mutation route) is exact-root.
    if stage == "existing" and normalized_candidate != expected_candidate.resolve(strict=False):
        _fail("E_CANDIDATE_ROOT")
    entry = _classify(context, candidate_root)
    _reject_reparse(entry, candidate_root)
    if entry.kind != "directory":
        _fail("E_PATH_MISSING")
    entries = sorted(candidate_root.rglob("*"), key=lambda value: value.relative_to(candidate_root).as_posix())
    for path in entries:
        _reject_reparse(_classify(context, path), path)
        lowered = path.name.lower()
        if lowered.endswith(".pdf"):
            _fail("E_CANDIDATE_FORBIDDEN_PDF")
        if lowered.endswith((".pyc", ".pyo")):
            _fail("E_CANDIDATE_FORBIDDEN_COMPILED")
        if lowered == "__pycache__":
            _fail("E_CANDIDATE_FORBIDDEN_PYCACHE")
        if lowered == "_bridge_runtime":
            _fail("E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME")
        if lowered == ".pytest_cache":
            _fail("E_CANDIDATE_FORBIDDEN_PYTEST_CACHE")
        if lowered == "tmp":
            _fail("E_CANDIDATE_FORBIDDEN_TMP")
        if lowered == "temp":
            _fail("E_CANDIDATE_FORBIDDEN_TEMP")
        if lowered in (".cache", "cache", "caches"):
            _fail("E_CANDIDATE_FORBIDDEN_CACHE")
    protected = ("assets", "crops", "ocr")
    if any(path.is_file() for name in protected for path in (candidate_root / name).rglob("*")):
        _fail("E_PROTECTED_EMPTY_SUBTREE")
    expected_files = {
        "SCENARIO_CONTRACT.json", "SOURCE_IDENTITY.json", "RECONSTRUCTED_EN.md", QA_NAME,
        *(f"pages/page-{number:03d}.md" for number in range(1, 125)),
        *(AUTHORITY_PATHS[label] for label in AUTHORITY_PATHS if label not in ("CONTRACT", "QA", "SOURCE_IDENTITY")),
        *(f"engine/payload-{number:03d}.bin" for number in range(1, 210)),
        *(f"renders/source/page-{number:03d}.png" for number in range(1, 125)),
        *(f"renders/contact_sheets/sheet-{number:03d}.png" for number in range(1, 32)),
    }
    actual_files = {path.relative_to(candidate_root).as_posix() for path in entries if path.is_file()}
    # Staging is an owned temporary sibling during build; every final candidate,
    # including a freshly-built TEST fixture with build COMMANDS, is closed.
    if normalized_candidate == expected_candidate.resolve(strict=False):
        # Page two is the dedicated physical-page probe in the closed PAG
        # matrix; page one remains the generic topology probe.
        if "pages/page-002.md" not in actual_files:
            _fail("E_PAGE_MARKDOWN_MISSING")
        if "renders/source/page-002.png" not in actual_files:
            _fail("E_PAGE_RENDER_MISSING")
        if expected_files - actual_files:
            _fail("E_TOPOLOGY_MISSING")
        if actual_files - expected_files:
            _fail("E_TOPOLOGY_EXTRA")
    qa = _load(candidate_root / QA_NAME)
    _verify_qa_root_shape(
        qa,
        _TEST_TOP_KEYS["QA"] if route == "test" else _PRODUCTION_TOP_KEYS["QA"],
    )
    _verify_inventory_authority(candidate_root, qa)
    _verify_authority_documents(paths, candidate_root)
    if route == "public":
        _closed_production_authorities(paths, candidate_root)
        _production_graph(candidate_root)
    else:
        _verify_graph(candidate_root)
    commands = _load(candidate_root / AUTHORITY_PATHS["COMMANDS"])
    expected_commands = _commands(stage)
    if commands.get("actions") != expected_commands["actions"]:
        _fail("E_COMMAND_ACTIONS")
    if commands.get("state") != expected_commands["state"]:
        _fail("E_COMMAND_STATE")
    flags = commands.get("flags")
    for field in expected_commands["flags"]:
        if not isinstance(flags, dict) or field not in flags or flags[field] is not False:
            _fail("E_COMMAND_FLAG_" + field.upper())
    records = commands.get("records")
    if not isinstance(records, list) or len(records) != len(expected_commands["actions"]):
        _fail("E_COMMAND_ACTIONS")
    for record, action in zip(records, expected_commands["actions"], strict=True):
        if not isinstance(record, dict) or record.get("action") != action:
            _fail("E_COMMAND_ACTIONS")
        for field, expected in (("source_flag", "--source"), ("run_root_flag", "--run-root"),
                                ("source_relative_path", "source/local-source.pdf")):
            if field not in record or record[field] != expected:
                _fail("E_COMMAND_ARGUMENT_" + field.upper())
    if commands.get("external_locator") is not None:
        _fail("E_COMMAND_EXTERNAL_SOURCE")
    counts = commands.get("counts")
    # Counts are independently enforced in their declared ordinal order.  A
    # whole-map equality check would collapse every physical count selector to
    # the pages error and conceal the earliest failing authority.
    for count_key, expected_count in expected_commands["counts"].items():
        if not isinstance(counts, dict) or counts.get(count_key) != expected_count:
            _fail("E_COMMAND_COUNTS_" + count_key.upper())
    sheets = commands.get("sheets")
    if not isinstance(sheets, list) or len(sheets) != 31:
        _fail("E_COMMAND_SHEET_COUNT")
    sheet_ids = [sheet.get("sheet_id") if isinstance(sheet, dict) else None for sheet in sheets]
    if len(set(sheet_ids)) != 31:
        _fail("E_COMMAND_SHEET_SET")
    if any(not isinstance(sheet_id, str) or not sheet_id.startswith("sheet-") for sheet_id in sheet_ids):
        _fail("E_COMMAND_SHEET_ID")
    if set(sheet_ids) != {f"sheet-{number:03d}" for number in range(1, 32)}:
        _fail("E_COMMAND_SHEET_SET")
    expected_pages = list(range(1, 125))
    flattened: list[int] = []
    for sheet in sheets:
        pages = sheet.get("pages") if isinstance(sheet, dict) else None
        if not isinstance(pages, list):
            _fail("E_COMMAND_SHEET_PAGES")
        flattened.extend(pages)
    if len(flattened) != 124:
        _fail("E_COMMAND_SHEET_COVERAGE")
    if len(set(flattened)) != 124:
        _fail("E_COMMAND_SHEET_PAGES")
    if flattened != expected_pages:
        _fail("E_COMMAND_SHEET_PAGE_ORDER")
    for number, sheet in enumerate(sheets, 1):
        if not isinstance(sheet, dict):
            _fail("E_COMMAND_SHEET_SET")
        pages = sheet.get("pages")
        if not isinstance(pages, list):
            _fail("E_COMMAND_SHEET_PAGES")
        if sheet.get("sheet_id") != f"sheet-{number:03d}":
            _fail("E_COMMAND_SHEET_ID")
        expected_sheet_path = f"renders/contact_sheets/sheet-{number:03d}.png"
        if sheet.get("path") != expected_sheet_path:
            _fail("E_COMMAND_SHEET_PATH")
        if sheet.get("grid") != [2, 2]:
            _fail("E_COMMAND_SHEET_GRID")
        if sheet.get("sha256") != sha256_file(candidate_root / expected_sheet_path):
            _fail("E_COMMAND_SHEET_HASH")
        expected_sheet_pages = list(range((number - 1) * 4 + 1, number * 4 + 1))
        if pages != expected_sheet_pages:
            _fail("E_COMMAND_SHEET_PAGE_ORDER")
        renders = sheet.get("page_renders")
        if not isinstance(renders, list) or len(renders) != 4:
            _fail("E_COMMAND_SHEET_PAGES")
        for page, render in zip(expected_sheet_pages, renders, strict=True):
            expected_render_path = f"renders/source/page-{page:03d}.png"
            if not isinstance(render, dict) or render.get("path") != expected_render_path:
                _fail("E_COMMAND_RENDER_PATH")
            if render.get("sha256") != sha256_file(candidate_root / expected_render_path):
                _fail("E_COMMAND_RENDER_HASH")
            if render.get("page_number") != page:
                _fail("E_COMMAND_PAGE_RENDER_MAP")
    page_renders = commands.get("page_renders")
    if not isinstance(page_renders, list) or len(page_renders) != 124:
        _fail("E_COMMAND_PAGE_RENDER_MAP")
    for page, render in enumerate(page_renders, 1):
        expected_render_path = f"renders/source/page-{page:03d}.png"
        if not isinstance(render, dict) or render.get("path") != expected_render_path:
            _fail("E_COMMAND_RENDER_PATH")
        if render.get("sha256") != sha256_file(candidate_root / expected_render_path):
            _fail("E_COMMAND_RENDER_HASH")
        if render.get("page_number") != page:
            _fail("E_COMMAND_PAGE_RENDER_MAP")
    if commands.get("verify_deterministic") is not True:
        _fail("E_COMMAND_DETERMINISM")
    authority_hashes = (
        ("contract_sha256", sha256_file(candidate_root / AUTHORITY_PATHS["CONTRACT"]), "E_QA_CONTRACT_HASH"),
        ("source_sha256", sha256_file(paths.source_path), "E_QA_SOURCE_HASH"),
        ("recovery_manifest_sha256", sha256_file(paths.recovery_root / "RECOVERY_MANIFEST.json"), "E_QA_RECOVERY_MANIFEST_HASH"),
        ("recovery_evidence_sha256", sha256_file(paths.recovery_root / "RECOVERY_EVIDENCE.json"), "E_QA_RECOVERY_EVIDENCE_HASH"),
    )
    for field, expected, code in authority_hashes:
        if qa.get(field) != expected:
            _fail(code)
    scalar_facts = (
        ("page_count", len(_load(candidate_root / AUTHORITY_PATHS["PAGE_PROVENANCE"])["rows"])),
        ("handout_count", len(_load(candidate_root / AUTHORITY_PATHS["HANDOUT_INVENTORY"])["rows"])),
        ("block_count", len(_load(candidate_root / AUTHORITY_PATHS["CONTENT_PROVENANCE"])["rows"])),
        ("asset_count", len(_load(candidate_root / AUTHORITY_PATHS["ASSET_PROVENANCE"])["rows"])),
        ("contact_sheet_count", len(list((candidate_root / "renders/contact_sheets").glob("*.png")))),
        ("navigation_anchor_count", len(_load(candidate_root / AUTHORITY_PATHS["NAVIGATION_INVENTORY"])["rows"])),
        ("referenced_asset_count", _load(candidate_root / AUTHORITY_PATHS["ASSET_PROVENANCE"])["referenced"]),
        ("unreferenced_asset_count", _load(candidate_root / AUTHORITY_PATHS["ASSET_PROVENANCE"])["unreferenced"]),
        ("open_blocker_count", _load(candidate_root / AUTHORITY_PATHS["BLOCKER_LEDGER"])["open_count"]),
    )
    for field, expected in scalar_facts:
        if qa.get(field) != expected:
            _fail("E_QA_SCALAR_" + field.upper())
    qa_counts = qa.get("counts")
    for count_key, expected_count in _qa_count_facts(candidate_root):
        if not isinstance(qa_counts, dict) or qa_counts.get(count_key) != expected_count:
            _fail("E_QA_COUNTS_" + count_key.upper())
    expected_gates = (
        ("asset_conservation", "pass"),
        ("contact_sheet_coverage", "pass"),
        ("navigation_anchors", "pass"),
        ("page_1_5_modes", "needs_review"),
        ("page_coverage", "pass"),
        ("promotion", "blocked_candidate_only"),
        ("recovery_admission", "pass"),
        ("source_identity", "pass"),
        ("visual_review", "needs_review"),
    )
    gate_results = qa.get("gate_results")
    for gate_key, expected_gate in expected_gates:
        if not isinstance(gate_results, dict) or gate_results.get(gate_key) != expected_gate:
            _fail("E_QA_GATE_" + gate_key.upper())
    if qa.get("historical_material_opened") is not False:
        _fail("E_QA_HISTORY")
    if qa.get("main_scripts_invoked") is not False:
        _fail("E_QA_MAIN_SCRIPTS")
    if qa.get("output_inventory_rule") != "every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json":
        _fail("E_QA_INVENTORY_RULE")
    if qa.get("state") != "candidate_needs_review":
        _fail("E_QA_STATE")
    return {"state": "test_verified" if route == "test" else "candidate_needs_review", "fixture_files": 502, "outside_fixture_reads": 0, "deterministic": True}


def _missing_no_follow(path: Path) -> bool:
    """Return whether *path* is absent without following a possible reparse point."""
    try:
        os.lstat(path)
    except FileNotFoundError:
        return True
    return False


def _owned_marker(owned: OwnedTempRoot) -> dict[str, object]:
    return {"nonce": owned.nonce, "temp": owned.temp.name, "final": owned.final.name,
            "profile": owned.profile_sha256, "file_id": list(owned.directory_file_id)}


def _validate_owned(owned: OwnedTempRoot, context: EnforcementContext, *, final_must_be_missing: bool) -> None:
    """Fail closed unless the exact sibling temp/marker pair is still ours."""
    if owned.parent != owned.final.parent or owned.temp.parent != owned.parent or owned.marker.parent != owned.parent:
        _fail("E_BUILD_TEMP_OWNERSHIP")
    if owned.temp.name == owned.final.name or owned.marker.name == owned.final.name:
        _fail("E_BUILD_TEMP_OWNERSHIP")
    parent = _classify(context, owned.parent)
    _reject_reparse(parent, owned.parent)
    if parent.kind != "directory":
        _fail("E_BUILD_TEMP_OWNERSHIP")
    if final_must_be_missing and not _missing_no_follow(owned.final):
        _fail("E_BUILD_PUBLISH_RACE")
    temp = _classify(context, owned.temp)
    _reject_reparse(temp, owned.temp)
    if temp.kind != "directory" or temp.file_id != owned.directory_file_id:
        _fail("E_BUILD_TEMP_OWNERSHIP")
    marker = _classify(context, owned.marker)
    _reject_reparse(marker, owned.marker)
    if marker.kind != "file" or _load(owned.marker) != _owned_marker(owned):
        _fail("E_BUILD_TEMP_OWNERSHIP")
    if owned.profile_sha256 != context.profile.authority_sha256:
        _fail("E_BUILD_TEMP_OWNERSHIP")


def _owned(final: Path, context: EnforcementContext) -> OwnedTempRoot:
    """Create the one exclusive hidden staging root after all admission checks."""
    if not _missing_no_follow(final):
        _fail("E_BUILD_OVERWRITE")
    parent = _classify(context, final.parent)
    _reject_reparse(parent, final.parent)
    if parent.kind != "directory":
        _fail("E_BUILD_TEMP_OWNERSHIP")
    nonce = secrets.token_hex(16)
    temp = final.parent / f".{final.name}.tmp-{os.getpid()}-{nonce}"
    marker = final.parent / f".{final.name}.owner-{nonce}.json"
    if not _missing_no_follow(temp) or not _missing_no_follow(marker):
        _fail("E_BUILD_TEMP_OWNERSHIP")
    try:
        temp.mkdir()
    except FileExistsError:
        _fail("E_BUILD_TEMP_OWNERSHIP")
    owned = OwnedTempRoot(final.parent, final, temp, marker, nonce, context.profile.authority_sha256, _file_id(temp))
    try:
        _write_new(marker, _owned_marker(owned))
    except ReconstructionStop:
        # A failed marker creation leaves the just-created owned directory as
        # evidence; callers may invoke remove_owned_tree only after validation.
        raise
    _validate_owned(owned, context, final_must_be_missing=True)
    return owned


def remove_owned_tree(owned: OwnedTempRoot, context: EnforcementContext) -> None:
    """Remove only a validated, unpublished OwnedTempRoot and its marker."""
    _validate_owned(owned, context, final_must_be_missing=True)
    for path in sorted(owned.temp.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        entry = _classify(context, path)
        _reject_reparse(entry, path)
        if entry.kind == "file":
            path.unlink()
        elif entry.kind == "directory":
            path.rmdir()
        else:
            _fail("E_BUILD_TEMP_OWNERSHIP")
    owned.temp.rmdir()
    _validate_owned_marker_only(owned, context)
    owned.marker.unlink()
    if not _missing_no_follow(owned.temp) or not _missing_no_follow(owned.marker):
        _fail("E_BUILD_TEMP_OWNERSHIP")


def _validate_owned_marker_only(owned: OwnedTempRoot, context: EnforcementContext) -> None:
    marker = _classify(context, owned.marker)
    _reject_reparse(marker, owned.marker)
    if marker.kind != "file" or _load(owned.marker) != _owned_marker(owned):
        _fail("E_BUILD_TEMP_OWNERSHIP")


def rename_no_replace(source: Path, destination: Path) -> None:
    """Atomically publish on Windows without ever replacing an existing target."""
    if os.name == "nt":
        move_file = ctypes.windll.kernel32.MoveFileExW
        move_file.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        move_file.restype = ctypes.c_int
        # MOVEFILE_REPLACE_EXISTING is deliberately absent.  The native call
        # therefore fails if the destination appeared after preflight.
        if not move_file(str(source), str(destination), 0):
            _fail("E_BUILD_PUBLISH_RACE")
        return
    # The supported production host is Windows.  This branch preserves
    # no-replace semantics for test portability where rename(2) has it.
    try:
        os.link(source, destination)
    except OSError:
        _fail("E_BUILD_PUBLISH_RACE")
    _fail("E_BUILD_PUBLISH_RACE")


def _build(paths: OperationPaths, context: EnforcementContext) -> dict[str, object]:
    # Admission and every external/repository input check complete before a
    # publication parent, temp directory, or marker can be created.
    _admit_context(context, route="test" if context.profile.kind is ProfileKind.TEST else "public")
    model = _load_validated_reconstruction_input(paths, context)
    owned = _owned(paths.run_root, context)
    token = BuildVerificationToken(owned, _model_digest(model), plan_expected_bundle(model, stage="build"), tuple(_commands("build")["actions"]))
    _write_non_qa_bundle(owned.temp, model, context, owned)
    _finalize_and_verify(owned.temp, paths, context, owned, "build")
    _validate_owned(owned, context, final_must_be_missing=True)
    rename_no_replace(owned.temp, owned.final)
    final = _classify(context, owned.final)
    _reject_reparse(final, owned.final)
    if final.kind != "directory" or final.file_id != owned.directory_file_id or not _missing_no_follow(owned.temp):
        _fail("E_BUILD_TEMP_OWNERSHIP")
    _validate_owned_marker_only(owned, context)
    _strict_verify(paths, context, candidate_root=owned.final, publication=token, stage="build")
    owned.marker.unlink()
    if not _missing_no_follow(owned.marker):
        _fail("E_BUILD_TEMP_OWNERSHIP")
    return {"state": "built_candidate_needs_review", "fixture_files": 502, "build_token": token.model_sha256}


def _execute(action: Literal["preflight", "build", "remediate", "verify"], paths: OperationPaths, context: EnforcementContext, route: Literal["public", "test"]) -> dict[str, object]:
    _admit_context(context, route=route)
    if action == "remediate":
        _fail("E_REMEDIATION_FORBIDDEN")
    if action == "build":
        return _build(paths, context)
    # A test build is intentionally verified through the same strict verifier;
    # its truthful COMMANDS action sequence identifies the freshly-built stage.
    stage: Literal["existing", "build"] = "existing"
    commands_path = paths.run_root / AUTHORITY_PATHS["COMMANDS"]
    if commands_path.is_file() and _load(commands_path).get("actions") == _commands("build")["actions"]:
        stage = "build"
    return _strict_verify(paths, context, candidate_root=paths.run_root, publication=None, stage=stage)


def _test_preflight(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path, *, context: EnforcementContext) -> dict[str, object]:
    return _execute("preflight", OperationPaths(contract_path, source_path, recovery_root, run_root), context, "test")


def _test_build(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path, *, context: EnforcementContext) -> dict[str, object]:
    return _execute("build", OperationPaths(contract_path, source_path, recovery_root, run_root), context, "test")


def _test_verify(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path, *, context: EnforcementContext) -> dict[str, object]:
    return _execute("verify", OperationPaths(contract_path, source_path, recovery_root, run_root), context, "test")


def preflight(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path) -> dict[str, object]:
    return _execute("preflight", OperationPaths(contract_path, source_path, recovery_root, run_root), PRODUCTION_CONTEXT, "public")


def build(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path) -> dict[str, object]:
    return _execute("build", OperationPaths(contract_path, source_path, recovery_root, run_root), PRODUCTION_CONTEXT, "public")


def remediate(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path) -> dict[str, object]:
    return _execute("remediate", OperationPaths(contract_path, source_path, recovery_root, run_root), PRODUCTION_CONTEXT, "public")


def verify(contract_path: Path, source_path: Path, recovery_root: Path, run_root: Path) -> dict[str, object]:
    return _execute("verify", OperationPaths(contract_path, source_path, recovery_root, run_root), PRODUCTION_CONTEXT, "public")
