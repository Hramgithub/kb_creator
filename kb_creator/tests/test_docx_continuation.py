"""Real reconstruction/language/DOCX fixture; only external rendering is simulated."""
import copy
import hashlib
import json
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from kb_creator.pipeline import docx_continuation as subject, language_continuation as language
from kb_creator.pipeline import reader_projection, five_step_docx
from kb_creator.pipeline.identity import deterministic_inventory, file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.tests.test_language_continuation import predecessor, _draft, _read, _write
from kb_creator.tests.fidelity_fixture import synthetic_guard


@pytest.fixture(scope="module")
def book(tmp_path_factory):
    root = tmp_path_factory.mktemp("real-book")
    # The upstream fixture normally emits placeholder image bytes. Supply a
    # real PNG before any artifact is hashed, so the actual DOCX builder runs.
    image_bytes = io.BytesIO()
    Image.new("RGB", (24, 16), "white").save(image_bytes, format="PNG")
    original_write = Path.write_bytes
    original_text = Path.write_text
    def write_fixture_image(path, data):
        if path.name == "handout.png" and data == b"image":
            data = image_bytes.getvalue()
        return original_write(path, data)
    def write_fixture_text(path, data, *args, **kwargs):
        # Give the synthetic book a real heading/TOC before promotion seals it.
        return original_text(path, data.replace("Page 1", "# Заголовок"), *args, **kwargs)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "write_bytes", write_fixture_image)
        patch.setattr(Path, "write_text", write_fixture_text)
        def source_with_visible_handout(path):
            pdf = canvas.Canvas(str(path), pagesize=(500, 700), invariant=1)
            pdf.drawString(40, 650, "page 1")
            pdf.showPage()
            pdf.drawString(40, 650, "page 2")
            pdf.drawImage(ImageReader(io.BytesIO(image_bytes.getvalue())), 40, 500,
                          width=90, height=60)
            pdf.showPage()
            pdf.save()
        patch.setattr("kb_creator.tests.test_language_continuation._source", source_with_visible_handout)
        run, glossary = predecessor.__wrapped__(root)
    prepared = language.prepare_continuation(run, glossary, root / "prepared")
    drafted = language.submit_continuation(root / "prepared", _draft(prepared, root / "draft.json"), root / "drafted")
    proof = _read(Path(drafted["template_path"]))
    for row in proof["units"]:
        row["disposition"] = "checked_unchanged"
    _write(root / "proof.json", proof)
    final = language.submit_continuation(root / "drafted", root / "proof.json", root / "final")
    master = Path(final["final_root"]) / "MASTER_RU.md"
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **file_identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(master.parent / "semantic_context/RU_PROJECTION.json")},
               "source_toc": {"state": "absent", "source_pdf_sha256": final["inputs"]["source_pdf"]["identity"]["sha256"], "reason": "Synthetic one-page mechanics fixture has no source TOC."},
               "body_links": [], "asset_choices": [], "display_roles": [], "hit_points": {"presentation": "numeric", "expected_counts": []}}
    options["options_sha256"] = reader_projection.seal(options)
    folder = root / "decisions"; folder.mkdir(exist_ok=True)
    _write(folder / "reader.json", options)
    return root


def _build(book, output, *, runtime=None):
    language_manifest, master = subject._language(subject._reference(book / "final" / language.MANIFEST))
    source = Path(language_manifest["inputs"]["source_pdf"]["path"])
    guard_root = book / "guards" / hashlib.sha256(str(output).encode()).hexdigest()[:12]
    config, _, plan, _ = synthetic_guard(master.parent, guard_root,
                                         title="Тест", source_pdf=source,
                                         reader_options=book / "decisions/reader.json",
                                         source_graphic_page=2)
    return subject.build_docx_continuation(book / "final", output, title="Тест",
                                           reader_options=book / "decisions/reader.json",
                                           config=config, fidelity_plan=plan, runtime=runtime)


def _render_adapter(docx, output, *args, **kwargs):
    """Coverage contract fixture, never claimed as an actual LibreOffice render."""
    output.mkdir()
    rows = []
    for index in (1, 2):
        path = output / f"page-{index:03d}.png"
        Image.new("RGB", (12, 15), (index * 60, 0, 0)).save(path)
        rows.append({"page": index, "image": {"path": path.name, **file_identity(path)}})
    _write(output / "review_index.json", {"page_count": 2, "pages": rows})
    _write(output / "render_inventory.json", {"page_count": 2, "pages": rows})
    return {"page_count": 2, "export_engine": "injected_test"}


@pytest.fixture
def rendered(book, tmp_path, monkeypatch):
    monkeypatch.setattr(five_step_docx, "render_docx_transient", _render_adapter)
    tools = tmp_path / "tools"; tools.mkdir()
    runtime = {"tools_root": str(tools)}
    for name in ("pdftoppm", "python", "libreoffice"):
        path = tools / name; path.touch(); runtime[name] = str(path)
    root = tmp_path / "envelope"
    _build(book, root, runtime=runtime)
    return root


def _submissions(root, tmp_path):
    text = _read(root / "text-review-task.json")
    text = {"schema": "kb_creator.docx_text_review_submission.v1", "task_sha256": text["task_sha256"], "docx": text["docx"], "reviewer_role": "agent", "blocks": [{"block_id": row["block_id"], "text_sha256": row["text_sha256"], "read": True} for row in text["blocks"]], "findings": []}
    visual = _read(root / "visual-review-task.json")
    visual = {**visual, "schema": "kb_creator.docx_visual_review_submission.v1", "reviewer_role": "agent", "pages": [{**row, "read": True} for row in visual["pages"]], "findings": []}
    folder = tmp_path / "submissions"; folder.mkdir()
    _write(folder / "text.json", text); _write(folder / "visual.json", visual)
    return folder


def test_real_build_without_runtime_preserves_language_and_requires_render(book, tmp_path):
    before = deterministic_inventory(book / "final")
    root = tmp_path / "docx"
    result = _build(book, root)
    assert result["state"] == "pending_render"
    assert (root / "package/docx/document.docx").is_file()
    assert _read(root / "text-review-task.json")["blocks"]
    assert deterministic_inventory(book / "final") == before
    assert subject.verify_docx_continuation(root)["book_acceptance"] == "pending"
    with pytest.raises(ValueError, match="rendered"):
        subject.submit_docx_reviews(root, tmp_path / "no", text_submission=tmp_path / "missing", visual_submission=tmp_path / "missing")
    with pytest.raises(ValueError, match="already exists"):
        _build(book, root)


@pytest.mark.parametrize("overlap", [False, True])
def test_verified_review_draft_predecessor_supports_build_and_remains_protected(
        book, tmp_path, monkeypatch, overlap):
    # Inject only the verified language boundary's alternate lineage shape;
    # exercise the real root guard, package builder, and DOCX verification.
    verified_language, master = subject._language(subject._reference(book / "final" / language.MANIFEST))
    verified_language = copy.deepcopy(verified_language)
    source = tmp_path / "review-master"
    source.mkdir()
    manifest = source / "MANIFEST.json"
    manifest.write_text("{}", encoding="utf-8")
    inputs = verified_language["inputs"]
    inputs.pop("run_state")
    inputs["predecessor_kind"] = "verified_review_draft"
    inputs["review_master"] = subject._reference(manifest)
    # A review-draft lineage must carry explicit zero-issue authority; absence
    # of these records is a broken lineage, not the legacy no-issue route.
    evidence = source / "final-evidence.json"
    _write(evidence, {"source_issues": {"issues": []}})
    master_en = Path(inputs["master_en"]["path"])
    issue_bindings = source / "ISSUE_EN_BINDINGS.v1.json"
    _write(issue_bindings, sealed("kb_creator.issue_en_bindings.v1", {
        "master_en": {"path": "MASTER_EN.md", **file_identity(master_en)},
        "final_evidence": {"path": str(evidence), **file_identity(evidence)}, "bindings": [],
    }, digest_key="bindings_sha256"))
    inputs["issue_en_bindings"] = subject._reference(issue_bindings)
    inputs["final_evidence"] = {"path": str(evidence), **file_identity(evidence)}
    monkeypatch.setattr(subject, "_language", lambda _: (verified_language, master))
    before = deterministic_inventory(source)
    output = source / "derived" if overlap else tmp_path / "docx"
    if overlap:
        with pytest.raises(ValueError, match="overlaps immutable predecessor"):
            _build(book, output)
        assert not output.exists()
    else:
        result = _build(book, output)
        assert result["state"] == "pending_render"
        assert result["inputs"]["review_master"] == subject._reference(manifest)
        assert subject.verify_docx_continuation(output)["book_acceptance"] == "pending"
        assert (output / "package/docx/document.docx").is_file()
    assert deterministic_inventory(source) == before


@pytest.mark.parametrize("missing", ["issue_en_bindings", "final_evidence"])
def test_verified_review_draft_missing_issue_authority_fails_closed(book, tmp_path, monkeypatch, missing):
    verified_language, master = subject._language(subject._reference(book / "final" / language.MANIFEST))
    verified_language = copy.deepcopy(verified_language)
    source = tmp_path / "review-master"; source.mkdir()
    manifest = source / "MANIFEST.json"; manifest.write_text("{}", encoding="utf-8")
    inputs = verified_language["inputs"]
    inputs.pop("run_state")
    inputs["predecessor_kind"] = "verified_review_draft"
    inputs["review_master"] = subject._reference(manifest)
    monkeypatch.setattr(subject, "_language", lambda _: (verified_language, master))
    with pytest.raises(ValueError, match="lacks source issue authority"):
        _build(book, tmp_path / "docx")


@pytest.mark.parametrize("defect", ["duplicate", "partial", "blank", "stale", "foreign_task", "findings", "text_partial", "text_unread"])
def test_reviews_reject_incomplete_stale_or_duplicate_pages(rendered, tmp_path, defect):
    folder = _submissions(rendered, tmp_path)
    text, visual = _read(folder / "text.json"), _read(folder / "visual.json")
    if defect == "duplicate": visual["pages"][1] = copy.deepcopy(visual["pages"][0])
    elif defect == "partial": visual["pages"].pop()
    elif defect == "blank": visual["pages"][0]["read"] = False
    elif defect == "stale": visual["pages"][0]["identity"]["sha256"] = "0" * 64
    elif defect == "foreign_task": visual["task_sha256"] = "0" * 64
    elif defect == "findings": visual["findings"] = ["unresolved clipping"]
    elif defect == "text_partial": text["blocks"].pop()
    else: text["blocks"][0]["read"] = False
    _write(folder / "text.json", text); _write(folder / "visual.json", visual)
    with pytest.raises(ValueError):
        subject.submit_docx_reviews(rendered, tmp_path / "rejected", text_submission=folder / "text.json", visual_submission=folder / "visual.json")
    assert not (tmp_path / "rejected").exists()


def test_complete_explicit_reviews_require_independent_release(rendered, tmp_path):
    folder = _submissions(rendered, tmp_path)
    before = deterministic_inventory(rendered)
    result = subject.submit_docx_reviews(rendered, tmp_path / "review", text_submission=folder / "text.json", visual_submission=folder / "visual.json")
    assert result["state"] == "ready_for_independent_release"
    assert result["book_acceptance"] == "pending"
    assert subject.verify_docx_review(tmp_path / "review") == result
    assert deterministic_inventory(rendered) == before
    (rendered / "package/render/page-002.png").write_bytes(b"changed")
    with pytest.raises(ValueError, match="inventory"):
        subject.verify_docx_review(tmp_path / "review")


@pytest.mark.parametrize("defect", ["code", "language_reference", "task", "docx"])
def test_verifier_binds_predecessor_code_and_actual_artifacts(book, tmp_path, monkeypatch, defect):
    root = tmp_path / "envelope"; _build(book, root)
    if defect == "code": monkeypatch.setattr(subject, "_codes", lambda: [])
    elif defect == "language_reference":
        value = _read(root / subject.MANIFEST)
        value["language"]["identity"]["sha256"] = "0" * 64
        value.pop("continuation_sha256")
        _write(root / subject.MANIFEST, sealed(subject.SCHEMA, value, digest_key="continuation_sha256"))
    else:
        (root / ("text-review-task.json" if defect == "task" else "package/docx/document.docx")).write_bytes(b"changed")
    with pytest.raises(ValueError): subject.verify_docx_continuation(root)


def test_cli_help_without_test_pythonpath():
    env = dict(os.environ); env.pop("PYTHONPATH", None)
    result = subprocess.run([sys.executable, "-B", "-m", "kb_creator.scripts.continue_docx", "--help"], env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
