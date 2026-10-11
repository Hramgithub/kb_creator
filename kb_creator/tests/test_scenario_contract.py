import copy
import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.scripts.scenario_contract import (
    ACCEPTANCE,
    SHADOW_EVIDENCE,
    canonical_contract_bytes,
    contract_sha256,
    load_contract,
    resolve_source_path,
    validate_contract,
)


ROOT = Path(__file__).parents[1]
VIRAL = ROOT / "contracts" / "viral.json"
INNSMOUTH = ROOT / "contracts" / "innsmouth.json"
SCHEMA = ROOT / "contracts" / "scenario_contract.v1.schema.json"


def read(path=VIRAL):
    return json.loads(path.read_text(encoding="utf-8"))


def valid_exception(page=42, *, exception_id="viral-publication-suppression-001"):
    return {
        "id": exception_id,
        "stage": "master_en",
        "kind": "publication_suppression",
        "operation": "suppress_exact_block",
        "scope": {"pages": [page], "selector": {"kind": "block_id", "value": "block-42-a"}},
        "expected_matches": 1,
        "rationale": "Source block is intentionally suppressed.",
        "evidence": [
            {"kind": "source_page", "ref": "source:42"},
            {"kind": "review_receipt", "ref": "handoffs/example.md"},
        ],
        "approval": "required",
    }


def contract_for_bytes(path):
    data = read()
    payload = path.read_bytes()
    data["source"]["byte_count"] = len(payload)
    data["source"]["sha256"] = hashlib.sha256(payload).hexdigest().upper()
    return data


def test_schema_is_draft_2020_12_and_both_branches_are_closed():
    schema = read(SCHEMA)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["oneOf"] == [{"$ref": "#/$defs/runtimeContract"}, {"$ref": "#/$defs/shadowContract"}]
    assert schema["$defs"]["runtimeContract"]["additionalProperties"] is False
    assert schema["$defs"]["shadowContract"]["additionalProperties"] is False
    for name in ("scenario", "runtimeSource", "shadowSource", "scope", "pageRole", "artifacts", "policies", "selector", "evidence", "exception", "compatibilityEvidence"):
        assert schema["$defs"][name]["additionalProperties"] is False


def test_contracts_load_only_under_their_explicit_profiles_and_are_immutable():
    viral = load_contract(VIRAL, "intake")
    shadow = load_contract(INNSMOUTH, "compatibility_shadow")
    assert viral["contract_role"] == "runtime"
    assert shadow["contract_role"] == "compatibility_shadow"
    with pytest.raises(TypeError):
        viral["schema"] = "changed"
    with pytest.raises(ValueError, match="not eligible"):
        load_contract(INNSMOUTH, "intake")
    with pytest.raises(ValueError, match="not a compatibility shadow"):
        load_contract(VIRAL, "compatibility_shadow")


def test_viral_exact_runtime_facts_roles_names_policies_and_gates():
    data = read()
    assert data["contract_role"] == "runtime"
    assert data["source"] == {
        "kind": "external_pdf", "identity_status": "complete", "locator_hint": "Call_of_Cthulhu_Viral.pdf",
        "sha256": "0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05",
        "byte_count": 20718150, "page_count": 124, "page_number_base": 1,
        "media_box_points": [612, 792], "rotation_degrees": 0,
    }
    assert data["scope"] == {"mode": "all_source_pages", "first_page": 1, "last_page": 124, "required_entities": {"numbered_player_handouts": 39}}
    assert [(row["role"], row["first_page"], row["last_page"]) for row in data["page_roles"]] == [
        ("cover", 1, 1), ("credits", 2, 2), ("front_matter", 3, 4), ("contents", 5, 5),
        ("scenario_body", 6, 68), ("player_handouts", 69, 103), ("keeper_maps", 104, 110),
        ("pregenerated_investigators", 111, 123), ("back_cover", 124, 124),
    ]
    assert [row["content_mode"] for row in data["page_roles"][:4]] == ["unknown"] * 4
    assert data["artifacts"] == {"reconstructed_en": "RECONSTRUCTED_EN.md", "master_en": "MASTER_EN.md", "master_ru": "MASTER_RU.md", "html": "Viral_RU.html", "pdf": "Viral_RU.pdf", "production_manifest": "PRODUCTION_MANIFEST.json"}
    assert data["policies"]["translation"]["lineage_source"] == "accepted_current_master_en"
    assert data["policies"]["translation"]["historical_source_mode"] == "terminology_or_comparison_only"
    for stage, (gates, authority) in ACCEPTANCE.items():
        assert data["acceptance"][stage] == {"automated_gates": gates, "approval_authority": authority}


def test_viral_intake_only_unknown_modes_and_test_local_closure():
    data = read()
    validate_contract(data, "intake")
    with pytest.raises(ValueError, match="unknown content mode"):
        validate_contract(data, "reconstruction_ready")
    closed = copy.deepcopy(data)
    for row in closed["page_roles"]:
        if row["content_mode"] == "unknown":
            row["content_mode"] = "mixed"
    validate_contract(closed, "reconstruction_ready")
    assert any(row["content_mode"] == "unknown" for row in read()["page_roles"])


def test_innsmouth_shadow_is_required_null_and_exact_closed_evidence():
    data = read(INNSMOUTH)
    validate_contract(data, "compatibility_shadow")
    assert data["source"] == {"kind": "external_pdf", "identity_status": "incomplete", "locator_hint": None, "sha256": None, "byte_count": None, "page_count": None, "page_number_base": None, "media_box_points": None, "rotation_degrees": None}
    assert data["scope"] is None and data["page_roles"] == []
    assert data["policies"] is None and data["acceptance"] is None and data["exceptions"] == []
    assert data["compatibility_evidence"] == SHADOW_EVIDENCE


@pytest.mark.parametrize("path,profile", [(VIRAL, "intake"), (INNSMOUTH, "compatibility_shadow")])
def test_raw_and_frozen_canonical_bytes_and_hash_are_equal(path, profile):
    raw = read(path)
    frozen = load_contract(path, profile)
    assert canonical_contract_bytes(raw) == canonical_contract_bytes(frozen)
    assert contract_sha256(raw) == contract_sha256(frozen)
    reordered = {key: raw[key] for key in reversed(raw)}
    assert canonical_contract_bytes(reordered) == canonical_contract_bytes(raw)
    assert b"runtime_path" not in canonical_contract_bytes(raw)
    assert not canonical_contract_bytes(raw).endswith(b"\n")


@pytest.mark.parametrize("text", [
    '{"schema":"x","schema":"y"}',
    '{"outer":{"id":"a","id":"b"}}',
])
def test_duplicate_json_keys_fail_at_every_depth(tmp_path, text):
    path = tmp_path / "duplicate.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_contract(path)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_json_constants_fail_loading(tmp_path, constant):
    path = tmp_path / "nonfinite.json"
    path.write_text('{"value":' + constant + "}", encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite"):
        load_contract(path)


@pytest.mark.parametrize("mutator", [
    lambda d: d.pop("scenario"),
    lambda d: d.update(extra=True),
    lambda d: d["scenario"].update(extra=True),
    lambda d: d.update(contract_revision=True),
    lambda d: d.update(contract_role="compatibility_shadow"),
    lambda d: d["scenario"].update(id="Bad_Id"),
    lambda d: d["scenario"].update(title=" Viral "),
    lambda d: d["scenario"].update(publication_languages=["ru", "en"]),
    lambda d: d["scenario"].update(publication_languages=["en", "en"]),
    lambda d: d["source"].update(kind="embedded_pdf"),
    lambda d: d["source"].update(identity_status="incomplete"),
    lambda d: d["source"].update(page_number_base=0),
    lambda d: d["source"].update(rotation_degrees=True),
    lambda d: d["scope"].update(mode="selected_pages"),
    lambda d: d["scope"].update(first_page=2),
])
def test_structural_identity_role_and_scope_negatives(mutator):
    data = read()
    mutator(data)
    with pytest.raises(ValueError):
        validate_contract(data)


@pytest.mark.parametrize("field,value", [
    ("byte_count", True), ("byte_count", 0), ("page_count", False), ("page_count", -1),
    ("sha256", "a" * 64), ("sha256", "G" * 64), ("sha256", "A" * 63),
])
def test_source_strict_integer_and_hash_negatives(field, value):
    data = read()
    data["source"][field] = value
    with pytest.raises(ValueError):
        validate_contract(data)


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), 0, -1])
def test_geometry_requires_positive_finite_non_boolean_numbers(value):
    data = read()
    data["source"]["media_box_points"][0] = value
    with pytest.raises(ValueError):
        validate_contract(data)


@pytest.mark.parametrize("key,value", [
    ("html", "wrong.pdf"), ("html", "../Viral.html"), ("html", "C:Viral.html"),
    ("html", "https:Viral.html"), ("html", " Viral.html"), ("html", "Viral\x00.html"),
    ("html", "Viral_accepted_20260830.html"), ("html", "Viral_r7.html"), ("html", "Viral-v1.html"),
    ("html", "<review-required>.html"), ("html", "placeholder.html"),
])
def test_artifact_safety_and_suffix_negatives(key, value):
    data = read()
    data["artifacts"][key] = value
    with pytest.raises(ValueError):
        validate_contract(data)


def test_artifact_missing_extra_and_duplicate_names_fail():
    for mutation in ("missing", "extra", "duplicate", "case_duplicate"):
        data = read()
        if mutation == "missing":
            data["artifacts"].pop("pdf")
        elif mutation == "extra":
            data["artifacts"]["epub"] = "Viral.epub"
        elif mutation == "duplicate":
            data["artifacts"]["master_ru"] = data["artifacts"]["master_en"]
        else:
            data["artifacts"]["master_ru"] = data["artifacts"]["master_en"].lower()
        with pytest.raises(ValueError):
            validate_contract(data)


@pytest.mark.parametrize("mutator", [
    lambda d: d["page_roles"][1].update(first_page=3),
    lambda d: d["page_roles"][1].update(first_page=1),
    lambda d: d["page_roles"].__setitem__(0, {**d["page_roles"][0], "first_page": 2}),
    lambda d: d["page_roles"][-1].update(last_page=125),
    lambda d: d["page_roles"][-1].update(last_page=123),
    lambda d: d["page_roles"][0].update(role="unknown_role"),
    lambda d: d["page_roles"][0].update(content_mode="guess"),
    lambda d: d["page_roles"][0].update(traits=["low_text", "low_text"]),
    lambda d: d["page_roles"][0].update(traits=["unreviewed"]),
    lambda d: d["page_roles"][0].update(strategies=["visual_preserve", "visual_preserve"]),
])
def test_page_partition_and_taxonomy_negatives(mutator):
    data = read()
    mutator(data)
    with pytest.raises(ValueError):
        validate_contract(data)


@pytest.mark.parametrize("mutator", [
    lambda d: d["policies"].pop("render"),
    lambda d: d["policies"].update(execution={}),
    lambda d: d["policies"]["render"].update(command="pdftoppm"),
    lambda d: d["policies"]["render"].update(profile="innsmouth_print"),
    lambda d: d["policies"]["visual"].update(required_review=False),
    lambda d: d["policies"]["navigation"].update(strategies=["reading_order", "reading_order"]),
    lambda d: d["policies"]["publication"].update(strategies=["visual_preserve"]),
    lambda d: d["policies"]["translation"].update(lineage_source="historical_ru"),
    lambda d: d["policies"]["translation"].update(historical_source_mode="merge_source"),
])
def test_closed_policy_negatives(mutator):
    data = read()
    mutator(data)
    with pytest.raises(ValueError):
        validate_contract(data)


@pytest.mark.parametrize("mutator", [
    lambda d: d["acceptance"].pop("html"),
    lambda d: d["acceptance"].update(epub={}),
    lambda d: d["acceptance"]["html"].update(extra=True),
    lambda d: d["acceptance"]["html"].update(automated_gates=d["acceptance"]["html"]["automated_gates"][:-1]),
    lambda d: d["acceptance"]["html"].update(automated_gates=d["acceptance"]["html"]["automated_gates"] + ["unknown"]),
    lambda d: d["acceptance"]["html"].update(automated_gates=list(reversed(d["acceptance"]["html"]["automated_gates"]))),
    lambda d: d["acceptance"]["html"].update(automated_gates=[d["acceptance"]["html"]["automated_gates"][0]] * 7),
    lambda d: d["acceptance"]["html"].update(approval_authority="anyone"),
])
def test_exact_acceptance_gate_and_authority_negatives(mutator):
    data = read()
    mutator(data)
    with pytest.raises(ValueError):
        validate_contract(data)


def test_valid_exception_and_disjoint_same_selector_pass():
    data = read()
    data["exceptions"] = [valid_exception(42), valid_exception(43, exception_id="viral-publication-suppression-002")]
    validate_contract(data)


@pytest.mark.parametrize("mutator", [
    lambda e: e.update(id="Unsafe_ID"),
    lambda e: e.update(rationale="short"),
    lambda e: e.update(rationale=" untrimmed rationale "),
    lambda e: e.update(expected_matches=True),
    lambda e: e.update(expected_matches=0),
    lambda e: e.update(expected_matches=2),
    lambda e: e.update(approval="approved"),
    lambda e: e["scope"].update(pages=[]),
    lambda e: e["scope"].update(pages=[43, 42]),
    lambda e: e["scope"].update(pages=[42, 42]),
    lambda e: e["scope"].update(pages=[0]),
    lambda e: e["scope"].update(selector={"kind": "unknown", "value": "x"}),
    lambda e: e["scope"].update(selector={"kind": "block_id", "value": " "}),
    lambda e: e.update(evidence=[]),
    lambda e: e.update(evidence=[{"kind": "unknown", "ref": "x"}]),
    lambda e: e.update(evidence=[{"kind": "source_page", "ref": " x "}]),
    lambda e: e.update(evidence=[{"kind": "source_page", "ref": "source:42"}] * 2),
    lambda e: e.update(skip_identity=True),
])
def test_exception_shape_scope_evidence_and_antibypass_negatives(mutator):
    data = read()
    exception = valid_exception()
    mutator(exception)
    data["exceptions"] = [exception]
    with pytest.raises(ValueError):
        validate_contract(data)


@pytest.mark.parametrize("kind,stage,operation", [
    ("text_repair", "master_en", "replace_exact_text"),
    ("reading_order", "master_en", "reorder_exact_blocks"),
    ("list_continuation", "master_en", "continue_numbering"),
    ("publication_suppression", "pdf", "suppress_exact_block"),
    ("semantic_link", "pdf", "retarget_exact_reference"),
    ("asset_owner", "pdf", "relocate_exact_asset_owner"),
    ("render_placement", "master_en", "apply_named_placement"),
    ("page_break", "html", "insert_page_break_before_heading"),
    ("publication_suppression", "master_en", "skip_identity"),
])
def test_every_invalid_exception_triple_class_fails(kind, stage, operation):
    data = read()
    exception = valid_exception()
    exception.update(kind=kind, stage=stage, operation=operation)
    data["exceptions"] = [exception]
    with pytest.raises(ValueError):
        validate_contract(data)


def test_duplicate_exception_id_and_overlapping_selector_fail():
    for second in (valid_exception(43), valid_exception(42, exception_id="viral-publication-suppression-002")):
        data = read()
        data["exceptions"] = [valid_exception(42), second]
        with pytest.raises(ValueError):
            validate_contract(data)


def test_nonempty_shadow_exception_and_shadow_evidence_mutations_fail():
    data = read(INNSMOUTH)
    data["exceptions"] = [valid_exception()]
    with pytest.raises(ValueError):
        validate_contract(data, "compatibility_shadow")
    for mutation in ("extra", "hash", "runtime"):
        data = read(INNSMOUTH)
        if mutation == "extra":
            data["compatibility_evidence"]["source_path"] = "x.pdf"
        elif mutation == "hash":
            data["compatibility_evidence"]["control_pdf_sha256"]["sha256"] = "A" * 64
        else:
            data["compatibility_evidence"]["runtime_authority"] = True
        with pytest.raises(ValueError):
            validate_contract(data, "compatibility_shadow")


def test_shadow_rejection_precedes_any_filesystem_probe(monkeypatch):
    shadow = load_contract(INNSMOUTH, "compatibility_shadow")
    monkeypatch.setattr(Path, "is_file", lambda self: (_ for _ in ()).throw(AssertionError("filesystem probed")))
    with pytest.raises(ValueError, match="before filesystem access"):
        resolve_source_path(shadow, "Z:/definitely/missing.pdf", observed_page_count=1, observed_media_box_points=[1, 1], observed_rotation_degrees=0)


def test_source_resolution_verifies_file_and_observations(tmp_path):
    path = tmp_path / "source.pdf"
    path.write_bytes(b"reviewed-source-bytes")
    data = contract_for_bytes(path)
    frozen = validate_contract(data)
    before = contract_sha256(frozen)
    resolved = resolve_source_path(frozen, path, observed_page_count=124, observed_media_box_points=[612, 792], observed_rotation_degrees=0)
    assert resolved == path.resolve()
    assert contract_sha256(frozen) == before


@pytest.mark.parametrize("case", ["missing_path", "directory", "byte_count", "hash", "missing_observation", "page", "geometry", "rotation"])
def test_source_resolution_negative_matrix(tmp_path, case):
    path = tmp_path / "source.pdf"
    path.write_bytes(b"reviewed-source-bytes")
    data = contract_for_bytes(path)
    target = path
    kwargs = {"observed_page_count": 124, "observed_media_box_points": [612, 792], "observed_rotation_degrees": 0}
    if case == "missing_path":
        target = tmp_path / "missing.pdf"
    elif case == "directory":
        target = tmp_path
    elif case == "byte_count":
        data["source"]["byte_count"] += 1
    elif case == "hash":
        data["source"]["sha256"] = "A" * 64
    elif case == "missing_observation":
        kwargs["observed_page_count"] = None
    elif case == "page":
        kwargs["observed_page_count"] = 123
    elif case == "geometry":
        kwargs["observed_media_box_points"] = [612, 791]
    elif case == "rotation":
        kwargs["observed_rotation_degrees"] = 90
    frozen = validate_contract(data)
    before = contract_sha256(frozen)
    with pytest.raises(ValueError):
        resolve_source_path(frozen, target, **kwargs)
    assert contract_sha256(frozen) == before


def test_no_runtime_wiring_or_legacy_config_in_contracts():
    for path in (VIRAL, INNSMOUTH):
        text = path.read_text(encoding="utf-8")
        assert "translator/config/" + "viral" + ".package.json" not in text
        assert "runtime_path" not in text
