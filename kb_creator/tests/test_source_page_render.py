import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline.source_page_render import ORIGIN, RECIPE, render_source_pdf_page, replay_source_render_context, validate_source_page_render_row
from kb_creator.pipeline import source_page_render as source_render


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _renderer() -> Path:
    configured = os.environ.get("KB_CREATOR_PDFTOPPM")
    resolved = configured or shutil.which("pdftoppm")
    if not resolved:
        pytest.skip("pdftoppm is unavailable; set KB_CREATOR_PDFTOPPM for this test")
    return Path(resolved)


def _pdf(path: Path) -> None:
    from reportlab.pdfgen.canvas import Canvas
    canvas = Canvas(str(path), pagesize=(72, 144))
    canvas.drawString(10, 120, "glyph-like visual")
    canvas.showPage(); canvas.save()


def _source_pdf_with_glyph_raster(path: Path) -> None:
    """Make the route's reviewed input a full-size source page with a raster visual."""
    from PIL import Image, ImageDraw
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen.canvas import Canvas

    glyph = path.with_name("glyph-raster.png")
    image = Image.new("RGB", (80, 80), "white")
    ImageDraw.Draw(image).line([(8, 70), (40, 8), (72, 70)], fill="black", width=6)
    image.save(glyph)
    canvas = Canvas(str(path), pagesize=(612, 792))
    canvas.drawString(72, 720, "Synthetic reviewed source page")
    canvas.drawImage(ImageReader(str(glyph)), 266, 320, width=80, height=80)
    canvas.showPage(); canvas.save()


def _resume_fixture(tmp_path: Path):
    """Load the sealed one-page replay helper without importing test modules globally."""
    source = Path(__file__).with_name("test_reconstruction_replay_resume.py")
    spec = importlib.util.spec_from_file_location("source_render_resume_fixture", source)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_source_page_render_binds_pdf_page_renderer_and_mediabox(tmp_path):
    renderer = _renderer()
    source, output = tmp_path / "source.pdf", tmp_path / "review.png"
    _pdf(source)
    result = render_source_pdf_page(source, 1, renderer, 300, output, expected_source_sha256=_sha(source), expected_renderer_sha256=_sha(renderer))
    assert result["recipe"] == RECIPE
    assert result["pixels"] == [300, 600]
    assert result["sha256"] == _sha(output)


def test_private_render_scope_reuses_binary_but_not_caller_output_or_facts(tmp_path, monkeypatch):
    renderer = _renderer(); source = tmp_path / "source.pdf"; _pdf(source)
    original_run = source_render.subprocess.run
    launches = []

    def counted(*args, **kwargs):
        launches.append(args[0])
        return original_run(*args, **kwargs)

    monkeypatch.setattr(source_render.subprocess, "run", counted)
    kwargs = {"expected_source_sha256": _sha(source), "expected_renderer_sha256": _sha(renderer)}
    with source_render._reuse_rendered_pages():
        scope_root = source_render._ACTIVE_RENDER_SCOPE.get().root
        first = render_source_pdf_page(source, 1, renderer, 72, tmp_path / "first.png", **kwargs)
        first["pixels"][0] = 0
        (tmp_path / "first.png").write_bytes(b"caller-mutated")
        second = render_source_pdf_page(source, 1, renderer, 72, tmp_path / "second.png", **kwargs)
        assert len(launches) == 1
        assert second["pixels"] == [72, 144]
        assert second["sha256"] == _sha(tmp_path / "second.png")
        assert (tmp_path / "second.png").read_bytes() != (tmp_path / "first.png").read_bytes()
        render_source_pdf_page(source, 1, renderer, 144, tmp_path / "other-dpi.png", **kwargs)
        assert len(launches) == 2
    assert not scope_root.exists()
    assert source_render._ACTIVE_RENDER_SCOPE.get() is None
    render_source_pdf_page(source, 1, renderer, 72, tmp_path / "next-call.png", **kwargs)
    assert len(launches) == 3


@pytest.mark.parametrize("dependency", ["source", "renderer", "missing_renderer"])
def test_private_render_scope_rejects_fresh_dependency_drift(tmp_path, monkeypatch, dependency):
    real_renderer = _renderer(); renderer = real_renderer
    source = tmp_path / "source.pdf"; _pdf(source)
    if dependency != "source":
        # A mutable authority file drives this negative probe; subprocess still
        # launches the real Poppler binary to produce a valid first PNG.
        renderer = tmp_path / "renderer-authority.bin"
        renderer.write_bytes(b"renderer authority")
        real_run = source_render.subprocess.run

        def launch_real(command, **kwargs):
            return real_run([str(real_renderer), *command[1:]], **kwargs)

        monkeypatch.setattr(source_render.subprocess, "run", launch_real)
    kwargs = {"expected_source_sha256": _sha(source), "expected_renderer_sha256": _sha(renderer)}
    with source_render._reuse_rendered_pages():
        render_source_pdf_page(source, 1, renderer, 72, tmp_path / "first.png", **kwargs)
        target = source if dependency == "source" else renderer
        if dependency == "missing_renderer":
            target.unlink()
        else:
            data = bytearray(target.read_bytes()); data[-1] ^= 1; target.write_bytes(data)
        with pytest.raises(ValueError, match="missing|authority mismatch"):
            render_source_pdf_page(source, 1, renderer, 72, tmp_path / "reused.png", **kwargs)
        assert not (tmp_path / "reused.png").exists()


def test_private_render_scope_rejects_corrupt_payload_and_cleans_exception(tmp_path):
    renderer = _renderer(); source = tmp_path / "source.pdf"; _pdf(source)
    kwargs = {"expected_source_sha256": _sha(source), "expected_renderer_sha256": _sha(renderer)}
    with pytest.raises(ValueError, match="private source-page render payload changed"):
        with source_render._reuse_rendered_pages():
            scope = source_render._ACTIVE_RENDER_SCOPE.get(); root = scope.root
            render_source_pdf_page(source, 1, renderer, 72, tmp_path / "first.png", **kwargs)
            next(iter(scope.entries.values())).path.write_bytes(b"tampered private PNG")
            render_source_pdf_page(source, 1, renderer, 72, tmp_path / "reused.png", **kwargs)
    assert not root.exists() and not (tmp_path / "reused.png").exists()


@pytest.mark.parametrize("failure", ["subprocess", "invalid_png", "copy"])
def test_private_render_scope_cleans_failed_production(tmp_path, monkeypatch, failure):
    renderer = _renderer(); source = tmp_path / "source.pdf"; _pdf(source)
    kwargs = {"expected_source_sha256": _sha(source), "expected_renderer_sha256": _sha(renderer)}
    if failure == "subprocess":
        monkeypatch.setattr(source_render.subprocess, "run", lambda *a, **k: type("Result", (), {"returncode": 1})())
    elif failure == "invalid_png":
        def bad_render(command, **_kwargs):
            Path(command[-1] + ".png").write_bytes(b"invalid PNG")
            return type("Result", (), {"returncode": 0})()
        monkeypatch.setattr(source_render.subprocess, "run", bad_render)
    else:
        def partial_copy(_source, target):
            Path(target).write_bytes(b"partial")
            raise OSError("copy failed")
        monkeypatch.setattr(source_render.shutil, "copyfile", partial_copy)
    with pytest.raises((OSError, ValueError)):
        with source_render._reuse_rendered_pages():
            root = source_render._ACTIVE_RENDER_SCOPE.get().root
            render_source_pdf_page(source, 1, renderer, 72, tmp_path / "failed.png", **kwargs)
    assert not root.exists() and not (tmp_path / "failed.png").exists()
    assert list(tmp_path.glob(".source-render-*")) == []


def test_private_render_scope_distinguishes_source_page_renderer_and_recipe(tmp_path, monkeypatch):
    from reportlab.pdfgen.canvas import Canvas
    real_renderer = _renderer(); source = tmp_path / "source.pdf"
    canvas = Canvas(str(source), pagesize=(72, 144))
    for label in ("one", "two"):
        canvas.drawString(10, 120, label); canvas.showPage()
    canvas.save()
    twin = tmp_path / "same-bytes-other-path.pdf"; shutil.copyfile(source, twin)
    shadow = tmp_path / "other-renderer-authority.bin"; shadow.write_bytes(b"other renderer")
    real_run = source_render.subprocess.run
    launches = []

    def counted(command, **kwargs):
        launches.append(command)
        if command[0] == str(shadow):
            command = [str(real_renderer), *command[1:]]
        return real_run(command, **kwargs)

    monkeypatch.setattr(source_render.subprocess, "run", counted)
    real_hash = _sha(real_renderer)
    with source_render._reuse_rendered_pages():
        for index, (pdf, page, binary, digest) in enumerate((
            (source, 1, real_renderer, real_hash),
            (source, 2, real_renderer, real_hash),
            (twin, 1, real_renderer, real_hash),
            (source, 1, shadow, _sha(shadow)),
        )):
            render_source_pdf_page(pdf, page, binary, 72, tmp_path / f"distinct-{index}.png",
                expected_source_sha256=_sha(pdf), expected_renderer_sha256=digest)
        monkeypatch.setattr(source_render, "RECIPE", RECIPE + "-test-variant")
        render_source_pdf_page(source, 1, real_renderer, 72, tmp_path / "other-recipe.png",
            expected_source_sha256=_sha(source), expected_renderer_sha256=real_hash)
        assert len(launches) == 5


def test_private_render_scope_rejects_dependency_change_during_render(tmp_path, monkeypatch):
    renderer = _renderer(); source = tmp_path / "source.pdf"; _pdf(source)
    source_hash, renderer_hash = _sha(source), _sha(renderer)
    real_run = source_render.subprocess.run

    def render_then_drift(*args, **kwargs):
        result = real_run(*args, **kwargs)
        data = bytearray(source.read_bytes()); data[-1] ^= 1; source.write_bytes(data)
        return result

    monkeypatch.setattr(source_render.subprocess, "run", render_then_drift)
    with pytest.raises(ValueError, match="changed during render"):
        with source_render._reuse_rendered_pages():
            root = source_render._ACTIVE_RENDER_SCOPE.get().root
            render_source_pdf_page(source, 1, renderer, 72, tmp_path / "rejected.png",
                expected_source_sha256=source_hash, expected_renderer_sha256=renderer_hash)
    assert not root.exists() and not (tmp_path / "rejected.png").exists()


def test_replay_context_accepts_lowercase_sealed_hashes(tmp_path):
    renderer = _renderer(); source = tmp_path / "source.pdf"; _pdf(source)
    (tmp_path / "run.json").write_text(__import__("json").dumps({"local": {"source_path": str(source), "common_paths": {"pdftoppm": str(renderer)}}, "source": {"sha256": _sha(source).lower()}}), encoding="utf-8")
    context = replay_source_render_context(tmp_path, {"renderer": {"sha256": _sha(renderer).lower()}})
    assert context["source_sha256"] == _sha(source) and context["renderer_sha256"] == _sha(renderer)


@pytest.mark.parametrize("source_hash,renderer_hash", [("0" * 64, None), (None, "0" * 64)])
def test_source_page_render_rejects_stale_authority_before_output(tmp_path, source_hash, renderer_hash):
    renderer = _renderer()
    source, output = tmp_path / "source.pdf", tmp_path / "review.png"
    _pdf(source)
    with pytest.raises(ValueError, match="authority mismatch"):
        render_source_pdf_page(source, 1, renderer, 300, output, expected_source_sha256=source_hash or _sha(source), expected_renderer_sha256=renderer_hash or _sha(renderer))
    assert not output.exists()


def test_source_page_render_row_requires_closed_same_page_placeholder_and_review():
    row = {"origin": ORIGIN, "source_page": 41, "source_sha256": "A" * 64, "logical_name": "manco-glyph.png", "placement": "full_page", "render": {"recipe": RECIPE, "dpi": 300, "renderer_sha256": "B" * 64, "pixels": [2625, 3375], "bytes": 42, "sha256": "C" * 64}, "source_visual_review": {"visual_reviewed": True, "rationale": "Source manuscript is visible."}}
    assert validate_source_page_render_row(row, decision_page=41, expected_source_sha256="A" * 64, expected_renderer_sha256="B" * 64, markdown="![Manco glyph]({{asset:manco-glyph.png}})", page_visual_reviewed=True) == row
    row["source_page"] = 40
    with pytest.raises(ValueError, match="reviewed source page"):
        validate_source_page_render_row(row, decision_page=41, expected_source_sha256="A" * 64, expected_renderer_sha256="B" * 64, markdown="![Manco glyph]({{asset:manco-glyph.png}})", page_visual_reviewed=True)


@pytest.mark.parametrize("markdown", ["{{asset:manco-glyph.png}}", "[glyph]({{asset:manco-glyph.png}})", "![]({{asset:manco-glyph.png}})", "![one]({{asset:manco-glyph.png}})\n![two]({{asset:manco-glyph.png}})"])
def test_source_page_render_row_rejects_nonvisible_or_duplicate_placeholder(markdown):
    row = {"origin": ORIGIN, "source_page": 41, "source_sha256": "A" * 64, "logical_name": "manco-glyph.png", "placement": "full_page", "render": {"recipe": RECIPE, "dpi": 300, "renderer_sha256": "B" * 64, "pixels": [2625, 3375], "bytes": 42, "sha256": "C" * 64}, "source_visual_review": {"visual_reviewed": True, "rationale": "Source manuscript is visible."}}
    with pytest.raises(ValueError, match="Markdown image placeholder"):
        validate_source_page_render_row(row, decision_page=41, expected_source_sha256="a" * 64, expected_renderer_sha256="b" * 64, markdown=markdown, page_visual_reviewed=True)


@pytest.mark.parametrize("page_reviewed", [True, False])
def test_stage05_and_stage06_replay_the_same_closed_source_render(tmp_path, page_reviewed):
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v3_content
    from kb_creator.scripts.materialize_mineru_ai_merge import _validate_decision
    renderer = _renderer()
    source = tmp_path / "source.pdf"; _pdf(source)
    preview = tmp_path / "preview.png"
    facts = render_source_pdf_page(source, 1, renderer, 300, preview, expected_source_sha256=_sha(source), expected_renderer_sha256=_sha(renderer))
    row = {"origin": ORIGIN, "source_page": 1, "source_sha256": _sha(source), "logical_name": "glyph-page.png", "placement": "full_page", "render": {key: facts[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")}, "source_visual_review": {"visual_reviewed": True, "rationale": "Glyph is visible in the source facsimile."}}
    decision = {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "reader", "overlay_preference": "original_pipeline_txt", "selected_blocks": [], "markdown": "![Glyph page]({{asset:glyph-page.png}})", "assets": [row], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed"}}
    views = {name: {"blocks": []} for name in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")}
    decision["review"]["visual_reviewed"] = page_reviewed
    packets = {1: {"source_page": 1, "semantic_role": "reader", "views": views}}
    context = {"source": source, "renderer": renderer, "source_sha256": _sha(source), "renderer_sha256": _sha(renderer)}
    allowlist = {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []}
    audit = audit_v3_content(packets, {1: decision}, allowlist=allowlist, geometry={}, visual_inventory={}, source_render_context=context)
    assert audit["passed"] and audit["pages"][0]["source_page_renders"] == [{"origin": ORIGIN, "logical_name": "glyph-page.png", "source_page": 1, "render": row["render"]}]
    context["proofs"] = {1: audit["pages"][0]["source_page_renders"]}
    blocks, assets, markdown = _validate_decision(decision, packets[1], {"views": {}}, tmp_path, set(), context, tmp_path / "owned-source-render-staging")
    assert blocks == [] and markdown == decision["markdown"] and assets[0]["sha256"] == facts["sha256"]
    assert assets[0]["resolved_source"].is_file()
    assert decision["review"]["visual_reviewed"] is page_reviewed
    row["source_visual_review"]["visual_reviewed"] = False
    with pytest.raises(ValueError, match="closed visual review"):
        audit_v3_content(packets, {1: decision}, allowlist=allowlist, geometry={}, visual_inventory={}, source_render_context=context)
    row["source_visual_review"]["visual_reviewed"] = True
    context["proofs"] = {1: []}
    with pytest.raises(ValueError, match="Stage05 proof"):
        _validate_decision(decision, packets[1], {"views": {}}, tmp_path, set(), context, tmp_path / "owned-source-render-staging")


def test_source_render_late_failure_keeps_raw_input_immutable(monkeypatch, tmp_path):
    """A failed source render may write only to the caller-owned staging root."""
    from kb_creator.scripts import materialize_mineru_ai_merge as materializer
    from kb_creator.scripts.materialize_mineru_ai_merge import _validate_decision

    renderer = _renderer()
    source = tmp_path / "source.pdf"
    _pdf(source)
    raw_root = tmp_path / "raw"
    marker = raw_root / "views" / "original_pipeline_txt" / "book_content_list.json"
    marker.parent.mkdir(parents=True)
    marker.write_text("[]", encoding="utf-8")

    preview = tmp_path / "sealed-preview.png"
    facts = render_source_pdf_page(
        source, 1, renderer, 300, preview,
        expected_source_sha256=_sha(source), expected_renderer_sha256=_sha(renderer),
    )
    row = {
        "origin": ORIGIN,
        "source_page": 1,
        "source_sha256": _sha(source),
        "logical_name": "glyph-page.png",
        "placement": "full_page",
        "render": {key: facts[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")},
        "source_visual_review": {"visual_reviewed": True, "rationale": "reviewed"},
    }
    decision = {
        "schema": "kb_creator.mineru_ai_page_decision.v1",
        "source_page": 1,
        "semantic_role": "reader",
        "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [],
        "markdown": "![Glyph page]({{asset:glyph-page.png}})",
        "assets": [row],
        "unresolved": [],
        "review": {"visual_reviewed": True, "notes": "reviewed"},
    }
    packet = {"source_page": 1, "semantic_role": "reader", "views": {"original_pipeline_txt": {"blocks": []}}}
    context = {
        "source": source,
        "renderer": renderer,
        "source_sha256": _sha(source),
        "renderer_sha256": _sha(renderer),
        "proofs": {1: [{"origin": ORIGIN, "logical_name": "glyph-page.png", "source_page": 1, "render": row["render"]}]},
    }
    before = {path.relative_to(raw_root).as_posix(): path.read_bytes() for path in raw_root.rglob("*") if path.is_file()}
    staging = tmp_path / "owned-source-render-staging"

    def fail_after_render(*args, **kwargs):
        output = Path(args[4])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.with_suffix(".partial").write_bytes(b"partial render")
        raise RuntimeError("synthetic late renderer failure")

    monkeypatch.setattr(materializer, "render_source_pdf_page", fail_after_render)
    with pytest.raises(RuntimeError, match="synthetic late renderer failure"):
        _validate_decision(decision, packet, {"views": {}}, raw_root, set(), context, staging)

    after = {path.relative_to(raw_root).as_posix(): path.read_bytes() for path in raw_root.rglob("*") if path.is_file()}
    assert after == before
    assert not (raw_root / ".source-page-render-staging").exists()
    assert (staging / "page-001-glyph-page.partial").is_file()


@pytest.mark.parametrize(("raw_type", "reader_text", "logical_name"), [
    ("image", "MATCHBOOK COPY", "handout-9.png"),
    ("table", "Quantity Item Weight Price", "p042-ledger.png"),
])
@pytest.mark.parametrize("image_before_text", [False, True])
def test_author_to_stage06_to_promotion_closes_selected_asset_region_text(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, raw_type: str, reader_text: str, logical_name: str, image_before_text: bool):
    """Public Stage05/06 route for p40-image and p42-corrupt-table shaped evidence."""
    from kb_creator.pipeline import reconstruction_promotion as promotion
    from kb_creator.pipeline import reconstruction_replay as replay
    from kb_creator.pipeline import reconstruction_replay_resume as resume
    from kb_creator.pipeline.identity import deterministic_inventory, file_identity
    from kb_creator.pipeline.manifests import sealed
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    fixture = _resume_fixture(tmp_path); authorities, _, _ = fixture._fixture(tmp_path); run = authorities.run_root
    renderer = _renderer(); source_pdf = tmp_path / "asset-proof.pdf"; _pdf(source_pdf)
    run_data = json.loads((run / "run.json").read_text(encoding="utf-8")); run_data["source"]["sha256"] = _sha(source_pdf); run_data["local"] = {"source_path": str(source_pdf), "common_paths": {"pdftoppm": str(renderer)}}; (run / "run.json").write_text(json.dumps(run_data), encoding="utf-8")
    geometry_path = run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"; geometry = json.loads(geometry_path.read_text(encoding="utf-8")); geometry.pop("plan_sha256"); geometry["renderer"] = {"sha256": _sha(renderer)}; geometry = sealed("kb_creator.mineru_geometry_plan.v2", geometry, digest_key="plan_sha256"); geometry_path.write_text(json.dumps(geometry), encoding="utf-8")
    view, source_path = "original_pipeline_txt", "images/handout.png"
    raw_asset = run / "outputs/02-mineru-three-view/views/original_pipeline_txt/artifacts" / source_path
    raw_asset.parent.mkdir(parents=True); raw_asset.write_bytes(b"reviewed selected handout raster")
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"; packet = json.loads(packet_path.read_text(encoding="utf-8"))
    for data in packet["views"].values(): data["blocks"][0].update({"type": raw_type, "bbox": [100, 100, 900, 900], "assets": [source_path], "text": ""})
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    comparison_path = run / "outputs/03-compare-views/comparison.json"; comparison = json.loads(comparison_path.read_text(encoding="utf-8")); comparison.pop("comparison_sha256")
    for data in comparison["views"].values(): data["blocks"][0].update({"type": raw_type, "bbox": [100, 100, 900, 900], "assets": [source_path], "text": ""})
    comparison = sealed("kb_creator.mineru_multi_view_comparison.v3", comparison, digest_key="comparison_sha256"); comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    original = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"; original.parent.mkdir(parents=True); original.write_bytes(b"source page visual")
    asset_visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/assets" / source_path; asset_visual.parent.mkdir(parents=True); asset_visual.write_bytes(raw_asset.read_bytes())
    manifest_path = run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"; manifest = json.loads(manifest_path.read_text(encoding="utf-8")); manifest.pop("manifest_sha256")
    manifest["files"] += [{"path": "visual/original_pipeline_txt/pages/page-001.png", **file_identity(original)}, {"path": "visual/original_pipeline_txt/assets/images/handout.png", **file_identity(asset_visual)}]
    manifest = sealed("kb_creator.mineru_visual_merge_bundle.v3", manifest, digest_key="manifest_sha256"); manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    queue_path = run / "review/review_queue.json"; queue = json.loads(queue_path.read_text(encoding="utf-8")); queue.pop("queue_sha256"); queue["source_sha256"] = _sha(source_pdf); queue["comparison"] = {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}; queue["items"][0]["merge_packet"] = {"path": "merge_packets/pages/page-001.json", **file_identity(packet_path)}; queue = sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256"); queue_path.write_text(json.dumps(queue), encoding="utf-8")
    # Only the sealed synthetic Stage01-04 prefix is injected; public queue, author, audit, materializer and promotion execute unchanged.
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda _root: authorities); monkeypatch.setattr(resume, "validate_replayed_prefix", lambda _root: authorities)
    drafts = tmp_path / "asset-drafts"; drafts.mkdir()
    markdown = "> " + reader_text
    (drafts / "page-001.json").write_text(json.dumps({"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "body", "overlay_preference": view, "selected_blocks": [{"view": view, "raw_index": 0, "purpose": "asset"}], "markdown": markdown, "assets": [{"view": view, "source_path": source_path, "logical_name": logical_name, "placement": "reference_only"}], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed selected visual text"}}), encoding="utf-8")
    spec = tmp_path / "asset-spec.json"; spec.write_text(json.dumps({"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": [{"source_page": 1, "role_contract": {"role": "body", "group_id": "asset-proof"}, "units": [{"id": "handout", "kind": "handout", "representation": "blockquote", "raw_indices": [0], "start": markdown, "end": markdown, "visual_assertion_ids": ["asset-text"]}]}], "visual_text_assertions": [{"assertion_id": "asset-text", "source_page": 1, "text": reader_text, "relation": "within_selected_asset_region", "bbox": [200, 200, 700, 300], "asset": {"view_id": view, "raw_index": 0, "logical_name": logical_name, "source_path": source_path}, "rationale": "bounded reviewer transcription of printed selected asset text"}]}), encoding="utf-8")
    if image_before_text:
        draft_path = drafts / "page-001.json"
        draft = json.loads(draft_path.read_text(encoding="utf-8"))
        draft["markdown"] = f"![Source facsimile]({{{{asset:{logical_name}}}}})\n\n" + markdown
        draft["assets"][0]["placement"] = "inline"
        draft_path.write_text(json.dumps(draft), encoding="utf-8")
    authored = tmp_path / "asset-authored"; author.author_drafts(run, drafts, authored, [spec])
    assert resume.replay_resume_engine(run, authored / "decision_set.json", authored)["state"] == "candidate_ready_for_reconstruction_qa"
    audit = json.loads((run / "outputs/05-fidelity-audit/audit.json").read_text(encoding="utf-8")); assert audit["schema"] == "kb_creator.ai-merge-fidelity-audit/v4" and audit["passed"] is True
    submission = resume.load_replay_submission(authorities); decision_set = json.loads((submission.root / "decision_set.json").read_text(encoding="utf-8"))
    promotion._validate_candidate(run, {"source": {"page_count": 1}, "page_roles": [{"first_page": 1, "last_page": 1, "role": "body"}], "scope": {"required_entities": {"numbered_player_handouts": 0}}}, submission.root, decision_set, run=run_data, fidelity_path=run / "outputs/05-fidelity-audit/audit.json", fidelity=audit, candidate_root=run / "outputs/06-materialize-candidate", replay_bridge_sha256=authorities.bridge_sha256, replay_submission=submission.receipt, stage6_files=deterministic_inventory(run / "outputs/06-materialize-candidate"))


@pytest.mark.parametrize("correct_title", [False, True])
def test_author_to_replay_to_promotion_validates_source_render_and_rejects_stale_proof(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, correct_title: bool
):
    """Exercise authoring, public Stage05/06 replay, and promotion's content validator."""
    from kb_creator.pipeline import reconstruction_promotion as promotion
    from kb_creator.pipeline import reconstruction_replay as replay
    from kb_creator.pipeline import reconstruction_replay_resume as resume
    from kb_creator.pipeline.identity import deterministic_inventory, file_identity
    from kb_creator.pipeline.manifests import sealed
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    renderer = _renderer()
    source = tmp_path / "source-with-glyph.pdf"
    _source_pdf_with_glyph_raster(source)
    fixture = _resume_fixture(tmp_path)
    authorities, _, _ = fixture._fixture(tmp_path)
    run = authorities.run_root

    # Bind the synthetic source and Poppler before resealing the replay authorities.
    run_data = json.loads((run / "run.json").read_text(encoding="utf-8"))
    run_data["source"]["sha256"] = _sha(source)
    run_data["local"] = {
        "source_path": str(source),
        "common_paths": {"pdftoppm": str(renderer)},
    }
    (run / "run.json").write_text(json.dumps(run_data), encoding="utf-8")
    geometry_path = run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geometry.pop("plan_sha256")
    geometry["renderer"] = {"sha256": _sha(renderer)}
    geometry = sealed("kb_creator.mineru_geometry_plan.v2", geometry, digest_key="plan_sha256")
    geometry_path.write_text(json.dumps(geometry), encoding="utf-8")
    original_visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    original_visual.parent.mkdir(parents=True)
    original_visual.write_bytes(b"synthetic original-pipeline visual")
    visual_path = run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"
    visual = json.loads(visual_path.read_text(encoding="utf-8"))
    visual.pop("manifest_sha256")
    visual["files"].append({"path": "visual/original_pipeline_txt/pages/page-001.png", **file_identity(original_visual)})
    visual = sealed("kb_creator.mineru_visual_merge_bundle.v3", visual, digest_key="manifest_sha256")
    visual_path.write_text(json.dumps(visual), encoding="utf-8")
    queue_path = run / "review/review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue.pop("queue_sha256")
    queue["source_sha256"] = _sha(source)
    queue = sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256")
    queue_path.write_text(json.dumps(queue), encoding="utf-8")

    # The fixture supplies a sealed Stage01-04 prefix; real queue/submission validators remain active.
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda _root: authorities)
    monkeypatch.setattr(resume, "validate_replayed_prefix", lambda _root: authorities)
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    reader_heading = "Stable corrected heading" if correct_title else "Stable heading"
    (drafts / "page-001.json").write_text(
        json.dumps(
            {
                "schema": "kb_creator.mineru_ai_page_decision.v1",
                "source_page": 1,
                "semantic_role": "body",
                "overlay_preference": "original_pipeline_txt",
                "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}],
                "markdown": f"# {reader_heading}\n\n![Reviewed glyph page]({{{{asset:glyph-page.png}}}})",
                "assets": [],
                "unresolved": [],
                "review": {"visual_reviewed": True, "notes": "reviewed source glyph"},
            }
        ),
        encoding="utf-8",
    )
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "semantic_structure_profile": "visually_reviewed_semantic_containers_v1",
                "pages": [
                    {
                        "source_page": 1,
                        **({"reviewed_block_corrections": [{
                            "view": "original_pipeline_txt", "raw_index": 0,
                            "before": "Stable heading", "after": reader_heading,
                            "reason": "Synthetic source reviewer confirms the complete heading.",
                        }]} if correct_title else {}),
                        "source_page_render": {
                            "logical_name": "glyph-page.png",
                            "dpi": 300,
                            "visual_reviewed": True,
                            "rationale": "The synthetic source contains the reviewed glyph raster.",
                        },
                        "units": [
                            {
                                "id": "heading",
                                "kind": "heading",
                                "representation": "atx_heading",
                                "raw_indices": [0],
                                "start": "# " + reader_heading,
                                "end": "# " + reader_heading,
                                "heading_level": 1,
                            }
                        ],
                    }
                ],
                "ocr_equivalence_classes": [],
            }
        ),
        encoding="utf-8",
    )
    authored = tmp_path / "authored"
    author.author_drafts(run, drafts, authored, [spec])
    result = resume.replay_resume_engine(run, authored / "decision_set.json", authored)
    assert result["state"] == "candidate_ready_for_reconstruction_qa"

    audit = json.loads((run / "outputs/05-fidelity-audit/audit.json").read_text(encoding="utf-8"))
    candidate = run / "outputs/06-materialize-candidate"
    manifest = json.loads((candidate / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    assert audit["pages"][0]["source_page_renders"][0]["origin"] == ORIGIN
    assert manifest["assets"][0]["origin"] == ORIGIN
    assert "![Reviewed glyph page](assets/" in (candidate / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")

    submission = resume.load_replay_submission(authorities)
    decision_set = json.loads((submission.root / "decision_set.json").read_text(encoding="utf-8"))
    promotion._validate_candidate(
        run,
        {"source": {"page_count": 1}, "page_roles": [{"first_page": 1, "last_page": 1, "role": "body"}], "scope": {"required_entities": {"numbered_player_handouts": 0}}},
        submission.root,
        decision_set,
        run=run_data,
        fidelity_path=run / "outputs/05-fidelity-audit/audit.json",
        fidelity=audit,
        candidate_root=candidate,
        replay_bridge_sha256=authorities.bridge_sha256,
        replay_submission=submission.receipt,
        stage6_files=deterministic_inventory(candidate),
    )
    stale = json.loads(json.dumps(audit))
    stale["pages"][0]["source_page_renders"][0]["render"]["sha256"] = "0" * 64
    with pytest.raises(promotion.ReconstructionPromotionError, match="Stage05 proof"):
        promotion._validate_candidate(
            run,
            {"source": {"page_count": 1}, "page_roles": [{"first_page": 1, "last_page": 1, "role": "body"}], "scope": {"required_entities": {"numbered_player_handouts": 0}}},
            submission.root,
            decision_set,
            run=run_data,
            fidelity_path=run / "outputs/05-fidelity-audit/audit.json",
            fidelity=stale,
            candidate_root=candidate,
            replay_bridge_sha256=authorities.bridge_sha256,
            replay_submission=submission.receipt,
            stage6_files=deterministic_inventory(candidate),
        )
