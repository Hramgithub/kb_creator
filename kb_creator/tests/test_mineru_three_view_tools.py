import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.scripts.compare_mineru_three_views import compare_views, diff_blocks, normalize_content
from kb_creator.scripts.prepare_mineru_three_view_inputs import prepare_inputs


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _make_source(path: Path) -> None:
    from reportlab.pdfgen import canvas

    doc = canvas.Canvas(str(path), pagesize=(612, 792))
    for index in range(3):
        doc.drawString(72, 720, f"Source page {index + 1}")
        doc.showPage()
    doc.save()


def test_preparer_rejects_wrong_source_hash_before_writing(tmp_path):
    source = tmp_path / "source.pdf"
    _make_source(source)
    with pytest.raises(ValueError, match="SHA-256"):
        prepare_inputs(source, tmp_path / "inputs", "A" * 64, "1,3", 200, "sample")
    assert not (tmp_path / "inputs").exists()


def test_preparer_writes_mapped_vector_and_image_only_raster_manifest(tmp_path):
    from pypdf import PdfReader

    source = tmp_path / "source.pdf"
    _make_source(source)
    inputs = tmp_path / "inputs"
    manifest = prepare_inputs(source, inputs, _sha(source), "3,1", 200, "sample")
    assert manifest["ordered_pages"] == [{"sample_page": 1, "source_page": 3}, {"sample_page": 2, "source_page": 1}]
    assert json.loads((inputs / "sample_pages.json").read_text(encoding="utf-8"))["outputs"] == manifest["outputs"]
    vector = PdfReader(str(inputs / "sample_vector.pdf"))
    raster = PdfReader(str(inputs / "sample_raster.pdf"))
    assert len(vector.pages) == len(raster.pages) == 2
    assert "Source page 3" in vector.pages[0].extract_text()
    assert raster.pages[0].extract_text().strip() == ""
    assert len(raster.pages[0].images) == 1


def test_preparer_requires_exact_resume_identity(tmp_path):
    source = tmp_path / "source.pdf"
    _make_source(source)
    inputs = tmp_path / "inputs"
    prepare_inputs(source, inputs, _sha(source), "1", 200, "sample")
    with pytest.raises(FileExistsError):
        prepare_inputs(source, inputs, _sha(source), "1", 200, "sample")
    assert prepare_inputs(source, inputs, _sha(source), "1", 200, "sample", resume=True)["ordered_pages"][0]["source_page"] == 1


def test_preparer_is_byte_deterministic_for_identical_source_and_options(tmp_path):
    source = tmp_path / "source.pdf"
    _make_source(source)
    first, second = tmp_path / "first", tmp_path / "second"
    prepare_inputs(source, first, _sha(source), "3,1", 200, "sample")
    prepare_inputs(source, second, _sha(source), "3,1", 200, "sample")
    for name in ("sample_vector.pdf", "sample_raster.pdf", "sample_pages.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_raster_only_full_mapping_is_text_free_deterministic_and_safe_to_resume(tmp_path):
    from pypdf import PdfReader

    source = tmp_path / "source.pdf"
    _make_source(source)
    first, second = tmp_path / "first", tmp_path / "second"
    first_manifest = prepare_inputs(source, first, _sha(source), "1-3", 200, "full", raster_only=True)
    prepare_inputs(source, second, _sha(source), "1-3", 200, "full", raster_only=True)
    assert first_manifest["mode"] == "raster_only"
    assert first_manifest["ordered_pages"] == [{"sample_page": 1, "source_page": 1}, {"sample_page": 2, "source_page": 2}, {"sample_page": 3, "source_page": 3}]
    assert set(first_manifest["outputs"]) == {"raster_pdf"}
    assert not (first / "full_vector.pdf").exists()
    raster = PdfReader(str(first / "full_raster.pdf"))
    assert len(raster.pages) == 3
    assert all(page.extract_text().strip() == "" for page in raster.pages)
    for name in ("full_raster.pdf", "sample_pages.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    with pytest.raises(FileExistsError):
        prepare_inputs(source, first, _sha(source), "1-3", 200, "full", raster_only=True)
    resumed = prepare_inputs(source, first, _sha(source), "1-3", 200, "full", raster_only=True, resume=True)
    assert resumed["outputs"] == first_manifest["outputs"]
    with pytest.raises(ValueError, match="selected preparation mode"):
        prepare_inputs(source, first, _sha(source), "1-3", 200, "full", resume=True)


def test_preparer_uses_full_non_letter_mediabox_not_asymmetric_cropbox(tmp_path):
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject

    source = tmp_path / "source.pdf"
    from reportlab.pdfgen import canvas

    document = canvas.Canvas(str(source), pagesize=(595, 841), invariant=1)
    document.drawString(40, 810, "Header outside crop")
    document.showPage()
    document.save()
    reader = PdfReader(source)
    reader.pages[0].cropbox = RectangleObject([0, 0, 595, 770])
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    with source.open("wb") as stream:
        writer.write(stream)

    output = tmp_path / "output"
    manifest = prepare_inputs(
        source,
        output,
        _sha(source),
        "1",
        72,
        "source",
        raster_only=True,
    )
    geometry = manifest["render"]["page_geometry"][0]
    assert manifest["render"]["source_box"] == "MediaBox"
    assert geometry["media_box_coordinates"] == [0.0, 0.0, 595.0, 841.0]
    assert geometry["crop_box_coordinates"] == [0.0, 0.0, 595.0, 770.0]
    assert geometry["raster_pixel_dimensions"] == [595, 841]
    raster = PdfReader(output / "source_raster.pdf")
    assert [float(raster.pages[0].mediabox.width), float(raster.pages[0].mediabox.height)] == [595.0, 841.0]
    assert raster.pages[0].extract_text().strip() == ""


def test_preparer_applies_rotation_once_and_zeroes_raster_rotation(tmp_path):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas

    original = tmp_path / "original.pdf"
    document = canvas.Canvas(str(original), pagesize=(300, 500), invariant=1)
    document.drawString(30, 450, "Rotated")
    document.showPage()
    document.save()
    source = tmp_path / "rotated.pdf"
    reader = PdfReader(original)
    reader.pages[0].rotate(90)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    with source.open("wb") as stream:
        writer.write(stream)

    output = tmp_path / "output"
    manifest = prepare_inputs(
        source,
        output,
        _sha(source),
        "1",
        72,
        "source",
        raster_only=True,
    )
    geometry = manifest["render"]["page_geometry"][0]
    assert geometry["displayed_page_size_points"] == [500.0, 300.0]
    assert geometry["raster_pixel_dimensions"] == [500, 300]
    raster_page = PdfReader(output / "source_raster.pdf").pages[0]
    assert int(raster_page.get("/Rotate", 0)) == 0
    assert [float(raster_page.mediabox.width), float(raster_page.mediabox.height)] == [500.0, 300.0]


def test_preparer_rejects_mixed_geometry_before_output(tmp_path):
    from reportlab.pdfgen import canvas

    source = tmp_path / "mixed.pdf"
    document = canvas.Canvas(str(source), pagesize=(500, 700), invariant=1)
    document.drawString(30, 650, "First")
    document.showPage()
    document.setPageSize((600, 700))
    document.drawString(30, 650, "Second")
    document.showPage()
    document.save()
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="uniform MediaBox"):
        prepare_inputs(
            source,
            output,
            _sha(source),
            "1-2",
            72,
            "source",
            raster_only=True,
        )
    assert not output.exists()


def test_normalization_maps_mineru_page_indices_and_assets():
    blocks = normalize_content([
        {"type": "text", "page_idx": 0, "text": "alpha", "bbox": [0, 0, 10, 10]},
        {"type": "image", "page_idx": 1, "content": "image description", "img_path": "images/x.jpg", "bbox": [1, 1, 9, 9]},
    ], {1: 5, 2: 12})
    assert [(block["source_page"], block["type"], block["assets"]) for block in blocks] == [(5, "text", []), (12, "image", ["images/x.jpg"])]


def test_comparator_preserves_title_signals_and_reports_semantic_conflict():
    title = normalize_content([{"type":"text","page_idx":0,"text":"Heading","bbox":[0,0,10,10],"is_title":True}], {1: 1})
    text = normalize_content([{"type":"text","page_idx":0,"text":"Heading","bbox":[0,0,10,10]}], {1: 1})
    result = diff_blocks(title, text)
    assert title[0]["semantic_evidence"]["model_title"] is True
    assert result["semantic_conflicts"] == [{"kind":"title_to_text_downgrade","left_raw_index":0,"right_raw_index":0,"bbox_iou":1.0,"resolution":None}]


def _write_view(root: Path, rows, *, v2=None, middle=None, markdown="# sample\n", layout=True):
    root.mkdir(parents=True)
    stem = "sample"
    (root / f"{stem}_content_list.json").write_text(json.dumps(rows), encoding="utf-8")
    (root / f"{stem}_content_list_v2.json").write_text(json.dumps([] if v2 is None else v2), encoding="utf-8")
    (root / f"{stem}_middle.json").write_text(json.dumps({} if middle is None else middle), encoding="utf-8")
    (root / f"{stem}.md").write_text(markdown, encoding="utf-8")
    if layout:
        (root / f"{stem}_layout.pdf").write_bytes(b"%PDF-1.4\n")


def test_comparator_reports_differences_and_never_discards_blocks(tmp_path):
    manifest = tmp_path / "sample_pages.json"
    manifest.write_text(json.dumps({"ordered_pages": [{"sample_page": 1, "source_page": 5}]}), encoding="utf-8")
    shared = [{"type": "text", "page_idx": 0, "text": "same", "bbox": [0, 0, 10, 10]}]
    changed = shared + [{"type": "image", "page_idx": 0, "img_path": "images/new.jpg", "bbox": [20, 20, 30, 30]}]
    roots = {name: tmp_path / name for name in ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")}
    _write_view(roots["original_hybrid"], shared)
    _write_view(roots["original_pipeline_ocr"], changed)
    _write_view(roots["raster_hybrid"], shared)
    (roots["original_pipeline_ocr"] / "images").mkdir()
    (roots["original_pipeline_ocr"] / "images" / "new.jpg").write_bytes(b"asset")
    result = compare_views(manifest, roots, tmp_path / "comparison")
    diff = result["pairwise"]["original_hybrid__vs__original_pipeline_ocr"]
    assert result["status"] == "pass"
    assert len(diff["right_unmatched"]) == 1
    assert diff["right_unmatched"][0]["assets"] == ["images/new.jpg"]
    assert (tmp_path / "comparison" / "comparison.md").is_file()


def test_comparator_ingests_unambiguous_v2_middle_and_markdown_title_evidence(tmp_path):
    manifest = tmp_path / "sample_pages.json"
    manifest.write_text(json.dumps({"ordered_pages": [{"sample_page": 1, "source_page": 25}]}), encoding="utf-8")
    title = {"type": "text", "page_idx": 0, "text": "Santina Maria Salvatore", "text_level": 2, "bbox": [0, 0, 10, 10]}
    v2 = [[{"type": "title", "content": {"title_content": [{"type": "text", "content": "Santina Maria Salvatore"}], "level": 2}, "bbox": [0, 0, 10, 10]}]]
    middle = {"pdf_info": [{"para_blocks": [{"type": "title", "lines": [{"spans": [{"type": "text", "content": "Santina Maria Salvatore"}]}], "bbox": [0, 0, 10, 10]}]}]}
    roots = {name: tmp_path / name for name in ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")}
    for root in roots.values():
        _write_view(root, [title], v2=v2, middle=middle, markdown="## Santina Maria Salvatore\n")
    result = compare_views(manifest, roots, tmp_path / "comparison")
    evidence = result["views"]["original_hybrid"]["blocks"][0]["semantic_evidence"]
    assert evidence == {"text_level": 2, "v2_title": True, "middle_title": True, "markdown_heading": True, "model_title": False}


def test_normalize_preserves_closed_v2_table_caption_and_cells_without_metadata_leakage():
    rows = [{"type": "table", "page_idx": 0, "bbox": [0, 0, 10, 10], "img_path": "images/table.png"}]
    v2 = [[{"type": "table", "bbox": [0, 0, 10, 10], "content": {"table_caption": "WEBB", "html": "<table><tr><th>STR</th><td>60 &amp; 1</td></tr></table>", "image_source": "images/secret.png", "table_type": "simple_table", "table_nest_level": 7}}]]
    block = normalize_content(rows, {1: 1}, v2=v2)[0]
    assert block["text"] == "WEBB STR 60 & 1"
    assert "images" not in block["text"] and "simple_table" not in block["text"] and "<td" not in block["text"]
    assert block["semantic_evidence"]["v2_table_text"] is True


def test_diff_blocks_uses_raw_index_identity_and_keeps_image_overlap_page_local():
    left = normalize_content([
        {"type": "text", "page_idx": 0, "text": "Hospital, Cellar", "text_level": 2, "bbox": [0, 0, 10, 10]},
        {"type": "image", "page_idx": 1, "img_path": "images/p26.jpg", "bbox": [0, 0, 10, 10]},
    ], {1: 39, 2: 40})
    right = normalize_content([{"type": "text", "page_idx": 0, "text": "Hospital, Cellar", "bbox": [0, 0, 10, 10]}], {1: 39})
    left[0]["raw_index"] = 41; left[1]["raw_index"] = 42; right[0]["raw_index"] = 99
    result = diff_blocks(left, right)
    assert result["bbox_matches"] == [{"left_raw_index": 41, "right_raw_index": 99, "bbox_iou": 1.0}]
    assert result["semantic_conflicts"] == [{"kind": "title_to_text_downgrade", "left_raw_index": 41, "right_raw_index": 99, "bbox_iou": 1.0, "resolution": None}]


def test_diff_blocks_reports_cross_view_image_heading_overlap_with_colliding_indices():
    heading = normalize_content([{"type": "text", "page_idx": 0, "text": "Summary", "text_level": 2, "bbox": [0, 0, 10, 10]}], {1: 25})
    image = normalize_content([{"type": "image", "page_idx": 0, "img_path": "images/summary.jpg", "bbox": [0, 0, 10, 10]}], {1: 25})
    assert heading[0]["raw_index"] == image[0]["raw_index"] == 0
    conflicts = diff_blocks(heading, image)["semantic_conflicts"]
    assert {tuple(sorted(conflict.items())) for conflict in conflicts if conflict["kind"] == "image_heading_overlap"} == {
        tuple(sorted({"kind": "image_heading_overlap", "asset_side": "right", "heading_side": "left", "asset_raw_index": 0, "heading_raw_index": 0, "bbox_iou": 1.0, "resolution": None}.items()))
    }
    image[0]["source_page"] = 26
    assert not [conflict for conflict in diff_blocks(heading, image)["semantic_conflicts"] if conflict["kind"] == "image_heading_overlap"]


@pytest.mark.parametrize("reference,error", [("../outside.jpg", ValueError), ("C:\\outside.jpg", ValueError), ("images/missing.jpg", FileNotFoundError)])
def test_comparator_rejects_asset_escape_and_missing_referenced_asset(tmp_path, reference, error):
    manifest = tmp_path / "sample_pages.json"
    manifest.write_text(json.dumps({"ordered_pages": [{"sample_page": 1, "source_page": 5}]}), encoding="utf-8")
    rows = [{"type": "image", "page_idx": 0, "img_path": reference, "bbox": [0, 0, 10, 10]}]
    roots = {name: tmp_path / name for name in ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")}
    for root in roots.values():
        _write_view(root, rows)
    with pytest.raises(error):
        compare_views(manifest, roots, tmp_path / "comparison")


def test_mineru_wrapper_declares_both_profiles_and_runtime_environment():
    wrapper = (Path(__file__).parents[1] / "scripts" / "run_mineru_three_view.ps1").read_text(encoding="utf-8")
    for required in ("$MinerURoot", "hybrid_high", "pipeline_ocr", "initialize.ps1", "MINERU_TOOLS_CONFIG_JSON", "NO_PROXY", "HF_HOME", "TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER", "hybrid-engine", '"pipeline", "--method", "ocr"'):
        assert required in wrapper


def test_mineru_setup_installs_required_cpu_before_optional_gpu_probe():
    scripts = Path(__file__).parents[2] / "MinerU" / "scripts"
    setup = (scripts / "setup.ps1").read_text(encoding="utf-8")
    cpu_install = setup.index('Install-MinerUProfile -Profile "pipeline-cpu-v1"')
    hardware_probe = setup.index('"probe-capability.ps1") -ToolRoot $roots.ToolRoot -HardwareOnly')
    assert cpu_install < hardware_probe
    assert 'Install-MinerUProfile -Profile "windows-cu128-v1"' in setup
    assert "MinerU setup: SKIPPED" not in setup
    assert 'pipeline[0].state -ne "ready"' in setup


def test_mineru_capability_probe_is_provider_scoped_and_cpu_is_never_skipped():
    scripts = Path(__file__).parents[2] / "MinerU" / "scripts"
    probe = (scripts / "probe-capability.ps1").read_text(encoding="utf-8")
    verify = (scripts / "verify.ps1").read_text(encoding="utf-8")
    for required in (
        '"providers.json"',
        '"nri.mineru_provider_capabilities.v1"',
        '"pipeline_cpu"',
        '"hybrid_cuda"',
        '"vlm_cuda"',
        '"ready"',
        '"unavailable"',
        "nvidia-smi",
    ):
        assert required in probe
    assert 'MinerU verification: SKIPPED' not in verify
    assert '"pipeline-cpu-v1"' in verify
