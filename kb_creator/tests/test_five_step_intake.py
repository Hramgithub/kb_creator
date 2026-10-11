from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from kb_creator.pipeline import five_step_intake as intake
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.manifests import sealed


def test_decision_author_preserves_reviewed_structural_profile(tmp_path, monkeypatch):
    queue = {"items": [{"source_page": 1}], "required_decision_schema": "kb_creator.mineru_ai_page_decision.v1",
             "queue_sha256": "A" * 64, "contract_sha256": "B" * 64, "source_sha256": "C" * 64}
    monkeypatch.setattr(intake.reconstruction, "load_run", lambda _: {})
    monkeypatch.setattr(intake.reconstruction, "validate_queue", lambda *_: queue)
    decision = tmp_path / "page.json"
    _write(decision, {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1,
                      "unresolved": [], "review": {"visual_reviewed": True},
                      "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2"}})
    result = intake.author_reconstruction_decision_set(tmp_path, [decision], tmp_path / "submitted")
    value = json.loads(Path(result["decision_set"]).read_text())
    assert value["schema"] == intake.reconstruction.DECISION_SET_V2_SCHEMA
    assert value["semantic_structure_profile"] == "reviewed_role_outline_and_partitions_v2"
    assert value["decisions"][0]["sha256"] == file_identity(decision)["sha256"]
    allowlist = tmp_path / "reviewed.json"
    _write(allowlist, {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v2", "source_text_exclusions": []})
    packaged = intake.author_reconstruction_decision_set(tmp_path, [decision], tmp_path / "with-allowlist", reviewed_allowlist=allowlist)
    authored = json.loads(Path(packaged["decision_set"]).read_text())
    assert authored["reviewed_allowlist"] == {"path": "reviewed_allowlist.json", **file_identity(allowlist)}
    assert (tmp_path / "with-allowlist/reviewed_allowlist.json").read_bytes() == allowlist.read_bytes()
    with pytest.raises(intake.FiveStepIntakeError, match="every queued page"):
        intake.author_reconstruction_decision_set(tmp_path, [], tmp_path / "missing")


def test_reviewed_source_span_maps_exact_page_lines_without_vocabulary_guess(tmp_path):
    body = "## Record\n\nField 12  \nOther field 30"
    master = tmp_path / "MASTER_EN.md"
    master.write_text("<!-- source-page-001 -->\n\nProse says STR 20.\n\n" + body + "\n", encoding="utf-8")
    decision = tmp_path / "decision.json"
    _write(decision, {"source_page": 1, "markdown": body, "semantic_structure": {"units": [
        {"id": "record", "kind": "statblock", "container_parent": None,
         "markdown_span": {"start_line": 1, "end_line": 4, "sha256": sha256_bytes(body.encode())}}
    ]}})
    result = intake._source_spans(master, [decision], tmp_path)
    assert len(result["spans"]) == 1
    assert result["spans"][0]["start_line"] == 5
    assert result["spans"][0]["end_line"] == 8
    master.write_text(master.read_text(encoding="utf-8") + "\n" + body + "\n", encoding="utf-8")
    with pytest.raises(intake.FiveStepIntakeError, match="unique exact"):
        intake._source_spans(master, [decision], tmp_path)
from kb_creator.pipeline.reconstruction import resume_engine, run_engine
from kb_creator.pipeline.reconstruction_promotion import materialize_reconstruction_promotion
from kb_creator.tests.test_reconstruction_promotion import (
    _closed_decisions, _contract, _resume_adapters, _run_adapters, _runtime,
    _source as promotion_source,
)


def _pdf(path: Path, pages: int = 2) -> None:
    document = canvas.Canvas(str(path))
    for number in range(pages):
        document.drawString(72, 720, f"source page {number + 1}")
        document.showPage()
    document.save()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _submission(passport: dict) -> dict:
    page_count = passport["source"]["page_count"]
    return {
        "schema": intake.SUBMISSION_SCHEMA,
        "passport_sha256": passport["intake_sha256"],
        "source": {
            "sha256": passport["source"]["sha256"], "byte_count": passport["source"]["bytes"],
            "page_count": page_count, "media_box_points": passport["source"]["media_box_points"],
            "rotation_degrees": passport["source"]["rotation_degrees"],
        },
        "contract": {
            "scenario": {"id": "short-source", "title": "Short Source"},
            "scope": {"mode": "all_source_pages", "first_page": 1, "last_page": page_count,
                      "required_entities": {"numbered_player_handouts": 0}},
            "page_roles": [{"role": "reviewed-pages", "first_page": 1, "last_page": page_count,
                            "content_mode": "mixed", "traits": [], "strategies": ["reading_order"]}],
            "reconstruction": {"strategies": ["reading_order"], "required_review": True},
            "acceptance": {"approval_authority": "configured_reconstruction_review"},
        },
    }


def test_prepare_and_submit_binds_current_source_and_closed_page_contract(tmp_path: Path) -> None:
    source = tmp_path / "short.pdf"
    _pdf(source)
    intake_root = tmp_path / "intake"
    result = intake.prepare_intake(source, intake_root)
    assert result["state"] == "needs_agent_work"
    passport = json.loads((intake_root / "passport.json").read_text(encoding="utf-8"))
    assert [row["role"] for row in passport["draft_page_coverage"]] == ["unknown", "unknown"]
    submission = tmp_path / "submission.json"
    _write(submission, _submission(passport))
    contract_root = tmp_path / "contract"
    submitted = intake.submit_intake(intake_root, submission, contract_root)
    assert submitted["state"] == "contract_ready"
    assert json.loads(Path(submitted["contract_path"]).read_text(encoding="utf-8"))["scenario"]["id"] == "short-source"


def test_submit_rejects_source_changed_after_intake(tmp_path: Path) -> None:
    source = tmp_path / "short.pdf"
    _pdf(source)
    intake_root = tmp_path / "intake"
    intake.prepare_intake(source, intake_root)
    passport = json.loads((intake_root / "passport.json").read_text(encoding="utf-8"))
    _pdf(source, pages=3)
    submission = tmp_path / "submission.json"
    _write(submission, _submission(passport))
    with pytest.raises(intake.FiveStepIntakeError, match="source changed"):
        intake.submit_intake(intake_root, submission, tmp_path / "contract")


def test_start_reconstruction_exposes_existing_decision_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run_root = tmp_path / "run"
    review = run_root / "review"
    review.mkdir(parents=True)
    _write(review / "decision_set.template.json", {"schema": "template"})
    _write(review / "review_queue.json", {"schema": "queue"})

    def fake_run(*args, **kwargs):
        return {"state": "needs_review", "review_queue": str(review / "review_queue.json")}

    monkeypatch.setattr(intake.reconstruction, "run_engine", fake_run)
    result = intake.start_reconstruction(tmp_path / "contract.json", tmp_path / "source.pdf", run_root, "run-1", None)
    task = json.loads(Path(result["task_path"]).read_text(encoding="utf-8"))
    assert result["template_path"].endswith("decision_set.template.json")
    assert task["review_queue"]["path"] == "review/review_queue.json"


def _promoted_root(tmp_path: Path) -> tuple[Path, Path]:
    run_root = tmp_path / "upstream" / "short-source" / "reconstruction" / "run-001"
    package = run_root / "promotion" / "reconstruction-upstream-v1"
    content = package / "content"
    (content / "assets").mkdir(parents=True)
    (content / "pages").mkdir()
    (content / "assets" / "map.png").write_bytes(b"map")
    (content / "pages" / "page-001.md").write_text("first\n", encoding="utf-8")
    (content / "pages" / "page-002.md").write_text("second\n", encoding="utf-8")
    (content / "RECONSTRUCTED_EN.md").write_text(
        "<!-- source-page-001 -->\n# One\n![map](assets/map.png)\n<!-- source-page-002 -->\n# Two\n", encoding="utf-8"
    )
    (content / "SEMANTIC_STRUCTURE.json").write_text("{}\n", encoding="utf-8")
    source_record = {"basename": "short.pdf", "bytes": 42, "sha256": "A" * 64,
                     "page_count": 2, "media_box_points": [612.0, 792.0], "rotation_degrees": 0}
    _write(package / "SOURCE_IDENTITY.json", {"source": source_record})
    _write(package / "RECONSTRUCTION_MANIFEST.json", {"scenario": {"id": "short-source"}, "review": {}})
    task = run_root / "five-step-reconstruction.task.json"
    _write(task, {"task": "bound"})
    review = run_root / "agent-review-authority.json"
    manifest_identity = {"path": "RECONSTRUCTION_MANIFEST.json", **file_identity(package / "RECONSTRUCTION_MANIFEST.json")}
    authority = sealed(intake.AUTHORITY_SCHEMA, {
        "scenario_id": "short-source", "stage": "reconstruction", "source": source_record,
        "task": {"path": "five-step-reconstruction.task.json", **file_identity(task)},
        "submission": {}, "evidence": [manifest_identity],
        "reviewer_role": "codex_content_executor", "reviewed_at_utc": "2026-09-19T00:00:00Z", "unresolved": [],
    }, digest_key="authority_sha256")
    _write(review, authority)
    return package, review


def test_build_master_en_preserves_pages_assets_and_detects_lost_asset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    package, review = _promoted_root(tmp_path)
    monkeypatch.setattr(intake.reconstruction_promotion, "validate_reconstruction_package", lambda *args, **kwargs: ({}, None))
    # The lightweight package intentionally has no full promotion review; bind it
    # to the exact task/evidence shape required by the new authority verifier.
    manifest = json.loads((package / "RECONSTRUCTION_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["review"] = {"queue": {}, "decision_set": {}, "decisions": []}
    manifest["fidelity"] = {}
    manifest["qa"] = {}
    _write(package / "RECONSTRUCTION_MANIFEST.next.json", manifest)
    (package / "RECONSTRUCTION_MANIFEST.json").unlink()
    (package / "RECONSTRUCTION_MANIFEST.next.json").rename(package / "RECONSTRUCTION_MANIFEST.json")
    authority = json.loads(review.read_text(encoding="utf-8"))
    authority["submission"] = {}
    authority["evidence"] = [{"path": "RECONSTRUCTION_MANIFEST.json", **file_identity(package / "RECONSTRUCTION_MANIFEST.json")}, {}, {}, {}, {}]
    authority.pop("authority_sha256")
    _write(review.with_suffix(".next"), sealed(intake.AUTHORITY_SCHEMA, authority, digest_key="authority_sha256"))
    review.unlink(); review.with_suffix(".next").rename(review)
    output = tmp_path / "master-en"
    result = intake.build_master_en(package, review, output)
    assert result["state"] == "verified"
    assert (output / "pages" / "page-002.md").is_file()
    assert (output / "SEMANTIC_STRUCTURE.json").is_file()
    (output / "assets" / "map.png").unlink()
    with pytest.raises(intake.FiveStepIntakeError, match="inventory mismatch"):
        intake.verify_master_en(output)


def test_build_master_en_rejects_escaping_asset_reference(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    package, review = _promoted_root(tmp_path)
    monkeypatch.setattr(intake.reconstruction_promotion, "validate_reconstruction_package", lambda *args, **kwargs: ({}, None))
    # Reuse the same exact lightweight authority preparation as above.
    manifest = json.loads((package / "RECONSTRUCTION_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["review"] = {"queue": {}, "decision_set": {}, "decisions": []}; manifest["fidelity"] = {}; manifest["qa"] = {}
    _write(package / "RECONSTRUCTION_MANIFEST.next.json", manifest); (package / "RECONSTRUCTION_MANIFEST.json").unlink(); (package / "RECONSTRUCTION_MANIFEST.next.json").rename(package / "RECONSTRUCTION_MANIFEST.json")
    authority = json.loads(review.read_text(encoding="utf-8")); authority["submission"] = {}; authority["evidence"] = [{"path": "RECONSTRUCTION_MANIFEST.json", **file_identity(package / "RECONSTRUCTION_MANIFEST.json")}, {}, {}, {}, {}]; authority.pop("authority_sha256")
    _write(review.with_suffix(".next"), sealed(intake.AUTHORITY_SCHEMA, authority, digest_key="authority_sha256")); review.unlink(); review.with_suffix(".next").rename(review)
    source = package / "content" / "RECONSTRUCTED_EN.md"
    source.write_text(source.read_text(encoding="utf-8").replace("assets/map.png", "../escape.png"), encoding="utf-8")
    with pytest.raises(intake.FiveStepIntakeError, match="escapes result root"):
        intake.build_master_en(package, review, tmp_path / "master-en")


def test_build_master_en_validates_real_promoted_package(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"; promotion_source(source)
    contract = tmp_path / "contract.json"; _write(contract, _contract(source, 1))
    run_root = tmp_path / "upstream" / "sample" / "reconstruction" / f"run-{uuid.uuid4().hex}"
    run_root.parent.mkdir(parents=True)
    run_engine(contract, source, run_root, run_root.name, adapters=_run_adapters(), runtime=_runtime(tmp_path / "runtime"))
    decision_set, decisions_root = _closed_decisions(run_root, tmp_path / "decisions", 1, None)
    resume_engine(run_root, decision_set, decisions_root, adapters=_resume_adapters(run_root, 1))
    _write(run_root / "five-step-reconstruction.task.json", {"schema": "task"})
    promoted = materialize_reconstruction_promotion(run_root, working_root=tmp_path / "upstream")
    package = Path(promoted["package_root"])
    authority = intake._agent_authority(run_root, package)
    review = run_root / "agent-review-authority.json"; _write(review, authority)
    assert intake._validate_authority(package, review)["scenario_id"] == "sample"
    result = intake.build_master_en(package, review, tmp_path / "master-en-real")
    assert result["state"] == "verified"
    assert (tmp_path / "master-en-real" / "assets" / "handout.png").is_file()
    _write(run_root / "five-step-reconstruction.task.next.json", {"schema": "changed"})
    (run_root / "five-step-reconstruction.task.json").unlink()
    (run_root / "five-step-reconstruction.task.next.json").rename(run_root / "five-step-reconstruction.task.json")
    with pytest.raises(intake.FiveStepIntakeError, match="authority is stale"):
        intake._validate_authority(package, review)
