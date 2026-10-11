"""Small public route for an additive owner after an intact lexical successor."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.review_draft_materialization import verify_final_review_draft
from kb_creator.pipeline.five_step_intake import build_review_master_en, verify_master_en
from kb_creator.pipeline.review_draft_preparation import validate_review_draft_author_input
from kb_creator.pipeline.semantic_owner_successor import (
    SemanticOwnerSuccessorError, _recorded_authorities,
    prepare_review_draft_semantic_owner_successor,
)
from kb_creator.pipeline.source_choice_successor_preparation import prepare_source_choice_successor
from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.scripts import author_reviewed_semantic_decisions as author
from kb_creator.scripts import materialize_mineru_ai_merge as materializer


def _fixture_module():
    path = Path(__file__).with_name("test_source_choice_composite_integration.py")
    spec = importlib.util.spec_from_file_location("owner_composite_fixture", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _case(tmp_path, monkeypatch):
    fixture = _fixture_module()
    built = fixture._build_r0(tmp_path, monkeypatch, whole_block_correction=True,
                              quoted_dialogue=True, lexical_unowned_second=True,
                              owner_successor_fixture=True)
    original = _read(Path(built["spec_paths"][0]))
    decision = _read(built["master"] / "evidence/review/page-001.json")
    packet = _read(built["run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json")
    line = decision["markdown"].split("\n").index("Bad second paragraph.") + 1
    selected = [(row["view"], row["raw_index"]) for row in decision["selected_blocks"]]
    second = next((view, raw) for view, raw in selected if any(
        block.get("raw_index") == raw and block.get("text") == "Bad second paragraph."
        for block in packet["views"][view]["blocks"]))
    reviewed = copy.deepcopy(original)
    reviewed["pages"][0]["units"].append({"id": "added-second-label", "kind": "label",
        "representation": "semantic_span", "view": second[0], "raw_indices": [second[1]],
        "start_line": line, "end_line": line})
    reviewed_path = _write(tmp_path / "reviewed-augmented-spec.json", reviewed)
    queue_path = Path(choices.prepare_v2(built["master"], built["mechanical"],
        tmp_path / "owner-queue", binding_root=tmp_path)["queue"])
    queue = _read(queue_path)
    selected_rows = []
    for row in queue["choices"]:
        candidate = next((alternative for alternative in row["alternatives"]
                          if alternative.get("selectable") and
                          "Alternate" in alternative.get("reader_text", "")), None)
        selected_rows.append((row["issue_id"], candidate["alternative_id"] if candidate
                              else row["provisional_alternative_id"]))
    ledger_path = Path(choices.record_decisions_v2(queue_path,
        fixture._submission_choices(queue_path, selected_rows, tmp_path / "owner-submission.json"),
        tmp_path / "owner-ledger")["ledger"])
    r1 = prepare_source_choice_successor(input_path=built["r0_input"], binding_root=tmp_path,
        ledger_path=ledger_path, draft_pages=built["draft_pages"], spec_paths=built["spec_paths"],
        output_dir=tmp_path / "owner-lexical-r1")
    stage_output = built["run"] / "outputs/04-visual-merge-bundle"
    recorded = [
        {"path": relative, **file_identity(stage_output / relative)}
        for relative in ("merge_packets/pages/page-001.json", "visual/visual_manifest.json",
                         "visual/geometry_plan.json")
    ]
    reproducible = {"outputs": {"files": recorded}}
    _write(built["run"] / "stages/04-visual-merge-bundle/stage.json", {
        "reproducible": reproducible,
        "reproducible_sha256": sha256_bytes(canonical_bytes(reproducible)),
    })
    return built, r1, reviewed_path, ledger_path


def test_additive_owner_small_public_route(tmp_path, monkeypatch):
    built, r1, reviewed, ledger = _case(tmp_path, monkeypatch)
    lexical_input = Path(r1["input"]["path"])
    result = prepare_review_draft_semantic_owner_successor(
        lexical_input=lexical_input, binding_root=tmp_path,
        reviewed_spec_paths=[reviewed], output_dir=tmp_path / "owner-prepared")
    assert result["state"] == "prepared_pending_validation"
    assert result["added_owner_count"] == result["page_count"] == 1
    input_path, spec_path = Path(result["input_path"]), Path(result["spec_paths"][0])
    old_input, new_input = _read(lexical_input), _read(input_path)
    assert new_input["source_issues"] == old_input["source_issues"]
    assert new_input["unresolved_dispositions"] == old_input["unresolved_dispositions"]
    for name, record in old_input["bindings"].items():
        if not name.startswith("source_choice_successor_spec-"):
            assert new_input["bindings"][name] == record
    assert new_input["bindings"]["source_choice_ledger"] == old_input["bindings"]["source_choice_ledger"]
    assert new_input["bindings"]["semantic_owner_predecessor_input"]["sha256"] == file_identity(lexical_input)["sha256"]
    old_units = _read(Path(r1["spec_paths"][0]))["pages"][0]["units"]
    units = _read(spec_path)["pages"][0]["units"]
    assert [unit for unit in units if unit["id"] != "added-second-label"] == old_units
    assert next(unit for unit in units if unit["id"] == "added-second-label")["start_line"] < 5
    preflight = author.validate_spec(built["run"], None, [spec_path],
        draft_pages=Path(result["draft_pages"]), draft_input=input_path, binding_root=tmp_path)
    assert preflight["correction_coverage"]["unbound_keys"] == 0
    authored = tmp_path / "owner-authored"
    author.author_drafts(built["run"], Path(result["draft_pages"]), authored, [spec_path],
        mode="review_draft", draft_input=input_path, binding_root=tmp_path)
    descriptor = verify_final_review_draft(run_root=built["run"], authored_root=authored,
        input_path=input_path, evidence_path=authored / "review-draft-evidence.json", binding_root=tmp_path)
    assert Path(descriptor["decisions_root"]).is_dir()
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
        Path(descriptor["decisions_root"]), tmp_path / "owner-materialized",
        review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    master = tmp_path / "owner-master"
    build_review_master_en(tmp_path / "owner-materialized", authored / "review-draft-evidence.json",
                           master, binding_root=tmp_path)
    assert verify_master_en(master, binding_root=tmp_path)["state"] == "verified_review_draft"


@pytest.mark.parametrize("mutation", ["old_unit", "remove_unit", "duplicate_id", "foreign_source",
                                     "unselected_source", "duplicate_ownership", "crossing_span",
                                     "altered_fragment", "wrong_line", "non_unit_field", "no_addition"])
def test_additive_owner_rejects_reviewed_drift(tmp_path, monkeypatch, mutation):
    built, r1, reviewed, _ = _case(tmp_path, monkeypatch)
    spec = _read(reviewed)
    units = spec["pages"][0]["units"]
    if mutation == "old_unit":
        units[0]["kind"] = "paragraph"
    elif mutation == "remove_unit":
        units.pop(0)
    elif mutation == "duplicate_id":
        units[-1]["id"] = units[0]["id"]
    elif mutation == "foreign_source":
        units[-1]["raw_indices"] = [999999]
    elif mutation == "unselected_source":
        units[-1]["view"] = "original_pipeline_ocr"
    elif mutation == "duplicate_ownership":
        units[-1]["raw_indices"] = units[0]["raw_indices"]
    elif mutation == "crossing_span":
        units[-1]["start_line"] = 3
    elif mutation == "altered_fragment":
        units[-1]["source_fragments"] = [{"view": units[-1]["view"],
            "raw_index": units[-1]["raw_indices"][0], "start": 0, "end": 3}]
    elif mutation == "wrong_line":
        units[-1]["start_line"] = 999
    elif mutation == "non_unit_field":
        spec["pages"][0]["post_patches"] = []
    elif mutation == "no_addition":
        units.pop()
    _write(reviewed, spec)
    with pytest.raises((SemanticOwnerSuccessorError, ValueError)):
        prepare_review_draft_semantic_owner_successor(
            lexical_input=Path(r1["input"]["path"]), binding_root=tmp_path,
            reviewed_spec_paths=[reviewed], output_dir=tmp_path / "rejected-owner")
    assert not (tmp_path / "rejected-owner").exists()


@pytest.mark.parametrize("mutation", ["predecessor", "queue", "ledger", "submission",
                                     "review_manifest", "packet", "decision", "coverage", "draft"])
def test_additive_owner_rejects_record_drift(tmp_path, monkeypatch, mutation):
    built, r1, reviewed, ledger = _case(tmp_path, monkeypatch)
    lexical = _read(Path(r1["input"]["path"]))
    if mutation in {"predecessor", "queue", "ledger", "coverage", "draft"}:
        key = {"predecessor": "source_choice_predecessor", "queue": "source_choice_queue",
               "ledger": "source_choice_ledger", "coverage": "source_choice_coverage_dispositions",
               "draft": "source_choice_successor_page-001"}[mutation]
        path = tmp_path / lexical["bindings"][key]["path"]
    elif mutation == "submission":
        path = ledger.parent / "SOURCE_CHOICE_SUBMISSION.v2.json"
    elif mutation == "review_manifest":
        queue = _read(tmp_path / lexical["bindings"]["source_choice_queue"]["path"])
        path = Path(queue["review_manifest"]["path"])
    elif mutation == "packet":
        path = built["run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    else:
        path = built["master"] / "evidence/review/page-001.json"
    if mutation == "submission":
        changed = _read(path)
        changed["choices"][0]["reason"] = "Foreign submission decision"
        _write(path, changed)
    else:
        path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises((SemanticOwnerSuccessorError, ValueError)):
        prepare_review_draft_semantic_owner_successor(
            lexical_input=Path(r1["input"]["path"]), binding_root=tmp_path,
            reviewed_spec_paths=[reviewed], output_dir=tmp_path / "rejected-record")
    assert not (tmp_path / "rejected-record").exists()


def test_public_preflight_and_author_reject_resealed_wrong_spec_path(tmp_path, monkeypatch):
    built, r1, reviewed, _ = _case(tmp_path, monkeypatch)
    result = prepare_review_draft_semantic_owner_successor(
        lexical_input=Path(r1["input"]["path"]), binding_root=tmp_path,
        reviewed_spec_paths=[reviewed], output_dir=tmp_path / "owner-prepared")
    original = Path(result["spec_paths"][0])
    foreign = tmp_path / "foreign-copied-spec.json"
    foreign.write_bytes(original.read_bytes())
    input_path = tmp_path / "resealed-wrong-spec.json"
    value = _read(Path(result["input_path"]))
    value["bindings"]["source_choice_successor_spec-00"] = {"path": foreign.name,
        **file_identity(foreign)}
    value["input_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items()
                                                       if key != "input_sha256"}))
    _write(input_path, value)
    validate_review_draft_author_input(input_path=input_path, binding_root=tmp_path)
    with pytest.raises(ValueError, match="sealed semantic spec paths differ"):
        author.validate_spec(built["run"], None, [original],
            draft_pages=Path(result["draft_pages"]), draft_input=input_path, binding_root=tmp_path)
    with pytest.raises(ValueError, match="sealed semantic spec paths differ"):
        author.author_drafts(built["run"], Path(result["draft_pages"]), tmp_path / "forged-author",
            [original], mode="review_draft", draft_input=input_path, binding_root=tmp_path)
    assert not (tmp_path / "forged-author").exists()
    reviewed.write_bytes(reviewed.read_bytes() + b" ")
    with pytest.raises(ValueError, match="identity drift"):
        validate_review_draft_author_input(input_path=Path(result["input_path"]), binding_root=tmp_path)


def test_recorded_manifest_rejects_foreign_same_bytes_path(tmp_path, monkeypatch):
    _, r1, _, _ = _case(tmp_path, monkeypatch)
    lexical = _read(Path(r1["input"]["path"]))
    queue = _read(tmp_path / lexical["bindings"]["source_choice_queue"]["path"])
    original = Path(queue["review_manifest"]["path"])
    foreign = tmp_path / "foreign-master-manifest.json"
    foreign.write_bytes(original.read_bytes())
    queue["review_manifest"] = {"path": str(foreign.resolve()), **file_identity(foreign)}
    with pytest.raises(SemanticOwnerSuccessorError, match="differs from queued master"):
        _recorded_authorities(queue)
