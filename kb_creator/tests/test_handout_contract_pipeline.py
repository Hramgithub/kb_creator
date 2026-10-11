"""Contract-v3 intake and CPU-first binding without OCR execution."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError, validate
from reportlab.pdfgen import canvas

from kb_creator.pipeline import five_step_intake as intake
from kb_creator.pipeline import mineru_cpu_first as cpu
from kb_creator.pipeline import reconstruction
from kb_creator.pipeline import reconstruction_promotion as promotion
from kb_creator.pipeline import reconstruction_replay as replay
from kb_creator.pipeline.identity import file_identity
from kb_creator.tests.test_mineru_cpu_packet_b import _runtime_fixture
from kb_creator.tests.test_reconstruction_promotion import (
    _closed_decisions,
    _contract as legacy_contract,
    _resume_adapters,
    _run_adapters,
    _runtime,
    _source as promotion_source,
)


CONTRACTS = Path(__file__).parents[1] / "contracts"


def _source(path: Path) -> None:
    document = canvas.Canvas(str(path), pagesize=(500, 700), invariant=1)
    document.drawString(40, 650, "Handout source")
    document.showPage()
    document.save()


def _v3_submission(root: Path) -> dict:
    value = json.loads((root / "intake-submission.v3.template.json").read_text(encoding="utf-8"))
    value["contract"]["scenario"] = {"id": "handout-source", "title": "Handout Source"}
    value["contract"]["scope"]["required_entities"] = {"handout_label_sets": [
        {"scope_id": "alpha", "labels": [
            {"label": "1", "occurrences": [{"source_page": 1, "section": "body"}]}
        ]}
    ]}
    value["contract"]["page_roles"] = [{"role": "body", "first_page": 1, "last_page": 1, "content_mode": "text", "traits": [], "strategies": ["reading_order"]}]
    value["contract"]["reconstruction"]["strategies"] = ["reading_order"]
    return value


def test_v3_intake_binds_scalar_source_to_runspec_v4_and_source_identity(tmp_path: Path):
    source = tmp_path / "source.pdf"
    _source(source)
    intake_root = tmp_path / "intake"
    intake.prepare_intake(source, intake_root)
    submission = _v3_submission(intake_root)
    submission_path = tmp_path / "submission.json"
    submission_path.write_text(json.dumps(submission), encoding="utf-8")
    contract = intake._validate_submission(intake_root, submission_path)
    assert contract["contract_revision"] == 3
    assert contract["source"].get("media_box_points") == [500, 700]
    runtime, _, _ = _runtime_fixture(tmp_path / "runtime")
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    run = reconstruction.build_run_spec(contract_path, source, tmp_path / "run", "handout-v3", runtime)
    assert run["schema"] == cpu.RUN_SCHEMA_V4
    validate(run, json.loads((CONTRACTS / "run_spec.v4.schema.json").read_text(encoding="utf-8")))
    identity = promotion._source_identity(run, contract)
    validate(identity, json.loads((CONTRACTS / "reconstruction_source_identity.v3.schema.json").read_text(encoding="utf-8")))
    promotion._validate_source_identity(identity, "handout-source")


@pytest.mark.parametrize("mutation", ["bool_count", "nan_box", "unordered_scope", "unordered_occurrence", "wrong_section", "unknown_section_role"])
def test_v3_authority_rejects_noncanonical_scalar_and_ordering(tmp_path: Path, mutation: str):
    source = tmp_path / "source.pdf"
    _source(source)
    root = tmp_path / "intake"
    intake.prepare_intake(source, root)
    value = _v3_submission(root)
    contract = {"schema": reconstruction.CONTRACT_SCHEMA_V3, "contract_revision": 3, **value["contract"], "source": value["source"]}
    if mutation == "bool_count":
        contract["source"]["page_count"] = True
    elif mutation == "nan_box":
        contract["source"]["media_box_points"][0] = math.nan
    elif mutation == "unordered_scope":
        contract["scope"]["required_entities"]["handout_label_sets"].insert(0, {"scope_id": "zeta", "labels": [{"label": "1", "occurrences": [{"source_page": 1, "section": "body"}]}]})
    else:
        if mutation == "unordered_occurrence":
            contract["source"]["page_count"] = 2
            contract["scope"]["last_page"] = 2
            contract["scope"]["required_entities"]["handout_label_sets"][0]["labels"][0]["occurrences"] = [{"source_page": 2, "section": "body"}, {"source_page": 1, "section": "body"}]
        elif mutation == "wrong_section":
            contract["scope"]["required_entities"]["handout_label_sets"][0]["labels"][0]["occurrences"][0]["section"] = "appendix"
        else:
            contract["page_roles"][0]["role"] = "front_matter"
    with pytest.raises(reconstruction.ControlPlaneError):
        reconstruction.validate_contract(copy.deepcopy(contract))


def test_v3_contract_schema_is_closed_for_scalar_and_per_page_authorities(tmp_path: Path):
    source = tmp_path / "source.pdf"
    _source(source)
    root = tmp_path / "intake"
    intake.prepare_intake(source, root)
    value = _v3_submission(root)
    scalar = {"schema": reconstruction.CONTRACT_SCHEMA_V3, "contract_revision": 3, **value["contract"], "source": value["source"]}
    schema = json.loads((CONTRACTS / "scenario_reconstruction_contract.v3.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validate(scalar, schema)
    per_page = copy.deepcopy(scalar)
    per_page["source"] = {
        "sha256": scalar["source"]["sha256"], "byte_count": scalar["source"]["byte_count"], "page_count": 1,
        "page_geometry": [{"source_page": 1, "media_box_coordinates": [0, 0, 500, 700], "crop_box_coordinates": [0, 0, 500, 700], "rotation_degrees": 0, "user_unit": 1}],
    }
    validate(per_page, schema)
    unknown = copy.deepcopy(scalar)
    unknown["scope"]["required_entities"]["handout_label_sets"][0]["labels"][0]["unexpected"] = True
    with pytest.raises(ValidationError):
        validate(unknown, schema)
    missing = copy.deepcopy(scalar)
    del missing["scope"]["required_entities"]["handout_label_sets"][0]["labels"][0]["occurrences"][0]["section"]
    with pytest.raises(ValidationError):
        validate(missing, schema)


def test_v4_run_passes_replay_source_schema_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source = tmp_path / "source.pdf"
    _source(source)
    intake_root = tmp_path / "intake"
    intake.prepare_intake(source, intake_root)
    contract = {"schema": reconstruction.CONTRACT_SCHEMA_V3, "contract_revision": 3, **_v3_submission(intake_root)["contract"], "source": _v3_submission(intake_root)["source"]}
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    runtime, _, _ = _runtime_fixture(tmp_path / "runtime")
    run_root = tmp_path / "run"
    run = reconstruction.write_run(contract_path, source, run_root, "v4-replay", runtime)
    assert run["schema"] == cpu.RUN_SCHEMA_V4
    monkeypatch.setattr(replay, "_runtime_matches", lambda *args: None)
    monkeypatch.setattr(reconstruction, "_validate_stage_prefix", lambda *args: [])
    registry = replay.load_registry()
    monkeypatch.setattr(replay, "load_registry", lambda: {"stages": [], "registry_sha256": registry["registry_sha256"]})
    result = replay.verify_replay_source(contract_path, source, run_root, "04", runtime)
    assert result["state"] == "eligible"


def test_v3_candidate_gate_uses_reviewed_decision_occurrences_and_rejects_missing_label(tmp_path: Path):
    """Exercise the candidate gate after a real fixture materialization, without OCR."""
    source = tmp_path / "promotion-source.pdf"
    promotion_source(source)
    legacy = tmp_path / "legacy-contract.json"
    legacy.write_text(json.dumps(legacy_contract(source, 1)), encoding="utf-8")
    run_root = tmp_path / "run"
    reconstruction.run_engine(legacy, source, run_root, "v3-candidate", _run_adapters(), _runtime(tmp_path / "runtime"))
    decision_set, decisions_root = _closed_decisions(run_root, tmp_path / "decisions", 1)
    page = decisions_root / "pages/page-002.json"
    decision = json.loads(page.read_text(encoding="utf-8"))
    decision["markdown"] = "## Player Handout A"
    page.write_text(json.dumps(decision), encoding="utf-8")
    decision_set_value = json.loads(decision_set.read_text(encoding="utf-8"))
    decision_set_value["decisions"][1].update(file_identity(page))
    decision_set.write_text(json.dumps(decision_set_value), encoding="utf-8")
    reconstruction.resume_engine(run_root, decision_set, decisions_root, _resume_adapters(run_root, 1))

    contract = legacy_contract(source, 0)
    contract.update(schema=reconstruction.CONTRACT_SCHEMA_V3, contract_revision=3)
    contract["scope"]["required_entities"] = {"handout_label_sets": [
        {"scope_id": "alpha", "labels": [{"label": "A", "occurrences": [{"source_page": 2, "section": "body"}]}]}
    ]}
    reconstruction.validate_contract(contract)
    snapshot = run_root / "review/validated-submission-v1"
    promotion._validate_candidate(run_root, contract, snapshot, json.loads((snapshot / "decision_set.json").read_text(encoding="utf-8")))
    missing = copy.deepcopy(contract)
    missing["scope"]["required_entities"]["handout_label_sets"][0]["labels"].append(
        {"label": "B", "occurrences": [{"source_page": 2, "section": "body"}]}
    )
    with pytest.raises(promotion.ReconstructionPromotionError, match="handout occurrence ledger mismatch"):
        promotion._validate_candidate(run_root, missing, snapshot, json.loads((snapshot / "decision_set.json").read_text(encoding="utf-8")))
