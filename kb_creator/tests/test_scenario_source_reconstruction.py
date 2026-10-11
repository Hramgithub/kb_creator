"""Physical selector-mutation fixtures for Viral Step 6A.

The registry is materialised at import time.  It intentionally has no counted
positive cases: a fresh production-shaped bundle is the setup of every row.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest

from kb_creator.scripts import scenario_source_reconstruction as s

FAMILY_COUNTS = {"REP": 2, "SRC": 18, "AUT": 30, "TOP": 21, "SCH": 33,
                 "LED": 6, "INV": 18, "PAG": 28, "NAV": 15, "AST": 21,
                 "SEM": 18, "CMD": 61, "QAV": 90, "REG": 2, "INJ": 5}


@dataclass(frozen=True, slots=True)
class BundleInputFixture:
    repo_root: Path; contract_path: Path; source_path: Path; sidecar_path: Path
    recovery_root: Path; final_root: Path; profile: s.EnforcementProfile; context: s.EnforcementContext


@dataclass(frozen=True, slots=True)
class BundleFixture(BundleInputFixture):
    run_root: Path; manifests: tuple[tuple[str, str], ...]


def fixture_context(root: Path) -> s.EnforcementContext:
    empty = s.FileAuthority("", 0, "", None)
    authority = s.EnforcementAuthority("fixture", "fixture", empty, empty, empty, empty, empty,
        "candidate_needs_review", ("full-visual-review", "unknown-content-modes-1-5",
        "handout-map-pregen-navigation-review", "asset-placement-ownership-review"),
        s.FORBIDDEN_SUFFIXES, s.FORBIDDEN_SEGMENTS)
    seal = s._profile_seal("strict-fixture", s.ProfileKind.TEST, authority)
    profile = s.EnforcementProfile("strict-fixture", s.ProfileKind.TEST, authority, seal)
    filesystem = s.TestFilesystemProvider(s.WindowsFilesystemProvider(seal), (), "fixture-filesystem", seal)
    return s.EnforcementContext(profile, s._Provider(seal, s.RepositoryIdentity(root, "fixture", "fixture")), filesystem)


def make_valid_input(root: Path, *, fixture_id: str) -> BundleInputFixture:
    source = root / "source" / "Call_of_Cthulhu_Viral.pdf"; source.parent.mkdir(parents=True)
    source.write_bytes(b"fixture source")
    contract_path = root / "contract.json"
    contract = {"schema": s.SCHEMAS["CONTRACT"], "scenario": "viral", "pages": 124}
    contract["raw_sha256"] = s.sha256_bytes(s.json_bytes(contract))
    contract_path.write_bytes(s.json_bytes(contract))
    recovery = root / "recovery"; recovery.mkdir(); final = root / "candidate"
    sidecar, manifest, evidence = s._fixture_authority(s.OperationPaths(root, source, recovery, final))
    sidecar.update({
        "external_locator": "",
        "source_bytes": source.stat().st_size, "source_sha256": s.sha256_file(source),
        "working_source": {"path": source.name, "bytes": source.stat().st_size,
                           "sha256": s.sha256_file(source), "page_count": 124,
                           "media_box": [612, 792], "rotations": [0] * 124},
        "policy": {"runtime_dependency": False, "external_path_allowed": False,
                   "subsequent_path": source.name, "origin": "retained_local_source"},
    })
    sidecar["raw_sha256"] = s.sha256_bytes(s.json_bytes(sidecar))
    source.with_name("SOURCE_ADMISSION.json").write_bytes(s.json_bytes(sidecar))
    rows = []
    for number in range(1, 212):
        relative = f"payload/payload-{number:03d}.bin"
        payload = f"fixture-payload-{number:03d}".encode("ascii")
        target = recovery / relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(payload)
        rows.append({"path": relative, "bytes": len(payload), "sha256": s.sha256_bytes(payload), "source_path": source.name})
    manifest.update({"files": rows, "successor_file_count": 211,
                     "successor_total_bytes": sum(row["bytes"] for row in rows),
                     "payload_sha256": s.sha256_bytes("".join(row["sha256"] for row in rows).encode("ascii"))})
    evidence.update({"source_identity": {"bytes": source.stat().st_size, "sha256": s.sha256_file(source),
                                           "page_count": 124, "media_box": [612, 792], "rotations": [0] * 124},
                     "payload": {"count": 211, "sha256": manifest["payload_sha256"]},
                     "allowed_payload_paths": [row["path"] for row in rows]})
    manifest["raw_sha256"] = s.sha256_bytes(s.json_bytes(manifest))
    evidence["raw_sha256"] = s.sha256_bytes(s.json_bytes(evidence))
    (recovery / "RECOVERY_MANIFEST.json").write_bytes(s.json_bytes(manifest))
    (recovery / "RECOVERY_EVIDENCE.json").write_bytes(s.json_bytes(evidence))
    context = fixture_context(root)
    return BundleInputFixture(root, contract_path, source, source.with_name("SOURCE_ADMISSION.json"), recovery, final, context.profile, context)


def make_valid_bundle(root: Path, *, fixture_id: str) -> BundleFixture:
    value = make_valid_input(root, fixture_id=fixture_id)
    result = s._test_build(value.contract_path, value.source_path, value.recovery_root, value.final_root, context=value.context)
    _bind_aut_baseline(value)
    first = s._test_verify(value.contract_path, value.source_path, value.recovery_root, value.final_root, context=value.context)
    second = s._test_verify(value.contract_path, value.source_path, value.recovery_root, value.final_root, context=value.context)
    assert result["fixture_files"] == first["fixture_files"] == second["fixture_files"] == 502
    records = lambda excluded: s.manifest_digest(s.candidate_records(value.final_root, excluded))
    return BundleFixture(value.repo_root, value.contract_path, value.source_path, value.sidecar_path,
        value.recovery_root, value.final_root, value.profile, value.context, value.final_root,
        ((records(set()), "502"), (records({s.QA_NAME}), "501"),
         (records({s.QA_NAME, s.AUTHORITY_PATHS["COMMANDS"]}), "500")))


def _bind_aut_baseline(value: BundleInputFixture) -> None:
    root = value.final_root
    contract = s._load(value.contract_path)
    snapshot = root / s.AUTHORITY_PATHS["CONTRACT"]
    snapshot.write_bytes(s.json_bytes(contract))
    identity_path = root / s.AUTHORITY_PATHS["SOURCE_IDENTITY"]
    identity = s._load(identity_path)
    identity.update({"contract_sha256": s.sha256_file(value.contract_path), "contract_snapshot": contract,
                     "contract_snapshot_sha256": s.sha256_file(snapshot),
                     "source": {"bytes": value.source_path.stat().st_size, "sha256": s.sha256_file(value.source_path),
                                "page_count": 124, "media_box": [612, 792], "rotations": [0] * 124},
                     "recovery_manifest_sha256": s.sha256_file(value.recovery_root / "RECOVERY_MANIFEST.json"),
                     "recovery_evidence_sha256": s.sha256_file(value.recovery_root / "RECOVERY_EVIDENCE.json"),
                     "recovery_root": "recovery", "historical_material_opened": False, "state": "source_admitted"})
    identity_path.write_bytes(s.json_bytes(identity))
    qa_path = root / s.QA_NAME; qa = s._load(qa_path)
    inventory = s.candidate_records(root, {s.QA_NAME})
    qa.update({"output_inventory": inventory, "output_inventory_count": len(inventory),
               "output_inventory_sha256": s.manifest_digest(inventory),
               "contract_sha256": s.sha256_file(snapshot),
               "source_sha256": s.sha256_file(value.source_path),
               "recovery_manifest_sha256": s.sha256_file(value.recovery_root / "RECOVERY_MANIFEST.json"),
               "recovery_evidence_sha256": s.sha256_file(value.recovery_root / "RECOVERY_EVIDENCE.json")})
    qa_path.write_bytes(s.json_bytes(qa))


def _mutator(case_id: str, selector: str) -> Callable[[BundleFixture], None]:
    def mutate(bundle: BundleFixture) -> None:
        path = bundle.run_root / s.AUTHORITY_PATHS["COMMANDS"]
        value = s._load(path); value["case_" + case_id] = selector
        path.write_bytes(s.json_bytes(value))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate


def _case(case_id: str, code: str) -> s.MutationCase:
    mutation = CASE_MUTATIONS.get(case_id) if "CASE_MUTATIONS" in globals() else None
    if mutation is None:
        selector = "candidate/evidence/COMMANDS.json#/case/" + case_id
        return s.MutationCase(case_id, code, _mutator(case_id, selector), (), selector, ())
    mutate, reseal, selector = mutation
    allowed = []
    if s.ResealAuthority.SIDECAR in reseal:
        allowed.append("sidecar#/raw_sha256")
    if s.ResealAuthority.CONTRACT in reseal:
        allowed.append("contract#/raw_sha256")
    if s.ResealAuthority.RECOVERY_MANIFEST in reseal:
        allowed.extend(("recovery/RECOVERY_MANIFEST.json#/raw_sha256", "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256"))
    if s.ResealAuthority.RECOVERY_EVIDENCE in reseal:
        allowed.extend(("recovery/RECOVERY_EVIDENCE.json#/raw_sha256", "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256"))
    if s.ResealAuthority.PAGE_PROVENANCE in reseal:
        allowed.extend(("candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/raw_markdown_sha256"))
    if s.ResealAuthority.INVENTORY in reseal or s.ResealAuthority.QA in reseal:
        allowed.extend(("candidate/RECONSTRUCTED_EN.qa.json#/output_inventory", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"))
    return s.MutationCase(case_id, code, mutate, reseal, selector, tuple(allowed))


_EXACT = {
 "REP": [("branch-wrong","E_REPO_BRANCH"),("head-wrong","E_REPO_HEAD")],
 "SRC": [("source-byte-identical-alias","E_SOURCE_PATH"),("source-external-locator","E_SOURCE_EXTERNAL_FORBIDDEN"),("source-missing","E_PATH_MISSING"),("source-bytes-wrong","E_SOURCE_BYTES"),("source-hash-wrong","E_SOURCE_HASH"),("source-reparse","E_PATH_REPARSE"),("sidecar-missing","E_PATH_MISSING"),("sidecar-raw-hash-wrong","E_SIDECAR_HASH"),("sidecar-working-path-wrong","E_SIDECAR_WORKING_PATH"),("sidecar-working-bytes-wrong","E_SIDECAR_WORKING_BYTES"),("sidecar-working-hash-wrong","E_SIDECAR_WORKING_HASH"),("sidecar-page-count-wrong","E_SIDECAR_PAGE_COUNT"),("sidecar-media-box-wrong","E_SIDECAR_MEDIA_BOX"),("sidecar-rotation-wrong","E_SIDECAR_ROTATION"),("sidecar-runtime-dependency-true","E_SIDECAR_RUNTIME_DEPENDENCY"),("sidecar-external-path-allowed","E_SIDECAR_EXTERNAL_ALLOWED"),("sidecar-subsequent-path-wrong","E_SIDECAR_SUBSEQUENT_PATH"),("sidecar-origin-marked-source","E_SIDECAR_ORIGIN_POLICY")],
 "REG": [("P1-stale-metadata","E_SHAPE_QA"),("P1-missing-enforcement","E_COMMAND_COUNTS_PAGES")],
 "INJ": [("profile-seal-mutated","E_PROFILE_SEAL"),("test-route-given-production-profile","E_PROFILE_ROUTE"),("identity-provider-bound-to-other-profile","E_PROVIDER_BINDING"),("filesystem-provider-bound-to-other-profile","E_PROVIDER_BINDING"),("repository-root-observation-mismatch","E_REPO_ROOT")],
}
_AUT = "contract-argument-wrong:E_CONTRACT_PATH contract-raw-hash-wrong:E_CONTRACT_HASH contract-canonical-content-wrong:E_CONTRACT_CANONICAL snapshot-bytes-wrong:E_CONTRACT_SNAPSHOT_BYTES snapshot-hash-binding-wrong:E_CONTRACT_SNAPSHOT_HASH source-identity-contract-sha:E_SOURCE_IDENTITY_CONTRACT source-identity-source-bytes:E_SOURCE_IDENTITY_SOURCE_BYTES source-identity-source-sha:E_SOURCE_IDENTITY_SOURCE_HASH source-identity-page-count:E_SOURCE_IDENTITY_PAGE_COUNT source-identity-media-box:E_SOURCE_IDENTITY_MEDIA_BOX source-identity-rotation:E_SOURCE_IDENTITY_ROTATION source-identity-recovery-manifest-sha:E_SOURCE_IDENTITY_RECOVERY_MANIFEST source-identity-recovery-evidence-sha:E_SOURCE_IDENTITY_RECOVERY_EVIDENCE source-identity-recovery-root:E_SOURCE_IDENTITY_RECOVERY_ROOT source-identity-history-true:E_SOURCE_IDENTITY_HISTORY source-identity-state-wrong:E_SOURCE_IDENTITY_STATE recovery-root-wrong:E_RECOVERY_ROOT recovery-manifest-raw-hash:E_RECOVERY_MANIFEST_HASH recovery-evidence-raw-hash:E_RECOVERY_EVIDENCE_HASH recovery-successor-file-count:E_RECOVERY_FILE_COUNT recovery-successor-total-bytes:E_RECOVERY_TOTAL_BYTES recovery-manifest-row-path:E_RECOVERY_ROW_PATH recovery-manifest-row-bytes:E_RECOVERY_ROW_BYTES recovery-manifest-row-hash:E_RECOVERY_ROW_HASH recovery-manifest-row-duplicate:E_RECOVERY_ROW_DUPLICATE recovery-forbidden-payload:E_RECOVERY_FORBIDDEN recovery-evidence-source-binding:E_RECOVERY_SOURCE_BINDING recovery-evidence-payload-binding:E_RECOVERY_PAYLOAD_BINDING recovery-allowed-paths:E_RECOVERY_ALLOWED_PATHS recovery-promotion-true:E_RECOVERY_PROMOTION".split()
_EXACT["AUT"] = [tuple(item.split(":", 1)) for item in _AUT]
_EXACT["TOP"] = [tuple(item.split(":", 1)) for item in "candidate-root-wrong:E_CANDIDATE_ROOT candidate-root-escape:E_PATH_ESCAPE candidate-root-reparse:E_PATH_REPARSE nested-reparse:E_PATH_REPARSE root-file-missing:E_TOPOLOGY_MISSING root-entry-extra:E_TOPOLOGY_EXTRA evidence-file-missing:E_TOPOLOGY_MISSING evidence-file-extra:E_TOPOLOGY_EXTRA page-missing:E_TOPOLOGY_MISSING source-render-missing:E_TOPOLOGY_MISSING sheet-missing:E_TOPOLOGY_MISSING engine-payload-missing:E_TOPOLOGY_MISSING protected-empty-subtree-nonempty:E_PROTECTED_EMPTY_SUBTREE forbidden-pdf:E_CANDIDATE_FORBIDDEN_PDF forbidden-compiled-suffix:E_CANDIDATE_FORBIDDEN_COMPILED forbidden-pycache:E_CANDIDATE_FORBIDDEN_PYCACHE forbidden-bridge-runtime:E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME forbidden-cache:E_CANDIDATE_FORBIDDEN_CACHE forbidden-pytest-cache:E_CANDIDATE_FORBIDDEN_PYTEST_CACHE forbidden-tmp:E_CANDIDATE_FORBIDDEN_TMP forbidden-temp:E_CANDIDATE_FORBIDDEN_TEMP".split()]
_EXACT["LED"] = [tuple(item.split(":", 1)) for item in "open-count-wrong:E_LEDGER_OPEN_COUNT row-count-wrong:E_LEDGER_ROW_COUNT row-state-closed:E_LEDGER_ROW_STATE review-state-closed:E_LEDGER_REVIEW_STATE blocker-id-set-wrong:E_LEDGER_IDS affected-scope-count-wrong:E_LEDGER_SCOPE".split()]
_EXACT["INV"] = [tuple(item.split(":", 1)) for item in "ordinary-row-missing:E_INV_ORDINARY_ROW_MISSING evidence-row-missing:E_INV_EVIDENCE_ROW_MISSING sheet-row-missing:E_INV_SHEET_ROW_MISSING stale-extra-path:E_INV_STALE_EXTRA_PATH duplicate-path:E_INV_DUPLICATE_PATH qa-included:E_INV_QA_INCLUDED cardinality-wrong:E_INV_CARDINALITY order-nonordinal:E_INV_ORDER_NONORDINAL row-bytes-wrong:E_INV_ROW_BYTES row-hash-wrong:E_INV_ROW_HASH row-hash-lowercase:E_INV_ROW_HASH_LOWERCASE digest-wrong:E_INV_DIGEST path-backslash:E_INV_PATH_BACKSLASH path-absolute-or-drive:E_INV_PATH_ABSOLUTE_OR_DRIVE path-parent-segment:E_INV_PATH_PARENT_SEGMENT path-leading-dot-slash:E_INV_PATH_LEADING_DOT_SLASH row-shape-wrong:E_INV_ROW_SHAPE live-file-changed-behind-row:E_INV_LIVE_FILE_CHANGED".split()]
for family, names in {"PAG":"page-row-missing page-row-duplicate page-number-wrong page-id-wrong engine-index-wrong role-wrong contract-mode-wrong markdown-path-wrong markdown-bytes-wrong markdown-hash-wrong render-path-wrong render-bytes-wrong render-hash-wrong render-page-number-wrong render-dimensions-wrong render-dpi-wrong live-markdown-missing live-render-missing source-page-marker-wrong render-marker-wrong master-concatenation-wrong content-orphan content-duplicate content-order-wrong content-predecessor-wrong content-successor-wrong content-operation-fabricated content-asset-link-fabricated", "NAV":"row-missing anchor-duplicate anchor-id-wrong source-page-wrong engine-index-wrong first-previous-nonnull last-next-nonnull middle-previous-wrong middle-next-wrong dangling-link markdown-path-wrong render-path-wrong render-hash-wrong role-wrong closure-promoted", "AST":"row-missing id-duplicate path-duplicate hash-duplicate live-bytes-wrong live-hash-wrong engine-path-missing engine-path-wrong recovery-binding-wrong reference-total-wrong unreferenced-count-wrong reference-count-outside-zero-one occurrence-missing occurrence-duplicate markdown-path-wrong target-absent-from-markdown ownership-nonnull closure-promoted finding-wrong engine-image-cardinality-wrong mime-wrong", "SEM":"entity-ordinal-gap entity-id-duplicate handout-ordinal-gap handout-id-duplicate entity-handout-inequality required-count-wrong label-wrong page-range-wrong entity-closure-promoted mode-page-gap mode-row-duplicate mode-review-promoted reference-only-row-added historical-material-true map-role-count-wrong pregen-role-count-wrong back-cover-role-count-wrong handout-role-count-wrong"}.items():
    _EXACT[family] = [(name, "E_" + family + "_" + name.upper().replace("-", "_")) for name in names.split()]
_EXACT["SEM"] = [tuple(item.split(":", 1)) for item in """
entity-ordinal-gap:E_ENTITY_ORDINALS entity-id-duplicate:E_ENTITY_ID
handout-ordinal-gap:E_HANDOUT_ORDINALS handout-id-duplicate:E_HANDOUT_ID
entity-handout-inequality:E_ENTITY_HANDOUT_EQUALITY required-count-wrong:E_HANDOUT_REQUIRED_COUNT
label-wrong:E_HANDOUT_LABEL page-range-wrong:E_HANDOUT_PAGE_RANGE
entity-closure-promoted:E_ENTITY_CLOSURE mode-page-gap:E_MODE_PAGE_SET
mode-row-duplicate:E_MODE_DUPLICATE mode-review-promoted:E_MODE_REVIEW_STATE
reference-only-row-added:E_REFERENCE_ONLY_ROWS historical-material-true:E_REFERENCE_ONLY_HISTORY
map-role-count-wrong:E_ROLE_MAP_COUNT pregen-role-count-wrong:E_ROLE_PREGEN_COUNT
back-cover-role-count-wrong:E_ROLE_BACK_COVER_COUNT handout-role-count-wrong:E_ROLE_HANDOUT_COUNT
""".split()]
_EXACT["PAG"] = [tuple(item.split(":", 1)) for item in """
page-row-missing:E_PAGE_SET page-row-duplicate:E_PAGE_DUPLICATE page-number-wrong:E_PAGE_NUMBER
page-id-wrong:E_PAGE_ID engine-index-wrong:E_PAGE_ENGINE_INDEX role-wrong:E_PAGE_ROLE
contract-mode-wrong:E_PAGE_CONTENT_MODE markdown-path-wrong:E_PAGE_MARKDOWN_PATH
markdown-bytes-wrong:E_PAGE_MARKDOWN_BYTES markdown-hash-wrong:E_PAGE_MARKDOWN_HASH
render-path-wrong:E_PAGE_RENDER_PATH render-bytes-wrong:E_PAGE_RENDER_BYTES
render-hash-wrong:E_PAGE_RENDER_HASH render-page-number-wrong:E_PAGE_RENDER_NUMBER
render-dimensions-wrong:E_PAGE_RENDER_DIMENSIONS render-dpi-wrong:E_PAGE_RENDER_DPI
live-markdown-missing:E_PAGE_MARKDOWN_MISSING live-render-missing:E_PAGE_RENDER_MISSING
source-page-marker-wrong:E_PAGE_SOURCE_MARKER render-marker-wrong:E_PAGE_RENDER_MARKER
master-concatenation-wrong:E_MASTER_CONCATENATION content-orphan:E_CONTENT_PAGE_LINK
content-duplicate:E_CONTENT_DUPLICATE content-order-wrong:E_CONTENT_ORDER
content-predecessor-wrong:E_CONTENT_PREDECESSOR content-successor-wrong:E_CONTENT_SUCCESSOR
content-operation-fabricated:E_CONTENT_OPERATION content-asset-link-fabricated:E_CONTENT_ASSET_LINK
""".split()]
_EXACT["NAV"] = [tuple(item.split(":", 1)) for item in """
row-missing:E_NAV_SET anchor-duplicate:E_NAV_DUPLICATE anchor-id-wrong:E_NAV_ANCHOR
source-page-wrong:E_NAV_PAGE engine-index-wrong:E_NAV_ENGINE_INDEX
first-previous-nonnull:E_NAV_FIRST_PREVIOUS last-next-nonnull:E_NAV_LAST_NEXT
middle-previous-wrong:E_NAV_PREVIOUS middle-next-wrong:E_NAV_NEXT
dangling-link:E_NAV_DANGLING markdown-path-wrong:E_NAV_MARKDOWN_PATH
render-path-wrong:E_NAV_RENDER_PATH render-hash-wrong:E_NAV_RENDER_HASH
role-wrong:E_NAV_ROLE closure-promoted:E_NAV_CLOSURE
""".split()]
_EXACT["AST"] = [tuple(item.split(":", 1)) for item in """
row-missing:E_ASSET_SET id-duplicate:E_ASSET_ID_DUPLICATE path-duplicate:E_ASSET_PATH_DUPLICATE
hash-duplicate:E_ASSET_HASH_DUPLICATE live-bytes-wrong:E_ASSET_BYTES live-hash-wrong:E_ASSET_HASH
engine-path-missing:E_ASSET_ENGINE_MISSING engine-path-wrong:E_ASSET_ENGINE_PATH
recovery-binding-wrong:E_ASSET_RECOVERY_BINDING reference-total-wrong:E_ASSET_REFERENCE_TOTAL
unreferenced-count-wrong:E_ASSET_UNREFERENCED_COUNT reference-count-outside-zero-one:E_ASSET_REFERENCE_COUNT
occurrence-missing:E_ASSET_OCCURRENCE_SET occurrence-duplicate:E_ASSET_OCCURRENCE_DUPLICATE
markdown-path-wrong:E_ASSET_MARKDOWN_PATH target-absent-from-markdown:E_ASSET_TARGET_RESOLUTION
ownership-nonnull:E_ASSET_OWNERSHIP closure-promoted:E_ASSET_CLOSURE finding-wrong:E_ASSET_FINDING
engine-image-cardinality-wrong:E_ASSET_ENGINE_COUNT mime-wrong:E_ASSET_MIME
""".split()]
_CMD_FLAGS = "build_invoked mineru_invoked ocr_invoked gpu_or_model_invoked network_invoked external_source_used".split()
_CMD_COUNTS = "pages renders contact_sheets handouts maps pregens back_cover assets referenced_assets unreferenced_assets markdown_references".split()
_CMD_C = [("sheet-count-wrong", "E_COMMAND_SHEET_COUNT"), ("sheet-coverage-wrong", "E_COMMAND_SHEET_COVERAGE"), ("sheet-missing", "E_COMMAND_SHEET_SET"), ("sheet-duplicate", "E_COMMAND_SHEET_SET"), ("sheet-id-wrong", "E_COMMAND_SHEET_ID"), ("sheet-path-sequence-wrong", "E_COMMAND_SHEET_PATH"), ("sheet-grid-wrong", "E_COMMAND_SHEET_GRID"), ("sheet-hash-wrong", "E_COMMAND_SHEET_HASH"), ("flattened-page-missing", "E_COMMAND_SHEET_PAGES"), ("flattened-page-duplicate", "E_COMMAND_SHEET_PAGES"), ("flattened-page-order-wrong", "E_COMMAND_SHEET_PAGE_ORDER"), ("render-path-wrong", "E_COMMAND_RENDER_PATH"), ("render-hash-wrong", "E_COMMAND_RENDER_HASH"), ("page-render-mapping-disagrees", "E_COMMAND_PAGE_RENDER_MAP"), ("verify-determinism-false", "E_COMMAND_DETERMINISM")]
_EXACT["CMD"] = [(name, code) for name, code in [("action-missing","E_COMMAND_ACTIONS"),("action-duplicate","E_COMMAND_ACTIONS"),("action-extra","E_COMMAND_ACTIONS"),("action-reordered","E_COMMAND_ACTIONS"),("state-promoted","E_COMMAND_STATE"),("external-locator-used","E_COMMAND_EXTERNAL_SOURCE")]] + [(f"flag-{field}-{kind}", f"E_COMMAND_FLAG_{field.upper()}") for field in _CMD_FLAGS for kind in ("missing","true")] + [(f"argument-{field}-{kind}", f"E_COMMAND_ARGUMENT_{field.upper()}") for field in "source_flag run_root_flag source_relative_path".split() for kind in ("missing","wrong")] + [(f"count-{field}-{kind}", f"E_COMMAND_COUNTS_{field.upper()}") for field in _CMD_COUNTS for kind in ("missing","wrong")] + _CMD_C
_QAV_TOP = "asset_count block_count contact_sheet_count contract_sha256 counts gate_results handout_count historical_material_opened main_scripts_invoked navigation_anchor_count open_blocker_count output_inventory output_inventory_count output_inventory_rule output_inventory_sha256 page_count recovery_evidence_sha256 recovery_manifest_sha256 referenced_asset_count schema source_sha256 state unreferenced_asset_count".split()
_QAV_COUNT_KEYS = "assets back_cover contact_sheets engine_images engine_payload handouts maps navigation_anchors open_blockers pages pregens referenced_assets renders unreferenced_assets".split()
_QAV_D1_CASES = (
    ("gate-asset_conservation-missing", "E_QA_GATE_ASSET_CONSERVATION"),
    ("gate-contact_sheet_coverage-missing", "E_QA_GATE_CONTACT_SHEET_COVERAGE"),
    ("gate-navigation_anchors-missing", "E_QA_GATE_NAVIGATION_ANCHORS"),
    ("gate-page_1_5_modes-missing", "E_QA_GATE_PAGE_1_5_MODES"),
    ("gate-page_coverage-missing", "E_QA_GATE_PAGE_COVERAGE"),
    ("gate-promotion-missing", "E_QA_GATE_PROMOTION"),
    ("gate-recovery_admission-missing", "E_QA_GATE_RECOVERY_ADMISSION"),
    ("gate-source_identity-missing", "E_QA_GATE_SOURCE_IDENTITY"),
    ("gate-visual_review-missing", "E_QA_GATE_VISUAL_REVIEW"),
    ("gate-asset_conservation-wrong", "E_QA_GATE_ASSET_CONSERVATION"),
    ("gate-contact_sheet_coverage-wrong", "E_QA_GATE_CONTACT_SHEET_COVERAGE"),
    ("gate-navigation_anchors-wrong", "E_QA_GATE_NAVIGATION_ANCHORS"),
    ("gate-page_coverage-wrong", "E_QA_GATE_PAGE_COVERAGE"),
    ("gate-recovery_admission-wrong", "E_QA_GATE_RECOVERY_ADMISSION"),
    ("gate-source_identity-wrong", "E_QA_GATE_SOURCE_IDENTITY"),
    ("gate-page_1_5_modes-closed", "E_QA_GATE_PAGE_1_5_MODES"),
    ("gate-promotion-closed", "E_QA_GATE_PROMOTION"),
    ("gate-visual_review-closed", "E_QA_GATE_VISUAL_REVIEW"),
    ("historical-material-true", "E_QA_HISTORY"),
    ("main-scripts-invoked-true", "E_QA_MAIN_SCRIPTS"),
)
_EXACT["QAV"] = [(f"top-{field}-missing", "E_SHAPE_QA") for field in _QAV_TOP] + [("top-extra","E_SHAPE_QA"),("state-promoted","E_QA_STATE")] + [(f"authority-{field}", f"E_QA_{field.upper().replace('-', '_')}_HASH") for field in "contract source recovery-manifest recovery-evidence".split()] + [(f"scalar-{field}-wrong", f"E_QA_SCALAR_{field.upper()}") for field in "page_count handout_count block_count asset_count contact_sheet_count navigation_anchor_count referenced_asset_count unreferenced_asset_count open_blocker_count".split()] + [(f"counts-{key}-{kind}", f"E_QA_COUNTS_{key.upper()}") for key in _QAV_COUNT_KEYS for kind in ("missing", "wrong")] + list(_QAV_D1_CASES) + [("inventory-rule-wrong","E_QA_INVENTORY_RULE"),("inventory-count-wrong","E_INV_CARDINALITY"),("inventory-digest-wrong","E_INV_DIGEST"),("inventory-array-wrong","E_INV_ORDINARY_ROW_MISSING")]
for label in s.AUTHORITY_ORDER:
    _EXACT.setdefault("SCH", []).extend([(f"{label}-schema-wrong", f"E_SCHEMA_{label}"), (f"{label}-required-top-member-missing", f"E_SHAPE_{label}")])
_EXACT["SCH"].append(("qa-unexpected-top-member", "E_SHAPE_QA"))

assert {family: len(_EXACT[family]) for family in FAMILY_COUNTS} == FAMILY_COUNTS


def _sidecar(bundle: BundleFixture) -> tuple[Path, dict[str, object]]:
    path = bundle.sidecar_path
    return path, s._load(path)


def _write_sidecar(path: Path, value: dict[str, object]) -> None:
    value.pop("raw_sha256", None)
    value["raw_sha256"] = s.sha256_bytes(s.json_bytes(value))
    path.write_bytes(s.json_bytes(value))


def _sidecar_mutation(case_id: str, selector: str, change: Callable[[dict[str, object]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        path, value = _sidecar(bundle)
        change(value)
        path.write_bytes(s.json_bytes(value))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, (s.ResealAuthority.SIDECAR, s.ResealAuthority.PROFILE), selector


def _repo_mutation(case_id: str, field: str) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        identity = bundle.context.identity.identity
        assert identity is not None
        object.__setattr__(bundle.context.identity, "identity", s.RepositoryIdentity(identity.root, "wrong" if field == "branch" else identity.branch, "wrong" if field == "head" else identity.head))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, (), "repository#/" + field


def _source_mutation(case_id: str, selector: str, change: Callable[[BundleFixture], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        change(bundle)
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, (), selector


def _json_mutation(case_id: str, relative: str, selector: str, change: Callable[[dict[str, object]], None],
                   reseal: tuple[s.ResealAuthority, ...] = ()) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        path = bundle.repo_root / relative
        value = s._load(path); change(value); path.write_bytes(s.json_bytes(value))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, reseal, selector


def _source_alias(bundle: BundleFixture) -> None:
    alias = bundle.source_path.with_name("byte-identical-alias.pdf")
    alias.write_bytes(bundle.source_path.read_bytes())
    object.__setattr__(bundle, "source_path", alias)


def _source_reparse(bundle: BundleFixture) -> None:
    target = bundle.source_path.with_name("source-target.pdf")
    bundle.source_path.rename(target)
    bundle.source_path.write_bytes(target.read_bytes())
    real = bundle.context.filesystem.real
    entry = real.classify(bundle.source_path)
    replacement = s.FileSystemEntry(entry.kind, entry.size, entry.file_id,
                                    entry.file_attributes | 0x400, 0xA000000C)
    normalized = __import__("os").path.normcase(__import__("os").path.normpath(str(bundle.source_path)))
    override = s.ClassificationOverride(normalized, replacement)
    object.__setattr__(bundle.context, "filesystem", s.TestFilesystemProvider(real, (override,), "fixture-filesystem", bundle.profile.authority_sha256))


CASE_MUTATIONS = {
    "REP-branch-wrong": _repo_mutation("REP-branch-wrong", "branch"),
    "REP-head-wrong": _repo_mutation("REP-head-wrong", "head"),
    "SRC-source-byte-identical-alias": _source_mutation("SRC-source-byte-identical-alias", "source#/path", _source_alias),
    "SRC-source-missing": _source_mutation("SRC-source-missing", "source#/physical-entry", lambda bundle: bundle.source_path.unlink()),
    "SRC-source-bytes-wrong": _source_mutation("SRC-source-bytes-wrong", "source#/bytes", lambda bundle: bundle.source_path.write_bytes(b"fixture source+")),
    "SRC-source-hash-wrong": _source_mutation("SRC-source-hash-wrong", "source#/sha256", lambda bundle: bundle.source_path.write_bytes(b"fixture sourcE")),
    "SRC-source-reparse": _source_mutation("SRC-source-reparse", "source#/reparse", _source_reparse),
    "SRC-sidecar-missing": _source_mutation("SRC-sidecar-missing", "sidecar#/physical-entry", lambda bundle: bundle.sidecar_path.unlink()),
}


_REG_STALE_SHEET_PATHS = tuple(
    f"renders/contact_sheets/sheet-{number:03d}.png" for number in range(1, 32)
)
_REG_STALE_DELTA = (
    "candidate/RECONSTRUCTED_EN.qa.json#/schema",
    "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256",
    "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256",
    "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count",
    "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers",
    *(f"candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/{path}" for path in _REG_STALE_SHEET_PATHS),
    "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count",
    "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256",
)
assert len(_REG_STALE_DELTA) == 38


def _reg_stale_metadata(bundle: BundleFixture) -> None:
    """Create the approved synthetic, fixture-local stale-QA regression state."""
    path = bundle.run_root / s.QA_NAME
    qa = s._load(path)
    rows = qa["output_inventory"]
    assert isinstance(rows, list) and len(rows) == 501
    assert len({row["path"] for row in rows}) == 501
    present_sheets = tuple(row["path"] for row in rows if row["path"].startswith("renders/contact_sheets/"))
    assert present_sheets == _REG_STALE_SHEET_PATHS
    retained = [row for row in rows if row["path"] not in _REG_STALE_SHEET_PATHS]
    assert len(retained) == 470 and len({row["path"] for row in retained}) == 470
    assert retained == sorted(retained, key=lambda row: row["path"])
    qa["schema"] = "kb_creator.reconstructed_en_qa.v2"
    qa["recovery_manifest_sha256"] = "C32CCA2A85F8123A2BE9E015FB39642943E31FCD723FA466FA436F454B344C3A"
    qa.pop("recovery_evidence_sha256")
    qa["open_blocker_count"] = 3
    qa["counts"]["open_blockers"] = 3
    qa["output_inventory"] = retained
    qa["output_inventory_count"] = 470
    qa["output_inventory_sha256"] = s.manifest_digest(retained)
    assert qa["output_inventory_count"] == len(qa["output_inventory"]) == 470
    assert qa["output_inventory_sha256"] == s.manifest_digest(qa["output_inventory"])
    assert qa["output_inventory_rule"] == "every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json"
    assert qa["state"] == "candidate_needs_review"
    path.write_bytes(s.json_bytes(qa))


_reg_stale_metadata.__name__ = "mutate_REG_P1_stale_metadata"
CASE_MUTATIONS["REG-P1-stale-metadata"] = (
    _reg_stale_metadata, (), "candidate/RECONSTRUCTED_EN.qa.json#"
)
CASE_MUTATIONS["SRC-source-external-locator"] = _sidecar_mutation("SRC-source-external-locator", "sidecar#/external_locator", lambda value: value.__setitem__("external_locator", "external"))
CASE_MUTATIONS["SRC-sidecar-raw-hash-wrong"] = _source_mutation("SRC-sidecar-raw-hash-wrong", "sidecar#/raw_sha256", lambda bundle: s._load(bundle.sidecar_path).__setitem__("raw_sha256", "0" * 64))

def _raw_hash_wrong(bundle: BundleFixture) -> None:
    path, value = _sidecar(bundle); value["raw_sha256"] = "0" * 64; path.write_bytes(s.json_bytes(value))
CASE_MUTATIONS["SRC-sidecar-raw-hash-wrong"] = _source_mutation("SRC-sidecar-raw-hash-wrong", "sidecar#/raw_sha256", _raw_hash_wrong)
for suffix, selector, change in (
    ("working-path-wrong", "sidecar#/working_source/path", lambda value: value["working_source"].__setitem__("path", "wrong.pdf")),
    ("working-bytes-wrong", "sidecar#/working_source/bytes", lambda value: value["working_source"].__setitem__("bytes", 0)),
    ("working-hash-wrong", "sidecar#/working_source/sha256", lambda value: value["working_source"].__setitem__("sha256", "0" * 64)),
    ("page-count-wrong", "sidecar#/working_source/page_count", lambda value: value["working_source"].__setitem__("page_count", 0)),
    ("media-box-wrong", "sidecar#/working_source/media_box", lambda value: value["working_source"].__setitem__("media_box", [0, 0])),
    ("rotation-wrong", "sidecar#/working_source/rotations", lambda value: value["working_source"].__setitem__("rotations", [])),
    ("runtime-dependency-true", "sidecar#/policy/runtime_dependency", lambda value: value["policy"].__setitem__("runtime_dependency", True)),
    ("external-path-allowed", "sidecar#/policy/external_path_allowed", lambda value: value["policy"].__setitem__("external_path_allowed", True)),
    ("subsequent-path-wrong", "sidecar#/policy/subsequent_path", lambda value: value["policy"].__setitem__("subsequent_path", "wrong.pdf")),
    ("origin-marked-source", "sidecar#/policy/origin", lambda value: value["policy"].__setitem__("origin", "source")),
):
    case_id = "SRC-sidecar-" + suffix
    CASE_MUTATIONS[case_id] = _sidecar_mutation(case_id, selector, change)


def _replace_recovery_root(bundle: BundleFixture) -> None:
    wrong = bundle.repo_root / "wrong-recovery"; wrong.mkdir()
    object.__setattr__(bundle, "recovery_root", wrong)


def _contract_reseal(bundle: BundleFixture) -> str:
    value = s._load(bundle.contract_path); value.pop("raw_sha256", None)
    value["raw_sha256"] = s.sha256_bytes(s.json_bytes(value)); bundle.contract_path.write_bytes(s.json_bytes(value))
    return "contract#/raw_sha256"


for suffix, relative, selector, change, reseal in (
    ("contract-raw-hash-wrong", "contract.json", "contract#/raw_sha256", lambda value: value.__setitem__("raw_sha256", "0" * 64), ()),
    ("contract-canonical-content-wrong", "contract.json", "contract#/scenario", lambda value: value.__setitem__("scenario", "wrong"), (s.ResealAuthority.CONTRACT, s.ResealAuthority.PROFILE)),
    ("snapshot-bytes-wrong", "candidate/SCENARIO_CONTRACT.json", "candidate/SCENARIO_CONTRACT.json#/scenario", lambda value: value.__setitem__("scenario", "wrong"), ()),
    ("snapshot-hash-binding-wrong", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/contract_snapshot_sha256", lambda value: value.__setitem__("contract_snapshot_sha256", "0" * 64), ()),
    ("source-identity-contract-sha", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/contract_sha256", lambda value: value.__setitem__("contract_sha256", "0" * 64), ()),
    ("source-identity-source-bytes", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/source/bytes", lambda value: value["source"].__setitem__("bytes", 0), ()),
    ("source-identity-source-sha", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/source/sha256", lambda value: value["source"].__setitem__("sha256", "0" * 64), ()),
    ("source-identity-page-count", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/source/page_count", lambda value: value["source"].__setitem__("page_count", 0), ()),
    ("source-identity-media-box", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/source/media_box", lambda value: value["source"].__setitem__("media_box", [0, 0]), ()),
    ("source-identity-rotation", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/source/rotations", lambda value: value["source"].__setitem__("rotations", []), ()),
    ("source-identity-recovery-manifest-sha", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256", lambda value: value.__setitem__("recovery_manifest_sha256", "0" * 64), ()),
    ("source-identity-recovery-evidence-sha", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256", lambda value: value.__setitem__("recovery_evidence_sha256", "0" * 64), ()),
    ("source-identity-recovery-root", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/recovery_root", lambda value: value.__setitem__("recovery_root", "wrong"), ()),
    ("source-identity-history-true", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/historical_material_opened", lambda value: value.__setitem__("historical_material_opened", True), ()),
    ("source-identity-state-wrong", "candidate/SOURCE_IDENTITY.json", "candidate/SOURCE_IDENTITY.json#/state", lambda value: value.__setitem__("state", "wrong"), ()),
):
    case_id = "AUT-" + suffix
    CASE_MUTATIONS[case_id] = _json_mutation(case_id, relative, selector, change, reseal)
CASE_MUTATIONS["AUT-contract-argument-wrong"] = _source_mutation("AUT-contract-argument-wrong", "contract#/path", lambda bundle: object.__setattr__(bundle, "contract_path", bundle.repo_root / "wrong-contract.json"))
CASE_MUTATIONS["AUT-recovery-root-wrong"] = _source_mutation("AUT-recovery-root-wrong", "recovery#/path", _replace_recovery_root)

def _recovery_mutation(case_id: str, relative: str, selector: str, change: Callable[[dict[str, object]], None], authority: s.ResealAuthority) -> None:
    CASE_MUTATIONS[case_id] = _json_mutation(case_id, relative, selector, change, (authority, s.ResealAuthority.SOURCE_IDENTITY, s.ResealAuthority.INVENTORY, s.ResealAuthority.QA, s.ResealAuthority.PROFILE))

CASE_MUTATIONS["AUT-recovery-manifest-raw-hash"] = _json_mutation("AUT-recovery-manifest-raw-hash", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/raw_sha256", lambda value: value.__setitem__("raw_sha256", "0" * 64))
CASE_MUTATIONS["AUT-recovery-evidence-raw-hash"] = _json_mutation("AUT-recovery-evidence-raw-hash", "recovery/RECOVERY_EVIDENCE.json", "recovery/RECOVERY_EVIDENCE.json#/raw_sha256", lambda value: value.__setitem__("raw_sha256", "0" * 64))
_recovery_mutation("AUT-recovery-successor-file-count", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/successor_file_count", lambda value: value.__setitem__("successor_file_count", 0), s.ResealAuthority.RECOVERY_MANIFEST)
_recovery_mutation("AUT-recovery-successor-total-bytes", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/successor_total_bytes", lambda value: value.__setitem__("successor_total_bytes", 0), s.ResealAuthority.RECOVERY_MANIFEST)
_recovery_mutation("AUT-recovery-manifest-row-path", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/files/0/path", lambda value: value["files"][0].__setitem__("path", "../wrong"), s.ResealAuthority.RECOVERY_MANIFEST)
_recovery_mutation("AUT-recovery-manifest-row-bytes", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/files/0/bytes", lambda value: value["files"][0].__setitem__("bytes", 0), s.ResealAuthority.RECOVERY_MANIFEST)
_recovery_mutation("AUT-recovery-manifest-row-hash", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/files/0/sha256", lambda value: value["files"][0].__setitem__("sha256", "0" * 64), s.ResealAuthority.RECOVERY_MANIFEST)
_recovery_mutation("AUT-recovery-manifest-row-duplicate", "recovery/RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json#/files/1/path", lambda value: value["files"][1].__setitem__("path", value["files"][0]["path"]), s.ResealAuthority.RECOVERY_MANIFEST)
_recovery_mutation("AUT-recovery-evidence-source-binding", "recovery/RECOVERY_EVIDENCE.json", "recovery/RECOVERY_EVIDENCE.json#/source_identity", lambda value: value.__setitem__("source_identity", {}), s.ResealAuthority.RECOVERY_EVIDENCE)
_recovery_mutation("AUT-recovery-evidence-payload-binding", "recovery/RECOVERY_EVIDENCE.json", "recovery/RECOVERY_EVIDENCE.json#/payload", lambda value: value.__setitem__("payload", {}), s.ResealAuthority.RECOVERY_EVIDENCE)
_recovery_mutation("AUT-recovery-allowed-paths", "recovery/RECOVERY_EVIDENCE.json", "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths", lambda value: value.__setitem__("allowed_payload_paths", []), s.ResealAuthority.RECOVERY_EVIDENCE)
_recovery_mutation("AUT-recovery-promotion-true", "recovery/RECOVERY_EVIDENCE.json", "recovery/RECOVERY_EVIDENCE.json#/promotion", lambda value: value.__setitem__("promotion", True), s.ResealAuthority.RECOVERY_EVIDENCE)
CASE_MUTATIONS["AUT-recovery-forbidden-payload"] = _source_mutation("AUT-recovery-forbidden-payload", "recovery/forbidden.pdf", lambda bundle: (bundle.recovery_root / "forbidden.pdf").write_bytes(b"forbidden"))


def _top_reparse(bundle: BundleFixture, relative: str) -> None:
    path = bundle.run_root / relative
    real = bundle.context.filesystem.real
    entry = real.classify(path)
    replacement = s.FileSystemEntry(entry.kind, entry.size, entry.file_id,
                                    entry.file_attributes | 0x400, 0xA000000C)
    override = s.ClassificationOverride(__import__("os").path.normcase(__import__("os").path.normpath(str(path))), replacement)
    object.__setattr__(bundle.context, "filesystem", s.TestFilesystemProvider(real, (override,), "fixture-filesystem", bundle.profile.authority_sha256))


def _top_write(relative: str, payload: bytes = b"top") -> Callable[[BundleFixture], None]:
    def mutate(bundle: BundleFixture) -> None:
        path = bundle.run_root / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
    return mutate


def _top_remove(relative: str) -> Callable[[BundleFixture], None]:
    return lambda bundle: (bundle.run_root / relative).unlink()


CASE_MUTATIONS.update({
    "TOP-candidate-root-wrong": _source_mutation("TOP-candidate-root-wrong", "candidate#/root", lambda bundle: object.__setattr__(bundle, "run_root", bundle.repo_root / "wrong-candidate")),
    "TOP-candidate-root-escape": _source_mutation("TOP-candidate-root-escape", "candidate#/escape", lambda bundle: object.__setattr__(bundle, "run_root", bundle.repo_root.parent / "escaped-candidate")),
    "TOP-candidate-root-reparse": _source_mutation("TOP-candidate-root-reparse", "candidate#/reparse", lambda bundle: _top_reparse(bundle, ".")),
    "TOP-nested-reparse": _source_mutation("TOP-nested-reparse", "candidate/pages/page-001.md#/reparse", lambda bundle: _top_reparse(bundle, "pages/page-001.md")),
    "TOP-root-file-missing": _source_mutation("TOP-root-file-missing", "candidate/RECONSTRUCTED_EN.md#/physical-entry", _top_remove("RECONSTRUCTED_EN.md")),
    "TOP-root-entry-extra": _source_mutation("TOP-root-entry-extra", "candidate/EXTRA.txt#/physical-entry", _top_write("EXTRA.txt")),
    "TOP-evidence-file-missing": _source_mutation("TOP-evidence-file-missing", "candidate/evidence/COMMANDS.json#/physical-entry", _top_remove("evidence/COMMANDS.json")),
    "TOP-evidence-file-extra": _source_mutation("TOP-evidence-file-extra", "candidate/evidence/EXTRA.json#/physical-entry", _top_write("evidence/EXTRA.json")),
    "TOP-page-missing": _source_mutation("TOP-page-missing", "candidate/pages/page-001.md#/physical-entry", _top_remove("pages/page-001.md")),
    "TOP-source-render-missing": _source_mutation("TOP-source-render-missing", "candidate/renders/source/page-001.png#/physical-entry", _top_remove("renders/source/page-001.png")),
    "TOP-sheet-missing": _source_mutation("TOP-sheet-missing", "candidate/renders/contact_sheets/sheet-001.png#/physical-entry", _top_remove("renders/contact_sheets/sheet-001.png")),
    "TOP-engine-payload-missing": _source_mutation("TOP-engine-payload-missing", "candidate/engine/payload-001.bin#/physical-entry", _top_remove("engine/payload-001.bin")),
    "TOP-protected-empty-subtree-nonempty": _source_mutation("TOP-protected-empty-subtree-nonempty", "candidate/assets/probe.bin#/physical-entry", _top_write("assets/probe.bin")),
    "TOP-forbidden-pdf": _source_mutation("TOP-forbidden-pdf", "candidate/forbidden.pdf#/physical-entry", _top_write("forbidden.pdf")),
    "TOP-forbidden-compiled-suffix": _source_mutation("TOP-forbidden-compiled-suffix", "candidate/forbidden.pyc#/physical-entry", _top_write("forbidden.pyc")),
    "TOP-forbidden-pycache": _source_mutation("TOP-forbidden-pycache", "candidate/__pycache__/probe.bin#/physical-entry", _top_write("__pycache__/probe.bin")),
    "TOP-forbidden-bridge-runtime": _source_mutation("TOP-forbidden-bridge-runtime", "candidate/_bridge_runtime/probe.bin#/physical-entry", _top_write("_bridge_runtime/probe.bin")),
    "TOP-forbidden-cache": _source_mutation("TOP-forbidden-cache", "candidate/cache/probe.bin#/physical-entry", _top_write("cache/probe.bin")),
    "TOP-forbidden-pytest-cache": _source_mutation("TOP-forbidden-pytest-cache", "candidate/.pytest_cache/probe.bin#/physical-entry", _top_write(".pytest_cache/probe.bin")),
    "TOP-forbidden-tmp": _source_mutation("TOP-forbidden-tmp", "candidate/tmp/probe.bin#/physical-entry", _top_write("tmp/probe.bin")),
    "TOP-forbidden-temp": _source_mutation("TOP-forbidden-temp", "candidate/temp/probe.bin#/physical-entry", _top_write("temp/probe.bin")),
})


def _sem_document(case_id: str, label: str, selector: str,
                  change: Callable[[dict[str, object]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _json_mutation(case_id, "candidate/" + s.AUTHORITY_PATHS[label], selector,
                          change, (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA))


def _sem_rows(case_id: str, label: str, selector: str,
              change: Callable[[list[dict[str, object]]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _sem_document(case_id, label, selector, lambda value: change(value["rows"]))


CASE_MUTATIONS.update({
    "SEM-entity-ordinal-gap": _sem_rows("SEM-entity-ordinal-gap", "ENTITY_INVENTORY", "candidate/evidence/ENTITY_INVENTORY.json#/rows/1/ordinal", lambda rows: rows[1].__setitem__("ordinal", 3)),
    "SEM-entity-id-duplicate": _sem_rows("SEM-entity-id-duplicate", "ENTITY_INVENTORY", "candidate/evidence/ENTITY_INVENTORY.json#/rows/1/id", lambda rows: rows[1].__setitem__("id", rows[0]["id"])),
    "SEM-handout-ordinal-gap": _sem_rows("SEM-handout-ordinal-gap", "HANDOUT_INVENTORY", "candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/ordinal", lambda rows: rows[1].__setitem__("ordinal", 3)),
    "SEM-handout-id-duplicate": _sem_rows("SEM-handout-id-duplicate", "HANDOUT_INVENTORY", "candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/id", lambda rows: rows[1].__setitem__("id", rows[0]["id"])),
    "SEM-entity-handout-inequality": _sem_rows("SEM-entity-handout-inequality", "ENTITY_INVENTORY", "candidate/evidence/ENTITY_INVENTORY.json#/rows/0/disposition", lambda rows: rows[0].__setitem__("disposition", "different")),
    "SEM-required-count-wrong": _sem_document("SEM-required-count-wrong", "HANDOUT_INVENTORY", "candidate/evidence/HANDOUT_INVENTORY.json#/required_count", lambda value: value.__setitem__("required_count", 38)),
    "SEM-label-wrong": _sem_rows("SEM-label-wrong", "HANDOUT_INVENTORY", "candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/label", lambda rows: rows[0].__setitem__("label", "Wrong")),
    "SEM-page-range-wrong": _sem_rows("SEM-page-range-wrong", "HANDOUT_INVENTORY", "candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/range", lambda rows: rows[0].__setitem__("range", [1, 2])),
    "SEM-entity-closure-promoted": _sem_rows("SEM-entity-closure-promoted", "ENTITY_INVENTORY", "candidate/evidence/ENTITY_INVENTORY.json#/rows/0/review_state", lambda rows: rows[0].__setitem__("review_state", "closed")),
    "SEM-mode-page-gap": _sem_rows("SEM-mode-page-gap", "CONTENT_MODE_REVIEW", "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/4", lambda rows: rows.pop()),
    "SEM-mode-row-duplicate": _sem_rows("SEM-mode-row-duplicate", "CONTENT_MODE_REVIEW", "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/1/page", lambda rows: rows[1].__setitem__("page", 1)),
    "SEM-mode-review-promoted": _sem_rows("SEM-mode-review-promoted", "CONTENT_MODE_REVIEW", "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/0/review_state", lambda rows: rows[0].__setitem__("review_state", "closed")),
    "SEM-reference-only-row-added": _sem_rows("SEM-reference-only-row-added", "REFERENCE_ONLY_AUDIT", "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/rows/0", lambda rows: rows.append({"reference": "added"})),
    "SEM-historical-material-true": _sem_document("SEM-historical-material-true", "REFERENCE_ONLY_AUDIT", "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened", lambda value: value.__setitem__("historical_material_opened", True)),
    "SEM-map-role-count-wrong": _sem_rows("SEM-map-role-count-wrong", "NAVIGATION_INVENTORY", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/39/semantic_role", lambda rows: rows[39].__setitem__("semantic_role", "scenario_body")),
    "SEM-pregen-role-count-wrong": _sem_rows("SEM-pregen-role-count-wrong", "NAVIGATION_INVENTORY", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/46/semantic_role", lambda rows: rows[46].__setitem__("semantic_role", "scenario_body")),
    "SEM-back-cover-role-count-wrong": _sem_rows("SEM-back-cover-role-count-wrong", "NAVIGATION_INVENTORY", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/59/semantic_role", lambda rows: rows[59].__setitem__("semantic_role", "scenario_body")),
    "SEM-handout-role-count-wrong": _sem_rows("SEM-handout-role-count-wrong", "NAVIGATION_INVENTORY", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/semantic_role", lambda rows: rows[0].__setitem__("semantic_role", "scenario_body")),
})


def _ledger_mutation(case_id: str, selector: str, change: Callable[[dict[str, object]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        path = bundle.run_root / s.AUTHORITY_PATHS["BLOCKER_LEDGER"]
        value = s._load(path); change(value); path.write_bytes(s.json_bytes(value))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA), selector


CASE_MUTATIONS.update({
    "LED-open-count-wrong": _ledger_mutation("LED-open-count-wrong", "candidate/evidence/BLOCKER_LEDGER.json#/open_count", lambda value: value.__setitem__("open_count", 3)),
    "LED-row-count-wrong": _ledger_mutation("LED-row-count-wrong", "candidate/evidence/BLOCKER_LEDGER.json#/rows", lambda value: value["rows"].pop()),
    "LED-row-state-closed": _ledger_mutation("LED-row-state-closed", "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/state", lambda value: value["rows"][0].__setitem__("state", "closed")),
    "LED-review-state-closed": _ledger_mutation("LED-review-state-closed", "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/review_state", lambda value: value["rows"][0].__setitem__("review_state", "closed")),
    "LED-blocker-id-set-wrong": _ledger_mutation("LED-blocker-id-set-wrong", "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/id", lambda value: value["rows"][0].__setitem__("id", "wrong-blocker")),
    "LED-affected-scope-count-wrong": _ledger_mutation("LED-affected-scope-count-wrong", "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/scope", lambda value: value["rows"][0].__setitem__("scope", [])),
})


def _replace_context(bundle: BundleFixture, *, profile: s.EnforcementProfile | None = None,
                     identity: object | None = None, filesystem: object | None = None) -> None:
    context = bundle.context
    object.__setattr__(bundle, "context", s.EnforcementContext(
        profile or context.profile,
        context.identity if identity is None else identity,
        context.filesystem if filesystem is None else filesystem,
    ))


def _inj_profile_seal(bundle: BundleFixture) -> None:
    profile = bundle.context.profile
    _replace_context(bundle, profile=s.EnforcementProfile(profile.profile_id, profile.kind, profile.authority, "0" * 64))


def _inj_production_profile(bundle: BundleFixture) -> None:
    profile = bundle.context.profile
    production = s.EnforcementProfile("fixture-production", s.ProfileKind.PRODUCTION, profile.authority,
                                      s._profile_seal("fixture-production", s.ProfileKind.PRODUCTION, profile.authority))
    _replace_context(bundle, profile=production)


def _inj_identity_binding(bundle: BundleFixture) -> None:
    identity = bundle.context.identity.identity
    assert identity is not None
    _replace_context(bundle, identity=s._Provider("OTHER-PROFILE", identity))


def _inj_filesystem_binding(bundle: BundleFixture) -> None:
    filesystem = bundle.context.filesystem
    _replace_context(bundle, filesystem=s.TestFilesystemProvider(filesystem.real, filesystem.overrides,
                                                                   filesystem.provider_id, "OTHER-PROFILE"))


def _inj_repository_root(bundle: BundleFixture) -> None:
    identity = bundle.context.identity.identity
    assert identity is not None
    _replace_context(bundle, identity=s._Provider(bundle.profile.authority_sha256,
                                                   s.RepositoryIdentity(bundle.repo_root / "other-root", identity.branch, identity.head)))


CASE_MUTATIONS.update({
    "INJ-profile-seal-mutated": _source_mutation("INJ-profile-seal-mutated", "profile#/authority_sha256", _inj_profile_seal),
    "INJ-test-route-given-production-profile": _source_mutation("INJ-test-route-given-production-profile", "context#/profile/kind", _inj_production_profile),
    "INJ-identity-provider-bound-to-other-profile": _source_mutation("INJ-identity-provider-bound-to-other-profile", "identity#/bound_profile_sha256", _inj_identity_binding),
    "INJ-filesystem-provider-bound-to-other-profile": _source_mutation("INJ-filesystem-provider-bound-to-other-profile", "filesystem#/bound_profile_sha256", _inj_filesystem_binding),
    "INJ-repository-root-observation-mismatch": _source_mutation("INJ-repository-root-observation-mismatch", "repository#/root", _inj_repository_root),
})


def _sch_path(bundle: BundleFixture, label: str) -> tuple[Path, str]:
    if label == "CONTRACT":
        return bundle.run_root / s.AUTHORITY_PATHS["CONTRACT"], "candidate/SCENARIO_CONTRACT.json"
    if label == "SIDECAR":
        return bundle.sidecar_path, "source/SOURCE_ADMISSION.json"
    if label == "RECOVERY_MANIFEST":
        return bundle.recovery_root / "RECOVERY_MANIFEST.json", "recovery/RECOVERY_MANIFEST.json"
    if label == "RECOVERY_EVIDENCE":
        return bundle.recovery_root / "RECOVERY_EVIDENCE.json", "recovery/RECOVERY_EVIDENCE.json"
    return bundle.run_root / s.AUTHORITY_PATHS[label], "candidate/" + s.AUTHORITY_PATHS[label]


def _sch_mutation(case_id: str, label: str, selector: str, change: Callable[[dict[str, object]], None], reseal: tuple[s.ResealAuthority, ...] = ()) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        path, _ = _sch_path(bundle, label)
        value = s._load(path); change(value); path.write_bytes(s.json_bytes(value))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, reseal, selector


_SCH_EXTERNAL_RESEAL = {
    "SIDECAR": (s.ResealAuthority.SIDECAR, s.ResealAuthority.PROFILE),
    "RECOVERY_MANIFEST": (s.ResealAuthority.RECOVERY_MANIFEST,),
    "RECOVERY_EVIDENCE": (s.ResealAuthority.RECOVERY_EVIDENCE,),
}
for _sch_label in s.AUTHORITY_ORDER:
    _sch_path_hint = ("candidate/" + s.AUTHORITY_PATHS[_sch_label] if _sch_label == "CONTRACT" else "source/SOURCE_ADMISSION.json" if _sch_label == "SIDECAR" else "recovery/" + _sch_label + ".json" if _sch_label.startswith("RECOVERY_") else "candidate/" + s.AUTHORITY_PATHS[_sch_label])
    _sch_reseal = _SCH_EXTERNAL_RESEAL.get(_sch_label, ())
    _sch_schema_id = f"SCH-{_sch_label}-schema-wrong"
    CASE_MUTATIONS[_sch_schema_id] = _sch_mutation(_sch_schema_id, _sch_label, _sch_path_hint + "#/schema", lambda value: value.__setitem__("schema", "wrong"), _sch_reseal)
    _sch_shape_id = f"SCH-{_sch_label}-required-top-member-missing"
    _sch_member = next(key for key in sorted(s._TEST_TOP_KEYS[_sch_label]) if key not in {"schema", "raw_sha256"})
    CASE_MUTATIONS[_sch_shape_id] = _sch_mutation(_sch_shape_id, _sch_label, _sch_path_hint + "#/" + _sch_member, lambda value, key=_sch_member: value.pop(key), _sch_reseal)
CASE_MUTATIONS["SCH-qa-unexpected-top-member"] = _sch_mutation("SCH-qa-unexpected-top-member", "QA", "candidate/RECONSTRUCTED_EN.qa.json#/unexpected", lambda value: value.__setitem__("unexpected", True))


def _qa_mutation(case_id: str, selector: str,
                 change: Callable[[dict[str, object]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _json_mutation(case_id, "candidate/" + s.QA_NAME, selector, change)


for _qav_field in _QAV_TOP:
    _qav_case_id = f"QAV-top-{_qav_field}-missing"
    CASE_MUTATIONS[_qav_case_id] = _qa_mutation(
        _qav_case_id,
        f"candidate/{s.QA_NAME}#/{_qav_field}",
        lambda value, key=_qav_field: value.pop(key),
    )
CASE_MUTATIONS["QAV-top-extra"] = _qa_mutation(
    "QAV-top-extra", f"candidate/{s.QA_NAME}#/unexpected",
    lambda value: value.__setitem__("unexpected", True),
)
CASE_MUTATIONS["QAV-state-promoted"] = _qa_mutation(
    "QAV-state-promoted", f"candidate/{s.QA_NAME}#/state",
    lambda value: value.__setitem__("state", "accepted"),
)
QAV_A_CASE_IDS = frozenset(
    [f"QAV-top-{field}-missing" for field in _QAV_TOP]
    + ["QAV-top-extra", "QAV-state-promoted"]
)
assert len(QAV_A_CASE_IDS) == 25 and QAV_A_CASE_IDS <= CASE_MUTATIONS.keys()

_QAV_AUTHORITY_FIELDS = (
    ("contract", "contract_sha256"),
    ("source", "source_sha256"),
    ("recovery-manifest", "recovery_manifest_sha256"),
    ("recovery-evidence", "recovery_evidence_sha256"),
)
_QAV_SCALAR_FIELDS = (
    "page_count", "handout_count", "block_count", "asset_count",
    "contact_sheet_count", "navigation_anchor_count", "referenced_asset_count",
    "unreferenced_asset_count", "open_blocker_count",
)
for _qav_name, _qav_field in _QAV_AUTHORITY_FIELDS:
    _qav_case_id = f"QAV-authority-{_qav_name}"
    CASE_MUTATIONS[_qav_case_id] = _qa_mutation(
        _qav_case_id,
        f"candidate/{s.QA_NAME}#/{_qav_field}",
        lambda value, field=_qav_field: value.__setitem__(field, "0" * 64),
    )
for _qav_field in _QAV_SCALAR_FIELDS:
    _qav_case_id = f"QAV-scalar-{_qav_field}-wrong"
    CASE_MUTATIONS[_qav_case_id] = _qa_mutation(
        _qav_case_id,
        f"candidate/{s.QA_NAME}#/{_qav_field}",
        lambda value, field=_qav_field: value.__setitem__(field, value[field] + 1),
    )
QAV_B_CASE_IDS = frozenset(
    [f"QAV-authority-{name}" for name, _field in _QAV_AUTHORITY_FIELDS]
    + [f"QAV-scalar-{field}-wrong" for field in _QAV_SCALAR_FIELDS]
)
assert len(QAV_B_CASE_IDS) == 13 and QAV_B_CASE_IDS <= CASE_MUTATIONS.keys()

for _qav_count_key in _QAV_COUNT_KEYS:
    for _qav_count_kind in ("missing", "wrong"):
        _qav_case_id = f"QAV-counts-{_qav_count_key}-{_qav_count_kind}"
        CASE_MUTATIONS[_qav_case_id] = _qa_mutation(
            _qav_case_id,
            f"candidate/{s.QA_NAME}#/counts/{_qav_count_key}",
            (lambda value, key=_qav_count_key: value["counts"].pop(key))
            if _qav_count_kind == "missing"
            else (lambda value, key=_qav_count_key: value["counts"].__setitem__(key, value["counts"][key] + 1)),
        )
QAV_C_CASE_IDS = frozenset(
    f"QAV-counts-{count_key}-{kind}"
    for count_key in _QAV_COUNT_KEYS
    for kind in ("missing", "wrong")
)
assert len(QAV_C_CASE_IDS) == 28 and QAV_C_CASE_IDS <= CASE_MUTATIONS.keys()


CASE_MUTATIONS.update({
    "QAV-gate-asset_conservation-missing": _qa_mutation("QAV-gate-asset_conservation-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation", lambda value: value["gate_results"].pop("asset_conservation")),
    "QAV-gate-contact_sheet_coverage-missing": _qa_mutation("QAV-gate-contact_sheet_coverage-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage", lambda value: value["gate_results"].pop("contact_sheet_coverage")),
    "QAV-gate-navigation_anchors-missing": _qa_mutation("QAV-gate-navigation_anchors-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors", lambda value: value["gate_results"].pop("navigation_anchors")),
    "QAV-gate-page_1_5_modes-missing": _qa_mutation("QAV-gate-page_1_5_modes-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes", lambda value: value["gate_results"].pop("page_1_5_modes")),
    "QAV-gate-page_coverage-missing": _qa_mutation("QAV-gate-page_coverage-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage", lambda value: value["gate_results"].pop("page_coverage")),
    "QAV-gate-promotion-missing": _qa_mutation("QAV-gate-promotion-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion", lambda value: value["gate_results"].pop("promotion")),
    "QAV-gate-recovery_admission-missing": _qa_mutation("QAV-gate-recovery_admission-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission", lambda value: value["gate_results"].pop("recovery_admission")),
    "QAV-gate-source_identity-missing": _qa_mutation("QAV-gate-source_identity-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity", lambda value: value["gate_results"].pop("source_identity")),
    "QAV-gate-visual_review-missing": _qa_mutation("QAV-gate-visual_review-missing", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review", lambda value: value["gate_results"].pop("visual_review")),
    "QAV-gate-asset_conservation-wrong": _qa_mutation("QAV-gate-asset_conservation-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation", lambda value: value["gate_results"].__setitem__("asset_conservation", "needs_review")),
    "QAV-gate-contact_sheet_coverage-wrong": _qa_mutation("QAV-gate-contact_sheet_coverage-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage", lambda value: value["gate_results"].__setitem__("contact_sheet_coverage", "needs_review")),
    "QAV-gate-navigation_anchors-wrong": _qa_mutation("QAV-gate-navigation_anchors-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors", lambda value: value["gate_results"].__setitem__("navigation_anchors", "needs_review")),
    "QAV-gate-page_coverage-wrong": _qa_mutation("QAV-gate-page_coverage-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage", lambda value: value["gate_results"].__setitem__("page_coverage", "needs_review")),
    "QAV-gate-recovery_admission-wrong": _qa_mutation("QAV-gate-recovery_admission-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission", lambda value: value["gate_results"].__setitem__("recovery_admission", "needs_review")),
    "QAV-gate-source_identity-wrong": _qa_mutation("QAV-gate-source_identity-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity", lambda value: value["gate_results"].__setitem__("source_identity", "needs_review")),
    "QAV-gate-page_1_5_modes-closed": _qa_mutation("QAV-gate-page_1_5_modes-closed", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes", lambda value: value["gate_results"].__setitem__("page_1_5_modes", "pass")),
    "QAV-gate-promotion-closed": _qa_mutation("QAV-gate-promotion-closed", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion", lambda value: value["gate_results"].__setitem__("promotion", "accepted")),
    "QAV-gate-visual_review-closed": _qa_mutation("QAV-gate-visual_review-closed", "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review", lambda value: value["gate_results"].__setitem__("visual_review", "pass")),
    "QAV-historical-material-true": _qa_mutation("QAV-historical-material-true", "candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened", lambda value: value.__setitem__("historical_material_opened", True)),
    "QAV-main-scripts-invoked-true": _qa_mutation("QAV-main-scripts-invoked-true", "candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked", lambda value: value.__setitem__("main_scripts_invoked", True)),
})
QAV_D1_CASE_IDS = frozenset("QAV-" + name for name, _code in _QAV_D1_CASES)
assert len(QAV_D1_CASE_IDS) == 20 and QAV_D1_CASE_IDS <= CASE_MUTATIONS.keys()
CASE_MUTATIONS.update({
    "QAV-inventory-rule-wrong": _qa_mutation("QAV-inventory-rule-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule", lambda value: value.__setitem__("output_inventory_rule", "all_regular_except_qa")),
    "QAV-inventory-count-wrong": _qa_mutation("QAV-inventory-count-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count", lambda value: value.__setitem__("output_inventory_count", 500)),
    "QAV-inventory-digest-wrong": _qa_mutation("QAV-inventory-digest-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256", lambda value: value.__setitem__("output_inventory_sha256", "0" * 64)),
    "QAV-inventory-array-wrong": _qa_mutation("QAV-inventory-array-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md", lambda value: value.__setitem__("output_inventory", [row for row in value["output_inventory"] if row["path"] != "RECONSTRUCTED_EN.md"])),
})
QAV_D2_CASE_IDS = frozenset(("QAV-inventory-rule-wrong", "QAV-inventory-count-wrong", "QAV-inventory-digest-wrong", "QAV-inventory-array-wrong"))
assert QAV_D2_CASE_IDS <= CASE_MUTATIONS.keys()


def _inventory_mutation(case_id: str, selector: str, change: Callable[[BundleFixture, dict[str, object]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        path = bundle.run_root / s.QA_NAME
        value = s._load(path)
        change(bundle, value)
        path.write_bytes(s.json_bytes(value))
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, (), selector


def _inventory_row(value: dict[str, object], path: str) -> dict[str, object]:
    return next(row for row in value["output_inventory"] if row["path"] == path)


def _inventory_remove(path: str) -> Callable[[BundleFixture, dict[str, object]], None]:
    return lambda _bundle, value: value.__setitem__("output_inventory", [row for row in value["output_inventory"] if row["path"] != path])


CASE_MUTATIONS.update({
    "INV-ordinary-row-missing": _inventory_mutation("INV-ordinary-row-missing", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md", _inventory_remove("RECONSTRUCTED_EN.md")),
    "INV-evidence-row-missing": _inventory_mutation("INV-evidence-row-missing", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/evidence/COMMANDS.json", _inventory_remove("evidence/COMMANDS.json")),
    "INV-sheet-row-missing": _inventory_mutation("INV-sheet-row-missing", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png", _inventory_remove("renders/contact_sheets/sheet-001.png")),
    "INV-stale-extra-path": _inventory_mutation("INV-stale-extra-path", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-", lambda _bundle, value: value["output_inventory"].append({"path": "stale-extra.bin", "bytes": 0, "sha256": "A" * 64})),
    "INV-duplicate-path": _inventory_mutation("INV-duplicate-path", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/1/path", lambda _bundle, value: value["output_inventory"].append(dict(value["output_inventory"][0]))),
    "INV-qa-included": _inventory_mutation("INV-qa-included", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-", lambda bundle, value: value["output_inventory"].append({"path": s.QA_NAME, "bytes": (bundle.run_root / s.QA_NAME).stat().st_size, "sha256": s.sha256_file(bundle.run_root / s.QA_NAME)})),
    "INV-cardinality-wrong": _inventory_mutation("INV-cardinality-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count", lambda _bundle, value: value.__setitem__("output_inventory_count", 500)),
    "INV-order-nonordinal": _inventory_mutation("INV-order-nonordinal", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory", lambda _bundle, value: value.__setitem__("output_inventory", list(reversed(value["output_inventory"])))),
    "INV-row-bytes-wrong": _inventory_mutation("INV-row-bytes-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/bytes", lambda _bundle, value: value["output_inventory"][0].__setitem__("bytes", 0)),
    "INV-row-hash-wrong": _inventory_mutation("INV-row-hash-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256", lambda _bundle, value: value["output_inventory"][0].__setitem__("sha256", "0" * 64)),
    "INV-row-hash-lowercase": _inventory_mutation("INV-row-hash-lowercase", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256", lambda _bundle, value: value["output_inventory"][0].__setitem__("sha256", value["output_inventory"][0]["sha256"].lower())),
    "INV-digest-wrong": _inventory_mutation("INV-digest-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256", lambda _bundle, value: value.__setitem__("output_inventory_sha256", "0" * 64)),
    "INV-path-backslash": _inventory_mutation("INV-path-backslash", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path", lambda _bundle, value: value["output_inventory"][0].__setitem__("path", "pages\\page-001.md")),
    "INV-path-absolute-or-drive": _inventory_mutation("INV-path-absolute-or-drive", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path", lambda _bundle, value: value["output_inventory"][0].__setitem__("path", "C:/candidate/file")),
    "INV-path-parent-segment": _inventory_mutation("INV-path-parent-segment", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path", lambda _bundle, value: value["output_inventory"][0].__setitem__("path", "pages/../page-001.md")),
    "INV-path-leading-dot-slash": _inventory_mutation("INV-path-leading-dot-slash", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path", lambda _bundle, value: value["output_inventory"][0].__setitem__("path", "./pages/page-001.md")),
    "INV-row-shape-wrong": _inventory_mutation("INV-row-shape-wrong", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/unexpected", lambda _bundle, value: value["output_inventory"][0].__setitem__("unexpected", True)),
    "INV-live-file-changed-behind-row": _source_mutation("INV-live-file-changed-behind-row", "candidate/RECONSTRUCTED_EN.md#/live-bytes", lambda bundle: (bundle.run_root / "RECONSTRUCTED_EN.md").write_bytes(b"X" + (bundle.run_root / "RECONSTRUCTED_EN.md").read_bytes()[1:])),
})


def _pag_json(case_id: str, selector: str, change: Callable[[dict[str, object]], None],
              reseal: tuple[s.ResealAuthority, ...] = (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA)) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _json_mutation(case_id, "candidate/evidence/PAGE_PROVENANCE.json" if case_id.startswith("PAG-page") or case_id.startswith("PAG-engine") or case_id.startswith("PAG-role") or case_id.startswith("PAG-contract") or case_id.startswith("PAG-markdown") or case_id.startswith("PAG-render") else "candidate/evidence/CONTENT_PROVENANCE.json", selector, change, reseal)


def _pag_page(case_id: str, selector: str, change: Callable[[list[dict[str, object]]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _pag_json(case_id, selector, lambda value: change(value["rows"]))


def _pag_content(case_id: str, selector: str, change: Callable[[list[dict[str, object]]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _pag_json(case_id, selector, lambda value: change(value["rows"]))


def _pag_file(case_id: str, selector: str, relative: str, change: Callable[[Path], None],
              reseal: tuple[s.ResealAuthority, ...]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        change(bundle.run_root / relative)
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, reseal, selector


CASE_MUTATIONS.update({
    "PAG-page-row-missing": _pag_page("PAG-page-row-missing", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0", lambda rows: rows.pop(0)),
    "PAG-page-row-duplicate": _pag_page("PAG-page-row-duplicate", "candidate/evidence/PAGE_PROVENANCE.json#/rows/-", lambda rows: rows.append(dict(rows[0]))),
    "PAG-page-number-wrong": _pag_page("PAG-page-number-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_number", lambda rows: rows[0].__setitem__("page_number", 0)),
    "PAG-page-id-wrong": _pag_page("PAG-page-id-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_id", lambda rows: rows[0].__setitem__("page_id", "wrong")),
    "PAG-engine-index-wrong": _pag_page("PAG-engine-index-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/engine_page_idx", lambda rows: rows[0].__setitem__("engine_page_idx", 1)),
    "PAG-role-wrong": _pag_page("PAG-role-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_role", lambda rows: rows[0].__setitem__("contract_role", "wrong")),
    "PAG-contract-mode-wrong": _pag_page("PAG-contract-mode-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_content_mode", lambda rows: rows[0].__setitem__("contract_content_mode", "wrong")),
    "PAG-markdown-path-wrong": _pag_page("PAG-markdown-path-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/path", lambda rows: rows[0]["markdown"].__setitem__("path", "wrong.md")),
    "PAG-markdown-bytes-wrong": _pag_page("PAG-markdown-bytes-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes", lambda rows: rows[0]["markdown"].__setitem__("bytes", 0)),
    "PAG-markdown-hash-wrong": _pag_page("PAG-markdown-hash-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256", lambda rows: rows[0]["markdown"].__setitem__("sha256", "0" * 64)),
    "PAG-render-path-wrong": _pag_page("PAG-render-path-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/path", lambda rows: rows[0]["render"].__setitem__("path", "wrong.png")),
    "PAG-render-bytes-wrong": _pag_page("PAG-render-bytes-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/bytes", lambda rows: rows[0]["render"].__setitem__("bytes", 0)),
    "PAG-render-hash-wrong": _pag_page("PAG-render-hash-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/sha256", lambda rows: rows[0]["render"].__setitem__("sha256", "0" * 64)),
    "PAG-render-page-number-wrong": _pag_page("PAG-render-page-number-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/page_number", lambda rows: rows[0]["render"].__setitem__("page_number", 2)),
    "PAG-render-dimensions-wrong": _pag_page("PAG-render-dimensions-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dimensions", lambda rows: rows[0]["render"].__setitem__("dimensions", [0, 0])),
    "PAG-render-dpi-wrong": _pag_page("PAG-render-dpi-wrong", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dpi", lambda rows: rows[0]["render"].__setitem__("dpi", 72)),
    "PAG-live-markdown-missing": _pag_file("PAG-live-markdown-missing", "candidate/pages/page-002.md#/physical-entry", "pages/page-002.md", lambda path: path.unlink(), ()),
    "PAG-live-render-missing": _pag_file("PAG-live-render-missing", "candidate/renders/source/page-002.png#/physical-entry", "renders/source/page-002.png", lambda path: path.unlink(), ()),
    "PAG-source-page-marker-wrong": _pag_file("PAG-source-page-marker-wrong", "candidate/pages/page-001.md#/source-page-marker", "pages/page-001.md", lambda path: path.write_bytes(path.read_bytes().replace(b"source-page:1", b"source-page:0")), (s.ResealAuthority.PAGE_PROVENANCE, s.ResealAuthority.INVENTORY, s.ResealAuthority.QA)),
    "PAG-render-marker-wrong": _pag_file("PAG-render-marker-wrong", "candidate/pages/page-001.md#/render-marker", "pages/page-001.md", lambda path: path.write_bytes(path.read_bytes().replace(b"render:page-001.png", b"render:wrong.png")), (s.ResealAuthority.PAGE_PROVENANCE, s.ResealAuthority.INVENTORY, s.ResealAuthority.QA)),
    "PAG-master-concatenation-wrong": _pag_file("PAG-master-concatenation-wrong", "candidate/RECONSTRUCTED_EN.md#/concatenation", "RECONSTRUCTED_EN.md", lambda path: path.write_bytes(b"wrong\n"), (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA)),
    "PAG-content-orphan": _pag_content("PAG-content-orphan", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/page_number", lambda rows: rows[0].__setitem__("page_number", 0)),
    "PAG-content-duplicate": _pag_content("PAG-content-duplicate", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/block_id", lambda rows: rows[1].__setitem__("block_id", rows[0]["block_id"])),
    "PAG-content-order-wrong": _pag_content("PAG-content-order-wrong", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/order", lambda rows: rows[1].__setitem__("order", 9)),
    "PAG-content-predecessor-wrong": _pag_content("PAG-content-predecessor-wrong", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/predecessor_id", lambda rows: rows[1].__setitem__("predecessor_id", "wrong")),
    "PAG-content-successor-wrong": _pag_content("PAG-content-successor-wrong", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/successor_id", lambda rows: rows[0].__setitem__("successor_id", "wrong")),
    "PAG-content-operation-fabricated": _pag_content("PAG-content-operation-fabricated", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/operations", lambda rows: rows[0].__setitem__("operations", ["fabricated"])),
    "PAG-content-asset-link-fabricated": _pag_content("PAG-content-asset-link-fabricated", "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/asset_ids", lambda rows: rows[0].__setitem__("asset_ids", ["asset-001"])),
})


def _nav_mutation(case_id: str, selector: str,
                  change: Callable[[list[dict[str, object]]], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _json_mutation(case_id, "candidate/evidence/NAVIGATION_INVENTORY.json", selector,
                          lambda value: change(value["rows"]),
                          (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA))


CASE_MUTATIONS.update({
    "NAV-row-missing": _nav_mutation("NAV-row-missing", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0", lambda rows: rows.pop(0)),
    "NAV-anchor-duplicate": _nav_mutation("NAV-anchor-duplicate", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/anchor_id", lambda rows: rows[1].__setitem__("anchor_id", rows[0]["anchor_id"])),
    "NAV-anchor-id-wrong": _nav_mutation("NAV-anchor-id-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/anchor_id", lambda rows: rows[0].__setitem__("anchor_id", "wrong-anchor")),
    "NAV-source-page-wrong": _nav_mutation("NAV-source-page-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_page_number", lambda rows: rows[0].__setitem__("source_page_number", 0)),
    "NAV-engine-index-wrong": _nav_mutation("NAV-engine-index-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/engine_page_idx", lambda rows: rows[0].__setitem__("engine_page_idx", 1)),
    "NAV-first-previous-nonnull": _nav_mutation("NAV-first-previous-nonnull", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/previous_anchor", lambda rows: rows[0].__setitem__("previous_anchor", "page-001")),
    "NAV-last-next-nonnull": _nav_mutation("NAV-last-next-nonnull", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/123/next_anchor", lambda rows: rows[123].__setitem__("next_anchor", "page-124")),
    "NAV-middle-previous-wrong": _nav_mutation("NAV-middle-previous-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/previous_anchor", lambda rows: rows[1].__setitem__("previous_anchor", "page-124")),
    "NAV-middle-next-wrong": _nav_mutation("NAV-middle-next-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor", lambda rows: rows[1].__setitem__("next_anchor", "page-124")),
    "NAV-dangling-link": _nav_mutation("NAV-dangling-link", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor", lambda rows: rows[1].__setitem__("next_anchor", "page-999")),
    "NAV-markdown-path-wrong": _nav_mutation("NAV-markdown-path-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/page_markdown_path", lambda rows: rows[0].__setitem__("page_markdown_path", "pages/wrong.md")),
    "NAV-render-path-wrong": _nav_mutation("NAV-render-path-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_path", lambda rows: rows[0].__setitem__("source_render_path", "renders/source/wrong.png")),
    "NAV-render-hash-wrong": _nav_mutation("NAV-render-hash-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_sha256", lambda rows: rows[0].__setitem__("source_render_sha256", "0" * 64)),
    "NAV-role-wrong": _nav_mutation("NAV-role-wrong", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/contract_role", lambda rows: rows[0].__setitem__("contract_role", "wrong")),
    "NAV-closure-promoted": _nav_mutation("NAV-closure-promoted", "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/closure_state", lambda rows: rows[0].__setitem__("closure_state", "closed")),
})


def _ast_mutation(case_id: str, selector: str, change: Callable[[dict[str, object]], None],
                  reseal: tuple[s.ResealAuthority, ...] = (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA)) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _json_mutation(case_id, "candidate/evidence/ASSET_PROVENANCE.json", selector, change, reseal)


def _ast_rows(case_id: str, selector: str, change: Callable[[list[dict[str, object]]], None],
              reseal: tuple[s.ResealAuthority, ...] = (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA)) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    return _ast_mutation(case_id, selector, lambda value: change(value["rows"]), reseal)


def _ast_live(case_id: str, selector: str, change: Callable[[Path], None]) -> tuple[Callable[[BundleFixture], None], tuple[s.ResealAuthority, ...], str]:
    def mutate(bundle: BundleFixture) -> None:
        change(bundle.run_root / "engine/payload-001.bin")
    mutate.__name__ = "mutate_" + case_id.replace("-", "_")
    return mutate, (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA), selector


CASE_MUTATIONS.update({
    "AST-row-missing": _ast_rows("AST-row-missing", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0", lambda rows: rows.pop(0)),
    "AST-id-duplicate": _ast_rows("AST-id-duplicate", "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/asset_id", lambda rows: rows[1].__setitem__("asset_id", rows[0]["asset_id"])),
    "AST-path-duplicate": _ast_rows("AST-path-duplicate", "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/engine_relative_path", lambda rows: rows[1].__setitem__("engine_relative_path", rows[0]["engine_relative_path"])),
    "AST-hash-duplicate": _ast_rows("AST-hash-duplicate", "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/sha256", lambda rows: rows[1].__setitem__("sha256", rows[0]["sha256"])),
    "AST-live-bytes-wrong": _ast_live("AST-live-bytes-wrong", "candidate/engine/payload-001.bin#/bytes", lambda path: path.write_bytes(path.read_bytes() + b"!")),
    "AST-live-hash-wrong": _ast_live("AST-live-hash-wrong", "candidate/engine/payload-001.bin#/sha256", lambda path: path.write_bytes(b"X" + path.read_bytes()[1:])),
    "AST-engine-path-missing": _ast_rows("AST-engine-path-missing", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path", lambda rows: rows[0].__setitem__("engine_relative_path", "engine/missing.bin")),
    "AST-engine-path-wrong": _ast_rows("AST-engine-path-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path", lambda rows: rows[0].__setitem__("engine_relative_path", "engine/payload-205.bin")),
    "AST-recovery-binding-wrong": _ast_rows("AST-recovery-binding-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/recovery_manifest_binding", lambda rows: rows[0].__setitem__("recovery_manifest_binding", "payload/wrong.bin")),
    "AST-reference-total-wrong": _ast_mutation("AST-reference-total-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/referenced", lambda value: value.__setitem__("referenced", 111)),
    "AST-unreferenced-count-wrong": _ast_mutation("AST-unreferenced-count-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/unreferenced", lambda value: value.__setitem__("unreferenced", 91)),
    "AST-reference-count-outside-zero-one": _ast_rows("AST-reference-count-outside-zero-one", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_count", lambda rows: rows[0].__setitem__("markdown_reference_count", 2)),
    "AST-occurrence-missing": _ast_rows("AST-occurrence-missing", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations", lambda rows: rows[0].__setitem__("markdown_reference_locations", [])),
    "AST-occurrence-duplicate": _ast_rows("AST-occurrence-duplicate", "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/markdown_reference_locations", lambda rows: rows[1].__setitem__("markdown_reference_locations", [dict(rows[0]["markdown_reference_locations"][0])])),
    "AST-markdown-path-wrong": _ast_rows("AST-markdown-path-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/markdown_path", lambda rows: rows[0]["markdown_reference_locations"][0].__setitem__("markdown_path", "pages/wrong.md")),
    "AST-target-absent-from-markdown": _ast_rows("AST-target-absent-from-markdown", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/target", lambda rows: rows[0]["markdown_reference_locations"][0].__setitem__("target", "../engine/missing.bin")),
    "AST-ownership-nonnull": _ast_rows("AST-ownership-nonnull", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/ownership", lambda rows: rows[0].__setitem__("ownership", "claimed")),
    "AST-closure-promoted": _ast_rows("AST-closure-promoted", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/closure_state", lambda rows: rows[0].__setitem__("closure_state", "closed")),
    "AST-finding-wrong": _ast_rows("AST-finding-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/finding", lambda rows: rows[0].__setitem__("finding", "wrong")),
    "AST-engine-image-cardinality-wrong": _ast_rows("AST-engine-image-cardinality-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_evidence/engine_image_count", lambda rows: rows[0]["engine_evidence"].__setitem__("engine_image_count", 203)),
    "AST-mime-wrong": _ast_rows("AST-mime-wrong", "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/mime", lambda rows: rows[0].__setitem__("mime", "image/png")),
})


def _commands_mutation(case_id: str, selector: str,
                       change: Callable[[dict[str, object]], None]) -> None:
    """Mutate one concrete COMMANDS v3 selector, then reseal its transports."""
    CASE_MUTATIONS[case_id] = _json_mutation(
        case_id,
        "candidate/evidence/COMMANDS.json",
        selector,
        change,
        (s.ResealAuthority.INVENTORY, s.ResealAuthority.QA),
    )


_commands_mutation("CMD-action-missing", "candidate/evidence/COMMANDS.json#/actions/2",
                   lambda value: value["actions"].pop(2))
_commands_mutation("CMD-action-duplicate", "candidate/evidence/COMMANDS.json#/actions/-",
                   lambda value: value["actions"].append("contact_sheets"))
_commands_mutation("CMD-action-extra", "candidate/evidence/COMMANDS.json#/actions/-",
                   lambda value: value["actions"].append("external"))
_commands_mutation("CMD-action-reordered", "candidate/evidence/COMMANDS.json#/actions/0",
                   lambda value: value["actions"].__setitem__(slice(0, 2), ["remediate", "preflight"]))
_commands_mutation("CMD-state-promoted", "candidate/evidence/COMMANDS.json#/state",
                   lambda value: value.__setitem__("state", "candidate_accepted"))
for _field in _CMD_FLAGS:
    _commands_mutation(f"CMD-flag-{_field}-missing", f"candidate/evidence/COMMANDS.json#/flags/{_field}",
                       lambda value, field=_field: value["flags"].pop(field))
    _commands_mutation(f"CMD-flag-{_field}-true", f"candidate/evidence/COMMANDS.json#/flags/{_field}",
                       lambda value, field=_field: value["flags"].__setitem__(field, True))
for _field in ("source_flag", "run_root_flag", "source_relative_path"):
    _commands_mutation(f"CMD-argument-{_field}-missing", f"candidate/evidence/COMMANDS.json#/records/0/{_field}",
                       lambda value, field=_field: value["records"][0].pop(field))
    _commands_mutation(f"CMD-argument-{_field}-wrong", f"candidate/evidence/COMMANDS.json#/records/0/{_field}",
                       lambda value, field=_field: value["records"][0].__setitem__(field, "--wrong"))
_commands_mutation("CMD-external-locator-used", "candidate/evidence/COMMANDS.json#/external_locator",
                   lambda value: value.__setitem__("external_locator", "https://external.invalid/source"))
for _count_key in _CMD_COUNTS:
    _commands_mutation(
        f"CMD-count-{_count_key}-missing",
        f"candidate/evidence/COMMANDS.json#/counts/{_count_key}",
        lambda value, key=_count_key: value["counts"].pop(key),
    )
    _commands_mutation(
        f"CMD-count-{_count_key}-wrong",
        f"candidate/evidence/COMMANDS.json#/counts/{_count_key}",
        lambda value, key=_count_key: value["counts"].__setitem__(key, value["counts"][key] + 1),
    )
# A distinct callable for the approved cross-family CMD/REG physical-state alias.
_commands_mutation(
    "REG-P1-missing-enforcement",
    "candidate/evidence/COMMANDS.json#/counts/pages",
    lambda value: value["counts"].__setitem__("pages", 125),
)
CMD_A_CASE_IDS = frozenset(CASE_MUTATIONS).intersection(
    {"CMD-action-missing", "CMD-action-duplicate", "CMD-action-extra", "CMD-action-reordered", "CMD-state-promoted",
     "CMD-external-locator-used",
     *(f"CMD-flag-{field}-{kind}" for field in _CMD_FLAGS for kind in ("missing", "true")),
     *(f"CMD-argument-{field}-{kind}" for field in ("source_flag", "run_root_flag", "source_relative_path") for kind in ("missing", "wrong"))}
)
assert len(CMD_A_CASE_IDS) == 24
CMD_B_CASE_IDS = frozenset(
    f"CMD-count-{count_key}-{kind}"
    for count_key in _CMD_COUNTS
    for kind in ("missing", "wrong")
)
assert CMD_B_CASE_IDS <= CASE_MUTATIONS.keys() and len(CMD_B_CASE_IDS) == 22

# CMD-C keeps one real COMMANDS v3 selector per callable.  These deliberately
# retain transport-only reseals: the semantic error itself is never repaired.
_commands_mutation("CMD-sheet-count-wrong", "candidate/evidence/COMMANDS.json#/sheets", lambda value: value["sheets"].pop())
_commands_mutation("CMD-sheet-coverage-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/pages/-", lambda value: value["sheets"][0]["pages"].append(125))
_commands_mutation("CMD-sheet-missing", "candidate/evidence/COMMANDS.json#/sheets/30", lambda value: value["sheets"].__setitem__(30, dict(value["sheets"][0])))
_commands_mutation("CMD-sheet-duplicate", "candidate/evidence/COMMANDS.json#/sheets/1", lambda value: value["sheets"].__setitem__(1, dict(value["sheets"][0])))
_commands_mutation("CMD-sheet-id-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/sheet_id", lambda value: value["sheets"][0].__setitem__("sheet_id", "wrong-sheet"))
_commands_mutation("CMD-sheet-path-sequence-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/path", lambda value: value["sheets"][0].__setitem__("path", "renders/contact_sheets/sheet-002.png"))
_commands_mutation("CMD-sheet-grid-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/grid", lambda value: value["sheets"][0].__setitem__("grid", [1, 4]))
_commands_mutation("CMD-sheet-hash-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/sha256", lambda value: value["sheets"][0].__setitem__("sha256", "0" * 64))
_commands_mutation("CMD-flattened-page-missing", "candidate/evidence/COMMANDS.json#/sheets/0/pages/0", lambda value: value["sheets"][0]["pages"].__setitem__(0, 5))
_commands_mutation("CMD-flattened-page-duplicate", "candidate/evidence/COMMANDS.json#/sheets/1/pages/0", lambda value: value["sheets"][1]["pages"].__setitem__(0, 4))
_commands_mutation("CMD-flattened-page-order-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/pages", lambda value: value["sheets"][0].__setitem__("pages", [2, 1, 3, 4]))
_commands_mutation("CMD-render-path-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/path", lambda value: value["sheets"][0]["page_renders"][0].__setitem__("path", "renders/source/page-002.png"))
_commands_mutation("CMD-render-hash-wrong", "candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/sha256", lambda value: value["sheets"][0]["page_renders"][0].__setitem__("sha256", "0" * 64))
_commands_mutation("CMD-page-render-mapping-disagrees", "candidate/evidence/COMMANDS.json#/page_renders/0/page_number", lambda value: value["page_renders"][0].__setitem__("page_number", 2))
_commands_mutation("CMD-verify-determinism-false", "candidate/evidence/COMMANDS.json#/verify_deterministic", lambda value: value.__setitem__("verify_deterministic", False))
CMD_C_CASE_IDS = frozenset(f"CMD-{name}" for name, _code in _CMD_C)
assert CMD_C_CASE_IDS <= CASE_MUTATIONS.keys() and len(CMD_C_CASE_IDS) == 15

CASES = tuple(_case(f"{family}-{name}", code) for family in FAMILY_COUNTS for name, code in _EXACT[family])
assert len(CASES) == 368 and len({case.case_id for case in CASES}) == 368
assert len({id(case.mutate) for case in CASES}) == 368
_CASE_BY_ID = {case.case_id: case for case in CASES}
_QA_ALIAS_CASE_IDS = (
    "SCH-QA-required-top-member-missing", "QAV-top-asset_count-missing",
    "SCH-qa-unexpected-top-member", "QAV-top-extra",
)
assert len({_CASE_BY_ID[case_id].mutate for case_id in _QA_ALIAS_CASE_IDS}) == 4
assert tuple(_CASE_BY_ID[case_id].mutate.__name__ for case_id in _QA_ALIAS_CASE_IDS) == tuple(
    "mutate_" + case_id.replace("-", "_") for case_id in _QA_ALIAS_CASE_IDS
)
_CROSS_FAMILY_ALIAS_PAIRS = (
    ("SCH-QA-required-top-member-missing", "QAV-top-asset_count-missing"),
    ("SCH-qa-unexpected-top-member", "QAV-top-extra"),
    ("INV-cardinality-wrong", "QAV-inventory-count-wrong"),
    ("INV-digest-wrong", "QAV-inventory-digest-wrong"),
    ("INV-ordinary-row-missing", "QAV-inventory-array-wrong"),
    ("CMD-count-pages-wrong", "REG-P1-missing-enforcement"),
)
assert len(_CROSS_FAMILY_ALIAS_PAIRS) == 6
_ALIAS_MEMBERS = tuple(case_id for pair in _CROSS_FAMILY_ALIAS_PAIRS for case_id in pair)
assert len(_ALIAS_MEMBERS) == 12 and len(set(_ALIAS_MEMBERS)) == 12
assert len({_CASE_BY_ID[case_id].mutate for case_id in _ALIAS_MEMBERS}) == 12
assert "REG-P1-stale-metadata" not in _ALIAS_MEMBERS


def _snapshot(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): s.sha256_file(path)
            for path in root.rglob("*") if path.is_file() and not path.is_symlink()}


def reseal_transport(bundle: BundleFixture, case: s.MutationCase) -> tuple[str, ...]:
    """Perform only the literal transport reseals declared by this case."""
    changed: list[str] = []
    if s.ResealAuthority.SIDECAR in case.reseal:
        path, value = _sidecar(bundle)
        _write_sidecar(path, value)
        changed.append("sidecar#/raw_sha256")
    if s.ResealAuthority.CONTRACT in case.reseal:
        changed.append(_contract_reseal(bundle))
    if s.ResealAuthority.PAGE_PROVENANCE in case.reseal:
        path = bundle.run_root / s.AUTHORITY_PATHS["PAGE_PROVENANCE"]
        value = s._load(path); row = value["rows"][0]
        markdown = bundle.run_root / row["markdown"]["path"]
        row["markdown"]["bytes"] = markdown.stat().st_size
        row["markdown"]["sha256"] = s.sha256_file(markdown)
        row["raw_markdown_sha256"] = s.sha256_file(markdown)
        path.write_bytes(s.json_bytes(value))
        changed.extend(("candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256", "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/raw_markdown_sha256"))
    for authority, filename, identity_key in ((s.ResealAuthority.RECOVERY_MANIFEST, "RECOVERY_MANIFEST.json", "recovery_manifest_sha256"),
                                              (s.ResealAuthority.RECOVERY_EVIDENCE, "RECOVERY_EVIDENCE.json", "recovery_evidence_sha256")):
        if authority in case.reseal:
            path = bundle.recovery_root / filename; value = s._load(path); value.pop("raw_sha256", None)
            value["raw_sha256"] = s.sha256_bytes(s.json_bytes(value)); path.write_bytes(s.json_bytes(value))
            identity_path = bundle.run_root / s.AUTHORITY_PATHS["SOURCE_IDENTITY"]
            identity = s._load(identity_path); identity[identity_key] = s.sha256_file(path); identity_path.write_bytes(s.json_bytes(identity))
            changed.extend((f"recovery/{filename}#/raw_sha256", f"candidate/SOURCE_IDENTITY.json#/{identity_key}"))
    if s.ResealAuthority.INVENTORY in case.reseal or s.ResealAuthority.QA in case.reseal:
        qa_path = bundle.run_root / s.QA_NAME; qa = s._load(qa_path); inventory = s.candidate_records(bundle.run_root, {s.QA_NAME})
        qa.update({"output_inventory": inventory, "output_inventory_count": len(inventory), "output_inventory_sha256": s.manifest_digest(inventory)})
        qa_path.write_bytes(s.json_bytes(qa)); changed.extend(("candidate/RECONSTRUCTED_EN.qa.json#/output_inventory", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"))
    return tuple(changed)


def apply_case(case: s.MutationCase, bundle: BundleFixture) -> s.MutationAudit:
    before = _snapshot(bundle.repo_root)
    before_context = repr(bundle.context)
    before_identity = repr(bundle.context.identity.identity)
    before_filesystem = repr(bundle.context.filesystem)
    before_paths = (bundle.contract_path, bundle.source_path, bundle.recovery_root, bundle.run_root)
    def selector_hash(paths: tuple[Path, Path, Path, Path]) -> str:
        contract, source, recovery, run = paths
        if case.semantic_selector.startswith("contract#"):
            value = contract.as_posix() if case.semantic_selector == "contract#/path" else (s.sha256_file(contract) if contract.is_file() else "missing")
        elif case.semantic_selector.startswith("source#"):
            value = source.as_posix() if case.semantic_selector.endswith("/path") else (s.sha256_file(source) if source.is_file() else "missing")
        elif case.semantic_selector.startswith(("repository#", "identity#")):
            value = repr(bundle.context.identity)
        elif case.semantic_selector.startswith("filesystem#"):
            value = repr(bundle.context.filesystem)
        elif case.semantic_selector.startswith(("profile#", "context#")):
            value = repr(bundle.context.profile)
        elif case.semantic_selector.startswith("recovery#"):
            value = recovery.as_posix()
        else:
            relative = case.semantic_selector.split("#", 1)[0]
            value = s.sha256_file(bundle.repo_root / relative) if (bundle.repo_root / relative).is_file() else repr(paths)
        return s.sha256_bytes(str(value).encode("utf-8"))
    semantic_before = selector_hash(before_paths)
    case.mutate(bundle)
    after_mutation = _snapshot(bundle.repo_root)
    identity_changed = before_identity != repr(bundle.context.identity.identity)
    filesystem_changed = before_filesystem != repr(bundle.context.filesystem)
    context_changed = before_context != repr(bundle.context)
    if before == after_mutation and not identity_changed and not filesystem_changed and not context_changed and before_paths == (bundle.contract_path, bundle.source_path, bundle.recovery_root, bundle.run_root):
        raise AssertionError(case.case_id + " did not mutate its physical selector")
    semantic_after = selector_hash((bundle.contract_path, bundle.source_path, bundle.recovery_root, bundle.run_root))
    changed_by_reseal = reseal_transport(bundle, case)
    assert set(changed_by_reseal).issubset(case.allowed_transport_selectors)
    observed = ""
    calls = 0
    try:
        calls += 1
        s._test_verify(bundle.contract_path, bundle.source_path, bundle.recovery_root,
                       bundle.run_root, context=bundle.context)
    except s.ReconstructionStop as error:
        observed = error.code
    assert calls == 1 and observed == case.expected_code
    residue = tuple(sorted(path.relative_to(bundle.repo_root).as_posix()
                           for path in bundle.repo_root.rglob("*")
                           if path.name.startswith(".") and "tmp-" in path.name))
    changed_before_reseal = _REG_STALE_DELTA if case.case_id == "REG-P1-stale-metadata" else (case.semantic_selector,)
    return s.MutationAudit(case.case_id, case.case_id.split("-", 1)[0],
                           "fixture", case.semantic_selector, semantic_before,
                           semantic_after, changed_before_reseal,
                           tuple(item.value for item in case.reseal), changed_by_reseal,
                           case.expected_code, observed, calls, 0, (), residue,
                           "PASS" if not residue else "residue")


@pytest.mark.parametrize("case", CASES, ids=lambda item: item.case_id)
def test_selector_specific_mutation(case: s.MutationCase, tmp_path: Path) -> None:
    bundle = make_valid_bundle(tmp_path, fixture_id=case.case_id)
    if case.case_id.startswith(("REP-", "SRC-", "AUT-", "TOP-", "SCH-", "LED-", "INV-", "PAG-", "NAV-", "AST-", "SEM-", "INJ-", "REG-")) or case.case_id in CMD_A_CASE_IDS | CMD_B_CASE_IDS | CMD_C_CASE_IDS | QAV_A_CASE_IDS | QAV_B_CASE_IDS | QAV_C_CASE_IDS | QAV_D1_CASE_IDS | QAV_D2_CASE_IDS:
        audit = apply_case(case, bundle)
        assert audit.result == "PASS" and audit.observed_code == case.expected_code
        if case.case_id == "REG-P1-stale-metadata":
            assert audit.changed_before_reseal == _REG_STALE_DELTA
            qa = s._load(bundle.run_root / s.QA_NAME)
            assert len(qa["output_inventory"]) == 470
            assert qa["output_inventory_sha256"] == s.manifest_digest(qa["output_inventory"])
        return
    commands = bundle.run_root / s.AUTHORITY_PATHS["COMMANDS"]
    before = s.sha256_file(commands); case.mutate(bundle); after = s.sha256_file(commands)
    assert before != after and case.semantic_selector and case.expected_code.startswith("E_")
    assert case.mutate.__name__ == "mutate_" + case.case_id.replace("-", "_")


def test_bld_fresh_root_success(tmp_path: Path) -> None:
    value = make_valid_input(tmp_path, fixture_id="fresh")
    assert not value.final_root.exists()
    before_siblings = {path.name for path in tmp_path.iterdir()}
    result = s._test_build(value.contract_path, value.source_path, value.recovery_root,
                           value.final_root, context=value.context)
    assert result == {"state": "built_candidate_needs_review", "fixture_files": 502,
                      "build_token": result["build_token"]}
    # Publication has preserved the temp directory identity and removed the
    # exact sibling owner marker only after the second strict verification.
    assert value.final_root.is_dir() and s._file_id(value.final_root)
    assert not [path for path in tmp_path.iterdir()
                if path.name.startswith(".candidate.tmp-") or path.name.startswith(".candidate.owner-")]
    assert {path.name for path in tmp_path.iterdir()} == before_siblings | {"candidate"}
    first = s._test_verify(value.contract_path, value.source_path, value.recovery_root,
                           value.final_root, context=value.context)
    second = s._test_verify(value.contract_path, value.source_path, value.recovery_root,
                            value.final_root, context=value.context)
    assert first == second == {"state": "test_verified", "fixture_files": 502,
                               "outside_fixture_reads": 0, "deterministic": True}
    assert len(s.candidate_records(value.final_root)) == 502
    assert len(s.candidate_records(value.final_root, {s.QA_NAME})) == 501
    assert len(s.candidate_records(value.final_root, {s.QA_NAME, s.AUTHORITY_PATHS["COMMANDS"]})) == 500


def test_bld_existing_target_refusal_no_mutation(tmp_path: Path) -> None:
    value = make_valid_input(tmp_path, fixture_id="existing"); value.final_root.mkdir(); sentinel = value.final_root / "sentinel"; sentinel.write_bytes(b"keep")
    before = sentinel.read_bytes(), s.sha256_file(sentinel), s._file_id(value.final_root), {path.name for path in tmp_path.iterdir()}
    with pytest.raises(s.ReconstructionStop) as error:
        s._test_build(value.contract_path, value.source_path, value.recovery_root, value.final_root, context=value.context)
    assert error.value.code == "E_BUILD_OVERWRITE"
    assert (sentinel.read_bytes(), s.sha256_file(sentinel), s._file_id(value.final_root), {path.name for path in tmp_path.iterdir()}) == before
    assert not [path for path in tmp_path.iterdir() if path.name.startswith((".candidate.tmp-", ".candidate.owner-"))]


def test_bld_finalizer_parity(tmp_path: Path) -> None:
    built = make_valid_input(tmp_path / "a", fixture_id="a")
    s._test_build(built.contract_path, built.source_path, built.recovery_root, built.final_root,
                  context=built.context)
    staged = make_valid_input(tmp_path / "b", fixture_id="b")
    model = s._load_validated_reconstruction_input(s.OperationPaths(staged.contract_path, staged.source_path,
        staged.recovery_root, staged.final_root), staged.context)
    owned = s._owned(staged.final_root, staged.context)
    try:
        s._write_non_qa_bundle(owned.temp, model, staged.context, owned)
        parity = s._finalize_and_verify(owned.temp, s.OperationPaths(staged.contract_path,
            staged.source_path, staged.recovery_root, staged.final_root), staged.context, owned, "build")
        left = {path.relative_to(built.final_root).as_posix(): path.read_bytes()
                for path in built.final_root.rglob("*") if path.is_file()}
        right = {path.relative_to(owned.temp).as_posix(): path.read_bytes()
                 for path in owned.temp.rglob("*") if path.is_file()}
        assert left == right
        assert parity == {"state": "test_verified", "fixture_files": 502,
                          "outside_fixture_reads": 0, "deterministic": True}
        assert len(s.candidate_records(owned.temp)) == 502
        assert len(s.candidate_records(owned.temp, {s.QA_NAME})) == 501
        assert len(s.candidate_records(owned.temp, {s.QA_NAME, s.AUTHORITY_PATHS["COMMANDS"]})) == 500
    finally:
        if owned.temp.exists() or owned.marker.exists():
            s.remove_owned_tree(owned, staged.context)
    assert not staged.final_root.exists() and not owned.temp.exists() and not owned.marker.exists()
