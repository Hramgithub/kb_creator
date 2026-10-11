"""Orchestration tests; adapters are explicit doubles, not live MinerU evidence."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document
from reportlab.pdfgen import canvas

from kb_creator.pipeline import five_step as flow
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.reader_projection import seal
from kb_creator.__main__ import _parser
from kb_creator.pipeline.five_step_docx import _default_config
from kb_creator.tests.fidelity_fixture import synthetic_guard, synthetic_source_review


def test_v1_run_status_is_authenticated_read_only_and_never_current_ready(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    glossary = tmp_path / "glossary.json"
    source.write_bytes(b"%PDF-1.4\n")
    glossary.write_text("{}", encoding="utf-8")
    run = tmp_path / "legacy"
    run.mkdir()
    original = sealed(flow.LEGACY_SCHEMA, {
        "profile": "five_step_docx_v1", "state": "ready_for_docx_review", "phase": "complete",
        "source": {"path": str(source), "identity": file_identity(source)},
        "glossary": {"path": str(glossary), "identity": file_identity(glossary)},
        "evidence": [],
    }, digest_key="state_sha256")
    state_path = run / "state.json"
    state_path.write_text(json.dumps(original), encoding="utf-8")
    before = state_path.read_bytes()
    viewed = flow.status(run)
    assert viewed["state"] == "legacy_read_only"
    assert viewed["historical_state"] == "ready_for_docx_review"
    assert viewed["source_completeness"] == "not_assessed"
    assert viewed["mutation"] == "retired"
    assert state_path.read_bytes() == before
    with pytest.raises(flow.FiveStepError, match="unsupported run state"):
        flow.resume(run)
    with pytest.raises(flow.FiveStepError, match="unsupported run state"):
        flow.rebuild_docx(run, config=tmp_path / "unused.json")
    assert state_path.read_bytes() == before
    tampered = dict(original, profile="other")
    state_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="state_sha256 mismatch"):
        flow.status(run)
    unknown = sealed("kb_creator.five_step_run.v99", {key: value for key, value in original.items() if key not in {"schema", "state_sha256"}}, digest_key="state_sha256")
    state_path.write_text(json.dumps(unknown), encoding="utf-8")
    with pytest.raises(flow.FiveStepError, match="unsupported run state"):
        flow.status(run)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def adapters(monkeypatch):
    calls = []

    def task(root, name):
        root.mkdir()
        write(root / "task.json", {"kind": name})
        write(root / "template.json", {"kind": name})
        return {"task_path": root / "task.json", "template_path": root / "template.json"}

    def prepare(source, output, **kwargs):
        calls.append("intake")
        return task(output, "intake")

    def intake(root, submission, output):
        calls.append("contract")
        output.mkdir()
        write(output / "contract.json", {"scenario": {"id": "fixture"}})
        return {"contract_path": output / "contract.json"}

    def reconstruct(contract, source, output, name, runtime, **kwargs):
        calls.append(("replay", kwargs["replay_from"]) if kwargs else "reconstruction")
        return task(output, "reconstruction")

    def finish(root, submission, decisions):
        calls.append("finish")
        write(root / "review.json", {})
        return {"reconstruction_root": root, "review_path": root / "review.json"}

    def en(root, review, output):
        calls.append("en")
        output.mkdir()
        (output / "MASTER_EN.md").write_text("# Source\n", encoding="utf-8")
        return {"master_en": output / "MASTER_EN.md"}

    def language(master, glossary, output):
        calls.append("language")
        return task(output, "draft")

    def draft(root, submission, output):
        calls.append("draft")
        return task(output, "proofread")

    def final(root, draft, submission, output):
        calls.append("final")
        output.mkdir()
        (output / "MASTER_RU.md").write_text("# Источник\n", encoding="utf-8")
        write(output / "semantic_context" / "RU_PROJECTION.json", {"units": []})
        return {"master_ru": output / "MASTER_RU.md"}

    def docx(master, output, **kwargs):
        calls.append("docx")
        output.mkdir()
        document = Document()
        document.add_paragraph("Проверяемый текст")
        document.save(output / "result.docx")
        (output / "page-1.png").write_bytes(b"test-image")
        return {"docx_path": str(output / "result.docx"), "render_pages": [str(output / "page-1.png")]}

    modules = {"intake": SimpleNamespace(prepare_intake=prepare, submit_intake=intake, start_reconstruction=reconstruct, finish_reconstruction=finish, build_master_en=en),
               "language": SimpleNamespace(prepare_language=language, submit_draft=draft, submit_proofread=final, verify_language_result=lambda _: {"state": "verified"}),
               "docx": SimpleNamespace(build_docx_package=docx, verify_docx_package=lambda _: {"state": "verified"})}
    monkeypatch.setattr(flow, "_module", modules.__getitem__)
    monkeypatch.setattr(flow, "_runtime", lambda _: None)
    monkeypatch.setattr(flow, "_codes", lambda step: [{"step": step, "version": 1}])
    return calls


def _source_pdf(path):
    pdf = canvas.Canvas(str(path), pagesize=(400, 600), invariant=1)
    pdf.drawString(20, 560, "Synthetic text-only source")
    pdf.showPage()
    pdf.save()


def start(tmp_path, *, docx_config=None):
    source = tmp_path / "source.pdf"
    _source_pdf(source)
    glossary = tmp_path / "glossary.json"
    write(glossary, {"terms": []})
    inventory, review = synthetic_source_review(source, tmp_path / "source-guard")
    if docx_config is None:
        docx_config = tmp_path / "docx-config.json"
        write(docx_config, _default_config("Synthetic"))
    return flow.start(source, glossary, tmp_path / "run", docx_config=docx_config,
                      source_inventory=inventory, source_review=review)


def fidelity_plan(tmp_path, root, *, config=None, options=None, suffix="first"):
    state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    master = Path(state["paths"]["master_ru"])
    config = config or Path(state["docx_config"])
    options = options or reader_options(tmp_path, root)
    _, _, plan_path, _ = synthetic_guard(master.parent, tmp_path / f"fidelity-{suffix}",
                                         title="Synthetic", source_pdf=tmp_path / "source.pdf",
                                         config=config, reader_options=options)
    value = json.loads(plan_path.read_text(encoding="utf-8"))
    value["inventory"] = {"path": state["source_inventory"]["path"],
                          **state["source_inventory"]["identity"]}
    value["review"] = {"path": state["source_review"]["path"],
                       **state["source_review"]["identity"]}
    plan = sealed(value["schema"], {key: row for key, row in value.items()
                                     if key not in {"schema", "plan_sha256"}},
                  digest_key="plan_sha256")
    write(plan_path, plan)
    return plan_path


def reader_options(tmp_path, root, *, master_identity=None, source_sha256=None):
    final = Path(json.loads((root / "state.json").read_text(encoding="utf-8"))["paths"]["final"])
    master = final / "MASTER_RU.md"
    projection = final / "semantic_context" / "RU_PROJECTION.json"
    value = {
        "schema": "kb_creator.five_step_reader_options.v1",
        "master_ru": master_identity or {"path": "MASTER_RU.md", **file_identity(master)},
        "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(projection)},
        "source_toc": {"state": "absent", "source_pdf_sha256": source_sha256 or file_identity(tmp_path / "source.pdf")["sha256"], "reason": "Source reviewed"},
        "body_links": [], "asset_choices": [], "hit_points": {}, "display_roles": [],
    }
    path = tmp_path / "reader-options.json"
    write(path, {**value, "options_sha256": seal(value)})
    return path


def to_reader_options(tmp_path, *, docx_config=None):
    result = start(tmp_path, docx_config=docx_config)
    root = tmp_path / "run"
    for expected in ["reconstruction", "documentary_draft", "proofread_final", "reader_options"]:
        submission = tmp_path / "submission.json"
        write(submission, {})
        result = flow.resume(root, submission=submission, decisions_root=tmp_path)
        assert result["phase"] == expected, result
        assert result["state"] == "needs_agent_work", result
    return root, result


def to_visual(tmp_path):
    root, result = to_reader_options(tmp_path)
    assert not (root / "docx-001").exists()
    options = reader_options(tmp_path, root)
    result = flow.resume(root, reader_options=options,
                         fidelity_plan=fidelity_plan(tmp_path, root, options=options))
    assert result["phase"] == "docx_text_review", result
    result = flow.resume(root, submission=text_review_submission(result))
    assert result["phase"] == "docx_visual", result
    return root, result


def text_review_submission(result):
    task = json.loads(Path(result["task_path"]).read_text(encoding="utf-8"))
    return_path = Path(result["run_root"]) / "text-review-submission.json"
    write(return_path, {
        "schema": "kb_creator.docx_text_review_submission.v1", "task_sha256": task["task_sha256"],
        "docx": task["docx"], "reviewer_role": "agent",
        "blocks": [{"block_id": row["block_id"], "text_sha256": row["text_sha256"], "read": True} for row in task["blocks"]],
        "findings": [],
    })
    return return_path


def test_status_and_empty_resume_do_not_run_agent_work(tmp_path, adapters):
    result = start(tmp_path)
    root = tmp_path / "run"
    before = (root / "state.json").read_bytes()
    assert result["step"] == 1
    assert len(result["steps"]) == 5
    assert flow.status(root) == result
    assert flow.resume(root) == result
    assert (root / "state.json").read_bytes() == before
    assert adapters == ["intake"]


def test_resume_cli_accepts_reader_options():
    args = _parser().parse_args(["translate", "resume", "--run-root", "run", "--reader-options", "options.json"])
    assert args.reader_options == Path("options.json")


def test_explicit_successor_routes_verified_extraction_reuse(tmp_path, adapters):
    source, glossary, previous = tmp_path / "source.pdf", tmp_path / "terms.json", tmp_path / "previous"
    _source_pdf(source)
    inventory, review = synthetic_source_review(source, tmp_path / "source-guard")
    write(glossary, {"terms": []})
    previous.mkdir()
    root = tmp_path / "successor"
    flow.start(source, glossary, root, replay_from=previous,
               source_inventory=inventory, source_review=review)
    submission = tmp_path / "submission.json"
    write(submission, {})
    result = flow.resume(root, submission=submission)
    assert result["phase"] == "reconstruction"
    assert adapters[-1] == ("replay", previous.resolve())
    assert previous.is_dir()


def test_corruption_and_source_change_block_reuse(tmp_path, adapters):
    start(tmp_path)
    root = tmp_path / "run"
    (root / "intake-001/task.json").write_text("changed", encoding="utf-8")
    with pytest.raises(flow.FiveStepError, match="changed evidence"):
        flow.resume(root)
    (tmp_path / "source.pdf").write_bytes(b"changed")
    with pytest.raises(flow.FiveStepError, match="source changed"):
        flow.status(root)


def test_all_five_steps_require_explicit_final_visual_review(tmp_path, adapters):
    root, result = to_visual(tmp_path)
    value = json.loads(Path(result["template_path"]).read_text(encoding="utf-8"))
    submission = tmp_path / "visual.json"
    write(submission, value)
    assert flow.resume(root, submission=submission)["state"] == "failed"
    value["pages"][0]["reviewed"] = True
    write(submission, value)
    final = flow.resume(root, submission=submission)
    assert final["state"] == "ready_for_docx_review"
    assert all(row["state"] == "complete" for row in final["steps"])


def test_first_docx_waits_for_source_bound_reader_options(tmp_path, adapters):
    root, waiting = to_reader_options(tmp_path)
    assert "docx" not in adapters
    assert Path(waiting["task_path"]).is_file()
    template = json.loads(Path(waiting["template_path"]).read_text(encoding="utf-8"))
    assert template["source_toc"]["state"] == "unresolved"
    assert template["source_toc"]["source_pdf_sha256"] == file_identity(tmp_path / "source.pdf")["sha256"]
    options = reader_options(tmp_path, root)
    result = flow.resume(root, reader_options=options,
                         fidelity_plan=fidelity_plan(tmp_path, root, options=options))
    assert result["phase"] == "docx_text_review"
    assert adapters[-1] == "docx"
    state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    assert state["reader_options"]["identity"] == file_identity(tmp_path / "reader-options.json")


def test_first_docx_passes_bound_reader_options_and_config(tmp_path, adapters):
    config = tmp_path / "style.json"
    write(config, {"typography": {}})
    root, _ = to_reader_options(tmp_path, docx_config=config)
    docx_module = flow._module("docx")
    original = docx_module.build_docx_package
    received = {}

    def build(*args, **kwargs):
        received.update(kwargs)
        return original(*args, **kwargs)

    docx_module.build_docx_package = build
    options = reader_options(tmp_path, root)
    flow.resume(root, reader_options=options,
                fidelity_plan=fidelity_plan(tmp_path, root, options=options))
    assert received["config"] == config.resolve()
    assert received["reader_options"] == (tmp_path / "reader-options.json").resolve()


def test_reader_options_rejects_foreign_guard_config_before_state_write(tmp_path, adapters):
    root, _ = to_reader_options(tmp_path)
    options = reader_options(tmp_path, root)
    foreign = tmp_path / "foreign-style.json"
    write(foreign, {"foreign": True})
    plan = fidelity_plan(tmp_path, root, config=foreign, options=options, suffix="foreign")
    before = (root / "state.json").read_bytes()
    with pytest.raises(flow.FiveStepError, match="config differs"):
        flow.resume(root, reader_options=options, fidelity_plan=plan)
    assert (root / "state.json").read_bytes() == before
    assert not (root / "docx-001").exists()


def test_docx_text_review_requires_full_coverage_before_visual_task(tmp_path, adapters):
    root, _ = to_reader_options(tmp_path)
    options = reader_options(tmp_path, root)
    waiting = flow.resume(root, reader_options=options,
                          fidelity_plan=fidelity_plan(tmp_path, root, options=options))
    template = json.loads(Path(waiting["template_path"]).read_text(encoding="utf-8"))
    invalid = tmp_path / "incomplete-text-review.json"
    write(invalid, template)
    rejected = flow.resume(root, submission=invalid)
    assert rejected["state"] == "failed"
    assert rejected["phase"] == "docx_text_review"
    assert not (root / "visual-task-001").exists()


@pytest.mark.parametrize("kind", ["master", "source"])
def test_first_docx_rejects_stale_reader_options_before_output(tmp_path, adapters, kind):
    root, _ = to_reader_options(tmp_path)
    kwargs = {"master_identity": {"path": "MASTER_RU.md", "bytes": 0, "sha256": "0" * 64}} if kind == "master" else {"source_sha256": "0" * 64}
    options = reader_options(tmp_path, root, **kwargs)
    result = flow.resume(root, reader_options=options,
                         fidelity_plan=fidelity_plan(tmp_path, root, options=options))
    assert result["state"] == "failed"
    assert result["phase"] == "reader_options"
    assert not (root / "docx-001").exists()
    assert "docx" not in adapters


def test_missing_reader_options_flag_cannot_bypass_guarded_docx_route(tmp_path, adapters):
    start(tmp_path)
    root = tmp_path / "run"
    for expected in ["reconstruction", "documentary_draft", "proofread_final"]:
        submission = tmp_path / f"legacy-{expected}.json"
        write(submission, {})
        assert flow.resume(root, submission=submission, decisions_root=tmp_path)["phase"] == expected
    state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    state.pop("require_reader_options")
    flow._save(root, state)
    submission = tmp_path / "legacy-proofread.json"
    write(submission, {})
    result = flow.resume(root, submission=submission)
    assert result["state"] == "failed"
    assert "docx" not in adapters
    assert not (root / "docx-001").exists()


def test_style_rebuild_reuses_language_and_preserves_predecessor(tmp_path, adapters):
    root, result = to_visual(tmp_path)
    old_docx = Path(result["docx_path"])
    before = adapters[:]
    config = tmp_path / "style.json"
    write(config, {"font": "fixture"})
    rebuilt = flow.rebuild_docx(root, config=config,
                                fidelity_plan=fidelity_plan(tmp_path, root, config=config,
                                                            suffix="rebuild"))
    assert rebuilt["state"] == "needs_agent_work"
    assert adapters == before + ["docx"]
    assert old_docx.is_file()
    assert rebuilt["docx_path"] != str(old_docx)
    assert flow.status(root)["phase"] == "docx_text_review"


def test_step_five_code_change_requires_rebuild_not_retranslation(tmp_path, adapters, monkeypatch):
    root, _ = to_visual(tmp_path)
    monkeypatch.setattr(flow, "_codes", lambda step: [{"step": step, "version": 2 if step == 5 else 1}])
    with pytest.raises(flow.FiveStepError, match="step 5 implementation"):
        flow.status(root)
    config = tmp_path / "style.json"
    write(config, {})
    before = adapters[:]
    assert flow.rebuild_docx(root, config=config,
                             fidelity_plan=fidelity_plan(tmp_path, root, config=config,
                                                         suffix="rebuild"))["phase"] == "docx_text_review"
    assert adapters == before + ["docx"]


def test_language_steps_bind_shared_context_and_numeric_helpers():
    for step in (3, 4):
        paths = {row["path"] for row in flow._codes(step)}
        assert "kb_creator/pipeline/language_context.py" in paths
        assert "kb_creator/pipeline/language_numeric.py" in paths


def test_step_five_binds_reader_projection_implementation():
    paths = {row["path"] for row in flow._codes(5)}
    assert "kb_creator/pipeline/reader_projection.py" in paths
    assert "kb_creator/pipeline/docx_text_review.py" in paths
