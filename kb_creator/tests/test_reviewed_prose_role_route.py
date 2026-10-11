"""Exercise reviewed prose roles through authoring and replay, not only helpers."""

import json
from copy import deepcopy

import pytest

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.scripts import author_reviewed_semantic_decisions as author
from kb_creator.tests.test_after_anchor_route import _resume_fixture


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("corrected", [False, True])
def test_prose_role_public_preflight_author_and_replay(tmp_path, monkeypatch, corrected):
    fixture = _resume_fixture()
    authorities, _, baseline = fixture._fixture(tmp_path)
    run = authorities.run_root
    reader = "An ordinary prose paragraph."
    source = reader.replace("prose", "pr0se") if corrected else reader
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = _read(packet_path)
    comparison = _read(authorities.comparison)
    for view, data in packet["views"].items():
        block = data["blocks"][0]
        block["text"] = source
        block["semantic_evidence"]["markdown_heading"] = True
        comparison["views"][view]["blocks"] = deepcopy(data["blocks"])
    _write(packet_path, packet)
    comparison.pop("comparison_sha256")
    comparison = sealed("kb_creator.mineru_multi_view_comparison.v3", comparison, digest_key="comparison_sha256")
    _write(authorities.comparison, comparison)
    visual_rel = "visual/original_pipeline_txt/pages/page-001.png"
    visual_file = run / "outputs/04-visual-merge-bundle" / visual_rel
    visual_file.parent.mkdir(parents=True)
    visual_file.write_bytes(b"synthetic reviewed prose visual")
    manifest = _read(authorities.visual_manifest)
    manifest.pop("manifest_sha256")
    manifest["files"].append({"path": visual_rel, **file_identity(visual_file)})
    _write(authorities.visual_manifest, sealed("kb_creator.mineru_visual_merge_bundle.v3", manifest, digest_key="manifest_sha256"))
    queue_path = run / "review/review_queue.json"
    queue = _read(queue_path)
    queue.pop("queue_sha256")
    queue["comparison"].update(file_identity(authorities.comparison))
    queue["items"][0]["merge_packet"].update(file_identity(packet_path))
    _write(queue_path, sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256"))
    run_data = _read(run / "run.json")
    from pathlib import Path
    run_data["source"].update(file_identity(Path(run_data["local"]["source_path"])))
    _write(run / "run.json", run_data)
    decision_path = baseline / "pages/page-001.json"
    decision = _read(decision_path)
    decision["markdown"] = source
    _write(decision_path, decision)
    page = {
        "source_page": 1, "role_contract": {"role": "body", "group_id": "prose"}, "units": [],
        "reviewed_prose_roles_v1": [{"role": "ordinary_prose", "view": "original_pipeline_txt", "raw_index": 0,
            "markdown_span": {"start_line": 1, "end_line": 1}, "visual_reviewed": True,
            "rationale": "Source typography is an ordinary paragraph; detector title is a false positive."}],
    }
    if corrected:
        page["post_patches"] = [{"before": source, "after": reader, "count": 1}]
        page["reviewed_block_corrections"] = [{"view": "original_pipeline_txt", "raw_index": 0,
            "before": "pr0se", "after": "prose", "reason": "Exact source visual spelling."}]
        page["reviewed_prose_bindings_v1"] = [{"view": "original_pipeline_txt", "raw_index": 0,
            "markdown_span": {"start_line": 1, "end_line": 1}}]
    spec = tmp_path / "role-spec.json"
    _write(spec, {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": [page]})
    candidate, authored = tmp_path / "preflight", tmp_path / "authored"
    author.validate_spec(run, baseline, [spec], candidate_output=candidate)
    author.author(run, baseline, authored, [spec])
    expected = _read(candidate / "pages/page-001.json")
    actual = _read(authored / "pages/page-001.json")
    assert actual["markdown"] == reader
    assert actual["reviewed_prose_roles_v1"] == expected["reviewed_prose_roles_v1"]
    assert actual["semantic_structure"]["units"] == []
    fixture._patch_prefix(monkeypatch, authorities)
    result = fixture.resume.replay_resume_engine(run, authored / "decision_set.json", authored)
    assert result["state"] == "candidate_ready_for_reconstruction_qa"
    audit = _read(run / "outputs/05-fidelity-audit/audit.json")
    assert audit["passed"] is True
    # Removing the role must restore the structural failure, despite identical text.
    from kb_creator.pipeline.semantic_structure import SemanticStructureError, validate_semantic_structure
    actual.pop("reviewed_prose_roles_v1")
    inventory = author._visual_inventory(run)
    with pytest.raises(SemanticStructureError):
        validate_semantic_structure({1: actual}, {1: packet}, inventory, required_pages=[1])


@pytest.mark.parametrize("empty_region", [False, True])
def test_prose_role_review_draft_and_real_successor(tmp_path, monkeypatch, empty_region):
    from pathlib import Path
    from kb_creator.tests import test_source_choice_composite_integration as fixture
    from kb_creator.scripts.materialize_mineru_ai_merge import _validated_v2_title_role

    built = fixture._build_r0(tmp_path, monkeypatch, whole_block_correction=True,
        empty_region=empty_region, quoted_dialogue=not empty_region, prose_role=True)
    r0 = _read(tmp_path / "r0-authored/pages/page-001.json")
    role = r0["reviewed_prose_roles_v1"][0]
    key = (role["view"], role["raw_index"])
    packet = _read(built["run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json")
    allowlist = _read(tmp_path / "r0-authored/reviewed_allowlist.v3.json")
    assertions = {r["assertion_id"]: r for r in allowlist["visual_text_assertions"]}
    assert _validated_v2_title_role(r0, packet, "Good second paragraph.", key, set(), assertions)
    if empty_region:
        assert not _validated_v2_title_role(r0, packet, "Good second paragraph.", key, set(), {})
    removed = deepcopy(r0)
    removed.pop("reviewed_prose_roles_v1")
    assert not _validated_v2_title_role(removed, packet, "Good second paragraph.", key, set(), assertions)
    queue = Path(fixture.choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "queue", binding_root=tmp_path)["queue"])
    selected = []
    for row in _read(queue)["choices"]:
        alternative = next(a for a in row["alternatives"] if a["alternative_id"] == row["provisional_alternative_id"])
        if not empty_region and alternative["raw_text"] == "Bad first paragraph.":
            alternative = next(a for a in row["alternatives"] if a["raw_text"] == "Alternate first paragraph.")
        selected.append((row["issue_id"], alternative["alternative_id"]))
    submission = fixture._submission_choices(queue, selected, tmp_path / "submission.json")
    ledger = Path(fixture.choices.record_decisions_v2(queue, submission, tmp_path / "ledger")["ledger"])
    r1 = fixture.prepare_source_choice_successor(input_path=built["r0_input"], binding_root=tmp_path,
        ledger_path=ledger, draft_pages=built["draft_pages"], spec_paths=built["spec_paths"], output_dir=tmp_path / "r1-input")
    authored = tmp_path / "r1-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored,
        [Path(p) for p in r1["spec_paths"]], mode="review_draft", draft_input=Path(r1["input"]["path"]), binding_root=tmp_path)
    final = _read(authored / "pages/page-001.json")
    final_role = final["reviewed_prose_roles_v1"][0]
    assert final["markdown"].splitlines()[final_role["markdown_span"]["start_line"] - 1] == "Good second paragraph."
    assert final_role["original_text_sha256"] == role["original_text_sha256"]
    assert final_role["markdown_span"]["start_line"] == (5 if empty_region else 3)
    evidence = authored / "review-draft-evidence.json"
    descriptor = fixture.verify_final_review_draft(run_root=built["run"], authored_root=authored,
        input_path=Path(r1["input"]["path"]), evidence_path=evidence, binding_root=tmp_path)
    materialized = tmp_path / "r1-materialized"
    fixture.materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
        Path(descriptor["decisions_root"]), materialized, review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    fixture.build_review_master_en(materialized, evidence, tmp_path / "r1-master", binding_root=tmp_path)
    assert (tmp_path / "r1-master/MASTER_EN.md").read_text(encoding="utf-8").endswith("Good second paragraph.\n")
