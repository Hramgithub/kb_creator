import hashlib
import json
import math
from pathlib import Path
import subprocess

import pytest
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import FloatObject, NameObject, NumberObject, RectangleObject
from reportlab.pdfgen import canvas
from jsonschema import validate

from kb_creator.scripts.build_mineru_visual_merge_bundle import (
    ASPECT_TOLERANCE,
    CPU_TRIPTYCH,
    DIMENSION_TOLERANCE_PT,
    GEOMETRY_POLICY,
    GeometryContractError,
    _attach_render_evidence,
    _first_mismatch,
    _seal,
    _write_geometry_failure,
    build_geometry_plan,
    build_bundle,
    build_optional_companions,
    validate_v2_bundle,
)
from kb_creator.scripts.prepare_mineru_three_view_inputs import (
    SOURCE_DISPLAYED_MEDIABOX_POLICY,
    prepare_inputs,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _pdf(path: Path, width: float, height: float, *, pages: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = canvas.Canvas(str(path), pagesize=(width, height), invariant=1)
    for page in range(pages):
        document.drawString(12, height - 20, f"page {page + 1}")
        document.showPage()
    document.save()


def _rewrite_pdf(path: Path, *, media=None, crop=None, rotations=None, user_unit=1) -> None:
    reader = PdfReader(path)
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        if media is not None:
            page.mediabox = RectangleObject(media[index] if isinstance(media[0], (list, tuple)) else media)
        if crop is not None:
            page.cropbox = RectangleObject(crop[index] if isinstance(crop[0], (list, tuple)) else crop)
        if rotations is not None:
            page[NameObject("/Rotate")] = NumberObject(rotations[index] if isinstance(rotations, list) else rotations)
        page[NameObject("/UserUnit")] = FloatObject(user_unit)
        writer.add_page(page)
    with path.open("wb") as stream:
        writer.write(stream)


def _authority(width="595", height="841", pages=1):
    width_value, height_value = float(width), float(height)
    return {
        "schema": "kb_creator.mineru_three_view_inputs.v2",
        "ordered_pages": [{"sample_page": page, "source_page": page} for page in range(1, pages + 1)],
        "render": {
            "geometry_policy": GEOMETRY_POLICY,
            "source_box": "MediaBox",
            "raster_has_text_layer": False,
            "dpi": 200,
            "page_geometry": [
                {
                    "source_page": page,
                    "media_box_coordinates": [0, 0, width, height],
                    "crop_box_coordinates": [0, 0, width, height],
                    "source_rotation_degrees": 0,
                    "source_user_unit": 1,
                    "displayed_page_size_points": [width, height],
                    "raster_pixel_dimensions": [math.ceil(width_value * 200 / 72), math.ceil(height_value * 200 / 72)],
                    "raster_pdf_page_size_points": [width, height],
                    "raster_pdf_rotation_degrees": 0,
                    "raster_pdf_user_unit": 1,
                }
                for page in range(1, pages + 1)
            ],
        },
    }


def _plan(tmp_path: Path, views=CPU_TRIPTYCH, *, size=(595, 841), rotation=0, authority=None):
    layouts = {}
    for view in views:
        path = tmp_path / f"{view}.pdf"
        _pdf(path, *size)
        if rotation:
            _rewrite_pdf(path, rotations=rotation)
        layouts[view] = path
    marker = tmp_path / "prepared.json"
    marker.write_text("{}", encoding="utf-8")
    identities = {"path_hint": "fixture", "bytes": 2, "sha256": "A" * 64}
    return build_geometry_plan(
        prepared_manifest=authority or _authority(*map(str, size)),
        prepared_identity={"path_hint": "prepared.json", "bytes": 2, "sha256": _sha(marker)},
        layouts=layouts,
        views=tuple(views),
        dpi=110,
        renderer={"path_hint": "pdftoppm", "bytes": 1, "sha256": "B" * 64, "version": "fixture", "argv_recipe": "pdftoppm-mediabox-png-v1"},
        run_identity_sha256="C" * 64,
        source_identity=identities,
        comparison_identity=identities,
        view_set_identity={**identities, "receipt_sha256": "D" * 64},
    )


def test_source_authority_regression_keeps_595x841_canvas_after_1653x2337_sampling(tmp_path):
    source = tmp_path / "source.pdf"
    _pdf(source, 595, 841)
    output = tmp_path / "prepared"
    manifest = prepare_inputs(
        source, output, _sha(source), "1", 200, "source", raster_only=True,
        geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY,
    )
    row = manifest["render"]["page_geometry"][0]
    assert row["raster_pixel_dimensions"] == [1653, 2337]
    assert row["raster_pdf_page_size_points"] == [595.0, 841.0]
    page = PdfReader(output / "source_raster.pdf").pages[0]
    assert [float(page.mediabox.width), float(page.mediabox.height)] == [595.0, 841.0]
    assert math.ceil(float(page.mediabox.width) * 110 / 72) == 910
    assert math.ceil(float(page.mediabox.height) * 110 / 72) == 1285
    assert page.extract_text().strip() == "" and len(page.images) == 1
    validate(manifest, json.loads((Path(__file__).resolve().parents[1] / "contracts" / "mineru_three_view_inputs.v2.schema.json").read_text(encoding="utf-8")))


@pytest.mark.parametrize("size", [(612, 792), (792, 612), (421.125, 613.875)])
def test_source_authority_accepts_arbitrary_uniform_canvas(tmp_path, size):
    source = tmp_path / "source.pdf"
    _pdf(source, *size)
    manifest = prepare_inputs(source, tmp_path / "out", _sha(source), "1", 144, "x", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    observed = manifest["raster_pdf_verification"][0]["displayed_page_size_points"]
    assert observed == [float(size[0]), float(size[1])]


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_source_authority_flattens_all_right_angle_rotations(tmp_path, rotation):
    source = tmp_path / f"source-{rotation}.pdf"
    _pdf(source, 300, 500)
    _rewrite_pdf(source, rotations=rotation)
    manifest = prepare_inputs(source, tmp_path / f"out-{rotation}", _sha(source), "1", 72, "x", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    expected = [300.0, 500.0] if rotation in (0, 180) else [500.0, 300.0]
    assert manifest["render"]["page_geometry"][0]["displayed_page_size_points"] == expected
    assert manifest["raster_pdf_verification"][0]["rotation_degrees"] == 0


def test_source_authority_preserves_nonzero_origin_extent_and_ignores_crop_lure(tmp_path):
    source = tmp_path / "origin.pdf"
    _pdf(source, 500, 700)
    _rewrite_pdf(source, media=[10, 20, 605, 861], crop=[10, 20, 500, 700])
    manifest = prepare_inputs(source, tmp_path / "out", _sha(source), "1", 72, "x", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    row = manifest["render"]["page_geometry"][0]
    assert row["media_box_coordinates"] == [10.0, 20.0, 605.0, 861.0]
    assert row["displayed_page_size_points"] == [595.0, 841.0]
    assert row["crop_box_coordinates"] != row["media_box_coordinates"]


def test_source_authority_rejects_mixed_rotation_nonright_and_nonunit_userunit(tmp_path):
    source = tmp_path / "mixed.pdf"
    _pdf(source, 500, 700, pages=2)
    _rewrite_pdf(source, rotations=[0, 90])
    manifest = prepare_inputs(source, tmp_path / "mixed-out", _sha(source), "1-2", 72, "x", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    assert manifest["schema"] == "kb_creator.mineru_three_view_inputs.v3"
    assert [row["displayed_page_size_points"] for row in manifest["render"]["page_geometry"]] == [[500.0, 700.0], [700.0, 500.0]]
    for name, rotation, unit, match in (("angle", 45, 1, "right angle"), ("unit", 0, 2, "UserUnit 1")):
        path = tmp_path / f"{name}.pdf"
        _pdf(path, 500, 700)
        _rewrite_pdf(path, rotations=rotation, user_unit=unit)
        with pytest.raises(ValueError, match=match):
            prepare_inputs(path, tmp_path / f"{name}-out", _sha(path), "1", 72, "x", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)


def test_source_authority_rejects_mixed_page_sizes_before_output(tmp_path):
    source = tmp_path / "mixed-size.pdf"
    document = canvas.Canvas(str(source), pagesize=(500, 700), invariant=1)
    document.showPage()
    document.setPageSize((501, 700))
    document.showPage()
    document.save()
    output = tmp_path / "out"
    manifest = prepare_inputs(source, output, _sha(source), "1-2", 72, "x", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    assert manifest["schema"] == "kb_creator.mineru_three_view_inputs.v3"
    assert [row["displayed_page_size_points"] for row in manifest["render"]["page_geometry"]] == [[500.0, 700.0], [501.0, 700.0]]


def _row(width: str, height: str, *, view=CPU_TRIPTYCH[0], page=1, rotation=0, unit="1"):
    return {"view_id": view, "source_page": page, "rotation_degrees": rotation, "user_unit": unit, "effective_displayed_size_points": [width, height]}


def test_decimal_dimension_and_aspect_boundaries_are_fail_closed():
    authority = [{"source_page": 1, "displayed_page_size_points": ["100", "100"]}]
    assert str(DIMENSION_TOLERANCE_PT) == "0.001" and str(ASPECT_TOLERANCE) == "0.000005"
    assert _first_mismatch([_row("100.001", "100.001")], authority, (CPU_TRIPTYCH[0],)) is None
    assert _first_mismatch([_row("100.0011", "100")], authority, (CPU_TRIPTYCH[0],))["kind"] == "displayed_dimension"
    small = [{"source_page": 1, "displayed_page_size_points": ["1", "100"]}]
    assert _first_mismatch([_row("1.000004", "100")], small, (CPU_TRIPTYCH[0],)) is None
    assert _first_mismatch([_row("1.000006", "100")], small, (CPU_TRIPTYCH[0],))["kind"] == "aspect_ratio"


@pytest.mark.parametrize("value", ["0", "-1", "NaN", "Infinity", "-Infinity"])
def test_geometry_preflight_rejects_nonpositive_or_nonfinite_dimensions(value):
    authority = [{"source_page": 1, "displayed_page_size_points": ["100", "100"]}]
    mismatch = _first_mismatch([_row(value, "100")], authority, (CPU_TRIPTYCH[0],))
    assert mismatch["kind"] in {"nonpositive_dimension", "invalid_numeric_geometry"}


@pytest.mark.parametrize("count", [3, 4, 5])
def test_geometry_plan_supports_exact_dynamic_view_counts_and_stable_cpu_triptych(tmp_path, count):
    views = (*CPU_TRIPTYCH, "original_hybrid_high", "original_vlm")[:count]
    plan = _plan(tmp_path, views)
    assert plan["succeeded_views"][:3] == list(CPU_TRIPTYCH)
    assert len(plan["layouts"]) == count and plan["targets"][0]["target_pixels"] == [910, 1285]


def test_geometry_plan_rejects_raster_rotation_and_observed_physical_drift(tmp_path):
    with pytest.raises(GeometryContractError) as drift:
        _plan(tmp_path / "drift", size=(595.08, 841.32), authority=_authority())
    assert drift.value.mismatch["kind"] == "displayed_dimension"
    with pytest.raises(GeometryContractError) as rotated:
        _plan(tmp_path / "rotated", rotation=90, authority=_authority("841", "595"))
    assert rotated.value.mismatch["kind"] == "raster_rotation"


def test_geometry_plan_page_count_failure_contains_all_observed_views(tmp_path):
    views = CPU_TRIPTYCH
    layouts = {}
    for view in views:
        path = tmp_path / f"{view}.pdf"
        _pdf(path, 595, 841, pages=2 if view == views[0] else 1)
        layouts[view] = path
    identity = {"path_hint": "fixture", "bytes": 2, "sha256": "A" * 64}
    with pytest.raises(GeometryContractError) as caught:
        build_geometry_plan(
            prepared_manifest=_authority(), prepared_identity=identity, layouts=layouts, views=views, dpi=110,
            renderer={"path_hint": "pdftoppm", "bytes": 1, "sha256": "B" * 64, "version": "fixture", "argv_recipe": "pdftoppm-mediabox-png-v1"},
            run_identity_sha256="C" * 64, source_identity=identity, comparison_identity=identity,
            view_set_identity={**identity, "receipt_sha256": "D" * 64},
        )
    assert caught.value.mismatch == {"kind": "page_count", "view_id": views[0], "expected": 1, "actual": 2}
    assert {row["view_id"] for row in caught.value.matrix} == set(views)


def test_geometry_plan_accepts_preserved_original_rotation_with_flattened_raster(tmp_path):
    layouts = {}
    for view in CPU_TRIPTYCH:
        path = tmp_path / f"{view}.pdf"
        if view == CPU_TRIPTYCH[-1]:
            _pdf(path, 841, 595)
        else:
            _pdf(path, 595, 841)
            _rewrite_pdf(path, rotations=90)
        layouts[view] = path
    marker = tmp_path / "prepared.json"
    marker.write_text("{}", encoding="utf-8")
    identity = {"path_hint": "fixture", "bytes": 2, "sha256": "A" * 64}
    plan = build_geometry_plan(
        prepared_manifest=_authority("841", "595"), prepared_identity={**identity, "sha256": _sha(marker)},
        layouts=layouts, views=CPU_TRIPTYCH, dpi=110,
        renderer={"path_hint": "pdftoppm", "bytes": 1, "sha256": "B" * 64, "version": "fixture", "argv_recipe": "pdftoppm-mediabox-png-v1"},
        run_identity_sha256="C" * 64, source_identity=identity, comparison_identity=identity,
        view_set_identity={**identity, "receipt_sha256": "D" * 64},
    )
    assert [row["rotation_degrees"] for row in plan["observed_geometry"]] == [90, 90, 0]


def test_rendered_pixel_mismatch_is_fatal_and_optional_companions_do_not_resize(tmp_path):
    views = (*CPU_TRIPTYCH, "original_hybrid_high")
    plan = _plan(tmp_path / "plan", views, size=(72, 72))
    rendered = {}
    for view in views:
        path = tmp_path / "renders" / view / "page-001.png"
        path.parent.mkdir(parents=True)
        Image.new("RGB", (110 if view != views[-1] else 111, 110), "white").save(path)
        rendered[view] = [path]
    with pytest.raises(GeometryContractError, match="canonical target"):
        _attach_render_evidence(plan, rendered, tmp_path)
    Image.new("RGB", (110, 110), "white").save(rendered[views[-1]][0])
    sealed = _attach_render_evidence(plan, rendered, tmp_path)
    companions = build_optional_companions(rendered, tmp_path / "companions", views[3:])
    assert sealed["plan_sha256"] and len(companions) == 1
    with Image.open(companions[0]) as image:
        assert image.size == (110, 128)


def test_geometry_failure_is_deterministic_sealed_and_output_free(tmp_path):
    identities = {"source": {"sha256": "A" * 64}}
    error = GeometryContractError("bad", matrix=[_row("595.08", "841.32")], mismatch={"kind": "displayed_dimension", "source_page": 1, "view_id": CPU_TRIPTYCH[2]})
    root = tmp_path / "failure"
    _write_geometry_failure(root, error=error, identities=identities, renderer={"sha256": "B" * 64}, views=CPU_TRIPTYCH, dpi=110)
    receipt = json.loads((root / "geometry-failure.json").read_text(encoding="utf-8"))
    assert list(root.iterdir()) == [root / "geometry-failure.json"]
    assert receipt["outputs_created"] == []
    assert receipt["failure_sha256"] == _seal(receipt, "failure_sha256")["failure_sha256"]


def test_v2_geometry_path_contains_no_geometry_repair_primitive_or_poppler_scale_flag():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "build_mineru_visual_merge_bundle.py").read_text(encoding="utf-8")
    for forbidden in (".resize(", ".thumbnail(", "ImageOps.fit", '"-cropbox"', '"-scale-to"', '"-scale-to-x"', '"-scale-to-y"'):
        assert forbidden not in source


def _bundle_fixture(tmp_path: Path, *, drift=False):
    source = tmp_path / "source.pdf"
    _pdf(source, 595, 841)
    prepared_root = tmp_path / "prepared"
    prepared = prepare_inputs(source, prepared_root, _sha(source), "1", 200, "source", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    prepared_path = prepared_root / "sample_pages.json"
    raw_root = tmp_path / "raw"
    for view in CPU_TRIPTYCH:
        layout = raw_root / "views" / view / "artifacts" / "document_layout.pdf"
        _pdf(layout, 595.08 if drift and view == CPU_TRIPTYCH[-1] else 595, 841.32 if drift and view == CPU_TRIPTYCH[-1] else 841)
    view_set_path = raw_root / "view-set.json"
    view_set = _seal({"schema": "kb_creator.mineru_view_set.v1", "run_identity_sha256": "C" * 64, "succeeded_views": list(CPU_TRIPTYCH)}, "receipt_sha256")
    view_set_path.write_text(json.dumps(view_set), encoding="utf-8")
    comparison_path = tmp_path / "comparison.json"
    comparison = {
        "schema": "kb_creator.mineru_multi_view_comparison.v2", "status": "pass_for_review", "run_identity_sha256": "C" * 64,
        "manifest": {"path": str(prepared_path), "bytes": prepared_path.stat().st_size, "sha256": _sha(prepared_path)},
        "view_set": {"path": str(view_set_path), "bytes": view_set_path.stat().st_size, "sha256": _sha(view_set_path), "receipt_sha256": view_set["receipt_sha256"]},
        "succeeded_views": list(CPU_TRIPTYCH), "views": {view: {"blocks": []} for view in CPU_TRIPTYCH}, "pairwise": {},
    }
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    contract = tmp_path / "contract.json"
    contract.write_text(json.dumps({"schema": "kb_creator.scenario_reconstruction_contract.v1", "source": {"page_count": 1}, "scope": {"first_page": 1, "last_page": 1}, "page_roles": [{"first_page": 1, "last_page": 1, "role": "page"}]}), encoding="utf-8")
    renderer = tmp_path / "pdftoppm.exe"
    renderer.write_bytes(b"fixture-renderer")
    return source, prepared, prepared_path, raw_root, view_set_path, comparison_path, contract, renderer


def _fake_poppler(monkeypatch, renderer: Path):
    calls = []
    def run(argv, **kwargs):
        calls.append(list(argv))
        if argv == [str(renderer.resolve()), "-v"] or argv == [str(renderer), "-v"]:
            return subprocess.CompletedProcess(argv, 0, "", "pdftoppm fixture 1.0\n")
        prefix = Path(argv[-1])
        Image.new("RGB", (910, 1285), "white").save(prefix.with_name(prefix.name + "-1.png"))
        return subprocess.CompletedProcess(argv, 0, "", "")
    monkeypatch.setattr("kb_creator.scripts.build_mineru_visual_merge_bundle.subprocess.run", run)
    return calls


def test_v2_builder_synthetic_e2e_emits_sealed_exact_geometry_graph(tmp_path, monkeypatch):
    source, _, prepared_path, raw_root, view_set, comparison, contract, renderer = _bundle_fixture(tmp_path)
    calls = _fake_poppler(monkeypatch, renderer)
    output = tmp_path / "bundle"
    manifest = build_bundle(
        raw_root=raw_root, output_root=output, raw_receipt=view_set, raw_receipt_sha256=_sha(view_set),
        source=source, source_sha256=_sha(source), comparison=comparison, comparison_sha256=_sha(comparison),
        pdftoppm=str(renderer), dpi=110, reconstruction_contract=contract,
        prepared_manifest=prepared_path, prepared_manifest_sha256=_sha(prepared_path),
    )
    validate_v2_bundle(output, manifest)
    plan = json.loads((output / "visual" / "geometry_plan.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "kb_creator.mineru_visual_merge_bundle.v2"
    assert plan["targets"] == [{"source_page": 1, "displayed_size_points": ["595.0", "841.0"], "target_pixels": [910, 1285]}]
    assert plan["transforms"] == {"pad": False, "crop": False, "post_render_resize": False}
    assert len(plan["rendered_pages"]) == 3 and all(row["dimensions"] == [910, 1285] for row in plan["rendered_pages"])
    assert len(calls) == 5  # version preflight, render helper version, three closed renders
    for command in calls[2:]:
        assert command[1:8] == ["-r", "110", "-png", "-f", "1", "-l", "1"]
    validate(manifest, json.loads((Path(__file__).resolve().parents[1] / "contracts" / "mineru_visual_merge_bundle.v2.schema.json").read_text(encoding="utf-8")))
    validate(plan, json.loads((Path(__file__).resolve().parents[1] / "contracts" / "mineru_geometry_plan.v1.schema.json").read_text(encoding="utf-8")))

    extra = output / "visual" / "unexpected.bin"
    extra.write_bytes(b"not-in-inventory")
    with pytest.raises(ValueError, match="inventory"):
        validate_v2_bundle(output, manifest)
    extra.unlink()

    rendered_page = output / plan["rendered_pages"][0]["path"]
    original_bytes = rendered_page.read_bytes()
    rendered_page.write_bytes(original_bytes + b"tamper")
    with pytest.raises(ValueError, match="inventory changed|rendered page identity"):
        validate_v2_bundle(output, manifest)
    rendered_page.write_bytes(original_bytes)
    validate_v2_bundle(output, manifest)


def test_v2_builder_geometry_reject_is_pre_render_sealed_and_output_free(tmp_path, monkeypatch):
    source, _, prepared_path, raw_root, view_set, comparison, contract, renderer = _bundle_fixture(tmp_path, drift=True)
    calls = _fake_poppler(monkeypatch, renderer)
    output = tmp_path / "bundle"
    with pytest.raises(GeometryContractError):
        build_bundle(
            raw_root=raw_root, output_root=output, raw_receipt=view_set, raw_receipt_sha256=_sha(view_set),
            source=source, source_sha256=_sha(source), comparison=comparison, comparison_sha256=_sha(comparison),
            pdftoppm=str(renderer), dpi=110, reconstruction_contract=contract,
            prepared_manifest=prepared_path, prepared_manifest_sha256=_sha(prepared_path),
        )
    assert calls == [[str(renderer.resolve()), "-v"]]
    receipt = json.loads((output / "geometry-failure.json").read_text(encoding="utf-8"))
    assert receipt["first_mismatch"]["kind"] == "displayed_dimension"
    assert len(receipt["observed_geometry"]) == 3 and receipt["outputs_created"] == []
    assert [path.name for path in output.iterdir()] == ["geometry-failure.json"]
    validate(receipt, json.loads((Path(__file__).resolve().parents[1] / "contracts" / "mineru_geometry_failure.v1.schema.json").read_text(encoding="utf-8")))
