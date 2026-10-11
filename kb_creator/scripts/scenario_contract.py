"""Pure, stdlib-only validation for ScenarioContract.v1 documents."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any

SCHEMA = "kb_creator.scenario_contract.v1"
PROFILES = {"compatibility_shadow", "intake", "reconstruction_ready"}
ROLES = {"cover", "credits", "front_matter", "contents", "scenario_body", "player_handouts", "keeper_maps", "pregenerated_investigators", "back_cover"}
MODES = {"text", "mixed", "visual", "unknown"}
TRAITS = {"multi_column", "low_text", "zero_text", "table_heavy", "statblock", "form_like"}
STRATEGIES = {"embedded_text", "reading_order", "ocr_region", "visual_preserve"}
STAGES = ("reconstructed_en", "master_en", "master_ru", "html", "pdf", "production")
ARTIFACTS = ("reconstructed_en", "master_en", "master_ru", "html", "pdf", "production_manifest")
POLICY_DOMAINS = ("reconstruction", "publication", "translation", "visual", "navigation", "render")
HEX = re.compile(r"^[0-9A-F]{64}$")
IDENT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")

ACCEPTANCE = {
    "reconstructed_en": (["source_identity", "page_coverage", "role_partition", "text_ocr_provenance", "required_entity_closure", "asset_closure", "no_open_blockers"], "configured_reconstruction_review"),
    "master_en": (["accepted_reconstructed", "source_disposition", "semantic_navigation", "handout_mapping", "table_statblock_closure", "asset_closure", "no_technical_reader_noise"], "explicit_user_reading_acceptance"),
    "master_ru": (["accepted_master_en_lineage", "structural_parity", "terminology", "untranslated_terms", "links", "asset_closure"], "explicit_user_reading_acceptance"),
    "html": (["accepted_master_ru", "deterministic_output", "links", "assets", "unique_ids", "generated_only", "navigation"], "explicit_user_visual_navigation_acceptance"),
    "pdf": (["accepted_html", "print_only_delta", "render_coverage", "no_blank_pages", "destinations", "section_boundaries", "full_visual_qa", "generated_only"], "explicit_user_print_acceptance"),
    "production": (["accepted_packages", "closed_inventory", "stable_names", "asset_union", "contract_schema_code_snapshots", "qa_closure"], "explicit_production_snapshot_acceptance"),
}
EXCEPTION_TRIPLES = {
    "text_repair": ({"reconstructed_en"}, "replace_exact_text"),
    "reading_order": ({"reconstructed_en"}, "reorder_exact_blocks"),
    "list_continuation": ({"reconstructed_en"}, "continue_numbering"),
    "publication_suppression": ({"master_en"}, "suppress_exact_block"),
    "semantic_link": ({"master_en", "html"}, "retarget_exact_reference"),
    "asset_owner": ({"master_en", "master_ru", "html"}, "relocate_exact_asset_owner"),
    "render_placement": ({"html", "pdf"}, "apply_named_placement"),
    "page_break": ({"pdf"}, "insert_page_break_before_heading"),
}
SELECTOR_KINDS = {"exact_text", "block_id", "heading_id", "asset_id", "page_boundary"}
EVIDENCE_KINDS = {"source_page", "review_receipt", "accepted_manifest"}

SHADOW_EVIDENCE = {
    "control_pdf_sha256": {"sha256": "5850B26A077390ABFF4A321E754A3709D6148FA4AC7A9F4D63BDBEFF6949B1BB", "status": "unavailable_control_identity"},
    "retained_markdown_candidate_sha256": {"sha256": "1504A9C71CA995748E4125B7303C0D3064E588ABB226EBB5AB99A5F5763C993C", "kind": "retained_markdown_candidate"},
    "reconstructed_page_marker_domain": {"kind": "reconstructed_markdown_page_markers", "base": 0, "first": 0, "last": 45, "count": 46},
    "accepted_reconstructed_evidence": {
        "reconstructed_markdown": {"byte_count": 138426, "sha256": "8F5A35B6FBE545691EEF66C52A848F0F04776A247CCAAF40B16140FEB0C543BF"},
        "reconstructed_qa": {"byte_count": 75179, "sha256": "8C351053E49AE3546BCA5857394DDCCBA2FF60AE05DA75C03ACB47E076B06DA9"},
        "assets": {"count": 136, "inventory_sha256": "B6F9BF00B01DB09ED06723871B97B424206C5A79EB624C8F5768A847B1CE3B39"},
    },
    "accepted_stage_manifests": {
        "master_en": {"root": "inputs/innsmouth/master_en/accepted_20260830_r6", "manifest": "MASTER_EN.acceptance.json", "byte_count": 1320, "sha256": "AD9A6546EB7421F4387A4E6B547B2CD6B61346A3B326D25110A56028FC919B83"},
        "master_ru": {"root": "inputs/innsmouth/master_ru/accepted_20260830_r6", "manifest": "MASTER_RU.acceptance.json", "byte_count": 4075, "sha256": "B87C34F312258FB349B6AE549A398637096CE3A29D9B623EEDA28D5ECF4EC384"},
        "html": {"root": "inputs/innsmouth/html/accepted_20260830_r6", "manifest": "HTML.acceptance.json", "byte_count": 7208, "sha256": "F3A6EC483858060B46EB266893FEE7D4AE4F63D3A9A0A26CCB899D5903B4375A"},
        "pdf": {"root": "inputs/innsmouth/pdf/accepted_20260830_r7", "manifest": "PDF.acceptance.json", "byte_count": 7890, "sha256": "5861569529394C8B04BD7903B1BD07C420812AD63DC1C669F7CA4E11E40E0154"},
    },
    "authority": "existing_accepted_manifests_and_verifiers",
    "runtime_authority": False,
}


def _err(message: str) -> None:
    raise ValueError(message)


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_thaw(item) for item in value]
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _object(value: Any, required: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _err(f"{name} must be an object")
    actual = set(value)
    if actual != required:
        _err(f"{name} keys mismatch; missing={sorted(required - actual)}, extra={sorted(actual - required)}")
    return value


def _exact_integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        _err(f"{name} must be an exact integer")
    if minimum is not None and value < minimum:
        _err(f"{name} must be >= {minimum}")
    return value


def _finite_number(value: Any, name: str, *, positive: bool = False) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        _err(f"{name} must be a finite JSON number")
    if positive and value <= 0:
        _err(f"{name} must be positive")
    return value


def _string(value: Any, name: str, *, minimum: int = 1) -> str:
    if not isinstance(value, str) or value != value.strip() or len(value) < minimum or CONTROL.search(value):
        _err(f"{name} must be a trimmed non-control string")
    return value


def _unique_list(value: Any, name: str, allowed: set[str] | None = None, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        _err(f"{name} must be {'a nonempty' if nonempty else 'an'} array")
    if any(isinstance(item, (dict, list)) for item in value) or len(value) != len(set(value)):
        _err(f"{name} contains duplicates or non-scalar values")
    if allowed is not None and any(item not in allowed for item in value):
        _err(f"{name} contains an unknown value")
    return value


def _safe_basename(value: Any, name: str, suffix: str) -> str:
    text = _string(value, name)
    lowered = text.lower()
    if ("/" in text or "\\" in text or ".." in text or ":" in text or "<" in text or ">" in text or not lowered.endswith(suffix)
            or re.search(r"(?:^|[_-])(accepted|release|placeholder|todo|tbd)(?:[_\-.]|$)", lowered)
            or re.search(r"(?:^|[_-])(?:20\d{6}|[rv]\d+)(?:[_\-.]|$)", lowered)):
        _err(f"unsafe or wrongly suffixed {name}")
    return text


def _validate_scenario(value: Any) -> None:
    scenario = _object(value, {"id", "title", "product_type", "source_language", "publication_languages"}, "scenario")
    if not isinstance(scenario["id"], str) or not IDENT.fullmatch(scenario["id"]):
        _err("invalid scenario id")
    _string(scenario["title"], "scenario.title")
    if scenario["product_type"] != "coc_scenario" or scenario["source_language"] != "en":
        _err("invalid scenario identity")
    if scenario["publication_languages"] != ["en", "ru"]:
        _err("publication languages must be exactly ['en', 'ru']")


def _validate_artifacts(value: Any) -> None:
    artifacts = _object(value, set(ARTIFACTS), "artifacts")
    suffixes = {"reconstructed_en": ".md", "master_en": ".md", "master_ru": ".md", "html": ".html", "pdf": ".pdf", "production_manifest": ".json"}
    names = [_safe_basename(artifacts[key], f"artifacts.{key}", suffixes[key]) for key in ARTIFACTS]
    if len(names) != len({name.casefold() for name in names}):
        _err("artifact names must be unique")


def _validate_shadow(root: dict[str, Any], profile: str) -> None:
    if profile != "compatibility_shadow":
        _err("compatibility shadow is not eligible for runtime profiles")
    source = _object(root["source"], {"kind", "identity_status", "locator_hint", "sha256", "byte_count", "page_count", "page_number_base", "media_box_points", "rotation_degrees"}, "source")
    if source["kind"] != "external_pdf" or source["identity_status"] != "incomplete":
        _err("invalid shadow source classification")
    for key in ("locator_hint", "sha256", "byte_count", "page_count", "page_number_base", "media_box_points", "rotation_degrees"):
        if source[key] is not None:
            _err(f"shadow source.{key} must be null")
    if root["scope"] is not None or root["page_roles"] != [] or root["policies"] is not None or root["acceptance"] is not None:
        _err("shadow runtime topology and policy fields must be null/empty")
    if root["exceptions"] != []:
        _err("shadow exceptions must be empty")
    if json.dumps(root["compatibility_evidence"], sort_keys=True, separators=(",", ":")) != json.dumps(SHADOW_EVIDENCE, sort_keys=True, separators=(",", ":")):
        _err("compatibility evidence is not the exact reviewed closed evidence")


def _validate_source(value: Any) -> dict[str, Any]:
    source = _object(value, {"kind", "identity_status", "locator_hint", "sha256", "byte_count", "page_count", "page_number_base", "media_box_points", "rotation_degrees"}, "source")
    if source["kind"] != "external_pdf" or source["identity_status"] != "complete":
        _err("invalid runtime source classification")
    _safe_basename(source["locator_hint"], "source.locator_hint", ".pdf")
    if not isinstance(source["sha256"], str) or not HEX.fullmatch(source["sha256"]):
        _err("source.sha256 must be 64 uppercase hexadecimal characters")
    _exact_integer(source["byte_count"], "source.byte_count", minimum=1)
    _exact_integer(source["page_count"], "source.page_count", minimum=1)
    _exact_integer(source["page_number_base"], "source.page_number_base", minimum=1)
    box = source["media_box_points"]
    if not isinstance(box, list) or len(box) != 2:
        _err("source.media_box_points must contain exactly two numbers")
    for index, number in enumerate(box):
        _finite_number(number, f"source.media_box_points[{index}]", positive=True)
    _exact_integer(source["rotation_degrees"], "source.rotation_degrees")
    if source["rotation_degrees"] not in (0, 90, 180, 270):
        _err("invalid source rotation")
    return source


def _validate_scope(value: Any, source: dict[str, Any]) -> dict[str, Any]:
    scope = _object(value, {"mode", "first_page", "last_page", "required_entities"}, "scope")
    if scope["mode"] != "all_source_pages":
        _err("unsupported scope mode")
    first = _exact_integer(scope["first_page"], "scope.first_page", minimum=1)
    last = _exact_integer(scope["last_page"], "scope.last_page", minimum=1)
    if first != source["page_number_base"] or last != first + source["page_count"] - 1:
        _err("scope does not exactly cover the source")
    entities = _object(scope["required_entities"], {"numbered_player_handouts"}, "scope.required_entities")
    _exact_integer(entities["numbered_player_handouts"], "numbered_player_handouts", minimum=0)
    return scope


def _validate_page_roles(value: Any, scope: dict[str, Any], profile: str) -> None:
    if not isinstance(value, list) or not value:
        _err("page_roles must be a nonempty array")
    expected = scope["first_page"]
    for index, value_row in enumerate(value):
        row = _object(value_row, {"role", "first_page", "last_page", "content_mode", "traits", "strategies"}, f"page_roles[{index}]")
        if row["role"] not in ROLES or row["content_mode"] not in MODES:
            _err("unknown page role or content mode")
        first = _exact_integer(row["first_page"], f"page_roles[{index}].first_page", minimum=1)
        last = _exact_integer(row["last_page"], f"page_roles[{index}].last_page", minimum=1)
        if first != expected or last < first or last > scope["last_page"]:
            _err("page roles must be sorted, gap-free, non-overlapping, and inside scope")
        _unique_list(row["traits"], f"page_roles[{index}].traits", TRAITS)
        _unique_list(row["strategies"], f"page_roles[{index}].strategies", STRATEGIES, nonempty=True)
        expected = last + 1
    if expected != scope["last_page"] + 1:
        _err("page roles do not completely cover scope")
    if profile == "reconstruction_ready" and any(row["content_mode"] == "unknown" for row in value):
        _err("unknown content mode blocks reconstruction")


def _validate_policies(value: Any) -> None:
    policies = _object(value, set(POLICY_DOMAINS), "policies")
    for domain in {"reconstruction", "publication", "visual", "navigation"}:
        policy = _object(policies[domain], {"strategies", "required_review"}, f"policies.{domain}")
        strategies = _unique_list(policy["strategies"], f"policies.{domain}.strategies", STRATEGIES, nonempty=True)
        if policy["required_review"] is not True:
            _err(f"policies.{domain}.required_review must be true")
        exact = {"publication": ["reading_order"], "visual": ["visual_preserve"], "navigation": ["reading_order"]}
        if domain in exact and strategies != exact[domain]:
            _err(f"policies.{domain}.strategies is not the exact v1 list")
    translation = _object(policies["translation"], {"strategies", "lineage_source", "historical_source_mode", "required_review"}, "policies.translation")
    if translation != {"strategies": ["reading_order"], "lineage_source": "accepted_current_master_en", "historical_source_mode": "terminology_or_comparison_only", "required_review": True}:
        _err("translation policy violates the reviewed lineage boundary")
    render = _object(policies["render"], {"strategies", "profile", "required_review"}, "policies.render")
    if render != {"strategies": ["visual_preserve"], "profile": "viral_print", "required_review": True}:
        _err("render policy is not the closed Viral v1 profile")


def _validate_acceptance(value: Any) -> None:
    acceptance = _object(value, set(STAGES), "acceptance")
    for stage in STAGES:
        record = _object(acceptance[stage], {"automated_gates", "approval_authority"}, f"acceptance.{stage}")
        expected_gates, expected_authority = ACCEPTANCE[stage]
        if record["automated_gates"] != expected_gates or record["approval_authority"] != expected_authority:
            _err(f"acceptance.{stage} is not the exact ordered v1 gate declaration")


def _validate_exceptions(value: Any, scope: dict[str, Any]) -> None:
    if not isinstance(value, list):
        _err("exceptions must be an array")
    ids: set[str] = set()
    selectors: list[tuple[str, str, str, set[int]]] = []
    for index, value_exception in enumerate(value):
        exception = _object(value_exception, {"id", "stage", "kind", "operation", "scope", "expected_matches", "rationale", "evidence", "approval"}, f"exceptions[{index}]")
        exception_id = exception["id"]
        if not isinstance(exception_id, str) or not IDENT.fullmatch(exception_id) or exception_id in ids:
            _err("exception ids must be unique safe kebab ids")
        ids.add(exception_id)
        triple = EXCEPTION_TRIPLES.get(exception["kind"])
        if triple is None or exception["stage"] not in triple[0] or exception["operation"] != triple[1]:
            _err("invalid exception kind/stage/operation triple")
        if exception["approval"] != "required" or _exact_integer(exception["expected_matches"], "exception.expected_matches") != 1:
            _err("exception approval/match count is invalid")
        _string(exception["rationale"], "exception.rationale", minimum=12)
        exception_scope = _object(exception["scope"], {"pages", "selector"}, "exception.scope")
        pages = exception_scope["pages"]
        if not isinstance(pages, list) or not pages:
            _err("exception.scope.pages must be nonempty")
        for page in pages:
            _exact_integer(page, "exception.scope.pages item", minimum=1)
        if pages != sorted(set(pages)) or pages[0] < scope["first_page"] or pages[-1] > scope["last_page"]:
            _err("exception.scope.pages must be sorted, unique, and inside scope")
        selector = _object(exception_scope["selector"], {"kind", "value"}, "exception.scope.selector")
        if selector["kind"] not in SELECTOR_KINDS:
            _err("unknown exception selector kind")
        _string(selector["value"], "exception.scope.selector.value")
        evidence = exception["evidence"]
        if not isinstance(evidence, list) or not evidence:
            _err("exception evidence must be nonempty")
        evidence_pairs = []
        for evidence_index, value_evidence in enumerate(evidence):
            row = _object(value_evidence, {"kind", "ref"}, f"exception.evidence[{evidence_index}]")
            if row["kind"] not in EVIDENCE_KINDS:
                _err("unknown exception evidence kind")
            _string(row["ref"], "exception evidence ref")
            evidence_pairs.append((row["kind"], row["ref"]))
        if len(evidence_pairs) != len(set(evidence_pairs)):
            _err("duplicate exception evidence")
        current = (exception["stage"], selector["kind"], selector["value"], set(pages))
        for stage, kind, selector_value, previous_pages in selectors:
            if (stage, kind, selector_value) == current[:3] and previous_pages & current[3]:
                _err("overlapping same-selector exceptions")
        selectors.append(current)


def _validate(data: Any, profile: str) -> dict[str, Any]:
    if profile not in PROFILES:
        _err("unknown validation profile")
    root = _thaw(data)
    if not isinstance(root, dict):
        _err("contract must be an object")
    role = root.get("contract_role")
    common = {"schema", "contract_revision", "contract_role", "scenario", "source", "scope", "page_roles", "artifacts", "policies", "acceptance", "exceptions"}
    expected = common | ({"compatibility_evidence"} if role == "compatibility_shadow" else set())
    root = _object(root, expected, "contract")
    if root["schema"] != SCHEMA or _exact_integer(root["contract_revision"], "contract_revision") != 1:
        _err("schema or contract revision mismatch")
    if role not in {"runtime", "compatibility_shadow"}:
        _err("unknown contract role")
    _validate_scenario(root["scenario"])
    _validate_artifacts(root["artifacts"])
    if role == "compatibility_shadow":
        _validate_shadow(root, profile)
        return root
    if profile == "compatibility_shadow":
        _err("runtime contract is not a compatibility shadow")
    source = _validate_source(root["source"])
    scope = _validate_scope(root["scope"], source)
    _validate_page_roles(root["page_roles"], scope, profile)
    _validate_policies(root["policies"])
    _validate_acceptance(root["acceptance"])
    _validate_exceptions(root["exceptions"], scope)
    return root


def validate_contract(data: Any, profile: str = "intake") -> Any:
    return _freeze(_validate(data, profile))


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _err(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> None:
    _err(f"non-finite JSON number: {value}")


def load_contract(path: str | Path, profile: str = "intake") -> Any:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_nonfinite_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid UTF-8 JSON contract: {error}") from error
    return validate_contract(raw, profile)


def canonical_contract_bytes(data: Any) -> bytes:
    raw = _thaw(data)
    profile = "compatibility_shadow" if isinstance(raw, dict) and raw.get("contract_role") == "compatibility_shadow" else "intake"
    validated = _validate(raw, profile)
    return json.dumps(validated, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def contract_sha256(data: Any) -> str:
    return hashlib.sha256(canonical_contract_bytes(data)).hexdigest().upper()


def resolve_source_path(contract: Any, runtime_path: str | Path, *, observed_page_count: Any = None, observed_media_box_points: Any = None, observed_rotation_degrees: Any = None) -> Path:
    raw = _thaw(contract)
    if not isinstance(raw, dict) or raw.get("contract_role") != "runtime":
        _err("source resolution rejects compatibility shadows before filesystem access")
    validated = _validate(raw, "intake")
    source = validated["source"]
    page_count = _exact_integer(observed_page_count, "observed_page_count", minimum=1)
    if not isinstance(observed_media_box_points, (list, tuple)) or len(observed_media_box_points) != 2:
        _err("observed_media_box_points must contain exactly two finite numbers")
    media_box = [_finite_number(value, f"observed_media_box_points[{index}]", positive=True) for index, value in enumerate(observed_media_box_points)]
    rotation = _exact_integer(observed_rotation_degrees, "observed_rotation_degrees")
    path = Path(runtime_path).expanduser().resolve()
    if not path.is_file():
        _err("runtime source must be an existing regular file")
    digest = hashlib.sha256()
    byte_count = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            byte_count += len(chunk)
            digest.update(chunk)
    if byte_count != source["byte_count"]:
        _err("runtime source byte count mismatch")
    if digest.hexdigest().upper() != source["sha256"]:
        _err("runtime source SHA-256 mismatch")
    if page_count != source["page_count"]:
        _err("observed page count mismatch")
    if media_box != source["media_box_points"]:
        _err("observed media box mismatch")
    if rotation != source["rotation_degrees"]:
        _err("observed rotation mismatch")
    return path
