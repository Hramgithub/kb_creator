from __future__ import annotations

import json
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from kb_creator.pipeline.identity import deterministic_inventory, file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline import five_step_successor as subject
from kb_creator.pipeline import five_step_language as language_subject
from kb_creator.tests.fidelity_fixture import synthetic_guard


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _predecessor(tmp_path: Path) -> Path:
    root = tmp_path / "previous"; root.mkdir()
    source = tmp_path / "source.pdf"
    pdf = canvas.Canvas(str(source), pagesize=(400, 600), invariant=1)
    pdf.drawString(20, 560, "Synthetic successor source")
    pdf.showPage(); pdf.save()
    glossary = tmp_path / "terms.json"; _write(glossary, {"terms": []})
    for name in ("language-001", "draft-001", "final-001"):
        directory = root / name; directory.mkdir(); _write(directory / "artifact.json", {"name": name})
    _write(root / "final-001" / "evidence" / "proofread.submission.json", {"units": []})
    evidence = root / "language-001"
    state = {"schema": "kb_creator.five_step_run.v1", "source": {"path": str(source), "identity": file_identity(source)}, "glossary": {"path": str(glossary), "identity": file_identity(glossary)}, "paths": {"language": str(root / "language-001"), "draft": str(root / "draft-001"), "final": str(root / "final-001")}, "title": "Fixture", "evidence": [{"step": 3, "root": "language-001", "files": deterministic_inventory(evidence), "code": [{"path": "old.py", "bytes": 1, "sha256": "0" * 64}]}]}
    _write(root / "state.json", sealed("kb_creator.five_step_run.v1", state, digest_key="state_sha256"))
    return root


@pytest.fixture
def language(monkeypatch: pytest.MonkeyPatch):
    def submit(language_root: Path, draft_root: Path, submission: Path, output: Path):
        output.mkdir(); (output / "MASTER_RU.md").write_text("# RU\n", encoding="utf-8")
        (output / "semantic_context").mkdir(); _write(output / "semantic_context" / "RU_PROJECTION.json", {"fixture": True})
        _write(output / "MASTER_RU.manifest.json", {"fixture": True})
        return {"master_ru": output / "MASTER_RU.md"}
    monkeypatch.setattr("kb_creator.pipeline.five_step_language.verify_language_result", lambda root: {"state": "verified"})
    monkeypatch.setattr("kb_creator.pipeline.five_step_language.submit_proofread", submit)


def test_prepare_preserves_predecessor_and_binds_full_submission(tmp_path: Path, language) -> None:
    previous = _predecessor(tmp_path); original = (previous / "state.json").read_bytes()
    submission = tmp_path / "submission.json"; _write(submission, {"units": []})
    result = subject.successor_prepare(previous, tmp_path / "successor", submission)
    assert result["state"] == "needs_reader_options"
    assert (previous / "state.json").read_bytes() == original
    state = json.loads((tmp_path / "successor" / "state.json").read_text(encoding="utf-8"))
    assert state["proofread_submission"]["identity"] == file_identity(submission)
    assert state["outputs"]["final"]["root"] == "final-001"


def test_prepare_rejects_changed_predecessor_evidence(tmp_path: Path, language) -> None:
    previous = _predecessor(tmp_path)
    (previous / "language-001" / "artifact.json").write_text("changed", encoding="utf-8")
    submission = tmp_path / "submission.json"; _write(submission, {})
    with pytest.raises(subject.FiveStepSuccessorError, match="inventory"):
        subject.successor_prepare(previous, tmp_path / "successor", submission)


def test_prepare_rejects_missing_submission_and_existing_successor(tmp_path: Path, language) -> None:
    previous = _predecessor(tmp_path)
    with pytest.raises(subject.FiveStepSuccessorError, match="submission"):
        subject.successor_prepare(previous, tmp_path / "successor", tmp_path / "missing.json")
    target = tmp_path / "successor"; target.mkdir()
    submission = tmp_path / "submission.json"; _write(submission, {})
    with pytest.raises(subject.FiveStepSuccessorError, match="root must be absent"):
        subject.successor_prepare(previous, target, submission)


@pytest.mark.parametrize("source,draft,final,reason,expected", [
    ("one\ntwo", "один\nдва", "один два", "prose reflow approved", True),
    ("- one\n- two", "- один\n- два", "- один - два", "prose reflow approved", False),
    ("one\ntwo", "один\nдва", "один три", "prose reflow approved", False),
    ("one\ntwo", "один\nдва", "один два", "ordinary edit", False),
])
def test_plain_prose_reflow_is_explicit_and_content_conserving(source, draft, final, reason, expected) -> None:
    row = {"source_text": source, "predecessor_final_ru_text": draft, "ru_text": final, "reason": reason}
    assert language_subject._declared_plain_prose_reflow(row) is expected


@pytest.mark.parametrize("tamper", [None, "seal", "source", "draft", "text", "unknown"])
def test_reflow_authority_rejects_tampering(tamper) -> None:
    binding = {"unit_id": "u1", "source_hash": "source", "draft_ru_sha256": "draft"}
    before = {**binding, "final_ru_text": "один\nдва"}
    after = {**binding, "final_ru_text": "один два"}
    if tamper == "source": before["source_hash"] = "other"
    if tamper == "draft": after["draft_ru_sha256"] = "other"
    if tamper == "text": after["final_ru_text"] = "один три"
    previous = language_subject._seal(
        "kb_creator.five_step_language_proofread_submission.v2", {"units": [before]}, "submission_sha256")
    if tamper == "seal": previous["units"][0]["final_ru_text"] = "подмена"
    supplied = {"units": [after], "reflow_authority": {
        "schema": "kb_creator.five_step_reflow_authority.v1",
        "predecessor_submission": previous,
        "rows": [{"unit_id": "unknown" if tamper == "unknown" else "u1"}]}}
    if tamper is None:
        assert language_subject._verified_reflow_texts(supplied, [binding]) == {"u1": "один\nдва"}
    else:
        with pytest.raises(language_subject.FiveStepLanguageError):
            language_subject._verified_reflow_texts(supplied, [binding])


def test_review_rejects_false_page_and_accepts_only_full_clean_template(tmp_path: Path, language, monkeypatch: pytest.MonkeyPatch) -> None:
    previous = _predecessor(tmp_path); submission = tmp_path / "submission.json"; _write(submission, {})
    root = tmp_path / "successor"; subject.successor_prepare(previous, root, submission)
    options = root / "options.json"; final = root / "final-001"
    option_value = {"schema": "kb_creator.five_step_reader_options.v1", "master_ru": {"path": "MASTER_RU.md", **file_identity(final / "MASTER_RU.md")}, "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(final / "semantic_context" / "RU_PROJECTION.json")}, "source_toc": {}, "body_links": [], "asset_choices": [], "hit_points": {}, "display_roles": []}
    _write(options, sealed("kb_creator.five_step_reader_options.v1", option_value, digest_key="options_sha256"))
    config = tmp_path / "docx.json"; _write(config, {})
    def build(master, output, **kwargs):
        output.mkdir(); (output / "docx").mkdir(); (output / "docx" / "document.docx").write_bytes(b"docx"); (output / "page-1.png").write_bytes(b"png")
        return {"docx_path": output / "docx" / "document.docx", "render_pages": [output / "page-1.png"]}
    monkeypatch.setattr("kb_creator.pipeline.five_step_docx.build_docx_package", build)
    monkeypatch.setattr("kb_creator.pipeline.five_step_docx.verify_docx_package", lambda root: {"state": "verified"})
    _, _, plan, _ = synthetic_guard(final, tmp_path / "fidelity", source_pdf=tmp_path / "source.pdf",
                                    reader_options=options, config=config)
    subject.successor_build(root, options, config, {"docx": {}}, fidelity_plan=plan)
    template = json.loads((root / "visual-task-001" / "submission.template.json").read_text(encoding="utf-8"))
    bad = {**template, "pages": [{"page": 1, "reviewed": False, "findings": []}]}; bad_path = tmp_path / "bad.json"; _write(bad_path, bad)
    with pytest.raises(subject.FiveStepSuccessorError, match="all rendered"):
        subject.successor_review(root, bad_path)
    good = {**template, "pages": [{"page": 1, "reviewed": True, "findings": []}]}; good_path = tmp_path / "good.json"; _write(good_path, good)
    assert subject.successor_review(root, good_path)["state"] == "ready_for_docx_review"
    old = deterministic_inventory(root / "docx-001")
    assert subject.successor_build(root, options, config, {"docx": {}}, fidelity_plan=plan)["active_docx"] == "docx-002"
    assert deterministic_inventory(root / "docx-001") == old
    next_template = json.loads((root / "visual-task-002" / "submission.template.json").read_text())
    next_template["pages"][0]["reviewed"] = True
    _write(good_path, next_template)
    subject.successor_review(root, good_path)
    state = json.loads((root / "state.json").read_text())
    assert {"visual-review-001", "visual-review-002", "visual-task-001", "visual-task-002"} <= set(state["outputs"])
